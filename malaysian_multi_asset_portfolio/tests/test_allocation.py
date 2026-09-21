"""
Unit tests for portfolio weight validation and allocation exposure aggregation.
"""
import pandas as pd
import numpy as np
import pytest

from portfolios.presets import validate_portfolio_weights
from src.allocation import compute_allocation_breakdowns


def test_portfolio_weight_validation():
    """Verify weight sum checking."""
    valid_w = {"^KLSE": 0.50, "ACWI": 0.30, "0800EA.KL": 0.20}
    is_valid, total_pct, msg = validate_portfolio_weights(valid_w)
    assert is_valid is True
    assert total_pct == 100.0

    invalid_w = {"^KLSE": 0.50, "ACWI": 0.30}
    is_valid, total_pct, msg = validate_portfolio_weights(invalid_w)
    assert is_valid is False
    assert total_pct == 80.0


def test_allocation_breakdowns():
    """Verify exposure aggregation across asset classes and currencies."""
    w = {"^KLSE": 0.40, "SPY": 0.40, "0800EA.KL": 0.20}
    res = compute_allocation_breakdowns(w)

    df_class = res["by_asset_class"]
    eq_share = df_class[df_class["Asset Class"] == "Equities"]["Weight %"].iloc[0]
    fi_share = df_class[df_class["Asset Class"] == "Fixed Income"]["Weight %"].iloc[0]

    assert pytest.approx(eq_share, 0.01) == 80.0
    assert pytest.approx(fi_share, 0.01) == 20.0

    df_curr = res["by_currency"]
    myr_curr = df_curr[df_curr["Currency"] == "MYR"]["Weight %"].iloc[0]
    usd_curr = df_curr[df_curr["Currency"] == "USD"]["Weight %"].iloc[0]

    assert pytest.approx(myr_curr, 0.01) == 60.0  # 40% KLSE + 20% 0800EA.KL
    assert pytest.approx(usd_curr, 0.01) == 40.0  # 40% SPY
