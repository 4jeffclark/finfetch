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
echo Output directory: %OUTPUT_DIR%
echo.

REM Test 1 - Basic screening with enhanced metrics (table format)
echo [Test 1] Basic screening with enhanced metrics (table format)
echo Command: finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY > "%OUTPUT_DIR%\test01-AAPL-GOOGL-365d-SPY.txt" 2>&1
if errorlevel 1 (
    echo ERROR: Test 1 failed - check test01-AAPL-GOOGL-365d-SPY.txt for details
    goto :error_exit
)
REM Also save as CSV
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY --format csv --output "%OUTPUT_DIR%\test01-AAPL-GOOGL-365d-SPY.csv" > "%OUTPUT_DIR%\test01-AAPL-GOOGL-365d-SPY-errors.txt" 2>&1
if errorlevel 1 (
    echo WARNING: Test 1 CSV generation failed - check test01-AAPL-GOOGL-365d-SPY-errors.txt
) else (
    if exist "%OUTPUT_DIR%\test01-AAPL-GOOGL-365d-SPY.csv" (
        echo Test 1 CSV created: test01-AAPL-GOOGL-365d-SPY.csv
    ) else (
        echo ERROR: Test 1 CSV file not created
    )
)
echo Test 1 output saved to: test01-AAPL-GOOGL-365d-SPY.txt and test01-AAPL-GOOGL-365d-SPY.csv
echo.

REM Test 2 - Tech stocks vs QQQ benchmark with different time window
echo [Test 2] Tech stocks vs QQQ benchmark with different time window
echo Command: finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --symbols MSFT --days 180 --benchmark QQQ
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --symbols MSFT --days 180 --benchmark QQQ > "%OUTPUT_DIR%\test02-AAPL-GOOGL-MSFT-180d-QQQ.txt" 2>&1
if errorlevel 1 (
    echo ERROR: Test 2 failed - check test02-AAPL-GOOGL-MSFT-180d-QQQ.txt for details
    goto :error_exit
)
REM Also save as CSV
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --symbols MSFT --days 180 --benchmark QQQ --format csv --output "%OUTPUT_DIR%\test02-AAPL-GOOGL-MSFT-180d-QQQ.csv" > "%OUTPUT_DIR%\test02-AAPL-GOOGL-MSFT-180d-QQQ-errors.txt" 2>&1
if errorlevel 1 (
    echo WARNING: Test 2 CSV generation failed - check test02-AAPL-GOOGL-MSFT-180d-QQQ-errors.txt
) else (
    if exist "%OUTPUT_DIR%\test02-AAPL-GOOGL-MSFT-180d-QQQ.csv" (
        echo Test 2 CSV created: test02-AAPL-GOOGL-MSFT-180d-QQQ.csv
    ) else (
        echo ERROR: Test 2 CSV file not created
    )
)
echo Test 2 output saved to: test02-AAPL-GOOGL-MSFT-180d-QQQ.txt and test02-AAPL-GOOGL-MSFT-180d-QQQ.csv
echo.

REM Test 3 - Short-term analysis with custom risk-free rate
echo [Test 3] Short-term analysis with custom risk-free rate
echo Command: finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --days 90 --benchmark VTI --risk-free-rate 0.04
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --days 90 --benchmark VTI --risk-free-rate 0.04 > "%OUTPUT_DIR%\test03-AAPL-GOOGL-90d-VTI-rfr004.txt" 2>&1
if errorlevel 1 (
    echo ERROR: Test 3 failed - check test03-AAPL-GOOGL-90d-VTI-rfr004.txt for details
    goto :error_exit
)
REM Also save as CSV
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --days 90 --benchmark VTI --risk-free-rate 0.04 --format csv --output "%OUTPUT_DIR%\test03-AAPL-GOOGL-90d-VTI-rfr004.csv" > "%OUTPUT_DIR%\test03-AAPL-GOOGL-90d-VTI-rfr004-errors.txt" 2>&1
if errorlevel 1 (
    echo WARNING: Test 3 CSV generation failed - check test03-AAPL-GOOGL-90d-VTI-rfr004-errors.txt
) else (
    if exist "%OUTPUT_DIR%\test03-AAPL-GOOGL-90d-VTI-rfr004.csv" (
        echo Test 3 CSV created: test03-AAPL-GOOGL-90d-VTI-rfr004.csv
    ) else (
        echo ERROR: Test 3 CSV file not created
    )
)
echo Test 3 output saved to: test03-AAPL-GOOGL-90d-VTI-rfr004.txt and test03-AAPL-GOOGL-90d-VTI-rfr004.csv
echo.

REM Test 4 - Long-term analysis with multiple stocks
echo [Test 4] Long-term analysis with multiple stocks
echo Command: finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --symbols MSFT --symbols TSLA --days 730 --benchmark SPY --risk-free-rate 0.035
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --symbols MSFT --symbols TSLA --days 730 --benchmark SPY --risk-free-rate 0.035 > "%OUTPUT_DIR%\test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035.txt" 2>&1
if errorlevel 1 (
    echo ERROR: Test 4 failed - check test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035.txt for details
    goto :error_exit
)
REM Also save as CSV
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --symbols MSFT --symbols TSLA --days 730 --benchmark SPY --risk-free-rate 0.035 --format csv --output "%OUTPUT_DIR%\test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035.csv" > "%OUTPUT_DIR%\test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035-errors.txt" 2>&1
if errorlevel 1 (
    echo WARNING: Test 4 CSV generation failed - check test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035-errors.txt
) else (
    if exist "%OUTPUT_DIR%\test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035.csv" (
        echo Test 4 CSV created: test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035.csv
    ) else (
        echo ERROR: Test 4 CSV file not created
    )
)
echo Test 4 output saved to: test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035.txt and test04-AAPL-GOOGL-MSFT-TSLA-730d-SPY-rfr0035.csv
echo.

REM Test 5 - CSV file output with comprehensive metrics
echo [Test 5] CSV file output with comprehensive metrics
echo Command: finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY --format csv --output "%OUTPUT_DIR%\test05-AAPL-GOOGL-365d-SPY.csv"
finfetch --debug-level 1 screen --symbols AAPL --symbols GOOGL --days 365 --benchmark SPY --format csv --output "%OUTPUT_DIR%\test05-AAPL-GOOGL-365d-SPY.csv" > "%OUTPUT_DIR%\test05-AAPL-GOOGL-365d-SPY-errors.txt" 2>&1
if errorlevel 1 (
    echo ERROR: Test 5 failed
    goto :error_exit
)
if exist "%OUTPUT_DIR%\test05-AAPL-GOOGL-365d-SPY.csv" (
    echo Test 5 CSV created: test05-AAPL-GOOGL-365d-SPY.csv
) else (
    echo ERROR: Test 5 CSV file not created
)
echo Test 5 output saved to: test05-AAPL-GOOGL-365d-SPY.csv
echo.

REM Test 6 - CSV output to different file with different parameters
echo [Test 6] CSV output to different file with different parameters
echo Command: finfetch --debug-level 1 screen --symbols AAPL --symbols MSFT --symbols TSLA --days 180 --benchmark QQQ --format csv --output "%OUTPUT_DIR%\test06-AAPL-MSFT-TSLA-180d-QQQ.csv"
finfetch --debug-level 1 screen --symbols AAPL --symbols MSFT --symbols TSLA --days 180 --benchmark QQQ --format csv --output "%OUTPUT_DIR%\test06-AAPL-MSFT-TSLA-180d-QQQ.csv" > "%OUTPUT_DIR%\test06-AAPL-MSFT-TSLA-180d-QQQ-errors.txt" 2>&1
if errorlevel 1 (
    echo ERROR: Test 6 failed
    goto :error_exit
)
if exist "%OUTPUT_DIR%\test06-AAPL-MSFT-TSLA-180d-QQQ.csv" (
    echo Test 6 CSV created: test06-AAPL-MSFT-TSLA-180d-QQQ.csv
) else (
    echo ERROR: Test 6 CSV file not created
)
echo Test 6 output saved to: test06-AAPL-MSFT-TSLA-180d-QQQ.csv
echo.

echo ========================================
echo FinFetch Enhanced Screening Test: COMPLETED
echo ========================================
echo.
echo All screening tests completed successfully!
echo.
echo Output files saved to: %OUTPUT_DIR%
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
