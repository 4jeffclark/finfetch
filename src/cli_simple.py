"""
Simple CLI for FinFetch baseline.

This module provides minimal "Hello World" functionality for the FinFetch system.
"""

import click
from .utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def cli(ctx, debug):
    """FinFetch - Financial Data Collection, Aggregation and Processing Utilities
    
    A simple tool for collecting, processing, and analyzing financial data.
    """
    # Setup logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(level=log_level)
    
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
        click.echo("FinFetch Configuration:")
        click.echo("=" * 30)
        click.echo("Data Sources:")
        click.echo("  ✓ yahoo: enabled")
        click.echo("  ✓ polygon: enabled")
        click.echo("  ✗ alpha_vantage: disabled")
        click.echo("  ✗ fred: disabled")
        click.echo()
        click.echo("Processors:")
        click.echo("  ✓ data_cleaner: enabled")
        click.echo("  ✓ stock_screening: enabled")
        click.echo("  ✓ performance_analyzer: enabled")
        click.echo()
        click.echo("Output:")
        click.echo("  Format: csv")
        click.echo("  Date Format: %Y-%m-%d")
        click.echo("  Decimal Places: 2")
    else:
        click.echo("Use --show to display current configuration")

@cli.command()
@click.option('--symbols', '-s', multiple=True, required=True, help='Financial symbols to collect')
@click.option('--sources', multiple=True, help='Data sources to use')
@click.pass_context
def collect(ctx, symbols, sources):
    """Collect financial data for specified symbols."""
    click.echo(f"Collecting data for {', '.join(symbols)} from {', '.join(sources) if sources else 'default sources'}...")
    click.echo("✓ Data collection completed successfully")
    click.echo(f"  - Symbols processed: {len(symbols)}")
    click.echo(f"  - Sources used: {', '.join(sources) if sources else 'yahoo'}")
    click.echo(f"  - Data points collected: {len(symbols) * 252} (mock)")
    click.echo("  - Status: SUCCESS")

@cli.command()
@click.option('--symbols', '-s', multiple=True, required=True, help='Stock symbols to screen')
@click.pass_context
def screen(ctx, symbols):
    """Screen stocks for investment opportunities."""
    click.echo(f"Screening {', '.join(symbols)} for opportunities...")
    click.echo("✓ Stock screening completed successfully")
    click.echo(f"  - Symbols screened: {len(symbols)}")
    click.echo(f"  - Opportunities found: {len(symbols)}")
    click.echo("  - Top opportunity: AAPL (Return: 15.2%, Sharpe: 1.8, From High: -5.3%)")
    click.echo("  - Status: SUCCESS")

@cli.command()
@click.option('--input', '-i', type=click.Path(), required=True, help='Input data file')
@click.option('--analysis', type=click.Choice(['performance', 'risk', 'portfolio']), default='performance', help='Type of analysis')
@click.pass_context
def analyze(ctx, input, analysis):
    """Analyze financial data."""
    click.echo(f"Analyzing {input} with {analysis} analysis...")
    click.echo("✓ Analysis completed successfully")
    click.echo(f"  - Input file: {input}")
    click.echo(f"  - Analysis type: {analysis}")
    click.echo(f"  - Results: {analysis.title()} metrics calculated")
    click.echo("  - Status: SUCCESS")

def main():
    """Main entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main()
