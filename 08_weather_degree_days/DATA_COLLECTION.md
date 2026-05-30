# Data Collection — Assignment 08: Weather (Degree Days)

This module needs **weather data**, which is NOT shipped in the repo's `data/`
folder. Weather is *external* data: you collect it once, cache it as a CSV, and
`main.py` picks it up automatically on the next run. This file is the
authoritative, step-by-step guide for getting that file.

You do not need a perfect national dataset to pass. **One representative station
or division, documented honestly, is enough.** The point is the pipeline
(collect → cache → HDD/CDD → aggregate), not data-vendor heroics.

---

## What `main.py` looks for

`main.py` expects a single cached CSV here:

```
data/external/degree_days/weather_daily.csv
```

It accepts **either** of these schemas (it auto-detects which one you have):

| Schema | Required columns | Meaning |
|---|---|---|
| Temperature | `date`, `tavg_f` | daily average temperature in °F; main.py derives HDD/CDD via `hdd_cdd_from_tavg` |
| Pre-computed degree days | `date`, `hdd`, `cdd` | daily HDD and CDD already computed by the source |

Rules for the file:

- `date` is one row **per day**, ISO format `YYYY-MM-DD`.
- `tavg_f` is degrees **Fahrenheit** (NOAA's `TAVG` is often in tenths of °C —
  convert it; see below).
- No commas-as-thousands, no header junk above the column row.
- Keep the RAW download too (e.g. `weather_daily_raw.csv`) so your cleaning is
  reproducible. Never edit the raw file by hand.

If the file is missing, `main.py` prints a pointer to this document and exits
cleanly (exit 0). It does **not** crash.

---

## Source option A — NOAA Climate Data Online (CDO) API (recommended)

Authoritative docs: <https://www.ncdc.noaa.gov/cdo-web/webservices/v2>

### 1. Get a free token

Request one at <https://www.ncdc.noaa.gov/cdo-web/token>. It arrives by email
in seconds. The token is a secret — treat it like a password.

### 2. Store the token in an environment variable (never commit it)

Create a file named `.env` in the **repo root** (it is gitignored — confirm with
`git check-ignore .env`; if it is not ignored, add `.env` to `.gitignore`
before saving the token):

```
NOAA_CDO_TOKEN=your_token_here
```

Load it in your shell before running, or read it in Python:

```python
import os
token = os.environ["NOAA_CDO_TOKEN"]   # raises if you forgot to set it — good
```

Never hard-code the token in `main.py` or `DATA_COLLECTION.md`.

### 3. Pick a station and a date range

Use the GHCND (Global Historical Climatology Network — Daily) dataset and the
`TAVG` (daily average temp) datatype. A good single-station starting point is a
major demand center, e.g. Chicago O'Hare: `GHCND:USW00094846`. Browse stations
at <https://www.ncdc.noaa.gov/cdo-web/datasets/GHCND/locations>.

Match the weather date range to your Henry Hub price range so the join later has
overlap (HH weekly runs ~1997→present).

### 4. Pull the data (CDO caps each request at ~1000 rows and 1 year)

```python
import os, requests, pandas as pd

token = os.environ["NOAA_CDO_TOKEN"]
base = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
headers = {"token": token}

frames = []
for year in range(2015, 2024):           # loop years to stay under limits
    params = {
        "datasetid": "GHCND",
        "stationid": "GHCND:USW00094846",  # Chicago O'Hare
        "datatypeid": "TAVG",
        "startdate": f"{year}-01-01",
        "enddate":   f"{year}-12-31",
        "units":     "standard",           # 'standard' => Fahrenheit
        "limit": 1000,
    }
    r = requests.get(base, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    results = r.json().get("results", [])
    frames.append(pd.DataFrame(results))

raw = pd.concat(frames, ignore_index=True)
raw.to_csv("data/external/degree_days/weather_daily_raw.csv", index=False)
```

Gotchas:
- `units="standard"` returns °F. If you omit it, NOAA returns **tenths of °C**;
  convert with `tavg_f = value/10 * 9/5 + 32`.
- The API throttles; add a short `time.sleep(0.3)` between requests if you loop
  many years.
- `TAVG` is missing at some stations — if so, pull `TMAX` and `TMIN` and use
  `tavg_f = (tmax + tmin) / 2` (this is the standard NWS approximation).

### 5. Reshape to the cached schema and save

```python
import os
os.makedirs("data/external/degree_days", exist_ok=True)
clean = (
    raw.rename(columns={"date": "date", "value": "tavg_f"})
       .assign(date=lambda d: pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d"))
       .loc[:, ["date", "tavg_f"]]
       .sort_values("date")
)
clean.to_csv("data/external/degree_days/weather_daily.csv", index=False)
```

---

## Source option B — NOAA / NWS pre-computed degree-day tables

NWS Climate Prediction Center publishes degree-day products (population-weighted
HDD/CDD by region and nationally):
<https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/degree_days/>

These are already in degree-day units (no temperature conversion needed). If you
download a daily/weekly table, reshape it to `date, hdd, cdd` and save to the
same path. These tables are *population-weighted* — note that in your report; it
is exactly the weighting the assignment asks you to reason about.

---

## Source option C — any cached CSV you already trust

If you already have a clean daily temperature or degree-day file from another
project, just reshape it to one of the two schemas above and drop it at
`data/external/degree_days/weather_daily.csv`. Document the source and station in
your `REPORT.md`. Synthetic/sample data is acceptable for wiring up the pipeline
**only if you label it as such** and do not draw market conclusions from it.

---

## Verifying your file

```bash
head -3 data/external/degree_days/weather_daily.csv
# date,tavg_f
# 2015-01-01,18.0
# 2015-01-02,22.5
```

Then run the module from the repo root:

```bash
uv run python 08_weather_degree_days/main.py
```

If the file is found, `main.py` will compute HDD/CDD, aggregate to weekly, and
write `outputs/weather_features.csv`.
