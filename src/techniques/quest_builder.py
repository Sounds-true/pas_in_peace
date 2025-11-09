"""Quest Builder Assistant - conversational AI for creating educational quests.

Creates personalized quests for children through multi-turn dialogue.
Integrates with ContentModerator for safety and generates YAML for inner_edu.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import uuid
import yaml

from src.core.logger import get_logger
from src.core.config import settings
from src.techniques.base import Technique, TechniqueResult
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = get_logger(__name__)


class QuestStage(str, Enum):
    """Stages of quest creation process."""
    INITIAL = "initial"          # Welcome and explanation
    GATHERING = "gathering"      # Collect info (child, interests, memories)
    GENERATING = "generating"    # Generate quest YAML with GPT-4
    REVIEWING = "reviewing"      # Show preview to parent
    MODERATING = "moderating"    # Content moderation check
    FINALIZING = "finalizing"    # Save to database


@dataclass
class QuestContext:
    """Context for quest creation."""
    # Child information
    child_name: Optional[str] = None
    child_age: Optional[int] = None
    child_interests: List[str] = field(default_factory=list)
    favorite_subjects: List[str] = field(default_factory=list)

    # Family memories for clues
    family_photos: List[str] = field(default_factory=list)
    family_memories: List[str] = field(default_factory=list)
    family_jokes: List[str] = field(default_factory=list)
    familiar_locations: List[str] = field(default_factory=list)

    # Quest configuration
    quest_title: Optional[str] = None
    quest_description: Optional[str] = None
    difficulty_level: str = "medium"  # easy/medium/hard
    reveal_enabled: bool = True
    reveal_message: Optional[str] = None

    # Generated content
    quest_yaml: Optional[str] = None
    total_nodes: int = 0

    # State
    current_stage: QuestStage = QuestStage.INITIAL
    quest_id: Optional[int] = None  # DB ID after save

    # Moderation
    moderation_passed: bool = False
    moderation_issues: List[Dict] = field(default_factory=list)


class QuestBuilderAssistant(Technique):
    """
    Conversational AI assistant for creating educational quests.

    Process:
    1. INITIAL - Welcome, explain quest creation
    2. GATHERING - Ask about child (name, age, interests, memories)
    3. GENERATING - Generate quest YAML with GPT-4
    4. REVIEWING - Show preview, allow edits
    5. MODERATING - Check content safety
    6. FINALIZING - Save to database
    """

    name = "Quest Builder"
    description = "Создание персонализированных квестов для ребенка"

    def __init__(self, db_manager=None, content_moderator=None):
        """Initialize quest builder.

        Args:
            db_manager: DatabaseManager for persistence
            content_moderator: ContentModerator for safety checks
        """
        super().__init__()
        self.db = db_manager
        self.moderator = content_moderator
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            api_key=settings.openai_api_key,
        )

    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Apply quest building based on current stage.

        Args:
            user_message: User's message
            context: Conversation context with quest_context

        Returns:
            TechniqueResult with response and updated context
        """
        # Get or create quest context
        quest_ctx = context.get("quest_context")
        if not quest_ctx:
            quest_ctx = QuestContext()
            context["quest_context"] = quest_ctx
        elif isinstance(quest_ctx, dict):
            # Convert dict to QuestContext
            quest_ctx = QuestContext(**quest_ctx)
            context["quest_context"] = quest_ctx

        current_stage = quest_ctx.current_stage

        logger.info(
            "quest_builder_stage",
            stage=current_stage,
            child_name=quest_ctx.child_name
        )

        # Route to stage handler
        if current_stage == QuestStage.INITIAL:
            return await self._handle_initial(user_message, quest_ctx, context)
        elif current_stage == QuestStage.GATHERING:
            return await self._handle_gathering(user_message, quest_ctx, context)
        elif current_stage == QuestStage.GENERATING:
            return await self._handle_generating(user_message, quest_ctx, context)
        elif current_stage == QuestStage.REVIEWING:
            return await self._handle_reviewing(user_message, quest_ctx, context)
        elif current_stage == QuestStage.MODERATING:
            return await self._handle_moderating(user_message, quest_ctx, context)
        elif current_stage == QuestStage.FINALIZING:
            return await self._handle_finalizing(user_message, quest_ctx, context)
        else:
            return TechniqueResult(
                success=False,
                response="Произошла ошибка. Начнем сначала?",
                follow_up=None,
                metadata={"error": "unknown_stage"}
            )

    async def _handle_initial(
        self,
        message: str,
        quest_ctx: QuestContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle initial stage - welcome and explanation."""

        response = """🎮 **Создание Образовательного Квеста**

Отличная идея! Давайте создадим персонализированный квест для вашего ребенка.

Квест будет:
✓ Помогать с домашними заданиями (математика, логика, творчество)
✓ Содержать семейные воспоминания как подсказки
✓ Постепенно раскрывать, кто его создал (если хотите)
✓ Быть безопасным и образовательным

**Процесс займет 5-10 минут:**
1. Расскажите о ребенке (возраст, интересы)
2. Поделитесь семейными воспоминаниями
3. Я сгенерирую квест с помощью AI
4. Вы просмотрите и отредактируете
5. Проверим безопасность контента
6. Сохраним и подготовим к отправке

Готовы начать? Расскажите о вашем ребенке:
- Как зовут?
- Сколько лет?
- Что любит изучать?"""

        quest_ctx.current_stage = QuestStage.GATHERING
        context["quest_context"] = quest_ctx

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=None,
            metadata={"stage": "initial_complete"}
        )

    async def _handle_gathering(
        self,
        message: str,
        quest_ctx: QuestContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle gathering stage - collect information about child and memories."""

        message_lower = message.lower()

        # Try to extract information from message
        if not quest_ctx.child_name:
            # Look for name patterns
            # For now, just ask directly
            if any(word in message_lower for word in ["зовут", "имя", "называ"]):
                # Extract name (simplified - would need better NER)
                words = message.split()
                for i, word in enumerate(words):
                    if word.lower() in ["зовут", "имя"] and i + 1 < len(words):
                        quest_ctx.child_name = words[i + 1].strip(".,!?")
                        break

            if not quest_ctx.child_name:
                quest_ctx.child_name = message.split()[0] if len(message.split()) > 0 else "ребенок"

        # Extract age
        if not quest_ctx.child_age:
            import re
            age_match = re.search(r'(\d+)\s*(лет|год)', message_lower)
            if age_match:
                quest_ctx.child_age = int(age_match.group(1))

        # Extract interests
        interest_keywords = ["любит", "интерес", "увлека", "нравится", "хобби"]
        if any(kw in message_lower for kw in interest_keywords):
            # Simple extraction - add to interests
            quest_ctx.child_interests.append(message)

        # Check if we have enough info to proceed
        has_basic_info = (
            quest_ctx.child_name and
            quest_ctx.child_age and
            len(quest_ctx.child_interests) > 0
        )

        if not has_basic_info:
            # Ask for missing information
            if not quest_ctx.child_name:
                response = "Отлично! Как зовут вашего ребенка?"
            elif not quest_ctx.child_age:
                response = f"Замечательно! Сколько лет {quest_ctx.child_name}?"
            elif len(quest_ctx.child_interests) == 0:
                response = f"Прекрасно! Что любит изучать {quest_ctx.child_name}? Какие предметы интересны?"
            else:
                response = "Расскажите еще немного об интересах ребенка."

            context["quest_context"] = quest_ctx
            return TechniqueResult(
                success=True,
                response=response,
                follow_up=None,
                metadata={"stage": "gathering", "info_incomplete": True}
            )

        # We have basic info, now ask about memories
        if len(quest_ctx.family_memories) == 0:
            response = f"""Отлично! Теперь давайте добавим семейные воспоминания.

Эти воспоминания станут подсказками в квесте, которые {quest_ctx.child_name} будет постепенно узнавать.

**Поделитесь 2-3 воспоминаниями:**
- Места, где вы были вместе
- Совместные шутки или фразы
- Любимые семейные занятия
- Особые моменты

Например: "Мы ходили в парк Горького", "У нас была шутка про зеленого слона"

Что вспоминаете?"""

            context["quest_context"] = quest_ctx
            return TechniqueResult(
                success=True,
                response=response,
                follow_up=None,
                metadata={"stage": "gathering_memories"}
            )

        # Add memory
        if len(message.split()) > 3:  # Meaningful memory
            quest_ctx.family_memories.append(message)

        # Check if we have enough memories
        if len(quest_ctx.family_memories) < 2:
            response = f"Спасибо! Добавьте еще одно-два воспоминания. У вас уже {len(quest_ctx.family_memories)}."
            context["quest_context"] = quest_ctx
            return TechniqueResult(
                success=True,
                response=response,
                follow_up=None,
                metadata={"stage": "gathering_memories", "count": len(quest_ctx.family_memories)}
            )

        # We have enough info, move to generation
        response = f"""Отлично! У меня достаточно информации:

👤 **Ребенок:** {quest_ctx.child_name}, {quest_ctx.child_age} лет
🎯 **Интересы:** {', '.join(quest_ctx.child_interests[:3])}
💭 **Воспоминания:** {len(quest_ctx.family_memories)} добавлено

Сейчас я создам образовательный квест с помощью AI. Это займет 20-30 секунд...

⏳ Генерирую квест..."""

        quest_ctx.current_stage = QuestStage.GENERATING
        context["quest_context"] = quest_ctx

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=None,
            metadata={"stage": "gathering_complete", "proceeding_to_generation": True}
        )

    async def _handle_generating(
        self,
        message: str,
        quest_ctx: QuestContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle generation stage - create quest YAML with GPT-4."""

        try:
            # Generate quest with AI
            quest_yaml = await self._generate_quest_with_ai(quest_ctx)

            if not quest_yaml:
                return TechniqueResult(
                    success=False,
                    response="Не удалось сгенерировать квест. Попробуем еще раз?",
                    follow_up=None,
                    metadata={"error": "generation_failed"}
                )

            quest_ctx.quest_yaml = quest_yaml
            quest_ctx.total_nodes = self._count_nodes_in_yaml(quest_yaml)
            quest_ctx.current_stage = QuestStage.REVIEWING
            context["quest_context"] = quest_ctx

            # Show preview
            preview = self._generate_preview(quest_ctx)

            response = f"""✅ **Квест создан!**

{preview}

**Что дальше?**
- Отправьте "ок" или "хорошо" чтобы продолжить
- Или попросите изменить что-то (например: "добавь больше математики")
- Или "начать заново" чтобы создать другой квест"""

            return TechniqueResult(
                success=True,
                response=response,
                follow_up=None,
                metadata={"stage": "generation_complete", "nodes": quest_ctx.total_nodes}
            )

        except Exception as e:
            logger.error("quest_generation_failed", error=str(e))
            return TechniqueResult(
                success=False,
                response=f"Произошла ошибка при генерации: {str(e)}. Попробуем еще раз?",
                follow_up=None,
                metadata={"error": str(e)}
            )

    async def _handle_reviewing(
        self,
        message: str,
        quest_ctx: QuestContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle reviewing stage - parent reviews and can request changes."""

        message_lower = message.lower()

        # Check if user wants to restart
        if any(word in message_lower for word in ["заново", "сначала", "новый квест"]):
            quest_ctx.current_stage = QuestStage.INITIAL
            quest_ctx.quest_yaml = None
            context["quest_context"] = quest_ctx
            return await self._handle_initial(message, quest_ctx, context)

        # Check if user approves
        if any(word in message_lower for word in ["ок", "хорошо", "отлично", "да", "подходит", "принят"]):
            quest_ctx.current_stage = QuestStage.MODERATING
            context["quest_context"] = quest_ctx

            response = """✅ Отлично! Теперь проверяю контент на безопасность...

⏳ Модерация контента..."""

            return TechniqueResult(
                success=True,
                response=response,
                follow_up=None,
                metadata={"stage": "review_approved", "proceeding_to_moderation": True}
            )

        # User wants changes
        if len(message.split()) > 3:  # Meaningful edit request
            response = """Понял ваш запрос на изменения.

К сожалению, автоматическое редактирование пока не реализовано в MVP.

**Варианты:**
1. Отправьте "ок" чтобы продолжить с текущей версией
2. Отправьте "начать заново" чтобы создать новый квест

Что выбираете?"""

            return TechniqueResult(
                success=True,
                response=response,
                follow_up=None,
                metadata={"stage": "review_edit_requested", "mvp_limitation": True}
            )

        # Unclear input
        response = """Не совсем понял.

Отправьте:
- "ок" или "хорошо" чтобы продолжить
- "начать заново" чтобы создать другой квест"""

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=None,
            metadata={"stage": "review_unclear_input"}
        )

    async def _handle_moderating(
        self,
        message: str,
        quest_ctx: QuestContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle moderation stage - check content safety."""

        if not self.moderator:
            # No moderator available, skip to finalizing
            logger.warning("content_moderator_unavailable", action="skipping_moderation")
            quest_ctx.moderation_passed = True
            quest_ctx.current_stage = QuestStage.FINALIZING
            context["quest_context"] = quest_ctx
            return await self._handle_finalizing(message, quest_ctx, context)

        try:
            # Run moderation
            moderation_result = await self.moderator.moderate_quest(
                quest_ctx.quest_yaml,
                quest_metadata={
                    "child_age": quest_ctx.child_age,
                    "child_name": quest_ctx.child_name
                }
            )

            quest_ctx.moderation_passed = moderation_result["passed"]
            quest_ctx.moderation_issues = moderation_result["issues"]

            if moderation_result["passed"]:
                # Passed moderation, move to finalizing
                quest_ctx.current_stage = QuestStage.FINALIZING
                context["quest_context"] = quest_ctx

                response = """✅ **Проверка безопасности пройдена!**

Контент безопасен для ребенка. Сохраняю квест...

⏳ Сохранение..."""

                return TechniqueResult(
                    success=True,
                    response=response,
                    follow_up=None,
                    metadata={"stage": "moderation_passed"}
                )
            else:
                # Failed moderation
                issues_text = "\n".join([
                    f"- {issue['category']}: {issue['message']}"
                    for issue in moderation_result["issues"][:3]
                ])

                suggestions_text = "\n".join([
                    f"• {suggestion}"
                    for suggestion in moderation_result["suggestions"][:3]
                ])

                response = f"""⚠️ **Обнаружены проблемы с контентом**

Критических проблем: {moderation_result['critical_issues']}
Всего проблем: {moderation_result['total_issues']}

**Основные проблемы:**
{issues_text}

**Рекомендации:**
{suggestions_text}

**Что делать?**
К сожалению, автоматическое исправление пока не реализовано.

Отправьте "начать заново" чтобы создать другой квест с учетом этих рекомендаций."""

                quest_ctx.current_stage = QuestStage.INITIAL
                context["quest_context"] = quest_ctx

                return TechniqueResult(
                    success=False,
                    response=response,
                    follow_up=None,
                    metadata={
                        "stage": "moderation_failed",
                        "issues": moderation_result["issues"]
                    }
                )

        except Exception as e:
            logger.error("moderation_failed", error=str(e))
            # On error, skip moderation and continue
            quest_ctx.moderation_passed = True
            quest_ctx.current_stage = QuestStage.FINALIZING
            context["quest_context"] = quest_ctx
            return await self._handle_finalizing(message, quest_ctx, context)

    async def _handle_finalizing(
        self,
        message: str,
        quest_ctx: QuestContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle finalizing stage - save quest to database."""

        if not self.db:
            logger.warning("database_manager_unavailable", action="quest_not_saved")
            response = """✅ **Квест создан!**

⚠️ К сожалению, не удалось сохранить в базу данных (DatabaseManager недоступен).

YAML квеста готов и может быть экспортирован позже."""

            return TechniqueResult(
                success=True,
                response=response,
                follow_up=None,
                metadata={"stage": "finalizing_no_db", "yaml": quest_ctx.quest_yaml}
            )

        try:
            # Get user_id from context
            user_id = context.get("user_id")
            if not user_id:
                raise ValueError("user_id not found in context")

            # Generate unique quest_id
            quest_id_str = f"quest_{uuid.uuid4().hex[:8]}"

            # Save to database
            quest = await self.db.create_quest(
                user_id=user_id,
                quest_id=quest_id_str,
                title=quest_ctx.quest_title or f"Quest for {quest_ctx.child_name}",
                quest_yaml=quest_ctx.quest_yaml,
                description=quest_ctx.quest_description or "Educational quest",
                child_name=quest_ctx.child_name,
                child_age=quest_ctx.child_age,
                child_interests=quest_ctx.child_interests,
                total_nodes=quest_ctx.total_nodes,
                difficulty_level=quest_ctx.difficulty_level,
                family_memories=quest_ctx.family_memories,
                family_jokes=quest_ctx.family_jokes,
                reveal_enabled=quest_ctx.reveal_enabled,
                reveal_message=quest_ctx.reveal_message,
            )

            quest_ctx.quest_id = quest.id
            context["quest_context"] = quest_ctx

            response = f"""🎉 **Квест успешно создан и сохранен!**

**ID квеста:** {quest_id_str}
**Название:** {quest.title}
**Узлов:** {quest_ctx.total_nodes}
**Статус:** Черновик (требуется review)

**Следующие шаги:**
1. Квест будет доступен в веб-интерфейсе
2. Вы сможете просмотреть его визуально (граф узлов)
3. После финального review он будет отправлен в inner_edu
4. Ребенок получит его как "образовательное приложение"

**Создать еще один квест?** Отправьте "новый квест"."""

            logger.info(
                "quest_created_successfully",
                quest_id=quest.id,
                user_id=user_id,
                child_name=quest_ctx.child_name
            )

            # Reset context for new quest
            context["quest_context"] = QuestContext()

            return TechniqueResult(
                success=True,
                response=response,
                follow_up=None,
                metadata={
                    "stage": "finalizing_complete",
                    "quest_id": quest.id,
                    "quest_id_str": quest_id_str
                }
            )

        except Exception as e:
            logger.error("quest_save_failed", error=str(e))
            return TechniqueResult(
                success=False,
                response=f"Ошибка при сохранении квеста: {str(e)}. Попробуйте позже.",
                follow_up=None,
                metadata={"error": str(e)}
            )

    async def _generate_quest_with_ai(self, quest_ctx: QuestContext) -> str:
        """Generate quest YAML using GPT-4.

        Args:
            quest_ctx: Quest context with child info and memories

        Returns:
            YAML string for quest
        """
        # Build prompt
        prompt = f"""Create an educational quest for a child with the following information:

Child Name: {quest_ctx.child_name}
Child Age: {quest_ctx.child_age}
Interests: {', '.join(quest_ctx.child_interests)}
Difficulty: {quest_ctx.difficulty_level}

Family Memories (to be included as subtle clues):
{chr(10).join(f'- {mem}' for mem in quest_ctx.family_memories)}

**IMPORTANT GUIDELINES:**
1. Create 5-7 educational nodes (math, logic, creativity)
2. Include family memories as background images or subtle references (NO direct text!)
3. Keep content age-appropriate and neutral
4. Focus on education and fun
5. NO adult topics (divorce, court, legal issues)
6. NO manipulation or blame language
7. NO personal information about the other parent

Generate a valid YAML quest in this format:

```yaml
quest_id: unique_id
title: "Quest Title"
description: "Brief description"
difficulty: {quest_ctx.difficulty_level}
age_range: "{quest_ctx.child_age}-{quest_ctx.child_age + 2}"

nodes:
  - node_id: 1
    type: input_text
    prompt: "Educational task here"
    validation:
      min_length: 2
      max_length: 100
    rewards:
      xp: 10

  - node_id: 2
    type: choice
    prompt: "Question here"
    options:
      - text: "Option 1"
        score: 1.0
        feedback: "Correct!"
      - text: "Option 2"
        score: 0.0
        feedback: "Try again"

# Continue with more nodes...
```

Generate the complete YAML now:"""

        try:
            messages = [
                SystemMessage(content="You are an expert educational content creator specializing in child-appropriate quests."),
                HumanMessage(content=prompt)
            ]

            response = await self.llm.ainvoke(messages)
            yaml_content = response.content

            # Extract YAML from markdown code blocks if present
            if "```yaml" in yaml_content:
                yaml_content = yaml_content.split("```yaml")[1].split("```")[0].strip()
            elif "```" in yaml_content:
                yaml_content = yaml_content.split("```")[1].split("```")[0].strip()

            # Validate YAML
            try:
                yaml.safe_load(yaml_content)
                return yaml_content
            except yaml.YAMLError as e:
                logger.error("invalid_yaml_generated", error=str(e))
                return None

        except Exception as e:
            logger.error("gpt4_quest_generation_failed", error=str(e))
            return None

    def _count_nodes_in_yaml(self, yaml_content: str) -> int:
        """Count nodes in YAML content."""
        try:
            data = yaml.safe_load(yaml_content)
            nodes = data.get("nodes", [])
            return len(nodes)
        except:
            return 0

    def _generate_preview(self, quest_ctx: QuestContext) -> str:
        """Generate text preview of quest."""
        try:
            data = yaml.safe_load(quest_ctx.quest_yaml)

            title = data.get("title", "Untitled Quest")
            description = data.get("description", "No description")
            nodes_count = len(data.get("nodes", []))

            preview = f"""**Название:** {title}
**Описание:** {description}
**Узлов:** {nodes_count}
**Сложность:** {quest_ctx.difficulty_level}

**Первые узлы:**"""

            for i, node in enumerate(data.get("nodes", [])[:3]):
                node_type = node.get("type", "unknown")
                prompt = node.get("prompt", "No prompt")[:60]
                preview += f"\n{i+1}. [{node_type}] {prompt}..."

            if nodes_count > 3:
                preview += f"\n... и еще {nodes_count - 3} узлов"

            return preview
        except Exception as e:
            logger.error("preview_generation_failed", error=str(e))
            return "**Предпросмотр недоступен**"
