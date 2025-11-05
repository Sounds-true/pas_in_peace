"""BIFF (Brief, Informative, Friendly, Firm) letter transformer."""

from typing import Dict, Any, List
from dataclasses import dataclass
import re

from src.core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class BIFFAnalysis:
    """Analysis of a letter against BIFF principles."""
    is_brief: bool
    is_informative: bool
    is_friendly: bool
    is_firm: bool

    word_count: int
    issues: List[str]
    suggestions: List[str]
    score: float  # 0-1


class BIFFTransformer:
    """
    Transform letters to follow BIFF principles.

    BIFF method by Bill Eddy:
    - Brief: Short and to the point
    - Informative: Provides necessary information
    - Friendly: Polite tone
    - Firm: Sets clear boundaries
    """

    # Aggressive/hostile phrases to avoid
    HOSTILE_PATTERNS = [
        r'\bвсегда\b', r'\bникогда\b', r'\bвечно\b',  # Absolutes
        r'\bты\s+виноват', r'\bты\s+плох', r'\bиз-за\s+тебя',  # Blame
        r'\bдолжен', r'\bобязан',  # Demands
        r'\bманипул', r'\bврёшь', r'\bобман',  # Accusations
        r'\bугроз', r'\bпожалуешься',  # Threats
    ]

    # Defensive/emotional phrases
    DEFENSIVE_PATTERNS = [
        r'я\s+чувствую\s+себя', r'мне\s+обидно', r'я\s+расстроен',  # Emotions
        r'помнишь\s+когда', r'ты\s+же\s+сам',  # Past grievances
    ]

    def transform(self, letter_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Transform letter to BIFF format.

        Args:
            letter_text: Original letter text
            context: Additional context (recipient, purpose, etc.)

        Returns:
            Dict with transformed_text, analysis, suggestions
        """
        # Analyze original letter
        analysis = self._analyze(letter_text)

        # Transform
        transformed = letter_text

        # Apply transformations
        if not analysis.is_brief:
            transformed = self._make_brief(transformed)

        if not analysis.is_informative:
            transformed = self._make_informative(transformed, context)

        if not analysis.is_friendly:
            transformed = self._make_friendly(transformed)

        if not analysis.is_firm:
            transformed = self._make_firm(transformed)

        # Re-analyze transformed
        final_analysis = self._analyze(transformed)

        return {
            "original_text": letter_text,
            "transformed_text": transformed,
            "original_analysis": analysis,
            "final_analysis": final_analysis,
            "improvements": {
                "brief": final_analysis.is_brief and not analysis.is_brief,
                "informative": final_analysis.is_informative and not analysis.is_informative,
                "friendly": final_analysis.is_friendly and not analysis.is_friendly,
                "firm": final_analysis.is_firm and not analysis.is_firm,
            },
            "suggestions": analysis.suggestions
        }

    def _analyze(self, text: str) -> BIFFAnalysis:
        """Analyze letter against BIFF principles."""
        word_count = len(text.split())
        issues = []
        suggestions = []

        # Brief check (< 200 words ideal)
        is_brief = word_count <= 200
        if not is_brief:
            issues.append("Письмо слишком длинное")
            suggestions.append("Сократите до 150-200 слов. Фокус на одном вопросе.")

        # Informative check (has specific info)
        has_dates = bool(re.search(r'\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|\d{1,2})', text, re.IGNORECASE))
        has_specific_request = any(word in text.lower() for word in ['когда', 'где', 'во сколько', 'как'])
        is_informative = has_dates or has_specific_request
        if not is_informative:
            issues.append("Недостаточно конкретики")
            suggestions.append("Добавьте конкретные даты, время, место или вопросы")

        # Friendly check (no hostile language)
        hostile_found = []
        for pattern in self.HOSTILE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                hostile_found.append(pattern)

        is_friendly = len(hostile_found) == 0
        if not is_friendly:
            issues.append("Обнаружены агрессивные фразы")
            suggestions.append("Уберите обвинения, ультиматумы и абсолютные утверждения ('всегда', 'никогда')")

        # Firm check (has clear statement/boundary)
        has_clear_ask = any(word in text.lower() for word in ['прошу', 'прошу уведомить', 'необходимо', 'планирую'])
        is_firm = has_clear_ask
        if not is_firm:
            issues.append("Нет чёткого запроса или границы")
            suggestions.append("Добавьте чёткий запрос или утверждение: 'Планирую забрать ребёнка в субботу в 10:00'")

        # Calculate score
        score = sum([is_brief, is_informative, is_friendly, is_firm]) / 4.0

        return BIFFAnalysis(
            is_brief=is_brief,
            is_informative=is_informative,
            is_friendly=is_friendly,
            is_firm=is_firm,
            word_count=word_count,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def _make_brief(self, text: str) -> str:
        """Make letter more brief."""
        # Remove redundant phrases
        redundant = [
            (r'я\s+хочу\s+сказать\s+что', 'я считаю что'),
            (r'мне\s+кажется\s+что', ''),
            (r'возможно\s+вы\s+помните', ''),
        ]

        for pattern, replacement in redundant:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Simplify sentences
        sentences = text.split('.')
        if len(sentences) > 6:
            # Keep first 2, middle 2, last 2
            text = '. '.join(sentences[:2] + sentences[-2:]) + '.'

        return text.strip()

    def _make_informative(self, text: str, context: Dict[str, Any] = None) -> str:
        """Make letter more informative."""
        # Add template for missing info
        if not re.search(r'\d{1,2}', text):
            # No dates found, suggest adding
            info_prompt = "\n\n[Добавьте конкретную дату/время]"
            text = text + info_prompt

        return text

    def _make_friendly(self, text: str) -> str:
        """Make letter more friendly (remove hostile language)."""
        # Replace hostile patterns
        replacements = {
            r'\bвсегда\b': 'часто',
            r'\bникогда\b': 'редко',
            r'\bты\s+виноват': 'ситуация сложная',
            r'\bдолжен': 'было бы хорошо если',
            r'\bобязан': 'прошу рассмотреть',
            r'\bманипул\w+': 'влияешь',
        }

        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Remove defensive statements
        text = re.sub(r'я\s+чувствую\s+себя\s+\w+', '', text, flags=re.IGNORECASE)

        return text.strip()

    def _make_firm(self, text: str) -> str:
        """Make letter more firm (add clear statements)."""
        # If no clear request, add template
        if not any(word in text.lower() for word in ['прошу', 'планирую', 'сообщаю']):
            firm_addition = "\n\nПрошу подтвердить получение этого сообщения."
            text = text + firm_addition

        return text

    def get_biff_template(self, purpose: str) -> str:
        """
        Get BIFF template for common letter purposes.

        Args:
            purpose: Letter purpose (schedule_change, information_request, boundary)

        Returns:
            BIFF template text
        """
        templates = {
            "schedule_change": """
            Привет [Имя],

            Сообщаю, что [дата] я планирую забрать [ребёнка] в [время] для [причина].

            Верну к [время]. Прошу подтвердить получение.

            Спасибо,
            [Ваше имя]
            """.strip(),

            "information_request": """
            Привет [Имя],

            Прошу сообщить о [конкретный вопрос] до [дата].

            Это нужно для [причина].

            Спасибо за понимание,
            [Ваше имя]
            """.strip(),

            "boundary": """
            Привет [Имя],

            Сообщаю, что [чёткое утверждение границы].

            Надеюсь на понимание.

            [Ваше имя]
            """.strip(),
        }

        return templates.get(purpose, templates["information_request"])
