"""Crisis detection using SuicidalBERT and other safety models."""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple, Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

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

    async def analyze_risk_factors(self, text: str) -> Dict[str, Any]:
        """
        Analyze multiple risk factors in the text.

        Returns detailed risk assessment.
        """
        risk_assessment = {
            "suicide_risk": False,
            "self_harm_risk": False,
            "harm_to_others": False,
            "substance_abuse": False,
            "severe_depression": False,
            "confidence_scores": {},
            "recommended_action": "continue_monitoring"
        }

        # Check for various risk factors
        is_crisis, confidence = await self.detect(text)

        if is_crisis:
            risk_assessment["suicide_risk"] = True
            risk_assessment["confidence_scores"]["suicide"] = confidence

            if confidence > 0.9:
                risk_assessment["recommended_action"] = "immediate_intervention"
            elif confidence > 0.7:
                risk_assessment["recommended_action"] = "escalate_to_crisis_protocol"
            else:
                risk_assessment["recommended_action"] = "increase_monitoring"

        # Check for harm to others
        harm_keywords = ["убью", "причиню вред", "отомщу", "kill", "hurt", "revenge"]
        text_lower = text.lower()
        for keyword in harm_keywords:
            if keyword in text_lower:
                risk_assessment["harm_to_others"] = True
                risk_assessment["confidence_scores"]["harm_to_others"] = 0.8
                risk_assessment["recommended_action"] = "escalate_to_crisis_protocol"
                break

        return risk_assessment

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        self.model = None
        self.tokenizer = None