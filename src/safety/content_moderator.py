"""Content moderator for quest safety.

Checks quest content for toxic patterns and provides recommendations.
Two-tier approach:
1. Pattern-based (fast, keyword detection)
2. AI-based (slower, SupervisorAgent integration)
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import re

from src.core.logger import get_logger

logger = get_logger(__name__)


class ModerationSeverity(str, Enum):
    """Severity levels for moderation issues."""
    CRITICAL = "critical"  # Must fix before deployment
    HIGH = "high"          # Strongly recommended to fix
    MEDIUM = "medium"      # Consider revising
    LOW = "low"            # Minor suggestion


class ModerationCategory(str, Enum):
    """Categories of moderation issues."""
    MANIPULATION = "manipulation"           # Gaslighting, guilt-tripping
    BLAME = "blame"                        # Blaming other parent
    PERSONAL_INFO = "personal_info"        # PII of custodial parent
    INAPPROPRIATE_CONTENT = "inappropriate" # Age-inappropriate
    NEGATIVE_EMOTION = "negative_emotion"  # Excessive negativity
    PRESSURE = "pressure"                  # Pressuring child
    VIOLENCE = "violence"                  # Violent content
    ADULT_TOPICS = "adult_topics"          # Divorce details, court, etc.


# Red flag patterns for quick detection
RED_FLAG_PATTERNS = {
    ModerationCategory.MANIPULATION: [
        r"должен.*вин",  # "должен винить"
        r"это.*виноват",
        r"плох.*мама|плох.*папа",
        r"не любит.*тебя",
        r"оставил.*нас",
        r"предал.*нас",
    ],
    ModerationCategory.BLAME: [
        r"мама.*виноват|папа.*виноват",
        r"из-за.*мам|из-за.*пап",
        r"мама.*разруш|папа.*разруш",
        r"развод.*виноват",
        r"суд.*виноват",
    ],
    ModerationCategory.PERSONAL_INFO: [
        r"\d{3}-\d{3}-\d{4}",  # Phone
        r"\d{4}\s\d{6}",  # Passport
        r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}",  # Email
        r"живет.*по.*адрес",
        r"номер.*телефон",
    ],
    ModerationCategory.PRESSURE: [
        r"ты.*должен",
        r"обязан",
        r"если.*не.*то",
        r"иначе",
        r"заставл",
    ],
    ModerationCategory.VIOLENCE: [
        r"убить|убив|убийств",
        r"избить|бить|удар",
        r"насили",
        r"причин.*боль",
    ],
    ModerationCategory.ADULT_TOPICS: [
        r"развод",
        r"суд",
        r"алимент",
        r"адвокат",
        r"юрист",
        r"опека",
        r"лишение.*прав",
    ],
}


class ContentModerator:
    """Moderates quest content for safety and appropriateness."""

    def __init__(self, supervisor_agent=None):
        """Initialize content moderator.

        Args:
            supervisor_agent: Optional SupervisorAgent for AI-based moderation
        """
        self.supervisor = supervisor_agent

    async def check_content(
        self,
        content: str,
        context: Optional[Dict] = None
    ) -> Tuple[bool, List[Dict]]:
        """Check content for safety issues.

        Args:
            content: Content to check
            context: Optional context (child age, content type)

        Returns:
            Tuple of (is_safe, issues_found)
            issues_found format: [{"category": str, "severity": str, "message": str, "location": str}]
        """
        issues = []

        # Pattern-based check (fast)
        pattern_issues = self._check_patterns(content)
        issues.extend(pattern_issues)

        # Check for excessive negativity
        negativity_issues = self._check_negativity(content)
        issues.extend(negativity_issues)

        # AI-based check if available (slower but more accurate)
        if self.supervisor:
            ai_issues = await self._check_with_ai(content, context)
            issues.extend(ai_issues)

        # Determine if safe
        is_safe = not any(
            issue["severity"] in [ModerationSeverity.CRITICAL.value, ModerationSeverity.HIGH.value]
            for issue in issues
        )

        if not is_safe:
            logger.warning(
                "content_moderation_failed",
                issues_count=len(issues),
                critical_count=sum(1 for i in issues if i["severity"] == ModerationSeverity.CRITICAL.value)
            )

        return is_safe, issues

    def _check_patterns(self, content: str) -> List[Dict]:
        """Check content against red flag patterns.

        Args:
            content: Content to check

        Returns:
            List of issues found
        """
        issues = []
        content_lower = content.lower()

        for category, patterns in RED_FLAG_PATTERNS.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, content_lower, re.IGNORECASE))
                if matches:
                    # Get context around match
                    for match in matches:
                        start = max(0, match.start() - 30)
                        end = min(len(content), match.end() + 30)
                        context_snippet = content[start:end]

                        issue = {
                            "category": category.value,
                            "severity": self._get_severity_for_category(category),
                            "message": self._get_message_for_category(category),
                            "location": f"...{context_snippet}...",
                            "pattern_matched": pattern
                        }
                        issues.append(issue)
                        logger.info(
                            "pattern_match_found",
                            category=category.value,
                            pattern=pattern
                        )

        return issues

    def _get_severity_for_category(self, category: ModerationCategory) -> str:
        """Get severity level for category."""
        severity_map = {
            ModerationCategory.MANIPULATION: ModerationSeverity.CRITICAL.value,
            ModerationCategory.BLAME: ModerationSeverity.CRITICAL.value,
            ModerationCategory.VIOLENCE: ModerationSeverity.CRITICAL.value,
            ModerationCategory.PERSONAL_INFO: ModerationSeverity.HIGH.value,
            ModerationCategory.PRESSURE: ModerationSeverity.HIGH.value,
            ModerationCategory.ADULT_TOPICS: ModerationSeverity.MEDIUM.value,
            ModerationCategory.NEGATIVE_EMOTION: ModerationSeverity.MEDIUM.value,
            ModerationCategory.INAPPROPRIATE_CONTENT: ModerationSeverity.HIGH.value,
        }
        return severity_map.get(category, ModerationSeverity.LOW.value)

    def _get_message_for_category(self, category: ModerationCategory) -> str:
        """Get user-friendly message for category."""
        messages = {
            ModerationCategory.MANIPULATION: "Content contains manipulative language that could harm the child.",
            ModerationCategory.BLAME: "Content blames the other parent. Focus on positive experiences instead.",
            ModerationCategory.PERSONAL_INFO: "Personal information detected. Remove for privacy.",
            ModerationCategory.INAPPROPRIATE_CONTENT: "Content may not be age-appropriate.",
            ModerationCategory.NEGATIVE_EMOTION: "Content is overly negative. Balance with positive elements.",
            ModerationCategory.PRESSURE: "Content pressures the child. Let them make their own choices.",
            ModerationCategory.VIOLENCE: "Violent content detected. This is not appropriate for children.",
            ModerationCategory.ADULT_TOPICS: "Adult topics like divorce/court should be avoided.",
        }
        return messages.get(category, "Content flagged for review.")

    def _check_negativity(self, content: str) -> List[Dict]:
        """Check for excessive negativity in content.

        Args:
            content: Content to check

        Returns:
            List of issues if negativity excessive
        """
        negative_words = [
            "плохо", "ужасно", "кошмар", "страшно", "больно",
            "грустно", "печально", "одиноко", "брошен", "предат",
            "виноват", "ненавиж", "злюсь", "боюсь"
        ]

        content_lower = content.lower()
        negative_count = sum(1 for word in negative_words if word in content_lower)
        word_count = len(content.split())

        # If >20% of meaningful words are negative
        if word_count > 20 and (negative_count / word_count) > 0.2:
            return [{
                "category": ModerationCategory.NEGATIVE_EMOTION.value,
                "severity": ModerationSeverity.MEDIUM.value,
                "message": f"Content has high negativity ({negative_count} negative words). Balance with positive experiences.",
                "location": "Overall tone",
                "negative_word_count": negative_count,
                "total_words": word_count
            }]

        return []

    async def _check_with_ai(
        self,
        content: str,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """Check content with AI (SupervisorAgent or GPT-4).

        Args:
            content: Content to check
            context: Context for evaluation

        Returns:
            List of AI-detected issues
        """
        if not self.supervisor:
            # Fallback to GPT-4 if SupervisorAgent unavailable
            return await self._check_with_gpt4(content, context)

        try:
            # Build prompt for supervisor
            prompt = f"""Evaluate this quest content for a child for safety and appropriateness:

Content: "{content}"

Context: {context or 'General educational quest'}

Check for:
1. Manipulation or gaslighting
2. Blaming the other parent
3. Age-inappropriate content
4. Pressure on the child
5. Adult topics (divorce, court, legal)

Return a safety assessment with specific issues found."""

            # Call supervisor evaluate method
            result = await self.supervisor.evaluate(
                user_message=prompt,
                context={"moderation_check": True, "content": content}
            )

            # Parse issues from supervisor response
            issues = self._parse_supervisor_response(result)

            logger.info(
                "ai_moderation_complete",
                content_length=len(content),
                issues_found=len(issues)
            )
            return issues

        except Exception as e:
            logger.error("ai_moderation_failed", error=str(e))
            # Fallback to GPT-4
            return await self._check_with_gpt4(content, context)

    async def _check_with_gpt4(
        self,
        content: str,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """Fallback moderation using GPT-4 directly.

        Args:
            content: Content to check
            context: Context for evaluation

        Returns:
            List of AI-detected issues
        """
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage
            from src.core.config import settings

            llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.1,
                api_key=settings.openai_api_key
            )

            system_prompt = """You are a content safety expert specializing in child protection.
Evaluate content for:
- Manipulation/gaslighting
- Blaming other parent
- Age-inappropriate topics
- Pressure on child
- Adult topics (divorce, legal)

Return a JSON list of issues with format:
[{"category": "manipulation", "severity": "critical", "message": "...", "location": "..."}]

Return empty list [] if content is safe."""

            child_age = context.get("child_age", 10) if context else 10
            user_prompt = f"""Evaluate this quest content for a {child_age}-year-old child:

"{content}"

Return JSON list of issues or [] if safe:"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = await llm.ainvoke(messages)
            response_text = response.content.strip()

            # Parse JSON response
            import json
            if response_text.startswith("["):
                issues = json.loads(response_text)
                logger.info(
                    "gpt4_moderation_complete",
                    issues_count=len(issues)
                )
                return issues
            else:
                logger.warning(
                    "gpt4_moderation_invalid_format",
                    response=response_text[:100]
                )
                return []

        except Exception as e:
            logger.error("gpt4_moderation_failed", error=str(e))
            return []

    def _parse_supervisor_response(self, result: Any) -> List[Dict]:
        """Parse SupervisorAgent response into issues list.

        Args:
            result: SupervisorAgent evaluation result

        Returns:
            List of issues
        """
        issues = []

        # If result is a dict with 'issues' key
        if isinstance(result, dict) and "issues" in result:
            issues = result["issues"]

        # If result is a TechniqueResult
        elif hasattr(result, "metadata") and "issues" in result.metadata:
            issues = result.metadata["issues"]

        # Otherwise parse from response text
        elif hasattr(result, "response"):
            # Try to extract issues from text
            # This is a fallback for text-based responses
            pass

        return issues

    async def moderate_quest(self, quest_yaml: str, quest_metadata: Dict) -> Dict:
        """Moderate entire quest YAML.

        Checks:
        - Quest title and description
        - All step prompts
        - Feedback messages
        - Reveal message

        Args:
            quest_yaml: Full YAML content
            quest_metadata: Metadata (child age, interests)

        Returns:
            Moderation result: {"passed": bool, "issues": List[Dict], "suggestions": List[str]}
        """
        issues = []
        suggestions = []

        # Parse YAML sections (simplified - actual implementation would parse YAML)
        # For now, check entire content
        is_safe, content_issues = await self.check_content(
            quest_yaml,
            context=quest_metadata
        )

        issues.extend(content_issues)

        # Generate suggestions for fixes
        if issues:
            suggestions = self._generate_fix_suggestions(issues)

        result = {
            "passed": is_safe,
            "issues": issues,
            "suggestions": suggestions,
            "total_issues": len(issues),
            "critical_issues": sum(1 for i in issues if i["severity"] == ModerationSeverity.CRITICAL.value),
            "high_issues": sum(1 for i in issues if i["severity"] == ModerationSeverity.HIGH.value),
        }

        logger.info(
            "quest_moderation_complete",
            passed=is_safe,
            total_issues=len(issues),
            critical=result["critical_issues"]
        )

        return result

    def _generate_fix_suggestions(self, issues: List[Dict]) -> List[str]:
        """Generate actionable suggestions to fix issues.

        Args:
            issues: List of moderation issues

        Returns:
            List of fix suggestions
        """
        suggestions = []

        # Group by category
        categories = {}
        for issue in issues:
            cat = issue["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(issue)

        # Generate category-specific suggestions
        if ModerationCategory.MANIPULATION.value in categories:
            suggestions.append(
                "Remove manipulative language. Focus on positive shared experiences and memories."
            )

        if ModerationCategory.BLAME.value in categories:
            suggestions.append(
                "Avoid blaming the other parent. Frame content neutrally around education and fun."
            )

        if ModerationCategory.PERSONAL_INFO.value in categories:
            suggestions.append(
                "Remove personal information (phone numbers, addresses, etc.) for privacy."
            )

        if ModerationCategory.ADULT_TOPICS.value in categories:
            suggestions.append(
                "Remove adult topics (divorce, court, legal issues). Keep content child-focused."
            )

        if ModerationCategory.NEGATIVE_EMOTION.value in categories:
            suggestions.append(
                "Balance negative emotions with positive memories and future hopes."
            )

        if ModerationCategory.PRESSURE.value in categories:
            suggestions.append(
                "Remove pressure language. Let the child explore freely without obligations."
            )

        if not suggestions:
            suggestions.append("Review flagged content and consider alternative phrasing.")

        return suggestions

    def get_safe_alternative(self, problematic_phrase: str, category: ModerationCategory) -> str:
        """Get safe alternative for problematic phrase.

        Args:
            problematic_phrase: Phrase that was flagged
            category: Category of issue

        Returns:
            Suggested safe alternative
        """
        alternatives = {
            ModerationCategory.MANIPULATION: "Focus on shared positive experiences",
            ModerationCategory.BLAME: "Describe the situation neutrally",
            ModerationCategory.PERSONAL_INFO: "[REDACTED FOR PRIVACY]",
            ModerationCategory.ADULT_TOPICS: "Let's focus on fun and learning",
            ModerationCategory.PRESSURE: "You're free to choose",
            ModerationCategory.NEGATIVE_EMOTION: "Remember the good times we had",
        }

        return alternatives.get(category, "Consider rephrasing this")
