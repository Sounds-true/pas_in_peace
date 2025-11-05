"""Violence threat assessment with emotional discharge differentiation."""

import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.core.logger import get_logger
from src.safety.risk_stratifier import ViolenceRiskAssessment


logger = get_logger(__name__)


@dataclass
class ThreatAnalysis:
    """Detailed threat analysis results."""
    is_threat: bool
    threat_type: str  # "emotional_discharge", "threat_with_plan", "imminent_danger"
    specificity_score: float  # 0-1, how specific is the threat
    emotional_intensity: float  # 0-1, emotional charge
    has_target: bool
    target_type: Optional[str]  # "ex_partner", "child", "other"
    has_means: bool
    has_timeline: bool
    contextual_markers: List[str]
    matched_patterns: List[str]
    confidence: float


class ViolenceThreatAssessor:
    """
    Assesses violence threats with differentiation between:
    1. Emotional discharge ("just venting")
    2. Threat with plan
    3. Imminent danger

    Based on:
    - Tarasoff duty to warn principles
    - Violence risk assessment literature
    - Emotional catharsis vs. genuine threat markers

    Key insight from research:
    Only 5% of violence is related to severe mental illness.
    Most threats in therapy contexts are emotional discharge, not genuine intent.

    References:
    - Tarasoff v. Regents of University of California (1976)
    - Violence Risk Assessment and Management (VRAM) guidelines
    """

    def __init__(self):
        """Initialize violence threat assessor."""

        # Explicit threat keywords (high specificity)
        self.explicit_threat_keywords = {
            "russian": [
                "убью", "убить", "уничтожу", "убиваю",
                "покончу с", "расправлюсь", "задушу",
                "зарежу", "застрелю", "избью до смерти"
            ],
            "english": [
                "kill", "murder", "destroy", "end",
                "strangle", "stab", "shoot", "beat to death"
            ]
        }

        # Emotional discharge markers (lower specificity)
        self.emotional_discharge_markers = {
            "russian": [
                "так злюсь", "хочется кричать", "бесит",
                "хочется убить", "мог бы убить", "готов убить",
                "иногда думаю", "когда злюсь", "в моменты гнева",
                "просто говорю", "выпускаю пар", "не на самом деле"
            ],
            "english": [
                "so angry", "want to scream", "infuriates",
                "could kill", "want to kill", "ready to kill",
                "sometimes think", "when angry", "in moments of rage",
                "just saying", "venting", "not really"
            ]
        }

        # Plan/means indicators
        self.plan_indicators = {
            "russian": [
                "план", "планирую", "собираюсь", "завтра", "сегодня",
                "на этой неделе", "подготовил", "достану", "знаю где",
                "есть оружие", "куплю", "найду способ"
            ],
            "english": [
                "plan", "planning", "going to", "tomorrow", "today",
                "this week", "prepared", "will get", "know where",
                "have weapon", "will buy", "find a way"
            ]
        }

        # Imminent danger markers
        self.imminent_markers = {
            "russian": [
                "прямо сейчас", "сегодня", "завтра", "на этой неделе",
                "иду к ней", "еду туда", "встречаюсь с ним",
                "готов действовать", "уже решил"
            ],
            "english": [
                "right now", "today", "tomorrow", "this week",
                "going to her", "driving there", "meeting him",
                "ready to act", "already decided"
            ]
        }

        # Target identifiers
        self.target_patterns = {
            "ex_partner": {
                "russian": [
                    "бывш", "экс", "она", "он", "мать ребенка", "отец ребенка",
                    "партнер", "супруг"
                ],
                "english": [
                    "ex", "she", "he", "mother of", "father of",
                    "partner", "spouse"
                ]
            },
            "child": {
                "russian": [
                    "ребенок", "сын", "дочь", "дети", "ребёнок"
                ],
                "english": [
                    "child", "son", "daughter", "children", "kid"
                ]
            },
            "other": {
                "russian": [
                    "адвокат", "судья", "юрист", "социальный работник",
                    "психолог", "терапевт"
                ],
                "english": [
                    "lawyer", "judge", "attorney", "social worker",
                    "psychologist", "therapist"
                ]
            }
        }

        # Protective factors (reduce threat credibility)
        self.protective_factors = {
            "russian": [
                "но я не буду", "но знаю что нельзя", "понимаю что нельзя",
                "просто фантазия", "не сделаю", "контролирую себя",
                "ради детей", "не хочу причинить вред"
            ],
            "english": [
                "but I won't", "but I know I can't", "understand I can't",
                "just fantasy", "won't do it", "control myself",
                "for the children", "don't want to harm"
            ]
        }

    async def assess_violence_threat(
        self,
        text: str,
        user_history: Optional[Dict[str, Any]] = None
    ) -> ViolenceRiskAssessment:
        """
        Assess violence threat in text.

        Args:
            text: User message to assess
            user_history: Optional user history context

        Returns:
            ViolenceRiskAssessment with threat analysis
        """
        # Analyze threat components
        analysis = self._analyze_threat(text)

        # Check user history for violence patterns
        history_of_violence = False
        if user_history:
            history_of_violence = user_history.get("violence_history", False)

        # Determine threat type based on analysis
        threat_type = self._determine_threat_type(analysis, history_of_violence)

        # Extract protective factors
        protective = self._extract_protective_factors(text)

        # Calculate confidence
        confidence = self._calculate_confidence(analysis, len(protective))

        logger.info(
            "violence_threat_assessed",
            threat_type=threat_type,
            specificity=analysis.specificity_score,
            emotional_intensity=analysis.emotional_intensity,
            has_target=analysis.has_target,
            confidence=confidence
        )

        return ViolenceRiskAssessment(
            violence_risk_present=analysis.is_threat,
            threat_type=threat_type,
            target_mentioned=analysis.has_target,
            means_available=analysis.has_means,
            history_of_violence=history_of_violence,
            protective_factors=protective,
            confidence=confidence
        )

    def _analyze_threat(self, text: str) -> ThreatAnalysis:
        """Detailed threat analysis."""
        text_lower = text.lower()

        # Check for explicit threats
        explicit_matches = []
        for lang, keywords in self.explicit_threat_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    explicit_matches.append(keyword)

        # Check for emotional discharge markers
        emotional_markers = []
        for lang, markers in self.emotional_discharge_markers.items():
            for marker in markers:
                if marker in text_lower:
                    emotional_markers.append(marker)

        # Check for plan indicators
        plan_matches = []
        for lang, indicators in self.plan_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    plan_matches.append(indicator)

        # Check for imminent danger markers
        imminent_matches = []
        for lang, markers in self.imminent_markers.items():
            for marker in markers:
                if marker in text_lower:
                    imminent_matches.append(marker)

        # Identify target
        has_target, target_type = self._identify_target(text_lower)

        # Calculate specificity score
        # Higher if explicit threat + plan + target
        specificity_score = 0.0
        if explicit_matches:
            specificity_score += 0.4
        if plan_matches:
            specificity_score += 0.3
        if has_target:
            specificity_score += 0.2
        if imminent_matches:
            specificity_score += 0.1

        # Calculate emotional intensity
        # Higher if emotional discharge markers present
        emotional_intensity = 0.5  # baseline
        if emotional_markers:
            emotional_intensity += 0.3
        if len(explicit_matches) > 2:  # Repeated explicit words
            emotional_intensity += 0.2

        # Check for means
        has_means = self._check_means(text_lower)

        # Determine if it's a threat
        is_threat = len(explicit_matches) > 0 or (
            len(plan_matches) > 0 and has_target
        )

        return ThreatAnalysis(
            is_threat=is_threat,
            threat_type="",  # Determined later
            specificity_score=min(specificity_score, 1.0),
            emotional_intensity=min(emotional_intensity, 1.0),
            has_target=has_target,
            target_type=target_type,
            has_means=has_means or len(plan_matches) > 0,
            has_timeline=len(imminent_matches) > 0,
            contextual_markers=emotional_markers + plan_matches + imminent_matches,
            matched_patterns=explicit_matches,
            confidence=0.0  # Calculated later
        )

    def _identify_target(self, text: str) -> Tuple[bool, Optional[str]]:
        """Identify if a target is mentioned and type."""
        for target_type, patterns in self.target_patterns.items():
            for lang, keywords in patterns.items():
                for keyword in keywords:
                    if keyword in text:
                        return True, target_type
        return False, None

    def _check_means(self, text: str) -> bool:
        """Check if means are mentioned."""
        means_keywords = [
            # Russian
            "оружие", "пистолет", "нож", "топор", "машина",
            "яд", "таблетки", "веревка",
            # English
            "weapon", "gun", "knife", "axe", "car",
            "poison", "pills", "rope"
        ]

        for keyword in means_keywords:
            if keyword in text:
                return True
        return False

    def _extract_protective_factors(self, text: str) -> List[str]:
        """Extract protective factors from text."""
        text_lower = text.lower()
        protective = []

        for lang, factors in self.protective_factors.items():
            for factor in factors:
                if factor in text_lower:
                    protective.append(factor)

        return protective

    def _determine_threat_type(
        self,
        analysis: ThreatAnalysis,
        history_of_violence: bool
    ) -> str:
        """
        Determine threat type based on analysis.

        Types:
        1. emotional_discharge: Venting, no genuine intent
        2. threat_with_plan: Threat with some planning
        3. imminent_danger: Immediate danger
        """
        # IMMINENT DANGER: High specificity + timeline + means
        if (analysis.specificity_score >= 0.7 and
            analysis.has_timeline and
            analysis.has_means):
            return "imminent_danger"

        # IMMINENT DANGER: History of violence + explicit threat + target
        if (history_of_violence and
            analysis.specificity_score >= 0.5 and
            analysis.has_target):
            return "imminent_danger"

        # THREAT WITH PLAN: Moderate specificity + plan indicators
        if (analysis.specificity_score >= 0.5 and
            analysis.has_means and
            analysis.has_target):
            return "threat_with_plan"

        # EMOTIONAL DISCHARGE: High emotional intensity but low specificity
        if (analysis.emotional_intensity >= 0.6 and
            analysis.specificity_score < 0.5):
            return "emotional_discharge"

        # EMOTIONAL DISCHARGE: Explicit words but no plan/means/timeline
        if (analysis.matched_patterns and
            not analysis.has_means and
            not analysis.has_timeline):
            return "emotional_discharge"

        # Default: If threat detected but ambiguous
        if analysis.is_threat:
            return "threat_with_plan"

        return "emotional_discharge"

    def _calculate_confidence(
        self,
        analysis: ThreatAnalysis,
        protective_count: int
    ) -> float:
        """Calculate confidence in threat assessment."""
        # Base confidence on specificity
        confidence = analysis.specificity_score * 0.7

        # Increase if multiple patterns matched
        if len(analysis.matched_patterns) > 1:
            confidence += 0.1

        # Increase if clear target and means
        if analysis.has_target and analysis.has_means:
            confidence += 0.1

        # Decrease if protective factors present
        if protective_count > 0:
            confidence -= 0.1 * min(protective_count, 2)

        # Adjust based on emotional intensity
        # High emotional intensity without specificity suggests discharge
        if analysis.emotional_intensity > 0.7 and analysis.specificity_score < 0.4:
            confidence = max(0.3, confidence - 0.2)  # Lower confidence in genuine threat

        return max(0.0, min(1.0, confidence))
