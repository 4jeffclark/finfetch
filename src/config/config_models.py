"""
Configuration models for FinFetch.

This module defines the configuration data models using Pydantic
for validation and type safety.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
import os


class SourceConfig(BaseModel):
    """Configuration for a data source."""
    enabled: bool = Field(True, description="Whether the source is enabled")
    api_key: Optional[str] = Field(None, description="API key for the source")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")
    timeout: int = Field(30, description="Request timeout in seconds")
    base_url: Optional[str] = Field(None, description="Base URL for the source")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True


class ProcessorConfig(BaseModel):
    """Configuration for a data processor."""
    enabled: bool = Field(True, description="Whether the processor is enabled")
    config: Dict[str, Any] = Field(default_factory=dict, description="Processor-specific configuration")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True


class OutputConfig(BaseModel):
    """Configuration for output formatting."""
    default_format: str = Field("csv", description="Default output format")
    date_format: str = Field("%Y-%m-%d", description="Date format string")
    decimal_places: int = Field(2, description="Number of decimal places")
    include_metadata: bool = Field(True, description="Include metadata in output")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: str = Field("INFO", description="Logging level")
    format: str = Field("json", description="Log format")
    file: Optional[str] = Field(None, description="Log file path")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True


class FinFetchConfig(BaseModel):
    """Main FinFetch configuration."""
    version: str = Field("1.0", description="Configuration version")
    sources: Dict[str, SourceConfig] = Field(default_factory=dict, description="Data source configurations")
    processors: Dict[str, ProcessorConfig] = Field(default_factory=dict, description="Processor configurations")
    output: OutputConfig = Field(default_factory=OutputConfig, description="Output configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
        
    @validator('sources', pre=True)
    def parse_sources(cls, v):
        """Parse sources configuration."""
        if isinstance(v, dict):
            return {k: SourceConfig(**v[k]) if isinstance(v[k], dict) else v[k] for k in v}
        return v
        
    @validator('processors', pre=True)
    def parse_processors(cls, v):
        """Parse processors configuration."""
        if isinstance(v, dict):
            return {k: ProcessorConfig(**v[k]) if isinstance(v[k], dict) else v[k] for k in v}
        return v


def get_default_config() -> FinFetchConfig:
    """Get default FinFetch configuration."""
    return FinFetchConfig(
        sources={
            "yahoo": SourceConfig(
                enabled=True,
                rate_limit=2000,
                timeout=30
            ),
            "polygon": SourceConfig(
                enabled=True,
                api_key=os.getenv("POLYGON_API_KEY"),
                rate_limit=5,
                timeout=30
            ),
            "alpha_vantage": SourceConfig(
                enabled=False,
                api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
                rate_limit=5,
                timeout=30
            ),
            "fred": SourceConfig(
                enabled=False,
                api_key=os.getenv("FRED_API_KEY"),
                rate_limit=120,
                timeout=30
            )
        },
        processors={
            "data_cleaner": ProcessorConfig(
                enabled=True,
                config={
                    "fill_method": "forward",
                    "remove_outliers": True,
                    "outlier_threshold": 3.0
                }
            ),
            "technical_indicators": ProcessorConfig(
                enabled=True,
                config={
                    "indicators": ["sma", "ema", "rsi", "macd", "bollinger_bands"],
                    "periods": {
                        "sma": [20, 50, 200],
                        "ema": [12, 26],
                        "rsi": 14
                    }
                }
            ),
            "stock_screening": ProcessorConfig(
                enabled=True,
                config={
                    "risk_free_rate": 0.03,
                    "lookback_years": 5,
                    "week_52_lookback": 52,
                    "min_data_points": 1000
                }
            )
        }
    )
