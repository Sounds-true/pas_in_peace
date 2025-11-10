# Unified Database Schema - pas_in_peace + inner_edu Integration

**Version:** 1.0
**Date:** 2025-11-09
**Status:** ✅ Ready for Implementation

---

## 🎯 Overview

Unified PostgreSQL database schema combining:
- **pas_in_peace Phase 4.1/4.2** (Multi-track recovery, moderation, analytics)
- **inner_edu** (Quest builder, educational modules, learning profiles)

**Key Strategy:** Merge with minimal conflicts, extend existing models, add new tables.

---

## 📊 Schema Comparison

### Conflicting Models (Need Merge)

| Model | pas_in_peace | inner_edu | Resolution |
|-------|-------------|-----------|------------|
| **User** | Basic (id, telegram_id) | Extended (telegram_id, child_name, learning_profile) | ✅ Use inner_edu as base, add Phase 4 fields |
| **Quest** | Basic (yaml_content) | Extended (graph_structure, moderation) | ✅ Use inner_edu as base, add Phase 4 analytics |
| **QuestProgress** | Basic progress | Basic progress | ✅ Keep inner_edu, add Phase 4 fields |

### New Tables from pas_in_peace Phase 4

- `user_tracks` - Multi-track recovery system (4 tracks)
- `milestones` - Track progress milestones
- `child_privacy` - Privacy settings & consent
- `quest_analytics` - Aggregated quest analytics
- `psychologist_reviews` - Psychologist review system

### Existing Tables from inner_edu (Keep)

- `quest_builder_sessions` - AI builder dialogue state
- `user_quest_library` - User quest collections
- `quest_ratings` - Community quest ratings

---

## 🗄️ Unified Schema (SQLAlchemy Models)

### 1. Users Table (MERGED)

```python
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, Enum, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()


class UserMode(str, enum.Enum):
    """User mode: educational or therapeutic"""
    EDUCATIONAL = "educational"
    THERAPEUTIC = "therapeutic"


class User(Base):
    """
    Unified User model
    Combines pas_in_peace parent + inner_edu parent
    """
    __tablename__ = "users"

    # Core fields (inner_edu)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)

    # Parent info
    parent_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)

    # Child info (inner_edu)
    child_name = Column(String(255), nullable=True)
    child_age = Column(Integer, nullable=True)

    # Learning & Psychological profiles
    learning_profile = Column(JSONB, nullable=True)
    # Structure: {
    #   "visual_preference": 0.0-1.0,
    #   "logical_preference": 0.0-1.0,
    #   "attention_span": "short|medium|long",
    #   "difficulties": ["memory", "attention", "motivation"],
    #   "strengths": ["creativity", "logic", "empathy"]
    # }

    # Mode (Phase 4 addition)
    mode = Column(Enum(UserMode), default=UserMode.EDUCATIONAL, index=True)
    # Mode switch happens when low states detected or parent requests

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    quests = relationship("Quest", back_populates="author")
    builder_sessions = relationship("QuestBuilderSession", back_populates="user")
    quest_library = relationship("UserQuestLibrary", back_populates="user")
    tracks = relationship("UserTrack", back_populates="user")  # Phase 4
    privacy_settings = relationship("ChildPrivacy", back_populates="user", uselist=False)  # Phase 4


class ChildPrivacy(Base):
    """
    Privacy settings for child (Phase 4.3)
    Controls what parent can see
    """
    __tablename__ = "child_privacy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Privacy levels
    share_progress = Column(Boolean, default=False)
    share_quest_details = Column(Boolean, default=False)
    share_emotional_state = Column(Boolean, default=False)
    share_analytics = Column(Boolean, default=False)

    # Consent tracking
    consent_given_by_child = Column(Boolean, default=False)
    consent_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)
    consent_version = Column(String(50), nullable=True)  # "1.0", "1.1", etc.

    # Audit trail
    consent_history = Column(JSONB, default=list)
    # [{"timestamp": "...", "action": "granted|revoked", "fields": [...]}]

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="privacy_settings")
```

---

### 2. Quests Table (MERGED)

```python
class ModerationStatus(str, enum.Enum):
    """Quest moderation status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"  # Needs review


class Quest(Base):
    """
    Unified Quest model
    Combines pas_in_peace quest + inner_edu quest
    """
    __tablename__ = "quests"

    # Core fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Quest content
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # PRIMARY STORAGE: Graph structure (inner_edu)
    graph_structure = Column(JSONB, nullable=False)
    # Structure: {
    #   "nodes": [{"id": "...", "type": "...", "position": {...}, "data": {...}}],
    #   "edges": [{"id": "...", "source": "...", "target": "...", "label": "..."}]
    # }

    # GENERATED: YAML content (for compatibility)
    yaml_content = Column(Text, nullable=True)
    # Auto-generated from graph_structure when needed

    # Metadata (inner_edu)
    psychological_module = Column(String(100), nullable=True, index=True)
    # e.g., "IFS_Level1", "DBT_Basics", "Emotional_Literacy"

    location = Column(String(100), nullable=True)
    # e.g., "tower_confusion", "forest_memory", "bridge_reality"

    difficulty = Column(String(50), nullable=True)
    # "beginner", "intermediate", "advanced"

    age_range = Column(String(20), nullable=True)
    # "7-9", "10-12", "13-14"

    estimated_duration = Column(Integer, nullable=True)
    # Minutes to complete

    tags = Column(ARRAY(String), nullable=True)
    # ["math", "logic", "family", "emotions"]

    # Moderation (inner_edu + Phase 4.2 enhancements)
    is_public = Column(Boolean, default=False, index=True)
    moderation_status = Column(Enum(ModerationStatus), default=ModerationStatus.PENDING, index=True)
    moderation_reason = Column(Text, nullable=True)
    moderation_issues = Column(JSONB, nullable=True)
    # [{"category": "manipulation", "severity": "high", "message": "..."}]

    # Phase 4.3: Psychologist Review
    psychologist_reviewed = Column(Boolean, default=False, index=True)
    psychologist_review_id = Column(UUID(as_uuid=True), ForeignKey("psychologist_reviews.id"), nullable=True)

    # Phase 4.3: Family connection tracking
    reveal_count = Column(Integer, default=0)
    # Number of "reveal" moments in quest (family connection points)

    family_photos_count = Column(Integer, default=0)
    family_memories_count = Column(Integer, default=0)

    # Statistics (inner_edu)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    plays_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    # Auto-calculated: completion_count / plays_count

    # Analytics (Phase 4.3)
    average_completion_time = Column(Integer, nullable=True)
    # Seconds, auto-calculated from quest_progress records

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    author = relationship("User", back_populates="quests")
    ratings = relationship("QuestRating", back_populates="quest")
    progress_records = relationship("QuestProgress", back_populates="quest")
    psychologist_review = relationship("PsychologistReview", foreign_keys=[psychologist_review_id], uselist=False)
    analytics = relationship("QuestAnalytics", back_populates="quest", uselist=False)
```

---

### 3. Quest Progress (MERGED)

```python
class QuestProgress(Base):
    """
    Quest progress tracking (child playing quest)
    Merged: pas_in_peace + inner_edu
    """
    __tablename__ = "quest_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    quest_id = Column(UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False, index=True)

    # Progress state
    current_node_id = Column(String(255), nullable=True)
    # Current node in graph_structure

    current_step = Column(Integer, default=0)
    # Linear step counter

    completed = Column(Boolean, default=False, index=True)

    # Session data
    session_data = Column(JSONB, nullable=True)
    # {
    #   "visited_nodes": ["node1", "node2", ...],
    #   "choices_made": [{"node": "...", "choice": "..."}],
    #   "xp_earned": 150,
    #   "badges_earned": ["first_quest", "math_master"],
    #   "reveal_moments_seen": 2
    # }

    # Performance metrics (Phase 4.3)
    xp_earned = Column(Integer, default=0)
    badges_earned = Column(ARRAY(String), default=list)
    reveal_moments_viewed = Column(Integer, default=0)

    # Timing
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_activity_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    quest = relationship("Quest", back_populates="progress_records")
```

---

### 4. Multi-Track System (NEW - Phase 4)

```python
class TrackType(str, enum.Enum):
    """Recovery track types"""
    SELF_WORK = "self_work"
    CHILD_CONNECTION = "child_connection"
    NEGOTIATION = "negotiation"
    COMMUNITY = "community"


class TrackPhase(str, enum.Enum):
    """Track progression phases"""
    AWARENESS = "awareness"
    EXPRESSION = "expression"
    ACTION = "action"
    MASTERY = "mastery"


class UserTrack(Base):
    """
    Multi-track recovery progress (Phase 4.2)
    4 parallel tracks for alienated parents
    """
    __tablename__ = "user_tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Track identity
    track_type = Column(Enum(TrackType), nullable=False, index=True)

    # Progress
    current_phase = Column(Enum(TrackPhase), default=TrackPhase.AWARENESS, index=True)
    completion_percentage = Column(Integer, default=0)
    # 0-100, within current phase

    total_actions = Column(Integer, default=0)
    # Total actions completed in this track

    # Milestones
    milestones_completed = Column(ARRAY(String), default=list)
    # ["first_quest_created", "10_days_streak", "child_response"]

    # Next action suggestion
    next_action = Column(JSONB, nullable=True)
    # {
    #   "type": "quest_create|letter_write|community_post",
    #   "suggestion": "Create your first quest",
    #   "estimated_time": 15
    # }

    # Analytics
    last_activity_at = Column(TIMESTAMP(timezone=True), nullable=True)
    phase_started_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="tracks")
    milestones_rel = relationship("Milestone", back_populates="track")


class Milestone(Base):
    """
    Track milestones (Phase 4.2)
    Celebrations and achievements
    """
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    track_id = Column(UUID(as_uuid=True), ForeignKey("user_tracks.id"), nullable=False, index=True)

    # Milestone data
    milestone_type = Column(String(100), nullable=False, index=True)
    # "first_quest", "10_quests", "streak_7", "child_completed"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Gamification
    xp_reward = Column(Integer, default=0)
    badge = Column(String(100), nullable=True)

    achieved_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    acknowledged = Column(Boolean, default=False)
    # User has seen the celebration

    # Relationships
    track = relationship("UserTrack", back_populates="milestones_rel")
```

---

### 5. Quest Builder Sessions (KEEP - inner_edu)

```python
class QuestBuilderSession(Base):
    """
    AI Quest Builder conversation sessions (inner_edu)
    """
    __tablename__ = "quest_builder_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Conversation state
    current_stage = Column(String(50), default="greeting")
    # "greeting", "collecting_info", "clarifying", "generating", "reviewing", "quest_ready"

    conversation_history = Column(JSONB, default=list)
    # [{"role": "user|assistant", "content": "...", "timestamp": "..."}]

    # Quest being built
    current_graph = Column(JSONB, nullable=True)
    # Graph structure being constructed

    quest_context = Column(JSONB, nullable=True)
    # {
    #   "child_name": "...",
    #   "child_age": 9,
    #   "child_interests": ["animals", "puzzles"],
    #   "family_photos": ["photo1.jpg"],
    #   "family_memories": ["..."],
    #   "family_jokes": ["..."]
    # }

    # Moderation status (Phase 4.2 integration)
    moderation_checked = Column(Boolean, default=False)
    moderation_passed = Column(Boolean, default=False)
    moderation_issues = Column(JSONB, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="builder_sessions")
```

---

### 6. Quest Library & Ratings (KEEP - inner_edu)

```python
class UserQuestLibrary(Base):
    """User's quest collection (inner_edu)"""
    __tablename__ = "user_quest_library"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    quest_id = Column(UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False, index=True)

    # Organization
    folder = Column(String(100), nullable=True)
    # "favorites", "in_progress", "completed", "custom_folder_name"

    notes = Column(Text, nullable=True)
    # Personal notes about this quest

    added_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="quest_library")
    quest = relationship("Quest")


class QuestRating(Base):
    """Quest ratings from community (inner_edu)"""
    __tablename__ = "quest_ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    quest_id = Column(UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False, index=True)

    rating = Column(Integer, nullable=False)
    # 1-5 stars

    review_text = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    quest = relationship("Quest", back_populates="ratings")
```

---

### 7. Psychologist Reviews (NEW - Phase 4.3)

```python
class ReviewStatus(str, enum.Enum):
    """Review status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"


class PsychologistReview(Base):
    """
    Professional psychologist reviews of quests (Phase 4.3)
    """
    __tablename__ = "psychologist_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quest_id = Column(UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False, index=True)
    psychologist_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Review status
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING, index=True)

    # Ratings (1-5 scale)
    emotional_safety_score = Column(Integer, nullable=True)
    therapeutic_correctness_score = Column(Integer, nullable=True)
    age_appropriateness_score = Column(Integer, nullable=True)
    reveal_timing_score = Column(Integer, nullable=True)

    overall_rating = Column(Integer, nullable=True)
    # Average of 4 scores

    # Approval
    is_approved = Column(Boolean, default=False, index=True)

    # Feedback
    feedback_text = Column(Text, nullable=True)

    strengths = Column(ARRAY(Text), nullable=True)
    # ["Good pacing", "Age-appropriate challenges"]

    improvements = Column(ARRAY(Text), nullable=True)
    # ["Could add more emotional scaffolding"]

    red_flags = Column(ARRAY(Text), nullable=True)
    # ["Potential manipulation pattern"]

    notes_for_parent = Column(Text, nullable=True)
    # Private notes visible to parent

    notes_for_community = Column(Text, nullable=True)
    # Public notes visible in badge

    # Playthrough data
    playthrough_duration_minutes = Column(Integer, nullable=True)

    # Timestamps
    requested_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    started_at = Column(TIMESTAMP(timezone=True), nullable=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    quest = relationship("Quest", foreign_keys=[quest_id])
```

---

### 8. Quest Analytics (NEW - Phase 4.3)

```python
class QuestAnalytics(Base):
    """
    Aggregated quest analytics (Phase 4.3)
    Privacy-preserving aggregate data only
    """
    __tablename__ = "quest_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quest_id = Column(UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False, unique=True, index=True)

    # Completion metrics
    total_starts = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)

    # Time metrics (in seconds)
    avg_completion_time = Column(Integer, nullable=True)
    median_completion_time = Column(Integer, nullable=True)

    # Engagement metrics
    avg_xp_earned = Column(Float, default=0.0)
    avg_badges_earned = Column(Float, default=0.0)

    # Reveal moments
    reveal_view_rate = Column(Float, default=0.0)
    # Percentage of users who saw reveal moments

    # Node-level analytics (aggregated)
    node_completion_rates = Column(JSONB, nullable=True)
    # {"node_id": completion_rate, ...}

    node_average_times = Column(JSONB, nullable=True)
    # {"node_id": avg_seconds, ...}

    # Privacy: NO individual user data stored here
    # Only aggregates: counts, averages, percentages

    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    quest = relationship("Quest", back_populates="analytics")
```

---

## 🔄 Migration Strategy

### Step 1: Create Unified Models File

```bash
# Location: /home/user/pas_in_peace/src/database/models_unified.py
# Copy this schema ^
```

### Step 2: Alembic Migration

```python
# alembic/versions/YYYY_MM_DD_unified_schema.py

def upgrade():
    # 1. Extend existing tables (User, Quest, QuestProgress)
    op.add_column('users', sa.Column('parent_name', sa.String(255)))
    op.add_column('users', sa.Column('child_age', sa.Integer))
    op.add_column('users', sa.Column('mode', sa.Enum(UserMode)))
    # ... etc

    # 2. Create new tables (UserTrack, Milestone, ChildPrivacy, etc.)
    op.create_table('user_tracks', ...)
    op.create_table('milestones', ...)
    op.create_table('child_privacy', ...)
    op.create_table('psychologist_reviews', ...)
    op.create_table('quest_analytics', ...)

    # 3. Migrate data if needed
    # (Most tables are new, so no data migration required)
```

### Step 3: Update DatabaseManager

```python
# src/database/manager.py
# Update to use unified models
from src.database.models_unified import (
    User, Quest, QuestProgress, UserTrack, Milestone,
    ChildPrivacy, QuestAnalytics, PsychologistReview,
    QuestBuilderSession, UserQuestLibrary, QuestRating
)
```

---

## 📝 Implementation Checklist

- [ ] Create `models_unified.py` with all schemas above
- [ ] Write Alembic migration `unified_schema.py`
- [ ] Test migration on development database
- [ ] Update DatabaseManager to use unified models
- [ ] Update all API routes to use unified models
- [ ] Run tests to ensure no breaking changes
- [ ] Deploy to staging
- [ ] Deploy to production

---

## ✅ Benefits of Unified Schema

1. **Single Source of Truth**: One database for both projects
2. **No Duplication**: Merged models eliminate redundancy
3. **Privacy-First**: ChildPrivacy table enforces consent
4. **Analytics-Ready**: Aggregate data without privacy violations
5. **Modular**: Can still run inner_edu or pas_in_peace independently
6. **Scalable**: Schema supports both Educational and Therapeutic modes

---

**Status:** ✅ Schema finalized, ready for implementation
**Next Step:** Create Alembic migration

