"""Data acquisition helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import AnalysisConfig, DataSource

YAHOO_REQUIRED_COLUMNS = ("Open", "High", "Low", "Close", "Adj Close", "Volume")


def _validate_dataframe(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    missing = [col for col in YAHOO_REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Data for {ticker} missing expected columns: {', '.join(missing)}"
        )
    cleaned = df.copy()
    cleaned.index = pd.to_datetime(cleaned.index)
    cleaned.sort_index(inplace=True)
    cleaned.dropna(how="all", inplace=True)
    return cleaned


def _load_local_csv(path: Path, ticker: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return _validate_dataframe(df, ticker)


def _download_yahoo(ticker: str, config: AnalysisConfig) -> pd.DataFrame:
    try:
        import yfinance as yf  # Lazy import to keep core logic testable without dependency.
    except ImportError as exc:
        raise RuntimeError(
            "yfinance is required for Yahoo data downloads. "
            "Install dependencies with `pip install -r requirements.txt`."
        ) from exc

    df = yf.download(
        ticker,
        start=config.start_for_download(),
        end=config.end_for_download(),
        interval=config.interval,
        auto_adjust=config.auto_adjust,
        progress=False,
        threads=False,
    )
    if df.empty:
        raise RuntimeError(
            f"No data returned for {ticker} using the provided parameters."
        )
    df.index.name = "Date"
    return _validate_dataframe(df, ticker)


def load_price_history(
    ticker: str, config: AnalysisConfig
) -> Tuple[pd.DataFrame, str]:
    """Fetch price data based on configuration and return alongside a label."""
    if config.data_source == DataSource.YAHOO:
        df = _download_yahoo(ticker, config)
        source_label = "Yahoo Finance"
    elif config.data_source == DataSource.LOCAL:
        path = config.resolve_local_path(ticker)
        if path is None:
            raise ValueError(
                "Local data source specified but no path provided or resolved."
            )
        df = _load_local_csv(path, ticker)
        source_label = f"Local CSV ({path})"
    else:
        raise ValueError(f"Unsupported data source: {config.data_source}")
    return df, source_label
