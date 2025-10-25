"""
Configuration manager for FinFetch.

This module provides configuration loading, saving, and management
functionality for the FinFetch system.
"""

import os
import yaml
from typing import Optional, Dict, Any
from pathlib import Path

from .config_models import FinFetchConfig, get_default_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manages FinFetch configuration."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or self._find_config_file()
        self.config = self._load_config()
        
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        # Check current directory
        current_dir = Path.cwd()
        config_files = [
            current_dir / "finfetch.yaml",
            current_dir / "finfetch.yml",
            current_dir / ".finfetch.yaml",
            current_dir / ".finfetch.yml"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                return str(config_file)
        
        # Check home directory
        home_dir = Path.home()
        home_config = home_dir / ".finfetch.yaml"
        if home_config.exists():
            return str(home_config)
        
        # Return default path
        return str(current_dir / "finfetch.yaml")
        
    def _load_config(self) -> FinFetchConfig:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                return FinFetchConfig(**config_data)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_file}: {e}")
                logger.info("Using default configuration")
                return get_default_config()
        else:
            logger.info(f"Config file {self.config_file} not found, using default configuration")
            return get_default_config()
            
    def save_config(self, config: Optional[FinFetchConfig] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save (uses current config if None)
        """
        if config is None:
            config = self.config
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config.dict(), f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_file}: {e}")
            raise
            
    def get_config(self) -> FinFetchConfig:
        """Get current configuration."""
        return self.config
        
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        try:
            # Convert to FinFetchConfig and merge
            current_dict = self.config.dict()
            self._deep_update(current_dict, updates)
            self.config = FinFetchConfig(**current_dict)
            logger.info("Configuration updated successfully")
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise
            
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Deep update dictionary."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
                
    def validate_config(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate by creating a new instance
            FinFetchConfig(**self.config.dict())
            logger.info("Configuration validation passed")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
            
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = get_default_config()
        logger.info("Configuration reset to defaults")
        
    def get_source_config(self, source_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific source."""
        if source_name in self.config.sources:
            return self.config.sources[source_name].dict()
        return None
        
    def get_processor_config(self, processor_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific processor."""
        if processor_name in self.config.processors:
            return self.config.processors[processor_name].dict()
        return None


def load_config(config_file: Optional[str] = None) -> FinFetchConfig:
    """
    Load configuration from file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        FinFetchConfig object
    """
    manager = ConfigManager(config_file)
    return manager.get_config()


def save_config(config: FinFetchConfig, config_file: Optional[str] = None) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration to save
        config_file: Path to configuration file
    """
    manager = ConfigManager(config_file)
    manager.save_config(config)
