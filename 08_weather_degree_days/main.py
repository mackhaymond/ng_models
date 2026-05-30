"""
Assignment 08: Weather Demand — Heating and Cooling Degree Days

Run from the repo root:

    uv run python 08_weather_degree_days/main.py

WHAT THIS MODULE DOES
---------------------
Weather is the single largest short-run driver of natural-gas demand: cold days
mean heating load (furnaces, much of it gas), hot days mean power-sector cooling
load (air conditioning, much of it gas-fired generation). This module turns raw
temperature into the industry-standard demand proxies -- Heating Degree Days
(HDD) and Cooling Degree Days (CDD) -- and aggregates them to a weekly frequency
you can later line up against Henry Hub prices.

EXTERNAL DATA
-------------
There is NO weather data in the repo's data/ folder. You collect it once and
cache it as a CSV. See DATA_COLLECTION.md in this folder for the exact steps,
the NOAA token setup, and the expected file location/schema. If the cached file
is absent, this script prints a clear pointer and exits cleanly (exit 0) -- it
never crashes.

This file is an INCOMPLETE guided starter. The plumbing (path resolution, file
detection, schema auto-detect, demo aggregation) is wired for you. The modeling
DECISIONS -- which weather variable, what base temperature, sum vs mean when
aggregating, how to define an anomaly, whether to claim weather "causes" price
moves -- are left as TODOs WITH guidance. You make and defend those calls.
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
from ng_models.features import hdd_cdd_from_tavg

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# Where DATA_COLLECTION.md tells you to cache the collected weather file.
WEATHER_CSV = DATA_DIR / "external" / "degree_days" / "weather_daily.csv"


def load_weather_daily(path: Path) -> pd.DataFrame:
    """Load the cached daily weather file and normalize it to date + hdd + cdd.

    Accepts either schema documented in DATA_COLLECTION.md:
      - date, tavg_f            -> HDD/CDD derived here via hdd_cdd_from_tavg
      - date, hdd, cdd          -> already pre-computed by the source
    Returns a date-sorted frame with columns: date, hdd, cdd (and tavg_f if it
    was provided).
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "date" not in df.columns:
        raise ValueError(
            f"{path.name} must have a 'date' column. Found: {list(df.columns)}"
        )
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df = df.sort_values("date").reset_index(drop=True)

    if {"hdd", "cdd"}.issubset(df.columns):
        # Source already provides degree days.
        return df

    if "tavg_f" not in df.columns:
        raise ValueError(
            f"{path.name} must have either ('tavg_f') or ('hdd','cdd'). "
            f"Found: {list(df.columns)}. See DATA_COLLECTION.md."
        )

    # TODO (decision E -- base temperature): hdd_cdd_from_tavg defaults to a 65 F
    # base. 65 F is the U.S. industry convention (see ASSIGNMENT 'Concepts'), but
    # it is an assumption, not a law of nature. Keep 65 unless you can justify a
    # different balance point for your region -- and if you change it, say why in
    # the report.
    dd = hdd_cdd_from_tavg(df["tavg_f"], base_f=65.0)
    out = df.copy()
    out["hdd"] = dd["hdd"].to_numpy()
    out["cdd"] = dd["cdd"].to_numpy()
    return out


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Confirm the external weather data has been collected.
    # ------------------------------------------------------------------
    if not WEATHER_CSV.exists():
        print("No cached weather data found.")
        print(f"Expected file: {WEATHER_CSV}")
        print(
            "This is an EXTERNAL-DATA module. Follow "
            "08_weather_degree_days/DATA_COLLECTION.md to collect daily weather "
            "from the NOAA CDO API (free token) and cache it at the path above, "
            "then re-run this script."
        )
        return  # clean exit (0) -- do not crash on missing optional data

    weather = load_weather_daily(WEATHER_CSV)
    print(f"Loaded {len(weather)} daily weather rows "
          f"({weather['date'].min().date()} -> {weather['date'].max().date()}).")

    # ------------------------------------------------------------------
    # 2. Aggregate DAILY degree days to WEEKLY.
    # ------------------------------------------------------------------
    # API note (pandas resample): to roll a daily series up to weeks ending on
    # Friday (to line up with the weekly Henry Hub series, which is W-FRI):
    #     weekly = (weather.set_index("date")
    #                      .resample("W-FRI")
    #                      .agg({...})
    #                      .reset_index())
    #
    # TODO (decision C -- aggregation operator): HDD and CDD are *additive* energy
    # quantities (degree-days accumulate over the week). Mean would tell you the
    # average daily intensity; SUM gives total weekly heating/cooling need. Decide
    # which one matches "how much demand did this week create" and use it for hdd
    # and cdd. Write one sentence in REPORT.md defending the choice.
    #
    # Replace the operator below with your chosen aggregation.
    AGG = "mean"  # <-- placeholder so the script runs; CHANGE THIS and justify it
    weekly = (
        weather.set_index("date")
        .resample("W-FRI")
        .agg({"hdd": AGG, "cdd": AGG})
        .reset_index()
    )
    print(f"Aggregated to {len(weekly)} weekly rows using agg='{AGG}' "
          "(revisit whether mean is the right operator -- see TODO).")

    # ------------------------------------------------------------------
    # 3. Build a weather NORMAL and an ANOMALY.
    # ------------------------------------------------------------------
    # A 'normal' is the typical value for that point in the calendar; an 'anomaly'
    # is actual minus normal -- the *surprise* that actually moves markets.
    #
    # API note: week-of-year via the shared helper is add_calendar_columns; for a
    # quick normal you can group by ISO week:
    #     weekly["iso_week"] = weekly["date"].dt.isocalendar().week.astype(int)
    #     normal = weekly.groupby("iso_week")["hdd"].transform("mean")
    #
    # TODO (decision E/A -- normal definition + leakage): a *full-sample* mean uses
    # future years to define "normal" for an early week -- fine for a descriptive
    # plot, NOT fine if this anomaly ever becomes a model feature (that is
    # leakage; see module 09). Decide: is this anomaly purely descriptive here, or
    # a future predictor? If predictor, you must build the normal from PAST years
    # only (expanding/trailing). State your choice in the report.
    weekly["iso_week"] = weekly["date"].dt.isocalendar().week.astype(int)
    weekly["hdd_normal"] = weekly.groupby("iso_week")["hdd"].transform("mean")
    weekly["hdd_anomaly"] = weekly["hdd"] - weekly["hdd_normal"]

    # ------------------------------------------------------------------
    # 4. (Optional) Line the weekly weather up against Henry Hub.
    # ------------------------------------------------------------------
    # The weekly Henry Hub spot series IS in the repo: NG.RNGWHHD.W.csv.
    #     hh = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="hh_spot")
    # TODO (decisions C + J): the HH 'date' may not land exactly on W-FRI -- align
    # on the week, not the raw timestamp (e.g. resample HH to W-FRI too, or
    # merge_asof). Then, if you observe that cold (high-HDD) weeks coincide with
    # price strength, write it as an ASSOCIATION, not "cold weather causes price
    # spikes": storage level, supply outages, and expectations are confounders you
    # have not controlled. This is the correlation-vs-causation standard.

    # ------------------------------------------------------------------
    # 5. Save outputs.
    # ------------------------------------------------------------------
    features_path = OUTPUT_DIR / "weather_features.csv"
    weekly.to_csv(features_path, index=False)
    print(f"Wrote {features_path}")

    # API note (plotting): the shared helper draws a single line:
    #     from ng_models.plotting import save_line_plot
    #     save_line_plot(weekly, x="date", y="hdd_anomaly",
    #                    title="Weekly HDD anomaly", output_path=plot_path)
    # TODO: produce outputs/weather_anomaly_plot.png and write one sentence about
    # what it shows AND what it does not show (one station is not the nation).
    plot_path = OUTPUT_DIR / "weather_anomaly_plot.png"
    print(f"(TODO) Save an anomaly plot to: {plot_path}")

    print(f"Outputs directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
