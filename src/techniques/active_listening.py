"""Active listening technique with reflective responses."""

from typing import Dict, Any
from src.techniques.base import Technique, TechniqueResult, TechniqueCategory, DistressLevel


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
        Apply active listening with reflection.

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

        # Build reflective response
        reflection = self._build_reflection(themes, primary_emotion)

        # Add clarifying question
        clarifying_q = self._get_appropriate_question(distress_level, themes)

        response = f"""
{reflection}

{clarifying_q}

Я здесь, чтобы слушать. Нет спешки.
        """.strip()

        return TechniqueResult(
            success=True,
            response=response,
            follow_up="Продолжайте делиться, если хотите. Ваша история важна.",
            recommended_next_step="continue_listening",
            metadata={
                "technique": "active_listening",
                "themes_detected": themes,
                "emotion": primary_emotion
            }
        )

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
