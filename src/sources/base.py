"""
Base class for financial data sources.

This module defines the abstract base class that all financial data sources
must implement to be compatible with the FinFetch system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import asyncio
import logging

from ..core.data_models import FinancialData, DataSource
from ..utils.logger import get_logger


class BaseDataSource(ABC):
    """
    Abstract base class for financial data sources.
    
    All data sources must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, config: Optional[DataSource] = None):
        """
        Initialize the data source.
        
        Args:
            config: Data source configuration
        """
        self.config = config or DataSource(name=self.__class__.__name__)
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self._rate_limiter = None
        
    @property
    def name(self) -> str:
        """Get the name of this data source."""
        return self.config.name
        
    @property
    def enabled(self) -> bool:
        """Check if this data source is enabled."""
        return self.config.enabled
        
    @abstractmethod
    async def collect_data(
        self,
        symbols: List[str],
        start_date: Union[str, datetime, date],
        end_date: Union[str, datetime, date],
        **kwargs
    ) -> Dict[str, FinancialData]:
        """
        Collect financial data for the given symbols and date range.
        
        Args:
            symbols: List of financial symbols to collect
            start_date: Start date for data collection
            end_date: End date for data collection
            **kwargs: Additional parameters specific to the data source
            
        Returns:
            Dictionary mapping symbols to FinancialData objects
        """
        pass
        
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the data source configuration.
        
        Returns:
            True if the configuration is valid, False otherwise
        """
        pass
        
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test the connection to the data source.
        
        Returns:
            True if connection is successful, False otherwise
        """
        pass
        
    def get_supported_symbols(self) -> List[str]:
        """
        Get list of supported symbols for this data source.
        
        Returns:
            List of supported symbols (empty list if not applicable)
        """
        return []
        
    def get_available_indicators(self) -> List[str]:
        """
        Get list of available technical indicators.
        
        Returns:
            List of available indicators
        """
        return []
        
    async def _apply_rate_limiting(self) -> None:
        """
        Apply rate limiting if configured.
        
        This method should be called before making API requests
        to respect the data source's rate limits.
        """
        if self.config.rate_limit:
            # Simple rate limiting implementation
            # In practice, you'd want a more sophisticated rate limiter
            await asyncio.sleep(60.0 / self.config.rate_limit)
            
    def _normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol format for this data source.
        
        Args:
            symbol: Original symbol
            
        Returns:
            Normalized symbol
        """
        return symbol.upper().strip()
        
    def _validate_date_range(
        self,
        start_date: Union[str, datetime, date],
        end_date: Union[str, datetime, date]
    ) -> tuple[datetime, datetime]:
        """
        Validate and normalize date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Tuple of normalized datetime objects
            
        Raises:
            ValueError: If date range is invalid
        """
        # Convert string dates to datetime objects
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        elif isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
            
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        elif isinstance(end_date, date) and not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())
            
        # Validate date range
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
            
        return start_date, end_date
        
    def _create_financial_data(
        self,
        symbol: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FinancialData:
        """
        Create a FinancialData object from raw data.
        
        Args:
            symbol: Financial symbol
            data: Raw data (typically a pandas DataFrame)
            metadata: Optional metadata
            
        Returns:
            FinancialData object
        """
        return FinancialData(
            symbol=self._normalize_symbol(symbol),
            data=data,
            metadata=metadata or {},
            sources=[self.name]
        )
