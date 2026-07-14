"""
Shared helpers for the IBEX 35 GARCH risk project.

This module is the single source of truth for the pieces that were
previously copy-pasted, verbatim, into every notebook: the data-download
block, the standardized Student-t quantile, and the EWMA volatility
recursion. It intentionally does NOT hold any analysis, model-fitting, or
plotting logic -- that stays in the notebooks, which remain the actual
deliverable. See each notebook's own markdown for the theory and
interpretation behind these functions; this module only defines them once.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

DEFAULT_TICKERS = {"IBEX35": "^IBEX", "SP500": "^GSPC"}
DEFAULT_END = pd.Timestamp("2026-07-01")


def download_data(start=None, end=None, tickers=None, pct=True):
    """
    Download adjusted daily closes, align to common trading days, and
    return log returns.

    Downloads via yfinance with auto_adjust=True (splits/dividends
    corrected), keeps only days where every ticker actually traded
    (dropna(how="any")) rather than forward-filling gaps -- forward-filling
    would manufacture artificial zero-return days for whichever market was
    closed. See Stage 1's "note on trading-day alignment" for the full
    reasoning.

    Parameters
    ----------
    start : pd.Timestamp, optional
        Start of the download window. Defaults to 10 years before `end`.
    end : pd.Timestamp, optional
        End of the download window (exclusive). Defaults to a fixed cutoff
        (2026-07-01) rather than "today", so results are reproducible
        across runs.
    tickers : dict, optional
        Mapping of {short_name: yfinance_ticker}. Defaults to
        {"IBEX35": "^IBEX", "SP500": "^GSPC"}.
    pct : bool, default True
        If True, scale log returns to percent (100x) -- the convention used
        from Stage 3 onward, since GARCH is fit by numerical maximum
        likelihood and raw decimal returns are too small for the optimizer
        to condition well. If False, return raw decimal log returns -- the
        convention used in Stages 1-2, which don't fit any numerically
        sensitive optimizer.

    Returns
    -------
    prices : pd.DataFrame
        Adjusted close prices, indexed by date, one column per ticker.
    returns : pd.DataFrame
        Log returns (percent-scaled if pct=True), same columns as `prices`.
    """
    if tickers is None:
        tickers = DEFAULT_TICKERS
    if end is None:
        end = DEFAULT_END
    if start is None:
        start = end - pd.DateOffset(years=10)

    raw = yf.download(list(tickers.values()), start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"].rename(columns={v: k for k, v in tickers.items()})
    prices = prices.dropna(how="any")

    returns = np.log(prices / prices.shift(1)).dropna()
    if pct:
        returns = 100 * returns

    return prices, returns


def std_t_quantile(nu, p):
    """
    p-quantile of the standardized (zero-mean, unit-variance) Student-t
    distribution with nu degrees of freedom.

    scipy's `stats.t.ppf` gives the quantile of the *raw* Student-t, which
    has variance nu/(nu-2), not 1. Rescaling by sqrt((nu-2)/nu) matches the
    unit-variance shocks a GARCH model with dist="t" actually estimates.
    """
    raw_q = stats.t.ppf(p, nu)
    scale = np.sqrt((nu - 2) / nu)
    return raw_q * scale


def ewma_volatility(returns, lam=0.94, seed_window=30):
    """
    RiskMetrics-style EWMA volatility.

    sigma_t^2 = lam * sigma_{t-1}^2 + (1 - lam) * r_{t-1}^2

    seeded with the sample variance of the first `seed_window`
    observations. Those seed observations are the least-reliable part of
    the resulting series (see the "EWMA warm-up" note in Stages 4-5); when
    backtesting, exclude the first `seed_window` days from breach counts
    for a fair comparison against other volatility estimators.
    """
    var = np.empty(len(returns))
    var[0] = returns.iloc[:seed_window].var()
    for t in range(1, len(returns)):
        var[t] = lam * var[t - 1] + (1 - lam) * returns.iloc[t - 1] ** 2
    return pd.Series(np.sqrt(var), index=returns.index)
