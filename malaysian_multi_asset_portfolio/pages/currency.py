"""
Currency Analysis Page — Multi-Currency Reporting (MYR, USD, SGD, GBP, EUR, AUD) & Compounding FX Return Attribution.
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.settings import SUPPORTED_CURRENCIES, CURRENCY_NAMES
from src.currency import (
    convert_prices_to_reporting_currency,
    summarize_fx_impact_table,
)
from src.returns import compute_cagr
from src.risk import compute_annualized_volatility
from src.drawdowns import compute_drawdown_series
from src.portfolio import simulate_portfolio
from src.charts import (
    plot_multi_currency_comparison,
    apply_theme,
)


def render_currency_page(
    weights: dict,
    price_matrix_local: pd.DataFrame,
    fx_matrix: pd.DataFrame,
    reporting_currency: str,
    portfolio_name: str,
    rebalance_freq: str = "Annual",
    transaction_cost: float = 0.0
):
    st.markdown(f"## 💱 Multi-Currency & FX Impact Analysis: {portfolio_name}")
    st.caption("Evaluating how exchange rate fluctuations alter the risk, return, and compounding experience of a Malaysian investor.")

    tab_multi, tab_attr = st.tabs([
        "🌐 Multi-Currency Performance Comparison",
        "🔍 Asset-Level FX Return Attribution"
    ])

    with tab_multi:
        st.markdown("### 📊 Portfolio Trajectory Across Major Global Currencies")
        st.caption("Simulates the exact same portfolio asset holdings converted into different reporting currencies.")

        multi_wealth_dict = {}
        curr_summary_rows = []

        for c in SUPPORTED_CURRENCIES:
            try:
                # Convert prices to currency c
                p_c = convert_prices_to_reporting_currency(price_matrix_local, fx_matrix, target_currency=c)
                r_c = p_c.pct_change().dropna(how="all")
                s_ret, s_w, _, _ = simulate_portfolio(
                    asset_returns_df=r_c,
                    weights=weights,
                    rebalance_freq=rebalance_freq,
                    transaction_cost=transaction_cost,
                    initial_capital=100000.0,
                )
                multi_wealth_dict[c] = s_w

                cagr_c = compute_cagr(s_ret)
                vol_c = compute_annualized_volatility(s_ret)
                _, _, max_dd_c = compute_drawdown_series(s_ret)
                tot_ret_c = float((s_w.iloc[-1] / s_w.iloc[0] - 1.0) * 100.0)

                curr_summary_rows.append({
                    "Reporting Currency": c,
                    "Currency Name": CURRENCY_NAMES.get(c, c),
                    "Final Value (Base 100k)": f"{s_w.iloc[-1]:,.0f}",
                    "Total Return": f"{tot_ret_c:+.2f}%",
                    "CAGR": f"{cagr_c * 100:.2f}%",
                    "Annualized Vol": f"{vol_c * 100:.2f}%",
                    "Max Drawdown": f"{max_dd_c:.2f}%",
                })
            except Exception:
                pass

        if multi_wealth_dict:
            df_multi_wealth = pd.DataFrame(multi_wealth_dict)
            fig_curr_comp = plot_multi_currency_comparison(df_multi_wealth)
            st.plotly_chart(fig_curr_comp, use_container_width=True, key="multi_currency_comparison_chart")

            st.markdown("### 📋 Multi-Currency Performance Table")
            df_curr_summary = pd.DataFrame(curr_summary_rows)
            st.dataframe(df_curr_summary, hide_index=True, use_container_width=True)

    with tab_attr:
        st.markdown(f"### 🔍 Asset-Level Currency Attribution (Reported in {reporting_currency})")
        st.caption("Decomposes each asset's total return into pure local price appreciation vs exchange rate gain/loss.")

        fx_summary_df = summarize_fx_impact_table(price_matrix_local, fx_matrix, target_currency=reporting_currency)
        if not fx_summary_df.empty:
            cols_show = [
                "Asset Symbol", "Asset Name", "Native Currency", "Reporting Currency",
                "Local Asset Return", "FX Effect", "Investor Return"
            ]
            st.dataframe(fx_summary_df[cols_show], hide_index=True, use_container_width=True)

            # Download FX Attribution CSV
            csv_fx = fx_summary_df[cols_show].to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download FX Attribution CSV",
                data=csv_fx,
                file_name=f"{portfolio_name.lower().replace(' ', '_')}_fx_attribution_{reporting_currency.lower()}.csv",
                mime="text/csv",
                key="download_fx_attribution_csv_btn",
            )

        st.markdown("---")
        st.info(
            "📐 **Compounding FX Attribution Methodology**:\n\n"
            "$$\\left(1 + R_{\\text{Investor}}\\right) = \\left(1 + R_{\\text{Local}}\\right) \\times \\left(1 + R_{\\text{FX}}\\right)$$\n\n"
            "$$R_{\\text{Investor}} = R_{\\text{Local}} + R_{\\text{FX}} + \\left(R_{\\text{Local}} \\times R_{\\text{FX}}\\right)$$\n\n"
            "Where **$R_{\\text{Local}}$** is the native currency asset performance, **$R_{\\text{FX}}$** is the exchange rate appreciation/depreciation against the reporting currency, "
            "and the interaction term captures cross-compounding."
        )
