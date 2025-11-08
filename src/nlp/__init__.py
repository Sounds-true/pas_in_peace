"""NLP module for emotion detection and text analysis."""

# NOTE: Heavy ML modules temporarily disabled (see DEVELOPMENT_ROADMAP.md)
# They cause initialization hangs due to model loading
# from .emotion_detector import EmotionDetector
# from .pii_protector import PIIProtector  # Replaced with SimplePIIProtector
# from .entity_extractor import EntityExtractor, Entity, ExtractedContext
# from .intent_classifier import IntentClassifier, Intent, IntentResult
# from .speech_handler import SpeechHandler, TranscriptionResult

# Lightweight modules (no ML dependencies)
from .simple_pii_protector import SimplePIIProtector

__all__ = [
    # "EmotionDetector",  # Disabled
    # "PIIProtector",  # Disabled
    "SimplePIIProtector",  # NEW: Lightweight replacement
    # "EntityExtractor",  # Disabled
    # "Entity",  # Disabled
    # "ExtractedContext",  # Disabled
    # "IntentClassifier",  # Disabled
    # "Intent",  # Disabled
    # "IntentResult",  # Disabled
    # "SpeechHandler",  # Disabled
    # "TranscriptionResult",  # Disabled
]