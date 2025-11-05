"""Motivational Interviewing (MI) techniques with OARS framework."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import random

from src.techniques.base import Technique, TechniqueResult, TechniqueCategory, DistressLevel
from src.core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class OARSResult:
    """Result of OARS technique application."""
    technique_used: str  # "open_question", "affirmation", "reflection", "summary"
    response: str
    change_talk_detected: bool
    ambivalence_level: float  # 0-1
    next_recommended: str


class MotivationalInterviewing(Technique):
    """
    Motivational Interviewing using OARS framework.

    OARS = Open questions, Affirmations, Reflections, Summaries

    Core principles:
    - Express empathy through reflective listening
    - Develop discrepancy between current behavior and goals
    - Roll with resistance (avoid argumentation)
    - Support self-efficacy and optimism

    References:
    - Miller & Rollnick (2013) - Motivational Interviewing 3rd Edition
    - SAMHSA TIP 35 - Enhancing Motivation for Change
    """

    def __init__(self):
        """Initialize MI technique."""
        super().__init__()
        self.name = "Motivational Interviewing"
        self.category = TechniqueCategory.ACTIVE_LISTENING
        self.description = "Client-centered counseling style for eliciting behavior change"
        self.suitable_for_distress = [
            DistressLevel.LOW,
            DistressLevel.MODERATE,
            DistressLevel.HIGH
        ]

        # OARS components patterns
        self.open_question_stems = {
            "russian": [
                "Что для вас важнее всего в этой ситуации?",
                "Как вы видите свою жизнь через год, если ситуация изменится?",
                "Расскажите подробнее о том, что вы чувствуете...",
                "Что было бы для вас хорошим результатом?",
                "Как вы понимаете, что готовы к изменениям?",
                "Что мешает вам сделать первый шаг?",
                "Как ваш ребенок может выиграть от ваших изменений?",
                "Что вы уже пробовали? Что работало?",
                "Как бы выглядел идеальный день для вас?",
                "Что дает вам силы продолжать?"
            ],
            "english": [
                "What matters most to you in this situation?",
                "How do you see your life a year from now if things change?",
                "Tell me more about what you're feeling...",
                "What would be a good outcome for you?",
                "How do you know you're ready for change?",
                "What's holding you back from taking the first step?",
                "How might your child benefit from these changes?",
                "What have you already tried? What worked?",
                "What would an ideal day look like for you?",
                "What gives you strength to continue?"
            ]
        }

        # Change talk indicators
        self.change_talk_keywords = {
            "russian": [
                "хочу", "нужно", "должен", "попробую", "планирую",
                "готов", "могу", "буду", "изменю", "сделаю"
            ],
            "english": [
                "want to", "need to", "should", "will try", "planning to",
                "ready to", "can", "will", "change", "do"
            ]
        }

        # Sustain talk (resistance) indicators
        self.sustain_talk_keywords = {
            "russian": [
                "не могу", "не получится", "невозможно", "бесполезно",
                "не хочу", "не буду", "слишком сложно"
            ],
            "english": [
                "can't", "won't work", "impossible", "pointless",
                "don't want to", "won't", "too difficult"
            ]
        }

    async def apply(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> TechniqueResult:
        """
        Apply MI using appropriate OARS technique.

        Flow:
        1. Detect change talk vs sustain talk
        2. Select appropriate OARS response
        3. Generate empathic, non-judgmental response
        4. Recommend next step

        Args:
            user_message: User's message
            context: Emotional state, ambivalence, etc.

        Returns:
            TechniqueResult with MI response
        """
        # Analyze message for change/sustain talk
        change_talk = self._detect_change_talk(user_message)
        ambivalence = self._assess_ambivalence(user_message, context)

        # Select OARS technique based on context
        oars_technique = self._select_oars_technique(
            user_message,
            change_talk,
            ambivalence,
            context
        )

        # Generate response
        oars_result = await self._apply_oars(
            oars_technique,
            user_message,
            context,
            change_talk,
            ambivalence
        )

        logger.info(
            "mi_applied",
            technique=oars_result.technique_used,
            change_talk=oars_result.change_talk_detected,
            ambivalence=oars_result.ambivalence_level
        )

        return TechniqueResult(
            success=True,
            response=oars_result.response,
            follow_up=None,
            recommended_next_step=oars_result.next_recommended,
            metadata={
                "oars_technique": oars_result.technique_used,
                "change_talk": oars_result.change_talk_detected,
                "ambivalence_level": oars_result.ambivalence_level
            }
        )

    def _detect_change_talk(self, text: str) -> bool:
        """Detect change talk (DARN-C: Desire, Ability, Reasons, Need, Commitment)."""
        text_lower = text.lower()

        # Check for change talk keywords
        for lang, keywords in self.change_talk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True

        return False

    def _assess_ambivalence(self, text: str, context: Dict[str, Any]) -> float:
        """
        Assess level of ambivalence (0 = clear, 1 = highly ambivalent).

        Ambivalence = wanting to change AND not wanting to change simultaneously.
        """
        text_lower = text.lower()

        change_count = 0
        sustain_count = 0

        # Count change talk
        for lang, keywords in self.change_talk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    change_count += 1

        # Count sustain talk
        for lang, keywords in self.sustain_talk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    sustain_count += 1

        # High ambivalence if both present
        if change_count > 0 and sustain_count > 0:
            return 0.7 + min(sustain_count / 10, 0.3)

        # Moderate ambivalence if only sustain talk
        if sustain_count > 0:
            return 0.5

        # Low ambivalence if change talk present
        if change_count > 0:
            return 0.2

        # Unclear
        return 0.4

    def _select_oars_technique(
        self,
        text: str,
        change_talk: bool,
        ambivalence: float,
        context: Dict[str, Any]
    ) -> str:
        """
        Select appropriate OARS technique.

        Strategy:
        - High ambivalence → Reflection (explore both sides)
        - Change talk → Affirmation (reinforce)
        - Sustain talk → Reflection (roll with resistance)
        - Unclear → Open question (explore)
        - Periodically → Summary (consolidate)
        """
        # Check if summary is due (every 3-4 exchanges)
        message_count = context.get("message_count", 0)
        if message_count > 0 and message_count % 4 == 0:
            return "summary"

        # High ambivalence → Reflection to explore both sides
        if ambivalence > 0.6:
            return "reflection"

        # Change talk detected → Affirmation
        if change_talk and ambivalence < 0.4:
            return "affirmation"

        # Sustain talk (resistance) → Reflective listening
        sustain_detected = any(
            keyword in text.lower()
            for keywords in self.sustain_talk_keywords.values()
            for keyword in keywords
        )
        if sustain_detected:
            return "reflection"

        # Default: Open question to explore
        return "open_question"

    async def _apply_oars(
        self,
        technique: str,
        user_message: str,
        context: Dict[str, Any],
        change_talk: bool,
        ambivalence: float
    ) -> OARSResult:
        """Apply specific OARS technique."""
        if technique == "open_question":
            return self._open_question(user_message, context)
        elif technique == "affirmation":
            return self._affirmation(user_message, context)
        elif technique == "reflection":
            return self._reflection(user_message, context, ambivalence)
        elif technique == "summary":
            return self._summary(user_message, context)
        else:
            return self._open_question(user_message, context)

    def _open_question(self, user_message: str, context: Dict[str, Any]) -> OARSResult:
        """Generate open-ended question to explore."""
        # Select appropriate question based on context
        language = context.get("language", "russian")
        questions = self.open_question_stems.get(language, self.open_question_stems["russian"])

        # Context-aware selection
        if "ребенок" in user_message.lower() or "child" in user_message.lower():
            # Focus on child-related questions
            child_questions = [q for q in questions if "ребенок" in q.lower() or "child" in q.lower()]
            question = random.choice(child_questions) if child_questions else random.choice(questions)
        else:
            question = random.choice(questions)

        return OARSResult(
            technique_used="open_question",
            response=question,
            change_talk_detected=False,
            ambivalence_level=0.5,
            next_recommended="reflection"
        )

    def _affirmation(self, user_message: str, context: Dict[str, Any]) -> OARSResult:
        """Generate affirmation to reinforce change talk."""
        # Identify what to affirm
        affirmations = {
            "russian": [
                "Я вижу, что вы готовы работать над изменениями. Это требует большой смелости.",
                "Вы уже сделали важный шаг, признав необходимость перемен.",
                "Ваше желание стать лучше для ребенка показывает вашу силу как родителя.",
                "Несмотря на все трудности, вы продолжаете двигаться вперед. Это впечатляет.",
                "Вы демонстрируете настоящую заботу о благополучии ребенка.",
                "То, что вы здесь и работаете над собой, уже большое достижение.",
                "Ваша готовность пробовать новые подходы говорит о вашей гибкости."
            ],
            "english": [
                "I see you're willing to work on changes. That takes great courage.",
                "You've already taken an important step by acknowledging the need for change.",
                "Your desire to be better for your child shows your strength as a parent.",
                "Despite all the difficulties, you keep moving forward. That's impressive.",
                "You're demonstrating real care for your child's well-being.",
                "Being here and working on yourself is already a major accomplishment.",
                "Your willingness to try new approaches shows your flexibility."
            ]
        }

        language = context.get("language", "russian")
        affirmation = random.choice(affirmations.get(language, affirmations["russian"]))

        return OARSResult(
            technique_used="affirmation",
            response=affirmation,
            change_talk_detected=True,
            ambivalence_level=0.3,
            next_recommended="open_question"
        )

    def _reflection(
        self,
        user_message: str,
        context: Dict[str, Any],
        ambivalence: float
    ) -> OARSResult:
        """
        Generate reflective listening response.

        Types of reflections:
        - Simple: Repeat or slightly rephrase
        - Complex: Add meaning or emotion
        - Double-sided: Reflect ambivalence
        """
        # For high ambivalence, use double-sided reflection
        if ambivalence > 0.6:
            response = self._double_sided_reflection(user_message, context)
        else:
            response = self._complex_reflection(user_message, context)

        return OARSResult(
            technique_used="reflection",
            response=response,
            change_talk_detected=False,
            ambivalence_level=ambivalence,
            next_recommended="open_question" if ambivalence > 0.5 else "affirmation"
        )

    def _double_sided_reflection(self, user_message: str, context: Dict[str, Any]) -> str:
        """Reflect both sides of ambivalence."""
        templates = {
            "russian": [
                "С одной стороны, вы {sustain}, но с другой стороны, вы также {change}.",
                "Я слышу, что часть вас {sustain}, и в то же время другая часть {change}.",
                "Вы чувствуете противоречие: {sustain}, но при этом {change}."
            ],
            "english": [
                "On one hand, you {sustain}, but on the other hand, you also {change}.",
                "I hear that part of you {sustain}, while another part {change}.",
                "You feel torn: {sustain}, yet you also {change}."
            ]
        }

        language = context.get("language", "russian")
        template = random.choice(templates.get(language, templates["russian"]))

        # Simplified: use generic placeholders
        # In production, would extract actual statements from user_message
        response = template.format(
            sustain="чувствуете, что это сложно" if language == "russian" else "feel it's difficult",
            change="хотите изменений" if language == "russian" else "want change"
        )

        return response

    def _complex_reflection(self, user_message: str, context: Dict[str, Any]) -> str:
        """Reflect with added emotional depth."""
        # Extract emotion from context
        emotion = context.get("emotion", "distress")

        emotion_reflections = {
            "russian": {
                "anger": "Я слышу, что вы испытываете сильный гнев из-за этой ситуации.",
                "despair": "Похоже, что вы чувствуете безнадежность и отчаяние.",
                "grief": "Я чувствую вашу глубокую боль и потерю.",
                "guilt": "Вы несете тяжелое бремя вины.",
                "default": "Я слышу, что это очень тяжело для вас."
            },
            "english": {
                "anger": "I hear that you're experiencing strong anger about this situation.",
                "despair": "It sounds like you're feeling hopeless and desperate.",
                "grief": "I sense your deep pain and loss.",
                "guilt": "You're carrying a heavy burden of guilt.",
                "default": "I hear that this is very difficult for you."
            }
        }

        language = context.get("language", "russian")
        emotion_map = emotion_reflections.get(language, emotion_reflections["russian"])
        response = emotion_map.get(emotion, emotion_map["default"])

        return response

    def _summary(self, user_message: str, context: Dict[str, Any]) -> OARSResult:
        """Generate summary of conversation so far."""
        # Simplified summary
        # In production, would use conversation history

        summaries = {
            "russian": [
                "Давайте подведем итог. Вы говорили о {topic1}, о {topic2}, и о том, что {change_talk}. Я правильно понимаю?",
                "Мы обсудили несколько важных моментов: {topic1}, {topic2}. Что из этого кажется вам наиболее важным для работы?"
            ],
            "english": [
                "Let's summarize. You've talked about {topic1}, about {topic2}, and that {change_talk}. Do I understand correctly?",
                "We've discussed several important points: {topic1}, {topic2}. What seems most important for you to work on?"
            ]
        }

        language = context.get("language", "russian")
        summary = random.choice(summaries.get(language, summaries["russian"]))

        # Generic placeholders
        summary = summary.format(
            topic1="ваши чувства" if language == "russian" else "your feelings",
            topic2="вашу ситуацию" if language == "russian" else "your situation",
            change_talk="хотите изменений" if language == "russian" else "want change"
        )

        return OARSResult(
            technique_used="summary",
            response=summary,
            change_talk_detected=False,
            ambivalence_level=0.4,
            next_recommended="open_question"
        )

    def is_appropriate(
        self,
        distress_level: DistressLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """MI is NOT appropriate for crisis situations."""
        if distress_level == DistressLevel.CRISIS:
            return False
        return super().is_appropriate(distress_level, context)
