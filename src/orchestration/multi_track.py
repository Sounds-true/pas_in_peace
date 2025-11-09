"""Multi-track recovery system manager.

Manages parallel progress across 4 recovery tracks:
- SELF_WORK: Emotional processing, CBT, journaling
- CHILD_CONNECTION: Quests, letters to child, photo albums
- NEGOTIATION: Communication with ex-partner, legal actions
- COMMUNITY: Support groups, connections with other parents

Each track has phases: AWARENESS → EXPRESSION → ACTION → MASTERY
"""

from typing import Dict, List, Optional, TypedDict
from datetime import datetime, timedelta
from enum import Enum

from src.core.logger import get_logger
from src.storage.models import RecoveryTrackEnum, TrackPhaseEnum

logger = get_logger(__name__)


class TrackProgress(TypedDict):
    """Progress state for a single recovery track."""
    track: str  # RecoveryTrackEnum value
    phase: str  # TrackPhaseEnum value
    completion_percentage: int  # 0-100
    milestones: List[Dict]  # [{"name": str, "achieved_at": str, "description": str}]
    next_action: Dict  # {"suggestion": str, "technique": str, "estimated_time": str}
    last_activity: Optional[str]  # ISO datetime
    total_actions: int


# Track-to-action mapping for intent detection
TRACK_ACTION_PATTERNS = {
    RecoveryTrackEnum.SELF_WORK.value: [
        "чувств", "эмоц", "гнев", "грусть", "тревог", "стресс",
        "CBT", "когнитив", "переосмысл", "дневник", "рефлекс",
        "медитац", "дыхани", "практик", "упражнен",
    ],
    RecoveryTrackEnum.CHILD_CONNECTION.value: [
        "ребен", "сын", "дочь", "дет", "квест", "письмо",
        "фото", "альбом", "воспоминан", "подарок", "история",
        "игр", "связь с ребенком", "контакт",
    ],
    RecoveryTrackEnum.NEGOTIATION.value: [
        "бывш", "экс-партн", "алиенатор", "перегов", "общени",
        "суд", "юрист", "адвокат", "документ", "заявлен",
        "встреч", "разговор", "договориться",
    ],
    RecoveryTrackEnum.COMMUNITY.value: [
        "груп", "поддержк", "сообщество", "други", "родител",
        "форум", "чат", "встреч", "ресурс", "организац",
        "помощь", "совет", "опыт",
    ],
}

# Cross-track impact: which actions affect multiple tracks
CROSS_TRACK_ACTIONS = {
    "quest_created": [
        RecoveryTrackEnum.SELF_WORK.value,  # Creative expression
        RecoveryTrackEnum.CHILD_CONNECTION.value,  # Primary
    ],
    "letter_to_child": [
        RecoveryTrackEnum.SELF_WORK.value,  # Emotional processing
        RecoveryTrackEnum.CHILD_CONNECTION.value,  # Primary
    ],
    "letter_to_ex": [
        RecoveryTrackEnum.SELF_WORK.value,  # Emotional processing
        RecoveryTrackEnum.NEGOTIATION.value,  # Primary
    ],
    "goal_set": [
        RecoveryTrackEnum.SELF_WORK.value,  # Self-improvement
    ],
    "support_group_joined": [
        RecoveryTrackEnum.COMMUNITY.value,  # Primary
        RecoveryTrackEnum.SELF_WORK.value,  # Emotional support
    ],
}


class MultiTrackManager:
    """Manages multi-track recovery system."""

    def __init__(self, db_manager):
        """Initialize multi-track manager.

        Args:
            db_manager: DatabaseManager instance for persistence
        """
        self.db = db_manager

    async def initialize_tracks(self, user_id: int) -> Dict[str, TrackProgress]:
        """Initialize all 4 recovery tracks for new user.

        Creates empty progress state for each track with default values.
        Idempotent - safe to call multiple times.

        Args:
            user_id: User ID

        Returns:
            Dict of track_name -> TrackProgress
        """
        tracks = {}

        for track in RecoveryTrackEnum:
            tracks[track.value] = TrackProgress(
                track=track.value,
                phase=TrackPhaseEnum.AWARENESS.value,
                completion_percentage=0,
                milestones=[],
                next_action={
                    "suggestion": self._get_initial_suggestion(track.value),
                    "technique": self._get_initial_technique(track.value),
                    "estimated_time": "5-10 minutes"
                },
                last_activity=None,
                total_actions=0
            )

        logger.info("tracks_initialized", user_id=user_id, tracks=list(tracks.keys()))
        return tracks

    def _get_initial_suggestion(self, track: str) -> str:
        """Get initial next action suggestion for track."""
        suggestions = {
            RecoveryTrackEnum.SELF_WORK.value:
                "Let's start with understanding your emotional state. How are you feeling today?",
            RecoveryTrackEnum.CHILD_CONNECTION.value:
                "Ready to reconnect with your child? We could create a quest or write a letter.",
            RecoveryTrackEnum.NEGOTIATION.value:
                "Let's review your communication strategy. What's your goal with your ex-partner?",
            RecoveryTrackEnum.COMMUNITY.value:
                "Finding support is important. Would you like help finding parent support groups?",
        }
        return suggestions.get(track, "Let's explore this area together.")

    def _get_initial_technique(self, track: str) -> str:
        """Get initial technique for track."""
        techniques = {
            RecoveryTrackEnum.SELF_WORK.value: "active_listening",
            RecoveryTrackEnum.CHILD_CONNECTION.value: "quest_builder",
            RecoveryTrackEnum.NEGOTIATION.value: "letter_writing",
            RecoveryTrackEnum.COMMUNITY.value: "resource_finder",
        }
        return techniques.get(track, "active_listening")

    async def get_all_progress(self, user_id: int) -> Dict[str, TrackProgress]:
        """Get progress for all tracks.

        Args:
            user_id: User ID

        Returns:
            Dict of track_name -> TrackProgress
        """
        # Get user from database
        user = await self.db.get_or_create_user(str(user_id))

        # If no tracks initialized, initialize them
        if not user.recovery_tracks:
            tracks = await self.initialize_tracks(user_id)
            # Save to database
            await self.db.update_user_state(
                telegram_id=str(user_id),
                # NOTE: We'd need to add a method to update recovery_tracks
            )
            return tracks

        return user.recovery_tracks

    def get_primary_track(self, user_recovery_tracks: Dict) -> str:
        """Determine primary (most active) track.

        Args:
            user_recovery_tracks: User's recovery_tracks JSON

        Returns:
            Track name with highest recent activity
        """
        if not user_recovery_tracks:
            return RecoveryTrackEnum.SELF_WORK.value

        # Find track with most recent activity
        most_recent = None
        most_recent_track = RecoveryTrackEnum.SELF_WORK.value

        for track_name, progress in user_recovery_tracks.items():
            last_activity = progress.get("last_activity")
            if last_activity:
                activity_time = datetime.fromisoformat(last_activity)
                if most_recent is None or activity_time > most_recent:
                    most_recent = activity_time
                    most_recent_track = track_name

        return most_recent_track

    async def update_progress(
        self,
        user_id: int,
        track: str,
        delta: int,
        action_type: str,
        milestone_achieved: Optional[str] = None
    ) -> Dict[str, TrackProgress]:
        """Update progress for one or more tracks.

        Args:
            user_id: User ID
            track: Primary track being updated
            delta: Progress increase (0-100)
            action_type: Type of action (for cross-track impact)
            milestone_achieved: Optional milestone name

        Returns:
            Updated tracks dict
        """
        tracks = await self.get_all_progress(user_id)

        # Update primary track
        await self._update_single_track(
            tracks, track, delta, milestone_achieved
        )

        # Check for cross-track impact
        affected_tracks = self.get_cross_track_impact(action_type)
        for affected_track in affected_tracks:
            if affected_track != track:
                # Secondary tracks get partial credit
                secondary_delta = max(1, delta // 3)
                await self._update_single_track(
                    tracks, affected_track, secondary_delta, None
                )
                logger.info(
                    "cross_track_progress",
                    primary_track=track,
                    affected_track=affected_track,
                    delta=secondary_delta
                )

        # TODO: Persist to database
        # await self.db.update_user_recovery_tracks(user_id, tracks)

        return tracks

    async def _update_single_track(
        self,
        tracks: Dict[str, TrackProgress],
        track: str,
        delta: int,
        milestone_achieved: Optional[str] = None
    ) -> None:
        """Update progress for a single track (internal helper)."""
        if track not in tracks:
            logger.warning("track_not_found", track=track)
            return

        progress = tracks[track]

        # Update percentage
        old_percentage = progress["completion_percentage"]
        new_percentage = min(100, old_percentage + delta)
        progress["completion_percentage"] = new_percentage

        # Update phase based on percentage
        if new_percentage >= 75:
            progress["phase"] = TrackPhaseEnum.MASTERY.value
        elif new_percentage >= 50:
            progress["phase"] = TrackPhaseEnum.ACTION.value
        elif new_percentage >= 25:
            progress["phase"] = TrackPhaseEnum.EXPRESSION.value
        else:
            progress["phase"] = TrackPhaseEnum.AWARENESS.value

        # Add milestone if provided
        if milestone_achieved:
            milestone = {
                "name": milestone_achieved,
                "achieved_at": datetime.utcnow().isoformat(),
                "description": f"Completed milestone in {track} track"
            }
            progress["milestones"].append(milestone)
            logger.info("milestone_achieved", track=track, milestone=milestone_achieved)

        # Update activity timestamp
        progress["last_activity"] = datetime.utcnow().isoformat()
        progress["total_actions"] += 1

        # Generate next action suggestion
        progress["next_action"] = self._generate_next_action(track, new_percentage)

    def _generate_next_action(self, track: str, percentage: int) -> Dict:
        """Generate AI-powered next action suggestion.

        NOTE: This is a simplified version. Full version would use GPT-4.

        Args:
            track: Track name
            percentage: Current completion percentage

        Returns:
            Next action dict with suggestion, technique, estimated_time
        """
        # Phase-aware suggestions
        phase = TrackPhaseEnum.AWARENESS.value
        if percentage >= 75:
            phase = TrackPhaseEnum.MASTERY.value
        elif percentage >= 50:
            phase = TrackPhaseEnum.ACTION.value
        elif percentage >= 25:
            phase = TrackPhaseEnum.EXPRESSION.value

        suggestions = {
            (RecoveryTrackEnum.SELF_WORK.value, TrackPhaseEnum.AWARENESS.value):
                ("Let's explore your emotions deeper", "cbt", "10-15 minutes"),
            (RecoveryTrackEnum.SELF_WORK.value, TrackPhaseEnum.EXPRESSION.value):
                ("Write about your feelings in a letter", "letter_writing", "20-30 minutes"),
            (RecoveryTrackEnum.SELF_WORK.value, TrackPhaseEnum.ACTION.value):
                ("Set a goal for emotional regulation", "goal_tracking", "15-20 minutes"),
            (RecoveryTrackEnum.SELF_WORK.value, TrackPhaseEnum.MASTERY.value):
                ("Reflect on your growth journey", "active_listening", "10 minutes"),

            (RecoveryTrackEnum.CHILD_CONNECTION.value, TrackPhaseEnum.AWARENESS.value):
                ("Tell me about your child", "active_listening", "5-10 minutes"),
            (RecoveryTrackEnum.CHILD_CONNECTION.value, TrackPhaseEnum.EXPRESSION.value):
                ("Create a personalized quest for your child", "quest_builder", "30-45 minutes"),
            (RecoveryTrackEnum.CHILD_CONNECTION.value, TrackPhaseEnum.ACTION.value):
                ("Write a letter to your child", "letter_writing", "20-30 minutes"),
            (RecoveryTrackEnum.CHILD_CONNECTION.value, TrackPhaseEnum.MASTERY.value):
                ("Create a photo album of memories", "project_creator", "30+ minutes"),

            (RecoveryTrackEnum.NEGOTIATION.value, TrackPhaseEnum.AWARENESS.value):
                ("Review your communication history", "active_listening", "10 minutes"),
            (RecoveryTrackEnum.NEGOTIATION.value, TrackPhaseEnum.EXPRESSION.value):
                ("Draft a neutral communication to your ex", "letter_writing", "20-30 minutes"),
            (RecoveryTrackEnum.NEGOTIATION.value, TrackPhaseEnum.ACTION.value):
                ("Prepare for mediation or court", "resource_finder", "30 minutes"),
            (RecoveryTrackEnum.NEGOTIATION.value, TrackPhaseEnum.MASTERY.value):
                ("Develop long-term co-parenting strategy", "goal_tracking", "20 minutes"),

            (RecoveryTrackEnum.COMMUNITY.value, TrackPhaseEnum.AWARENESS.value):
                ("Explore available support resources", "resource_finder", "10-15 minutes"),
            (RecoveryTrackEnum.COMMUNITY.value, TrackPhaseEnum.EXPRESSION.value):
                ("Join a parent support group", "resource_finder", "Variable"),
            (RecoveryTrackEnum.COMMUNITY.value, TrackPhaseEnum.ACTION.value):
                ("Share your story with the community", "active_listening", "15-20 minutes"),
            (RecoveryTrackEnum.COMMUNITY.value, TrackPhaseEnum.MASTERY.value):
                ("Mentor other alienated parents", "active_listening", "Ongoing"),
        }

        suggestion, technique, time = suggestions.get(
            (track, phase),
            ("Continue your recovery journey", "active_listening", "10 minutes")
        )

        return {
            "suggestion": suggestion,
            "technique": technique,
            "estimated_time": time
        }

    def detect_track_from_message(self, message: str) -> str:
        """Detect which track a message relates to (intent detection).

        Uses keyword matching as fallback for ML-based intent classification.

        Args:
            message: User message

        Returns:
            Track name (defaults to SELF_WORK if unclear)
        """
        message_lower = message.lower()

        # Count matches for each track
        track_scores = {}
        for track, patterns in TRACK_ACTION_PATTERNS.items():
            score = sum(1 for pattern in patterns if pattern in message_lower)
            track_scores[track] = score

        # Return track with highest score
        if max(track_scores.values()) > 0:
            best_track = max(track_scores.items(), key=lambda x: x[1])[0]
            logger.info("track_detected", track=best_track, message_preview=message[:50])
            return best_track

        # Default to SELF_WORK
        return RecoveryTrackEnum.SELF_WORK.value

    def get_cross_track_impact(self, action_type: str) -> List[str]:
        """Get list of tracks affected by an action.

        Args:
            action_type: Type of action (e.g., "quest_created")

        Returns:
            List of track names affected by this action
        """
        return CROSS_TRACK_ACTIONS.get(action_type, [])

    def should_suggest_track_switch(
        self,
        current_track: str,
        tracks: Dict[str, TrackProgress]
    ) -> Optional[str]:
        """Determine if we should suggest switching tracks.

        Suggests switch if:
        - Current track >30 days inactive
        - Another track has much lower progress

        Args:
            current_track: Current primary track
            tracks: All track progress

        Returns:
            Suggested track name or None
        """
        current_progress = tracks.get(current_track, {})
        last_activity = current_progress.get("last_activity")

        # Check if current track inactive for >30 days
        if last_activity:
            last_time = datetime.fromisoformat(last_activity)
            if datetime.utcnow() - last_time > timedelta(days=30):
                # Find track with lowest progress
                min_progress_track = min(
                    tracks.items(),
                    key=lambda x: x[1]["completion_percentage"]
                )[0]
                if min_progress_track != current_track:
                    logger.info(
                        "track_switch_suggested",
                        from_track=current_track,
                        to_track=min_progress_track,
                        reason="current_inactive"
                    )
                    return min_progress_track

        return None

    async def check_milestone(
        self,
        user_id: int,
        track: str,
        action_type: str
    ) -> Optional[str]:
        """Check if action triggers a milestone.

        Args:
            user_id: User ID
            track: Track name
            action_type: Action type

        Returns:
            Milestone name if achieved, None otherwise
        """
        # Milestone definitions
        milestones = {
            (RecoveryTrackEnum.SELF_WORK.value, "first_cbt"):
                "First CBT Reframing",
            (RecoveryTrackEnum.CHILD_CONNECTION.value, "quest_created"):
                "Quest Creator",
            (RecoveryTrackEnum.CHILD_CONNECTION.value, "letter_to_child"):
                "Letter to Child",
            (RecoveryTrackEnum.NEGOTIATION.value, "letter_to_ex"):
                "First Communication Attempt",
            (RecoveryTrackEnum.COMMUNITY.value, "support_group_joined"):
                "Community Member",
        }

        milestone = milestones.get((track, action_type))
        if milestone:
            # Save to database
            await self.db.create_track_milestone(
                user_id=user_id,
                track=track,
                milestone_type=action_type,
                milestone_name=milestone,
            )
            logger.info("milestone_created", user_id=user_id, track=track, milestone=milestone)

        return milestone
