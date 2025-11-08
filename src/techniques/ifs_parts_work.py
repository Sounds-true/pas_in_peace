"""Internal Family Systems (IFS) - Parts Work for emotional processing."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from src.techniques.base import Technique, TechniqueResult, TechniqueCategory, DistressLevel
from src.core.logger import get_logger


logger = get_logger(__name__)


class PartType(Enum):
    """Types of parts in IFS model."""
    MANAGER = "manager"  # Proactive protectors
    FIREFIGHTER = "firefighter"  # Reactive protectors
    EXILE = "exile"  # Wounded, vulnerable parts
    SELF = "self"  # Core, compassionate self


@dataclass
class IdentifiedPart:
    """An identified part of the psyche."""
    part_type: PartType
    name: str
    emotion: str
    protective_intent: str  # What it's trying to protect
    underlying_fear: str  # What it's afraid of
    confidence: float  # 0-1


class IFSPartsWork(Technique):
    """
    Internal Family Systems (IFS) Parts Work.

    Core concepts:
    - Everyone has multiple "parts" (sub-personalities)
    - Parts have positive intentions (even destructive ones)
    - Accessing "Self" (core compassionate awareness) heals parts
    - Key process: Identify → Understand intent → Compassion → Unburdening

    Particularly useful for:
    - Anger management ("What part of you feels angry?")
    - Internal conflict ("Part of me wants X, part wants Y")
    - Self-criticism ("Which part is being critical?")

    References:
    - Richard Schwartz (1995) - Internal Family Systems Therapy
    - Schwartz & Sweezy (2020) - Internal Family Systems Therapy 2nd Edition
    """

    def __init__(self):
        """Initialize IFS technique."""
        super().__init__()
        self.name = "Internal Family Systems (IFS)"
        self.category = TechniqueCategory.EMOTION_REGULATION
        self.description = "Work with different parts of self to resolve internal conflicts"
        self.suitable_for_distress = [
            DistressLevel.MODERATE,
            DistressLevel.HIGH
        ]

        # Part identification patterns
        self.part_indicators = {
            "russian": {
                "manager": ["должен", "обязан", "нужно", "контролировать", "планировать"],
                "firefighter": ["хочется кричать", "убить", "разрушить", "сорваться", "взорваться"],
                "exile": ["боюсь", "страшно", "больно", "одиноко", "брошен", "не нужен"]
            },
            "english": {
                "manager": ["should", "must", "have to", "control", "plan"],
                "firefighter": ["want to scream", "kill", "destroy", "lash out", "explode"],
                "exile": ["afraid", "scared", "hurt", "lonely", "abandoned", "unwanted"]
            }
        }

        # Questions to explore parts
        self.exploration_questions = {
            "russian": [
                "Какая часть вас сейчас говорит?",
                "Что эта часть пытается защитить?",
                "Чего она боится?",
                "Что произойдет, если она перестанет это делать?",
                "Как вы чувствуете себя по отношению к этой части?",
                "Что эта часть хочет, чтобы вы знали?",
                "Сколько лет этой части? (метафорически)",
                "Где в теле вы чувствуете эту часть?"
            ],
            "english": [
                "Which part of you is speaking right now?",
                "What is this part trying to protect?",
                "What is it afraid of?",
                "What would happen if it stopped doing this?",
                "How do you feel toward this part?",
                "What does this part want you to know?",
                "How old is this part? (metaphorically)",
                "Where in your body do you feel this part?"
            ]
        }

    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """
        Apply IFS parts work.

        Flow:
        1. Identify the active part
        2. Ask about its protective intent
        3. Explore underlying fear
        4. Access Self-energy (compassion)
        5. Dialogue with the part

        Args:
            user_message: User's message
            context: Emotional state, situation

        Returns:
            TechniqueResult with IFS response
        """
        # Identify which part is active
        identified_part = self._identify_part(user_message, context)

        # Generate IFS response based on identified part
        if identified_part:
            response = await self._dialogue_with_part(
                identified_part,
                user_message,
                context
            )
        else:
            # Start parts identification
            response = self._initiate_parts_work(user_message, context)

        logger.info(
            "ifs_applied",
            part_identified=identified_part.name if identified_part else "unknown",
            part_type=identified_part.part_type.value if identified_part else "unknown"
        )

        return TechniqueResult(
            success=True,
            response=response,
            follow_up=None,
            recommended_next_step="continue_parts_dialogue",
            metadata={
                "part_identified": identified_part.name if identified_part else None,
                "part_type": identified_part.part_type.value if identified_part else None,
                "protective_intent": identified_part.protective_intent if identified_part else None
            }
        )

    def _identify_part(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Optional[IdentifiedPart]:
        """
        Identify which part is speaking.

        Heuristics:
        - Anger/rage → Firefighter
        - "Should/must" → Manager
        - Fear/vulnerability → Exile
        """
        text_lower = text.lower()
        language = context.get("language", "russian")
        emotion = context.get("emotion", "neutral")

        # Check for firefighter (reactive protector)
        firefighter_patterns = self.part_indicators[language]["firefighter"]
        if any(pattern in text_lower for pattern in firefighter_patterns):
            return IdentifiedPart(
                part_type=PartType.FIREFIGHTER,
                name="Защитник-Огнетушитель" if language == "russian" else "Firefighter Protector",
                emotion="rage/anger",
                protective_intent="Защищает от боли через гнев" if language == "russian" else "Protects from pain through anger",
                underlying_fear="Быть беспомощным и уязвимым" if language == "russian" else "Being helpless and vulnerable",
                confidence=0.8
            )

        # Check for manager (proactive protector)
        manager_patterns = self.part_indicators[language]["manager"]
        if any(pattern in text_lower for pattern in manager_patterns):
            return IdentifiedPart(
                part_type=PartType.MANAGER,
                name="Менеджер" if language == "russian" else "Manager",
                emotion="anxiety/control",
                protective_intent="Контролирует ситуацию, чтобы избежать боли" if language == "russian" else "Controls situation to avoid pain",
                underlying_fear="Потеря контроля" if language == "russian" else "Loss of control",
                confidence=0.7
            )

        # Check for exile (wounded part)
        exile_patterns = self.part_indicators[language]["exile"]
        if any(pattern in text_lower for pattern in exile_patterns):
            return IdentifiedPart(
                part_type=PartType.EXILE,
                name="Раненая часть" if language == "russian" else "Wounded Part",
                emotion="fear/sadness",
                protective_intent="Нуждается в утешении и защите" if language == "russian" else "Needs comfort and protection",
                underlying_fear="Быть отвергнутым снова" if language == "russian" else "Being rejected again",
                confidence=0.75
            )

        # Check emotion from context
        if emotion in ["anger", "rage"]:
            return IdentifiedPart(
                part_type=PartType.FIREFIGHTER,
                name="Гневная часть" if language == "russian" else "Angry Part",
                emotion=emotion,
                protective_intent="Защита через выражение гнева" if language == "russian" else "Protection through anger expression",
                underlying_fear="Глубокая боль под гневом" if language == "russian" else "Deep pain beneath anger",
                confidence=0.6
            )

        return None

    async def _dialogue_with_part(
        self,
        part: IdentifiedPart,
        user_message: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate dialogue with the identified part.

        IFS steps:
        1. Notice the part
        2. Curiosity about its intent
        3. Compassion for its burden
        4. Dialogue to understand
        """
        language = context.get("language", "russian")

        # Build response based on part type
        if part.part_type == PartType.FIREFIGHTER:
            response = self._dialogue_firefighter(part, language)
        elif part.part_type == PartType.MANAGER:
            response = self._dialogue_manager(part, language)
        elif part.part_type == PartType.EXILE:
            response = self._dialogue_exile(part, language)
        else:
            response = self._generic_parts_dialogue(part, language)

        return response

    def _dialogue_firefighter(self, part: IdentifiedPart, language: str) -> str:
        """Dialogue with firefighter part (reactive protector)."""
        if language == "russian":
            return f"""Я замечаю, что сейчас активна часть вас, которая чувствует сильный гнев.

Давайте остановимся на минуту и спросим у этой части: **что она пытается защитить?**

Часто гнев - это защитник, который прикрывает что-то более уязвимое внутри. Возможно, под гневом есть боль, страх или чувство бессилия.

Вы можете спросить у этой гневной части: "Чего ты боишься? Что произойдет, если ты перестанешь злиться?"

Что она отвечает?"""
        else:
            return f"""I notice that a part of you feeling strong anger is active right now.

Let's pause for a moment and ask this part: **what is it trying to protect?**

Often anger is a protector covering something more vulnerable inside. Perhaps beneath the anger there's pain, fear, or a sense of helplessness.

You can ask this angry part: "What are you afraid of? What would happen if you stopped being angry?"

What does it answer?"""

    def _dialogue_manager(self, part: IdentifiedPart, language: str) -> str:
        """Dialogue with manager part (proactive protector)."""
        if language == "russian":
            return f"""Я слышу часть вас, которая пытается все контролировать и держать под контролем.

Эта часть работает очень усердно, чтобы защитить вас. Но она, вероятно, устала.

Попробуйте спросить у нее с любопытством:
- "Что ты пытаешься предотвратить?"
- "Чего ты боишься, что произойдет, если ты расслабишься?"

Часто менеджер боится, что если он перестанет контролировать, всплывет невыносимая боль.

Можете ли вы поблагодарить эту часть за ее работу и спросить: "Что тебе нужно от меня?\""""
        else:
            return f"""I hear a part of you that's trying to control and manage everything.

This part works very hard to protect you. But it's probably exhausted.

Try asking it with curiosity:
- "What are you trying to prevent?"
- "What are you afraid will happen if you relax?"

Often the manager fears that if it stops controlling, unbearable pain will surface.

Can you thank this part for its work and ask: "What do you need from me?\""""

    def _dialogue_exile(self, part: IdentifiedPart, language: str) -> str:
        """Dialogue with exile (wounded part)."""
        if language == "russian":
            return f"""Я чувствую, что сейчас говорит очень уязвимая, раненая часть вас.

Эта часть несет боль, возможно, из прошлого. Она нуждается в сочувствии и защите.

Можете ли вы представить, что обнимаете эту часть с любовью? Скажите ей:

"Я вижу твою боль. Я здесь с тобой. Ты в безопасности со мной."

Эта часть, вероятно, долго пряталась. Что она хочет, чтобы вы знали?

Иногда помогает спросить: "Сколько тебе лет?" (метафорически). Это часто показывает, когда возникла эта рана."""
        else:
            return f"""I sense that a very vulnerable, wounded part of you is speaking now.

This part carries pain, perhaps from the past. It needs compassion and protection.

Can you imagine embracing this part with love? Tell it:

"I see your pain. I'm here with you. You're safe with me."

This part has probably been hiding for a long time. What does it want you to know?

Sometimes it helps to ask: "How old are you?" (metaphorically). This often shows when this wound was created."""

    def _generic_parts_dialogue(self, part: IdentifiedPart, language: str) -> str:
        """Generic parts dialogue."""
        if language == "russian":
            return f"""Я замечаю, что сейчас активна определенная часть вас.

Давайте познакомимся с ней поближе:

1. **Какая это часть?** Как бы вы ее назвали?
2. **Что она чувствует?** (гнев, страх, грусть...)
3. **Что она пытается сделать для вас?** (защитить, предупредить, контролировать...)
4. **Чего она боится?** Что произойдет, если она перестанет это делать?

Подойдите к этой части с любопытством, а не с осуждением. Каждая часть имеет позитивное намерение, даже если ее методы проблематичны.

Что вы узнаете, когда задаете эти вопросы?"""
        else:
            return f"""I notice that a specific part of you is active right now.

Let's get to know it better:

1. **What part is this?** How would you name it?
2. **What does it feel?** (anger, fear, sadness...)
3. **What is it trying to do for you?** (protect, warn, control...)
4. **What is it afraid of?** What would happen if it stopped doing this?

Approach this part with curiosity, not judgment. Every part has a positive intention, even if its methods are problematic.

What do you learn when you ask these questions?"""

    def _initiate_parts_work(self, user_message: str, context: Dict[str, Any]) -> str:
        """Initiate parts work when no clear part identified."""
        language = context.get("language", "russian")

        if language == "russian":
            return """Я слышу, что вы переживаете сложные чувства.

Попробуем подход Internal Family Systems: представьте, что разные части вас имеют разные мнения или чувства.

Например:
- Часть, которая злится
- Часть, которая боится
- Часть, которая хочет все контролировать

**Какая часть вас сейчас говорит?** Как бы вы ее назвали?

Это может показаться странным, но попробуйте отнестись к этому с любопытством."""
        else:
            return """I hear that you're experiencing complex feelings.

Let's try an Internal Family Systems approach: imagine that different parts of you have different opinions or feelings.

For example:
- A part that's angry
- A part that's afraid
- A part that wants to control everything

**Which part of you is speaking right now?** How would you name it?

This might seem strange, but try approaching it with curiosity."""

    def is_appropriate(
        self,
        distress_level: DistressLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """IFS requires some emotional regulation capacity."""
        # Not appropriate for crisis
        if distress_level == DistressLevel.CRISIS:
            return False

        # Check if user has some self-awareness
        # (In production, would check user's therapy readiness)
        return super().is_appropriate(distress_level, context)
