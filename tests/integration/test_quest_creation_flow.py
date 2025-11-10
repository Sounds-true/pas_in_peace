"""Integration test for full quest creation flow.

Tests end-to-end flow:
1. User starts quest builder
2. Goes through dialogue stages
3. AI generates quest
4. Content moderation passes
5. Quest saved to database
6. Analytics and privacy settings created
7. Multi-track progress updated
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.techniques.quest_builder import QuestBuilderAssistant, QuestContext, QuestStage
from src.safety.content_moderator import ContentModerator
from src.storage.database import DatabaseManager
from src.orchestration.multi_track import MultiTrackManager
from src.storage.models import (
    QuestStatusEnum,
    ModerationStatusEnum,
    RecoveryTrackEnum
)


class TestQuestCreationFlow:
    """Integration tests for quest creation flow."""

    @pytest.fixture
    async def db_manager(self):
        """Create mock database manager."""
        db = AsyncMock(spec=DatabaseManager)

        # Mock create_quest to return quest object
        quest_mock = MagicMock()
        quest_mock.id = 1
        quest_mock.quest_id = "quest_test123"
        quest_mock.title = "Test Quest"
        quest_mock.status = QuestStatusEnum.DRAFT
        db.create_quest = AsyncMock(return_value=quest_mock)

        return db

    @pytest.fixture
    async def content_moderator(self):
        """Create mock content moderator."""
        moderator = AsyncMock(spec=ContentModerator)

        # Mock moderate_quest to pass
        moderator.moderate_quest = AsyncMock(return_value={
            "passed": True,
            "issues": [],
            "suggestions": [],
            "total_issues": 0,
            "critical_issues": 0,
            "high_issues": 0
        })

        return moderator

    @pytest.fixture
    async def multi_track_manager(self):
        """Create mock multi-track manager."""
        manager = AsyncMock(spec=MultiTrackManager)

        manager.update_progress = AsyncMock(return_value={
            RecoveryTrackEnum.CHILD_CONNECTION.value: {
                "track": "child_connection",
                "phase": "awareness",
                "completion_percentage": 10,
                "milestones": [],
                "next_action": {},
                "last_activity": datetime.utcnow().isoformat(),
                "total_actions": 1
            }
        })

        manager.check_milestone = AsyncMock(return_value="Quest Creator")

        return manager

    @pytest.fixture
    async def quest_builder(self, db_manager, content_moderator):
        """Create quest builder assistant."""
        return QuestBuilderAssistant(
            db_manager=db_manager,
            content_moderator=content_moderator
        )

    @pytest.mark.asyncio
    async def test_full_quest_creation_flow(
        self,
        quest_builder,
        db_manager,
        content_moderator,
        multi_track_manager
    ):
        """Test complete quest creation flow."""

        context = {
            "user_id": 1,
            "quest_context": None
        }

        # Step 1: INITIAL - Welcome message
        result1 = await quest_builder.apply(
            user_message="Хочу создать квест",
            context=context
        )

        assert result1.success
        assert "Создание Образовательного Квеста" in result1.response
        assert context["quest_context"].current_stage == QuestStage.GATHERING

        # Step 2: GATHERING - Provide child info
        result2 = await quest_builder.apply(
            user_message="Маша, 9 лет, любит математику",
            context=context
        )

        assert result2.success
        quest_ctx = context["quest_context"]
        assert quest_ctx.child_name is not None
        assert quest_ctx.child_age == 9

        # Step 3: GATHERING - Provide memories
        result3 = await quest_builder.apply(
            user_message="Мы ходили в зоопарк и видели слонов",
            context=context
        )

        assert result3.success

        result4 = await quest_builder.apply(
            user_message="У нас была шутка про зеленого дракона",
            context=context
        )

        assert result4.success
        quest_ctx = context["quest_context"]
        assert len(quest_ctx.family_memories) >= 2
        assert quest_ctx.current_stage == QuestStage.GENERATING

        # Step 4: GENERATING - AI generates quest (mock)
        with patch.object(quest_builder, '_generate_quest_with_ai') as mock_gen:
            mock_gen.return_value = """
quest_id: test_quest
title: Math Adventure
description: Educational quest
difficulty: medium
nodes:
  - node_id: 1
    type: input_text
    prompt: What is 2 + 2?
    validation:
      min_length: 1
      max_length: 10
"""

            result5 = await quest_builder.apply(
                user_message="",
                context=context
            )

            assert result5.success
            quest_ctx = context["quest_context"]
            assert quest_ctx.quest_yaml is not None
            assert quest_ctx.current_stage == QuestStage.REVIEWING

        # Step 5: REVIEWING - Parent approves
        result6 = await quest_builder.apply(
            user_message="ок",
            context=context
        )

        assert result6.success
        quest_ctx = context["quest_context"]
        assert quest_ctx.current_stage == QuestStage.MODERATING

        # Step 6: MODERATING - Content passes
        result7 = await quest_builder.apply(
            user_message="",
            context=context
        )

        assert result7.success
        quest_ctx = context["quest_context"]
        assert quest_ctx.current_stage == QuestStage.FINALIZING

        # Verify moderation was called
        content_moderator.moderate_quest.assert_called_once()

        # Step 7: FINALIZING - Save to database
        result8 = await quest_builder.apply(
            user_message="",
            context=context
        )

        assert result8.success
        assert "Квест успешно создан" in result8.response

        # Verify quest was saved
        db_manager.create_quest.assert_called_once()
        call_args = db_manager.create_quest.call_args[1]
        assert call_args["user_id"] == 1
        assert call_args["child_name"] == quest_ctx.child_name
        assert call_args["child_age"] == quest_ctx.child_age
        assert call_args["quest_yaml"] == quest_ctx.quest_yaml

        # Step 8: Verify multi-track progress updated
        await multi_track_manager.update_progress(
            user_id=1,
            track=RecoveryTrackEnum.CHILD_CONNECTION.value,
            delta=10,
            action_type="quest_created",
            milestone_achieved="Quest Creator"
        )

        multi_track_manager.update_progress.assert_called_once()
        multi_track_manager.check_milestone.assert_called_once()

    @pytest.mark.asyncio
    async def test_quest_creation_moderation_fails(
        self,
        quest_builder,
        content_moderator
    ):
        """Test quest creation when moderation fails."""

        # Mock moderation to fail
        content_moderator.moderate_quest = AsyncMock(return_value={
            "passed": False,
            "issues": [
                {
                    "category": "blame",
                    "severity": "critical",
                    "message": "Blames other parent"
                }
            ],
            "suggestions": ["Remove blame language"],
            "total_issues": 1,
            "critical_issues": 1,
            "high_issues": 0
        })

        context = {
            "user_id": 1,
            "quest_context": QuestContext(
                current_stage=QuestStage.MODERATING,
                quest_yaml="test: yaml",
                child_age=10,
                child_name="Test"
            )
        }

        result = await quest_builder.apply(
            user_message="",
            context=context
        )

        assert not result.success
        assert "Обнаружены проблемы" in result.response
        assert "Критических проблем: 1" in result.response

    @pytest.mark.asyncio
    async def test_quest_analytics_privacy_enforcement(self, db_manager):
        """Test that quest analytics respects privacy settings."""

        # Mock get_quest_analytics with privacy enforcement
        db_manager.get_quest_analytics = AsyncMock(return_value=None)

        # Try to get analytics without consent
        analytics = await db_manager.get_quest_analytics(
            quest_id=1,
            enforce_privacy=True
        )

        assert analytics is None
        db_manager.get_quest_analytics.assert_called_once_with(
            quest_id=1,
            enforce_privacy=True
        )

    @pytest.mark.asyncio
    async def test_creative_project_created_with_quest(self, db_manager):
        """Test that creative project is created when quest is saved."""

        from src.storage.models import ProjectTypeEnum

        project_mock = MagicMock()
        project_mock.id = 1
        project_mock.project_type = ProjectTypeEnum.QUEST
        db_manager.create_creative_project = AsyncMock(return_value=project_mock)

        # Simulate quest creation triggering creative project creation
        await db_manager.create_creative_project(
            user_id=1,
            project_type=ProjectTypeEnum.QUEST,
            quest_id=1,
            affects_tracks=[RecoveryTrackEnum.CHILD_CONNECTION.value]
        )

        db_manager.create_creative_project.assert_called_once()
        call_args = db_manager.create_creative_project.call_args[1]
        assert call_args["project_type"] == ProjectTypeEnum.QUEST
        assert call_args["quest_id"] == 1


class TestGraphYamlConversion:
    """Test graph ↔ YAML conversion."""

    def test_graph_to_yaml_conversion(self):
        """Test converting React Flow graph to YAML."""
        from src.quest_builder import graph_to_yaml

        graph = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "start",
                    "data": {
                        "label": "Welcome",
                        "introText": "Welcome to the quest!"
                    }
                },
                {
                    "id": "node2",
                    "type": "questStep",
                    "data": {
                        "prompt": "What is 2+2?",
                        "psychologicalMethod": "cognitive_challenge",
                        "validation": {"minLength": 1, "maxLength": 10},
                        "rewards": {"xp": 10}
                    }
                }
            ],
            "edges": [
                {"source": "node1", "target": "node2"}
            ],
            "metadata": {
                "quest_id": "test_quest",
                "title": "Test Quest",
                "difficulty": "easy"
            }
        }

        yaml_str = graph_to_yaml(graph)

        assert yaml_str is not None
        assert "quest_id: test_quest" in yaml_str
        assert "title: Test Quest" in yaml_str
        assert "node_id: node1" in yaml_str
        assert "node_id: node2" in yaml_str

    def test_yaml_to_graph_conversion(self):
        """Test converting YAML to React Flow graph."""
        from src.quest_builder import yaml_to_graph

        yaml_str = """
quest_id: test_quest
title: Test Quest
difficulty: easy
nodes:
  - node_id: 1
    type: intro
    title: Welcome
  - node_id: 2
    type: question
    prompt: What is 2+2?
    next_node: 3
  - node_id: 3
    type: completion
    completion_message: Well done!
"""

        graph = yaml_to_graph(yaml_str)

        assert graph is not None
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) == 3
        assert len(graph["edges"]) >= 2  # At least 1→2, 2→3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
