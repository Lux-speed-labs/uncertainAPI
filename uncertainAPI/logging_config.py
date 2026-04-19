"""Loguru logging configuration for uncertainAPI.

This module configures loguru as the logging backend, replacing Python's
standard logging module with a more powerful and user-friendly alternative.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from loguru import logger


def configure_loguru(
    level: str = "INFO",
    log_file: str | None = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    format_string: str | None = None,
    diagnose: bool = False,
) -> None:
    """Configure loguru for the application.

    Args:
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to log file. If None, logs only to stderr.
        rotation: When to rotate log files (e.g., "10 MB", "1 day").
        retention: How long to keep old log files.
        format_string: Custom format string. If None, uses sensible default.
        diagnose: Enable diagnosis mode (shows variables on exceptions).

    Example:
        # Basic setup
        configure_loguru()

        # Production setup with file logging
        configure_loguru(
            level="INFO",
            log_file="/var/log/uncertainapi/app.log",
            rotation="100 MB",
            retention="30 days",
        )

        # Development setup with debug
        configure_loguru(
            level="DEBUG",
            diagnose=True,
        )
    """
    # Remove default handler
    logger.remove()

    # Default format with colors and structure
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level> | "
            "{extra}"
        )

    # Add stderr handler (console output)
    logger.add(
        sys.stderr,
        format=format_string,
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=diagnose,
    )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=format_string,
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=diagnose,
            enqueue=True,  # Async logging for better performance
        )

    logger.info("loguru.configured", level=level, log_file=log_file)


def configure_loguru_for_django(settings: Any) -> None:
    """Configure loguru based on Django settings.

    Args:
        settings: Django settings module.

    Reads from settings:
        - DEBUG: Enables diagnose mode if True
        - UNCERTAINAPI['LOGGING']['LEVEL']: Log level
        - UNCERTAINAPI['LOGGING']['FILE']: Log file path
        - UNCERTAINAPI['LOGGING']['ROTATION']: Rotation policy
        - UNCERTAINAPI['LOGGING']['RETENTION']: Retention policy
    """
    uncertainapi_settings = getattr(settings, "UNCERTAINAPI", {})
    logging_config = uncertainapi_settings.get("LOGGING", {})

    level = logging_config.get("LEVEL", "DEBUG" if settings.DEBUG else "INFO")
    log_file = logging_config.get("FILE")
    rotation = logging_config.get("ROTATION", "10 MB")
    retention = logging_config.get("RETENTION", "1 week")
    diagnose = settings.DEBUG

    configure_loguru(
        level=level,
        log_file=log_file,
        rotation=rotation,
        retention=retention,
        diagnose=diagnose,
    )


# Intercept standard logging and redirect to loguru
class InterceptHandler:
    """Intercept standard logging calls and redirect to loguru.

    This allows libraries using standard logging to work with loguru.
    """

    def write(self, message: str) -> None:
        """Write log message."""
        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == __file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=None).info(message.rstrip())


def setup_django_loguru_intercept() -> None:
    """Setup Django to use loguru for all logging.

    Call this in your Django settings or AppConfig.ready().
    """
    import logging

    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    # Intercept specific loggers
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True


# Export configured logger
__all__ = [
    "logger",
    "configure_loguru",
    "configure_loguru_for_django",
    "setup_django_loguru_intercept",
]



