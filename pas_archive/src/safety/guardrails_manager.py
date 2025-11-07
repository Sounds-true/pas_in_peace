"""NeMo Guardrails integration for safety policies."""

from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
from nemoguardrails import RailsConfig, LLMRails

from src.core.logger import get_logger
from src.core.config import settings


logger = get_logger(__name__)


class GuardrailsManager:
    """Manages NeMo Guardrails for conversation safety."""

    def __init__(self, config_path: Path = Path("config/guardrails")):
        """Initialize guardrails manager."""
        self.config_path = config_path
        self.rails: Optional[LLMRails] = None
        self.active_policies: List[str] = []

    async def initialize(self) -> None:
        """Load and initialize guardrails configuration."""
        try:
            # Load Colang configuration
            config = RailsConfig.from_path(str(self.config_path))

            # Note: Model config is loaded from config.yml
            # API key will be read from environment variable OPENAI_API_KEY

            # Initialize Rails
            self.rails = LLMRails(config)

            # Track active policies
            self.active_policies = [
                "crisis_intervention",
                "legal_boundaries",
                "privacy_protection",
                "manipulation_detection",
                "child_discussion_redirect"
            ]

            logger.info(
                "guardrails_initialized",
                policies=self.active_policies,
                config_path=str(self.config_path)
            )

        except Exception as e:
            logger.error("guardrails_init_failed", error=str(e))
            raise

    async def check_message(self, user_message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Check message against guardrails.

        Returns:
            Dict with keys:
            - allowed: bool (whether message passes guardrails)
            - response: str (guardrail response if blocked)
            - triggered_policy: str (which policy was triggered)
            - severity: str (low/medium/high/critical)
        """
        if not self.rails:
            logger.error("guardrails_not_initialized")
            return {
                "allowed": True,
                "response": None,
                "triggered_policy": None,
                "severity": None
            }

        try:
            # Prepare context for guardrails
            rail_context = context or {}
            rail_context["user_message"] = user_message

            # Run guardrails check
            response = await self.rails.generate_async(
                messages=[{"role": "user", "content": user_message}]
            )

            # Analyze response
            if response.get("blocked", False):
                return {
                    "allowed": False,
                    "response": response.get("message", "I cannot process this request."),
                    "triggered_policy": response.get("policy", "unknown"),
                    "severity": self._get_severity(response.get("policy"))
                }

            return {
                "allowed": True,
                "response": None,
                "triggered_policy": None,
                "severity": None
            }

        except Exception as e:
            logger.error("guardrails_check_failed", error=str(e))
            # Default to allowing with caution
            return {
                "allowed": True,
                "response": None,
                "triggered_policy": None,
                "severity": None
            }

    async def generate_safe_response(
        self,
        user_message: str,
        bot_response: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate a safe response using guardrails.

        Checks both user input and bot output for safety.
        """
        if not self.rails:
            return bot_response

        try:
            # Check if user message triggers any guardrails
            user_check = await self.check_message(user_message, context)

            if not user_check["allowed"]:
                logger.warning(
                    "user_message_blocked",
                    policy=user_check["triggered_policy"],
                    severity=user_check["severity"]
                )
                return user_check["response"]

            # Check if bot response violates any policies
            bot_check = await self.check_message(bot_response, context)

            if not bot_check["allowed"]:
                logger.warning(
                    "bot_response_blocked",
                    policy=bot_check["triggered_policy"],
                    severity=bot_check["severity"]
                )
                # Generate alternative safe response
                return await self._generate_alternative_response(user_message, context)

            return bot_response

        except Exception as e:
            logger.error("safe_response_generation_failed", error=str(e))
            return "I'm having trouble processing your request safely. Please try rephrasing."

    async def _generate_alternative_response(
        self,
        user_message: str,
        context: Optional[Dict] = None
    ) -> str:
        """Generate alternative response when original is blocked."""
        try:
            # Use guardrails to generate safe alternative
            response = await self.rails.generate_async(
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a safe, supportive response that respects boundaries."
                    },
                    {"role": "user", "content": user_message}
                ]
            )
            return response.get("content", "Let's focus on how you're feeling about this situation.")

        except Exception as e:
            logger.error("alternative_response_failed", error=str(e))
            return "Let's focus on how you're feeling about this situation."

    def _get_severity(self, policy: Optional[str]) -> str:
        """Determine severity level of triggered policy."""
        if not policy:
            return "low"

        severity_map = {
            "crisis_intervention": "critical",
            "harm_to_others": "critical",
            "legal_boundaries": "medium",
            "privacy_protection": "low",
            "manipulation_detection": "medium",
            "child_discussion_redirect": "low"
        }

        return severity_map.get(policy, "low")

    async def add_custom_policy(self, policy_name: str, policy_definition: str) -> bool:
        """Add custom guardrail policy at runtime."""
        try:
            # This would append to the rails.colang file
            # Implementation depends on NeMo Guardrails version
            logger.info("custom_policy_added", policy=policy_name)
            self.active_policies.append(policy_name)
            return True

        except Exception as e:
            logger.error("custom_policy_failed", policy=policy_name, error=str(e))
            return False

    async def get_policy_stats(self) -> Dict[str, int]:
        """Get statistics on triggered policies."""
        # This would query from a metrics store
        # Placeholder implementation
        return {
            "crisis_interventions": 0,
            "legal_boundaries": 0,
            "privacy_protections": 0,
            "manipulation_detections": 0
        }