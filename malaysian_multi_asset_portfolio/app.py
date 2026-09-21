"""
Malaysian Multi-Asset Portfolio Analytics
A MYR-Centric Investment Management Research Dashboard

Main Application Entry Point.
"""
from datetime import datetime, date
import zoneinfo
import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Malaysian Multi-Asset Portfolio Analytics",
    page_icon="🇲🇾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Permanently hide sidebar container, collapse button, and default multi-page navigation
st.markdown(
    """
    <style>
        [data-testid="stSidebar"], 
        [data-testid="collapsedControl"], 
        [data-testid="stSidebarNav"], 
        [data-testid="stSidebarNavItems"] {
            display: none !important;
        }
        section.main > div {
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Dark Quantitative Terminal CSS
st.markdown(
    """
    <style>
    /* Global styling */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Bar & Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #00f0ff !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #94a3b8 !important;
    }
    
    /* Tab Styling */
    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    button[aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom-color: #00f0ff !important;
    }
    
    /* Clock and Badges */
    .clock-badge {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.12), rgba(16, 185, 129, 0.12));
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 0.85rem;
        color: #f8fafc;
        display: inline-block;
    }
    .disclaimer-badge {
        background: rgba(239, 68, 68, 0.1);
        border-left: 3px solid #ef4444;
        padding: 6px 12px;
        font-size: 0.78rem;
        color: #fca5a5;
        border-radius: 4px;
        margin-top: 6px;
        margin-bottom: 6px;
    }
    .control-container {
        background-color: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Import internal engine modules
from config.settings import (
    BASE_CURRENCY,
    SUPPORTED_CURRENCIES,
    CURRENCY_SYMBOLS,
    CURRENCY_NAMES,
    TIMEZONE_STR,
    TIMEZONE_LABEL,
    DEFAULT_RISK_FREE_RATE,
    REBALANCING_FREQUENCIES,
    TRANSACTION_COST_PRESETS,
    DEFAULT_TRANSACTION_COST,
    DEFAULT_INITIAL_CAPITAL,
    GENERAL_DISCLAIMER,
    BENCHMARK_PRESETS,
)
from src.asset_universe import ASSET_UNIVERSE, get_asset_info
from src.data_loader import fetch_all_market_data
from src.data_cleaner import clean_and_align_market_data, generate_data_quality_report
from src.currency import convert_prices_to_reporting_currency
from src.returns import compute_asset_daily_returns
from src.portfolio import simulate_portfolio
from portfolios.presets import (
    MODEL_PORTFOLIOS,
    validate_portfolio_weights,
    normalize_weights,
)

# Import Page Views
from pages.overview import render_overview_page
from pages.portfolio_analysis import render_portfolio_analysis_page
from pages.allocation import render_allocation_page
from pages.risk import render_risk_page
from pages.currency import render_currency_page
from pages.performance import render_performance_page
from pages.stress_test import render_stress_test_page
from pages.drawdowns import render_drawdowns_page
from pages.correlation import render_correlation_page
from pages.optimization_page import render_optimization_page


# --- Data Caching Layer ---
@st.cache_data(ttl=3600, show_spinner=False)
def load_cached_market_data():
    raw_dict = fetch_all_market_data(start_date="2014-01-01", force_refresh=False)
    cleaned_dict = clean_and_align_market_data(raw_dict)
    return cleaned_dict


# Load market datasets
with st.spinner("🔄 Ingesting multi-asset market data and FX pairs..."):
    market_data = load_cached_market_data()

price_matrix_local = market_data["price_matrix_local"]
fx_matrix = market_data["fx_matrix"]
coverage_report = generate_data_quality_report(market_data)

# --- Top Header & Live MYT Clock ---
now_myt = datetime.now(zoneinfo.ZoneInfo(TIMEZONE_STR))
c_title, c_clock = st.columns([2.2, 1])

with c_title:
    st.markdown("# 🇲🇾 Malaysian Multi-Asset Portfolio Analytics")
    st.caption("A MYR-Centric Quantitative Portfolio Research & Investment Management Terminal")

with c_clock:
    st.markdown(
        f"""
        <div style="text-align: right;">
            <div class="clock-badge">
                <b>🕒 Market Time ({TIMEZONE_LABEL})</b><br>
                📅 {now_myt.strftime('%d %b %Y')}&nbsp;&nbsp;|&nbsp;&nbsp;<b>{now_myt.strftime('%H:%M:%S')}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Top Expandable Control Panel ---
with st.expander("🎛️ **Portfolio Controls, Currency Selection & Simulation Parameters**", expanded=True):
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)

    with col_c1:
        st.markdown("##### 💱 Reporting Currency")
        reporting_curr = st.selectbox(
            "Base / Reporting Currency:",
            options=SUPPORTED_CURRENCIES,
            index=0,  # Default MYR
            format_func=lambda c: f"{c} - {CURRENCY_NAMES.get(c, c)} ({CURRENCY_SYMBOLS.get(c, '')})",
            key="ctrl_reporting_curr",
        )

        st.markdown("##### 🎯 Benchmark Selection")
        bm_key = st.selectbox(
            "Comparative Benchmark:",
            options=list(BENCHMARK_PRESETS.keys()),
            index=0,  # FBM KLCI
            key="ctrl_bm_key",
        )
        bm_config = BENCHMARK_PRESETS[bm_key]

    with col_c2:
        st.markdown("##### 💼 Model Portfolio")
        portfolio_options = list(MODEL_PORTFOLIOS.keys()) + ["Custom Portfolio"]
        selected_port_name = st.selectbox(
            "Select Allocation Model:",
            options=portfolio_options,
            index=1,  # Default Malaysian Balanced
            key="ctrl_port_name",
        )

        st.markdown("##### ⚖️ Rebalancing Schedule")
        rebal_freq = st.selectbox(
            "Periodic Rebalancing:",
            options=REBALANCING_FREQUENCIES,
            index=4,  # Annual
            key="ctrl_rebal_freq",
        )

    with col_c3:
        st.markdown("##### ⚙️ Risk & Cost Assumptions")
        tc_choice = st.selectbox(
            "Transaction Cost (%):",
            options=list(TRANSACTION_COST_PRESETS.keys()),
            index=0,  # 0.00%
            key="ctrl_tc_choice",
        )
        tc_val = TRANSACTION_COST_PRESETS[tc_choice]

        rf_rate = st.number_input(
            "Risk-Free Rate (p.a. %):",
            min_value=0.0,
            max_value=15.0,
            value=DEFAULT_RISK_FREE_RATE * 100.0,
            step=0.25,
            key="ctrl_rf_rate",
        ) / 100.0

    with col_c4:
        st.markdown("##### 📅 Historical Date Horizon")
        min_avail_date = price_matrix_local.index[0].date()
        max_avail_date = price_matrix_local.index[-1].date()

        date_preset = st.radio(
            "Quick Horizon:",
            options=["1Y", "3Y", "5Y", "10Y", "Max"],
            index=3,
            horizontal=True,
            key="ctrl_date_preset",
        )

        if date_preset == "1Y":
            filter_start = max_avail_date - pd.DateOffset(years=1)
        elif date_preset == "3Y":
            filter_start = max_avail_date - pd.DateOffset(years=3)
        elif date_preset == "5Y":
            filter_start = max_avail_date - pd.DateOffset(years=5)
        elif date_preset == "10Y":
            filter_start = max_avail_date - pd.DateOffset(years=10)
        else:
            filter_start = min_avail_date

        sub_d1, sub_d2 = st.columns(2)
        start_date = sub_d1.date_input("Start Date", value=max(pd.to_datetime(filter_start).date(), min_avail_date), min_value=min_avail_date, max_value=max_avail_date, key="ctrl_start_date")
        end_date = sub_d2.date_input("End Date", value=max_avail_date, min_value=min_avail_date, max_value=max_avail_date, key="ctrl_end_date")

    # Custom Portfolio Sliders if selected
    if selected_port_name == "Custom Portfolio":
        st.markdown("---")
        st.markdown("##### 🎛️ Custom Asset Allocation Weights (%):")
        custom_cols = st.columns(4)
        custom_w = {}
        preset_ref = MODEL_PORTFOLIOS["Malaysian Balanced"]["weights"]
        for idx, (sym, meta) in enumerate(ASSET_UNIVERSE.items()):
            col_target = custom_cols[idx % 4]
            default_val = float(preset_ref.get(sym, 0.0) * 100.0)
            custom_w[sym] = col_target.slider(
                f"{meta['name']} ({sym}):",
                min_value=0.0,
                max_value=100.0,
                value=default_val,
                step=5.0,
                key=f"slider_custom_w_{sym}",
            ) / 100.0
        active_weights = custom_w
        is_valid, tot_pct, val_msg = validate_portfolio_weights(active_weights)
        if not is_valid:
            st.warning(f"⚠️ {val_msg} (Weights auto-normalized to 100%)")
            active_weights = normalize_weights(active_weights)
        port_disclaimer = None
    else:
        active_weights = MODEL_PORTFOLIOS[selected_port_name]["weights"]
        port_disclaimer = MODEL_PORTFOLIOS[selected_port_name].get("disclaimer")

    # Bottom Actions and Research Disclaimer in Control Bar
    col_act, col_disc = st.columns([1, 4])
    with col_act:
        if st.button("🔄 Reload Data Cache", key="btn_reload_cache"):
            st.cache_data.clear()
            st.rerun()
    with col_disc:
        st.markdown(
            """
            <div class="disclaimer-badge">
                <b>RESEARCH & EDUCATIONAL NATURE</b>: Not financial advice. Stylized models labeled 'EPF-Inspired' or 'PNB-Inspired' are academic approximations and do NOT represent actual institutional holdings or decisions.
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- Core Simulation Execution ---
# 1. Convert price matrix to user's selected reporting currency
price_matrix_reporting = convert_prices_to_reporting_currency(
    price_matrix_local,
    fx_matrix,
    target_currency=reporting_curr,
)

# 2. Slice to chosen date range
mask = (price_matrix_reporting.index.date >= start_date) & (price_matrix_reporting.index.date <= end_date)
price_sub = price_matrix_reporting.loc[mask]

# 3. Derive daily asset returns in reporting currency
asset_returns_df = compute_asset_daily_returns(price_sub)

# 4. Simulate active portfolio
port_returns, port_wealth, drift_w, sim_meta = simulate_portfolio(
    asset_returns_df=asset_returns_df,
    weights=active_weights,
    rebalance_freq=rebal_freq,
    transaction_cost=tc_val,
    initial_capital=DEFAULT_INITIAL_CAPITAL,
)

# 5. Simulate benchmark
if bm_config["type"] == "single_asset":
    bm_weights = {bm_config["ticker"]: 1.0}
else:
    bm_weights = bm_config["weights"]

bm_returns, bm_wealth, _, _ = simulate_portfolio(
    asset_returns_df=asset_returns_df,
    weights=bm_weights,
    rebalance_freq=rebal_freq,
    transaction_cost=0.0,
    initial_capital=DEFAULT_INITIAL_CAPITAL,
)

# --- Top Navigation Bar ---
nav_tabs = st.tabs([
    "📊 Overview",
    "📈 Portfolio Analysis",
    "🥧 Allocation & Exposure",
    "🛡️ Risk & Downside",
    "💱 Currency & FX Impact",
    "🏆 Performance & Benchmarks",
    "⚡ Stress Testing",
    "📉 Drawdowns",
    "🔗 Correlation",
    "🎯 Optimization Research",
])

with nav_tabs[0]:
    render_overview_page(
        portfolio_returns=port_returns,
        portfolio_wealth=port_wealth,
        benchmark_returns=bm_returns,
        benchmark_wealth=bm_wealth,
        weights=active_weights,
        asset_returns_df=asset_returns_df,
        reporting_currency=reporting_curr,
        portfolio_name=selected_port_name,
        portfolio_disclaimer=port_disclaimer,
        risk_free_rate=rf_rate,
        coverage_info=coverage_report,
    )

with nav_tabs[1]:
    render_portfolio_analysis_page(
        portfolio_returns=port_returns,
        portfolio_wealth=port_wealth,
        benchmark_wealth=bm_wealth,
        drift_weights=drift_w,
        reporting_currency=reporting_curr,
        portfolio_name=selected_port_name,
    )

with nav_tabs[2]:
    render_allocation_page(
        weights=active_weights,
        asset_returns_df=asset_returns_df,
        portfolio_name=selected_port_name,
    )

with nav_tabs[3]:
    render_risk_page(
        portfolio_returns=port_returns,
        weights=active_weights,
        asset_returns_df=asset_returns_df,
        portfolio_name=selected_port_name,
        risk_free_rate=rf_rate,
    )

with nav_tabs[4]:
    render_currency_page(
        weights=active_weights,
        price_matrix_local=price_matrix_local.loc[mask],
        fx_matrix=fx_matrix.loc[mask],
        reporting_currency=reporting_curr,
        portfolio_name=selected_port_name,
        rebalance_freq=rebal_freq,
        transaction_cost=tc_val,
    )

with nav_tabs[5]:
    render_performance_page(
        portfolio_returns=port_returns,
        benchmark_returns=bm_returns,
        asset_returns_df=asset_returns_df,
        portfolio_name=selected_port_name,
        benchmark_name=bm_config["name"],
        reporting_currency=reporting_curr,
        risk_free_rate=rf_rate,
        rebalance_freq=rebal_freq,
        transaction_cost=tc_val,
    )

with nav_tabs[6]:
    render_stress_test_page(
        portfolio_returns=port_returns,
        benchmark_returns=bm_returns,
        weights=active_weights,
        portfolio_name=selected_port_name,
        benchmark_name=bm_config["name"],
    )

with nav_tabs[7]:
    render_drawdowns_page(
        portfolio_returns=port_returns,
        portfolio_name=selected_port_name,
    )

with nav_tabs[8]:
    render_correlation_page(
        asset_returns_df=asset_returns_df,
    )

with nav_tabs[9]:
    render_optimization_page(
        asset_returns_df=asset_returns_df,
        current_portfolio_returns=port_returns,
        risk_free_rate=rf_rate,
    )
