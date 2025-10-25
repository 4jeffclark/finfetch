"""
Alpha Vantage data source implementation.

This module provides integration with Alpha Vantage API for collecting
financial data.
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import pandas as pd

from .base import BaseDataSource
from ..core.data_models import FinancialData, DataSource
from ..utils.logger import get_logger


class AlphaVantageSource(BaseDataSource):
    """
    Alpha Vantage data source implementation.
    """
    
    def __init__(self, api_key: str, config: Optional[DataSource] = None):
        """
        Initialize Alpha Vantage source.
        
        Args:
            api_key: Alpha Vantage API key
            config: Data source configuration
        """
        if config is None:
            config = DataSource(
                name="Alpha Vantage",
                api_key=api_key,
                base_url="https://www.alphavantage.co/query",
                rate_limit=5,  # Alpha Vantage free tier limit
                timeout=30
            )
        else:
            config.api_key = api_key
        super().__init__(config)
        
    async def collect_data(
        self,
        symbols: List[str],
        start_date: Union[str, datetime, date],
        end_date: Union[str, datetime, date],
        **kwargs
    ) -> Dict[str, FinancialData]:
        """
        Collect data from Alpha Vantage.
        
        Args:
            symbols: List of financial symbols
            start_date: Start date for data collection
            end_date: End date for data collection
            **kwargs: Additional parameters
            
        Returns:
            Dictionary mapping symbols to FinancialData objects
        """
        self.logger.info(f"Collecting data from Alpha Vantage for {len(symbols)} symbols")
        
        # Validate date range
        start_dt, end_dt = self._validate_date_range(start_date, end_date)
        
        # Collect data for each symbol
        results = {}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
            for symbol in symbols:
                try:
                    await self._apply_rate_limiting()
                    data = await self._fetch_symbol_data(session, symbol, start_dt, end_dt)
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
        session: aiohttp.ClientSession,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[FinancialData]:
        """
        Fetch data for a single symbol.
        
        Args:
            session: HTTP session
            symbol: Financial symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            FinancialData object or None if no data
        """
        # Construct URL for daily time series
        url = self.config.base_url
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': self.config.api_key,
            'outputsize': 'full'
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_alpha_vantage_data(symbol, data, start_date, end_date)
                else:
                    self.logger.error(f"HTTP {response.status} for {symbol}")
                    return None
        except Exception as e:
            self.logger.error(f"Request failed for {symbol}: {e}")
            return None
            
    def _parse_alpha_vantage_data(
        self,
        symbol: str,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> Optional[FinancialData]:
        """
        Parse Alpha Vantage API response.
        
        Args:
            symbol: Financial symbol
            data: Raw API response data
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            FinancialData object or None
        """
        try:
            if 'Time Series (Daily)' not in data:
                self.logger.error(f"No time series data in response for {symbol}")
                return None
                
            time_series = data['Time Series (Daily)']
            
            # Convert to DataFrame
            df_data = []
            for date_str, values in time_series.items():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                
                # Filter by date range
                if start_date <= date_obj <= end_date:
                    df_data.append({
                        'date': date_obj,
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close']),
                        'volume': int(values['5. volume'])
                    })
            
            if not df_data:
                return None
                
            df = pd.DataFrame(df_data)
            df = df.sort_values('date').reset_index(drop=True)
            
            # Create metadata
            metadata = {
                'source': 'Alpha Vantage',
                'symbol': symbol,
                'data_points': len(df),
                'date_range': {
                    'start': df['date'].min().isoformat(),
                    'end': df['date'].max().isoformat()
                },
                'api_info': {
                    'function': data.get('Meta Data', {}).get('2. Symbol', symbol),
                    'last_refreshed': data.get('Meta Data', {}).get('3. Last Refreshed', '')
                }
            }
            
            return self._create_financial_data(symbol, df, metadata)
            
        except Exception as e:
            self.logger.error(f"Error parsing Alpha Vantage data for {symbol}: {e}")
            return None
            
    def validate(self) -> bool:
        """Validate Alpha Vantage configuration."""
        return self.config.api_key is not None and len(self.config.api_key) > 0
        
    async def test_connection(self) -> bool:
        """Test connection to Alpha Vantage."""
        try:
            async with aiohttp.ClientSession() as session:
                url = self.config.base_url
                params = {
                    'function': 'TIME_SERIES_DAILY',
                    'symbol': 'AAPL',
                    'apikey': self.config.api_key
                }
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception:
            return False
