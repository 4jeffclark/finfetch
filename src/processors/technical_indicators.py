"""
Technical indicators processor for FinFetch.

This module provides technical analysis indicators for financial data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseProcessor
from ..core.data_models import FinancialData
from ..utils.logger import get_logger


class TechnicalIndicatorsProcessor(BaseProcessor):
    """
    Technical indicators processor for financial data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the technical indicators processor.
        
        Args:
            config: Processor configuration
        """
        super().__init__(config)
        self.indicators = self.config.get('indicators', [
            'sma', 'ema', 'rsi', 'macd', 'bollinger_bands'
        ])
        self.periods = self.config.get('periods', {
            'sma': [20, 50, 200],
            'ema': [12, 26],
            'rsi': 14,
            'macd': [12, 26, 9],
            'bollinger_bands': [20, 2]
        })
        
    @property
    def name(self) -> str:
        """Get processor name."""
        return "Technical Indicators"
        
    def process(self, data: Dict[str, FinancialData]) -> Dict[str, FinancialData]:
        """
        Add technical indicators to financial data.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary mapping symbols to FinancialData objects with indicators
        """
        self._log_processing_start(len(data))
        start_time = datetime.now()
        
        processed_data = {}
        for symbol, financial_data in data.items():
            try:
                processed_financial_data = self._add_indicators(financial_data)
                processed_data[symbol] = processed_financial_data
                
                # Update metadata
                processing_info = {
                    'processor': self.name,
                    'indicators_added': self.indicators,
                    'original_columns': len(financial_data.data.columns),
                    'new_columns': len(processed_financial_data.data.columns)
                }
                self._update_metadata(processed_financial_data, self.name, processing_info)
                
            except Exception as e:
                self._log_processing_error(symbol, e)
                # Keep original data if processing fails
                processed_data[symbol] = financial_data
                
        processing_time = (datetime.now() - start_time).total_seconds()
        self._log_processing_complete(len(processed_data), processing_time)
        
        return processed_data
        
    def _add_indicators(self, financial_data: FinancialData) -> FinancialData:
        """
        Add technical indicators to a single symbol's data.
        
        Args:
            financial_data: FinancialData object to process
            
        Returns:
            FinancialData object with indicators added
        """
        df = financial_data.data.copy()
        
        # Add each indicator
        for indicator in self.indicators:
            if indicator == 'sma':
                df = self._add_sma(df)
            elif indicator == 'ema':
                df = self._add_ema(df)
            elif indicator == 'rsi':
                df = self._add_rsi(df)
            elif indicator == 'macd':
                df = self._add_macd(df)
            elif indicator == 'bollinger_bands':
                df = self._add_bollinger_bands(df)
            elif indicator == 'stochastic':
                df = self._add_stochastic(df)
            elif indicator == 'williams_r':
                df = self._add_williams_r(df)
        
        # Create new FinancialData object
        processed_data = FinancialData(
            symbol=financial_data.symbol,
            data=df,
            metadata=financial_data.metadata.copy(),
            sources=financial_data.sources.copy(),
            last_updated=datetime.now()
        )
        
        return processed_data
        
    def _add_sma(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Simple Moving Average indicators."""
        if 'close' not in df.columns:
            return df
            
        periods = self.periods.get('sma', [20, 50, 200])
        for period in periods:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            
        return df
        
    def _add_ema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Exponential Moving Average indicators."""
        if 'close' not in df.columns:
            return df
            
        periods = self.periods.get('ema', [12, 26])
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
            
        return df
        
    def _add_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Relative Strength Index indicator."""
        if 'close' not in df.columns:
            return df
            
        period = self.periods.get('rsi', 14)
        
        # Calculate price changes
        delta = df['close'].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        df['rsi'] = rsi
        
        return df
        
    def _add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add MACD indicator."""
        if 'close' not in df.columns:
            return df
            
        fast, slow, signal = self.periods.get('macd', [12, 26, 9])
        
        # Calculate EMAs
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        df['macd'] = macd_line
        df['macd_signal'] = signal_line
        df['macd_histogram'] = histogram
        
        return df
        
    def _add_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Bollinger Bands indicator."""
        if 'close' not in df.columns:
            return df
            
        period, std_dev = self.periods.get('bollinger_bands', [20, 2])
        
        # Calculate middle band (SMA)
        middle_band = df['close'].rolling(window=period).mean()
        
        # Calculate standard deviation
        std = df['close'].rolling(window=period).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        df['bb_upper'] = upper_band
        df['bb_middle'] = middle_band
        df['bb_lower'] = lower_band
        
        return df
        
    def _add_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Stochastic Oscillator indicator."""
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            return df
            
        period = self.periods.get('stochastic', 14)
        
        # Calculate lowest low and highest high
        lowest_low = df['low'].rolling(window=period).min()
        highest_high = df['high'].rolling(window=period).max()
        
        # Calculate %K
        k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        
        # Calculate %D (smoothed %K)
        d_percent = k_percent.rolling(window=3).mean()
        
        df['stoch_k'] = k_percent
        df['stoch_d'] = d_percent
        
        return df
        
    def _add_williams_r(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Williams %R indicator."""
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            return df
            
        period = self.periods.get('williams_r', 14)
        
        # Calculate highest high and lowest low
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        # Calculate Williams %R
        williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
        
        df['williams_r'] = williams_r
        
        return df
        
    def validate_config(self) -> bool:
        """Validate processor configuration."""
        valid_indicators = [
            'sma', 'ema', 'rsi', 'macd', 'bollinger_bands', 
            'stochastic', 'williams_r'
        ]
        
        for indicator in self.indicators:
            if indicator not in valid_indicators:
                self.logger.error(f"Invalid indicator: {indicator}")
                return False
                
        return True
