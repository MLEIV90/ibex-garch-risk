# IBEX GARCH Risk

Volatility modelling and market-risk analysis of the IBEX 35 using the ARIMA-GARCH framework.

## Project structure

```
notebooks/   Jupyter notebooks, one per analysis stage
data/        Cached market data (git-ignored, reproducible from the notebooks)
```

## Stages

1. **Data & exploration** (`notebooks/01_exploration.ipynb`) — download IBEX 35 and S&P 500 data, compute log returns, and examine the stylized facts of financial returns (volatility clustering, heavy tails, autocorrelation) that motivate GARCH modelling.

## Setup

```bash
pip install -r requirements.txt
jupyter lab
```
