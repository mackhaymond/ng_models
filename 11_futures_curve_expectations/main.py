"""
Assignment 11: Futures Curve and Market-Implied Expectations
============================================================

Goal of this module
--------------------
Build a Henry Hub *futures curve* snapshot from the four EIA continuous-contract
series (RNGC1..RNGC4), classify its shape (contango vs backwardation), and then
ask the hard question: is the futures curve a useful *benchmark* for a spot-price
forecast? Futures are market prices, NOT forecasts (see docs/GLOSSARY_SEED.md
"Why futures are NOT forecasts"), so the whole point is to compare them honestly.

Contract notation (EIA continuous series)
-----------------------------------------
- RNGC1 = "Contract 1" = the front / prompt month (nearest contract still trading).
- RNGC2, RNGC3, RNGC4 = the 2nd, 3rd, 4th nearest contract months.
  These are *continuous* series: each day RNGC1 is whatever the prompt contract is
  that day, so the underlying delivery month rolls forward over time. They are NOT
  a fixed July-2024 contract held constant.

DATA SCOPE WARNING (read before you model)
------------------------------------------
The futures files (RNGC1..4) in data/ END at 2024-04-05 and only cover 4 contracts.
The spot series (RNGWHHD) runs to 2026. Any spot-vs-futures comparison MUST be
scoped to the overlap window (<= 2024-04-05). To work with a current, deeper curve
you must collect it yourself -- see DATA_COLLECTION.md in this folder.

Run from repo root:

    uv run python 11_futures_curve_expectations/main.py

This file is intentionally INCOMPLETE. It loads and aligns the data for you and
leaves the modeling DECISIONS as TODOs with inline guidance. Fill them in; do not
expect this starter to produce the deliverables on its own.
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
from ng_models.io import load_series_csv
from ng_models.plotting import save_line_plot

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# The four EIA continuous futures contracts (daily) + the daily spot price.
# C1 is the prompt/front month; C2..C4 are the next three nearer months.
FUTURES_FILES = {
    1: "NG.RNGC1.D.csv",
    2: "NG.RNGC2.D.csv",
    3: "NG.RNGC3.D.csv",
    4: "NG.RNGC4.D.csv",
}
SPOT_FILE = "NG.RNGWHHD.D.csv"


def load_curve_long() -> pd.DataFrame | None:
    """Load all four futures contracts into one LONG (tidy) frame.

    Returns a DataFrame with columns [date, contract, price] where ``contract``
    is the integer 1..4. Returns None if any required file is missing (so the
    caller can print an actionable message and exit cleanly).

    pandas note (type K, direct help):
    - load_series_csv(DATA_DIR, filename, value_name="price") returns columns
      ["date", "price"], date-sorted. We add a ``contract`` column and stack.
    - pd.concat([...], ignore_index=True) stacks frames vertically (row-wise).
    """
    frames = []
    for n, fname in FUTURES_FILES.items():
        path = DATA_DIR / fname
        if not path.exists():
            print(f"[missing] {path}")
            print("Futures data is incomplete. See DATA_COLLECTION.md to collect "
                  "the current NYMEX curve, or restore the RNGC1..4 files in data/.")
            return None
        df = load_series_csv(DATA_DIR, fname, value_name="price")
        df["contract"] = n
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    # ------------------------------------------------------------------
    # 0. Load. Bail out cleanly if inputs are missing.
    # ------------------------------------------------------------------
    curve_long = load_curve_long()
    if curve_long is None:
        return

    spot_path = DATA_DIR / SPOT_FILE
    if not spot_path.exists():
        print(f"[missing] {spot_path}")
        print("Spot series NG.RNGWHHD.D.csv not found. See DATA_COLLECTION.md.")
        return
    spot = load_series_csv(DATA_DIR, SPOT_FILE, value_name="spot")

    fut_end = curve_long["date"].max()
    spot_end = spot["date"].max()
    print(f"Futures data covers through: {fut_end.date()}  (contracts 1..4 only)")
    print(f"Spot data covers through:    {spot_end.date()}")
    print("NOTE: any spot-vs-futures comparison must be scoped to the overlap "
          f"window, i.e. dates <= {fut_end.date()}.\n")

    # ------------------------------------------------------------------
    # 1. Reshape long -> WIDE to build a curve snapshot table.
    #    One row per date, one column per contract (C1..C4).
    #
    #    Package guide (type K): pivot reshapes long->wide.
    #        wide = curve_long.pivot(index="date", columns="contract", values="price")
    #        wide.columns = [f"C{c}" for c in wide.columns]   # tidy names
    #    A "curve snapshot" is ONE such row: the prices C1..C4 observed on a
    #    single day. The shape of that row (rising vs falling across C1->C4) is
    #    what contango/backwardation describe.
    # ------------------------------------------------------------------
    # TODO: build `wide` with pivot, rename columns to C1..C4, and decide how to
    #       handle days where not all four contracts trade (dropna? forward-fill?
    #       -- justify your choice; a snapshot with a missing leg is not a curve).

    # ------------------------------------------------------------------
    # 2. Classify curve shape on each snapshot.
    #    Contango  = later months priced ABOVE nearer months (C4 > C1).
    #    Backwardation = later months BELOW nearer months (C4 < C1).
    #    The simplest summary statistic is the front-to-back spread C4 - C1
    #    (or C2 - C1). You decide which spread defines "shape" for your memo and
    #    whether a small spread should count as "flat".
    #
    #    Package guide (type K): vectorized labeling with np.select / np.sign:
    #        spread = wide["C4"] - wide["C1"]
    #        shape = np.where(spread > 0, "contango",
    #                 np.where(spread < 0, "backwardation", "flat"))
    # ------------------------------------------------------------------
    # TODO: compute your chosen spread column, classify shape, and add both to
    #       the snapshot table. Question: is C4-C1 the right contract pair given
    #       that you only have 4 contracts (~4 months of curve)? Defend it.

    # ------------------------------------------------------------------
    # 3. Save the curve snapshot table.
    #    Deliverable: outputs/futures_curve_snapshots.csv
    #    Each row = one forecast/observation date + C1..C4 + spread + shape.
    # ------------------------------------------------------------------
    # TODO: write your snapshot DataFrame to OUTPUT_DIR / "futures_curve_snapshots.csv"
    #       (DataFrame.to_csv(path)). Make sure `date` is a real column, not lost
    #       in the index (use .reset_index() after the pivot if needed).

    # ------------------------------------------------------------------
    # 4. Plot ONE representative curve snapshot (contract on x, price on y).
    #    Deliverable: outputs/curve_shape_plot.png
    #    A curve plot is x = contract number (1..4), y = price, for a chosen date.
    #
    #    Package guide (type K): save_line_plot expects a long frame with the
    #    x and y columns. Build a 4-row frame for one date:
    #        snap = curve_long[curve_long["date"] == some_date]
    #        save_line_plot(snap, x="contract", y="price",
    #                       title=f"HH futures curve {some_date.date()}",
    #                       output_path=OUTPUT_DIR / "curve_shape_plot.png")
    # ------------------------------------------------------------------
    # TODO: pick a date (e.g. the last fully-populated trading day) and save the
    #       curve plot. State in your report what the shape was on that day.

    # ------------------------------------------------------------------
    # 5. THE TIMING / LEAKAGE TRAP -- futures as a benchmark for spot.
    #
    #    A futures contract's SETTLEMENT today is NOT today's spot, and it is NOT
    #    the spot during its delivery month either. You must pin down EXACTLY which
    #    comparison you are making. Two honest framings (pick ONE and defend it):
    #
    #    (a) SAME-DAY predictive efficiency / basis:
    #        On date t, compare the prompt futures C1(t) to spot(t). Their gap is
    #        the "basis". This is leakage-free (both known on day t) but it does
    #        NOT test whether futures predict future spot -- it just measures the
    #        spot-vs-prompt gap.
    #
    #    (b) DELIVERY-MONTH outcome (predictive test):
    #        Treat C1(t) (or Cn(t)) observed on day t as a *forecast* of spot
    #        ~n months later, then compare to the REALIZED spot around that future
    #        delivery period. This DOES test predictiveness, but every row must
    #        carry BOTH a forecast_origin (=t) AND a target_date (=t + horizon).
    #        LEAKAGE TRAP: never line C1(t) up against spot(t) and call it a
    #        forecast -- that compares a price to itself-ish, not to the future.
    #
    #    Package guide (type K): align two daily series on date with merge_asof
    #    (nearest trading day) or a plain merge after building target_date:
    #        cmp = pd.merge_asof(left.sort_values("target_date"),
    #                            spot.sort_values("date"),
    #                            left_on="target_date", right_on="date",
    #                            direction="nearest")
    #    Metrics: from ng_models.metrics import mae, rmse, summarize_predictions.
    # ------------------------------------------------------------------
    # TODO: (decision E/A/B) Choose framing (a) or (b). Write one sentence:
    #       "I forecast [spot at what horizon] from [origin t] using [which Cn]."
    #       Then build a comparison frame with explicit forecast_origin AND
    #       target_date columns, restricted to the overlap window (<= fut_end).
    # TODO: (decision B) Pick the baseline the futures benchmark must be judged
    #       against -- e.g. random walk spot(t) as the forecast of spot(t+h).
    #       Does the futures curve beat random walk? from ng_models.metrics import the
    #       error functions and report futures-vs-spot errors next to baseline errors.
    # TODO: write outputs/futures_vs_spot_benchmark.csv with columns at least:
    #       [forecast_origin, target_date, contract_used, futures_price,
    #        realized_spot, baseline_forecast].

    print(f"Outputs should be written to: {OUTPUT_DIR}")
    print("Open ASSIGNMENT.md and fill in the TODOs above, then re-run.")


if __name__ == "__main__":
    main()
