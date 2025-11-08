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


logger = get_logger(__name__)


class PASBot:
    """Main bot class for PAS (Parental Alienation Support) Bot."""

    def __init__(self):
        """Initialize the bot."""
        self.app: Optional[Application] = None
        self.crisis_detector = CrisisDetector()
        self.state_manager = StateManager()

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
            "/letter - Начать написание письма\\n"
            "/goals - Посмотреть ваши цели\\n"
            "/resources - Полезные ресурсы\\n"
            "/crisis - Экстренная помощь\\n"
            "/privacy - Информация о конфиденциальности\\n\\n"
            "Вы можете просто написать мне о том, что вас беспокоит."
        )

        await update.message.reply_text(help_text)

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
        """Handle regular text messages."""
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text

        log_user_interaction(
            logger,
            user_id=user_id,
            message_type="text",
            message_length=len(message_text)
        )

        # Check for crisis signals
        is_crisis, confidence = await self.crisis_detector.detect(message_text)

        if is_crisis and confidence > settings.suicidalbert_threshold:
            # Log safety event
            from src.core.logger import log_safety_event
            log_safety_event(
                logger,
                event_type="crisis_detected",
                severity="critical",
                user_id=user_id,
                confidence=confidence
            )

            # Send crisis response
            await self.crisis_command(update, context)
            return

        # Process message through state manager
        response = await self.state_manager.process_message(user_id, message_text)

        # Send response
        await update.message.reply_text(response)

    async def setup_bot_commands(self, app: Application) -> None:
        """Set up bot commands for Telegram menu."""
        commands = [
            BotCommand("start", "Начать диалог"),
            BotCommand("help", "Помощь"),
            BotCommand("letter", "Написать письмо"),
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
        app.add_handler(CommandHandler("crisis", self.crisis_command))
        app.add_handler(CommandHandler("privacy", self.privacy_command))

        # Message handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def initialize(self) -> None:
        """Initialize bot and dependencies."""
        # Setup logging
        setup_logging(settings.log_level)

        # Create application
        self.app = Application.builder().token(
            settings.telegram_bot_token.get_secret_value()
        ).build()

        # Setup handlers
        self.setup_handlers(self.app)

        # Setup bot commands
        await self.setup_bot_commands(self.app)

        # Initialize components
        await self.crisis_detector.initialize()
        await self.state_manager.initialize()

        logger.info("bot_initialized", environment=settings.environment)

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