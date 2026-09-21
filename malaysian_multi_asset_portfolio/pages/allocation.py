"""
Asset Allocation Page — Multi-Dimensional Exposure (Asset Class, Region, Country, Currency) & Risk Attribution.
"""
import streamlit as st
import pandas as pd
import numpy as np

from src.allocation import compute_allocation_breakdowns
from src.risk import compute_risk_contributions
from src.charts import (
    plot_allocation_donut,
    plot_risk_contribution_bars,
)


def render_allocation_page(
    weights: dict,
    asset_returns_df: pd.DataFrame,
    portfolio_name: str
):
    st.markdown(f"## 🥧 Asset Allocation & Risk Decomposition: {portfolio_name}")
    st.caption("Decomposing portfolio structure across asset classes, geographic regions, native currencies, and risk contributions.")

    alloc_res = compute_allocation_breakdowns(weights)
    if not alloc_res:
        st.warning("No allocation data available.")
        return

    tab_class, tab_geo, tab_curr, tab_risk = st.tabs([
        "📊 Asset Class Allocation",
        "🌍 Regional & Country Exposure",
        "💱 Currency Exposure",
        "⚡ Capital vs Risk Contribution"
    ])

    with tab_class:
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.markdown("### 🥧 Asset Class Exposure Breakdown")
            df_class = alloc_res["by_asset_class"]
            fig_donut = plot_allocation_donut(df_class, names_col="Asset Class", title="Asset Class Breakdown")
            st.plotly_chart(fig_donut, use_container_width=True, key="alloc_class_donut")

        with c2:
            st.markdown("### 📋 Asset Class Allocation Table")
            st.dataframe(
                df_class.style.format({"Weight %": "{:.2f}%"}),
                hide_index=True,
                use_container_width=True,
            )

        st.markdown("### 🔍 Individual Asset Holdings Detail")
        df_assets = alloc_res["by_asset"]
        st.dataframe(
            df_assets[["Ticker", "Asset Name", "Asset Class", "Region", "Currency", "Weight %"]].style.format({"Weight %": "{:.2f}%"}),
            hide_index=True,
            use_container_width=True,
        )

    with tab_geo:
        c_reg, c_cntry = st.columns(2)
        with c_reg:
            st.markdown("### 🌐 Regional Exposure Breakdown")
            df_region = alloc_res["by_region"]
            fig_reg = plot_allocation_donut(df_region, names_col="Region", title="Geographic Region Exposure")
            st.plotly_chart(fig_reg, use_container_width=True, key="alloc_region_donut")
            st.dataframe(df_region.style.format({"Weight %": "{:.2f}%"}), hide_index=True, use_container_width=True)

        with c_cntry:
            st.markdown("### 🗺️ Country Exposure Breakdown")
            df_country = alloc_res["by_country"]
            fig_cntry = plot_allocation_donut(df_country, names_col="Country", title="Country Exposure")
            st.plotly_chart(fig_cntry, use_container_width=True, key="alloc_country_donut")
            st.dataframe(df_country.style.format({"Weight %": "{:.2f}%"}), hide_index=True, use_container_width=True)

    with tab_curr:
        c_curr_chart, c_curr_tbl = st.columns([1.2, 1])
        with c_curr_chart:
            st.markdown("### 💱 Native Currency Exposure")
            st.caption("Measures what percentage of portfolio assets are denominated in foreign currencies vs domestic MYR.")
            df_currency = alloc_res["by_currency"]
            fig_curr = plot_allocation_donut(df_currency, names_col="Currency", title="Denominated Currency Breakdown")
            st.plotly_chart(fig_curr, use_container_width=True, key="alloc_currency_donut")

        with c_curr_tbl:
            st.markdown("### 📋 Currency Exposure Table")
            st.dataframe(df_currency.style.format({"Weight %": "{:.2f}%"}), hide_index=True, use_container_width=True)

            myr_exp = df_currency[df_currency["Currency"] == "MYR"]["Weight %"].sum() if "MYR" in df_currency["Currency"].values else 0.0
            foreign_exp = 100.0 - myr_exp
            st.info(f"**Domestic MYR Exposure**: `{myr_exp:.1f}%`\n\n**Total Foreign Currency Exposure**: `{foreign_exp:.1f}%`")

    with tab_risk:
        st.markdown("### ⚡ Capital Weight vs Risk Contribution Share")
        st.caption("Answers the core research question: *'Which assets are actually driving portfolio risk?'*")

        df_rc = compute_risk_contributions(weights, asset_returns_df)
        if not df_rc.empty:
            fig_rc = plot_risk_contribution_bars(df_rc)
            st.plotly_chart(fig_rc, use_container_width=True, key="alloc_risk_contrib_bars")

            st.dataframe(
                df_rc[["Ticker", "Asset Name", "Asset Class", "Weight %", "Asset Volatility %", "Risk Contribution %", "Risk Share %"]].style.format({
                    "Weight %": "{:.2f}%",
                    "Asset Volatility %": "{:.2f}%",
                    "Risk Contribution %": "{:.2f}%",
                    "Risk Share %": "{:.2f}%",
                }),
                hide_index=True,
                use_container_width=True,
            )

    # Download Allocation CSV
    csv_alloc = alloc_res["by_asset"].to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Asset Allocation Breakdown CSV",
        data=csv_alloc,
        file_name=f"{portfolio_name.lower().replace(' ', '_')}_allocation.csv",
        mime="text/csv",
        key="download_allocation_csv_btn",
    )
