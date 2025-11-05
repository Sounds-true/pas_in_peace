"""Intent classification for PA bot messages."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from src.core.logger import get_logger


logger = get_logger(__name__)


class Intent(str, Enum):
    """User intent types."""
    CRISIS = "crisis"  # Urgent help, suicidal thoughts
    EMOTIONAL_SUPPORT = "emotional_support"  # Need to talk, feeling overwhelmed
    QUESTION = "question"  # Asking for information about PA
    LETTER_WRITING = "letter_writing"  # Help with writing letters
    GOAL_SETTING = "goal_setting"  # Setting or tracking goals
    TECHNIQUE_REQUEST = "technique_request"  # Asking for coping techniques

    # Legal Tools (Sprint 4)
    CONTACT_DIARY = "contact_diary"  # Court-admissible contact documentation
    BIFF_HELP = "biff_help"  # High-conflict communication help
    MEDIATION_PREP = "mediation_prep"  # Mediation preparation
    PARENTING_MODEL = "parenting_model"  # Co-parenting vs Parallel parenting

    GRATITUDE = "gratitude"  # Saying thanks, positive feedback
    GREETING = "greeting"  # Hello, starting conversation
    FAREWELL = "farewell"  # Goodbye, ending conversation
    UNKNOWN = "unknown"  # Can't determine intent


@dataclass
class IntentResult:
    """Intent classification result."""
    intent: Intent
    confidence: float
    secondary_intents: List[Tuple[Intent, float]] = None  # Other possible intents
    keywords: List[str] = None  # Keywords that triggered this intent

    def __post_init__(self):
        if self.secondary_intents is None:
            self.secondary_intents = []
        if self.keywords is None:
            self.keywords = []


class IntentClassifier:
    """
    Classify user intent from message text.

    Uses pattern matching and keyword detection for Russian language.
    Can be extended with ML models in future.
    """

    def __init__(self):
        """Initialize intent classifier."""
        self.initialized = False

        # Intent patterns: each intent has keywords and patterns
        self.intent_patterns = {
            Intent.CRISIS: {
                'keywords': [
                    'хочу умереть', 'покончить с собой', 'суицид', 'самоубийство',
                    'не могу больше', 'нет смысла жить', 'конец', 'последний раз',
                    'прощай навсегда', 'устал жить'
                ],
                'patterns': [
                    r'не\s+вижу\s+смысла',
                    r'лучше\s+(?:бы\s+)?умереть',
                    r'не\s+хочу\s+жить',
                ],
                'weight': 1.0  # Highest priority
            },

            Intent.EMOTIONAL_SUPPORT: {
                'keywords': [
                    'плохо', 'больно', 'страдаю', 'переживаю', 'тяжело',
                    'не справляюсь', 'устал', 'одиноко', 'отчаяние',
                    'тревожно', 'панику', 'страшно', 'разрываюсь'
                ],
                'patterns': [
                    r'мне\s+(?:так\s+)?(?:плохо|тяжело|больно)',
                    r'не\s+могу\s+(?:справиться|вынести)',
                    r'(?:чувствую|ощущаю)\s+(?:боль|тревогу|страх)',
                ],
                'weight': 0.9
            },

            Intent.QUESTION: {
                'keywords': [
                    'что такое', 'как', 'почему', 'когда', 'где',
                    'объясни', 'расскажи', 'подскажи', 'можно ли',
                    'правда ли', 'это нормально'
                ],
                'patterns': [
                    r'^(?:что|как|почему|когда|где)\b',
                    r'\bможно\s+ли\b',
                    r'\bправда\s+(?:ли|что)\b',
                    r'\?$',  # Ends with question mark
                ],
                'weight': 0.7
            },

            Intent.LETTER_WRITING: {
                'keywords': [
                    'письмо', 'написать', 'ответить', 'сообщение',
                    'email', 'текст', 'формулировка', 'как сказать',
                    'хочу написать', 'помоги написать'
                ],
                'patterns': [
                    r'напиш\w+\s+письмо',
                    r'помо\w+\s+(?:с\s+)?письм',
                    r'как\s+(?:мне\s+)?(?:написать|ответить|сказать)',
                    r'формулиров\w+',
                ],
                'weight': 0.8
            },

            Intent.GOAL_SETTING: {
                'keywords': [
                    'цель', 'план', 'хочу', 'буду', 'планирую',
                    'намерен', 'собираюсь', 'поставить цель',
                    'достичь', 'добиться'
                ],
                'patterns': [
                    r'(?:хочу|буду|планирую|собираюсь)\s+\w+',
                    r'(?:моя|новая)\s+цель',
                    r'поставить\s+цель',
                    r'к\s+\d+\s+(?:января|февраля|марта|дню|числу)',  # Date-bound goals
                ],
                'weight': 0.75
            },

            Intent.TECHNIQUE_REQUEST: {
                'keywords': [
                    'техника', 'упражнение', 'практика', 'метод',
                    'как справиться', 'что делать', 'помоги успокоиться',
                    'совет', 'рекомендация'
                ],
                'patterns': [
                    r'что\s+(?:мне\s+)?делать',
                    r'как\s+(?:мне\s+)?(?:справиться|успокоиться)',
                    r'дай\s+(?:совет|рекомендацию)',
                    r'какие?\s+(?:техники|упражнения|методы)',
                ],
                'weight': 0.8
            },

            Intent.GRATITUDE: {
                'keywords': [
                    'спасибо', 'благодарю', 'благодарен', 'помогло',
                    'ценю', 'признателен', 'лучше стало'
                ],
                'patterns': [
                    r'спасибо\b',
                    r'благодар\w+',
                    r'мне\s+помогло',
                    r'стало\s+лучше',
                ],
                'weight': 0.6
            },

            Intent.GREETING: {
                'keywords': [
                    'привет', 'здравствуй', 'добрый день', 'доброе утро',
                    'добрый вечер', 'здравия', 'приветствую'
                ],
                'patterns': [
                    r'^(?:привет|здравствуй|добр)',
                    r'добр\w+\s+(?:день|утро|вечер)',
                ],
                'weight': 0.5
            },

            Intent.FAREWELL: {
                'keywords': [
                    'пока', 'до свидания', 'прощай', 'увидимся',
                    'всего доброго', 'до встречи', 'досвидания'
                ],
                'patterns': [
                    r'^(?:пока|прощай|до\s+свидания)',
                    r'всего\s+(?:доброго|хорошего)',
                ],
                'weight': 0.5
            },

            # Legal Tools (Sprint 4)
            Intent.CONTACT_DIARY: {
                'keywords': [
                    'дневник', 'документировать', 'записать встречу', 'контакт с ребенком',
                    'для суда', 'доказательство', 'фиксировать', 'запись контактов',
                    'court diary', 'document contact', 'log visit'
                ],
                'patterns': [
                    r'(?:вести|создать|начать)\s+дневник',
                    r'(?:записать|документировать)\s+(?:встречу|контакт)',
                    r'для\s+суд',
                    r'(?:нужно|хочу)\s+фиксировать',
                ],
                'weight': 0.8
            },

            Intent.BIFF_HELP: {
                'keywords': [
                    'biff', 'конфликтный', 'ответить', 'как написать', 'агрессивное сообщение',
                    'высококонфликтный', 'провокация', 'нейтрально ответить',
                    'не эскалировать', 'деловое общение'
                ],
                'patterns': [
                    r'как\s+(?:ответить|написать)\s+(?:на|бывш|ex)',
                    r'(?:конфликтн|агрессивн)\w+\s+(?:сообщение|письмо)',
                    r'(?:не\s+)?эскалиров',
                    r'деловое?\s+общение',
                    r'нейтральн\w+\s+ответ',
                ],
                'weight': 0.8
            },

            Intent.MEDIATION_PREP: {
                'keywords': [
                    'медиация', 'посредник', 'переговоры', 'подготовка к медиации',
                    'mediator', 'mediation', 'соглашение', 'готовиться к встрече',
                    'семейный посредник'
                ],
                'patterns': [
                    r'подготов\w+\s+к\s+(?:медиац|переговор)',
                    r'(?:идти|иду|пойду)\s+(?:на\s+)?медиац',
                    r'как\s+(?:подготовиться|готовиться)',
                    r'что\s+(?:нужно|взять|подготовить)\s+(?:для|на)\s+медиац',
                ],
                'weight': 0.85
            },

            Intent.PARENTING_MODEL: {
                'keywords': [
                    'co-parenting', 'parallel parenting', 'совместное воспитание',
                    'параллельное воспитание', 'модель воспитания', 'как общаться',
                    'минимизировать контакт', 'сотрудничество', 'высокий конфликт'
                ],
                'patterns': [
                    r'(?:совместн|параллельн)\w+\s+воспитан',
                    r'(?:co-?parenting|parallel\s+parenting)',
                    r'как\s+(?:лучше\s+)?(?:воспитывать|общаться)\s+(?:после|при)',
                    r'(?:модель|стиль)\s+воспитан',
                    r'(?:какую|какой)\s+(?:модель|систему)\s+(?:выбрать|использовать)',
                ],
                'weight': 0.8
            },
        }

    async def initialize(self) -> None:
        """Initialize classifier."""
        if self.initialized:
            return

        # Compile regex patterns for efficiency
        for intent, config in self.intent_patterns.items():
            config['compiled_patterns'] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in config['patterns']
            ]

        self.initialized = True
        logger.info("intent_classifier_initialized")

    async def classify(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentResult:
        """
        Classify user intent from message text.

        Args:
            text: User message
            context: Optional conversation context for better classification

        Returns:
            IntentResult with primary and secondary intents
        """
        if not self.initialized:
            await self.initialize()

        text_lower = text.lower()
        scores = {}  # intent -> score
        matched_keywords = {}  # intent -> list of matched keywords

        # Score each intent
        for intent, config in self.intent_patterns.items():
            score = 0.0
            keywords = []

            # Check keywords
            for keyword in config['keywords']:
                if keyword in text_lower:
                    score += 1.0
                    keywords.append(keyword)

            # Check patterns
            for pattern in config['compiled_patterns']:
                if pattern.search(text_lower):
                    score += 2.0  # Patterns are more reliable than keywords

            # Apply intent weight
            score *= config['weight']

            if score > 0:
                scores[intent] = score
                matched_keywords[intent] = keywords

        # Context-based boosting
        if context:
            scores = self._apply_context_boost(scores, context)

        # Find primary intent
        if not scores:
            return IntentResult(
                intent=Intent.UNKNOWN,
                confidence=0.0
            )

        # Sort by score
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_intent, primary_score = sorted_intents[0]

        # Normalize confidence (0-1)
        max_possible_score = 10.0  # Rough estimate
        confidence = min(primary_score / max_possible_score, 1.0)

        # Get secondary intents (within 70% of primary score)
        secondary = [
            (intent, min(score / max_possible_score, 1.0))
            for intent, score in sorted_intents[1:]
            if score >= primary_score * 0.7
        ]

        return IntentResult(
            intent=primary_intent,
            confidence=confidence,
            secondary_intents=secondary,
            keywords=matched_keywords.get(primary_intent, [])
        )

    def _apply_context_boost(
        self,
        scores: Dict[Intent, float],
        context: Dict[str, Any]
    ) -> Dict[Intent, float]:
        """Apply context-based score boosting."""
        boosted = scores.copy()

        # If user was in crisis recently, boost crisis intent
        if context.get('recent_crisis', False):
            if Intent.CRISIS in boosted:
                boosted[Intent.CRISIS] *= 1.5

        # If in letter writing flow, boost letter intent
        if context.get('writing_letter', False):
            if Intent.LETTER_WRITING in boosted:
                boosted[Intent.LETTER_WRITING] *= 1.3

        # If in goal tracking flow, boost goal intent
        if context.get('tracking_goals', False):
            if Intent.GOAL_SETTING in boosted:
                boosted[Intent.GOAL_SETTING] *= 1.3

        return boosted

    async def classify_batch(
        self,
        messages: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[IntentResult]:
        """Classify multiple messages."""
        return [await self.classify(msg, context) for msg in messages]

    def get_intent_description(self, intent: Intent) -> str:
        """Get human-readable description of intent."""
        descriptions = {
            Intent.CRISIS: "Кризисная ситуация, нужна срочная помощь",
            Intent.EMOTIONAL_SUPPORT: "Эмоциональная поддержка",
            Intent.QUESTION: "Вопрос об отчуждении родителей",
            Intent.LETTER_WRITING: "Помощь с написанием письма",
            Intent.GOAL_SETTING: "Постановка или отслеживание целей",
            Intent.TECHNIQUE_REQUEST: "Запрос терапевтической техники",

            # Legal Tools
            Intent.CONTACT_DIARY: "Ведение дневника контактов для суда",
            Intent.BIFF_HELP: "Помощь с BIFF коммуникацией",
            Intent.MEDIATION_PREP: "Подготовка к медиации",
            Intent.PARENTING_MODEL: "Выбор модели воспитания (co-parenting/parallel)",

            Intent.GRATITUDE: "Благодарность",
            Intent.GREETING: "Приветствие",
            Intent.FAREWELL: "Прощание",
            Intent.UNKNOWN: "Неясное намерение"
        }
        return descriptions.get(intent, "")
