"""
Overview Page — Executive KPI Cards, Cumulative Performance, Allocation, and Disclaimers.
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.settings import (
    CURRENCY_SYMBOLS,
    CURRENCY_NAMES,
    TIMEZONE_LABEL,
    GENERAL_DISCLAIMER,
)
from src.returns import compute_cagr, compute_wealth_index
from src.risk import (
    compute_annualized_volatility,
    compute_sharpe_ratio,
    compute_calmar_ratio,
    compute_risk_contributions,
)
from src.drawdowns import compute_drawdown_series
from src.allocation import compute_allocation_breakdowns
from src.charts import (
    plot_cumulative_wealth,
    plot_allocation_donut,
    plot_risk_contribution_bars,
)


def render_overview_page(
    portfolio_returns: pd.Series,
    portfolio_wealth: pd.Series,
    benchmark_returns: pd.Series,
    benchmark_wealth: pd.Series,
    weights: dict,
    asset_returns_df: pd.DataFrame,
    reporting_currency: str,
    portfolio_name: str,
    portfolio_disclaimer: str = None,
    risk_free_rate: float = 0.03,
    coverage_info: dict = None
):
    sym = CURRENCY_SYMBOLS.get(reporting_currency, "RM")

    # Header Title
    st.markdown("## 📊 Portfolio Executive Overview")
    st.caption(f"MYR-Centric Multi-Asset Performance & Risk Analytics. All timestamps formatted in **{TIMEZONE_LABEL}**.")

    # Institutional Model Disclaimer Banner if applicable
    if portfolio_disclaimer:
        st.warning(f"ℹ️ **Institutional Model Note**: {portfolio_disclaimer}")

    # Top Executive KPI Cards
    if portfolio_returns.empty:
        st.warning("No portfolio returns available for selected date range.")
        return

    cagr = compute_cagr(portfolio_returns)
    ann_vol = compute_annualized_volatility(portfolio_returns)
    sharpe = compute_sharpe_ratio(portfolio_returns, risk_free_rate=risk_free_rate)
    _, _, max_dd = compute_drawdown_series(portfolio_returns)
    calmar = compute_calmar_ratio(cagr, max_dd)
    curr_val = portfolio_wealth.iloc[-1] if not portfolio_wealth.empty else 100000.0
    tot_gain = (curr_val / portfolio_wealth.iloc[0] - 1.0) * 100.0 if not portfolio_wealth.empty else 0.0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric(f"Current Value ({reporting_currency})", f"{sym} {curr_val:,.0f}", f"{tot_gain:+.1f}% Total")
    k2.metric("CAGR (Compound Annual)", f"{cagr * 100:.2f}%")
    k3.metric("Annualized Volatility", f"{ann_vol * 100:.2f}%")
    k4.metric("Sharpe Ratio", f"{sharpe:.2f}", f"Rf: {risk_free_rate * 100:.1f}%")
    k5.metric("Maximum Drawdown", f"{max_dd:.2f}%")
    k6.metric("Calmar Ratio", f"{calmar:.2f}")

    st.markdown("---")

    # Cumulative Performance Chart
    st.markdown("### 📈 Cumulative Wealth Trajectory")
    st.caption(f"Historical capital growth of **{portfolio_name}** vs Benchmark reported in **{reporting_currency}**.")
    fig_wealth = plot_cumulative_wealth(portfolio_wealth, benchmark_wealth, currency_symbol=sym)
    st.plotly_chart(fig_wealth, use_container_width=True, key="overview_wealth_chart")

    # Multi-Column Breakdown: Allocation Donut + Risk Contribution Bars
    c_alloc, c_rc = st.columns(2)
    alloc_res = compute_allocation_breakdowns(weights)

    with c_alloc:
        st.markdown("### 🥧 Asset Class Allocation")
        if "by_asset_class" in alloc_res:
            fig_donut = plot_allocation_donut(
                alloc_res["by_asset_class"],
                names_col="Asset Class",
                title="Target Asset Class Exposure"
            )
            st.plotly_chart(fig_donut, use_container_width=True, key="overview_alloc_donut")

    with c_rc:
        st.markdown("### ⚡ Risk Contribution Decomposition")
        df_rc = compute_risk_contributions(weights, asset_returns_df)
        if not df_rc.empty:
            fig_rc = plot_risk_contribution_bars(df_rc)
            st.plotly_chart(fig_rc, use_container_width=True, key="overview_risk_contrib_bars")

    # Currency Exposure Donut & Research Summary
    c_curr_exp, c_sum = st.columns(2)

    with c_curr_exp:
        st.markdown("### 💱 Native Currency Exposure")
        if "by_currency" in alloc_res:
            fig_curr = plot_allocation_donut(
                alloc_res["by_currency"],
                names_col="Currency",
                title="Portfolio Exposure by Native Currency"
            )
            st.plotly_chart(fig_curr, use_container_width=True, key="overview_currency_donut")

    with c_sum:
        st.markdown("### 📝 Non-Predictive Research Summary")
        n_days = len(portfolio_returns)
        start_d = portfolio_returns.index[0].strftime("%d %b %Y")
        end_d = portfolio_returns.index[-1].strftime("%d %b %Y")

        st.info(
            f"Over the historical period from **{start_d}** to **{end_d}** ({n_days:,} trading days), "
            f"the **{portfolio_name}** generated a Compound Annual Growth Rate (CAGR) of **{cagr * 100:.2f}%** in **{reporting_currency}** "
            f"with an annualized volatility of **{ann_vol * 100:.2f}%** and a maximum peak-to-trough drawdown of **{max_dd:.2f}%**.\n\n"
            f"The historical Sharpe Ratio was **{sharpe:.2f}** (relative to a {risk_free_rate * 100:.1f}% risk-free rate). "
            f"This summary is strictly descriptive of historical data and does not represent a guarantee or forecast of future results."
        )

    # Transparency & Data Audit
    if coverage_info:
        st.markdown("---")
        with st.expander("🔍 Data Coverage & Integrity Disclosures", expanded=False):
            st.markdown(
                f"- **Data Range (MYT)**: `{coverage_info.get('start_date')}` to `{coverage_info.get('end_date')}` ({coverage_info.get('total_trading_days', 0):,} trading days)\n"
                f"- **Base Currency**: `{reporting_currency}` ({CURRENCY_NAMES.get(reporting_currency, reporting_currency)})\n"
                f"- **Primary Timezone**: `{TIMEZONE_LABEL}`\n"
                f"- **General Disclaimer**: {GENERAL_DISCLAIMER}"
            )
