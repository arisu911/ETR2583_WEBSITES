"""
Multi-currency conversion & historical FX compounding attribution engine.
Converts multi-asset price matrices to any reporting currency (MYR, USD, SGD, GBP, EUR, AUD)
using date-specific historical exchange rates, and isolates local asset return from currency effect.
"""
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np

from src.asset_universe import ASSET_UNIVERSE, get_asset_info


def get_fx_rate_series(
    fx_matrix: pd.DataFrame,
    from_currency: str,
    to_currency: str
) -> pd.Series:
    """
    Extract or calculate cross FX rate series: 1 unit of `from_currency` in `to_currency`.
    E.g. from USD to MYR returns USD/MYR exchange rate (~4.40).
    """
    if from_currency == to_currency:
        return pd.Series(1.0, index=fx_matrix.index)

    # Base pairs in fx_matrix are against MYR:
    # "USD/MYR" = MYR per 1 USD
    # "SGD/MYR" = MYR per 1 SGD
    # "GBP/MYR" = MYR per 1 GBP
    # "EUR/MYR" = MYR per 1 EUR
    # "AUD/MYR" = MYR per 1 AUD

    def _to_myr_rate(curr: str) -> pd.Series:
        if curr == "MYR":
            return pd.Series(1.0, index=fx_matrix.index)
        pair = f"{curr}/MYR"
        if pair in fx_matrix.columns:
            return fx_matrix[pair]
        # Fallback
        return pd.Series(1.0, index=fx_matrix.index)

    rate_from_to_myr = _to_myr_rate(from_currency)
    rate_to_to_myr = _to_myr_rate(to_currency)

    # Rate from A to B = (MYR per A) / (MYR per B)
    rate_from_to_target = rate_from_to_myr / rate_to_to_myr
    return rate_from_to_target


def convert_prices_to_reporting_currency(
    price_matrix_local: pd.DataFrame,
    fx_matrix: pd.DataFrame,
    target_currency: str = "MYR"
) -> pd.DataFrame:
    """
    Convert all asset prices in the price matrix from their respective native currencies
    to the chosen target/reporting currency (e.g. MYR, USD, SGD, GBP, EUR, AUD).
    """
    df_converted = pd.DataFrame(index=price_matrix_local.index)

    for col in price_matrix_local.columns:
        info = get_asset_info(col)
        native_curr = info.get("currency", "USD")
        fx_rate = get_fx_rate_series(fx_matrix, from_currency=native_curr, to_currency=target_currency)
        df_converted[col] = price_matrix_local[col] * fx_rate

    return df_converted


def compute_currency_attribution(
    price_matrix_local: pd.DataFrame,
    fx_matrix: pd.DataFrame,
    ticker: str,
    target_currency: str = "MYR"
) -> pd.DataFrame:
    """
    Compute daily and cumulative return attribution for a foreign asset:
    - R_local: Asset return in its local/native currency
    - R_fx: FX exchange rate return vs reporting currency
    - R_interaction: R_local * R_fx
    - R_investor: Total investor return in reporting currency ( (1+R_local)*(1+R_fx) - 1 )

    Returns DataFrame with daily returns and cumulative growth curves.
    """
    if ticker not in price_matrix_local.columns:
        return pd.DataFrame()

    info = get_asset_info(ticker)
    native_curr = info.get("currency", "USD")

    p_local = price_matrix_local[ticker].dropna()
    fx_rate = get_fx_rate_series(fx_matrix, from_currency=native_curr, to_currency=target_currency).reindex(p_local.index).ffill()

    r_local = p_local.pct_change().dropna()
    r_fx = fx_rate.pct_change().reindex(r_local.index).dropna()

    common_idx = r_local.index.intersection(r_fx.index)
    r_local = r_local.loc[common_idx]
    r_fx = r_fx.loc[common_idx]

    r_interaction = r_local * r_fx
    r_investor = (1.0 + r_local) * (1.0 + r_fx) - 1.0

    df_attr = pd.DataFrame({
        "r_local": r_local,
        "r_fx": r_fx,
        "r_interaction": r_interaction,
        "r_investor": r_investor,
        "cum_local": (1.0 + r_local).cumprod() - 1.0,
        "cum_fx": (1.0 + r_fx).cumprod() - 1.0,
        "cum_investor": (1.0 + r_investor).cumprod() - 1.0,
    }, index=common_idx)

    return df_attr


def summarize_fx_impact_table(
    price_matrix_local: pd.DataFrame,
    fx_matrix: pd.DataFrame,
    target_currency: str = "MYR"
) -> pd.DataFrame:
    """
    Generate summary table showing Local Return, FX Contribution, and Investor Return
    for all assets over the available historical period.
    """
    records = []
    for col in price_matrix_local.columns:
        info = get_asset_info(col)
        native_curr = info.get("currency", "USD")

        attr = compute_currency_attribution(price_matrix_local, fx_matrix, col, target_currency=target_currency)
        if attr.empty:
            continue

        tot_local = float(attr["cum_local"].iloc[-1]) * 100.0
        tot_fx = float(attr["cum_fx"].iloc[-1]) * 100.0
        tot_investor = float(attr["cum_investor"].iloc[-1]) * 100.0

        records.append({
            "Asset Symbol": col,
            "Asset Name": info.get("name", col),
            "Native Currency": native_curr,
            "Reporting Currency": target_currency,
            "Local Asset Return": f"{tot_local:+.2f}%",
            "FX Effect": f"{tot_fx:+.2f}%",
            "Investor Return": f"{tot_investor:+.2f}%",
            "_raw_local": tot_local,
            "_raw_fx": tot_fx,
            "_raw_investor": tot_investor,
        })

    return pd.DataFrame(records)
