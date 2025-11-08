"""Goal Tracking Technique for setting and monitoring user goals."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from src.techniques.base import Technique, TechniqueResult
from src.core.logger import get_logger

logger = get_logger(__name__)


class GoalStage(Enum):
    """Stages of goal tracking dialogue."""
    INITIAL = "initial"
    COLLECTING = "collecting"  # Gather goal details
    CLARIFYING = "clarifying"  # Make it SMART
    CONFIRMING = "confirming"  # Confirm and save
    COMPLETED = "completed"


@dataclass
class GoalContext:
    """Context for goal tracking dialogue."""
    current_stage: GoalStage = GoalStage.INITIAL

    # Goal details
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

    # SMART criteria
    specific: Optional[str] = None
    measurable: Optional[str] = None
    timeframe: Optional[str] = None

    # Milestones
    milestones: List[str] = field(default_factory=list)

    # Meta
    goal_id: Optional[int] = None
    attempts: int = 0


class GoalTrackingAssistant(Technique):
    """
    Interactive goal setting and tracking technique.

    Helps users define SMART goals with milestones and tracks progress over time.

    Stages:
    1. INITIAL - Welcome and explain goal setting
    2. COLLECTING - Gather basic goal information
    3. CLARIFYING - Make goal SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
    4. CONFIRMING - Review and confirm goal
    5. COMPLETED - Goal saved
    """

    def __init__(self):
        """Initialize goal tracking assistant."""
        super().__init__()
        self.name = "Goal Tracking"
        self.description = "Помощь в постановке и отслеживании целей"

        # Predefined goal categories
        self.goal_categories = {
            "communication": "Общение с ребёнком",
            "emotional_regulation": "Управление эмоциями",
            "self_care": "Забота о себе",
            "legal": "Юридические вопросы",
            "documentation": "Документирование",
            "relationships": "Отношения"
        }

    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Apply goal tracking technique."""
        # Get or create goal context
        goal_ctx = context.get("goal_context")
        if not goal_ctx:
            goal_ctx = GoalContext()
            context["goal_context"] = goal_ctx

        logger.info(
            "goal_tracking_stage",
            stage=goal_ctx.current_stage.value,
            title=goal_ctx.title
        )

        # Route to appropriate handler
        if goal_ctx.current_stage == GoalStage.INITIAL:
            return await self._handle_initial(user_message, goal_ctx, context)
        elif goal_ctx.current_stage == GoalStage.COLLECTING:
            return await self._handle_collecting(user_message, goal_ctx, context)
        elif goal_ctx.current_stage == GoalStage.CLARIFYING:
            return await self._handle_clarifying(user_message, goal_ctx, context)
        elif goal_ctx.current_stage == GoalStage.CONFIRMING:
            return await self._handle_confirming(user_message, goal_ctx, context)
        else:
            # Default fallback
            return await self._handle_initial(user_message, goal_ctx, context)

    async def _handle_initial(
        self,
        user_message: str,
        goal_ctx: GoalContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle initial stage - introduce goal setting."""
        response = """🎯 **Постановка целей**

Я помогу вам определить цель и разработать план её достижения.

Это поможет вам:
• Сосредоточиться на конкретных шагах
• Отслеживать прогресс
• Чувствовать контроль над ситуацией

Давайте начнём! **Что бы вы хотели достичь?**

Например:
• "Восстановить регулярное общение с ребёнком"
• "Научиться справляться с тревогой"
• "Собрать документы для суда"
"""

        goal_ctx.current_stage = GoalStage.COLLECTING

        return TechniqueResult(
            success=True,
            response=response,
            metadata={
                "stage": "initial",
                "goal_tracking_active": True
            }
        )

    async def _handle_collecting(
        self,
        user_message: str,
        goal_ctx: GoalContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle collecting stage - gather goal details."""
        message = user_message.strip()

        # First time - get goal title
        if not goal_ctx.title:
            goal_ctx.title = message

            # Try to categorize
            goal_ctx.category = self._categorize_goal(message)

            response = f"""Отлично! Ваша цель: **"{goal_ctx.title}"**

Теперь давайте сделаем её более конкретной.

**Опишите подробнее:**
• Что конкретно вы хотите сделать?
• Как вы поймёте, что цель достигнута?
• Какой результат для вас будет успехом?"""

            return TechniqueResult(
                success=True,
                response=response,
                metadata={"stage": "collecting", "goal_title": goal_ctx.title}
            )

        # Second time - get description
        elif not goal_ctx.description:
            goal_ctx.description = message
            goal_ctx.current_stage = GoalStage.CLARIFYING

            return await self._handle_clarifying("", goal_ctx, context)

        return TechniqueResult(
            success=True,
            response="Пожалуйста, опишите вашу цель подробнее.",
            metadata={"stage": "collecting"}
        )

    async def _handle_clarifying(
        self,
        user_message: str,
        goal_ctx: GoalContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle clarifying stage - make goal SMART."""

        # Ask for specifics
        if not goal_ctx.specific:
            # Generate SMART suggestions
            suggestions = self._generate_smart_suggestions(goal_ctx)

            response = f"""📋 **Давайте сделаем цель более конкретной**

Ваша цель: "{goal_ctx.title}"

Чтобы цель была достижимой, важно определить:

**1. Конкретные действия:**
{suggestions['specific']}

**2. Как измерить прогресс:**
{suggestions['measurable']}

**3. Временные рамки:**
Через сколько времени вы хотите достичь этой цели?
• Неделя
• Месяц
• 3 месяца
• 6 месяцев

Напишите выбранный срок или свой вариант."""

            goal_ctx.specific = goal_ctx.description

            return TechniqueResult(
                success=True,
                response=response,
                metadata={"stage": "clarifying_timeframe"}
            )

        # Get timeframe
        if not goal_ctx.timeframe:
            goal_ctx.timeframe = self._parse_timeframe(user_message)

            # Move to milestones
            response = f"""⏱️ Отлично! Срок: **{goal_ctx.timeframe}**

Теперь давайте разобьём цель на небольшие шаги.

**Какие промежуточные результаты помогут достичь цели?**

Например, если цель "Восстановить общение с ребёнком":
• Написать письмо
• Связаться через посредника
• Договориться о звонке

Напишите 2-3 шага, или напишите "готово" чтобы продолжить."""

            return TechniqueResult(
                success=True,
                response=response,
                metadata={"stage": "clarifying_milestones"}
            )

        # Collect milestones
        message = user_message.strip().lower()
        if message not in ["готово", "достаточно", "хватит", "продолжить"]:
            # Add milestone
            goal_ctx.milestones.append(user_message.strip())

            if len(goal_ctx.milestones) < 3:
                return TechniqueResult(
                    success=True,
                    response=f"✓ Шаг {len(goal_ctx.milestones)} добавлен. Ещё один шаг? (или напишите 'готово')",
                    metadata={"stage": "clarifying_milestones", "milestones_count": len(goal_ctx.milestones)}
                )

        # Move to confirmation
        goal_ctx.current_stage = GoalStage.CONFIRMING
        return await self._handle_confirming("", goal_ctx, context)

    async def _handle_confirming(
        self,
        user_message: str,
        goal_ctx: GoalContext,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Handle confirming stage - review and save goal."""

        # Show summary
        milestones_text = "\n".join([f"   {i+1}. {m}" for i, m in enumerate(goal_ctx.milestones)])

        response = f"""✅ **Ваша цель готова!**

📝 **Цель:** {goal_ctx.title}

📋 **Описание:** {goal_ctx.description}

⏱️ **Срок:** {goal_ctx.timeframe}

🎯 **Промежуточные шаги:**
{milestones_text or "   (не указаны)"}

---

Сохранить эту цель? (да/нет)"""

        message = user_message.strip().lower()

        # If user confirms
        if message in ["да", "yes", "сохранить", "хорошо", "ok", "+"]:
            # Save to database
            db = context.get("db")
            user_state = context.get("user_state")

            if db and user_state:
                try:
                    # Calculate target date
                    target_date = self._calculate_target_date(goal_ctx.timeframe)

                    # Create goal
                    goal = await db.create_goal(
                        user_id=user_state.user_id,
                        title=goal_ctx.title,
                        description=goal_ctx.description,
                        category=goal_ctx.category or "personal"
                    )

                    # Update with SMART details
                    from src.storage.database import DatabaseManager
                    async with db.session() as db_session:
                        from sqlalchemy import select
                        from src.storage.models import Goal

                        stmt = select(Goal).where(Goal.id == goal.id)
                        result = await db_session.execute(stmt)
                        goal_obj = result.scalar_one_or_none()

                        if goal_obj:
                            goal_obj.specific = goal_ctx.specific
                            goal_obj.measurable = goal_ctx.description
                            goal_obj.time_bound = goal_ctx.timeframe
                            goal_obj.milestones = goal_ctx.milestones
                            goal_obj.target_date = target_date

                            await db_session.commit()

                    goal_ctx.goal_id = goal.id
                    logger.info("goal_created", goal_id=goal.id, user_id=user_state.user_id)

                    response = f"""🎉 **Цель сохранена!**

Я буду периодически спрашивать о вашем прогрессе.

Вы можете в любой момент:
• Посмотреть цели: /goals
• Обновить прогресс: "обновить цель"

💙 Удачи в достижении вашей цели!"""

                except Exception as e:
                    logger.error("goal_save_failed", error=str(e))
                    response = f"""✅ Цель готова!

(Не удалось сохранить в базу данных, но вы можете вернуться к ней позже)

Продолжим разговор?"""
            else:
                response = f"""✅ Цель готова!

Продолжим разговор?"""

            goal_ctx.current_stage = GoalStage.COMPLETED

            return TechniqueResult(
                success=True,
                response=response,
                metadata={
                    "stage": "completed",
                    "goal_id": goal_ctx.goal_id,
                    "goal_created": True
                }
            )

        # Still showing confirmation
        if not message or message == "":
            return TechniqueResult(
                success=True,
                response=response,
                metadata={"stage": "confirming"}
            )

        # User declined
        return TechniqueResult(
            success=True,
            response="Хорошо, мы можем поработать над целью позже. Продолжим разговор?",
            metadata={"stage": "cancelled"}
        )

    def _categorize_goal(self, goal_text: str) -> str:
        """Automatically categorize goal based on keywords."""
        text_lower = goal_text.lower()

        if any(word in text_lower for word in ["общение", "звонок", "встреча", "письмо", "связь"]):
            return "communication"
        elif any(word in text_lower for word in ["эмоц", "тревог", "стресс", "спокой", "чувств"]):
            return "emotional_regulation"
        elif any(word in text_lower for word in ["забота", "отдых", "здоровье", "сон", "спорт"]):
            return "self_care"
        elif any(word in text_lower for word in ["суд", "юрист", "документ", "адвокат", "право"]):
            return "legal"
        elif any(word in text_lower for word in ["запис", "дневник", "документ", "фиксир"]):
            return "documentation"
        else:
            return "relationships"

    def _generate_smart_suggestions(self, goal_ctx: GoalContext) -> Dict[str, str]:
        """Generate SMART suggestions based on goal."""
        title_lower = (goal_ctx.title or "").lower()

        if "общение" in title_lower or "связь" in title_lower:
            specific = "• Написать письмо ребёнку\n• Позвонить через посредника\n• Отправить сообщение в соцсетях"
            measurable = "• Количество попыток связаться\n• Длительность разговора\n• Ответ получен/не получен"
        elif "эмоц" in title_lower or "тревог" in title_lower:
            specific = "• Практиковать дыхательные упражнения\n• Вести дневник эмоций\n• Обратиться к психологу"
            measurable = "• Уровень тревоги по шкале 1-10\n• Количество практик в неделю\n• Изменение самочувствия"
        elif "документ" in title_lower:
            specific = "• Собрать выписки\n• Сделать фотокопии\n• Систематизировать файлы"
            measurable = "• Количество собранных документов\n• Процент готовности пакета\n• Дата завершения"
        else:
            specific = "• Определите конкретные действия\n• Распишите последовательность шагов"
            measurable = "• Как вы поймёте, что цель достигнута?\n• Какие показатели будете отслеживать?"

        return {
            "specific": specific,
            "measurable": measurable
        }

    def _parse_timeframe(self, message: str) -> str:
        """Parse timeframe from user message."""
        text_lower = message.lower()

        if "неделя" in text_lower or "week" in text_lower:
            return "1 неделя"
        elif "месяц" in text_lower and "3" not in text_lower and "6" not in text_lower:
            return "1 месяц"
        elif "3" in text_lower and "месяц" in text_lower:
            return "3 месяца"
        elif "6" in text_lower or "полгода" in text_lower:
            return "6 месяцев"
        elif "год" in text_lower:
            return "1 год"
        else:
            # Try to extract number
            import re
            numbers = re.findall(r'\d+', message)
            if numbers:
                return f"{numbers[0]} дней"
            return "1 месяц"  # Default

    def _calculate_target_date(self, timeframe: str) -> datetime:
        """Calculate target date from timeframe string."""
        from datetime import timedelta

        timeframe_lower = timeframe.lower()

        if "неделя" in timeframe_lower or "week" in timeframe_lower:
            import re
            weeks = re.findall(r'\d+', timeframe)
            weeks = int(weeks[0]) if weeks else 1
            return datetime.utcnow() + timedelta(weeks=weeks)
        elif "месяц" in timeframe_lower or "month" in timeframe_lower:
            import re
            months = re.findall(r'\d+', timeframe)
            months = int(months[0]) if months else 1
            return datetime.utcnow() + timedelta(days=30 * months)
        elif "год" in timeframe_lower or "year" in timeframe_lower:
            return datetime.utcnow() + timedelta(days=365)
        else:
            # Default to 30 days
            return datetime.utcnow() + timedelta(days=30)
