"""
Performance analysis for FinFetch.

This module provides performance analysis capabilities for financial data,
including returns, volatility, and benchmark comparisons.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseAnalyzer
from ..core.data_models import FinancialData
from ..utils.logger import get_logger


class PerformanceAnalyzer(BaseAnalyzer):
    """
    Performance analyzer for financial data.
    
    This analyzer calculates performance metrics including:
    - Total returns and annualized returns
    - Volatility and risk metrics
    - Benchmark comparisons
    - Performance attribution
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the performance analyzer.
        
        Args:
            config: Analyzer configuration
        """
        super().__init__(config)
        self.benchmark = self.config.get('benchmark', 'SPY')
        self.risk_free_rate = self.config.get('risk_free_rate', 0.03)
        self.lookback_periods = self.config.get('lookback_periods', [30, 90, 252, 504])  # 1M, 3M, 1Y, 2Y
        
    @property
    def name(self) -> str:
        """Get analyzer name."""
        return "Performance Analyzer"
        
    def analyze(self, data: Dict[str, FinancialData]) -> Dict[str, Any]:
        """
        Analyze performance metrics for all symbols.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary containing performance analysis results
        """
        self._log_analysis_start(len(data))
        start_time = datetime.now()
        
        results = {
            "analysis_type": "performance",
            "timestamp": start_time.isoformat(),
            "symbols": list(data.keys()),
            "metrics": {},
            "summary": {}
        }
        
        # Calculate metrics for each symbol
        for symbol, financial_data in data.items():
            try:
                symbol_metrics = self._analyze_symbol(financial_data)
                results["metrics"][symbol] = symbol_metrics
            except Exception as e:
                self._log_analysis_error(symbol, e)
                results["metrics"][symbol] = {"error": str(e)}
                
        # Calculate summary statistics
        results["summary"] = self._calculate_summary(results["metrics"])
        
        analysis_time = (datetime.now() - start_time).total_seconds()
        self._log_analysis_complete(len(data), analysis_time)
        
        return results
        
    def _analyze_symbol(self, financial_data: FinancialData) -> Dict[str, Any]:
        """
        Analyze performance for a single symbol.
        
        Args:
            financial_data: FinancialData object to analyze
            
        Returns:
            Dictionary containing performance metrics
        """
        df = financial_data.data
        
        if df.empty or 'close' not in df.columns:
            return {"error": "No price data available"}
            
        # Ensure data is sorted by date
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp').reset_index(drop=True)
        elif 'date' in df.columns:
            df = df.sort_values('date').reset_index(drop=True)
            
        # Calculate returns
        returns = df['close'].pct_change().dropna()
        
        if len(returns) == 0:
            return {"error": "No returns data available"}
            
        # Basic performance metrics
        total_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
        
        # Annualized return
        years = len(df) / 252  # Assume 252 trading days per year
        annualized_return = ((df['close'].iloc[-1] / df['close'].iloc[0]) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # Volatility metrics
        volatility = returns.std() * np.sqrt(252) * 100
        
        # Risk metrics
        sharpe_ratio = (annualized_return - self.risk_free_rate * 100) / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Lookback period analysis
        lookback_analysis = {}
        for period in self.lookback_periods:
            if len(returns) >= period:
                period_returns = returns.tail(period)
                period_return = (df['close'].iloc[-1] / df['close'].iloc[-period] - 1) * 100
                period_volatility = period_returns.std() * np.sqrt(252) * 100
                period_sharpe = (period_return - self.risk_free_rate * 100) / period_volatility if period_volatility > 0 else 0
                
                lookback_analysis[f"{period}d"] = {
                    "return": round(period_return, 2),
                    "volatility": round(period_volatility, 2),
                    "sharpe_ratio": round(period_sharpe, 2)
                }
        
        return {
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return, 2),
            "volatility": round(volatility, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown, 2),
            "lookback_analysis": lookback_analysis,
            "data_points": len(df),
            "date_range": {
                "start": df.iloc[0].get('timestamp', df.iloc[0].get('date', 'unknown')),
                "end": df.iloc[-1].get('timestamp', df.iloc[-1].get('date', 'unknown'))
            }
        }
        
    def _calculate_summary(self, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics across all symbols.
        
        Args:
            metrics: Dictionary of symbol metrics
            
        Returns:
            Dictionary containing summary statistics
        """
        valid_metrics = {k: v for k, v in metrics.items() if "error" not in v}
        
        if not valid_metrics:
            return {"error": "No valid metrics available"}
            
        # Calculate averages
        returns = [m.get("annualized_return", 0) for m in valid_metrics.values()]
        volatilities = [m.get("volatility", 0) for m in valid_metrics.values()]
        sharpe_ratios = [m.get("sharpe_ratio", 0) for m in valid_metrics.values()]
        
        return {
            "symbol_count": len(valid_metrics),
            "average_return": round(np.mean(returns), 2),
            "average_volatility": round(np.mean(volatilities), 2),
            "average_sharpe": round(np.mean(sharpe_ratios), 2),
            "best_performer": max(valid_metrics.items(), key=lambda x: x[1].get("annualized_return", 0))[0],
            "worst_performer": min(valid_metrics.items(), key=lambda x: x[1].get("annualized_return", 0))[0],
            "highest_sharpe": max(valid_metrics.items(), key=lambda x: x[1].get("sharpe_ratio", 0))[0],
            "lowest_volatility": min(valid_metrics.items(), key=lambda x: x[1].get("volatility", 0))[0]
        }
        
    def validate_config(self) -> bool:
        """Validate analyzer configuration."""
        if self.risk_free_rate < 0 or self.risk_free_rate > 1:
            self.logger.error(f"Invalid risk_free_rate: {self.risk_free_rate}")
            return False
            
        if not isinstance(self.lookback_periods, list) or len(self.lookback_periods) == 0:
            self.logger.error(f"Invalid lookback_periods: {self.lookback_periods}")
            return False
            
        return True
