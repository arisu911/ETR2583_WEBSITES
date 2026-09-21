"""
Unit tests for portfolio simulation, rebalancing, and transaction costs.
"""
import pandas as pd
import numpy as np
import pytest

from src.portfolio import simulate_portfolio


def test_toy_portfolio_weighted_returns():
    """
    Test 3-asset toy portfolio:
    Asset A: 50%
    Asset B: 30%
    Asset C: 20%
    Day 1 returns: A=+10%, B=+5%, C=-2%
    Expected Day 1 Portfolio Return = 0.50*0.10 + 0.30*0.05 + 0.20*(-0.02)
                                  = 0.05 + 0.015 - 0.004 = +0.061 (6.10%)
    """
    dates = pd.date_range("2024-01-01", periods=3, freq="B")
    returns_df = pd.DataFrame({
        "A": [0.10, 0.02, -0.01],
        "B": [0.05, -0.03, 0.04],
        "C": [-0.02, 0.01, 0.02],
    }, index=dates)

    weights = {"A": 0.50, "B": 0.30, "C": 0.20}

    s_ret, s_wealth, df_w, meta = simulate_portfolio(
        asset_returns_df=returns_df,
        weights=weights,
        rebalance_freq="Buy & Hold (No Rebalancing)",
        transaction_cost=0.0,
        initial_capital=100000.0
    )

    # Day 1 return check
    assert pytest.approx(s_ret.iloc[0], 1e-5) == 0.061
    assert pytest.approx(s_wealth.iloc[0], 0.01) == 106100.0


def test_rebalancing_with_transaction_costs():
    """Verify that rebalancing deducts turnover * transaction_cost correctly."""
    dates = pd.date_range("2022-01-01", periods=520, freq="B")
    np.random.seed(42)
    returns_df = pd.DataFrame({
        "A": np.random.randn(520) * 0.01,
        "B": np.random.randn(520) * 0.01,
    }, index=dates)

    weights = {"A": 0.60, "B": 0.40}

    # Monthly rebalancing with 0.10% transaction cost
    s_ret, s_wealth, df_w, meta = simulate_portfolio(
        asset_returns_df=returns_df,
        weights=weights,
        rebalance_freq="Monthly",
        transaction_cost=0.001,
        initial_capital=100000.0
    )

    assert meta["rebalance_count"] >= 10
    assert meta["total_fees_paid"] > 0.0
