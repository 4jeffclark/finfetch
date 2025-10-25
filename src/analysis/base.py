"""
Base analyzer class for FinFetch.

This module defines the abstract base class that all analyzers
must implement to be compatible with the FinFetch system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.data_models import FinancialData, ProcessingResult
from ..utils.logger import get_logger


class BaseAnalyzer(ABC):
    """
    Abstract base class for financial data analyzers.
    
    All analyzers must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the analyzer.
        
        Args:
            config: Analyzer configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this analyzer."""
        pass
        
    @abstractmethod
    def analyze(self, data: Dict[str, FinancialData]) -> Dict[str, Any]:
        """
        Analyze financial data.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary containing analysis results
        """
        pass
        
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the analyzer configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
        
    def get_analysis_info(self) -> Dict[str, Any]:
        """
        Get information about this analyzer.
        
        Returns:
            Dictionary containing analyzer information
        """
        return {
            "name": self.name,
            "config": self.config,
            "description": self.__doc__ or "No description available"
        }
        
    def _log_analysis_start(self, symbol_count: int) -> None:
        """Log the start of analysis."""
        self.logger.info(f"Starting {self.name} analysis for {symbol_count} symbols")
        
    def _log_analysis_complete(self, symbol_count: int, analysis_time: float) -> None:
        """Log the completion of analysis."""
        self.logger.info(f"Completed {self.name} analysis for {symbol_count} symbols in {analysis_time:.2f}s")
        
    def _log_analysis_error(self, symbol: str, error: Exception) -> None:
        """Log an analysis error."""
        self.logger.error(f"Error analyzing {symbol} in {self.name}: {error}")
        
    def _update_metadata(self, data: FinancialData, analyzer_name: str, analysis_info: Dict[str, Any]) -> None:
        """
        Update data metadata with analysis information.
        
        Args:
            data: FinancialData object to update
            analyzer_name: Name of the analyzer
            analysis_info: Information about the analysis
        """
        if "analysis_history" not in data.metadata:
            data.metadata["analysis_history"] = []
            
        data.metadata["analysis_history"].append({
            "analyzer": analyzer_name,
            "timestamp": datetime.now().isoformat(),
            "info": analysis_info
        })
