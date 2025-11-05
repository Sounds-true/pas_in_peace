"""Risk stratification based on Columbia-SSRS protocol."""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from src.core.logger import get_logger


logger = get_logger(__name__)


class RiskLevel(Enum):
    """Risk levels based on Columbia-SSRS."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class IdeationType(Enum):
    """Types of suicidal ideation."""
    NONE = "none"
    PASSIVE = "passive"  # Wish to be dead
    ACTIVE_NO_INTENT = "active_no_intent"  # Thoughts of suicide, no intent
    ACTIVE_WITH_METHOD = "active_with_method"  # Suicidal thoughts with method
    ACTIVE_WITH_INTENT = "active_with_intent"  # Intent to act
    ACTIVE_WITH_PLAN = "active_with_plan"  # Specific plan and intent


@dataclass
class SuicidalRiskAssessment:
    """Results of suicidal risk assessment."""
    risk_present: bool
    ideation_type: IdeationType
    has_plan: bool
    has_means: bool
    has_intent: bool
    has_timeline: bool  # Imminent timeframe mentioned
    protective_factors: List[str]
    risk_factors: List[str]
    keywords_matched: List[str]
    confidence: float
    assessment_timestamp: datetime


@dataclass
class ViolenceRiskAssessment:
    """Results of violence risk assessment."""
    violence_risk_present: bool
    threat_type: str  # "emotional_discharge", "threat_with_plan", "imminent_danger"
    target_mentioned: bool
    means_available: bool
    history_of_violence: bool
    protective_factors: List[str]
    confidence: float


@dataclass
class ChildHarmAssessment:
    """Results of child harm risk assessment."""
    child_harm_risk_present: bool
    severity: str  # "none", "low", "moderate", "high", "critical"
    specific_threat: bool
    confidence: float


@dataclass
class ComprehensiveRiskAssessment:
    """Comprehensive risk assessment result."""
    risk_level: RiskLevel
    suicidal_assessment: Optional[SuicidalRiskAssessment]
    violence_assessment: Optional[ViolenceRiskAssessment]
    child_harm_assessment: Optional[ChildHarmAssessment]
    recommended_action: str
    immediate_intervention_required: bool
    crisis_protocol_type: Optional[str]  # "high_risk", "medium_risk", "low_risk"
    monitoring_frequency: Optional[str]  # "immediate", "hourly", "daily", "weekly"
    reasoning: str
    timestamp: datetime


class RiskStratifier:
    """
    Risk stratification engine based on Columbia-SSRS protocol.

    Implements evidence-based risk stratification:
    - Columbia Suicide Severity Rating Scale (C-SSRS)
    - Duty to warn (Tarasoff) principles for violence
    - Child protection protocols

    References:
    - Posner et al. (2011). Columbia-Suicide Severity Rating Scale (C-SSRS)
    - SAFE-T Protocol with C-SSRS
    """

    def __init__(self):
        """Initialize risk stratifier."""
        # Columbia-SSRS screening thresholds
        self.high_risk_threshold = 4  # Level 4-5 on C-SSRS
        self.moderate_risk_threshold = 2  # Level 2-3 on C-SSRS

        # Protective factors (reduce risk)
        self.protective_factors_keywords = {
            "russian": [
                "поддержка семьи", "друзья помогают", "вера", "религия",
                "надежда", "планы на будущее", "хочу увидеть",
                "ради детей", "не могу причинить боль"
            ],
            "english": [
                "family support", "friends help", "faith", "religion",
                "hope", "future plans", "want to see",
                "for my children", "can't hurt"
            ]
        }

        # Risk factors (increase risk)
        self.risk_factors_keywords = {
            "russian": [
                "одинок", "никого нет", "изолирован", "алкоголь",
                "употребляю", "не сплю", "бессонница", "потерял работу",
                "финансовые проблемы", "развод", "потеря"
            ],
            "english": [
                "alone", "no one", "isolated", "alcohol",
                "using", "can't sleep", "insomnia", "lost job",
                "financial problems", "divorce", "loss"
            ]
        }

    def stratify_risk(
        self,
        suicidal_assessment: Optional[SuicidalRiskAssessment] = None,
        violence_assessment: Optional[ViolenceRiskAssessment] = None,
        child_harm_assessment: Optional[ChildHarmAssessment] = None,
        user_history: Optional[Dict[str, Any]] = None
    ) -> ComprehensiveRiskAssessment:
        """
        Stratify overall risk level based on all assessments.

        Args:
            suicidal_assessment: Suicidal risk assessment results
            violence_assessment: Violence risk assessment results
            child_harm_assessment: Child harm risk assessment results
            user_history: User's historical context

        Returns:
            ComprehensiveRiskAssessment with stratified risk level
        """
        # Initialize scores
        risk_score = 0
        reasoning_parts = []
        immediate_intervention = False
        crisis_protocol = None
        monitoring = "weekly"  # default

        # CRITICAL: Child harm or imminent violence
        if child_harm_assessment and child_harm_assessment.child_harm_risk_present:
            if child_harm_assessment.severity in ["high", "critical"]:
                logger.critical(
                    "child_harm_risk_detected",
                    severity=child_harm_assessment.severity,
                    specific_threat=child_harm_assessment.specific_threat
                )
                return ComprehensiveRiskAssessment(
                    risk_level=RiskLevel.CRITICAL,
                    suicidal_assessment=suicidal_assessment,
                    violence_assessment=violence_assessment,
                    child_harm_assessment=child_harm_assessment,
                    recommended_action="IMMEDIATE_CRISIS_PROTOCOL_CHILD_PROTECTION",
                    immediate_intervention_required=True,
                    crisis_protocol_type="critical_child_protection",
                    monitoring_frequency="immediate",
                    reasoning="Critical child harm risk detected. Child protection protocols activated.",
                    timestamp=datetime.now()
                )

        # HIGH: Suicidal risk assessment
        if suicidal_assessment and suicidal_assessment.risk_present:
            ideation_score = self._score_ideation(suicidal_assessment.ideation_type)
            risk_score += ideation_score

            # Columbia-SSRS criteria
            if suicidal_assessment.has_intent and suicidal_assessment.has_plan:
                risk_score += 3  # Major escalation
                reasoning_parts.append("Suicidal intent + specific plan detected")

            if suicidal_assessment.has_means:
                risk_score += 2
                reasoning_parts.append("Means available")

            if suicidal_assessment.has_timeline:
                risk_score += 2  # Imminent timeframe
                reasoning_parts.append("Imminent timeframe mentioned")

            # Protective factors reduce risk
            protective_count = len(suicidal_assessment.protective_factors)
            if protective_count > 0:
                risk_score -= min(protective_count, 2)  # Max -2 reduction
                reasoning_parts.append(f"{protective_count} protective factors identified")

            # Risk factors increase risk
            risk_factors_count = len(suicidal_assessment.risk_factors)
            if risk_factors_count >= 3:
                risk_score += 1
                reasoning_parts.append(f"{risk_factors_count} risk factors present")

            # Check user history for previous attempts
            if user_history and user_history.get("previous_suicide_attempt"):
                risk_score += 2
                reasoning_parts.append("Previous suicide attempt documented")

            logger.warning(
                "suicidal_risk_detected",
                risk_score=risk_score,
                ideation_type=suicidal_assessment.ideation_type.value,
                has_plan=suicidal_assessment.has_plan,
                has_intent=suicidal_assessment.has_intent
            )

        # MODERATE-HIGH: Violence risk
        if violence_assessment and violence_assessment.violence_risk_present:
            if violence_assessment.threat_type == "imminent_danger":
                risk_score += 4
                reasoning_parts.append("Imminent violence threat detected")
                immediate_intervention = True
            elif violence_assessment.threat_type == "threat_with_plan":
                risk_score += 3
                reasoning_parts.append("Violence threat with plan")
            elif violence_assessment.threat_type == "emotional_discharge":
                risk_score += 1
                reasoning_parts.append("Emotional discharge (anger/frustration)")

            logger.warning(
                "violence_risk_detected",
                threat_type=violence_assessment.threat_type,
                target_mentioned=violence_assessment.target_mentioned,
                means_available=violence_assessment.means_available
            )

        # Stratify based on total risk score
        risk_level, action, protocol, monitoring = self._determine_risk_level(
            risk_score,
            immediate_intervention
        )

        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "No significant risk detected"

        logger.info(
            "risk_stratification_complete",
            risk_level=risk_level.value,
            risk_score=risk_score,
            immediate_intervention=immediate_intervention
        )

        return ComprehensiveRiskAssessment(
            risk_level=risk_level,
            suicidal_assessment=suicidal_assessment,
            violence_assessment=violence_assessment,
            child_harm_assessment=child_harm_assessment,
            recommended_action=action,
            immediate_intervention_required=immediate_intervention,
            crisis_protocol_type=protocol,
            monitoring_frequency=monitoring,
            reasoning=reasoning,
            timestamp=datetime.now()
        )

    def _score_ideation(self, ideation_type: IdeationType) -> int:
        """Score ideation type based on Columbia-SSRS."""
        ideation_scores = {
            IdeationType.NONE: 0,
            IdeationType.PASSIVE: 1,  # "Wish to be dead"
            IdeationType.ACTIVE_NO_INTENT: 2,  # Level 2 C-SSRS
            IdeationType.ACTIVE_WITH_METHOD: 3,  # Level 3 C-SSRS
            IdeationType.ACTIVE_WITH_INTENT: 4,  # Level 4 C-SSRS
            IdeationType.ACTIVE_WITH_PLAN: 5,  # Level 5 C-SSRS
        }
        return ideation_scores.get(ideation_type, 0)

    def _determine_risk_level(
        self,
        risk_score: int,
        immediate_intervention: bool
    ) -> tuple[RiskLevel, str, Optional[str], str]:
        """
        Determine risk level from score.

        Returns:
            (risk_level, recommended_action, crisis_protocol_type, monitoring_frequency)
        """
        if immediate_intervention or risk_score >= 8:
            # HIGH RISK: Immediate crisis protocol
            return (
                RiskLevel.HIGH,
                "IMMEDIATE_CRISIS_PROTOCOL",
                "high_risk",
                "immediate"
            )
        elif risk_score >= 5:
            # MODERATE RISK: Safety planning + frequent monitoring
            return (
                RiskLevel.MODERATE,
                "SAFETY_PLANNING_AND_MONITORING",
                "medium_risk",
                "daily"
            )
        elif risk_score >= 2:
            # LOW RISK: Supportive care + passive monitoring
            return (
                RiskLevel.LOW,
                "SUPPORTIVE_CARE_WITH_MONITORING",
                "low_risk",
                "weekly"
            )
        else:
            # NO RISK: Continue normal flow
            return (
                RiskLevel.NONE,
                "CONTINUE_NORMAL_FLOW",
                None,
                "as_needed"
            )

    def extract_protective_factors(self, text: str) -> List[str]:
        """Extract protective factors from text."""
        text_lower = text.lower()
        protective = []

        for lang, keywords in self.protective_factors_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    protective.append(keyword)

        return protective

    def extract_risk_factors(self, text: str) -> List[str]:
        """Extract risk factors from text."""
        text_lower = text.lower()
        risk_factors = []

        for lang, keywords in self.risk_factors_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    risk_factors.append(keyword)

        return risk_factors
