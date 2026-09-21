"""
Portfolio Optimization Page — Minimum Volatility, Maximum Sharpe, Risk Parity, and Efficient Frontier.
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.settings import DEFAULT_RISK_FREE_RATE
from src.optimization import (
    optimize_portfolio_weights,
    generate_efficient_frontier_simulations,
)
from src.asset_universe import get_asset_info
from src.returns import compute_cagr
from src.risk import compute_annualized_volatility
from src.charts import plot_efficient_frontier


def render_optimization_page(
    asset_returns_df: pd.DataFrame,
    current_portfolio_returns: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
):
    st.markdown("## 🎯 Portfolio Optimization & Efficient Frontier Research")
    st.caption("Investigating historical quantitative portfolio construction frameworks: Min Volatility, Max Sharpe, and Risk Parity.")

    st.warning("⚠️ **Research Disclaimer**: Optimization solutions are mathematical formulations based purely on historical sample moments. They do not constitute investment advice or forecasts of future returns.")

    if asset_returns_df.empty:
        st.warning("No returns data available for optimization.")
        return

    # User inputs for optimization constraints
    c_lim1, c_lim2 = st.columns(2)
    with c_lim1:
        max_asset_w = st.slider("Maximum Individual Asset Weight (%):", 20, 100, 40, step=5, key="slider_opt_max_w") / 100.0
    with c_lim2:
        min_asset_w = st.slider("Minimum Individual Asset Weight (%):", 0, 10, 0, step=1, key="slider_opt_min_w") / 100.0

    # Calculate optimal weights for all 4 frameworks
    eq_w, eq_stats = optimize_portfolio_weights(asset_returns_df, objective="equal_weight", risk_free_rate=risk_free_rate)
    min_vol_w, min_vol_stats = optimize_portfolio_weights(asset_returns_df, objective="min_volatility", min_weight=min_asset_w, max_weight=max_asset_w, risk_free_rate=risk_free_rate)
    max_shp_w, max_shp_stats = optimize_portfolio_weights(asset_returns_df, objective="max_sharpe", min_weight=min_asset_w, max_weight=max_asset_w, risk_free_rate=risk_free_rate)
    rp_w, rp_stats = optimize_portfolio_weights(asset_returns_df, objective="risk_parity", min_weight=min_asset_w, max_weight=max_asset_w, risk_free_rate=risk_free_rate)

    tab_frontier, tab_weights, tab_models = st.tabs([
        "🌌 Efficient Frontier Simulation",
        "⚖️ Optimal Weights Comparison Table",
        "📖 Optimization Models Methodology"
    ])

    with tab_frontier:
        st.markdown("### 🌌 Historical Efficient Frontier & Risk-Return Plane")
        st.caption("1,500 Monte Carlo simulated multi-asset portfolios plotted on the Annualized Volatility vs Expected Return plane.")

        sim_df = generate_efficient_frontier_simulations(asset_returns_df, num_portfolios=1500, risk_free_rate=risk_free_rate)

        # Highlight points
        curr_vol = compute_annualized_volatility(current_portfolio_returns) * 100.0 if not current_portfolio_returns.empty else 10.0
        curr_ret = compute_cagr(current_portfolio_returns) * 100.0 if not current_portfolio_returns.empty else 8.0

        opt_points = {
            "Min Volatility": (min_vol_stats["volatility"] * 100.0, min_vol_stats["expected_return"] * 100.0),
            "Max Sharpe": (max_shp_stats["volatility"] * 100.0, max_shp_stats["expected_return"] * 100.0),
            "Current Portfolio": (curr_vol, curr_ret),
        }

        fig_ef = plot_efficient_frontier(sim_df, opt_points=opt_points)
        st.plotly_chart(fig_ef, use_container_width=True, key="optimization_efficient_frontier_chart")

        k1, k2, k3 = st.columns(3)
        k1.metric("Min Volatility Portfolio Vol", f"{min_vol_stats['volatility']*100:.2f}%", f"Return: {min_vol_stats['expected_return']*100:.2f}%")
        k2.metric("Max Sharpe Ratio", f"{max_shp_stats['sharpe']:.2f}", f"Return: {max_shp_stats['expected_return']*100:.2f}%")
        k3.metric("Current Portfolio Sharpe", f"{(curr_ret - risk_free_rate*100)/curr_vol:.2f}" if curr_vol > 0 else "—")

    with tab_weights:
        st.markdown("### ⚖️ Side-by-Side Target Allocation Weights Comparison")

        records = []
        for ticker in asset_returns_df.columns:
            info = get_asset_info(ticker)
            records.append({
                "Ticker": ticker,
                "Asset Name": info.get("name", ticker),
                "Asset Class": info.get("asset_class", "Other"),
                "Equal Weight": eq_w.get(ticker, 0.0) * 100.0,
                "Min Volatility": min_vol_w.get(ticker, 0.0) * 100.0,
                "Max Sharpe": max_shp_w.get(ticker, 0.0) * 100.0,
                "Risk Parity (ERC)": rp_w.get(ticker, 0.0) * 100.0,
            })

        df_weights_comp = pd.DataFrame(records)
        st.dataframe(
            df_weights_comp.style.format({
                "Equal Weight": "{:.1f}%",
                "Min Volatility": "{:.1f}%",
                "Max Sharpe": "{:.1f}%",
                "Risk Parity (ERC)": "{:.1f}%",
            }),
            hide_index=True,
            use_container_width=True,
        )

        # Download Weights CSV
        csv_w = df_weights_comp.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Optimization Weights CSV",
            data=csv_w,
            file_name="optimal_weights_comparison.csv",
            mime="text/csv",
            key="download_optimization_weights_csv_btn",
        )

    with tab_models:
        st.markdown("### 📖 Mathematical Foundations of the Optimization Frameworks")
        st.markdown(
            """
            1. **Equal Weight ($1/N$)**:
               - A simple, naive baseline allocation assigning equal capital ($1/N$) to each asset in the investable universe.
            2. **Minimum Volatility Portfolio**:
               - Solves $\\min_w w^T \\Sigma w$ subject to $\\sum w_i = 1$ and $w_{\\min} \\le w_i \\le w_{\\max}$.
               - Seeks the portfolio with the lowest possible historical variance without return targeting.
            3. **Maximum Sharpe Ratio (Tangency Portfolio)**:
               - Solves $\\max_w \\frac{w^T \\mu - r_f}{\\sqrt{w^T \\Sigma w}}$ subject to budget constraints.
               - Seeks the optimal risk-return trade-off relative to the risk-free rate ($r_f$).
            4. **Risk Parity (Equal Risk Contribution - ERC)**:
               - Solves for weights such that the percentage risk contribution ($PRC_i$) is equal across all assets ($PRC_i = 1/N$).
               - Prevents high-volatility assets (e.g. equities) from dominating total portfolio risk.
            """
        )
