"""
Unit tests for drawdown calculation, peak-to-trough series, and recovery metrics.
"""
import pandas as pd
import numpy as np
import pytest

from src.drawdowns import compute_drawdown_series, compute_drawdown_episodes


def test_drawdown_series_and_max_dd():
    """Verify drawdown depth on known step returns."""
    rets = pd.Series([0.10, -0.20, 0.05, -0.10])
    wealth, dd, max_dd = compute_drawdown_series(rets)

    # 0: 1.10 (HWM 1.10, DD 0.0%)
    # 1: 0.88 (HWM 1.10, DD = (0.88 - 1.10)/1.10 = -20.0%)
    # 2: 0.924 (HWM 1.10, DD = (0.924 - 1.10)/1.10 = -16.0%)
    # 3: 0.8316 (HWM 1.10, DD = (0.8316 - 1.10)/1.10 = -24.4%)
    assert pytest.approx(dd.iloc[0], 0.01) == 0.0
    assert pytest.approx(dd.iloc[1], 0.01) == -20.0
    assert pytest.approx(dd.iloc[3], 0.01) == -24.4
    assert pytest.approx(max_dd, 0.01) == -24.4
