"""Date/calendar and forecast-framing helpers for the ng-models curriculum.

These two functions cover (1) turning a date into calendar features a model can
use (month, week-of-year, quarter) and (2) framing a forecasting problem by
attaching the FUTURE value you want to predict to each row, along with the
bookkeeping that keeps the curriculum's "every forecast row has a forecast
origin AND a target date" standard.

pandas notes:
- ``df[date_col].dt`` exposes datetime parts (``.year``, ``.month``,
  ``.quarter``) on a ``datetime64`` Series.
- ``Series.shift(n)`` moves values DOWN by ``n`` rows; ``shift(-n)`` moves them
  UP by ``n`` rows (pulling FUTURE rows back to the current row).
"""

from __future__ import annotations

import pandas as pd

def add_calendar_columns(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Add calendar-derived columns from a date column.

    Parameters
    ----------
    df : pd.DataFrame
        Source table.
    date_col : str, default ``"date"``
        Name of the column holding dates (coerced to ``datetime64`` internally).

    Returns
    -------
    pd.DataFrame
        A copy of ``df`` with added columns: ``year``, ``month``, ``iso_year``,
        ``iso_week``, ``quarter``.

    Notes
    -----
    These are pure functions of the row's OWN date, so they are always
    leakage-safe -- the calendar date of a row is known at that row.

    ISO vs. calendar week: ``dt.isocalendar()`` returns the ISO-8601 week
    numbering, where weeks start on Monday and week 1 is the week containing the
    first Thursday of the year. Near year boundaries ``iso_year`` can differ
    from the plain ``year`` (e.g. 2021-01-01 falls in ISO week 53 of iso_year
    2020), which is exactly why both are kept. They are cast to ``int`` because
    ``isocalendar()`` returns a nullable ``UInt32`` dtype that some models
    dislike.
    """
    out = df.copy()
    dt = pd.to_datetime(out[date_col])
    iso = dt.dt.isocalendar()
    out["year"] = dt.dt.year
    out["month"] = dt.dt.month
    out["iso_year"] = iso.year.astype(int)
    out["iso_week"] = iso.week.astype(int)
    out["quarter"] = dt.dt.quarter
    return out

def make_forward_target(df: pd.DataFrame, value_col: str, horizon: int, target_name: str = "target") -> pd.DataFrame:
    """Attach the future value to predict, plus forecast-origin bookkeeping.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``date`` column and ``value_col``.
    value_col : str
        The column whose FUTURE value becomes the prediction target.
    horizon : int
        How many ROWS ahead to look. Must satisfy ``0 < horizon < len(df)``.
    target_name : str, default ``"target"``
        Name for the new target column.

    Returns
    -------
    pd.DataFrame
        A copy of ``df`` (re-sorted by date) with:
        - ``<target_name>``: the value of ``value_col`` ``horizon`` rows ahead;
        - ``target_date``: the date that target value belongs to;
        - ``forecast_origin``: this row's date (when the forecast is made);
        - ``horizon_steps``: the horizon, recorded per row.
        The last ``horizon`` rows have ``NaN`` target/``NaT`` target_date
        because their future is not in the data yet -- drop them before
        training.

    Why ``shift(-horizon)`` and why the horizon guard
    -------------------------------------------------
    ``shift(-horizon)`` with a POSITIVE horizon pulls a FUTURE row's value back
    onto the current (origin) row: row ``t`` gets the value observed at ``t +
    horizon``. That is correct -- the label is genuinely in the future relative
    to the origin, while every PREDICTOR you build (lags, rolling stats) stays
    in the past. The origin date and target date are stored explicitly so each
    forecast row is fully auditable.

    The ``assert 0 < horizon < len(df)`` guard matters: a NEGATIVE horizon would
    make ``shift(-horizon)`` a positive shift, pulling a PAST value into the
    target and silently turning the exercise into "predicting the past" -- a
    leakage bug that would look fine numerically. ``horizon == 0`` would set the
    target to the row's own value (trivial leakage), and ``horizon >= len(df)``
    would make every target ``NaN``. Failing loudly here prevents all three.
    """
    assert 0 < horizon < len(df), (
        f"horizon must satisfy 0 < horizon < len(df) (got horizon={horizon}, "
        f"len(df)={len(df)}); a non-positive horizon would leak past/current "
        "values into the target."
    )
    out = df.sort_values("date").copy()
    out[target_name] = out[value_col].shift(-horizon)
    out["target_date"] = out["date"].shift(-horizon)
    out["forecast_origin"] = out["date"]
    out["horizon_steps"] = horizon
    return out
