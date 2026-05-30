"""
Assignment 09: Feature Engineering and the Model-Ready Panel

Run from repo root:

    uv run python 09_feature_table_leakage/main.py

WHAT THIS MODULE IS ABOUT
-------------------------
Up to now you have studied series one or two at a time. Here you assemble the
first *model-ready panel* (a.k.a. feature table / model matrix / design matrix):
ONE rectangular table where each row is a single forecast you could have made,
with:
  - a `forecast_origin` (the date the forecast is made),
  - a `target_date` and `target` (the future value you are predicting),
  - and a set of PREDICTOR columns (features) that were all knowable AT the
    forecast origin.
The whole game is leakage avoidance: every feature on a row must use only
information that was actually available on that row's `forecast_origin`.

DEPENDENCY ON EARLIER MODULES
-----------------------------
This module CONSUMES the outputs you produced in modules 06, 07, and 08:
  - 06_storage_fundamentals/outputs/storage_panel.csv
  - 07_supply_demand_balance/outputs/monthly_balance_panel.csv
  - 08_weather_degree_days/outputs/weather_features.csv
If any of those are missing, this script prints a clear "complete 0X first"
message and exits cleanly (it does NOT crash). Run modules 06/07/08 first.

This file is intentionally INCOMPLETE. The plumbing (loading, checking inputs,
saving outputs) is wired for you. The MODELING DECISIONS are left as TODOs with
inline guidance — you make the call and defend it in REPORT.md.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from ng_models.paths import data_dir, ensure_output_dir
from ng_models.io import load_metadata, load_series_csv, search_metadata
from ng_models.time_utils import make_forward_target, add_calendar_columns
from ng_models.features import add_lags, add_rolling_stats
from ng_models.metrics import summarize_predictions

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# Inputs produced by the prior modules. (path, the module that makes it.)
UPSTREAM_INPUTS = {
    "storage": (ROOT / "06_storage_fundamentals" / "outputs" / "storage_panel.csv", "06"),
    "balance": (ROOT / "07_supply_demand_balance" / "outputs" / "monthly_balance_panel.csv", "07"),
    "weather": (ROOT / "08_weather_degree_days" / "outputs" / "weather_features.csv", "08"),
}


def check_inputs() -> dict[str, Path] | None:
    """Verify upstream outputs exist. Return the resolved paths, or None if any
    are missing (after printing an actionable message). This is what keeps the
    script exit-0 instead of crashing when a dependency hasn't been run yet."""
    missing = [(name, mod, p) for name, (p, mod) in UPSTREAM_INPUTS.items() if not p.exists()]
    if missing:
        print("Cannot build the panel yet — these upstream outputs are missing:")
        for name, mod, p in missing:
            print(f"  - {name}: complete module {mod} first (expected {p})")
        print("\nRun, e.g.:  uv run python 06_storage_fundamentals/main.py")
        return None
    return {name: p for name, (p, _) in UPSTREAM_INPUTS.items()}


def main() -> None:
    inputs = check_inputs()
    if inputs is None:
        # Clean, actionable exit — not a crash.
        print(f"\nWhen the inputs exist, outputs will be written to: {OUTPUT_DIR}")
        return

    # ------------------------------------------------------------------
    # STEP 1 — Load the spine: weekly Henry Hub price.
    # The panel's "spine" is the series whose dates define one row per forecast
    # origin. Weekly Henry Hub is a natural spine for this curriculum.
    # API: load_series_csv(DATA_DIR, "<file>", value_name="<col>") returns a
    #      tidy ['date', '<col>'] frame, date-sorted.
    # ------------------------------------------------------------------
    hh = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="hh_price")
    print(f"Loaded {len(hh)} weekly Henry Hub rows "
          f"({hh['date'].min().date()} .. {hh['date'].max().date()}).")

    # ------------------------------------------------------------------
    # STEP 2 — DEFINE THE TARGET.  (Modeling decision — taxonomy types D & E.)
    # The forecast object is YOUR call. Three reasonable options for this module:
    #   (a) next-week price LEVEL          -> value_col="hh_price", horizon=1
    #   (b) next-week CHANGE / log return  -> first build a change column,
    #                                          then target that column
    #   (c) next-MONTH average price       -> resample to monthly first
    # make_forward_target attaches the future value AND the bookkeeping the
    # curriculum requires (forecast_origin, target_date, horizon_steps):
    #   panel = make_forward_target(hh, value_col="hh_price", horizon=1,
    #                               target_name="target_hh_next")
    # The horizon is in ROWS — on a weekly spine, horizon=1 means "one week
    # ahead". Decide which target answers the question you want to ask, write
    # that sentence in REPORT.md, then build it.
    #
    # TODO: build `panel` from `hh` using make_forward_target with YOUR chosen
    #       target and horizon. (Placeholder below uses a 1-week level target so
    #       the script runs; replace it with your justified choice.)
    panel = make_forward_target(hh, value_col="hh_price", horizon=1,
                                target_name="target_hh_next")

    # ------------------------------------------------------------------
    # STEP 3 — ADD PRICE-DERIVED FEATURES.  (Decision: which lags/windows — type A/D.)
    # These come straight off the spine and are leakage-safe by construction:
    #   add_lags(df, columns, lags)           -> <col>_lag_<k>     (k rows back)
    #   add_rolling_stats(df, columns, windows)-> <col>_roll_mean_<w>,
    #                                             <col>_roll_std_<w>
    #       (rolling helpers shift(1) BEFORE the window, so the current row is
    #        NOT in its own feature — read features.py to see why.)
    # TODO: choose lag list and window list that match your horizon and defend
    #       them (why 1/4/8 weeks? what recent-history span is informative?).
    panel = add_lags(panel, columns=["hh_price"], lags=[1, 4])          # <- your choice
    panel = add_rolling_stats(panel, columns=["hh_price"], windows=[4]) # <- your choice
    panel = add_calendar_columns(panel, date_col="date")  # month/week — always safe

    # ------------------------------------------------------------------
    # STEP 4 — AS-OF JOIN THE FUNDAMENTAL FEATURES.  (Decision: release lag — type A.)
    # The upstream panels are published with a delay. You must attach, for each
    # forecast_origin, only the value that was ALREADY PUBLIC by then.
    # pandas tool: merge_asof. For each left row it grabs the most recent right
    # row at or before the key — but ONLY if you have first shifted the right
    # series forward by its real publication lag, OR you build an explicit
    # "available_date" column and join on that.
    #
    #   weather = pd.read_csv(inputs["weather"], parse_dates=["date"]).sort_values("date")
    #   # Decide the release lag for THIS source, then either shift its date
    #   # forward by that lag or shift its values: e.g. for weekly EIA storage
    #   # published ~5 days after the week it covers, the value for week-ending
    #   # Friday is only usable the FOLLOWING week.
    #   panel = pd.merge_asof(
    #       panel.sort_values("forecast_origin"),
    #       weather.rename(columns={"date": "wx_available_date"}),
    #       left_on="forecast_origin", right_on="wx_available_date",
    #       direction="backward",   # never look forward in time
    #   )
    #
    # TODO: load each upstream file, give every fundamental column a documented
    #       release lag, and merge_asof it onto `panel`. Then ask yourself the
    #       leakage question for EACH column: "was this value public on the
    #       forecast_origin date?" (Left as a TODO on purpose — this is the core
    #       skill of the module. The script runs without it so you can iterate.)
    #
    # MONTHLY -> WEEKLY: the balance panel (module 07) is MONTHLY. You must
    # broadcast each month's figure onto the weekly spine — and respect that a
    # month's data is not public until after the month ends plus the agency lag.
    # merge_asof with a properly-lagged monthly available_date handles both the
    # frequency mismatch and the leakage in one step. (Decision — type A/C.)

    # ------------------------------------------------------------------
    # STEP 5 — MISSINGNESS REPORT + LEAKAGE-SAFE HANDLING.  (Decision — type A.)
    # Count NaNs per column BEFORE you decide what to do with them.
    #   miss = (panel.isna().sum().rename("n_missing").to_frame())
    #   miss["pct_missing"] = (miss["n_missing"] / len(panel)).round(4)
    # For imputation, only use information from the PAST: forward-fill (ffill)
    # is leakage-safe; back-fill (bfill) and a global mean both leak the future.
    # The leading NaNs from lags/rolling/target are EXPECTED — drop them, don't
    # fill them.
    # TODO: write `missingness_report.csv`; decide ffill vs drop per column and
    #       justify it (would the value really have been known, or are you
    #       inventing it?).
    miss = panel.isna().sum().rename("n_missing").to_frame()
    miss["pct_missing"] = (miss["n_missing"] / len(panel)).round(4)
    miss.to_csv(OUTPUT_DIR / "missingness_report.csv")
    print(f"Wrote missingness report ({len(miss)} columns).")

    # ------------------------------------------------------------------
    # STEP 6 — DATA DICTIONARY.  (Documentation standard — required.)
    # Every feature needs: name, source, unit, transform, availability lag, why.
    # Build this BY HAND from what you actually added — a reviewer must be able
    # to audit each feature's timing. Example row included so you see the shape:
    data_dictionary = pd.DataFrame([
        {
            "name": "hh_price_lag_1",
            "source": "EIA NG.RNGWHHD.W (Henry Hub weekly spot)",
            "unit": "USD/MMBtu",
            "transform": "lag 1 row (1 week)",
            "availability_lag": "known at origin (own past price)",
            "why": "recent price level is the strongest cheap predictor",
        },
        # TODO: add one row PER feature column you keep (lags, rolling stats,
        #       calendar, and every fundamental you as-of-joined). For each
        #       fundamental, the `availability_lag` must reflect its real
        #       publication delay, not the period it covers.
    ])
    data_dictionary.to_csv(OUTPUT_DIR / "data_dictionary.csv", index=False)
    print(f"Wrote data dictionary ({len(data_dictionary)} rows — expand it).")

    # ------------------------------------------------------------------
    # STEP 7 — SAVE THE PANEL and run a SANITY assertion.
    # Curriculum standard: every forecast row carries origin + target date, and
    # the target must be strictly in the future relative to the origin.
    trained = panel.dropna(subset=["target_hh_next"]).copy()
    assert (trained["target_date"] > trained["forecast_origin"]).all(), (
        "Leakage guard failed: some target_date is not after its forecast_origin."
    )
    panel.to_csv(OUTPUT_DIR / "model_panel.csv", index=False)
    print(f"Wrote model_panel.csv ({len(panel)} rows, {panel.shape[1]} columns).")

    # ------------------------------------------------------------------
    # STEP 8 — BASELINE ONLY (NO ML YET).  (Decision: which baseline — type B/H.)
    # The point of this module is the PANEL, not the model. Prove the panel is
    # usable by scoring ONE honest baseline on it. For a 1-week level target the
    # natural null is the random walk: predict next week's price = this week's.
    #   trained["baseline_rw"] = trained["hh_price"]      # last known level
    #   scores = summarize_predictions(
    #       trained.rename(columns={"target_hh_next": "actual",
    #                               "baseline_rw": "prediction"}))
    # TODO: pick the baseline that MATCHES your target (random walk for a level,
    #       seasonal-naive for a seasonal level, zero-change for a change target)
    #       and report MAE/RMSE. Any model you fit later must beat THIS. Do NOT
    #       fit LightGBM/XGBoost here — that is module 10.
    if "hh_price" in trained:
        scored = trained.rename(columns={"target_hh_next": "actual"}).copy()
        scored["prediction"] = scored["hh_price"]  # random-walk placeholder
        print("Random-walk baseline (placeholder) on the panel:",
              {k: round(v, 4) for k, v in summarize_predictions(scored).items()})

    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
