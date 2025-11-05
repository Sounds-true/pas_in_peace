"""Validation and empathetic response techniques."""

from typing import Dict, Any
from src.techniques.base import Technique, TechniqueResult, TechniqueCategory, DistressLevel


class ValidationTechnique(Technique):
    """
    Validation technique - acknowledging and validating emotions.

    Provides empathetic responses that validate the user's experience,
    which is crucial for parents experiencing parental alienation.
    """

    def __init__(self):
        """Initialize validation technique."""
        super().__init__()
        self.name = "Emotional Validation"
        self.category = TechniqueCategory.VALIDATION
        self.description = (
            "Признание и валидация ваших чувств и переживаний. "
            "Помогает почувствовать, что вас слышат и понимают."
        )
        self.suitable_for_distress = [
            DistressLevel.LOW,
            DistressLevel.MODERATE,
            DistressLevel.HIGH,
            DistressLevel.CRISIS
        ]

        # Emotion-specific validation responses (for PA context)
        self.validation_templates = {
            "grief": {
                "validation": "То, что вы чувствуете горе и потерю — совершенно естественно. "
                             "Отчуждение от ребёнка — это одна из самых болезненных ситуаций, "
                             "которые может пережить родитель.",
                "normalize": "Многие родители в вашей ситуации описывают похожие чувства утраты. "
                            "Ваши эмоции — нормальная реакция на ненормальную ситуацию."
            },
            "anger": {
                "validation": "Ваш гнев понятен. Вы столкнулись с несправедливостью, "
                             "которая затрагивает самое важное — ваши отношения с ребёнком.",
                "normalize": "Гнев — это естественная реакция на то, что вас лишили возможности "
                            "быть родителем. Важно признать этот гнев и найти конструктивные способы с ним справляться."
            },
            "sadness": {
                "validation": "Ваша грусть и тоска по ребёнку совершенно понятны. "
                             "Это показывает глубину вашей любви и привязанности.",
                "normalize": "Грусть — это часть процесса. Позвольте себе чувствовать её, "
                            "но знайте, что многие родители находят способы справиться с этой болью."
            },
            "fear": {
                "validation": "Ваш страх за ребёнка и за будущее ваших отношений абсолютно обоснован. "
                             "Неопределённость пугает, особенно когда речь о любимом человеке.",
                "normalize": "Страх — это сигнал того, что вам важно. "
                            "Важно услышать этот страх, но не позволить ему парализовать вас."
            },
            "guilt": {
                "validation": "Чувство вины часто возникает у заботливых родителей. "
                             "Вы анализируете свои действия, потому что вам не всё равно.",
                "normalize": "Но важно помнить: отчуждение — это не результат плохого родительства. "
                            "Это сложная ситуация, в которой задействовано много факторов, часто вне вашего контроля."
            },
            "helplessness": {
                "validation": "Чувство беспомощности в этой ситуации понятно. "
                             "Вы столкнулись с ситуацией, где многое не в ваших руках.",
                "normalize": "Многие родители чувствуют себя так же. "
                            "Но даже в условиях ограниченного контроля есть шаги, которые вы можете предпринять."
            },
            "loneliness": {
                "validation": "Чувство одиночества в этой ситуации очень реально. "
                             "Не все понимают, через что вы проходите.",
                "normalize": "Знайте, что вы не одиноки. Тысячи родителей переживают подобное. "
                            "Ваши чувства валидны, и есть люди, которые понимают."
            },
            "neutral": {
                "validation": "Я слышу вас и понимаю, насколько это сложно для вас.",
                "normalize": "Ваши переживания важны, и вы имеете право на все свои чувства."
            }
        }

    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """
        Apply validation technique based on detected emotion.

        Args:
            user_message: User's message
            context: Context including primary emotion, distress level, etc.

        Returns:
            TechniqueResult with validation response
        """
        primary_emotion = context.get("primary_emotion", "neutral")
        distress_level = context.get("distress_level", "moderate")

        # Get validation template for detected emotion
        validation_data = self.validation_templates.get(
            primary_emotion,
            self.validation_templates["neutral"]
        )

        # Build validation response
        validation_part = validation_data["validation"]
        normalize_part = validation_data["normalize"]

        # Add context-specific elements for PA
        pa_specific = self._get_pa_specific_validation(primary_emotion)

        response = f"""
{validation_part}

{normalize_part}

{pa_specific}

Вы делаете всё возможное в невероятно сложной ситуации. Ваша любовь к ребёнку очевидна.
        """.strip()

        # Determine follow-up based on distress
        if distress_level in ["high", "crisis"]:
            follow_up = (
                "Прямо сейчас важнее всего ваше благополучие. "
                "Хотели бы вы попробовать упражнение для успокоения, "
                "или вам нужно просто выговориться?"
            )
            recommended_next = "grounding_or_listening"
        else:
            follow_up = (
                "Как вы себя чувствуете после того, как поделились этим? "
                "Хотите продолжить разговор об этих чувствах или перейти к конкретным шагам?"
            )
            recommended_next = "explore_or_action"

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=follow_up,
            recommended_next_step=recommended_next,
            metadata={
                "technique": "validation",
                "emotion": primary_emotion,
                "distress_level": distress_level
            }
        )

    def _get_pa_specific_validation(self, emotion: str) -> str:
        """
        Get PA-specific validation message.

        Args:
            emotion: Primary emotion

        Returns:
            PA-specific validation text
        """
        pa_messages = {
            "grief": "Отчуждение от ребёнка — это неоднозначная потеря. "
                    "Ребёнок жив, но связь нарушена. Это особенно тяжело.",

            "anger": "Ваш гнев может быть направляющей силой — помочь вам защищать свои права "
                    "и границы. Главное — найти конструктивные пути его выражения.",

            "guilt": "Родительское отчуждение часто используется как инструмент манипуляции. "
                   "Важно различать реальную ответственность и навязанную вину.",

            "fear": "Хотя будущее неопределённо, факт в том, что вы продолжаете заботиться. "
                   "Это уже имеет значение, даже если ребёнок пока этого не видит.",

            "helplessness": "Хотя вы не можете контролировать всё, вы можете контролировать: "
                           "свою реакцию, свои действия, своё самопомощь и подготовку к воссоединению.",

            "loneliness": "Многие родители в ситуации отчуждения чувствуют себя изолированными. "
                         "Но есть сообщества поддержки и ресурсы, где вас понимают.",

            "sadness": "Ваша печаль — это свидетельство вашей любви. "
                      "Сохранение этой любви, несмотря на боль, требует огромной силы."
        }

        return pa_messages.get(emotion, "")

    def is_appropriate(
        self,
        distress_level: DistressLevel,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Validation is appropriate for all distress levels.
        It's often the first step before other techniques.
        """
        return True  # Always appropriate
