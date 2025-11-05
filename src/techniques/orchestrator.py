"""Technique Orchestrator for selecting and applying appropriate therapeutic techniques."""

from typing import Dict, Any, Optional, List
from enum import Enum

from src.techniques.base import Technique, TechniqueResult, DistressLevel
from src.techniques.motivational_interviewing import MotivationalInterviewing
from src.techniques.ifs_parts_work import IFSPartsWork
from src.techniques.cbt import CBTReframing
from src.techniques.grounding import GroundingTechnique
from src.techniques.active_listening import ActiveListening
from src.techniques.supervisor_agent import SupervisorAgent
from src.core.logger import get_logger


logger = get_logger(__name__)


class EmotionalState(Enum):
    """Emotional states for technique selection."""
    SHOCK = "shock"
    RAGE = "rage"
    DESPAIR = "despair"
    GUILT = "guilt"
    BARGAINING = "bargaining"
    OBSESSIVE_FIGHTING = "obsessive_fighting"
    ACCEPTANCE = "acceptance"
    NEUTRAL = "neutral"


class TechniqueOrchestrator:
    """
    Orchestrates selection and application of therapeutic techniques.

    Responsibilities:
    1. Select appropriate technique based on context
    2. Apply technique
    3. Run through Supervisor Agent for quality control
    4. Return validated response

    Technique selection strategy:
    - CRISIS → Crisis protocol (not therapeutic technique)
    - HIGH distress + RAGE → IFS Parts Work or Grounding
    - MODERATE distress + Ambivalence → Motivational Interviewing
    - Cognitive distortions → CBT Reframing
    - General support → Active Listening
    """

    def __init__(self):
        """Initialize orchestrator with all techniques."""
        # Initialize all techniques
        self.techniques: Dict[str, Technique] = {
            "motivational_interviewing": MotivationalInterviewing(),
            "ifs_parts_work": IFSPartsWork(),
            "cbt_reframing": CBTReframing(),
            "grounding": GroundingTechnique(),
            "active_listening": ActiveListening()
        }

        # Initialize supervisor
        self.supervisor = SupervisorAgent()

        # Technique priority by emotional state
        self.technique_priority = {
            EmotionalState.SHOCK: ["grounding", "active_listening"],
            EmotionalState.RAGE: ["ifs_parts_work", "grounding"],
            EmotionalState.DESPAIR: ["active_listening", "cbt_reframing", "motivational_interviewing"],
            EmotionalState.GUILT: ["cbt_reframing", "ifs_parts_work"],
            EmotionalState.BARGAINING: ["motivational_interviewing", "active_listening"],
            EmotionalState.OBSESSIVE_FIGHTING: ["ifs_parts_work", "cbt_reframing"],
            EmotionalState.ACCEPTANCE: ["motivational_interviewing", "active_listening"],
            EmotionalState.NEUTRAL: ["active_listening", "motivational_interviewing"]
        }

    async def select_and_apply_technique(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """
        Select and apply appropriate technique.

        Args:
            user_message: User's message
            context: Context including emotion, distress level, etc.

        Returns:
            TechniqueResult from selected technique
        """
        # Extract context
        distress_level = self._determine_distress_level(context)
        emotional_state = self._determine_emotional_state(context)

        # Select technique
        selected_technique = self._select_technique(
            distress_level,
            emotional_state,
            user_message,
            context
        )

        logger.info(
            "technique_selected",
            technique=selected_technique.name,
            distress_level=distress_level.value,
            emotional_state=emotional_state.value
        )

        # Apply technique
        result = await selected_technique.apply(user_message, context)

        # Supervise response
        supervision = await self.supervisor.supervise_response(
            result.response,
            user_message,
            context
        )

        if not supervision.approved:
            logger.warning(
                "response_rejected_by_supervisor",
                technique=selected_technique.name,
                issues=supervision.critical_issues
            )

            # Fallback to safe response
            result = await self._generate_safe_fallback(user_message, context)

        # Add supervision metadata
        result.metadata = result.metadata or {}
        result.metadata.update({
            "technique_used": selected_technique.name,
            "supervision_score": supervision.overall_score,
            "supervision_approved": supervision.approved
        })

        return result

    def _determine_distress_level(self, context: Dict[str, Any]) -> DistressLevel:
        """Determine distress level from context."""
        # Check risk level first
        risk_level = context.get("risk_level", "none")
        if risk_level == "critical":
            return DistressLevel.CRISIS
        elif risk_level == "high":
            return DistressLevel.HIGH
        elif risk_level == "moderate":
            return DistressLevel.MODERATE
        elif risk_level == "low":
            return DistressLevel.LOW

        # Check emotion intensity
        emotion_intensity = context.get("emotion_intensity", 0.5)
        if emotion_intensity > 0.8:
            return DistressLevel.HIGH
        elif emotion_intensity > 0.5:
            return DistressLevel.MODERATE
        else:
            return DistressLevel.LOW

    def _determine_emotional_state(self, context: Dict[str, Any]) -> EmotionalState:
        """Determine emotional state from context."""
        emotion = context.get("emotion", "neutral")

        emotion_map = {
            "anger": EmotionalState.RAGE,
            "rage": EmotionalState.RAGE,
            "sadness": EmotionalState.DESPAIR,
            "despair": EmotionalState.DESPAIR,
            "guilt": EmotionalState.GUILT,
            "shame": EmotionalState.GUILT,
            "shock": EmotionalState.SHOCK,
            "acceptance": EmotionalState.ACCEPTANCE
        }

        return emotion_map.get(emotion, EmotionalState.NEUTRAL)

    def _select_technique(
        self,
        distress_level: DistressLevel,
        emotional_state: EmotionalState,
        user_message: str,
        context: Dict[str, Any]
    ) -> Technique:
        """
        Select appropriate technique.

        Selection strategy:
        1. Check emotional state priorities
        2. Check technique appropriateness for distress level
        3. Fallback to active listening
        """
        # Get priority techniques for emotional state
        priority_techniques = self.technique_priority.get(
            emotional_state,
            ["active_listening"]
        )

        # Try each priority technique
        for technique_name in priority_techniques:
            technique = self.techniques.get(technique_name)
            if technique and technique.is_appropriate(distress_level, context):
                return technique

        # Fallback to active listening
        return self.techniques["active_listening"]

    async def _generate_safe_fallback(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """Generate safe fallback response when supervision fails."""
        language = context.get("language", "russian")

        if language == "russian":
            response = """Я слышу, что вам сейчас очень тяжело.

Ваши чувства важны, и я здесь, чтобы поддержать вас.

Давайте сделаем паузу и просто поговорим о том, что вы сейчас чувствуете. Что для вас наиболее тяжело прямо сейчас?"""
        else:
            response = """I hear that this is very difficult for you right now.

Your feelings matter, and I'm here to support you.

Let's take a pause and just talk about what you're feeling. What's most difficult for you right now?"""

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=None,
            recommended_next_step="continue_dialogue",
            metadata={"technique": "safe_fallback", "supervision_triggered": True}
        )

    def get_available_techniques(self) -> List[Dict[str, Any]]:
        """Get list of available techniques."""
        return [
            technique.get_info()
            for technique in self.techniques.values()
        ]

    async def apply_specific_technique(
        self,
        technique_name: str,
        user_message: str,
        context: Dict[str, Any]
    ) -> Optional[TechniqueResult]:
        """Apply specific technique by name."""
        technique = self.techniques.get(technique_name)
        if not technique:
            logger.error("technique_not_found", technique_name=technique_name)
            return None

        result = await technique.apply(user_message, context)
        return result
