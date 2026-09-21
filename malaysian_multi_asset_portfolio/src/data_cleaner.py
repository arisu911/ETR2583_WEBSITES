"""
Data cleaning, validation, and multi-market calendar alignment module.
Aligns assets traded across different international holidays (Malaysia, US, UK, SG, AU)
without look-ahead bias and generates comprehensive data-quality audit reports.
"""
from typing import Dict, Any, Tuple, List, Optional
import pandas as pd
import numpy as np


def clean_single_price_series(df: pd.DataFrame, ticker: str = "") -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Clean and extract the adjusted/close price series for a single ticker.
    Checks for duplicates, non-positive values, and NaNs.
    """
    audit = {
        "ticker": ticker,
        "raw_count": len(df),
        "duplicates_dropped": 0,
        "invalid_prices_dropped": 0,
        "clean_count": 0,
    }
    if df.empty:
        return pd.Series(dtype=float), audit

    # Choose Adj Close if available, else Close
    price_col = "Adj Close" if "Adj Close" in df.columns else "Close"
    s = df[price_col].dropna().copy()
    s = s.sort_index()

    # Drop duplicate dates
    dup_mask = s.index.duplicated(keep="first")
    audit["duplicates_dropped"] = int(dup_mask.sum())
    s = s[~dup_mask]

    # Filter zero or negative prices
    valid_mask = s > 0
    audit["invalid_prices_dropped"] = int((~valid_mask).sum())
    s = s[valid_mask]

    audit["clean_count"] = len(s)
    return s, audit


def build_aligned_price_matrix(
    asset_dict: Dict[str, pd.DataFrame],
    fx_dict: Dict[str, pd.DataFrame],
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Build unified daily price and FX matrices aligned on common business calendar.
    Uses forward-fill to carry over market prices across regional holidays (e.g. Bursa closed on Hari Raya, US open).

    Returns:
    - price_matrix_local: DataFrame of asset prices in local currencies
    - fx_matrix: DataFrame of FX rates to MYR (e.g. USD/MYR, SGD/MYR, etc.)
    - audit_report: Dict with alignment metadata and coverage statistics
    """
    prices_raw: Dict[str, pd.Series] = {}
    audits: List[Dict[str, Any]] = []

    for sym, df in asset_dict.items():
        s, aud = clean_single_price_series(df, ticker=sym)
        if not s.empty:
            prices_raw[sym] = s
            audits.append(aud)

    if not prices_raw:
        return pd.DataFrame(), pd.DataFrame(), {"status": "empty"}

    df_prices = pd.DataFrame(prices_raw)

    # FX Series
    fx_raw: Dict[str, pd.Series] = {}
    for pair, df_fx in fx_dict.items():
        s_fx, _ = clean_single_price_series(df_fx, ticker=pair)
        if not s_fx.empty:
            fx_raw[pair] = s_fx

    df_fx = pd.DataFrame(fx_raw)

    # Align dates
    all_dates = df_prices.index.union(df_fx.index).sort_values()
    df_prices = df_prices.reindex(all_dates).ffill().bfill()
    df_fx = df_fx.reindex(all_dates).ffill().bfill()

    # Filter date range if specified
    if start_date is not None:
        df_prices = df_prices[df_prices.index >= pd.to_datetime(start_date)]
        df_fx = df_fx[df_fx.index >= pd.to_datetime(start_date)]
    if end_date is not None:
        df_prices = df_prices[df_prices.index <= pd.to_datetime(end_date)]
        df_fx = df_fx[df_fx.index <= pd.to_datetime(end_date)]

    # Drop any remaining all-NaN rows
    df_prices = df_prices.dropna(how="all")
    df_fx = df_fx.reindex(df_prices.index).ffill().bfill()

    audit_summary = {
        "total_trading_days": len(df_prices),
        "start_date": df_prices.index[0].strftime("%Y-%m-%d") if not df_prices.empty else "N/A",
        "end_date": df_prices.index[-1].strftime("%Y-%m-%d") if not df_prices.empty else "N/A",
        "assets_loaded": list(df_prices.columns),
        "fx_loaded": list(df_fx.columns),
        "asset_audits": audits,
    }

    return df_prices, df_fx, audit_summary


def format_data_audit_table(audit_summary: Dict[str, Any]) -> pd.DataFrame:
    """Format audit details into a clean display DataFrame."""
    audits = audit_summary.get("asset_audits", [])
    records = []
    for a in audits:
        records.append({
            "Ticker": a.get("ticker", ""),
            "Raw Observations": f"{a.get('raw_count', 0):,}",
            "Duplicates Removed": a.get("duplicates_dropped", 0),
            "Invalid Filtered": a.get("invalid_prices_dropped", 0),
            "Usable Daily Records": f"{a.get('clean_count', 0):,}",
        })
    return pd.DataFrame(records)


def clean_and_align_market_data(raw_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Clean, align, and wrap raw market datasets into standard market data dictionary."""
    asset_dict = raw_dict.get("assets", {})
    fx_dict = raw_dict.get("fx", {})
    p_mat, fx_mat, audit = build_aligned_price_matrix(asset_dict, fx_dict)
    return {
        "price_matrix_local": p_mat,
        "fx_matrix": fx_mat,
        "audit_report": audit,
    }


def generate_data_quality_report(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract audit report metadata from market data dictionary."""
    return market_data.get("audit_report", {})
