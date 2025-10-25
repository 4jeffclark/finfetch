"""
Logging utilities for FinFetch.

This module provides structured logging functionality for the FinFetch system.
"""

import logging
import sys
from typing import Optional, Dict, Any
import structlog
from datetime import datetime


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None
) -> None:
    """
    Setup structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Log format type ("json" or "console")
        log_file: Optional log file path
    """
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
        
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    if format_type == "json":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class FinFetchLogger:
    """
    Custom logger class for FinFetch with additional context.
    """
    
    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            context: Additional context to include in all log messages
        """
        self.logger = get_logger(name)
        self.context = context or {}
        
    def _add_context(self, **kwargs) -> Dict[str, Any]:
        """Add context to log message."""
        return {**self.context, **kwargs}
        
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **self._add_context(**kwargs))
        
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **self._add_context(**kwargs))
        
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **self._add_context(**kwargs))
        
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **self._add_context(**kwargs))
        
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, **self._add_context(**kwargs))
        
    def bind(self, **kwargs) -> 'FinFetchLogger':
        """
        Create a new logger instance with additional context.
        
        Args:
            **kwargs: Additional context to bind
            
        Returns:
            New logger instance with bound context
        """
        new_context = {**self.context, **kwargs}
        return FinFetchLogger(self.logger.name, new_context)
