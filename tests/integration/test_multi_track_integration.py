"""Integration tests for Multi-Track Recovery System.

Tests integration with StateManager and cross-track impacts.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.orchestration.multi_track import MultiTrackManager, RecoveryTrackEnum, TrackPhaseEnum
from src.storage.database import DatabaseManager
from src.storage.models import User


class TestMultiTrackIntegration:
    """Integration tests for multi-track system."""

    @pytest.fixture
    async def db_manager(self):
        """Create mock database manager."""
        db = AsyncMock(spec=DatabaseManager)

        # Mock get_or_create_user
        user_mock = MagicMock(spec=User)
        user_mock.id = 1
        user_mock.telegram_id = "123456"
        user_mock.recovery_tracks = {}
        user_mock.primary_track = "self_work"
        db.get_or_create_user = AsyncMock(return_value=user_mock)

        # Mock create_track_milestone
        milestone_mock = MagicMock()
        milestone_mock.id = 1
        db.create_track_milestone = AsyncMock(return_value=milestone_mock)

        return db

    @pytest.fixture
    async def multi_track_manager(self, db_manager):
        """Create multi-track manager."""
        return MultiTrackManager(db_manager=db_manager)

    @pytest.mark.asyncio
    async def test_initialize_tracks(self, multi_track_manager):
        """Test initializing all 4 tracks for new user."""

        tracks = await multi_track_manager.initialize_tracks(user_id=1)

        # Should have all 4 tracks
        assert len(tracks) == 4
        assert RecoveryTrackEnum.SELF_WORK.value in tracks
        assert RecoveryTrackEnum.CHILD_CONNECTION.value in tracks
        assert RecoveryTrackEnum.NEGOTIATION.value in tracks
        assert RecoveryTrackEnum.COMMUNITY.value in tracks

        # Each track should start at AWARENESS phase with 0%
        for track_name, progress in tracks.items():
            assert progress["phase"] == TrackPhaseEnum.AWARENESS.value
            assert progress["completion_percentage"] == 0
            assert progress["total_actions"] == 0
            assert len(progress["milestones"]) == 0
            assert "next_action" in progress

    @pytest.mark.asyncio
    async def test_update_progress_single_track(
        self,
        multi_track_manager,
        db_manager
    ):
        """Test updating progress for a single track."""

        # Initialize tracks first
        await multi_track_manager.initialize_tracks(user_id=1)

        # Update SELF_WORK track
        tracks = await multi_track_manager.update_progress(
            user_id=1,
            track=RecoveryTrackEnum.SELF_WORK.value,
            delta=15,
            action_type="goal_set",
            milestone_achieved="First Goal"
        )

        self_work = tracks[RecoveryTrackEnum.SELF_WORK.value]

        # Should have 15% progress
        assert self_work["completion_percentage"] == 15

        # Should still be in AWARENESS phase (0-25%)
        assert self_work["phase"] == TrackPhaseEnum.AWARENESS.value

        # Should have milestone
        assert len(self_work["milestones"]) == 1
        assert self_work["milestones"][0]["name"] == "First Goal"

        # Should have updated activity
        assert self_work["total_actions"] == 1

    @pytest.mark.asyncio
    async def test_cross_track_impact(
        self,
        multi_track_manager,
        db_manager
    ):
        """Test that actions can affect multiple tracks."""

        await multi_track_manager.initialize_tracks(user_id=1)

        # Creating a quest should impact SELF_WORK and CHILD_CONNECTION
        tracks = await multi_track_manager.update_progress(
            user_id=1,
            track=RecoveryTrackEnum.CHILD_CONNECTION.value,
            delta=20,
            action_type="quest_created",
            milestone_achieved="Quest Creator"
        )

        # Primary track (CHILD_CONNECTION) should have full delta
        child_conn = tracks[RecoveryTrackEnum.CHILD_CONNECTION.value]
        assert child_conn["completion_percentage"] == 20

        # Secondary track (SELF_WORK) should have partial credit (20/3 ≈ 6)
        self_work = tracks[RecoveryTrackEnum.SELF_WORK.value]
        assert self_work["completion_percentage"] > 0
        assert self_work["completion_percentage"] < child_conn["completion_percentage"]

    @pytest.mark.asyncio
    async def test_phase_transitions(
        self,
        multi_track_manager,
        db_manager
    ):
        """Test that phases transition correctly based on percentage."""

        await multi_track_manager.initialize_tracks(user_id=1)

        track = RecoveryTrackEnum.SELF_WORK.value

        # Start: AWARENESS (0-25%)
        tracks1 = await multi_track_manager.update_progress(
            user_id=1,
            track=track,
            delta=20,
            action_type="goal_set"
        )
        assert tracks1[track]["phase"] == TrackPhaseEnum.AWARENESS.value

        # Progress to EXPRESSION (25-50%)
        tracks2 = await multi_track_manager.update_progress(
            user_id=1,
            track=track,
            delta=20,
            action_type="letter_to_child"
        )
        assert tracks2[track]["phase"] == TrackPhaseEnum.EXPRESSION.value

        # Progress to ACTION (50-75%)
        tracks3 = await multi_track_manager.update_progress(
            user_id=1,
            track=track,
            delta=20,
            action_type="goal_set"
        )
        assert tracks3[track]["phase"] == TrackPhaseEnum.ACTION.value

        # Progress to MASTERY (75-100%)
        tracks4 = await multi_track_manager.update_progress(
            user_id=1,
            track=track,
            delta=20,
            action_type="goal_set"
        )
        assert tracks4[track]["phase"] == TrackPhaseEnum.MASTERY.value

    @pytest.mark.asyncio
    async def test_detect_track_from_message(self, multi_track_manager):
        """Test intent detection from user messages."""

        # Test CHILD_CONNECTION patterns
        track1 = multi_track_manager.detect_track_from_message(
            "Хочу создать квест для ребенка"
        )
        assert track1 == RecoveryTrackEnum.CHILD_CONNECTION.value

        track2 = multi_track_manager.detect_track_from_message(
            "Напишу письмо сыну"
        )
        assert track2 == RecoveryTrackEnum.CHILD_CONNECTION.value

        # Test SELF_WORK patterns
        track3 = multi_track_manager.detect_track_from_message(
            "Чувствую грусть и тревогу"
        )
        assert track3 == RecoveryTrackEnum.SELF_WORK.value

        # Test NEGOTIATION patterns
        track4 = multi_track_manager.detect_track_from_message(
            "Нужно поговорить с бывшим партнером"
        )
        assert track4 == RecoveryTrackEnum.NEGOTIATION.value

        # Test COMMUNITY patterns
        track5 = multi_track_manager.detect_track_from_message(
            "Ищу группу поддержки"
        )
        assert track5 == RecoveryTrackEnum.COMMUNITY.value

        # Test default fallback
        track6 = multi_track_manager.detect_track_from_message(
            "Привет, как дела?"
        )
        assert track6 == RecoveryTrackEnum.SELF_WORK.value  # Default

    @pytest.mark.asyncio
    async def test_milestone_creation(
        self,
        multi_track_manager,
        db_manager
    ):
        """Test that milestones are recorded in database."""

        milestone_name = await multi_track_manager.check_milestone(
            user_id=1,
            track=RecoveryTrackEnum.CHILD_CONNECTION.value,
            action_type="quest_created"
        )

        assert milestone_name == "Quest Creator"

        # Verify database method was called
        db_manager.create_track_milestone.assert_called_once()
        call_args = db_manager.create_track_milestone.call_args[1]
        assert call_args["user_id"] == 1
        assert call_args["track"] == RecoveryTrackEnum.CHILD_CONNECTION.value
        assert call_args["milestone_type"] == "quest_created"
        assert call_args["milestone_name"] == "Quest Creator"

    @pytest.mark.asyncio
    async def test_get_primary_track(self, multi_track_manager):
        """Test determining primary (most active) track."""

        # Create tracks with different activity times
        now = datetime.utcnow()

        tracks = {
            RecoveryTrackEnum.SELF_WORK.value: {
                "last_activity": now.isoformat()  # Most recent
            },
            RecoveryTrackEnum.CHILD_CONNECTION.value: {
                "last_activity": None  # Never used
            },
            RecoveryTrackEnum.NEGOTIATION.value: {
                "last_activity": (now.replace(day=now.day-5)).isoformat()  # 5 days ago
            }
        }

        primary = multi_track_manager.get_primary_track(tracks)

        assert primary == RecoveryTrackEnum.SELF_WORK.value

    @pytest.mark.asyncio
    async def test_track_switching_suggestion(self, multi_track_manager):
        """Test track switching suggestions after inactivity."""

        from datetime import timedelta

        # Create tracks where CHILD_CONNECTION hasn't been active for 35 days
        old_date = datetime.utcnow() - timedelta(days=35)

        tracks = {
            RecoveryTrackEnum.CHILD_CONNECTION.value: {
                "last_activity": old_date.isoformat(),
                "completion_percentage": 50
            },
            RecoveryTrackEnum.SELF_WORK.value: {
                "last_activity": datetime.utcnow().isoformat(),
                "completion_percentage": 10  # Lower progress
            }
        }

        suggested = multi_track_manager.should_suggest_track_switch(
            current_track=RecoveryTrackEnum.CHILD_CONNECTION.value,
            tracks=tracks
        )

        # Should suggest switching to SELF_WORK (lowest progress)
        assert suggested == RecoveryTrackEnum.SELF_WORK.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
