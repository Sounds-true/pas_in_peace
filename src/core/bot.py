"""Main Telegram bot implementation."""

import asyncio
from typing import Optional
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.core.config import settings
from src.core.logger import get_logger, log_user_interaction, setup_logging
from src.safety.crisis_detector import CrisisDetector
from src.orchestration.state_manager import StateManager
from src.nlp.pii_protector import PIIProtector


logger = get_logger(__name__)


class PASBot:
    """Main bot class for PAS (Parental Alienation Support) Bot."""

    def __init__(self):
        """Initialize the bot."""
        self.app: Optional[Application] = None
        self.crisis_detector = CrisisDetector()
        self.state_manager = StateManager()
        self.pii_protector = PIIProtector()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        user_id = str(user.id)

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="command",
            command="start"
        )

        # Initialize user state
        await self.state_manager.initialize_user(user_id)

        welcome_message = (
            "Здравствуйте! Я бот поддержки для родителей, столкнувшихся с отчуждением.\\n\\n"
            "Я здесь, чтобы:\\n"
            "• Выслушать ваши переживания\\n"
            "• Помочь справиться с эмоциями\\n"
            "• Поддержать в написании писем\\n"
            "• Предложить техники самопомощи\\n\\n"
            "Помните: я не заменяю профессиональную психологическую помощь. "
            "Если вам нужна срочная помощь, обратитесь по телефону доверия: "
            f"{settings.crisis_hotline_ru}\\n\\n"
            "Как вы себя чувствуете сегодня?"
        )

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        user_id = str(update.effective_user.id)

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="command",
            command="help"
        )

        help_text = (
            "📚 Доступные команды:\\n\\n"
            "/start - Начать диалог\\n"
            "/help - Показать это сообщение\\n"
            "/progress - Ваш прогресс по 4 направлениям\\n"
            "/letter - Начать написание письма\\n"
            "/letters - Посмотреть мои письма\\n"
            "/goals - Посмотреть ваши цели\\n"
            "/resources - Полезные ресурсы\\n"
            "/crisis - Экстренная помощь\\n"
            "/privacy - Информация о конфиденциальности\\n\\n"
            "Вы можете просто написать мне о том, что вас беспокоит."
        )

        await update.message.reply_text(help_text)

    async def letter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /letter command - start letter writing."""
        user_id = str(update.effective_user.id)

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="command",
            command="letter"
        )

        # Process through state manager with "письмо" keyword
        response = await self.state_manager.process_message(user_id, "хочу написать письмо")
        await update.message.reply_text(response)

    async def letters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /letters command - view and resume letter drafts."""
        user_id = str(update.effective_user.id)

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="command",
            command="letters"
        )

        # Get user from state manager to access database
        user_state = await self.state_manager.get_or_create_user_state(user_id)

        if not self.state_manager.db:
            await update.message.reply_text("Извините, база данных недоступна.")
            return

        try:
            # Retrieve all letters for this user
            letters = await self.state_manager.db.get_user_letters(
                user_id=user_state.user_id,
                status=None  # Get all letters
            )

            if not letters:
                message = (
                    "📝 У вас пока нет сохранённых писем.\n\n"
                    "Используйте /letter чтобы начать писать новое письмо."
                )
            else:
                # Build message with letter list
                message = f"📚 **Ваши письма** ({len(letters)}):\n\n"

                for idx, letter in enumerate(letters, 1):
                    status_emoji = "✅" if letter.status == "completed" else "✏️"
                    message += f"{status_emoji} **{idx}. {letter.title or f'Письмо #{letter.id}'}**\n"
                    message += f"   Кому: {letter.recipient_role or 'не указано'}\n"
                    message += f"   Статус: {letter.status}\n"
                    message += f"   Создано: {letter.created_at.strftime('%d.%m.%Y')}\n\n"

                message += "\nЧтобы продолжить редактирование, напишите номер письма.\n"
                message += "Чтобы создать новое письмо, используйте /letter"

            await update.message.reply_text(message)

        except Exception as e:
            logger.error("letters_list_failed", error=str(e), user_id=user_id)
            await update.message.reply_text(
                "Произошла ошибка при загрузке писем. Попробуйте позже."
            )

    async def goals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /goals command - view and manage goals."""
        user_id = str(update.effective_user.id)

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="command",
            command="goals"
        )

        # Get user from state manager to access database
        user_state = await self.state_manager.get_or_create_user_state(user_id)

        if not self.state_manager.db:
            await update.message.reply_text("Извините, база данных недоступна.")
            return

        try:
            # Retrieve active goals for this user
            goals = await self.state_manager.db.get_active_goals(user_id=user_state.user_id)

            if not goals:
                message = (
                    "🎯 **У вас пока нет активных целей**\n\n"
                    "Постановка целей помогает:\n"
                    "• Видеть прогресс\n"
                    "• Чувствовать контроль над ситуацией\n"
                    "• Двигаться к конкретному результату\n\n"
                    "Хотите поставить цель? Напишите: **\"хочу поставить цель\"**"
                )
            else:
                # Build message with goals list
                message = f"🎯 **Ваши цели** ({len(goals)}):\n\n"

                for idx, goal in enumerate(goals, 1):
                    progress = goal.progress_percentage or 0.0
                    progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))

                    message += f"**{idx}. {goal.title}**\n"
                    message += f"   {progress_bar} {int(progress)}%\n"

                    if goal.description:
                        desc_short = goal.description[:60] + "..." if len(goal.description) > 60 else goal.description
                        message += f"   📝 {desc_short}\n"

                    if goal.time_bound:
                        message += f"   ⏱️ Срок: {goal.time_bound}\n"

                    if goal.milestones:
                        completed = len(goal.completed_milestones) if goal.completed_milestones else 0
                        total = len(goal.milestones)
                        message += f"   ✓ Шагов выполнено: {completed}/{total}\n"

                    message += "\n"

                message += "\nЧтобы обновить прогресс, напишите: **\"обновить цель [номер]\"**\n"
                message += "Чтобы поставить новую цель: **\"хочу поставить цель\"**"

            await update.message.reply_text(message)

        except Exception as e:
            logger.error("goals_list_failed", error=str(e), user_id=user_id)
            await update.message.reply_text(
                "Произошла ошибка при загрузке целей. Попробуйте позже."
            )

    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /progress command - view multi-track recovery progress."""
        user_id = str(update.effective_user.id)

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="command",
            command="progress"
        )

        if not self.state_manager.multi_track_manager or not self.state_manager.db:
            await update.message.reply_text(
                "Система отслеживания прогресса временно недоступна."
            )
            return

        try:
            # Convert user_id to int
            user_id_int = int(user_id) if user_id.isdigit() else hash(user_id) % 1000000

            # Get all track progress
            tracks = await self.state_manager.multi_track_manager.get_all_progress(user_id_int)

            if not tracks:
                message = (
                    "📊 **Ваш прогресс восстановления**\n\n"
                    "Система мультитрекинга еще не инициализирована.\n"
                    "Начните диалог, и я создам индивидуальный план восстановления."
                )
                await update.message.reply_text(message)
                return

            # Build progress report
            message = "📊 **Ваш прогресс по 4 направлениям восстановления**\n\n"

            # Track names in Russian
            track_names = {
                "self_work": "💚 Работа над собой",
                "child_connection": "💙 Связь с ребенком",
                "negotiation": "🤝 Переговоры",
                "community": "👥 Сообщество"
            }

            # Phase names in Russian
            phase_names = {
                "awareness": "Осознание",
                "expression": "Выражение",
                "action": "Действие",
                "mastery": "Мастерство"
            }

            for track_key, track_data in tracks.items():
                percentage = track_data.get("completion_percentage", 0)
                phase = track_data.get("phase", "awareness")
                total_actions = track_data.get("total_actions", 0)

                # Progress bar (10 blocks)
                filled = int(percentage / 10)
                progress_bar = "█" * filled + "░" * (10 - filled)

                message += f"{track_names.get(track_key, track_key)}\n"
                message += f"{progress_bar} {percentage}%\n"
                message += f"Фаза: {phase_names.get(phase, phase)} | Действий: {total_actions}\n"

                # Show next action
                next_action = track_data.get("next_action", {})
                if next_action.get("suggestion"):
                    message += f"➡️ {next_action['suggestion'][:80]}\n"

                # Show milestones if any
                milestones = track_data.get("milestones", [])
                if milestones:
                    recent_milestone = milestones[-1]
                    message += f"🏆 Последнее достижение: {recent_milestone.get('name', 'N/A')}\n"

                message += "\n"

            # Check if should suggest track switch
            current_track = self.state_manager.multi_track_manager.get_primary_track(tracks)
            suggested_switch = self.state_manager.multi_track_manager.should_suggest_track_switch(
                current_track, tracks
            )

            if suggested_switch:
                message += f"💡 **Рекомендация:** Попробуйте уделить внимание направлению \"{track_names.get(suggested_switch)}\" - оно требует развития.\n\n"

            message += "📝 Используйте /help для просмотра доступных действий."

            await update.message.reply_text(message)

        except Exception as e:
            logger.error("progress_display_failed", error=str(e), user_id=user_id)
            await update.message.reply_text(
                "Произошла ошибка при загрузке прогресса. Попробуйте позже."
            )

    async def crisis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /crisis command - immediate crisis resources."""
        user_id = str(update.effective_user.id)

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="command",
            command="crisis",
            severity="high"
        )

        crisis_message = (
            "🆘 Если вам нужна срочная помощь:\\n\\n"
            "📞 Телефоны доверия:\\n"
            f"• Россия: {settings.crisis_hotline_ru} (круглосуточно)\\n"
            f"• International: {settings.crisis_hotline_intl}\\n\\n"
            "🏥 Экстренные службы:\\n"
            "• Скорая помощь: 103\\n"
            "• Единая служба экстренной помощи: 112\\n\\n"
            "💙 Помните: обращение за помощью - это признак силы, а не слабости.\\n"
            "Вы не одиноки."
        )

        await update.message.reply_text(crisis_message)

        # Transition to crisis state
        await self.state_manager.transition_to_crisis(user_id)

    async def _send_crisis_response(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        crisis_protocol: str,
        risk_assessment: dict
    ) -> None:
        """Send appropriate crisis response based on protocol type."""
        user_id = str(update.effective_user.id)

        if crisis_protocol == "suicide_prevention":
            crisis_message = (
                "🆘 **Я очень обеспокоен тем, что вы мне сообщили.**\\n\\n"
                "Ваша безопасность — главный приоритет. Пожалуйста, немедленно обратитесь за профессиональной помощью:\\n\\n"
                "📞 **Телефон доверия (круглосуточно):**\\n"
                f"• {settings.crisis_hotline_ru}\\n\\n"
                "🏥 **Экстренная помощь:**\\n"
                "• Скорая помощь: 103\\n"
                "• Полиция: 102\\n"
                "• Единая служба: 112\\n\\n"
                "💙 **Я здесь, чтобы поддержать вас, но в критической ситуации необходима помощь специалистов.**"
            )
        elif crisis_protocol == "violence_prevention":
            crisis_message = (
                "⚠️ **Я понимаю, что вы испытываете сильный гнев.**\\n\\n"
                "Важно обеспечить безопасность всех. Пожалуйста, сделайте паузу и обратитесь за поддержкой:\\n\\n"
                "📞 **Помощь в кризисной ситуации:**\\n"
                f"• Телефон доверия: {settings.crisis_hotline_ru}\\n"
                "• Полиция (при угрозе насилия): 102\\n\\n"
                "💡 **Сейчас:**\\n"
                "• Отойдите от ситуации физически\\n"
                "• Сделайте несколько глубоких вдохов\\n"
                "• Позвоните специалисту\\n\\n"
                "Я здесь, чтобы помочь вам справиться с этими чувствами безопасным способом."
            )
        else:
            # Generic crisis response
            crisis_message = (
                "🆘 **Ваше сообщение вызывает серьёзную озабоченность.**\\n\\n"
                "Пожалуйста, обратитесь за профессиональной помощью:\\n\\n"
                "📞 **Круглосуточная поддержка:**\\n"
                f"• {settings.crisis_hotline_ru}\\n\\n"
                "💙 Я здесь для поддержки, но специалисты смогут помочь вам лучше."
            )

        await update.message.reply_text(crisis_message)

        # Add recommended action if available
        if risk_assessment.get("recommended_action"):
            await update.message.reply_text(
                f"📋 **Рекомендация:** {risk_assessment['recommended_action']}"
            )

        # Transition to crisis state
        await self.state_manager.transition_to_crisis(user_id)

    async def privacy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /privacy command."""
        user_id = str(update.effective_user.id)

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="command",
            command="privacy"
        )

        privacy_message = (
            "🔐 Конфиденциальность и безопасность:\\n\\n"
            "• Все данные шифруются\\n"
            "• Личная информация автоматически удаляется\\n"
            "• Мы не сохраняем имена, адреса, телефоны\\n"
            "• Данные хранятся только на территории РФ\\n"
            "• Вы можете удалить все данные командой /delete\\n\\n"
            "⚠️ Исключения:\\n"
            "При угрозе жизни или здоровью мы обязаны "
            "передать информацию соответствующим службам.\\n\\n"
            "Подробнее: /privacy_policy"
        )

        await update.message.reply_text(privacy_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages with PII protection."""
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="text",
            message_length=len(message_text)
        )

        # Check for PII in message
        pii_detected = False
        if self.pii_protector and hasattr(self.pii_protector, 'analyzer'):
            try:
                pii_entities = await self.pii_protector.detect_pii(message_text, language="ru")
                if pii_entities:
                    pii_detected = True
                    logger.warning(
                        "pii_detected_in_message",
                        user_id=user_id,
                        entity_types=[entity.entity_type for entity in pii_entities]
                    )

                    # Warn user about PII
                    await update.message.reply_text(
                        "⚠️ Я заметил, что вы поделились личной информацией "
                        "(имена, телефоны, адреса и т.д.).\n\n"
                        "Для вашей безопасности рекомендую избегать указания "
                        "конкретных личных данных в наших разговорах.\n\n"
                        "Продолжаю обработку вашего сообщения..."
                    )
            except Exception as e:
                logger.error("pii_detection_failed", error=str(e))

        # Check for crisis signals using comprehensive risk assessment
        risk_assessment = await self.crisis_detector.analyze_risk_factors(
            message_text,
            user_history={"user_id": user_id}
        )

        # Check if immediate intervention is required
        if risk_assessment.get("immediate_intervention_required", False):
            # Log safety event
            from src.core.logger import log_safety_event
            log_safety_event(
                logger,
                event_type="crisis_detected",
                severity=risk_assessment.get("risk_level", "critical"),
                user_id=user_id,
                confidence=risk_assessment.get("confidence_scores", {}).get("suicide", 0.0),
                risk_level=risk_assessment.get("risk_level"),
                recommended_action=risk_assessment.get("recommended_action")
            )

            # Send crisis response with appropriate protocol
            crisis_protocol = risk_assessment.get("crisis_protocol_type", "suicide_prevention")
            await self._send_crisis_response(update, context, crisis_protocol, risk_assessment)
            return

        # For high (but not critical) risk, pass risk context to state manager
        if risk_assessment.get("risk_level") in ["high", "moderate"]:
            # Store risk assessment in context for state manager
            context.user_data["risk_assessment"] = risk_assessment

        # Process message through state manager
        response = await self.state_manager.process_message(user_id, message_text)

        # Send response
        await update.message.reply_text(response)

    async def setup_bot_commands(self, app: Application) -> None:
        """Set up bot commands for Telegram menu."""
        commands = [
            BotCommand("start", "Начать диалог"),
            BotCommand("help", "Помощь"),
            BotCommand("progress", "Прогресс восстановления"),
            BotCommand("letter", "Написать письмо"),
            BotCommand("letters", "Мои письма"),
            BotCommand("goals", "Мои цели"),
            BotCommand("resources", "Полезные ресурсы"),
            BotCommand("crisis", "Экстренная помощь"),
            BotCommand("privacy", "Конфиденциальность"),
        ]
        await app.bot.set_my_commands(commands)

    def setup_handlers(self, app: Application) -> None:
        """Set up message and command handlers."""
        # Command handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("progress", self.progress_command))
        app.add_handler(CommandHandler("letter", self.letter_command))
        app.add_handler(CommandHandler("letters", self.letters_command))
        app.add_handler(CommandHandler("goals", self.goals_command))
        app.add_handler(CommandHandler("crisis", self.crisis_command))
        app.add_handler(CommandHandler("privacy", self.privacy_command))

        # Message handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def initialize(self) -> None:
        """Initialize bot and dependencies."""
        # Setup logging
        setup_logging(settings.log_level)

        # Create application
        logger.info("creating_telegram_application")
        self.app = Application.builder().token(
            settings.telegram_bot_token.get_secret_value()
        ).build()
        logger.info("telegram_application_created")

        # Setup handlers
        logger.info("setting_up_handlers")
        self.setup_handlers(self.app)
        logger.info("handlers_setup_complete")

        # Setup bot commands
        # TEMPORARILY DISABLED - May be hanging during Telegram API call
        # await self.setup_bot_commands(self.app)

        # Initialize components
        logger.info("about_to_init_crisis_detector")
        await self.crisis_detector.initialize()
        logger.info("about_to_init_state_manager")
        await self.state_manager.initialize()
        logger.info("state_manager_init_completed")

        # Initialize PII protector (optional)
        # TEMPORARILY DISABLED - Hangs during Spacy model loading
        # try:
        #     await self.pii_protector.initialize()
        #     logger.info("pii_protector_enabled")
        # except Exception as e:
        #     logger.warning("pii_protector_disabled", reason=str(e))
        logger.warning("pii_protector_disabled", reason="Temporarily disabled due to model loading hang")

        logger.info("about_to_complete_initialization")
        logger.info("bot_initialized", environment=settings.environment)
        logger.info("initialization_complete")

    async def run_polling(self) -> None:
        """Run bot in polling mode (development)."""
        if not self.app:
            await self.initialize()

        logger.info("bot_starting", mode="polling")

        # Start polling
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

        logger.info("bot_running", mode="polling")

        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("bot_stopping", reason="keyboard_interrupt")
        finally:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()

    async def run_webhook(self, webhook_url: str, port: int = 8000) -> None:
        """Run bot in webhook mode (production)."""
        if not self.app:
            await self.initialize()

        logger.info("bot_starting", mode="webhook", url=webhook_url)

        # Set webhook
        await self.app.bot.set_webhook(webhook_url)

        # Start webhook
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=settings.telegram_bot_token.get_secret_value(),
            webhook_url=webhook_url,
        )

        logger.info("bot_running", mode="webhook", port=port)

        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("bot_stopping", reason="keyboard_interrupt")
        finally:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()


# Create bot instance
bot = PASBot()