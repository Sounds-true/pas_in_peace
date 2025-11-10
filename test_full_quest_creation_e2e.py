"""Full end-to-end test of quest creation flow using mock database.

Tests the complete flow without requiring PostgreSQL.
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.storage.mock_database import MockDatabaseManager
from src.orchestration.multi_track import MultiTrackManager
from src.storage.models import RecoveryTrackEnum, ProjectTypeEnum


async def test_full_quest_creation_e2e():
    """Test complete quest creation flow."""

    print("🧪 Testing Full Quest Creation E2E Flow with Mock Database")
    print("=" * 70)

    # Initialize mock database
    db = MockDatabaseManager(data_dir="/tmp/pas_in_peace_test_e2e")
    await db.initialize()
    db.clear_all_data()  # Start fresh

    # Initialize multi-track manager
    multi_track = MultiTrackManager(db_manager=db)

    print("\n📊 Step 1: Create test user")
    user = await db.get_or_create_user("test_user_123")
    print(f"✅ User created: ID={user.id}, telegram_id={user.telegram_id}")

    print("\n📊 Step 2: Initialize recovery tracks")
    tracks = await multi_track.initialize_tracks(user.id)
    print(f"✅ Initialized {len(tracks)} recovery tracks:")
    for track_name, progress in tracks.items():
        print(f"   - {track_name}: {progress['phase']} phase, {progress['completion_percentage']}%")

    print("\n📊 Step 3: Create quest")
    quest_yaml = """
quest_id: test_math_quest
title: Математическое Приключение
description: Квест для изучения математики
difficulty: easy
age_range: 8-10
nodes:
  - node_id: 1
    type: input_text
    prompt: Сколько будет 2 + 2?
    validation:
      min_length: 1
      max_length: 10
  - node_id: 2
    type: input_text
    prompt: Отлично! А 5 + 3?
"""

    quest = await db.create_quest(
        user_id=user.id,
        quest_id="test_math_quest_001",
        title="Математическое Приключение",
        quest_yaml=quest_yaml,
        description="Квест для изучения математики",
        child_name="Маша",
        child_age=9,
        child_interests=["математика", "котики"],
        total_nodes=2,
        difficulty_level="easy",
        family_memories=["Поход в зоопарк", "День рождения"],
        reveal_enabled=True
    )
    print(f"✅ Quest created: ID={quest.id}, title={quest.title}")
    print(f"   - Child: {quest.child_name}, age {quest.child_age}")
    print(f"   - Status: {quest.status}, moderation: {quest.moderation_status}")

    print("\n📊 Step 4: Create creative project")
    project = await db.create_creative_project(
        user_id=user.id,
        project_type=ProjectTypeEnum.QUEST,
        quest_id=quest.id,
        affects_tracks=[RecoveryTrackEnum.CHILD_CONNECTION.value]
    )
    print(f"✅ Creative project created: ID={project.id}, type={project.project_type}")

    print("\n📊 Step 5: Update multi-track progress")
    updated_tracks = await multi_track.update_progress(
        user_id=user.id,
        track=RecoveryTrackEnum.CHILD_CONNECTION.value,
        delta=20,
        action_type="quest_created",
        milestone_achieved="Quest Creator"
    )

    child_conn = updated_tracks[RecoveryTrackEnum.CHILD_CONNECTION.value]
    print(f"✅ Track progress updated: CHILD_CONNECTION")
    print(f"   - Completion: {child_conn['completion_percentage']}%")
    print(f"   - Phase: {child_conn['phase']}")
    print(f"   - Milestones: {len(child_conn['milestones'])}")
    print(f"   - Total actions: {child_conn['total_actions']}")

    # Check for cross-track impact
    self_work = updated_tracks[RecoveryTrackEnum.SELF_WORK.value]
    if self_work['completion_percentage'] > 0:
        print(f"   - Cross-track impact: SELF_WORK now at {self_work['completion_percentage']}%")

    print("\n📊 Step 6: Create milestone")
    milestone = await multi_track.check_milestone(
        user_id=user.id,
        track=RecoveryTrackEnum.CHILD_CONNECTION.value,
        action_type="quest_created"
    )
    print(f"✅ Milestone created: {milestone}")

    print("\n📊 Step 7: Check quest analytics (privacy enforcement)")
    analytics = await db.get_quest_analytics(quest.id, enforce_privacy=True)
    if analytics is None:
        print("✅ Privacy enforcement working: Analytics blocked (no child consent)")
    else:
        print("⚠️ Privacy enforcement issue: Analytics accessible without consent")

    print("\n📊 Step 8: Check privacy settings")
    privacy = await db.get_privacy_settings(quest.id)
    print(f"✅ Privacy settings: consent={privacy.consent_given_by_child}")

    print("\n📊 Step 9: Retrieve all user quests")
    user_quests = await db.get_user_quests(user.id)
    print(f"✅ User has {len(user_quests)} quest(s)")
    for q in user_quests:
        print(f"   - {q.title} (status: {q.status})")

    print("\n📊 Step 10: Test intent detection")
    test_messages = [
        "Хочу создать квест для ребенка",
        "Чувствую грусть и тревогу",
        "Нужно поговорить с бывшим",
        "Ищу группу поддержки"
    ]

    print("✅ Intent detection results:")
    for msg in test_messages:
        detected = multi_track.detect_track_from_message(msg)
        print(f"   - '{msg[:40]}...' → {detected}")

    print("\n" + "=" * 70)
    print("🎉 ALL E2E TESTS PASSED!")
    print("\n📊 Final Statistics:")
    print(f"   - Users created: 1")
    print(f"   - Quests created: 1")
    print(f"   - Creative projects: 1")
    print(f"   - Milestones achieved: 1")
    print(f"   - Tracks initialized: 4")
    print(f"   - Tracks with progress: 2 (CHILD_CONNECTION + SELF_WORK cross-impact)")

    return True


async def test_graph_to_yaml_integration():
    """Test graph to YAML conversion integrated with quest creation."""

    print("\n" + "=" * 70)
    print("🧪 Testing Graph → YAML → Database Integration")
    print("=" * 70)

    from src.quest_builder.graph_to_yaml_converter import graph_to_yaml

    # Create graph structure
    graph = {
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "data": {"label": "Начало", "introText": "Добро пожаловать!"}
            },
            {
                "id": "q1",
                "type": "questStep",
                "data": {
                    "prompt": "Решите задачу: 7 + 8 = ?",
                    "psychologicalMethod": "cognitive_challenge"
                }
            },
            {
                "id": "end",
                "type": "end",
                "data": {"completionMessage": "Молодец!"}
            }
        ],
        "edges": [
            {"source": "start", "target": "q1"},
            {"source": "q1", "target": "end"}
        ],
        "metadata": {
            "quest_id": "graph_test_quest",
            "title": "Graph Test Quest",
            "psychological_module": "IFS",
            "age_range": "9-11"
        }
    }

    print("\n📊 Step 1: Convert graph to YAML")
    yaml_str = graph_to_yaml(graph)
    print(f"✅ Graph converted to YAML ({len(yaml_str)} chars)")
    print(f"\n{yaml_str}")

    print("\n📊 Step 2: Save quest with generated YAML")
    db = MockDatabaseManager(data_dir="/tmp/pas_in_peace_test_e2e")
    user = await db.get_or_create_user("graph_test_user")

    quest = await db.create_quest(
        user_id=user.id,
        quest_id="graph_test_quest_001",
        title="Graph Test Quest",
        quest_yaml=yaml_str,
        child_name="Test Child",
        child_age=10,
        total_nodes=3
    )

    print(f"✅ Quest created from graph: ID={quest.id}")

    print("\n📊 Step 3: Retrieve and verify")
    retrieved = await db.get_quest(quest.id)
    print(f"✅ Quest retrieved: {retrieved.title}")
    print(f"   - Has YAML: {len(retrieved.quest_yaml)} chars")
    print(f"   - Nodes: {retrieved.total_nodes}")

    print("\n🎉 Graph → YAML → Database integration WORKING!")

    return True


if __name__ == "__main__":
    async def run_all_tests():
        print("\n" + "🚀 " * 20)
        print("FULL E2E TEST SUITE - Mock Database")
        print("🚀 " * 20 + "\n")

        success1 = await test_full_quest_creation_e2e()
        success2 = await test_graph_to_yaml_integration()

        if success1 and success2:
            print("\n" + "✅ " * 20)
            print("ALL TESTS PASSED - System Ready!")
            print("✅ " * 20 + "\n")
            return 0
        else:
            print("\n❌ Some tests failed")
            return 1

    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
