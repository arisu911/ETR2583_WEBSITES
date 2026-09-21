"""
Data loading and caching module for multi-asset universe & FX series.
Fetches daily prices and exchange rates via yfinance with robust local Parquet caching.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf

from config.settings import (
    RAW_DATA_DIR,
    CACHE_DATA_DIR,
    PROCESSED_DATA_DIR,
    DEFAULT_RISK_FREE_RATE,
)
from src.asset_universe import ASSET_UNIVERSE, FX_TICKERS


def _clean_cache_filename(symbol: str, prefix: str = "asset") -> Path:
    """Generate safe filename for caching."""
    clean_sym = symbol.replace("^", "INDEX_").replace("=X", "_FX").replace(".KL", "_KL")
    return RAW_DATA_DIR / f"{prefix}_{clean_sym}.parquet"


def download_ticker_history(
    symbol: str,
    period: str = "10y",
    force_refresh: bool = False
) -> pd.DataFrame:
    """
    Download daily historical price data for an asset or FX ticker.
    Caches to Parquet and returns clean OHLCV DataFrame with normalized datetime index.
    """
    cache_file = _clean_cache_filename(symbol, prefix="price")

    if cache_file.exists() and not force_refresh:
        try:
            df = pd.read_parquet(cache_file)
            if not df.empty and isinstance(df.index, pd.DatetimeIndex):
                return df
        except Exception:
            pass

    # Special handling for synthetic cash proxy
    if symbol == "MYR_CASH":
        # Create 10-year daily cash index starting at 100.0 compounding at DEFAULT_RISK_FREE_RATE
        dates = pd.date_range(end=pd.Timestamp.today(), periods=252 * 10, freq="B")
        daily_rate = (1.0 + DEFAULT_RISK_FREE_RATE) ** (1.0 / 252.0) - 1.0
        cash_vals = 100.0 * np.cumprod(1.0 + np.full(len(dates), daily_rate))
        df_cash = pd.DataFrame({
            "Open": cash_vals,
            "High": cash_vals,
            "Low": cash_vals,
            "Close": cash_vals,
            "Adj Close": cash_vals,
            "Volume": 0,
        }, index=dates)
        df_cash.index = pd.to_datetime(df_cash.index).tz_localize(None)
        df_cash.to_parquet(cache_file)
        return df_cash

    try:
        yf_obj = yf.Ticker(symbol)
        df = yf_obj.history(period=period, interval="1d", auto_adjust=False)
        if df.empty:
            df = yf.download(symbol, period=period, interval="1d", progress=False, auto_adjust=False)
    except Exception as e:
        df = pd.DataFrame()

    if df.empty:
        raise ValueError(f"Unable to download data for ticker '{symbol}'.")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Standardize columns
    cols = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
    df = df[cols].copy()

    # Normalize index to timezone-naive UTC/calendar date for cross-asset matrix alignment
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    df.index = pd.to_datetime(df.index).normalize()

    # Save to Parquet
    df.to_parquet(cache_file)
    return df


from typing import Dict, Any, List, Optional, Tuple


def generate_synthetic_cash_proxy(
    dates: pd.DatetimeIndex,
    annual_rate: float = DEFAULT_RISK_FREE_RATE,
    initial_value: float = 100.0
) -> pd.Series:
    """Generate daily synthetic cash compounding price series."""
    daily_rate = (1.0 + annual_rate) ** (1.0 / 252.0) - 1.0
    cash_vals = initial_value * np.cumprod(1.0 + np.full(len(dates), daily_rate))
    return pd.Series(cash_vals, index=dates, name="MYR_CASH")


def load_all_universe_data(
    period: str = "10y",
    force_refresh: bool = False
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """
    Download and load daily historical prices for the entire multi-asset universe and FX pairs.
    Returns:
    - asset_data: Dict[ticker, df]
    - fx_data: Dict[pair_name, df]
    """
    asset_data: Dict[str, pd.DataFrame] = {}
    fx_data: Dict[str, pd.DataFrame] = {}

    for sym in ASSET_UNIVERSE.keys():
        try:
            asset_data[sym] = download_ticker_history(sym, period=period, force_refresh=force_refresh)
        except Exception:
            pass

    for name, sym in FX_TICKERS.items():
        try:
            fx_data[name] = download_ticker_history(sym, period=period, force_refresh=force_refresh)
        except Exception:
            pass

    return asset_data, fx_data


def fetch_all_market_data(
    start_date: str = "2014-01-01",
    period: str = "10y",
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Fetch and return all raw asset and FX datasets."""
    asset_data, fx_data = load_all_universe_data(period=period, force_refresh=force_refresh)
    return {
        "assets": asset_data,
        "fx": fx_data,
    }
