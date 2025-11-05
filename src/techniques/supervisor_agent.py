"""Supervisor Agent for quality control of therapeutic responses."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from src.core.logger import get_logger


logger = get_logger(__name__)


class QualityDimension(Enum):
    """Quality dimensions for therapeutic responses."""
    EMPATHY = "empathy"
    SAFETY = "safety"
    ACCURACY = "accuracy"
    THERAPEUTIC_VALUE = "therapeutic_value"
    RESPECT_AUTONOMY = "respect_autonomy"
    APPROPRIATE_BOUNDARIES = "appropriate_boundaries"


@dataclass
class QualityScore:
    """Quality score for a response."""
    dimension: QualityDimension
    score: float  # 0-1
    reasoning: str
    improvement_suggestions: List[str]


@dataclass
class SupervisionResult:
    """Result of supervision."""
    approved: bool
    overall_score: float  # 0-1
    dimension_scores: List[QualityScore]
    critical_issues: List[str]
    recommended_revisions: List[str]
    safe_to_send: bool


class SupervisorAgent:
    """
    Supervisor Agent for validating therapeutic responses.

    Implements quality control layer before responses are sent to users.
    Based on best practices from:
    - Clinical supervision literature
    - AI safety guidelines
    - Mental health app evaluation frameworks

    Key responsibilities:
    1. Check for harmful content
    2. Validate therapeutic appropriateness
    3. Ensure empathy and respect
    4. Verify safety protocols
    """

    def __init__(self):
        """Initialize supervisor agent."""
        # Red flags (auto-reject)
        self.red_flags = {
            "russian": [
                "убей", "умри", "покончи", "соверши суицид",
                "ты виноват", "ты плохой родитель",
                "забудь о ребенке", "сдайся"
            ],
            "english": [
                "kill", "die", "commit suicide", "end it",
                "you're to blame", "you're a bad parent",
                "forget about the child", "give up"
            ]
        }

        # Empathy indicators (should be present)
        self.empathy_indicators = {
            "russian": [
                "я слышу", "я понимаю", "я чувствую", "это тяжело",
                "ваша боль", "ваши чувства", "я вижу"
            ],
            "english": [
                "I hear", "I understand", "I sense", "this is difficult",
                "your pain", "your feelings", "I see"
            ]
        }

        # Quality thresholds
        self.min_empathy_score = 0.5
        self.min_safety_score = 0.8
        self.min_overall_score = 0.6

    async def supervise_response(
        self,
        response: str,
        user_message: str,
        context: Dict[str, Any]
    ) -> SupervisionResult:
        """
        Supervise a generated response before sending.

        Args:
            response: Generated response to validate
            user_message: Original user message
            context: Context including emotion, risk level, etc.

        Returns:
            SupervisionResult with approval decision
        """
        dimension_scores = []

        # Check each quality dimension
        empathy_score = self._check_empathy(response, context)
        dimension_scores.append(empathy_score)

        safety_score = self._check_safety(response, context)
        dimension_scores.append(safety_score)

        accuracy_score = self._check_accuracy(response, user_message, context)
        dimension_scores.append(accuracy_score)

        therapeutic_value_score = self._check_therapeutic_value(response, context)
        dimension_scores.append(therapeutic_value_score)

        autonomy_score = self._check_respect_autonomy(response)
        dimension_scores.append(autonomy_score)

        boundaries_score = self._check_boundaries(response)
        dimension_scores.append(boundaries_score)

        # Calculate overall score
        overall_score = sum(s.score for s in dimension_scores) / len(dimension_scores)

        # Identify critical issues
        critical_issues = []
        safe_to_send = True

        if safety_score.score < self.min_safety_score:
            critical_issues.append("SAFETY VIOLATION")
            safe_to_send = False

        if empathy_score.score < self.min_empathy_score:
            critical_issues.append("INSUFFICIENT EMPATHY")

        # Check for red flags
        red_flag_found = self._check_red_flags(response)
        if red_flag_found:
            critical_issues.append(f"RED FLAG: {red_flag_found}")
            safe_to_send = False

        # Determine approval
        approved = (
            safe_to_send and
            overall_score >= self.min_overall_score and
            len(critical_issues) == 0
        )

        # Generate recommendations
        recommended_revisions = self._generate_revisions(dimension_scores, critical_issues)

        logger.info(
            "supervision_complete",
            approved=approved,
            overall_score=overall_score,
            critical_issues_count=len(critical_issues)
        )

        return SupervisionResult(
            approved=approved,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            critical_issues=critical_issues,
            recommended_revisions=recommended_revisions,
            safe_to_send=safe_to_send
        )

    def _check_empathy(self, response: str, context: Dict[str, Any]) -> QualityScore:
        """Check empathy level."""
        response_lower = response.lower()
        language = context.get("language", "russian")

        # Count empathy indicators
        indicators = self.empathy_indicators.get(language, self.empathy_indicators["russian"])
        empathy_count = sum(1 for indicator in indicators if indicator in response_lower)

        # Score based on presence of indicators
        score = min(empathy_count / 3.0, 1.0)  # 3+ indicators = full score

        suggestions = []
        if score < 0.5:
            if language == "russian":
                suggestions.append("Добавьте фразы валидации: 'Я слышу вашу боль', 'Это действительно тяжело'")
            else:
                suggestions.append("Add validation phrases: 'I hear your pain', 'This is really difficult'")

        return QualityScore(
            dimension=QualityDimension.EMPATHY,
            score=score,
            reasoning=f"Found {empathy_count} empathy indicators",
            improvement_suggestions=suggestions
        )

    def _check_safety(self, response: str, context: Dict[str, Any]) -> QualityScore:
        """Check safety of response."""
        response_lower = response.lower()

        # Check for red flags
        red_flag = self._check_red_flags(response_lower)

        if red_flag:
            return QualityScore(
                dimension=QualityDimension.SAFETY,
                score=0.0,
                reasoning=f"Red flag detected: {red_flag}",
                improvement_suggestions=["Remove harmful content", "Reframe with supportive language"]
            )

        # Check if crisis protocol mentioned when needed
        risk_level = context.get("risk_level", "none")
        if risk_level in ["high", "critical"]:
            has_crisis_mention = any(
                word in response_lower
                for word in ["кризисная линия", "8-800", "помощь", "crisis line", "hotline"]
            )
            if not has_crisis_mention:
                return QualityScore(
                    dimension=QualityDimension.SAFETY,
                    score=0.5,
                    reasoning="High risk but no crisis resources mentioned",
                    improvement_suggestions=["Add crisis hotline information"]
                )

        return QualityScore(
            dimension=QualityDimension.SAFETY,
            score=1.0,
            reasoning="No safety issues detected",
            improvement_suggestions=[]
        )

    def _check_accuracy(self, response: str, user_message: str, context: Dict[str, Any]) -> QualityScore:
        """Check accuracy and relevance."""
        # Simplified: Check if response relates to user message
        # In production, would use semantic similarity

        # Check for generic/template responses
        generic_phrases = ["понимаю", "это сложно", "I understand", "this is difficult"]
        is_too_generic = all(phrase in response.lower() for phrase in generic_phrases[:2])

        if is_too_generic and len(response) < 100:
            score = 0.4
            suggestions = ["Make response more specific to user's situation"]
        else:
            score = 0.7
            suggestions = []

        return QualityScore(
            dimension=QualityDimension.ACCURACY,
            score=score,
            reasoning="Response relevance checked",
            improvement_suggestions=suggestions
        )

    def _check_therapeutic_value(self, response: str, context: Dict[str, Any]) -> QualityScore:
        """Check therapeutic value."""
        # Check for actionable suggestions or insights
        actionable_words = ["попробуйте", "можете", "давайте", "try", "you can", "let's"]
        has_actionable = any(word in response.lower() for word in actionable_words)

        score = 0.8 if has_actionable else 0.5

        suggestions = []
        if not has_actionable:
            suggestions.append("Add actionable steps or techniques")

        return QualityScore(
            dimension=QualityDimension.THERAPEUTIC_VALUE,
            score=score,
            reasoning="Therapeutic value assessed",
            improvement_suggestions=suggestions
        )

    def _check_respect_autonomy(self, response: str) -> QualityScore:
        """Check respect for user autonomy."""
        # Check for authoritarian language
        authoritarian_words = ["должны", "обязаны", "нужно", "must", "have to", "should"]
        has_authoritarian = any(word in response.lower() for word in authoritarian_words)

        score = 0.5 if has_authoritarian else 1.0

        suggestions = []
        if has_authoritarian:
            suggestions.append("Replace 'should/must' with 'might consider' or 'could try'")

        return QualityScore(
            dimension=QualityDimension.RESPECT_AUTONOMY,
            score=score,
            reasoning="Autonomy check",
            improvement_suggestions=suggestions
        )

    def _check_boundaries(self, response: str) -> QualityScore:
        """Check appropriate professional boundaries."""
        # Check for overly personal or medical advice
        boundary_violations = [
            "я тоже", "у меня было", "мой опыт", "me too", "I also", "my experience",
            "диагноз", "лечение", "таблетки", "diagnosis", "treatment", "medication"
        ]

        has_violation = any(phrase in response.lower() for phrase in boundary_violations)

        score = 0.4 if has_violation else 1.0

        suggestions = []
        if has_violation:
            suggestions.append("Maintain professional boundaries - no personal disclosure or medical advice")

        return QualityScore(
            dimension=QualityDimension.APPROPRIATE_BOUNDARIES,
            score=score,
            reasoning="Boundary check",
            improvement_suggestions=suggestions
        )

    def _check_red_flags(self, text: str) -> Optional[str]:
        """Check for red flag content."""
        text_lower = text.lower()

        for language, flags in self.red_flags.items():
            for flag in flags:
                if flag in text_lower:
                    return flag

        return None

    def _generate_revisions(
        self,
        scores: List[QualityScore],
        critical_issues: List[str]
    ) -> List[str]:
        """Generate revision recommendations."""
        revisions = []

        # Collect all suggestions
        for score in scores:
            revisions.extend(score.improvement_suggestions)

        # Add critical issue fixes
        for issue in critical_issues:
            if "SAFETY" in issue:
                revisions.insert(0, "⚠️ CRITICAL: Remove unsafe content before sending")
            elif "EMPATHY" in issue:
                revisions.insert(0, "Add empathic validation")

        return revisions
