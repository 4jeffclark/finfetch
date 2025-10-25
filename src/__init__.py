"""
FinFetch - Financial Data Collection, Aggregation and Processing Utilities

A comprehensive Python package for collecting, aggregating, and processing
financial data from various sources.
"""

__version__ = "0.1.0"
__author__ = "FinFetch Development Team"
__email__ = "dev@finfetch.com"

from .core.finfetch import FinFetch
from .core.data_models import FinancialData, DataSource, ProcessingResult
from .sources.base import BaseDataSource
from .processors.base import BaseProcessor
from .analysis.base import BaseAnalyzer
from .config import ConfigManager, load_config, save_config

__all__ = [
    "FinFetch",
    "FinancialData", 
    "DataSource",
    "ProcessingResult",
    "BaseDataSource",
    "BaseProcessor",
    "BaseAnalyzer",
    "ConfigManager",
    "load_config",
    "save_config",
]
