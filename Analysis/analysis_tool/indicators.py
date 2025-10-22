"""Technical indicator computations."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def add_sma(df: pd.DataFrame) -> None:
    close = df["Close"]
    for window in (10, 20, 50, 200):
        df[f"SMA_{window}"] = close.rolling(window, min_periods=window).mean()


def add_ema(df: pd.DataFrame) -> None:
    close = df["Close"]
    for span in (12, 26):
        df[f"EMA_{span}"] = _ema(close, span=span)


def add_rsi(df: pd.DataFrame, period: int = 14) -> None:
    close = df["Close"]
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1 / period, adjust=False).mean()
    roll_down = down.ewm(alpha=1 / period, adjust=False).mean()
    rs = roll_up / roll_down.replace(0, np.nan)
    df[f"RSI_{period}"] = 100 - (100 / (1 + rs))


def add_macd(df: pd.DataFrame) -> None:
    ema12 = _ema(df["Close"], span=12)
    ema26 = _ema(df["Close"], span=26)
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    df["MACD"] = macd
    df["MACD_SIGNAL"] = signal
    df["MACD_HIST"] = macd - signal


def add_bollinger(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> None:
    roll = df["Close"].rolling(window=window, min_periods=window)
    middle = roll.mean()
    std = roll.std()
    df[f"BB_MIDDLE_{window}"] = middle
    df[f"BB_UPPER_{window}"] = middle + num_std * std
    df[f"BB_LOWER_{window}"] = middle - num_std * std


def add_daily_returns(df: pd.DataFrame) -> None:
    df["DAILY_RETURN"] = df["Adj Close"].pct_change()


INDICATOR_FUNCTIONS = {
    "sma": add_sma,
    "ema": add_ema,
    "rsi": add_rsi,
    "macd": add_macd,
    "bollinger": add_bollinger,
    "returns": add_daily_returns,
}


def apply_indicators(df: pd.DataFrame, indicators: Iterable[str]) -> None:
    """Mutate *df* to include the requested technical indicators."""
    for name in indicators:
        func = INDICATOR_FUNCTIONS.get(name.lower())
        if not func:
            raise ValueError(f"Unknown indicator '{name}'.")
        func(df)
