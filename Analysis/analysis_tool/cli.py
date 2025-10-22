"""Command-line interface for the OMEGA Trader analysis toolkit."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

from .config import AnalysisConfig, DataSource
from .workflow import run_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analysis_tool",
        description="Download market data, compute indicators, and generate summaries.",
    )
    parser.add_argument(
        "-t",
        "--ticker",
        dest="tickers",
        nargs="+",
        required=True,
        help="One or more ticker symbols (e.g. AAPL MSFT).",
    )
    parser.add_argument("--start", dest="start_date", help="Start date YYYY-MM-DD.")
    parser.add_argument("--end", dest="end_date", help="End date YYYY-MM-DD.")
    parser.add_argument(
        "--interval",
        default="1d",
        help="Price interval (e.g. 1d, 1wk, 1mo, 1h, 30m, 15m).",
    )
    parser.add_argument(
        "-i",
        "--indicator",
        dest="indicators",
        nargs="+",
        help="Specify indicators (default: sma ema rsi macd bollinger returns).",
    )
    parser.add_argument(
        "--data-source",
        choices=[choice.value for choice in DataSource],
        default=DataSource.YAHOO.value,
        help="Where to load data from.",
    )
    parser.add_argument(
        "--local-path",
        help="Path to CSV file or directory containing CSV files for local mode.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Create matplotlib plots for each ticker in the reports directory.",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory for generated reports and charts (default: reports/).",
    )
    parser.add_argument(
        "--no-auto-adjust",
        dest="auto_adjust",
        action="store_false",
        help="Disable Yahoo auto-adjustment for dividends/splits.",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress verbose output, returning only exit status.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="OMEGA Trader Analysis 1.0.0",
    )
    return parser


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.data_source == DataSource.LOCAL.value and not args.local_path:
        parser.error("--local-path is required when --data-source=local.")
    return args


def build_config(args: argparse.Namespace) -> AnalysisConfig:
    indicators = args.indicators or ("sma", "ema", "rsi", "macd", "bollinger", "returns")
    return AnalysisConfig(
        tickers=args.tickers,
        start_date=args.start_date,
        end_date=args.end_date,
        interval=args.interval,
        indicators=indicators,
        data_source=DataSource(args.data_source),
        local_path=args.local_path,
        plot=args.plot,
        output_dir=args.output_dir,
        auto_adjust=args.auto_adjust,
        silent=args.silent,
    )


def main(argv: Iterable[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)
    config = build_config(args)
    try:
        results = run_analysis(config)
    except Exception as exc:  # noqa: BLE001 - surface to CLI with friendly message.
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    if not config.silent:
        for result in results:
            header = f"\n=== {result.ticker} ==="
            print(header)
            print(f"Data source: {result.data_source}")
            summary_table = result.summary.get("table")
            if summary_table:
                print(summary_table)
            else:
                print(result.summary["metrics"])
            if result.plot_path:
                print(f"Chart saved to: {result.plot_path}")
        print("\nCompleted analysis for "
              f"{', '.join(res.ticker for res in results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
