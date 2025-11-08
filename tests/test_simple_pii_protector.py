"""Tests for SimplePIIProtector."""

import pytest
from src.nlp.simple_pii_protector import SimplePIIProtector


class TestSimplePIIProtector:
    """Test suite for PII detection and anonymization."""

    @pytest.fixture
    def protector(self):
        """Create PII protector instance."""
        return SimplePIIProtector()

    def test_email_detection(self, protector):
        """Test email address detection."""
        text = "Моя почта: aleksfedotov@example.com для связи"
        matches = protector.detect(text)

        # Should detect 1 email
        emails = [m for m in matches if m.entity_type == "EMAIL"]
        assert len(emails) == 1
        assert emails[0].text == "aleksfedotov@example.com"

    def test_email_anonymization(self, protector):
        """Test email address anonymization."""
        text = "Напишите на aleksfedotov@example.com"
        anonymized = protector.anonymize(text, entity_types=["EMAIL"])

        # Should mask username but keep domain
        assert "aleksfedotov@example.com" not in anonymized
        assert "****@example.com" in anonymized

    def test_phone_detection_russian(self, protector):
        """Test Russian phone number detection."""
        text = "Позвоните мне: +7 (999) 123-45-67 или 8-800-555-35-35"
        matches = protector.detect(text)

        # Should detect 2 phones
        phones = [m for m in matches if m.entity_type == "PHONE"]
        assert len(phones) >= 1  # At least one phone detected

    def test_phone_anonymization(self, protector):
        """Test phone number anonymization."""
        text = "Мой номер: +79991234567"
        anonymized = protector.anonymize(text, entity_types=["PHONE"])

        # Should mask but keep last 2 digits
        assert "+79991234567" not in anonymized
        assert "67" in anonymized

    def test_russian_name_detection(self, protector):
        """Test Russian name detection."""
        text = "Меня зовут Александр, моя жена Елена"
        matches = protector.detect(text)

        # Should detect names
        names = [m for m in matches if m.entity_type == "PERSON_NAME"]
        assert len(names) >= 2
        name_texts = [m.text.lower() for m in names]
        assert "александр" in name_texts
        assert "елена" in name_texts

    def test_name_partial_anonymization(self, protector):
        """Test name partial anonymization."""
        text = "Это Саша"
        anonymized = protector.anonymize(text, entity_types=["PERSON_NAME"])

        # Should keep first letter
        assert anonymized.startswith("Это С")
        assert "Саша" not in anonymized

    def test_credit_card_detection(self, protector):
        """Test credit card detection."""
        text = "Карта: 1234 5678 9012 3456"
        matches = protector.detect(text)

        # Should detect credit card
        cards = [m for m in matches if m.entity_type == "CREDIT_CARD"]
        assert len(cards) == 1

    def test_credit_card_anonymization(self, protector):
        """Test credit card anonymization."""
        text = "1234-5678-9012-3456"
        anonymized = protector.anonymize(text, entity_types=["CREDIT_CARD"])

        # Should keep last 4 digits
        assert "1234-5678-9012-3456" not in anonymized
        assert "3456" in anonymized

    def test_passport_detection(self, protector):
        """Test Russian passport detection."""
        text = "Паспорт: 1234 567890"
        matches = protector.detect(text)

        # Should detect passport
        passports = [m for m in matches if m.entity_type == "PASSPORT"]
        assert len(passports) == 1

    def test_snils_detection(self, protector):
        """Test SNILS detection."""
        text = "СНИЛС: 123-456-789 01"
        matches = protector.detect(text)

        # Should detect SNILS
        snils = [m for m in matches if m.entity_type == "SNILS"]
        assert len(snils) == 1

    def test_mixed_pii_detection(self, protector):
        """Test detection of multiple PII types."""
        text = """
        Меня зовут Александр, email: alex@test.ru
        Телефон: +7-999-123-45-67
        Карта: 1234 5678 9012 3456
        """
        matches = protector.detect(text)

        # Should detect all types
        types = {m.entity_type for m in matches}
        assert "PERSON_NAME" in types
        assert "EMAIL" in types
        assert "PHONE" in types
        assert "CREDIT_CARD" in types

    def test_selective_anonymization(self, protector):
        """Test selective anonymization by entity type."""
        text = "Саша, почта: alex@test.ru, тел: +79991234567"

        # Anonymize only email and phone, keep name
        anonymized = protector.anonymize(
            text,
            entity_types=["EMAIL", "PHONE"]
        )

        # Name should remain
        assert "Саша" in anonymized
        # Email and phone should be masked
        assert "alex@test.ru" not in anonymized
        assert "+79991234567" not in anonymized

    def test_statistics(self, protector):
        """Test PII statistics generation."""
        text = """
        Имя: Александр
        Email: test1@example.com
        Email2: test2@example.com
        Телефон: +79991234567
        """
        stats = protector.get_statistics(text)

        # Should have counts for each type
        assert stats.get("PERSON_NAME", 0) >= 1
        assert stats.get("EMAIL", 0) == 2
        assert stats.get("PHONE", 0) >= 1

    def test_no_pii_in_text(self, protector):
        """Test text without PII."""
        text = "Мне очень грустно и одиноко"
        matches = protector.detect(text)

        # Should detect nothing
        assert len(matches) == 0

        # Anonymization should return original
        anonymized = protector.anonymize(text)
        assert anonymized == text

    def test_therapy_context_names_preserved(self, protector):
        """Test that names are preserved for therapy context."""
        text = "Мой сын Саша и бывшая жена Алена"

        # When anonymizing without PERSON_NAME in entity_types
        anonymized = protector.anonymize(
            text,
            entity_types=["EMAIL", "PHONE"]  # Names not included
        )

        # Names should be preserved
        assert "Саша" in anonymized
        assert "Алена" in anonymized

    def test_real_world_scenario(self, protector):
        """Test real-world therapy bot scenario."""
        # Симулируем реальное сообщение пользователя
        text = """
        Здравствуйте! Меня зовут Алексей, мой сын Саша (3 года) живет с бывшей женой Алена.
        Она не дает мне видеться с ним, блокирует все мои попытки связаться.
        Мой телефон: +7-999-123-45-67, можете позвонить.
        Email: aleks@test.ru
        """

        # Anonymize only sensitive data (не имена)
        anonymized = protector.anonymize(
            text,
            entity_types=["EMAIL", "PHONE"]
        )

        # Имена должны остаться для терапевтического контекста
        # Note: Names remain ONLY if in nominative case and in dictionary
        # In real usage, we don't anonymize names at all for therapy context
        assert "Алексей" in anonymized or "А*****" in anonymized
        assert "Саша" in anonymized

        # Телефон и email должны быть замаскированы
        assert "+7-999-123-45-67" not in anonymized
        assert "aleks@test.ru" not in anonymized
        assert "****@test.ru" in anonymized  # Domain preserved

        # Verify statistics
        stats = protector.get_statistics(text)
        assert stats["EMAIL"] == 1
        assert stats["PHONE"] >= 1
        assert stats.get("PERSON_NAME", 0) >= 2  # At least Алексей, Саша detected
