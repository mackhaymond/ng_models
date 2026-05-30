"""
Assignment 13 (OPTIONAL): Power Markets, Gas Burn, and ISO Demand.

WHAT THIS MODULE IS ABOUT
-------------------------
Natural gas is the swing fuel in much of the U.S. power grid: when electricity
demand rises or renewables fall, gas-fired plants ramp up and burn more gas.
That "power burn" is one of the biggest demand categories for gas, so power-grid
data is a candidate *feature* for a gas-price model. This module is a guided
exploration of whether ONE region's power data carries usable signal for the
NATIONAL Henry Hub (HH) price -- and, crucially, whether it would still be
honest (no leakage) and meaningful (right region, right frequency) if you used it.

It is OPTIONAL. It pulls in EXTERNAL data via the `gridstatus` package (one ISO's
load / generation-by-fuel). Installing `gridstatus` and collecting that data is
described in DATA_COLLECTION.md. So this module can run and teach even before you
install anything, main.py ships TWO paths:

  PATH 1 (always runs): an in-repo proxy demo using EIA monthly "Natural Gas
          Deliveries to Electric Power Consumers" for Texas (a stand-in for the
          ERCOT footprint), already in data/. It shows the *shape* of the
          analysis -- aggregate, lag, merge with HH, compare -- with zero
          external dependencies.

  PATH 2 (commented, optional): a worked `gridstatus` ERCOT fetch + weekly
          aggregation + merge with HH. It is intentionally left as a guided,
          commented sketch + TODOs. Enable it only after reading
          DATA_COLLECTION.md and installing the package.

Run from the repo ROOT:

    uv run python 13_power_gas_burn_gridstatus_optional/main.py

This file is intentionally INCOMPLETE. The substantive decisions -- which region,
which power metric, how to lag it against the forecast origin, whether the signal
is national or only regional -- are left to you as TODOs with guidance.
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

# In-repo proxy for the ERCOT footprint: EIA monthly gas delivered to electric
# power consumers in Texas. Units = Million Cubic Feet (MMcf). This is NOT the
# same as hourly ISO load -- it is a coarse monthly stand-in so the pipeline is
# demonstrable without gridstatus. The real ISO data comes via DATA_COLLECTION.md.
PROXY_POWER_GAS_FILE = "NG.N3045TX2.M.csv"   # Texas, deliveries to electric power, monthly, MMcf
HH_WEEKLY_FILE = "NG.RNGWHHD.W.csv"          # Henry Hub spot, weekly, $/MMBtu


def run_proxy_demo() -> None:
    """PATH 1 -- runs with only in-repo data. A SHAPE demo, not the assignment.

    This shows the analysis skeleton you will mirror with real ISO data:
    load a power-sector gas series, load HH, align frequency, LAG the power
    series, merge, and look at co-movement. The decisions are still yours.
    """
    power_path = DATA_DIR / PROXY_POWER_GAS_FILE
    hh_path = DATA_DIR / HH_WEEKLY_FILE
    if not power_path.exists() or not hh_path.exists():
        print(f"Proxy inputs missing under {DATA_DIR} -- skipping proxy demo.")
        return

    # load_series_csv returns columns ['date', <value_name>], sorted by date.
    power = load_series_csv(DATA_DIR, PROXY_POWER_GAS_FILE, value_name="tx_power_gas_mmcf")
    hh = load_series_csv(DATA_DIR, HH_WEEKLY_FILE, value_name="hh_spot_usd_mmbtu")

    # --- Frequency mismatch (taxonomy C) ----------------------------------
    # The proxy is MONTHLY; HH here is WEEKLY. Real ISO load is HOURLY. You can
    # never merge series at different frequencies without an explicit rule.
    # Below we bring HH to a monthly mean so the proxy demo can merge cleanly.
    # API: set a DatetimeIndex, then .resample('MS').mean() (MS = month-start).
    hh_monthly = (
        hh.set_index("date")["hh_spot_usd_mmbtu"]
        .resample("MS")  # MS = calendar month start, matching EIA monthly stamps
        .mean()
        .rename("hh_spot_usd_mmbtu")
        .reset_index()
    )
    # TODO(decision: aggregation -- taxonomy C): for the REAL hourly ISO load you
    # collect, is .mean() the right weekly aggregator, or .sum(), or .max()?
    # A monthly AVERAGE price vs a monthly SUM of burn answer different questions.
    # Decide and justify per variable in REPORT.md.

    # --- Leakage / timing (taxonomy A) ------------------------------------
    # The point of this module: power data observed for month T must NOT be used
    # to "predict" the HH price of that SAME month T -- that is same-period
    # leakage. A feature must be known at the forecast origin (the end of the
    # prior period). We demonstrate a 1-period lag below.
    # API: .shift(1) moves a column DOWN one row (so row T now holds month T-1).
    power = power.copy()
    power["tx_power_gas_mmcf_lag1"] = power["tx_power_gas_mmcf"].shift(1)
    # TODO(decision: lag choice -- taxonomy A/D): is a 1-MONTH lag the right
    # alignment? EIA publishes the electric-power deliveries figure with a
    # MULTI-MONTH reporting delay. What lag k actually reflects "known at the
    # forecast origin"? Decide k from the publication schedule and defend it.

    merged = pd.merge(power, hh_monthly, on="date", how="inner").dropna(
        subset=["tx_power_gas_mmcf_lag1", "hh_spot_usd_mmbtu"]
    )
    if merged.empty:
        print("Proxy merge produced no overlapping rows -- check date alignment.")
        return

    # A correlation is NOT causation and NOT a forecast (taxonomy J/B).
    corr_lagged = merged["tx_power_gas_mmcf_lag1"].corr(merged["hh_spot_usd_mmbtu"])
    print("[proxy demo] Texas power-sector gas (lag 1mo) vs national HH monthly mean")
    print(f"[proxy demo]   overlapping months : {len(merged)}")
    print(f"[proxy demo]   correlation (lagged): {corr_lagged:+.3f}")
    print("[proxy demo]   NOTE: this is ONE state vs the NATIONAL price -- a")
    print("[proxy demo]   regional series need not move the national HH. See")
    print("[proxy demo]   the causality-boundary task in ASSIGNMENT.md.")

    # Save a small artifact so the rest of the module has something to inspect.
    proxy_out = merged[["date", "tx_power_gas_mmcf_lag1", "hh_spot_usd_mmbtu"]]
    proxy_csv = OUTPUT_DIR / "proxy_power_gas_vs_hh.csv"
    proxy_out.to_csv(proxy_csv, index=False)
    print(f"[proxy demo] wrote {proxy_csv}")

    # save_line_plot(df, x, y, title, output_path) -> Path. One series per call.
    save_line_plot(
        merged,
        x="date",
        y="tx_power_gas_mmcf_lag1",
        title="Texas power-sector gas deliveries (lag 1mo), MMcf -- PROXY for ERCOT",
        output_path=OUTPUT_DIR / "proxy_power_gas.png",
    )


def run_gridstatus_example() -> None:
    """PATH 2 -- the REAL assignment, using external ISO data. Guarded + guided.

    This is the work you submit. It needs the `gridstatus` package and a network
    fetch (or cached file). If the package is absent, it prints a pointer and
    returns cleanly so `main.py` always exits 0. See DATA_COLLECTION.md.
    """
    try:
        import gridstatus  # noqa: F401
    except ImportError:
        print(
            "[gridstatus path] `gridstatus` is not installed. This path is "
            "OPTIONAL.\n"
            "  To attempt it: read 13_power_gas_burn_gridstatus_optional/"
            "DATA_COLLECTION.md\n"
            "  then `uv add gridstatus` (or `uv pip install gridstatus`)."
        )
        return

    # If a cached fetch exists, prefer it (never hammer the API on every run).
    cache_path = OUTPUT_DIR / "iso_weekly_power.csv"
    if cache_path.exists():
        iso_weekly = pd.read_csv(cache_path, parse_dates=["date"])
        print(f"[gridstatus path] loaded cached ISO data: {cache_path}")
    else:
        print(
            "[gridstatus path] gridstatus is installed but no cached file at\n"
            f"  {cache_path}. Follow DATA_COLLECTION.md to fetch + cache, then "
            "re-run."
        )
        # ----- WORKED FETCH SKETCH (commented; you complete + uncomment) -----
        # Choose ONE ISO and a SMALL window first (debugging on a year of data
        # is painful and rude to the API). ERCOT and CAISO are good first picks.
        #
        # iso = gridstatus.Ercot()
        # # get_load returns a DataFrame with a 'Time' column + 'Load' (MW),
        # # typically at 5-min / hourly resolution.
        # raw = iso.get_load(start="2023-06-01", end="2023-09-01")
        # raw = raw.rename(columns={"Time": "ts", "Load": "load_mw"})
        # raw["ts"] = pd.to_datetime(raw["ts"], utc=True)
        #
        # TODO(decision: frequency mismatch -- taxonomy C): hourly/RT load vs
        # weekly HH. Pick a weekly aggregation that matches what you claim the
        # feature MEANS (peak demand -> max? total energy -> sum? typical
        # level -> mean?). Justify it.
        #   iso_weekly = (
        #       raw.set_index("ts")["load_mw"]
        #          .resample("W-FRI")        # week ending Friday, to align w/ HH
        #          .mean()                    # <-- your choice; defend it
        #          .rename("load_mw_weekly")
        #          .reset_index()
        #          .rename(columns={"ts": "date"})
        #   )
        #   iso_weekly["date"] = iso_weekly["date"].dt.tz_localize(None)
        #   iso_weekly.to_csv(cache_path, index=False)   # cache it!
        return

    # ----- MERGE WITH HENRY HUB + ANALYSIS (you complete) -------------------
    hh = load_series_csv(DATA_DIR, HH_WEEKLY_FILE, value_name="hh_spot_usd_mmbtu")
    # TODO(decision: leakage -- taxonomy A): SAME-DAY/SAME-WEEK power is the
    # classic leak here. Power for the week you are forecasting is not known at
    # the forecast origin. LAG the ISO feature before merging:
    #     iso_weekly["load_lag1w"] = iso_weekly["load_mw_weekly"].shift(1)
    # Decide the lag from "what was knowable at the origin", then defend it.
    #
    # TODO(decision: scope / causality boundary -- taxonomy J): you are relating
    # ONE ISO to the NATIONAL HH. Before any "load drives price" wording, ask:
    # could a regional ISO move a national benchmark? What confound (weather,
    # storage) drives both? State this as a hypothesis in REPORT.md, not a claim.
    #
    # TODO(decision: baseline -- taxonomy B): if you ever turn this into a
    # forecast, what naive baseline must the power-augmented model beat? A model
    # with a regional feature that does not beat random-walk HH adds nothing.
    print("[gridstatus path] HH loaded; complete the lag+merge+analysis TODOs.")
    _ = hh  # silence unused warning until you wire up the merge


def main() -> None:
    print("Assignment 13 is OPTIONAL (power markets / ISO demand bridge).\n")
    print("=== PATH 1: in-repo proxy demo (Texas power-sector gas vs HH) ===")
    run_proxy_demo()
    print("\n=== PATH 2: gridstatus ISO example (optional, external data) ===")
    run_gridstatus_example()
    print(f"\nAll generated files go to: {OUTPUT_DIR}")
    print("See DATA_COLLECTION.md before attempting the gridstatus path.")


if __name__ == "__main__":
    main()
