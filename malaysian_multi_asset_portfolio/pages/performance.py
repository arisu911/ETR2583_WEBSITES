"""
Performance Page — Benchmark Comparison (Alpha, Beta, Information Ratio) & Cross-Model Portfolio Scatter.
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.settings import DEFAULT_RISK_FREE_RATE
from src.benchmarks import (
    compute_benchmark_comparison_metrics,
    format_benchmark_table,
)
from src.performance import compare_all_model_portfolios
from src.charts import (
    plot_risk_return_scatter,
    apply_theme,
)


def render_performance_page(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    asset_returns_df: pd.DataFrame,
    portfolio_name: str,
    benchmark_name: str,
    reporting_currency: str,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    rebalance_freq: str = "Annual",
    transaction_cost: float = 0.0
):
    st.markdown(f"## 🏆 Performance & Benchmark Analytics: {portfolio_name}")
    st.caption(f"Relative active performance vs **{benchmark_name}** and comparative risk-return benchmarking across all model portfolios.")

    tab_bm, tab_cross = st.tabs([
        f"🎯 Benchmark Comparison vs {benchmark_name}",
        "📊 Multi-Model Portfolio Benchmark Matrix"
    ])

    with tab_bm:
        st.markdown(f"### 📋 Active Benchmark Relative Performance ({portfolio_name} vs {benchmark_name})")
        bm_metrics = compute_benchmark_comparison_metrics(
            portfolio_returns,
            benchmark_returns,
            risk_free_rate=risk_free_rate
        )

        if bm_metrics:
            bm_table = format_benchmark_table(bm_metrics, benchmark_name=benchmark_name)
            st.dataframe(bm_table, hide_index=True, use_container_width=True)

            b1, b2, b3, b4 = st.columns(4)
            alpha_val = bm_metrics.get("Jensen's Alpha (α)", 0.0)
            b1.metric("Jensen's Alpha (α)", f"{alpha_val:+.2f}%")
            b2.metric("Beta to Benchmark (β)", f"{bm_metrics['Beta (β)']:.2f}x")
            b3.metric("Tracking Error", f"{bm_metrics['Tracking Error']:.2f}%")
            b4.metric("Information Ratio", f"{bm_metrics['Information Ratio']:.2f}")

    with tab_cross:
        st.markdown("### 📊 Cross-Model Portfolio Comparison Matrix")
        st.caption("Standardized performance across all 7 institutional and traditional asset allocation models.")

        comp_df = compare_all_model_portfolios(
            asset_returns_df=asset_returns_df,
            rebalance_freq=rebalance_freq,
            transaction_cost=transaction_cost,
            risk_free_rate=risk_free_rate,
        )

        if not comp_df.empty:
            # Risk Return Scatter
            fig_scatter = plot_risk_return_scatter(comp_df)
            st.plotly_chart(fig_scatter, use_container_width=True, key="performance_scatter_chart")

            # Table
            cols_show = [
                "Portfolio", "Type", "Total Return", "CAGR", "Annual Volatility",
                f"Sharpe (Rf={risk_free_rate*100:.1f}%)", "Sortino", "Max Drawdown", "Calmar", "1D VaR (95%)"
            ]
            st.dataframe(comp_df[cols_show], hide_index=True, use_container_width=True)

            # Download CSV
            csv_comp = comp_df[cols_show].to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Model Portfolio Comparison CSV",
                data=csv_comp,
                file_name=f"model_portfolio_comparison_{reporting_currency.lower()}.csv",
                mime="text/csv",
                key="download_performance_comparison_csv_btn",
            )
