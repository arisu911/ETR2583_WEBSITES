"""
Statistical aggregation, correlation, and covariance matrix calculations.
"""
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from scipy import stats

from src.asset_universe import get_asset_info


def compute_correlation_matrix(
    asset_returns_df: pd.DataFrame,
    use_asset_names: bool = True
) -> pd.DataFrame:
    """
    Calculate Pearson correlation matrix across all assets in DataFrame.
    Optionally labels columns and index with full descriptive asset names.
    """
    clean_df = asset_returns_df.dropna()
    corr = clean_df.corr()

    if use_asset_names:
        rename_map = {col: get_asset_info(col).get("name", col) for col in corr.columns}
        corr = corr.rename(index=rename_map, columns=rename_map)

    return corr


def compute_rolling_correlation(
    series_a: pd.Series,
    series_b: pd.Series,
    window: int = 60
) -> pd.Series:
    """Calculate rolling Pearson correlation between two return series."""
    df = pd.DataFrame({"a": series_a, "b": series_b}).dropna()
    return df["a"].rolling(window).corr(df["b"])


def compute_distribution_summary(
    series: pd.Series,
    label: str = "Series",
    is_percentage: bool = True
) -> Dict[str, Any]:
    """Calculate descriptive distribution metrics for a returns or wealth series."""
    clean_s = series.dropna()
    n = len(clean_s)
    if n == 0:
        return {}

    p10, p25, p50, p75, p90, p95 = np.percentile(clean_s, [10, 25, 50, 75, 90, 95])
    skew_val = float(stats.skew(clean_s, bias=False)) if n > 2 else 0.0
    kurt_val = float(stats.kurtosis(clean_s, bias=False)) if n > 3 else 0.0

    return {
        "metric": label,
        "count": n,
        "mean": float(clean_s.mean()),
        "median": float(clean_s.median()),
        "std": float(clean_s.std()),
        "min": float(clean_s.min()),
        "max": float(clean_s.max()),
        "p10": float(p10),
        "p25": float(p25),
        "p50": float(p50),
        "p75": float(p75),
        "p90": float(p90),
        "p95": float(p95),
        "skewness": round(skew_val, 3),
        "kurtosis": round(kurt_val, 3),
        "is_percentage": is_percentage,
    }
