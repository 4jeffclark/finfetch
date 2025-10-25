"""
Data cleaning processor for FinFetch.

This module provides data cleaning functionality for financial data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from .base import BaseProcessor
from ..core.data_models import FinancialData
from ..utils.logger import get_logger


class DataCleaner(BaseProcessor):
    """
    Data cleaning processor for financial data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data cleaner.
        
        Args:
            config: Processor configuration
        """
        super().__init__(config)
        self.fill_method = self.config.get('fill_method', 'forward')
        self.remove_outliers = self.config.get('remove_outliers', True)
        self.outlier_threshold = self.config.get('outlier_threshold', 3.0)
        
    @property
    def name(self) -> str:
        """Get processor name."""
        return "Data Cleaner"
        
    def process(self, data: Dict[str, FinancialData]) -> Dict[str, FinancialData]:
        """
        Clean financial data.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary mapping symbols to cleaned FinancialData objects
        """
        self._log_processing_start(len(data))
        start_time = datetime.now()
        
        cleaned_data = {}
        for symbol, financial_data in data.items():
            try:
                cleaned_financial_data = self._clean_symbol_data(financial_data)
                cleaned_data[symbol] = cleaned_financial_data
                
                # Update metadata
                processing_info = {
                    'processor': self.name,
                    'cleaning_applied': True,
                    'original_records': len(financial_data.data),
                    'cleaned_records': len(cleaned_financial_data.data)
                }
                self._update_metadata(cleaned_financial_data, self.name, processing_info)
                
            except Exception as e:
                self._log_processing_error(symbol, e)
                # Keep original data if cleaning fails
                cleaned_data[symbol] = financial_data
                
        processing_time = (datetime.now() - start_time).total_seconds()
        self._log_processing_complete(len(cleaned_data), processing_time)
        
        return cleaned_data
        
    def _clean_symbol_data(self, financial_data: FinancialData) -> FinancialData:
        """
        Clean data for a single symbol.
        
        Args:
            financial_data: FinancialData object to clean
            
        Returns:
            Cleaned FinancialData object
        """
        df = financial_data.data.copy()
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Sort by date if date column exists
        if 'date' in df.columns:
            df = df.sort_values('date').reset_index(drop=True)
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Remove outliers if configured
        if self.remove_outliers:
            df = self._remove_outliers(df)
        
        # Validate data consistency
        df = self._validate_data_consistency(df)
        
        # Create new FinancialData object
        cleaned_data = FinancialData(
            symbol=financial_data.symbol,
            data=df,
            metadata=financial_data.metadata.copy(),
            sources=financial_data.sources.copy(),
            last_updated=datetime.now()
        )
        
        return cleaned_data
        
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            DataFrame with missing values handled
        """
        if self.fill_method == 'forward':
            df = df.fillna(method='ffill')
        elif self.fill_method == 'backward':
            df = df.fillna(method='bfill')
        elif self.fill_method == 'interpolate':
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            df[numeric_columns] = df[numeric_columns].interpolate()
        elif self.fill_method == 'drop':
            df = df.dropna()
        
        return df
        
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove outliers from the DataFrame.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            DataFrame with outliers removed
        """
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns:
                # Calculate z-scores
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                
                # Remove outliers
                outlier_mask = z_scores > self.outlier_threshold
                if outlier_mask.any():
                    self.logger.info(f"Removing {outlier_mask.sum()} outliers from {col}")
                    df = df[~outlier_mask]
        
        return df
        
    def _validate_data_consistency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and fix data consistency issues.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            DataFrame with consistency issues fixed
        """
        # Check for negative prices
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in df.columns:
                negative_mask = df[col] < 0
                if negative_mask.any():
                    self.logger.warning(f"Found {negative_mask.sum()} negative values in {col}, setting to NaN")
                    df.loc[negative_mask, col] = np.nan
        
        # Check OHLC consistency
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            # High should be >= max(open, close)
            high_violations = df['high'] < df[['open', 'close']].max(axis=1)
            if high_violations.any():
                self.logger.warning(f"Found {high_violations.sum()} high price violations")
                df.loc[high_violations, 'high'] = df.loc[high_violations, ['open', 'close']].max(axis=1)
            
            # Low should be <= min(open, close)
            low_violations = df['low'] > df[['open', 'close']].min(axis=1)
            if low_violations.any():
                self.logger.warning(f"Found {low_violations.sum()} low price violations")
                df.loc[low_violations, 'low'] = df.loc[low_violations, ['open', 'close']].min(axis=1)
        
        return df
        
    def validate_config(self) -> bool:
        """Validate processor configuration."""
        valid_fill_methods = ['forward', 'backward', 'interpolate', 'drop']
        if self.fill_method not in valid_fill_methods:
            self.logger.error(f"Invalid fill_method: {self.fill_method}")
            return False
            
        if self.outlier_threshold <= 0:
            self.logger.error(f"Invalid outlier_threshold: {self.outlier_threshold}")
            return False
            
        return True
