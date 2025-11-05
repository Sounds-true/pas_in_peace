"""SMART goals validator."""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class SMARTAnalysis:
    """Analysis of goal against SMART criteria."""
    specific: bool
    measurable: bool
    achievable: bool
    relevant: bool
    time_bound: bool
    score: float
    suggestions: list


class SMARTValidator:
    """Validate goals against SMART criteria."""

    def validate(self, goal_text: str) -> SMARTAnalysis:
        """Validate goal is SMART."""

        # Simple keyword-based validation
        specific = any(word in goal_text.lower() for word in ['буду', 'сделаю', 'начну'])
        measurable = any(char.isdigit() for char in goal_text) or 'раз' in goal_text.lower()
        achievable = len(goal_text.split()) < 30  # Not too complex
        relevant = 'ребен' in goal_text.lower() or 'контакт' in goal_text.lower()
        time_bound = any(word in goal_text.lower() for word in ['до', 'через', 'к', 'дата'])

        score = sum([specific, measurable, achievable, relevant, time_bound]) / 5.0

        suggestions = []
        if not specific:
            suggestions.append("Сделайте цель более конкретной: 'Буду звонить...'")
        if not measurable:
            suggestions.append("Добавьте измеримость: 'X раз в неделю'")
        if not time_bound:
            suggestions.append("Добавьте срок: 'до [дата]'")

        return SMARTAnalysis(
            specific=specific,
            measurable=measurable,
            achievable=achievable,
            relevant=relevant,
            time_bound=time_bound,
            score=score,
            suggestions=suggestions
        )
