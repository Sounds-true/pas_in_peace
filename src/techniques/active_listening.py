"""Active listening technique with reflective responses."""

from typing import Dict, Any
from openai import AsyncOpenAI
from src.techniques.base import Technique, TechniqueResult, TechniqueCategory, DistressLevel
from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


class ActiveListening(Technique):
    """
    Active listening with reflection.

    Demonstrates understanding by reflecting back what the user has expressed,
    helping them feel heard and understood.
    """

    def __init__(self):
        """Initialize active listening technique."""
        super().__init__()
        self.name = "Active Listening"
        self.category = TechniqueCategory.ACTIVE_LISTENING
        self.description = (
            "Активное слушание с отражением — помогает вам почувствовать, "
            "что вас действительно слышат и понимают."
        )
        self.suitable_for_distress = [
            DistressLevel.LOW,
            DistressLevel.MODERATE,
            DistressLevel.HIGH
        ]

        # Reflective listening stems in Russian
        self.reflection_stems = [
            "Я слышу, что вы чувствуете",
            "Похоже, вы переживаете",
            "Звучит так, будто",
            "Если я правильно понимаю",
            "Вы говорите о том, что",
            "Для вас важно",
            "Вас беспокоит"
        ]

        # Clarifying questions
        self.clarifying_questions = [
            "Расскажите мне больше об этом?",
            "Что вы чувствовали в тот момент?",
            "Как это повлияло на вас?",
            "Что было самым сложным в этой ситуации?",
            "Как вы справляетесь с этим сейчас?"
        ]

    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """
        Apply active listening with reflection using LLM for contextual responses.

        Args:
            user_message: User's message
            context: Context including emotion, distress level, etc.

        Returns:
            TechniqueResult with reflective response
        """
        primary_emotion = context.get("primary_emotion", "")
        distress_level = context.get("distress_level", "moderate")

        # Extract key themes from user message
        themes = self._extract_themes(user_message, primary_emotion)

        # Use LLM to generate empathetic, contextual response
        try:
            response = await self._generate_llm_response(
                user_message,
                primary_emotion,
                distress_level,
                themes,
                context  # Pass full context including history
            )
        except Exception as e:
            logger.error("llm_response_failed", error=str(e))
            # Fallback to template-based response
            reflection = self._build_reflection(themes, primary_emotion)
            clarifying_q = self._get_appropriate_question(distress_level, themes)
            response = f"{reflection}\n\n{clarifying_q}\n\nЯ здесь, чтобы слушать. Нет спешки."

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=None,  # LLM response is complete
            recommended_next_step="continue_listening",
            metadata={
                "technique": "active_listening",
                "themes_detected": themes,
                "emotion": primary_emotion,
                "used_llm": True
            }
        )

    async def _generate_llm_response(
        self,
        user_message: str,
        emotion: str,
        distress_level: str,
        themes: list[str],
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate empathetic response using OpenAI API with conversation history.

        Args:
            user_message: User's message
            emotion: Detected emotion
            distress_level: Level of distress
            themes: Detected themes
            context: Full context including message history

        Returns:
            Generated empathetic response
        """
        client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())

        # Get message history from context
        user_state = context.get("user_state") if context else None
        message_count = user_state.messages_count if user_state else 0

        # Determine dialogue stage
        if message_count <= 2:
            stage = "начало диалога - активное слушание и валидация"
        elif message_count <= 5:
            stage = "понимание ситуации - сбор деталей"
        else:
            stage = "переход к действиям - предложите письмо или упражнение"

        # Build system prompt with dialogue progression
        system_prompt = f"""Вы — эмпатичный психотерапевт для родителей, переживающих родительское отчуждение. Вы НЕ робот, а живой человек.

ТЕКУЩАЯ СИТУАЦИЯ:
- Сообщение #{message_count + 1} в диалоге
- Этап: {stage}
- Эмоция: {emotion}
- Уровень дистресса: {distress_level}
- Темы в сообщении: {', '.join(themes) if themes else 'общие переживания'}

СТРАТЕГИЯ ПО ЭТАПАМ:

📍 Сообщения 1-2: Активное слушание
   - Отразите чувства простыми словами
   - Один естественный вопрос для понимания
   - БЕЗ шаблонных фраз типа "я здесь чтобы поддержать"

📍 Сообщения 3-5: Глубокое понимание
   - Суммируйте услышанное своими словами
   - Уточните детали ситуации (сколько времени, что пробовали)
   - Начните видеть паттерны

📍 Сообщения 6+: Мягкий переход к действиям
   - Кратко резюмируйте ситуацию (1-2 предложения)
   - Предложите конкретный следующий шаг:
     * "Возможно, имеет смысл написать письмо вашему сыну/дочери?"
     * "Хотите попробовать упражнение для работы с этими чувствами?"
     * "Давайте вместе подумаем о ваших целях?"

ВАЖНЫЕ ПРИНЦИПЫ:
✓ Говорите как живой человек, НЕ как робот
✓ Варьируйте начало ответов (не "я слышу", "я вижу" каждый раз)
✓ БЕЗ шаблонов вроде "я здесь чтобы...", "знайте что..."
✓ НЕ давайте юридических советов
✓ НЕ осуждайте другого родителя, даже если клиент это делает
✓ Признавайте боль, но постепенно ведите к конструктивным действиям

ФОРМАТ:
- 2-4 предложения максимум
- Естественный, живой язык
- Одно действие (вопрос ИЛИ предложение, не оба сразу)"""

        try:
            # Build messages with history
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history (last 10 messages for context)
            if user_state and hasattr(user_state, 'message_history'):
                for msg in user_state.message_history[-10:]:
                    if hasattr(msg, 'type'):
                        if msg.type == 'human':
                            messages.append({"role": "user", "content": msg.content})
                        elif msg.type == 'ai':
                            messages.append({"role": "assistant", "content": msg.content})

            # Add current message
            messages.append({"role": "user", "content": user_message})

            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=400,
                temperature=0.8,  # Increased for more variability
                presence_penalty=0.6,  # Reduce repetition
                frequency_penalty=0.6   # Reduce repetition
            )

            response_text = response.choices[0].message.content
            logger.info("llm_response_generated",
                       message_length=len(response_text),
                       message_count=message_count,
                       stage=stage)
            return response_text.strip()

        except Exception as e:
            logger.error("openai_api_error", error=str(e))
            raise

    def _extract_themes(self, message: str, emotion: str) -> list[str]:
        """
        Extract key themes from user message.

        Args:
            message: User's message
            emotion: Detected emotion

        Returns:
            List of detected themes
        """
        themes = []
        message_lower = message.lower()

        # PA-specific themes
        theme_keywords = {
            "contact_denied": ["не дают", "запрещают", "не пускают", "не разрешают", "don't allow"],
            "child_refuses": ["не хочет", "отказывается", "избегает", "refuses", "doesn't want"],
            "manipulation": ["настраивает", "манипулирует", "врёт", "manipulates", "lies"],
            "court": ["суд", "судья", "lawyer", "юрист", "court"],
            "alienator": ["бывший", "бывшая", "ex", "другой родитель"],
            "missing_child": ["скучаю", "тоска", "хочу видеть", "miss", "long for"],
            "guilt": ["виноват", "вина", "моя ошибка", "guilt", "my fault"],
            "helpless": ["ничего не могу", "бессилен", "helpless", "powerless"],
            "hope": ["надежда", "надеюсь", "может быть", "hope", "maybe"]
        }

        for theme, keywords in theme_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                themes.append(theme)

        return themes if themes else ["general_distress"]

    def _build_reflection(self, themes: list[str], emotion: str) -> str:
        """
        Build reflective statement based on themes and emotion.

        Args:
            themes: Detected themes
            emotion: Primary emotion

        Returns:
            Reflective statement
        """
        # Theme-specific reflections
        theme_reflections = {
            "contact_denied": "Я слышу, что вам не дают возможности общаться с ребёнком. "
                             "Это невероятно болезненная ситуация.",

            "child_refuses": "Похоже, ребёнок сам отказывается от контакта. "
                            "Это ранит особенно сильно, когда это исходит от самого ребёнка.",

            "manipulation": "Звучит так, будто вы чувствуете, что ситуацией манипулируют. "
                           "Это добавляет боли к и без того сложной ситуации.",

            "court": "Я слышу, что вы имеете дело с юридической системой. "
                    "Это может быть стрессовым и overwhelming.",

            "missing_child": "Ваша тоска по ребёнку очевидна. "
                            "Эта пустота и желание быть рядом — показатель вашей любви.",

            "guilt": "Вы берёте на себя ответственность и анализируете свои действия. "
                    "Это показывает вашу заботу, но важно быть справедливым к себе.",

            "helpless": "Чувство бессилия в этой ситуации понятно. "
                       "Вы столкнулись с чем-то, что трудно контролировать.",

            "hope": "Я слышу, что даже в этой сложной ситуации вы сохраняете надежду. "
                   "Это требует силы."
        }

        # Emotion-based reflection if no specific themes
        emotion_reflections = {
            "grief": "Я слышу глубокую боль в ваших словах.",
            "anger": "Я слышу вашу фрустрацию и гнев по поводу этой ситуации.",
            "sadness": "Я слышу печаль и тоску в том, чем вы делитесь.",
            "fear": "Я слышу беспокойство и страх за будущее.",
            "anxiety": "Я слышу тревогу в ваших словах."
        }

        # Build reflection from themes
        if themes and themes[0] in theme_reflections:
            return theme_reflections[themes[0]]
        elif emotion in emotion_reflections:
            return emotion_reflections[emotion]
        else:
            return "Я слышу, как тяжело вам сейчас. Спасибо, что поделились этим."

    def _get_appropriate_question(
        self,
        distress_level: str,
        themes: list[str]
    ) -> str:
        """
        Get appropriate clarifying question based on context.

        Args:
            distress_level: Current distress level
            themes: Detected themes

        Returns:
            Clarifying question
        """
        # For high distress, gentler questions
        if distress_level in ["high", "crisis"]:
            return "Как вы справляетесь с этим прямо сейчас?"

        # Theme-specific questions
        theme_questions = {
            "contact_denied": "Как давно это продолжается? Что вы уже пробовали?",
            "child_refuses": "Как ребёнок выражает это? Было ли это резкое изменение?",
            "manipulation": "Какие конкретные ситуации заставляют вас так думать?",
            "court": "На какой стадии сейчас юридический процесс?",
            "missing_child": "Что больше всего вам не хватает в общении с ребёнком?",
            "guilt": "Что конкретно вы считаете своей ошибкой?",
            "helpless": "Что бы вам помогло почувствовать хоть немного контроля?",
            "hope": "Что поддерживает вашу надежду?"
        }

        if themes and themes[0] in theme_questions:
            return theme_questions[themes[0]]

        return "Расскажите мне больше — что для вас сейчас самое важное?"

    def is_appropriate(
        self,
        distress_level: DistressLevel,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Active listening is appropriate for most levels,
        but less so for crisis (where action is needed).
        """
        return distress_level != DistressLevel.CRISIS
