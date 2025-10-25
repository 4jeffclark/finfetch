#!/usr/bin/env python3
"""
Create test configuration for Polygon integration test.

This script creates a test configuration file for the Polygon integration test,
including sample symbols and test parameters.
"""

import json
import sys
from datetime import datetime, timedelta

def create_test_config(output_path: str) -> None:
    """
    Create test configuration file.
    
    Args:
        output_path: Path to save the configuration file
    """
    # Calculate date range (last 5 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    
    config = {
        "test_info": {
            "name": "Polygon Integration Test",
            "description": "Test Polygon.io data source and financial metrics processor",
            "created": datetime.now().isoformat(),
            "version": "1.0"
        },
        "test_symbols": [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "NVDA", "META", "NFLX", "AMD", "INTC"
        ],
        "date_range": {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        },
        "polygon_config": {
            "api_key": "YOUR_POLYGON_API_KEY",  # Replace with actual key
            "rate_limit": 5,
            "timeout": 30
        },
        "metrics_config": {
            "risk_free_rate": 0.03,
            "lookback_years": 5,
            "week_52_lookback": 52,
            "min_data_points": 1000
        },
        "test_parameters": {
            "max_symbols": 10,
            "expected_metrics": [
                "ann_total_return_pct",
                "sharpe_ratio", 
                "pct_from_52w_high",
                "volatility",
                "max_drawdown"
            ]
        }
    }
    
    # Save configuration
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Test configuration created: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_test_config.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    create_test_config(output_path)
    print("Configuration creation completed successfully!")
