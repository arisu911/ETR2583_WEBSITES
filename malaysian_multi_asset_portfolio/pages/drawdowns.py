"""
Drawdown Analytics Page — Underwater Curve, Decline Durations, Recovery Timelines, and Major Episodes.
"""
import streamlit as st
import pandas as pd
import numpy as np

from src.drawdowns import (
    compute_drawdown_series,
    compute_drawdown_episodes,
)
from src.charts import plot_underwater_drawdown


def render_drawdowns_page(
    portfolio_returns: pd.Series,
    portfolio_name: str
):
    st.markdown(f"## 📉 Drawdown & Stress History: {portfolio_name}")
    st.caption("Historical peak-to-trough drawdowns, duration of capital impairment, and recovery timelines.")

    if portfolio_returns.empty:
        st.warning("No returns data available.")
        return

    wealth, dd_series, max_dd = compute_drawdown_series(portfolio_returns)
    curr_dd = float(dd_series.iloc[-1]) if not dd_series.empty else 0.0
    avg_dd = float(dd_series[dd_series < 0].mean()) if (dd_series < 0).sum() > 0 else 0.0
    underwater_days_pct = float((dd_series < 0).sum() / len(dd_series) * 100.0) if len(dd_series) > 0 else 0.0

    # Top KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Maximum Historical Drawdown", f"{max_dd:.2f}%")
    c2.metric("Current Drawdown from Peak", f"{curr_dd:.2f}%")
    c3.metric("Average In-Drawdown Depth", f"{avg_dd:.2f}%")
    c4.metric("Days Below All-Time High", f"{underwater_days_pct:.1f}%")

    st.markdown("---")

    # Underwater Chart
    st.markdown("### 🌊 Historical Underwater Drawdown Chart")
    fig_dd = plot_underwater_drawdown(dd_series, title=f"{portfolio_name} Underwater Drawdown Curve")
    st.plotly_chart(fig_dd, use_container_width=True, key="drawdowns_underwater_chart")

    # Major Episodes Table
    st.markdown("### 📋 Top Historical Drawdown Episodes")
    st.caption("Identifies the deepest historical declines, dates of peak/trough, and duration required to fully recover capital.")

    df_ep = compute_drawdown_episodes(dd_series, top_n=6)
    if not df_ep.empty:
        cols_show = [
            "Max Drawdown", "Peak Date", "Trough Date", "Recovery Date",
            "Decline (Days)", "Recovery (Days)", "Total Duration"
        ]
        st.dataframe(df_ep[cols_show], hide_index=True, use_container_width=True)

        # Download CSV
        csv_dd = df_ep[cols_show].to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Drawdown Episodes CSV",
            data=csv_dd,
            file_name=f"{portfolio_name.lower().replace(' ', '_')}_drawdown_episodes.csv",
            mime="text/csv",
            key="download_drawdown_episodes_csv_btn",
        )
    else:
        st.info("No significant drawdown episodes detected in the selected period.")
