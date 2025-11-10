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
    LEGAL_CONSULTATION = "legal_consultation"
    TECHNIQUE_SELECTION = "technique_selection"
    TECHNIQUE_EXECUTION = "technique_execution"
    END_SESSION = "end_session"


class RecoveryTrackEnum(str, enum.Enum):
    """Recovery track enumeration for multi-track system."""
    SELF_WORK = "self_work"
    CHILD_CONNECTION = "child_connection"
    NEGOTIATION = "negotiation"
    COMMUNITY = "community"


class TrackPhaseEnum(str, enum.Enum):
    """Track phase enumeration for recovery progress."""
    AWARENESS = "awareness"      # 0-25%
    EXPRESSION = "expression"    # 25-50%
    ACTION = "action"           # 50-75%
    MASTERY = "mastery"         # 75-100%


class ProjectTypeEnum(str, enum.Enum):
    """Creative project type enumeration."""
    QUEST = "quest"
    LETTER = "letter"
    GOAL = "goal"


class QuestStatusEnum(str, enum.Enum):
    """Quest status enumeration."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    MODERATION_FAILED = "moderation_failed"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class ModerationStatusEnum(str, enum.Enum):
    """Content moderation status."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class UserModeEnum(str, enum.Enum):
    """User mode enumeration for inner_edu integration."""
    EDUCATIONAL = "educational"  # 80-90% of users - learning support
    THERAPEUTIC = "therapeutic"  # 10-20% of users - serious psychological issues


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(100), unique=True, nullable=False, index=True)

    # User mode (Phase 4.3 - inner_edu integration)
    mode = Column(Enum(UserModeEnum), default=UserModeEnum.EDUCATIONAL)
    parent_name = Column(String(255))
    learning_profile = Column(JSON, default=dict)

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

    # Multi-track recovery system (Phase 4)
    recovery_tracks = Column(JSON, default=dict)  # Dict[RecoveryTrack, TrackProgress]
    primary_track = Column(String(50), default="self_work")  # Current focus track
    recovery_week = Column(Integer, default=0)  # Week since journey start
    recovery_day = Column(Integer, default=0)  # Day in current week

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    letters = relationship("Letter", back_populates="user", cascade="all, delete-orphan")
    quests = relationship("Quest", back_populates="user", cascade="all, delete-orphan")
    creative_projects = relationship("CreativeProject", back_populates="user", cascade="all, delete-orphan")
    track_milestones = relationship("TrackMilestone", back_populates="user", cascade="all, delete-orphan")
    user_tracks = relationship("UserTrack", back_populates="user", cascade="all, delete-orphan")
    psychological_profile = relationship("PsychologicalProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    quest_builder_sessions = relationship("QuestBuilderSession", back_populates="user", cascade="all, delete-orphan")
    quest_library = relationship("UserQuestLibrary", back_populates="user", cascade="all, delete-orphan")
    quest_progress_records = relationship("QuestProgress", back_populates="user", cascade="all, delete-orphan")
    quest_ratings = relationship("QuestRating", back_populates="user", cascade="all, delete-orphan")


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
    content = Column(Text, nullable=False)  # Actual message content (TODO: encrypt in production)

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
    creative_project = relationship("CreativeProject", back_populates="goal", uselist=False)


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
    creative_project = relationship("CreativeProject", back_populates="letter", uselist=False)


class MetricsSnapshot(Base):
    """Metrics snapshot for analytics and monitoring."""

    __tablename__ = "metrics_snapshots"

    id = Column(Integer, primary_key=True)

    # Snapshot metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    period = Column(String(20), default="1h")  # 1h, 24h, 7d, 30d

    # Usage metrics
    total_messages = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    avg_messages_per_session = Column(Float, default=0.0)
    avg_session_duration_minutes = Column(Float, default=0.0)

    # Technique usage distribution
    techniques_distribution = Column(JSON, default=dict)  # {"cbt": 10, "validation": 5, ...}

    # Conversion metrics
    conversations_total = Column(Integer, default=0)
    letters_started = Column(Integer, default=0)
    letters_completed = Column(Integer, default=0)
    goals_created = Column(Integer, default=0)
    conversion_rate_letters = Column(Float, default=0.0)  # % of conversations that led to letters
    conversion_rate_goals = Column(Float, default=0.0)  # % of conversations that led to goals

    # Emotional trends
    emotions_detected = Column(JSON, default=dict)  # {"sadness": 15, "anger": 8, ...}
    avg_emotional_score = Column(Float, default=0.0)  # 0-1 scale
    avg_distress_level = Column(Float, default=0.0)  # 0-1 scale

    # Safety metrics
    crisis_detections = Column(Integer, default=0)
    pii_warnings = Column(Integer, default=0)

    # Quality metrics
    avg_empathy_score = Column(Float, default=0.0)
    avg_safety_score = Column(Float, default=0.0)
    avg_therapeutic_value = Column(Float, default=0.0)

    # Technical metrics
    total_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    avg_response_time_seconds = Column(Float, default=0.0)
    p95_response_time_seconds = Column(Float, default=0.0)
    error_rate_percent = Column(Float, default=0.0)
    api_calls_openai = Column(Integer, default=0)

    # Additional analytics
    peak_hour = Column(Integer)  # Hour of day with most activity (0-23)
    most_used_technique = Column(String(50))
    most_detected_emotion = Column(String(50))


class Quest(Base):
    """Quest model for educational quests created for children."""

    __tablename__ = "quests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Quest metadata
    quest_id = Column(String(200), unique=True, nullable=False, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)

    # Child information
    child_name = Column(String(100))
    child_age = Column(Integer)
    child_interests = Column(JSON, default=list)  # Topics, hobbies, favorite subjects

    # Quest content (Phase 4.3 - dual storage)
    graph_structure = Column(JSON)  # PRIMARY storage (JSONB) for inner_edu compatibility
    quest_yaml = Column(Text, nullable=False)  # Generated from graph_structure, for backward compatibility
    total_nodes = Column(Integer, default=0)
    difficulty_level = Column(String(20))  # easy/medium/hard

    # Inner Edu metadata (Phase 4.3)
    psychological_module = Column(String(100), index=True)  # IFS, DBT, CBT, etc.
    location = Column(String(100))  # Game world location
    age_range = Column(String(20))  # "7-9", "10-12", etc.

    # Family memories and clues (for reveal mechanics)
    family_photos = Column(JSON, default=list)  # Paths to photos
    family_memories = Column(JSON, default=list)  # Memory descriptions
    family_jokes = Column(JSON, default=list)  # Inside jokes, phrases
    familiar_locations = Column(JSON, default=list)  # Places child recognizes

    # Status tracking
    status = Column(Enum(QuestStatusEnum), default=QuestStatusEnum.DRAFT)
    moderation_status = Column(Enum(ModerationStatusEnum), default=ModerationStatusEnum.PENDING)
    moderation_issues = Column(JSON, default=list)  # Toxic content found, patterns flagged
    moderation_notes = Column(Text)

    # Reveal mechanics configuration
    reveal_enabled = Column(Boolean, default=True)
    reveal_threshold_percentage = Column(Float, default=0.8)  # When to show reveal (80%)
    reveal_message = Column(Text)  # Final message from parent
    reveal_count = Column(Integer, default=0)  # Number of times reveal was viewed
    last_reveal_at = Column(DateTime)  # Last reveal view timestamp

    # Public marketplace (Phase 4.3 - inner_edu)
    is_public = Column(Boolean, default=False, index=True)  # Available in public library
    rating = Column(Float, default=0.0)  # Average rating (1-5)
    plays_count = Column(Integer, default=0)  # Number of times played

    # Psychologist review (Phase 4.3)
    psychologist_reviewed = Column(Boolean, default=False)
    psychologist_review_id = Column(Integer, ForeignKey("psychologist_reviews.id"))
    reviewed_at = Column(DateTime)

    # Deployment
    deployed_to_inner_edu = Column(Boolean, default=False)
    inner_edu_quest_id = Column(String(200), index=True)  # ID in inner_edu system
    deployed_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_edited = Column(DateTime, onupdate=datetime.utcnow)
    approved_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="quests")
    quest_analytics = relationship("QuestAnalytics", back_populates="quest", uselist=False, cascade="all, delete-orphan")
    privacy_settings = relationship("ChildPrivacySettings", back_populates="quest", uselist=False, cascade="all, delete-orphan")
    creative_project = relationship("CreativeProject", back_populates="quest", uselist=False)
    psychologist_review = relationship("PsychologistReview", foreign_keys=[psychologist_review_id], uselist=False)
    ratings = relationship("QuestRating", back_populates="quest", cascade="all, delete-orphan")
    progress_records = relationship("QuestProgress", back_populates="quest", cascade="all, delete-orphan")


class CreativeProject(Base):
    """Meta-table linking all creative projects (quests, letters, goals)."""

    __tablename__ = "creative_projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Project type and reference
    project_type = Column(Enum(ProjectTypeEnum), nullable=False)
    quest_id = Column(Integer, ForeignKey("quests.id"), unique=True)
    letter_id = Column(Integer, ForeignKey("letters.id"), unique=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), unique=True)

    # Status
    status = Column(String(20), default="active")  # active/completed/abandoned
    progress_percentage = Column(Float, default=0.0)

    # Multi-track impact
    affects_tracks = Column(JSON, default=list)  # List[RecoveryTrack] that this project impacts

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="creative_projects")
    quest = relationship("Quest", back_populates="creative_project")
    letter = relationship("Letter", back_populates="creative_project")
    goal = relationship("Goal", back_populates="creative_project")


class QuestAnalytics(Base):
    """Aggregated analytics for quest progress (privacy-safe, child consent required)."""

    __tablename__ = "quest_analytics"

    id = Column(Integer, primary_key=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), unique=True, nullable=False)

    # Progress tracking (aggregated only, NO personal messages/answers)
    nodes_completed = Column(Integer, default=0)
    total_nodes = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)

    # Educational progress (aggregated metrics only)
    educational_progress = Column(JSON, default=dict)  # {"math": 75, "logic": 60, ...}
    achievements_unlocked = Column(JSON, default=list)  # Achievement IDs only
    difficulty_progression = Column(JSON, default=dict)  # Trend over time

    # Engagement metrics
    play_count = Column(Integer, default=0)
    last_played = Column(DateTime, index=True)
    total_time_spent_minutes = Column(Float, default=0.0)
    average_session_minutes = Column(Float, default=0.0)

    # Reveal progress
    clues_discovered = Column(Integer, default=0)
    total_clues = Column(Integer, default=0)
    reveal_phase = Column(String(50))  # NEUTRAL/SUBTLE_CLUES/INVESTIGATION/REVEAL
    reveal_completed = Column(Boolean, default=False)
    reveal_completed_at = Column(DateTime)

    # Child privacy consent
    child_consented_to_sharing = Column(Boolean, default=False)
    consent_updated_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    quest = relationship("Quest", back_populates="quest_analytics")


class ChildPrivacySettings(Base):
    """Child privacy settings for quest data sharing (consent management)."""

    __tablename__ = "child_privacy_settings"

    id = Column(Integer, primary_key=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), unique=True, nullable=False)

    # Consent levels (default: all disabled)
    share_completion_progress = Column(Boolean, default=False)  # Share % completed
    share_educational_progress = Column(Boolean, default=False)  # Share subject scores
    share_achievements = Column(Boolean, default=False)  # Share unlocked achievements
    share_play_frequency = Column(Boolean, default=False)  # Share last played, session count

    # Notification preferences
    notify_both_parents = Column(Boolean, default=True)  # Send to both or only creator
    notification_frequency = Column(String(20), default="immediate")  # immediate/daily/weekly

    # Audit trail
    consent_given_by_child = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime)
    consent_revoked_at = Column(DateTime)
    consent_history = Column(JSON, default=list)  # Audit log of changes

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    quest = relationship("Quest", back_populates="privacy_settings")


class PsychologicalProfile(Base):
    """Unified psychological profile for parent (aggregated from all interactions)."""

    __tablename__ = "psychological_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Emotional trends (aggregated from sessions/messages)
    emotional_trends = Column(JSON, default=dict)  # {"sadness": [0.6, 0.5, 0.4], "anger": [...]}
    emotional_baseline = Column(Float, default=0.5)  # Average emotional score
    emotional_volatility = Column(Float, default=0.0)  # Standard deviation

    # Crisis history
    crisis_history = Column(JSON, default=list)  # Timestamps and context of crisis incidents
    last_crisis_date = Column(DateTime)
    crisis_frequency = Column(Float, default=0.0)  # Incidents per week

    # Coping strategies (what works for this user)
    coping_strategies = Column(JSON, default=dict)  # {"grounding": 0.8, "cbt": 0.6, ...}
    most_effective_technique = Column(String(50))

    # Triggers and patterns
    triggers = Column(JSON, default=list)  # Known emotional triggers
    distress_patterns = Column(JSON, default=dict)  # Time of day, day of week patterns

    # Communication style
    communication_style = Column(String(50))  # Direct/indirect/emotional/logical
    preferred_tone = Column(String(50))  # Empathetic/practical/both

    # Content quality tracking
    toxic_patterns = Column(JSON, default=list)  # Patterns of toxic communication
    toxicity_trend = Column(String(20))  # improving/stable/worsening
    last_toxicity_incident = Column(DateTime)

    # Growth areas
    growth_areas = Column(JSON, default=list)  # Focus areas for development
    progress_notes = Column(Text)

    # Recommendations
    recommended_techniques = Column(JSON, default=list)  # Personalized technique suggestions
    recommended_resources = Column(JSON, default=list)  # External resources

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="psychological_profile")


class TrackMilestone(Base):
    """Recovery track milestone achievements."""

    __tablename__ = "track_milestones"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Milestone details
    track = Column(String(50), nullable=False, index=True)  # RecoveryTrack enum value
    milestone_type = Column(String(100), nullable=False)  # first_letter/quest_created/goal_achieved/etc
    milestone_name = Column(String(200))
    description = Column(Text)

    # Achievement context
    achievement_context = Column(JSON, default=dict)  # Additional metadata
    related_project_id = Column(Integer)  # Reference to CreativeProject
    related_project_type = Column(String(20))  # quest/letter/goal

    # Timestamps
    achieved_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="track_milestones")


class PsychologistReview(Base):
    """Professional psychologist review for quests (Phase 4.3)."""

    __tablename__ = "psychologist_reviews"

    id = Column(Integer, primary_key=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), unique=True, nullable=False)

    # Reviewer information
    reviewer_name = Column(String(255))
    reviewer_credentials = Column(String(500))

    # Four rating scales (1-5 each)
    emotional_safety_score = Column(Integer, nullable=False)
    therapeutic_correctness_score = Column(Integer, nullable=False)
    age_appropriateness_score = Column(Integer, nullable=False)
    reveal_timing_score = Column(Integer, nullable=False)

    # Overall assessment
    overall_score = Column(Float)  # Average of 4 scales
    is_approved = Column(Boolean, default=False, index=True)

    # Detailed feedback
    strengths = Column(Text)  # What works well
    concerns = Column(Text)  # Potential issues
    recommendations = Column(Text)  # Suggested improvements
    modification_notes = Column(Text)  # Required changes for approval

    # Review metadata
    review_duration_minutes = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    quest = relationship("Quest", foreign_keys=[quest_id], back_populates="psychologist_review")


class QuestBuilderSession(Base):
    """AI Quest Builder session tracking (from inner_edu)."""

    __tablename__ = "quest_builder_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # AI conversation history
    conversation_history = Column(JSON, default=list)  # List of messages

    # Dialog stage (greeting → collecting_info → clarifying → generating → reviewing → quest_ready)
    current_stage = Column(String(50), default="greeting")

    # Current graph being built
    current_graph = Column(JSON)  # Graph structure (nodes + edges)

    # Quest context
    quest_context = Column(JSON)  # Child info, preferences, memories

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="quest_builder_sessions")


class UserQuestLibrary(Base):
    """User's quest library (public marketplace quests from inner_edu)."""

    __tablename__ = "user_quest_library"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False, index=True)

    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="quest_library")
    quest = relationship("Quest")


class QuestProgress(Base):
    """Child's quest completion progress (privacy-protected, requires consent)."""

    __tablename__ = "quest_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False, index=True)

    # Progress tracking
    current_step = Column(Integer, default=0)
    completed = Column(Boolean, default=False)

    # Session tracking
    session_count = Column(Integer, default=0)
    total_time_minutes = Column(Float, default=0.0)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    last_played_at = Column(DateTime, index=True)

    # Relationships
    user = relationship("User", back_populates="quest_progress_records")
    quest = relationship("Quest", back_populates="progress_records")


class QuestRating(Base):
    """Quest ratings from parents (public marketplace)."""

    __tablename__ = "quest_ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False, index=True)

    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="quest_ratings")
    quest = relationship("Quest", back_populates="ratings")


class UserTrack(Base):
    """User recovery track progress (Phase 4.3 - normalized from recovery_tracks JSON)."""

    __tablename__ = "user_tracks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Track type
    track_type = Column(Enum(RecoveryTrackEnum), nullable=False)

    # Current phase
    current_phase = Column(Enum(TrackPhaseEnum), default=TrackPhaseEnum.AWARENESS)

    # Progress tracking
    completion_percentage = Column(Integer, default=0)
    weeks_active = Column(Integer, default=0)
    days_active = Column(Integer, default=0)

    # Activity tracking
    total_activities = Column(Integer, default=0)
    completed_activities = Column(Integer, default=0)
    last_activity_at = Column(DateTime)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_tracks")