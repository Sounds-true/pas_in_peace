"""Speech-to-text handler for voice messages."""

from typing import Optional, Dict, Any, TYPE_CHECKING
from pathlib import Path
import asyncio
from dataclasses import dataclass

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    if TYPE_CHECKING:
        import speech_recognition as sr

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

from src.core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class TranscriptionResult:
    """Speech transcription result."""
    text: str
    confidence: float
    language: str
    duration_seconds: float
    backend: str  # 'google', 'sphinx', 'whisper', etc.


class SpeechHandler:
    """
    Handle voice message transcription.

    Supports multiple backends:
    - Google Speech Recognition (free, requires internet)
    - Sphinx (offline, lower accuracy)
    - Whisper (future: OpenAI Whisper for best accuracy)
    """

    def __init__(self, backend: str = 'google', language: str = 'ru-RU'):
        """
        Initialize speech handler.

        Args:
            backend: 'google', 'sphinx', or 'whisper'
            language: Language code (default: Russian)
        """
        self.backend = backend
        self.language = language
        self.recognizer = None
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize speech recognition."""
        if self.initialized:
            return True

        if not SPEECH_RECOGNITION_AVAILABLE:
            logger.warning("speech_recognition_not_installed",
                          message="Install: pip install SpeechRecognition")
            return False

        try:
            self.recognizer = sr.Recognizer()

            # Configure recognizer
            self.recognizer.energy_threshold = 300  # Adjust for noise
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8  # Seconds of silence

            self.initialized = True
            logger.info("speech_handler_initialized", backend=self.backend)
            return True

        except Exception as e:
            logger.error("speech_handler_init_failed", error=str(e))
            return False

    async def transcribe_voice_message(
        self,
        audio_path: Path,
        convert_format: bool = True
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe voice message to text.

        Args:
            audio_path: Path to audio file (ogg, mp3, wav, etc.)
            convert_format: Auto-convert to WAV if needed

        Returns:
            TranscriptionResult or None if failed
        """
        if not self.initialized:
            if not await self.initialize():
                return None

        try:
            # Convert to WAV if needed
            if audio_path.suffix.lower() != '.wav':
                if convert_format and PYDUB_AVAILABLE:
                    audio_path = await self._convert_to_wav(audio_path)
                else:
                    logger.warning("audio_conversion_skipped",
                                  format=audio_path.suffix,
                                  message="Install pydub: pip install pydub")

            # Load audio file
            with sr.AudioFile(str(audio_path)) as source:
                # Record audio data
                audio_data = self.recognizer.record(source)

                # Get duration
                duration = len(audio_data.frame_data) / (
                    audio_data.sample_rate * audio_data.sample_width
                )

            # Transcribe based on backend
            if self.backend == 'google':
                result = await self._transcribe_google(audio_data, duration)
            elif self.backend == 'sphinx':
                result = await self._transcribe_sphinx(audio_data, duration)
            elif self.backend == 'whisper':
                result = await self._transcribe_whisper(audio_data, duration)
            else:
                logger.error("unknown_backend", backend=self.backend)
                return None

            if result:
                logger.info("voice_transcribed",
                           text_length=len(result.text),
                           duration=result.duration_seconds,
                           backend=result.backend)

            return result

        except sr.UnknownValueError:
            logger.warning("speech_not_understood")
            return None
        except sr.RequestError as e:
            logger.error("speech_recognition_request_failed", error=str(e))
            return None
        except Exception as e:
            logger.error("voice_transcription_failed", error=str(e))
            return None

    async def _transcribe_google(
        self,
        audio_data: "sr.AudioData",
        duration: float
    ) -> Optional[TranscriptionResult]:
        """Transcribe using Google Speech Recognition (free)."""
        try:
            # Run in thread pool (blocking call)
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                lambda: self.recognizer.recognize_google(
                    audio_data,
                    language=self.language,
                    show_all=False
                )
            )

            return TranscriptionResult(
                text=text,
                confidence=0.85,  # Google doesn't return confidence in free API
                language=self.language,
                duration_seconds=duration,
                backend='google'
            )

        except Exception as e:
            logger.error("google_transcription_failed", error=str(e))
            return None

    async def _transcribe_sphinx(
        self,
        audio_data: "sr.AudioData",
        duration: float
    ) -> Optional[TranscriptionResult]:
        """Transcribe using Sphinx (offline)."""
        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                lambda: self.recognizer.recognize_sphinx(
                    audio_data,
                    language=self.language
                )
            )

            return TranscriptionResult(
                text=text,
                confidence=0.6,  # Sphinx has lower accuracy
                language=self.language,
                duration_seconds=duration,
                backend='sphinx'
            )

        except Exception as e:
            logger.error("sphinx_transcription_failed", error=str(e))
            return None

    async def _transcribe_whisper(
        self,
        audio_data: "sr.AudioData",
        duration: float
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe using OpenAI Whisper (future implementation).

        Requires: pip install openai-whisper
        """
        logger.warning("whisper_not_implemented",
                      message="Use 'google' or 'sphinx' backend for now")
        return None

    async def _convert_to_wav(self, audio_path: Path) -> Path:
        """Convert audio file to WAV format."""
        if not PYDUB_AVAILABLE:
            raise ImportError("pydub not available")

        try:
            # Load audio
            audio = AudioSegment.from_file(str(audio_path))

            # Export as WAV
            wav_path = audio_path.with_suffix('.wav')
            audio.export(str(wav_path), format='wav')

            logger.info("audio_converted",
                       from_format=audio_path.suffix,
                       to_format='.wav')

            return wav_path

        except Exception as e:
            logger.error("audio_conversion_failed", error=str(e))
            raise

    async def transcribe_telegram_voice(
        self,
        voice_file_path: Path
    ) -> Optional[str]:
        """
        Convenience method for Telegram voice messages.

        Telegram sends voice as OGG Opus format.

        Returns:
            Transcribed text or None
        """
        result = await self.transcribe_voice_message(
            voice_file_path,
            convert_format=True
        )

        return result.text if result else None

    def is_available(self) -> bool:
        """Check if speech recognition is available."""
        return SPEECH_RECOGNITION_AVAILABLE

    def get_supported_backends(self) -> list:
        """Get list of supported backends."""
        backends = []
        if SPEECH_RECOGNITION_AVAILABLE:
            backends.append('google')
            try:
                import pocketsphinx
                backends.append('sphinx')
            except ImportError:
                pass

        return backends
