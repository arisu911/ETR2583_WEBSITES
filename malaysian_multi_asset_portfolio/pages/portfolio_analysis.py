"""
Portfolio Analysis Page — Detailed Wealth Growth, Rolling Returns, Calendar Matrices, and Rebalance Drift.
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.settings import CURRENCY_SYMBOLS
from src.returns import (
    compute_monthly_returns_matrix,
    compute_annual_returns_table,
)
from src.charts import (
    plot_cumulative_wealth,
    plot_monthly_returns_heatmap,
    apply_theme,
)
import plotly.graph_objects as go


def render_portfolio_analysis_page(
    portfolio_returns: pd.Series,
    portfolio_wealth: pd.Series,
    benchmark_wealth: pd.Series,
    drift_weights: pd.DataFrame,
    reporting_currency: str,
    portfolio_name: str
):
    sym = CURRENCY_SYMBOLS.get(reporting_currency, "RM")
    st.markdown(f"## 📈 Portfolio Deep-Dive: {portfolio_name}")
    st.caption(f"Historical multi-year trajectory, rolling return persistence, calendar heatmaps, and rebalancing drift.")

    if portfolio_returns.empty:
        st.warning("No returns data available.")
        return

    tab_growth, tab_monthly, tab_annual, tab_drift = st.tabs([
        "💰 Capital Wealth & Rolling Returns",
        "🗓️ Monthly Returns Heatmap",
        "📊 Annual Performance Breakdown",
        "⚖️ Rebalancing Weight Drift"
    ])

    with tab_growth:
        st.markdown("### 📈 Cumulative Capital Growth Trajectory")
        fig_wealth = plot_cumulative_wealth(portfolio_wealth, benchmark_wealth, currency_symbol=sym)
        st.plotly_chart(fig_wealth, use_container_width=True, key="analysis_wealth_chart")

        st.markdown("### 🔄 Rolling Compound Annualized Returns")
        st.caption("Trailing 60-day (~3M), 120-day (~6M), and 252-day (1Y) rolling annualized return persistence.")
        fig_roll = go.Figure()

        roll_60 = portfolio_returns.rolling(60).mean() * 252.0 * 100.0
        roll_120 = portfolio_returns.rolling(120).mean() * 252.0 * 100.0
        roll_252 = portfolio_returns.rolling(252).mean() * 252.0 * 100.0

        fig_roll.add_trace(go.Scatter(x=roll_60.index, y=roll_60, name="Rolling 60-Day (3M) Ann. Return", line=dict(color="#38bdf8", width=1.5)))
        fig_roll.add_trace(go.Scatter(x=roll_120.index, y=roll_120, name="Rolling 120-Day (6M) Ann. Return", line=dict(color="#f59e0b", width=1.6)))
        fig_roll.add_trace(go.Scatter(x=roll_252.index, y=roll_252, name="Rolling 252-Day (1Y) Ann. Return", line=dict(color="#10b981", width=2.0)))
        fig_roll.add_hline(y=0, line=dict(color="rgba(255,255,255,0.2)", width=1, dash="dash"))

        fig_roll.update_yaxes(title="Annualized Return (%)", ticksuffix="%")
        fig_roll.update_xaxes(title="Date")
        st.plotly_chart(apply_theme(fig_roll, "Rolling Annualized Return Horizons"), use_container_width=True, key="analysis_rolling_chart")

    with tab_monthly:
        st.markdown("### 🗓️ Calendar Month Return Heatmap (Jan–Dec)")
        st.caption("Month-by-month historical returns compounding across calendar years.")
        monthly_df = compute_monthly_returns_matrix(portfolio_returns)
        if not monthly_df.empty:
            fig_m = plot_monthly_returns_heatmap(monthly_df)
            st.plotly_chart(fig_m, use_container_width=True, key="analysis_monthly_heatmap")
            st.dataframe(monthly_df.style.format("{:+.2f}%", na_rep="—"), use_container_width=True)

            # Download CSV
            csv_m = monthly_df.to_csv().encode("utf-8")
            st.download_button(
                "📥 Download Monthly Returns CSV",
                data=csv_m,
                file_name=f"{portfolio_name.lower().replace(' ', '_')}_monthly_returns_{reporting_currency.lower()}.csv",
                mime="text/csv",
                key="download_monthly_csv_btn",
            )

    with tab_annual:
        st.markdown("### 📊 Annual Calendar Year Performance Table")
        annual_df = compute_annual_returns_table(portfolio_returns)
        if not annual_df.empty:
            cols_show = [
                "Year", "Annual Return", "Annualized Vol", "Max Drawdown",
                "Best Month", "Worst Month", "Positive Months", "Trading Days"
            ]
            st.dataframe(annual_df[cols_show], hide_index=True, use_container_width=True)

            csv_ann = annual_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Annual Performance CSV",
                data=csv_ann,
                file_name=f"{portfolio_name.lower().replace(' ', '_')}_annual_returns_{reporting_currency.lower()}.csv",
                mime="text/csv",
                key="download_annual_csv_btn",
            )

    with tab_drift:
        st.markdown("### ⚖️ Asset Allocation Weight Drift Over Time")
        st.caption("Tracks how market movements alter portfolio weight distributions prior to periodic rebalancing.")
        if not drift_weights.empty:
            fig_drift = go.Figure()
            for col in drift_weights.columns:
                fig_drift.add_trace(go.Scatter(
                    x=drift_weights.index,
                    y=drift_weights[col] * 100.0,
                    name=col,
                    mode="lines",
                    stackgroup="one",
                    hovertemplate=f"<b>{col}</b>: %{{y:.1f}}%<extra></extra>",
                ))
            fig_drift.update_yaxes(title="Portfolio Weight (%)", ticksuffix="%", range=[0, 100])
            fig_drift.update_xaxes(title="Historical Date")
            st.plotly_chart(apply_theme(fig_drift, "Historical Asset Weight Drift & Rebalancing Cycles"), use_container_width=True, key="analysis_drift_chart")
