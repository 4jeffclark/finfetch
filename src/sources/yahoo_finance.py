"""
Yahoo Finance data source implementation.

This module provides integration with Yahoo Finance for collecting
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


class YahooFinanceSource(BaseDataSource):
    """
    Yahoo Finance data source implementation.
    """
    
    def __init__(self, config: Optional[DataSource] = None):
        """
        Initialize Yahoo Finance source.
        
        Args:
            config: Data source configuration
        """
        if config is None:
            config = DataSource(
                name="Yahoo Finance",
                base_url="https://query1.finance.yahoo.com",
                rate_limit=2000,  # Yahoo Finance rate limit
                timeout=30
            )
        super().__init__(config)
        
    async def collect_data(
        self,
        symbols: List[str],
        start_date: Union[str, datetime, date],
        end_date: Union[str, datetime, date],
        **kwargs
    ) -> Dict[str, FinancialData]:
        """
        Collect data from Yahoo Finance.
        
        Args:
            symbols: List of financial symbols
            start_date: Start date for data collection
            end_date: End date for data collection
            **kwargs: Additional parameters
            
        Returns:
            Dictionary mapping symbols to FinancialData objects
        """
        self.logger.info(f"Collecting data from Yahoo Finance for {len(symbols)} symbols")
        
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
        # Convert dates to timestamps
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        
        # Construct URL
        url = f"{self.config.base_url}/v8/finance/chart/{symbol}"
        params = {
            'period1': start_timestamp,
            'period2': end_timestamp,
            'interval': '1d',
            'includePrePost': 'true',
            'events': 'div,split'
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_yahoo_data(symbol, data)
                else:
                    self.logger.error(f"HTTP {response.status} for {symbol}")
                    return None
        except Exception as e:
            self.logger.error(f"Request failed for {symbol}: {e}")
            return None
            
    def _parse_yahoo_data(self, symbol: str, data: Dict[str, Any]) -> Optional[FinancialData]:
        """
        Parse Yahoo Finance API response.
        
        Args:
            symbol: Financial symbol
            data: Raw API response data
            
        Returns:
            FinancialData object or None
        """
        try:
            if 'chart' not in data or 'result' not in data['chart']:
                return None
                
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            # Create DataFrame
            df_data = {
                'date': [datetime.fromtimestamp(ts) for ts in timestamps],
                'open': quotes.get('open', []),
                'high': quotes.get('high', []),
                'low': quotes.get('low', []),
                'close': quotes.get('close', []),
                'volume': quotes.get('volume', [])
            }
            
            df = pd.DataFrame(df_data)
            
            # Remove rows with all NaN values
            df = df.dropna(how='all')
            
            if df.empty:
                return None
                
            # Create metadata
            metadata = {
                'source': 'Yahoo Finance',
                'symbol': symbol,
                'data_points': len(df),
                'date_range': {
                    'start': df['date'].min().isoformat(),
                    'end': df['date'].max().isoformat()
                }
            }
            
            return self._create_financial_data(symbol, df, metadata)
            
        except Exception as e:
            self.logger.error(f"Error parsing Yahoo data for {symbol}: {e}")
            return None
            
    def validate(self) -> bool:
        """Validate Yahoo Finance configuration."""
        return True  # Yahoo Finance doesn't require API keys
        
    async def test_connection(self) -> bool:
        """Test connection to Yahoo Finance."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.base_url}/v8/finance/chart/AAPL"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception:
            return False
