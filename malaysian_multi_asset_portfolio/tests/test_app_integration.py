"""
Integration test validating full pipeline execution across all core analytical modules.
"""
import pandas as pd
import numpy as np
import pytest

from src.asset_universe import ASSET_UNIVERSE
from src.data_loader import generate_synthetic_cash_proxy
from src.currency import convert_prices_to_reporting_currency, summarize_fx_impact_table
from src.returns import compute_asset_daily_returns, compute_cagr
from src.portfolio import simulate_portfolio
from src.risk import compute_risk_contributions, compute_comprehensive_risk_table
from src.benchmarks import compute_benchmark_comparison_metrics
from src.stress_testing import simulate_hypothetical_scenario
from src.optimization import optimize_portfolio_weights
from portfolios.presets import MODEL_PORTFOLIOS


def test_full_pipeline_simulation():
    """Verify synthetic full-cycle portfolio pipeline without network dependencies."""
    dates = pd.date_range("2020-01-01", periods=500, freq="B")
    np.random.seed(42)

    # Mock prices for 5 universe assets
    tickers = ["^KLSE", "0800EA.KL", "SPY", "GLD", "MYR_CASH"]
    prices_data = {
        "^KLSE": (1.0 + np.random.randn(500) * 0.008).cumprod() * 1500.0,
        "0800EA.KL": (1.0 + np.random.randn(500) * 0.002).cumprod() * 1.15,
        "SPY": (1.0 + np.random.randn(500) * 0.01).cumprod() * 300.0,
        "GLD": (1.0 + np.random.randn(500) * 0.007).cumprod() * 140.0,
        "MYR_CASH": generate_synthetic_cash_proxy(dates, annual_rate=0.03).values,
    }
    price_df = pd.DataFrame(prices_data, index=dates)

    # Mock FX
    fx_data = {
        "USD/MYR": (1.0 + np.random.randn(500) * 0.003).cumprod() * 4.20,
        "SGD/MYR": (1.0 + np.random.randn(500) * 0.002).cumprod() * 3.10,
        "GBP/MYR": (1.0 + np.random.randn(500) * 0.003).cumprod() * 5.40,
        "EUR/MYR": (1.0 + np.random.randn(500) * 0.003).cumprod() * 4.70,
        "AUD/MYR": (1.0 + np.random.randn(500) * 0.004).cumprod() * 2.80,
    }
    fx_df = pd.DataFrame(fx_data, index=dates)

    # 1. Currency conversion to MYR
    p_converted = convert_prices_to_reporting_currency(price_df, fx_df, target_currency="MYR")
    assert p_converted.shape == price_df.shape

    # 2. Returns
    r_df = compute_asset_daily_returns(p_converted)
    assert len(r_df) == 499

    # 3. Simulate Malaysian Balanced portfolio
    weights = MODEL_PORTFOLIOS["Malaysian Balanced"]["weights"]
    s_ret, s_wealth, drift_w, meta = simulate_portfolio(
        asset_returns_df=r_df,
        weights=weights,
        rebalance_freq="Annual",
        transaction_cost=0.001,
        initial_capital=100000.0,
    )
    assert len(s_ret) == len(r_df)
    assert s_wealth.iloc[0] > 0

    # 4. Risk decomposition
    df_rc = compute_risk_contributions(weights, r_df)
    assert not df_rc.empty
    assert pytest.approx(df_rc["Risk Share %"].sum(), 0.01) == 100.0

    # 5. Stress Testing
    tot_impact, df_impact = simulate_hypothetical_scenario(weights, scenario_name="Global Equity Crash")
    assert isinstance(tot_impact, float)

    # 6. Optimization
    min_vol_w, _ = optimize_portfolio_weights(r_df, objective="min_volatility")
    assert pytest.approx(sum(min_vol_w.values()), 0.01) == 1.0
