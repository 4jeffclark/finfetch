"""
Debug configuration system for FinFetch.

This module provides a centralized debug level system with clear definitions
for what content appears at each level.
"""

import logging
from enum import IntEnum
from typing import Optional


class DebugLevel(IntEnum):
    """Debug levels for FinFetch output control."""
    
    # Level 0: Clean output - only essential results (tables, data)
    CLEAN = 0
    
    # Level 1: Basic info - success messages, basic status
    BASIC = 1
    
    # Level 2: Detailed info - progress updates, intermediate results
    DETAILED = 2
    
    # Level 3: Debug - internal state, data processing details
    DEBUG = 3
    
    # Level 4: Verbose - all logging, full trace information
    VERBOSE = 4


class DebugConfig:
    """Centralized debug configuration for FinFetch."""
    
    def __init__(self, level: DebugLevel = DebugLevel.CLEAN):
        self.level = level
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging based on debug level."""
        if self.level >= DebugLevel.VERBOSE:
            log_level = logging.DEBUG
        elif self.level >= DebugLevel.DEBUG:
            log_level = logging.INFO
        elif self.level >= DebugLevel.DETAILED:
            log_level = logging.WARNING
        else:
            log_level = logging.ERROR
        
        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s' if self.level >= DebugLevel.DEBUG else '%(message)s'
        )
    
    def should_show(self, level: DebugLevel) -> bool:
        """Check if content at given level should be shown."""
        return self.level >= level
    
    def set_level(self, level: DebugLevel):
        """Update debug level."""
        self.level = level
        self._setup_logging()


# Global debug configuration instance
_debug_config: Optional[DebugConfig] = None


def get_debug_config() -> DebugConfig:
    """Get the global debug configuration."""
    global _debug_config
    if _debug_config is None:
        _debug_config = DebugConfig()
    return _debug_config


def set_debug_level(level: DebugLevel):
    """Set the global debug level."""
    config = get_debug_config()
    config.set_level(level)


def should_show(level: DebugLevel) -> bool:
    """Check if content at given level should be shown."""
    return get_debug_config().should_show(level)


def debug_print(message: str, level: DebugLevel = DebugLevel.BASIC):
    """Print message only if debug level allows it."""
    if should_show(level):
        print(message)


def debug_log(message: str, level: DebugLevel = DebugLevel.DEBUG):
    """Log message only if debug level allows it."""
    if should_show(level):
        logger = logging.getLogger(__name__)
        if level >= DebugLevel.VERBOSE:
            logger.debug(message)
        elif level >= DebugLevel.DEBUG:
            logger.info(message)
        elif level >= DebugLevel.DETAILED:
            logger.warning(message)
        else:
            logger.error(message)
