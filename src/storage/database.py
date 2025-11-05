"""Database manager for PostgreSQL operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update, delete, func
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.logger import get_logger
from .models import Base, User, Session, Message, Goal, Letter


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
        content_hash: str,
        detected_emotions: Dict[str, float],
        emotional_intensity: float,
        distress_level: str,
        crisis_detected: bool = False,
        crisis_confidence: float = 0.0,
        guardrail_triggered: Optional[str] = None,
        conversation_state: Optional[str] = None,
    ) -> Message:
        """Save message (PII-scrubbed)."""
        async with self.session() as db_session:
            message = Message(
                user_id=user_id,
                session_id=session_id,
                role=role,
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

            # Update user message count
            stmt = select(User).where(User.id == user_id)
            result = await db_session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                user.total_messages += 1

            return message

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

    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("database_closed")