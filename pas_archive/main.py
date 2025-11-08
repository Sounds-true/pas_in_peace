#!/usr/bin/env python3
"""Main entry point for PAS Bot."""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.bot import bot
from src.core.config import settings
from src.core.logger import get_logger, setup_logging


# Load environment variables
load_dotenv()

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)


async def main():
    """Run the bot."""
    try:
        logger.info(
            "bot_starting",
            environment=settings.environment,
            debug=settings.debug
        )

        if settings.environment == "production" and settings.telegram_webhook_url:
            # Run in webhook mode for production
            await bot.run_webhook(
                webhook_url=settings.telegram_webhook_url,
                port=8000
            )
        else:
            # Run in polling mode for development
            await bot.run_polling()

    except KeyboardInterrupt:
        logger.info("bot_stopped", reason="keyboard_interrupt")
    except Exception as e:
        logger.error("bot_crashed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())