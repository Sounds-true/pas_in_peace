"""Base class for therapeutic techniques."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TechniqueCategory(str, Enum):
    """Categories of therapeutic techniques."""
    CBT = "cognitive_behavioral"
    GROUNDING = "grounding"
    VALIDATION = "validation"
    ACTIVE_LISTENING = "active_listening"
    EMOTION_REGULATION = "emotion_regulation"
    MINDFULNESS = "mindfulness"


class DistressLevel(str, Enum):
    """Distress levels for technique selection."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRISIS = "crisis"


@dataclass
class TechniqueResult:
    """Result of applying a technique."""
    success: bool
    response: str
    follow_up: Optional[str] = None
    recommended_next_step: Optional[str] = None
    metadata: Dict[str, Any] = None


class Technique(ABC):
    """
    Base class for all therapeutic techniques.

    Each technique must implement:
    - apply(): Execute the technique
    - is_appropriate(): Check if technique is suitable for current context
    """

    def __init__(self):
        """Initialize the technique."""
        self.name: str = "Base Technique"
        self.category: TechniqueCategory = TechniqueCategory.CBT
        self.description: str = ""
        self.suitable_for_distress: list[DistressLevel] = []

    @abstractmethod
    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """
        Apply the therapeutic technique.

        Args:
            user_message: The user's current message
            context: Additional context (emotion, distress level, etc.)

        Returns:
            TechniqueResult with response and metadata
        """
        raise NotImplementedError

    def is_appropriate(
        self,
        distress_level: DistressLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if this technique is appropriate for the current situation.

        Args:
            distress_level: Current user distress level
            context: Additional context

        Returns:
            True if technique is appropriate
        """
        return distress_level in self.suitable_for_distress

    def get_info(self) -> Dict[str, Any]:
        """
        Get technique information.

        Returns:
            Dict with technique metadata
        """
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "suitable_for": [level.value for level in self.suitable_for_distress]
        }
