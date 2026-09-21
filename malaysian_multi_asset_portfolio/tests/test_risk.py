"""
Unit tests for risk metrics, Sharpe/Sortino, VaR/CVaR, and risk contribution sum.
"""
import pandas as pd
import numpy as np
import pytest

from src.risk import (
    compute_annualized_volatility,
    compute_sharpe_ratio,
    compute_sortino_ratio,
    compute_historical_var,
    compute_historical_cvar,
    compute_risk_contributions,
    compute_diversification_metrics,
)


def test_volatility_and_sharpe():
    """Verify annualized volatility and Sharpe ratio on deterministic returns."""
    np.random.seed(42)
    # Daily returns with daily std ~ 1% -> Ann Vol ~ 1% * sqrt(252) ~ 15.87%
    rets = pd.Series(np.random.normal(0.0005, 0.01, 504))

    ann_vol = compute_annualized_volatility(rets)
    assert 0.14 <= ann_vol <= 0.18

    sharpe = compute_sharpe_ratio(rets, risk_free_rate=0.03)
    assert isinstance(sharpe, float)


def test_risk_contributions_sum_to_100_percent():
    """Verify that percentage risk contributions (PRC) sum to exactly 100%."""
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    np.random.seed(42)
    returns_df = pd.DataFrame({
        "Asset1": np.random.randn(100) * 0.01,
        "Asset2": np.random.randn(100) * 0.015,
        "Asset3": np.random.randn(100) * 0.005,
    }, index=dates)

    weights = {"Asset1": 0.40, "Asset2": 0.40, "Asset3": 0.20}
    df_rc = compute_risk_contributions(weights, returns_df)

    assert not df_rc.empty
    total_prc = df_rc["Risk Share %"].sum()
    assert pytest.approx(total_prc, 0.01) == 100.0


def test_diversification_ratio():
    """Verify diversification ratio >= 1.0 for non-perfectly correlated assets."""
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    np.random.seed(42)
    returns_df = pd.DataFrame({
        "A": np.random.randn(100) * 0.01,
        "B": np.random.randn(100) * 0.01,
    }, index=dates)

    weights = {"A": 0.50, "B": 0.50}
    metrics = compute_diversification_metrics(weights, returns_df)

    assert metrics["diversification_ratio"] >= 1.0
    assert metrics["enc"] == 2.0
