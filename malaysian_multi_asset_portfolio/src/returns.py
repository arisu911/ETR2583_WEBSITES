"""
Financial returns calculation module:
- Daily, monthly, and annual returns
- Compound Annual Growth Rate (CAGR)
- Monthly returns matrix (Jan–Dec heatmap table)
- Annual return breakdown & rolling return metrics
"""
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np


def compute_asset_daily_returns(price_matrix: pd.DataFrame) -> pd.DataFrame:
    """Calculate percentage change daily returns for all assets in matrix."""
    return price_matrix.pct_change().dropna(how="all")


def compute_cagr(
    returns_series: pd.Series,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).
    CAGR = (End Value / Start Value) ^ (1 / Years) - 1
    """
    clean_r = returns_series.dropna()
    n = len(clean_r)
    if n < 2:
        return 0.0

    wealth = (1.0 + clean_r).cumprod()
    total_growth = wealth.iloc[-1]
    years = n / float(periods_per_year)
    if years <= 0 or total_growth <= 0:
        return 0.0

    cagr = (total_growth ** (1.0 / years)) - 1.0
    return float(cagr)


def compute_wealth_index(
    returns_series: pd.Series,
    initial_capital: float = 100000.0
) -> pd.Series:
    """Calculate cumulative wealth index series starting from initial capital."""
    clean_r = returns_series.dropna()
    wealth = initial_capital * (1.0 + clean_r).cumprod()
    return wealth


def compute_monthly_returns_matrix(returns_series: pd.Series) -> pd.DataFrame:
    """
    Generate Year x Month returns matrix (January to December) + Year Total.
    Values are formatted as percentages.
    """
    clean_r = returns_series.dropna()
    if clean_r.empty:
        return pd.DataFrame()

    # Resample to monthly compounding
    monthly_ret = clean_r.resample("ME").apply(lambda x: (1.0 + x).cumprod().iloc[-1] - 1.0 if len(x) > 0 else 0.0)

    df_m = pd.DataFrame({
        "Year": monthly_ret.index.year,
        "Month": monthly_ret.index.month,
        "Return": monthly_ret.values * 100.0,
    })

    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    pivot = df_m.pivot(index="Year", columns="Month", values="Return")
    pivot.columns = [month_names[m - 1] for m in pivot.columns]

    # Calculate full year compound return
    yearly_ret = clean_r.resample("YE").apply(lambda x: (1.0 + x).cumprod().iloc[-1] - 1.0 if len(x) > 0 else 0.0)
    pivot["Year Total"] = yearly_ret.values * 100.0 if len(yearly_ret) == len(pivot) else np.nan

    return pivot.sort_index(ascending=False)


def compute_annual_returns_table(returns_series: pd.Series) -> pd.DataFrame:
    """
    Generate annual summary table:
    Year, Annual Return, Volatility, Max DD, Best Month, Worst Month, Positive Months, Negative Months.
    """
    from src.drawdowns import compute_drawdown_series

    clean_r = returns_series.dropna()
    if clean_r.empty:
        return pd.DataFrame()

    rows = []
    for year, group in clean_r.groupby(clean_r.index.year):
        n = len(group)
        if n < 5:
            continue

        cum_ret = (1.0 + group).cumprod().iloc[-1] - 1.0
        ann_vol = group.std() * np.sqrt(252) * 100.0
        _, _, max_dd = compute_drawdown_series(group)

        # Monthly breakdown
        m_rets = group.resample("ME").apply(lambda x: (1.0 + x).cumprod().iloc[-1] - 1.0)
        best_m = m_rets.max() * 100.0 if not m_rets.empty else 0.0
        worst_m = m_rets.min() * 100.0 if not m_rets.empty else 0.0
        pos_m = (m_rets > 0).sum()
        neg_m = (m_rets < 0).sum()

        rows.append({
            "Year": str(year),
            "Annual Return": f"{cum_ret * 100:+.2f}%",
            "Annualized Vol": f"{ann_vol:.2f}%",
            "Max Drawdown": f"{max_dd:.2f}%",
            "Best Month": f"{best_m:+.2f}%",
            "Worst Month": f"{worst_m:+.2f}%",
            "Positive Months": f"{pos_m} / {len(m_rets)}",
            "Trading Days": n,
            "_raw_return": cum_ret * 100.0,
            "_raw_vol": ann_vol,
            "_raw_max_dd": max_dd,
        })

    return pd.DataFrame(rows).sort_values(by="Year", ascending=False).reset_index(drop=True)
