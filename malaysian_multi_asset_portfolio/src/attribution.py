"""
Performance & Currency Attribution Engine.
Decomposes total portfolio return into asset-level capital return vs foreign exchange contribution.
"""
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np

from src.asset_universe import get_asset_info
from src.currency import get_fx_rate_series


def compute_portfolio_return_attribution(
    weights: Dict[str, float],
    price_matrix_local: pd.DataFrame,
    fx_matrix: pd.DataFrame,
    target_currency: str = "MYR"
) -> pd.DataFrame:
    """
    Calculate return contribution of each asset in the portfolio, separating
    local price appreciation from currency exchange rate gain/loss.

    Returns DataFrame:
    [Ticker, Asset Name, Asset Class, Weight %, Local Return %, FX Effect %, Investor Return %, Weighted Contribution %]
    """
    total_w = sum(weights.values())
    if total_w <= 0:
        return pd.DataFrame()

    records = []
    for ticker, raw_w in weights.items():
        if raw_w <= 0 or ticker not in price_matrix_local.columns:
            continue
        w = raw_w / total_w
        info = get_asset_info(ticker)
        native_curr = info.get("currency", "USD")

        p_s = price_matrix_local[ticker].dropna()
        fx_s = get_fx_rate_series(fx_matrix, from_currency=native_curr, to_currency=target_currency).reindex(p_s.index).ffill()

        # Cumulative returns
        tot_local = (p_s.iloc[-1] / p_s.iloc[0] - 1.0) if len(p_s) > 1 else 0.0
        tot_fx = (fx_s.iloc[-1] / fx_s.iloc[0] - 1.0) if len(fx_s) > 1 else 0.0
        tot_investor = (1.0 + tot_local) * (1.0 + tot_fx) - 1.0
        weighted_contrib = w * tot_investor

        records.append({
            "Ticker": ticker,
            "Asset Name": info.get("name", ticker),
            "Asset Class": info.get("asset_class", "Other"),
            "Currency": native_curr,
            "Weight %": w * 100.0,
            "Local Return %": tot_local * 100.0,
            "FX Effect %": tot_fx * 100.0,
            "Investor Return %": tot_investor * 100.0,
            "Portfolio Contribution %": weighted_contrib * 100.0,
        })

    df_attr = pd.DataFrame(records)
    return df_attr
