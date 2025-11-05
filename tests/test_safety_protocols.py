"""Tests for safety protocols implementation."""

import pytest
import asyncio
from datetime import datetime

from src.safety.risk_stratifier import (
    RiskStratifier,
    RiskLevel,
    IdeationType,
    SuicidalRiskAssessment,
    ViolenceRiskAssessment,
    ChildHarmAssessment
)
from src.safety.violence_threat_assessor import ViolenceThreatAssessor
from src.safety.safety_planning import SafetyPlanner
from src.safety.crisis_detector import CrisisDetector


class TestRiskStratifier:
    """Test risk stratification based on Columbia-SSRS."""

    def setup_method(self):
        """Setup test environment."""
        self.stratifier = RiskStratifier()

    def test_high_risk_with_plan_and_means(self):
        """Test HIGH risk: ideation + plan + means + intent."""
        suicidal_assessment = SuicidalRiskAssessment(
            risk_present=True,
            ideation_type=IdeationType.ACTIVE_WITH_PLAN,
            has_plan=True,
            has_means=True,
            has_intent=True,
            has_timeline=True,
            protective_factors=[],
            risk_factors=["одинок", "алкоголь"],
            keywords_matched=["убить себя", "таблетки"],
            confidence=0.95,
            assessment_timestamp=datetime.now()
        )

        result = self.stratifier.stratify_risk(
            suicidal_assessment=suicidal_assessment
        )

        assert result.risk_level == RiskLevel.HIGH
        assert result.immediate_intervention_required is True
        assert result.crisis_protocol_type == "high_risk"
        assert result.monitoring_frequency == "immediate"

    def test_moderate_risk_with_ideation_no_plan(self):
        """Test MODERATE risk: ideation without plan."""
        suicidal_assessment = SuicidalRiskAssessment(
            risk_present=True,
            ideation_type=IdeationType.ACTIVE_NO_INTENT,
            has_plan=False,
            has_means=False,
            has_intent=False,
            has_timeline=False,
            protective_factors=["поддержка семьи"],
            risk_factors=["одинок"],
            keywords_matched=["не хочу жить"],
            confidence=0.75,
            assessment_timestamp=datetime.now()
        )

        result = self.stratifier.stratify_risk(
            suicidal_assessment=suicidal_assessment
        )

        assert result.risk_level == RiskLevel.MODERATE
        assert result.recommended_action == "SAFETY_PLANNING_AND_MONITORING"
        assert result.crisis_protocol_type == "medium_risk"

    def test_low_risk_passive_ideation(self):
        """Test LOW risk: passive ideation only."""
        suicidal_assessment = SuicidalRiskAssessment(
            risk_present=True,
            ideation_type=IdeationType.PASSIVE,
            has_plan=False,
            has_means=False,
            has_intent=False,
            has_timeline=False,
            protective_factors=["вера", "планы на будущее"],
            risk_factors=[],
            keywords_matched=["хочу умереть"],
            confidence=0.6,
            assessment_timestamp=datetime.now()
        )

        result = self.stratifier.stratify_risk(
            suicidal_assessment=suicidal_assessment
        )

        assert result.risk_level == RiskLevel.LOW
        assert result.recommended_action == "SUPPORTIVE_CARE_WITH_MONITORING"

    def test_critical_child_harm_risk(self):
        """Test CRITICAL risk: child harm detected."""
        child_harm_assessment = ChildHarmAssessment(
            child_harm_risk_present=True,
            severity="critical",
            specific_threat=True,
            confidence=0.9
        )

        result = self.stratifier.stratify_risk(
            child_harm_assessment=child_harm_assessment
        )

        assert result.risk_level == RiskLevel.CRITICAL
        assert result.immediate_intervention_required is True
        assert "child_protection" in result.crisis_protocol_type

    def test_protective_factors_reduce_risk(self):
        """Test that protective factors reduce risk score."""
        # Scenario 1: Without protective factors
        assessment1 = SuicidalRiskAssessment(
            risk_present=True,
            ideation_type=IdeationType.ACTIVE_WITH_METHOD,
            has_plan=True,
            has_means=True,
            has_intent=False,
            has_timeline=False,
            protective_factors=[],
            risk_factors=["одинок", "алкоголь"],
            keywords_matched=["суицид"],
            confidence=0.85,
            assessment_timestamp=datetime.now()
        )

        # Scenario 2: With protective factors
        assessment2 = SuicidalRiskAssessment(
            risk_present=True,
            ideation_type=IdeationType.ACTIVE_WITH_METHOD,
            has_plan=True,
            has_means=True,
            has_intent=False,
            has_timeline=False,
            protective_factors=["поддержка семьи", "вера", "планы на будущее"],
            risk_factors=["одинок", "алкоголь"],
            keywords_matched=["суицид"],
            confidence=0.85,
            assessment_timestamp=datetime.now()
        )

        result1 = self.stratifier.stratify_risk(suicidal_assessment=assessment1)
        result2 = self.stratifier.stratify_risk(suicidal_assessment=assessment2)

        # Result2 should have lower risk level due to protective factors
        assert result2.risk_level.value <= result1.risk_level.value


class TestViolenceThreatAssessor:
    """Test violence threat assessment."""

    def setup_method(self):
        """Setup test environment."""
        self.assessor = ViolenceThreatAssessor()

    @pytest.mark.asyncio
    async def test_emotional_discharge_detected(self):
        """Test detection of emotional discharge (not genuine threat)."""
        text = "Я так зол на нее! Хочется убить, но понимаю что нельзя. Просто выпускаю пар."

        result = await self.assessor.assess_violence_threat(text)

        assert result.threat_type == "emotional_discharge"
        assert result.violence_risk_present is True
        assert len(result.protective_factors) > 0  # "но понимаю что нельзя"

    @pytest.mark.asyncio
    async def test_genuine_threat_with_plan(self):
        """Test detection of genuine threat with plan."""
        text = "Убью ее завтра. Знаю где она живет, уже купил нож."

        result = await self.assessor.assess_violence_threat(text)

        assert result.threat_type in ["threat_with_plan", "imminent_danger"]
        assert result.target_mentioned is True
        assert result.means_available is True

    @pytest.mark.asyncio
    async def test_imminent_danger_detection(self):
        """Test detection of imminent danger."""
        text = "Еду к ней прямо сейчас. Убью. У меня есть пистолет."

        result = await self.assessor.assess_violence_threat(text)

        assert result.threat_type == "imminent_danger"
        assert result.confidence >= 0.7

    @pytest.mark.asyncio
    async def test_no_threat_angry_expression(self):
        """Test that mere anger is not classified as threat."""
        text = "Я так злюсь на ситуацию! Это несправедливо!"

        result = await self.assessor.assess_violence_threat(text)

        # Should detect as emotional discharge or no threat
        assert result.threat_type == "emotional_discharge"
        assert result.confidence < 0.5


class TestSafetyPlanner:
    """Test safety planning module."""

    def setup_method(self):
        """Setup test environment."""
        self.planner = SafetyPlanner()

    @pytest.mark.asyncio
    async def test_create_safety_plan(self):
        """Test safety plan creation."""
        plan = await self.planner.create_safety_plan(
            user_id="test_user_123",
            warning_signs=["Мысли о суициде усиливаются", "Чувствую безнадежность"],
            coping_strategies=["Дыхательные техники", "Звонок другу"],
            reasons_for_living=["Мои дети", "Хочу увидеть их счастливыми"],
            safe_people=[{"name": "Иван", "phone": "+7-XXX-XXX-XXXX"}],
            safe_places=["Дом друга", "Парк рядом"]
        )

        assert plan.user_id == "test_user_123"
        assert len(plan.warning_signs) == 2
        assert len(plan.coping_strategies) == 2
        assert len(plan.crisis_hotlines) > 0  # Default hotlines added
        assert plan.active is True

    @pytest.mark.asyncio
    async def test_create_safety_contract(self):
        """Test safety contract creation."""
        contract = await self.planner.create_safety_contract(
            user_id="test_user_123",
            commitment_type="no_harm"
        )

        assert contract.user_id == "test_user_123"
        assert "обещаю" in contract.contract_text.lower()
        assert contract.active is True

    def test_get_default_coping_strategies(self):
        """Test retrieval of default coping strategies."""
        strategies = self.planner.get_default_coping_strategies(language="russian")

        assert len(strategies) > 5
        assert any("дыхание" in s.lower() for s in strategies)

    def test_get_crisis_hotlines(self):
        """Test retrieval of crisis hotlines."""
        hotlines = self.planner.get_crisis_hotlines(country="russia")

        assert len(hotlines) > 0
        assert any("8-800-2000-122" in h["phone"] for h in hotlines)


class TestCrisisDetectorIntegration:
    """Test integration of crisis detector with new protocols."""

    def setup_method(self):
        """Setup test environment."""
        self.detector = CrisisDetector()

    @pytest.mark.asyncio
    async def test_high_risk_detection_and_stratification(self):
        """Test end-to-end high risk detection and stratification."""
        await self.detector.initialize()

        text = "Не хочу больше жить. У меня есть таблетки, приму их сегодня вечером."

        assessment = await self.detector.analyze_risk_factors(text)

        assert assessment["suicide_risk"] is True
        assert assessment["risk_level"] == RiskLevel.HIGH.value
        assert assessment["immediate_intervention_required"] is True
        assert assessment["crisis_protocol_type"] == "high_risk"

    @pytest.mark.asyncio
    async def test_violence_threat_differentiation(self):
        """Test differentiation of violence threats."""
        await self.detector.initialize()

        # Emotional discharge
        text1 = "Хочется убить ее, когда так злюсь! Но не буду, конечно."
        assessment1 = await self.detector.analyze_risk_factors(text1)

        # Genuine threat
        text2 = "Убью ее завтра. Знаю где она."
        assessment2 = await self.detector.analyze_risk_factors(text2)

        assert assessment1["harm_to_others"] is True
        assert assessment2["harm_to_others"] is True

        # Confidence or risk level should differ
        assert assessment2["risk_level"] != "none"

    @pytest.mark.asyncio
    async def test_false_positive_handling(self):
        """Test handling of potential false positives."""
        await self.detector.initialize()

        text = "Не могу жить без своего ребенка. Очень скучаю."

        assessment = await self.detector.analyze_risk_factors(text)

        # Should NOT be classified as high risk (emotional expression, not suicidal)
        assert assessment["risk_level"] in ["none", "low"]


@pytest.mark.asyncio
async def test_comprehensive_scenario_high_risk():
    """Test comprehensive high-risk scenario flow."""
    detector = CrisisDetector()
    planner = SafetyPlanner()

    await detector.initialize()

    # User expresses suicidal ideation with plan
    text = "Покончу с собой сегодня. У меня есть таблетки и веревка. Решил."

    assessment = await detector.analyze_risk_factors(text)

    # Should trigger HIGH RISK
    assert assessment["risk_level"] == RiskLevel.HIGH.value
    assert assessment["immediate_intervention_required"] is True

    # In production, this would trigger:
    # 1. Crisis protocol
    # 2. Safety plan creation (if user responds)
    # 3. Daily monitoring

    # Simulate user responding positively to crisis protocol
    plan = await planner.create_safety_plan(
        user_id="test_user",
        warning_signs=["Мысли о суициде", "Одиночество"],
        coping_strategies=["Позвонить на линию", "Дыхательные техники"],
        reasons_for_living=["Мой ребенок"],
        safe_people=[{"name": "Friend", "phone": "123"}],
        safe_places=["Home"]
    )

    assert plan.active is True
    assert len(plan.crisis_hotlines) > 0


@pytest.mark.asyncio
async def test_comprehensive_scenario_emotional_discharge():
    """Test comprehensive emotional discharge scenario."""
    assessor = ViolenceThreatAssessor()

    # User vents anger but no genuine threat
    text = "Так злюсь на него! Хочется убить! Но просто говорю, не на самом деле."

    result = await assessor.assess_violence_threat(text)

    assert result.threat_type == "emotional_discharge"
    assert len(result.protective_factors) > 0

    # In production, this would:
    # 1. Acknowledge emotions
    # 2. Offer coping techniques (IFS, NVC)
    # 3. No crisis protocol escalation
