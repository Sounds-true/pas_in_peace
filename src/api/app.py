"""FastAPI application for PAS recovery tracking API.

Provides REST API endpoints for:
- Multi-track recovery progress
- Quest creation and management
- User psychological profiles
- Analytics and reporting
"""

from typing import Optional
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.logger import get_logger
from src.storage.database import DatabaseManager
from src.orchestration.multi_track import MultiTrackManager
from src.api.routes import tracks_router


logger = get_logger(__name__)


# Global instances (initialized on startup)
db_manager: Optional[DatabaseManager] = None
multi_track_manager: Optional[MultiTrackManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup/shutdown)."""
    global db_manager, multi_track_manager

    # Startup
    logger.info("api_startup_initiated")

    try:
        # Initialize database
        db_manager = DatabaseManager()
        await db_manager.initialize()
        logger.info("api_database_initialized")

        # Initialize multi-track manager
        multi_track_manager = MultiTrackManager(db_manager=db_manager)
        logger.info("api_multi_track_manager_initialized")

        logger.info("api_startup_complete")

        yield  # Application runs here

    finally:
        # Shutdown
        logger.info("api_shutdown_initiated")

        if db_manager:
            await db_manager.close()
            logger.info("api_database_closed")

        logger.info("api_shutdown_complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="PAS Recovery Tracking API",
        description="API for multi-track recovery progress tracking for alienated parents",
        version="0.3.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )

    # CORS middleware (configure for production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins if hasattr(settings, 'allowed_origins') else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(tracks_router, prefix="/api/tracks", tags=["tracks"])

    # Health check endpoint
    @app.get("/health", status_code=status.HTTP_200_OK)
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "0.3.0",
            "database": "connected" if db_manager and db_manager.initialized else "disconnected"
        }

    # Root endpoint
    @app.get("/", status_code=status.HTTP_200_OK)
    async def root():
        """Root endpoint."""
        return {
            "service": "PAS Recovery Tracking API",
            "version": "0.3.0",
            "docs": "/api/docs"
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error("api_unhandled_exception",
                    path=request.url.path,
                    method=request.method,
                    error=str(exc),
                    exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(exc) if settings.debug else "An unexpected error occurred"
            }
        )

    logger.info("fastapi_app_created")

    return app


# Dependency for route handlers to access global instances
def get_db_manager() -> DatabaseManager:
    """Get database manager instance."""
    if not db_manager:
        raise RuntimeError("Database manager not initialized")
    return db_manager


def get_multi_track_manager() -> MultiTrackManager:
    """Get multi-track manager instance."""
    if not multi_track_manager:
        raise RuntimeError("Multi-track manager not initialized")
    return multi_track_manager
