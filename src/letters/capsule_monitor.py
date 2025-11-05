"""Monitor time capsule letters for toxicity and notify users when ready to edit.

Logic:
- User writes time capsule with toxic content
- User ignores warnings
- Bot tracks user's emotional state
- When user becomes calmer → notify about toxic capsule
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.storage.database import DatabaseManager
from src.letters.types import LetterType
from src.core.logger import get_logger


logger = get_logger(__name__)


class CapsuleMonitor:
    """
    Monitor time capsule letters and notify users when they're ready to review toxic content.

    Checks:
    - User has time capsule with toxicity_warnings_ignored=True
    - User's emotional state has improved (distress_level decreased)
    - Enough time has passed since ignoring (at least 24 hours)
    """

    def __init__(self, db: DatabaseManager):
        """Initialize capsule monitor."""
        self.db = db

    async def check_toxic_capsules(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Check if user has toxic capsules that should be reviewed.

        Args:
            user_id: User ID

        Returns:
            List of capsules that need review
        """
        try:
            # Get user's time capsule letters with ignored warnings
            letters = await self.db.get_user_letters(
                user_id=user_id,
                status="draft"
            )

            toxic_capsules = []

            for letter in letters:
                # Check if it's a time capsule
                if letter.letter_type != LetterType.TIME_CAPSULE.value:
                    continue

                # Check if warnings were ignored
                if not letter.toxicity_warnings_ignored:
                    continue

                # Check if toxic
                if not letter.toxicity_score or letter.toxicity_score < 0.5:
                    continue

                # Check if enough time passed (24 hours)
                if letter.created_at:
                    hours_since_creation = (datetime.utcnow() - letter.created_at).total_seconds() / 3600
                    if hours_since_creation < 24:
                        continue

                toxic_capsules.append({
                    'letter_id': letter.id,
                    'title': letter.title,
                    'toxicity_score': letter.toxicity_score,
                    'created_at': letter.created_at,
                    'telegraph_url': letter.telegraph_url
                })

            return toxic_capsules

        except Exception as e:
            logger.error("toxic_capsule_check_failed", user_id=user_id, error=str(e))
            return []

    async def should_notify_user(
        self,
        user_id: int,
        current_distress_level: float
    ) -> bool:
        """
        Check if user should be notified about toxic capsules.

        Args:
            user_id: User ID
            current_distress_level: Current distress (0.0-1.0)

        Returns:
            True if should notify
        """
        try:
            # Get toxic capsules
            capsules = await self.check_toxic_capsules(user_id)

            if not capsules:
                return False

            # User should be notified if:
            # 1. Current distress is low (< 0.4)
            # 2. Has toxic capsules that are > 24h old
            #
            # Note: More sophisticated emotional state tracking (comparing current
            # vs historical distress) can be added later when we have session
            # emotional state tracking implemented.
            if current_distress_level < 0.4:
                logger.info("user_ready_for_capsule_review",
                           user_id=user_id,
                           distress=current_distress_level,
                           capsules_count=len(capsules))
                return True

            return False

        except Exception as e:
            logger.error("should_notify_check_failed", user_id=user_id, error=str(e))
            return False

    def format_notification(self, capsules: List[Dict[str, Any]]) -> str:
        """
        Format notification message about toxic capsules.

        Args:
            capsules: List of toxic capsules

        Returns:
            Formatted message
        """
        if not capsules:
            return ""

        if len(capsules) == 1:
            capsule = capsules[0]
            return f"""
💡 **Напоминание о капсуле для ребёнка**

Вы создали письмо-капсулу для ребёнка {capsule['created_at'].strftime('%d.%m.%Y')}.

При создании бот обнаружил токсичное содержимое (токсичность: {capsule['toxicity_score']:.0%}), которое может навредить ребёнку в будущем.

Сейчас вы в более спокойном состоянии. Возможно, вы готовы пересмотреть это письмо?

🔗 Открыть письмо: {capsule.get('telegraph_url', 'Ссылка недоступна')}

Рекомендую смягчить формулировки, чтобы защитить психику ребёнка.
            """
        else:
            message = f"""
💡 **Напоминание о капсулах для ребёнка**

У вас есть {len(capsules)} писем-капсул с токсичным содержимым.

Сейчас вы в более спокойном состоянии. Возможно, стоит их пересмотреть?

**Письма:**
            """

            for i, capsule in enumerate(capsules[:5], 1):
                message += f"\n{i}. {capsule['title']} (токсичность: {capsule['toxicity_score']:.0%})"

            message += "\n\nИспользуйте /my_letters чтобы открыть их."

            return message

    async def mark_notification_sent(self, user_id: int, letter_id: int):
        """Mark that notification was sent for this letter."""
        try:
            # Update letter metadata
            # TODO: Add notification_sent_at field to Letter model
            logger.info("capsule_notification_sent",
                       user_id=user_id,
                       letter_id=letter_id)

        except Exception as e:
            logger.error("mark_notification_failed",
                        user_id=user_id,
                        letter_id=letter_id,
                        error=str(e))
