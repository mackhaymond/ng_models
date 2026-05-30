# Assignment 13: Optional Bridge: Power Markets, Gas Burn, and ISO Demand

**Phase:** Extensions
**Level:** Advanced / **Optional**
**Estimated time:** 8-16 hours

> This module is OPTIONAL and uses EXTERNAL data (`gridstatus`). It is not
> required for the capstone. Attempt it only if power markets interest you. See
> `DATA_COLLECTION.md` for installing `gridstatus` and fetching/caching ISO data.

## Why this module exists

In much of the U.S., gas-fired plants are the **marginal** (price-setting)
generator: when electricity demand rises or wind/solar fall, gas plants ramp up
and burn more gas. That **power burn** is one of the largest, most weather- and
price-sensitive components of gas demand. So power-grid data is a tempting
*feature* for a gas-price model. The job here is to test that temptation
honestly: does ONE region's power signal actually help forecast the NATIONAL
Henry Hub price, and can you use it **without leakage** and at the **right
frequency and scope**?

## Concepts you'll use

Plain-English, ground-up. Cross-referenced to `docs/GLOSSARY_SEED.md`.

- **ISO / RTO (footprint):** An Independent System Operator runs the grid and
  wholesale power market for a *region* -- a set of states, not the country
  (e.g. ERCOT ~ Texas, CAISO ~ California). The region it covers is its
  "footprint." This matters because the price you forecast (Henry Hub) is
  *national*, but ISO data is *regional*.
- **Load:** Electricity demand, measured in megawatts (MW). It swings with
  weather (AC in summer, heating in winter) and time of day. High load means
  more generation must run, often pulling in gas plants.
- **Generation mix / dispatch:** Which fuels are producing power right now (gas,
  wind, solar, coal, nuclear). The grid "dispatches" cheapest plants first;
  gas is frequently the last unit turned on, so it absorbs the swings.
- **Gas burn / power burn:** Natural gas consumed to make electricity. It rises
  with load and falls when renewables cover more demand. It is gas *demand*, so
  it can tighten the gas balance and (in theory) lift price. See
  `docs/GLOSSARY_SEED.md` -> "Power burn / gas-fired generation as marginal".
- **Renewables displacement:** When wind/solar generate a lot, they push gas off
  the dispatch stack, lowering gas burn even if total load is unchanged. So
  *load alone* under-explains gas burn; the *gas share* of generation is closer.
- **Spark spread:** The (rough) gross margin of a gas plant:
  `power_price - heat_rate * gas_price`, where heat rate (Btu/kWh) is how much
  gas energy it takes to make a unit of electricity. A wide spark spread means
  gas plants are profitable to run, so they burn more gas. You will likely only
  *define* it here, not compute a full version.
- **Frequency mismatch:** ISO data is hourly/real-time; Henry Hub here is
  weekly; the EIA power-gas proxy is monthly. Combining series of different
  frequencies requires an explicit aggregation rule, and the rule (mean vs sum
  vs max) changes what the number *means*.
- **Same-day (same-period) power leakage:** Using power data from the very period
  you are forecasting. That data was not known at the forecast origin, so it
  cannot honestly be a feature. You must **lag** the power series.
- **Causality boundary:** A regional power series can *correlate* with the
  national price without *driving* it -- shared drivers (weather, storage) move
  both. Stay on the correlation side of the line unless you can rule out the
  confounds.

## Package guide

Minimal, concrete API snippets for the libraries this module needs. (Library
*calls* are fair game to look up directly; the modeling *choices* are yours.)

**ng_models helpers (already importable in `main.py`):**

```python
from ng_models.io import load_series_csv          # -> DataFrame['date', <name>]
from ng_models.plotting import save_line_plot      # one y-series per call

power = load_series_csv(DATA_DIR, "NG.N3045TX2.M.csv", value_name="tx_power_gas_mmcf")
save_line_plot(df, x="date", y="col", title="...", output_path=OUTPUT_DIR / "p.png")
```

**pandas -- frequency alignment, lagging, merging:**

```python
# Resample to a regular frequency (needs a DatetimeIndex first):
s = df.set_index("date")["col"]
weekly  = s.resample("W-FRI").mean().reset_index()   # week ending Friday
monthly = s.resample("MS").mean().reset_index()      # MS = month start

# Lag a column (shift DOWN one row so row T holds the prior period's value):
df["col_lag1"] = df["col"].shift(1)

# Merge two series on the date key (inner keeps only overlapping dates):
m = pd.merge(left, right, on="date", how="inner")

# Quick co-movement check (NOT causation, NOT a forecast):
m["a"].corr(m["b"])
```

**gridstatus (optional path -- see `DATA_COLLECTION.md`):**

```python
import gridstatus
iso  = gridstatus.Ercot()
load = iso.get_load(start="2023-06-01", end="2023-09-01")   # 'Time', 'Load' (MW)
mix  = iso.get_fuel_mix(start="2023-06-01", end="2023-09-01") # 'Time' + per-fuel MW
# Method/column names vary by ISO + version -- check the docs page for your ISO.
```

## Data scope

Keep scope small. Pick ONE ISO and a SHORT window (one season).

Expected data inputs:

- **ISO load and/or fuel mix** via `gridstatus` (external -- `DATA_COLLECTION.md`),
  OR the in-repo EIA monthly power-gas proxy (`NG.N3045xx2.M.csv`).
- **Henry Hub spot**, weekly (`NG.RNGWHHD.W.csv`) -- the national benchmark you
  compare against. Regional gas prices, if you collect them, are an alternative.

## Tasks

1. **Choose one ISO** supported by `gridstatus` (or use the EIA proxy) and state
   its footprint. Record why you chose it.
2. **Load** load and/or fuel mix for a limited window. Note units and the native
   frequency (hourly/RT).
3. **Aggregate to a comparable frequency** (e.g. weekly to match HH). Decide and
   justify the aggregator (mean vs sum vs max) for the quantity you chose.
4. **Lag the power feature** so nothing from the target period leaks in. Decide
   the lag from what was knowable at the forecast origin and defend it.
5. **Compare** the lagged regional power metric to Henry Hub (and/or a regional
   gas price). Look at co-movement; resist causal wording.
6. **Decide and write a memo:** should this data enter the core model, or stay
   optional? Address the regional-vs-national scope explicitly.

## Deliverables

- `outputs/iso_weekly_power.csv` (your cached, aggregated ISO data; or the proxy
  file `outputs/proxy_power_gas_vs_hh.csv` if you stay on the EIA path)
- `outputs/power_load_or_fuelmix.png`
- `REPORT.md` (fill in `REPORT_TEMPLATE.md`)

## Rules (non-negotiable standards)

- **No leakage.** Never use power data from the target period as a feature; lag it.
- **Right frequency.** State every series' frequency; justify each aggregation.
- **Forecast origin + target date.** If you build forecast rows, label both.
- **Beat a baseline.** Any forecast must beat a stated naive baseline to count.
- **No causal claims from correlation.** A regional series correlating with the
  national price is a hypothesis, not a mechanism. Name the confound.
- **State what would make it fail.** What out-of-sample regime breaks this?
- Keep raw `data/` immutable; write only under this module's `outputs/`.
- A chart needs a sentence on what it shows AND what it does not show.
- Do not move to a fancier model before the baseline/diagnostic is done.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis, and at what frequency?
- Which ISO/region, what window, what units?
- What was the most important data decision (aggregation? lag? scope?)?
- What result surprised you?
- What would you not trust yet (scope, leakage, sample size)?
- Should this feature enter the core model? Why or why not?
- What should the next assignment investigate?
