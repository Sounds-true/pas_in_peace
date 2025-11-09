"""API routes for multi-track recovery system.

Endpoints:
- GET /api/tracks/{user_id} - Get all track progress
- GET /api/tracks/{user_id}/{track_name} - Get specific track progress
- POST /api/tracks/{user_id}/{track_name}/progress - Update progress
- GET /api/tracks/{user_id}/milestones - Get user milestones
- GET /api/tracks/{user_id}/suggestions - Get track switch suggestions
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from src.core.logger import get_logger
from src.storage.models import RecoveryTrackEnum, TrackPhaseEnum
from src.api.app import get_db_manager, get_multi_track_manager
from src.storage.database import DatabaseManager
from src.orchestration.multi_track import MultiTrackManager


logger = get_logger(__name__)
router = APIRouter()


# Request/Response models
class TrackProgressUpdate(BaseModel):
    """Request model for updating track progress."""
    delta: int = Field(..., ge=0, le=100, description="Progress increase (0-100)")
    action_type: str = Field(..., description="Type of action (e.g., 'quest_created', 'letter_to_child')")
    milestone_achieved: Optional[str] = Field(None, description="Optional milestone name")


class TrackProgressResponse(BaseModel):
    """Response model for track progress."""
    track: str
    phase: str
    completion_percentage: int
    milestones: List[Dict]
    next_action: Dict
    last_activity: Optional[str]
    total_actions: int


class AllTracksResponse(BaseModel):
    """Response model for all tracks."""
    user_id: int
    tracks: Dict[str, TrackProgressResponse]
    primary_track: str


class MilestoneResponse(BaseModel):
    """Response model for milestone."""
    id: int
    track: str
    milestone_type: str
    milestone_name: str
    description: Optional[str]
    achieved_at: str
    achievement_context: Dict


class TrackSuggestionResponse(BaseModel):
    """Response model for track switch suggestion."""
    suggested_track: Optional[str]
    reason: Optional[str]
    current_track: str
    current_track_inactive_days: Optional[int]


# Endpoints
@router.get("/{user_id}", response_model=AllTracksResponse, status_code=status.HTTP_200_OK)
async def get_all_tracks(
    user_id: int,
    db: DatabaseManager = Depends(get_db_manager),
    mtm: MultiTrackManager = Depends(get_multi_track_manager)
):
    """Get progress for all 4 recovery tracks.

    Args:
        user_id: Telegram user ID

    Returns:
        All track progress with primary track indicator
    """
    try:
        logger.info("api_get_all_tracks_request", user_id=user_id)

        # Get all track progress
        tracks = await mtm.get_all_progress(user_id)

        if not tracks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tracks not found. Initialize user first."
            )

        # Get primary track
        primary_track = mtm.get_primary_track(tracks)

        # Convert to response format
        tracks_response = {
            track_name: TrackProgressResponse(**track_data)
            for track_name, track_data in tracks.items()
        }

        return AllTracksResponse(
            user_id=user_id,
            tracks=tracks_response,
            primary_track=primary_track
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_get_all_tracks_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve track progress: {str(e)}"
        )


@router.get("/{user_id}/{track_name}", response_model=TrackProgressResponse, status_code=status.HTTP_200_OK)
async def get_track(
    user_id: int,
    track_name: str,
    db: DatabaseManager = Depends(get_db_manager),
    mtm: MultiTrackManager = Depends(get_multi_track_manager)
):
    """Get progress for a specific recovery track.

    Args:
        user_id: Telegram user ID
        track_name: Track name (self_work, child_connection, negotiation, community)

    Returns:
        Track progress details
    """
    try:
        logger.info("api_get_track_request", user_id=user_id, track=track_name)

        # Validate track name
        try:
            RecoveryTrackEnum(track_name)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid track name. Must be one of: {[t.value for t in RecoveryTrackEnum]}"
            )

        # Get all tracks (there's no method to get just one track)
        tracks = await mtm.get_all_progress(user_id)

        if not tracks or track_name not in tracks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Track '{track_name}' not found for user {user_id}"
            )

        return TrackProgressResponse(**tracks[track_name])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_get_track_failed", user_id=user_id, track=track_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve track: {str(e)}"
        )


@router.post("/{user_id}/{track_name}/progress", response_model=AllTracksResponse, status_code=status.HTTP_200_OK)
async def update_track_progress(
    user_id: int,
    track_name: str,
    update: TrackProgressUpdate,
    db: DatabaseManager = Depends(get_db_manager),
    mtm: MultiTrackManager = Depends(get_multi_track_manager)
):
    """Update progress for a recovery track.

    This will also update any cross-track impacts (e.g., creating a quest
    affects both SELF_WORK and CHILD_CONNECTION tracks).

    Args:
        user_id: Telegram user ID
        track_name: Track name to update
        update: Progress update details

    Returns:
        Updated track progress for all tracks
    """
    try:
        logger.info("api_update_track_progress_request",
                   user_id=user_id,
                   track=track_name,
                   delta=update.delta,
                   action_type=update.action_type)

        # Validate track name
        try:
            RecoveryTrackEnum(track_name)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid track name. Must be one of: {[t.value for t in RecoveryTrackEnum]}"
            )

        # Update progress (includes cross-track impact)
        updated_tracks = await mtm.update_progress(
            user_id=user_id,
            track=track_name,
            delta=update.delta,
            action_type=update.action_type,
            milestone_achieved=update.milestone_achieved
        )

        # Get primary track
        primary_track = mtm.get_primary_track(updated_tracks)

        # Convert to response format
        tracks_response = {
            track_name: TrackProgressResponse(**track_data)
            for track_name, track_data in updated_tracks.items()
        }

        return AllTracksResponse(
            user_id=user_id,
            tracks=tracks_response,
            primary_track=primary_track
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_update_track_progress_failed",
                    user_id=user_id,
                    track=track_name,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update track progress: {str(e)}"
        )


@router.get("/{user_id}/milestones", response_model=List[MilestoneResponse], status_code=status.HTTP_200_OK)
async def get_user_milestones(
    user_id: int,
    track: Optional[str] = None,
    limit: int = 20,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get user's achieved milestones.

    Args:
        user_id: Telegram user ID
        track: Optional track filter (self_work, child_connection, etc.)
        limit: Maximum number of milestones to return

    Returns:
        List of achieved milestones
    """
    try:
        logger.info("api_get_milestones_request", user_id=user_id, track=track, limit=limit)

        # Validate track name if provided
        if track:
            try:
                RecoveryTrackEnum(track)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid track name. Must be one of: {[t.value for t in RecoveryTrackEnum]}"
                )

        # Get milestones from database
        milestones = await db.get_user_milestones(
            user_id=user_id,
            track=track,
            limit=limit
        )

        # Convert to response format
        return [
            MilestoneResponse(
                id=m.id,
                track=m.track,
                milestone_type=m.milestone_type,
                milestone_name=m.milestone_name,
                description=m.description,
                achieved_at=m.achieved_at.isoformat(),
                achievement_context=m.achievement_context or {}
            )
            for m in milestones
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_get_milestones_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve milestones: {str(e)}"
        )


@router.get("/{user_id}/suggestions", response_model=TrackSuggestionResponse, status_code=status.HTTP_200_OK)
async def get_track_suggestions(
    user_id: int,
    db: DatabaseManager = Depends(get_db_manager),
    mtm: MultiTrackManager = Depends(get_multi_track_manager)
):
    """Get track switch suggestions for user.

    Analyzes user's track activity and suggests which track to focus on next.
    Suggestions are made if:
    - Current track is inactive for >30 days
    - Another track has significantly lower progress

    Args:
        user_id: Telegram user ID

    Returns:
        Track switch suggestion (if any)
    """
    try:
        logger.info("api_get_track_suggestions_request", user_id=user_id)

        # Get all track progress
        tracks = await mtm.get_all_progress(user_id)

        if not tracks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tracks not found"
            )

        # Get primary track
        current_track = mtm.get_primary_track(tracks)

        # Check for suggestions
        suggested_track = mtm.should_suggest_track_switch(current_track, tracks)

        # Calculate inactivity days for current track
        from datetime import datetime
        inactive_days = None
        last_activity = tracks[current_track].get("last_activity")
        if last_activity:
            last_time = datetime.fromisoformat(last_activity)
            inactive_days = (datetime.utcnow() - last_time).days

        return TrackSuggestionResponse(
            suggested_track=suggested_track,
            reason="Current track inactive for >30 days" if suggested_track else None,
            current_track=current_track,
            current_track_inactive_days=inactive_days
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_get_track_suggestions_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )
