"""
Asset allocation breakdown and multi-dimensional exposure analysis module:
- Asset Class Exposure (Equities, Fixed Income, Real Estate, Gold, Cash)
- Geographic Region Exposure (Malaysia, US, Global, Asia-Pacific, Europe)
- Country Exposure
- Native Currency Exposure
"""
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np

from src.asset_universe import get_asset_info


def compute_allocation_breakdowns(weights: Dict[str, float]) -> Dict[str, pd.DataFrame]:
    """
    Given portfolio weights dictionary, calculate allocation exposure distributions across:
    - by_asset: table of individual assets
    - by_asset_class: Equities vs Fixed Income vs REITs vs Gold vs Cash
    - by_region: Malaysia vs US vs Global vs Asia-Pacific vs Europe
    - by_currency: MYR vs USD vs SGD vs GBP vs EUR vs AUD
    """
    total_w = sum(weights.values())
    if total_w <= 0:
        return {}

    records = []
    for ticker, raw_w in weights.items():
        if raw_w <= 0:
            continue
        norm_w = raw_w / total_w
        info = get_asset_info(ticker)
        records.append({
            "Ticker": ticker,
            "Asset Name": info.get("name", ticker),
            "Asset Class": info.get("asset_class", "Other"),
            "Region": info.get("region", "Global"),
            "Country": info.get("country", "Global"),
            "Currency": info.get("currency", "USD"),
            "Weight": norm_w,
            "Weight %": norm_w * 100.0,
        })

    df_assets = pd.DataFrame(records)

    # 1. By Asset Class
    df_class = df_assets.groupby("Asset Class")["Weight %"].sum().reset_index()
    df_class = df_class.sort_values(by="Weight %", ascending=False).reset_index(drop=True)

    # 2. By Region
    df_region = df_assets.groupby("Region")["Weight %"].sum().reset_index()
    df_region = df_region.sort_values(by="Weight %", ascending=False).reset_index(drop=True)

    # 3. By Currency
    df_currency = df_assets.groupby("Currency")["Weight %"].sum().reset_index()
    df_currency = df_currency.sort_values(by="Weight %", ascending=False).reset_index(drop=True)

    # 4. By Country
    df_country = df_assets.groupby("Country")["Weight %"].sum().reset_index()
    df_country = df_country.sort_values(by="Weight %", ascending=False).reset_index(drop=True)

    return {
        "by_asset": df_assets,
        "by_asset_class": df_class,
        "by_region": df_region,
        "by_currency": df_currency,
        "by_country": df_country,
    }
