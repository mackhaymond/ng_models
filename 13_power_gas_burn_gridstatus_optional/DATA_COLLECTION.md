# Data Collection: ISO Power Data (gridstatus) for the Gas-Burn Bridge

## Why this file exists

This module is **optional** and uses **external** data that does NOT ship in
`data/`: hourly electricity **load** and **generation-by-fuel** from a U.S.
Independent System Operator (ISO). That data comes from the `gridstatus` Python
package (https://opensource.gridstatus.io/). This document tells you how to
install it, what to fetch, how to cache it, and where to save it so `main.py`
can read it without edits. It also gives an **EIA electricity alternative** if
you do not want to install `gridstatus` at all.

`main.py` still runs and teaches the pipeline **without any of this** -- it ships
an in-repo "proxy" using EIA monthly gas-to-electric-power deliveries for Texas
(`NG.N3045TX2.M.csv`). That proxy is monthly and coarse; the point of collecting
ISO data is to get the real, high-frequency power signal.

## What is an ISO and which one to pick

An ISO/RTO operates the grid and the wholesale power market for a region (its
**footprint** -- a set of states, not the whole country). Pick **one** and keep
the window **small** at first (one summer, or one cold snap). Good first picks:

- **ERCOT** -- Texas. Self-contained grid, very gas-heavy, big summer swings.
  Roughly matches the in-repo Texas proxy, so you can sanity-check.
- **CAISO** -- California. High solar -> strong "renewables displacement" of gas.
- **PJM / MISO / SPP / ISONE / NYISO** -- also supported; larger/more complex.

The ISO you pick defines your **causality boundary**: you are looking at one
region, but Henry Hub is a **national** benchmark. Choosing the ISO is a modeling
decision -- justify it in `REPORT.md`.

## Install

This repo uses `uv`. From the repo root:

```bash
uv add gridstatus          # adds it to the project
# or, ephemeral:
uv pip install gridstatus
```

Many `gridstatus` endpoints are public and need no key. Some sources (and the
hosted `gridstatus.io` API) require a free API key -- see the docs. Start with a
public ISO method (e.g. ERCOT `get_load`) to avoid keys entirely.

## What to fetch

You need at least ONE of these per chosen ISO, over a small window:

1. **Load** (electricity demand, in **MW**). This is the headline power-demand
   series. Method names vary by ISO; commonly `iso.get_load(start, end)` returns
   a `Time` column plus a `Load` column, usually at 5-minute or hourly cadence.
2. **Generation by fuel** (MW by fuel type: gas, wind, solar, coal, nuclear...).
   Commonly `iso.get_fuel_mix(start, end)` returns `Time` plus one column per
   fuel. The **gas** column is your direct power-burn proxy; (gas / total) is the
   gas **share** of generation.

Minimal worked example (ERCOT, one summer):

```python
import gridstatus
import pandas as pd

iso = gridstatus.Ercot()
load = iso.get_load(start="2023-06-01", end="2023-09-01")   # MW, sub-hourly
load = load.rename(columns={"Time": "ts", "Load": "load_mw"})
load["ts"] = pd.to_datetime(load["ts"], utc=True)

mix = iso.get_fuel_mix(start="2023-06-01", end="2023-09-01")  # MW per fuel
# mix has a 'Time' column and per-fuel columns like 'Natural Gas', 'Wind', ...
```

> API names drift between `gridstatus` versions and ISOs. If a method 404s or a
> column is renamed, check `dir(iso)` and the docs page for your ISO rather than
> guessing. This is a package-API stall (type K) -- look it up, do not fight it.

## Frequency: aggregate hourly -> weekly BEFORE merging with HH

Henry Hub here is **weekly** ($/MMBtu). ISO data is **hourly/RT**. You cannot
merge different frequencies without an explicit aggregation rule, and the rule
**changes the meaning**:

```python
load_weekly = (
    load.set_index("ts")["load_mw"]
        .resample("W-FRI")   # week ending Friday; pick the anchor that aligns w/ HH
        .mean()              # mean=typical level, max=peak, sum=total energy
        .rename("load_mw_weekly")
        .reset_index()
        .rename(columns={"ts": "date"})
)
load_weekly["date"] = load_weekly["date"].dt.tz_localize(None)  # drop tz for merge
```

Choosing `mean` vs `max` vs `sum` is a modeling decision -- justify it for the
quantity you claim the feature represents.

## Leakage: lag the power feature

Power for the week you are forecasting is **not known at the forecast origin**.
Using it is **same-period leakage**. Before merging, lag it to what was knowable:

```python
load_weekly["load_lag1w"] = load_weekly["load_mw_weekly"].shift(1)
```

Decide the lag from "what was actually observable at the origin" and defend it.

## Caching: never re-hit the API every run

Save the aggregated result and read it back on subsequent runs. `main.py` looks
for the cache automatically.

## Where to save it (target schema `main.py` reads)

Save the **weekly aggregated** file here:

`13_power_gas_burn_gridstatus_optional/outputs/iso_weekly_power.csv`

| column | type | unit | example | notes |
|---|---|---|---|---|
| `date` | date `YYYY-MM-DD` | -- | `2023-06-09` | week-ending date (the resample anchor) |
| `load_mw_weekly` | float | MW | `52310.4` | your chosen weekly aggregate of load |
| `gas_gen_mw_weekly` | float | MW | `28110.2` | optional: weekly gas generation |
| `gas_share` | float | fraction 0-1 | `0.54` | optional: gas / total generation |

Raw, un-aggregated dumps can go in a `data/external/iso_demand/` folder you
create **inside this module** -- never in the repo-level `data/` (immutable).

## EIA electricity alternative (no gridstatus install)

If you skip `gridstatus`, EIA publishes **monthly** "Natural Gas Deliveries to
Electric Power Consumers" per state (`NG.N3045xx2.M`, units MMcf) -- already in
`data/` (Texas = `NG.N3045TX2.M.csv`, California = `NG.N3045CA2.M.csv`). This is
the same series `main.py`'s proxy demo uses. Trade-off: it is **monthly** and a
**delivered-volume** measure, not hourly load -- so you lose the within-week
power dynamics that are the whole point of ISO data. State that limitation.

## Collection checklist (data hygiene -- graded)

- [ ] Record **source URL** + **download date** (provenance) in `REPORT.md`.
- [ ] One ISO, small window first; expand only after the pipeline works.
- [ ] Confirm **units** (MW for load/gen; MMcf for EIA volumes) and note them.
- [ ] Parse timestamps as real datetimes; handle the timezone before merging.
- [ ] Choose and **justify** the weekly aggregation (mean/max/sum).
- [ ] **Lag** the power feature so nothing from the target week leaks in.
- [ ] **Cache** the aggregated file to `outputs/iso_weekly_power.csv`.
- [ ] Do not write into the repo-level `data/`.

## Sanity checks after collection

- Weekly load should track weather: ERCOT summer peaks far above shoulder weeks.
- Gas share should rise when load is high or wind/solar is low (dispatch logic).
- A regional power series correlating with national HH does **not** prove the
  region moves the price -- weather and storage drive both. Keep it a hypothesis.
