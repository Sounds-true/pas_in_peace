"""SQLAlchemy models for PAS Bot."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
import enum


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TherapyPhaseEnum(str, enum.Enum):
    """Therapy phase enumeration."""
    CRISIS = "crisis"
    UNDERSTANDING = "understanding"
    ACTION = "action"
    SUSTAINABILITY = "sustainability"


class ConversationStateEnum(str, enum.Enum):
    """Conversation state enumeration."""
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


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(100), unique=True, nullable=False, index=True)

    # State information
    current_state = Column(Enum(ConversationStateEnum), default=ConversationStateEnum.START)
    therapy_phase = Column(Enum(TherapyPhaseEnum), default=TherapyPhaseEnum.UNDERSTANDING)

    # Emotional tracking
    emotional_score = Column(Float, default=0.5)  # 0-1 scale
    crisis_level = Column(Float, default=0.0)  # 0-1 scale

    # Statistics
    total_messages = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    crisis_incidents = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Context (encrypted in production)
    context = Column(JSON, default=dict)

    # Privacy flags
    consent_given = Column(Boolean, default=False)
    data_retention_days = Column(Integer, default=90)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    letters = relationship("Letter", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Therapy session model."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session details
    session_number = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Emotional tracking
    initial_emotional_score = Column(Float)
    final_emotional_score = Column(Float)
    primary_emotion = Column(String(50))

    # Session content
    techniques_used = Column(JSON, default=list)  # List of technique names
    topics_discussed = Column(JSON, default=list)

    # Assessment
    session_quality = Column(Float)  # 0-1 scale
    therapeutic_alliance = Column(Float)  # 0-1 scale

    # Summary
    summary = Column(Text)
    therapist_notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Message model."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))

    # Message content (PII-scrubbed)
    role = Column(String(20), nullable=False)  # user/assistant/system
    content_hash = Column(String(64))  # SHA-256 hash for deduplication

    # Emotional analysis
    detected_emotions = Column(JSON, default=dict)
    emotional_intensity = Column(Float)
    distress_level = Column(String(20))

    # Safety flags
    crisis_detected = Column(Boolean, default=False)
    crisis_confidence = Column(Float)
    guardrail_triggered = Column(String(100))

    # Context
    conversation_state = Column(String(50))
    technique_context = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="messages")
    session = relationship("Session", back_populates="messages")


class Goal(Base):
    """User goal model."""

    __tablename__ = "goals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # emotional_regulation/communication/self_care/etc

    # SMART criteria
    specific = Column(Text)
    measurable = Column(Text)
    achievable = Column(Text)
    relevant = Column(Text)
    time_bound = Column(String(100))

    # Progress tracking
    status = Column(String(20), default="active")  # active/completed/blocked/abandoned
    progress_percentage = Column(Float, default=0.0)

    # Milestones
    milestones = Column(JSON, default=list)
    completed_milestones = Column(JSON, default=list)

    # Blockers
    blockers = Column(JSON, default=list)
    blocker_resolution_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    target_date = Column(DateTime)
    completed_at = Column(DateTime)
    last_reviewed = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="goals")


class Letter(Base):
    """Letter drafts and versions model."""

    __tablename__ = "letters"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Letter metadata
    title = Column(String(200))
    recipient_role = Column(String(100))  # ex-partner/school/therapist/etc
    purpose = Column(String(100))  # communication/mediation/documentation/etc

    # Letter type (NEW)
    letter_type = Column(String(50), default="for_sending")  # for_sending/time_capsule/therapeutic

    # Letter versions
    version_number = Column(Integer, default=1)
    draft_content = Column(Text)  # Current draft (PII-scrubbed)

    # Style and approach
    communication_style = Column(String(50))  # BIFF/NVC/formal/etc
    tone_assessment = Column(JSON, default=dict)

    # Toxicity analysis (NEW)
    toxicity_score = Column(Float)  # 0.0-1.0 overall toxicity
    toxicity_details = Column(JSON, default=dict)  # Detoxify results + LLM recommendations
    toxicity_warnings_ignored = Column(Boolean, default=False)  # User chose to keep toxic content

    # Telegraph integration (NEW)
    telegraph_url = Column(String(500))  # Current version URL
    telegraph_path = Column(String(200))  # Path for editing
    telegraph_access_token = Column(String(200))  # For updates
    telegraph_versions = Column(JSON, default=list)  # Version history with toxicity tracking

    # Review and feedback
    guardrail_checks = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    revision_history = Column(JSON, default=list)

    # Status
    status = Column(String(20), default="draft")  # draft/reviewed/finalized/sent/archived

    # Emotional context
    emotions_processed = Column(JSON, default=list)
    initial_emotional_state = Column(String(50))
    final_emotional_state = Column(String(50))

    # Time capsule
    is_time_capsule = Column(Boolean, default=False)
    time_capsule_open_date = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_edited = Column(DateTime, onupdate=datetime.utcnow)
    finalized_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="letters")