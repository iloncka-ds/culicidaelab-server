"""Logging configuration for CulicidaeLab backend.

This module provides structured logging configuration with JSON formatting
for better log aggregation and monitoring in containerized environments.
"""

import logging
import logging.config
import os
import sys
from typing import Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: The log record to format.

        Returns:
            JSON formatted log string.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "service": "culicidaelab-backend",
            "environment": os.getenv("FASTAPI_ENV", "production"),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry, ensure_ascii=False)


def get_logging_config() -> dict[str, Any]:
    """Get logging configuration based on environment.

    Returns:
        Dictionary containing logging configuration.
    """
    environment = os.getenv("FASTAPI_ENV", "production")
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"

    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "json" if environment == "production" else "standard",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "backend": {
                "level": "DEBUG" if debug_mode else "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }

    return config


def setup_logging():
    """Setup logging configuration for the application."""
    config = get_logging_config()
    logging.config.dictConfig(config)

    # Get logger for this module
    logger = logging.getLogger(__name__)
    environment = os.getenv("FASTAPI_ENV", "production")

    logger.info(
        "Logging configuration initialized",
        extra={
            "extra_fields": {
                "environment": environment,
                "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
            },
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Name for the logger.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)


# Convenience function for adding structured data to logs
def log_with_context(logger: logging.Logger, level: str, message: str, **context):
    """Log a message with additional context data.

    Args:
        logger: Logger instance to use.
        level: Log level (info, warning, error, etc.).
        message: Log message.
        **context: Additional context data to include.
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra={"extra_fields": context})
