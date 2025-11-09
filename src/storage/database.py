"""Database manager for PostgreSQL operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update, delete, func
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.logger import get_logger
from .models import (
    Base, User, Session, Message, Goal, Letter,
    Quest, CreativeProject, QuestAnalytics, ChildPrivacySettings,
    PsychologicalProfile, TrackMilestone,
    QuestStatusEnum, ModerationStatusEnum, ProjectTypeEnum
)


logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self):
        """Initialize database manager."""
        self.engine = None
        self.async_session_maker = None

    async def initialize(self) -> None:
        """Initialize database connection."""
        try:
            # Create async engine
            self.engine = create_async_engine(
                settings.database_url,
                echo=settings.debug,
                pool_size=10,
                max_overflow=20,
            )

            # Create session maker
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("database_initialized", url=settings.database_url.split("@")[1])

        except Exception as e:
            logger.error("database_init_failed", error=str(e))
            raise

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """Get database session context manager."""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized")

        session = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("database_session_error", error=str(e))
            raise
        finally:
            await session.close()

    # User operations
    async def get_or_create_user(self, telegram_id: str) -> User:
        """Get existing user or create new one."""
        async with self.session() as session:
            # Try to get existing user
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Update last activity
                user.last_activity = datetime.utcnow()
                return user

            # Create new user
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.flush()

            logger.info("user_created", telegram_id=telegram_id, user_id=user.id)
            return user

    async def update_user_state(
        self,
        telegram_id: str,
        state: Optional[str] = None,
        emotional_score: Optional[float] = None,
        crisis_level: Optional[float] = None,
        therapy_phase: Optional[str] = None,
        total_messages: Optional[int] = None,  # NEW: Fix for Bug #1
    ) -> None:
        """Update user state."""
        async with self.session() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return

            if state:
                user.current_state = state
            if emotional_score is not None:
                user.emotional_score = emotional_score
            if crisis_level is not None:
                user.crisis_level = crisis_level
            if therapy_phase:
                user.therapy_phase = therapy_phase
            if total_messages is not None:  # NEW: Update total_messages
                user.total_messages = total_messages

            user.last_activity = datetime.utcnow()

    # Session operations
    async def create_session(self, user_id: int) -> Session:
        """Create new therapy session."""
        async with self.session() as db_session:
            # Get session count for user
            stmt = select(func.count(Session.id)).where(Session.user_id == user_id)
            result = await db_session.execute(stmt)
            session_count = result.scalar() or 0

            # Create session
            new_session = Session(
                user_id=user_id,
                session_number=session_count + 1
            )
            db_session.add(new_session)
            await db_session.flush()

            logger.info("session_created", user_id=user_id, session_id=new_session.id)
            return new_session

    async def end_session(
        self,
        session_id: int,
        final_emotional_score: float,
        summary: Optional[str] = None
    ) -> None:
        """End therapy session."""
        async with self.session() as db_session:
            stmt = select(Session).where(Session.id == session_id)
            result = await db_session.execute(stmt)
            session = result.scalar_one_or_none()

            if session:
                session.ended_at = datetime.utcnow()
                session.duration_seconds = int(
                    (session.ended_at - session.started_at).total_seconds()
                )
                session.final_emotional_score = final_emotional_score
                session.summary = summary

    # Message operations
    async def save_message(
        self,
        user_id: int,
        session_id: Optional[int],
        role: str,
        content: str,  # NEW: actual message content
        content_hash: str,
        detected_emotions: Dict[str, float],
        emotional_intensity: float,
        distress_level: str,
        crisis_detected: bool = False,
        crisis_confidence: float = 0.0,
        guardrail_triggered: Optional[str] = None,
        conversation_state: Optional[str] = None,
    ) -> Message:
        """Save message with content."""
        async with self.session() as db_session:
            message = Message(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,  # NEW: save actual content
                content_hash=content_hash,
                detected_emotions=detected_emotions,
                emotional_intensity=emotional_intensity,
                distress_level=distress_level,
                crisis_detected=crisis_detected,
                crisis_confidence=crisis_confidence,
                guardrail_triggered=guardrail_triggered,
                conversation_state=conversation_state,
            )
            db_session.add(message)
            await db_session.flush()

            # NOTE: total_messages counter is managed by StateManager
            # It increments user_state.messages_count and saves via save_user_state()
            # This prevents double-counting (user + assistant messages)

            return message

    async def load_message_history(
        self,
        telegram_id: str,
        limit: int = 50
    ) -> List[Message]:
        """Load message history for a user from database."""
        async with self.session() as db_session:
            # Get user first
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await db_session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return []

            # Get messages ordered by creation time (oldest first for proper history)
            stmt = select(Message).where(
                Message.user_id == user.id
            ).order_by(Message.created_at.asc()).limit(limit)

            result = await db_session.execute(stmt)
            return list(result.scalars().all())

    # Goal operations
    async def create_goal(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Goal:
        """Create new goal."""
        async with self.session() as db_session:
            goal = Goal(
                user_id=user_id,
                title=title,
                description=description,
                category=category,
            )
            db_session.add(goal)
            await db_session.flush()

            logger.info("goal_created", user_id=user_id, goal_id=goal.id)
            return goal

    async def get_active_goals(self, user_id: int) -> List[Goal]:
        """Get user's active goals."""
        async with self.session() as db_session:
            stmt = select(Goal).where(
                Goal.user_id == user_id,
                Goal.status == "active"
            ).order_by(Goal.created_at.desc())
            result = await db_session.execute(stmt)
            return list(result.scalars().all())

    async def update_goal_progress(
        self,
        goal_id: int,
        progress_percentage: float,
        status: Optional[str] = None,
    ) -> None:
        """Update goal progress."""
        async with self.session() as db_session:
            stmt = select(Goal).where(Goal.id == goal_id)
            result = await db_session.execute(stmt)
            goal = result.scalar_one_or_none()

            if goal:
                goal.progress_percentage = progress_percentage
                goal.last_reviewed = datetime.utcnow()
                if status:
                    goal.status = status
                if progress_percentage >= 100:
                    goal.completed_at = datetime.utcnow()

    # Letter operations
    async def create_letter(
        self,
        user_id: int,
        title: Optional[str] = None,
        recipient_role: Optional[str] = None,
        purpose: Optional[str] = None,
        # Sprint 9 fields
        letter_type: Optional[str] = None,
        draft_content: Optional[str] = None,
        communication_style: Optional[str] = None,
        toxicity_score: Optional[float] = None,
        toxicity_details: Optional[dict] = None,
        toxicity_warnings_ignored: Optional[bool] = None,
        telegraph_url: Optional[str] = None,
        telegraph_path: Optional[str] = None,
        telegraph_access_token: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Letter:
        """Create new letter draft with optional Sprint 9 fields."""
        async with self.session() as db_session:
            letter = Letter(
                user_id=user_id,
                title=title,
                recipient_role=recipient_role,
                purpose=purpose,
            )

            # Set Sprint 9 fields if provided
            if letter_type:
                letter.letter_type = letter_type
            if draft_content:
                letter.draft_content = draft_content
            if communication_style:
                letter.communication_style = communication_style
            if toxicity_score is not None:
                letter.toxicity_score = toxicity_score
            if toxicity_details:
                letter.toxicity_details = toxicity_details
            if toxicity_warnings_ignored is not None:
                letter.toxicity_warnings_ignored = toxicity_warnings_ignored
            if telegraph_url:
                letter.telegraph_url = telegraph_url
            if telegraph_path:
                letter.telegraph_path = telegraph_path
            if telegraph_access_token:
                letter.telegraph_access_token = telegraph_access_token
            if status:
                letter.status = status

            db_session.add(letter)
            await db_session.flush()

            logger.info("letter_created", user_id=user_id, letter_id=letter.id, letter_type=letter_type)
            return letter

    async def update_letter_draft(
        self,
        letter_id: int,
        draft_content: str,
        version_number: Optional[int] = None,
    ) -> None:
        """Update letter draft."""
        async with self.session() as db_session:
            stmt = select(Letter).where(Letter.id == letter_id)
            result = await db_session.execute(stmt)
            letter = result.scalar_one_or_none()

            if letter:
                letter.draft_content = draft_content
                letter.last_edited = datetime.utcnow()
                if version_number:
                    letter.version_number = version_number

    async def get_user_letters(self, user_id: int, status: Optional[str] = None) -> List[Letter]:
        """Get user's letters."""
        async with self.session() as db_session:
            stmt = select(Letter).where(Letter.user_id == user_id)
            if status:
                stmt = stmt.where(Letter.status == status)
            stmt = stmt.order_by(Letter.created_at.desc())

            result = await db_session.execute(stmt)
            return list(result.scalars().all())

    async def get_letter_by_id(self, letter_id: int) -> Optional[Letter]:
        """Get letter by ID."""
        async with self.session() as db_session:
            stmt = select(Letter).where(Letter.id == letter_id)
            result = await db_session.execute(stmt)
            return result.scalar_one_or_none()

    async def save_letter_draft(
        self,
        letter_id: int,
        draft_content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save letter draft content and metadata."""
        async with self.session() as db_session:
            stmt = select(Letter).where(Letter.id == letter_id)
            result = await db_session.execute(stmt)
            letter = result.scalar_one_or_none()

            if letter:
                letter.draft_content = draft_content
                letter.last_edited = datetime.utcnow()

                # Update metadata if provided
                if metadata:
                    if "revision_history" in metadata:
                        letter.revision_history = metadata["revision_history"]
                    if "status" in metadata:
                        letter.status = metadata["status"]

                logger.info("letter_draft_saved", letter_id=letter_id)

    async def update_letter_metadata(
        self,
        letter_id: int,
        toxicity_score: Optional[float] = None,
        toxicity_details: Optional[dict] = None,
        toxicity_warnings_ignored: Optional[bool] = None,
        telegraph_url: Optional[str] = None,
        telegraph_path: Optional[str] = None,
        telegraph_access_token: Optional[str] = None,
        telegraph_versions: Optional[list] = None,
        communication_style: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """Update Sprint 9 letter metadata."""
        async with self.session() as db_session:
            stmt = select(Letter).where(Letter.id == letter_id)
            result = await db_session.execute(stmt)
            letter = result.scalar_one_or_none()

            if letter:
                if toxicity_score is not None:
                    letter.toxicity_score = toxicity_score
                if toxicity_details is not None:
                    letter.toxicity_details = toxicity_details
                if toxicity_warnings_ignored is not None:
                    letter.toxicity_warnings_ignored = toxicity_warnings_ignored
                if telegraph_url:
                    letter.telegraph_url = telegraph_url
                if telegraph_path:
                    letter.telegraph_path = telegraph_path
                if telegraph_access_token:
                    letter.telegraph_access_token = telegraph_access_token
                if telegraph_versions is not None:
                    letter.telegraph_versions = telegraph_versions
                if communication_style:
                    letter.communication_style = communication_style
                if status:
                    letter.status = status

                letter.last_edited = datetime.utcnow()

                logger.info("letter_metadata_updated", letter_id=letter_id)

    # Cleanup and privacy operations
    async def cleanup_old_data(self, days: int = 90) -> None:
        """Clean up old data per privacy policy."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        async with self.session() as db_session:
            # Delete old messages
            stmt = delete(Message).where(Message.created_at < cutoff_date)
            await db_session.execute(stmt)

            # Delete old sessions
            stmt = delete(Session).where(Session.started_at < cutoff_date)
            await db_session.execute(stmt)

            logger.info("old_data_cleaned", cutoff_date=cutoff_date.isoformat())

    async def delete_user_data(self, telegram_id: str) -> None:
        """Delete all user data (GDPR compliance)."""
        async with self.session() as db_session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await db_session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                await db_session.delete(user)  # Cascade will delete related data
                logger.info("user_data_deleted", telegram_id=telegram_id)

    # Quest operations (Phase 4.1)
    async def create_quest(
        self,
        user_id: int,
        quest_id: str,
        title: str,
        quest_yaml: str,
        description: Optional[str] = None,
        child_name: Optional[str] = None,
        child_age: Optional[int] = None,
        child_interests: Optional[List[str]] = None,
        total_nodes: int = 0,
        difficulty_level: Optional[str] = None,
        family_photos: Optional[List[str]] = None,
        family_memories: Optional[List[str]] = None,
        family_jokes: Optional[List[str]] = None,
        familiar_locations: Optional[List[str]] = None,
        reveal_enabled: bool = True,
        reveal_threshold_percentage: float = 0.8,
        reveal_message: Optional[str] = None,
    ) -> Quest:
        """Create new quest for child."""
        async with self.session() as db_session:
            quest = Quest(
                user_id=user_id,
                quest_id=quest_id,
                title=title,
                description=description,
                child_name=child_name,
                child_age=child_age,
                child_interests=child_interests or [],
                quest_yaml=quest_yaml,
                total_nodes=total_nodes,
                difficulty_level=difficulty_level,
                family_photos=family_photos or [],
                family_memories=family_memories or [],
                family_jokes=family_jokes or [],
                familiar_locations=familiar_locations or [],
                reveal_enabled=reveal_enabled,
                reveal_threshold_percentage=reveal_threshold_percentage,
                reveal_message=reveal_message,
                status=QuestStatusEnum.DRAFT,
                moderation_status=ModerationStatusEnum.PENDING,
            )
            db_session.add(quest)
            await db_session.flush()

            # Create associated analytics and privacy settings
            quest_analytics = QuestAnalytics(
                quest_id=quest.id,
                total_nodes=total_nodes
            )
            db_session.add(quest_analytics)

            privacy_settings = ChildPrivacySettings(quest_id=quest.id)
            db_session.add(privacy_settings)

            await db_session.flush()

            logger.info("quest_created", user_id=user_id, quest_id=quest.id, title=title)
            return quest

    async def get_quest(self, quest_id: int) -> Optional[Quest]:
        """Get quest by ID."""
        async with self.session() as db_session:
            stmt = select(Quest).where(Quest.id == quest_id)
            result = await db_session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_quest_by_quest_id(self, quest_id: str) -> Optional[Quest]:
        """Get quest by quest_id string."""
        async with self.session() as db_session:
            stmt = select(Quest).where(Quest.quest_id == quest_id)
            result = await db_session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_user_quests(
        self,
        user_id: int,
        status: Optional[QuestStatusEnum] = None
    ) -> List[Quest]:
        """Get all quests for user, optionally filtered by status."""
        async with self.session() as db_session:
            stmt = select(Quest).where(Quest.user_id == user_id)
            if status:
                stmt = stmt.where(Quest.status == status)
            stmt = stmt.order_by(Quest.created_at.desc())
            result = await db_session.execute(stmt)
            return list(result.scalars().all())

    async def update_quest(
        self,
        quest_id: int,
        quest_yaml: Optional[str] = None,
        status: Optional[QuestStatusEnum] = None,
        moderation_status: Optional[ModerationStatusEnum] = None,
        moderation_issues: Optional[List[Dict]] = None,
        moderation_notes: Optional[str] = None,
        deployed_to_inner_edu: Optional[bool] = None,
        inner_edu_quest_id: Optional[str] = None,
    ) -> None:
        """Update quest fields."""
        async with self.session() as db_session:
            stmt = select(Quest).where(Quest.id == quest_id)
            result = await db_session.execute(stmt)
            quest = result.scalar_one_or_none()

            if quest:
                if quest_yaml:
                    quest.quest_yaml = quest_yaml
                    quest.last_edited = datetime.utcnow()
                if status:
                    quest.status = status
                    if status == QuestStatusEnum.APPROVED:
                        quest.approved_at = datetime.utcnow()
                if moderation_status:
                    quest.moderation_status = moderation_status
                if moderation_issues is not None:
                    quest.moderation_issues = moderation_issues
                if moderation_notes:
                    quest.moderation_notes = moderation_notes
                if deployed_to_inner_edu is not None:
                    quest.deployed_to_inner_edu = deployed_to_inner_edu
                    if deployed_to_inner_edu:
                        quest.deployed_at = datetime.utcnow()
                if inner_edu_quest_id:
                    quest.inner_edu_quest_id = inner_edu_quest_id

    async def delete_quest(self, quest_id: int) -> None:
        """Delete quest (cascade deletes analytics and privacy settings)."""
        async with self.session() as db_session:
            stmt = select(Quest).where(Quest.id == quest_id)
            result = await db_session.execute(stmt)
            quest = result.scalar_one_or_none()

            if quest:
                await db_session.delete(quest)
                logger.info("quest_deleted", quest_id=quest_id)

    # CreativeProject operations (Phase 4.1)
    async def create_creative_project(
        self,
        user_id: int,
        project_type: ProjectTypeEnum,
        quest_id: Optional[int] = None,
        letter_id: Optional[int] = None,
        goal_id: Optional[int] = None,
        affects_tracks: Optional[List[str]] = None,
    ) -> CreativeProject:
        """Create creative project linking quest/letter/goal."""
        async with self.session() as db_session:
            project = CreativeProject(
                user_id=user_id,
                project_type=project_type,
                quest_id=quest_id,
                letter_id=letter_id,
                goal_id=goal_id,
                affects_tracks=affects_tracks or [],
                status="active",
                progress_percentage=0.0,
            )
            db_session.add(project)
            await db_session.flush()

            logger.info(
                "creative_project_created",
                user_id=user_id,
                project_id=project.id,
                project_type=project_type.value
            )
            return project

    async def get_user_projects(
        self,
        user_id: int,
        project_type: Optional[ProjectTypeEnum] = None,
        status: Optional[str] = None,
    ) -> List[CreativeProject]:
        """Get all creative projects for user."""
        async with self.session() as db_session:
            stmt = select(CreativeProject).where(CreativeProject.user_id == user_id)
            if project_type:
                stmt = stmt.where(CreativeProject.project_type == project_type)
            if status:
                stmt = stmt.where(CreativeProject.status == status)
            stmt = stmt.order_by(CreativeProject.last_activity.desc())
            result = await db_session.execute(stmt)
            return list(result.scalars().all())

    async def update_project_progress(
        self,
        project_id: int,
        progress_percentage: float,
        status: Optional[str] = None,
    ) -> None:
        """Update creative project progress."""
        async with self.session() as db_session:
            stmt = select(CreativeProject).where(CreativeProject.id == project_id)
            result = await db_session.execute(stmt)
            project = result.scalar_one_or_none()

            if project:
                project.progress_percentage = progress_percentage
                project.last_activity = datetime.utcnow()
                if status:
                    project.status = status
                if progress_percentage >= 100:
                    project.completed_at = datetime.utcnow()
                    project.status = "completed"

    # QuestAnalytics operations with privacy enforcement (Phase 4.1)
    async def get_quest_analytics(
        self,
        quest_id: int,
        enforce_privacy: bool = True
    ) -> Optional[QuestAnalytics]:
        """Get quest analytics with privacy check."""
        async with self.session() as db_session:
            stmt = select(QuestAnalytics).where(QuestAnalytics.quest_id == quest_id)
            result = await db_session.execute(stmt)
            analytics = result.scalar_one_or_none()

            if analytics and enforce_privacy:
                # Check privacy settings
                privacy_stmt = select(ChildPrivacySettings).where(
                    ChildPrivacySettings.quest_id == quest_id
                )
                privacy_result = await db_session.execute(privacy_stmt)
                privacy_settings = privacy_result.scalar_one_or_none()

                if not privacy_settings or not privacy_settings.consent_given_by_child:
                    logger.warning(
                        "quest_analytics_privacy_blocked",
                        quest_id=quest_id,
                        reason="child_consent_not_given"
                    )
                    return None

            return analytics

    async def update_quest_analytics(
        self,
        quest_id: int,
        nodes_completed: Optional[int] = None,
        completion_percentage: Optional[float] = None,
        educational_progress: Optional[Dict] = None,
        achievements_unlocked: Optional[List[str]] = None,
        play_count_increment: int = 0,
        time_spent_minutes: Optional[float] = None,
        clues_discovered: Optional[int] = None,
        reveal_phase: Optional[str] = None,
        reveal_completed: Optional[bool] = None,
    ) -> None:
        """Update quest analytics (aggregated data only)."""
        async with self.session() as db_session:
            stmt = select(QuestAnalytics).where(QuestAnalytics.quest_id == quest_id)
            result = await db_session.execute(stmt)
            analytics = result.scalar_one_or_none()

            if analytics:
                if nodes_completed is not None:
                    analytics.nodes_completed = nodes_completed
                if completion_percentage is not None:
                    analytics.completion_percentage = completion_percentage
                if educational_progress is not None:
                    analytics.educational_progress = educational_progress
                if achievements_unlocked is not None:
                    analytics.achievements_unlocked = achievements_unlocked
                if play_count_increment > 0:
                    analytics.play_count += play_count_increment
                    analytics.last_played = datetime.utcnow()
                if time_spent_minutes is not None:
                    analytics.total_time_spent_minutes += time_spent_minutes
                    # Recalculate average
                    if analytics.play_count > 0:
                        analytics.average_session_minutes = (
                            analytics.total_time_spent_minutes / analytics.play_count
                        )
                if clues_discovered is not None:
                    analytics.clues_discovered = clues_discovered
                if reveal_phase:
                    analytics.reveal_phase = reveal_phase
                if reveal_completed is not None:
                    analytics.reveal_completed = reveal_completed
                    if reveal_completed:
                        analytics.reveal_completed_at = datetime.utcnow()

                analytics.last_updated = datetime.utcnow()

    # ChildPrivacySettings operations (Phase 4.1)
    async def get_privacy_settings(self, quest_id: int) -> Optional[ChildPrivacySettings]:
        """Get child privacy settings for quest."""
        async with self.session() as db_session:
            stmt = select(ChildPrivacySettings).where(
                ChildPrivacySettings.quest_id == quest_id
            )
            result = await db_session.execute(stmt)
            return result.scalar_one_or_none()

    async def update_privacy_settings(
        self,
        quest_id: int,
        consent_given: Optional[bool] = None,
        share_completion_progress: Optional[bool] = None,
        share_educational_progress: Optional[bool] = None,
        share_achievements: Optional[bool] = None,
        share_play_frequency: Optional[bool] = None,
        notify_both_parents: Optional[bool] = None,
        notification_frequency: Optional[str] = None,
    ) -> None:
        """Update child privacy settings with audit trail."""
        async with self.session() as db_session:
            stmt = select(ChildPrivacySettings).where(
                ChildPrivacySettings.quest_id == quest_id
            )
            result = await db_session.execute(stmt)
            settings = result.scalar_one_or_none()

            if settings:
                # Build audit entry
                changes = {}

                if consent_given is not None and consent_given != settings.consent_given_by_child:
                    changes["consent_given_by_child"] = {
                        "from": settings.consent_given_by_child,
                        "to": consent_given
                    }
                    settings.consent_given_by_child = consent_given
                    if consent_given:
                        settings.consent_timestamp = datetime.utcnow()
                    else:
                        settings.consent_revoked_at = datetime.utcnow()

                if share_completion_progress is not None:
                    settings.share_completion_progress = share_completion_progress
                if share_educational_progress is not None:
                    settings.share_educational_progress = share_educational_progress
                if share_achievements is not None:
                    settings.share_achievements = share_achievements
                if share_play_frequency is not None:
                    settings.share_play_frequency = share_play_frequency
                if notify_both_parents is not None:
                    settings.notify_both_parents = notify_both_parents
                if notification_frequency is not None:
                    settings.notification_frequency = notification_frequency

                # Append audit entry
                if changes:
                    audit_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "changes": changes
                    }
                    consent_history = settings.consent_history or []
                    consent_history.append(audit_entry)
                    settings.consent_history = consent_history

                settings.last_updated = datetime.utcnow()

                logger.info(
                    "privacy_settings_updated",
                    quest_id=quest_id,
                    consent_given=consent_given,
                    changes=changes
                )

    async def can_share_with_parent(self, quest_id: int) -> bool:
        """Check if data can be shared with parent (privacy enforcement)."""
        settings = await self.get_privacy_settings(quest_id)
        if not settings:
            return False
        return settings.consent_given_by_child

    # PsychologicalProfile operations (Phase 4.1)
    async def get_or_create_psychological_profile(self, user_id: int) -> PsychologicalProfile:
        """Get or create psychological profile for user."""
        async with self.session() as db_session:
            stmt = select(PsychologicalProfile).where(
                PsychologicalProfile.user_id == user_id
            )
            result = await db_session.execute(stmt)
            profile = result.scalar_one_or_none()

            if not profile:
                profile = PsychologicalProfile(user_id=user_id)
                db_session.add(profile)
                await db_session.flush()
                logger.info("psychological_profile_created", user_id=user_id)

            return profile

    async def update_psychological_profile(
        self,
        user_id: int,
        emotional_trends: Optional[Dict] = None,
        emotional_baseline: Optional[float] = None,
        crisis_incident: Optional[Dict] = None,
        coping_strategy_effectiveness: Optional[Dict[str, float]] = None,
        triggers: Optional[List[str]] = None,
        communication_style: Optional[str] = None,
        toxic_pattern: Optional[Dict] = None,
        growth_areas: Optional[List[str]] = None,
        recommended_techniques: Optional[List[str]] = None,
    ) -> None:
        """Update psychological profile with aggregated data."""
        async with self.session() as db_session:
            profile = await self.get_or_create_psychological_profile(user_id)

            if emotional_trends:
                profile.emotional_trends = emotional_trends
            if emotional_baseline is not None:
                profile.emotional_baseline = emotional_baseline
            if crisis_incident:
                crisis_history = profile.crisis_history or []
                crisis_history.append(crisis_incident)
                profile.crisis_history = crisis_history
                profile.last_crisis_date = datetime.utcnow()
            if coping_strategy_effectiveness:
                profile.coping_strategies = coping_strategy_effectiveness
                # Find most effective
                if coping_strategy_effectiveness:
                    most_effective = max(
                        coping_strategy_effectiveness.items(),
                        key=lambda x: x[1]
                    )
                    profile.most_effective_technique = most_effective[0]
            if triggers is not None:
                profile.triggers = triggers
            if communication_style:
                profile.communication_style = communication_style
            if toxic_pattern:
                toxic_patterns = profile.toxic_patterns or []
                toxic_patterns.append(toxic_pattern)
                profile.toxic_patterns = toxic_patterns
                profile.last_toxicity_incident = datetime.utcnow()
            if growth_areas is not None:
                profile.growth_areas = growth_areas
            if recommended_techniques is not None:
                profile.recommended_techniques = recommended_techniques

            profile.last_updated = datetime.utcnow()

    # TrackMilestone operations (Phase 4.1)
    async def create_track_milestone(
        self,
        user_id: int,
        track: str,
        milestone_type: str,
        milestone_name: Optional[str] = None,
        description: Optional[str] = None,
        achievement_context: Optional[Dict] = None,
        related_project_id: Optional[int] = None,
        related_project_type: Optional[str] = None,
    ) -> TrackMilestone:
        """Create track milestone for recovery progress."""
        async with self.session() as db_session:
            milestone = TrackMilestone(
                user_id=user_id,
                track=track,
                milestone_type=milestone_type,
                milestone_name=milestone_name,
                description=description,
                achievement_context=achievement_context or {},
                related_project_id=related_project_id,
                related_project_type=related_project_type,
            )
            db_session.add(milestone)
            await db_session.flush()

            logger.info(
                "track_milestone_created",
                user_id=user_id,
                track=track,
                milestone_type=milestone_type
            )
            return milestone

    async def get_user_milestones(
        self,
        user_id: int,
        track: Optional[str] = None,
        limit: int = 50,
    ) -> List[TrackMilestone]:
        """Get user's track milestones."""
        async with self.session() as db_session:
            stmt = select(TrackMilestone).where(TrackMilestone.user_id == user_id)
            if track:
                stmt = stmt.where(TrackMilestone.track == track)
            stmt = stmt.order_by(TrackMilestone.achieved_at.desc()).limit(limit)
            result = await db_session.execute(stmt)
            return list(result.scalars().all())

    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("database_closed")