"""
Mediation Preparation Module

Helps parents prepare for family mediation sessions by:
- Assessing readiness for mediation
- Organizing goals and priorities
- Preparing documentation
- Developing negotiation strategies
- Creating checklists

Mediation Context:
Family mediation is a voluntary, confidential process where a neutral
third party (mediator) helps parents reach agreements on custody,
parenting time, and related issues.

References:
- Association for Conflict Resolution (ACR) standards
- Family Mediation Canada best practices
- Academy of Professional Family Mediators guidelines

Author: pas_in_peace
License: MIT
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime


class MediationReadiness(Enum):
    """Parent's readiness level for mediation"""
    NOT_READY = "not_ready"  # High conflict, safety concerns
    NEEDS_PREP = "needs_preparation"  # Willing but unprepared
    READY = "ready"  # Prepared and willing
    WELL_PREPARED = "well_prepared"  # Excellent preparation


class MediationGoalCategory(Enum):
    """Categories of mediation goals"""
    CUSTODY_ARRANGEMENT = "custody_arrangement"
    PARENTING_TIME = "parenting_time"
    DECISION_MAKING = "decision_making"
    COMMUNICATION = "communication"
    FINANCIAL = "financial"
    RELOCATION = "relocation"
    HOLIDAY_SCHEDULE = "holiday_schedule"
    EXTRACURRICULAR = "extracurricular"
    OTHER = "other"


class Priority(Enum):
    """Priority levels for goals"""
    MUST_HAVE = "must_have"  # Non-negotiable
    HIGH_PRIORITY = "high_priority"  # Very important
    MEDIUM_PRIORITY = "medium_priority"  # Important but flexible
    LOW_PRIORITY = "low_priority"  # Nice to have


@dataclass
class MediationGoal:
    """Single mediation goal"""
    category: MediationGoalCategory
    priority: Priority
    description: str
    ideal_outcome: str
    acceptable_alternatives: List[str]
    dealbreakers: List[str]  # What you cannot accept
    rationale: str  # Why this matters (child-focused)


@dataclass
class ReadinessAssessment:
    """Assessment of parent's readiness for mediation"""
    readiness_level: MediationReadiness
    score: float  # 0-1
    strengths: List[str]
    areas_to_improve: List[str]
    recommendations: List[str]
    safety_concerns: List[str]
    red_flags: List[str]


class MediationReadinessAssessor:
    """
    Assesses parent's readiness for mediation

    Evaluates emotional readiness, preparation level, and safety factors
    """

    def assess_readiness(
        self,
        has_safety_concerns: bool,
        emotional_state: str,  # "stable", "distressed", "overwhelmed"
        goals_defined: bool,
        documents_organized: bool,
        understands_process: bool,
        willing_to_compromise: bool,
        can_communicate_calmly: bool,
        has_legal_counsel: bool = False,
        has_support_system: bool = False
    ) -> ReadinessAssessment:
        """
        Assess readiness for mediation

        Args:
            has_safety_concerns: Domestic violence or safety issues
            emotional_state: Current emotional state
            goals_defined: Has clear goals for mediation
            documents_organized: Has organized relevant documents
            understands_process: Understands mediation process
            willing_to_compromise: Willing to negotiate
            can_communicate_calmly: Can stay calm in discussions
            has_legal_counsel: Has consulted with lawyer
            has_support_system: Has emotional support

        Returns:
            ReadinessAssessment
        """
        strengths = []
        areas_to_improve = []
        recommendations = []
        safety_concerns = []
        red_flags = []

        # Calculate readiness score
        score = 0.0
        max_score = 7

        # Safety is paramount
        if has_safety_concerns:
            red_flags.append(
                "⚠️  SAFETY CONCERN: Медиация может быть небезопасна при "
                "наличии домашнего насилия. Проконсультируйтесь с юристом."
            )
            safety_concerns.append(
                "Рассмотрите челночную медиацию (shuttle mediation) или "
                "отложите медиацию до стабилизации ситуации."
            )
            score = 0
            readiness_level = MediationReadiness.NOT_READY
        else:
            # Emotional readiness
            if emotional_state == "stable":
                score += 1
                strengths.append("✓ Эмоционально стабильны")
            elif emotional_state == "distressed":
                score += 0.5
                areas_to_improve.append(
                    "Эмоциональное состояние: Рассмотрите терапию перед медиацией"
                )
            else:  # overwhelmed
                areas_to_improve.append(
                    "Эмоциональное состояние: Медиация может быть слишком сложной сейчас"
                )
                recommendations.append(
                    "Поработайте с терапевтом для стабилизации состояния"
                )

            # Goal definition
            if goals_defined:
                score += 1
                strengths.append("✓ Цели четко определены")
            else:
                areas_to_improve.append("Цели: Нужно определить приоритеты")
                recommendations.append(
                    "Используйте модуль постановки целей для подготовки"
                )

            # Document organization
            if documents_organized:
                score += 1
                strengths.append("✓ Документы организованы")
            else:
                areas_to_improve.append("Документы: Требуется организация")
                recommendations.append(
                    "Соберите: расписания, финансовые документы, "
                    "коммуникации с другим родителем"
                )

            # Process understanding
            if understands_process:
                score += 1
                strengths.append("✓ Понимаете процесс медиации")
            else:
                areas_to_improve.append("Понимание процесса: Требуется изучение")
                recommendations.append(
                    "Изучите: как работает медиация, роль медиатора, "
                    "ваши права и обязанности"
                )

            # Willingness to compromise
            if willing_to_compromise:
                score += 1
                strengths.append("✓ Готовы к компромиссам")
            else:
                areas_to_improve.append(
                    "Гибкость: Медиация требует готовности к компромиссам"
                )
                recommendations.append(
                    "Подумайте: что для вас действительно важно (must-have) "
                    "vs что можно обсудить"
                )
                red_flags.append(
                    "⚠️  Негибкая позиция может сделать медиацию неэффективной"
                )

            # Communication ability
            if can_communicate_calmly:
                score += 1
                strengths.append("✓ Можете общаться спокойно")
            else:
                areas_to_improve.append(
                    "Коммуникация: Сложность сохранять спокойствие"
                )
                recommendations.append(
                    "Практикуйте: техники заземления, BIFF коммуникацию, "
                    "тайм-ауты при эмоциях"
                )

            # Legal counsel (bonus)
            if has_legal_counsel:
                score += 0.5
                strengths.append("✓ Консультировались с юристом")
            else:
                recommendations.append(
                    "Рекомендуется: консультация с семейным юристом "
                    "перед медиацией"
                )

            # Support system (bonus)
            if has_support_system:
                strengths.append("✓ Есть система поддержки")
            else:
                recommendations.append(
                    "Полезно: иметь поддержку (терапевт, друзья, группа поддержки)"
                )

            # Determine readiness level
            normalized_score = score / max_score

            if normalized_score >= 0.85:
                readiness_level = MediationReadiness.WELL_PREPARED
            elif normalized_score >= 0.65:
                readiness_level = MediationReadiness.READY
            elif normalized_score >= 0.40:
                readiness_level = MediationReadiness.NEEDS_PREP
            else:
                readiness_level = MediationReadiness.NOT_READY

        return ReadinessAssessment(
            readiness_level=readiness_level,
            score=score / max_score if not has_safety_concerns else 0.0,
            strengths=strengths,
            areas_to_improve=areas_to_improve,
            recommendations=recommendations,
            safety_concerns=safety_concerns,
            red_flags=red_flags
        )


class MediationGoalPlanner:
    """
    Helps parents define and prioritize mediation goals

    Uses child-focused framework and interest-based negotiation
    """

    def create_goal(
        self,
        category: MediationGoalCategory,
        priority: Priority,
        description: str,
        ideal_outcome: str,
        acceptable_alternatives: Optional[List[str]] = None,
        dealbreakers: Optional[List[str]] = None,
        rationale: Optional[str] = None
    ) -> MediationGoal:
        """
        Create a mediation goal

        Args:
            category: Goal category
            priority: Priority level
            description: Brief description of goal
            ideal_outcome: Best-case outcome
            acceptable_alternatives: List of acceptable alternatives
            dealbreakers: What you cannot accept
            rationale: Why this matters (child-focused)

        Returns:
            MediationGoal
        """
        return MediationGoal(
            category=category,
            priority=priority,
            description=description,
            ideal_outcome=ideal_outcome,
            acceptable_alternatives=acceptable_alternatives or [],
            dealbreakers=dealbreakers or [],
            rationale=rationale or ""
        )

    def prioritize_goals(
        self,
        goals: List[MediationGoal]
    ) -> Dict[Priority, List[MediationGoal]]:
        """
        Organize goals by priority

        Args:
            goals: List of goals

        Returns:
            Dictionary of goals organized by priority
        """
        organized = {
            Priority.MUST_HAVE: [],
            Priority.HIGH_PRIORITY: [],
            Priority.MEDIUM_PRIORITY: [],
            Priority.LOW_PRIORITY: []
        }

        for goal in goals:
            organized[goal.priority].append(goal)

        return organized

    def validate_child_focus(self, rationale: str) -> Tuple[bool, str]:
        """
        Validate that rationale is child-focused, not parent-focused

        Args:
            rationale: Rationale text

        Returns:
            Tuple of (is_child_focused, feedback)
        """
        # Red flags: parent-focused language
        parent_focused_phrases = [
            "я хочу", "мне нужно", "я заслуживаю", "это справедливо для меня",
            "он/она не должен", "я прав", "это моё право",
            "I want", "I need", "I deserve", "it's fair to me",
            "he/she shouldn't", "I'm right", "it's my right"
        ]

        # Green flags: child-focused language
        child_focused_phrases = [
            "ребенку нужно", "в интересах ребенка", "для развития ребенка",
            "стабильность ребенка", "благополучие ребенка", "ребенок сможет",
            "child needs", "child's best interest", "child's development",
            "child's stability", "child's wellbeing", "child can"
        ]

        rationale_lower = rationale.lower()

        parent_focused_count = sum(
            1 for phrase in parent_focused_phrases
            if phrase in rationale_lower
        )

        child_focused_count = sum(
            1 for phrase in child_focused_phrases
            if phrase in rationale_lower
        )

        if parent_focused_count > child_focused_count:
            return False, (
                "Обоснование сфокусировано на ваших желаниях, а не на потребностях ребенка. "
                "Переформулируйте: как это решение поможет ребенку?"
            )
        elif child_focused_count > 0:
            return True, "Хорошо: обоснование сфокусировано на ребенке."
        else:
            return False, (
                "Добавьте объяснение: как это решение послужит интересам ребенка?"
            )


class MediationDocumentOrganizer:
    """
    Helps organize documents needed for mediation

    Provides checklists and organization tips
    """

    @staticmethod
    def get_document_checklist() -> Dict[str, List[str]]:
        """Get comprehensive document checklist"""
        return {
            "Custody & Parenting Time": [
                "Текущее расписание посещений",
                "История контактов с ребенком",
                "Записи о пропущенных визитах",
                "Коммуникации о расписании",
                "Фотографии времени с ребенком"
            ],
            "Child Information": [
                "Школьные отчеты и табели",
                "Медицинские записи",
                "Расписание внеклассных активностей",
                "Контакты врачей и учителей",
                "Особые потребности ребенка (если есть)"
            ],
            "Communication Records": [
                "Переписка с другим родителем (emails, SMS)",
                "Журнал телефонных звонков",
                "Документация BIFF коммуникаций",
                "Записи о конфликтах и их разрешении"
            ],
            "Financial Documents": [
                "Справки о доходах",
                "Расходы на ребенка (с чеками)",
                "Договоренности о финансовой поддержке",
                "Расходы на образование и здравоохранение"
            ],
            "Legal Documents": [
                "Текущие судебные постановления",
                "Соглашения о воспитании",
                "Документы о разводе",
                "Документы об опеке (если есть)"
            ],
            "Logistics": [
                "Ваш рабочий график",
                "График другого родителя (если известен)",
                "Расстояния между домами",
                "Варианты транспорта для ребенка",
                "Календарь школьных каникул"
            ]
        }

    @staticmethod
    def get_organization_tips() -> List[str]:
        """Get document organization tips"""
        return [
            "✓ Используйте хронологический порядок (от старых к новым)",
            "✓ Создайте индекс или оглавление",
            "✓ Выделите ключевые даты и события",
            "✓ Удалите дубликаты",
            "✓ Подготовьте копии для медиатора и другого родителя",
            "✓ Храните оригиналы отдельно",
            "✓ Используйте закладки или вкладки для разделов",
            "✓ Подготовьте краткое резюме (1-2 страницы)",
            "✓ Проверьте на PII (не включайте номера паспортов и т.д.)",
            "✓ Принесите бумажные и электронные копии"
        ]


class MediationStrategyPlanner:
    """
    Helps develop negotiation strategies for mediation

    Uses interest-based negotiation principles
    """

    @staticmethod
    def identify_interests_vs_positions(
        position: str
    ) -> Dict[str, str]:
        """
        Help distinguish between positions and underlying interests

        Position = what you want
        Interest = why you want it

        Args:
            position: Stated position

        Returns:
            Analysis with interests and alternative solutions
        """
        return {
            "position": position,
            "prompt": "Почему это важно для вас? Какую потребность это удовлетворяет?",
            "example_interests": [
                "Стабильность для ребенка",
                "Поддержание связи с ребенком",
                "Справедливое распределение времени",
                "Гибкость в расписании",
                "Минимизация конфликтов"
            ],
            "alternative_solutions": "Если вы понимаете свой интерес (interest), можно найти альтернативные пути его удовлетворения."
        }

    @staticmethod
    def get_negotiation_principles() -> List[str]:
        """Get interest-based negotiation principles"""
        return [
            "1. Фокус на интересах, а не позициях",
            "2. Отделяйте людей от проблемы",
            "3. Генерируйте множество вариантов решения",
            "4. Используйте объективные критерии (что лучше для ребенка)",
            "5. Ищите взаимную выгоду (win-win)",
            "6. Будьте готовы к компромиссу",
            "7. Сохраняйте спокойствие и уважение",
            "8. Слушайте активно"
        ]

    @staticmethod
    def prepare_for_difficult_topics() -> Dict[str, Dict[str, str]]:
        """Get preparation for difficult topics"""
        return {
            "Other Parent's Anger": {
                "strategy": "Не защищайтесь, не контратакуйте",
                "response": "Перенаправьте на интересы ребенка: 'Давайте сосредоточимся на том, что лучше для [ребенок]'",
                "self_care": "Используйте заземление, делайте паузы"
            },
            "Unfair Accusations": {
                "strategy": "Не оправдывайтесь подробно",
                "response": "Кратко: 'Я вижу это иначе. Давайте посмотрим на факты.'",
                "self_care": "Помните: вы здесь ради ребенка, не для защиты репутации"
            },
            "Financial Disagreements": {
                "strategy": "Используйте объективные данные",
                "response": "Предоставьте документацию, предложите формулу/расчет",
                "self_care": "Отделяйте деньги от эмоций"
            },
            "Impasse": {
                "strategy": "Запросите помощь медиатора",
                "response": "'Мы застряли. Можете помочь нам найти творческое решение?'",
                "self_care": "Делайте перерыв при необходимости"
            }
        }

    @staticmethod
    def get_batna_worksheet() -> Dict[str, str]:
        """
        Get BATNA (Best Alternative to Negotiated Agreement) worksheet

        Knowing your BATNA helps you negotiate from strength
        """
        return {
            "What is BATNA": (
                "BATNA = Лучшая альтернатива соглашению. "
                "Что произойдет, если медиация не удастся?"
            ),
            "Your BATNA": "Что вы будете делать, если не достигнете соглашения?",
            "Examples": (
                "- Обращение в суд\n"
                "- Продолжение текущего статус-кво\n"
                "- Арбитраж\n"
                "- Независимая оценка опеки"
            ),
            "How to use": (
                "Знание своей BATNA помогает:\n"
                "✓ Понять, какие предложения принимать\n"
                "✓ Не соглашаться на плохие условия\n"
                "✓ Переговорить с уверенностью\n\n"
                "Правило: Принимайте соглашение только если оно лучше вашей BATNA"
            )
        }


class MediationChecklist:
    """
    Provides comprehensive checklists for mediation preparation
    """

    @staticmethod
    def get_pre_mediation_checklist() -> List[Dict[str, str]]:
        """Get checklist for before mediation"""
        return [
            {
                "task": "Оценка готовности",
                "description": "Пройдите оценку готовности к медиации",
                "status": "pending"
            },
            {
                "task": "Постановка целей",
                "description": "Определите и приоритизируйте свои цели",
                "status": "pending"
            },
            {
                "task": "Организация документов",
                "description": "Соберите и организуйте все необходимые документы",
                "status": "pending"
            },
            {
                "task": "Консультация с юристом",
                "description": "Проконсультируйтесь с семейным юристом",
                "status": "pending"
            },
            {
                "task": "Изучение процесса",
                "description": "Поймите, как работает медиация",
                "status": "pending"
            },
            {
                "task": "Стратегия переговоров",
                "description": "Разработайте стратегию (interests, BATNA)",
                "status": "pending"
            },
            {
                "task": "Подготовка к сложным темам",
                "description": "Спланируйте ответы на возможные провокации",
                "status": "pending"
            },
            {
                "task": "Самоуход",
                "description": "Запланируйте поддержку до/после медиации",
                "status": "pending"
            },
            {
                "task": "Логистика",
                "description": "Подтвердите дату, время, место медиации",
                "status": "pending"
            }
        ]

    @staticmethod
    def get_day_of_mediation_checklist() -> List[str]:
        """Get checklist for day of mediation"""
        return [
            "□ Хорошо выспались и поели",
            "□ Принесли все документы",
            "□ Принесли блокнот для заметок",
            "□ Одеты нейтрально и профессионально",
            "□ Прибыли на 10-15 минут раньше",
            "□ Телефон на беззвучном режиме",
            "□ Знаете свои цели и приоритеты",
            "□ Помните BATNA",
            "□ Готовы к компромиссу",
            "□ Настроены на фокус: интересы ребенка"
        ]

    @staticmethod
    def get_during_mediation_tips() -> List[str]:
        """Get tips for during mediation"""
        return [
            "✓ Слушайте активно, не перебивайте",
            "✓ Говорите спокойно и медленно",
            "✓ Используйте BIFF коммуникацию",
            "✓ Просите паузу при необходимости",
            "✓ Делайте заметки",
            "✓ Задавайте уточняющие вопросы",
            "✓ Будьте гибкими, но помните must-haves",
            "✓ Сосредоточьтесь на интересах, не позициях",
            "✓ Обращайтесь к медиатору за помощью",
            "✓ Не принимайте решения под давлением"
        ]

    @staticmethod
    def get_post_mediation_checklist() -> List[str]:
        """Get checklist for after mediation"""
        return [
            "□ Получили письменную копию соглашения",
            "□ Прочитали соглашение полностью",
            "□ Поняли все пункты соглашения",
            "□ Показали соглашение юристу (рекомендуется)",
            "□ Подписали соглашение (если согласны)",
            "□ Получили заверенную копию",
            "□ Запланировали next steps",
            "□ Обработали эмоции с терапевтом",
            "□ Начали имплементацию соглашения"
        ]


# Example mediation goals
EXAMPLE_MEDIATION_GOALS = [
    {
        "category": MediationGoalCategory.PARENTING_TIME,
        "priority": Priority.MUST_HAVE,
        "description": "Регулярные выходные с ребенком",
        "ideal_outcome": "Каждую вторую неделю с пятницы вечера до воскресенья вечера",
        "acceptable_alternatives": [
            "Субботы с утра до воскресенья вечера каждую неделю",
            "Один полный уикенд плюс один день в неделю"
        ],
        "dealbreakers": [
            "Менее 4 дней в месяц",
            "Только дневные визиты без ночевок"
        ],
        "rationale": (
            "Ребенку нужна стабильная связь с обоими родителями. "
            "Ночевки позволяют установить рутины и более глубокую связь."
        )
    },
    {
        "category": MediationGoalCategory.DECISION_MAKING,
        "priority": Priority.HIGH_PRIORITY,
        "description": "Совместные решения о здравоохранении",
        "ideal_outcome": "Оба родителя участвуют в медицинских решениях",
        "acceptable_alternatives": [
            "Один родитель решает рутинные вопросы, оба - серьезные",
            "Получать информацию и консультироваться перед решениями"
        ],
        "dealbreakers": [
            "Полное исключение из медицинских решений"
        ],
        "rationale": (
            "Оба родителя должны быть информированы о здоровье ребенка "
            "и участвовать в важных медицинских решениях."
        )
    }
]
