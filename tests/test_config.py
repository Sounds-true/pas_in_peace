"""Test configuration loading."""

import pytest
from src.core.config import Settings


def test_settings_can_be_imported():
    """Test that settings can be imported."""
    assert Settings is not None


def test_default_values():
    """Test default configuration values."""
    # Create settings without env file (will use defaults)
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test_token",
        openai_api_key="test_key",
        database_url="postgresql+asyncpg://test:test@localhost/test",
        secret_key="test_secret",
        pii_encryption_key="test_encryption_key"
    )

    assert settings.openai_model == "gpt-4-turbo-preview"
    assert settings.openai_temperature == 0.7
    assert settings.log_level == "INFO"
    assert settings.environment == "development"
    assert settings.debug is False


def test_crisis_hotline_defaults():
    """Test crisis hotline defaults."""
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test_token",
        openai_api_key="test_key",
        database_url="postgresql+asyncpg://test:test@localhost/test",
        secret_key="test_secret",
        pii_encryption_key="test_encryption_key"
    )

    assert settings.crisis_hotline_ru == "8-800-2000-122"
    assert settings.crisis_hotline_intl == "988"


def test_threshold_values():
    """Test threshold configuration."""
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test_token",
        openai_api_key="test_key",
        database_url="postgresql+asyncpg://test:test@localhost/test",
        secret_key="test_secret",
        pii_encryption_key="test_encryption_key"
    )

    assert settings.suicidalbert_threshold == 0.7
    assert 0.0 <= settings.suicidalbert_threshold <= 1.0