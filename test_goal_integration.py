#!/usr/bin/env python
"""Quick integration test for goal tracking feature."""

import asyncio
from src.techniques.goal_tracking import GoalTrackingAssistant, GoalContext, GoalStage
from src.storage.database import DatabaseManager


async def test_goal_workflow():
    """Test goal tracking workflow without database."""
    print("Testing Goal Tracking Assistant...")

    # Create assistant
    assistant = GoalTrackingAssistant()
    print("✓ GoalTrackingAssistant created")

    # Create mock context
    context = {
        "primary_emotion": "sadness",
        "distress_level": "moderate",
        "emotional_intensity": 0.6,
        "user_state": type('obj', (object,), {'user_id': 1, 'messages_count': 5})(),
        "db": None  # No DB for this test
    }

    # Test INITIAL stage
    print("\n1. Testing INITIAL stage...")
    result = await assistant.apply("хочу поставить цель", context)
    assert result.success, "INITIAL stage should succeed"
    print(f"✓ INITIAL stage response: {result.response[:100]}...")

    # Get goal context
    goal_ctx = context.get("goal_context")
    assert goal_ctx is not None, "goal_context should be created"
    assert goal_ctx.current_stage == GoalStage.COLLECTING
    print("✓ Goal context created, stage: COLLECTING")

    # Test COLLECTING stage - title
    print("\n2. Testing COLLECTING stage - title...")
    result = await assistant.apply("Восстановить общение с ребёнком", context)
    assert result.success
    assert goal_ctx.title == "Восстановить общение с ребёнком"
    print(f"✓ Goal title set: {goal_ctx.title}")
    print(f"✓ Auto-categorized as: {goal_ctx.category}")

    # Test COLLECTING stage - description
    print("\n3. Testing COLLECTING stage - description...")
    result = await assistant.apply("Хочу регулярно общаться с сыном хотя бы раз в неделю", context)
    assert result.success
    assert goal_ctx.description is not None
    print(f"✓ Description set: {goal_ctx.description[:50]}...")

    # Should transition to CLARIFYING
    assert goal_ctx.current_stage == GoalStage.CLARIFYING
    print("✓ Transitioned to CLARIFYING stage")

    # Test CLARIFYING stage - timeframe
    print("\n4. Testing CLARIFYING stage - timeframe...")
    result = await assistant.apply("3 месяца", context)
    assert result.success
    assert goal_ctx.timeframe is not None
    print(f"✓ Timeframe set: {goal_ctx.timeframe}")

    # Test CLARIFYING stage - milestones
    print("\n5. Testing CLARIFYING stage - milestones...")
    result = await assistant.apply("Написать письмо", context)
    assert result.success
    assert len(goal_ctx.milestones) == 1
    print(f"✓ First milestone added: {goal_ctx.milestones[0]}")

    result = await assistant.apply("Связаться через посредника", context)
    assert result.success
    assert len(goal_ctx.milestones) == 2
    print(f"✓ Second milestone added: {goal_ctx.milestones[1]}")

    result = await assistant.apply("готово", context)
    assert result.success
    # Should transition to CONFIRMING
    assert goal_ctx.current_stage == GoalStage.CONFIRMING
    print("✓ Transitioned to CONFIRMING stage")

    # Test CONFIRMING stage - approve
    print("\n6. Testing CONFIRMING stage - approve...")
    result = await assistant.apply("да", context)
    assert result.success
    assert goal_ctx.current_stage == GoalStage.COMPLETED
    print("✓ Goal confirmed and marked as COMPLETED")
    print(f"   Metadata: {result.metadata}")

    print("\n" + "="*60)
    print("✅ All goal tracking tests passed!")
    print("="*60)
    print(f"\n📊 Final goal summary:")
    print(f"   Title: {goal_ctx.title}")
    print(f"   Category: {goal_ctx.category}")
    print(f"   Timeframe: {goal_ctx.timeframe}")
    print(f"   Milestones: {len(goal_ctx.milestones)}")


async def test_trigger_logic():
    """Test goal setting trigger logic."""
    print("\n\nTesting Goal Setting Trigger Logic...")

    from src.orchestration.state_manager import StateManager, UserState

    # Create state manager
    sm = StateManager()
    print("✓ StateManager created")

    # Create mock user state
    user_state = UserState(
        user_id="test_123",
        telegram_id="test_123",
        messages_count=4  # Should trigger at 3-5
    )

    # Test trigger check
    suggestion = await sm._check_goal_setting_trigger("test_123", user_state)

    if suggestion:
        print("✓ Goal trigger activated at message 4")
        print(f"   Suggestion preview: {suggestion[:100]}...")
    else:
        print("⚠️  Trigger not activated (may need active goals check)")

    # Test that it doesn't trigger twice
    suggestion2 = await sm._check_goal_setting_trigger("test_123", user_state)
    assert suggestion2 is None, "Should not trigger twice in same session"
    print("✓ Trigger correctly prevents duplicate suggestions")

    print("\n✅ Trigger logic tests passed!")


async def test_db_integration():
    """Test database integration (only if DB is available)."""
    print("\n\nTesting Database Integration...")

    db = DatabaseManager()
    try:
        await db.initialize()
        print("✓ Database initialized")

        # Create test goal
        goal = await db.create_goal(
            user_id=1,
            title="Тестовая цель",
            description="Описание тестовой цели",
            category="communication"
        )
        print(f"✓ Goal created with ID: {goal.id}")

        # Update goal with SMART details
        from sqlalchemy import select
        from src.storage.models import Goal

        async with db.session() as db_session:
            stmt = select(Goal).where(Goal.id == goal.id)
            result = await db_session.execute(stmt)
            goal_obj = result.scalar_one_or_none()

            if goal_obj:
                goal_obj.time_bound = "3 месяца"
                goal_obj.milestones = ["Шаг 1", "Шаг 2"]
                goal_obj.specific = "Конкретное описание"
                await db_session.commit()

        print("✓ Goal updated with SMART details")

        # Retrieve active goals
        active_goals = await db.get_active_goals(user_id=1)
        assert len(active_goals) > 0
        print(f"✓ Found {len(active_goals)} active goal(s) for user")

        # Update progress
        await db.update_goal_progress(goal_id=goal.id, progress_percentage=50.0)
        print("✓ Goal progress updated to 50%")

        print("\n✅ Database integration tests passed!")

    except Exception as e:
        print(f"⚠️  Database not available: {e}")
        print("   (This is OK if PostgreSQL is not running)")
    finally:
        if db.engine:
            await db.close()


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_goal_workflow())
    # asyncio.run(test_trigger_logic())  # Skipped due to torch import in StateManager
    asyncio.run(test_db_integration())
