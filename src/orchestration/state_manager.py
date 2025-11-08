"""State management using LangGraph."""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import asyncio

from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage

from src.core.logger import get_logger
from src.core.config import settings
from src.safety.guardrails_manager import GuardrailsManager
from src.nlp.emotion_detector import EmotionDetector
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.intent_classifier import IntentClassifier, Intent
from src.nlp.speech_handler import SpeechHandler
from src.techniques import (
    CBTReframing,
    GroundingTechnique,
    ValidationTechnique,
    ActiveListening,
    LetterWritingAssistant
)
from src.techniques.orchestrator import TechniqueOrchestrator
from src.rag import KnowledgeRetriever, PAKnowledgeBase
from src.monitoring import MetricsCollector
from src.legal import LegalToolsHandler
from src.storage.database import DatabaseManager
from src.storage.models import ConversationStateEnum, TherapyPhaseEnum
from src.nlp.simple_pii_protector import SimplePIIProtector


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
    LEGAL_CONSULTATION = "legal_consultation"
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

        # Will be initialized in async initialize() method
        self.guardrails = None
        self.emotion_detector = None
        self.entity_extractor = None
        self.intent_classifier = None
        self.speech_handler = None
        self.knowledge_retriever = None

        # Initialize therapeutic techniques (lightweight, no ML)
        self.techniques = {
            "cbt": CBTReframing(),
            "grounding": GroundingTechnique(),
            "validation": ValidationTechnique(),
            "active_listening": ActiveListening(),
            "letter_writing": LetterWritingAssistant()
        }

        # Initialize orchestrator and other lightweight components
        self.technique_orchestrator = TechniqueOrchestrator()
        self.metrics_collector = MetricsCollector()
        self.legal_tools = LegalToolsHandler()
        self.db = DatabaseManager()
        self.pii_protector = SimplePIIProtector()  # NEW: Simple PII protection

        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the state graph and dependencies."""
        try:
            # Initialize database (required for persistence)
            try:
                await self.db.initialize()
                logger.info("database_enabled")
            except Exception as e:
                logger.warning("database_disabled", reason=str(e))
                # Continue without database - will use in-memory only
                self.db = None

            # Try to initialize guardrails (optional for MVP)
            # TEMPORARILY DISABLED - Guardrails causes hanging during initialization
            # try:
            #     await self.guardrails.initialize()
            #     logger.info("guardrails_enabled")
            # except Exception as e:
            #     logger.warning("guardrails_disabled", reason=str(e))
            #     self.guardrails = None
            logger.warning("guardrails_disabled", reason="Temporarily disabled due to initialization issues")
            self.guardrails = None

            # Initialize emotion detector (optional for MVP)
            # TEMPORARILY DISABLED - Emotion Detector causes hanging during model loading
            # try:
            #     await self.emotion_detector.initialize()
            #     logger.info("emotion_detector_enabled")
            # except Exception as e:
            #     logger.warning("emotion_detector_disabled", reason=str(e))
            #     # Continue without emotion detector - will use keyword fallback
            logger.warning("emotion_detector_disabled", reason="Temporarily disabled due to initialization hang")
            self.emotion_detector = None

            # Initialize RAG retriever and load knowledge base
            # TEMPORARILY DISABLED - RAG initialization causes hanging during model loading
            # try:
            #     await self.knowledge_retriever.initialize()
            #     # Load knowledge base documents
            #     documents = PAKnowledgeBase.get_all_documents()
            #     await self.knowledge_retriever.add_documents(documents)
            #     logger.info("knowledge_retriever_enabled", doc_count=len(documents))
            # except Exception as e:
            #     logger.warning("knowledge_retriever_disabled", reason=str(e))
            #     # Continue without RAG - will use only predefined responses
            logger.warning("knowledge_retriever_disabled", reason="Temporarily disabled due to initialization hang")
            self.knowledge_retriever = None

            # Initialize entity extractor (optional)
            # TEMPORARILY DISABLED - Hangs during initialization like other ML components
            # try:
            #     await self.entity_extractor.initialize()
            #     logger.info("entity_extractor_enabled")
            # except Exception as e:
            #     logger.warning("entity_extractor_disabled", reason=str(e))
            #     # Continue without entity extraction - will work without context enrichment
            logger.warning("entity_extractor_disabled", reason="Temporarily disabled due to initialization hang")
            self.entity_extractor = None

            # Initialize intent classifier (optional)
            # TEMPORARILY DISABLED - Hangs during initialization like other ML components
            # try:
            #     await self.intent_classifier.initialize()
            #     logger.info("intent_classifier_enabled")
            # except Exception as e:
            #     logger.warning("intent_classifier_disabled", reason=str(e))
            #     # Continue without intent classification - will use state machine only
            logger.warning("intent_classifier_disabled", reason="Temporarily disabled due to initialization hang")
            self.intent_classifier = None

            # Initialize speech handler (optional)
            # TEMPORARILY DISABLED - Skip to avoid potential initialization hang
            # try:
            #     if self.speech_handler.is_available():
            #         await self.speech_handler.initialize()
            #         logger.info("speech_handler_enabled", backend=self.speech_handler.backend)
            #     else:
            #         logger.warning("speech_handler_unavailable",
            #                       message="Install: pip install SpeechRecognition pydub")
            #         self.speech_handler = None
            # except Exception as e:
            #     logger.warning("speech_handler_disabled", reason=str(e))
            #     self.speech_handler = None
            logger.warning("speech_handler_disabled", reason="Temporarily disabled")
            self.speech_handler = None

            # Build the state graph
            logger.info("about_to_build_state_graph")
            try:
                self.graph = self._build_state_graph()
                logger.info("state_graph_built")
            except Exception as e:
                logger.error("state_graph_build_failed", error=str(e), exc_info=True)
                raise

            self.initialized = True
            logger.info("state_manager_initialized")

        except Exception as e:
            logger.error("state_manager_init_failed", error=str(e))
            raise

    def _build_state_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        logger.info("creating_state_graph_workflow")
        # Create the graph
        workflow = StateGraph(Dict[str, Any])
        logger.info("workflow_created")

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
                "reassess": END  # End conversation, wait for next user message
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
                "continue": "technique_selection"  # Use orchestrator for conversational responses
            }
        )

        # Casual chat flow
        workflow.add_conditional_edges(
            "casual_chat",
            self._route_after_casual_chat,
            {
                "emotion_shift": "emotion_check",
                "end": "end_session",  # Only say goodbye when user explicitly says goodbye
                "continue": "technique_selection"  # Use orchestrator for conversational responses
            }
        )

        # Technique flow
        workflow.add_edge("technique_selection", "technique_execution")
        workflow.add_conditional_edges(
            "technique_execution",
            self._route_after_technique,
            {
                "success": END,  # End after technique to wait for next user message
                "retry": "technique_selection"
            }
        )

        # Letter writing flow
        workflow.add_edge("letter_writing", "moderate_support")

        # Goal tracking flow
        workflow.add_edge("goal_tracking", "moderate_support")

        # End session
        workflow.add_edge("end_session", END)

        logger.info("compiling_workflow")
        compiled = workflow.compile()
        logger.info("workflow_compiled")
        return compiled

    async def initialize_user(self, user_id: str) -> None:
        """Initialize a new user state, loading from database if exists."""
        # Try to load from database first
        if self.db:
            try:
                db_user = await self.db.get_or_create_user(user_id)
                # Convert DB model to UserState
                user_state = UserState(
                    user_id=user_id,
                    current_state=ConversationState(db_user.current_state.value),
                    therapy_phase=TherapyPhase(db_user.therapy_phase.value),
                    emotional_score=db_user.emotional_score,
                    crisis_level=db_user.crisis_level,
                    messages_count=db_user.total_messages,
                    session_start=db_user.created_at,
                    last_activity=db_user.last_activity,
                    context=db_user.context or {},
                )

                # Load message history from database
                logger.debug("loading_message_history", user_id=user_id)
                db_messages = await self.db.load_message_history(user_id, limit=50)
                logger.debug("loaded_messages_from_db", user_id=user_id, count=len(db_messages))

                for db_msg in db_messages:
                    if db_msg.role == "user":
                        user_state.message_history.append(HumanMessage(content=db_msg.content))
                    elif db_msg.role == "assistant":
                        user_state.message_history.append(AIMessage(content=db_msg.content))

                self.user_states[user_id] = user_state
                logger.info("user_loaded_from_db", user_id=user_id,
                           messages_loaded=len(db_messages),
                           history_length=len(user_state.message_history))
                return
            except Exception as e:
                logger.warning("user_load_from_db_failed", user_id=user_id, error=str(e))
                # Fall through to create new in-memory state

        # Create new in-memory state
        self.user_states[user_id] = UserState(user_id=user_id)
        logger.info("user_initialized_in_memory", user_id=user_id)

    async def get_user_state(self, user_id: str) -> Optional[UserState]:
        """Get user state, loading from database if not in cache."""
        # Check in-memory cache first
        if user_id in self.user_states:
            return self.user_states[user_id]

        # Try to load from database
        if self.db:
            try:
                await self.initialize_user(user_id)
                return self.user_states.get(user_id)
            except Exception as e:
                logger.warning("get_user_state_failed", user_id=user_id, error=str(e))

        return None

    async def save_user_state(self, user_state: UserState) -> None:
        """Save user state to database."""
        if not self.db:
            return  # No database available, skip save

        try:
            # Update user in database (includes Bug #1 fix: total_messages)
            await self.db.update_user_state(
                telegram_id=user_state.user_id,
                state=user_state.current_state.value,
                emotional_score=user_state.emotional_score,
                crisis_level=user_state.crisis_level,
                therapy_phase=user_state.therapy_phase.value,
                total_messages=user_state.messages_count,  # NEW: Fix Bug #1
            )
            logger.debug("user_state_saved", user_id=user_state.user_id,
                        total_messages=user_state.messages_count)
        except Exception as e:
            logger.error("user_state_save_failed",
                        user_id=user_state.user_id,
                        error=str(e))
            # Don't raise - continue even if save fails

    async def save_message_to_db(
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save message to database for conversation history persistence."""
        if not self.db:
            return  # No database available, skip save

        try:
            # Get user from database to get internal user ID
            db_user = await self.db.get_or_create_user(user_id)

            # PII Protection: Anonymize content before saving
            # Detect PII and log statistics
            pii_stats = self.pii_protector.get_statistics(content)
            if pii_stats:
                logger.warning("pii_detected_in_message",
                             user_id=user_id,
                             role=role,
                             pii_types=pii_stats)

            # Anonymize sensitive content (keep names for therapy context)
            anonymized_content = self.pii_protector.anonymize(
                content,
                entity_types=["EMAIL", "PHONE", "CREDIT_CARD", "PASSPORT", "SNILS"]
                # Note: PERSON_NAME not anonymized - needed for therapy context
            )

            # Calculate content hash for deduplication
            import hashlib
            content_hash = hashlib.sha256(anonymized_content.encode()).hexdigest()

            # Extract metadata
            metadata = metadata or {}
            detected_emotions = metadata.get("detected_emotions", {})
            emotional_intensity = metadata.get("emotional_intensity", 0.5)
            distress_level = metadata.get("distress_level", "moderate")
            crisis_detected = metadata.get("crisis_detected", False)
            crisis_confidence = metadata.get("crisis_confidence", 0.0)
            guardrail_triggered = metadata.get("guardrail_triggered")
            conversation_state = metadata.get("conversation_state")

            # Save message with PII protection
            await self.db.save_message(
                user_id=db_user.id,
                session_id=None,  # Session tracking not implemented yet
                role=role,
                content=anonymized_content,  # Save anonymized version
                content_hash=content_hash,
                detected_emotions=detected_emotions,
                emotional_intensity=emotional_intensity,
                distress_level=distress_level,
                crisis_detected=crisis_detected,
                crisis_confidence=crisis_confidence,
                guardrail_triggered=guardrail_triggered,
                conversation_state=conversation_state,
            )
            logger.debug("message_saved_to_db", user_id=user_id, role=role,
                        pii_anonymized=bool(pii_stats))

        except Exception as e:
            logger.error("message_save_to_db_failed",
                        user_id=user_id,
                        error=str(e))
            # Don't raise - continue even if save fails

    async def transition_to_crisis(self, user_id: str) -> None:
        """Immediately transition user to crisis state."""
        user_state = self.user_states.get(user_id)
        if user_state:
            user_state.current_state = ConversationState.CRISIS_INTERVENTION
            user_state.crisis_level = 1.0
            user_state.therapy_phase = TherapyPhase.CRISIS
            logger.warning("user_crisis_transition", user_id=user_id)
            # Save to database
            await self.save_user_state(user_state)

    async def process_message(self, user_id: str, message: str) -> str:
        """Process user message through the state machine."""
        import time
        start_time = time.time()

        logger.info("process_message_started", user_id=user_id, message_preview=message[:50])

        if not self.initialized:
            await self.initialize()
            logger.info("state_manager_initialized_in_process")

        # Get or create user state
        user_state = self.user_states.get(user_id)
        if not user_state:
            await self.initialize_user(user_id)
            user_state = self.user_states[user_id]

        # Update user state
        user_state.last_activity = datetime.now()
        user_state.messages_count += 1
        user_state.message_history.append(HumanMessage(content=message))

        # Save user message to database
        await self.save_message_to_db(
            user_id=user_id,
            role="user",
            content=message
        )

        # Check guardrails (if enabled)
        if self.guardrails:
            guardrail_check = await self.guardrails.check_message(message, {"user_id": user_id})
        else:
            guardrail_check = {"allowed": True}

        if not guardrail_check["allowed"]:
            logger.warning(
                "message_blocked_by_guardrails",
                user_id=user_id,
                policy=guardrail_check["triggered_policy"]
            )
            # Record guardrails activation
            await self.metrics_collector.record_guardrails_activation(
                rule_triggered=guardrail_check["triggered_policy"]
            )
            return guardrail_check["response"]

        # Classify intent (optional, graceful degradation)
        intent_result = None
        if self.intent_classifier and self.intent_classifier.initialized:
            try:
                intent_result = await self.intent_classifier.classify(
                    message,
                    context=user_state.context
                )
                logger.info("intent_classified",
                           user_id=user_id,
                           intent=intent_result.intent.value,
                           confidence=intent_result.confidence)
            except Exception as e:
                logger.warning("intent_classification_failed", error=str(e))

        # Extract entities (optional, graceful degradation)
        extracted_context = None
        if self.entity_extractor and self.entity_extractor.initialized:
            try:
                extracted_context = await self.entity_extractor.extract(
                    message,
                    user_context=user_state.context
                )
                # Update user context with extracted entities
                user_state.context = await self.entity_extractor.update_user_context(
                    user_id,
                    extracted_context,
                    user_state.context
                )
                logger.info("entities_extracted",
                           user_id=user_id,
                           child_names=extracted_context.child_names,
                           entities_count=len(extracted_context.entities))
            except Exception as e:
                logger.warning("entity_extraction_failed", error=str(e))

        # Handle legal tool intents directly (bypass state graph for legal consultations)
        if intent_result and intent_result.intent in [
            Intent.CONTACT_DIARY,
            Intent.BIFF_HELP,
            Intent.MEDIATION_PREP,
            Intent.PARENTING_MODEL
        ]:
            try:
                logger.info("legal_intent_detected",
                           user_id=user_id,
                           intent=intent_result.intent.value)

                # Update state to legal consultation
                user_state.current_state = ConversationState.LEGAL_CONSULTATION

                # Handle through legal tools
                legal_response = await self.legal_tools.handle_intent(
                    intent=intent_result.intent,
                    message=message,
                    user_id=user_id,
                    context=user_state.context
                )

                # Record metrics
                await self.metrics_collector.record_message(
                    user_id=user_id,
                    technique_used=f"legal_{intent_result.intent.value}",
                    emotion_detected=None
                )

                # Update message history
                user_state.message_history.append(SystemMessage(content=legal_response.response_text))

                # Record response time
                response_time = time.time() - start_time
                await self.metrics_collector.record_response_time(response_time)

                # Save user state to database
                await self.save_user_state(user_state)

                return legal_response.response_text

            except Exception as e:
                logger.error("legal_tools_handling_failed",
                           user_id=user_id,
                           intent=intent_result.intent.value,
                           error=str(e))
                # Fall through to normal processing

        # Process through state graph
        try:
            # Prepare state for graph (enriched with intent and entities)
            graph_state = {
                "user_id": user_id,
                "message": message,
                "user_state": user_state,
                "intent": intent_result.intent if intent_result else None,
                "intent_confidence": intent_result.confidence if intent_result else 0.0,
                "extracted_context": extracted_context,
                "timestamp": datetime.now().isoformat()
            }

            logger.info("invoking_state_graph", user_id=user_id, message_length=len(message))
            # Run the graph
            result = await self.graph.ainvoke(graph_state)
            logger.info("state_graph_completed", user_id=user_id)

            # Extract response
            response = result.get("response", "I'm here to support you. How can I help?")

            # Apply guardrails to response (if enabled)
            if self.guardrails:
                safe_response = await self.guardrails.generate_safe_response(
                    message, response, {"user_id": user_id}
                )
            else:
                safe_response = response

            # Update message history
            user_state.message_history.append(SystemMessage(content=safe_response))

            # Save assistant message to database
            await self.save_message_to_db(
                user_id=user_id,
                role="assistant",
                content=safe_response,
                metadata={
                    "technique_used": technique_used if user_state.completed_techniques else None,
                    "conversation_state": user_state.current_state.value,
                }
            )

            # Record metrics for successful message processing
            response_time = time.time() - start_time
            await self.metrics_collector.record_response_time(response_time)

            # Record message with technique info if available
            technique_used = user_state.completed_techniques[-1] if user_state.completed_techniques else None
            await self.metrics_collector.record_message(
                user_id=user_id,
                technique_used=technique_used,
                emotion_detected=None  # Could be enhanced with emotion name
            )

            # Save user state to database
            await self.save_user_state(user_state)

            return safe_response

        except Exception as e:
            logger.error("message_processing_failed", user_id=user_id, error=str(e))
            # Record error
            await self.metrics_collector.record_error(error_type=str(type(e).__name__))
            return "I apologize, I'm having trouble processing your message. Please try again."

    # State handlers
    async def _handle_start(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start state."""
        state["response"] = "Let's begin. How are you feeling today?"
        return state

    async def _handle_emotion_check(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emotion check state with real emotion detection."""
        user_state = state["user_state"]
        message = state["message"]

        # Try to use emotion detector if available
        if self.emotion_detector and self.emotion_detector.model:
            try:
                assessment = await self.emotion_detector.assess_emotional_state(message)

                # Update user state based on assessment
                user_state.emotional_score = 1.0 - assessment["distress_score"]
                user_state.crisis_level = assessment["distress_score"]

                # Store assessment in state
                state["emotion_assessed"] = True
                state["primary_emotion"] = assessment["primary_emotion"]
                state["emotional_intensity"] = assessment["emotional_intensity"]
                state["recommended_approach"] = assessment["recommended_approach"]

                logger.info(
                    "emotion_detected",
                    user_id=user_state.user_id,
                    emotion=assessment["primary_emotion"],
                    distress=assessment["distress_level"],
                    intensity=round(assessment["emotional_intensity"], 2)
                )

                return state

            except Exception as e:
                logger.error("emotion_detection_failed", error=str(e))
                # Fall through to keyword-based detection

        # Fallback: Keyword-based emotion detection
        message_lower = message.lower()
        if any(word in message_lower for word in ["terrible", "awful", "can't cope", "ужасно", "не могу", "покончить", "суицид"]):
            user_state.emotional_score = 0.2
            user_state.crisis_level = 0.7
            state["primary_emotion"] = "grief"
        elif any(word in message_lower for word in ["sad", "lonely", "difficult", "грустно", "одиноко", "тяжело"]):
            user_state.emotional_score = 0.4
            user_state.crisis_level = 0.3
            state["primary_emotion"] = "sadness"
        else:
            user_state.emotional_score = 0.6
            user_state.crisis_level = 0.1
            state["primary_emotion"] = "neutral"

        state["emotion_assessed"] = True
        logger.info(
            "emotion_detected_fallback",
            user_id=user_state.user_id,
            emotion=state.get("primary_emotion"),
            crisis_level=user_state.crisis_level
        )

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
            "Я чувствую, что вы проходите через очень трудное время. "
            "Давайте разберемся с этим по шагам. Хотите ли вы попробовать упражнение на заземление, "
            "или вы предпочитаете рассказать мне больше о том, что происходит?"
        )
        return state

    async def _handle_moderate_support(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle moderate support state."""
        state["response"] = (
            "Спасибо, что поделились со мной. Я здесь, чтобы поддержать вас. "
            "Хотите ли вы поговорить о своих чувствах подробнее, поработать над письмом, "
            "или возможно, поставить цели для движения вперед?"
        )
        return state

    async def _handle_casual_chat(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle casual chat state."""
        state["response"] = "Я рад пообщаться с вами. О чем вы хотите поговорить?"
        return state

    async def _handle_letter_writing(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle letter writing state."""
        state["response"] = (
            "Давайте вместе поработаем над письмом. "
            "Кому вы хотите написать, и какую главную мысль хотите передать?"
        )
        return state

    async def _handle_goal_tracking(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle goal tracking state."""
        state["response"] = "Давайте посмотрим на ваши цели. На чем вы хотите сосредоточиться?"
        return state

    async def _handle_technique_selection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle technique selection state with intelligent orchestrator selection."""
        user_state = state["user_state"]
        message = state["message"]
        primary_emotion = state.get("primary_emotion", "neutral")
        emotional_intensity = state.get("emotional_intensity", 0.5)

        # Build context for orchestrator
        context = {
            "emotion": primary_emotion,
            "emotion_intensity": emotional_intensity,
            "language": "russian",
            "message_count": user_state.messages_count,
            "user_state": user_state,  # CRITICAL: Pass user_state for message history
            "db": self.db  # Add database manager for techniques that need persistence
        }

        # Map crisis_level to risk_level for orchestrator
        if user_state.crisis_level > 0.7:
            context["risk_level"] = "critical"
        elif user_state.crisis_level > 0.5:
            context["risk_level"] = "high"
        elif user_state.crisis_level > 0.3:
            context["risk_level"] = "moderate"
        else:
            context["risk_level"] = "low"

        # Use orchestrator for intelligent technique selection and application
        try:
            result = await self.technique_orchestrator.select_and_apply_technique(
                message,
                context
            )

            state["technique_result"] = result
            state["response"] = result.response

            if result.follow_up:
                state["response"] += f"\n\n{result.follow_up}"

            logger.info(
                "technique_orchestrated",
                user_id=user_state.user_id,
                technique=result.metadata.get("technique_used"),
                supervision_approved=result.metadata.get("supervision_approved"),
                supervision_score=result.metadata.get("supervision_score")
            )

        except Exception as e:
            logger.error("technique_orchestration_failed", user_id=user_state.user_id, error=str(e))
            # Fallback to legacy selection
            distress_level = context.get("risk_level", "moderate")
            selected_technique_key = self._select_technique(distress_level, primary_emotion, state)
            state["selected_technique"] = selected_technique_key
            state["response"] = f"Давайте попробуем {self.techniques[selected_technique_key].name}."

        return state

    async def _handle_technique_execution(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle technique execution using real therapeutic techniques."""
        # Check if orchestrator already executed the technique
        if "technique_result" in state and hasattr(state["technique_result"], "success"):
            # Technique already applied by orchestrator
            result = state["technique_result"]
            if result.success:
                # Track technique completion
                user_state = state["user_state"]
                technique_used = result.metadata.get("technique_used")
                if technique_used and technique_used not in user_state.completed_techniques:
                    user_state.completed_techniques.append(technique_used)
            return state

        # Legacy path: execute technique if not already done by orchestrator
        technique_key = state.get("selected_technique", "validation")
        technique = self.techniques.get(technique_key)

        if not technique:
            state["response"] = "Извините, я не могу применить эту технику прямо сейчас."
            return state

        # Prepare context for technique
        context = {
            "primary_emotion": state.get("primary_emotion", "neutral"),
            "distress_level": state.get("distress_level", "moderate"),
            "emotional_intensity": state.get("emotional_intensity", 0.5),
            "user_state": state["user_state"],
            "db": self.db  # Add database manager for techniques that need persistence
        }

        # Apply the technique
        try:
            result = await technique.apply(state["message"], context)

            if result.success:
                response = result.response
                if result.follow_up:
                    response += f"\n\n{result.follow_up}"

                state["response"] = response
                state["technique_result"] = result.metadata

                # Track technique completion
                user_state = state["user_state"]
                if technique_key not in user_state.completed_techniques:
                    user_state.completed_techniques.append(technique_key)

                logger.info(
                    "technique_applied",
                    user_id=user_state.user_id,
                    technique=technique_key,
                    success=True
                )
            else:
                state["response"] = "Давайте попробуем другой подход."

        except Exception as e:
            logger.error("technique_execution_failed", technique=technique_key, error=str(e))
            state["response"] = "Я здесь, чтобы поддержать вас. Расскажите мне больше о том, что вы чувствуете."

        return state

    def _select_technique(
        self,
        distress_level: str,
        primary_emotion: str,
        state: Dict[str, Any]
    ) -> str:
        """
        Select appropriate technique based on context.

        Args:
            distress_level: Current distress level (low/moderate/high/crisis)
            primary_emotion: Detected primary emotion
            state: Full state dict

        Returns:
            Technique key to use
        """
        # Crisis or high distress: Grounding first
        if distress_level in ["crisis", "high"]:
            return "grounding"

        # Check if user wants specific type of help
        message_lower = state.get("message", "").lower()

        if any(word in message_lower for word in ["упражнение", "техника", "дыхание", "exercise"]):
            return "grounding"

        if any(word in message_lower for word in ["думаю", "мысли", "считаю", "thinking"]):
            return "cbt"

        # Default flow based on emotion
        emotion_to_technique = {
            "anger": "cbt",  # Reframe angry thoughts
            "grief": "validation",  # Validate deep pain
            "sadness": "validation",
            "fear": "grounding",  # Ground the anxiety
            "anxiety": "grounding"
        }

        return emotion_to_technique.get(primary_emotion, "validation")

    async def _handle_end_session(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle end session state."""
        state["response"] = (
            "Спасибо за наш разговор сегодня. "
            "Помните, я здесь, когда вам понадобится поддержка. Берегите себя."
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

    async def augment_with_knowledge(
        self,
        query: str,
        base_response: str,
        top_k: int = 2
    ) -> str:
        """
        Augment response with retrieved knowledge.

        Args:
            query: User query/message
            base_response: Base response from technique or handler
            top_k: Number of documents to retrieve

        Returns:
            Augmented response with relevant knowledge
        """
        if not self.knowledge_retriever or not self.knowledge_retriever.initialized:
            return base_response

        try:
            # Retrieve relevant documents
            results = await self.knowledge_retriever.retrieve(query, top_k=top_k, threshold=0.4)

            if not results:
                return base_response

            # Format retrieved knowledge
            knowledge_snippets = []
            for result in results:
                # Extract relevant portion of document
                doc_content = result.document.content.strip()
                # Limit to first 200 characters
                snippet = doc_content[:200] + "..." if len(doc_content) > 200 else doc_content
                knowledge_snippets.append(snippet)

            # Augment response with knowledge
            if knowledge_snippets:
                augmented = f"{base_response}\n\n📚 **Дополнительная информация:**\n"
                for i, snippet in enumerate(knowledge_snippets, 1):
                    augmented += f"\n{i}. {snippet}\n"

                return augmented
            else:
                return base_response

        except Exception as e:
            logger.error("knowledge_augmentation_failed", error=str(e))
            return base_response

    async def process_voice_message(self, user_id: str, audio_path: Path) -> str:
        """
        Process voice message by transcribing and processing as text.

        Args:
            user_id: User ID
            audio_path: Path to voice message file

        Returns:
            Bot response
        """
        if not self.speech_handler:
            return "Извините, обработка голосовых сообщений недоступна. Пожалуйста, напишите текстом."

        try:
            # Transcribe voice to text
            transcription = await self.speech_handler.transcribe_telegram_voice(audio_path)

            if not transcription:
                return "Извините, не удалось распознать речь. Попробуйте записать сообщение ещё раз или напишите текстом."

            logger.info("voice_transcribed",
                       user_id=user_id,
                       text_length=len(transcription))

            # Process transcribed text as regular message
            response = await self.process_message(user_id, transcription)

            # Prepend transcription info
            return f"🎤 Вы сказали: \"{transcription}\"\n\n{response}"

        except Exception as e:
            logger.error("voice_message_processing_failed",
                        user_id=user_id,
                        error=str(e))
            return "Извините, произошла ошибка при обработке голосового сообщения. Попробуйте написать текстом."