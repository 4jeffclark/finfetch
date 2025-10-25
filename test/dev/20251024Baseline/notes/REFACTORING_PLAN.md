# FinFetch Refactoring Plan

## 🎯 **Current State Analysis**

The current baseline has:
- ✅ **Good Foundation**: Core FinFetch class, data sources, processors
- ✅ **Basic CLI**: collect, process, validate commands
- ✅ **Stock Screening**: Specialized screen command
- ❌ **Inconsistent Structure**: Mixed use case approaches
- ❌ **Limited Integration**: No clear integration strategy
- ❌ **Configuration**: No unified configuration system

## 🔄 **Recommended Refactoring**

### **1. CLI Structure Refactoring**

#### **Current Structure:**
```
finfetch
├── collect <symbols> [options]
├── process <input> [options]  
├── validate <symbol> [options]
├── screen <symbols> [options]
├── sources
└── processors
```

#### **Proposed Structure:**
```
finfetch
├── collect <symbols> [options]     # Data collection
├── process <input> [options]       # Data processing
├── screen <symbols> [options]      # Stock screening
├── analyze <input> [options]        # Analysis & reporting
├── sources                          # Source management
├── processors                        # Processor management
├── config                           # Configuration management
└── help                             # Comprehensive help
```

### **2. Command Refactoring Details**

#### **`finfetch collect` - Enhanced Data Collection**
```bash
# Basic collection
finfetch collect -s AAPL GOOGL MSFT

# With specific sources
finfetch collect -s AAPL GOOGL MSFT --sources yahoo polygon

# With date range
finfetch collect -s AAPL GOOGL MSFT --start-date 2020-01-01 --end-date 2024-12-31

# With output format
finfetch collect -s AAPL GOOGL MSFT --output data.csv --format csv

# Real-time data
finfetch collect -s AAPL GOOGL MSFT --real-time --sources polygon
```

#### **`finfetch process` - Enhanced Data Processing**
```bash
# Basic processing
finfetch process -i data.json

# With specific processors
finfetch process -i data.json --processors clean indicators

# With configuration
finfetch process -i data.json --config processing.yaml

# Pipeline processing
finfetch process -i data.json --pipeline "clean->indicators->aggregate"
```

#### **`finfetch screen` - Enhanced Stock Screening**
```bash
# Basic screening
finfetch screen -s AAPL GOOGL MSFT

# With ranking
finfetch screen -s AAPL GOOGL MSFT --rank --top 10

# With custom criteria
finfetch screen -s AAPL GOOGL MSFT --criteria "sharpe>1.5,return>10"

# With output
finfetch screen -s AAPL GOOGL MSFT --output opportunities.csv --rank
```

#### **`finfetch analyze` - New Analysis Command**
```bash
# Performance analysis
finfetch analyze -i data.json --analysis performance

# Risk analysis
finfetch analyze -i data.json --analysis risk

# Portfolio analysis
finfetch analyze -i data.json --analysis portfolio

# Custom analysis
finfetch analyze -i data.json --analysis custom --config analysis.yaml
```

#### **`finfetch config` - New Configuration Command**
```bash
# Show current configuration
finfetch config show

# Set configuration
finfetch config set sources.polygon.api_key "your_key"

# Validate configuration
finfetch config validate

# Reset to defaults
finfetch config reset
```

### **3. Programming Library Interface**

#### **Enhanced Core Classes:**
```python
from finfetch import FinFetch, DataSource, Processor, Analysis

# Main orchestrator with configuration
ff = FinFetch(config_file="finfetch.yaml")

# Data sources with configuration
yahoo = YahooFinanceSource()
polygon = PolygonSource(api_key="...")

# Processors with configuration
cleaner = DataCleaner(config={"fill_method": "forward"})
indicators = TechnicalIndicatorsProcessor(config={"indicators": ["sma", "rsi"]})
screener = StockScreeningProcessor(config={"risk_free_rate": 0.03})

# Analysis with configuration
analyzer = PerformanceAnalyzer(config={"benchmark": "SPY"})
```

#### **Use Case Examples:**

##### **Retirement Portfolio:**
```python
# Long-term data collection
data = await ff.collect(
    symbols=["SPY", "BND", "GLD", "VTI", "VXUS"],
    start_date="2010-01-01",
    end_date="2024-12-31",
    sources=[yahoo, polygon]
)

# Process for portfolio optimization
processed = ff.process(
    data,
    processors=[cleaner, indicators],
    config={"risk_free_rate": 0.03}
)

# Analyze for retirement planning
analysis = ff.analyze(
    processed,
    analysis_type="portfolio_optimization",
    config={"benchmark": "SPY", "risk_free_rate": 0.03}
)
```

##### **Day Trading Screening:**
```python
# Real-time data collection
data = await ff.collect(
    symbols=["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"],
    sources=[polygon],
    real_time=True,
    config={"update_frequency": "1min"}
)

# Screen for momentum opportunities
opportunities = ff.screen(
    data,
    criteria="momentum",
    config={"indicators": ["rsi", "macd", "bollinger_bands"]}
)
```

##### **Algorithmic Trading:**
```python
# High-frequency data collection
data = await ff.collect(
    symbols=["SPY", "QQQ", "IWM"],
    sources=[polygon],
    real_time=True,
    config={"update_frequency": "1min", "history_days": 30}
)

# Process for signal generation
processed = ff.process(
    data,
    processors=[cleaner, indicators, screener],
    config={"signal_generation": True}
)

# Analyze for backtesting
analysis = ff.analyze(
    processed,
    analysis_type="backtesting",
    config={"strategy": "momentum", "lookback": 20}
)
```

### **4. Configuration System**

#### **Global Configuration File (`finfetch.yaml`):**
```yaml
# FinFetch Configuration
version: "1.0"

# Data Sources
sources:
  yahoo:
    enabled: true
    rate_limit: 2000
    timeout: 30
  
  polygon:
    enabled: true
    api_key: ${POLYGON_API_KEY}
    rate_limit: 5
    timeout: 30
  
  alpha_vantage:
    enabled: false
    api_key: ${ALPHA_VANTAGE_API_KEY}
    rate_limit: 5
    timeout: 30

# Processors
processors:
  data_cleaner:
    enabled: true
    fill_method: "forward"
    remove_outliers: true
    outlier_threshold: 3.0
  
  technical_indicators:
    enabled: true
    indicators: ["sma", "ema", "rsi", "macd", "bollinger_bands"]
    periods:
      sma: [20, 50, 200]
      ema: [12, 26]
      rsi: 14
  
  stock_screening:
    enabled: true
    risk_free_rate: 0.03
    lookback_years: 5
    week_52_lookback: 52
    min_data_points: 1000

# Output Configuration
output:
  default_format: "csv"
  date_format: "%Y-%m-%d"
  decimal_places: 2
  include_metadata: true

# Logging
logging:
  level: "INFO"
  format: "json"
  file: "finfetch.log"
```

### **5. Integration Strategy**

#### **Existing Libraries Integration:**
```python
# pandas integration
import pandas as pd
data = ff.collect(symbols=["AAPL"], sources=[yahoo])
df = data.to_dataframe()  # Convert to pandas DataFrame

# numpy integration
import numpy as np
returns = df['close'].pct_change()
volatility = np.std(returns) * np.sqrt(252)

# scikit-learn integration
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()
model.fit(features, targets)
```

#### **Database Integration:**
```python
# SQL integration
from finfetch.integrations import SQLIntegration
sql = SQLIntegration(connection_string="postgresql://...")
ff.add_integration(sql)

# Store data
ff.store(data, table="stock_data")

# Query data
historical = ff.query("SELECT * FROM stock_data WHERE symbol = 'AAPL'")
```

#### **Cloud Integration:**
```python
# AWS S3 integration
from finfetch.integrations import S3Integration
s3 = S3Integration(bucket="my-financial-data")
ff.add_integration(s3)

# Store data
ff.store(data, path="data/2024/01/")

# Load data
data = ff.load(path="data/2024/01/")
```

## 🚀 **Implementation Plan**

### **Phase 1: CLI Refactoring (Week 1)**
1. Refactor CLI structure
2. Add configuration management
3. Implement help system
4. Add new commands (analyze, config)

### **Phase 2: Library Interface (Week 2)**
1. Enhance core classes
2. Add configuration support
3. Implement use case examples
4. Add integration interfaces

### **Phase 3: Configuration System (Week 3)**
1. Implement YAML configuration
2. Add configuration management
3. Add environment variable support
4. Add configuration validation

### **Phase 4: Integration & Testing (Week 4)**
1. Add integration examples
2. Implement comprehensive testing
3. Add documentation
4. Performance optimization

## 📊 **Success Metrics**

### **1. Use Case Coverage**
- ✅ Retirement portfolio optimization
- ✅ Growth portfolio optimization  
- ✅ Day trading screening
- ✅ Algorithmic trading

### **2. Integration Coverage**
- ✅ pandas/numpy integration
- ✅ Database integration
- ✅ Cloud integration
- ✅ Visualization integration

### **3. Developer Experience**
- ✅ Easy to use CLI
- ✅ Clear documentation
- ✅ Good error messages
- ✅ Comprehensive help

### **4. Performance**
- ✅ Fast data collection
- ✅ Efficient processing
- ✅ Scalable architecture
- ✅ Memory efficient

This refactoring plan provides a coherent interface to existing financial data capabilities while remaining flexible and extensible for different use cases.
