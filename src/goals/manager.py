"""Goal tracking and management."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from src.goals.smart_validator import SMARTValidator
from src.core.logger import get_logger

logger = get_logger(__name__)


class GoalStatus(str, Enum):
    """Goal status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class Goal:
    """User goal."""
    id: str
    user_id: str
    text: str
    status: GoalStatus = GoalStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    target_date: Optional[datetime] = None
    progress: int = 0  # 0-100
    notes: List[str] = field(default_factory=list)


class GoalManager:
    """Manage user goals."""

    def __init__(self):
        """Initialize goal manager."""
        self.validator = SMARTValidator()
        self.goals: Dict[str, List[Goal]] = {}  # user_id -> goals

    async def create_goal(self, user_id: str, goal_text: str) -> Dict[str, Any]:
        """Create new goal."""

        # Validate SMART
        analysis = self.validator.validate(goal_text)

        if analysis.score < 0.6:
            return {
                "success": False,
                "message": "Цель не соответствует SMART критериям",
                "analysis": analysis,
                "suggestions": analysis.suggestions
            }

        # Create goal
        goal = Goal(
            id=f"goal_{user_id}_{int(datetime.now().timestamp())}",
            user_id=user_id,
            text=goal_text
        )

        if user_id not in self.goals:
            self.goals[user_id] = []

        self.goals[user_id].append(goal)

        logger.info("goal_created", user_id=user_id, goal_id=goal.id)

        return {
            "success": True,
            "message": f"✅ Цель создана!\n\n{goal_text}\n\nSMART оценка: {analysis.score*100:.0f}%",
            "goal": goal
        }

    async def list_goals(self, user_id: str) -> List[Goal]:
        """List user's active goals."""
        return [g for g in self.goals.get(user_id, []) if g.status == GoalStatus.ACTIVE]

    async def update_progress(self, user_id: str, goal_id: str, progress: int) -> str:
        """Update goal progress."""
        user_goals = self.goals.get(user_id, [])
        for goal in user_goals:
            if goal.id == goal_id:
                goal.progress = min(100, max(0, progress))
                if goal.progress >= 100:
                    goal.status = GoalStatus.COMPLETED

                return f"Прогресс обновлён: {goal.progress}%"

        return "Цель не найдена"
