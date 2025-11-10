"""
Конвертер YAML квестов в граф (nodes/edges) для React Flow
"""
import yaml
from typing import Dict, List
from pathlib import Path
from .agent import QuestNode, QuestEdge, QuestGraph


class YAMLToGraphConverter:
    """Конвертирует существующие YAML квесты в граф для визуального редактора"""

    def __init__(self):
        self.node_spacing_y = 150  # Вертикальное расстояние между узлами
        self.center_x = 400  # Центр по X

    def convert_quest_file(self, yaml_path: str) -> QuestGraph:
        """
        Конвертировать YAML файл квеста в граф

        Args:
            yaml_path: Путь к YAML файлу

        Returns:
            QuestGraph с nodes и edges
        """
        # Загрузить YAML
        with open(yaml_path, 'r', encoding='utf-8') as f:
            quest_data = yaml.safe_load(f)

        return self.convert_quest_data(quest_data)

    def convert_quest_data(self, quest_data: Dict) -> QuestGraph:
        """
        Конвертировать данные квеста в граф

        Args:
            quest_data: Словарь с данными квеста из YAML

        Returns:
            QuestGraph
        """
        nodes = []
        edges = []
        current_y = 50

        # 1. StartNode
        start_node = QuestNode(
            id="start",
            type="start",
            position={"x": self.center_x, "y": current_y},
            data={
                "title": quest_data.get("title", "Квест"),
                "description": quest_data.get("description", "").strip()
            }
        )
        nodes.append(start_node)
        current_y += self.node_spacing_y

        # 2. Конвертируем steps в QuestStep или Choice nodes
        steps = quest_data.get("steps", [])
        previous_node_id = "start"

        for idx, step in enumerate(steps):
            step_id = step.get("id", f"step_{idx+1}")
            step_type = step.get("type", "input_text")

            if step_type == "choice":
                # ChoiceNode
                node = self._create_choice_node(step, step_id, current_y)
            else:
                # QuestStepNode (для input_text и других типов)
                node = self._create_quest_step_node(step, step_id, current_y)

            nodes.append(node)

            # Создать edge от предыдущего узла к текущему
            edge = QuestEdge(
                id=f"e_{previous_node_id}_to_{step_id}",
                source=previous_node_id,
                target=step_id,
                animated=True
            )
            edges.append(edge)

            previous_node_id = step_id
            current_y += self.node_spacing_y

        # 3. Reality Bridge (если есть)
        if "reality_bridge" in quest_data:
            rb_data = quest_data["reality_bridge"]
            rb_node = QuestNode(
                id="reality_bridge",
                type="realityBridge",
                position={"x": self.center_x, "y": current_y},
                data={
                    "title": rb_data.get("title", "Reality Bridge"),
                    "description": rb_data.get("description", "").strip(),
                    "deadline_hours": rb_data.get("deadline_hours", 48),
                    "reminder_hours": rb_data.get("reminder_hours", 24)
                }
            )
            nodes.append(rb_node)

            # Edge от последнего step к Reality Bridge
            edge = QuestEdge(
                id=f"e_{previous_node_id}_to_rb",
                source=previous_node_id,
                target="reality_bridge",
                animated=True
            )
            edges.append(edge)

            previous_node_id = "reality_bridge"
            current_y += self.node_spacing_y

        # 4. EndNode
        end_node = QuestNode(
            id="end",
            type="end",
            position={"x": self.center_x, "y": current_y},
            data={
                "message": quest_data.get("completion_message", "Квест завершен!").strip(),
                "xp": quest_data.get("rewards", {}).get("experience_points", 0)
            }
        )
        nodes.append(end_node)

        # Edge к EndNode
        edge = QuestEdge(
            id=f"e_{previous_node_id}_to_end",
            source=previous_node_id,
            target="end"
        )
        edges.append(edge)

        return QuestGraph(nodes=nodes, edges=edges)

    def _create_quest_step_node(self, step: Dict, step_id: str, y: int) -> QuestNode:
        """Создать QuestStepNode из step данных"""
        return QuestNode(
            id=step_id,
            type="questStep",
            position={"x": self.center_x, "y": y},
            data={
                "step_type": step.get("type", "input_text"),
                "prompt": step.get("prompt", ""),
                "hint": step.get("hint", ""),
                "validation": step.get("validation", {}),
                "character": "wise_owl",  # Default персонаж
                "psychological_method": "metacognition",  # Default
                "dialogue": step.get("prompt", "")  # Используем prompt как dialogue
            }
        )

    def _create_choice_node(self, step: Dict, step_id: str, y: int) -> QuestNode:
        """Создать ChoiceNode из step данных"""
        return QuestNode(
            id=step_id,
            type="choice",
            position={"x": self.center_x, "y": y},
            data={
                "question": step.get("prompt", ""),
                "options": [
                    {
                        "text": opt.get("text", ""),
                        "score": opt.get("score", 1.0),
                        "feedback": opt.get("feedback", "")
                    }
                    for opt in step.get("options", [])
                ]
            }
        )

    def convert_all_quests(self, quests_dir: str = "/home/user/inner_edu/src/data/quests") -> List[Dict]:
        """
        Конвертировать все квесты из директории

        Returns:
            Список словарей с информацией о квестах и их графами
        """
        quests_path = Path(quests_dir)
        converted_quests = []

        # Найти все YAML файлы
        yaml_files = list(quests_path.rglob("*.yaml")) + list(quests_path.rglob("*.yml"))

        for yaml_file in yaml_files:
            try:
                # Конвертировать
                graph = self.convert_quest_file(str(yaml_file))

                # Загрузить оригинальные данные для метаданных
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    quest_data = yaml.safe_load(f)

                converted_quests.append({
                    "quest_id": quest_data.get("id", yaml_file.stem),
                    "title": quest_data.get("title", "Квест"),
                    "location": quest_data.get("location", "unknown"),
                    "difficulty": quest_data.get("difficulty", "medium"),
                    "psychological_module": quest_data.get("psychological_module", ""),
                    "graph": graph,
                    "yaml_path": str(yaml_file)
                })

            except Exception as e:
                print(f"Error converting {yaml_file}: {e}")
                continue

        return converted_quests


# Тестовый запуск
if __name__ == "__main__":
    converter = YAMLToGraphConverter()

    # Конвертировать первый квест
    quest_path = "/home/user/inner_edu/src/data/quests/tower_confusion/quest_01_simple_words.yaml"
    graph = converter.convert_quest_file(quest_path)

    print(f"Converted quest:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    print(f"\nNode types:")
    for node in graph.nodes:
        print(f"  - {node.id}: {node.type}")
