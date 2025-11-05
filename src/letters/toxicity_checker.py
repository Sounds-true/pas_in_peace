"""Toxicity analysis for letters using Detoxify + LLM."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re

try:
    from detoxify import Detoxify
    DETOXIFY_AVAILABLE = True
except ImportError:
    DETOXIFY_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

from src.core.logger import get_logger
from src.core.config import settings


logger = get_logger(__name__)


@dataclass
class ToxicPhrase:
    """A toxic phrase detected in text."""
    text: str
    type: str  # insult, threat, obscene, etc.
    score: float  # 0.0-1.0
    context: str  # Surrounding text
    suggestion: Optional[str] = None  # LLM suggestion for replacement


@dataclass
class ToxicityAnalysis:
    """Complete toxicity analysis result."""
    overall_score: float  # 0.0-1.0 combined toxicity
    is_toxic: bool  # Above threshold?
    scores: Dict[str, float]  # Detoxify scores
    toxic_phrases: List[ToxicPhrase]
    llm_recommendation: Optional[str] = None  # Detailed LLM analysis
    safe_alternative: Optional[str] = None  # LLM rewritten version


class ToxicityChecker:
    """
    Check letter toxicity using Detoxify + LLM.

    Flow:
    1. Detoxify detects toxic patterns
    2. Extract specific toxic phrases
    3. LLM provides detailed recommendations
    """

    def __init__(self):
        """Initialize toxicity checker."""
        self.detoxify = None
        self.llm = None
        self.initialized = False

        # Toxic patterns for Russian text
        self.toxic_patterns = {
            'insult': [
                r'\bсука\b', r'\bсволочь\b', r'\bубл[юя]док\b', r'\bид[ие]от\b',
                r'\bдур[ао]к\b', r'\bд[еи]била\w*', r'\bурод\w*', r'\bтварь\b'
            ],
            'threat': [
                r'заплат[иь]\w*', r'пожале[еюйя]\w*', r'отомщ\w*', r'накажу',
                r'подам\s+в\s+суд', r'лиш[уюиь]\w*\s+родительских'
            ],
            'blame': [
                r'ты\s+виноват\w*', r'из-за\s+тебя', r'твоя\s+вина',
                r'ты\s+разруш[ие]\w*', r'ты\s+укра[лд]\w*'
            ],
            'manipulation': [
                r'ребёнок\s+не\s+хочет', r'ребёнок\s+боится',
                r'видишь\s+что\s+ты\s+сдела[лд]', r'дети\s+страдают\s+из-за\s+тебя'
            ]
        }

    async def initialize(self) -> bool:
        """Initialize Detoxify and LLM."""
        if self.initialized:
            return True

        # Initialize Detoxify
        if DETOXIFY_AVAILABLE:
            try:
                self.detoxify = Detoxify('multilingual')
                logger.info("detoxify_initialized")
            except Exception as e:
                logger.warning("detoxify_init_failed", error=str(e))
                return False
        else:
            logger.warning("detoxify_not_available")
            return False

        # Initialize LLM (optional)
        if LLM_AVAILABLE and hasattr(settings, 'OPENAI_API_KEY'):
            try:
                self.llm = ChatOpenAI(
                    model="gpt-4",
                    temperature=0.3,
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info("llm_initialized_for_toxicity")
            except Exception as e:
                logger.warning("llm_init_failed", error=str(e))
                self.llm = None

        self.initialized = True
        return True

    async def analyze(
        self,
        text: str,
        threshold: float = 0.5,
        use_llm: bool = True
    ) -> ToxicityAnalysis:
        """
        Analyze text toxicity.

        Args:
            text: Text to analyze
            threshold: Toxicity threshold (0.0-1.0)
            use_llm: Use LLM for detailed recommendations

        Returns:
            ToxicityAnalysis with scores and recommendations
        """
        if not self.initialized:
            await self.initialize()

        # Step 1: Detoxify analysis
        detoxify_scores = self._detoxify_analyze(text)

        # Step 2: Extract toxic phrases
        toxic_phrases = self._extract_toxic_phrases(text, detoxify_scores)

        # Step 3: Calculate overall score
        overall_score = max(detoxify_scores.values()) if detoxify_scores else 0.0
        is_toxic = overall_score >= threshold

        # Step 4: LLM recommendations (if toxic and LLM available)
        llm_recommendation = None
        safe_alternative = None

        if is_toxic and use_llm and self.llm:
            try:
                llm_result = await self._get_llm_recommendations(text, toxic_phrases)
                llm_recommendation = llm_result.get('recommendation')
                safe_alternative = llm_result.get('alternative')
            except Exception as e:
                logger.error("llm_recommendation_failed", error=str(e))

        return ToxicityAnalysis(
            overall_score=overall_score,
            is_toxic=is_toxic,
            scores=detoxify_scores,
            toxic_phrases=toxic_phrases,
            llm_recommendation=llm_recommendation,
            safe_alternative=safe_alternative
        )

    def _detoxify_analyze(self, text: str) -> Dict[str, float]:
        """Run Detoxify analysis."""
        if not self.detoxify:
            return {}

        try:
            results = self.detoxify.predict(text)
            return {
                'toxicity': float(results.get('toxicity', 0)),
                'severe_toxicity': float(results.get('severe_toxicity', 0)),
                'obscene': float(results.get('obscene', 0)),
                'threat': float(results.get('threat', 0)),
                'insult': float(results.get('insult', 0)),
                'identity_attack': float(results.get('identity_attack', 0))
            }
        except Exception as e:
            logger.error("detoxify_analysis_failed", error=str(e))
            return {}

    def _extract_toxic_phrases(
        self,
        text: str,
        scores: Dict[str, float]
    ) -> List[ToxicPhrase]:
        """Extract specific toxic phrases using patterns."""
        toxic_phrases = []
        text_lower = text.lower()

        # Check each pattern category
        for category, patterns in self.toxic_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    phrase = text[match.start():match.end()]

                    # Get context (20 chars before/after)
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    context = text[start:end]

                    toxic_phrases.append(ToxicPhrase(
                        text=phrase,
                        type=category,
                        score=scores.get(category, scores.get('toxicity', 0.5)),
                        context=context
                    ))

        return toxic_phrases

    async def _get_llm_recommendations(
        self,
        text: str,
        toxic_phrases: List[ToxicPhrase]
    ) -> Dict[str, str]:
        """Get detailed recommendations from LLM."""
        if not self.llm:
            return {}

        # Build toxic phrases summary
        phrases_summary = "\n".join([
            f"- '{phrase.text}' (тип: {phrase.type}, контекст: ...{phrase.context}...)"
            for phrase in toxic_phrases[:5]  # Limit to top 5
        ])

        system_prompt = """Ты - психолог, специализирующийся на родительском отчуждении.
Помогаешь родителям писать конструктивные письма.

Твоя задача:
1. Объяснить почему токсичные фразы вредны (особенно для ребёнка в будущем)
2. Предложить конкретные альтернативы
3. Быть эмпатичным но честным"""

        user_prompt = f"""Проанализируй письмо на токсичность:

ТЕКСТ:
{text}

ОБНАРУЖЕННЫЕ ПРОБЛЕМЫ:
{phrases_summary if phrases_summary else "Общая токсичность без конкретных фраз"}

Дай рекомендации:
1. Почему эти фразы проблематичны? (особенно если ребёнок прочитает в будущем)
2. Как переформулировать конструктивно?
3. Предложи альтернативную версию письма.

Формат ответа:
ПОЧЕМУ ПРОБЛЕМАТИЧНО:
[объяснение]

РЕКОМЕНДАЦИИ:
[конкретные советы]

АЛЬТЕРНАТИВА:
[переписанная версия письма]"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = await self.llm.ainvoke(messages)
            content = response.content

            # Parse response
            recommendation = content
            alternative = None

            if "АЛЬТЕРНАТИВА:" in content:
                parts = content.split("АЛЬТЕРНАТИВА:")
                recommendation = parts[0].strip()
                alternative = parts[1].strip() if len(parts) > 1 else None

            return {
                'recommendation': recommendation,
                'alternative': alternative
            }

        except Exception as e:
            logger.error("llm_analysis_failed", error=str(e))
            return {}

    def format_warnings(self, analysis: ToxicityAnalysis) -> str:
        """Format toxicity warnings for user."""
        if not analysis.is_toxic:
            return "✅ Письмо не содержит токсичных фраз."

        warnings = []
        warnings.append(f"⚠️ **Обнаружена токсичность: {analysis.overall_score:.0%}**\n")

        # List toxic phrases
        if analysis.toxic_phrases:
            warnings.append("**Проблемные фразы:**")
            for phrase in analysis.toxic_phrases[:5]:
                type_emoji = {
                    'insult': '😠',
                    'threat': '⚡',
                    'blame': '👉',
                    'manipulation': '🎭'
                }.get(phrase.type, '⚠️')

                warnings.append(
                    f"{type_emoji} \"{phrase.text}\" (тип: {phrase.type})"
                )

        # Add LLM recommendation
        if analysis.llm_recommendation:
            warnings.append(f"\n💡 **Рекомендации:**\n{analysis.llm_recommendation}")

        # Add safe alternative
        if analysis.safe_alternative:
            warnings.append(f"\n✍️ **Альтернативный вариант:**\n{analysis.safe_alternative}")

        return "\n".join(warnings)
