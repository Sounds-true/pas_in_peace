"""Grounding techniques for emotional regulation."""

from typing import Dict, Any
from src.techniques.base import Technique, TechniqueResult, TechniqueCategory, DistressLevel


class GroundingTechnique(Technique):
    """
    Grounding techniques to help manage overwhelming emotions.

    Uses 5-4-3-2-1 sensory awareness and other grounding exercises
    specifically adapted for parents experiencing distress from alienation.
    """

    def __init__(self):
        """Initialize grounding technique."""
        super().__init__()
        self.name = "Grounding Exercise"
        self.category = TechniqueCategory.GROUNDING
        self.description = (
            "Техники заземления помогают справиться с подавляющими эмоциями, "
            "возвращая вас в настоящий момент через сенсорное осознание."
        )
        self.suitable_for_distress = [
            DistressLevel.MODERATE,
            DistressLevel.HIGH,
            DistressLevel.CRISIS
        ]

    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """
        Apply grounding technique based on distress level.

        Args:
            user_message: User's message
            context: Context including distress level, emotion, etc.

        Returns:
            TechniqueResult with grounding exercise
        """
        distress_level = context.get("distress_level", "moderate")
        primary_emotion = context.get("primary_emotion", "")

        # High distress or crisis: Simple grounding
        if distress_level in ["high", "crisis"] or "crisis" in context:
            response = self._get_simple_grounding()
            follow_up = (
                "Попробуйте выполнить это упражнение сейчас. "
                "Это займёт всего 2-3 минуты. Дайте знать, когда будете готовы продолжить."
            )

        # Moderate distress: 5-4-3-2-1 technique
        elif distress_level == "moderate":
            response = self._get_5_4_3_2_1_technique()
            follow_up = (
                "Выполните это упражнение в своём темпе. "
                "Не спешите. Каждый шаг помогает вернуть контроль над вашим состоянием."
            )

        # Low distress: Mindful breathing
        else:
            response = self._get_mindful_breathing()
            follow_up = "Попробуйте это дыхательное упражнение в течение 1-2 минут."

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=follow_up,
            recommended_next_step="check_emotion_after_grounding",
            metadata={
                "technique": "grounding",
                "distress_level": distress_level,
                "exercise_type": self._get_exercise_type(distress_level)
            }
        )

    def _get_simple_grounding(self) -> str:
        """Simple grounding for high distress."""
        return """
🌿 **Простое упражнение заземления**

Сейчас важно вернуть себя в настоящий момент.

**Выполните по порядку:**

1️⃣ **Остановитесь**
   • Где бы вы ни были, остановитесь на мгновение

2️⃣ **Дышите**
   • Сделайте глубокий вдох на 4 счёта
   • Задержите дыхание на 2 счёта
   • Выдохните на 6 счётов
   • Повторите 3 раза

3️⃣ **Почувствуйте опору**
   • Почувствуйте, как ваши ноги касаются пола
   • Если сидите — как тело соприкасается с поверхностью
   • Это ваша опора, ваша стабильность

4️⃣ **Назовите вслух или про себя:**
   • 3 вещи, которые вы видите
   • 3 звука, которые вы слышите
   • 3 ощущения в теле

Вы в безопасности. Вы в настоящем моменте.
        """.strip()

    def _get_5_4_3_2_1_technique(self) -> str:
        """5-4-3-2-1 sensory grounding technique."""
        return """
🌿 **Техника заземления 5-4-3-2-1**

Это упражнение использует ваши чувства, чтобы вернуть вас в настоящий момент.

**Назовите (вслух или про себя):**

👀 **5 вещей**, которые вы **ВИДИТЕ** вокруг себя
   (Например: стол, лампа, окно, книга, телефон)

✋ **4 вещи**, которые вы можете **ПОТРОГАТЬ**
   (Например: текстура одежды, гладкая поверхность стола, тепло чашки)

👂 **3 вещи**, которые вы **СЛЫШИТЕ**
   (Например: звук холодильника, птицы за окном, ваше дыхание)

👃 **2 вещи**, которые вы можете **ПОНЮХАТЬ**
   (Например: кофе, свежий воздух, запах комнаты)

👅 **1 вещь**, которую вы можете **ПОПРОБОВАТЬ** на вкус
   (Например: остаток вкуса еды, или просто осознайте вкус во рту)

---

Это упражнение помогает:
• Прервать цикл тревожных мыслей
• Вернуться в "здесь и сейчас"
• Почувствовать контроль над ситуацией
        """.strip()

    def _get_mindful_breathing(self) -> str:
        """Mindful breathing exercise."""
        return """
🌬️ **Осознанное дыхание**

Простое, но мощное упражнение для успокоения.

**Инструкция:**

1. Найдите удобное положение (сидя или стоя)

2. Положите одну руку на грудь, другую — на живот

3. Дышите следуя ритму:
   • Вдох через нос на 4 счёта (живот поднимается)
   • Задержка на 4 счёта
   • Выдох через рот на 6 счётов (живот опускается)
   • Пауза на 2 счёта

4. Повторите 5-10 раз

**Фокус внимания:**
• Как воздух входит в нос (прохладный)
• Как выходит через рот (тёплый)
• Как движется живот вверх-вниз
• Ощущение рук на теле

Если мысли уводят вас, мягко верните внимание к дыханию.
        """.strip()

    def _get_exercise_type(self, distress_level: str) -> str:
        """Get exercise type based on distress level."""
        mapping = {
            "low": "mindful_breathing",
            "moderate": "5_4_3_2_1",
            "high": "simple_grounding",
            "crisis": "simple_grounding"
        }
        return mapping.get(distress_level, "5_4_3_2_1")

    def is_appropriate(
        self,
        distress_level: DistressLevel,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Grounding is appropriate for most distress levels,
        especially useful for high distress and crisis.
        """
        return True  # Grounding works for all levels
