"""State management using LangGraph."""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

from src.core.logger import get_logger
from src.core.config import settings
from src.safety.guardrails_manager import GuardrailsManager


logger = get_logger(__name__)


class ConversationState(str, Enum):
    """Conversation states."""
    START = "start"
    EMOTION_CHECK = "emotion_check"
    CRISIS_INTERVENTION = "crisis_intervention"
    HIGH_DISTRESS = "high_distress"
    MODERATE_SUPPORT = "moderate_support"
    CASUAL_CHAT = "casual_chat"
    LETTER_WRITING = "letter_writing"
    GOAL_TRACKING = "goal_tracking"
    TECHNIQUE_SELECTION = "technique_selection"
    TECHNIQUE_EXECUTION = "technique_execution"
    END_SESSION = "end_session"


class TherapyPhase(str, Enum):
    """Therapy phases."""
    CRISIS = "crisis"
    UNDERSTANDING = "understanding"
    ACTION = "action"
    SUSTAINABILITY = "sustainability"


@dataclass
class UserState:
    """User state information."""
    user_id: str
    current_state: ConversationState = ConversationState.START
    therapy_phase: TherapyPhase = TherapyPhase.UNDERSTANDING
    emotional_score: float = 0.5  # 0-1 scale
    crisis_level: float = 0.0  # 0-1 scale
    messages_count: int = 0
    session_start: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    message_history: List[BaseMessage] = field(default_factory=list)
    active_goals: List[Dict[str, Any]] = field(default_factory=list)
    completed_techniques: List[str] = field(default_factory=list)


class StateManager:
    """Manages conversation states using LangGraph."""

    def __init__(self):
        """Initialize state manager."""
        self.user_states: Dict[str, UserState] = {}
        self.graph: Optional[StateGraph] = None
        self.guardrails = GuardrailsManager()
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the state graph and dependencies."""
        try:
            # Try to initialize guardrails (optional for MVP)
            try:
                await self.guardrails.initialize()
                logger.info("guardrails_enabled")
            except Exception as e:
                logger.warning("guardrails_disabled", reason=str(e))
                self.guardrails = None

            # Build the state graph
            self.graph = self._build_state_graph()

            self.initialized = True
            logger.info("state_manager_initialized")

        except Exception as e:
            logger.error("state_manager_init_failed", error=str(e))
            raise

    def _build_state_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        # Create the graph
        workflow = StateGraph(Dict[str, Any])

        # Add nodes for each state
        workflow.add_node("start", self._handle_start)
        workflow.add_node("emotion_check", self._handle_emotion_check)
        workflow.add_node("crisis_intervention", self._handle_crisis)
        workflow.add_node("high_distress", self._handle_high_distress)
        workflow.add_node("moderate_support", self._handle_moderate_support)
        workflow.add_node("casual_chat", self._handle_casual_chat)
        workflow.add_node("letter_writing", self._handle_letter_writing)
        workflow.add_node("goal_tracking", self._handle_goal_tracking)
        workflow.add_node("technique_selection", self._handle_technique_selection)
        workflow.add_node("technique_execution", self._handle_technique_execution)
        workflow.add_node("end_session", self._handle_end_session)

        # Set entry point
        workflow.set_entry_point("start")

        # Add edges (transitions)
        workflow.add_edge("start", "emotion_check")

        # Conditional edges based on emotion check
        workflow.add_conditional_edges(
            "emotion_check",
            self._route_after_emotion_check,
            {
                "crisis": "crisis_intervention",
                "high": "high_distress",
                "moderate": "moderate_support",
                "low": "casual_chat"
            }
        )

        # Crisis flow
        workflow.add_edge("crisis_intervention", "high_distress")

        # High distress flow
        workflow.add_conditional_edges(
            "high_distress",
            self._route_after_high_distress,
            {
                "technique": "technique_selection",
                "reassess": "emotion_check"
            }
        )

        # Moderate support flow
        workflow.add_conditional_edges(
            "moderate_support",
            self._route_after_moderate_support,
            {
                "technique": "technique_selection",
                "letter": "letter_writing",
                "goals": "goal_tracking",
                "continue": "emotion_check"
            }
        )

        # Casual chat flow
        workflow.add_conditional_edges(
            "casual_chat",
            self._route_after_casual_chat,
            {
                "emotion_shift": "emotion_check",
                "end": "end_session",
                "continue": "casual_chat"
            }
        )

        # Technique flow
        workflow.add_edge("technique_selection", "technique_execution")
        workflow.add_conditional_edges(
            "technique_execution",
            self._route_after_technique,
            {
                "success": "moderate_support",
                "retry": "technique_selection"
            }
        )

        # Letter writing flow
        workflow.add_edge("letter_writing", "moderate_support")

        # Goal tracking flow
        workflow.add_edge("goal_tracking", "moderate_support")

        # End session
        workflow.add_edge("end_session", END)

        return workflow.compile()

    async def initialize_user(self, user_id: str) -> None:
        """Initialize a new user state."""
        self.user_states[user_id] = UserState(user_id=user_id)
        logger.info("user_initialized", user_id=user_id)

    async def get_user_state(self, user_id: str) -> Optional[UserState]:
        """Get user state."""
        return self.user_states.get(user_id)

    async def transition_to_crisis(self, user_id: str) -> None:
        """Immediately transition user to crisis state."""
        user_state = self.user_states.get(user_id)
        if user_state:
            user_state.current_state = ConversationState.CRISIS_INTERVENTION
            user_state.crisis_level = 1.0
            user_state.therapy_phase = TherapyPhase.CRISIS
            logger.warning("user_crisis_transition", user_id=user_id)

    async def process_message(self, user_id: str, message: str) -> str:
        """Process user message through the state machine."""
        if not self.initialized:
            await self.initialize()

        # Get or create user state
        user_state = self.user_states.get(user_id)
        if not user_state:
            await self.initialize_user(user_id)
            user_state = self.user_states[user_id]

        # Update user state
        user_state.last_activity = datetime.now()
        user_state.messages_count += 1
        user_state.message_history.append(HumanMessage(content=message))

        # Check guardrails
        guardrail_check = await self.guardrails.check_message(message, {"user_id": user_id})
        if not guardrail_check["allowed"]:
            logger.warning(
                "message_blocked_by_guardrails",
                user_id=user_id,
                policy=guardrail_check["triggered_policy"]
            )
            return guardrail_check["response"]

        # Process through state graph
        try:
            # Prepare state for graph
            graph_state = {
                "user_id": user_id,
                "message": message,
                "user_state": user_state,
                "timestamp": datetime.now().isoformat()
            }

            # Run the graph
            result = await self.graph.ainvoke(graph_state)

            # Extract response
            response = result.get("response", "I'm here to support you. How can I help?")

            # Apply guardrails to response
            safe_response = await self.guardrails.generate_safe_response(
                message, response, {"user_id": user_id}
            )

            # Update message history
            user_state.message_history.append(SystemMessage(content=safe_response))

            return safe_response

        except Exception as e:
            logger.error("message_processing_failed", user_id=user_id, error=str(e))
            return "I apologize, I'm having trouble processing your message. Please try again."

    # State handlers
    async def _handle_start(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start state."""
        state["response"] = "Let's begin. How are you feeling today?"
        return state

    async def _handle_emotion_check(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emotion check state."""
        # This would integrate with emotion detection models
        user_state = state["user_state"]

        # Placeholder emotion detection
        message = state["message"].lower()
        if any(word in message for word in ["terrible", "awful", "can't cope", "ужасно", "не могу"]):
            user_state.emotional_score = 0.2
            user_state.crisis_level = 0.7
        elif any(word in message for word in ["sad", "lonely", "difficult", "грустно", "одиноко"]):
            user_state.emotional_score = 0.4
            user_state.crisis_level = 0.3
        else:
            user_state.emotional_score = 0.6
            user_state.crisis_level = 0.1

        state["emotion_assessed"] = True
        return state

    async def _handle_crisis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle crisis intervention."""
        state["response"] = (
            "I'm deeply concerned about what you're sharing. Your safety is paramount. "
            f"Please reach out to the crisis hotline at {settings.crisis_hotline_ru} "
            "for immediate support. I'm here to listen if you want to talk about what's troubling you."
        )
        return state

    async def _handle_high_distress(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle high distress state."""
        state["response"] = (
            "I can sense you're going through something very difficult. "
            "Let's take this one step at a time. Would you like to try a grounding exercise, "
            "or would you prefer to tell me more about what's happening?"
        )
        return state

    async def _handle_moderate_support(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle moderate support state."""
        state["response"] = (
            "Thank you for sharing. I'm here to support you. "
            "Would you like to explore your feelings further, work on a letter, "
            "or perhaps set some goals for moving forward?"
        )
        return state

    async def _handle_casual_chat(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle casual chat state."""
        state["response"] = "I'm glad to chat with you. What's on your mind?"
        return state

    async def _handle_letter_writing(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle letter writing state."""
        state["response"] = (
            "Let's work on a letter together. "
            "Who would you like to write to, and what's the main message you want to convey?"
        )
        return state

    async def _handle_goal_tracking(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle goal tracking state."""
        state["response"] = "Let's review your goals. What would you like to focus on?"
        return state

    async def _handle_technique_selection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle technique selection state."""
        state["selected_technique"] = "cognitive_reframing"  # Placeholder
        state["response"] = "Let's try a cognitive reframing exercise."
        return state

    async def _handle_technique_execution(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle technique execution state."""
        technique = state.get("selected_technique", "active_listening")
        state["response"] = f"Applying {technique} technique..."
        return state

    async def _handle_end_session(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle end session state."""
        state["response"] = (
            "Thank you for our conversation today. "
            "Remember, I'm here whenever you need support. Take care."
        )
        return state

    # Routing functions
    def _route_after_emotion_check(self, state: Dict[str, Any]) -> str:
        """Route after emotion check."""
        user_state = state["user_state"]
        if user_state.crisis_level > 0.7:
            return "crisis"
        elif user_state.emotional_score < 0.3:
            return "high"
        elif user_state.emotional_score < 0.6:
            return "moderate"
        else:
            return "low"

    def _route_after_high_distress(self, state: Dict[str, Any]) -> str:
        """Route after high distress handling."""
        message = state["message"].lower()
        if "exercise" in message or "technique" in message:
            return "technique"
        return "reassess"

    def _route_after_moderate_support(self, state: Dict[str, Any]) -> str:
        """Route after moderate support."""
        message = state["message"].lower()
        if "letter" in message or "письмо" in message:
            return "letter"
        elif "goal" in message or "цель" in message:
            return "goals"
        elif any(word in message for word in ["technique", "exercise", "help me", "техника"]):
            return "technique"
        return "continue"

    def _route_after_casual_chat(self, state: Dict[str, Any]) -> str:
        """Route after casual chat."""
        message = state["message"].lower()
        if any(word in message for word in ["bye", "goodbye", "пока", "до свидания"]):
            return "end"
        elif any(word in message for word in ["upset", "sad", "расстроен", "грустно"]):
            return "emotion_shift"
        return "continue"

    def _route_after_technique(self, state: Dict[str, Any]) -> str:
        """Route after technique execution."""
        # Placeholder - would check technique effectiveness
        return "success"