"""
Risk analysis for FinFetch.

This module provides risk analysis capabilities for financial data,
including VaR, CVaR, and correlation analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from scipy import stats

from .base import BaseAnalyzer
from ..core.data_models import FinancialData
from ..utils.logger import get_logger


class RiskAnalyzer(BaseAnalyzer):
    """
    Risk analyzer for financial data.
    
    This analyzer calculates risk metrics including:
    - Value at Risk (VaR) and Conditional VaR (CVaR)
    - Correlation analysis
    - Beta calculations
    - Tail risk metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the risk analyzer.
        
        Args:
            config: Analyzer configuration
        """
        super().__init__(config)
        self.confidence_levels = self.config.get('confidence_levels', [0.95, 0.99])
        self.lookback_days = self.config.get('lookback_days', 252)  # 1 year
        self.benchmark = self.config.get('benchmark', 'SPY')
        
    @property
    def name(self) -> str:
        """Get analyzer name."""
        return "Risk Analyzer"
        
    def analyze(self, data: Dict[str, FinancialData]) -> Dict[str, Any]:
        """
        Analyze risk metrics for all symbols.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary containing risk analysis results
        """
        self._log_analysis_start(len(data))
        start_time = datetime.now()
        
        results = {
            "analysis_type": "risk",
            "timestamp": start_time.isoformat(),
            "symbols": list(data.keys()),
            "metrics": {},
            "correlation_matrix": {},
            "summary": {}
        }
        
        # Calculate risk metrics for each symbol
        returns_data = {}
        for symbol, financial_data in data.items():
            try:
                symbol_metrics = self._analyze_symbol(financial_data)
                results["metrics"][symbol] = symbol_metrics
                
                # Collect returns for correlation analysis
                if "returns" in symbol_metrics:
                    returns_data[symbol] = symbol_metrics["returns"]
                    
            except Exception as e:
                self._log_analysis_error(symbol, e)
                results["metrics"][symbol] = {"error": str(e)}
                
        # Calculate correlation matrix
        if len(returns_data) > 1:
            results["correlation_matrix"] = self._calculate_correlation_matrix(returns_data)
            
        # Calculate summary statistics
        results["summary"] = self._calculate_summary(results["metrics"])
        
        analysis_time = (datetime.now() - start_time).total_seconds()
        self._log_analysis_complete(len(data), analysis_time)
        
        return results
        
    def _analyze_symbol(self, financial_data: FinancialData) -> Dict[str, Any]:
        """
        Analyze risk for a single symbol.
        
        Args:
            financial_data: FinancialData object to analyze
            
        Returns:
            Dictionary containing risk metrics
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
            
        # Use only recent data for risk analysis
        recent_returns = returns.tail(self.lookback_days)
        
        if len(recent_returns) < 30:  # Minimum data requirement
            return {"error": "Insufficient data for risk analysis"}
            
        # VaR and CVaR calculations
        var_metrics = {}
        for confidence in self.confidence_levels:
            var = self._calculate_var(recent_returns, confidence)
            cvar = self._calculate_cvar(recent_returns, confidence)
            
            var_metrics[f"var_{int(confidence*100)}"] = round(var * 100, 2)
            var_metrics[f"cvar_{int(confidence*100)}"] = round(cvar * 100, 2)
            
        # Volatility metrics
        volatility = recent_returns.std() * np.sqrt(252) * 100
        volatility_annualized = recent_returns.std() * np.sqrt(252)
        
        # Tail risk metrics
        skewness = stats.skew(recent_returns)
        kurtosis = stats.kurtosis(recent_returns)
        
        # Maximum drawdown
        cumulative_returns = (1 + recent_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Downside deviation
        negative_returns = recent_returns[recent_returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) * 100 if len(negative_returns) > 0 else 0
        
        return {
            "volatility": round(volatility, 2),
            "volatility_annualized": round(volatility_annualized, 4),
            "max_drawdown": round(max_drawdown, 2),
            "downside_deviation": round(downside_deviation, 2),
            "skewness": round(skewness, 4),
            "kurtosis": round(kurtosis, 4),
            **var_metrics,
            "returns": recent_returns.tolist(),  # For correlation analysis
            "data_points": len(recent_returns)
        }
        
    def _calculate_var(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Value at Risk."""
        return np.percentile(returns, (1 - confidence) * 100)
        
    def _calculate_cvar(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Conditional Value at Risk."""
        var = self._calculate_var(returns, confidence)
        tail_returns = returns[returns <= var]
        return tail_returns.mean() if len(tail_returns) > 0 else var
        
    def _calculate_correlation_matrix(self, returns_data: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate correlation matrix between symbols.
        
        Args:
            returns_data: Dictionary mapping symbols to returns lists
            
        Returns:
            Correlation matrix as nested dictionary
        """
        # Convert to DataFrame
        df = pd.DataFrame(returns_data)
        
        # Calculate correlation matrix
        corr_matrix = df.corr()
        
        # Convert to nested dictionary
        correlation_dict = {}
        for symbol1 in corr_matrix.index:
            correlation_dict[symbol1] = {}
            for symbol2 in corr_matrix.columns:
                correlation_dict[symbol1][symbol2] = round(corr_matrix.loc[symbol1, symbol2], 4)
                
        return correlation_dict
        
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
        volatilities = [m.get("volatility", 0) for m in valid_metrics.values()]
        max_drawdowns = [m.get("max_drawdown", 0) for m in valid_metrics.values()]
        skewnesses = [m.get("skewness", 0) for m in valid_metrics.values()]
        kurtoses = [m.get("kurtosis", 0) for m in valid_metrics.values()]
        
        return {
            "symbol_count": len(valid_metrics),
            "average_volatility": round(np.mean(volatilities), 2),
            "average_max_drawdown": round(np.mean(max_drawdowns), 2),
            "average_skewness": round(np.mean(skewnesses), 4),
            "average_kurtosis": round(np.mean(kurtoses), 4),
            "highest_volatility": max(valid_metrics.items(), key=lambda x: x[1].get("volatility", 0))[0],
            "lowest_volatility": min(valid_metrics.items(), key=lambda x: x[1].get("volatility", 0))[0],
            "highest_skewness": max(valid_metrics.items(), key=lambda x: x[1].get("skewness", 0))[0],
            "highest_kurtosis": max(valid_metrics.items(), key=lambda x: x[1].get("kurtosis", 0))[0]
        }
        
    def validate_config(self) -> bool:
        """Validate analyzer configuration."""
        if not all(0 < cl < 1 for cl in self.confidence_levels):
            self.logger.error(f"Invalid confidence_levels: {self.confidence_levels}")
            return False
            
        if self.lookback_days < 30:
            self.logger.error(f"Invalid lookback_days: {self.lookback_days}")
            return False
            
        return True
