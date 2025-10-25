@echo off
REM FinFetch Real Screening Test Runner
REM Comprehensive test of stock screening with different benchmarks and time windows

echo ========================================
echo FinFetch Real Screening Test Runner
echo ========================================
echo.

REM Set up environment
set SESSION_DIR=%~dp0
set OUTPUT_DIR=%SESSION_DIR%outputs\00-finfetch-baseline-test

REM Create directories
mkdir "%OUTPUT_DIR%" 2>nul

echo Test environment setup: PASSED
echo.

REM Test 1 - Basic screening with enhanced metrics (table format)
echo python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY
python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY
if errorlevel 1 (
    echo ERROR: Test 1 failed
    goto :error_exit
)
echo.

REM Test 2 - Tech stocks vs QQQ benchmark with different time window
echo python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --symbols MSFT --days 180 --benchmark QQQ
python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --symbols MSFT --days 180 --benchmark QQQ
if errorlevel 1 (
    echo ERROR: Test 2 failed
    goto :error_exit
)
echo.

REM Test 3 - Short-term analysis with custom risk-free rate
echo python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --days 90 --benchmark VTI --risk-free-rate 0.04
python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --days 90 --benchmark VTI --risk-free-rate 0.04
if errorlevel 1 (
    echo ERROR: Test 3 failed
    goto :error_exit
)
echo.

REM Test 4 - Long-term analysis with multiple stocks
echo python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --symbols MSFT --symbols TSLA --days 730 --benchmark SPY --risk-free-rate 0.035
python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --symbols MSFT --symbols TSLA --days 730 --benchmark SPY --risk-free-rate 0.035
if errorlevel 1 (
    echo ERROR: Test 4 failed
    goto :error_exit
)
echo.

REM Test 5 - CSV file output with comprehensive metrics
echo python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY --format csv --output screening_results.csv
python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY --format csv --output screening_results.csv
if errorlevel 1 (
    echo ERROR: Test 5 failed
    goto :error_exit
)
echo.

REM Test 6 - CSV output to different file with different parameters
echo python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols MSFT --symbols TSLA --days 180 --benchmark QQQ --format csv --output tech_analysis.csv
python ../../../src/finfetch.py --debug-level 0 screen --symbols AAPL --symbols MSFT --symbols TSLA --days 180 --benchmark QQQ --format csv --output tech_analysis.csv
if errorlevel 1 (
    echo ERROR: Test 6 failed
    goto :error_exit
)
echo.

REM Commented out mock tests - focusing on real screening functionality
REM Test 1: Help Command
REM echo Testing help command...
REM python ../../../src/finfetch.py help
REM if errorlevel 1 (
REM     echo ERROR: Help command test failed
REM     goto :error_exit
REM )
REM echo Help command test: PASSED
REM echo.

REM Test 2: Configuration Command
REM echo Testing configuration command...
REM python ../../../src/finfetch.py config --show
REM if errorlevel 1 (
REM     echo ERROR: Configuration command test failed
REM     goto :error_exit
REM )
REM echo Configuration command test: PASSED
REM echo.

REM Test 3: Data Collection Command
REM echo Testing data collection command...
REM python ../../../src/finfetch.py collect --symbols AAPL --sources yahoo
REM if errorlevel 1 (
REM     echo ERROR: Data collection command test failed
REM     goto :error_exit
REM )
REM echo Data collection command test: PASSED
REM echo.

REM Test 5: Analysis Command
REM echo Testing analysis command...
REM python ../../../src/finfetch.py analyze --input data.json --analysis performance
REM if errorlevel 1 (
REM     echo ERROR: Analysis command test failed
REM     goto :error_exit
REM )
REM echo Analysis command test: PASSED
REM echo.


echo ========================================
echo FinFetch Enhanced Screening Test: COMPLETED
echo ========================================
echo.
echo All screening tests completed successfully!
echo.
echo FinFetch enhanced capabilities demonstrated:
echo - Enhanced metrics with comprehensive financial data
echo - Multiple benchmark comparisons (SPY, QQQ, VTI)
echo - Flexible time windows (90 days to 2 years)
echo - Custom risk-free rates and parameters
echo - CSV file export with standardized metrics
echo - Clean output with debug level control
echo.
echo Example commands:
echo - finfetch screen --symbols AAPL --days 365 --benchmark SPY
echo - finfetch screen --symbols AAPL GOOGL --days 180 --benchmark QQQ
echo - finfetch screen --symbols AAPL --days 90 --benchmark VTI --risk-free-rate 0.04
echo - finfetch screen --symbols AAPL --format csv --output results.csv
echo - finfetch screen --symbols AAPL --debug-level 1 (for verbose output)
echo.
goto :end

:error_exit
echo.
echo ========================================
echo FinFetch Baseline Test: FAILED
echo ========================================
echo.
echo Please check the error messages above and resolve any issues.
exit /b 1

:end
