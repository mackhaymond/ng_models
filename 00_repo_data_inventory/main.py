"""Assignment 00: Repository and Natural Gas Data Inventory.

GOAL
----
Before you can forecast anything, you have to know what data you have. This
module is a guided "inventory" of the EIA-style natural-gas catalog in
``data/``. You will:

1. Load the catalog (``data/_metadata.csv``) with correctly-parsed dates.
2. Count series by frequency and by units (these run as a working demo).
3. Find CANDIDATE series for the things a gas model cares about (price,
   storage, production, consumption, imports/exports, LNG) -- YOUR TODO.
4. Open a few candidate files and confirm their shape -- YOUR TODO.
5. Plot a simple summary -- YOUR TODO.

You do NOT re-implement the loaders. ``load_metadata``, ``search_metadata`` and
``load_series_csv`` already exist in ``ng_models.io`` -- you USE them to explore.

Run from the repo root:

    uv run python 00_repo_data_inventory/main.py

The demo portion (load + frequency/units counts) runs and writes
``outputs/frequency_counts.csv`` and ``outputs/top_units.csv`` as-is. The TODO
portions are guided stubs for you to complete.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt

# --- Make the shared library importable -------------------------------------
# Every module follows this same pattern: resolve paths relative to THIS file
# (__file__), never relative to wherever you happen to run from. Then put
# ``src/`` on the import path so ``from ng_models...`` works.
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from ng_models.paths import data_dir, ensure_output_dir
from ng_models.io import load_metadata, search_metadata, load_series_csv

# data_dir() walks up from HERE to find the repo root, so this works no matter
# the current working directory. OUTPUT_DIR is created if it does not exist.
DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")


def main() -> None:
    # ------------------------------------------------------------------
    # 0. Guard: this module needs data/_metadata.csv. If it is missing,
    #    print an actionable message and exit cleanly (do not crash).
    # ------------------------------------------------------------------
    meta_path = DATA_DIR / "_metadata.csv"
    if not meta_path.exists():
        print(f"Could not find {meta_path}.")
        print("This module reads the data catalog shipped in the repo's data/ folder.")
        print("Make sure you are running from the repo root and that data/ is present.")
        return

    # ==================================================================
    # PART A -- WORKING DEMO (runs as-is). Read it; it is your template.
    # ==================================================================

    # load_metadata parses start_date/end_date from 8-digit integers
    # (e.g. 20100101) into real datetimes. You do NOT implement this.
    metadata = load_metadata(DATA_DIR)
    print(f"Loaded catalog: {metadata.shape[0]} series, columns = {list(metadata.columns)}")
    print(metadata.head())

    # Count series by frequency. value_counts() tallies each distinct value;
    # dropna=False so missing frequencies are visible, not silently dropped.
    # A/M/W/D = annual / monthly / weekly / daily.
    freq_counts = metadata["frequency"].value_counts(dropna=False)
    print("\nSeries by frequency:")
    print(freq_counts)
    # .rename_axis names the index column; reset_index turns the Series into a
    # 2-column DataFrame so the CSV has headers instead of a bare index.
    freq_counts.rename_axis("frequency").reset_index(name="n_series").to_csv(
        OUTPUT_DIR / "frequency_counts.csv", index=False
    )

    # Top 15 units. Same pattern. Units tell you what each number MEANS
    # (Bcf, MMcf, $/MMBtu, ...) and which series can be compared.
    top_units = metadata["units"].value_counts(dropna=False).head(15)
    print("\nTop 15 units:")
    print(top_units)
    top_units.rename_axis("units").reset_index(name="n_series").to_csv(
        OUTPUT_DIR / "top_units.csv", index=False
    )

    # ==================================================================
    # PART B -- YOUR TODOs. Guided stubs below. Fill them in.
    # ==================================================================

    # ------------------------------------------------------------------
    # TODO 1 (candidate-series selection): build a table of series that
    # are plausibly useful for natural-gas modeling.
    #
    # search_metadata(metadata, keywords) returns the rows whose combined
    # series_id/name/description/units text contains ANY of the keywords
    # (case-insensitive substring, logical OR). Example call:
    #
    #     hits = search_metadata(metadata, ["henry hub", "rngwhhd"])
    #
    # Decide which categories matter and which keywords surface the RIGHT
    # series for each (price, storage/working gas, production, consumption,
    # imports, exports, LNG). Broad keywords return thousands of rows -- you
    # must judge which series_ids are actually the headline series vs noise.
    #
    # Leading question: for each category, which ONE or TWO series_ids would
    # you actually feed a model, and why those over the hundreds of regional
    # / sectoral variants the search also returns?
    #
    # Build a DataFrame with these columns and write it to
    # outputs/candidate_series.csv (index=False):
    #   series_id, name, description, units, frequency,
    #   start_date, end_date, filename, why_relevant
    # where why_relevant is YOUR one-line note (the search cannot write it).
    #
    # Pattern to get you started (you choose the categories/keywords and the
    # filtering down to headline series):
    #
    #   rows = []
    #   for category, keywords in CATEGORY_KEYWORDS.items():
    #       hits = search_metadata(metadata, keywords)
    #       # ... pick the headline row(s) you care about from `hits` ...
    #       # ... append with a why_relevant note ...
    #   candidates = pd.DataFrame(rows)
    #   candidates.to_csv(OUTPUT_DIR / "candidate_series.csv", index=False)
    #
    # candidates = ...

    # ------------------------------------------------------------------
    # TODO 2 (verify file shape): open 3-5 of your candidate files and
    # confirm they really have Date,Value columns and sane coverage.
    #
    # load_series_csv(DATA_DIR, filename, value_name="...") returns a tidy
    # frame with columns ["date", value_name], sorted by date. It RAISES if
    # the file is missing Date/Value, so a clean load IS your verification.
    # Example:
    #
    #     hh = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="henry_hub")
    #     print(hh.shape, hh["date"].min(), hh["date"].max())
    #
    # Leading question: does the row_count in metadata match len() of the
    # loaded series? If not, what does that tell you about the metadata?

    # ------------------------------------------------------------------
    # TODO 3 (one summary plot): make at least one chart summarizing the
    # catalog -- e.g. number of series per frequency as a bar chart.
    #
    # save_line_plot in ng_models.plotting draws LINES; for a bar chart use
    # matplotlib directly:
    #
    #     fig, ax = plt.subplots(figsize=(7, 4))
    #     freq_counts.plot(kind="bar", ax=ax)          # Series.plot is easiest
    #     ax.set_title("Series count by frequency")
    #     ax.set_xlabel("frequency"); ax.set_ylabel("n_series")
    #     fig.tight_layout()
    #     fig.savefig(OUTPUT_DIR / "frequency_bar.png", dpi=150)
    #     plt.close(fig)
    #
    # Leading question: what does this chart show about which frequencies
    # dominate the catalog -- and what does it NOT tell you about how useful
    # those series are for forecasting weekly Henry Hub?

    print(f"\nOutputs written to: {OUTPUT_DIR}")
    print("Wrote frequency_counts.csv and top_units.csv. "
          "Complete the TODOs to add candidate_series.csv and a plot.")


if __name__ == "__main__":
    main()
