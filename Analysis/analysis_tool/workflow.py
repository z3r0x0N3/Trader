"""High-level orchestration for running stock analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from .config import AnalysisConfig
from .data import load_price_history
from .indicators import apply_indicators
from .report import export_plot, generate_summary


@dataclass
class AnalysisResult:
    ticker: str
    data_source: str
    dataframe: pd.DataFrame
    summary: Dict[str, object]
    plot_path: Optional[str] = None


def run_analysis(config: AnalysisConfig) -> List[AnalysisResult]:
    results: List[AnalysisResult] = []
    for ticker in config.tickers:
        df, data_source = load_price_history(ticker, config)
        apply_indicators(df, config.indicators)
        summary = generate_summary(ticker, df)
        plot_path: Optional[str] = None
        if config.plot:
            plot_path = str(
                export_plot(
                    ticker,
                    df,
                    config.indicators,
                    config.resolve_output_dir(),
                )
            )
        results.append(
            AnalysisResult(
                ticker=ticker,
                data_source=data_source,
                dataframe=df,
                summary=summary,
                plot_path=plot_path,
            )
        )
    return results
