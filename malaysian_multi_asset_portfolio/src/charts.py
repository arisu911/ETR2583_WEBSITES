"""
Interactive Plotly visualization module for Malaysian Multi-Asset Portfolio Analytics.
Follows modern quantitative terminal design standards:
- Dark slate/charcoal background (#0b0f19 / #111827)
- Vibrant institutional color palette (Cyan, Emerald, Amber, Crimson, Purple, Royal Blue)
- Formatted tooltips, clear units, and dynamic currency labels (RM, $, S$, £, €, A$)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Visual Styling Constants
BG_DARK = "#0b0f19"
BG_CARD = "#111827"
GRID_COLOR = "rgba(255, 255, 255, 0.08)"
TEXT_PRIMARY = "#f8fafc"
TEXT_MUTED = "#94a3b8"

COLOR_CYAN = "#00f0ff"
COLOR_GREEN = "#10b981"
COLOR_AMBER = "#f59e0b"
COLOR_RED = "#ef4444"
COLOR_PURPLE = "#a855f7"
COLOR_BLUE = "#3b82f6"

PALETTE = ["#00f0ff", "#10b981", "#f59e0b", "#a855f7", "#3b82f6", "#ec4899", "#14b8a6", "#f97316"]


def apply_theme(fig: go.Figure, title: str = "", height: int = 440) -> go.Figure:
    """Apply consistent dark financial terminal layout styling to Plotly figures."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=15, color=TEXT_PRIMARY, family="Inter, -apple-system, sans-serif"),
            x=0.01,
            y=0.96,
        ),
        height=height,
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_DARK,
        margin=dict(l=45, r=25, t=55, b=45),
        font=dict(color=TEXT_MUTED, family="Inter, -apple-system, sans-serif", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=TEXT_PRIMARY),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=False,
            showline=True,
            linecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_MUTED, size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=True,
            zerolinecolor="rgba(255, 255, 255, 0.15)",
            showline=True,
            linecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_MUTED, size=11),
        ),
        hovermode="x unified",
    )
    return fig


def plot_cumulative_wealth(
    portfolio_wealth: pd.Series,
    benchmark_wealth: Optional[pd.Series] = None,
    currency_symbol: str = "RM",
    title: str = "Cumulative Portfolio Wealth Growth"
) -> go.Figure:
    """Plot cumulative wealth index growth curve (Portfolio vs Benchmark)."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=portfolio_wealth.index,
        y=portfolio_wealth,
        name="Portfolio Value",
        line=dict(color=COLOR_CYAN, width=2.4),
        hovertemplate=f"Portfolio: {currency_symbol} %{{y:,.2f}}<extra></extra>",
    ))

    if benchmark_wealth is not None and not benchmark_wealth.empty:
        # Scale benchmark to same initial capital
        init_val = portfolio_wealth.iloc[0] if len(portfolio_wealth) > 0 else 100000.0
        bm_scaled = init_val * (benchmark_wealth / benchmark_wealth.iloc[0])
        fig.add_trace(go.Scatter(
            x=bm_scaled.index,
            y=bm_scaled,
            name="Benchmark",
            line=dict(color=TEXT_MUTED, width=1.6, dash="dash"),
            hovertemplate=f"Benchmark: {currency_symbol} %{{y:,.2f}}<extra></extra>",
        ))

    fig.update_yaxes(title=f"Capital Value ({currency_symbol})")
    fig.update_xaxes(title="Historical Date")
    return apply_theme(fig, title)


def plot_underwater_drawdown(
    drawdown_series: pd.Series,
    title: str = "Historical Drawdown (Underwater Curve)"
) -> go.Figure:
    """Plot underwater drawdown curve with max drawdown marker."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=drawdown_series.index,
        y=drawdown_series,
        name="Drawdown (%)",
        fill="tozeroy",
        fillcolor="rgba(239, 68, 68, 0.22)",
        line=dict(color=COLOR_RED, width=1.6),
        hovertemplate="Drawdown: %{y:.2f}%<extra></extra>",
    ))

    if not drawdown_series.empty:
        min_val = drawdown_series.min()
        min_idx = drawdown_series.idxmin()
        fig.add_annotation(
            x=min_idx,
            y=min_val,
            text=f"Max DD: {min_val:.2f}%",
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLOR_RED,
            ax=0,
            ay=-30,
            font=dict(color=TEXT_PRIMARY, size=11),
            bgcolor=BG_DARK,
            bordercolor=COLOR_RED,
            borderwidth=1,
        )

    fig.update_yaxes(title="Drawdown (%)", ticksuffix="%")
    fig.update_xaxes(title="Date")
    return apply_theme(fig, title)


def plot_allocation_donut(
    df_breakdown: pd.DataFrame,
    names_col: str,
    values_col: str = "Weight %",
    title: str = "Portfolio Allocation Breakdown"
) -> go.Figure:
    """Plot interactive donut chart for asset class, region, or currency exposures."""
    fig = go.Figure(data=[go.Pie(
        labels=df_breakdown[names_col],
        values=df_breakdown[values_col],
        hole=0.55,
        marker=dict(colors=PALETTE, line=dict(color=BG_DARK, width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color=TEXT_PRIMARY),
        hovertemplate="<b>%{label}</b><br>Weight: %{value:.1f}%<extra></extra>",
    )])

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=14, color=TEXT_PRIMARY),
            x=0.01,
            y=0.96,
        ),
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_DARK,
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
    )
    return fig


def plot_risk_contribution_bars(df_rc: pd.DataFrame) -> go.Figure:
    """Plot Capital Allocation Weight % vs Percentage Risk Contribution % side-by-side."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_rc["Asset Name"],
        y=df_rc["Weight %"],
        name="Capital Weight %",
        marker=dict(color=COLOR_CYAN),
        hovertemplate="Capital: %{y:.1f}%<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=df_rc["Asset Name"],
        y=df_rc["Risk Share %"],
        name="Risk Contribution %",
        marker=dict(color=COLOR_AMBER),
        hovertemplate="Risk Contribution: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(barmode="group", bargap=0.25)
    fig.update_yaxes(title="Percentage (%)", ticksuffix="%")
    fig.update_xaxes(title="Portfolio Asset", tickangle=-30)
    return apply_theme(fig, "Capital Allocation vs Risk Contribution Share (%)")


def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Plot multi-asset Pearson correlation heatmap."""
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns,
        y=corr_df.index,
        colorscale="Viridis",
        zmin=-0.2,
        zmax=1.0,
        colorbar=dict(title="Correlation (r)", len=0.8),
        hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="<b>Multi-Asset Historical Correlation Matrix</b>", font=dict(size=14, color=TEXT_PRIMARY)),
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_DARK,
        margin=dict(l=100, r=20, t=50, b=100),
        height=520,
        xaxis=dict(tickangle=-45, tickfont=dict(color=TEXT_MUTED, size=10)),
        yaxis=dict(tickfont=dict(color=TEXT_MUTED, size=10)),
    )
    return fig


def plot_monthly_returns_heatmap(monthly_df: pd.DataFrame) -> go.Figure:
    """Plot Year x Month calendar returns matrix heatmap."""
    month_cols = [c for c in monthly_df.columns if c != "Year Total"]
    clean_vals = monthly_df[month_cols].fillna(0.0).values

    fig = go.Figure(data=go.Heatmap(
        z=clean_vals,
        x=month_cols,
        y=monthly_df.index.astype(str),
        colorscale="RdYlGn",
        zmid=0.0,
        colorbar=dict(title="Monthly Return %", len=0.8),
        text=np.round(clean_vals, 1),
        texttemplate="%{text}%",
        textfont=dict(size=10, color="black"),
        hovertemplate="Year %{y}, %{x}<br>Return: %{z:.2f}%<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="<b>Monthly Returns Matrix (Jan–Dec)</b>", font=dict(size=14, color=TEXT_PRIMARY)),
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_DARK,
        margin=dict(l=50, r=20, t=50, b=30),
        height=420,
        yaxis=dict(autorange="reversed"),
    )
    return fig


def plot_efficient_frontier(
    sim_df: pd.DataFrame,
    opt_points: Optional[Dict[str, Tuple[float, float]]] = None
) -> go.Figure:
    """Plot Monte Carlo simulated portfolios on Risk-Return plane with optimal markers."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sim_df["Volatility %"],
        y=sim_df["Return %"],
        mode="markers",
        marker=dict(
            size=4,
            color=sim_df["Sharpe Ratio"],
            colorscale="Plasma",
            showscale=True,
            colorbar=dict(title="Sharpe", len=0.8),
            opacity=0.6,
        ),
        name="Simulated Portfolios",
        hovertemplate="Vol: %{x:.2f}%<br>Return: %{y:.2f}%<br>Sharpe: %{marker.color:.2f}<extra></extra>",
    ))

    if opt_points:
        colors_map = {"Min Volatility": COLOR_GREEN, "Max Sharpe": COLOR_AMBER, "Current Portfolio": COLOR_CYAN}
        for label, (v, r) in opt_points.items():
            c = colors_map.get(label, "#ffffff")
            fig.add_trace(go.Scatter(
                x=[v],
                y=[r],
                mode="markers+text",
                marker=dict(size=13, color=c, symbol="star", line=dict(color="white", width=1)),
                name=label,
                text=[f"<b>{label}</b>"],
                textposition="top center",
                textfont=dict(size=11, color=TEXT_PRIMARY),
                hovertemplate=f"<b>{label}</b><br>Vol: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<extra></extra>",
            ))

    fig.update_xaxes(title="Annualized Volatility (%)", ticksuffix="%")
    fig.update_yaxes(title="Annualized Expected Return (%)", ticksuffix="%")
    return apply_theme(fig, "Historical Efficient Frontier & Portfolio Optimization Space")


def plot_multi_currency_comparison(
    multi_curr_df: pd.DataFrame,
    title: str = "Portfolio Cumulative Growth Across Currencies"
) -> go.Figure:
    """Plot portfolio wealth trajectory reported across MYR, USD, SGD, GBP, EUR, and AUD."""
    fig = go.Figure()

    curr_colors = {"MYR": COLOR_CYAN, "USD": COLOR_GREEN, "SGD": COLOR_AMBER, "GBP": COLOR_PURPLE, "EUR": COLOR_BLUE, "AUD": "#ec4899"}

    for col in multi_curr_df.columns:
        c = curr_colors.get(col, "#ffffff")
        fig.add_trace(go.Scatter(
            x=multi_curr_df.index,
            y=multi_curr_df[col],
            name=f"Reported in {col}",
            line=dict(color=c, width=2.0 if col == "MYR" else 1.4),
            hovertemplate=f"{col}: %{{y:,.2f}}<extra></extra>",
        ))

    fig.update_yaxes(title="Normalized Capital Value (Base = 100,000)")
    fig.update_xaxes(title="Date")
    return apply_theme(fig, title)


def plot_risk_return_scatter(df_comparison: pd.DataFrame) -> go.Figure:
    """Plot risk-return scatter comparison across all preset model portfolios."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_comparison["_raw_vol"],
        y=df_comparison["_raw_cagr"],
        mode="markers+text",
        text=df_comparison["Portfolio"],
        textposition="top right",
        textfont=dict(size=11, color=TEXT_PRIMARY),
        marker=dict(
            size=12,
            color=df_comparison["_raw_sharpe"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Sharpe", len=0.8),
            line=dict(width=1, color="white"),
        ),
        name="Model Portfolios",
        hovertemplate="<b>%{text}</b><br>Vol: %{x:.2f}%<br>CAGR: %{y:.2f}%<extra></extra>",
    ))

    fig.update_xaxes(title="Annualized Volatility (%)", ticksuffix="%")
    fig.update_yaxes(title="CAGR (%)", ticksuffix="%")
    return apply_theme(fig, "Model Portfolios: Historical Risk vs Return Trade-Off")
