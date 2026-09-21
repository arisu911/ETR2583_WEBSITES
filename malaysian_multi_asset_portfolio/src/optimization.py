"""
Portfolio construction and historical optimization research module:
- Equal Weight Portfolio
- Minimum Volatility Portfolio (Quadratic Optimization)
- Maximum Sharpe Portfolio
- Equal Risk Contribution / Risk Parity Portfolio
- Efficient Frontier Simulation
"""
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np
from scipy.optimize import minimize

from config.settings import DEFAULT_RISK_FREE_RATE
from src.asset_universe import get_asset_info


def optimize_portfolio_weights(
    asset_returns_df: pd.DataFrame,
    objective: str = "max_sharpe",
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    min_weight: float = 0.0,
    max_weight: float = 0.40,
    periods_per_year: int = 252
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Compute optimal portfolio weights based on historical returns and covariance.

    Objectives:
    - 'equal_weight': Equal weight 1/N
    - 'min_volatility': Minimize historical annualized portfolio volatility
    - 'max_sharpe': Maximize historical annualized Sharpe Ratio
    - 'risk_parity': Equalize historical risk contributions across assets
    """
    clean_df = asset_returns_df.dropna()
    assets = list(clean_df.columns)
    n = len(assets)
    if n == 0:
        return {}, {}

    if objective == "equal_weight":
        eq_w = {a: 1.0 / n for a in assets}
        return eq_w, {"objective": "Equal Weight", "cagr": 0.0, "volatility": 0.0, "sharpe": 0.0}

    # Annualized mean returns and covariance matrix
    mean_daily = clean_df.mean().values
    ann_returns = mean_daily * periods_per_year
    cov_matrix = clean_df.cov().values * periods_per_year

    # Constraints: sum(w) = 1, min_w <= w_i <= max_w
    bounds = tuple((min_weight, max_weight) for _ in range(n))
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    init_w = np.full(n, 1.0 / n)

    if objective == "min_volatility":
        def _obj_vol(w):
            return np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))

        res = minimize(_obj_vol, init_w, method="SLSQP", bounds=bounds, constraints=constraints)
        opt_w = res.x if res.success else init_w

    elif objective == "max_sharpe":
        def _obj_sharpe(w):
            port_ret = np.dot(w, ann_returns)
            port_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
            if port_vol <= 1e-6:
                return 1e6
            sharpe = (port_ret - risk_free_rate) / port_vol
            return -sharpe  # Minimize negative Sharpe

        res = minimize(_obj_sharpe, init_w, method="SLSQP", bounds=bounds, constraints=constraints)
        opt_w = res.x if res.success else init_w

    elif objective == "risk_parity":
        def _obj_risk_parity(w):
            port_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
            if port_vol <= 1e-6:
                return 1e6
            mrc = np.dot(cov_matrix, w) / port_vol
            rc = w * mrc
            target_rc = port_vol / n
            # Sum of squared deviations from target equal risk share
            return np.sum((rc - target_rc) ** 2)

        res = minimize(_obj_risk_parity, init_w, method="SLSQP", bounds=bounds, constraints=constraints)
        opt_w = res.x if res.success else init_w

    else:
        opt_w = init_w

    # Clean small epsilon floats and renormalize to 1.0
    opt_w = np.maximum(0.0, opt_w)
    opt_w = opt_w / np.sum(opt_w)

    port_ret = float(np.dot(opt_w, ann_returns))
    port_vol = float(np.sqrt(np.dot(opt_w.T, np.dot(cov_matrix, opt_w))))
    sharpe = float((port_ret - risk_free_rate) / port_vol) if port_vol > 0 else 0.0

    weights_dict = {assets[i]: float(opt_w[i]) for i in range(n)}
    stats = {
        "objective": objective,
        "expected_return": port_ret,
        "volatility": port_vol,
        "sharpe": sharpe,
    }

    return weights_dict, stats


def generate_efficient_frontier_simulations(
    asset_returns_df: pd.DataFrame,
    num_portfolios: int = 1500,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252
) -> pd.DataFrame:
    """
    Generate Monte Carlo simulated portfolios across the asset universe to map the Efficient Frontier.
    """
    clean_df = asset_returns_df.dropna()
    assets = list(clean_df.columns)
    n = len(assets)
    if n < 2:
        return pd.DataFrame()

    ann_returns = clean_df.mean().values * periods_per_year
    cov_matrix = clean_df.cov().values * periods_per_year

    results = []
    np.random.seed(42)

    for _ in range(num_portfolios):
        w = np.random.dirichlet(np.ones(n), size=1)[0]
        port_ret = float(np.dot(w, ann_returns))
        port_vol = float(np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))))
        sharpe = (port_ret - risk_free_rate) / port_vol if port_vol > 0 else 0.0

        results.append({
            "Return %": port_ret * 100.0,
            "Volatility %": port_vol * 100.0,
            "Sharpe Ratio": sharpe,
        })

    return pd.DataFrame(results)
