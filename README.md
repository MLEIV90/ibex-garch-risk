# IBEX 35 GARCH Risk

[🇪🇸 Español](README.es.md) · **🇬🇧 English**

Market-risk model **validation** on the Spanish IBEX 35 index, using the
ARIMA–GARCH framework. The endpoint is not trading performance but a risk
question: **which volatility model produces the most reliable Value-at-Risk, and
does it survive formal backtesting?** The S&P 500 is included as a comparison
benchmark, making it a cross-market study.

Built as a Risk Analytics / FRM-oriented econometric project: every stage pairs
theory with an interpretation of the actual results.

## What it does

A five-stage pipeline, one notebook per stage, from raw prices to regulatory
validation of the risk estimates:

1. **Data & exploration** (`notebooks/01_exploration.ipynb`) — log returns and
   the stylized facts (volatility clustering, heavy tails, non-normality) that
   motivate everything that follows.
2. **Stationarity & mean model** (`notebooks/02_stationarity_arima.ipynb`) —
   ADF/KPSS testing, an ARIMA mean model, and the bridge to GARCH: returns are
   uncorrelated in the mean but their squared residuals are not.
3. **The GARCH family** (`notebooks/03_garch_family.ipynb`) — GARCH(1,1),
   GJR-GARCH and EGARCH with Student-t innovations; persistence, the leverage
   effect and tail thickness, validated on standardized residuals.
4. **VaR & Expected Shortfall** (`notebooks/04_var_es.ipynb`) — dynamic
   parametric VaR and ES from the preferred models, benchmarked against an
   EWMA/RiskMetrics baseline.
5. **VaR backtesting** (`notebooks/05_var_backtesting.ipynb`) — Kupiec and
   Christoffersen tests implemented from scratch, plus the Basel traffic-light
   framework, with an honest read of where each model passes and fails.

## Headline findings

**Cross-market volatility (Stage 3):**
- The **leverage effect is stronger in the S&P 500** than the IBEX (GJR γ ≈ 0.24
  vs 0.18): US drops raise volatility more sharply.
- The **S&P 500 has heavier tails** (Student-t ν ≈ 5 vs ≈ 7 for the IBEX).
- Volatility is highly persistent in both (α+β ≈ 0.92–0.98).

**Risk validation (Stages 4–5):**
- At 99%, **GARCH lands in Basel's green zone** for both indices (≈3.1 and ≈3.9
  scaled exceptions per 250 days) while the **EWMA baseline lands in yellow**
  (≈5.3–5.6) — the added model complexity is justified.
- **Only one of eight (index, model, level) combinations cleanly passes**
  conditional coverage: IBEX 35 GJR-GARCH at 99% (Kupiec p = 0.24).
- Most failures come from **too many breaches, not clustering** — the models
  react well to regime changes but the **parametric VaR underestimates tail
  risk**, especially at 95%.

**Honest conclusion:** parametric VaR — even with GARCH and Student-t
innovations — systematically underestimates risk in this sample. This is a
genuine validation finding, not a failure: it points to **Expected Shortfall or
an EVT approach** as more prudent for the tail. The project deliberately reports
this rather than forcing a "the model passes" narrative.

## Why this isn't another generic ARIMA-GARCH repo

Generic "fit GARCH and plot the volatility" notebooks are everywhere and are
mostly descriptive or trading-oriented. This one plays a different game:
**model validation with a regulatory / FRM lens**, on a **non-Anglo market**,
with **formal VaR backtesting** and an **honest EWMA benchmark** — the parts most
repos skip. The through-line with the rest of my portfolio: a credit-scoring
project validated a PD model; this validates a VaR model.

## Methodology notes

- **Adjusted prices** (`auto_adjust=True`): corrected for splits/dividends to
  avoid artificial volatility. ^IBEX and ^GSPC are price-return indices, correct
  for volatility modelling.
- **No survivorship bias:** analyzing the index series (not its constituents)
  inherits a history that already accounted for firms that dropped out.
- **~10-year window:** ample for GARCH, includes the COVID-2020 stress; older
  regimes deliberately excluded. A 5/10/15-year sensitivity analysis is a noted
  robustness extension.

## Setup

```bash
pip install -r requirements.txt
jupyter lab
```

Each notebook is self-contained: it downloads its own data via `yfinance` and
can be run top to bottom.

## Stack

Python · pandas · numpy · scipy · statsmodels · arch (Kevin Sheppard) · pmdarima
· yfinance · matplotlib — Elo not involved here; this is pure econometrics:
ARIMA, GARCH/EGARCH/GJR, VaR, Expected Shortfall, Kupiec & Christoffersen.

## Limitations & possible extensions

- Parametric VaR underestimates the tail; an **EVT / Expected-Shortfall**
  treatment would be the natural next step.
- **Sensitivity analysis** across window lengths (5/10/15y, including 2008).
- An optional **machine-learning challenger** (e.g. LSTM or gradient boosting on
  realized volatility) as an honest comparison — kept out of the core so it
  doesn't dilute the risk-validation focus.
