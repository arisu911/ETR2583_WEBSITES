"""
Unit tests for returns, compounding, CAGR, and monthly matrices.
"""
import pandas as pd
import numpy as np
import pytest

from src.returns import (
    compute_cagr,
    compute_wealth_index,
    compute_monthly_returns_matrix,
)


def test_cagr_calculation():
    """
    Test CAGR formula:
    If an asset grows from 100 to 144 over 2 years (252*2 = 504 trading days),
    CAGR = (144 / 100) ^ (1 / 2) - 1 = 1.20 - 1 = +20.0% p.a.
    """
    # Daily constant return such that product over 504 days is 1.44
    daily_ret = (1.44) ** (1.0 / 504.0) - 1.0
    returns_series = pd.Series([daily_ret] * 504)

    cagr = compute_cagr(returns_series, periods_per_year=252)
    assert pytest.approx(cagr, 0.001) == 0.20


def test_wealth_index_calculation():
    """Verify wealth index growth starting from 100,000 RM."""
    rets = pd.Series([0.10, -0.05, 0.20])
    wealth = compute_wealth_index(rets, initial_capital=100000.0)

    # 100,000 * 1.10 = 110,000
    # 110,000 * 0.95 = 104,500
    # 104,500 * 1.20 = 125,400
    assert pytest.approx(wealth.iloc[0], 0.01) == 110000.0
    assert pytest.approx(wealth.iloc[1], 0.01) == 104500.0
    assert pytest.approx(wealth.iloc[2], 0.01) == 125400.0
