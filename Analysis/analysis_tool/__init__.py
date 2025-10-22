"""Top-level package for the OMEGA Trader analysis toolkit."""

from .config import AnalysisConfig, DataSource
from .workflow import run_analysis

__all__ = ["AnalysisConfig", "DataSource", "run_analysis"]
