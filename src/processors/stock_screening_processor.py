"""
Stock screening processor for FinFetch.

This module provides stock screening capabilities with real financial metrics.
"""

import logging
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sources.yahoo_simple import YahooSimpleSource
from processors.financial_metrics_calculator import FinancialMetricsCalculator

logger = logging.getLogger(__name__)


class StockScreeningProcessor:
    """Process stock screening with real financial metrics."""
    
    def __init__(self, risk_free_rate: float = 0.0366, benchmark_symbol: str = "SPY"):
        """
        Initialize the screening processor.
        
        Args:
            risk_free_rate: Annual risk-free rate (default 3.66%)
            benchmark_symbol: Benchmark symbol for alpha/beta calculations (default SPY)
        """
        self.data_source = YahooSimpleSource()
        self.metrics_calculator = FinancialMetricsCalculator(risk_free_rate, benchmark_symbol)
        self.benchmark_symbol = benchmark_symbol
    
    def screen_stocks(
        self, 
        symbols: List[str], 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Screen stocks and calculate financial metrics.
        
        Args:
            symbols: List of stock symbols to screen
            start_date: Start date for data collection
            end_date: End date for data collection
            
        Returns:
            List of dictionaries containing screening results
        """
        logger.info(f"Screening {len(symbols)} stocks: {', '.join(symbols)}")
        
        # Collect data for all symbols
        data = self.data_source.collect_data(symbols, start_date, end_date)
        
        if not data:
            logger.warning("No data collected for any symbols")
            return []
        
        # Collect benchmark data for calculations
        benchmark_data = None
        try:
            benchmark_data_dict = self.data_source.collect_data([self.benchmark_symbol], start_date, end_date)
            if self.benchmark_symbol in benchmark_data_dict:
                benchmark_data = benchmark_data_dict[self.benchmark_symbol].copy()
                # Ensure benchmark data has the same processing as stock data
                if 'daily_return' not in benchmark_data.columns:
                    benchmark_data['daily_return'] = benchmark_data['close'].pct_change()
                logger.info(f"Collected {self.benchmark_symbol} benchmark data")
            else:
                logger.warning(f"Failed to collect {self.benchmark_symbol} benchmark data")
        except Exception as e:
            logger.warning(f"Error collecting {self.benchmark_symbol} data: {e}")
        
        # Calculate metrics for each symbol
        results = []
        for symbol, df in data.items():
            try:
                metrics = self.metrics_calculator.calculate_metrics(df, symbol, benchmark_data)
                if metrics:
                    results.append(metrics)
                    logger.info(f"Calculated metrics for {symbol}")
                else:
                    logger.warning(f"Failed to calculate metrics for {symbol}")
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        # Sort by Sharpe ratio (descending)
        results.sort(key=lambda x: x.get('sharpe_ratio', -999), reverse=True)
        
        logger.info(f"Screening completed. Processed {len(results)} stocks successfully")
        return results
    
    def format_results(self, results: List[Dict], format_type: str = 'table') -> str:
        """
        Format screening results for display.
        
        Args:
            results: List of screening results
            format_type: Format type ('table', 'csv', 'json')
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results to display"
        
        # Define the standard set of metrics to display
        standard_metrics = self._get_standard_metrics(results)
        
        if format_type == 'table':
            return self._format_table(standard_metrics)
        elif format_type == 'csv':
            return self._format_csv(standard_metrics)
        else:
            return str(standard_metrics)
    
    def _get_standard_metrics(self, results: List[Dict]) -> List[Dict]:
        """
        Extract and standardize metrics for consistent display.
        
        Returns a consistent set of metrics regardless of output format.
        """
        standard_results = []
        
        for result in results:
            # Extract the core metrics we want to display
            standard_result = {
                'symbol': result.get('symbol', 'N/A'),
                'current_price': result.get('current_price', 0),
                'annualized_return': result.get('annualized_return', 0),
                'total_return': result.get('total_return', 0),
                'sharpe_ratio': result.get('sharpe_ratio', 0),
                'alpha': result.get('alpha', 0),
                'beta': result.get('beta', 0),
                'volatility': result.get('volatility', 0),
                'max_drawdown': result.get('max_drawdown', 0),
                'percent_from_high': result.get('percent_from_high', 0),
                'percent_from_low': result.get('percent_from_low', 0),
                'rsi': result.get('rsi', 0),
                'volume_ratio': result.get('volume_ratio', 0),
                'high_52w': result.get('high_52w', 0),
                'low_52w': result.get('low_52w', 0),
                'sma_20': result.get('sma_20', 0),
                'sma_50': result.get('sma_50', 0),
                'data_points': result.get('data_points', 0)
            }
            standard_results.append(standard_result)
        
        return standard_results
    
    def _format_table(self, results: List[Dict]) -> str:
        """Format results as a table with comprehensive metrics."""
        if not results:
            return "No results"
        
        # Create header with more comprehensive metrics
        header = [
            "Symbol", "Price", "Return%", "Sharpe", "Alpha%", "Beta", 
            "Volatility%", "Max DD%", "From High%", "From Low%", "RSI", "Vol Ratio"
        ]
        
        # Format data rows
        rows = []
        for result in results:
            row = [
                result.get('symbol', 'N/A'),
                f"${result.get('current_price', 0):.2f}",
                f"{result.get('annualized_return', 0):.1f}%",
                f"{result.get('sharpe_ratio', 0):.2f}",
                f"{result.get('alpha', 0):.1f}%",
                f"{result.get('beta', 0):.2f}",
                f"{result.get('volatility', 0):.1f}%",
                f"{result.get('max_drawdown', 0):.1f}%",
                f"{result.get('percent_from_high', 0):.1f}%",
                f"{result.get('percent_from_low', 0):.1f}%",
                f"{result.get('rsi', 0):.0f}",
                f"{result.get('volume_ratio', 0):.1f}x"
            ]
            rows.append(row)
        
        # Calculate column widths
        col_widths = [max(len(str(header[i])), max(len(str(row[i])) for row in rows)) for i in range(len(header))]
        
        # Create table
        table_lines = []
        
        # Header
        header_line = " | ".join(header[i].ljust(col_widths[i]) for i in range(len(header)))
        table_lines.append(header_line)
        table_lines.append("-" * len(header_line))
        
        # Data rows
        for row in rows:
            row_line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
            table_lines.append(row_line)
        
        return "\n".join(table_lines)
    
    def _format_csv(self, results: List[Dict]) -> str:
        """Format results as CSV with consistent columns."""
        if not results:
            return "No results"
        
        # Define the standard columns we want in CSV (same as table, but more comprehensive)
        standard_columns = [
            'symbol', 'current_price', 'annualized_return', 'total_return', 
            'sharpe_ratio', 'alpha', 'beta', 'volatility', 'max_drawdown',
            'percent_from_high', 'percent_from_low', 'rsi', 'volume_ratio',
            'high_52w', 'low_52w', 'sma_20', 'sma_50', 'data_points'
        ]
        
        # Create CSV header
        csv_lines = [",".join(standard_columns)]
        
        # Create CSV rows
        for result in results:
            row = []
            for col in standard_columns:
                value = result.get(col, '')
                # Format numeric values appropriately
                if isinstance(value, (int, float)) and col != 'data_points':
                    if col in ['current_price', 'high_52w', 'low_52w', 'sma_20', 'sma_50']:
                        row.append(f"{value:.2f}")
                    elif col in ['annualized_return', 'total_return', 'alpha', 'volatility', 'max_drawdown', 'percent_from_high', 'percent_from_low']:
                        row.append(f"{value:.2f}")
                    elif col in ['sharpe_ratio', 'beta', 'rsi']:
                        row.append(f"{value:.2f}")
                    else:
                        row.append(f"{value:.2f}")
                else:
                    row.append(str(value))
            csv_lines.append(",".join(row))
        
        return "\n".join(csv_lines)
