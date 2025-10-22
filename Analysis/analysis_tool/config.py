"""Configuration models and helpers for the analysis workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional


class DataSource(str, Enum):
    """Supported sources for price data."""

    YAHOO = "yahoo"
    LOCAL = "local"


def _normalize_tickers(tickers: Iterable[str]) -> List[str]:
    normalized = []
    for ticker in tickers:
        ticker = ticker.strip().upper()
        if ticker:
            normalized.append(ticker)
    if not normalized:
        raise ValueError("At least one ticker symbol must be provided.")
    return normalized


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            f"Invalid date '{date_str}'. Expected ISO format YYYY-MM-DD."
        ) from exc


@dataclass(slots=True)
class AnalysisConfig:
    """Shared configuration for running the analysis workflow."""

    tickers: Iterable[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    interval: str = "1d"
    indicators: Iterable[str] = field(
        default_factory=lambda: ("sma", "ema", "rsi", "macd", "bollinger", "returns")
    )
    data_source: DataSource = DataSource.YAHOO
    local_path: Optional[str] = None
    plot: bool = False
    output_dir: Path = Path("reports")
    auto_adjust: bool = True
    silent: bool = False
    start_dt: Optional[datetime] = field(init=False, default=None)
    end_dt: Optional[datetime] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.tickers = _normalize_tickers(self.tickers)
        self.indicators = [name.lower() for name in self.indicators]
        self.start_dt = _parse_date(self.start_date)
        self.end_dt = _parse_date(self.end_date)
        if self.start_dt and self.end_dt and self.start_dt >= self.end_dt:
            raise ValueError("Start date must be before end date.")
        valid_intervals = {"1d", "1wk", "1mo", "1h", "30m", "15m"}
        if self.interval not in valid_intervals:
            raise ValueError(
                f"Unsupported interval '{self.interval}'. "
                f"Choose from: {', '.join(sorted(valid_intervals))}"
            )
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if self.local_path is not None:
            self.local_path = str(self.local_path)

    def resolve_output_dir(self) -> Path:
        """Ensure the output directory exists and return it."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

    def start_for_download(self) -> Optional[datetime]:
        return self.start_dt

    def end_for_download(self) -> Optional[datetime]:
        return self.end_dt

    def resolve_local_path(self, ticker: str) -> Optional[Path]:
        """Resolve the CSV path for local data mode."""
        if self.data_source != DataSource.LOCAL or not self.local_path:
            return None
        path = Path(self.local_path)
        if path.is_file():
            return path
        candidates = [
            path / f"{ticker}.csv",
            path / f"{ticker.upper()}.csv",
            path / f"{ticker.lower()}.csv",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            f"Could not locate local CSV for ticker '{ticker}' under {path}."
        )
