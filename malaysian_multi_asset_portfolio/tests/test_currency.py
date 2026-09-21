"""
Unit tests for multi-currency conversion and compounding FX attribution.
"""
import pandas as pd
import numpy as np
import pytest

from src.currency import (
    get_fx_rate_series,
    convert_prices_to_reporting_currency,
    compute_currency_attribution,
)


def test_currency_cross_rates():
    """Verify FX cross rate calculations from synthetic base pairs."""
    dates = pd.date_range("2024-01-01", periods=3, freq="B")
    fx_matrix = pd.DataFrame({
        "USD/MYR": [4.50, 4.60, 4.70],  # MYR per USD
        "SGD/MYR": [3.30, 3.35, 3.40],  # MYR per SGD
        "GBP/MYR": [5.70, 5.75, 5.80],  # MYR per GBP
        "EUR/MYR": [4.80, 4.85, 4.90],  # MYR per EUR
        "AUD/MYR": [2.90, 2.95, 3.00],  # MYR per AUD
    }, index=dates)

    # 1 USD in MYR on Day 0 = 4.50
    rate_usd_myr = get_fx_rate_series(fx_matrix, "USD", "MYR")
    assert rate_usd_myr.iloc[0] == 4.50

    # 1 MYR in USD on Day 0 = 1 / 4.50 = ~0.2222
    rate_myr_usd = get_fx_rate_series(fx_matrix, "MYR", "USD")
    assert pytest.approx(rate_myr_usd.iloc[0], 0.001) == 1.0 / 4.50

    # 1 USD in SGD on Day 0 = 4.50 / 3.30 = ~1.3636
    rate_usd_sgd = get_fx_rate_series(fx_matrix, "USD", "SGD")
    assert pytest.approx(rate_usd_sgd.iloc[0], 0.001) == 4.50 / 3.30


def test_compounding_currency_attribution():
    """
    Test exact compounding formula:
    (1 + R_investor) = (1 + R_local) * (1 + R_fx)
    Example:
    Local stock in USD gains +10.0% (R_local = 0.10)
    USD/MYR FX gains +2.0% (R_fx = 0.02)
    Expected Investor MYR Return = (1.10 * 1.02) - 1 = +12.20%
    """
    dates = pd.date_range("2024-01-01", periods=2, freq="B")
    # Day 0: Price = 100, FX = 4.00
    # Day 1: Price = 110 (+10%), FX = 4.08 (+2%)
    price_df = pd.DataFrame({"SPY": [100.0, 110.0]}, index=dates)
    fx_df = pd.DataFrame({"USD/MYR": [4.00, 4.08]}, index=dates)

    attr = compute_currency_attribution(price_df, fx_df, ticker="SPY", target_currency="MYR")
    assert not attr.empty

    r_local = attr["r_local"].iloc[0]
    r_fx = attr["r_fx"].iloc[0]
    r_inv = attr["r_investor"].iloc[0]

    assert pytest.approx(r_local, 1e-4) == 0.10
    assert pytest.approx(r_fx, 1e-4) == 0.02
    assert pytest.approx(r_inv, 1e-4) == 0.122
