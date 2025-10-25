"""
Data aggregation processor for FinFetch.

This module provides data aggregation functionality for combining
data from multiple sources.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseProcessor
from ..core.data_models import FinancialData
from ..utils.logger import get_logger


class DataAggregator(BaseProcessor):
    """
    Data aggregation processor for financial data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data aggregator.
        
        Args:
            config: Processor configuration
        """
        super().__init__(config)
        self.aggregation_method = self.config.get('aggregation_method', 'weighted_average')
        self.source_weights = self.config.get('source_weights', {})
        self.conflict_resolution = self.config.get('conflict_resolution', 'latest')
        
    @property
    def name(self) -> str:
        """Get processor name."""
        return "Data Aggregator"
        
    def process(self, data: Dict[str, FinancialData]) -> Dict[str, FinancialData]:
        """
        Aggregate financial data from multiple sources.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary mapping symbols to aggregated FinancialData objects
        """
        self._log_processing_start(len(data))
        start_time = datetime.now()
        
        aggregated_data = {}
        for symbol, financial_data in data.items():
            try:
                aggregated_financial_data = self._aggregate_symbol_data(financial_data)
                aggregated_data[symbol] = aggregated_financial_data
                
                # Update metadata
                processing_info = {
                    'processor': self.name,
                    'aggregation_method': self.aggregation_method,
                    'sources_aggregated': len(financial_data.sources),
                    'original_records': len(financial_data.data),
                    'aggregated_records': len(aggregated_financial_data.data)
                }
                self._update_metadata(aggregated_financial_data, self.name, processing_info)
                
            except Exception as e:
                self._log_processing_error(symbol, e)
                # Keep original data if aggregation fails
                aggregated_data[symbol] = financial_data
                
        processing_time = (datetime.now() - start_time).total_seconds()
        self._log_processing_complete(len(aggregated_data), processing_time)
        
        return aggregated_data
        
    def _aggregate_symbol_data(self, financial_data: FinancialData) -> FinancialData:
        """
        Aggregate data for a single symbol.
        
        Args:
            financial_data: FinancialData object to aggregate
            
        Returns:
            Aggregated FinancialData object
        """
        df = financial_data.data.copy()
        
        # If only one source, no aggregation needed
        if len(financial_data.sources) <= 1:
            return financial_data
            
        # Group by date and aggregate
        if 'date' in df.columns:
            df = self._aggregate_by_date(df)
        
        # Create new FinancialData object
        aggregated_data = FinancialData(
            symbol=financial_data.symbol,
            data=df,
            metadata=financial_data.metadata.copy(),
            sources=financial_data.sources.copy(),
            last_updated=datetime.now()
        )
        
        return aggregated_data
        
    def _aggregate_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate data by date.
        
        Args:
            df: DataFrame to aggregate
            
        Returns:
            Aggregated DataFrame
        """
        # Group by date
        grouped = df.groupby('date')
        
        # Define aggregation functions for different columns
        agg_functions = {}
        
        # Price columns - use weighted average or latest
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in df.columns:
                if self.aggregation_method == 'weighted_average':
                    agg_functions[col] = 'mean'
                elif self.aggregation_method == 'latest':
                    agg_functions[col] = 'last'
                else:
                    agg_functions[col] = 'mean'
        
        # Volume - sum
        if 'volume' in df.columns:
            agg_functions['volume'] = 'sum'
        
        # Other numeric columns - mean
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in agg_functions and col != 'date':
                agg_functions[col] = 'mean'
        
        # Perform aggregation
        aggregated_df = grouped.agg(agg_functions).reset_index()
        
        return aggregated_df
        
    def _resolve_conflicts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Resolve conflicts in data from multiple sources.
        
        Args:
            df: DataFrame with potential conflicts
            
        Returns:
            DataFrame with conflicts resolved
        """
        if self.conflict_resolution == 'latest':
            # Keep the latest data for each date
            df = df.sort_values('date').groupby('date').last().reset_index()
        elif self.conflict_resolution == 'weighted_average':
            # Use weighted average based on source weights
            df = self._apply_weighted_average(df)
        elif self.conflict_resolution == 'source_priority':
            # Use data from highest priority source
            df = self._apply_source_priority(df)
        
        return df
        
    def _apply_weighted_average(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply weighted average based on source weights.
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with weighted averages applied
        """
        # This is a simplified implementation
        # In practice, you'd need to track which source each row came from
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns:
                # Simple average for now - in practice you'd use source weights
                df[col] = df[col].mean()
        
        return df
        
    def _apply_source_priority(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply source priority for conflict resolution.
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with source priority applied
        """
        # This is a simplified implementation
        # In practice, you'd need to track which source each row came from
        # and apply priority rules
        
        return df
        
    def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """
        Calculate data quality score for aggregated data.
        
        Args:
            df: DataFrame to score
            
        Returns:
            Quality score between 0 and 1
        """
        if df.empty:
            return 0.0
        
        # Calculate completeness
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness = 1.0 - (missing_cells / total_cells)
        
        # Calculate consistency (no duplicate dates)
        if 'date' in df.columns:
            duplicate_dates = df['date'].duplicated().sum()
            consistency = 1.0 - (duplicate_dates / len(df))
        else:
            consistency = 1.0
        
        # Calculate overall quality score
        quality_score = (completeness + consistency) / 2.0
        
        return quality_score
        
    def validate_config(self) -> bool:
        """Validate processor configuration."""
        valid_methods = ['weighted_average', 'latest', 'source_priority']
        if self.aggregation_method not in valid_methods:
            self.logger.error(f"Invalid aggregation_method: {self.aggregation_method}")
            return False
            
        valid_resolutions = ['latest', 'weighted_average', 'source_priority']
        if self.conflict_resolution not in valid_resolutions:
            self.logger.error(f"Invalid conflict_resolution: {self.conflict_resolution}")
            return False
            
        return True
