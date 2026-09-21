"""
Asset Universe Metadata & Registry for Malaysian Multi-Asset Portfolio Analytics.
Defines asset classes, country, currency, region, ticker symbols, and economic role.
"""
from typing import Dict, Any, List
import pandas as pd

ASSET_UNIVERSE: Dict[str, Dict[str, Any]] = {
    "^KLSE": {
        "ticker": "^KLSE",
        "name": "FBM KLCI (Malaysia Equities)",
        "asset_class": "Equities",
        "region": "Malaysia",
        "country": "Malaysia",
        "currency": "MYR",
        "instrument_type": "Index",
        "description": "FTSE Bursa Malaysia KLCI 30 largest domestic market-cap companies.",
    },
    "EWM": {
        "ticker": "EWM",
        "name": "iShares MSCI Malaysia ETF",
        "asset_class": "Equities",
        "region": "Malaysia",
        "country": "Malaysia",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "US-listed liquid ETF tracking broad Malaysian equity market in USD.",
    },
    "0800EA.KL": {
        "ticker": "0800EA.KL",
        "name": "ABF Malaysia Bond Index Fund",
        "asset_class": "Fixed Income",
        "region": "Malaysia",
        "country": "Malaysia",
        "currency": "MYR",
        "instrument_type": "ETF",
        "description": "Domestic ETF tracking Malaysian Government Securities (MGS) & sovereign sukuk.",
    },
    "5180.KL": {
        "ticker": "5180.KL",
        "name": "KLCC Real Estate / Stapled Group",
        "asset_class": "Real Estate / REITs",
        "region": "Malaysia",
        "country": "Malaysia",
        "currency": "MYR",
        "instrument_type": "REIT",
        "description": "Premier Malaysian commercial property and REIT asset proxy.",
    },
    "MYR_CASH": {
        "ticker": "MYR_CASH",
        "name": "Malaysian Money Market / Cash",
        "asset_class": "Cash / Money Market",
        "region": "Malaysia",
        "country": "Malaysia",
        "currency": "MYR",
        "instrument_type": "Synthetic Cash",
        "description": "Domestic short-term money market proxy compounding at BNM OPR baseline (3.0% p.a.).",
    },
    "SPY": {
        "ticker": "SPY",
        "name": "S&P 500 ETF",
        "asset_class": "Equities",
        "region": "United States",
        "country": "United States",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "500 leading US large-cap corporations representing US equity core.",
    },
    "QQQ": {
        "ticker": "QQQ",
        "name": "Invesco NASDAQ-100 ETF",
        "asset_class": "Equities",
        "region": "United States",
        "country": "United States",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "100 largest non-financial innovative tech & growth leaders in the US.",
    },
    "IEF": {
        "ticker": "IEF",
        "name": "iShares 7-10 Year US Treasury Bond",
        "asset_class": "Fixed Income",
        "region": "United States",
        "country": "United States",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Intermediate-duration US government sovereign debt.",
    },
    "BND": {
        "ticker": "BND",
        "name": "Vanguard Total US Bond Market ETF",
        "asset_class": "Fixed Income",
        "region": "United States",
        "country": "United States",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Broad US investment-grade fixed income across sovereign and corporate bonds.",
    },
    "VNQ": {
        "ticker": "VNQ",
        "name": "Vanguard Real Estate ETF (US REITs)",
        "asset_class": "Real Estate / REITs",
        "region": "United States",
        "country": "United States",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Broad portfolio of US publicly traded equity REITs across sectors.",
    },
    "ACWI": {
        "ticker": "ACWI",
        "name": "iShares MSCI ACWI Global Equity ETF",
        "asset_class": "Equities",
        "region": "Global",
        "country": "Global",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Broad global equity exposure covering 23 developed and 24 emerging markets.",
    },
    "EEM": {
        "ticker": "EEM",
        "name": "iShares MSCI Emerging Markets ETF",
        "asset_class": "Equities",
        "region": "Emerging Markets",
        "country": "Global Emerging",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Large and mid-cap companies across 24 emerging market economies.",
    },
    "BNDX": {
        "ticker": "BNDX",
        "name": "Vanguard Total International Bond ETF",
        "asset_class": "Fixed Income",
        "region": "Global",
        "country": "Global Ex-US",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Investment-grade sovereign and corporate debt outside the United States.",
    },
    "EWS": {
        "ticker": "EWS",
        "name": "iShares MSCI Singapore ETF",
        "asset_class": "Equities",
        "region": "Asia-Pacific",
        "country": "Singapore",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Singapore large and mid-cap public equity companies.",
    },
    "EWU": {
        "ticker": "EWU",
        "name": "iShares MSCI United Kingdom ETF",
        "asset_class": "Equities",
        "region": "Europe",
        "country": "United Kingdom",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "UK broad equity market benchmark.",
    },
    "EZU": {
        "ticker": "EZU",
        "name": "iShares MSCI Eurozone ETF",
        "asset_class": "Equities",
        "region": "Europe",
        "country": "Eurozone",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Large and mid-cap equities across Eurozone member countries.",
    },
    "EWA": {
        "ticker": "EWA",
        "name": "iShares MSCI Australia ETF",
        "asset_class": "Equities",
        "region": "Asia-Pacific",
        "country": "Australia",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Leading Australian public equity companies.",
    },
    "GLD": {
        "ticker": "GLD",
        "name": "SPDR Gold Shares ETF",
        "asset_class": "Commodities / Gold",
        "region": "Global",
        "country": "Global",
        "currency": "USD",
        "instrument_type": "ETF",
        "description": "Physically backed gold bullion trust for hedge and inflation diversification.",
    },
}

FX_TICKERS: Dict[str, str] = {
    "USD/MYR": "MYR=X",
    "SGD/MYR": "SGDMYR=X",
    "GBP/MYR": "GBPMYR=X",
    "EUR/MYR": "EURMYR=X",
    "AUD/MYR": "AUDMYR=X",
}


def get_universe_dataframe() -> pd.DataFrame:
    """Return formatted asset universe as a pandas DataFrame."""
    records = []
    for sym, data in ASSET_UNIVERSE.items():
        records.append({
            "Ticker": sym,
            "Asset Name": data["name"],
            "Asset Class": data["asset_class"],
            "Region": data["region"],
            "Country": data["country"],
            "Currency": data["currency"],
            "Instrument Type": data["instrument_type"],
            "Description": data["description"],
        })
    return pd.DataFrame(records)


def get_asset_info(ticker: str) -> Dict[str, Any]:
    """Retrieve metadata dictionary for a specific ticker."""
    return ASSET_UNIVERSE.get(ticker, {
        "ticker": ticker,
        "name": ticker,
        "asset_class": "Other",
        "region": "Global",
        "country": "Global",
        "currency": "USD",
        "instrument_type": "Unknown",
        "description": "Custom asset",
    })
