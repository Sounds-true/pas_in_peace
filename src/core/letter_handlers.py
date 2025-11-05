"""Telegram bot handlers for letter writing feature.

Commands:
- /write_letter - Start writing a new letter
- /my_letters - View all user's letters
- Voice messages - Dictate letter content
"""

from typing import Optional
from pathlib import Path
import tempfile

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import ContextTypes, ConversationHandler
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

from src.letters import EnhancedLetterWriter, LetterType, get_letter_type_description
from src.storage.database import DatabaseManager
from src.core.logger import get_logger


logger = get_logger(__name__)


# Conversation states
CHOOSING_TYPE, WRITING_DRAFT, REVIEWING_TOXICITY = range(3)


class LetterHandlers:
    """Telegram handlers for letter writing."""

    def __init__(self, db: DatabaseManager):
        """Initialize letter handlers."""
        self.db = db
        self.letter_writer = EnhancedLetterWriter()

    async def initialize(self):
        """Initialize letter writer."""
        await self.letter_writer.initialize()

    async def cmd_write_letter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /write_letter command."""
        user = update.effective_user

        # Show letter type selection
        keyboard = [
            [InlineKeyboardButton("📤 Для отправки", callback_data="letter_type_for_sending")],
            [InlineKeyboardButton("🎁 Капсула для ребёнка", callback_data="letter_type_time_capsule")],
            [InlineKeyboardButton("💭 Терапевтическое (для себя)", callback_data="letter_type_therapeutic")],
            [InlineKeyboardButton("❌ Отмена", callback_data="letter_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            """
📝 **Написать письмо**

Выберите тип письма:

**📤 Для отправки** - бывшему партнёру, школе, суду
**🎁 Капсула для ребёнка** - письмо на будущее
**💭 Терапевтическое** - для выражения эмоций (не для отправки)

Что вы хотите написать?
            """,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        return CHOOSING_TYPE

    async def callback_letter_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle letter type selection."""
        query = update.callback_query
        await query.answer()

        user_id = str(query.from_user.id)
        callback_data = query.data

        if callback_data == "letter_cancel":
            await query.edit_message_text("Отменено.")
            return ConversationHandler.END

        # Parse letter type
        letter_type_map = {
            "letter_type_for_sending": LetterType.FOR_SENDING,
            "letter_type_time_capsule": LetterType.TIME_CAPSULE,
            "letter_type_therapeutic": LetterType.THERAPEUTIC
        }

        letter_type = letter_type_map.get(callback_data)
        if not letter_type:
            await query.edit_message_text("Ошибка: неверный тип письма")
            return ConversationHandler.END

        # Start letter session
        try:
            guidance = await self.letter_writer.start_letter(
                user_id=user_id,
                letter_type=letter_type,
                style="biff"  # Default to BIFF
            )

            await query.edit_message_text(
                guidance,
                parse_mode='Markdown'
            )

            return WRITING_DRAFT

        except Exception as e:
            logger.error("letter_start_failed", user_id=user_id, error=str(e))
            await query.edit_message_text(
                f"Ошибка при создании письма: {str(e)}"
            )
            return ConversationHandler.END

    async def handle_draft_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle draft text input."""
        user_id = str(update.effective_user.id)
        text = update.message.text

        try:
            result = await self.letter_writer.process_draft(user_id, text)

            if not result.get('success'):
                await update.message.reply_text(
                    f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}"
                )
                return WRITING_DRAFT

            if result.get('requires_review'):
                # Toxicity warnings - show options
                keyboard = [
                    [InlineKeyboardButton("✍️ Отредактировать", callback_data="letter_edit")],
                    [InlineKeyboardButton("💾 Сохранить как есть", callback_data="letter_save_toxic")],
                    [InlineKeyboardButton("❌ Отмена", callback_data="letter_cancel")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    result['message'],
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )

                return REVIEWING_TOXICITY

            else:
                # Clean letter or telegraph created
                await update.message.reply_text(
                    result['message'],
                    parse_mode='Markdown'
                )

                # Save to database
                await self._save_letter_to_db(user_id)

                return ConversationHandler.END

        except Exception as e:
            logger.error("draft_processing_failed", user_id=user_id, error=str(e))
            await update.message.reply_text(
                f"Ошибка при обработке письма: {str(e)}"
            )
            return ConversationHandler.END

    async def handle_draft_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice message for letter dictation."""
        user_id = str(update.effective_user.id)

        # Download voice file
        voice = update.message.voice
        voice_file = await voice.get_file()

        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
            await voice_file.download_to_drive(tmp.name)
            audio_path = Path(tmp.name)

        try:
            # Process voice
            result = await self.letter_writer.process_voice(user_id, audio_path)

            if not result.get('success'):
                await update.message.reply_text(
                    f"❌ {result.get('error')}"
                )
                return WRITING_DRAFT

            # Show transcription for confirmation
            keyboard = [
                [InlineKeyboardButton("✅ Да, всё верно", callback_data="voice_confirm")],
                [InlineKeyboardButton("✍️ Редактировать", callback_data="voice_edit")],
                [InlineKeyboardButton("🔄 Переписать", callback_data="voice_retry")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"""
🎤 **Распознано:**

{result['preview']}

Всё верно?
                """,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

            # Store transcription in context
            context.user_data['transcription'] = result['transcription']

            return WRITING_DRAFT

        except Exception as e:
            logger.error("voice_processing_failed", user_id=user_id, error=str(e))
            await update.message.reply_text(
                f"Ошибка обработки голоса: {str(e)}"
            )
            return WRITING_DRAFT
        finally:
            # Cleanup temp file
            audio_path.unlink(missing_ok=True)

    async def callback_voice_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice transcription confirmation."""
        query = update.callback_query
        await query.answer()

        user_id = str(query.from_user.id)
        transcription = context.user_data.get('transcription')

        if not transcription:
            await query.edit_message_text("Ошибка: транскрипция не найдена")
            return ConversationHandler.END

        # Process as draft
        try:
            result = await self.letter_writer.process_draft(user_id, transcription)

            if result.get('requires_review'):
                keyboard = [
                    [InlineKeyboardButton("✍️ Отредактировать", callback_data="letter_edit")],
                    [InlineKeyboardButton("💾 Сохранить", callback_data="letter_save_toxic")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    result['message'],
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )

                return REVIEWING_TOXICITY

            else:
                await query.edit_message_text(
                    result['message'],
                    parse_mode='Markdown'
                )

                await self._save_letter_to_db(user_id)

                return ConversationHandler.END

        except Exception as e:
            logger.error("voice_confirmation_failed", error=str(e))
            await query.edit_message_text(f"Ошибка: {str(e)}")
            return ConversationHandler.END

    async def callback_toxicity_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle toxicity review callbacks."""
        query = update.callback_query
        await query.answer()

        user_id = str(query.from_user.id)
        action = query.data

        if action == "letter_edit":
            await query.edit_message_text(
                "Отправьте отредактированную версию письма."
            )
            return WRITING_DRAFT

        elif action == "letter_save_toxic":
            # User chose to keep toxic content
            try:
                result = await self.letter_writer.acknowledge_toxicity(
                    user_id, proceed_anyway=True
                )

                await query.edit_message_text(
                    result.get('message', 'Письмо сохранено'),
                    parse_mode='Markdown'
                )

                await self._save_letter_to_db(user_id)

                return ConversationHandler.END

            except Exception as e:
                logger.error("toxicity_acknowledgment_failed", error=str(e))
                await query.edit_message_text(f"Ошибка: {str(e)}")
                return ConversationHandler.END

        elif action == "letter_cancel":
            self.letter_writer.clear_session(user_id)
            await query.edit_message_text("Отменено.")
            return ConversationHandler.END

    async def cmd_my_letters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /my_letters command - show user's letters."""
        user = update.effective_user

        try:
            # Get letters from DB
            letters = await self.db.get_user_letters(user.id)

            if not letters:
                await update.message.reply_text(
                    "У вас пока нет писем.\n\nИспользуйте /write_letter чтобы создать."
                )
                return

            # Build keyboard with letters
            keyboard = []
            for letter in letters[:10]:  # Show max 10
                icon = {
                    'for_sending': '📤',
                    'time_capsule': '🎁',
                    'therapeutic': '💭'
                }.get(letter.letter_type, '📝')

                keyboard.append([
                    InlineKeyboardButton(
                        f"{icon} {letter.title or 'Без названия'}",
                        callback_data=f"view_letter_{letter.id}"
                    )
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"📬 **Ваши письма ({len(letters)}):**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error("my_letters_failed", user_id=user.id, error=str(e))
            await update.message.reply_text(
                f"Ошибка при загрузке писем: {str(e)}"
            )

    async def _save_letter_to_db(self, user_id: str):
        """Save letter session to database."""
        session = self.letter_writer.get_session(user_id)
        if not session:
            return

        try:
            # Create letter in DB
            letter = await self.db.create_letter(
                user_id=int(user_id),
                title=f"Письмо от {session.created_at.strftime('%d.%m.%Y')}",
                recipient_role="",
                purpose=session.purpose,
                letter_type=session.letter_type.value,
                draft_content=session.draft,
                communication_style=session.style,
                toxicity_score=session.toxicity_analysis.overall_score if session.toxicity_analysis else None,
                toxicity_details=session.toxicity_analysis.__dict__ if session.toxicity_analysis else {},
                toxicity_warnings_ignored=session.user_acknowledged_toxicity,
                telegraph_url=session.telegraph_url,
                telegraph_path=session.telegraph_path,
                status='draft'
            )

            logger.info("letter_saved_to_db",
                       user_id=user_id,
                       letter_id=letter.id,
                       type=session.letter_type.value)

            # Clear session
            self.letter_writer.clear_session(user_id)

        except Exception as e:
            logger.error("letter_db_save_failed", user_id=user_id, error=str(e))

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel letter writing."""
        user_id = str(update.effective_user.id)
        self.letter_writer.clear_session(user_id)

        await update.message.reply_text("Создание письма отменено.")
        return ConversationHandler.END
