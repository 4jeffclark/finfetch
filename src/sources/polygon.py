"""
Polygon.io data source implementation.

This module provides integration with Polygon.io API for collecting
financial data and market metrics.
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import pandas as pd
from polygon import RESTClient

from .base import BaseDataSource
from ..core.data_models import FinancialData, DataSource
from ..utils.logger import get_logger


class PolygonSource(BaseDataSource):
    """
    Polygon.io data source implementation.
    """
    
    def __init__(self, api_key: str, config: Optional[DataSource] = None):
        """
        Initialize Polygon source.
        
        Args:
            api_key: Polygon.io API key
            config: Data source configuration
        """
        if config is None:
            config = DataSource(
                name="Polygon.io",
                api_key=api_key,
                base_url="https://api.polygon.io",
                rate_limit=5,  # Polygon.io rate limit
                timeout=30
            )
        else:
            config.api_key = api_key
        super().__init__(config)
        
        # Initialize Polygon client
        self.client = RESTClient(api_key=api_key)
        
    async def collect_data(
        self,
        symbols: List[str],
        start_date: Union[str, datetime, date],
        end_date: Union[str, datetime, date],
        **kwargs
    ) -> Dict[str, FinancialData]:
        """
        Collect data from Polygon.io.
        
        Args:
            symbols: List of financial symbols
            start_date: Start date for data collection
            end_date: End date for data collection
            **kwargs: Additional parameters
            
        Returns:
            Dictionary mapping symbols to FinancialData objects
        """
        self.logger.info(f"Collecting data from Polygon.io for {len(symbols)} symbols")
        
        # Validate date range
        start_dt, end_dt = self._validate_date_range(start_date, end_date)
        
        # Collect data for each symbol
        results = {}
        for symbol in symbols:
            try:
                await self._apply_rate_limiting()
                data = await self._fetch_symbol_data(symbol, start_dt, end_dt)
                if data is not None:
                    results[symbol] = data
                    self.logger.info(f"Successfully collected data for {symbol}")
                else:
                    self.logger.warning(f"No data available for {symbol}")
            except Exception as e:
                self.logger.error(f"Error collecting data for {symbol}: {e}")
                
        return results
        
    async def _fetch_symbol_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[FinancialData]:
        """
        Fetch data for a single symbol.
        
        Args:
            symbol: Financial symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            FinancialData object or None if no data
        """
        try:
            # Format dates for Polygon API
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # Get aggregates data
            aggs = self.client.get_aggs(
                symbol, 
                1, 
                "day", 
                start_str, 
                end_str, 
                adjusted=True
            )
            
            if not aggs or len(aggs) == 0:
                return None
                
            # Convert to DataFrame
            df_data = []
            for agg in aggs:
                df_data.append({
                    'timestamp': pd.to_datetime(agg.timestamp, unit='ms'),
                    'open': agg.open,
                    'high': agg.high,
                    'low': agg.low,
                    'close': agg.close,
                    'volume': agg.volume,
                    'vwap': getattr(agg, 'vwap', None),
                    'transactions': getattr(agg, 'transactions', None)
                })
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Create metadata
            metadata = {
                'source': 'Polygon.io',
                'symbol': symbol,
                'data_points': len(df),
                'date_range': {
                    'start': df['timestamp'].min().isoformat(),
                    'end': df['timestamp'].max().isoformat()
                },
                'api_info': {
                    'adjusted': True,
                    'timespan': 'day',
                    'multiplier': 1
                }
            }
            
            return self._create_financial_data(symbol, df, metadata)
            
        except Exception as e:
            self.logger.error(f"Error fetching Polygon data for {symbol}: {e}")
            return None
            
    def validate(self) -> bool:
        """Validate Polygon configuration."""
        return self.config.api_key is not None and len(self.config.api_key) > 0
        
    async def test_connection(self) -> bool:
        """Test connection to Polygon.io."""
        try:
            # Test with a simple request
            aggs = self.client.get_aggs(
                "AAPL", 
                1, 
                "day", 
                "2024-01-01", 
                "2024-01-02", 
                adjusted=True
            )
            return aggs is not None
        except Exception:
            return False
            
    def get_available_indicators(self) -> List[str]:
        """Get list of available indicators from Polygon."""
        return [
            'sma', 'ema', 'rsi', 'macd', 'bollinger_bands',
            'stochastic', 'williams_r', 'atr', 'adx'
        ]
