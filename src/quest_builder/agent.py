"""
QuestBuilderAgent - AI агент для создания квестов через GPT-4
Генерирует граф квеста в формате nodes/edges для React Flow
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from openai import AsyncOpenAI
from pydantic import BaseModel


class QuestNode(BaseModel):
    """Узел графа квеста"""
    id: str
    type: str  # start, questStep, choice, realityBridge, end
    position: Dict[str, float]  # {x, y}
    data: Dict


class QuestEdge(BaseModel):
    """Связь между узлами"""
    id: str
    source: str
    target: str
    label: Optional[str] = None
    animated: bool = False


class QuestGraph(BaseModel):
    """Полный граф квеста"""
    nodes: List[QuestNode]
    edges: List[QuestEdge]


class ConversationStage:
    """Стадии разговора с родителем"""
    GREETING = "greeting"
    COLLECTING_INFO = "collecting_info"
    CLARIFYING = "clarifying"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    QUEST_READY = "quest_ready"


class QuestBuilderAgent:
    """AI агент для создания квестов"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-1106-preview"  # Поддерживает function calling

    def _get_system_prompt(self, stage: str) -> str:
        """Системный промпт в зависимости от стадии"""
        base_prompt = """Ты - AI помощник для создания образовательных квестов для детей 7-14 лет с трудностями обучения.

Твоя задача - помочь родителю создать персонализированный квест через разговор.

Доступные психологические методы:
- metaphor (метафора) - объяснение через сравнение
- visualization (визуализация) - создание ментальных образов
- chunking (разбиение) - деление информации на части
- association (ассоциация) - связь с знакомым
- repetition (повторение) - закрепление через повтор
- gamification (игрофикация) - элементы игры

Персонажи:
- wise_owl (мудрая сова) - для объяснений
- memory_crystal (кристалл памяти) - для запоминания
- attention_butterfly (бабочка внимания) - для концентрации
- motivation_dragon (дракон мотивации) - для вдохновения

Локации (7 мест Понималии):
- tower_confusion (Башня Непонимания)
- forest_memory (Лес Памяти)
- river_attention (Река Внимания)
- mountain_motivation (Гора Мотивации)
- valley_emotions (Долина Эмоций)
- bridge_reality (Мост Реальности)
- castle_understanding (Замок Понимания)
"""

        stage_prompts = {
            ConversationStage.GREETING: """
Сейчас стадия: ПРИВЕТСТВИЕ
Поздоровайся с родителем дружелюбно и спроси, чему он хочет научить ребенка.""",

            ConversationStage.COLLECTING_INFO: """
Сейчас стадия: СБОР ИНФОРМАЦИИ
Задай вопросы:
1. Возраст ребенка?
2. Какие у него сложности? (память, внимание, мотивация, понимание)
3. О чем будет квест? (тема)
Задавай по одному вопросу за раз, дружелюбно.""",

            ConversationStage.CLARIFYING: """
Сейчас стадия: УТОЧНЕНИЕ ДЕТАЛЕЙ
Уточни:
1. Сколько шагов в квесте? (рекомендуй 5-7)
2. Линейный сюжет или с выборами?
3. Предпочитает ли ребенок визуальные образы или логику?""",

            ConversationStage.GENERATING: """
Сейчас стадия: ГЕНЕРАЦИЯ КВЕСТА
Скажи родителю, что генерируешь квест. Используй function calling для generate_quest_graph.""",

            ConversationStage.REVIEWING: """
Сейчас стадия: ПРОСМОТР КВЕСТА
Квест сгенерирован. Спроси, нравится ли родителю, нужны ли изменения.""",
        }

        return base_prompt + stage_prompts.get(stage, "")

    def _get_graph_generation_function(self) -> Dict:
        """GPT-4 function для генерации графа квеста"""
        return {
            "name": "generate_quest_graph",
            "description": "Генерирует граф образовательного квеста с узлами и связями",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Название квеста"
                    },
                    "nodes": {
                        "type": "array",
                        "description": "Узлы графа квеста",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": ["start", "questStep", "choice", "realityBridge", "end"]
                                },
                                "position": {
                                    "type": "object",
                                    "properties": {
                                        "x": {"type": "number"},
                                        "y": {"type": "number"}
                                    }
                                },
                                "data": {
                                    "type": "object",
                                    "description": "Содержимое узла (зависит от типа)"
                                }
                            },
                            "required": ["id", "type", "position", "data"]
                        }
                    },
                    "edges": {
                        "type": "array",
                        "description": "Связи между узлами",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "source": {"type": "string"},
                                "target": {"type": "string"},
                                "label": {"type": "string"},
                                "animated": {"type": "boolean"}
                            },
                            "required": ["id", "source", "target"]
                        }
                    }
                },
                "required": ["title", "nodes", "edges"]
            }
        }

    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict],
        current_stage: str,
        quest_context: Optional[Dict] = None
    ) -> Tuple[str, str, Optional[QuestGraph]]:
        """
        Обработать сообщение пользователя

        Returns:
            (ai_response, new_stage, quest_graph)
        """
        # Добавляем сообщение пользователя в историю
        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Определяем, нужно ли переходить к генерации
        should_generate = self._should_generate_quest(
            current_stage,
            conversation_history,
            quest_context
        )

        # Подготовка messages для OpenAI
        messages = [
            {"role": "system", "content": self._get_system_prompt(current_stage)}
        ] + conversation_history

        # Если нужно генерировать граф
        if should_generate:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=[self._get_graph_generation_function()],
                function_call={"name": "generate_quest_graph"}
            )

            message = response.choices[0].message

            if message.function_call:
                # GPT-4 сгенерировал граф
                function_args = json.loads(message.function_call.arguments)
                quest_graph = self._build_quest_graph(function_args, quest_context)

                ai_response = f"Отлично! Я создал квест '{function_args.get('title', 'Квест')}'. Сейчас ты увидишь граф квеста на экране. Можешь редактировать узлы или попросить меня изменить что-то."

                conversation_history.append({
                    "role": "assistant",
                    "content": ai_response
                })

                return ai_response, ConversationStage.REVIEWING, quest_graph

        # Обычный разговор без генерации
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=300
        )

        ai_response = response.choices[0].message.content
        conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })

        # Определяем следующую стадию
        new_stage = self._determine_next_stage(
            current_stage,
            conversation_history,
            quest_context
        )

        return ai_response, new_stage, None

    def _should_generate_quest(
        self,
        current_stage: str,
        conversation_history: List[Dict],
        quest_context: Optional[Dict]
    ) -> bool:
        """Определяет, нужно ли генерировать квест"""
        if current_stage == ConversationStage.GENERATING:
            return True

        # Проверяем, собрана ли вся необходимая информация
        if quest_context and all([
            quest_context.get("age"),
            quest_context.get("topic"),
            quest_context.get("difficulties"),
            quest_context.get("num_steps")
        ]):
            return True

        return False

    def _determine_next_stage(
        self,
        current_stage: str,
        conversation_history: List[Dict],
        quest_context: Optional[Dict]
    ) -> str:
        """Определяет следующую стадию разговора"""
        # Простая логика переходов (можно улучшить с ML)
        if current_stage == ConversationStage.GREETING:
            return ConversationStage.COLLECTING_INFO

        if current_stage == ConversationStage.COLLECTING_INFO:
            # Если собрали возраст, тему и сложности
            if quest_context and len(quest_context) >= 3:
                return ConversationStage.CLARIFYING

        if current_stage == ConversationStage.CLARIFYING:
            # Если уточнили количество шагов
            if quest_context and quest_context.get("num_steps"):
                return ConversationStage.GENERATING

        return current_stage

    def _build_quest_graph(self, function_args: Dict, quest_context: Optional[Dict]) -> QuestGraph:
        """Построить QuestGraph из GPT-4 function call"""
        nodes = []
        edges = []

        for node_data in function_args.get("nodes", []):
            nodes.append(QuestNode(**node_data))

        for edge_data in function_args.get("edges", []):
            edges.append(QuestEdge(**edge_data))

        return QuestGraph(nodes=nodes, edges=edges)

    async def refine_node(
        self,
        node_id: str,
        user_feedback: str,
        current_graph: QuestGraph
    ) -> QuestNode:
        """
        Улучшить конкретный узел графа по запросу пользователя

        Args:
            node_id: ID узла для улучшения
            user_feedback: Что изменить (например, "Сделай проще")
            current_graph: Текущий граф квеста

        Returns:
            Обновленный узел
        """
        # Найти узел
        node = next((n for n in current_graph.nodes if n.id == node_id), None)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        # Промпт для GPT-4
        prompt = f"""Улучши следующий узел квеста:

Тип: {node.type}
Текущее содержимое: {json.dumps(node.data, ensure_ascii=False, indent=2)}

Запрос пользователя: {user_feedback}

Верни улучшенное содержимое узла в JSON формате (только поле data)."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Ты помощник для улучшения квестов. Отвечай только JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        # Парсим ответ
        try:
            improved_data = json.loads(response.choices[0].message.content)
            node.data = improved_data
            return node
        except json.JSONDecodeError:
            # Fallback - возвращаем оригинальный узел
            return node

    def graph_to_yaml(self, graph: QuestGraph) -> str:
        """
        Конвертировать граф в YAML формат для совместимости с QuestEngine

        Args:
            graph: Граф квеста

        Returns:
            YAML строка
        """
        # TODO: Реализовать конвертацию graph -> YAML
        # Это нужно для выполнения квестов через существующий StateManager
        yaml_content = "# TODO: Convert graph to YAML\n"
        return yaml_content
