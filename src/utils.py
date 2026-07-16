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

import os

import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

DEFAULT_TICKERS = {"IBEX35": "^IBEX", "SP500": "^GSPC"}
DEFAULT_END = pd.Timestamp("2026-07-01")

# The default (tickers, start, end) combination is the one every notebook in
# this project actually uses. That fixed dataset is cached to disk and
# committed to the repo so results are reproducible offline and immune to
# Yahoo Finance silently revising historical prices -- see download_data's
# docstring. The cache never applies to a non-default window/ticker set.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_REPO_ROOT, "data")
PRICE_CACHE_PATH = os.path.join(DATA_DIR, "prices_ibex_sp500.csv")


def _normalize_prices(prices):
    """
    Canonical dtype/index/columns form for the prices DataFrame, applied
    identically whether `prices` just came from a fresh yfinance download or
    was reloaded from the CSV cache -- so the two code paths are guaranteed
    to return bit-for-bit identical DataFrames, not merely equal values.
    """
    prices = prices.astype("float64")
    prices.index = pd.DatetimeIndex(prices.index.astype("datetime64[ns]"), name="Date")
    prices.columns.name = "Ticker"
    return prices


def _download_prices(tickers, start, end):
    raw = yf.download(list(tickers.values()), start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"].rename(columns={v: k for k, v in tickers.items()})
    prices = prices.dropna(how="any")
    return _normalize_prices(prices)


def download_data(start=None, end=None, tickers=None, pct=True, force_download=False):
    """
    Load adjusted daily closes, align to common trading days, and return log
    returns.

    For the project's default (tickers, start, end) -- i.e. every call made
    without arguments, or with only `pct` set -- this is **cache-first**:
    if `data/prices_ibex_sp500.csv` exists, it's loaded from disk and the
    network is never touched; otherwise the data is downloaded via yfinance
    (auto_adjust=True, splits/dividends corrected) and the cache file is
    written so the next call doesn't need the network either. That cache
    file is committed to the repo, so cloning it and running the notebooks
    reproduces the exact published numbers with no network access and no
    exposure to Yahoo Finance silently revising historical prices between
    runs. Pass `force_download=True` to deliberately refresh the cache from
    a fresh download (e.g. if the fixed end date is ever moved forward).

    Only days where every ticker actually traded are kept
    (dropna(how="any")) rather than forward-filled -- forward-filling would
    manufacture artificial zero-return days for whichever market was
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
    force_download : bool, default False
        If True, always download fresh from yfinance and overwrite the
        cache (only for the default window; see above). If False (default),
        use the cache when it exists and the window/tickers are the default.

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

    is_default_window = (
        tickers == DEFAULT_TICKERS
        and end == DEFAULT_END
        and start == DEFAULT_END - pd.DateOffset(years=10)
    )

    if is_default_window and not force_download and os.path.exists(PRICE_CACHE_PATH):
        prices = pd.read_csv(PRICE_CACHE_PATH, index_col=0, parse_dates=True)
        prices = _normalize_prices(prices)
    else:
        prices = _download_prices(tickers, start, end)
        if is_default_window:
            os.makedirs(DATA_DIR, exist_ok=True)
            prices.to_csv(PRICE_CACHE_PATH)

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
