"""
Correlation & Co-Movement Page — Multi-Asset Correlation Heatmap & Rolling Correlation Dynamics.
"""
import streamlit as st
import pandas as pd
import numpy as np

from src.statistics import (
    compute_correlation_matrix,
    compute_rolling_correlation,
)
from src.charts import (
    plot_correlation_heatmap,
    apply_theme,
)
import plotly.graph_objects as go


def render_correlation_page(
    asset_returns_df: pd.DataFrame
):
    st.markdown("## 🔗 Cross-Asset Correlation & Co-Movement")
    st.caption("Analyzing historical linear co-movement, diversification potential, and rolling correlation regimes.")

    if asset_returns_df.empty:
        st.warning("No asset returns data available.")
        return

    tab_heat, tab_roll = st.tabs([
        "🔥 Multi-Asset Correlation Heatmap",
        "📈 Rolling Pairwise Correlation Dynamics"
    ])

    with tab_heat:
        st.markdown("### 🗺️ Multi-Asset Pearson Correlation Heatmap")
        corr_matrix = compute_correlation_matrix(asset_returns_df, use_asset_names=True)
        fig_heat = plot_correlation_heatmap(corr_matrix)
        st.plotly_chart(fig_heat, use_container_width=True, key="correlation_heatmap_chart")

        st.markdown("### 📋 Correlation Matrix Table")
        try:
            st.dataframe(corr_matrix.style.format("{:.2f}").background_gradient(cmap="viridis", axis=None), use_container_width=True)
        except Exception:
            st.dataframe(corr_matrix.style.format("{:.2f}"), use_container_width=True)

        csv_corr = corr_matrix.to_csv().encode("utf-8")
        st.download_button(
            "📥 Download Correlation Matrix CSV",
            data=csv_corr,
            file_name="multi_asset_correlation_matrix.csv",
            mime="text/csv",
            key="download_correlation_matrix_csv_btn",
        )

    with tab_roll:
        st.markdown("### 🔄 Rolling Pairwise Asset Correlation")
        st.caption("Inspects how cross-market correlation evolves across time (e.g. rising correlation during crisis periods).")

        assets = list(asset_returns_df.columns)
        c1, c2, c3 = st.columns(3)
        with c1:
            asset_a = st.selectbox("Select Asset A:", options=assets, index=0, key="corr_select_asset_a")
        with c2:
            asset_b = st.selectbox("Select Asset B:", options=assets, index=min(1, len(assets) - 1), key="corr_select_asset_b")
        with c3:
            roll_win = st.selectbox("Rolling Horizon:", options=[20, 60, 120, 252], index=1, key="corr_select_rolling_win")

        if asset_a != asset_b:
            roll_corr = compute_rolling_correlation(asset_returns_df[asset_a], asset_returns_df[asset_b], window=roll_win)
            fig_rc = go.Figure()
            fig_rc.add_trace(go.Scatter(
                x=roll_corr.index,
                y=roll_corr,
                name=f"{roll_win}-Day Rolling Correlation",
                line=dict(color="#00f0ff", width=2.0),
                hovertemplate=f"Correlation: %{{y:.3f}}<extra></extra>",
            ))
            fig_rc.add_hline(y=0, line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dash"))
            fig_rc.update_yaxes(title="Correlation (r)", range=[-1.05, 1.05])
            fig_rc.update_xaxes(title="Historical Date")
            st.plotly_chart(apply_theme(fig_rc, f"Rolling {roll_win}-Day Correlation: {asset_a} vs {asset_b}"), use_container_width=True, key="rolling_pairwise_corr_chart")
        else:
            st.info("Select two different assets to calculate pairwise correlation.")
