# IBEX GARCH Risk

Volatility modelling and market-risk analysis of the IBEX 35 using the ARIMA-GARCH framework.

## Project structure

```
notebooks/   Jupyter notebooks, one per analysis stage
data/        Cached market data (git-ignored, reproducible from the notebooks)
```

## Stages

1. **Data & exploration** (`notebooks/01_exploration.ipynb`) — download IBEX 35 and S&P 500 data, compute log returns, and examine the stylized facts of financial returns (volatility clustering, heavy tails, autocorrelation) that motivate GARCH modelling.
2. **Stationarity & mean model** (`notebooks/02_stationarity_arima.ipynb`) — test stationarity (ADF, KPSS) on prices and returns, identify and fit an ARIMA mean model via ACF/PACF and AIC search, and show via Ljung-Box and ARCH-LM that the residuals are uncorrelated but still have autocorrelated variance — the bridge to GARCH.
3. **The GARCH family** (`notebooks/03_garch_family.ipynb`) — fit and compare GARCH(1,1), GJR-GARCH and EGARCH with Student-t innovations, interpret persistence, the leverage effect and tail thickness across both indices, select a preferred model per index, and confirm via ARCH-LM that it has absorbed the volatility clustering.
4. **VaR & Expected Shortfall** (`notebooks/04_var_es.ipynb`) — compute dynamic parametric VaR (95%/99%) and Expected Shortfall (97.5%/99%) from the preferred GARCH models, benchmark against an EWMA/RiskMetrics baseline, and compare breach counts as a preview of Stage 5 backtesting.
5. **VaR backtesting & validation** (`notebooks/05_var_backtesting.ipynb`) — implement the Kupiec proportion-of-failures and Christoffersen independence/conditional-coverage tests from scratch, backtest GARCH vs. EWMA VaR at 95%/99%, connect the 99% results to the Basel traffic-light framework, and give an honest, non-cherry-picked read of where each model passes and fails.

## Setup

```bash
pip install -r requirements.txt
jupyter lab
```
