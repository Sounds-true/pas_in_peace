"""Mock database manager using JSON for testing without PostgreSQL.

Provides same interface as DatabaseManager but stores data in JSON files.
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict

from src.core.logger import get_logger
from src.storage.models import (
    QuestStatusEnum, ModerationStatusEnum, ProjectTypeEnum,
    RecoveryTrackEnum, TrackPhaseEnum
)

logger = get_logger(__name__)


class MockDatabaseManager:
    """Mock database manager for testing without PostgreSQL."""

    def __init__(self, data_dir: str = "/tmp/pas_in_peace_test"):
        """Initialize mock database.

        Args:
            data_dir: Directory to store JSON files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # JSON file paths
        self.users_file = self.data_dir / "users.json"
        self.quests_file = self.data_dir / "quests.json"
        self.quest_analytics_file = self.data_dir / "quest_analytics.json"
        self.privacy_settings_file = self.data_dir / "privacy_settings.json"
        self.creative_projects_file = self.data_dir / "creative_projects.json"
        self.track_milestones_file = self.data_dir / "track_milestones.json"
        self.letters_file = self.data_dir / "letters.json"
        self.goals_file = self.data_dir / "goals.json"

        # Initialize empty data structures
        self._init_data_files()

        logger.info("mock_database_initialized", data_dir=str(data_dir))

    def _init_data_files(self):
        """Initialize JSON data files if they don't exist."""
        for file in [
            self.users_file, self.quests_file, self.quest_analytics_file,
            self.privacy_settings_file, self.creative_projects_file,
            self.track_milestones_file, self.letters_file, self.goals_file
        ]:
            if not file.exists():
                self._save_json(file, {})

    def _load_json(self, file: Path) -> Dict:
        """Load JSON data from file."""
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, file: Path, data: Dict):
        """Save data to JSON file."""
        with open(file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    async def initialize(self):
        """Initialize mock database (no-op for JSON)."""
        logger.info("mock_database_ready")

    # User operations
    async def get_or_create_user(self, telegram_id: str) -> Any:
        """Get existing user or create new one."""
        users = self._load_json(self.users_file)

        if telegram_id in users:
            user_data = users[telegram_id]
            user_data['last_activity'] = datetime.utcnow().isoformat()
            self._save_json(self.users_file, users)
            logger.info("user_retrieved", telegram_id=telegram_id)
        else:
            user_data = {
                'id': len(users) + 1,
                'telegram_id': telegram_id,
                'current_state': 'start',
                'emotional_score': 0.5,
                'crisis_level': 0.0,
                'therapy_phase': 'understanding',
                'total_messages': 0,
                'recovery_tracks': {},
                'primary_track': 'self_work',
                'created_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat()
            }
            users[telegram_id] = user_data
            self._save_json(self.users_file, users)
            logger.info("user_created", telegram_id=telegram_id, user_id=user_data['id'])

        # Return mock user object
        class MockUser:
            def __init__(self, data):
                self.__dict__.update(data)

        return MockUser(user_data)

    async def update_user_state(
        self,
        telegram_id: str,
        state: Optional[str] = None,
        emotional_score: Optional[float] = None,
        crisis_level: Optional[float] = None,
        therapy_phase: Optional[str] = None,
        total_messages: Optional[int] = None,
    ):
        """Update user state."""
        users = self._load_json(self.users_file)

        if telegram_id in users:
            if state:
                users[telegram_id]['current_state'] = state
            if emotional_score is not None:
                users[telegram_id]['emotional_score'] = emotional_score
            if crisis_level is not None:
                users[telegram_id]['crisis_level'] = crisis_level
            if therapy_phase:
                users[telegram_id]['therapy_phase'] = therapy_phase
            if total_messages is not None:
                users[telegram_id]['total_messages'] = total_messages

            users[telegram_id]['last_activity'] = datetime.utcnow().isoformat()
            self._save_json(self.users_file, users)

    # Quest operations
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
    ) -> Any:
        """Create new quest."""
        quests = self._load_json(self.quests_file)

        quest_data = {
            'id': len(quests) + 1,
            'user_id': user_id,
            'quest_id': quest_id,
            'title': title,
            'description': description,
            'child_name': child_name,
            'child_age': child_age,
            'child_interests': child_interests or [],
            'quest_yaml': quest_yaml,
            'total_nodes': total_nodes,
            'difficulty_level': difficulty_level,
            'family_photos': family_photos or [],
            'family_memories': family_memories or [],
            'family_jokes': family_jokes or [],
            'familiar_locations': familiar_locations or [],
            'reveal_enabled': reveal_enabled,
            'reveal_threshold_percentage': reveal_threshold_percentage,
            'reveal_message': reveal_message,
            'status': QuestStatusEnum.DRAFT.value,
            'moderation_status': ModerationStatusEnum.PENDING.value,
            'created_at': datetime.utcnow().isoformat()
        }

        quests[str(quest_data['id'])] = quest_data
        self._save_json(self.quests_file, quests)

        # Create associated analytics and privacy settings
        await self._create_quest_analytics(quest_data['id'], total_nodes)
        await self._create_privacy_settings(quest_data['id'])

        logger.info("quest_created", quest_id=quest_data['id'], title=title)

        class MockQuest:
            def __init__(self, data):
                self.__dict__.update(data)

        return MockQuest(quest_data)

    async def _create_quest_analytics(self, quest_id: int, total_nodes: int):
        """Create quest analytics entry."""
        analytics = self._load_json(self.quest_analytics_file)
        analytics[str(quest_id)] = {
            'id': len(analytics) + 1,
            'quest_id': quest_id,
            'total_nodes': total_nodes,
            'nodes_completed': 0,
            'completion_percentage': 0.0,
            'play_count': 0,
            'created_at': datetime.utcnow().isoformat()
        }
        self._save_json(self.quest_analytics_file, analytics)

    async def _create_privacy_settings(self, quest_id: int):
        """Create privacy settings entry."""
        settings = self._load_json(self.privacy_settings_file)
        settings[str(quest_id)] = {
            'id': len(settings) + 1,
            'quest_id': quest_id,
            'consent_given_by_child': False,
            'share_completion_progress': False,
            'share_educational_progress': False,
            'created_at': datetime.utcnow().isoformat()
        }
        self._save_json(self.privacy_settings_file, settings)

    async def get_quest(self, quest_id: int) -> Optional[Any]:
        """Get quest by ID."""
        quests = self._load_json(self.quests_file)
        quest_data = quests.get(str(quest_id))

        if quest_data:
            class MockQuest:
                def __init__(self, data):
                    self.__dict__.update(data)
            return MockQuest(quest_data)
        return None

    async def get_user_quests(
        self,
        user_id: int,
        status: Optional[QuestStatusEnum] = None
    ) -> List[Any]:
        """Get all quests for user."""
        quests = self._load_json(self.quests_file)
        user_quests = []

        for quest_data in quests.values():
            if quest_data['user_id'] == user_id:
                if status is None or quest_data['status'] == status.value:
                    class MockQuest:
                        def __init__(self, data):
                            self.__dict__.update(data)
                    user_quests.append(MockQuest(quest_data))

        return user_quests

    # Creative Project operations
    async def create_creative_project(
        self,
        user_id: int,
        project_type: ProjectTypeEnum,
        quest_id: Optional[int] = None,
        letter_id: Optional[int] = None,
        goal_id: Optional[int] = None,
        affects_tracks: Optional[List[str]] = None,
    ) -> Any:
        """Create creative project."""
        projects = self._load_json(self.creative_projects_file)

        project_data = {
            'id': len(projects) + 1,
            'user_id': user_id,
            'project_type': project_type.value,
            'quest_id': quest_id,
            'letter_id': letter_id,
            'goal_id': goal_id,
            'affects_tracks': affects_tracks or [],
            'status': 'active',
            'progress_percentage': 0.0,
            'created_at': datetime.utcnow().isoformat()
        }

        projects[str(project_data['id'])] = project_data
        self._save_json(self.creative_projects_file, projects)

        logger.info("creative_project_created", project_id=project_data['id'])

        class MockProject:
            def __init__(self, data):
                self.__dict__.update(data)

        return MockProject(project_data)

    # Track Milestone operations
    async def create_track_milestone(
        self,
        user_id: int,
        track: str,
        milestone_type: str,
        milestone_name: str,
    ) -> Any:
        """Create track milestone."""
        milestones = self._load_json(self.track_milestones_file)

        milestone_data = {
            'id': len(milestones) + 1,
            'user_id': user_id,
            'track': track,
            'milestone_type': milestone_type,
            'milestone_name': milestone_name,
            'achieved_at': datetime.utcnow().isoformat()
        }

        milestones[str(milestone_data['id'])] = milestone_data
        self._save_json(self.track_milestones_file, milestones)

        logger.info("milestone_created", milestone_id=milestone_data['id'], name=milestone_name)

        class MockMilestone:
            def __init__(self, data):
                self.__dict__.update(data)

        return MockMilestone(milestone_data)

    # Quest Analytics operations
    async def get_quest_analytics(
        self,
        quest_id: int,
        enforce_privacy: bool = True
    ) -> Optional[Any]:
        """Get quest analytics with privacy check."""
        if enforce_privacy:
            # Check privacy settings
            settings = self._load_json(self.privacy_settings_file)
            privacy = settings.get(str(quest_id))

            if not privacy or not privacy.get('consent_given_by_child', False):
                logger.warning(
                    "quest_analytics_privacy_blocked",
                    quest_id=quest_id,
                    reason="child_consent_not_given"
                )
                return None

        analytics = self._load_json(self.quest_analytics_file)
        analytics_data = analytics.get(str(quest_id))

        if analytics_data:
            class MockAnalytics:
                def __init__(self, data):
                    self.__dict__.update(data)
            return MockAnalytics(analytics_data)
        return None

    async def get_privacy_settings(self, quest_id: int) -> Optional[Any]:
        """Get privacy settings for quest."""
        settings = self._load_json(self.privacy_settings_file)
        settings_data = settings.get(str(quest_id))

        if settings_data:
            class MockSettings:
                def __init__(self, data):
                    self.__dict__.update(data)
            return MockSettings(settings_data)
        return None

    # Letter operations (simplified)
    async def create_letter(self, user_id: int, **kwargs) -> Any:
        """Create letter."""
        letters = self._load_json(self.letters_file)
        letter_data = {
            'id': len(letters) + 1,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        letters[str(letter_data['id'])] = letter_data
        self._save_json(self.letters_file, letters)

        class MockLetter:
            def __init__(self, data):
                self.__dict__.update(data)
        return MockLetter(letter_data)

    # Goal operations (simplified)
    async def create_goal(self, user_id: int, title: str, **kwargs) -> Any:
        """Create goal."""
        goals = self._load_json(self.goals_file)
        goal_data = {
            'id': len(goals) + 1,
            'user_id': user_id,
            'title': title,
            'created_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        goals[str(goal_data['id'])] = goal_data
        self._save_json(self.goals_file, goals)

        class MockGoal:
            def __init__(self, data):
                self.__dict__.update(data)
        return MockGoal(goal_data)

    def clear_all_data(self):
        """Clear all test data (useful for test cleanup)."""
        for file in [
            self.users_file, self.quests_file, self.quest_analytics_file,
            self.privacy_settings_file, self.creative_projects_file,
            self.track_milestones_file, self.letters_file, self.goals_file
        ]:
            self._save_json(file, {})
        logger.info("mock_database_cleared")
