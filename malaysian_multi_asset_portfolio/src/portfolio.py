"""
Portfolio simulation and rebalancing engine.
Simulates daily multi-asset portfolio performance with configurable rebalancing frequencies
(Buy & Hold, Monthly, Quarterly, Semi-Annual, Annual) and realistic transaction costs.
"""
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np


def simulate_portfolio(
    asset_returns_df: pd.DataFrame,
    weights: Dict[str, float],
    rebalance_freq: str = "Annual",
    transaction_cost: float = 0.0,
    initial_capital: float = 100000.0
) -> Tuple[pd.Series, pd.Series, pd.DataFrame, Dict[str, Any]]:
    """
    Simulate portfolio performance over time given target weights and rebalance schedule.

    Parameters:
    - asset_returns_df: DataFrame of daily asset returns in target reporting currency
    - weights: Dict mapping ticker to target weight (e.g. {'^KLSE': 0.25, 'ACWI': 0.25, ...})
    - rebalance_freq: 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly', 'Buy & Hold (No Rebalancing)'
    - transaction_cost: fee percentage applied to rebalanced turnover (e.g. 0.001 for 0.10%)
    - initial_capital: starting capital value (e.g. 100,000 RM)

    Returns:
    - portfolio_returns: pd.Series of daily percentage returns
    - portfolio_wealth: pd.Series of daily portfolio capital values
    - drift_weights: pd.DataFrame of actual daily asset weights
    - metadata: Dict with rebalance dates count, total costs paid, and turnover
    """
    # Filter to assets present in weights and dataframe
    valid_assets = [col for col in weights.keys() if col in asset_returns_df.columns and weights[col] > 0]
    if not valid_assets:
        raise ValueError("No valid assets matched between weights and returns dataframe.")

    # Normalize target weights for valid assets
    total_w = sum(weights[col] for col in valid_assets)
    target_w = np.array([weights[col] / total_w for col in valid_assets])

    returns_matrix = asset_returns_df[valid_assets].dropna().values
    dates = asset_returns_df[valid_assets].dropna().index
    n_days, n_assets = returns_matrix.shape

    # Rebalance schedule identification
    # Generate boolean mask of rebalance days
    rebalance_mask = np.zeros(n_days, dtype=bool)

    if rebalance_freq != "Buy & Hold (No Rebalancing)":
        s_series = pd.Series(1, index=dates)
        if rebalance_freq == "Monthly":
            rebalance_dates = set(s_series.resample("ME").last().index)
        elif rebalance_freq == "Quarterly":
            rebalance_dates = set(s_series.resample("QE").last().index)
        elif rebalance_freq == "Semi-Annual":
            rebalance_dates = set(s_series.resample("6ME").last().index)
        elif rebalance_freq == "Annual":
            rebalance_dates = set(s_series.resample("YE").last().index)
        else:
            rebalance_dates = set(s_series.resample("YE").last().index)

        for i, dt in enumerate(dates):
            if dt in rebalance_dates:
                rebalance_mask[i] = True

    # Simulation arrays
    asset_values = np.zeros((n_days, n_assets), dtype=float)
    portfolio_wealth = np.zeros(n_days, dtype=float)
    portfolio_returns = np.zeros(n_days, dtype=float)
    drift_weights = np.zeros((n_days, n_assets), dtype=float)

    # Initialize Day 0
    current_asset_vals = initial_capital * target_w
    current_port_val = initial_capital
    total_fees_paid = 0.0
    rebalance_count = 0

    for t in range(n_days):
        # 1. Grow assets by today's return
        day_rets = returns_matrix[t]
        current_asset_vals = current_asset_vals * (1.0 + day_rets)
        prev_port_val = current_port_val
        current_port_val = np.sum(current_asset_vals)

        # 2. Check if rebalancing at end of day t
        if rebalance_mask[t] and t < n_days - 1:
            target_asset_vals = current_port_val * target_w
            trades = np.abs(target_asset_vals - current_asset_vals)
            turnover = np.sum(trades) / 2.0
            fee = turnover * transaction_cost
            total_fees_paid += fee
            current_port_val -= fee
            current_asset_vals = current_port_val * target_w
            rebalance_count += 1

        # Record daily state
        asset_values[t] = current_asset_vals
        portfolio_wealth[t] = current_port_val
        portfolio_returns[t] = (current_port_val - prev_port_val) / prev_port_val if prev_port_val > 0 else 0.0
        drift_weights[t] = current_asset_vals / current_port_val if current_port_val > 0 else target_w

    s_returns = pd.Series(portfolio_returns, index=dates, name="Portfolio_Return")
    s_wealth = pd.Series(portfolio_wealth, index=dates, name="Portfolio_Wealth")
    df_weights = pd.DataFrame(drift_weights, index=dates, columns=valid_assets)

    meta = {
        "rebalance_freq": rebalance_freq,
        "transaction_cost_pct": transaction_cost * 100.0,
        "total_fees_paid": total_fees_paid,
        "rebalance_count": rebalance_count,
        "initial_capital": initial_capital,
        "final_capital": portfolio_wealth[-1] if len(portfolio_wealth) > 0 else initial_capital,
    }

    return s_returns, s_wealth, df_weights, meta
