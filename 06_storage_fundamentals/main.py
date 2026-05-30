"""Assignment 06: Storage Fundamentals — Inventories, Seasonality, and Deviations.

Run from the repo root:

    uv run python 06_storage_fundamentals/main.py

WHAT THIS MODULE IS ABOUT
-------------------------
Weekly working gas in underground storage is the running "bank balance" of the US
gas market. This starter loads the EIA Lower-48 storage series and weekly Henry Hub
price, and scaffolds the four things you must produce:
  1. a leakage-checked weekly panel of price + storage,
  2. weekly storage change + injection/withdrawal classification,
  3. a storage deviation from a PAST-ONLY seasonal norm (the five-year-average idea),
  4. two plots and an economic interpretation in REPORT.md.

This file is intentionally INCOMPLETE. The data loading, path handling, and plotting
boilerplate are done for you. The MODELING DECISIONS — exactly how to build the
leakage-safe seasonal norm, how to classify flows, how to align the series, and how to
interpret the result — are left as TODOs with inline guidance. Make and defend those
calls yourself; that is the graded part.

Key standards enforced in this module (see ASSIGNMENT.md):
  - five-year average / seasonal norm must use PRIOR YEARS ONLY (no centering, no future).
  - EIA publishes Thursday for the week ending the prior Friday: storage cannot explain
    an earlier price. State this; lag storage if you build any predictive feature.
  - Bcf (volume) and $/MMBtu (rate) are incommensurable: never combine them arithmetically.
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
from ng_models.time_utils import add_calendar_columns

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# The Lower-48 anchor series and the weekly Henry Hub price. Both are weekly and share
# Friday-ending date stamps from 2010-01-01 onward.
STORAGE_FILE = "NG.NW2_EPG0_SWO_R48_BCF.W.csv"   # Lower 48, Working Gas, Bcf, weekly
HH_FILE = "NG.RNGWHHD.W.csv"                      # Henry Hub spot, $/MMBtu, weekly


def main() -> None:
    # ------------------------------------------------------------------ #
    # 0. Check inputs exist. Both ship in data/; fail cleanly if not.
    # ------------------------------------------------------------------ #
    missing = [f for f in (STORAGE_FILE, HH_FILE) if not (DATA_DIR / f).exists()]
    if missing:
        print("Missing required data file(s):", ", ".join(missing))
        print(f"Expected them in: {DATA_DIR}")
        print("These ship with the repo. If absent, re-pull data/ or see the repo README.")
        return

    # ------------------------------------------------------------------ #
    # 1. Metadata search: CONFIRM the series rather than trusting memory.
    #    (search_metadata OR-matches any keyword against id/name/desc/units.)
    # ------------------------------------------------------------------ #
    metadata = load_metadata(DATA_DIR)
    candidates = search_metadata(metadata, ["storage", "working gas", "underground"])
    print("Storage-related series in the catalog (look for the Lower 48 anchor):")
    print(candidates[["series_id", "name", "units", "frequency", "filename"]].head(25))
    print()
    # TODO(task 1): From the printout, record in REPORT.md the anchor series id, its
    #   UNITS and FREQUENCY (read them from metadata, do not assume), and which rows are
    #   the regional sub-series. Question: the Lower-48 total should equal the sum of the
    #   regional series — does it, and why might it not exactly?

    # ------------------------------------------------------------------ #
    # 2. Load both series and ALIGN them.
    #    load_series_csv returns tidy [date, <value_name>] sorted by date.
    # ------------------------------------------------------------------ #
    storage = load_series_csv(DATA_DIR, STORAGE_FILE, value_name="storage_bcf")
    hh = load_series_csv(DATA_DIR, HH_FILE, value_name="hh_price")

    # TODO(task 2): Build `panel` by joining storage and hh on "date".
    #   API: panel = storage.merge(hh, on="date", how="inner")
    #   Decision to make + defend in REPORT.md: inner join (overlap only, 2010+) vs.
    #   ffill vs. pd.merge_asof. Why is the inner join safe HERE specifically? (Hint:
    #   both series already share Friday-ending stamps.) What would force you to use
    #   merge_asof instead?
    panel = storage.merge(hh, on="date", how="inner")
    panel = panel.sort_values("date").reset_index(drop=True)
    panel = add_calendar_columns(panel, date_col="date")  # adds year, month, iso_week, ...

    if panel.empty:
        print("Join produced an empty panel — check the date columns line up.")
        return
    print(f"Panel: {len(panel)} weekly rows, {panel['date'].min().date()} -> "
          f"{panel['date'].max().date()}")

    # ------------------------------------------------------------------ #
    # 3. Weekly storage change + injection/withdrawal classification.
    # ------------------------------------------------------------------ #
    # API: a week-over-week change is panel["storage_bcf"].diff() (NaN on the first row).
    panel["storage_change_bcf"] = panel["storage_bcf"].diff()
    # TODO(task 3): Classify each week as "injection" vs "withdrawal" from the SIGN of
    #   storage_change_bcf. Decide how to treat an exactly-zero / NaN week and justify it.
    #   API sketch: np.where(panel["storage_change_bcf"] > 0, "injection", "withdrawal")
    #   Then SANITY-CHECK: group flow_type by month and confirm injections cluster in
    #   summer (Apr-Oct) and withdrawals in winter (Nov-Mar). If they don't, your sign or
    #   your dates are wrong.
    panel["flow_type"] = np.nan  # <-- replace with your classification

    # ------------------------------------------------------------------ #
    # 4. Storage deviation from a PAST-ONLY seasonal norm (the five-year-average idea).
    #    THIS IS THE LEAKAGE-CRITICAL STEP. See ASSIGNMENT.md "leakage trap".
    # ------------------------------------------------------------------ #
    # The norm for week-of-year w in year Y must average week-w values from years STRICTLY
    # BEFORE Y. No centering, no current-year value, no future weeks.
    #
    # A leakage-safe shape (groupby week-of-year, expanding mean over prior years, shifted
    # so the current year is excluded):
    #
    #   g = panel.groupby("iso_week")["storage_bcf"]
    #   panel["seasonal_norm"] = g.transform(lambda s: s.expanding().mean().shift(1))
    #
    # TODO(task 4): Decide and IMPLEMENT your norm. Open questions you must answer in the
    #   report:
    #     - 5 prior years (a true "five-year average") or ALL prior years? How would you
    #       cap an expanding mean at the last 5? (Hint: .rolling(5).mean() AFTER a shift,
    #       grouped by iso_week — but rolling counts ROWS, and within an iso_week group
    #       each row is a different year, so 5 rows == 5 prior years.)
    #     - What do you do for the early years (2010-2014) where fewer than 5 prior years
    #       exist — NaN, or use what you have? Defend it.
    #     - iso_week vs. month as the seasonal grain — which and why?
    #   Then compute the deviation = actual - norm:
    panel["seasonal_norm"] = np.nan          # <-- replace with your leakage-safe norm
    panel["storage_deviation_bcf"] = panel["storage_bcf"] - panel["seasonal_norm"]

    # ------------------------------------------------------------------ #
    # 5. Save the panel and the two plots.
    # ------------------------------------------------------------------ #
    panel_path = OUTPUT_DIR / "storage_panel.csv"
    panel.to_csv(panel_path, index=False)
    print(f"Wrote {panel_path}")

    # 5a. Seasonality plot: storage level by week-of-year, one line per year. This shows
    #     the repeating annual cycle the norm is meant to capture.
    fig, ax = plt.subplots(figsize=(11, 5))
    for yr, sub in panel.groupby("year"):
        ax.plot(sub["iso_week"], sub["storage_bcf"], alpha=0.6, label=str(int(yr)))
    ax.set_xlabel("ISO week of year")
    ax.set_ylabel("Working gas in storage (Bcf)")
    ax.set_title("Lower-48 storage seasonality by year")
    ax.legend(ncol=3, fontsize=7)
    seasonality_path = OUTPUT_DIR / "storage_seasonality.png"
    fig.savefig(seasonality_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {seasonality_path}")

    # 5b. Price vs. deviation on TWO y-axes (Bcf and $/MMBtu are incommensurable, so they
    #     must NOT share a scale). Only meaningful once task 4 fills seasonal_norm.
    if panel["storage_deviation_bcf"].notna().any():
        fig, ax1 = plt.subplots(figsize=(11, 5))
        ax1.plot(panel["date"], panel["hh_price"], color="tab:blue")
        ax1.set_ylabel("Henry Hub ($/MMBtu)", color="tab:blue")
        ax2 = ax1.twinx()
        ax2.plot(panel["date"], panel["storage_deviation_bcf"], color="tab:red", alpha=0.7)
        ax2.set_ylabel("Storage deviation vs norm (Bcf)", color="tab:red")
        ax2.axhline(0.0, color="grey", linewidth=0.8, linestyle="--")
        ax1.set_title("Henry Hub price vs. storage deviation from seasonal norm")
        dev_path = OUTPUT_DIR / "hh_vs_storage_deviation.png"
        fig.savefig(dev_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(f"Wrote {dev_path}")
    else:
        print("Skipped hh_vs_storage_deviation.png: seasonal_norm not implemented yet "
              "(finish task 4).")

    # TODO(task 5): In REPORT.md, write the economic interpretation. A deviation BELOW
    #   zero (deficit) is conventionally read as bullish, ABOVE zero (surplus) bearish.
    #   But: is what you see correlation, prediction, or causation? Name the confounds
    #   (weather, production) and state what this plot CANNOT show. Do NOT write a causal
    #   claim the chart can't support.

    print(f"\nOutputs written to: {OUTPUT_DIR}")
    print("Next: finish the TODOs (flow_type, leakage-safe seasonal_norm) and write REPORT.md.")


if __name__ == "__main__":
    main()
