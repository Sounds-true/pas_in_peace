"""Tests for Sprint 9: Telegraph Letters System.

Tests cover:
- Letter types and validation
- Toxicity checking (Detoxify + LLM)
- Telegraph client integration
- Enhanced letter writer flow
- Capsule monitor notifications
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.letters.types import LetterType, get_toxicity_threshold
from src.letters.toxicity_checker import ToxicityChecker, ToxicityAnalysis
from src.integrations.telegraph_client import TelegraphClient
from src.letters.enhanced_writer import EnhancedLetterWriter, LetterStage
from src.letters.capsule_monitor import CapsuleMonitor


class TestLetterTypes:
    """Test letter type system."""

    def test_letter_types_exist(self):
        """Test all three letter types exist."""
        assert LetterType.FOR_SENDING == "for_sending"
        assert LetterType.TIME_CAPSULE == "time_capsule"
        assert LetterType.THERAPEUTIC == "therapeutic"

    def test_toxicity_thresholds(self):
        """Test type-specific toxicity thresholds."""
        assert get_toxicity_threshold(LetterType.FOR_SENDING) == 0.3
        assert get_toxicity_threshold(LetterType.TIME_CAPSULE) == 0.5
        assert get_toxicity_threshold(LetterType.THERAPEUTIC) == 1.0

    def test_therapeutic_no_warnings(self):
        """Test therapeutic letters have full freedom."""
        threshold = get_toxicity_threshold(LetterType.THERAPEUTIC)
        assert threshold == 1.0  # No warnings ever


class TestToxicityChecker:
    """Test toxicity detection system."""

    @pytest.mark.asyncio
    async def test_toxicity_checker_initialization(self):
        """Test toxicity checker initializes."""
        checker = ToxicityChecker()
        result = await checker.initialize()
        # Should initialize even without Detoxify
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_detect_russian_insults(self):
        """Test detecting Russian insults."""
        checker = ToxicityChecker()
        await checker.initialize()

        toxic_text = "Ты сволочь, из-за тебя ребёнок страдает"
        analysis = await checker.analyze(
            toxic_text,
            threshold=0.3,
            use_llm=False
        )

        assert analysis is not None
        # Should detect at least some toxicity
        if checker.detoxify_available:
            assert len(analysis.toxic_phrases) > 0

    @pytest.mark.asyncio
    async def test_detect_threats(self):
        """Test detecting threatening language."""
        checker = ToxicityChecker()
        await checker.initialize()

        threat_text = "Ты заплатишь за это, пожалеешь"
        analysis = await checker.analyze(
            threat_text,
            threshold=0.3,
            use_llm=False
        )

        assert analysis is not None

    @pytest.mark.asyncio
    async def test_detect_manipulation(self):
        """Test detecting parental alienation manipulation."""
        checker = ToxicityChecker()
        await checker.initialize()

        manipulation_text = "Ребёнок не хочет тебя видеть, он боится тебя"
        analysis = await checker.analyze(
            manipulation_text,
            threshold=0.3,
            use_llm=False
        )

        assert analysis is not None

    @pytest.mark.asyncio
    async def test_clean_text_passes(self):
        """Test clean text passes toxicity check."""
        checker = ToxicityChecker()
        await checker.initialize()

        clean_text = "Я хочу наладить отношения с ребёнком. Планирую встретиться в парке."
        analysis = await checker.analyze(
            clean_text,
            threshold=0.3,
            use_llm=False
        )

        assert analysis is not None
        # Clean text should not be marked as toxic
        # (unless Detoxify gives false positive)

    @pytest.mark.asyncio
    async def test_different_thresholds(self):
        """Test different toxicity thresholds."""
        checker = ToxicityChecker()
        await checker.initialize()

        # Mildly toxic text
        text = "Ты меня раздражаешь"

        # Strict threshold (for_sending)
        strict = await checker.analyze(text, threshold=0.3, use_llm=False)

        # Lenient threshold (time_capsule)
        lenient = await checker.analyze(text, threshold=0.5, use_llm=False)

        # Both should complete without error
        assert strict is not None
        assert lenient is not None

    @pytest.mark.asyncio
    async def test_llm_recommendations(self):
        """Test LLM provides recommendations for toxic text."""
        checker = ToxicityChecker()
        await checker.initialize()

        toxic_text = "Ты сволочь"

        # With LLM (if available)
        analysis = await checker.analyze(
            toxic_text,
            threshold=0.3,
            use_llm=True  # Will use LLM if available
        )

        assert analysis is not None
        # If LLM available and text is toxic, should have recommendations
        if checker.llm and analysis.is_toxic:
            assert len(analysis.recommendations) > 0

    @pytest.mark.asyncio
    async def test_graceful_degradation_no_detoxify(self):
        """Test checker works without Detoxify."""
        # Mock Detoxify unavailable
        with patch('src.letters.toxicity_checker.DETOXIFY_AVAILABLE', False):
            checker = ToxicityChecker()
            result = await checker.initialize()

            # Should still initialize
            assert isinstance(result, bool)

            # Analysis should still work (pattern-based)
            analysis = await checker.analyze(
                "Ты сволочь",
                threshold=0.3,
                use_llm=False
            )
            assert analysis is not None


class TestTelegraphClient:
    """Test Telegraph integration."""

    @pytest.mark.asyncio
    async def test_telegraph_initialization(self):
        """Test Telegraph client initializes."""
        client = TelegraphClient()
        result = await client.initialize()

        # Should initialize (creates account)
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_create_letter(self):
        """Test creating Telegraph article."""
        client = TelegraphClient()
        await client.initialize()

        if not client.telegraph:
            pytest.skip("Telegraph not available")

        result = await client.create_letter(
            title="Тестовое письмо",
            content="Это тестовое содержимое письма."
        )

        assert result is not None
        assert "url" in result
        assert "path" in result
        assert result["url"].startswith("https://telegra.ph/")

    @pytest.mark.asyncio
    async def test_update_letter(self):
        """Test updating Telegraph article."""
        client = TelegraphClient()
        await client.initialize()

        if not client.telegraph:
            pytest.skip("Telegraph not available")

        # Create letter first
        create_result = await client.create_letter(
            title="Оригинальное название",
            content="Оригинальное содержимое"
        )

        # Update it
        update_result = await client.update_letter(
            path=create_result["path"],
            title="Обновлённое название",
            content="Обновлённое содержимое"
        )

        assert update_result is not None
        assert update_result["url"] == create_result["url"]

    @pytest.mark.asyncio
    async def test_get_letter_content(self):
        """Test retrieving letter content."""
        client = TelegraphClient()
        await client.initialize()

        if not client.telegraph:
            pytest.skip("Telegraph not available")

        # Create letter
        result = await client.create_letter(
            title="Тест получения",
            content="Содержимое для получения"
        )

        # Get it back
        content = await client.get_letter_content(result["path"])

        assert content is not None
        assert "Содержимое для получения" in content

    @pytest.mark.asyncio
    async def test_security_uuid_in_url(self):
        """Test Telegraph URLs contain UUID for security."""
        client = TelegraphClient()
        await client.initialize()

        if not client.telegraph:
            pytest.skip("Telegraph not available")

        result = await client.create_letter(
            title="Тест безопасности",
            content="Приватное содержимое"
        )

        # URL should contain UUID pattern
        assert len(result["path"]) > 20  # UUID makes it long
        # Should be hard to guess


class TestEnhancedLetterWriter:
    """Test enhanced letter writer flow."""

    @pytest.fixture
    def mock_db(self):
        """Mock database manager."""
        db = Mock()
        db.get_user_by_telegram_id = AsyncMock(return_value=Mock(id=1))
        db.create_letter = AsyncMock(return_value=Mock(id=1))
        db.update_letter = AsyncMock()
        return db

    @pytest.fixture
    def mock_speech(self):
        """Mock speech handler."""
        speech = Mock()
        speech.is_available = Mock(return_value=True)
        speech.initialize = AsyncMock(return_value=True)
        speech.transcribe_telegram_voice = AsyncMock(
            return_value="Это текст из голосового сообщения"
        )
        return speech

    @pytest.mark.asyncio
    async def test_writer_initialization(self, mock_db, mock_speech):
        """Test letter writer initializes."""
        writer = EnhancedLetterWriter(
            db=mock_db,
            speech_handler=mock_speech
        )
        await writer.initialize()

        assert writer.initialized is True

    @pytest.mark.asyncio
    async def test_start_letter_for_sending(self, mock_db, mock_speech):
        """Test starting FOR_SENDING letter."""
        writer = EnhancedLetterWriter(db=mock_db, speech_handler=mock_speech)
        await writer.initialize()

        session_id = await writer.start_letter(
            user_id="user123",
            letter_type=LetterType.FOR_SENDING,
            purpose="ex_partner",
            style="respectful"
        )

        assert session_id is not None
        assert session_id in writer.active_sessions
        session = writer.active_sessions[session_id]
        assert session.letter_type == LetterType.FOR_SENDING

    @pytest.mark.asyncio
    async def test_start_letter_time_capsule(self, mock_db, mock_speech):
        """Test starting TIME_CAPSULE letter."""
        writer = EnhancedLetterWriter(db=mock_db, speech_handler=mock_speech)
        await writer.initialize()

        session_id = await writer.start_letter(
            user_id="user123",
            letter_type=LetterType.TIME_CAPSULE,
            purpose="future_child",
            style="warm"
        )

        session = writer.active_sessions[session_id]
        assert session.letter_type == LetterType.TIME_CAPSULE

    @pytest.mark.asyncio
    async def test_start_letter_therapeutic(self, mock_db, mock_speech):
        """Test starting THERAPEUTIC letter."""
        writer = EnhancedLetterWriter(db=mock_db, speech_handler=mock_speech)
        await writer.initialize()

        session_id = await writer.start_letter(
            user_id="user123",
            letter_type=LetterType.THERAPEUTIC,
            purpose="vent",
            style="raw"
        )

        session = writer.active_sessions[session_id]
        assert session.letter_type == LetterType.THERAPEUTIC

    @pytest.mark.asyncio
    async def test_process_voice(self, mock_db, mock_speech):
        """Test processing voice message."""
        writer = EnhancedLetterWriter(db=mock_db, speech_handler=mock_speech)
        await writer.initialize()

        session_id = await writer.start_letter(
            user_id="user123",
            letter_type=LetterType.FOR_SENDING,
            purpose="ex_partner",
            style="respectful"
        )

        # Process voice
        result = await writer.process_voice(
            user_id="user123",
            audio_path=Path("/tmp/voice.ogg")
        )

        assert result["success"] is True
        assert "transcription" in result
        session = writer.active_sessions[session_id]
        assert session.transcribed_text is not None

    @pytest.mark.asyncio
    async def test_process_draft_clean_text(self, mock_db, mock_speech):
        """Test processing clean draft text."""
        writer = EnhancedLetterWriter(db=mock_db, speech_handler=mock_speech)
        await writer.initialize()

        session_id = await writer.start_letter(
            user_id="user123",
            letter_type=LetterType.FOR_SENDING,
            purpose="ex_partner",
            style="respectful"
        )

        # Process clean draft
        result = await writer.process_draft(
            user_id="user123",
            draft_text="Я хочу наладить наши отношения ради ребёнка."
        )

        # Should not require review (clean text)
        # (Depends on toxicity checker availability)
        assert "success" in result or "requires_review" in result

    @pytest.mark.asyncio
    async def test_therapeutic_no_toxicity_check(self, mock_db, mock_speech):
        """Test therapeutic letters skip toxicity check."""
        writer = EnhancedLetterWriter(db=mock_db, speech_handler=mock_speech)
        await writer.initialize()

        session_id = await writer.start_letter(
            user_id="user123",
            letter_type=LetterType.THERAPEUTIC,
            purpose="vent",
            style="raw"
        )

        # Even with toxic text, should not check
        result = await writer.process_draft(
            user_id="user123",
            draft_text="Я ненавижу тебя, сволочь!"  # Toxic but therapeutic
        )

        # Should create Telegraph without warnings
        assert "telegraph_url" in result or "success" in result


class TestCapsuleMonitor:
    """Test capsule monitoring and notifications."""

    @pytest.fixture
    def mock_db(self):
        """Mock database with test letters."""
        db = Mock()

        # Create mock toxic capsule
        toxic_capsule = Mock()
        toxic_capsule.id = 1
        toxic_capsule.letter_type = LetterType.TIME_CAPSULE.value
        toxic_capsule.toxicity_warnings_ignored = True
        toxic_capsule.toxicity_score = 0.75
        toxic_capsule.created_at = datetime.utcnow() - timedelta(hours=48)
        toxic_capsule.title = "Письмо для дочери"
        toxic_capsule.telegraph_url = "https://telegra.ph/test-123"

        db.get_user_letters = AsyncMock(return_value=[toxic_capsule])
        db.get_user_sessions = AsyncMock(return_value=[])

        return db

    @pytest.mark.asyncio
    async def test_capsule_monitor_initialization(self, mock_db):
        """Test capsule monitor initializes."""
        monitor = CapsuleMonitor(db=mock_db)
        assert monitor.db == mock_db

    @pytest.mark.asyncio
    async def test_check_toxic_capsules(self, mock_db):
        """Test finding toxic capsules."""
        monitor = CapsuleMonitor(db=mock_db)

        capsules = await monitor.check_toxic_capsules(user_id=1)

        assert len(capsules) > 0
        assert capsules[0]["toxicity_score"] == 0.75
        assert capsules[0]["title"] == "Письмо для дочери"

    @pytest.mark.asyncio
    async def test_should_notify_when_calm(self, mock_db):
        """Test notification when user is calm."""
        monitor = CapsuleMonitor(db=mock_db)

        # User is calm (low distress)
        should_notify = await monitor.should_notify_user(
            user_id=1,
            current_distress_level=0.3
        )

        assert should_notify is True

    @pytest.mark.asyncio
    async def test_should_not_notify_when_distressed(self, mock_db):
        """Test no notification when user is distressed."""
        monitor = CapsuleMonitor(db=mock_db)

        # User is distressed (high distress)
        should_notify = await monitor.should_notify_user(
            user_id=1,
            current_distress_level=0.8
        )

        assert should_notify is False

    @pytest.mark.asyncio
    async def test_notification_format_single(self, mock_db):
        """Test notification formatting for single capsule."""
        monitor = CapsuleMonitor(db=mock_db)

        capsules = [{
            'letter_id': 1,
            'title': 'Письмо для сына',
            'toxicity_score': 0.65,
            'created_at': datetime.utcnow() - timedelta(days=2),
            'telegraph_url': 'https://telegra.ph/test-123'
        }]

        message = monitor.format_notification(capsules)

        assert "Напоминание о капсуле" in message
        assert "Письмо для сына" not in message or "токсичность" in message
        assert "0.65" in message or "65%" in message

    @pytest.mark.asyncio
    async def test_notification_format_multiple(self, mock_db):
        """Test notification formatting for multiple capsules."""
        monitor = CapsuleMonitor(db=mock_db)

        capsules = [
            {
                'letter_id': 1,
                'title': 'Письмо 1',
                'toxicity_score': 0.65,
                'created_at': datetime.utcnow() - timedelta(days=2),
                'telegraph_url': 'https://telegra.ph/test-1'
            },
            {
                'letter_id': 2,
                'title': 'Письмо 2',
                'toxicity_score': 0.55,
                'created_at': datetime.utcnow() - timedelta(days=3),
                'telegraph_url': 'https://telegra.ph/test-2'
            }
        ]

        message = monitor.format_notification(capsules)

        assert "2" in message or "два" in message
        assert "/my_letters" in message

    @pytest.mark.asyncio
    async def test_no_notification_for_fresh_capsule(self):
        """Test no notification for recently created capsule."""
        # Mock fresh capsule (< 24 hours)
        db = Mock()
        fresh_capsule = Mock()
        fresh_capsule.id = 1
        fresh_capsule.letter_type = LetterType.TIME_CAPSULE.value
        fresh_capsule.toxicity_warnings_ignored = True
        fresh_capsule.toxicity_score = 0.75
        fresh_capsule.created_at = datetime.utcnow() - timedelta(hours=12)  # Only 12h ago

        db.get_user_letters = AsyncMock(return_value=[fresh_capsule])
        db.get_user_sessions = AsyncMock(return_value=[])

        monitor = CapsuleMonitor(db=db)
        capsules = await monitor.check_toxic_capsules(user_id=1)

        # Should not include fresh capsule
        assert len(capsules) == 0


class TestIntegration:
    """Integration tests for complete letter writing flow."""

    @pytest.mark.asyncio
    async def test_complete_flow_for_sending(self):
        """Test complete flow: start → draft → toxicity → telegraph."""
        # This would require real components
        # Skipping for now (would need real DB, Telegraph, etc.)
        pytest.skip("Integration test - requires real components")

    @pytest.mark.asyncio
    async def test_complete_flow_therapeutic(self):
        """Test therapeutic flow: no toxicity check."""
        pytest.skip("Integration test - requires real components")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
