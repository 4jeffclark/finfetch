"""
Data validation utilities for FinFetch.

This module provides utilities for validating financial data quality
and ensuring data integrity.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

from ..core.data_models import FinancialData, DataQualityReport


def validate_financial_data(data: FinancialData) -> DataQualityReport:
    """
    Validate financial data and generate a quality report.
    
    Args:
        data: FinancialData object to validate
        
    Returns:
        DataQualityReport with validation results
    """
    if data.data.empty:
        return DataQualityReport(
            symbol=data.symbol,
            total_records=0,
            quality_score=0.0,
            issues=["No data available"]
        )
    
    # Basic statistics
    total_records = len(data.data)
    missing_values = data.data.isnull().sum().to_dict()
    
    # Data range statistics
    numeric_columns = data.data.select_dtypes(include=[np.number]).columns
    data_range = {}
    for col in numeric_columns:
        if col in data.data.columns:
            col_data = data.data[col].dropna()
            if not col_data.empty:
                data_range[col] = {
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "mean": float(col_data.mean()),
                    "std": float(col_data.std())
                }
    
    # Identify issues
    issues = []
    
    # Check for missing values
    high_missing_threshold = 0.1  # 10% missing values
    for col, missing_count in missing_values.items():
        if missing_count > 0:
            missing_percentage = missing_count / total_records
            if missing_percentage > high_missing_threshold:
                issues.append(f"High missing values in {col}: {missing_percentage:.1%}")
            elif missing_count > 0:
                issues.append(f"Missing values in {col}: {missing_count}")
    
    # Check for duplicate dates
    if 'date' in data.data.columns:
        duplicate_dates = data.data['date'].duplicated().sum()
        if duplicate_dates > 0:
            issues.append(f"Duplicate dates found: {duplicate_dates}")
    
    # Check for negative prices (if applicable)
    price_columns = ['open', 'high', 'low', 'close']
    for col in price_columns:
        if col in data.data.columns:
            negative_prices = (data.data[col] < 0).sum()
            if negative_prices > 0:
                issues.append(f"Negative prices found in {col}: {negative_prices}")
    
    # Check for unrealistic price movements
    if 'close' in data.data.columns and len(data.data) > 1:
        price_changes = data.data['close'].pct_change().dropna()
        extreme_changes = (abs(price_changes) > 0.5).sum()  # 50% change
        if extreme_changes > 0:
            issues.append(f"Extreme price changes detected: {extreme_changes}")
    
    # Create quality report
    report = DataQualityReport(
        symbol=data.symbol,
        total_records=total_records,
        missing_values=missing_values,
        data_range=data_range,
        issues=issues
    )
    
    # Calculate quality score
    report.quality_score = report.calculate_quality_score()
    
    return report


class DataQualityChecker:
    """
    Advanced data quality checker for financial data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data quality checker.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.quality_thresholds = self.config.get('quality_thresholds', {
            'max_missing_percentage': 0.1,
            'max_price_change': 0.5,
            'min_records': 10
        })
    
    def check_data_quality(self, data: FinancialData) -> DataQualityReport:
        """
        Perform comprehensive data quality checks.
        
        Args:
            data: FinancialData object to check
            
        Returns:
            DataQualityReport with detailed quality assessment
        """
        report = validate_financial_data(data)
        
        # Additional quality checks
        self._check_data_consistency(data, report)
        self._check_temporal_consistency(data, report)
        self._check_price_consistency(data, report)
        
        return report
    
    def _check_data_consistency(self, data: FinancialData, report: DataQualityReport) -> None:
        """Check data consistency."""
        if data.data.empty:
            return
            
        # Check for required columns
        required_columns = ['date']
        missing_columns = [col for col in required_columns if col not in data.data.columns]
        if missing_columns:
            report.issues.append(f"Missing required columns: {missing_columns}")
    
    def _check_temporal_consistency(self, data: FinancialData, report: DataQualityReport) -> None:
        """Check temporal consistency of data."""
        if 'date' not in data.data.columns or data.data.empty:
            return
            
        # Check for date ordering
        dates = pd.to_datetime(data.data['date'])
        if not dates.is_monotonic_increasing:
            report.issues.append("Dates are not in chronological order")
        
        # Check for gaps in data
        if len(dates) > 1:
            date_diffs = dates.diff().dropna()
            expected_freq = date_diffs.mode().iloc[0] if not date_diffs.empty else None
            
            if expected_freq is not None:
                large_gaps = (date_diffs > expected_freq * 2).sum()
                if large_gaps > 0:
                    report.issues.append(f"Large gaps in data detected: {large_gaps}")
    
    def _check_price_consistency(self, data: FinancialData, report: DataQualityReport) -> None:
        """Check price data consistency."""
        price_columns = ['open', 'high', 'low', 'close']
        available_price_columns = [col for col in price_columns if col in data.data.columns]
        
        if not available_price_columns:
            return
            
        # Check OHLC consistency
        if all(col in data.data.columns for col in ['open', 'high', 'low', 'close']):
            ohlc_data = data.data[['open', 'high', 'low', 'close']].dropna()
            
            # High should be >= max(open, close)
            high_violations = (ohlc_data['high'] < ohlc_data[['open', 'close']].max(axis=1)).sum()
            if high_violations > 0:
                report.issues.append(f"High price violations: {high_violations}")
            
            # Low should be <= min(open, close)
            low_violations = (ohlc_data['low'] > ohlc_data[['open', 'close']].min(axis=1)).sum()
            if low_violations > 0:
                report.issues.append(f"Low price violations: {low_violations}")
    
    def get_quality_summary(self, reports: List[DataQualityReport]) -> Dict[str, Any]:
        """
        Get a summary of quality reports for multiple datasets.
        
        Args:
            reports: List of DataQualityReport objects
            
        Returns:
            Summary dictionary
        """
        if not reports:
            return {"total_symbols": 0, "average_quality": 0.0}
        
        total_symbols = len(reports)
        average_quality = sum(r.quality_score for r in reports) / total_symbols
        
        # Count issues by type
        issue_counts = {}
        for report in reports:
            for issue in report.issues:
                issue_type = issue.split(':')[0] if ':' in issue else issue
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        return {
            "total_symbols": total_symbols,
            "average_quality": average_quality,
            "issue_counts": issue_counts,
            "high_quality_symbols": sum(1 for r in reports if r.quality_score > 0.8),
            "low_quality_symbols": sum(1 for r in reports if r.quality_score < 0.5)
        }
