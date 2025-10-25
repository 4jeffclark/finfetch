"""
Base class for data processors.

This module defines the abstract base class that all data processors
must implement to be compatible with the FinFetch system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from ..core.data_models import FinancialData
from ..utils.logger import get_logger


class BaseProcessor(ABC):
    """
    Abstract base class for data processors.
    
    All data processors must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data processor.
        
        Args:
            config: Processor configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this processor."""
        pass
        
    @abstractmethod
    def process(self, data: Dict[str, FinancialData]) -> Dict[str, FinancialData]:
        """
        Process the financial data.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary mapping symbols to processed FinancialData objects
        """
        pass
        
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the processor configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
        
    def get_processing_info(self) -> Dict[str, Any]:
        """
        Get information about this processor.
        
        Returns:
            Dictionary containing processor information
        """
        return {
            "name": self.name,
            "config": self.config,
            "description": self.__doc__ or "No description available"
        }
        
    def _log_processing_start(self, symbol_count: int) -> None:
        """Log the start of processing."""
        self.logger.info(f"Starting {self.name} processing for {symbol_count} symbols")
        
    def _log_processing_complete(self, symbol_count: int, processing_time: float) -> None:
        """Log the completion of processing."""
        self.logger.info(f"Completed {self.name} processing for {symbol_count} symbols in {processing_time:.2f}s")
        
    def _log_processing_error(self, symbol: str, error: Exception) -> None:
        """Log a processing error."""
        self.logger.error(f"Error processing {symbol} in {self.name}: {error}")
        
    def _update_metadata(self, data: FinancialData, processor_name: str, processing_info: Dict[str, Any]) -> None:
        """
        Update data metadata with processing information.
        
        Args:
            data: FinancialData object to update
            processor_name: Name of the processor
            processing_info: Information about the processing
        """
        if "processing_history" not in data.metadata:
            data.metadata["processing_history"] = []
            
        data.metadata["processing_history"].append({
            "processor": processor_name,
            "timestamp": data.last_updated.isoformat(),
            "info": processing_info
        })
