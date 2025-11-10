"""Simple test of mock database without heavy dependencies."""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Import only mock database - no other dependencies
from src.storage.mock_database import MockDatabaseManager
from src.storage.models import RecoveryTrackEnum, ProjectTypeEnum, QuestStatusEnum


async def test_mock_database():
    """Test mock database functionality."""

    print("🧪 Testing Mock Database")
    print("=" * 70)

    # Initialize
    db = MockDatabaseManager(data_dir="/tmp/pas_test_simple")
    await db.initialize()
    db.clear_all_data()

    print("\n✅ Step 1: Create user")
    user = await db.get_or_create_user("user123")
    print(f"   User ID: {user.id}, telegram_id: {user.telegram_id}")
    assert user.id == 1
    assert user.telegram_id == "user123"

    print("\n✅ Step 2: Update user state")
    await db.update_user_state(
        "user123",
        state="active",
        emotional_score=0.7,
        total_messages=5
    )

    user2 = await db.get_or_create_user("user123")
    assert user2.current_state == "active"
    assert user2.emotional_score == 0.7
    print(f"   State updated: {user2.current_state}, score: {user2.emotional_score}")

    print("\n✅ Step 3: Create quest")
    quest = await db.create_quest(
        user_id=user.id,
        quest_id="quest_001",
        title="Test Quest",
        quest_yaml="quest: yaml",
        child_name="Маша",
        child_age=9,
        total_nodes=3
    )
    print(f"   Quest ID: {quest.id}, title: {quest.title}, child: {quest.child_name}")
    assert quest.id == 1
    assert quest.title == "Test Quest"
    assert quest.child_name == "Маша"

    print("\n✅ Step 4: Create creative project")
    project = await db.create_creative_project(
        user_id=user.id,
        project_type=ProjectTypeEnum.QUEST,
        quest_id=quest.id
    )
    print(f"   Project ID: {project.id}, type: {project.project_type}")
    assert project.id == 1

    print("\n✅ Step 5: Create milestone")
    milestone = await db.create_track_milestone(
        user_id=user.id,
        track="child_connection",
        milestone_type="quest_created",
        milestone_name="Quest Creator"
    )
    print(f"   Milestone ID: {milestone.id}, name: {milestone.milestone_name}")
    assert milestone.id == 1

    print("\n✅ Step 6: Test privacy enforcement")
    # Analytics should be blocked without consent
    analytics = await db.get_quest_analytics(quest.id, enforce_privacy=True)
    assert analytics is None, "Analytics should be blocked without consent"
    print("   Privacy enforcement: ✅ Analytics blocked (no consent)")

    # Get privacy settings
    privacy = await db.get_privacy_settings(quest.id)
    assert privacy.consent_given_by_child == False
    print(f"   Privacy settings: consent={privacy.consent_given_by_child}")

    print("\n✅ Step 7: Get user quests")
    quests = await db.get_user_quests(user.id)
    assert len(quests) == 1
    assert quests[0].title == "Test Quest"
    print(f"   Found {len(quests)} quest(s)")

    print("\n✅ Step 8: Create letter and goal")
    letter = await db.create_letter(user.id, title="Letter to child")
    goal = await db.create_goal(user.id, title="Daily exercise")
    print(f"   Letter ID: {letter.id}, Goal ID: {goal.id}")

    print("\n" + "=" * 70)
    print("🎉 ALL MOCK DATABASE TESTS PASSED!")
    print("\n📊 Summary:")
    print(f"   - Users: 1")
    print(f"   - Quests: 1")
    print(f"   - Projects: 1")
    print(f"   - Milestones: 1")
    print(f"   - Letters: 1")
    print(f"   - Goals: 1")
    print(f"   - Privacy enforcement: ✅ Working")

    return True


async def test_graph_to_yaml_with_mock():
    """Test graph to YAML converter with mock database."""

    print("\n" + "=" * 70)
    print("🧪 Testing Graph → YAML → Mock Database")
    print("=" * 70)

    from src.quest_builder.graph_to_yaml_converter import graph_to_yaml

    graph = {
        "nodes": [
            {"id": "1", "type": "start", "data": {"label": "Start", "introText": "Hi!"}},
            {"id": "2", "type": "questStep", "data": {"prompt": "Question?"}},
            {"id": "3", "type": "end", "data": {"completionMessage": "Done!"}}
        ],
        "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
        "metadata": {
            "quest_id": "graph_quest",
            "title": "Graph Quest",
            "psychological_module": "CBT"
        }
    }

    print("\n✅ Step 1: Convert graph to YAML")
    yaml_str = graph_to_yaml(graph)
    print(f"   YAML generated: {len(yaml_str)} chars")
    assert "quest_id: graph_quest" in yaml_str
    assert "title: Graph Quest" in yaml_str

    print("\n✅ Step 2: Save to mock database")
    db = MockDatabaseManager(data_dir="/tmp/pas_test_simple")
    user = await db.get_or_create_user("graph_user")
    quest = await db.create_quest(
        user_id=user.id,
        quest_id="graph_quest_001",
        title="Graph Quest",
        quest_yaml=yaml_str,
        total_nodes=3
    )
    print(f"   Quest created: ID={quest.id}, nodes={quest.total_nodes}")

    print("\n✅ Step 3: Verify stored data")
    retrieved = await db.get_quest(quest.id)
    assert retrieved is not None
    assert "graph_quest" in retrieved.quest_yaml
    print(f"   Retrieved quest: {retrieved.title}")
    print(f"   YAML stored: {len(retrieved.quest_yaml)} chars")

    print("\n🎉 Graph → YAML → Database integration WORKING!")

    return True


if __name__ == "__main__":
    async def run_tests():
        print("\n" + "🚀 " * 20)
        print("MOCK DATABASE TEST SUITE")
        print("🚀 " * 20 + "\n")

        test1 = await test_mock_database()
        test2 = await test_graph_to_yaml_with_mock()

        if test1 and test2:
            print("\n" + "✅ " * 20)
            print("ALL TESTS PASSED!")
            print("Mock Database Ready for Development")
            print("✅ " * 20 + "\n")
            return 0
        return 1

    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
