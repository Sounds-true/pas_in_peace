"""NLP module for emotion detection and text analysis."""

from .emotion_detector import EmotionDetector
from .pii_protector import PIIProtector
from .entity_extractor import EntityExtractor, Entity, ExtractedContext
from .intent_classifier import IntentClassifier, Intent, IntentResult
from .speech_handler import SpeechHandler, TranscriptionResult

__all__ = [
    "EmotionDetector",
    "PIIProtector",
    "EntityExtractor",
    "Entity",
    "ExtractedContext",
    "IntentClassifier",
    "Intent",
    "IntentResult",
    "SpeechHandler",
    "TranscriptionResult",
]