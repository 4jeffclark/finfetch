"""
Stock screening and opportunity identification processor for FinFetch.

This module provides stock screening functionality to identify the best buying
opportunities by calculating risk-adjusted returns, total returns, and 
percentage from 52-week highs for S&P 500 stocks. Based on the rars.py utility
for creating updated CSV tables helpful for reviewing stock buying opportunities.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .base import BaseProcessor
from ..core.data_models import FinancialData
from ..utils.logger import get_logger


class StockScreeningProcessor(BaseProcessor):
    """
    Stock screening processor for identifying the best buying opportunities.
    
    This processor calculates key metrics for stock screening:
    - Annual total returns for performance assessment
    - Sharpe ratios for risk-adjusted return analysis
    - Percentage from 52-week highs for opportunity identification
    - Additional metrics for comprehensive screening
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the stock screening processor.
        
        Args:
            config: Processor configuration for screening parameters
        """
        super().__init__(config)
        self.risk_free_rate = self.config.get('risk_free_rate', 0.03)  # 3% annual risk-free rate
        self.lookback_years = self.config.get('lookback_years', 5)  # 5 years for annual return
        self.week_52_lookback = self.config.get('week_52_lookback', 52)  # 52 weeks for high calculation
        self.min_data_points = self.config.get('min_data_points', 1000)  # Minimum data points required
        
    @property
    def name(self) -> str:
        """Get processor name."""
        return "Stock Screening"
        
    def process(self, data: Dict[str, FinancialData]) -> Dict[str, FinancialData]:
        """
        Calculate stock screening metrics for opportunity identification.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary mapping symbols to FinancialData objects with screening metrics
        """
        self._log_processing_start(len(data))
        start_time = datetime.now()
        
        processed_data = {}
        for symbol, financial_data in data.items():
            try:
                processed_financial_data = self._calculate_metrics(financial_data)
                processed_data[symbol] = processed_financial_data
                
                # Update metadata
                processing_info = {
                    'processor': self.name,
                    'metrics_calculated': True,
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
        
    def _calculate_metrics(self, financial_data: FinancialData) -> FinancialData:
        """
        Calculate financial metrics for a single symbol.
        
        Args:
            financial_data: FinancialData object to process
            
        Returns:
            FinancialData object with metrics added
        """
        df = financial_data.data.copy()
        
        # Check if we have enough data
        if len(df) < self.min_data_points:
            self.logger.warning(f"Insufficient data for {financial_data.symbol}: {len(df)} points")
            return financial_data
        
        # Ensure we have required columns
        if 'close' not in df.columns:
            self.logger.warning(f"No close price data for {financial_data.symbol}")
            return financial_data
            
        # Sort by timestamp if available
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp').reset_index(drop=True)
        elif 'date' in df.columns:
            df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate metrics
        df = self._add_log_returns(df)
        df = self._add_annual_return(df)
        df = self._add_sharpe_ratio(df)
        df = self._add_percentage_from_high(df)
        df = self._add_volatility(df)
        df = self._add_max_drawdown(df)
        
        # Create new FinancialData object
        processed_data = FinancialData(
            symbol=financial_data.symbol,
            data=df,
            metadata=financial_data.metadata.copy(),
            sources=financial_data.sources.copy(),
            last_updated=datetime.now()
        )
        
        return processed_data
        
    def _add_log_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add logarithmic returns."""
        if 'close' not in df.columns:
            return df
            
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        return df
        
    def _add_annual_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate annual total return percentage."""
        if 'close' not in df.columns or len(df) < 2:
            return df
            
        # Get first and last close prices
        first_close = df['close'].iloc[0]
        last_close = df['close'].iloc[-1]
        
        # Calculate years in dataset
        if 'timestamp' in df.columns:
            start_date = df['timestamp'].iloc[0]
            end_date = df['timestamp'].iloc[-1]
        elif 'date' in df.columns:
            start_date = df['date'].iloc[0]
            end_date = df['date'].iloc[-1]
        else:
            # Assume daily data and estimate years
            years = len(df) / 252  # 252 trading days per year
        else:
            years = (end_date - start_date).days / 365.25
            
        # Calculate annual return
        if years > 0:
            ann_return = ((last_close / first_close) ** (1/years) - 1) * 100
        else:
            ann_return = 0
            
        df['ann_total_return_pct'] = ann_return
        return df
        
    def _add_sharpe_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Sharpe ratio."""
        if 'log_ret' not in df.columns:
            df = self._add_log_returns(df)
            
        if 'log_ret' not in df.columns:
            return df
            
        # Calculate daily risk-free rate
        rf_daily = self.risk_free_rate / 252
        
        # Get daily returns
        daily_ret = df['log_ret'].dropna()
        
        if len(daily_ret) == 0:
            df['sharpe_ratio'] = np.nan
            return df
            
        # Calculate excess returns
        excess_mean = daily_ret.mean() - rf_daily
        vol = daily_ret.std()
        
        # Calculate Sharpe ratio
        if vol > 0:
            sharpe = excess_mean / vol * np.sqrt(252)
        else:
            sharpe = np.nan
            
        df['sharpe_ratio'] = sharpe
        return df
        
    def _add_percentage_from_high(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate percentage from 52-week high."""
        if 'high' not in df.columns or 'close' not in df.columns:
            return df
            
        # Get the last 52 weeks of data (or available data)
        lookback_days = min(self.week_52_lookback * 5, len(df))  # 5 trading days per week
        recent_data = df.tail(lookback_days)
        
        if len(recent_data) == 0:
            df['pct_from_52w_high'] = np.nan
            return df
            
        # Find maximum high in the period
        max_high = recent_data['high'].max()
        current_close = df['close'].iloc[-1]
        
        # Calculate percentage from high
        pct_from_high = ((current_close / max_high) - 1) * 100
        df['pct_from_52w_high'] = pct_from_high
        
        return df
        
    def _add_volatility(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate annualized volatility."""
        if 'log_ret' not in df.columns:
            df = self._add_log_returns(df)
            
        if 'log_ret' not in df.columns:
            return df
            
        daily_ret = df['log_ret'].dropna()
        
        if len(daily_ret) == 0:
            df['volatility'] = np.nan
            return df
            
        # Calculate annualized volatility
        vol = daily_ret.std() * np.sqrt(252)
        df['volatility'] = vol
        
        return df
        
    def _add_max_drawdown(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate maximum drawdown."""
        if 'close' not in df.columns:
            return df
            
        # Calculate running maximum
        running_max = df['close'].expanding().max()
        
        # Calculate drawdown
        drawdown = (df['close'] - running_max) / running_max * 100
        
        # Find maximum drawdown
        max_drawdown = drawdown.min()
        df['max_drawdown'] = max_drawdown
        
        return df
        
    def get_stock_screening_table(self, data: Dict[str, FinancialData]) -> pd.DataFrame:
        """
        Generate stock screening table for opportunity identification.
        
        Creates a CSV-ready table showing all stocks with their:
        - Annual total returns (performance)
        - Sharpe ratios (risk-adjusted returns) 
        - Percentage from 52-week highs (opportunity)
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            DataFrame formatted for stock screening CSV output
        """
        results = []
        
        for symbol, financial_data in data.items():
            df = financial_data.data
            
            # Extract key screening metrics (matching rars.py output format)
            screening_metrics = {
                'Ticker': symbol,
                'Ann_Total_Return_%': df.get('ann_total_return_pct', [np.nan]).iloc[-1],
                'Sharpe_Ratio': df.get('sharpe_ratio', [np.nan]).iloc[-1],
                '%_from_52w_High': df.get('pct_from_52w_high', [np.nan]).iloc[-1]
            }
            
            # Round numeric values to 2 decimal places (matching rars.py format)
            for key, value in screening_metrics.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    if key in ['Ann_Total_Return_%', 'Sharpe_Ratio', '%_from_52w_High']:
                        screening_metrics[key] = round(value, 2)
            
            results.append(screening_metrics)
        
        # Create DataFrame and sort by ticker
        df_results = pd.DataFrame(results)
        if not df_results.empty:
            df_results = df_results.sort_values('Ticker')
            
        return df_results
        
    def rank_stocks_by_opportunity(self, data: Dict[str, FinancialData]) -> pd.DataFrame:
        """
        Rank stocks by buying opportunity potential.
        
        Creates a ranked list combining:
        - High Sharpe ratios (good risk-adjusted returns)
        - High percentage from 52-week highs (potential for recovery)
        - Good annual returns (performance)
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            DataFrame with stocks ranked by opportunity score
        """
        screening_table = self.get_stock_screening_table(data)
        
        if screening_table.empty:
            return screening_table
            
        # Calculate opportunity score
        # Higher Sharpe ratio = better risk-adjusted return
        # Higher % from 52w high = more potential upside
        # Higher annual return = better performance
        
        # Normalize metrics (0-1 scale)
        sharpe_norm = (screening_table['Sharpe_Ratio'] - screening_table['Sharpe_Ratio'].min()) / (screening_table['Sharpe_Ratio'].max() - screening_table['Sharpe_Ratio'].min())
        return_norm = (screening_table['Ann_Total_Return_%'] - screening_table['Ann_Total_Return_%'].min()) / (screening_table['Ann_Total_Return_%'].max() - screening_table['Ann_Total_Return_%'].min())
        opportunity_norm = (screening_table['%_from_52w_High'] - screening_table['%_from_52w_High'].min()) / (screening_table['%_from_52w_High'].max() - screening_table['%_from_52w_High'].min())
        
        # Calculate opportunity score (weighted combination)
        # Higher score = better buying opportunity
        screening_table['Opportunity_Score'] = (
            0.4 * sharpe_norm +      # 40% weight on risk-adjusted returns
            0.3 * return_norm +       # 30% weight on performance
            0.3 * opportunity_norm    # 30% weight on upside potential
        )
        
        # Sort by opportunity score (descending)
        ranked_table = screening_table.sort_values('Opportunity_Score', ascending=False)
        
        return ranked_table
        
    def validate_config(self) -> bool:
        """Validate processor configuration."""
        if self.risk_free_rate < 0 or self.risk_free_rate > 1:
            self.logger.error(f"Invalid risk_free_rate: {self.risk_free_rate}")
            return False
            
        if self.lookback_years <= 0:
            self.logger.error(f"Invalid lookback_years: {self.lookback_years}")
            return False
            
        if self.min_data_points <= 0:
            self.logger.error(f"Invalid min_data_points: {self.min_data_points}")
            return False
            
        return True
