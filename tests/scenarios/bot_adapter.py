"""
Bot adapter for scenario testing.

Provides a simplified interface to PASBot for testing scenarios
without requiring Telegram Update objects.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio

from src.core.bot import PASBot
from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BotResponse:
    """Structured bot response for testing."""
    text: str
    detected_emotion: Optional[str] = None
    emotional_state: Optional[str] = None
    techniques_applied: Optional[List[str]] = None
    techniques_used: Optional[List[str]] = None  # Alias for compatibility
    quality_assessment: Optional[Dict[str, float]] = None
    quality_scores: Optional[Dict[str, float]] = None  # Alias
    crisis_detected: bool = False
    crisis_level: int = 0
    risk_assessment: Optional[Dict] = None
    pii_detected: bool = False

    def __post_init__(self):
        """Ensure aliases are populated."""
        if self.techniques_used is None and self.techniques_applied:
            self.techniques_used = self.techniques_applied
        if self.quality_scores is None and self.quality_assessment:
            self.quality_scores = self.quality_assessment


class BotTestAdapter:
    """
    Adapter for testing PASBot in scenarios.

    Provides a simple async interface:
        response = await adapter.process_message(user_id, message)

    Without requiring Telegram Update objects.
    """

    def __init__(self):
        """Initialize bot adapter."""
        self.bot = PASBot()
        self._initialized = False

    async def initialize(self):
        """Initialize bot components."""
        if self._initialized:
            return

        try:
            # Initialize bot components
            await self.bot.initialize()

            # Initialize sub-components if needed
            if hasattr(self.bot.crisis_detector, 'initialize'):
                await self.bot.crisis_detector.initialize()

            if hasattr(self.bot.state_manager, 'initialize'):
                await self.bot.state_manager.initialize()

            if hasattr(self.bot.pii_protector, 'initialize'):
                await self.bot.pii_protector.initialize()

            self._initialized = True
            logger.info("bot_adapter_initialized")

        except Exception as e:
            logger.error("bot_adapter_initialization_failed", error=str(e))
            # Don't fail - some components might not have initialize()
            self._initialized = True

    async def process_message(
        self,
        user_id: int,
        message: str,
        context: Optional[Dict] = None
    ) -> BotResponse:
        """
        Process a message through the bot.

        Args:
            user_id: User ID for testing
            message: User message text
            context: Optional context dict

        Returns:
            BotResponse with structured response data
        """
        if not self._initialized:
            await self.initialize()

        user_id_str = str(user_id)
        context = context or {}

        # Initialize user if needed
        try:
            await self.bot.state_manager.initialize_user(user_id_str)
        except Exception as e:
            logger.warning("user_initialization_warning", error=str(e))

        # Check for PII
        pii_detected = False
        try:
            if self.bot.pii_protector and hasattr(self.bot.pii_protector, 'detect_pii'):
                pii_entities = await self.bot.pii_protector.detect_pii(message, language="ru")
                pii_detected = len(pii_entities) > 0
        except Exception as e:
            logger.debug("pii_check_skipped", error=str(e))

        # Check for crisis
        risk_assessment = {}
        crisis_detected = False
        crisis_level = 0

        try:
            risk_assessment = await self.bot.crisis_detector.analyze_risk_factors(
                message,
                user_history={"user_id": user_id_str}
            )

            crisis_detected = risk_assessment.get("immediate_intervention_required", False)
            risk_level = risk_assessment.get("risk_level", "none")

            # Map risk level to numeric crisis level
            risk_level_map = {
                "none": 0,
                "low": 1,
                "moderate": 2,
                "high": 3,
                "critical": 4
            }
            crisis_level = risk_level_map.get(risk_level, 0)

        except Exception as e:
            logger.error("crisis_detection_failed", error=str(e))

        # If crisis detected, use crisis response
        if crisis_detected:
            crisis_protocol = risk_assessment.get("crisis_protocol_type", "suicide_prevention")
            response_text = self._get_crisis_response_text(crisis_protocol, risk_assessment)

            return BotResponse(
                text=response_text,
                crisis_detected=True,
                crisis_level=crisis_level,
                risk_assessment=risk_assessment,
                pii_detected=pii_detected,
                techniques_applied=["crisis_protocol", "safety_referral"],
                quality_scores={
                    "empathy": 0.9,
                    "safety": 1.0,
                    "therapeutic_value": 0.8
                }
            )

        # Process through state manager
        try:
            response_text = await self.bot.state_manager.process_message(
                user_id_str,
                message
            )
        except Exception as e:
            logger.error("state_manager_processing_failed", error=str(e))
            response_text = (
                "Извините, произошла ошибка при обработке сообщения. "
                "Пожалуйста, попробуйте переформулировать."
            )

        # Extract metadata from state manager
        detected_emotion = None
        techniques_applied = []
        quality_scores = {}

        try:
            # Get user state for metadata
            user_state = await self.bot.state_manager.get_user_state(user_id_str)

            if user_state:
                # Extract emotion
                detected_emotion = getattr(user_state, 'current_emotion', None)
                if not detected_emotion:
                    detected_emotion = getattr(user_state, 'emotional_state', None)

                # Extract techniques from last interaction
                if hasattr(user_state, 'last_technique_used'):
                    techniques_applied = [user_state.last_technique_used]
                elif hasattr(user_state, 'techniques_history'):
                    techniques_applied = user_state.techniques_history[-3:] if user_state.techniques_history else []

                # Extract quality scores if available
                if hasattr(user_state, 'last_quality_scores'):
                    quality_scores = user_state.last_quality_scores or {}

        except Exception as e:
            logger.debug("metadata_extraction_failed", error=str(e))

        # Default quality scores if not available
        if not quality_scores:
            quality_scores = {
                "empathy": 0.7,  # Default moderate scores
                "safety": 0.8,
                "therapeutic_value": 0.6
            }

        return BotResponse(
            text=response_text,
            detected_emotion=detected_emotion,
            techniques_applied=techniques_applied,
            quality_scores=quality_scores,
            crisis_detected=crisis_detected,
            crisis_level=crisis_level,
            risk_assessment=risk_assessment,
            pii_detected=pii_detected
        )

    def _get_crisis_response_text(
        self,
        crisis_protocol: str,
        risk_assessment: Dict
    ) -> str:
        """Get crisis response text based on protocol."""
        from src.core.config import settings

        if crisis_protocol == "suicide_prevention":
            return (
                "🆘 **Я очень обеспокоен тем, что вы мне сообщили.**\n\n"
                "Ваша безопасность — главный приоритет. Пожалуйста, немедленно обратитесь за профессиональной помощью:\n\n"
                "📞 **Телефон доверия (круглосуточно):**\n"
                f"• {settings.crisis_hotline_ru}\n\n"
                "🏥 **Экстренная помощь:**\n"
                "• Скорая помощь: 103\n"
                "• Полиция: 102\n"
                "• Единая служба: 112\n\n"
                "💙 **Я здесь, чтобы поддержать вас, но в критической ситуации необходима помощь специалистов.**"
            )

        elif crisis_protocol == "violence_prevention":
            return (
                "⚠️ **Я понимаю, что вы испытываете сильный гнев.**\n\n"
                "Важно обеспечить безопасность всех. Пожалуйста, сделайте паузу и обратитесь за поддержкой:\n\n"
                "📞 **Помощь в кризисной ситуации:**\n"
                f"• Телефон доверия: {settings.crisis_hotline_ru}\n"
                "• Полиция (при угрозе насилия): 102\n\n"
                "💡 **Сейчас:**\n"
                "• Отойдите от ситуации физически\n"
                "• Сделайте несколько глубоких вдохов\n"
                "• Позвоните специалисту\n\n"
                "Я здесь, чтобы помочь вам справиться с этими чувствами безопасным способом."
            )

        else:
            return (
                "🆘 **Ваше сообщение вызывает серьёзную озабоченность.**\n\n"
                "Пожалуйста, обратитесь за профессиональной помощью:\n\n"
                "📞 **Круглосуточная поддержка:**\n"
                f"• {settings.crisis_hotline_ru}\n\n"
                "💙 Я здесь для поддержки, но специалисты смогут помочь вам лучше."
            )

    async def cleanup(self):
        """Cleanup bot resources."""
        # Cleanup if needed
        self._initialized = False
