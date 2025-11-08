"""Configuration management using Pydantic Settings."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Telegram Configuration
    telegram_bot_token: SecretStr = Field(..., description="Telegram Bot Token")
    telegram_webhook_url: Optional[str] = Field(None, description="Webhook URL for production")

    # OpenAI Configuration
    openai_api_key: SecretStr = Field(..., description="OpenAI API Key")
    openai_model: str = Field("gpt-4-turbo-preview", description="OpenAI Model")
    openai_temperature: float = Field(0.7, ge=0.0, le=2.0)

    # Database Configuration
    database_url: str = Field(..., description="PostgreSQL connection string")
    redis_url: str = Field("redis://localhost:6379/0", description="Redis connection string")

    # Security Configuration
    secret_key: SecretStr = Field(..., description="Application secret key")
    pii_encryption_key: SecretStr = Field(..., description="Key for PII encryption")

    # Monitoring
    trulens_api_key: Optional[SecretStr] = Field(None, description="TruLens API Key")
    langsmith_api_key: Optional[SecretStr] = Field(None, description="LangSmith API Key")
    log_level: str = Field("INFO", description="Logging level")

    # Crisis Resources
    crisis_hotline_ru: str = Field("8-800-2000-122", description="Russian crisis hotline")
    crisis_hotline_intl: str = Field("988", description="International crisis hotline")

    # Environment
    environment: str = Field("development", description="Environment (development/staging/production)")
    debug: bool = Field(False, description="Debug mode")

    # Model Configuration
    suicidalbert_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Threshold for crisis detection")
    emotion_detection_model: str = Field("seara/rubert-base-go-emotions", description="Emotion detection model")

    # Rate Limiting
    max_messages_per_user_per_day: int = Field(100, description="Daily message limit per user")
    max_letter_drafts_per_session: int = Field(5, description="Max letter drafts in one session")

    # JITAI Configuration
    jitai_check_interval_hours: int = Field(24, description="Hours between JITAI checks")
    jitai_min_engagement_days: int = Field(3, description="Min days before JITAI activates")


# Create singleton settings instance
settings = Settings()