"""Forecast error metrics for the ng-models curriculum.

These compare a forecast against the realized actuals. Each takes two
array-likes (lists, numpy arrays, or pandas Series) of equal length aligned
row-by-row: ``y_true`` (what happened) and ``y_pred`` (what you predicted).

Concept primer:
- MAE  (mean absolute error): average of |actual - forecast|, in the same
  units as the series. Easy to read, robust to outliers.
- RMSE (root mean squared error): sqrt of the average squared error, also in
  the series' units, but squares the errors so it PUNISHES large misses more.
- MAPE (mean absolute percentage error): average of |error| / |actual|, a
  unit-free percentage. Undefined when an actual is 0 (division by zero) and
  blows up when actuals are tiny.
- sMAPE (symmetric MAPE): uses (|actual| + |forecast|) in the denominator, so
  it stays bounded and is symmetric in over- vs under-prediction.

numpy notes:
- ``np.asarray(x, dtype=float)`` coerces any array-like to a float numpy array.
- ``np.nanmean`` averages while ignoring ``NaN`` entries, so missing/aligned
  gaps don't poison the result.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

def mae(y_true, y_pred) -> float:
    """Mean Absolute Error: ``mean(|y_true - y_pred|)``.

    Parameters
    ----------
    y_true, y_pred : array-like
        Equal-length aligned actuals and predictions.

    Returns
    -------
    float
        Average absolute error, in the series' own units (``NaN`` rows ignored).
    """
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    return float(np.nanmean(np.abs(y_true_arr - y_pred_arr)))

def rmse(y_true, y_pred) -> float:
    """Root Mean Squared Error: ``sqrt(mean((y_true - y_pred)**2))``.

    Parameters
    ----------
    y_true, y_pred : array-like
        Equal-length aligned actuals and predictions.

    Returns
    -------
    float
        In the series' own units. Larger than MAE when errors are uneven,
        because squaring weights big misses more heavily.
    """
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.nanmean((y_true_arr - y_pred_arr) ** 2)))

def mape(y_true, y_pred) -> float:
    """Mean Absolute Percentage Error: ``mean(|y_true - y_pred| / |y_true|)``.

    Parameters
    ----------
    y_true, y_pred : array-like
        Equal-length aligned actuals and predictions.

    Returns
    -------
    float
        A fraction (multiply by 100 for a percentage). Rows where ``y_true == 0``
        are dropped because the percentage is undefined there.

    Warnings
    --------
    Emits a :class:`UserWarning` when zero-valued actuals are dropped (the result
    then describes only a subset of the data), and returns ``nan`` if EVERY
    actual is zero (nothing left to average). This is surfaced loudly because
    silently masking rows can make a bad forecast look artificially good.
    """
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    mask = y_true_arr != 0
    n_dropped = int((~mask).sum())
    if n_dropped:
        if not mask.any():
            warnings.warn(
                "mape: all actual values are zero; MAPE is undefined, returning nan.",
                stacklevel=2,
            )
            return float("nan")
        warnings.warn(
            f"mape: dropped {n_dropped} row(s) with zero actuals before computing "
            "MAPE; the result reflects only the remaining rows.",
            stacklevel=2,
        )
    return float(np.nanmean(np.abs((y_true_arr[mask] - y_pred_arr[mask]) / y_true_arr[mask])))

def smape(y_true, y_pred) -> float:
    """Symmetric Mean Absolute Percentage Error.

    ``mean( 2 * |y_true - y_pred| / (|y_true| + |y_pred|) )``

    Parameters
    ----------
    y_true, y_pred : array-like
        Equal-length aligned actuals and predictions.

    Returns
    -------
    float
        A fraction in ``[0, 2]`` (multiply by 100 for the conventional
        percentage). Unlike MAPE, the denominator uses both actual and forecast,
        so it stays finite as long as they are not BOTH zero, and it treats
        over- and under-prediction symmetrically.

    Notes
    -----
    Rows where both actual and forecast are zero give ``0/0``; those are dropped
    from the average via ``np.nanmean`` (the division yields ``NaN`` there).
    """
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    numerator = 2.0 * np.abs(y_true_arr - y_pred_arr)
    denominator = np.abs(y_true_arr) + np.abs(y_pred_arr)
    # Suppress numpy's divide-by-zero warning; 0/0 -> nan is handled by nanmean.
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = numerator / denominator
    return float(np.nanmean(ratio))

def summarize_predictions(df: pd.DataFrame, actual_col: str = "actual", pred_col: str = "prediction") -> dict[str, float]:
    """Compute all error metrics at once for a predictions table.

    Parameters
    ----------
    df : pd.DataFrame
        A table with one row per forecast, holding the realized value and the
        prediction.
    actual_col : str, default ``"actual"``
        Column holding the realized values.
    pred_col : str, default ``"prediction"``
        Column holding the forecasts.

    Returns
    -------
    dict[str, float]
        ``{"mae", "rmse", "mape", "smape"}`` -> metric value. Handy for building
        a comparison table across models/baselines (each call is one row).
    """
    return {
        "mae": mae(df[actual_col], df[pred_col]),
        "rmse": rmse(df[actual_col], df[pred_col]),
        "mape": mape(df[actual_col], df[pred_col]),
        "smape": smape(df[actual_col], df[pred_col]),
    }
