"""
Risk Analytics Page — Volatility, Downside Risk, Sharpe/Sortino/Calmar, VaR/CVaR, and Educational Concepts.
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.settings import DEFAULT_RISK_FREE_RATE
from src.risk import (
    compute_comprehensive_risk_table,
    compute_diversification_metrics,
    compute_historical_var,
    compute_historical_cvar,
)
from src.drawdowns import compute_drawdown_series
from src.charts import apply_theme
import plotly.graph_objects as go


def render_risk_page(
    portfolio_returns: pd.Series,
    weights: dict,
    asset_returns_df: pd.DataFrame,
    portfolio_name: str,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    confidence_level: float = 0.95
):
    st.markdown(f"## 🛡️ Risk & Downside Analytics: {portfolio_name}")
    st.caption("Quantitative risk evaluation, Value-at-Risk (VaR), Conditional VaR, and diversification metrics.")

    if portfolio_returns.empty:
        st.warning("No returns data available.")
        return

    _, _, max_dd = compute_drawdown_series(portfolio_returns)
    risk_table = compute_comprehensive_risk_table(portfolio_returns, max_dd_pct=max_dd, risk_free_rate=risk_free_rate)
    div_metrics = compute_diversification_metrics(weights, asset_returns_df)

    tab_risk, tab_tail, tab_div, tab_edu = st.tabs([
        "📋 Comprehensive Risk Metrics",
        "📉 Tail Risk & Return Distribution",
        "🔀 Portfolio Diversification Metrics",
        "📚 Educational Concept Library"
    ])

    with tab_risk:
        st.markdown("### 📋 Executive Risk Summary Table")
        st.dataframe(risk_table, hide_index=True, use_container_width=True)

        # Download Risk CSV
        csv_risk = risk_table.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Comprehensive Risk Metrics CSV",
            data=csv_risk,
            file_name=f"{portfolio_name.lower().replace(' ', '_')}_risk_metrics.csv",
            mime="text/csv",
            key="download_risk_metrics_csv_btn",
        )

    with tab_tail:
        st.markdown("### 📉 Empirical Return Distribution & Value-at-Risk (VaR)")
        st.caption("Histogram of daily returns with 95% Historical VaR and 95% Expected Shortfall (CVaR) cutoffs.")

        clean_r = portfolio_returns.dropna() * 100.0
        var_val = compute_historical_var(portfolio_returns, confidence=confidence_level)
        cvar_val = compute_historical_cvar(portfolio_returns, confidence=confidence_level)

        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=clean_r,
            nbinsx=50,
            marker=dict(color="rgba(56, 189, 248, 0.7)", line=dict(color="#00f0ff", width=1)),
            name="Daily Return Frequency",
            hovertemplate="Return Bin: %{x:.2f}%<br>Days Count: %{y}<extra></extra>",
        ))

        fig_dist.add_vline(x=-var_val, line=dict(color="#f59e0b", width=2, dash="dash"), annotation_text=f"{int(confidence_level*100)}% VaR: -{var_val:.2f}%", annotation_position="top left")
        fig_dist.add_vline(x=-cvar_val, line=dict(color="#ef4444", width=2, dash="dot"), annotation_text=f"{int(confidence_level*100)}% CVaR: -{cvar_val:.2f}%", annotation_position="bottom left")

        fig_dist.update_xaxes(title="Daily Return (%)", ticksuffix="%")
        fig_dist.update_yaxes(title="Observations Count")
        st.plotly_chart(apply_theme(fig_dist, "Daily Return Distribution with Tail Risk Cutoffs"), use_container_width=True, key="risk_distribution_chart")

        st.info(
            f"💡 **Interpretation**: At a **{int(confidence_level*100)}% confidence level**, the 1-day Historical VaR is **{var_val:.2f}%**. "
            f"On the 5% worst days exceeding this threshold, the expected average loss (**CVaR**) is **{cvar_val:.2f}%**."
        )

    with tab_div:
        st.markdown("### 🔀 Portfolio Diversification Metrics")
        st.caption("Quantitative measures evaluating portfolio breadth, concentration, and diversification benefit.")

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Constituent Assets (N)", f"{div_metrics['n_assets']}")
        d2.metric("Effective Assets (ENC)", f"{div_metrics['enc']:.1f}")
        d3.metric("Diversification Ratio (DR)", f"{div_metrics['diversification_ratio']:.2f}x")
        d4.metric("Avg Pairwise Correlation", f"{div_metrics['avg_correlation']:.2f}")

        st.markdown("---")
        st.markdown(
            """
            - **Effective Number of Constituents (ENC)**: The inverse Herfindahl index ($1 / \sum w_i^2$). If equal weighted across 5 assets, $ENC = 5.0$. Lower ENC indicates higher capital concentration in fewer assets.
            - **Diversification Ratio (DR)**: Ratio of weighted asset volatilities to actual portfolio volatility ($\sum w_i \sigma_i / \sigma_p$). Higher DR ($> 1.0$) demonstrates that uncorrelated asset co-movements actively dampen portfolio volatility.
            - **Average Pairwise Correlation ($\bar{\rho}$)**: Average cross-asset correlation. Lower values create greater non-linear risk reduction benefits.
            """
        )

    with tab_edu:
        st.markdown("### 📚 Educational Investment Concept Guide")
        st.caption("Concise explanations designed for students, researchers, and portfolio managers.")

        with st.expander("📌 What is Compound Annual Growth Rate (CAGR)?"):
            st.markdown("CAGR represents the annualized constant geometric rate of return required for an investment to grow from its initial balance to its final balance over multiple years.")

        with st.expander("📌 What is Annualized Volatility?"):
            st.markdown("Annualized Volatility measures the statistical dispersion of daily returns annualized using the standard convention ($\sigma \times \sqrt{252}$). It reflects overall price variation.")

        with st.expander("📌 What is the Sharpe Ratio vs Sortino Ratio?"):
            st.markdown(
                "**Sharpe Ratio** penalizes all volatility (both upward surges and downward drops). "
                "**Sortino Ratio** only penalizes harmful downward volatility below a target return, providing a clearer measure of downside risk-adjusted return."
            )

        with st.expander("📌 What is Value at Risk (VaR) and Conditional VaR (CVaR)?"):
            st.markdown(
                "**VaR** answers: *'What is the minimum loss expected on the 5% worst days?'* "
                "**CVaR (Expected Shortfall)** answers: *'When a tail loss worse than VaR occurs, what is the average expected loss magnitude?'*"
            )

        with st.expander("📌 What is Risk Contribution?"):
            st.markdown(
                "Capital allocation ($\%$) is not equal to risk allocation ($\%$). An asset with a small weight but high volatility or high correlation can drive the majority of total portfolio risk."
            )
