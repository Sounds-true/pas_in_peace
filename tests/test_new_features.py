"""Tests for new NLP features: Entity Extraction, Intent Classification, Speech-to-Text."""

import pytest
from src.nlp.entity_extractor import EntityExtractor, Entity
from src.nlp.intent_classifier import IntentClassifier, Intent
from src.nlp.speech_handler import SpeechHandler


class TestEntityExtractor:
    """Test entity extraction functionality."""

    @pytest.mark.asyncio
    async def test_entity_extractor_initialization(self):
        """Test entity extractor initializes."""
        extractor = EntityExtractor()
        result = await extractor.initialize()
        assert extractor.initialized is True

    @pytest.mark.asyncio
    async def test_extract_child_name(self):
        """Test extracting child name from message."""
        extractor = EntityExtractor()
        await extractor.initialize()

        text = "Моя дочь Алиса не хочет со мной разговаривать"
        context = await extractor.extract(text)

        assert context is not None
        assert len(context.entities) > 0
        # Should detect either "дочь" as relationship or "Алиса" as person
        assert any(e.type in ['person', 'relationship'] for e in context.entities)

    @pytest.mark.asyncio
    async def test_extract_relationships(self):
        """Test extracting relationships."""
        extractor = EntityExtractor()
        await extractor.initialize()

        text = "Моя бывшая жена настраивает ребёнка против меня"
        context = await extractor.extract(text)

        assert context is not None
        assert len(context.relationships) > 0

    @pytest.mark.asyncio
    async def test_extract_dates(self):
        """Test extracting court dates."""
        extractor = EntityExtractor()
        await extractor.initialize()

        text = "Суд назначен на 15 декабря"
        context = await extractor.extract(text)

        assert context is not None
        # Should detect date pattern
        assert any(e.type == 'date' for e in context.entities)

    @pytest.mark.asyncio
    async def test_update_user_context(self):
        """Test updating user context with extracted entities."""
        extractor = EntityExtractor()
        await extractor.initialize()

        text = "Мой сын Максим"
        context = await extractor.extract(text)

        existing_context = {}
        updated = await extractor.update_user_context(
            "user123",
            context,
            existing_context
        )

        assert 'child_names' in updated or 'relationships' in updated


class TestIntentClassifier:
    """Test intent classification functionality."""

    @pytest.mark.asyncio
    async def test_intent_classifier_initialization(self):
        """Test intent classifier initializes."""
        classifier = IntentClassifier()
        await classifier.initialize()
        assert classifier.initialized is True

    @pytest.mark.asyncio
    async def test_classify_crisis_intent(self):
        """Test crisis intent detection."""
        classifier = IntentClassifier()
        await classifier.initialize()

        text = "Не хочу больше жить, нет смысла"
        result = await classifier.classify(text)

        assert result.intent == Intent.CRISIS
        assert result.confidence > 0.5

    @pytest.mark.asyncio
    async def test_classify_emotional_support(self):
        """Test emotional support intent."""
        classifier = IntentClassifier()
        await classifier.initialize()

        text = "Мне очень тяжело, не могу справиться"
        result = await classifier.classify(text)

        assert result.intent == Intent.EMOTIONAL_SUPPORT
        assert result.confidence > 0.3

    @pytest.mark.asyncio
    async def test_classify_question(self):
        """Test question intent."""
        classifier = IntentClassifier()
        await classifier.initialize()

        text = "Что такое отчуждение родителей?"
        result = await classifier.classify(text)

        assert result.intent == Intent.QUESTION
        assert result.confidence > 0.3

    @pytest.mark.asyncio
    async def test_classify_letter_writing(self):
        """Test letter writing intent."""
        classifier = IntentClassifier()
        await classifier.initialize()

        text = "Помоги написать письмо бывшей жене"
        result = await classifier.classify(text)

        assert result.intent == Intent.LETTER_WRITING
        assert result.confidence > 0.4

    @pytest.mark.asyncio
    async def test_classify_goal_setting(self):
        """Test goal setting intent."""
        classifier = IntentClassifier()
        await classifier.initialize()

        text = "Хочу наладить отношения с ребёнком к новому году"
        result = await classifier.classify(text)

        assert result.intent == Intent.GOAL_SETTING
        assert result.confidence > 0.3

    @pytest.mark.asyncio
    async def test_classify_gratitude(self):
        """Test gratitude intent."""
        classifier = IntentClassifier()
        await classifier.initialize()

        text = "Спасибо, мне помогло!"
        result = await classifier.classify(text)

        assert result.intent == Intent.GRATITUDE
        assert result.confidence > 0.3

    @pytest.mark.asyncio
    async def test_classify_greeting(self):
        """Test greeting intent."""
        classifier = IntentClassifier()
        await classifier.initialize()

        text = "Привет!"
        result = await classifier.classify(text)

        assert result.intent == Intent.GREETING
        assert result.confidence > 0.2

    @pytest.mark.asyncio
    async def test_classify_unknown(self):
        """Test unknown intent for ambiguous text."""
        classifier = IntentClassifier()
        await classifier.initialize()

        text = "абракадабра фыва олдж"
        result = await classifier.classify(text)

        assert result.intent == Intent.UNKNOWN
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_secondary_intents(self):
        """Test secondary intent detection."""
        classifier = IntentClassifier()
        await classifier.initialize()

        # Message with multiple possible intents
        text = "Мне тяжело, что делать?"
        result = await classifier.classify(text)

        # Should have primary intent
        assert result.intent in [Intent.EMOTIONAL_SUPPORT, Intent.TECHNIQUE_REQUEST]

        # Might have secondary intents
        # (test is flexible since it depends on scoring)
        assert isinstance(result.secondary_intents, list)


class TestSpeechHandler:
    """Test speech-to-text functionality (if available)."""

    def test_speech_handler_availability(self):
        """Test if speech recognition is available."""
        handler = SpeechHandler()
        # This should not raise an error even if unavailable
        assert isinstance(handler.is_available(), bool)

    def test_supported_backends(self):
        """Test getting supported backends."""
        handler = SpeechHandler()
        backends = handler.get_supported_backends()
        assert isinstance(backends, list)
        # Should return list (might be empty if dependencies not installed)

    @pytest.mark.asyncio
    async def test_speech_handler_initialization_graceful(self):
        """Test speech handler initialization fails gracefully."""
        handler = SpeechHandler()
        # Should not raise exception even if dependencies missing
        try:
            result = await handler.initialize()
            assert isinstance(result, bool)
        except ImportError:
            # Expected if SpeechRecognition not installed
            pytest.skip("SpeechRecognition not installed")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
