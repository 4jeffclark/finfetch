"""
Portfolio analysis for FinFetch.

This module provides portfolio analysis capabilities for financial data,
including portfolio optimization, risk attribution, and performance attribution.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .base import BaseAnalyzer
from ..core.data_models import FinancialData
from ..utils.logger import get_logger


class PortfolioAnalyzer(BaseAnalyzer):
    """
    Portfolio analyzer for financial data.
    
    This analyzer calculates portfolio metrics including:
    - Portfolio returns and volatility
    - Risk attribution
    - Performance attribution
    - Portfolio optimization metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the portfolio analyzer.
        
        Args:
            config: Analyzer configuration
        """
        super().__init__(config)
        self.benchmark = self.config.get('benchmark', 'SPY')
        self.risk_free_rate = self.config.get('risk_free_rate', 0.03)
        self.rebalance_frequency = self.config.get('rebalance_frequency', 'monthly')
        self.optimization_method = self.config.get('optimization_method', 'equal_weight')
        
    @property
    def name(self) -> str:
        """Get analyzer name."""
        return "Portfolio Analyzer"
        
    def analyze(self, data: Dict[str, FinancialData]) -> Dict[str, Any]:
        """
        Analyze portfolio metrics for all symbols.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary containing portfolio analysis results
        """
        self._log_analysis_start(len(data))
        start_time = datetime.now()
        
        results = {
            "analysis_type": "portfolio",
            "timestamp": start_time.isoformat(),
            "symbols": list(data.keys()),
            "portfolio_metrics": {},
            "optimization": {},
            "attribution": {},
            "summary": {}
        }
        
        try:
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(data)
            results["portfolio_metrics"] = portfolio_metrics
            
            # Portfolio optimization
            optimization = self._optimize_portfolio(data)
            results["optimization"] = optimization
            
            # Risk attribution
            attribution = self._calculate_attribution(data)
            results["attribution"] = attribution
            
            # Summary
            results["summary"] = self._calculate_summary(portfolio_metrics, optimization)
            
        except Exception as e:
            self.logger.error(f"Portfolio analysis failed: {e}")
            results["error"] = str(e)
            
        analysis_time = (datetime.now() - start_time).total_seconds()
        self._log_analysis_complete(len(data), analysis_time)
        
        return results
        
    def _calculate_portfolio_metrics(self, data: Dict[str, FinancialData]) -> Dict[str, Any]:
        """
        Calculate portfolio-level metrics.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary containing portfolio metrics
        """
        # Prepare returns data
        returns_data = {}
        for symbol, financial_data in data.items():
            df = financial_data.data
            if not df.empty and 'close' in df.columns:
                returns = df['close'].pct_change().dropna()
                if len(returns) > 0:
                    returns_data[symbol] = returns
                    
        if len(returns_data) < 2:
            return {"error": "Insufficient data for portfolio analysis"}
            
        # Align returns data
        returns_df = pd.DataFrame(returns_data).dropna()
        
        if len(returns_df) < 30:
            return {"error": "Insufficient aligned data for portfolio analysis"}
            
        # Equal weight portfolio (default)
        weights = np.ones(len(returns_data)) / len(returns_data)
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Portfolio metrics
        total_return = (1 + portfolio_returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Correlation analysis
        correlation_matrix = returns_df.corr()
        avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
        
        return {
            "total_return": round(total_return * 100, 2),
            "annualized_return": round(annualized_return * 100, 2),
            "volatility": round(volatility * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 4),
            "max_drawdown": round(max_drawdown * 100, 2),
            "avg_correlation": round(avg_correlation, 4),
            "data_points": len(portfolio_returns),
            "weights": {symbol: round(weight, 4) for symbol, weight in zip(returns_data.keys(), weights)}
        }
        
    def _optimize_portfolio(self, data: Dict[str, FinancialData]) -> Dict[str, Any]:
        """
        Optimize portfolio weights.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary containing optimization results
        """
        # Prepare returns data
        returns_data = {}
        for symbol, financial_data in data.items():
            df = financial_data.data
            if not df.empty and 'close' in df.columns:
                returns = df['close'].pct_change().dropna()
                if len(returns) > 0:
                    returns_data[symbol] = returns
                    
        if len(returns_data) < 2:
            return {"error": "Insufficient data for portfolio optimization"}
            
        # Align returns data
        returns_df = pd.DataFrame(returns_data).dropna()
        
        if len(returns_df) < 30:
            return {"error": "Insufficient aligned data for portfolio optimization"}
            
        # Calculate covariance matrix
        cov_matrix = returns_df.cov() * 252  # Annualized
        
        # Mean returns
        mean_returns = returns_df.mean() * 252  # Annualized
        
        # Portfolio optimization methods
        optimization_results = {}
        
        # Equal weight (baseline)
        equal_weights = np.ones(len(returns_data)) / len(returns_data)
        equal_portfolio_return = np.dot(equal_weights, mean_returns)
        equal_portfolio_vol = np.sqrt(np.dot(equal_weights.T, np.dot(cov_matrix, equal_weights)))
        equal_sharpe = (equal_portfolio_return - self.risk_free_rate) / equal_portfolio_vol if equal_portfolio_vol > 0 else 0
        
        optimization_results["equal_weight"] = {
            "weights": {symbol: round(weight, 4) for symbol, weight in zip(returns_data.keys(), equal_weights)},
            "expected_return": round(equal_portfolio_return * 100, 2),
            "volatility": round(equal_portfolio_vol * 100, 2),
            "sharpe_ratio": round(equal_sharpe, 4)
        }
        
        # Minimum variance portfolio
        try:
            inv_cov = np.linalg.inv(cov_matrix)
            ones = np.ones(len(returns_data))
            min_var_weights = inv_cov @ ones / (ones.T @ inv_cov @ ones)
            min_var_weights = min_var_weights / min_var_weights.sum()  # Normalize
            
            min_var_return = np.dot(min_var_weights, mean_returns)
            min_var_vol = np.sqrt(np.dot(min_var_weights.T, np.dot(cov_matrix, min_var_weights)))
            min_var_sharpe = (min_var_return - self.risk_free_rate) / min_var_vol if min_var_vol > 0 else 0
            
            optimization_results["minimum_variance"] = {
                "weights": {symbol: round(weight, 4) for symbol, weight in zip(returns_data.keys(), min_var_weights)},
                "expected_return": round(min_var_return * 100, 2),
                "volatility": round(min_var_vol * 100, 2),
                "sharpe_ratio": round(min_var_sharpe, 4)
            }
        except np.linalg.LinAlgError:
            optimization_results["minimum_variance"] = {"error": "Singular covariance matrix"}
            
        return optimization_results
        
    def _calculate_attribution(self, data: Dict[str, FinancialData]) -> Dict[str, Any]:
        """
        Calculate risk and performance attribution.
        
        Args:
            data: Dictionary mapping symbols to FinancialData objects
            
        Returns:
            Dictionary containing attribution analysis
        """
        # Prepare returns data
        returns_data = {}
        for symbol, financial_data in data.items():
            df = financial_data.data
            if not df.empty and 'close' in df.columns:
                returns = df['close'].pct_change().dropna()
                if len(returns) > 0:
                    returns_data[symbol] = returns
                    
        if len(returns_data) < 2:
            return {"error": "Insufficient data for attribution analysis"}
            
        # Align returns data
        returns_df = pd.DataFrame(returns_data).dropna()
        
        if len(returns_df) < 30:
            return {"error": "Insufficient aligned data for attribution analysis"}
            
        # Equal weight portfolio
        weights = np.ones(len(returns_data)) / len(returns_data)
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Individual contribution to portfolio return
        individual_returns = returns_df.mean() * 252  # Annualized
        portfolio_return = portfolio_returns.mean() * 252  # Annualized
        
        contribution = {}
        for symbol in returns_data.keys():
            contribution[symbol] = {
                "weight": round(weights[list(returns_data.keys()).index(symbol)], 4),
                "individual_return": round(individual_returns[symbol] * 100, 2),
                "contribution": round(individual_returns[symbol] * weights[list(returns_data.keys()).index(symbol)] * 100, 2)
            }
            
        # Risk contribution (simplified)
        cov_matrix = returns_df.cov() * 252
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        
        risk_contribution = {}
        for i, symbol in enumerate(returns_data.keys()):
            marginal_contribution = 2 * np.dot(cov_matrix.iloc[i], weights)
            risk_contribution[symbol] = {
                "marginal_contribution": round(marginal_contribution, 6),
                "risk_contribution": round(weights[i] * marginal_contribution / portfolio_variance, 4)
            }
            
        return {
            "return_attribution": contribution,
            "risk_attribution": risk_contribution,
            "portfolio_return": round(portfolio_return * 100, 2),
            "portfolio_variance": round(portfolio_variance, 6)
        }
        
    def _calculate_summary(self, portfolio_metrics: Dict[str, Any], optimization: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate summary statistics.
        
        Args:
            portfolio_metrics: Portfolio metrics
            optimization: Optimization results
            
        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            "portfolio_return": portfolio_metrics.get("annualized_return", 0),
            "portfolio_volatility": portfolio_metrics.get("volatility", 0),
            "portfolio_sharpe": portfolio_metrics.get("sharpe_ratio", 0),
            "max_drawdown": portfolio_metrics.get("max_drawdown", 0)
        }
        
        # Add optimization comparison
        if "equal_weight" in optimization:
            eq = optimization["equal_weight"]
            summary["equal_weight_return"] = eq.get("expected_return", 0)
            summary["equal_weight_volatility"] = eq.get("volatility", 0)
            summary["equal_weight_sharpe"] = eq.get("sharpe_ratio", 0)
            
        if "minimum_variance" in optimization and "error" not in optimization["minimum_variance"]:
            mv = optimization["minimum_variance"]
            summary["min_var_return"] = mv.get("expected_return", 0)
            summary["min_var_volatility"] = mv.get("volatility", 0)
            summary["min_var_sharpe"] = mv.get("sharpe_ratio", 0)
            
        return summary
        
    def validate_config(self) -> bool:
        """Validate analyzer configuration."""
        if self.risk_free_rate < 0 or self.risk_free_rate > 1:
            self.logger.error(f"Invalid risk_free_rate: {self.risk_free_rate}")
            return False
            
        valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
        if self.rebalance_frequency not in valid_frequencies:
            self.logger.error(f"Invalid rebalance_frequency: {self.rebalance_frequency}")
            return False
            
        return True
