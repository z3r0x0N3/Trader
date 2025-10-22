"""Reporting helpers for analysis output."""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
from typing import Dict, Iterable, Optional

import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate


SUMMARY_COLUMNS = [
    "Ticker",
    "Last Close",
    "Change",
    "% Change",
    "52w High",
    "52w Low",
    "Avg Vol 20d",
    "RSI 14",
]


def _collect_summary(ticker: str, df: pd.DataFrame) -> Dict[str, float]:
    last = df.iloc[-1]
    prev_close = df["Close"].iloc[-2] if len(df) > 1 else float("nan")
    change = last["Close"] - prev_close if pd.notna(prev_close) else float("nan")
    pct = (change / prev_close * 100) if pd.notna(prev_close) and prev_close else float(
        "nan"
    )
    rsi = last.get("RSI_14") if "RSI_14" in df.columns else float("nan")
    return {
        "Ticker": ticker,
        "Last Close": round(float(last["Close"]), 2),
        "Change": round(float(change), 2) if pd.notna(change) else float("nan"),
        "% Change": round(float(pct), 2) if pd.notna(pct) else float("nan"),
        "52w High": round(float(df["High"].tail(252).max()), 2),
        "52w Low": round(float(df["Low"].tail(252).min()), 2),
        "Avg Vol 20d": round(float(df["Volume"].tail(20).mean()), 0),
        "RSI 14": round(float(rsi), 2) if pd.notna(rsi) else float("nan"),
    }


def build_summary_table(items: Iterable[Dict[str, float]]) -> str:
    rows = list(items)
    if not rows:
        return "No data available to summarize."
    return tabulate(rows, headers="keys", tablefmt="github", floatfmt=".2f")


def export_plot(
    ticker: str,
    df: pd.DataFrame,
    indicators: Iterable[str],
    output_dir: Path,
    figure_style: Optional[str] = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ticker}_chart.png"

    style_context = plt.style.context(figure_style) if figure_style else nullcontext()
    with style_context:
        fig, ax = plt.subplots(figsize=(10, 5))
        df["Close"].plot(ax=ax, label="Close", linewidth=1.5)

        if "sma" in indicators:
            for window in (20, 50):
                col = f"SMA_{window}"
                if col in df:
                    df[col].plot(ax=ax, label=col)
        if "ema" in indicators:
            for span in (12, 26):
                col = f"EMA_{span}"
                if col in df:
                    df[col].plot(ax=ax, label=col, linestyle="--")
        if "bollinger" in indicators:
            for suffix in ("UPPER", "LOWER"):
                col = f"BB_{suffix}_20"
                if col in df:
                    df[col].plot(
                        ax=ax,
                        label=col,
                        linestyle=":",
                        linewidth=0.9,
                        alpha=0.7,
                    )

        ax.set_title(f"{ticker} Price Action")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)

    return path


def generate_summary(
    ticker: str, df: pd.DataFrame, include_table: bool = True
) -> Dict[str, object]:
    summary = _collect_summary(ticker, df)
    stats: Dict[str, object] = {"metrics": summary}
    if include_table:
        stats["table"] = build_summary_table([summary])
    return stats
