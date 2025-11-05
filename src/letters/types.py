"""Letter types and enums for PAS Bot."""

from enum import Enum


class LetterType(str, Enum):
    """Types of letters users can write."""

    FOR_SENDING = "for_sending"  # Letter to ex-partner, school, court, etc.
    TIME_CAPSULE = "time_capsule"  # Letter for child to read in the future
    THERAPEUTIC = "therapeutic"  # Private letter for emotional processing (venting)


class LetterStage(str, Enum):
    """Stages of letter writing process."""
    INIT = "init"
    DRAFT = "draft"
    TRANSCRIPTION = "transcription"  # After voice dictation
    TOXICITY_CHECK = "toxicity_check"
    REVIEW_WARNINGS = "review_warnings"  # User reviewing toxicity warnings
    TRANSFORM = "transform"  # BIFF/NVC transformation
    VALIDATE = "validate"
    FINALIZE = "finalize"


def get_letter_type_description(letter_type: LetterType) -> str:
    """Get human-readable description of letter type."""
    descriptions = {
        LetterType.FOR_SENDING: """
📤 **Письмо для отправки**

Это письмо будет отправлено другому человеку (бывший партнёр, школа, суд).
Бот проверит его на:
• Токсичность и оскорбления
• BIFF/NVC стиль (конструктивное общение)
• PII (персональные данные)

Цель: решить практический вопрос конструктивно.
        """,

        LetterType.TIME_CAPSULE: """
🎁 **Капсула для ребёнка**

Письмо ребёнку, которое он прочитает в будущем.
Бот проверит его на:
• Токсичность (чтобы не навредить ребёнку)
• Враждебность к другому родителю

Цель: объяснить ситуацию, выразить любовь.

⚠️ Важно: избегайте обвинений другого родителя.
        """,

        LetterType.THERAPEUTIC: """
💭 **Терапевтическое письмо**

Личное письмо для выражения эмоций (НЕ для отправки).
Бот НЕ проверяет его - полная свобода выражения.

Здесь можно:
• Выразить гнев и боль без цензуры
• Написать всё что чувствуете
• Обработать эмоции через текст

⚠️ Это письмо останется приватным и не будет отправлено.
        """
    }
    return descriptions.get(letter_type, "")


def should_check_toxicity(letter_type: LetterType) -> bool:
    """Check if toxicity analysis is needed for this letter type."""
    return letter_type in [LetterType.FOR_SENDING, LetterType.TIME_CAPSULE]


def get_toxicity_threshold(letter_type: LetterType) -> float:
    """
    Get toxicity threshold for warnings.

    Returns:
        Threshold (0.0-1.0). Higher = more lenient.
    """
    thresholds = {
        LetterType.FOR_SENDING: 0.3,  # Strict: warn at 30% toxicity
        LetterType.TIME_CAPSULE: 0.5,  # Medium: warn at 50% toxicity
        LetterType.THERAPEUTIC: 1.0,  # No warnings
    }
    return thresholds.get(letter_type, 0.3)
