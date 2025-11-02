# FinFetch

**Financial Data Collection, Aggregation and Processing Utilities**

FinFetch is a comprehensive Python package designed for collecting, aggregating, and processing financial data from various sources. It provides a unified interface for accessing multiple financial data APIs and processing the collected data for analysis and reporting.

## Features

- **Multi-Source Data Collection**: Support for various financial data sources including Yahoo Finance, Alpha Vantage, FRED, and more
- **Data Aggregation**: Intelligent aggregation of data from multiple sources with conflict resolution
- **Data Processing**: Advanced data processing capabilities including cleaning, normalization, and transformation
- **Async Support**: High-performance async data collection for large-scale operations
- **Extensible Architecture**: Plugin-based architecture for easy extension with new data sources
- **Comprehensive Logging**: Structured logging for monitoring and debugging
- **Data Validation**: Built-in data validation using Pydantic models

## Installation

### From Source

```bash
git clone https://github.com/4jeffclark/finfetch.git
cd finfetch
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/4jeffclark/finfetch.git
cd finfetch
pip install -e ".[dev,docs]"
```

## Quick Start

```python
from finfetch import FinFetch
from finfetch.sources import YahooFinance, AlphaVantage

# Initialize FinFetch
ff = FinFetch()

# Add data sources
ff.add_source(YahooFinance(api_key="your_yahoo_key"))
ff.add_source(AlphaVantage(api_key="your_alpha_vantage_key"))

# Collect data
data = ff.collect_data(
    symbols=["AAPL", "GOOGL", "MSFT"],
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Process and aggregate data
processed_data = ff.process_data(data)
```

## Project Structure

```
finfetch/
├── src/finfetch/           # Main package source code
│   ├── __init__.py
│   ├── cli.py             # Command-line interface
│   ├── core/              # Core functionality
│   ├── sources/           # Data source implementations
│   ├── processors/        # Data processing modules
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
├── test/dev/             # Development testing structure
│   ├── backlog/          # Future feature designs
│   └── current-session/  # Active development work
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Development

This project follows the development principles and patterns defined in the [FinFetch Constitution](.specify/memory/constitution.md). For detailed implementation patterns and workflow procedures, see the [Work Pattern Guide](.specify/memory/work-pattern.md).

**Key Development Principles:**
- **Structured Development Approach**: Design → User Approval → Implementation → Testing → Documentation
- **User-Driven Development**: User runs tests and provides results - never assume outcomes
- **Start with Working Code**: Always begin with existing, working code patterns
- **Self-Documenting Work**: All development work must be documented for future reference
- **Test-Driven Development**: Tests must be written and validated before considering features complete

For complete development workflow details, naming conventions, file organization patterns, and implementation procedures, refer to the [Work Pattern Guide](.specify/memory/work-pattern.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the development workflow patterns
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository or contact the development team.
