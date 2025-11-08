"""Emotion detection using GoEmotions model."""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Tuple, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.core.logger import get_logger
from src.core.config import settings


logger = get_logger(__name__)


class EmotionDetector:
    """Detects emotions in text using GoEmotions classifier."""

    # GoEmotions labels (27 emotions)
    EMOTIONS = [
        'admiration', 'amusement', 'anger', 'annoyance', 'approval',
        'caring', 'confusion', 'curiosity', 'desire', 'disappointment',
        'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear',
        'gratitude', 'grief', 'joy', 'love', 'nervousness',
        'optimism', 'pride', 'realization', 'relief', 'remorse',
        'sadness', 'surprise'
    ]

    # Mapping to therapeutic relevance
    HIGH_DISTRESS_EMOTIONS = ['grief', 'sadness', 'fear', 'anger', 'disappointment', 'remorse']
    MODERATE_DISTRESS_EMOTIONS = ['nervousness', 'annoyance', 'embarrassment', 'confusion']
    POSITIVE_EMOTIONS = ['joy', 'gratitude', 'relief', 'pride', 'optimism', 'excitement']

    def __init__(self):
        """Initialize emotion detector."""
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.model_name = settings.emotion_detection_model  # Russian GoEmotions model

    async def initialize(self) -> None:
        """Load emotion detection model."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._load_model
            )
            logger.info("emotion_detector_initialized", model=self.model_name)
        except Exception as e:
            logger.error("emotion_detector_init_failed", error=str(e))
            raise

    def _load_model(self) -> None:
        """Load model synchronously."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.eval()

    def _run_inference(self, text: str) -> Dict[str, float]:
        """Run emotion classification inference."""
        if not self.model or not self.tokenizer:
            logger.error("model_not_loaded")
            return {}

        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.sigmoid(outputs.logits[0])

            # Map to emotion labels
            emotions = {}
            for idx, emotion in enumerate(self.EMOTIONS):
                if idx < len(probabilities):
                    emotions[emotion] = float(probabilities[idx])

            return emotions

        except Exception as e:
            logger.error("inference_failed", error=str(e))
            return {}

    async def detect_emotions(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Detect emotions in text.

        Args:
            text: Input text
            top_k: Number of top emotions to return

        Returns:
            List of (emotion, confidence) tuples
        """
        loop = asyncio.get_event_loop()
        emotions = await loop.run_in_executor(
            self.executor,
            self._run_inference,
            text
        )

        if not emotions:
            return []

        # Sort by confidence and return top_k
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        return sorted_emotions[:top_k]

    async def assess_emotional_state(self, text: str) -> Dict[str, any]:
        """
        Comprehensive emotional state assessment.

        Returns:
            Dict with emotional assessment details
        """
        emotions = await self.detect_emotions(text, top_k=10)

        if not emotions:
            return {
                "primary_emotion": "neutral",
                "emotional_intensity": 0.5,
                "distress_level": "low",
                "recommended_approach": "supportive"
            }

        # Calculate distress score
        distress_score = 0.0
        high_distress_count = 0
        moderate_distress_count = 0
        positive_count = 0

        for emotion, confidence in emotions:
            if emotion in self.HIGH_DISTRESS_EMOTIONS:
                distress_score += confidence * 1.5
                high_distress_count += 1
            elif emotion in self.MODERATE_DISTRESS_EMOTIONS:
                distress_score += confidence * 0.8
                moderate_distress_count += 1
            elif emotion in self.POSITIVE_EMOTIONS:
                distress_score -= confidence * 0.3
                positive_count += 1

        # Normalize distress score
        distress_score = max(0.0, min(1.0, distress_score / 3.0))

        # Determine distress level
        if distress_score > 0.7:
            distress_level = "high"
            recommended_approach = "intensive_support"
        elif distress_score > 0.4:
            distress_level = "moderate"
            recommended_approach = "active_listening"
        else:
            distress_level = "low"
            recommended_approach = "supportive"

        # Primary emotion
        primary_emotion = emotions[0][0] if emotions else "neutral"
        emotional_intensity = emotions[0][1] if emotions else 0.5

        assessment = {
            "primary_emotion": primary_emotion,
            "all_emotions": dict(emotions),
            "emotional_intensity": emotional_intensity,
            "distress_score": distress_score,
            "distress_level": distress_level,
            "recommended_approach": recommended_approach,
            "emotion_counts": {
                "high_distress": high_distress_count,
                "moderate_distress": moderate_distress_count,
                "positive": positive_count
            }
        }

        logger.info(
            "emotional_assessment",
            primary=primary_emotion,
            distress=distress_level,
            intensity=round(emotional_intensity, 2)
        )

        return assessment

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        self.model = None
        self.tokenizer = None