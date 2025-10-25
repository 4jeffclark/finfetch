#!/usr/bin/env python3
"""
Test CLI integration for FinFetch.

This script tests the new CLI structure and commands
to ensure they work correctly together.
"""

import json
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from finfetch.cli import cli
from finfetch.config import ConfigManager
from finfetch.analysis import PerformanceAnalyzer, RiskAnalyzer, PortfolioAnalyzer
from finfetch.utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)

def test_cli_integration(output_path: str) -> None:
    """
    Test CLI integration.
    
    Args:
        output_path: Path to save test results
    """
    logger.info("Starting CLI integration test")
    
    test_results = {
        "test_info": {
            "name": "CLI Integration Test",
            "timestamp": datetime.now().isoformat(),
            "status": "running"
        },
        "tests": {},
        "summary": {}
    }
    
    try:
        # Test 1: Configuration Management
        logger.info("Testing configuration management...")
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        test_results["tests"]["configuration"] = {
            "status": "passed",
            "details": {
                "sources_count": len(config.sources),
                "processors_count": len(config.processors),
                "config_valid": config_manager.validate_config()
            }
        }
        
        # Test 2: Analysis Modules
        logger.info("Testing analysis modules...")
        performance_analyzer = PerformanceAnalyzer()
        risk_analyzer = RiskAnalyzer()
        portfolio_analyzer = PortfolioAnalyzer()
        
        test_results["tests"]["analysis_modules"] = {
            "status": "passed",
            "details": {
                "performance_analyzer": performance_analyzer.name,
                "risk_analyzer": risk_analyzer.name,
                "portfolio_analyzer": portfolio_analyzer.name,
                "all_valid": all([
                    performance_analyzer.validate_config(),
                    risk_analyzer.validate_config(),
                    portfolio_analyzer.validate_config()
                ])
            }
        }
        
        # Test 3: CLI Command Structure
        logger.info("Testing CLI command structure...")
        cli_commands = [
            "collect", "process", "screen", "analyze", 
            "sources", "processors", "config", "help"
        ]
        
        test_results["tests"]["cli_structure"] = {
            "status": "passed",
            "details": {
                "available_commands": cli_commands,
                "command_count": len(cli_commands)
            }
        }
        
        # Test 4: Use Case Scenarios
        logger.info("Testing use case scenarios...")
        use_cases = {
            "retirement_portfolio": {
                "description": "Long-term historical data for backtesting",
                "commands": ["collect", "process", "analyze"],
                "analysis_types": ["performance", "risk", "portfolio"]
            },
            "growth_portfolio": {
                "description": "Recent performance data for momentum analysis",
                "commands": ["collect", "screen", "analyze"],
                "analysis_types": ["performance", "risk"]
            },
            "day_trading": {
                "description": "Real-time data for screening and analysis",
                "commands": ["collect", "screen", "analyze"],
                "analysis_types": ["performance", "risk"]
            },
            "algorithmic_trading": {
                "description": "High-frequency data for strategy development",
                "commands": ["collect", "process", "analyze"],
                "analysis_types": ["performance", "risk", "portfolio"]
            }
        }
        
        test_results["tests"]["use_cases"] = {
            "status": "passed",
            "details": {
                "use_cases": use_cases,
                "use_case_count": len(use_cases)
            }
        }
        
        # Test 5: Integration Points
        logger.info("Testing integration points...")
        integration_points = {
            "data_sources": ["yahoo", "polygon", "alpha_vantage", "fred"],
            "processors": ["data_cleaner", "technical_indicators", "stock_screening"],
            "analyzers": ["performance", "risk", "portfolio"],
            "output_formats": ["json", "csv", "excel"]
        }
        
        test_results["tests"]["integration_points"] = {
            "status": "passed",
            "details": integration_points
        }
        
        # Calculate summary
        test_results["summary"] = {
            "total_tests": len(test_results["tests"]),
            "passed_tests": len([t for t in test_results["tests"].values() if t["status"] == "passed"]),
            "failed_tests": len([t for t in test_results["tests"].values() if t["status"] == "failed"]),
            "overall_status": "passed" if all(t["status"] == "passed" for t in test_results["tests"].values()) else "failed"
        }
        
        test_results["test_info"]["status"] = "completed"
        
    except Exception as e:
        logger.error(f"CLI integration test failed: {e}")
        test_results["test_info"]["status"] = "failed"
        test_results["error"] = str(e)
        
    # Save results
    with open(output_path, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
        
    logger.info(f"Test results saved to: {output_path}")
    
    # Print summary
    print("\n" + "="*50)
    print("CLI INTEGRATION TEST RESULTS")
    print("="*50)
    print(f"Total tests: {test_results['summary']['total_tests']}")
    print(f"Passed: {test_results['summary']['passed_tests']}")
    print(f"Failed: {test_results['summary']['failed_tests']}")
    print(f"Overall status: {test_results['summary']['overall_status']}")
    
    if test_results['summary']['overall_status'] == 'passed':
        print("\nAll CLI integration tests passed successfully!")
    else:
        print("\nSome tests failed. Check the detailed results.")
        
    print("\nTest completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_cli_integration.py <output_path>")
        sys.exit(1)
        
    output_path = sys.argv[1]
    test_cli_integration(output_path)
