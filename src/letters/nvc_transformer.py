"""NVC (Nonviolent Communication) transformer for letters."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NVCStructure:
    """NVC four-part structure."""
    observation: str  # Objective facts
    feeling: str      # Emotions
    need: str         # Underlying needs
    request: str      # Specific request


class NVCTransformer:
    """
    Transform letters to Nonviolent Communication (NVC) format.

    NVC Formula (Rosenberg, 2003):
    1. OBSERVATION: "When I see/hear..." (facts, not judgments)
    2. FEELING: "I feel..." (emotions, not thoughts)
    3. NEED: "Because I need/value..." (universal human needs)
    4. REQUEST: "Would you be willing to..." (clear, positive, actionable)

    References:
    - Marshall Rosenberg (2003) - Nonviolent Communication: A Language of Life
    - Center for Nonviolent Communication (CNVC)
    """

    def __init__(self):
        """Initialize NVC transformer."""
        # Violent communication patterns to detect
        self.violent_patterns = {
            "russian": {
                "judgments": ["ты", "ты всегда", "ты никогда", "ты плохой", "ты манипулируешь"],
                "demands": ["должен", "обязан", "нужно чтобы ты"],
                "blame": ["из-за тебя", "твоя вина", "ты виноват"],
                "criticism": ["плохо", "неправильно", "ужасно", "отвратительно"]
            },
            "english": {
                "judgments": ["you", "you always", "you never", "you are bad", "you manipulate"],
                "demands": ["must", "have to", "should"],
                "blame": ["because of you", "your fault", "you're to blame"],
                "criticism": ["bad", "wrong", "terrible", "disgusting"]
            }
        }

        # Universal human needs (NVC framework)
        self.universal_needs = {
            "russian": {
                "connection": ["любовь", "уважение", "понимание", "принятие", "близость", "доверие"],
                "physical": ["безопасность", "отдых", "здоровье", "комфорт"],
                "autonomy": ["выбор", "свобода", "независимость", "самовыражение"],
                "meaning": ["смысл", "цель", "вклад", "рост"],
                "celebration": ["радость", "игра", "красота"],
                "integrity": ["честность", "подлинность", "последовательность"]
            },
            "english": {
                "connection": ["love", "respect", "understanding", "acceptance", "closeness", "trust"],
                "physical": ["safety", "rest", "health", "comfort"],
                "autonomy": ["choice", "freedom", "independence", "self-expression"],
                "meaning": ["meaning", "purpose", "contribution", "growth"],
                "celebration": ["joy", "play", "beauty"],
                "integrity": ["honesty", "authenticity", "consistency"]
            }
        }

        # Feeling words (emotions, not pseudo-feelings)
        self.feeling_words = {
            "russian": {
                "pleasant": ["рад", "счастлив", "вдохновлен", "спокоен", "благодарен", "облегчен"],
                "unpleasant": ["грустен", "разочарован", "обеспокоен", "растерян", "одинок", "напуган", "раздражен"]
            },
            "english": {
                "pleasant": ["glad", "happy", "inspired", "calm", "grateful", "relieved"],
                "unpleasant": ["sad", "disappointed", "concerned", "confused", "lonely", "scared", "irritated"]
            }
        }

    def transform(
        self,
        letter_text: str,
        language: str = "russian",
        recipient: str = "ex-partner"
    ) -> Dict[str, Any]:
        """
        Transform letter to NVC structure.

        Args:
            letter_text: Original letter text
            language: Language of transformation
            recipient: Type of recipient ("ex-partner", "child", "other")

        Returns:
            Dict with original, transformed text, and NVC structure
        """
        # Detect violent communication patterns
        violent_patterns_found = self._detect_violent_patterns(letter_text, language)

        # Extract facts vs judgments
        observations = self._extract_observations(letter_text, language)

        # Identify feelings
        feelings = self._identify_feelings(letter_text, language)

        # Infer underlying needs
        needs = self._infer_needs(letter_text, language, violent_patterns_found)

        # Formulate request
        request = self._formulate_request(letter_text, language, recipient)

        # Generate NVC-transformed text
        transformed_text = self._generate_nvc_text(
            observations,
            feelings,
            needs,
            request,
            language
        )

        logger.info(
            "nvc_transformation_complete",
            violent_patterns_count=len(violent_patterns_found),
            needs_identified=len(needs)
        )

        return {
            "original_text": letter_text,
            "transformed_text": transformed_text,
            "violent_patterns_detected": violent_patterns_found,
            "nvc_structure": NVCStructure(
                observation="; ".join(observations) if observations else "Когда происходит ситуация с ребенком",
                feeling=", ".join(feelings) if feelings else "я чувствую беспокойство",
                need=", ".join(needs) if needs else "потому что мне важна связь с ребенком",
                request=request if request else "Был бы благодарен обсудить это"
            ),
            "tips": self._generate_transformation_tips(violent_patterns_found, language)
        }

    def _detect_violent_patterns(self, text: str, language: str) -> List[str]:
        """Detect violent communication patterns."""
        text_lower = text.lower()
        detected = []

        patterns = self.violent_patterns.get(language, self.violent_patterns["russian"])

        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(f"{category}: '{keyword}'")

        return detected

    def _extract_observations(self, text: str, language: str) -> List[str]:
        """Extract objective observations (facts without judgments)."""
        # Simplified: in production, would use NLP to separate facts from judgments
        observations = []

        # Look for time-based facts
        time_patterns = [
            r"когда.*",
            r"в последний раз.*",
            r"вчера.*",
            r"when.*",
            r"last time.*",
            r"yesterday.*"
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            observations.extend(matches[:2])  # Max 2

        if not observations:
            if language == "russian":
                observations = ["Когда я не вижу ребенка"]
            else:
                observations = ["When I don't see our child"]

        return observations

    def _identify_feelings(self, text: str, language: str) -> List[str]:
        """Identify genuine feelings (emotions, not thoughts)."""
        text_lower = text.lower()
        identified_feelings = []

        feeling_words = self.feeling_words.get(language, self.feeling_words["russian"])

        # Check for unpleasant feelings (more common in conflict)
        for feeling in feeling_words["unpleasant"]:
            if feeling in text_lower:
                identified_feelings.append(feeling)

        # If no feelings found, infer from context
        if not identified_feelings:
            # Check for emotion keywords
            if any(word in text_lower for word in ["злюсь", "гнев", "angry", "rage"]):
                identified_feelings.append("раздражен" if language == "russian" else "frustrated")
            elif any(word in text_lower for word in ["грустно", "больно", "sad", "hurt"]):
                identified_feelings.append("грустен" if language == "russian" else "sad")
            else:
                identified_feelings.append("обеспокоен" if language == "russian" else "concerned")

        return identified_feelings[:3]  # Max 3 feelings

    def _infer_needs(self, text: str, language: str, violent_patterns: List[str]) -> List[str]:
        """Infer underlying universal needs."""
        text_lower = text.lower()
        needs = []

        # Map common patterns to needs
        need_map = {
            "russian": {
                "ребенок": "connection",
                "видеть": "connection",
                "общение": "connection",
                "понимание": "connection",
                "справедливость": "integrity",
                "уважение": "connection"
            },
            "english": {
                "child": "connection",
                "see": "connection",
                "communication": "connection",
                "understanding": "connection",
                "fairness": "integrity",
                "respect": "connection"
            }
        }

        universal_needs = self.universal_needs.get(language, self.universal_needs["russian"])

        # Find needs from text
        for keyword, need_category in need_map.get(language, need_map["russian"]).items():
            if keyword in text_lower:
                category_needs = universal_needs[need_category]
                if category_needs:
                    needs.append(category_needs[0])  # First need from category

        # Remove duplicates
        needs = list(dict.fromkeys(needs))

        # If no needs found, default to connection (most common in PA)
        if not needs:
            needs = [universal_needs["connection"][0]]  # "любовь" or "love"

        return needs[:2]  # Max 2 needs

    def _formulate_request(self, text: str, language: str, recipient: str) -> str:
        """Formulate clear, positive, actionable request."""
        # Different requests for different recipients
        if language == "russian":
            if recipient == "ex-partner":
                return "Был бы благодарен, если бы мы могли обсудить возможность моего общения с ребенком"
            elif recipient == "child":
                return "Был бы рад узнать, как у тебя дела, когда ты будешь готов"
            else:
                return "Был бы благодарен за вашу помощь в этой ситуации"
        else:
            if recipient == "ex-partner":
                return "Would you be willing to discuss the possibility of my communication with our child"
            elif recipient == "child":
                return "I would love to hear how you're doing, when you're ready"
            else:
                return "I would appreciate your help in this situation"

    def _generate_nvc_text(
        self,
        observations: List[str],
        feelings: List[str],
        needs: List[str],
        request: str,
        language: str
    ) -> str:
        """Generate transformed NVC text."""
        if language == "russian":
            template = """
**Наблюдение (факты без оценок):**
{observations}

**Чувства:**
Я чувствую {feelings}

**Потребности:**
Потому что мне важны {needs}

**Просьба:**
{request}
"""
        else:
            template = """
**Observation (facts without judgments):**
{observations}

**Feelings:**
I feel {feelings}

**Needs:**
Because I value {needs}

**Request:**
{request}
"""

        return template.format(
            observations=observations[0] if observations else "...",
            feelings=", ".join(feelings) if feelings else "...",
            needs=", ".join(needs) if needs else "...",
            request=request
        ).strip()

    def _generate_transformation_tips(self, violent_patterns: List[str], language: str) -> List[str]:
        """Generate tips for improvement."""
        tips = []

        if violent_patterns:
            if language == "russian":
                tips.append("🔴 Обнаружены паттерны ненасильственной коммуникации. Замените 'ты' на 'я' утверждения.")
                tips.append("💡 Сфокусируйтесь на своих чувствах и потребностях, а не на действиях другого.")
            else:
                tips.append("🔴 Violent communication patterns detected. Replace 'you' statements with 'I' statements.")
                tips.append("💡 Focus on your feelings and needs, not the other person's actions.")

        if language == "russian":
            tips.append("✅ Используйте конкретные наблюдения вместо обобщений.")
            tips.append("✅ Формулируйте просьбу, а не требование.")
        else:
            tips.append("✅ Use specific observations instead of generalizations.")
            tips.append("✅ Frame a request, not a demand.")

        return tips
