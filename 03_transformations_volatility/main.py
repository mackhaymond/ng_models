"""
Assignment 03: Levels, Log Prices, Returns, and Volatility

Goal of this module
--------------------
Take the weekly Henry Hub spot price and build the standard set of
*transformations* you will use for the rest of the curriculum:

    level  ->  log price  ->  difference  ->  log return  ->  rolling volatility

Along the way you decide WHICH transformation answers WHICH question
("where will the price be?" vs. "how big is the next move?") and you
look at when the series is volatile (volatility clustering) and what the
most extreme weekly moves were.

Run from repo root:

    uv run python 03_transformations_volatility/main.py

This file is an INTENTIONALLY INCOMPLETE guided starter. The plumbing
(paths, loading, saving) is wired up for you. The TODOs marked
`# DECISION:` are the modeling decisions you must make and defend in
REPORT.md -- the starter will not make them for you. The TODOs marked
`# API:` are just library mechanics; the inline comments tell you the
exact pandas/numpy/matplotlib call to use.
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

# Shared library. Resolve paths through ng_models.paths so the script runs
# from the repo root regardless of where the data physically lives -- never
# hard-code "../data".
from ng_models.paths import data_dir, ensure_output_dir
from ng_models.io import load_series_csv

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# The only input this module needs: weekly Henry Hub spot price.
HH_FILE = "NG.RNGWHHD.W.csv"

# DECISION: the rolling-volatility window, in ROWS (this series is weekly, so
# a window of W rows == W weeks). A common analyst choice is 52 (one year) so
# the volatility line is a "trailing 12-month" view, but 13 (a quarter) or 26
# (half year) react faster. Pick ONE, set it here, and justify the choice in
# REPORT.md: a longer window is smoother but lags regime changes; a shorter
# window is noisier but catches spikes sooner. See HINTS / Concepts in
# ASSIGNMENT.md (taxonomy type E, "which transformation/target").
VOL_WINDOW = 52


def add_transformations(hh: pd.DataFrame) -> pd.DataFrame:
    """Build the level/log/difference/return/volatility columns.

    Input `hh` has columns `date` (datetime64) and `hh_price` (float),
    already sorted ascending by date (load_series_csv guarantees this).
    Return a NEW DataFrame -- do not mutate the raw load.
    """
    df = hh.copy()

    # --- Guardrail: logs are only defined for strictly positive numbers. ---
    # API: assert there are no non-positive prices before you call np.log.
    # A spot price <= 0 would make log(price) NaN/-inf and silently corrupt
    # every return below it. If this assertion ever fires, investigate the
    # raw row rather than dropping it blindly.
    assert (df["hh_price"] > 0).all(), (
        "Found a non-positive Henry Hub price; log price is undefined. "
        "Inspect the raw rows before continuing."
    )

    # API: np.log(...) is the NATURAL log (base e). Element-wise over a Series.
    df["log_price"] = np.log(df["hh_price"])

    # DECISION + API: weekly *change in level*, in $/MMBtu.
    #   df["hh_price"].diff()  -> y_t - y_{t-1}
    # The FIRST row is NaN because there is no prior week to subtract. That NaN
    # is correct and expected -- do NOT fill it with 0 (that would invent a
    # week with no change). Decide in REPORT.md how you handle that first row
    # for downstream stats (typically: leave it NaN and let .describe() skip it).
    # TODO: df["price_diff"] = ...

    # DECISION + API: weekly LOG RETURN = log(y_t) - log(y_{t-1}) = log(y_t/y_{t-1}).
    #   df["log_price"].diff()    (equivalently np.log(df["hh_price"]).diff())
    # Same first-row NaN logic. A log return of 0.05 ~= a +5% week. Returns are
    # closer to stationary than the level -- you will argue why in REPORT.md.
    # TODO: df["log_return"] = ...

    # API: absolute return = the SIZE of the move, ignoring direction.
    #   df["log_return"].abs()
    # This is your "how big was the move" column; you'll use it for top moves
    # and as the raw material for volatility.
    # TODO: df["abs_return"] = ...

    # DECISION + API: rolling volatility = rolling standard deviation of the
    # log return over VOL_WINDOW weeks.
    #   df["log_return"].rolling(VOL_WINDOW).std()
    # Notes:
    #   - The first (VOL_WINDOW-1) values are NaN: not enough history yet. That
    #     is correct; do not backfill.
    #   - rolling().std() uses sample std (ddof=1) by default.
    #   - This is realized volatility in *log-return units per week*. Whether to
    #     annualize (multiply by sqrt(52)) is YOUR call -- state your unit.
    # TODO: df["roll_vol"] = ...

    return df


def top_absolute_moves(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the n largest weekly moves over the FULL sample.

    DECISION: define a "move". The brief offers two valid definitions:
      (a) abs(log_return)  -- a percentage-style move (scale-free), or
      (b) abs(price_diff)  -- a dollar move ($/MMBtu).
    These rank weeks differently: (b) favors high-price eras, (a) is
    comparable across the whole history. Pick ONE, and in REPORT.md say which
    and why. "Top moves" means the largest over the ENTIRE series, not within
    a rolling window.

    Each row of the output MUST carry the date so a reader can look the event
    up -- a magnitude with no date is not auditable.
    """
    # API: sort by your chosen move column descending, take the head.
    #   move_col = "abs_return"  # or "price_diff"-derived absolute column
    #   out = df.dropna(subset=[move_col]).sort_values(move_col, ascending=False).head(n)
    #   return out[["date", "hh_price", "log_return", "abs_return"]]
    # TODO: implement and return a small DataFrame including `date`.
    raise NotImplementedError("Define 'move', then return the top-n rows including date.")


def plot_volatility_panels(df: pd.DataFrame, output_path: Path) -> Path:
    """Multi-panel figure: price level, weekly change, rolling volatility.

    API guidance (matplotlib): a stacked 3-row figure that shares the x-axis
    makes the three views line up by date so you can SEE that big changes and
    high volatility cluster together.

        fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
        axes[0].plot(df["date"], df["hh_price"]);  axes[0].set_ylabel("$/MMBtu")
        axes[0].set_title("Henry Hub level")
        axes[1].plot(df["date"], df["log_return"]); axes[1].set_ylabel("log return")
        axes[1].set_title("Weekly log return")
        axes[2].plot(df["date"], df["roll_vol"]);   axes[2].set_ylabel("vol")
        axes[2].set_title(f"Rolling volatility ({VOL_WINDOW}w)")
        fig.tight_layout(); fig.savefig(output_path, dpi=150); plt.close(fig)

    (You may instead make three separate plots with ng_models.plotting.
    save_line_plot -- but the shared x-axis is what makes clustering visible.)
    """
    # TODO: build the 3-panel figure described above and save to output_path.
    # Then in REPORT.md add ONE sentence per panel: what it shows AND what it
    # does not show (e.g. "the level plot hides that 2008 and 2021 had similar
    # volatility at very different price levels").
    raise NotImplementedError("Build and save the 3-panel volatility figure.")


def main() -> None:
    # --- Load (plumbing done for you) ---------------------------------------
    hh_path = DATA_DIR / HH_FILE
    if not hh_path.exists():
        print(
            f"Could not find {HH_FILE} in {DATA_DIR}.\n"
            "This module needs the weekly Henry Hub series shipped in data/. "
            "See the repo data inventory (00_repo_data_inventory) / "
            "docs/DATA_SOURCE_NOTES.md to restore it, then re-run."
        )
        return

    hh = load_series_csv(DATA_DIR, HH_FILE, value_name="hh_price")
    print(f"Loaded {len(hh)} weekly rows: {hh['date'].min().date()} -> {hh['date'].max().date()}")

    # --- Transform ----------------------------------------------------------
    df = add_transformations(hh)

    # Guard: until you fill in the transformation TODOs, the columns the rest of
    # main() needs won't exist. Detect that and stop cleanly with a pointer,
    # so a fresh `uv run` exits 0 instead of crashing with a KeyError.
    required = ["price_diff", "log_return", "abs_return", "roll_vol"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(
            "Transformation columns not built yet: "
            + ", ".join(missing)
            + ".\nFill in the TODOs in add_transformations(), then re-run to "
            "produce the outputs and plots."
        )
        return

    # --- Compare summary stats (DECISION: which stats, and read them) -------
    # API: df[[...]].describe() gives count/mean/std/min/quartiles/max.
    # DECISION: in REPORT.md, contrast the LEVEL vs the DIFFERENCE vs the
    # LOG RETURN. Look at how mean and std behave: the level has a big nonzero
    # mean and drifts; differences/returns center near zero. That is the
    # ground-up evidence for "model returns, not levels" -- argue it.
    stats = df[["hh_price", "price_diff", "log_return"]].describe()
    print("\nSummary stats (level vs change vs log return):")
    print(stats)

    # --- Top absolute moves -------------------------------------------------
    moves = top_absolute_moves(df, n=10)
    print("\nTop 10 absolute weekly moves:")
    print(moves)

    # --- Save outputs -------------------------------------------------------
    transformed_path = OUTPUT_DIR / "transformed_hh.csv"
    moves_path = OUTPUT_DIR / "top_moves.csv"
    plot_path = OUTPUT_DIR / "volatility_plot.png"

    df.to_csv(transformed_path, index=False)
    moves.to_csv(moves_path, index=False)
    plot_volatility_panels(df, plot_path)

    print(f"\nWrote: {transformed_path}")
    print(f"Wrote: {moves_path}")
    print(f"Wrote: {plot_path}")
    print(f"\nAll outputs in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
