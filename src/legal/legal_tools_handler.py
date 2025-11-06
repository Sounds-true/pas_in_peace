"""
Legal Tools Handler - Integration with Bot

Handles user requests for legal tools:
- Contact Diary assistance
- BIFF communication help
- Mediation preparation guidance
- Parenting model recommendations

Author: pas_in_peace
License: MIT
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.core.logger import get_logger
from src.nlp.intent_classifier import Intent

from .contact_diary import (
    ContactDiary,
    ContactDiaryAssistant,
    ContactType,
    EntryCategory
)
from .biff_templates import (
    BIFFAnalyzer,
    BIFFTransformer,
    BIFFTemplateLibrary,
    BIFFCommunicationGuide
)
from .mediation_prep import (
    MediationReadinessAssessor,
    MediationGoalPlanner,
    MediationDocumentOrganizer,
    MediationStrategyPlanner,
    MediationChecklist
)
from .parenting_model_advisor import (
    ParentingModelAssessor,
    ParentingModelGuide,
    ParentingModelToolkit
)


logger = get_logger(__name__)


@dataclass
class LegalToolResponse:
    """Response from legal tool"""
    tool_type: str  # contact_diary, biff, mediation, parenting_model
    response_text: str
    interactive_mode: Optional[str] = None  # Mode for multi-turn interactions
    data: Optional[Dict[str, Any]] = None  # Additional data


class LegalToolsHandler:
    """
    Handles all legal tool requests

    Provides conversational interface to legal tools
    """

    def __init__(self):
        """Initialize legal tools handler"""
        self.biff_analyzer = BIFFAnalyzer()
        self.contact_diary_assistant = ContactDiaryAssistant()
        self.mediation_assessor = MediationReadinessAssessor()
        self.mediation_planner = MediationGoalPlanner()
        self.parenting_assessor = ParentingModelAssessor()

        # User-specific data storage (in production, use database)
        self.user_contact_diaries: Dict[str, ContactDiary] = {}

    async def handle_intent(
        self,
        intent: Intent,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> LegalToolResponse:
        """
        Handle legal tool intent

        Args:
            intent: User intent
            message: User message
            user_id: User ID
            context: Conversation context

        Returns:
            LegalToolResponse
        """
        if intent == Intent.CONTACT_DIARY:
            return await self._handle_contact_diary(message, user_id, context)

        elif intent == Intent.BIFF_HELP:
            return await self._handle_biff_help(message, user_id, context)

        elif intent == Intent.MEDIATION_PREP:
            return await self._handle_mediation_prep(message, user_id, context)

        elif intent == Intent.PARENTING_MODEL:
            return await self._handle_parenting_model(message, user_id, context)

        else:
            return LegalToolResponse(
                tool_type="unknown",
                response_text="Извините, я не могу помочь с этим запросом."
            )

    async def _handle_contact_diary(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> LegalToolResponse:
        """Handle contact diary requests"""

        # Check if user has diary
        if user_id not in self.user_contact_diaries:
            self.user_contact_diaries[user_id] = ContactDiary(parent_id=user_id)

        diary = self.user_contact_diaries[user_id]

        # Determine what user wants
        message_lower = message.lower()

        if any(word in message_lower for word in ['создать', 'начать', 'новый', 'create', 'start']):
            # User wants to create new entry
            response_text = self._get_diary_entry_guidance()
            return LegalToolResponse(
                tool_type="contact_diary",
                response_text=response_text,
                interactive_mode="creating_entry"
            )

        elif any(word in message_lower for word in ['что такое', 'объясни', 'расскажи', 'what is', 'explain']):
            # User wants explanation
            response_text = self._get_diary_explanation()
            return LegalToolResponse(
                tool_type="contact_diary",
                response_text=response_text
            )

        elif any(word in message_lower for word in ['совет', 'tips', 'как лучше', 'how to']):
            # User wants tips
            tips = self.contact_diary_assistant.provide_documentation_tips()
            response_text = (
                "**Советы по ведению дневника контактов:**\n\n"
                + "\n".join(tips)
            )
            return LegalToolResponse(
                tool_type="contact_diary",
                response_text=response_text
            )

        elif any(word in message_lower for word in ['переформулиров', 'reframe', 'нейтральн']):
            # User wants help reframing emotional text
            response_text = (
                "Отправьте мне текст, который вы хотите переформулировать "
                "в нейтральный, фактический формат для дневника.\n\n"
                "Я помогу убрать эмоции и интерпретации, оставив только "
                "наблюдаемые факты."
            )
            return LegalToolResponse(
                tool_type="contact_diary",
                response_text=response_text,
                interactive_mode="reframing"
            )

        else:
            # General introduction
            response_text = self._get_diary_introduction()
            return LegalToolResponse(
                tool_type="contact_diary",
                response_text=response_text
            )

    async def _handle_biff_help(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> LegalToolResponse:
        """Handle BIFF communication help"""

        message_lower = message.lower()

        if any(word in message_lower for word in ['что такое biff', 'объясни biff', 'what is biff']):
            # Explain BIFF
            principles = BIFFCommunicationGuide.get_biff_principles()
            dos_donts = BIFFCommunicationGuide.get_dos_and_donts()

            response_text = (
                "**BIFF - метод коммуникации в высококонфликтных ситуациях**\n\n"
                "**Принципы BIFF:**\n"
            )

            for principle, description in principles.items():
                response_text += f"• **{principle}:** {description}\n"

            response_text += "\n**DO (Делать):**\n"
            response_text += "\n".join(dos_donts['DO'])

            response_text += "\n\n**DON'T (Не делать):**\n"
            response_text += "\n".join(dos_donts["DON'T"])

            return LegalToolResponse(
                tool_type="biff",
                response_text=response_text
            )

        elif any(word in message_lower for word in ['проверить', 'анализ', 'check', 'analyze']):
            # User wants to check a message
            response_text = (
                "Отправьте мне текст сообщения, которое вы хотите отправить "
                "другому родителю, и я проверю его на соответствие принципам BIFF."
            )
            return LegalToolResponse(
                tool_type="biff",
                response_text=response_text,
                interactive_mode="analyzing"
            )

        elif any(word in message_lower for word in ['шаблон', 'template', 'пример', 'example']):
            # User wants templates
            categories = BIFFTemplateLibrary.get_template_categories()

            response_text = "**BIFF шаблоны по категориям:**\n\n"

            for category, templates in categories.items():
                if templates:
                    response_text += f"**{category.replace('_', ' ').title()}:**\n"
                    for template_name in templates:
                        response_text += f"  • {template_name}\n"
                    response_text += "\n"

            response_text += (
                "\nЧтобы получить конкретный шаблон, укажите его название.\n"
                "Например: 'request_schedule_change'"
            )

            return LegalToolResponse(
                tool_type="biff",
                response_text=response_text,
                data={"categories": categories}
            )

        elif any(word in message_lower for word in ['ответить на', 'respond to', 'reply to']):
            # User wants help responding
            response_text = (
                "Отправьте мне сообщение от другого родителя, "
                "на которое вам нужно ответить, и я помогу составить "
                "BIFF-ответ."
            )
            return LegalToolResponse(
                tool_type="biff",
                response_text=response_text,
                interactive_mode="responding"
            )

        else:
            # General introduction
            example = BIFFCommunicationGuide.get_example_transformation()

            response_text = (
                "**BIFF - коммуникация в высококонфликтных ситуациях**\n\n"
                "BIFF расшифровывается как:\n"
                "• **B**rief (Краткость)\n"
                "• **I**nformative (Информативность)\n"
                "• **F**riendly (Дружелюбность)\n"
                "• **F**irm (Твердость)\n\n"
                "**Пример трансформации:**\n\n"
                f"❌ **Плохо:**\n{example['BAD']}\n\n"
                f"✅ **BIFF:**\n{example['BIFF']}\n\n"
                f"{example['Why BIFF is better']}\n\n"
                "Что вас интересует?\n"
                "• Объяснение принципов BIFF\n"
                "• Проверка вашего сообщения\n"
                "• Шаблоны для типичных ситуаций\n"
                "• Помощь с ответом на сообщение"
            )

            return LegalToolResponse(
                tool_type="biff",
                response_text=response_text
            )

    async def _handle_mediation_prep(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> LegalToolResponse:
        """Handle mediation preparation"""

        message_lower = message.lower()

        if any(word in message_lower for word in ['готов', 'оценка', 'ready', 'assess']):
            # User wants readiness assessment
            response_text = (
                "**Оценка готовности к медиации**\n\n"
                "Ответьте на несколько вопросов, чтобы я мог оценить вашу готовность:\n\n"
                "1. Есть ли опасения по поводу домашнего насилия или безопасности? (да/нет)\n"
                "2. Как бы вы описали своё эмоциональное состояние? "
                "(стабильное/напряженное/подавленное)\n"
                "3. Определили ли вы свои цели для медиации? (да/нет)\n"
                "4. Организованы ли ваши документы? (да/нет)\n"
                "5. Понимаете ли процесс медиации? (да/нет)\n"
                "6. Готовы ли к компромиссам? (да/нет)\n"
                "7. Можете ли обсуждать вопросы спокойно? (да/нет)\n\n"
                "Ответьте на эти вопросы, и я дам оценку вашей готовности."
            )
            return LegalToolResponse(
                tool_type="mediation",
                response_text=response_text,
                interactive_mode="readiness_assessment"
            )

        elif any(word in message_lower for word in ['цел', 'goal', 'приоритет', 'priority']):
            # User wants help with goals
            response_text = (
                "**Постановка целей для медиации**\n\n"
                "При постановке целей для медиации важно:\n\n"
                "1. **Различать позиции и интересы**\n"
                "   - Позиция = ЧТО вы хотите\n"
                "   - Интерес = ПОЧЕМУ вы это хотите\n\n"
                "2. **Приоритизировать**\n"
                "   - Must-have (нельзя не получить)\n"
                "   - High priority (очень важно)\n"
                "   - Medium priority (важно, но гибко)\n"
                "   - Low priority (хорошо бы иметь)\n\n"
                "3. **Фокусироваться на ребенке**\n"
                "   - Как это решение поможет ребенку?\n"
                "   - В чем интересы ребенка?\n\n"
                "Какую цель вы хотите определить?\n"
                "Например: 'Хочу больше времени с ребенком' - и мы разберем "
                "интересы и альтернативы."
            )
            return LegalToolResponse(
                tool_type="mediation",
                response_text=response_text,
                interactive_mode="goal_setting"
            )

        elif any(word in message_lower for word in ['документ', 'document', 'что взять', 'what to bring']):
            # User wants document checklist
            checklist = MediationDocumentOrganizer.get_document_checklist()

            response_text = "**Документы для медиации:**\n\n"

            for category, items in checklist.items():
                response_text += f"**{category}:**\n"
                for item in items:
                    response_text += f"  ☐ {item}\n"
                response_text += "\n"

            tips = MediationDocumentOrganizer.get_organization_tips()
            response_text += "**Советы по организации:**\n\n"
            response_text += "\n".join(tips)

            return LegalToolResponse(
                tool_type="mediation",
                response_text=response_text
            )

        elif any(word in message_lower for word in ['чеклист', 'checklist', 'что делать', 'steps']):
            # User wants checklist
            pre_checklist = MediationChecklist.get_pre_mediation_checklist()

            response_text = "**Чеклист подготовки к медиации:**\n\n"

            for item in pre_checklist:
                status = "☐" if item['status'] == 'pending' else "✓"
                response_text += f"{status} **{item['task']}**\n"
                response_text += f"   {item['description']}\n\n"

            return LegalToolResponse(
                tool_type="mediation",
                response_text=response_text
            )

        else:
            # General introduction
            response_text = (
                "**Подготовка к медиации**\n\n"
                "Медиация - это процесс, где нейтральный посредник (медиатор) "
                "помогает родителям договориться об опеке, расписании и других вопросах.\n\n"
                "**Я могу помочь с:**\n"
                "• Оценкой вашей готовности\n"
                "• Определением целей и приоритетов\n"
                "• Организацией документов\n"
                "• Разработкой стратегии переговоров\n"
                "• Подготовкой к сложным темам\n\n"
                "Что вас интересует?"
            )

            return LegalToolResponse(
                tool_type="mediation",
                response_text=response_text
            )

    async def _handle_parenting_model(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> LegalToolResponse:
        """Handle parenting model recommendations"""

        message_lower = message.lower()

        if any(word in message_lower for word in ['что такое', 'объясни', 'различие', 'difference']):
            # Explain difference
            response_text = (
                "**Co-parenting vs Parallel Parenting**\n\n"
                "**Co-parenting (Совместное воспитание):**\n"
                "• Для родителей с низким конфликтом\n"
                "• Регулярная коммуникация\n"
                "• Гибкость в расписании\n"
                "• Совместные решения\n"
                "• Присутствие на событиях вместе\n\n"
                "**Parallel Parenting (Параллельное воспитание):**\n"
                "• Для родителей с высоким конфликтом\n"
                "• Минимальная коммуникация (только письменно)\n"
                "• Жесткое расписание\n"
                "• Независимые решения\n"
                "• Раздельное присутствие\n\n"
                "**Когда какая модель подходит?**\n"
                "• Co-parenting: Можете спокойно общаться, идти на компромиссы\n"
                "• Parallel: Конфликты эскалируют, сложно общаться\n\n"
                "Хотите пройти оценку, чтобы понять какая модель вам подходит?"
            )

            return LegalToolResponse(
                tool_type="parenting_model",
                response_text=response_text
            )

        elif any(word in message_lower for word in ['оценка', 'тест', 'assess', 'quiz', 'какая модель']):
            # User wants assessment
            response_text = (
                "**Оценка подходящей модели воспитания**\n\n"
                "Ответьте на вопросы о ваших отношениях с другим родителем:\n\n"
                "1. Можете ли вы обсуждать вопросы о ребенке спокойно? (да/нет)\n"
                "2. Часто ли вы спорите с другим родителем? (да/нет)\n"
                "3. Готовы ли вы к компромиссам ради ребенка? (да/нет)\n"
                "4. Уважает ли другой родитель ваши границы? (да/нет)\n"
                "5. Быстро ли конфликты перерастают в серьезные споры? (да/нет)\n"
                "6. Ребенок часто становится свидетелем конфликтов? (да/нет)\n"
                "7. Делится ли другой родитель информацией о ребенке? (да/нет)\n"
                "8. Можете быть гибкими с расписанием? (да/нет)\n"
                "9. Можете присутствовать на событиях ребенка вместе? (да/нет)\n"
                "10. Есть опасения по безопасности? (да/нет)\n\n"
                "Ответьте на эти вопросы, и я порекомендую подходящую модель."
            )

            return LegalToolResponse(
                tool_type="parenting_model",
                response_text=response_text,
                interactive_mode="model_assessment"
            )

        elif 'co-parenting' in message_lower or 'совместн' in message_lower:
            # User wants co-parenting info
            guide = ParentingModelGuide.get_coparenting_guide()

            response_text = (
                f"**Co-parenting (Совместное воспитание)**\n\n"
                f"{guide['definition']}\n\n"
                "**Подходит для:**\n"
            )
            for item in guide['best_for']:
                response_text += f"• {item}\n"

            response_text += "\n**Коммуникация:**\n"
            response_text += f"• Частота: {guide['communication']['frequency']}\n"
            response_text += f"• Методы: {', '.join(guide['communication']['methods'])}\n"
            response_text += f"• Темы: {guide['communication']['topics']}\n"

            response_text += "\n**Советы:**\n"
            for tip in guide['tips'][:5]:
                response_text += f"{tip}\n"

            return LegalToolResponse(
                tool_type="parenting_model",
                response_text=response_text
            )

        elif 'parallel' in message_lower or 'параллельн' in message_lower:
            # User wants parallel parenting info
            guide = ParentingModelGuide.get_parallel_parenting_guide()

            response_text = (
                f"**Parallel Parenting (Параллельное воспитание)**\n\n"
                f"{guide['definition']}\n\n"
                "**Подходит для:**\n"
            )
            for item in guide['best_for']:
                response_text += f"• {item}\n"

            response_text += "\n**Ключевые принципы:**\n"
            for principle in guide['key_principles']:
                response_text += f"{principle}\n"

            response_text += "\n**DO (Делать):**\n"
            for do in guide['dos'][:5]:
                response_text += f"{do}\n"

            response_text += "\n**DON'T (Не делать):**\n"
            for dont in guide['donts'][:5]:
                response_text += f"{dont}\n"

            return LegalToolResponse(
                tool_type="parenting_model",
                response_text=response_text
            )

        else:
            # General introduction
            response_text = (
                "**Выбор модели воспитания после развода**\n\n"
                "Существуют две основные модели:\n\n"
                "1. **Co-parenting** - совместное воспитание с сотрудничеством\n"
                "2. **Parallel parenting** - параллельное воспитание с минимальным контактом\n\n"
                "Я могу помочь:\n"
                "• Объяснить различия между моделями\n"
                "• Оценить какая модель вам подходит\n"
                "• Дать руководство по имплементации\n"
                "• Помочь с переходом между моделями\n\n"
                "Что вас интересует?"
            )

            return LegalToolResponse(
                tool_type="parenting_model",
                response_text=response_text
            )

    # Helper methods for generating responses
    def _get_diary_introduction(self) -> str:
        """Get contact diary introduction"""
        return (
            "**Дневник контактов с ребенком**\n\n"
            "Дневник контактов помогает документировать ваши встречи с ребенком "
            "в формате, который может быть использован в суде.\n\n"
            "**Ключевые принципы:**\n"
            "✓ Факты, а не эмоции\n"
            "✓ Наблюдаемые события, не интерпретации\n"
            "✓ Нейтральный язык\n"
            "✓ Конкретные даты, время, места\n"
            "✓ Прямые цитаты ребенка\n\n"
            "**Я могу помочь:**\n"
            "• Создать новую запись\n"
            "• Дать советы по документированию\n"
            "• Переформулировать эмоциональный текст в нейтральный\n\n"
            "Что вас интересует?"
        )

    def _get_diary_explanation(self) -> str:
        """Get detailed explanation of contact diary"""
        return (
            "**Дневник контактов - детальное объяснение**\n\n"
            "**Что это:**\n"
            "Структурированная система документирования ваших взаимодействий "
            "с ребенком в нейтральном, фактическом формате.\n\n"
            "**Зачем:**\n"
            "• Документация для суда\n"
            "• Доказательство посещений\n"
            "• Фиксация нарушений расписания\n"
            "• Запись поведения и высказываний ребенка\n\n"
            "**Как вести:**\n"
            "1. Записывайте сразу после события (пока помните детали)\n"
            "2. Используйте конкретные даты, время, места\n"
            "3. Описывайте только наблюдаемое (что видели/слышали)\n"
            "4. Избегайте интерпретаций ('он был рад' → 'он улыбался')\n"
            "5. Записывайте прямые цитаты ребенка\n"
            "6. Отмечайте пропущенные встречи и опоздания\n\n"
            "**Чего избегать:**\n"
            "✗ Эмоциональных слов ('ужасно', 'замечательно')\n"
            "✗ Интерпретаций ('он манипулирует')\n"
            "✗ Обвинений другого родителя\n"
            "✗ Субъективных мнений\n\n"
            "Готовы начать первую запись?"
        )

    def _get_diary_entry_guidance(self) -> str:
        """Get guidance for creating diary entry"""
        return (
            "**Создание записи в дневнике контактов**\n\n"
            "Для создания записи мне понадобится:\n\n"
            "1. **Дата и время контакта**\n"
            "   Например: 15 мая 2025, 14:00-17:00\n\n"
            "2. **Место**\n"
            "   Например: Парк Победы\n\n"
            "3. **Тип контакта**\n"
            "   • Личная встреча\n"
            "   • Видеозвонок\n"
            "   • Телефонный звонок\n"
            "   • Пропущенная встреча\n\n"
            "4. **Фактические наблюдения**\n"
            "   Что происходило? (только факты)\n\n"
            "5. **Высказывания ребенка** (опционально)\n"
            "   Прямые цитаты\n\n"
            "6. **Поведение ребенка** (опционально)\n"
            "   Наблюдаемое поведение\n\n"
            "Опишите встречу с ребенком, и я помогу структурировать "
            "запись в правильном формате."
        )
