#!/usr/bin/env python3
"""
Generate test report for Polygon integration test.

This script generates a comprehensive test report in Markdown format.
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List

def generate_test_report(results_path: str, output_path: str) -> None:
    """
    Generate test report.
    
    Args:
        results_path: Path to test results file
        output_path: Path to save the report
    """
    # Load results
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Generate report
    report_lines = []
    
    # Header
    report_lines.extend([
        "# Polygon Integration Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Test Overview",
        ""
    ])
    
    # Test info
    if 'test_info' in results:
        test_info = results['test_info']
        report_lines.extend([
            f"- **Test Name:** {test_info.get('name', 'Unknown')}",
            f"- **Status:** {test_info.get('status', 'Unknown')}",
            f"- **Timestamp:** {test_info.get('timestamp', 'Unknown')}",
            ""
        ])
    
    # Configuration
    if 'configuration' in results:
        config = results['configuration']
        report_lines.extend([
            "## Test Configuration",
            "",
            f"- **Symbols Tested:** {len(config.get('test_symbols', []))}",
            f"- **Date Range:** {config.get('date_range', {}).get('start_date', 'Unknown')} to {config.get('date_range', {}).get('end_date', 'Unknown')}",
            f"- **Max Symbols:** {config.get('test_parameters', {}).get('max_symbols', 'Unknown')}",
            ""
        ])
    
    # Results
    if 'results' in results:
        results_data = results['results']
        report_lines.extend([
            "## Test Results",
            "",
            f"- **Symbols Processed:** {results_data.get('symbols_processed', 0)}",
            f"- **Processing Time:** {results_data.get('processing_time', 0):.2f} seconds",
            f"- **Success:** {results_data.get('success', False)}",
            ""
        ])
        
        if results_data.get('errors'):
            report_lines.extend([
                "### Errors",
                ""
            ])
            for error in results_data['errors']:
                report_lines.append(f"- {error}")
            report_lines.append("")
    
    # Data quality
    if 'data_quality' in results:
        data_quality = results['data_quality']
        report_lines.extend([
            "## Data Quality",
            "",
            f"- **Symbols with Data:** {data_quality.get('symbols_with_data', 0)}",
            f"- **Total Data Points:** {data_quality.get('total_data_points', 0)}",
            f"- **Average Data Points per Symbol:** {data_quality.get('average_data_points', 0):.1f}",
            ""
        ])
    
    # Metrics summary
    if 'metrics_summary' in results and results['metrics_summary']:
        metrics_summary = results['metrics_summary']
        report_lines.extend([
            "## Financial Metrics Summary",
            "",
            "| Ticker | Annual Return (%) | Sharpe Ratio | From 52w High (%) | Volatility | Max Drawdown (%) |",
            "|--------|-------------------|--------------|-------------------|------------|------------------|"
        ])
        
        for metric in metrics_summary:
            ticker = metric.get('Ticker', 'Unknown')
            ann_return = metric.get('Ann_Total_Return_%', 'N/A')
            sharpe = metric.get('Sharpe_Ratio', 'N/A')
            from_high = metric.get('%_from_52w_High', 'N/A')
            volatility = metric.get('Volatility', 'N/A')
            max_dd = metric.get('Max_Drawdown', 'N/A')
            
            report_lines.append(f"| {ticker} | {ann_return} | {sharpe} | {from_high} | {volatility} | {max_dd} |")
        
        report_lines.append("")
    
    # Analysis
    report_lines.extend([
        "## Analysis",
        ""
    ])
    
    # Calculate some basic statistics
    if 'metrics_summary' in results and results['metrics_summary']:
        metrics = results['metrics_summary']
        
        # Filter out N/A values for calculations
        returns = [m.get('Ann_Total_Return_%') for m in metrics if isinstance(m.get('Ann_Total_Return_%'), (int, float))]
        sharpe_ratios = [m.get('Sharpe_Ratio') for m in metrics if isinstance(m.get('Sharpe_Ratio'), (int, float))]
        
        if returns:
            avg_return = sum(returns) / len(returns)
            max_return = max(returns)
            min_return = min(returns)
            
            report_lines.extend([
                f"- **Average Annual Return:** {avg_return:.2f}%",
                f"- **Best Performer:** {max_return:.2f}%",
                f"- **Worst Performer:** {min_return:.2f}%",
                ""
            ])
        
        if sharpe_ratios:
            avg_sharpe = sum(sharpe_ratios) / len(sharpe_ratios)
            max_sharpe = max(sharpe_ratios)
            
            report_lines.extend([
                f"- **Average Sharpe Ratio:** {avg_sharpe:.2f}",
                f"- **Best Risk-Adjusted Return:** {max_sharpe:.2f}",
                ""
            ])
    
    # Conclusion
    report_lines.extend([
        "## Conclusion",
        ""
    ])
    
    if results.get('results', {}).get('success', False):
        report_lines.extend([
            "✅ **Test Status: PASSED**",
            "",
            "The Polygon integration test completed successfully. All components are working correctly:",
            "- Polygon.io data source integration",
            "- Financial metrics calculation",
            "- Data processing pipeline",
            "- Results validation"
        ])
    else:
        report_lines.extend([
            "❌ **Test Status: FAILED**",
            "",
            "The Polygon integration test encountered issues. Please review the errors above."
        ])
    
    report_lines.extend([
        "",
        "---",
        f"*Report generated by FinFetch Test Suite on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Test report generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_test_report.py <results_path> <output_path>")
        sys.exit(1)
    
    results_path = sys.argv[1]
    output_path = sys.argv[2]
    
    try:
        generate_test_report(results_path, output_path)
        print("Test report generation completed successfully!")
    except Exception as e:
        print(f"Test report generation failed: {e}")
        sys.exit(1)
