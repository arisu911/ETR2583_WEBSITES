"""
Portfolio performance evaluation and cross-model comparison module.
Generates multi-portfolio comparison matrices across CAGR, Volatility, Sharpe, Drawdown, and Calmar ratios.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from config.settings import DEFAULT_RISK_FREE_RATE
from src.returns import compute_cagr, compute_wealth_index
from src.risk import (
    compute_annualized_volatility,
    compute_sharpe_ratio,
    compute_sortino_ratio,
    compute_calmar_ratio,
    compute_historical_var,
    compute_historical_cvar,
)
from src.drawdowns import compute_drawdown_series
from src.portfolio import simulate_portfolio
from portfolios.presets import MODEL_PORTFOLIOS


def evaluate_single_portfolio_performance(
    returns_series: pd.Series,
    name: str = "Portfolio",
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
) -> Dict[str, Any]:
    """Calculate executive performance & risk summary for a single return series."""
    clean_r = returns_series.dropna()
    if clean_r.empty:
        return {}

    _, dd_series, max_dd = compute_drawdown_series(clean_r)
    cagr = compute_cagr(clean_r)
    ann_vol = compute_annualized_volatility(clean_r)
    sharpe = compute_sharpe_ratio(clean_r, risk_free_rate=risk_free_rate)
    sortino = compute_sortino_ratio(clean_r, risk_free_rate=risk_free_rate)
    calmar = compute_calmar_ratio(cagr, max_dd)
    var_95 = compute_historical_var(clean_r, confidence=0.95)
    cvar_95 = compute_historical_cvar(clean_r, confidence=0.95)
    total_return = float((1.0 + clean_r).cumprod().iloc[-1] - 1.0) * 100.0

    return {
        "Portfolio Name": name,
        "Total Return %": total_return,
        "CAGR %": cagr * 100.0,
        "Annualized Vol %": ann_vol * 100.0,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Max Drawdown %": max_dd,
        "Calmar Ratio": calmar,
        "1-Day VaR (95%) %": var_95,
        "1-Day CVaR (95%) %": cvar_95,
        "Trading Days": len(clean_r),
    }


def compare_all_model_portfolios(
    asset_returns_df: pd.DataFrame,
    rebalance_freq: str = "Annual",
    transaction_cost: float = 0.0,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
) -> pd.DataFrame:
    """
    Simulate and generate side-by-side comparative performance table for all preset model portfolios:
    - Malaysian Conservative
    - Malaysian Balanced
    - Malaysian Growth
    - EPF-Inspired Model
    - PNB-Inspired Model
    - Global Balanced
    - Malaysian Asset Management Model
    """
    records = []
    for port_name, port_data in MODEL_PORTFOLIOS.items():
        try:
            s_ret, _, _, _ = simulate_portfolio(
                asset_returns_df=asset_returns_df,
                weights=port_data["weights"],
                rebalance_freq=rebalance_freq,
                transaction_cost=transaction_cost,
            )
            eval_res = evaluate_single_portfolio_performance(s_ret, name=port_name, risk_free_rate=risk_free_rate)
            records.append({
                "Portfolio": port_name,
                "Type": port_data.get("type", "Standard"),
                "Total Return": f"{eval_res['Total Return %']:+.2f}%",
                "CAGR": f"{eval_res['CAGR %']:.2f}%",
                "Annual Volatility": f"{eval_res['Annualized Vol %']:.2f}%",
                "Sharpe (Rf={:.1f}%)".format(risk_free_rate * 100): f"{eval_res['Sharpe Ratio']:.2f}",
                "Sortino": f"{eval_res['Sortino Ratio']:.2f}",
                "Max Drawdown": f"{eval_res['Max Drawdown %']:.2f}%",
                "Calmar": f"{eval_res['Calmar Ratio']:.2f}",
                "1D VaR (95%)": f"{eval_res['1-Day VaR (95%) %']:.2f}%",
                "_raw_cagr": eval_res["CAGR %"],
                "_raw_vol": eval_res["Annualized Vol %"],
                "_raw_sharpe": eval_res["Sharpe Ratio"],
                "_raw_max_dd": eval_res["Max Drawdown %"],
            })
        except Exception:
            pass

    return pd.DataFrame(records)
