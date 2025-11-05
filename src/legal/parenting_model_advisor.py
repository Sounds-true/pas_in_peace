"""
Co-parenting vs Parallel Parenting Decision Tool

Helps parents determine which parenting model is appropriate for their
situation based on conflict level, communication ability, and safety factors.

Parenting Models:
1. Co-parenting: Collaborative, flexible, frequent communication
   (Best for: Low-conflict, cooperative parents)

2. Parallel Parenting: Independent, structured, minimal contact
   (Best for: High-conflict, communication difficulties)

3. Transitional: Moving from parallel to co-parenting as conflict decreases

References:
- Ahrons, C. (1994). The Good Divorce
- Sullivan, M. (2008). Parallel Parenting guide
- Emery, R. (2016). Two Homes, One Childhood

Author: pas_in_peace
License: MIT
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ParentingModel(Enum):
    """Types of parenting models"""
    CO_PARENTING = "co_parenting"  # Collaborative
    PARALLEL_PARENTING = "parallel_parenting"  # Independent/minimal contact
    TRANSITIONAL = "transitional"  # Moving from parallel to co-parenting
    SUPERVISED = "supervised"  # Safety concerns present


class ConflictLevel(Enum):
    """Levels of inter-parental conflict"""
    LOW = "low"  # Rare disagreements, resolved calmly
    MODERATE = "moderate"  # Regular disagreements, some tension
    HIGH = "high"  # Frequent conflicts, difficulty communicating
    SEVERE = "severe"  # Constant hostility, potential safety concerns


@dataclass
class ParentingModelAssessment:
    """Assessment of appropriate parenting model"""
    recommended_model: ParentingModel
    conflict_level: ConflictLevel
    score: float  # 0-1 (0=high conflict, 1=low conflict)
    strengths: List[str]
    challenges: List[str]
    recommendations: List[str]
    safety_concerns: List[str]
    can_transition: bool  # Can move toward co-parenting


class ParentingModelAssessor:
    """
    Assesses which parenting model is appropriate

    Evaluates conflict level, communication patterns, and safety
    to recommend co-parenting or parallel parenting
    """

    def assess_parenting_model(
        self,
        # Communication factors
        can_communicate_calmly: bool,
        communication_frequency_ok: bool,
        can_compromise: bool,
        respects_boundaries: bool,

        # Conflict factors
        frequent_arguments: bool,
        escalates_quickly: bool,
        involves_child_in_conflict: bool,
        badmouths_other_parent: bool,

        # Cooperation factors
        flexible_with_schedule: bool,
        shares_information: bool,
        supports_other_parents_time: bool,
        attends_events_together: bool,

        # Safety factors
        history_of_violence: bool = False,
        substance_abuse: bool = False,
        mental_health_untreated: bool = False,
        child_afraid: bool = False
    ) -> ParentingModelAssessment:
        """
        Assess appropriate parenting model

        Args:
            can_communicate_calmly: Can discuss child matters calmly
            communication_frequency_ok: Comfortable with regular contact
            can_compromise: Willing to compromise for child's benefit
            respects_boundaries: Respects other parent's boundaries
            frequent_arguments: Arguments happen often
            escalates_quickly: Conflicts escalate rapidly
            involves_child_in_conflict: Child exposed to arguments
            badmouths_other_parent: Negative comments about other parent
            flexible_with_schedule: Open to schedule adjustments
            shares_information: Shares info about child proactively
            supports_other_parents_time: Encourages child's relationship
            attends_events_together: Can attend child's events together
            history_of_violence: Domestic violence history
            substance_abuse: Active substance abuse issues
            mental_health_untreated: Untreated mental health affecting parenting
            child_afraid: Child expresses fear of parent

        Returns:
            ParentingModelAssessment with recommendation
        """
        strengths = []
        challenges = []
        recommendations = []
        safety_concerns = []

        # Check safety first
        safety_issues = []
        if history_of_violence:
            safety_issues.append("История домашнего насилия")
        if substance_abuse:
            safety_issues.append("Активные проблемы с веществами")
        if mental_health_untreated:
            safety_issues.append("Нелеченные психические проблемы")
        if child_afraid:
            safety_issues.append("Ребенок выражает страх")

        if safety_issues:
            safety_concerns = safety_issues
            recommendations.append(
                "⚠️  КРИТИЧНО: Проконсультируйтесь с юристом и терапевтом. "
                "Может потребоваться supervised visitation."
            )
            return ParentingModelAssessment(
                recommended_model=ParentingModel.SUPERVISED,
                conflict_level=ConflictLevel.SEVERE,
                score=0.0,
                strengths=[],
                challenges=safety_issues,
                recommendations=recommendations,
                safety_concerns=safety_concerns,
                can_transition=False
            )

        # Calculate scores for different factors
        communication_score = 0
        conflict_score = 0
        cooperation_score = 0

        # Communication factors (positive indicators)
        if can_communicate_calmly:
            communication_score += 1
            strengths.append("✓ Способны общаться спокойно")
        else:
            challenges.append("✗ Сложности в спокойной коммуникации")

        if communication_frequency_ok:
            communication_score += 1
            strengths.append("✓ Комфортно с регулярным контактом")
        else:
            challenges.append("✗ Дискомфорт от частого общения")

        if can_compromise:
            communication_score += 1
            strengths.append("✓ Готовность к компромиссам")
        else:
            challenges.append("✗ Сложности с компромиссами")

        if respects_boundaries:
            communication_score += 1
            strengths.append("✓ Уважение границ")
        else:
            challenges.append("✗ Нарушение границ")

        # Conflict factors (negative indicators, inverted)
        if not frequent_arguments:
            conflict_score += 1
            strengths.append("✓ Редкие конфликты")
        else:
            challenges.append("✗ Частые аргументы")

        if not escalates_quickly:
            conflict_score += 1
            strengths.append("✓ Конфликты не эскалируют")
        else:
            challenges.append("✗ Быстрая эскалация конфликтов")

        if not involves_child_in_conflict:
            conflict_score += 1
            strengths.append("✓ Ребенок защищен от конфликтов")
        else:
            challenges.append("✗ Ребенок вовлечен в конфликты")
            recommendations.append(
                "КРИТИЧНО: Защитите ребенка от конфликтов между родителями"
            )

        if not badmouths_other_parent:
            conflict_score += 1
            strengths.append("✓ Нет негатива о другом родителе")
        else:
            challenges.append("✗ Негативные комментарии о другом родителе")
            recommendations.append(
                "Избегайте негативных комментариев о другом родителе при ребенке"
            )

        # Cooperation factors (positive indicators)
        if flexible_with_schedule:
            cooperation_score += 1
            strengths.append("✓ Гибкость в расписании")
        else:
            challenges.append("✗ Жесткость в расписании")

        if shares_information:
            cooperation_score += 1
            strengths.append("✓ Делится информацией о ребенке")
        else:
            challenges.append("✗ Ограниченный обмен информацией")

        if supports_other_parents_time:
            cooperation_score += 1
            strengths.append("✓ Поддерживает связь ребенка с другим родителем")
        else:
            challenges.append("✗ Не поддерживает связь с другим родителем")
            recommendations.append(
                "Поддерживайте позитивное отношение к времени ребенка с другим родителем"
            )

        if attends_events_together:
            cooperation_score += 1
            strengths.append("✓ Можете присутствовать на событиях вместе")
        else:
            challenges.append("✗ Сложности с совместным присутствием")

        # Calculate overall score (0-1)
        total_score = communication_score + conflict_score + cooperation_score
        max_score = 12  # 4 + 4 + 4
        normalized_score = total_score / max_score

        # Determine conflict level
        if normalized_score >= 0.75:
            conflict_level = ConflictLevel.LOW
        elif normalized_score >= 0.50:
            conflict_level = ConflictLevel.MODERATE
        elif normalized_score >= 0.25:
            conflict_level = ConflictLevel.HIGH
        else:
            conflict_level = ConflictLevel.SEVERE

        # Recommend parenting model
        if normalized_score >= 0.70:
            # Co-parenting appropriate
            recommended_model = ParentingModel.CO_PARENTING
            recommendations.extend([
                "Co-parenting рекомендуется: низкий конфликт, хорошая коммуникация",
                "Продолжайте развивать навыки совместной работы",
                "Будьте гибкими и сосредоточены на ребенке"
            ])
            can_transition = False  # Already at best model

        elif normalized_score >= 0.45:
            # Transitional - could work toward co-parenting
            recommended_model = ParentingModel.TRANSITIONAL
            recommendations.extend([
                "Переходная модель: двигайтесь от parallel к co-parenting",
                "Работайте над улучшением коммуникации (BIFF)",
                "Начните с малых шагов совместной работы",
                "Рассмотрите family therapy или coaching"
            ])
            can_transition = True

        else:
            # Parallel parenting needed
            recommended_model = ParentingModel.PARALLEL_PARENTING
            recommendations.extend([
                "Parallel parenting рекомендуется: высокий конфликт",
                "Минимизируйте прямой контакт",
                "Используйте письменную коммуникацию (BIFF)",
                "Установите жесткие границы и структуру",
                "Фокус: независимое воспитание в своё время"
            ])
            can_transition = True  # Can improve over time

        return ParentingModelAssessment(
            recommended_model=recommended_model,
            conflict_level=conflict_level,
            score=normalized_score,
            strengths=strengths,
            challenges=challenges,
            recommendations=recommendations,
            safety_concerns=safety_concerns,
            can_transition=can_transition
        )


class ParentingModelGuide:
    """
    Provides implementation guidance for each parenting model

    Explains characteristics, communication rules, and boundaries
    for co-parenting vs parallel parenting
    """

    @staticmethod
    def get_coparenting_guide() -> Dict[str, any]:
        """Get complete co-parenting implementation guide"""
        return {
            "definition": (
                "Co-parenting = Collaborative parenting with regular communication, "
                "flexibility, and joint decision-making."
            ),
            "best_for": [
                "Родители с низким конфликтом",
                "Способность общаться спокойно и уважительно",
                "Готовность к компромиссам",
                "Фокус на интересах ребенка, а не на прошлых обидах"
            ],
            "communication": {
                "frequency": "Регулярная (ежедневно или несколько раз в неделю)",
                "methods": ["Телефон", "Текст", "Email", "Лично", "Приложения для co-parenting"],
                "topics": "Все аспекты жизни ребенка: школа, здоровье, эмоции, активности, друзья",
                "style": "Открытая, прямая, дружелюбная"
            },
            "decision_making": {
                "approach": "Совместные решения по важным вопросам",
                "major_decisions": "Обсуждаются вместе: школа, здравоохранение, религия, активности",
                "daily_decisions": "Могут приниматься независимо, но с информированием",
                "conflict_resolution": "Обсуждение, компромисс, медиация при необходимости"
            },
            "schedule": {
                "flexibility": "Высокая - изменения обсуждаются и принимаются",
                "transitions": "Могут быть гибкими (забрать из школы, от друзей)",
                "adjustments": "Частые adjustments OK if both agree"
            },
            "boundaries": {
                "physical": "Могут общаться лично без напряжения",
                "events": "Присутствуют вместе на событиях ребенка",
                "new_partners": "Обсуждаются и со временем встречаются",
                "home_rules": "Координируются между домами для консистентности"
            },
            "challenges": [
                "Требует высокого уровня доверия и уважения",
                "Может быть сложно с новыми партнерами",
                "Риск слишком размытых границ",
                "Может быть эмоционально сложно видеть ex часто"
            ],
            "tips": [
                "✓ Регулярные check-ins о ребенке",
                "✓ Общий календарь",
                "✓ Консистентные правила между домами",
                "✓ Поддержка связи ребенка с другим родителем",
                "✓ Гибкость при необходимости",
                "✓ Фокус на командной работе"
            ]
        }

    @staticmethod
    def get_parallel_parenting_guide() -> Dict[str, any]:
        """Get complete parallel parenting implementation guide"""
        return {
            "definition": (
                "Parallel Parenting = Independent parenting with minimal contact, "
                "structured communication, and firm boundaries."
            ),
            "best_for": [
                "Родители с высоким конфликтом",
                "Сложности в прямой коммуникации",
                "Эскалация при контакте",
                "Разные стили воспитания"
            ],
            "communication": {
                "frequency": "Минимальная (только о необходимом)",
                "methods": ["ТОЛЬКО письменно: Email, приложение", "Избегать: звонки, личный контакт"],
                "topics": "ТОЛЬКО факты о ребенке: расписание, здоровье, школа",
                "style": "BIFF: Brief, Informative, Friendly, Firm"
            },
            "decision_making": {
                "approach": "Независимые решения в своё время с ребенком",
                "major_decisions": "Четко разграничены в соглашении (кто за что отвечает)",
                "daily_decisions": "Полностью независимы во время своей опеки",
                "conflict_resolution": "Обращение к соглашению, медиатору или суду (не прямое обсуждение)"
            },
            "schedule": {
                "flexibility": "Низкая - строгое следование расписанию",
                "transitions": "Фиксированные места и время (часто нейтральная территория)",
                "adjustments": "Только с заблаговременным письменным уведомлением"
            },
            "boundaries": {
                "physical": "Минимальный или нулевой личный контакт",
                "events": "Раздельное присутствие или очередность",
                "new_partners": "Не обсуждаются (личное дело каждого)",
                "home_rules": "Полностью независимые (разные правила OK)"
            },
            "key_principles": [
                "1. Минимизация контакта между родителями",
                "2. Жесткие, предсказуемые структуры",
                "3. Детальное письменное соглашение",
                "4. Независимость во время своей опеки",
                "5. Защита ребенка от конфликтов",
                "6. Письменная коммуникация ТОЛЬКО о ребенке"
            ],
            "what_to_specify": [
                "□ Точное расписание с датами и временем",
                "□ Фиксированные места transitions (школа, daycare, нейтральное место)",
                "□ Кто принимает решения по каждой области",
                "□ Протокол экстренной коммуникации",
                "□ Как делиться информацией о ребенке (через приложение)",
                "□ Правила о школьных событиях (чередование?)",
                "□ Процесс для изменений расписания",
                "□ Кто контакт с учителями, врачами"
            ],
            "dos": [
                "✓ Следуйте расписанию строго",
                "✓ Коммуницируйте только письменно",
                "✓ Используйте BIFF формат",
                "✓ Делайте transitions быстрыми и нейтральными",
                "✓ Уважайте время другого родителя (не звоните/не пишите ребенку без причины)",
                "✓ Ведите записи о коммуникациях",
                "✓ Фокус: качество вашего времени, не контроль другого"
            ],
            "donts": [
                "✗ Не пытайтесь обсуждать прошлое",
                "✗ Не критикуйте стиль воспитания другого",
                "✗ Не ждите гибкости",
                "✗ Не вовлекайте ребенка в logistics",
                "✗ Не расспрашивайте ребенка о другом родителе",
                "✗ Не пытайтесь 'улучшить' отношения если другой не готов"
            ],
            "for_child": [
                "• Объясните ребенку: 'У мамы и папы разные дома и разные правила - это нормально'",
                "• Не просите ребенка передавать сообщения",
                "• Не спрашивайте ребенка о другом родителе",
                "• Заверьте ребенка: 'Вы не виноваты, что мы не общаемся много'",
                "• Поддерживайте позитивное отношение ко времени с другим родителем"
            ]
        }

    @staticmethod
    def get_transition_guide() -> Dict[str, any]:
        """Get guide for transitioning from parallel to co-parenting"""
        return {
            "when_ready": [
                "Конфликт значительно снизился",
                "Оба родителя работают над собой (терапия, навыки)",
                "Прошло достаточно времени для healing",
                "BIFF коммуникация работает стабильно",
                "Оба хотят более тесного сотрудничества"
            ],
            "steps": [
                {
                    "step": 1,
                    "title": "Стабилизация parallel parenting",
                    "actions": [
                        "Следуйте parallel модели минимум 6-12 месяцев",
                        "Убедитесь что конфликты минимальны",
                        "Освойте BIFF коммуникацию"
                    ]
                },
                {
                    "step": 2,
                    "title": "Малые шаги сотрудничества",
                    "actions": [
                        "Начните делиться большей информацией о ребенке",
                        "Попробуйте одно совместное событие (короткое)",
                        "Обсудите один небольшой вопрос вместе"
                    ]
                },
                {
                    "step": 3,
                    "title": "Увеличение контакта",
                    "actions": [
                        "Добавьте краткие телефонные разговоры",
                        "Присутствуйте на событиях ребенка вместе",
                        "Начните консультироваться по решениям"
                    ]
                },
                {
                    "step": 4,
                    "title": "Гибкость и координация",
                    "actions": [
                        "Пробуйте небольшие изменения расписания",
                        "Координируйте некоторые правила между домами",
                        "Обсуждайте долгосрочные планы вместе"
                    ]
                }
            ],
            "warning_signs": [
                "⚠️ Если конфликты возвращаются - вернитесь к parallel",
                "⚠️ Если один родитель не готов - оставайтесь на parallel",
                "⚠️ Если ребенок страдает от напряжения - замедлите transition"
            ],
            "timeline": "Переход может занять 1-3 года. Не торопитесь.",
            "tip": "Лучше оставаться на successful parallel parenting, чем форсировать co-parenting и создавать конфликт."
        }


class ParentingModelToolkit:
    """
    Practical tools for implementing each parenting model
    """

    @staticmethod
    def get_communication_agreement_template(
        model: ParentingModel
    ) -> str:
        """
        Get communication agreement template for chosen model

        Args:
            model: Parenting model

        Returns:
            Template text
        """
        if model == ParentingModel.CO_PARENTING:
            return """
СОГЛАШЕНИЕ О КОММУНИКАЦИИ (CO-PARENTING)

Мы, родители [ИМЯ РЕБЕНКА], соглашаемся:

1. КОММУНИКАЦИЯ
   - Коммуницировать регулярно о благополучии ребенка
   - Использовать уважительный тон всегда
   - Отвечать на сообщения в течение 24 часов (не экстренные)
   - Немедленный ответ на экстренные ситуации

2. РЕШЕНИЯ
   - Обсуждать крупные решения вместе
   - Консультироваться перед новыми активностями
   - Делиться информацией о школе, здоровье

3. РАСПИСАНИЕ
   - Следовать базовому расписанию
   - Обсуждать изменения заблаговременно
   - Быть гибкими при необходимости

4. СОБЫТИЯ
   - Присутствовать вместе на событиях ребенка
   - Вести себя вежливо и уважительно

5. КОНФЛИКТЫ
   - Обсуждать разногласия спокойно
   - Использовать медиацию при impasse
   - НИКОГДА не вовлекать ребенка

Подписано: [ДАТА]
"""

        elif model == ParentingModel.PARALLEL_PARENTING:
            return """
СОГЛАШЕНИЕ О КОММУНИКАЦИИ (PARALLEL PARENTING)

Мы, родители [ИМЯ РЕБЕНКА], соглашаемся:

1. КОММУНИКАЦИЯ
   - ТОЛЬКО письменная коммуникация (email/приложение)
   - ТОЛЬКО о фактах, касающихся ребенка
   - BIFF формат: Brief, Informative, Friendly, Firm
   - Ответ в течение 48 часов (не экстренные)

2. ЭКСТРЕННЫЕ СИТУАЦИИ
   - Звонки разрешены ТОЛЬКО для экстренных случаев
   - Экстренное = угроза здоровью/безопасности
   - НЕ экстренное = изменения расписания, школьные вопросы

3. РЕШЕНИЯ
   - [РОДИТЕЛЬ 1] принимает решения о: [ОБЛАСТИ]
   - [РОДИТЕЛЬ 2] принимает решения о: [ОБЛАСТИ]
   - Независимые решения во время своей опеки
   - При разногласиях = обращение к медиатору

4. РАСПИСАНИЕ
   - СТРОГОЕ следование расписанию
   - Transitions: [МЕСТО] в [ВРЕМЯ]
   - Изменения ТОЛЬКО с минимум 7-дневным письменным уведомлением

5. TRANSITIONS
   - Быстрые, нейтральные, без разговоров
   - Обмен информацией через journal/приложение
   - НЕТ личных разговоров

6. СОБЫТИЯ РЕБЕНКА
   - [Выбрать один]:
     □ Раздельное присутствие
     □ Чередование присутствия
     □ Оба присутствуют, но раздельно сидят

7. ГРАНИЦЫ
   - Не звонить/не писать ребенку во время другого родителя без согласования
   - Не критиковать другого родителя
   - Не расспрашивать ребенка

8. НАРУШЕНИЯ
   - При нарушении соглашения = документирование
   - Повторные нарушения = обращение к медиатору/суду

Подписано: [ДАТА]
"""

        else:
            return "Template not available for this model"

    @staticmethod
    def get_coparenting_apps_recommendations() -> List[Dict[str, str]]:
        """Get recommended apps for co-parenting"""
        return [
            {
                "name": "OurFamilyWizard",
                "features": "Shared calendar, messaging, expense tracking",
                "best_for": "Both models, but especially high-conflict (court-admissible records)"
            },
            {
                "name": "Cozi",
                "features": "Shared calendar, shopping lists, to-do lists",
                "best_for": "Co-parenting (lower conflict)"
            },
            {
                "name": "2Houses",
                "features": "Schedule, expenses, documents, messages",
                "best_for": "Both models"
            },
            {
                "name": "Google Calendar",
                "features": "Shared calendar",
                "best_for": "Co-parenting (simple solution)"
            },
            {
                "name": "Talking Parents",
                "features": "Monitored communication, court-ready records",
                "best_for": "Parallel parenting (accountability)"
            }
        ]


# Quick assessment questionnaire
PARENTING_MODEL_QUESTIONNAIRE = {
    "intro": (
        "Ответьте на вопросы о ваших отношениях с другим родителем. "
        "Будьте честны - это поможет определить подходящую модель."
    ),
    "questions": [
        {
            "id": "communicate_calmly",
            "text": "Можете ли вы обсуждать вопросы о ребенке спокойно, без аргументов?",
            "type": "yes_no"
        },
        {
            "id": "frequent_arguments",
            "text": "Часто ли вы спорите с другим родителем?",
            "type": "yes_no"
        },
        {
            "id": "can_compromise",
            "text": "Готовы ли вы к компромиссам ради ребенка?",
            "type": "yes_no"
        },
        {
            "id": "respects_boundaries",
            "text": "Уважает ли другой родитель ваши границы?",
            "type": "yes_no"
        },
        {
            "id": "escalates_quickly",
            "text": "Быстро ли конфликты перерастают в серьезные споры?",
            "type": "yes_no"
        },
        {
            "id": "child_involved",
            "text": "Ребенок часто становится свидетелем или участником конфликтов?",
            "type": "yes_no"
        },
        {
            "id": "shares_info",
            "text": "Делится ли другой родитель информацией о ребенке?",
            "type": "yes_no"
        },
        {
            "id": "flexible",
            "text": "Можете ли вы оба быть гибкими с расписанием при необходимости?",
            "type": "yes_no"
        },
        {
            "id": "events_together",
            "text": "Можете ли вы присутствовать на событиях ребенка вместе без напряжения?",
            "type": "yes_no"
        },
        {
            "id": "safety_concerns",
            "text": "Есть ли опасения по поводу домашнего насилия или безопасности?",
            "type": "yes_no"
        }
    ]
}
