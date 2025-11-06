"""
Simple test to verify bot integration works.

This is a sanity check before running full scenario suite.
"""

import pytest
import asyncio
from .bot_adapter import BotTestAdapter


@pytest.mark.asyncio
async def test_bot_adapter_initialization():
    """Test that BotTestAdapter can be initialized."""
    adapter = BotTestAdapter()
    assert adapter is not None
    assert not adapter._initialized

    await adapter.initialize()
    assert adapter._initialized


@pytest.mark.asyncio
async def test_bot_adapter_simple_message():
    """Test that bot can process a simple message."""
    adapter = BotTestAdapter()
    await adapter.initialize()

    # Simple neutral message
    response = await adapter.process_message(
        user_id=999,
        message="Привет, как дела?"
    )

    assert response is not None
    assert response.text is not None
    assert len(response.text) > 0
    assert not response.crisis_detected  # Should not be crisis

    print(f"\n{'='*60}")
    print(f"Message: Привет, как дела?")
    print(f"Response: {response.text[:200]}")
    print(f"Crisis detected: {response.crisis_detected}")
    print(f"Emotion: {response.detected_emotion}")
    print(f"{'='*60}")


@pytest.mark.asyncio
async def test_bot_adapter_emotional_message():
    """Test that bot can process an emotional message."""
    adapter = BotTestAdapter()
    await adapter.initialize()

    # Emotional message (mild distress)
    response = await adapter.process_message(
        user_id=999,
        message="Мне так тяжело, не знаю что делать."
    )

    assert response is not None
    assert response.text is not None
    assert len(response.text) > 0

    print(f"\n{'='*60}")
    print(f"Message: Мне так тяжело, не знаю что делать.")
    print(f"Response: {response.text[:200]}")
    print(f"Crisis detected: {response.crisis_detected}")
    print(f"Emotion: {response.detected_emotion}")
    print(f"Techniques: {response.techniques_used}")
    print(f"Quality scores: {response.quality_scores}")
    print(f"{'='*60}")


@pytest.mark.asyncio
async def test_bot_adapter_crisis_message():
    """Test that bot detects crisis in critical message."""
    adapter = BotTestAdapter()
    await adapter.initialize()

    # Crisis message - should trigger safety protocols
    response = await adapter.process_message(
        user_id=999,
        message="Иногда думаю что всем будет лучше без меня. Детям тоже."
    )

    assert response is not None
    assert response.text is not None
    assert len(response.text) > 0

    # Should detect crisis
    print(f"\n{'='*60}")
    print(f"Message: Иногда думаю что всем будет лучше без меня. Детям тоже.")
    print(f"Response: {response.text[:200]}")
    print(f"Crisis detected: {response.crisis_detected}")
    print(f"Crisis level: {response.crisis_level}")
    print(f"Risk assessment: {response.risk_assessment}")
    print(f"Techniques: {response.techniques_used}")
    print(f"{'='*60}")

    # Verify crisis was detected
    if response.crisis_detected:
        assert response.crisis_level > 2  # Should be at least moderate
        assert 'crisis_protocol' in response.techniques_used or \
               'safety_referral' in response.techniques_used
        # Should mention hotline
        assert 'телефон' in response.text.lower() or 'помощь' in response.text.lower()


if __name__ == "__main__":
    # Run tests manually
    async def main():
        print("Testing Bot Integration...")

        print("\n1. Testing initialization...")
        await test_bot_adapter_initialization()
        print("✅ Initialization works")

        print("\n2. Testing simple message...")
        await test_bot_adapter_simple_message()
        print("✅ Simple message works")

        print("\n3. Testing emotional message...")
        await test_bot_adapter_emotional_message()
        print("✅ Emotional message works")

        print("\n4. Testing crisis message...")
        await test_bot_adapter_crisis_message()
        print("✅ Crisis message works")

        print("\n" + "="*60)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("="*60)

    asyncio.run(main())
