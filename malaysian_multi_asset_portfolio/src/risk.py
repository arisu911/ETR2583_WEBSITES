"""
Institutional risk metrics and portfolio risk decomposition module:
- Annualized Volatility & Downside Deviation
- Sharpe, Sortino, and Calmar Ratios
- Historical Value-at-Risk (VaR) & Conditional VaR (Expected Shortfall) at 90%, 95%, 99%
- Marginal and Percentage Risk Contribution (w^T * Sigma * w decomposition)
- Diversification Ratio & Effective Number of Constituents (ENC)
"""
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np

from config.settings import DEFAULT_RISK_FREE_RATE, DEFAULT_CONFIDENCE_LEVEL
from src.returns import compute_cagr


def compute_annualized_volatility(
    returns_series: pd.Series,
    periods_per_year: int = 252
) -> float:
    """Calculate annualized standard deviation of daily returns."""
    clean_r = returns_series.dropna()
    if len(clean_r) < 2:
        return 0.0
    return float(clean_r.std() * np.sqrt(periods_per_year))


def compute_downside_deviation(
    returns_series: pd.Series,
    target_return: float = 0.0,
    periods_per_year: int = 252
) -> float:
    """Calculate annualized downside semi-deviation below a target return threshold."""
    clean_r = returns_series.dropna()
    if len(clean_r) < 2:
        return 0.0
    downside_diff = np.minimum(0.0, clean_r - (target_return / periods_per_year))
    downside_var = np.mean(downside_diff ** 2)
    return float(np.sqrt(downside_var) * np.sqrt(periods_per_year))


def compute_sharpe_ratio(
    returns_series: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sharpe Ratio: (CAGR - Risk-Free Rate) / Annualized Volatility.
    """
    cagr = compute_cagr(returns_series, periods_per_year=periods_per_year)
    vol = compute_annualized_volatility(returns_series, periods_per_year=periods_per_year)
    if vol <= 0:
        return 0.0
    return float((cagr - risk_free_rate) / vol)


def compute_sortino_ratio(
    returns_series: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sortino Ratio: (CAGR - Risk-Free Rate) / Downside Deviation.
    """
    cagr = compute_cagr(returns_series, periods_per_year=periods_per_year)
    down_dev = compute_downside_deviation(returns_series, target_return=0.0, periods_per_year=periods_per_year)
    if down_dev <= 0:
        return 0.0
    return float((cagr - risk_free_rate) / down_dev)


def compute_calmar_ratio(cagr: float, max_drawdown_pct: float) -> float:
    """Calculate Calmar Ratio: CAGR / abs(Max Drawdown)."""
    abs_dd = abs(max_drawdown_pct) / 100.0
    if abs_dd <= 0:
        return 0.0
    return float(cagr / abs_dd)


def compute_historical_var(
    returns_series: pd.Series,
    confidence: float = DEFAULT_CONFIDENCE_LEVEL
) -> float:
    """
    Calculate 1-day Historical Value at Risk (VaR) percentage at chosen confidence level.
    E.g. at 95% confidence, VaR is the 5th percentile of daily losses.
    """
    clean_r = returns_series.dropna()
    if len(clean_r) < 10:
        return 0.0
    percentile_level = (1.0 - confidence) * 100.0
    var_val = -np.percentile(clean_r, percentile_level)
    return float(var_val * 100.0)


def compute_historical_cvar(
    returns_series: pd.Series,
    confidence: float = DEFAULT_CONFIDENCE_LEVEL
) -> float:
    """
    Calculate 1-day Historical Conditional Value at Risk (CVaR / Expected Shortfall).
    The average loss on days exceeding the VaR threshold.
    """
    clean_r = returns_series.dropna()
    if len(clean_r) < 10:
        return 0.0
    percentile_level = (1.0 - confidence) * 100.0
    cutoff = np.percentile(clean_r, percentile_level)
    tail_losses = clean_r[clean_r <= cutoff]
    if len(tail_losses) == 0:
        return 0.0
    cvar_val = -tail_losses.mean()
    return float(cvar_val * 100.0)


def compute_risk_contributions(
    weights: Dict[str, float],
    asset_returns_df: pd.DataFrame,
    periods_per_year: int = 252
) -> pd.DataFrame:
    """
    Calculate Marginal Risk Contribution (MRC) and Percentage Risk Contribution (PRC)
    for each asset in the portfolio using covariance matrix w^T * Sigma * w.

    Returns DataFrame:
    [Ticker, Asset Name, Weight %, Asset Vol %, Risk Contribution %, Risk Share %]
    """
    from src.asset_universe import get_asset_info

    valid_assets = [col for col in weights.keys() if col in asset_returns_df.columns and weights[col] > 0]
    if not valid_assets:
        return pd.DataFrame()

    total_w = sum(weights[c] for c in valid_assets)
    w = np.array([weights[c] / total_w for c in valid_assets])

    cov_matrix = asset_returns_df[valid_assets].cov().values * periods_per_year
    port_var = float(w.T @ cov_matrix @ w)
    port_vol = np.sqrt(port_var) if port_var > 0 else 1e-6

    # Marginal Risk Contribution = (Sigma @ w) / port_vol
    mrc = (cov_matrix @ w) / port_vol
    # Absolute Risk Contribution = w * mrc
    rc = w * mrc
    # Percentage Risk Contribution = rc / port_vol * 100
    prc = (rc / port_vol) * 100.0

    asset_vols = np.sqrt(np.diag(cov_matrix)) * 100.0

    records = []
    for i, col in enumerate(valid_assets):
        info = get_asset_info(col)
        records.append({
            "Ticker": col,
            "Asset Name": info.get("name", col),
            "Asset Class": info.get("asset_class", "Other"),
            "Weight %": w[i] * 100.0,
            "Asset Volatility %": asset_vols[i],
            "Risk Contribution %": rc[i] * 100.0,
            "Risk Share %": prc[i],
        })

    df_rc = pd.DataFrame(records)
    return df_rc


def compute_diversification_metrics(
    weights: Dict[str, float],
    asset_returns_df: pd.DataFrame,
    periods_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate portfolio diversification metrics:
    - Number of assets (N)
    - Effective Number of Constituents (ENC = 1 / sum(w_i^2))
    - Diversification Ratio (DR = weighted sum of asset vols / portfolio vol)
    - Average pairwise correlation between portfolio assets
    """
    valid_assets = [col for col in weights.keys() if col in asset_returns_df.columns and weights[col] > 0]
    if not valid_assets:
        return {"n_assets": 0, "enc": 0.0, "diversification_ratio": 1.0, "avg_correlation": 0.0}

    total_w = sum(weights[c] for c in valid_assets)
    w = np.array([weights[c] / total_w for c in valid_assets])

    cov_matrix = asset_returns_df[valid_assets].cov().values * periods_per_year
    corr_matrix = asset_returns_df[valid_assets].corr().values

    port_var = float(w.T @ cov_matrix @ w)
    port_vol = np.sqrt(port_var) if port_var > 0 else 1e-6

    asset_vols = np.sqrt(np.diag(cov_matrix))
    weighted_vol = float(np.sum(w * asset_vols))

    # Diversification Ratio
    dr = weighted_vol / port_vol if port_vol > 0 else 1.0

    # Effective Number of Constituents (Herfindahl-Hirschman index inverse)
    enc = float(1.0 / np.sum(w ** 2)) if np.sum(w ** 2) > 0 else len(valid_assets)

    # Average off-diagonal pairwise correlation
    if len(valid_assets) > 1:
        mask = ~np.eye(len(valid_assets), dtype=bool)
        avg_corr = float(np.mean(corr_matrix[mask]))
    else:
        avg_corr = 1.0

    return {
        "n_assets": len(valid_assets),
        "enc": enc,
        "diversification_ratio": dr,
        "avg_correlation": avg_corr,
    }


def compute_comprehensive_risk_table(
    returns_series: pd.Series,
    max_dd_pct: float,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
) -> pd.DataFrame:
    """Generate risk summary table across all key risk & risk-adjusted metrics."""
    cagr = compute_cagr(returns_series)
    ann_vol = compute_annualized_volatility(returns_series)
    down_dev = compute_downside_deviation(returns_series)
    sharpe = compute_sharpe_ratio(returns_series, risk_free_rate=risk_free_rate)
    sortino = compute_sortino_ratio(returns_series, risk_free_rate=risk_free_rate)
    calmar = compute_calmar_ratio(cagr, max_dd_pct)
    var_90 = compute_historical_var(returns_series, confidence=0.90)
    var_95 = compute_historical_var(returns_series, confidence=0.95)
    var_99 = compute_historical_var(returns_series, confidence=0.99)
    cvar_95 = compute_historical_cvar(returns_series, confidence=0.95)

    records = [
        ("Annualized Volatility (Std Dev)", f"{ann_vol * 100:.2f}%", "Total risk / dispersion of returns"),
        ("Downside Deviation", f"{down_dev * 100:.2f}%", "Volatility of negative returns only"),
        ("Sharpe Ratio (Rf = {:.1f}%)".format(risk_free_rate * 100), f"{sharpe:.2f}", "Excess return per unit of total risk"),
        ("Sortino Ratio (Rf = {:.1f}%)".format(risk_free_rate * 100), f"{sortino:.2f}", "Excess return per unit of downside risk"),
        ("Calmar Ratio", f"{calmar:.2f}", "CAGR / Maximum Drawdown"),
        ("Maximum Drawdown", f"{max_dd_pct:.2f}%", "Deepest historical peak-to-trough decline"),
        ("Historical 1-Day VaR (90%)", f"{var_90:.2f}%", "Loss threshold exceeded on 10% of days"),
        ("Historical 1-Day VaR (95%)", f"{var_95:.2f}%", "Loss threshold exceeded on 5% of days"),
        ("Historical 1-Day VaR (99%)", f"{var_99:.2f}%", "Loss threshold exceeded on 1% of days"),
        ("Historical 1-Day CVaR (95%)", f"{cvar_95:.2f}%", "Expected average loss when exceeding 95% VaR"),
    ]
    return pd.DataFrame(records, columns=["Risk Metric", "Value", "Description"])
