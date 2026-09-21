# Malaysian Multi-Asset Portfolio Analytics
### *A MYR-Centric Investment Management Research Dashboard*

---

## 📌 1. Project Overview & Research Philosophy

The **Malaysian Multi-Asset Portfolio Analytics** dashboard is a professional quantitative research platform built specifically for Malaysian institutional and private investors.

### The Central Research Question
> **"How does multi-asset allocation affect the risk, return, diversification, and currency-adjusted experience of a Malaysian Ringgit (MYR) investor?"**

Most global investment analytics software assumes USD as the domestic currency. However, for a Malaysian investor:
1. **Currency is an Active Return Driver**: Foreign asset gains can be amplified or wiped out by fluctuations in `USD/MYR`, `SGD/MYR`, `GBP/MYR`, `EUR/MYR`, and `AUD/MYR`.
2. **Local Equity & Bond Asymmetry**: Bursa Malaysia (`^KLSE`) and Malaysian Government Securities (`0800EA.KL`) have distinct correlation regimes compared to the S&P 500, MSCI ACWI, and US Treasuries.
3. **Cross-Border Compounding**: Calculating true MYR portfolio returns requires converting each historical foreign asset price on its corresponding calendar date using historical cross-currency exchange rates:
$$\left(1 + R_{\text{MYR}, t}\right) = \left(1 + R_{\text{Local}, t}\right) \times \left(1 + R_{\text{FX}, t}\right)$$

---

## ⚖️ 2. Institutional Model Disclaimers & Scope of Research

> [!IMPORTANT]
> **RESEARCH & EDUCATIONAL NATURE**:
> This platform is an independent quantitative research and educational analytics application. It is **NOT**:
> - Financial advice or personal recommendation.
> - A trading strategy, signal generator, or execution backtester.
> - A robo-advisor or automated asset management platform.
> - A prediction model or forecast of future asset returns.

### Institutional Model Transparency (EPF, PNB, Maybank)
- Model portfolios labeled **"EPF-Inspired Model"**, **"PNB-Inspired Model"**, or **"Malaysian Institutional-Style Model"** are **stylized academic approximations** designed using high-level asset class allocations publicly described in annual reports, institutional research, and market publications.
- They **do NOT represent the actual, proprietary holdings, security selection, derivatives hedging, private equity allocations, or internal trading decisions** of the Employees Provident Fund (EPF / KWSP), Permodalan Nasional Berhad (PNB), Maybank Asset Management, or any other institution.
- No commercial affiliation or endorsement is implied.

---

## 🏛️ 3. Project Directory Architecture

```
malaysian_multi_asset_portfolio/
│
├── app.py                      # Main Streamlit application entry point & dark terminal UI
├── requirements.txt            # Python dependencies (Streamlit, Pandas, Plotly, etc.)
├── .gitignore                  # Git cache and temporary artifact ignore rules
├── README.md                   # Comprehensive 26-point quantitative documentation
│
├── config/                     # Application settings & global constants
│   ├── __init__.py
│   └── settings.py             # Currencies, timezones, disclaimers, benchmark definitions
│
├── src/                        # Core mathematical and analytical modules
│   ├── __init__.py
│   ├── asset_universe.py       # Multi-asset registry (Equities, Bonds, REITs, Gold, FX)
│   ├── data_loader.py          # yfinance ingestion + Parquet caching + cash proxy
│   ├── data_cleaner.py         # Multi-market holiday alignment & data quality reporting
│   ├── currency.py             # Multi-currency conversion & historical FX attribution
│   ├── returns.py              # Compounding, CAGR, and monthly returns matrices
│   ├── portfolio.py            # Daily simulation, periodic rebalancing & fee accounting
│   ├── risk.py                 # Volatility, Sharpe/Sortino/Calmar, VaR/CVaR, Risk Contribution
│   ├── performance.py          # Benchmark relative metrics & cross-model comparison
│   ├── allocation.py           # Multi-dimensional exposure breakdowns (Class, Geo, FX)
│   ├── optimization.py         # Min Vol, Max Sharpe, Risk Parity & Efficient Frontier
│   ├── benchmarks.py           # Alpha, Beta, Tracking Error, Up/Down Capture
│   ├── stress_testing.py       # Hypothetical macro shocks & historical crisis replay
│   ├── drawdowns.py            # Underwater curves, decline durations & recovery episodes
│   ├── statistics.py           # Correlation matrices, rolling correlations & distributions
│   ├── attribution.py          # Capital gain vs currency return decomposition
│   └── charts.py               # Interactive dark Plotly visualization library
│
├── portfolios/                 # Model portfolio definitions
│   ├── __init__.py
│   └── presets.py              # 7 institutional & traditional model asset allocations
│
├── pages/                      # 10 modular Streamlit dashboard pages
│   ├── __init__.py
│   ├── overview.py             # Executive KPI cards, cumulative wealth & top summary
│   ├── portfolio_analysis.py   # Wealth curves, rolling returns, monthly heatmaps & drift
│   ├── allocation.py           # Multi-dimensional breakdowns & risk contribution share
│   ├── risk.py                 # Comprehensive risk table, VaR distribution & educational library
│   ├── currency.py             # Multi-currency reporting (MYR/USD/SGD/GBP/EUR/AUD) & FX attribution
│   ├── performance.py          # Active benchmark metrics & cross-model scatter
│   ├── stress_test.py          # Macro shock simulator & historical crisis replay
│   ├── drawdowns.py            # Underwater analysis & top historical drawdown episodes
│   ├── correlation.py          # Pearson correlation matrix heatmap & rolling dynamics
│   └── optimization_page.py    # Efficient frontier simulation & optimal weights comparison
│
├── tests/                      # Automated unit & integration test suite (pytest)
│   ├── __init__.py
│   ├── test_returns.py         # CAGR & compounding tests
│   ├── test_portfolio.py       # Simulation, rebalancing & transaction cost tests
│   ├── test_risk.py            # Volatility, Sharpe, VaR/CVaR & risk contribution tests
│   ├── test_currency.py        # Multi-currency cross-rate & compounding FX tests
│   ├── test_drawdowns.py       # Drawdown series & episode recovery tests
│   ├── test_allocation.py      # Allocation exposure & weight validator tests
│   └── test_app_integration.py # Full end-to-end analytical pipeline integration test
│
└── data/                       # Local cached market data
    ├── raw/                    # Raw Parquet price & FX cache files
    ├── processed/              # Cleaned aligned multi-asset matrices
    └── cache/                  # Runtime cache artifacts
```

---

## 🌐 4. Multi-Asset Universe & Instruments

The platform tracks 18 multi-asset instruments across 5 broad asset classes and 6 major global currencies:

| Symbol | Instrument Name | Asset Class | Region | Native Currency | Economic Role |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `^KLSE` | FTSE Bursa Malaysia KLCI | Equities | Malaysia | MYR | Malaysian Domestic Large-Cap Equities |
| `0800EA.KL` | ABF Malaysia Bond Index ETF | Fixed Income | Malaysia | MYR | Malaysian Ringgit Sovereign / MGS Bonds |
| `5180.KL` | KLCC Real Estate Investment Trust | Real Estate | Malaysia | MYR | Malaysian Commercial & Retail Property REIT |
| `MYR_CASH` | Malaysian Money Market Proxy | Cash | Malaysia | MYR | Risk-Free Capital Preservation (3.0% p.a.) |
| `SPY` | SPDR S&P 500 ETF Trust | Equities | US | USD | US Core Large-Cap Equities |
| `QQQ` | Invesco QQQ Trust | Equities | US | USD | US Tech & Innovation Equities |
| `IEF` | iShares 7-10 Year Treasury Bond | Fixed Income | US | USD | US Sovereign Intermediate Treasuries |
| `BND` | Vanguard Total Bond Market ETF | Fixed Income | US | USD | US Broad Aggregate Fixed Income |
| `VNQ` | Vanguard Real Estate ETF | Real Estate | US | USD | US Commercial Real Estate / REITs |
| `ACWI` | iShares MSCI ACWI ETF | Equities | Global | USD | Global All-Country World Equities |
| `EEM` | iShares MSCI Emerging Markets | Equities | Emerging Markets | USD | Developing Economy Equities |
| `BNDX` | Vanguard Total International Bond | Fixed Income | Global | USD | Non-US International Sovereign & Corp Debt |
| `EWS` | iShares MSCI Singapore ETF | Equities | Asia-Pacific | USD | Singapore Equities & Financials |
| `EWU` | iShares MSCI United Kingdom | Equities | Europe | USD | UK Equities |
| `EZU` | iShares MSCI Eurozone ETF | Equities | Europe | USD | Eurozone Large & Mid-Cap Equities |
| `EWA` | iShares MSCI Australia ETF | Equities | Asia-Pacific | USD | Australian Equities & Resources |
| `GLD` | SPDR Gold Shares | Commodities | Global | USD | Physical Gold Bullion / Safe-Haven Hedge |

### Foreign Exchange Rates Tracked Daily
- `USD/MYR` (`MYR=X`)
- `SGD/MYR` (`SGDMYR=X`)
- `GBP/MYR` (`GBPMYR=X`)
- `EUR/MYR` (`EURMYR=X`)
- `AUD/MYR` (`AUDMYR=X`)

---

## 💼 5. Model Portfolios & Allocations

The platform features 7 built-in model portfolios alongside a customizable portfolio editor:

### 1. Malaysian Conservative (Capital Preservation)
- **45%** Malaysian Sovereign Bonds (`0800EA.KL`)
- **25%** Malaysian Money Market / Cash (`MYR_CASH`)
- **15%** FBM KLCI Equities (`^KLSE`)
- **10%** Global ACWI Equities (`ACWI`)
- **5%** Gold Bullion (`GLD`)

### 2. Malaysian Balanced (Strategic Growth & Income)
- **30%** Malaysian Sovereign Bonds (`0800EA.KL`)
- **25%** FBM KLCI Equities (`^KLSE`)
- **20%** Global ACWI Equities (`ACWI`)
- **10%** US S&P 500 Equities (`SPY`)
- **5%** Malaysian REITs (`5180.KL`)
- **5%** Gold Bullion (`GLD`)
- **5%** Malaysian Cash (`MYR_CASH`)

### 3. Malaysian Growth (Long-Term Capital Appreciation)
- **30%** US S&P 500 Equities (`SPY`)
- **25%** Global ACWI Equities (`ACWI`)
- **20%** FBM KLCI Equities (`^KLSE`)
- **10%** US Tech QQQ (`QQQ`)
- **10%** Malaysian Sovereign Bonds (`0800EA.KL`)
- **5%** Emerging Markets (`EEM`)

### 4. EPF-Inspired Model (Stylized Institutional Pension Model)
*Based on publicly disclosed strategic asset allocation bands (Equities, Fixed Income, Real Estate, Money Market):*
- **45%** Fixed Income (`0800EA.KL`: 30%, `BNDX`: 15%)
- **40%** Global & Domestic Equities (`^KLSE`: 20%, `ACWI`: 15%, `EEM`: 5%)
- **10%** Real Estate & Infrastructure (`5180.KL`: 5%, `VNQ`: 5%)
- **5%** Money Market / Cash (`MYR_CASH`: 5%)

### 5. PNB-Inspired Model (Stylized National Unit Trust Model)
*Reflects high domestic equity weighting combined with global multi-asset expansion:*
- **50%** Malaysian Equities (`^KLSE`)
- **20%** Global Equities (`ACWI`: 15%, `SPY`: 5%)
- **15%** Malaysian Fixed Income (`0800EA.KL`)
- **10%** Malaysian Real Estate (`5180.KL`)
- **5%** Malaysian Cash (`MYR_CASH`)

### 6. Global Balanced (International 60/40 Model)
- **40%** Global ACWI Equities (`ACWI`)
- **20%** US S&P 500 Equities (`SPY`)
- **30%** US Intermediate Treasuries (`IEF`)
- **10%** Gold Bullion (`GLD`)

### 7. Malaysian Asset Management Model (Private Wealth Multi-Asset)
- **25%** FBM KLCI Equities (`^KLSE`)
- **25%** US S&P 500 Equities (`SPY`)
- **20%** Malaysian Sovereign Bonds (`0800EA.KL`)
- **10%** US Treasuries (`IEF`)
- **10%** Malaysian REITs (`5180.KL`)
- **5%** Gold Bullion (`GLD`)
- **5%** Malaysian Cash (`MYR_CASH`)

---

## 💱 6. Currency Engine & Compounding Return Attribution

When a Malaysian investor buys a US asset (e.g. `SPY`), their daily return in MYR is determined by both the asset's dollar performance and the USD/MYR exchange rate movement.

### Daily Geometric Compounding Formula
$$\left(1 + R_{\text{MYR}, t}\right) = \left(1 + R_{\text{Local}, t}\right) \times \left(1 + R_{\text{FX}, t}\right)$$
$$R_{\text{MYR}, t} = R_{\text{Local}, t} + R_{\text{FX}, t} + \left(R_{\text{Local}, t} \times R_{\text{FX}, t}\right)$$

Where:
- **$R_{\text{Local}, t}$**: Daily return in asset's native currency ($P_{\text{local}, t} / P_{\text{local}, t-1} - 1$).
- **$R_{\text{FX}, t}$**: Daily percentage change in exchange rate ($FX_{t} / FX_{t-1} - 1$).
- **$R_{\text{Local}, t} \times R_{\text{FX}, t}$**: Cross-compounding interaction term.

---

## ⚡ 7. Quantitative Risk & Portfolio Mathematics

### 1. Compound Annual Growth Rate (CAGR)
$$\text{CAGR} = \left(\frac{W_T}{W_0}\right)^{\frac{252}{N}} - 1$$

### 2. Annualized Volatility
$$\sigma_p = \sqrt{w^T \Sigma w} \times \sqrt{252}$$

### 3. Sharpe & Sortino Ratios
$$\text{Sharpe} = \frac{\text{CAGR} - r_f}{\sigma_p}$$
$$\text{Sortino} = \frac{\text{CAGR} - r_f}{\sigma_{\text{downside}}}, \quad \text{where } \sigma_{\text{downside}} = \sqrt{\frac{1}{N} \sum_{t=1}^N \min\left(0, R_t - \frac{r_f}{252}\right)^2} \times \sqrt{252}$$

### 4. Marginal and Percentage Risk Contribution (PRC)
$$\text{MRC}_i = \frac{\left(\Sigma w\right)_i}{\sigma_p}$$
$$\text{RC}_i = w_i \times \text{MRC}_i, \quad \text{PRC}_i = \frac{\text{RC}_i}{\sigma_p} \times 100\%$$
$$\sum_{i=1}^N \text{PRC}_i = 100.0\%$$

### 5. Historical Value-at-Risk (VaR) & Expected Shortfall (CVaR)
- **1-Day $\text{VaR}_{95\%}$**: The 5th percentile worst daily return.
- **1-Day $\text{CVaR}_{95\%}$**: The expected conditional average loss on days exceeding the $\text{VaR}_{95\%}$ threshold.

### 6. Diversification Ratio (DR) & Effective Number of Constituents (ENC)
$$\text{DR} = \frac{\sum_{i=1}^N w_i \sigma_i}{\sigma_p} \ge 1.0$$
$$\text{ENC} = \frac{1}{\sum_{i=1}^N w_i^2}$$

---

## 🌪️ 8. Macro Stress Testing & Historical Crisis Replay

The platform provides institutional-grade stress testing across both hypothetical shocks and actual historical market crises:

### 1. Predefined Macroeconomic Shocks
- **Global Equity Crash**: -30% Global Equities, -25% Bursa Malaysia, +3% Bonds, +10% Gold.
- **Interest Rate Shock**: -10% Equities, -8% Fixed Income, -12% REITs, +3% Gold.
- **MYR Weakening**: +10% USD/MYR, +6% SGD/GBP/EUR/AUD vs MYR; domestic asset local prices unchanged.
- **Global Risk-Off**: -20% Equities, -15% REITs, +5% Sovereign Bonds, +8% Gold.

### 2. Historical Crisis Replay
- **COVID-19 Market Crash**: Feb 19, 2020 – Apr 30, 2020.
- **2022 Global Rate Hike & Inflation Shock**: Jan 03, 2022 – Oct 14, 2022.
- **2018 US-China Trade War Escalation**: Jan 26, 2018 – Dec 24, 2018.

---

## 🎯 9. Portfolio Optimization Frameworks

The research dashboard includes 4 classical and modern portfolio construction models:

1. **Equal Weight ($1/N$)**: Baseline allocation assigning equal capital across all investable assets.
2. **Minimum Volatility Portfolio**:
   $$\min_w w^T \Sigma w \quad \text{s.t.} \quad \sum w_i = 1, \quad 0 \le w_i \le w_{\max}$$
3. **Maximum Sharpe Portfolio (Tangency Portfolio)**:
   $$\max_w \frac{w^T \mu - r_f}{\sqrt{w^T \Sigma w}} \quad \text{s.t.} \quad \sum w_i = 1, \quad 0 \le w_i \le w_{\max}$$
4. **Risk Parity / Equal Risk Contribution (ERC)**:
   $$\min_w \sum_{i=1}^N \sum_{j=1}^N \left(w_i (\Sigma w)_i - w_j (\Sigma w)_j\right)^2 \quad \text{s.t.} \quad \sum w_i = 1, \quad w_i \ge 0$$
5. **Efficient Frontier Simulation**: Monte Carlo simulation of 1,500 portfolios mapping the full risk-return envelope.

---

## 🖥️ 10. Streamlit Dashboard Pages Guide

The dashboard is structured into 10 dedicated research modules:

1. **`📊 Overview`**: Live MYT clock, reporting currency banner, executive KPI cards (Value, CAGR, Vol, Sharpe, Max DD, Calmar), cumulative wealth chart, asset allocation donut, risk share bars, non-predictive summary, and institutional disclaimers.
2. **`📈 Portfolio Analysis`**: Wealth trajectory, 60d/120d/252d rolling annualized returns, Jan–Dec monthly returns heatmap matrix, annual performance breakdown table, and weight drift over time.
3. **`🥧 Allocation & Exposure`**: Multi-dimensional breakdown by Asset Class, Geographic Region, Country, and Native Currency, plus Capital Weight vs Risk Contribution comparisons.
4. **`🛡️ Risk & Downside`**: Comprehensive risk table, daily return distribution histogram with VaR/CVaR cutoffs, diversification metrics (ENC, DR, $\bar{\rho}$), and an educational investment concept library.
5. **`💱 Currency & FX Impact`**: Multi-currency performance comparison (MYR vs USD vs SGD vs GBP vs EUR vs AUD), asset-level FX return attribution table, and compounding mathematical proofs.
6. **`🏆 Performance & Benchmarks`**: Active benchmark metrics (Alpha, Beta, Tracking Error, Information Ratio, Up/Down Capture) and cross-model risk-return scatter plot.
7. **`⚡ Stress Testing`**: Predefined macro shock scenarios, interactive custom shock slider builder, and historical crisis replays (COVID-19, 2022 Inflation).
8. **`📉 Drawdowns`**: Full underwater drawdown area chart, current drawdown depth, and top historical peak-to-trough-to-recovery episodes table.
9. **`🔗 Correlation`**: Multi-asset Pearson correlation matrix heatmap, correlation tables, and rolling 60-day/120-day pairwise correlation tracker.
10. **`🎯 Optimization Research`**: Efficient Frontier Monte Carlo simulation, optimal portfolio markers (Min Vol, Max Sharpe, Current), side-by-side target weights comparison, and optimization methodology.

---

## 🚀 11. Installation & Quickstart

### Prerequisites
- Python 3.10+ (Tested on Python 3.10, 3.11, 3.12, 3.14)
- Virtual environment recommended

### Installation Steps

```bash
# 1. Clone or navigate to the project directory
cd malaysian_multi_asset_portfolio

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Launch the Streamlit Research Dashboard
streamlit run app.py
```

The application will launch locally at `http://localhost:8501`.

---

## 🧪 12. Automated Test Suite

The test suite provides comprehensive unit and integration test coverage across all quantitative calculation engines:

```bash
# Run pytest test suite
pytest tests/ -v
```

### Verified Test Cases
- `test_returns.py`: CAGR mathematical accuracy and wealth index compounding.
- `test_portfolio.py`: 3-asset toy portfolio daily returns, periodic rebalancing, and transaction cost deduction.
- `test_risk.py`: Annualized volatility, Sharpe/Sortino ratios, and $\sum \text{PRC}_i = 100\%$ risk contribution validation.
- `test_currency.py`: Multi-currency cross rates and $(1+R_{\text{investor}}) = (1+R_{\text{local}})(1+R_{\text{FX}})$ compounding attribution.
- `test_drawdowns.py`: High-water mark tracking, drawdown series, and recovery episode identification.
- `test_allocation.py`: Portfolio weight validation and multi-dimensional exposure aggregation.
- `test_app_integration.py`: End-to-end multi-asset simulation, currency conversion, stress testing, and optimization pipeline.

---

## 📄 13. License & Academic Citation

This project is open-source under the MIT License. Developed for quantitative investment management research, academic study, and asset allocation education in Malaysia.
