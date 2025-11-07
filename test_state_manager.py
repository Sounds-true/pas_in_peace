#!/usr/bin/env python3
"""Test state manager directly to understand the issue."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.state_manager import StateManager
from src.core.logger import setup_logging

setup_logging("INFO")


async def main():
    """Test state manager."""
    state_manager = StateManager()
    await state_manager.initialize()

    user_id = "test_user_123"

    # Initialize user
    await state_manager.initialize_user(user_id)

    # First message
    print("\n=== First message ===")
    response1 = await state_manager.process_message(user_id, "Мне тяжело")
    print(f"Response 1: {response1[:100]}...")

    # Second message
    print("\n=== Second message ===")
    response2 = await state_manager.process_message(user_id, "что мне делать")
    print(f"Response 2: {response2[:100]}...")

    # Third message
    print("\n=== Third message ===")
    response3 = await state_manager.process_message(user_id, "помогите")
    print(f"Response 3: {response3[:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
