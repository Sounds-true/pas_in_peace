"""State management using LangGraph."""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import asyncio

from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

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
    ActiveListening
)
from src.rag import KnowledgeRetriever, PAKnowledgeBase


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
        self.emotion_detector = EmotionDetector()

        # Initialize new NLP components
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()
        self.speech_handler = SpeechHandler(backend='google', language='ru-RU')

        # Initialize therapeutic techniques
        self.techniques = {
            "cbt": CBTReframing(),
            "grounding": GroundingTechnique(),
            "validation": ValidationTechnique(),
            "active_listening": ActiveListening()
        }

        # Initialize RAG retriever
        self.knowledge_retriever = KnowledgeRetriever()

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

            # Initialize emotion detector (optional for MVP)
            try:
                await self.emotion_detector.initialize()
                logger.info("emotion_detector_enabled")
            except Exception as e:
                logger.warning("emotion_detector_disabled", reason=str(e))
                # Continue without emotion detector - will use keyword fallback

            # Initialize RAG retriever and load knowledge base
            try:
                await self.knowledge_retriever.initialize()
                # Load knowledge base documents
                documents = PAKnowledgeBase.get_all_documents()
                await self.knowledge_retriever.add_documents(documents)
                logger.info("knowledge_retriever_enabled", doc_count=len(documents))
            except Exception as e:
                logger.warning("knowledge_retriever_disabled", reason=str(e))
                # Continue without RAG - will use only predefined responses

            # Initialize entity extractor (optional)
            try:
                await self.entity_extractor.initialize()
                logger.info("entity_extractor_enabled")
            except Exception as e:
                logger.warning("entity_extractor_disabled", reason=str(e))
                # Continue without entity extraction - will work without context enrichment

            # Initialize intent classifier (optional)
            try:
                await self.intent_classifier.initialize()
                logger.info("intent_classifier_enabled")
            except Exception as e:
                logger.warning("intent_classifier_disabled", reason=str(e))
                # Continue without intent classification - will use state machine only

            # Initialize speech handler (optional)
            try:
                if self.speech_handler.is_available():
                    await self.speech_handler.initialize()
                    logger.info("speech_handler_enabled", backend=self.speech_handler.backend)
                else:
                    logger.warning("speech_handler_unavailable",
                                  message="Install: pip install SpeechRecognition pydub")
                    self.speech_handler = None
            except Exception as e:
                logger.warning("speech_handler_disabled", reason=str(e))
                self.speech_handler = None

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
        """Handle technique selection state with intelligent selection."""
        user_state = state["user_state"]
        primary_emotion = state.get("primary_emotion", "neutral")
        distress_level = state.get("distress_level", "moderate")

        # Select appropriate technique based on distress and emotion
        selected_technique_key = self._select_technique(distress_level, primary_emotion, state)
        state["selected_technique"] = selected_technique_key

        # Store selection for execution
        logger.info(
            "technique_selected",
            user_id=user_state.user_id,
            technique=selected_technique_key,
            distress=distress_level
        )

        state["response"] = f"Давайте попробуем {self.techniques[selected_technique_key].name}."
        return state

    async def _handle_technique_execution(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle technique execution using real therapeutic techniques."""
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
            "user_state": state["user_state"]
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