"""Enhanced letter writing system with Telegraph, toxicity checking, and voice dictation."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from src.letters.types import LetterType, LetterStage, get_letter_type_description, should_check_toxicity, get_toxicity_threshold
from src.letters.biff_transformer import BIFFTransformer
from src.letters.nvc_transformer import NVCTransformer
from src.letters.validator import LetterValidator
from src.letters.toxicity_checker import ToxicityChecker, ToxicityAnalysis
from src.integrations.telegraph_client import TelegraphClient
from src.nlp.speech_handler import SpeechHandler
from src.core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class LetterSession:
    """Letter writing session state."""
    user_id: str
    letter_type: LetterType
    stage: LetterStage
    purpose: str = ""  # schedule_change, information_request, boundary, etc.
    style: str = "biff"  # biff or nvc

    # Content
    draft: str = ""
    transcribed_text: str = ""  # From voice
    transformed: str = ""

    # Toxicity analysis
    toxicity_analysis: Optional[ToxicityAnalysis] = None
    user_acknowledged_toxicity: bool = False

    # Telegraph
    telegraph_url: Optional[str] = None
    telegraph_path: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    is_complete: bool = False


class EnhancedLetterWriter:
    """
    Enhanced letter writing with:
    - 3 letter types (for_sending, time_capsule, therapeutic)
    - Toxicity checking (Detoxify + LLM)
    - Telegraph integration for editing
    - Voice dictation support
    """

    def __init__(self):
        """Initialize enhanced letter writer."""
        self.biff = BIFFTransformer()
        self.nvc = NVCTransformer()
        self.validator = LetterValidator()
        self.toxicity_checker = ToxicityChecker()
        self.telegraph = TelegraphClient()
        self.speech_handler = SpeechHandler(backend='google', language='ru-RU')

        self.sessions: Dict[str, LetterSession] = {}
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize all components."""
        if self.initialized:
            return

        # Initialize toxicity checker
        try:
            await self.toxicity_checker.initialize()
            logger.info("toxicity_checker_initialized")
        except Exception as e:
            logger.warning("toxicity_checker_init_failed", error=str(e))

        # Initialize Telegraph
        try:
            await self.telegraph.initialize()
            logger.info("telegraph_initialized")
        except Exception as e:
            logger.warning("telegraph_init_failed", error=str(e))

        # Initialize speech handler (optional)
        try:
            if self.speech_handler.is_available():
                await self.speech_handler.initialize()
                logger.info("speech_handler_initialized")
        except Exception as e:
            logger.warning("speech_handler_init_failed", error=str(e))

        self.initialized = True

    async def start_letter(
        self,
        user_id: str,
        letter_type: LetterType,
        purpose: str = "",
        style: str = "biff"
    ) -> str:
        """
        Start guided letter writing session.

        Args:
            user_id: User ID
            letter_type: Type of letter (for_sending/time_capsule/therapeutic)
            purpose: Letter purpose
            style: biff or nvc

        Returns:
            Guidance message
        """
        if not self.initialized:
            await self.initialize()

        session = LetterSession(
            user_id=user_id,
            letter_type=letter_type,
            stage=LetterStage.INIT,
            purpose=purpose,
            style=style
        )
        self.sessions[user_id] = session

        # Get type description
        type_desc = get_letter_type_description(letter_type)

        # Get style template
        if style == "biff":
            template = self.biff.get_biff_template(purpose or "information_request")
            style_guide = """
**BIFF принципы:**
• Brief (Кратко) - не более 200 слов
• Informative (Информативно) - конкретные факты
• Friendly (Дружелюбно) - вежливый тон
• Firm (Твёрдо) - чёткие границы
"""
        else:
            template = self.nvc.transform("").get('nvc_template', '')
            style_guide = """
**NVC структура:**
1. Наблюдение (объективные факты)
2. Чувство (ваши эмоции)
3. Потребность (что для вас важно)
4. Просьба (конкретная и выполнимая)
"""

        guidance = f"""
{type_desc}

{style_guide}

**Шаблон:**
{template}

**Как начать:**
• Печатайте текст письма
• Или 🎤 Отправьте голосовое сообщение для надиктовки
"""

        session.stage = LetterStage.DRAFT
        return guidance

    async def process_voice(
        self,
        user_id: str,
        audio_path: Path
    ) -> Dict[str, Any]:
        """
        Process voice dictation for letter.

        Args:
            user_id: User ID
            audio_path: Path to voice message

        Returns:
            {
                "success": bool,
                "transcription": str,
                "preview": str  # For user confirmation
            }
        """
        session = self.sessions.get(user_id)
        if not session:
            return {"success": False, "error": "No active letter session"}

        if not self.speech_handler or not self.speech_handler.is_available():
            return {
                "success": False,
                "error": "Speech-to-text not available. Please type your letter."
            }

        try:
            # Transcribe voice
            transcription = await self.speech_handler.transcribe_telegram_voice(audio_path)

            if not transcription:
                return {
                    "success": False,
                    "error": "Could not transcribe voice. Please try again or type."
                }

            session.transcribed_text = transcription
            session.stage = LetterStage.TRANSCRIPTION

            logger.info("voice_transcribed",
                       user_id=user_id,
                       length=len(transcription))

            preview = transcription[:500] + "..." if len(transcription) > 500 else transcription

            return {
                "success": True,
                "transcription": transcription,
                "preview": preview
            }

        except Exception as e:
            logger.error("voice_processing_failed", user_id=user_id, error=str(e))
            return {
                "success": False,
                "error": f"Voice processing failed: {str(e)}"
            }

    async def process_draft(
        self,
        user_id: str,
        draft_text: str
    ) -> Dict[str, Any]:
        """
        Process letter draft with toxicity checking.

        Args:
            user_id: User ID
            draft_text: Draft letter text

        Returns:
            {
                "success": bool,
                "toxicity_analysis": ToxicityAnalysis (if applicable),
                "requires_review": bool,
                "message": str
            }
        """
        session = self.sessions.get(user_id)
        if not session:
            return {"success": False, "error": "No active letter session"}

        session.draft = draft_text
        session.stage = LetterStage.TOXICITY_CHECK

        # Check if toxicity analysis needed
        if not should_check_toxicity(session.letter_type):
            # Therapeutic letter - skip checks
            return await self._create_telegraph(user_id)

        # Run toxicity analysis
        try:
            threshold = get_toxicity_threshold(session.letter_type)
            analysis = await self.toxicity_checker.analyze(
                draft_text,
                threshold=threshold,
                use_llm=True  # Use LLM for detailed recommendations
            )

            session.toxicity_analysis = analysis

            if analysis.is_toxic:
                # Requires user review
                session.stage = LetterStage.REVIEW_WARNINGS

                warnings = self.toxicity_checker.format_warnings(analysis)

                return {
                    "success": True,
                    "toxicity_analysis": analysis,
                    "requires_review": True,
                    "message": f"""
{warnings}

**Что делать:**
• Отредактировать письмо (рекомендуется)
• Сохранить как есть (я понимаю риски)

{self._get_type_specific_warning(session.letter_type)}
"""
                }
            else:
                # Clean letter - proceed to Telegraph
                return await self._create_telegraph(user_id)

        except Exception as e:
            logger.error("toxicity_check_failed", user_id=user_id, error=str(e))
            # Continue anyway (graceful degradation)
            return await self._create_telegraph(user_id)

    def _get_type_specific_warning(self, letter_type: LetterType) -> str:
        """Get type-specific warning for toxic content."""
        warnings = {
            LetterType.FOR_SENDING: """
⚠️ **Важно:** Это письмо будет отправлено другому человеку.
Токсичные фразы могут:
• Ухудшить конфликт
• Быть использованы против вас в суде
• Навредить отношениям с ребёнком
            """,
            LetterType.TIME_CAPSULE: """
⚠️ **Важно:** Ребёнок прочитает это письмо в будущем.
Токсичные фразы могут:
• Навредить психике ребёнка
• Создать конфликт лояльности
• Разрушить доверие к вам

💡 Рекомендую переписать эти части более нейтрально.
            """,
            LetterType.THERAPEUTIC: ""
        }
        return warnings.get(letter_type, "")

    async def acknowledge_toxicity(
        self,
        user_id: str,
        proceed_anyway: bool = False
    ) -> Dict[str, Any]:
        """
        User acknowledged toxicity warnings.

        Args:
            user_id: User ID
            proceed_anyway: If True, save toxic version anyway

        Returns:
            Result dictionary
        """
        session = self.sessions.get(user_id)
        if not session:
            return {"success": False, "error": "No active session"}

        session.user_acknowledged_toxicity = proceed_anyway

        if proceed_anyway:
            # User chose to keep toxic content
            logger.info("user_accepted_toxic_content",
                       user_id=user_id,
                       letter_type=session.letter_type.value)
            return await self._create_telegraph(user_id)
        else:
            # User will edit
            return {
                "success": True,
                "message": "Отправьте отредактированную версию письма."
            }

    async def _create_telegraph(self, user_id: str) -> Dict[str, Any]:
        """Create Telegraph article for letter."""
        session = self.sessions.get(user_id)
        if not session:
            return {"success": False, "error": "No session"}

        if not self.telegraph or not self.telegraph.is_available():
            # Telegraph not available - save locally only
            session.is_complete = True
            return {
                "success": True,
                "message": "Письмо сохранено локально (Telegraph недоступен)",
                "draft": session.draft
            }

        try:
            # Create Telegraph article
            result = await self.telegraph.create_letter(
                title=f"Письмо: {session.letter_type.value}",
                content=session.draft,
                author_name="Анонимный автор"
            )

            session.telegraph_url = result['url']
            session.telegraph_path = result['path']
            session.stage = LetterStage.FINALIZE
            session.is_complete = True

            logger.info("telegraph_letter_created",
                       user_id=user_id,
                       url=result['url'])

            # Privacy warning
            privacy_warning = """
⚠️ **Безопасность:**
• Не делитесь ссылкой публично
• Ссылка работает как пароль - кто знает, тот может прочитать
• Для конфиденциальных данных используйте экспорт в PDF
"""

            return {
                "success": True,
                "telegraph_url": result['url'],
                "message": f"""
✅ Письмо создано!

🔗 **Ссылка для редактирования:**
{result['url']}

Вы можете продолжить редактирование в удобном редакторе Telegraph.
Все изменения автоматически сохраняются.

{privacy_warning}

Используйте /my_letters чтобы вернуться к этому письму позже.
"""
            }

        except Exception as e:
            logger.error("telegraph_creation_failed", user_id=user_id, error=str(e))
            session.is_complete = True
            return {
                "success": True,
                "message": "Письмо сохранено локально (Telegraph недоступен)",
                "draft": session.draft
            }

    def get_session(self, user_id: str) -> Optional[LetterSession]:
        """Get active letter session."""
        return self.sessions.get(user_id)

    def clear_session(self, user_id: str) -> None:
        """Clear letter session."""
        if user_id in self.sessions:
            del self.sessions[user_id]
