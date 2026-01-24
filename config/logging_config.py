"""
Logging Configuration for Mployable

Provides structured logging with file rotation, multiple handlers,
and environment-based configuration.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


class LogConfig:
    """Configuration for application logging"""

    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    # Log format
    DETAILED_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )
    SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    # Log file configuration
    LOG_DIR = Path("logs")
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5

    @classmethod
    def get_log_level(cls) -> int:
        """Get log level from environment or use default"""
        level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        return getattr(logging, level_str, logging.INFO)

    @classmethod
    def get_log_format(cls) -> str:
        """Get log format based on environment"""
        if os.getenv("ENVIRONMENT") == "production":
            return cls.SIMPLE_FORMAT
        return cls.DETAILED_FORMAT


def setup_logging(
    name: Optional[str] = None,
    log_level: Optional[int] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True,
) -> logging.Logger:
    """
    Setup and configure logging for the application

    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (defaults to env LOG_LEVEL or INFO)
        log_file: Log file path (defaults to logs/{name}.log)
        enable_console: Whether to log to console

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name or "mployable")

    # Set log level
    if log_level is None:
        log_level = LogConfig.get_log_level()
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Create logs directory if needed
    if log_file:
        LogConfig.LOG_DIR.mkdir(exist_ok=True)

    # Console handler (always for errors, optionally for all)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(LogConfig.get_log_format())
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        log_path = LogConfig.LOG_DIR / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=LogConfig.MAX_BYTES, backupCount=LogConfig.BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG)  # File always captures detailed logs
        file_formatter = logging.Formatter(LogConfig.DETAILED_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for a specific module

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Configure if not already configured
        log_file = f"{name.split('.')[-1]}.log"
        setup_logging(name, log_file=log_file)
    return logger


# Application-wide logger
app_logger = setup_logging("mployable", log_file="app.log")
api_logger = setup_logging("mployable.api", log_file="api.log")
error_logger = setup_logging("mployable.error", log_file="error.log")
