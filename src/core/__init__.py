"""
Core FinFetch functionality.

This module contains the core classes and functionality for the FinFetch
financial data collection and processing system.
"""

from .finfetch import FinFetch
from .data_models import FinancialData, DataSource, ProcessingResult

__all__ = [
    "FinFetch",
    "FinancialData",
    "DataSource", 
    "ProcessingResult",
]
