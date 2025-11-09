#!/usr/bin/env python3
"""FastAPI server entry point for PAS Recovery Tracking API.

Run with:
    python api_server.py

Or with uvicorn directly:
    uvicorn src.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

import uvicorn
from src.api.app import create_app
from src.core.config import settings
from src.core.logger import setup_logging, get_logger


# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)


def main():
    """Run the FastAPI server."""
    logger.info("api_server_starting",
               host="0.0.0.0",
               port=8000,
               environment=settings.environment,
               debug=settings.debug)

    # Create app
    app = create_app()

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info" if not settings.debug else "debug",
        reload=settings.debug,  # Auto-reload in development
        workers=1 if settings.debug else 4  # Multiple workers in production
    )


if __name__ == "__main__":
    main()
