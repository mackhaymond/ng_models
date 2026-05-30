"""Assignment 02: Calendar Structure and Naive Forecast Baselines.

Goal of this module
-------------------
Build simple, *leakage-free* baseline forecasts for weekly Henry Hub spot price
and evaluate them honestly on a fixed final test window. Later modules must beat
the best of these baselines out of sample, so getting them right (and provably
past-only) is the whole point.

Run from the repo root:

    uv run python 02_calendar_baselines/main.py

This file is an INCOMPLETE guided starter. The data load, path handling, and the
calendar/horizon framing are done for you. The substantive modeling decisions —
which horizon, how to build each leakage-free baseline, which test window, and
which baseline to crown — are left as TODOs with inline guidance. Read
ASSIGNMENT.md ("Concepts you'll use" + "Package guide") first.
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from ng_models.paths import data_dir, ensure_output_dir
from ng_models.io import load_series_csv
from ng_models.time_utils import add_calendar_columns
# Use the shared metric implementations rather than re-coding MAE/RMSE/MAPE.
from ng_models.metrics import mae, rmse, summarize_predictions

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

SERIES_FILE = "NG.RNGWHHD.W.csv"


def main() -> None:
    # ------------------------------------------------------------------
    # 0. Load the series, failing cleanly if the data file is absent.
    # ------------------------------------------------------------------
    series_path = DATA_DIR / SERIES_FILE
    if not series_path.exists():
        print(
            f"Could not find {series_path}.\n"
            "This module needs the weekly Henry Hub file. It ships with the repo "
            "under data/; if it is missing, see docs/DATA_SOURCE_NOTES.md to "
            "re-collect it before running this assignment."
        )
        return

    hh = load_series_csv(DATA_DIR, SERIES_FILE, value_name="price")
    # load_series_csv returns: date (datetime64), price (float), sorted ascending.
    hh = add_calendar_columns(hh, date_col="date")  # adds year, month, iso_week, ...
    print(f"Loaded {len(hh)} weekly rows: {hh['date'].min().date()} -> "
          f"{hh['date'].max().date()}")
    print(hh.head())

    # ------------------------------------------------------------------
    # 1. CHOOSE YOUR HORIZON.
    # ------------------------------------------------------------------
    # TODO: Pick ONE forecast horizon h (number of weekly rows ahead) and state
    #       in REPORT.md whether it is 1-step (h=1, "predict next week") or
    #       multi-step (e.g. h=4, "predict ~one month out"). Keep it fixed across
    #       all baselines so the comparison is fair.
    # Leading question: does "beat the naive baseline" get harder or easier as h
    #       grows, and why?
    HORIZON = None  # <-- set to an int, e.g. 1 or 4
    if HORIZON is None:
        print("\nNothing computed yet: set HORIZON (task 1) and implement the "
              "baselines below. See ASSIGNMENT.md tasks 1-5.")
        return

    # ------------------------------------------------------------------
    # 2. BUILD LEAKAGE-FREE BASELINES (each a column of per-origin forecasts).
    # ------------------------------------------------------------------
    # The frame `hh` is one row per week (the forecast origin). For each origin
    # you want a prediction of the price HORIZON rows later. Build these columns:
    #
    #   naive       -> last observed value (random walk). Past-only.
    #   exp_mean    -> EXPANDING historical mean (NOT full-sample mean).
    #   exp_median  -> EXPANDING historical median.
    #   woy_mean    -> week-of-year (iso_week) mean, prior-year same-week only.
    #   woy_median  -> week-of-year median, prior-year same-week only.
    #
    # LEAKAGE RULE (the graded standard): the value used to predict the target at
    # origin t may only depend on rows with date <= t. A full-sample
    # hh["price"].mean() is the classic leak — it contains the test years.
    #
    # API guidance (see ASSIGNMENT.md "Package guide" for more):
    #   hh["price"].shift(k)                       # value k rows back (past-only)
    #   hh["price"].expanding().mean().shift(1)    # mean of strictly-past rows
    #   hh.groupby("iso_week")["price"].apply(
    #       lambda s: s.expanding().mean().shift(1)
    #   ).reset_index(level=0, drop=True)          # seasonal, past-only
    #
    # TODO: implement the five baseline columns. Decide, for your chosen HORIZON,
    #       the exact shift each baseline needs so it stays past-only, and write
    #       that reasoning in the report. (Hint: the naive value known at origin t
    #       and used to predict t+h is the price at t, i.e. shift by h on the
    #       target frame — you work out the bookkeeping.)
    #
    # raise NotImplementedError("Implement the five baseline columns (task 2).")

    # ------------------------------------------------------------------
    # 3. FRAME THE TARGET AND PICK A FIXED TEST WINDOW.
    # ------------------------------------------------------------------
    # You need, per origin row: the future actual at t+HORIZON, plus
    # forecast_origin, target_date, horizon_steps for auditability.
    #
    # API guidance:
    #   hh["actual"]          = hh["price"].shift(-HORIZON)   # future value
    #   hh["target_date"]     = hh["date"].shift(-HORIZON)
    #   hh["forecast_origin"] = hh["date"]
    #   hh["horizon_steps"]   = HORIZON
    #   Then drop rows where actual or any baseline is NaN (warm-up + tail).
    #
    # TODO: choose a CONTIGUOUS final test window (e.g. last 104 weeks ~ 2 years),
    #       decided BEFORE you look at metrics. Select it by target_date, not by
    #       position-after-dropping, and record exact start/end dates in REPORT.md.
    #       Leading question: why must the test window be the most recent block
    #       and never a random sample of weeks?
    #
    # Example selection pattern (you set the cutoff):
    #   test = panel[panel["target_date"] >= CUTOFF].copy()

    # ------------------------------------------------------------------
    # 4. SCORE EACH BASELINE ON THE TEST WINDOW.
    # ------------------------------------------------------------------
    # Use the shared metrics. summarize_predictions returns mae/rmse/mape/smape
    # for one prediction column at a time:
    #   rows = []
    #   for col in ["naive", "exp_mean", "exp_median", "woy_mean", "woy_median"]:
    #       m = summarize_predictions(test, actual_col="actual", pred_col=col)
    #       rows.append({"baseline": col, **m})
    #   metrics_df = pd.DataFrame(rows)
    #
    # TODO: build metrics_df and write it to OUTPUT_DIR / "baseline_metrics.csv".
    #       Also write the per-origin test forecasts to
    #       OUTPUT_DIR / "test_forecasts.csv" (include forecast_origin,
    #       target_date, horizon_steps, actual, and each baseline column).
    #       Leading question: MAE vs RMSE — which do you report as primary for a
    #       price level, and what does MAPE do when price dips near $2?

    # ------------------------------------------------------------------
    # 5. PLOT actual vs >=3 baselines over the test window.
    # ------------------------------------------------------------------
    # Multiple lines, so drive matplotlib directly (the save_line_plot helper is
    # single-line only):
    #   fig, ax = plt.subplots(figsize=(11, 5))
    #   ax.plot(test["target_date"], test["actual"], label="actual")
    #   for col in [...]:
    #       ax.plot(test["target_date"], test[col], label=col)
    #   ax.legend(); ax.set_title(...)
    #   fig.tight_layout(); fig.savefig(OUTPUT_DIR / "baseline_comparison.png", dpi=150)
    #   plt.close(fig)
    #
    # TODO: produce baseline_comparison.png and, in REPORT.md, say what the chart
    #       shows AND what it does not show.

    # ------------------------------------------------------------------
    # 6. CROWN A BASELINE.
    # ------------------------------------------------------------------
    # TODO (decision, not code): in REPORT.md, state which baseline every later
    #       model must beat and WHY. Defend it from the metrics table, not vibes.

    print(f"\nOutputs should be written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
