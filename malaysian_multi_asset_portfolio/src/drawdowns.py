"""
Drawdown calculation, underwater curve analysis, and historical drawdown episodes module.
"""
from typing import Tuple, List, Dict, Any, Optional
import pandas as pd
import numpy as np


def compute_drawdown_series(returns_series: pd.Series) -> Tuple[pd.Series, pd.Series, float]:
    """
    Calculate wealth index, rolling high water mark, drawdown series (%), and maximum drawdown (%).
    """
    clean_r = returns_series.dropna()
    if clean_r.empty:
        return pd.Series(), pd.Series(), 0.0

    wealth = (1.0 + clean_r).cumprod()
    high_water_mark = wealth.cummax()
    drawdown = (wealth - high_water_mark) / high_water_mark * 100.0
    max_dd = float(drawdown.min())

    return wealth, drawdown, max_dd


def compute_drawdown_episodes(
    drawdown_series: pd.Series,
    top_n: int = 5
) -> pd.DataFrame:
    """
    Identify distinct peak-to-trough-to-recovery historical drawdown episodes.
    """
    if drawdown_series.empty:
        return pd.DataFrame()

    episodes = []
    in_dd = False
    peak_date = None
    trough_date = None
    trough_val = 0.0
    trough_idx = 0
    start_idx = 0

    idx = drawdown_series.index

    for i, (dt, val) in enumerate(drawdown_series.items()):
        if val < 0:
            if not in_dd:
                in_dd = True
                start_idx = i - 1 if i > 0 else 0
                peak_date = idx[start_idx]
                trough_date = dt
                trough_val = val
                trough_idx = i
            else:
                if val < trough_val:
                    trough_val = val
                    trough_date = dt
                    trough_idx = i
        else:
            if in_dd:
                recovery_date = dt
                duration_to_trough = trough_idx - start_idx
                recovery_duration = i - trough_idx
                total_duration = i - start_idx
                episodes.append({
                    "peak_date": peak_date.strftime("%Y-%m-%d"),
                    "trough_date": trough_date.strftime("%Y-%m-%d"),
                    "recovery_date": recovery_date.strftime("%Y-%m-%d"),
                    "max_drawdown_pct": trough_val,
                    "decline_days": int(duration_to_trough),
                    "recovery_days": int(recovery_duration),
                    "total_days": int(total_duration),
                    "is_recovered": True,
                })
                in_dd = False

    if in_dd:
        episodes.append({
            "peak_date": peak_date.strftime("%Y-%m-%d"),
            "trough_date": trough_date.strftime("%Y-%m-%d"),
            "recovery_date": "Active / In Recovery",
            "max_drawdown_pct": trough_val,
            "decline_days": int(trough_idx - start_idx),
            "recovery_days": np.nan,
            "total_days": int(len(drawdown_series) - start_idx),
            "is_recovered": False,
        })

    if not episodes:
        return pd.DataFrame()

    df_ep = pd.DataFrame(episodes)
    df_ep = df_ep.sort_values(by="max_drawdown_pct", ascending=True).head(top_n).reset_index(drop=True)

    df_ep["Max Drawdown"] = df_ep["max_drawdown_pct"].apply(lambda x: f"{x:.2f}%")
    df_ep["Decline (Days)"] = df_ep["decline_days"]
    df_ep["Recovery (Days)"] = df_ep["recovery_days"].apply(lambda x: f"{int(x)}" if pd.notna(x) else "—")
    df_ep["Total Duration"] = df_ep["total_days"]
    df_ep["Peak Date"] = df_ep["peak_date"]
    df_ep["Trough Date"] = df_ep["trough_date"]
    df_ep["Recovery Date"] = df_ep["recovery_date"]

    return df_ep
