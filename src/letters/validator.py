"""Letter validation for safety and effectiveness."""

from typing import List, Dict, Any
import re


class LetterValidator:
    """Validate letters for safety, PII, and effectiveness."""

    def validate(self, letter_text: str) -> Dict[str, Any]:
        """Validate letter and provide feedback."""

        issues = []
        warnings = []

        # Check for PII
        if self._has_sensitive_info(letter_text):
            warnings.append("Обнаружена персональная информация (номера, адреса)")

        # Check for hostile language
        if self._has_hostile_language(letter_text):
            issues.append("Обнаружен агрессивный тон")

        # Check length
        word_count = len(letter_text.split())
        if word_count > 300:
            warnings.append(f"Письмо слишком длинное ({word_count} слов). Рекомендуем < 200")

        is_safe = len(issues) == 0

        return {
            "is_safe": is_safe,
            "issues": issues,
            "warnings": warnings,
            "word_count": word_count,
            "recommendation": "approve" if is_safe else "revise"
        }

    def _has_sensitive_info(self, text: str) -> bool:
        """Check for phone numbers, addresses, etc."""
        patterns = [
            r'\+?\d[\d\s\-\(\)]{8,}',  # Phone numbers
            r'\d{6,}',  # Passport, SNILS
        ]
        return any(re.search(p, text) for p in patterns)

    def _has_hostile_language(self, text: str) -> bool:
        """Check for aggressive/hostile language."""
        hostile = ['ненавижу', 'ты виноват', 'ты плохой', 'угрожаю', 'всегда', 'никогда']
        return any(word in text.lower() for word in hostile)
