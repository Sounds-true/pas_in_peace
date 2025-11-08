"""Crisis detection using SuicidalBERT and other safety models."""

from typing import Tuple, Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from src.core.logger import get_logger, log_safety_event
from src.core.config import settings


logger = get_logger(__name__)


class CrisisDetector:
    """Detects crisis situations in user messages."""

    def __init__(self):
        """Initialize crisis detector."""
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        # Using keyword-based detection for MVP (gated models require HF auth)
        self.model_name = None  # "mental/mental-bert-base-uncased" requires HF auth

        # Crisis keywords for quick detection (Russian and English)
        self.crisis_keywords = [
            # Russian
            "убить себя", "покончить с собой", "не хочу жить",
            "самоубийство", "суицид", "конец всему",
            "лучше умереть", "нет смысла жить",
            # English
            "kill myself", "end it all", "suicide",
            "don't want to live", "better off dead",
            "no point living", "want to die"
        ]

    async def initialize(self) -> None:
        """Load the crisis detection model."""
        # For MVP: using keyword-based detection only
        # ML model requires HuggingFace authentication for gated repos
        logger.info("crisis_detector_initialized", mode="keyword-based")
        self.model = None  # Will use keyword matching only

    def _load_model(self) -> None:
        """Load model synchronously."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.eval()

    def _quick_keyword_check(self, text: str) -> bool:
        """Quick keyword-based crisis detection."""
        text_lower = text.lower()
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                return True
        return False

    def _run_model_inference(self, text: str) -> Tuple[bool, float]:
        """Run model inference synchronously."""
        if not self.model or not self.tokenizer:
            # Fallback to keyword detection
            is_crisis = self._quick_keyword_check(text)
            confidence = 0.9 if is_crisis else 0.1
            return is_crisis, confidence

        try:
            # Tokenize and run inference
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

                # Assuming binary classification (0: safe, 1: crisis)
                crisis_prob = probabilities[0][1].item() if probabilities.shape[1] > 1 else probabilities[0][0].item()

                is_crisis = crisis_prob > settings.suicidalbert_threshold
                return is_crisis, crisis_prob

        except Exception as e:
            logger.error("model_inference_failed", error=str(e))
            # Fallback to keyword detection
            is_crisis = self._quick_keyword_check(text)
            confidence = 0.9 if is_crisis else 0.1
            return is_crisis, confidence

    async def detect(self, text: str) -> Tuple[bool, float]:
        """
        Detect crisis in text.

        Returns:
            Tuple of (is_crisis, confidence_score)
        """
        # Quick keyword check first
        if self._quick_keyword_check(text):
            logger.warning("crisis_keyword_detected", text_length=len(text))
            return True, 0.95

        # Run model inference
        loop = asyncio.get_event_loop()
        is_crisis, confidence = await loop.run_in_executor(
            self.executor,
            self._run_model_inference,
            text
        )

        if is_crisis:
            logger.warning(
                "crisis_detected",
                confidence=confidence,
                text_length=len(text)
            )

        return is_crisis, confidence

    async def analyze_risk_factors(
        self,
        text: str,
        user_history: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple risk factors using Columbia-SSRS stratification.

        Args:
            text: User message
            user_history: User's historical context

        Returns:
            Comprehensive risk assessment with stratification
        """
        from src.safety.risk_stratifier import (
            RiskStratifier,
            SuicidalRiskAssessment,
            IdeationType
        )
        from src.safety.violence_threat_assessor import ViolenceThreatAssessor
        from datetime import datetime

        # Initialize stratifier and violence assessor
        stratifier = RiskStratifier()
        violence_assessor = ViolenceThreatAssessor()

        # Check for suicidal risk
        is_crisis, confidence = await self.detect(text)

        suicidal_assessment = None
        if is_crisis or self._quick_keyword_check(text):
            # Determine ideation type
            ideation_type = self._determine_ideation_type(text)

            # Check for plan, means, intent, timeline
            has_plan = self._check_plan(text)
            has_means = self._check_means(text)
            has_intent = self._check_intent(text)
            has_timeline = self._check_timeline(text)

            # Extract protective and risk factors
            protective_factors = stratifier.extract_protective_factors(text)
            risk_factors = stratifier.extract_risk_factors(text)

            suicidal_assessment = SuicidalRiskAssessment(
                risk_present=True,
                ideation_type=ideation_type,
                has_plan=has_plan,
                has_means=has_means,
                has_intent=has_intent,
                has_timeline=has_timeline,
                protective_factors=protective_factors,
                risk_factors=risk_factors,
                keywords_matched=self._get_matched_keywords(text),
                confidence=confidence,
                assessment_timestamp=datetime.now()
            )

        # Check for violence threat
        violence_assessment = await violence_assessor.assess_violence_threat(
            text,
            user_history
        )

        # Check for child harm (basic implementation)
        child_harm_assessment = self._assess_child_harm(text)

        # Stratify overall risk
        comprehensive_assessment = stratifier.stratify_risk(
            suicidal_assessment=suicidal_assessment,
            violence_assessment=violence_assessment,
            child_harm_assessment=child_harm_assessment,
            user_history=user_history
        )

        # Convert to legacy format for backward compatibility
        risk_assessment = {
            "suicide_risk": suicidal_assessment is not None and suicidal_assessment.risk_present,
            "self_harm_risk": False,  # TODO: Implement self-harm detection
            "harm_to_others": violence_assessment.violence_risk_present if violence_assessment else False,
            "substance_abuse": False,  # TODO: Implement substance abuse detection
            "severe_depression": False,  # TODO: Implement depression screening
            "confidence_scores": {
                "suicide": confidence if suicidal_assessment else 0.0,
                "violence": violence_assessment.confidence if violence_assessment else 0.0
            },
            "recommended_action": comprehensive_assessment.recommended_action,
            "risk_level": comprehensive_assessment.risk_level.value,
            "crisis_protocol_type": comprehensive_assessment.crisis_protocol_type,
            "monitoring_frequency": comprehensive_assessment.monitoring_frequency,
            "immediate_intervention_required": comprehensive_assessment.immediate_intervention_required,
            "reasoning": comprehensive_assessment.reasoning
        }

        logger.info(
            "comprehensive_risk_assessment_complete",
            risk_level=comprehensive_assessment.risk_level.value,
            immediate_intervention=comprehensive_assessment.immediate_intervention_required
        )

        return risk_assessment

    def _determine_ideation_type(self, text: str):
        """Determine type of suicidal ideation."""
        from src.safety.risk_stratifier import IdeationType

        text_lower = text.lower()

        # Active with plan (most severe)
        plan_keywords = ["план", "планирую", "собираюсь", "сегодня", "завтра", "plan", "planning", "going to"]
        intent_keywords = ["покончу", "убью себя", "сделаю это", "решил", "will do it", "decided"]

        has_plan_indicator = any(kw in text_lower for kw in plan_keywords)
        has_intent_indicator = any(kw in text_lower for kw in intent_keywords)

        if has_plan_indicator and has_intent_indicator:
            return IdeationType.ACTIVE_WITH_PLAN

        if has_intent_indicator:
            return IdeationType.ACTIVE_WITH_INTENT

        # Active with method
        method_keywords = ["таблетки", "нож", "петля", "оружие", "pills", "knife", "rope", "gun"]
        if any(kw in text_lower for kw in method_keywords):
            return IdeationType.ACTIVE_WITH_METHOD

        # Active ideation (no intent)
        active_keywords = ["убить себя", "суицид", "самоубийство", "suicide", "kill myself"]
        if any(kw in text_lower for kw in active_keywords):
            return IdeationType.ACTIVE_NO_INTENT

        # Passive ideation
        passive_keywords = ["не хочу жить", "лучше умереть", "хочу умереть", "don't want to live", "wish I was dead"]
        if any(kw in text_lower for kw in passive_keywords):
            return IdeationType.PASSIVE

        return IdeationType.NONE

    def _check_plan(self, text: str) -> bool:
        """Check if user has a specific plan."""
        plan_keywords = ["план", "планирую", "собираюсь", "сделаю", "приму", "plan", "will", "going to"]
        return any(kw in text.lower() for kw in plan_keywords)

    def _check_means(self, text: str) -> bool:
        """Check if means are available."""
        means_keywords = [
            "таблетки", "лекарства", "нож", "веревка", "оружие", "пистолет",
            "pills", "medication", "knife", "rope", "gun", "weapon"
        ]
        return any(kw in text.lower() for kw in means_keywords)

    def _check_intent(self, text: str) -> bool:
        """Check if user has intent to act."""
        intent_keywords = ["решил", "покончу", "сделаю это", "хочу умереть", "decided", "will do it", "want to die"]
        return any(kw in text.lower() for kw in intent_keywords)

    def _check_timeline(self, text: str) -> bool:
        """Check if imminent timeframe is mentioned."""
        timeline_keywords = ["сегодня", "сейчас", "завтра", "tonight", "today", "now", "tomorrow", "soon"]
        return any(kw in text.lower() for kw in timeline_keywords)

    def _get_matched_keywords(self, text: str) -> list:
        """Get list of matched crisis keywords."""
        text_lower = text.lower()
        matched = []
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                matched.append(keyword)
        return matched

    def _assess_child_harm(self, text: str):
        """Basic child harm assessment."""
        from src.safety.risk_stratifier import ChildHarmAssessment

        text_lower = text.lower()

        child_harm_keywords = [
            "ребенок умер", "ребенок страдал", "ребёнок умер", "убить ребенка",
            "child dies", "child suffers", "kill child", "harm child"
        ]

        child_risk = any(kw in text_lower for kw in child_harm_keywords)

        if child_risk:
            severity = "high"
            confidence = 0.8
        else:
            severity = "none"
            confidence = 0.1

        return ChildHarmAssessment(
            child_harm_risk_present=child_risk,
            severity=severity,
            specific_threat=child_risk,
            confidence=confidence
        )

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        self.model = None
        self.tokenizer = None