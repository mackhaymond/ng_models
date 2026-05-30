"""
Assignment 07: Supply-Demand Balance: Production, Consumption, Trade, and LNG

Build a first-principles monthly natural-gas balance panel (supply, demand,
trade, LNG) and align it with Henry Hub price WITHOUT inventing precision or
leaking future information.

The balance identity that organizes the whole assignment:

    production + imports = consumption + exports + storage_change

(equivalently: production + imports - consumption - exports = storage change.)
Gas cannot vanish, so anything produced or imported that is not consumed or
exported must move into or out of storage. You will assemble the left/right
pieces you can measure and reason about what the residual implies.

Run from repo root:

    uv run python 07_supply_demand_balance/main.py

This file is intentionally INCOMPLETE. It loads the candidate series and shows
ONE worked frequency-alignment example so you can see the pandas API; the
substantive decisions (which series, which aggregation, how to lag for
publication timing, how to compare regimes) are left as TODOs for you to make
and defend in REPORT.md.
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
from ng_models.plotting import save_line_plot

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# Candidate national monthly series confirmed present in data/_metadata.csv.
# These are SUGGESTIONS, not a locked answer: you must inspect the metadata
# (units, frequency, date range), decide which level/variant to use, and write
# a short series_selection note justifying each pick. Note the unit trap:
# N9070US2.M (dry production) is in Million Cubic Feet, while N9070US1.M is the
# SAME quantity in Billion Cubic Feet. Consumption/imports/exports below are all
# Million Cubic Feet (MMcf) -- do NOT mix MMcf and Bcf in one balance.
CANDIDATE_SERIES = {
    "dry_production_mmcf": "NG.N9070US2.M.csv",   # U.S. Dry Natural Gas Production (MMcf)
    "consumption_mmcf": "NG.N9140US2.M.csv",       # U.S. Natural Gas Total Consumption (MMcf)
    "imports_mmcf": "NG.N9100US2.M.csv",           # U.S. Natural Gas Imports (MMcf)
    "exports_mmcf": "NG.N9130US2.M.csv",           # U.S. Natural Gas Exports (MMcf)
}
HENRY_HUB_WEEKLY = "NG.RNGWHHD.W.csv"              # Henry Hub spot, weekly ($/MMBtu)


def main() -> None:
    # ------------------------------------------------------------------
    # Step 0 (do this FIRST, on paper): sketch your panel.
    # Before any code, draw the table you intend to build: one row per MONTH,
    # one column per balance component (supply side, demand side, trade), plus
    # price. Write the balance identity at the top. This forces you to decide
    # what each column means and what unit it is in before pandas hides it.
    # ------------------------------------------------------------------

    metadata = load_metadata(DATA_DIR)

    # The library search is a starting point for discovery. Widen/narrow the
    # keywords yourself; the goal is to FIND the national monthly series, then
    # read off their units/frequency from the metadata, not to trust this list.
    keywords = ["production", "consumption", "imports", "exports", "lng", "electric power"]
    candidates = search_metadata(metadata, keywords)
    print("Candidate fundamentals series (inspect units + frequency):")
    print(candidates[["series_id", "name", "units", "frequency"]].head(40).to_string(index=False))
    print()

    # Verify the suggested files actually exist before going further. If a file
    # is missing, fail with a clear message instead of crashing deep in pandas.
    missing = [fn for fn in list(CANDIDATE_SERIES.values()) + [HENRY_HUB_WEEKLY]
               if not (DATA_DIR / fn).exists()]
    if missing:
        print("Missing expected data files:")
        for fn in missing:
            print(f"  - {fn}")
        print("These national monthly series ship with the repo's data/. If they "
              "are absent, re-check data/_metadata.csv for the correct filenames.")
        return

    # ------------------------------------------------------------------
    # Step 1 (WORKED EXAMPLE -- read this for the pandas API, then reuse it):
    # Aggregate WEEKLY Henry Hub to a MONTHLY series so it can join the monthly
    # fundamentals. Frequency alignment is the core skill of this module.
    #
    # pandas resample API:
    #   s = df.set_index("date")["hh_price"]      # need a DatetimeIndex to resample
    #   monthly = s.resample("MS").mean()          # "MS" = month START, matches the
    #                                              #        YYYY-MM-01 stamps EIA uses
    #   monthly = monthly.reset_index()            # back to a date column
    # .mean() averages the weeks in each month. .last() would take the final
    # week instead -- a DIFFERENT economic choice. You decide mean vs last and
    # justify it (averaging smooths; last() matches an end-of-month snapshot).
    # ------------------------------------------------------------------
    hh_weekly = load_series_csv(DATA_DIR, HENRY_HUB_WEEKLY, value_name="hh_price")
    hh_monthly = (
        hh_weekly.set_index("date")["hh_price"]
        .resample("MS")
        .mean()
        .reset_index()
    )
    print(f"Henry Hub: {len(hh_weekly)} weekly rows -> {len(hh_monthly)} monthly rows "
          f"({hh_monthly['date'].min().date()} to {hh_monthly['date'].max().date()})")
    print()

    # ------------------------------------------------------------------
    # Step 2 (TODO -- you build the panel): load each chosen fundamentals series
    # and join them into ONE monthly DataFrame on the date column.
    #
    # Loading one series (reuse the worked pattern above):
    #   prod = load_series_csv(DATA_DIR, CANDIDATE_SERIES["dry_production_mmcf"],
    #                          value_name="dry_production_mmcf")
    #
    # Joining heterogeneous monthly series -- they start in different years
    # (imports/exports from 1973, consumption from 2001), so an inner join keeps
    # only the overlap. Pattern:
    #   panel = prod.merge(cons, on="date", how="inner").merge(imp, on="date", how="inner")...
    # QUESTION: inner vs outer join here -- what does each do to rows where one
    # series has not started yet, and which keeps your balance columns aligned?
    # Decide and note it in REPORT.md. Do NOT forward-fill a monthly value into
    # months it does not cover just to fill an outer-join gap -- see Step 4.
    #
    # TODO: define net_exports = exports - imports (all MMcf) as a trade column.
    # TODO: confirm every column is in the SAME unit (MMcf) before differencing.

    # ------------------------------------------------------------------
    # Step 3 (TODO -- transformations): for each balance component, compute the
    # comparison that answers your question. These are DIFFERENT questions:
    #   - level:  the raw MMcf this month.
    #   - MoM change:        panel[col].diff()        (this month vs last month)
    #   - YoY change:        panel[col].diff(12)      (this month vs same month
    #                        last year -- removes the seasonal cycle, 12 monthly
    #                        rows = one year)
    #   - YoY % change:      panel[col].pct_change(12)
    # QUESTION: gas demand has a huge winter/summer seasonal swing. Which of
    # these comparisons isolates a genuine shift from normal seasonality? Pick
    # one as your headline comparison and say why the others mislead here.

    # ------------------------------------------------------------------
    # Step 4 (LEAKAGE WARNING -- read before joining price to fundamentals):
    # Monthly EIA fundamentals are published with a LAG of roughly two months
    # (e.g. the Natural Gas Monthly for January data lands in late March). The
    # Henry Hub weekly price for January is known in January. If you put the
    # January price next to the January fundamentals as if both were known at
    # the same time, you have leaked: you used a number nobody had yet.
    #   - A lag is panel[col].shift(k) where k is the publication delay in months.
    #   - Forward-filling a monthly fundamental onto weekly price rows is the
    #     classic version of this bug: you spread a not-yet-published value
    #     across weeks before its release date.
    # TODO: decide the publication lag k for the EIA series, shift the
    # fundamentals by k before any comparison-to-price, and DEFEND k in REPORT.md.
    # (For pure within-fundamentals balance analysis -- all series same vintage --
    # no lag is needed; the lag matters the moment price enters.)

    # ------------------------------------------------------------------
    # Step 5 (TODO -- outputs): once the panel exists, write the deliverables.
    #   panel.to_csv(OUTPUT_DIR / "monthly_balance_panel.csv", index=False)
    #   save_line_plot(panel, x="date", y="<a component>", title="...",
    #                  output_path=OUTPUT_DIR / "balance_components.png")
    #   corr = panel[[<your balance cols>, "hh_price"]].corr()
    #   corr.to_csv(OUTPUT_DIR / "balance_correlations.csv")
    # QUESTION for the correlation table: a high correlation between, say,
    # net exports and price is NOT causation. What confound (e.g. shared trend,
    # the shale era) could drive both? State it before you write any sentence
    # with "because" in it.

    print(f"Outputs should be written to: {OUTPUT_DIR}")
    print("Panel not built yet -- complete Steps 2-5 in main.py.")


if __name__ == "__main__":
    main()
