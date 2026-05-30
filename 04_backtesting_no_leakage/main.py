"""
Assignment 04: Backtesting and the 'What Was Known Then?' Rule
==============================================================

GOAL
----
Build a *reusable, leakage-free* backtesting harness for a weekly time series
(Henry Hub spot). The whole point of this module is the EVALUATION PROTOCOL, not
the model: even a trivial "tomorrow = today" forecast is fine here, as long as
you score it honestly the way you would have had to in real time.

The one rule that governs everything below:

    A forecast made at `origin_date` may only use data with
    date <= origin_date. Nothing published after the origin is allowed in.

This is `rolling-origin` (a.k.a. `walk-forward`) validation. You fit/forecast
using only the past, record the prediction, roll the origin forward one step,
and repeat -- exactly how you would actually deploy a forecaster.

WHAT IS DONE FOR YOU
--------------------
- Loading the data via the shared library.
- `make_backtest_splits()` is fully implemented and documented -- study it; it
  is the reference pattern for generating (train, test) index ranges.
- A worked DEMO that prints the first expanding split's train/test date ranges.

WHAT YOU IMPLEMENT (the TODOs)
------------------------------
- The forecast LOOP that walks every split, makes predictions, and records a
  predictions table with origin_date / target_date / horizon / actual / prediction.
- A SECOND baseline (the first, naive "last value", is stubbed for you).
- The metrics-by-origin (or by-horizon) summary and the error plot.

Run from the repo root:

    uv run python 04_backtesting_no_leakage/main.py

This file is intentionally INCOMPLETE. It runs and prints the demo split as-is;
finish the TODOs to produce the deliverable outputs.
"""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Iterator

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- make the shared library importable, then resolve paths through it -------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from ng_models.paths import data_dir, ensure_output_dir
from ng_models.io import load_series_csv
from ng_models.metrics import mae, rmse, summarize_predictions  # noqa: F401  (you'll use these)
from ng_models.plotting import save_line_plot  # noqa: F401  (you'll use this)

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

HH_FILE = "NG.RNGWHHD.W.csv"  # weekly Henry Hub spot, $/MMBtu


# ---------------------------------------------------------------------------
# REFERENCE PATTERN (fully implemented -- study this, then reuse the splits).
# ---------------------------------------------------------------------------
def make_backtest_splits(
    n_rows: int,
    *,
    min_train: int = 260,        # ~5 years of weekly data before the first forecast
    horizon: int = 1,            # how many steps ahead the test point sits
    step: int = 1,               # how far the origin moves between splits
    window: str = "expanding",   # "expanding" (train grows) or "sliding" (fixed length)
    train_size: int | None = None,  # required length when window == "sliding"
) -> Iterator[tuple[np.ndarray, int]]:
    """Yield rolling-origin (train_index, test_index) pairs over `n_rows` rows.

    This generates POSITIONAL indices (0..n_rows-1), not dates -- you map them
    back to dates with `df.iloc[...]`. Each yielded pair is one forecast origin:

        train_idx : np.ndarray   the rows the forecaster may learn from
        test_idx  : int          the single row being forecast (origin + horizon)

    The forecast ORIGIN is the last training row (`train_idx[-1]`); the TARGET
    is `test_idx = origin + horizon`. By construction `test_idx` is always
    strictly after every training row, so no future data can leak in.

    Window flavors
    --------------
    - "expanding": training set starts at row 0 and GROWS as the origin moves
      forward (uses all history). Default and usually right for gas.
    - "sliding": training set is a FIXED length (`train_size`) that slides
      forward, dropping the oldest rows. Use when you suspect old regimes
      should be forgotten.

    Examples
    --------
    >>> list(make_backtest_splits(6, min_train=3, horizon=1, step=1))
    [(array([0, 1, 2]), 3), (array([0, 1, 2, 3]), 4), (array([0, 1, 2, 3, 4]), 5)]
    """
    if window == "sliding" and train_size is None:
        raise ValueError("window='sliding' requires train_size (the fixed training length).")
    if window not in {"expanding", "sliding"}:
        raise ValueError(f"window must be 'expanding' or 'sliding', got {window!r}")

    # The first origin is the row at index (min_train - 1): we need at least
    # `min_train` rows of history, and one target row `horizon` steps later.
    origin = min_train - 1
    while origin + horizon < n_rows:
        test_idx = origin + horizon
        if window == "expanding":
            train_idx = np.arange(0, origin + 1)
        else:  # sliding
            start = max(0, origin + 1 - train_size)
            train_idx = np.arange(start, origin + 1)
        yield train_idx, test_idx
        origin += step


def main() -> None:
    # -- Guard: the only input is shipped in data/, but fail clean if it moved --
    if not (DATA_DIR / HH_FILE).exists():
        print(f"Missing input {DATA_DIR / HH_FILE}.")
        print("This module uses the weekly Henry Hub file that ships in data/.")
        print("If it is absent, re-sync the repo's data/ directory, then re-run.")
        return

    # -- Load weekly Henry Hub spot. Columns: 'date' (datetime64), 'hh_price' --
    hh = load_series_csv(DATA_DIR, HH_FILE, value_name="hh_price")
    hh = hh.dropna(subset=["hh_price"]).reset_index(drop=True)
    print(f"Loaded {len(hh)} weekly Henry Hub rows: "
          f"{hh['date'].min().date()} -> {hh['date'].max().date()}")

    # -- Choose the backtest geometry. These are the knobs you must justify in --
    # -- the report: why this min_train, why this horizon, expanding vs sliding.
    HORIZON = 1   # TODO(decision): is 1-week-ahead the horizon you want to study?
    MIN_TRAIN = 260

    # ===================================================================
    # DEMO (done for you): print the FIRST expanding split's date ranges.
    # This is the pattern you will loop over below.
    # ===================================================================
    splits = list(make_backtest_splits(len(hh), min_train=MIN_TRAIN,
                                        horizon=HORIZON, window="expanding"))
    print(f"\nGenerated {len(splits)} rolling origins "
          f"(min_train={MIN_TRAIN}, horizon={HORIZON}, expanding).")
    train_idx, test_idx = splits[0]
    origin_row = hh.iloc[train_idx[-1]]   # last training row == forecast origin
    target_row = hh.iloc[test_idx]        # the row we are forecasting
    print("First split:")
    print(f"  train rows {train_idx[0]}..{train_idx[-1]} "
          f"({hh.iloc[train_idx[0]]['date'].date()} -> {origin_row['date'].date()})")
    print(f"  origin_date = {origin_row['date'].date()}  "
          f"target_date = {target_row['date'].date()}  horizon = {HORIZON}")

    # ===================================================================
    # TODO 1 -- THE FORECAST LOOP (you implement)
    # -------------------------------------------------------------------
    # Walk every (train_idx, test_idx) in `splits`. For each origin, build the
    # baselines using ONLY train rows, then record one row per forecast.
    #
    # Required columns in your predictions table (NON-NEGOTIABLE standard):
    #   origin_date, target_date, horizon, actual, prediction, model
    #
    # Baseline 1 -- naive "last value" (random walk), stubbed for you:
    #   The forecast for the target is simply the most recent observed value at
    #   the origin: hh.iloc[train_idx[-1]]['hh_price'].
    #   This is the right null for a LEVEL forecast (taxonomy type B).
    #
    # Baseline 2 -- YOU CHOOSE (TODO decision): a second honest baseline matched
    #   to a weekly, strongly-seasonal level. Candidates: seasonal-naive
    #   (value 52 weeks ago: the row with date ~= origin - 52 weeks), or a
    #   trailing mean of the last k training rows. Pick one, IMPLEMENT it from
    #   train rows only, and justify in the report why it is a fair comparison.
    #
    # API you need (type K -- direct):
    #   - row position lookups: hh.iloc[i]  /  hh.iloc[train_idx]
    #   - the value at a position: hh.iloc[i]['hh_price']
    #   - collect dict rows in a list, then pd.DataFrame(list_of_dicts)
    #
    # LEAKAGE CHECK before you trust a row: every value feeding `prediction`
    #   must come from train_idx (origin or earlier). If you ever index >= test_idx
    #   to build a prediction, you have leaked.
    #
    # predictions_records: list[dict] = []
    # for train_idx, test_idx in splits:
    #     origin_date = hh.iloc[train_idx[-1]]['date']
    #     target_date = hh.iloc[test_idx]['date']
    #     actual      = hh.iloc[test_idx]['hh_price']
    #     naive_pred  = hh.iloc[train_idx[-1]]['hh_price']
    #     predictions_records.append({... model="naive_last", ...})
    #     # TODO: append a second record for your chosen baseline.
    # predictions = pd.DataFrame(predictions_records)

    # ===================================================================
    # TODO 2 -- METRICS (you implement)
    # -------------------------------------------------------------------
    # Use ng_models.metrics. summarize_predictions(df, actual_col, pred_col)
    # returns {"mae","rmse","mape","smape"} for a frame -- call it once PER MODEL
    # (group by the 'model' column) to build a comparison table.
    #
    # Decision (taxonomy type H): which metric do you lead with for a $/MMBtu
    # level, and should you report it RELATIVE to the naive baseline (skill)?
    # State which baseline your second model must beat and whether it does.
    #
    # Save to: OUTPUT_DIR / "backtest_metrics.csv"
    # Save predictions to: OUTPUT_DIR / "backtest_predictions.csv"

    # ===================================================================
    # TODO 3 -- ERROR-BY-ORIGIN PLOT (you implement)
    # -------------------------------------------------------------------
    # Add an absolute-error column (abs(actual - prediction)) to predictions,
    # then plot it against origin_date so you can SEE which periods broke the
    # forecast (cold snaps, 2021 spike, 2022 volatility...).
    #
    # save_line_plot(df, x="origin_date", y="abs_error", title=..., output_path=
    #     OUTPUT_DIR / "error_by_origin.png") works if you pass a one-model frame.
    # For multiple models on one axis, use matplotlib directly (fig, ax = ...).

    print(f"\nWhen complete, write outputs to: {OUTPUT_DIR}")
    print("Outstanding TODOs: forecast loop, second baseline, metrics table, error plot.")


if __name__ == "__main__":
    main()
