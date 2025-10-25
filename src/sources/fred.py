"""
FRED (Federal Reserve Economic Data) source implementation.

This module provides integration with FRED API for collecting
economic and financial data.
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import pandas as pd

from .base import BaseDataSource
from ..core.data_models import FinancialData, DataSource
from ..utils.logger import get_logger


class FREDSource(BaseDataSource):
    """
    FRED data source implementation.
    """
    
    def __init__(self, api_key: str, config: Optional[DataSource] = None):
        """
        Initialize FRED source.
        
        Args:
            api_key: FRED API key
            config: Data source configuration
        """
        if config is None:
            config = DataSource(
                name="FRED",
                api_key=api_key,
                base_url="https://api.stlouisfed.org/fred",
                rate_limit=120,  # FRED rate limit
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
        Collect data from FRED.
        
        Args:
            symbols: List of FRED series IDs
            start_date: Start date for data collection
            end_date: End date for data collection
            **kwargs: Additional parameters
            
        Returns:
            Dictionary mapping series IDs to FinancialData objects
        """
        self.logger.info(f"Collecting data from FRED for {len(symbols)} series")
        
        # Validate date range
        start_dt, end_dt = self._validate_date_range(start_date, end_date)
        
        # Collect data for each series
        results = {}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
            for series_id in symbols:
                try:
                    await self._apply_rate_limiting()
                    data = await self._fetch_series_data(session, series_id, start_dt, end_dt)
                    if data is not None:
                        results[series_id] = data
                        self.logger.info(f"Successfully collected data for {series_id}")
                    else:
                        self.logger.warning(f"No data available for {series_id}")
                except Exception as e:
                    self.logger.error(f"Error collecting data for {series_id}: {e}")
                    
        return results
        
    async def _fetch_series_data(
        self,
        session: aiohttp.ClientSession,
        series_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[FinancialData]:
        """
        Fetch data for a single FRED series.
        
        Args:
            session: HTTP session
            series_id: FRED series ID
            start_date: Start date
            end_date: End date
            
        Returns:
            FinancialData object or None if no data
        """
        # Construct URL
        url = f"{self.config.base_url}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.config.api_key,
            'file_type': 'json',
            'observation_start': start_date.strftime('%Y-%m-%d'),
            'observation_end': end_date.strftime('%Y-%m-%d')
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_fred_data(series_id, data)
                else:
                    self.logger.error(f"HTTP {response.status} for {series_id}")
                    return None
        except Exception as e:
            self.logger.error(f"Request failed for {series_id}: {e}")
            return None
            
    def _parse_fred_data(self, series_id: str, data: Dict[str, Any]) -> Optional[FinancialData]:
        """
        Parse FRED API response.
        
        Args:
            series_id: FRED series ID
            data: Raw API response data
            
        Returns:
            FinancialData object or None
        """
        try:
            if 'observations' not in data:
                self.logger.error(f"No observations data in response for {series_id}")
                return None
                
            observations = data['observations']
            
            # Convert to DataFrame
            df_data = []
            for obs in observations:
                if obs['value'] != '.' and obs['value'] is not None:
                    df_data.append({
                        'date': datetime.strptime(obs['date'], '%Y-%m-%d'),
                        'value': float(obs['value'])
                    })
            
            if not df_data:
                return None
                
            df = pd.DataFrame(df_data)
            df = df.sort_values('date').reset_index(drop=True)
            
            # Create metadata
            metadata = {
                'source': 'FRED',
                'series_id': series_id,
                'data_points': len(df),
                'date_range': {
                    'start': df['date'].min().isoformat(),
                    'end': df['date'].max().isoformat()
                },
                'series_info': {
                    'title': data.get('title', ''),
                    'units': data.get('units', ''),
                    'frequency': data.get('frequency', ''),
                    'seasonal_adjustment': data.get('seasonal_adjustment', '')
                }
            }
            
            return self._create_financial_data(series_id, df, metadata)
            
        except Exception as e:
            self.logger.error(f"Error parsing FRED data for {series_id}: {e}")
            return None
            
    def validate(self) -> bool:
        """Validate FRED configuration."""
        return self.config.api_key is not None and len(self.config.api_key) > 0
        
    async def test_connection(self) -> bool:
        """Test connection to FRED."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.base_url}/series/observations"
                params = {
                    'series_id': 'GDP',
                    'api_key': self.config.api_key,
                    'file_type': 'json',
                    'limit': 1
                }
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception:
            return False
