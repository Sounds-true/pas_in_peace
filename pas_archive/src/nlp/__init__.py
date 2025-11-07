"""NLP module for emotion detection and text analysis."""

from .emotion_detector import EmotionDetector
from .pii_protector import PIIProtector

__all__ = ["EmotionDetector", "PIIProtector"]