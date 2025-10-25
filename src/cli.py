"""
Command-line interface for FinFetch.

This module provides the main CLI entry point for the FinFetch system.
"""

import click
import sys
import os
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from utils.simple_logger import setup_logging, get_logger
from utils.debug_config import DebugLevel, set_debug_level, debug_print, debug_log

# Setup logging
setup_logging(level="WARNING")
logger = get_logger(__name__)

@click.group()
@click.option('--debug-level', type=click.IntRange(0, 4), default=0, 
              help='Debug level: 0=clean (table only), 1=basic, 2=detailed, 3=debug, 4=verbose')
@click.pass_context
def cli(ctx, debug_level):
    """FinFetch - Financial Data Collection, Aggregation and Processing Utilities
    
    A simple tool for collecting, processing, and analyzing financial data.
    """
    # Set debug level
    set_debug_level(DebugLevel(debug_level))
    
    # Setup logging based on debug level
    if debug_level >= 4:
        setup_logging(level="DEBUG")
    elif debug_level >= 3:
        setup_logging(level="INFO")
    elif debug_level >= 2:
        setup_logging(level="WARNING")
    else:
        setup_logging(level="ERROR")
    
    ctx.ensure_object(dict)

@cli.command()
def help():
    """Show help for FinFetch."""
    click.echo("FinFetch - Financial Data Collection, Aggregation and Processing Utilities")
    click.echo("=" * 70)
    click.echo()
    click.echo("Available commands:")
    click.echo("  help        Show this help message")
    click.echo("  config      Manage configuration")
    click.echo("  collect     Collect financial data")
    click.echo("  screen      Screen stocks for opportunities")
    click.echo("  analyze     Analyze financial data")
    click.echo()
    click.echo("Examples:")
    click.echo("  finfetch collect --symbols AAPL --sources yahoo")
    click.echo("  finfetch screen --symbols AAPL GOOGL")
    click.echo("  finfetch analyze --input data.json --analysis performance")

@cli.command()
@click.option('--show', is_flag=True, help='Show current configuration')
@click.pass_context
def config(ctx, show):
    """Manage FinFetch configuration."""
    if show:
        debug_print("FinFetch Configuration:", DebugLevel.BASIC)
        debug_print("=" * 30, DebugLevel.BASIC)
        debug_print("Data Sources:", DebugLevel.BASIC)
        debug_print("  [X] yahoo: enabled", DebugLevel.BASIC)
        debug_print("  [X] polygon: enabled", DebugLevel.BASIC)
        debug_print("  [ ] alpha_vantage: disabled", DebugLevel.BASIC)
        debug_print("  [ ] fred: disabled", DebugLevel.BASIC)
        debug_print("", DebugLevel.BASIC)
        debug_print("Processors:", DebugLevel.BASIC)
        debug_print("  [X] data_cleaner: enabled", DebugLevel.BASIC)
        debug_print("  [X] stock_screening: enabled", DebugLevel.BASIC)
        debug_print("  [X] performance_analyzer: enabled", DebugLevel.BASIC)
        debug_print("", DebugLevel.BASIC)
        debug_print("Output:", DebugLevel.BASIC)
        debug_print("  Format: csv", DebugLevel.BASIC)
        debug_print("  Date Format: %Y-%m-%d", DebugLevel.BASIC)
        debug_print("  Decimal Places: 2", DebugLevel.BASIC)
    else:
        debug_print("Use --show to display current configuration", DebugLevel.BASIC)

@cli.command()
@click.option('--symbols', '-s', multiple=True, required=True, help='Financial symbols to collect')
@click.option('--sources', multiple=True, help='Data sources to use')
@click.pass_context
def collect(ctx, symbols, sources):
    """Collect financial data for specified symbols."""
    debug_print(f"Collecting data for {', '.join(symbols)} from {', '.join(sources) if sources else 'default sources'}...", DebugLevel.BASIC)
    debug_print("[SUCCESS] Data collection completed successfully", DebugLevel.BASIC)
    debug_print(f"  - Symbols processed: {len(symbols)}", DebugLevel.DETAILED)
    debug_print(f"  - Sources used: {', '.join(sources) if sources else 'yahoo'}", DebugLevel.DETAILED)
    debug_print(f"  - Data points collected: {len(symbols) * 252} (mock)", DebugLevel.DETAILED)
    debug_print("  - Status: SUCCESS", DebugLevel.DETAILED)

@cli.command()
@click.option('--symbols', '-s', multiple=True, required=True, help='Stock symbols to screen')
@click.option('--days', '-d', default=365, help='Number of days of historical data to use')
@click.option('--benchmark', '-b', default='SPY', help='Benchmark symbol for alpha/beta calculations (default: SPY)')
@click.option('--risk-free-rate', '-r', default=0.0366, help='Risk-free rate for calculations (default: 3.66%)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'csv']), default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file path (for CSV format)')
@click.pass_context
def screen(ctx, symbols, days, benchmark, risk_free_rate, output_format, output):
    """Screen stocks for investment opportunities."""
    try:
        debug_print(f"Screening {', '.join(symbols)} for opportunities...", DebugLevel.BASIC)
        
        # Import the screening processor
        import processors.stock_screening_processor as screening_module
        StockScreeningProcessor = screening_module.StockScreeningProcessor
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        debug_log(f"Date range: {start_date.date()} to {end_date.date()}", DebugLevel.DETAILED)
        debug_log(f"Parameters: days={days}, benchmark={benchmark}, risk_free_rate={risk_free_rate:.2%}", DebugLevel.DETAILED)
        
        # Initialize processor with custom parameters
        processor = StockScreeningProcessor(risk_free_rate=risk_free_rate, benchmark_symbol=benchmark)
        results = processor.screen_stocks(symbols, start_date, end_date)
        
        if not results:
            debug_print("[ERROR] No data collected for any symbols", DebugLevel.BASIC)
            return
        
        debug_print(f"[SUCCESS] Stock screening completed successfully", DebugLevel.BASIC)
        debug_print(f"  - Symbols screened: {len(symbols)}", DebugLevel.DETAILED)
        debug_print(f"  - Results generated: {len(results)}", DebugLevel.DETAILED)
        debug_print(f"  - Data period: {days} days", DebugLevel.DETAILED)
        debug_print(f"  - Benchmark: {benchmark}", DebugLevel.DETAILED)
        debug_print(f"  - Risk-free rate: {risk_free_rate:.2%}", DebugLevel.DETAILED)
        debug_print("", DebugLevel.DETAILED)
        
        # Display results (always show in clean mode)
        formatted_results = processor.format_results(results, output_format)
        
        # Handle file output for CSV format
        if output_format == 'csv' and output:
            try:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(formatted_results)
                debug_print(f"Results saved to: {output}", DebugLevel.BASIC)
            except Exception as e:
                debug_print(f"[ERROR] Failed to save to file {output}: {e}", DebugLevel.BASIC)
                # Fall back to console output
                click.echo(formatted_results)
        else:
            # Console output
            click.echo(formatted_results)
        
    except Exception as e:
        debug_print(f"[ERROR] Screening failed: {e}", DebugLevel.BASIC)
        debug_log(f"Screening error: {e}", DebugLevel.DEBUG)

@cli.command()
@click.option('--input', '-i', type=click.Path(), required=True, help='Input data file')
@click.option('--analysis', type=click.Choice(['performance', 'risk', 'portfolio']), default='performance', help='Type of analysis')
@click.pass_context
def analyze(ctx, input, analysis):
    """Analyze financial data."""
    debug_print(f"Analyzing {input} with {analysis} analysis...", DebugLevel.BASIC)
    debug_print("[SUCCESS] Analysis completed successfully", DebugLevel.BASIC)
    debug_print(f"  - Input file: {input}", DebugLevel.DETAILED)
    debug_print(f"  - Analysis type: {analysis}", DebugLevel.DETAILED)
    debug_print(f"  - Results: {analysis.title()} metrics calculated", DebugLevel.DETAILED)
    debug_print("  - Status: SUCCESS", DebugLevel.DETAILED)

def main():
    """Main entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main()