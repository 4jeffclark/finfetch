"""
Data models for FinFetch financial data structures.

This module defines the core data models used throughout the FinFetch system
for representing financial data, data sources, and processing results.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from dataclasses import dataclass, field
import pandas as pd
from pydantic import BaseModel, Field, validator


class DataSource(BaseModel):
    """
    Represents a data source configuration.
    """
    name: str = Field(..., description="Name of the data source")
    api_key: Optional[str] = Field(None, description="API key for the data source")
    base_url: Optional[str] = Field(None, description="Base URL for the data source")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")
    timeout: int = Field(30, description="Request timeout in seconds")
    enabled: bool = Field(True, description="Whether the source is enabled")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True


class FinancialData(BaseModel):
    """
    Represents financial data for a single symbol.
    """
    symbol: str = Field(..., description="Financial symbol")
    data: pd.DataFrame = Field(..., description="Financial data as DataFrame")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Data metadata")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update time")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        validate_assignment = True
        
    def merge_data(self, other_data: 'FinancialData', source_name: str) -> None:
        """
        Merge data from another source.
        
        Args:
            other_data: Financial data from another source
            source_name: Name of the source providing the data
        """
        # Add source to sources list
        if source_name not in self.sources:
            self.sources.append(source_name)
            
        # Merge DataFrames (this is a simplified merge - in practice you'd want more sophisticated logic)
        if self.data.empty:
            self.data = other_data.data.copy()
        else:
            # For now, just concatenate - in practice you'd want conflict resolution
            self.data = pd.concat([self.data, other_data.data], ignore_index=True)
            
        # Merge metadata
        self.metadata.update(other_data.metadata)
        
        # Update last updated time
        self.last_updated = datetime.now()
        
    def get_price_data(self) -> pd.DataFrame:
        """Get price data (OHLCV)."""
        price_columns = ['open', 'high', 'low', 'close', 'volume']
        available_columns = [col for col in price_columns if col in self.data.columns]
        return self.data[available_columns] if available_columns else pd.DataFrame()
        
    def get_indicators(self) -> pd.DataFrame:
        """Get technical indicators data."""
        indicator_columns = [col for col in self.data.columns 
                           if col not in ['open', 'high', 'low', 'close', 'volume', 'date']]
        return self.data[indicator_columns] if indicator_columns else pd.DataFrame()


class ProcessingResult(BaseModel):
    """
    Represents the result of data processing operations.
    """
    data: Dict[str, FinancialData] = Field(..., description="Processed financial data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    processing_time: float = Field(0.0, description="Processing time in seconds")
    success: bool = Field(True, description="Whether processing was successful")
    errors: List[str] = Field(default_factory=list, description="Processing errors")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        validate_assignment = True
        
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the processing result."""
        return {
            "symbols_processed": len(self.data),
            "processing_time": self.processing_time,
            "success": self.success,
            "error_count": len(self.errors),
            "metadata": self.metadata
        }


@dataclass
class CollectionConfig:
    """
    Configuration for data collection operations.
    """
    symbols: List[str] = field(default_factory=list)
    start_date: Optional[Union[str, datetime, date]] = None
    end_date: Optional[Union[str, datetime, date]] = None
    frequency: str = "daily"
    include_indicators: bool = True
    include_fundamentals: bool = False
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.symbols:
            raise ValueError("At least one symbol must be specified")
            
        if self.start_date and self.end_date:
            if isinstance(self.start_date, str):
                self.start_date = datetime.fromisoformat(self.start_date)
            if isinstance(self.end_date, str):
                self.end_date = datetime.fromisoformat(self.end_date)
                
            if self.start_date >= self.end_date:
                raise ValueError("Start date must be before end date")


class DataQualityReport(BaseModel):
    """
    Represents a data quality report for financial data.
    """
    symbol: str = Field(..., description="Financial symbol")
    total_records: int = Field(..., description="Total number of records")
    missing_values: Dict[str, int] = Field(default_factory=dict, description="Missing values per column")
    data_range: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Data range statistics")
    quality_score: float = Field(0.0, description="Overall data quality score (0-1)")
    issues: List[str] = Field(default_factory=list, description="Data quality issues found")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        
    def calculate_quality_score(self) -> float:
        """Calculate overall data quality score."""
        if self.total_records == 0:
            return 0.0
            
        # Simple quality score based on missing values
        total_cells = self.total_records * len(self.missing_values)
        if total_cells == 0:
            return 1.0
            
        missing_cells = sum(self.missing_values.values())
        completeness = 1.0 - (missing_cells / total_cells)
        
        # Penalize for issues
        issue_penalty = len(self.issues) * 0.1
        
        return max(0.0, completeness - issue_penalty)
