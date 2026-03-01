"""
Logging configuration for the application.
"""
import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure application logging."""
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.debug else "INFO",
        colorize=True
    )
    
    # Add file logger
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        compression="zip"
    )
    
    # Add error file logger
    logger.add(
        "logs/error.log",
        rotation="500 MB",
        retention="10 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        compression="zip"
    )
    
    return logger


# Initialize logger
log = setup_logging()
