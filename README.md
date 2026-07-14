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
   Christoffersen tests implemented from scratch, run on both a naive in-sample
   fit and a genuine **expanding-window out-of-sample backtest**, plus the
   Basel traffic-light framework, with an honest read of where each model
   passes and fails.

## Headline findings

**Cross-market volatility (Stage 3):**
- The **leverage effect is stronger in the S&P 500** than the IBEX (GJR γ ≈ 0.23
  vs 0.19): US drops raise volatility more sharply.
- The **S&P 500 has heavier tails** (Student-t ν ≈ 5.3 vs ≈ 7.3 for the IBEX).
- Volatility is highly persistent in both (α+β ≈ 0.92–0.98).

**Risk validation (Stages 4–5):**
- Stage 5's centerpiece is a **genuine out-of-sample backtest**: an expanding
  window refit every 5 trading days, forecasting one day ahead — not a model
  fit once on the full sample and evaluated on the same data it was fit on.
- Out-of-sample, the pass/fail split is **by index, not by model**: **all 4
  S&P 500 cells** (GARCH and EWMA, 95% and 99%) cleanly pass conditional
  coverage, while **all 4 IBEX 35 cells fail** — every one of them for the
  same reason.
- **The single most important finding**: every failing IBEX 35 cell has a
  *good* breach count (Kupiec p up to 0.99) but **statistically significant
  breach clustering** (Christoffersen independence test) — the model gets the
  average frequency of bad days right but reacts too slowly once a regime
  shift is underway. A naive, full-sample-fitted backtest sits right on the
  edge of hiding exactly this problem.
- **Basel's traffic-light framework cannot see this failure mode at all**:
  IBEX 35 GARCH's 99% VaR lands comfortably in Basel's green zone (breach rate
  ≈1.01%, almost exactly nominal) — the same cell that fails conditional
  coverage outright once independence is checked.

**Honest conclusion:** parametric VaR — even with GARCH, Student-t
innovations, and a genuinely out-of-sample test — validates cleanly for one
market (S&P 500) and fails for another (IBEX 35), for a specific,
identifiable reason (breach clustering, not miscalibrated coverage). This is
a genuine validation finding, not a failure: it points to **Expected
Shortfall, a faster-reacting variance specification, or an EVT approach** as
more prudent responses, and it demonstrates concretely why **out-of-sample
testing — including the independence of breaches, not just their count — is
the actual point of model validation**. The project deliberately reports this
rather than forcing a "the model passes" narrative.

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
- **Common trading days only:** the IBEX 35 and S&P 500 don't share a holiday
  calendar; forward-filling the gaps would manufacture fake zero-return days
  for whichever market was closed. All notebooks instead keep only days both
  markets actually traded (`dropna(how="any")`), so every return is a real
  price move.
- **Reproducible by design:** every notebook uses a fixed data cutoff
  (`2026-07-01`) rather than "today," so the documented results don't drift
  each time a notebook is re-run. Warnings are filtered narrowly (two named,
  known-benign messages) rather than blanket-suppressed, so genuine
  convergence or numerical warnings would still surface.
- **~10-year window:** ample for GARCH, includes the COVID-2020 stress; older
  regimes deliberately excluded. A 5/10/15-year sensitivity analysis is a noted
  robustness extension.
- **Out-of-sample validation:** Stage 5 refits GARCH on an expanding window
  (≈60% initial training, refit every 5 trading days) rather than relying on a
  single full-sample fit, which would otherwise let the model "see" the
  future — including COVID-2020 — before backtesting on it.
- **Fair EWMA comparisons exclude the warm-up window:** EWMA's variance
  recursion is seeded from its own first 30 observations, so those days are
  dropped from breach counts for *both* EWMA and GARCH before backtesting —
  otherwise EWMA's least-reliable days would bias the comparison.
- **Intentional code duplication:** the data-download block, the standardized
  Student-t quantile helper, and the EWMA recursion are repeated verbatim
  across notebooks 01-05 rather than imported from a shared module. Each
  notebook is meant to be read (and run) as a self-contained document — a
  `src/utils.py` would shrink the code but mean no single notebook could be
  copied out and understood or executed on its own, which matters more here
  than DRY-ness.

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
