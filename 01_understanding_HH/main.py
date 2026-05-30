"""Assignment 01 - Understanding weekly Henry Hub before modeling.

This is an EXPLORATORY DATA ANALYSIS (EDA) script. Before fitting any forecast
model, you look at the target series itself: weekly Henry Hub natural gas spot
price ($/MMBtu, EIA series NG.RNGWHHD.W).

What this script does (and what you will extend):
  1. Loads the weekly Henry Hub series from data/ via the shared ng_models helpers.
  2. Plots the full-sample price history so you can see regimes, spikes, and
     volatility clustering over ~1997-present.
  3. Computes an "average price by week-of-year" curve -- a first, crude look at
     calendar seasonality -- and plots it.
  4. (TODO, yours) Prints summary statistics and decides what they imply for a
     first baseline model.

The point is NOT to predict anything yet. It is to understand the series well
enough to (a) pick an honest first baseline and (b) state what would make that
baseline fail. You record those judgments in REPORT_TEMPLATE.md.

Run from the repo root:
    cd /Users/mackhaymond/code/projects/ng_models && uv run python 01_understanding_HH/main.py
"""

import sys
from pathlib import Path

import pandas as pd
import matplotlib

# Use a non-interactive backend so the script runs headless (no display / no
# blocking window). We save figures to files instead of calling plt.show().
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- Make the shared library importable, then resolve paths through it. -------
# ng_models lives in src/. Inserting it on sys.path lets `from ng_models...`
# work no matter what directory you launched python from.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ng_models.paths import data_dir, ensure_output_dir  # noqa: E402
from ng_models.io import load_series_csv  # noqa: E402

# data_dir(__file__) walks up from THIS file to the repo root and returns
# <repo>/data -- so the script works from the repo root or anywhere else.
# (Do NOT hardcode "../data/..."; that only works from inside this folder.)
DATA_DIR = data_dir(Path(__file__))
OUTPUT_DIR = ensure_output_dir(Path(__file__).resolve().parent / "outputs")

HH_FILE = "NG.RNGWHHD.W.csv"  # weekly Henry Hub spot, $/MMBtu


def main() -> None:
    # --- Load -----------------------------------------------------------------
    # load_series_csv handles date parsing + chronological sort for you, and
    # checks the file exists. It returns a tidy frame with columns
    # ["date", <value_name>]. If the file is missing, fail with a clear message
    # rather than a traceback.
    path = DATA_DIR / HH_FILE
    if not path.exists():
        print(f"Missing input: {path}")
        print("The weekly Henry Hub file should already be in data/. "
              "If not, re-pull the EIA data for this repo.")
        return

    df = load_series_csv(DATA_DIR, HH_FILE, value_name="price")
    # Now: df["date"] is datetime64, df["price"] is float, sorted ascending.

    # --- Plot 1: full-sample price history ------------------------------------
    # The single most important EDA plot for this module. Look for: long flat
    # vs. spiky stretches (volatility clustering), big spikes, and whether the
    # average LEVEL shifts and stays shifted (a regime) vs. cycles each year.
    price_fig, price_ax = plt.subplots(figsize=(12, 6))
    price_ax.plot(df["date"], df["price"])
    price_ax.set_title("Henry Hub Natural Gas Spot Price (Weekly)")
    price_ax.set_ylabel("$/MMBtu")
    price_ax.xaxis.set_major_locator(mdates.YearLocator(5))
    price_ax.grid(True)
    price_fig.tight_layout()
    price_fig.savefig(OUTPUT_DIR / "HH_price_weekly.png", dpi=150)
    plt.close(price_fig)

    # --- Average price by week-of-year ----------------------------------------
    # This collapses ~29 years onto a single 1..53 calendar axis by averaging
    # every "week 3", every "week 4", etc. It is a FIRST look at seasonality,
    # but be skeptical of it (see ASSIGNMENT.md "Concepts you'll use"):
    #   - isocalendar().week (1..52/53) groups by ISO week-of-year; .dt.month
    #     would be coarser. You are using week-of-year here.
    #   - A plain MEAN lets a handful of spike-years dominate a calendar week.
    #
    # TODO (decision -- taxonomy type I, seasonality vs regime): the mean curve
    # below mixes calm years with shock years. Add a second curve so you can SEE
    # whether the seasonal shape is robust or spike-driven. A median-by-week is a
    # natural robust comparison:
    #     by_week_median = df.groupby(df["date"].dt.isocalendar().week)["price"].median()
    # Decide which summary tells the seasonality story honestly, and say why in
    # your report. (Do not just trust the mean.)
    averaged_week_of_year = (
        df.groupby(df["date"].dt.isocalendar().week)["price"]
        .mean()
        .rename_axis("Week")
        .reset_index(name="price")
    )
    # Map week number -> a plotting date in a dummy year so the x-axis reads as
    # calendar months instead of 1..53.
    averaged_week_of_year["PlotDate"] = pd.Timestamp("2024-01-01") + pd.to_timedelta(
        (averaged_week_of_year["Week"].astype(int) - 1) * 7, unit="D"
    )

    average_fig, average_ax = plt.subplots(figsize=(12, 6))
    average_ax.plot(averaged_week_of_year["PlotDate"], averaged_week_of_year["price"])
    average_ax.set_title("Average Henry Hub Price by Week of Year")
    average_ax.set_xlim(
        mdates.date2num(pd.Timestamp("2024-01-01")),
        mdates.date2num(pd.Timestamp("2024-12-31")),
    )
    average_ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    average_ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    average_ax.set_ylabel("$/MMBtu")
    average_ax.grid(True)
    average_fig.tight_layout()
    average_fig.savefig(OUTPUT_DIR / "HH_average_price_by_week.png", dpi=150)
    plt.close(average_fig)

    # --- Summary statistics ---------------------------------------------------
    # TODO (API is free help; the INTERPRETATION is yours):
    #   pandas gives you everything in one call -- df["price"].describe() returns
    #   count/mean/std/min/25%/50%/75%/max. Individually:
    #       df["price"].mean(), .median(), .std(), .min(), .max(), .count()
    #   Print the ones the assignment asks for (count, min, max, mean, median,
    #   std) and copy them into REPORT_TEMPLATE.md.
    #
    # The harder question (taxonomy type B/I -- you decide, don't let the agent
    # decide for you): the mean (~$4) sits well above the median (~$3.4) and the
    # std is large relative to the mean. What does a fat right tail of spikes do
    # to a model that assumes prices hover near their average? Use that to argue
    # for or against forecasting the price LEVEL directly.
    #
    # print(df["price"].describe())

    # --- Baseline decision ----------------------------------------------------
    # TODO (decision -- taxonomy type B, which baseline must I beat): the report
    # ends with "My first benchmark model should be ___ because ___." Candidates:
    #   - naive / random walk: next week = this week
    #   - seasonal-naive: next week = same week last year (52-week lag)
    #   - rolling mean
    #   - simple ETS / Holt-Winters
    # Use the two plots above to justify your pick. Ask yourself: given how much
    # of the variation is spikes/regimes rather than a clean repeating calendar
    # cycle, is seasonal-naive actually a strong null here, or just an easy one?
    # Write the one-sentence recommendation in REPORT_TEMPLATE.md.

    print(f"Loaded {len(df)} weekly observations "
          f"({df['date'].min().date()} to {df['date'].max().date()}).")
    print(f"Saved plots to: {OUTPUT_DIR}")
    print("Next: fill in summary stats + the baseline recommendation in REPORT_TEMPLATE.md.")


if __name__ == "__main__":
    main()
