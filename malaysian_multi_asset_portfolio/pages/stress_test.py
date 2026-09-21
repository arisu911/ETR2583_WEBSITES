"""
Stress Testing Page — Macro Shock Scenarios, Custom Stress Simulator, and Historical Crisis Replay.
"""
import streamlit as st
import pandas as pd
import numpy as np

from src.stress_testing import (
    PREDEFINED_STRESS_SCENARIOS,
    HISTORICAL_CRISIS_PERIODS,
    simulate_hypothetical_scenario,
    replay_historical_crisis,
)


def render_stress_test_page(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    weights: dict,
    portfolio_name: str,
    benchmark_name: str
):
    st.markdown(f"## ⚡ Portfolio Stress Testing: {portfolio_name}")
    st.caption("Evaluating resilience under hypothetical macro shocks and historical market crises.")

    tab_predef, tab_custom, tab_crisis = st.tabs([
        "🌪️ Predefined Macro Shocks",
        "🎛️ Custom Scenario Builder",
        "📜 Historical Crisis Replay"
    ])

    with tab_predef:
        st.markdown("### 🌪️ Predefined Institutional Macro Stress Scenarios")
        scenario_choice = st.selectbox(
            "Select Macro Shock Scenario:",
            options=list(PREDEFINED_STRESS_SCENARIOS.keys()),
            index=0,
        )

        scenario_desc = PREDEFINED_STRESS_SCENARIOS[scenario_choice]["description"]
        st.info(f"**Scenario Narrative**: {scenario_desc}")

        tot_impact, df_impact = simulate_hypothetical_scenario(weights, scenario_name=scenario_choice)

        c_kpi, _ = st.columns([1, 2])
        with c_kpi:
            st.metric(
                "Estimated Portfolio Shock Impact",
                f"{tot_impact:+.2f}%",
                delta=f"{tot_impact:.2f}%",
                delta_color="inverse" if tot_impact < 0 else "normal",
            )

        st.markdown("### 📋 Asset-by-Asset Impact Breakdown")
        if not df_impact.empty:
            cols_show = [
                "Ticker", "Asset Name", "Asset Class", "Weight %",
                "Local Price Shock %", "FX Movement %", "Total Asset Shock %", "Portfolio Contribution %"
            ]
            st.dataframe(
                df_impact[cols_show].style.format({
                    "Weight %": "{:.2f}%",
                    "Local Price Shock %": "{:+.2f}%",
                    "FX Movement %": "{:+.2f}%",
                    "Total Asset Shock %": "{:+.2f}%",
                    "Portfolio Contribution %": "{:+.2f}%",
                }),
                hide_index=True,
                use_container_width=True,
            )

            # Download CSV
            csv_stress = df_impact[cols_show].to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Stress Test Results CSV",
                data=csv_stress,
                file_name=f"{portfolio_name.lower().replace(' ', '_')}_{scenario_choice.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                key="download_stress_test_csv_btn",
            )

    with tab_custom:
        st.markdown("### 🎛️ Custom Hypothetical Shock Builder")
        st.caption("Adjust percentage shocks for each broad asset class to simulate unique macroeconomic environments.")

        c1, c2, c3 = st.columns(3)
        with c1:
            eq_shock = st.slider("Equities Shock (%):", -50.0, 50.0, -20.0, step=5.0, key="slider_eq_shock") / 100.0
            fi_shock = st.slider("Fixed Income Shock (%):", -30.0, 30.0, 5.0, step=1.0, key="slider_fi_shock") / 100.0
        with c2:
            reit_shock = st.slider("Real Estate / REITs Shock (%):", -40.0, 40.0, -15.0, step=5.0, key="slider_reit_shock") / 100.0
            gold_shock = st.slider("Gold / Commodities Shock (%):", -30.0, 50.0, 10.0, step=5.0, key="slider_gold_shock") / 100.0
        with c3:
            cash_shock = st.slider("Cash / Money Market Shock (%):", -10.0, 10.0, 0.0, step=1.0, key="slider_cash_shock") / 100.0

        custom_shocks = {
            "Equities": eq_shock,
            "Fixed Income": fi_shock,
            "Real Estate / REITs": reit_shock,
            "Commodities / Gold": gold_shock,
            "Cash / Money Market": cash_shock,
        }

        cust_impact, df_cust_impact = simulate_hypothetical_scenario(
            weights,
            scenario_name="",
            custom_class_shocks=custom_shocks
        )

        st.metric(
            "Custom Scenario Portfolio Impact",
            f"{cust_impact:+.2f}%",
            delta=f"{cust_impact:.2f}%",
            delta_color="inverse" if cust_impact < 0 else "normal",
        )

        if not df_cust_impact.empty:
            st.dataframe(
                df_cust_impact[["Ticker", "Asset Name", "Asset Class", "Weight %", "Total Asset Shock %", "Portfolio Contribution %"]].style.format({
                    "Weight %": "{:.2f}%",
                    "Total Asset Shock %": "{:+.2f}%",
                    "Portfolio Contribution %": "{:+.2f}%",
                }),
                hide_index=True,
                use_container_width=True,
            )

    with tab_crisis:
        st.markdown("### 📜 Actual Historical Crisis Replay")
        st.caption("Inspects how the simulated portfolio and benchmark performed during documented historical market shocks.")

        crisis_choice = st.selectbox(
            "Select Historical Crisis Event:",
            options=list(HISTORICAL_CRISIS_PERIODS.keys()),
            index=0,
            key="crisis_event_selectbox",
        )

        crisis_res = replay_historical_crisis(
            portfolio_returns,
            benchmark_returns,
            crisis_name=crisis_choice,
        )

        if crisis_res and "error" not in crisis_res:
            st.info(f"**Period**: `{crisis_res['Period']}` — {crisis_res['Description']}")

            c_ret, c_dd, c_worst, c_vol = st.columns(4)
            c_ret.metric("Portfolio Return in Period", f"{crisis_res['Portfolio Return %']:+.2f}%", f"BM: {crisis_res['Benchmark Return %']:+.2f}%")
            c_dd.metric("Period Max Drawdown", f"{crisis_res['Portfolio Max Drawdown %']:.2f}%", f"BM: {crisis_res['Benchmark Max Drawdown %']:.2f}%")
            c_worst.metric("Worst Single Day", f"{crisis_res['Portfolio Worst Day %']:+.2f}%", f"BM: {crisis_res['Benchmark Worst Day %']:+.2f}%")
            c_vol.metric("Period Annualized Vol", f"{crisis_res['Portfolio Volatility %']:.2f}%", f"BM: {crisis_res['Benchmark Volatility %']:.2f}%")
        else:
            st.warning("Historical crisis window not covered by the current dataset date range.")
