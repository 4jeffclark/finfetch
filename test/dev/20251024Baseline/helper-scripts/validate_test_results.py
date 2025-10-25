#!/usr/bin/env python3
"""
Validate test results for Polygon integration test.

This script validates the test results to ensure they meet expected criteria.
"""

import json
import sys
from typing import Dict, Any, List

def validate_test_results(results_path: str) -> bool:
    """
    Validate test results.
    
    Args:
        results_path: Path to test results file
        
    Returns:
        True if validation passes, False otherwise
    """
    print("Validating test results...")
    
    # Load results
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    validation_errors = []
    
    # Check basic structure
    required_keys = ['test_info', 'configuration', 'results', 'metrics_summary', 'data_quality']
    for key in required_keys:
        if key not in results:
            validation_errors.append(f"Missing required key: {key}")
    
    # Check test info
    if 'test_info' in results:
        test_info = results['test_info']
        if test_info.get('status') != 'completed':
            validation_errors.append("Test status is not 'completed'")
    
    # Check results
    if 'results' in results:
        results_data = results['results']
        if results_data.get('symbols_processed', 0) == 0:
            validation_errors.append("No symbols were processed")
        
        if not results_data.get('success', False):
            validation_errors.append("Test was not successful")
    
    # Check data quality
    if 'data_quality' in results:
        data_quality = results['data_quality']
        if data_quality.get('symbols_with_data', 0) == 0:
            validation_errors.append("No symbols have data")
        
        if data_quality.get('total_data_points', 0) == 0:
            validation_errors.append("No data points collected")
    
    # Check metrics summary
    if 'metrics_summary' in results:
        metrics_summary = results['metrics_summary']
        if not isinstance(metrics_summary, list):
            validation_errors.append("Metrics summary should be a list")
        else:
            # Check if we have any metrics
            if len(metrics_summary) == 0:
                validation_errors.append("No metrics calculated")
            else:
                # Check first metric entry
                first_metric = metrics_summary[0]
                expected_keys = ['Ticker', 'Ann_Total_Return_%', 'Sharpe_Ratio', '%_from_52w_High']
                for key in expected_keys:
                    if key not in first_metric:
                        validation_errors.append(f"Missing expected metric key: {key}")
    
    # Report validation results
    if validation_errors:
        print("Validation FAILED:")
        for error in validation_errors:
            print(f"  - {error}")
        return False
    else:
        print("Validation PASSED: All checks completed successfully")
        return True

def print_validation_summary(results_path: str) -> None:
    """Print a summary of the validation results."""
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    
    # Test info
    if 'test_info' in results:
        test_info = results['test_info']
        print(f"Test Name: {test_info.get('name', 'Unknown')}")
        print(f"Status: {test_info.get('status', 'Unknown')}")
        print(f"Timestamp: {test_info.get('timestamp', 'Unknown')}")
    
    # Results
    if 'results' in results:
        results_data = results['results']
        print(f"\nResults:")
        print(f"  Symbols Processed: {results_data.get('symbols_processed', 0)}")
        print(f"  Processing Time: {results_data.get('processing_time', 0):.2f}s")
        print(f"  Success: {results_data.get('success', False)}")
        if results_data.get('errors'):
            print(f"  Errors: {len(results_data['errors'])}")
    
    # Data quality
    if 'data_quality' in results:
        data_quality = results['data_quality']
        print(f"\nData Quality:")
        print(f"  Symbols with Data: {data_quality.get('symbols_with_data', 0)}")
        print(f"  Total Data Points: {data_quality.get('total_data_points', 0)}")
        print(f"  Average Data Points: {data_quality.get('average_data_points', 0):.1f}")
    
    # Metrics summary
    if 'metrics_summary' in results and results['metrics_summary']:
        metrics_summary = results['metrics_summary']
        print(f"\nMetrics Summary:")
        print(f"  Total Metrics: {len(metrics_summary)}")
        
        # Show sample metrics
        if len(metrics_summary) > 0:
            sample = metrics_summary[0]
            print(f"  Sample Metrics for {sample.get('Ticker', 'Unknown')}:")
            print(f"    Annual Return: {sample.get('Ann_Total_Return_%', 'N/A')}%")
            print(f"    Sharpe Ratio: {sample.get('Sharpe_Ratio', 'N/A')}")
            print(f"    From 52w High: {sample.get('%_from_52w_High', 'N/A')}%")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_test_results.py <results_path>")
        sys.exit(1)
    
    results_path = sys.argv[1]
    
    try:
        success = validate_test_results(results_path)
        print_validation_summary(results_path)
        
        if success:
            print("\nValidation completed successfully!")
            sys.exit(0)
        else:
            print("\nValidation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Validation error: {e}")
        sys.exit(1)
