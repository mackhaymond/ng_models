"""Feature-engineering helpers for the ng-models curriculum.

These build predictor columns (lags, rolling statistics, degree days) from a
date-sorted DataFrame. The recurring theme is LEAKAGE AVOIDANCE: a feature
attached to a row may only use information that was actually available at that
row's date. Using the row's own (or future) value to predict that same row
inflates accuracy in backtests and then fails in production.

pandas notes:
- ``Series.shift(n)`` moves values DOWN by ``n`` rows (later in time), filling
  the top with ``NaN``. ``shift(1)`` therefore gives you "the previous row's
  value" -- i.e. yesterday's number, known today.
- ``Series.rolling(window).mean()`` computes a moving average over the last
  ``window`` rows (inclusive of the current row, unless you shift first).
- All functions ``sort_values("date")`` and ``copy()`` first so the input is
  not mutated and time order is guaranteed before any shift/rolling.
"""

from __future__ import annotations

import pandas as pd

def add_lags(df: pd.DataFrame, columns: list[str], lags: list[int]) -> pd.DataFrame:
    """Add lagged copies of columns as new features.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``date`` column and every name in ``columns``.
    columns : list[str]
        Columns to lag.
    lags : list[int]
        Positive offsets in ROWS. For ``lag=k`` the new column
        ``<col>_lag_<k>`` holds the value from ``k`` rows earlier.

    Returns
    -------
    pd.DataFrame
        A copy of ``df`` (re-sorted by date) with one new column per
        (column, lag) pair. The first ``k`` rows of each lagged column are
        ``NaN`` because there is no earlier value to copy.

    Why this is leakage-safe
    ------------------------
    ``shift(k)`` with positive ``k`` only ever pulls PAST values forward, so a
    lag feature on a given row never contains information from that row's own
    date or later. (Note: lags are measured in rows, so they only equal a fixed
    time span if the series is evenly spaced.)
    """
    out = df.sort_values("date").copy()
    for col in columns:
        for lag in lags:
            out[f"{col}_lag_{lag}"] = out[col].shift(lag)
    return out

def add_rolling_stats(df: pd.DataFrame, columns: list[str], windows: list[int]) -> pd.DataFrame:
    """Add rolling mean and standard deviation features over past values.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``date`` column and every name in ``columns``.
    columns : list[str]
        Columns to summarize.
    windows : list[int]
        Window sizes in ROWS. Each produces ``<col>_roll_mean_<w>`` and
        ``<col>_roll_std_<w>``.

    Returns
    -------
    pd.DataFrame
        A copy of ``df`` (re-sorted by date) with two new columns per
        (column, window) pair. Leading rows are ``NaN`` until enough history
        exists to fill the window.

    Why we ``shift(1)`` BEFORE rolling (critical for no leakage)
    -----------------------------------------------------------
    A plain ``rolling(w).mean()`` INCLUDES the current row in its window, so the
    feature for a given date would be computed using that date's own value --
    information you would not have when forecasting it. Shifting by 1 first means
    the window covers rows ``[t-w, ..., t-1]``: strictly past values, known
    before the current date. The rolling std is the spread of those same past
    values (a cheap recent-volatility proxy). If you intend to forecast the value
    at ``t``, this guarantees the predictor is observable at ``t``.
    """
    out = df.sort_values("date").copy()
    for col in columns:
        shifted = out[col].shift(1)
        for window in windows:
            out[f"{col}_roll_mean_{window}"] = shifted.rolling(window).mean()
            out[f"{col}_roll_std_{window}"] = shifted.rolling(window).std()
    return out

def hdd_cdd_from_tavg(tavg_f: pd.Series, base_f: float = 65.0) -> pd.DataFrame:
    """Convert average temperature into Heating and Cooling Degree Days.

    Parameters
    ----------
    tavg_f : pd.Series
        Average daily temperature in degrees Fahrenheit.
    base_f : float, default ``65.0``
        Comfort/balance-point temperature. The 65 F convention is the U.S.
        industry standard for energy degree-day calculations.

    Returns
    -------
    pd.DataFrame
        Columns ``hdd`` and ``cdd`` aligned to ``tavg_f``'s index.

    Concept
    -------
    Degree days measure how far the weather pushes energy demand away from the
    comfort point:
    - HDD = max(base - tavg, 0): how many degrees of HEATING were needed (cold
      days drive gas demand up). Zero on warm days.
    - CDD = max(tavg - base, 0): how many degrees of COOLING were needed (hot
      days drive electricity/gas-for-power demand). Zero on cold days.
    ``Series.clip(lower=0)`` floors the values at 0 so a day is never negative
    heating or negative cooling. These are contemporaneous transforms of weather
    (no shifting); whether a weather feature is leakage-safe depends on whether
    you use observed history or a forecast as your input.
    """
    hdd = (base_f - tavg_f).clip(lower=0)
    cdd = (tavg_f - base_f).clip(lower=0)
    return pd.DataFrame({"hdd": hdd, "cdd": cdd})
