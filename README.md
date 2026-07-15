# IBEX 35 GARCH Risk

[🇪🇸 Español](README.es.md) · **🇬🇧 English**

Market-risk model **validation** on the Spanish IBEX 35 index using the
ARIMA–GARCH framework. The endpoint is not trading performance but a risk
question: **would this VaR model have held up in real time, and does it survive
formal backtesting?** The S&P 500 is included as a benchmark, making it a
cross-market study.

Built as a Risk Analytics / FRM-oriented econometric project: every stage pairs
theory with an interpretation of the actual results, and the limitations are
stated explicitly.

## What it does

Five stages, one notebook each, from raw prices to regulatory validation:

1. **Data & exploration** (`01_exploration.ipynb`) — log returns and the stylized
   facts (volatility clustering, heavy tails, non-normality) that motivate
   everything downstream.
2. **Stationarity & mean model** (`02_stationarity_arima.ipynb`) — ADF/KPSS, an
   ARIMA mean model, and the bridge to GARCH: returns are uncorrelated in the
   mean, but their squared residuals are not.
3. **The GARCH family** (`03_garch_family.ipynb`) — GARCH(1,1), GJR-GARCH and
   EGARCH with Student-t innovations; persistence, leverage and tail thickness,
   validated on standardized residuals.
4. **VaR & Expected Shortfall** (`04_var_es.ipynb`) — dynamic parametric VaR and
   ES, against an EWMA/RiskMetrics baseline (same Student-t quantile, so the
   comparison isolates the volatility method).
5. **VaR backtesting** (`05_var_backtesting.ipynb`) — Kupiec and Christoffersen
   implemented from scratch, run on a genuine **out-of-sample** backtest
   (expanding window, model refit on past data only).

## Methodology: the out-of-sample backtest

The headline results come from a backtest that simulates what a risk manager
would actually have done: the first 60% of the sample is the initial estimation
window; for each of the remaining 995 days the model is re-estimated **only on
data up to t−1** and produces a 1-step-ahead volatility forecast (refit every 5
trading days as a documented computational compromise). An in-sample backtest is
also reported — explicitly labelled as biased — to make the difference visible.

## Headline findings

**Cross-market volatility (Stage 3, 2,486 obs):**
- **Leverage is stronger in the S&P 500** (GJR γ = 0.233) than the IBEX (0.189).
- **The S&P has heavier tails** (Student-t ν ≈ 5.4 vs ≈ 7.6 for the IBEX).
- **Volatility is more persistent in the S&P** (0.97–0.98 vs 0.92–0.93).
- Preferred by AIC: **GJR-GARCH for the IBEX, EGARCH for the S&P** — asymmetric
  models beat plain GARCH in both markets.

**Risk validation (Stage 5, out-of-sample, 995 obs at the headline 60/40 split):**
- **All four S&P 500 combinations pass** conditional coverage; **all four IBEX 35
  combinations fail.** The result splits by *market*, not by model — **but this
  verdict only holds in a calm test period, see below.**
- **The IBEX fails on clustering, not on count.** IBEX GARCH at 99% has near
  perfect unconditional coverage (10 breaches vs 10 expected, Kupiec p = 0.987 —
  the best value in the table) but fails independence (p = 0.003): its breaches
  arrive in clusters. The model gets *how often* right, but not *when*.
- GARCH produces fewer breaches than EWMA in both markets, but in the IBEX even
  GARCH cannot disperse them — the Spanish market's problem isn't solved by
  swapping the volatility model.
- **Stress-tested against its own methodology, twice.** The headline backtest
  refits every 5 days and uses a 60/40 train/test split, both arbitrary
  choices, so both were swept: (1) refit cadence at 1, 10 and 20 days — the
  IBEX's clustering tendency survives every cadence (independence p never
  exceeds 0.085; the S&P's never drops below 0.075), but the exact pass/fail
  verdict is cadence-sensitive for both markets; (2) **the train/test split
  itself — the single most important robustness check in this project.**

**The headline result above is a calm-period finding, and that turns out to
matter enormously.** The 60/40 split's test period (mid-2022 onward) happens
to exclude COVID-2020, which falls inside the *training* window instead.
Re-running the identical backtest with an initial window small enough to pull
COVID-2020 into the test period makes **all 8 cells fail** — including every
S&P 500 cell that passed cleanly before — and the S&P's failure mode becomes
genuine miscoverage (breach rates near double nominal at 99%), not just
clustering. What *does* survive a crisis-inclusive test period: the IBEX's
breach-clustering problem (independence fails at every split tried, COVID or
not) and the S&P's freedom from it (independence never fails, even during
COVID) — that specific cross-market difference is the one result robust to
every check in this project.

**What a validator would conclude:** the S&P 500's parametric GARCH VaR is
validated **in calm markets** but not (on raw coverage) once a genuine crisis
enters the test window; the IBEX 35 is not validated in either regime, and
fails specifically because its breaches cluster — the most dangerous failure
mode a risk model can have (failing repeatedly during a live crisis). A
backtest that never tests a stress period cannot make this distinction, and a
risk model's "pass" is close to meaningless without knowing whether its test
window contained one. Recommended next steps: regime-switching models,
Expected Shortfall, or an EVT treatment of the tail.

## Why this isn't another generic ARIMA-GARCH repo

Generic "fit GARCH and plot the volatility" notebooks are everywhere and are
mostly descriptive or trading-oriented. This one plays a different game:
**model validation with a regulatory / FRM lens**, on a **non-Anglo market**, with a
**genuine out-of-sample backtest**, formal statistical tests implemented from
scratch, and an **apples-to-apples EWMA benchmark** — the parts most repos skip.
The through-line with the rest of my portfolio: a credit-scoring project
validated a PD model; this validates a VaR model.

## Methodology notes

- **Adjusted prices** (`auto_adjust=True`): corrected for splits/dividends.
  ^IBEX and ^GSPC are price-return indices, correct for volatility modelling.
- **No survivorship bias:** analyzing the index series (not its constituents)
  inherits a history that already accounted for firms that dropped out.
- **Common trading days only:** the two markets are aligned on shared sessions
  rather than forward-filling, which would create artificial zero returns.
- **Fixed window** ending 2026-07-01 (~10 years, 2,486 obs) so results are
  reproducible; includes the COVID-2020 stress in-sample, though the headline
  60/40 OOS split places it in training rather than the test period — see
  Stage 5, Section 13.

## Limitations

Stated explicitly in the notebooks: 1-day horizon only (no multi-day VaR);
univariate (no portfolio risk or tail dependence via copulas); symmetric
Student-t (a skewed-t may fit equity returns better); parametric VaR
underestimates the extreme tail (EVT would model it directly); a single 10-year
window (5/10/15y sensitivity remains an open robustness gap, though Section 13
partially probes it by varying the train/test boundary within that window);
both the refit cadence (1/5/10/20 days) and the train/test split (35/50/60%,
crisis-inclusive vs. not) were stress-tested — see Stage 5, Sections 12-13 —
rather than left as untested assumptions; and VaR is a statistical measure — it
excludes liquidity and model risk.

## Setup

```bash
pip install -r requirements.txt
jupyter lab
```

Shared helpers live in `src/utils.py`; each notebook imports from there and runs
top to bottom.

## Stack

Python · pandas · numpy · scipy · statsmodels · arch (Kevin Sheppard) · pmdarima
· yfinance · matplotlib — ARIMA, GARCH/EGARCH/GJR, VaR, Expected Shortfall,
Kupiec & Christoffersen.
