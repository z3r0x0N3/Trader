# OMEGA Trader Analysis

Python-based toolkit for downloading equities data, calculating technical indicators, and generating compact performance summaries from the command line.

## Features
- Download historical OHLCV data via Yahoo Finance (powered by `yfinance`).
- Compute moving averages, RSI, MACD, Bollinger Bands, and daily returns.
- Generate text reports and optional plots saved to disk.
- Support batch mode for multiple tickers with configurable date ranges.

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m analysis_tool.cli --ticker AAPL --start 2023-01-01 --end 2023-12-31 --plot
```

## Command-Line Usage
```bash
python -m analysis_tool.cli \
  --ticker AAPL MSFT \
  --start 2024-01-01 \
  --end 2024-06-30 \
  --indicator sma ema rsi macd bollinger returns \
  --plot
```

Key flags:
- `--data-source yahoo|local`: switch between live downloads and CSV files.
- `--local-path`: CSV file or directory for offline mode (see `data_samples/`).
- `--interval`: granularity (1d, 1h, 30m, etc.).
- `--no-auto-adjust`: keep raw OHLC data from Yahoo (splits/dividends not applied).
- `--silent`: skip console output while still generating plots/reports.

## Local Data (Offline Mode)
Place CSV files with Yahoo-style column headers inside `data_samples/` and pass `--data-source local --local-path data_samples/sample.csv` to run computations without hitting the network.

## Project Layout
- `analysis_tool/`: Library and CLI code.
- `data_samples/`: Example CSV inputs for offline testing.
- `reports/`: Generated plots and summaries (created at runtime).

## Next Steps
- Extend indicator coverage with user-specific strategies.
- Integrate risk metrics such as Sharpe and Sortino ratios.
- Build automated tests under `tests/` once real data scenarios are defined.
