"""Structured logging configuration using structlog."""

import sys
import structlog
from typing import Any, Dict
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_dir: Path = Path("data/logs")) -> None:
    """Configure structured logging."""

    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            ),
            structlog.processors.dict_tracebacks,
            structlog.dev.ConsoleRenderer() if log_level == "DEBUG" else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str, **context: Any) -> structlog.BoundLogger:
    """Get a logger instance with optional context."""
    logger = structlog.get_logger(name)
    if context:
        logger = logger.bind(**context)
    return logger


def log_user_interaction(
    logger: structlog.BoundLogger,
    user_id: str,
    message_type: str,
    **kwargs: Any
) -> None:
    """Log user interaction with PII protection."""
    # Remove any potential PII from kwargs
    safe_kwargs = {
        k: v for k, v in kwargs.items()
        if k not in ["name", "phone", "email", "address"]
    }

    logger.info(
        "user_interaction",
        user_id=user_id,
        message_type=message_type,
        **safe_kwargs
    )


def log_safety_event(
    logger: structlog.BoundLogger,
    event_type: str,
    severity: str,
    user_id: str,
    **details: Any
) -> None:
    """Log safety-related events."""
    logger.warning(
        "safety_event",
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        **details
    )