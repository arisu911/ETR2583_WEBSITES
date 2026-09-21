"""
Global configuration and settings for Malaysian Multi-Asset Portfolio Analytics.
Centralizes currency definitions, timezone handling, asset universe metadata,
model portfolio presets, benchmark defaults, and analytical parameters.
"""
from pathlib import Path
from typing import Dict, Any, List

# Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DATA_DIR = DATA_DIR / "cache"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Currencies
BASE_CURRENCY = "MYR"
DEFAULT_BASE_CURRENCY = "MYR"
SUPPORTED_CURRENCIES = ["MYR", "USD", "SGD", "GBP", "EUR", "AUD"]

CURRENCY_SYMBOLS: Dict[str, str] = {
    "MYR": "RM",
    "USD": "$",
    "SGD": "S$",
    "GBP": "£",
    "EUR": "€",
    "AUD": "A$",
}

CURRENCY_NAMES: Dict[str, str] = {
    "MYR": "Malaysian Ringgit (MYR)",
    "USD": "United States Dollar (USD)",
    "SGD": "Singapore Dollar (SGD)",
    "GBP": "British Pound Sterling (GBP)",
    "EUR": "Euro (EUR)",
    "AUD": "Australian Dollar (AUD)",
}

# Timezone
TIMEZONE_STR = "Asia/Kuala_Lumpur"
PRIMARY_TIMEZONE = "Asia/Kuala_Lumpur"
TIMEZONE_LABEL = "MYT (UTC+8)"

# Risk-Free Rate Default (Bank Negara Malaysia OPR / Short MGS baseline)
DEFAULT_RISK_FREE_RATE = 0.030  # 3.00% annual
DEFAULT_INITIAL_CAPITAL = 100000.0
DEFAULT_TRANSACTION_COST = 0.0000

# Confidence Levels for Value-at-Risk (VaR / CVaR)
DEFAULT_CONFIDENCE_LEVEL = 0.95
SUPPORTED_CONFIDENCE_LEVELS = [0.90, 0.95, 0.99]

# Rebalancing Options
REBALANCING_FREQUENCIES: List[str] = [
    "Annual",
    "Semi-Annual",
    "Quarterly",
    "Monthly",
    "Buy & Hold (No Rebalancing)",
]

# Transaction Cost Presets
TRANSACTION_COST_PRESETS: Dict[str, float] = {
    "0.00% (Zero Fee Benchmark)": 0.0000,
    "0.05% (Institutional/Low Cost)": 0.0005,
    "0.10% (Standard Retail ETF)": 0.0010,
    "0.20% (Active / Emerging Market)": 0.0020,
}

# Period Presets
PERIOD_PRESETS: List[str] = ["1Y", "3Y", "5Y", "10Y", "Custom"]

# Benchmark Definitions
BENCHMARK_PRESETS: Dict[str, Dict[str, Any]] = {
    "FBM KLCI (Malaysian Equity)": {"name": "FBM KLCI", "type": "single_asset", "ticker": "^KLSE"},
    "S&P 500 (US Large Cap)": {"name": "S&P 500", "type": "single_asset", "ticker": "SPY"},
    "MSCI ACWI (Global Equity)": {"name": "MSCI ACWI", "type": "single_asset", "ticker": "ACWI"},
    "Global 60/40 (ACWI / BND)": {"name": "Global 60/40", "type": "multi_asset", "weights": {"ACWI": 0.60, "BND": 0.40}},
}

# Legal Disclaimers
GENERAL_DISCLAIMER = (
    "This research and educational dashboard is designed for academic, analytical, and exploratory "
    "portfolio modeling purposes. It does NOT constitute financial advice, an investment recommendation, "
    "a trading strategy, or a robo-advisory product. Historical performance is not indicative of future returns."
)

INSTITUTIONAL_DISCLAIMER = (
    "Educational research model inspired by publicly disclosed broad asset-class disclosures. "
    "It does NOT represent the actual holdings, internal security selection, portfolio weights, or "
    "investment decisions of EPF, PNB, Maybank, or any other financial institution."
)
