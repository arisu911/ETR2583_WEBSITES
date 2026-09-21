"""
Stress testing and scenario simulation module:
- Predefined hypothetical shocks (Global Equity Crash, Rate Shock, MYR Weakening, Global Risk-Off)
- Custom shock scenario builder
- Historical crisis replay (COVID-19 Crash 2020, 2022 Inflation & Rate Hike Cycle)
"""
from typing import Dict, Any, Tuple, List, Optional
import pandas as pd
import numpy as np

from src.asset_universe import get_asset_info
from src.drawdowns import compute_drawdown_series

PREDEFINED_STRESS_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "Global Equity Crash": {
        "description": "Severe global market panic: -30% Global Equities, -25% Malaysia Equities, flight to bonds (+3%) and gold (+10%).",
        "asset_class_shocks": {
            "Equities": -0.30,
            "Fixed Income": 0.03,
            "Real Estate / REITs": -0.20,
            "Commodities / Gold": 0.10,
            "Cash / Money Market": 0.00,
        },
        "asset_specific_shocks": {
            "^KLSE": -0.25,
            "EWM": -0.25,
            "0800EA.KL": 0.03,
            "5180.KL": -0.18,
        },
    },
    "Interest Rate Shock": {
        "description": "Rapid global monetary tightening: Fixed income falls -8%, REITs drop -12%, equities fall -10%, gold gains +3%.",
        "asset_class_shocks": {
            "Equities": -0.10,
            "Fixed Income": -0.08,
            "Real Estate / REITs": -0.12,
            "Commodities / Gold": 0.03,
            "Cash / Money Market": 0.00,
        },
        "asset_specific_shocks": {},
    },
    "MYR Weakening Shock": {
        "description": "Significant Ringgit depreciation: USD +10%, SGD/GBP/EUR/AUD +6% vs MYR; domestic asset local prices unchanged.",
        "asset_class_shocks": {
            "Equities": 0.00,
            "Fixed Income": 0.00,
            "Real Estate / REITs": 0.00,
            "Commodities / Gold": 0.00,
            "Cash / Money Market": 0.00,
        },
        "currency_shocks_vs_myr": {
            "USD": 0.10,
            "SGD": 0.06,
            "GBP": 0.06,
            "EUR": 0.06,
            "AUD": 0.06,
            "MYR": 0.00,
        },
    },
    "Global Risk-Off Flight to Safety": {
        "description": "Broad risk aversion: Equities fall -20%, REITs -15%, sovereign bonds rally +5%, gold surges +8%.",
        "asset_class_shocks": {
            "Equities": -0.20,
            "Fixed Income": 0.05,
            "Real Estate / REITs": -0.15,
            "Commodities / Gold": 0.08,
            "Cash / Money Market": 0.00,
        },
        "asset_specific_shocks": {},
    },
}

HISTORICAL_CRISIS_PERIODS: Dict[str, Dict[str, str]] = {
    "COVID-19 Market Crash (2020)": {
        "start": "2020-02-19",
        "end": "2020-04-30",
        "description": "Global pandemic outbreak trigger, worldwide lockdowns, and rapid market drawdown.",
    },
    "2022 Global Rate Hike & Inflation Shock": {
        "start": "2022-01-03",
        "end": "2022-10-14",
        "description": "Simultaneous stock and bond decline driven by 40-year high inflation and aggressive central bank tightening.",
    },
    "2018 US-China Trade War Escalation": {
        "start": "2018-01-26",
        "end": "2018-12-24",
        "description": "Rising tariff tensions, emerging market FX volatility, and global equity pullback.",
    },
}


def simulate_hypothetical_scenario(
    weights: Dict[str, float],
    scenario_name: str = "Global Equity Crash",
    custom_class_shocks: Optional[Dict[str, float]] = None
) -> Tuple[float, pd.DataFrame]:
    """
    Simulate instantaneous portfolio impact under a hypothetical stress shock.
    Returns:
    - total_portfolio_impact_pct: float
    - asset_impact_df: DataFrame with asset-by-asset impact breakdown
    """
    total_w = sum(weights.values())
    if total_w <= 0:
        return 0.0, pd.DataFrame()

    scenario_cfg = PREDEFINED_STRESS_SCENARIOS.get(scenario_name, {})
    class_shocks = custom_class_shocks if custom_class_shocks is not None else scenario_cfg.get("asset_class_shocks", {})
    specific_shocks = scenario_cfg.get("asset_specific_shocks", {})
    curr_shocks = scenario_cfg.get("currency_shocks_vs_myr", {})

    records = []
    total_port_impact = 0.0

    for ticker, raw_w in weights.items():
        if raw_w <= 0:
            continue
        w = raw_w / total_w
        info = get_asset_info(ticker)
        a_class = info.get("asset_class", "Other")
        a_curr = info.get("currency", "USD")

        # Determine price shock
        if ticker in specific_shocks:
            p_shock = specific_shocks[ticker]
        else:
            p_shock = class_shocks.get(a_class, 0.0)

        # Determine currency shock
        fx_shock = curr_shocks.get(a_curr, 0.0)

        # Combined shock = (1 + p_shock) * (1 + fx_shock) - 1
        asset_combined_shock = (1.0 + p_shock) * (1.0 + fx_shock) - 1.0
        weighted_contribution = w * asset_combined_shock

        total_port_impact += weighted_contribution

        records.append({
            "Ticker": ticker,
            "Asset Name": info.get("name", ticker),
            "Asset Class": a_class,
            "Currency": a_curr,
            "Weight %": w * 100.0,
            "Local Price Shock %": p_shock * 100.0,
            "FX Movement %": fx_shock * 100.0,
            "Total Asset Shock %": asset_combined_shock * 100.0,
            "Portfolio Contribution %": weighted_contribution * 100.0,
        })

    df_impact = pd.DataFrame(records)
    return total_port_impact * 100.0, df_impact


def replay_historical_crisis(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    crisis_name: str = "COVID-19 Market Crash (2020)"
) -> Dict[str, Any]:
    """
    Evaluate actual historical performance of the portfolio vs benchmark during a known historical crisis window.
    """
    cfg = HISTORICAL_CRISIS_PERIODS.get(crisis_name)
    if not cfg:
        return {}

    start_dt = pd.to_datetime(cfg["start"])
    end_dt = pd.to_datetime(cfg["end"])

    sub_p = portfolio_returns[(portfolio_returns.index >= start_dt) & (portfolio_returns.index <= end_dt)]
    sub_b = benchmark_returns[(benchmark_returns.index >= start_dt) & (benchmark_returns.index <= end_dt)]

    if sub_p.empty:
        return {"error": "Date range outside available history."}

    cum_p = float((1.0 + sub_p).cumprod().iloc[-1] - 1.0) * 100.0
    cum_b = float((1.0 + sub_b).cumprod().iloc[-1] - 1.0) * 100.0 if not sub_b.empty else 0.0

    _, _, max_dd_p = compute_drawdown_series(sub_p)
    _, _, max_dd_b = compute_drawdown_series(sub_b)

    worst_day_p = float(sub_p.min()) * 100.0
    worst_day_b = float(sub_b.min()) * 100.0 if not sub_b.empty else 0.0

    vol_p = float(sub_p.std() * np.sqrt(252)) * 100.0
    vol_b = float(sub_b.std() * np.sqrt(252)) * 100.0 if not sub_b.empty else 0.0

    return {
        "Crisis Name": crisis_name,
        "Period": f"{cfg['start']} to {cfg['end']}",
        "Description": cfg["description"],
        "Portfolio Return %": cum_p,
        "Benchmark Return %": cum_b,
        "Portfolio Max Drawdown %": max_dd_p,
        "Benchmark Max Drawdown %": max_dd_b,
        "Portfolio Worst Day %": worst_day_p,
        "Benchmark Worst Day %": worst_day_b,
        "Portfolio Volatility %": vol_p,
        "Benchmark Volatility %": vol_b,
    }
