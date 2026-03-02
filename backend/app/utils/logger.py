"""
Logging configuration for the application.
"""
import sys
from loguru import logger
from app.core.config import settings
import os


def setup_logging():
    """Configure application logging."""
    # Remove default logger
    logger.remove()
    
    # Determine log level based on debug setting
    log_level = "DEBUG" if settings.debug else "INFO"
    
    # Console logger - less verbose in production
    if settings.debug:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True
        )
    else:
        # Production: simpler format, only INFO and above to console
        logger.add(
            sys.stdout,
            format="<level>{time:YYYY-MM-DD HH:mm:ss}</level> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO",
            colorize=False
        )
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # File logger - always log INFO and above
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        compression="zip"
    )
    
    # Error file logger - always log ERROR regardless of debug setting
    logger.add(
        "logs/error.log",
        rotation="500 MB",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        compression="zip"
    )
    
    return logger


# Initialize logger
log = setup_logging()
