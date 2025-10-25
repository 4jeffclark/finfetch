"""
Financial metrics calculator for stock screening.

This module provides calculations for common financial metrics used in stock screening.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FinancialMetricsCalculator:
    """Calculate financial metrics for stock screening."""
    
    def __init__(self, risk_free_rate: float = 0.0366, benchmark_symbol: str = "SPY"):
        """
        Initialize the calculator.
        
        Args:
            risk_free_rate: Annual risk-free rate (default 3.66% - current Treasury rate)
            benchmark_symbol: Benchmark symbol for alpha calculation (default SPY)
        """
        self.risk_free_rate = risk_free_rate
        self.benchmark_symbol = benchmark_symbol
    
    def calculate_metrics(self, data: pd.DataFrame, symbol: str, benchmark_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Calculate comprehensive financial metrics for a stock.
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Stock symbol
            benchmark_data: Optional benchmark data (SPY) for alpha/beta calculation
            
        Returns:
            Dictionary of calculated metrics
        """
        try:
            # Ensure we have the required columns
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_cols):
                logger.error(f"Missing required columns for {symbol}")
                return {}
            
            # Sort by date
            data = data.sort_values('date').reset_index(drop=True)
            
            # Calculate returns
            data['daily_return'] = data['close'].pct_change()
            data['log_return'] = np.log(data['close'] / data['close'].shift(1))
            
            # Remove NaN values
            data = data.dropna()
            
            if len(data) < 30:  # Need at least 30 days of data
                logger.warning(f"Insufficient data for {symbol}: {len(data)} days")
                return {}
            
            metrics = {
                'symbol': symbol,
                'data_points': len(data),
                'date_range': {
                    'start': data['date'].min().strftime('%Y-%m-%d'),
                    'end': data['date'].max().strftime('%Y-%m-%d')
                }
            }
            
            # Basic price metrics
            metrics.update(self._calculate_price_metrics(data))
            
            # Risk metrics
            metrics.update(self._calculate_risk_metrics(data, benchmark_data))
            
            # Performance metrics
            metrics.update(self._calculate_performance_metrics(data, benchmark_data))
            
            # Technical metrics
            metrics.update(self._calculate_technical_metrics(data))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics for {symbol}: {e}")
            return {}
    
    def _calculate_price_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate basic price metrics."""
        current_price = data['close'].iloc[-1]
        high_52w = data['high'].max()
        low_52w = data['low'].min()
        
        return {
            'current_price': round(current_price, 2),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'percent_from_high': round(((current_price - high_52w) / high_52w) * 100, 2),
            'percent_from_low': round(((current_price - low_52w) / low_52w) * 100, 2)
        }
    
    def _calculate_risk_metrics(self, data: pd.DataFrame, benchmark_data: Optional[pd.DataFrame] = None) -> Dict:
        """Calculate risk metrics."""
        returns = data['daily_return'].dropna()
        
        # Volatility (annualized)
        volatility = returns.std() * np.sqrt(252)
        
        # Beta calculation with benchmark
        beta = 1.0  # Default if no benchmark
        if benchmark_data is not None and 'daily_return' in benchmark_data.columns:
            benchmark_returns = benchmark_data['daily_return'].dropna()
            # Align the data by date
            aligned_data = pd.merge(
                data[['date', 'daily_return']], 
                benchmark_data[['date', 'daily_return']], 
                on='date', 
                suffixes=('_stock', '_benchmark')
            )
            if len(aligned_data) > 10:  # Need sufficient data points
                stock_returns = aligned_data['daily_return_stock'].dropna()
                bench_returns = aligned_data['daily_return_benchmark'].dropna()
                if len(stock_returns) > 10 and len(bench_returns) > 10:
                    # Calculate beta: Cov(stock, benchmark) / Var(benchmark)
                    covariance = np.cov(stock_returns, bench_returns)[0, 1]
                    benchmark_variance = np.var(bench_returns)
                    if benchmark_variance > 0:
                        beta = covariance / benchmark_variance
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'volatility': round(volatility * 100, 2),  # As percentage
            'beta': round(beta, 2),
            'max_drawdown': round(max_drawdown * 100, 2)  # As percentage
        }
    
    def _calculate_performance_metrics(self, data: pd.DataFrame, benchmark_data: Optional[pd.DataFrame] = None) -> Dict:
        """Calculate performance metrics."""
        returns = data['daily_return'].dropna()
        
        # Total return
        total_return = (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
        
        # Annualized return
        days = (data['date'].iloc[-1] - data['date'].iloc[0]).days
        annualized_return = (1 + total_return) ** (365 / days) - 1
        
        # Sharpe ratio
        excess_return = returns.mean() * 252 - self.risk_free_rate
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # Alpha calculation with benchmark
        alpha = 0.0  # Default if no benchmark
        if benchmark_data is not None and 'daily_return' in benchmark_data.columns:
            benchmark_returns = benchmark_data['daily_return'].dropna()
            # Align the data by date
            aligned_data = pd.merge(
                data[['date', 'daily_return']], 
                benchmark_data[['date', 'daily_return']], 
                on='date', 
                suffixes=('_stock', '_benchmark')
            )
            if len(aligned_data) > 10:  # Need sufficient data points
                stock_returns = aligned_data['daily_return_stock'].dropna()
                bench_returns = aligned_data['daily_return_benchmark'].dropna()
                if len(stock_returns) > 10 and len(bench_returns) > 10:
                    # Calculate alpha: (stock_return - risk_free_rate) - beta * (benchmark_return - risk_free_rate)
                    stock_annualized = stock_returns.mean() * 252
                    bench_annualized = bench_returns.mean() * 252
                    
                    # Get beta from risk metrics (we'll calculate it here too)
                    covariance = np.cov(stock_returns, bench_returns)[0, 1]
                    benchmark_variance = np.var(bench_returns)
                    beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
                    
                    # Alpha = (R_stock - Rf) - beta * (R_benchmark - Rf)
                    alpha = (stock_annualized - self.risk_free_rate) - beta * (bench_annualized - self.risk_free_rate)
        else:
            # Fallback to simple alpha if no benchmark
            alpha = annualized_return - self.risk_free_rate
        
        return {
            'total_return': round(total_return * 100, 2),  # As percentage
            'annualized_return': round(annualized_return * 100, 2),  # As percentage
            'sharpe_ratio': round(sharpe_ratio, 2),
            'alpha': round(alpha * 100, 2)  # As percentage
        }
    
    def _calculate_technical_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators."""
        # Simple Moving Averages
        sma_20 = data['close'].rolling(window=20).mean().iloc[-1]
        sma_50 = data['close'].rolling(window=50).mean().iloc[-1]
        
        # RSI (simplified)
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        # Volume metrics
        avg_volume = data['volume'].mean()
        current_volume = data['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        return {
            'sma_20': round(sma_20, 2),
            'sma_50': round(sma_50, 2),
            'rsi': round(current_rsi, 2),
            'volume_ratio': round(volume_ratio, 2)
        }
