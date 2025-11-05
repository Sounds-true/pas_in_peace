"""
BIFF Template System - High-Conflict Communication Management

BIFF Method (Bill Eddy, High Conflict Institute):
- Brief: Keep responses short (2-5 sentences)
- Informative: Stick to facts, no emotions
- Friendly: Neutral, respectful tone
- Firm: Clear position without justification

This module helps parents communicate effectively with high-conflict
co-parents while maintaining boundaries and reducing escalation.

Reference:
- Eddy, B. (2011). BIFF: Quick Responses to High Conflict People
- High Conflict Institute best practices

Author: pas_in_peace
License: MIT
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re


class BIFFViolation(Enum):
    """Types of BIFF principle violations"""
    TOO_LONG = "too_long"  # More than ~100 words
    EMOTIONAL_LANGUAGE = "emotional_language"  # Contains emotions
    DEFENSIVE = "defensive"  # Justifying or explaining
    ATTACKING = "attacking"  # Blaming or criticizing
    UNCLEAR = "unclear"  # No clear action or information
    NOT_FRIENDLY = "not_friendly"  # Hostile tone
    WEAK_BOUNDARIES = "weak_boundaries"  # Apologetic or weak


@dataclass
class BIFFAnalysis:
    """Analysis of message against BIFF principles"""
    is_biff_compliant: bool
    score: float  # 0-1
    violations: List[BIFFViolation]
    suggestions: List[str]
    word_count: int
    tone: str  # "neutral", "emotional", "defensive", "attacking"


class BIFFAnalyzer:
    """
    Analyzes messages for BIFF compliance

    Helps parents understand if their communication follows
    BIFF principles or needs revision.
    """

    # Emotional words that violate BIFF principles
    EMOTIONAL_WORDS = [
        # Russian
        "обидно", "больно", "грустно", "злой", "ненавижу", "разочарован",
        "устал", "раздражает", "бесит", "достал", "невыносимо",
        "эгоист", "манипулятор", "лжец", "плохой", "ужасный",
        # English
        "hurt", "pain", "sad", "angry", "hate", "disappointed",
        "tired", "annoying", "frustrating", "unbearable",
        "selfish", "manipulator", "liar", "terrible", "awful"
    ]

    # Defensive phrases
    DEFENSIVE_PHRASES = [
        # Russian
        "я просто", "я всего лишь", "ты не понимаешь", "это не моя вина",
        "я же говорил", "сколько раз повторять", "почему ты не",
        # English
        "I just", "I only", "you don't understand", "it's not my fault",
        "I told you", "how many times", "why don't you"
    ]

    # Attacking phrases
    ATTACKING_PHRASES = [
        # Russian
        "ты всегда", "ты никогда", "из-за тебя", "твоя вина",
        "ты специально", "ты должен", "ты обязан",
        # English
        "you always", "you never", "because of you", "your fault",
        "you deliberately", "you should", "you must"
    ]

    def analyze(self, message: str) -> BIFFAnalysis:
        """
        Analyze message for BIFF compliance

        Args:
            message: Message text to analyze

        Returns:
            BIFFAnalysis with compliance assessment
        """
        violations = []
        suggestions = []

        # Check length (Brief)
        word_count = len(message.split())
        if word_count > 100:
            violations.append(BIFFViolation.TOO_LONG)
            suggestions.append(
                f"Сообщение слишком длинное ({word_count} слов). "
                "BIFF рекомендует 2-5 предложений (30-100 слов)."
            )

        # Check for emotional language
        message_lower = message.lower()
        found_emotional = [
            word for word in self.EMOTIONAL_WORDS
            if word in message_lower
        ]
        if found_emotional:
            violations.append(BIFFViolation.EMOTIONAL_LANGUAGE)
            suggestions.append(
                f"Найдены эмоциональные слова: {', '.join(found_emotional[:3])}. "
                "Замените на нейтральные факты."
            )

        # Check for defensive language
        found_defensive = [
            phrase for phrase in self.DEFENSIVE_PHRASES
            if phrase in message_lower
        ]
        if found_defensive:
            violations.append(BIFFViolation.DEFENSIVE)
            suggestions.append(
                "Обнаружены защитные фразы. "
                "BIFF избегает оправданий - просто изложите факты."
            )

        # Check for attacking language
        found_attacking = [
            phrase for phrase in self.ATTACKING_PHRASES
            if phrase in message_lower
        ]
        if found_attacking:
            violations.append(BIFFViolation.ATTACKING)
            suggestions.append(
                f"Обнаружены обвинительные фразы: {', '.join(found_attacking[:2])}. "
                "BIFF избегает обвинений - сосредоточьтесь на решениях."
            )

        # Check for unclear purpose
        has_question = "?" in message
        has_info = any(
            keyword in message_lower
            for keyword in ["время", "дата", "место", "ребенок", "встреча",
                          "time", "date", "place", "child", "meeting"]
        )
        if not has_question and not has_info:
            violations.append(BIFFViolation.UNCLEAR)
            suggestions.append(
                "Сообщение должно быть информативным: "
                "предоставьте конкретные факты или задайте ясный вопрос."
            )

        # Determine tone
        if found_attacking:
            tone = "attacking"
        elif found_defensive:
            tone = "defensive"
        elif found_emotional:
            tone = "emotional"
        else:
            tone = "neutral"

        # Check friendly tone (absence of hostile markers)
        hostile_markers = ["!", "!!!", "???", "ТЫ", "YOU"]
        hostile_count = sum(marker in message for marker in hostile_markers)
        if hostile_count >= 2:
            violations.append(BIFFViolation.NOT_FRIENDLY)
            suggestions.append(
                "Тон кажется враждебным. "
                "Используйте нейтральную формулировку без восклицаний."
            )

        # Calculate score
        max_violations = 7
        score = max(0.0, 1.0 - (len(violations) / max_violations))

        is_compliant = score >= 0.7 and len(violations) <= 2

        return BIFFAnalysis(
            is_biff_compliant=is_compliant,
            score=score,
            violations=violations,
            suggestions=suggestions,
            word_count=word_count,
            tone=tone
        )


class BIFFTransformer:
    """
    Transforms emotional/hostile messages into BIFF format

    Helps parents rewrite their messages to follow BIFF principles
    """

    @staticmethod
    def transform_to_biff(
        original_message: str,
        purpose: str = "general"
    ) -> Tuple[str, List[str]]:
        """
        Transform message to BIFF format

        Args:
            original_message: Original emotional/hostile message
            purpose: Purpose of message ("request", "inform", "respond")

        Returns:
            Tuple of (transformed_message, transformation_notes)
        """
        notes = []

        # Extract key facts from emotional message
        # This is a simplified version - in production would use NLP

        # Remove emotional language
        cleaned = original_message

        # Remove defensive phrases
        for phrase in BIFFAnalyzer.DEFENSIVE_PHRASES:
            if phrase in cleaned.lower():
                cleaned = re.sub(
                    re.escape(phrase),
                    "",
                    cleaned,
                    flags=re.IGNORECASE
                )
                notes.append(f"Удалены оправдания: '{phrase}'")

        # Remove attacking language
        for phrase in BIFFAnalyzer.ATTACKING_PHRASES:
            if phrase in cleaned.lower():
                cleaned = cleaned.replace(phrase, "")
                notes.append(f"Удалены обвинения: '{phrase}'")

        # Simplify and shorten
        sentences = cleaned.split(".")
        if len(sentences) > 5:
            cleaned = ". ".join(sentences[:5]) + "."
            notes.append("Сокращено до 5 предложений")

        # Add BIFF structure
        if purpose == "request":
            biff_template = (
                "Здравствуйте.\n\n"
                f"{cleaned.strip()}\n\n"
                "Пожалуйста, подтвердите получение.\n\n"
                "С уважением"
            )
        elif purpose == "inform":
            biff_template = (
                "Информирую:\n\n"
                f"{cleaned.strip()}\n\n"
                "С уважением"
            )
        else:
            biff_template = cleaned.strip()

        notes.append("Применен BIFF формат")

        return biff_template, notes


class BIFFTemplateLibrary:
    """
    Library of pre-written BIFF templates for common scenarios

    These templates follow BIFF principles and can be customized
    for specific situations.
    """

    TEMPLATES = {
        # Schedule Changes
        "request_schedule_change": {
            "ru": (
                "Здравствуйте.\n\n"
                "Не смогу забрать [ИМЯ РЕБЕНКА] в [ДЕНЬ] в [ВРЕМЯ] по причине [КРАТКАЯ ПРИЧИНА]. "
                "Предлагаю альтернативу: [АЛЬТЕРНАТИВНОЕ ВРЕМЯ].\n\n"
                "Пожалуйста, ответьте до [ДАТА].\n\n"
                "С уважением"
            ),
            "en": (
                "Hello.\n\n"
                "I won't be able to pick up [CHILD NAME] on [DAY] at [TIME] due to [BRIEF REASON]. "
                "I propose alternative: [ALTERNATIVE TIME].\n\n"
                "Please respond by [DATE].\n\n"
                "Regards"
            )
        },

        "decline_schedule_change": {
            "ru": (
                "Здравствуйте.\n\n"
                "Я не могу согласиться на изменение расписания [ДАТА]. "
                "Предлагаю придерживаться установленного графика.\n\n"
                "С уважением"
            ),
            "en": (
                "Hello.\n\n"
                "I cannot agree to schedule change on [DATE]. "
                "I propose we follow the established schedule.\n\n"
                "Regards"
            )
        },

        # Information Sharing
        "share_child_info": {
            "ru": (
                "Информирую о [РЕБЕНОК]:\n\n"
                "- [ФАКТ 1]\n"
                "- [ФАКТ 2]\n"
                "- [ФАКТ 3]\n\n"
                "Документы/контакты прилагаются при необходимости.\n\n"
                "С уважением"
            ),
            "en": (
                "Information about [CHILD]:\n\n"
                "- [FACT 1]\n"
                "- [FACT 2]\n"
                "- [FACT 3]\n\n"
                "Documents/contacts attached as needed.\n\n"
                "Regards"
            )
        },

        "request_child_info": {
            "ru": (
                "Здравствуйте.\n\n"
                "Прошу предоставить информацию о [РЕБЕНОК]: [ЧТО КОНКРЕТНО].\n\n"
                "Ответьте, пожалуйста, до [ДАТА].\n\n"
                "С уважением"
            ),
            "en": (
                "Hello.\n\n"
                "Please provide information about [CHILD]: [WHAT SPECIFICALLY].\n\n"
                "Please respond by [DATE].\n\n"
                "Regards"
            )
        },

        # Responding to Hostility
        "respond_to_hostile": {
            "ru": (
                "Здравствуйте.\n\n"
                "Отвечу только на деловую часть вашего сообщения: [КОНКРЕТНЫЙ ОТВЕТ].\n\n"
                "С уважением"
            ),
            "en": (
                "Hello.\n\n"
                "I'll respond only to the business part of your message: [SPECIFIC ANSWER].\n\n"
                "Regards"
            )
        },

        "acknowledge_only": {
            "ru": (
                "Информация получена.\n\n"
                "С уважением"
            ),
            "en": (
                "Information received.\n\n"
                "Regards"
            )
        },

        # Boundaries
        "set_communication_boundary": {
            "ru": (
                "Здравствуйте.\n\n"
                "В дальнейшем прошу общаться только по вопросам [РЕБЕНКА] "
                "через [СПОСОБ КОММУНИКАЦИИ: письменно/приложение].\n\n"
                "С уважением"
            ),
            "en": (
                "Hello.\n\n"
                "Going forward, please communicate only about [CHILD] "
                "via [COMMUNICATION METHOD: writing/app].\n\n"
                "Regards"
            )
        },

        # Medical/School
        "medical_notification": {
            "ru": (
                "Информирую:\n\n"
                "[РЕБЕНОК] посетил врача [ДАТА]. "
                "Диагноз: [ДИАГНОЗ]. "
                "Назначено: [ЛЕЧЕНИЕ].\n\n"
                "Контакт врача: [КОНТАКТ].\n\n"
                "С уважением"
            ),
            "en": (
                "Information:\n\n"
                "[CHILD] saw doctor on [DATE]. "
                "Diagnosis: [DIAGNOSIS]. "
                "Treatment: [TREATMENT].\n\n"
                "Doctor contact: [CONTACT].\n\n"
                "Regards"
            )
        },

        "school_notification": {
            "ru": (
                "Информирую:\n\n"
                "[РЕБЕНОК]: [ШКОЛЬНОЕ СОБЫТИЕ] [ДАТА] в [ВРЕМЯ]. "
                "Место: [МЕСТО].\n\n"
                "С уважением"
            ),
            "en": (
                "Information:\n\n"
                "[CHILD]: [SCHOOL EVENT] on [DATE] at [TIME]. "
                "Location: [LOCATION].\n\n"
                "Regards"
            )
        },

        # Emergency
        "emergency_notification": {
            "ru": (
                "СРОЧНО:\n\n"
                "[РЕБЕНОК]: [ЧТО ПРОИЗОШЛО]. "
                "Местонахождение: [ГДЕ]. "
                "Статус: [СТАТУС].\n\n"
                "Контакт: [ТЕЛЕФОН]."
            ),
            "en": (
                "URGENT:\n\n"
                "[CHILD]: [WHAT HAPPENED]. "
                "Location: [WHERE]. "
                "Status: [STATUS].\n\n"
                "Contact: [PHONE]."
            )
        },

        # Legal/Financial
        "request_agreement_compliance": {
            "ru": (
                "Здравствуйте.\n\n"
                "Согласно [СОГЛАШЕНИЮ О ВОСПИТАНИИ/РЕШЕНИЮ СУДА], "
                "[КОНКРЕТНЫЙ ПУНКТ] требует [ДЕЙСТВИЕ].\n\n"
                "Прошу выполнить до [ДАТА].\n\n"
                "С уважением"
            ),
            "en": (
                "Hello.\n\n"
                "According to [PARENTING AGREEMENT/COURT ORDER], "
                "[SPECIFIC CLAUSE] requires [ACTION].\n\n"
                "Please complete by [DATE].\n\n"
                "Regards"
            )
        },

        # Vacation/Travel
        "vacation_notification": {
            "ru": (
                "Информирую о поездке с [РЕБЕНОК]:\n\n"
                "Даты: [НАЧАЛО] - [КОНЕЦ]\n"
                "Место: [КУДА]\n"
                "Контакт: [ТЕЛЕФОН]\n"
                "Проживание: [АДРЕС]\n\n"
                "Маршрут прилагается.\n\n"
                "С уважением"
            ),
            "en": (
                "Travel information with [CHILD]:\n\n"
                "Dates: [START] - [END]\n"
                "Destination: [WHERE]\n"
                "Contact: [PHONE]\n"
                "Accommodation: [ADDRESS]\n\n"
                "Itinerary attached.\n\n"
                "Regards"
            )
        }
    }

    @classmethod
    def get_template(
        cls,
        template_name: str,
        language: str = "ru",
        **kwargs
    ) -> str:
        """
        Get BIFF template with placeholders filled

        Args:
            template_name: Name of template
            language: Language ("ru" or "en")
            **kwargs: Values to fill placeholders

        Returns:
            Filled template
        """
        if template_name not in cls.TEMPLATES:
            return f"Template '{template_name}' not found"

        template = cls.TEMPLATES[template_name].get(language, "")

        # Fill placeholders
        for key, value in kwargs.items():
            placeholder = f"[{key.upper()}]"
            template = template.replace(placeholder, str(value))

        return template

    @classmethod
    def list_templates(cls, category: Optional[str] = None) -> List[str]:
        """
        List available templates

        Args:
            category: Optional category filter

        Returns:
            List of template names
        """
        templates = list(cls.TEMPLATES.keys())

        if category:
            templates = [
                t for t in templates
                if category.lower() in t.lower()
            ]

        return templates

    @classmethod
    def get_template_categories(cls) -> Dict[str, List[str]]:
        """Get templates organized by category"""
        categories = {
            "schedule": [],
            "information": [],
            "boundaries": [],
            "medical_school": [],
            "emergency": [],
            "legal": [],
            "travel": []
        }

        for template_name in cls.TEMPLATES.keys():
            if "schedule" in template_name:
                categories["schedule"].append(template_name)
            elif "info" in template_name:
                categories["information"].append(template_name)
            elif "boundary" in template_name or "hostile" in template_name:
                categories["boundaries"].append(template_name)
            elif "medical" in template_name or "school" in template_name:
                categories["medical_school"].append(template_name)
            elif "emergency" in template_name:
                categories["emergency"].append(template_name)
            elif "agreement" in template_name:
                categories["legal"].append(template_name)
            elif "vacation" in template_name or "travel" in template_name:
                categories["travel"].append(template_name)

        return categories


class BIFFCommunicationGuide:
    """
    Guide for BIFF communication principles

    Provides education and tips for parents learning BIFF method
    """

    @staticmethod
    def get_biff_principles() -> Dict[str, str]:
        """Get explanation of BIFF principles"""
        return {
            "Brief": (
                "Краткость - 2-5 предложений. "
                "Чем длиннее сообщение, тем больше поводов для конфликта."
            ),
            "Informative": (
                "Информативность - только факты, без эмоций и мнений. "
                "Даты, время, места, имена."
            ),
            "Friendly": (
                "Дружелюбность - нейтральный, уважительный тон. "
                "Не значит 'друзья', значит 'деловой'."
            ),
            "Firm": (
                "Твердость - ясная позиция без оправданий. "
                "Не нужно объяснять или защищаться."
            )
        }

    @staticmethod
    def get_dos_and_donts() -> Dict[str, List[str]]:
        """Get dos and don'ts for BIFF communication"""
        return {
            "DO": [
                "✓ Отвечайте на деловую часть сообщения",
                "✓ Используйте факты и даты",
                "✓ Будьте краткими (2-5 предложений)",
                "✓ Сохраняйте нейтральный тон",
                "✓ Предлагайте решения, не проблемы",
                "✓ Заканчивайте вежливо",
                "✓ Проверяйте сообщение перед отправкой"
            ],
            "DON'T": [
                "✗ Не отвечайте на провокации",
                "✗ Не оправдывайтесь",
                "✗ Не обвиняйте",
                "✗ Не используйте эмоциональные слова",
                "✗ Не пишите длинные объяснения",
                "✗ Не отвечайте немедленно, если злитесь",
                "✗ Не пытайтесь 'выиграть' спор"
            ]
        }

    @staticmethod
    def get_example_transformation() -> Dict[str, str]:
        """Get example of bad vs BIFF message"""
        return {
            "BAD": (
                "Ты ОПЯТЬ опоздал на 40 минут! Я устала от твоего "
                "неуважения. Ребенок ждал и грустил. Ты никогда не думаешь "
                "ни о ком кроме себя. Это уже третий раз в этом месяце! "
                "Я больше не могу так. Если это повторится, я обращусь в суд. "
                "Тебе просто наплевать на нас всех!!!"
            ),
            "BIFF": (
                "Здравствуйте.\n\n"
                "Вы прибыли в 17:40 вместо запланированных 17:00 (14 мая). "
                "В будущем прошу придерживаться согласованного времени или "
                "уведомлять заранее.\n\n"
                "С уважением"
            ),
            "Why BIFF is better": (
                "BIFF версия:\n"
                "✓ Краткая (3 предложения vs 8)\n"
                "✓ Факты (время, дата) vs эмоции ('устала', 'грустил')\n"
                "✓ Нейтральная vs обвинительная\n"
                "✓ Четкий запрос vs угрозы\n"
                "✓ Не дает повода для эскалации"
            )
        }


# Integration with existing NVC system
class BIFFNVCBridge:
    """
    Bridge between BIFF (external communication) and NVC (internal processing)

    BIFF = what you SEND to high-conflict co-parent
    NVC = what you FEEL and NEED (internal work)
    """

    @staticmethod
    def explain_relationship() -> str:
        """Explain how BIFF and NVC work together"""
        return (
            "BIFF и NVC работают вместе:\n\n"
            "1. NVC помогает ВАМ:\n"
            "   - Понять свои чувства и потребности\n"
            "   - Обработать эмоции\n"
            "   - Найти свои истинные нужды\n\n"
            "2. BIFF помогает КОММУНИКАЦИИ:\n"
            "   - Выразить только необходимое\n"
            "   - Избежать эскалации\n"
            "   - Сохранить границы\n\n"
            "Процесс:\n"
            "→ Получаете провокационное сообщение\n"
            "→ Используете NVC для обработки эмоций (внутренняя работа)\n"
            "→ Используете BIFF для ответа (внешняя коммуникация)\n\n"
            "NVC = для себя. BIFF = для другого родителя."
        )
