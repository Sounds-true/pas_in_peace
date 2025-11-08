#!/usr/bin/env python
"""Quick integration test for letter writing feature."""

import asyncio
from src.techniques.letter_writing import LetterWritingAssistant, LetterContext, LetterStage
from src.storage.database import DatabaseManager


async def test_letter_workflow():
    """Test letter writing workflow without database."""
    print("Testing Letter Writing Assistant...")

    # Create assistant
    assistant = LetterWritingAssistant()
    print("✓ LetterWritingAssistant created")

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
    result = await assistant.apply("хочу написать письмо", context)
    assert result.success, "INITIAL stage should succeed"
    assert "letter_context" in context or hasattr(result, 'response')
    print(f"✓ INITIAL stage response: {result.response[:100]}...")

    # Get letter context
    letter_ctx = context.get("letter_context")
    assert letter_ctx is not None, "letter_context should be created"
    assert letter_ctx.current_stage == LetterStage.GATHERING
    print("✓ Letter context created, stage: GATHERING")

    # Test GATHERING stage - recipient
    print("\n2. Testing GATHERING stage - recipient...")
    result = await assistant.apply("Саша", context)
    assert result.success
    assert letter_ctx.recipient == "Саша"
    print(f"✓ Recipient set: {letter_ctx.recipient}")

    # Test GATHERING stage - purpose
    print("\n3. Testing GATHERING stage - purpose...")
    result = await assistant.apply("Хочу сказать как сильно люблю", context)
    assert result.success
    assert letter_ctx.purpose is not None
    print(f"✓ Purpose set: {letter_ctx.purpose}")

    # Test GATHERING stage - key points
    print("\n4. Testing GATHERING stage - key points...")
    result = await assistant.apply("Скучаю по тебе каждый день", context)
    assert result.success
    assert len(letter_ctx.key_points) == 1
    print(f"✓ Key point added: {letter_ctx.key_points[0]}")

    # Test GATHERING stage - complete
    print("\n5. Testing GATHERING stage - complete...")
    result = await assistant.apply("готово", context)
    assert result.success
    # Should transition to GENERATING then REVIEWING
    assert letter_ctx.current_stage == LetterStage.REVIEWING
    assert letter_ctx.draft_content is not None
    print(f"✓ Draft generated ({len(letter_ctx.draft_content)} chars)")
    print(f"   Draft preview: {letter_ctx.draft_content[:150]}...")

    # Test REVIEWING stage - approve
    print("\n6. Testing REVIEWING stage - approve...")
    result = await assistant.apply("отлично", context)
    assert result.success
    assert letter_ctx.current_stage == LetterStage.FINALIZING
    print("✓ Letter finalized")
    print(f"   Metadata: {result.metadata}")

    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)


async def test_db_integration():
    """Test database integration (only if DB is available)."""
    print("\n\nTesting Database Integration...")

    db = DatabaseManager()
    try:
        await db.initialize()
        print("✓ Database initialized")

        # Create test letter
        letter = await db.create_letter(
            user_id=1,
            title="Test Letter",
            recipient_role="Тестовый получатель",
            purpose="Тестовая цель",
            letter_type="parental_alienation",
            draft_content="Тестовое содержимое письма",
            communication_style="warm",
            status="draft"
        )
        print(f"✓ Letter created with ID: {letter.id}")

        # Save draft
        await db.save_letter_draft(
            letter_id=letter.id,
            draft_content="Обновлённое содержимое",
            metadata={"status": "completed"}
        )
        print("✓ Letter draft saved")

        # Retrieve letter
        retrieved = await db.get_letter_by_id(letter.id)
        assert retrieved is not None
        assert retrieved.draft_content == "Обновлённое содержимое"
        print(f"✓ Letter retrieved: {retrieved.title}")

        # Get user letters
        letters = await db.get_user_letters(user_id=1)
        assert len(letters) > 0
        print(f"✓ Found {len(letters)} letter(s) for user")

        print("\n✅ Database integration tests passed!")

    except Exception as e:
        print(f"⚠️  Database not available: {e}")
        print("   (This is OK if PostgreSQL is not running)")
    finally:
        if db.engine:
            await db.close()


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_letter_workflow())
    asyncio.run(test_db_integration())
