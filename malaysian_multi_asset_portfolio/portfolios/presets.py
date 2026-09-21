"""
Predefined Model Portfolios for Malaysian Multi-Asset Portfolio Analytics.
Includes traditional asset allocations, institutional-style reference models (EPF/PNB inspired),
and helper functions to validate weights.
"""
from typing import Dict, Any, Tuple
import numpy as np

MODEL_PORTFOLIOS: Dict[str, Dict[str, Any]] = {
    "Malaysian Balanced": {
        "name": "Malaysian Balanced",
        "description": "Balanced domestic and global growth with sovereign fixed income stability.",
        "type": "Standard",
        "weights": {
            "^KLSE": 0.25,     # Malaysian Equities
            "ACWI": 0.25,      # Global Equities
            "0800EA.KL": 0.20, # Malaysian Fixed Income
            "BNDX": 0.15,      # Global Fixed Income
            "5180.KL": 0.05,   # Malaysian REIT
            "GLD": 0.05,       # Gold
            "MYR_CASH": 0.05,  # Malaysian Cash
        },
        "disclaimer": None,
    },
    "Malaysian Conservative": {
        "name": "Malaysian Conservative",
        "description": "Capital preservation focus with heavy domestic and global fixed income weighting.",
        "type": "Standard",
        "weights": {
            "0800EA.KL": 0.45, # Malaysian Fixed Income
            "BNDX": 0.15,      # Global Fixed Income
            "^KLSE": 0.15,     # Malaysian Equities
            "ACWI": 0.10,      # Global Equities
            "5180.KL": 0.05,   # Malaysian REIT
            "GLD": 0.05,       # Gold
            "MYR_CASH": 0.05,  # Malaysian Cash
        },
        "disclaimer": None,
    },
    "Malaysian Growth": {
        "name": "Malaysian Growth",
        "description": "High equity allocation targeting long-term capital appreciation.",
        "type": "Standard",
        "weights": {
            "ACWI": 0.40,      # Global Equities
            "^KLSE": 0.30,     # Malaysian Equities
            "0800EA.KL": 0.15, # Malaysian Fixed Income
            "5180.KL": 0.05,   # Malaysian REIT
            "GLD": 0.05,       # Gold
            "MYR_CASH": 0.05,  # Malaysian Cash
        },
        "disclaimer": None,
    },
    "EPF-Inspired Model": {
        "name": "EPF-Inspired Model",
        "description": "Educational model inspired by broad Malaysian Employees Provident Fund strategic asset allocation tiers.",
        "type": "Institutional-Inspired",
        "weights": {
            "0800EA.KL": 0.35, # Malaysian Fixed Income (MGS)
            "ACWI": 0.22,      # Global Equities
            "^KLSE": 0.20,     # Malaysian Public Equities
            "BNDX": 0.11,      # Global Fixed Income
            "5180.KL": 0.04,   # Malaysian Real Estate / REITs
            "VNQ": 0.04,       # Global/US Real Estate
            "MYR_CASH": 0.04,  # Money Market / Cash
        },
        "disclaimer": (
            "This model is an educational research approximation inspired by publicly disclosed broad asset-class disclosures. "
            "It does NOT represent the actual holdings, security selection, internal asset allocation, or investment decisions "
            "of the Employees Provident Fund (EPF) of Malaysia."
        ),
    },
    "PNB-Inspired Model": {
        "name": "PNB-Inspired Model",
        "description": "Educational model inspired by broad Permodalan Nasional Berhad domestic-centric equity allocations.",
        "type": "Institutional-Inspired",
        "weights": {
            "^KLSE": 0.55,     # Malaysian Equities Core
            "ACWI": 0.15,      # International Equities
            "0800EA.KL": 0.15, # Fixed Income / Sukuk
            "5180.KL": 0.08,   # Real Estate / Property
            "MYR_CASH": 0.07,  # Money Market / Cash
        },
        "disclaimer": (
            "This model is an educational approximation inspired by publicly disclosed broad PNB asset-class categories. "
            "It does NOT represent actual PNB unit trust holdings, proprietary private equity investments, or management strategies."
        ),
    },
    "Global Balanced": {
        "name": "Global Balanced",
        "description": "Internationally diversified multi-asset portfolio with US and global assets.",
        "type": "Standard",
        "weights": {
            "ACWI": 0.40,      # Global Equities
            "BNDX": 0.30,      # Global Aggregate Bonds
            "SPY": 0.10,       # US Equities
            "GLD": 0.10,       # Gold
            "VNQ": 0.05,       # US Real Estate
            "MYR_CASH": 0.05,  # Cash
        },
        "disclaimer": None,
    },
    "Malaysian Asset Management Model": {
        "name": "Malaysian Asset Management Model",
        "description": "Illustrative domestic asset-management fund model balancing domestic alpha and global diversification.",
        "type": "Institutional-Inspired",
        "weights": {
            "^KLSE": 0.35,     # Malaysian Equities
            "ACWI": 0.25,      # Global Equities
            "0800EA.KL": 0.20, # Malaysian Fixed Income
            "IEF": 0.10,       # US Treasuries
            "5180.KL": 0.05,   # Malaysian REITs
            "GLD": 0.05,       # Gold
        },
        "disclaimer": (
            "Illustrative Malaysian institutional asset-management model. Not affiliated with or representative of any actual "
            "Maybank Asset Management, external unit trust fund, or proprietary portfolio product."
        ),
    },
}


def get_model_portfolio(name: str) -> Dict[str, Any]:
    """Retrieve model portfolio dictionary by name, defaulting to Malaysian Balanced."""
    return MODEL_PORTFOLIOS.get(name, MODEL_PORTFOLIOS["Malaysian Balanced"])


def validate_portfolio_weights(weights: Dict[str, float]) -> Tuple[bool, float, str]:
    """
    Validate that user or preset portfolio weights sum exactly to 100% (within float tolerance).
    Returns (is_valid, total_sum_pct, message).
    """
    total = sum(weights.values())
    total_pct = round(total * 100.0, 2)
    if abs(total - 1.0) < 1e-4:
        return True, total_pct, "Valid (100.0%)"
    return False, total_pct, f"Portfolio weights must total 100.0% (Current: {total_pct:.1f}%)"


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Normalize weights dictionary so that positive weights sum to exactly 1.0."""
    total = sum(max(0.0, w) for w in weights.values())
    if total <= 0:
        n = len(weights)
        return {k: 1.0 / n for k in weights}
    return {k: max(0.0, w) / total for k, w in weights.items()}
