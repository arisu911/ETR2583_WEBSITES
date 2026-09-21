"""
Benchmark comparison and active risk-adjusted performance module:
- Beta (Cov(p, bm) / Var(bm))
- Alpha (Jensen's Alpha)
- Tracking Error (Std of active returns)
- Information Ratio (Active Return / Tracking Error)
- Up-Market and Down-Market Capture Ratios
"""
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

from config.settings import DEFAULT_RISK_FREE_RATE
from src.returns import compute_cagr
from src.risk import compute_annualized_volatility, compute_sharpe_ratio
from src.drawdowns import compute_drawdown_series


def compute_benchmark_comparison_metrics(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate relative metrics of portfolio vs benchmark:
    Beta, Alpha, Correlation, Tracking Error, Information Ratio, Up/Down Capture.
    """
    df = pd.DataFrame({"port": portfolio_returns, "bm": benchmark_returns}).dropna()
    if len(df) < 10:
        return {}

    rp = df["port"]
    rb = df["bm"]

    # Basic stats
    cagr_p = compute_cagr(rp, periods_per_year=periods_per_year)
    cagr_b = compute_cagr(rb, periods_per_year=periods_per_year)
    vol_p = compute_annualized_volatility(rp, periods_per_year=periods_per_year)
    vol_b = compute_annualized_volatility(rb, periods_per_year=periods_per_year)
    _, _, max_dd_p = compute_drawdown_series(rp)
    _, _, max_dd_b = compute_drawdown_series(rb)

    # Beta and Correlation
    cov_val = float(np.cov(rp, rb)[0, 1])
    var_b = float(np.var(rb, ddof=1))
    beta = cov_val / var_b if var_b > 0 else 1.0
    corr = float(rp.corr(rb))

    # Jensen's Alpha (annualized)
    alpha = (cagr_p - risk_free_rate) - beta * (cagr_b - risk_free_rate)

    # Active returns & Tracking Error
    active_returns = rp - rb
    tracking_error = float(active_returns.std() * np.sqrt(periods_per_year))
    active_cagr = cagr_p - cagr_b
    information_ratio = active_cagr / tracking_error if tracking_error > 0 else 0.0

    # Up/Down Capture Ratios
    up_mask = rb > 0
    down_mask = rb < 0

    up_capture = (rp[up_mask].mean() / rb[up_mask].mean() * 100.0) if up_mask.sum() > 0 and rb[up_mask].mean() != 0 else 100.0
    down_capture = (rp[down_mask].mean() / rb[down_mask].mean() * 100.0) if down_mask.sum() > 0 and rb[down_mask].mean() != 0 else 100.0

    return {
        "Portfolio CAGR": cagr_p * 100.0,
        "Benchmark CAGR": cagr_b * 100.0,
        "Portfolio Volatility": vol_p * 100.0,
        "Benchmark Volatility": vol_b * 100.0,
        "Portfolio Max Drawdown": max_dd_p,
        "Benchmark Max Drawdown": max_dd_b,
        "Beta (β)": beta,
        "Jensen's Alpha (α)": alpha * 100.0,
        "Correlation (r)": corr,
        "Tracking Error": tracking_error * 100.0,
        "Information Ratio": information_ratio,
        "Up-Market Capture %": up_capture,
        "Down-Market Capture %": down_capture,
    }


def format_benchmark_table(metrics: Dict[str, Any], benchmark_name: str = "Benchmark") -> pd.DataFrame:
    """Format benchmark comparison metrics into a structured presentation table."""
    alpha_val = metrics.get("Jensen's Alpha (α)", 0)
    records = [
        ("Portfolio CAGR vs Benchmark", f"{metrics.get('Portfolio CAGR', 0):.2f}%", f"{metrics.get('Benchmark CAGR', 0):.2f}%", f"{metrics.get('Portfolio CAGR', 0) - metrics.get('Benchmark CAGR', 0):+.2f}%"),
        ("Annualized Volatility", f"{metrics.get('Portfolio Volatility', 0):.2f}%", f"{metrics.get('Benchmark Volatility', 0):.2f}%", f"{metrics.get('Portfolio Volatility', 0) - metrics.get('Benchmark Volatility', 0):+.2f}%"),
        ("Maximum Drawdown", f"{metrics.get('Portfolio Max Drawdown', 0):.2f}%", f"{metrics.get('Benchmark Max Drawdown', 0):.2f}%", "—"),
        ("Beta to Benchmark (β)", f"{metrics.get('Beta (β)', 1.0):.2f}x", "1.00x", "Systematic sensitivity"),
        ("Jensen's Alpha (α)", f"{alpha_val:+.2f}%", "0.00%", "Excess risk-adjusted alpha"),
        ("Return Correlation (r)", f"{metrics.get('Correlation (r)', 0):.3f}", "1.000", "Linear co-movement"),
        ("Tracking Error", f"{metrics.get('Tracking Error', 0):.2f}%", "0.00%", "Active return volatility"),
        ("Information Ratio", f"{metrics.get('Information Ratio', 0):.2f}", "—", "Active return / Tracking error"),
        ("Up-Market Capture Ratio", f"{metrics.get('Up-Market Capture %', 100):.1f}%", "100.0%", "Performance during positive benchmark days"),
        ("Down-Market Capture Ratio", f"{metrics.get('Down-Market Capture %', 100):.1f}%", "100.0%", "Performance during negative benchmark days"),
    ]
    return pd.DataFrame(records, columns=["Metric", "Portfolio", f"{benchmark_name}", "Active Difference / Note"])
