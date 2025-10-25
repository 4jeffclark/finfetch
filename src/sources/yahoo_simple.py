"""
Simple Yahoo Finance data source using yfinance.

This module provides a straightforward interface to Yahoo Finance data.
"""

import logging
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)


class YahooSimpleSource:
    """Simple Yahoo Finance data source using yfinance library."""
    
    def __init__(self):
        """Initialize the Yahoo Finance source."""
        self.name = "yahoo_simple"
    
    def collect_data(
        self, 
        symbols: List[str], 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Collect financial data for given symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date for data collection
            end_date: End date for data collection
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
            
        data = {}
        
        for symbol in symbols:
            try:
                logger.info(f"Collecting data for {symbol}")
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if df.empty:
                    logger.warning(f"No data found for {symbol}")
                    continue
                    
                # Standardize column names and reset index
                df.columns = df.columns.str.lower()
                df.index.name = 'date'
                df.reset_index(inplace=True)
                
                # Ensure we have the required columns
                required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
                if all(col in df.columns for col in required_cols):
                    data[symbol] = df
                    logger.info(f"Collected {len(df)} records for {symbol}")
                else:
                    logger.warning(f"Missing required columns for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {e}")
                continue
                
        return data
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get current quote for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'price': info.get('currentPrice', 0),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
