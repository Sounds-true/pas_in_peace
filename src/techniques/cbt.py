"""Cognitive Behavioral Therapy (CBT) techniques."""

from typing import Dict, Any
from src.techniques.base import Technique, TechniqueResult, TechniqueCategory, DistressLevel


class CBTReframing(Technique):
    """
    Cognitive Reframing technique from CBT.

    Helps users identify and challenge negative automatic thoughts,
    replacing them with more balanced perspectives.
    """

    def __init__(self):
        """Initialize CBT reframing technique."""
        super().__init__()
        self.name = "Cognitive Reframing"
        self.category = TechniqueCategory.CBT
        self.description = (
            "Помогает выявить и переосмыслить негативные автоматические мысли, "
            "заменяя их более сбалансированными взглядами на ситуацию."
        )
        self.suitable_for_distress = [
            DistressLevel.LOW,
            DistressLevel.MODERATE,
            DistressLevel.HIGH
        ]

        # Common cognitive distortions in parental alienation context
        self.distortions = {
            "catastrophizing": {
                "pattern": ["никогда", "всегда", "навсегда", "never", "always", "forever"],
                "reframe": "Давайте посмотрим на это по-другому. Хотя сейчас ситуация кажется постоянной, "
                          "многие родители в подобных обстоятельствах со временем восстанавливали отношения с детьми. "
                          "Что может быть первым маленьким шагом?"
            },
            "all_or_nothing": {
                "pattern": ["полностью", "совсем", "completely", "totally"],
                "reframe": "Я слышу, что вы чувствуете, будто потеряли всё. "
                          "Но давайте подумаем: есть ли хоть что-то, что вы ещё можете контролировать в этой ситуации? "
                          "Может быть, ваша забота о ребёнке, даже на расстоянии?"
            },
            "personalization": {
                "pattern": ["моя вина", "я виноват", "my fault", "i'm to blame"],
                "reframe": "Вы берёте на себя много ответственности. "
                          "Отчуждение — это сложная ситуация с участием многих факторов. "
                          "Вместо самообвинения, давайте сосредоточимся на том, что вы можете сделать сейчас."
            },
            "mind_reading": {
                "pattern": ["он думает", "она считает", "they think", "he believes"],
                "reframe": "Вы предполагаете, что знаете, что думает другой человек. "
                          "Как вы можете быть уверены? Возможно ли, что есть другое объяснение их поведению?"
            }
        }

    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """
        Apply cognitive reframing to user's message.

        Args:
            user_message: User's message containing potential cognitive distortions
            context: Context including emotion, distress level, etc.

        Returns:
            TechniqueResult with reframing response
        """
        message_lower = user_message.lower()

        # Detect cognitive distortions
        detected_distortion = None
        for distortion_type, distortion_data in self.distortions.items():
            if any(pattern in message_lower for pattern in distortion_data["pattern"]):
                detected_distortion = distortion_type
                break

        # Generate reframing response
        if detected_distortion:
            reframe_text = self.distortions[detected_distortion]["reframe"]
            response = (
                f"Я слышу вашу боль. {reframe_text}\n\n"
                "Попробуйте сформулировать эту же мысль более сбалансированно. "
                "Например, вместо абсолютных утверждений, можно использовать: "
                "'прямо сейчас', 'в данный момент', 'это может измениться'."
            )

            follow_up = (
                "Когда вы будете готовы, можете попробовать записать вашу мысль в двух вариантах: "
                "первоначальном и переосмысленном. Это поможет увидеть альтернативные взгляды на ситуацию."
            )

        else:
            # General CBT reframing approach
            response = (
                "Я слышу, как тяжело вам сейчас. Давайте попробуем посмотреть на эту ситуацию с разных сторон.\n\n"
                "Подумайте:\n"
                "• Какие факты подтверждают эту мысль?\n"
                "• Какие факты противоречат ей?\n"
                "• Что бы вы сказали другу в такой ситуации?\n"
                "• Есть ли более сбалансированный взгляд на это?"
            )

            follow_up = (
                "Помните: мысли — это не факты. "
                "Они отражают наше восприятие, которое можно изменить."
            )

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=follow_up,
            recommended_next_step="practice_reframing",
            metadata={
                "technique": "cbt_reframing",
                "distortion_detected": detected_distortion,
                "context_emotion": context.get("primary_emotion", "unknown")
            }
        )

    def is_appropriate(
        self,
        distress_level: DistressLevel,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        CBT reframing works best for moderate distress.
        Not suitable for crisis situations.
        """
        if distress_level == DistressLevel.CRISIS:
            return False

        return super().is_appropriate(distress_level, context)
