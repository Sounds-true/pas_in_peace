"""Letter Writing Assistant - помощь в написании писем ребёнку."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from src.core.logger import get_logger
from src.core.config import settings
from src.techniques.base import Technique, TechniqueResult
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


logger = get_logger(__name__)


class LetterStage(str, Enum):
    """Stages of letter writing process."""
    INITIAL = "initial"  # Начало: сбор информации
    GATHERING = "gathering"  # Сбор деталей
    GENERATING = "generating"  # Генерация черновика
    REVIEWING = "reviewing"  # Просмотр и редактирование
    EDITING = "editing"  # Редактирование
    FINALIZING = "finalizing"  # Финализация


@dataclass
class LetterContext:
    """Context for letter writing."""
    recipient: Optional[str] = None  # Кому (имя ребёнка)
    purpose: Optional[str] = None  # Цель письма
    key_points: list = None  # Ключевые моменты
    tone: str = "warm"  # Тон: warm/formal/casual
    draft_content: Optional[str] = None  # Черновик
    current_stage: LetterStage = LetterStage.INITIAL
    letter_id: Optional[int] = None  # ID письма в БД

    def __post_init__(self):
        if self.key_points is None:
            self.key_points = []


class LetterWritingAssistant(Technique):
    """
    Multi-turn dialogue assistant for writing letters to children.

    Этапы:
    1. INITIAL - Приветствие и объяснение процесса
    2. GATHERING - Сбор информации (кому, цель, ключевые моменты)
    3. GENERATING - Генерация черновика с помощью OpenAI
    4. REVIEWING - Показ черновика пользователю
    5. EDITING - Редактирование по запросу
    6. FINALIZING - Финализация и сохранение
    """

    name = "Letter Writing Assistant"
    description = "Помощь в написании писем ребёнку"

    def __init__(self):
        """Initialize letter writing assistant."""
        super().__init__()
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
        """
        Apply letter writing assistance based on current stage.

        Args:
            user_message: User's message
            context: Conversation context with letter_context

        Returns:
            TechniqueResult with response and updated context
        """
        # Get or create letter context
        letter_ctx = context.get("letter_context")
        if not letter_ctx:
            letter_ctx = LetterContext()
            context["letter_context"] = letter_ctx
        elif isinstance(letter_ctx, dict):
            # Convert dict to LetterContext
            letter_ctx = LetterContext(**letter_ctx)
            context["letter_context"] = letter_ctx

        current_stage = letter_ctx.current_stage

        logger.info(
            "letter_writing_stage",
            stage=current_stage,
            recipient=letter_ctx.recipient
        )

        # Route to appropriate handler
        if current_stage == LetterStage.INITIAL:
            return await self._handle_initial(user_message, letter_ctx, context)
        elif current_stage == LetterStage.GATHERING:
            return await self._handle_gathering(user_message, letter_ctx, context)
        elif current_stage == LetterStage.GENERATING:
            return await self._handle_generating(user_message, letter_ctx, context)
        elif current_stage == LetterStage.REVIEWING:
            return await self._handle_reviewing(user_message, letter_ctx, context)
        elif current_stage == LetterStage.EDITING:
            return await self._handle_editing(user_message, letter_ctx, context)
        elif current_stage == LetterStage.FINALIZING:
            return await self._handle_finalizing(user_message, letter_ctx, context)

        # Default fallback
        return await self._handle_initial(user_message, letter_ctx, context)

    async def _handle_initial(
        self,
        user_message: str,
        letter_ctx: LetterContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle initial stage - explain process and start gathering info."""
        response = """📝 **Помощь в написании письма**

Я помогу вам написать письмо вашему ребёнку. Мы пройдём этот процесс вместе, шаг за шагом.

**Процесс:**
1️⃣ Соберём информацию о письме
2️⃣ Создадим черновик
3️⃣ Отредактируем его вместе
4️⃣ Финализируем письмо

**Давайте начнём:**
Кому вы хотите написать письмо? (Имя ребёнка)"""

        # Move to gathering stage
        letter_ctx.current_stage = LetterStage.GATHERING

        # Record that letter writing was started (for conversion tracking)
        metrics_collector = context.get("metrics_collector")
        user_state = context.get("user_state")
        if metrics_collector and user_state:
            await metrics_collector.record_letter_started(user_state.user_id)

        return TechniqueResult(
            success=True,
            response=response,
            metadata={
                "stage": "initial",
                "next_stage": "gathering"
            }
        )

    async def _handle_gathering(
        self,
        user_message: str,
        letter_ctx: LetterContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle gathering stage - collect letter details."""
        message_lower = user_message.lower()

        # Stage 1: Get recipient name
        if not letter_ctx.recipient:
            letter_ctx.recipient = user_message.strip()
            response = f"""Хорошо, письмо для **{letter_ctx.recipient}**.

Какова **главная цель** этого письма?
Например:
• Выразить любовь и поддержку
• Объяснить сложную ситуацию
• Поделиться воспоминаниями
• Рассказать о своих чувствах
• Договориться о встрече"""

            return TechniqueResult(
                success=True,
                response=response,
                metadata={"stage": "gathering", "step": "purpose"}
            )

        # Stage 2: Get purpose
        if not letter_ctx.purpose:
            letter_ctx.purpose = user_message.strip()
            response = f"""Понимаю, вы хотите: "{letter_ctx.purpose}"

Какие **ключевые моменты** вы хотели бы включить в письмо?
(Можете написать несколько пунктов, или "готово" если всё сказали)

Например:
• Как сильно вы скучаете
• Конкретные воспоминания
• Что вы хотите сказать
• Планы на будущее"""

            return TechniqueResult(
                success=True,
                response=response,
                metadata={"stage": "gathering", "step": "key_points"}
            )

        # Stage 3: Collect key points
        if "готово" not in message_lower and "достаточно" not in message_lower:
            # Add key point
            letter_ctx.key_points.append(user_message.strip())
            response = f"""✅ Добавлено: "{user_message.strip()}"

У вас пока **{len(letter_ctx.key_points)} пункт(ов)**.

Есть ещё что добавить? (или напишите "готово")"""

            return TechniqueResult(
                success=True,
                response=response,
                metadata={"stage": "gathering", "points_count": len(letter_ctx.key_points)}
            )

        # All info gathered - move to generation
        letter_ctx.current_stage = LetterStage.GENERATING

        response = f"""Отлично! У меня есть вся информация:

📌 **Кому:** {letter_ctx.recipient}
🎯 **Цель:** {letter_ctx.purpose}
📝 **Ключевые моменты:** {len(letter_ctx.key_points)} пункт(ов)

Сейчас я создам черновик письма. Минутку...

_Генерирую письмо..._"""

        # Generate draft
        draft = await self._generate_draft(letter_ctx, context)
        letter_ctx.draft_content = draft
        letter_ctx.current_stage = LetterStage.REVIEWING

        review_response = f"""{response}

---

**📄 ЧЕРНОВИК ПИСЬМА:**

{draft}

---

Что вы думаете об этом письме?
• "Отлично" - если всё устраивает
• Напишите, что хотите изменить/добавить
• "Переписать" - если хотите начать заново"""

        return TechniqueResult(
            success=True,
            response=review_response,
            metadata={
                "stage": "generating_complete",
                "next_stage": "reviewing",
                "draft_length": len(draft)
            }
        )

    async def _generate_draft(
        self,
        letter_ctx: LetterContext,
        context: Dict[str, Any]
    ) -> str:
        """Generate letter draft using OpenAI."""
        # Build prompt for letter generation
        key_points_text = "\n".join([f"- {point}" for point in letter_ctx.key_points])

        system_prompt = """Вы - чуткий помощник, помогающий родителям писать письма своим детям
в ситуациях родительского отчуждения. Ваша задача - создать искреннее, тёплое письмо,
которое выражает любовь и поддержку, не обвиняя других и не вызывая чувство вины у ребёнка.

Стиль:
- Искренний и тёплый
- Без обвинений других людей
- Фокус на любви к ребёнку
- Простой, понятный язык
- Подходящий для возраста ребёнка"""

        user_prompt = f"""Создай письмо с такими параметрами:

**Кому:** {letter_ctx.recipient}
**Цель:** {letter_ctx.purpose}

**Ключевые моменты:**
{key_points_text}

Создай тёплое, искреннее письмо. Оно должно быть не слишком длинным (200-400 слов).
"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = await self.llm.ainvoke(messages)
            draft = response.content.strip()

            logger.info("letter_draft_generated", length=len(draft))
            return draft

        except Exception as e:
            logger.error("letter_generation_failed", error=str(e))
            # Fallback draft
            return f"""Дорогой {letter_ctx.recipient},

Я очень скучаю по тебе и часто думаю о тебе.

{chr(10).join(letter_ctx.key_points)}

Ты всегда в моём сердце.

С любовью,
Твой родитель"""

    async def _handle_generating(
        self,
        user_message: str,
        letter_ctx: LetterContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle generating stage (transition state)."""
        # This should not be called - generation happens in gathering
        # But handle it gracefully
        return await self._handle_reviewing(user_message, letter_ctx, context)

    async def _handle_reviewing(
        self,
        user_message: str,
        letter_ctx: LetterContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle reviewing stage - user reviews draft."""
        message_lower = user_message.lower()

        # User is satisfied
        if any(word in message_lower for word in ["отлично", "хорошо", "подходит", "устраивает", "да"]):
            letter_ctx.current_stage = LetterStage.FINALIZING
            return await self._handle_finalizing(user_message, letter_ctx, context)

        # User wants to rewrite
        if "переписать" in message_lower or "заново" in message_lower:
            # Reset context
            letter_ctx.key_points = []
            letter_ctx.draft_content = None
            letter_ctx.current_stage = LetterStage.GATHERING

            response = """Хорошо, давайте начнём заново.

Какова **главная цель** этого письма?"""

            return TechniqueResult(
                success=True,
                response=response,
                metadata={"stage": "reviewing", "action": "restart"}
            )

        # User wants to edit
        letter_ctx.current_stage = LetterStage.EDITING
        letter_ctx.editing_request = user_message

        response = """Понял, сейчас внесу изменения...

_Редактирую письмо..._"""

        # Edit the draft
        edited_draft = await self._edit_draft(letter_ctx, user_message, context)
        letter_ctx.draft_content = edited_draft
        letter_ctx.current_stage = LetterStage.REVIEWING

        final_response = f"""{response}

---

**📄 ОБНОВЛЁННЫЙ ЧЕРНОВИК:**

{edited_draft}

---

Теперь лучше?
• "Отлично" - если всё устраивает
• Напишите, что ещё изменить
• "Переписать" - начать заново"""

        return TechniqueResult(
            success=True,
            response=final_response,
            metadata={
                "stage": "editing_complete",
                "next_stage": "reviewing"
            }
        )

    async def _edit_draft(
        self,
        letter_ctx: LetterContext,
        editing_request: str,
        context: Dict[str, Any]
    ) -> str:
        """Edit the draft based on user feedback."""
        system_prompt = """Вы - редактор писем. Ваша задача - внести изменения в письмо
на основе пожеланий автора, сохраняя тёплый и искренний тон."""

        user_prompt = f"""Вот текущий черновик письма:

{letter_ctx.draft_content}

Пользователь просит:
{editing_request}

Внеси изменения в письмо согласно этому запросу."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = await self.llm.ainvoke(messages)
            edited = response.content.strip()

            logger.info("letter_edited", changes_requested=editing_request[:50])
            return edited

        except Exception as e:
            logger.error("letter_editing_failed", error=str(e))
            # Return original draft if editing fails
            return letter_ctx.draft_content

    async def _handle_editing(
        self,
        user_message: str,
        letter_ctx: LetterContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle editing stage (transition state)."""
        # Editing happens in reviewing stage
        return await self._handle_reviewing(user_message, letter_ctx, context)

    async def _handle_finalizing(
        self,
        user_message: str,
        letter_ctx: LetterContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle finalizing stage - save and complete."""

        # Save to database if available
        db = context.get("db")
        user_state = context.get("user_state")

        if db and user_state:
            try:
                # Create or update letter in database
                if letter_ctx.letter_id:
                    # Update existing letter
                    await db.save_letter_draft(
                        letter_id=letter_ctx.letter_id,
                        draft_content=letter_ctx.draft_content,
                        metadata={"status": "completed"}
                    )
                    logger.info("letter_updated", letter_id=letter_ctx.letter_id)
                else:
                    # Create new letter
                    letter = await db.create_letter(
                        user_id=user_state.user_id,
                        title=f"Письмо для {letter_ctx.recipient}",
                        recipient_role=letter_ctx.recipient,
                        purpose=letter_ctx.purpose,
                        letter_type="parental_alienation",
                        draft_content=letter_ctx.draft_content,
                        communication_style=letter_ctx.tone,
                        status="completed"
                    )
                    letter_ctx.letter_id = letter.id
                    logger.info("letter_created", letter_id=letter.id)

                    # Record letter completion for conversion tracking
                    metrics_collector = context.get("metrics_collector")
                    if metrics_collector:
                        await metrics_collector.record_letter_completed(user_state.user_id)

            except Exception as e:
                logger.error("letter_save_failed", error=str(e))
                # Continue even if save fails

        response = f"""✅ **Письмо готово!**

**Кому:** {letter_ctx.recipient}

Ваше письмо сохранено. Вы можете:
• Скопировать его и отправить
• Вернуться к редактированию позже (команда /letters)
• Написать ещё одно письмо (/letter)

---

**📄 ФИНАЛЬНАЯ ВЕРСИЯ:**

{letter_ctx.draft_content}

---

Это письмо написано с любовью. Надеюсь, оно поможет вам выразить свои чувства.

💙 Желаю вам всего самого лучшего!"""

        # Mark as complete
        letter_ctx.current_stage = LetterStage.FINALIZING

        return TechniqueResult(
            success=True,
            response=response,
            follow_up="Хотите написать ещё одно письмо или продолжить разговор?",
            metadata={
                "stage": "finalized",
                "recipient": letter_ctx.recipient,
                "letter_completed": True,
                "letter_id": letter_ctx.letter_id
            }
        )
