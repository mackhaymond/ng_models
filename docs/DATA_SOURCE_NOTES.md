# Data Source Notes

## External source anchors

Use these as curriculum anchors; do not treat them as exhaustive.

- EIA Open Data / API documentation: https://www.eia.gov/opendata/documentation.php
- EIA Open Data **API key registration** (free, instant): https://www.eia.gov/opendata/register.php
- EIA Natural Gas Data page: https://www.eia.gov/naturalgas/data.php
- EIA Henry Hub weekly spot price page: https://www.eia.gov/dnav/ng/hist/rngwhhdw.htm
- EIA weekly natural gas storage report: https://www.eia.gov/naturalgas/storage/
- EIA NYMEX natural gas futures price page: https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm
- NOAA Climate Data Online (CDO) API documentation: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
- NOAA CDO **API token request**: https://www.ncdc.noaa.gov/cdo-web/token
- National Weather Service degree-day definition: https://www.weather.gov/key/climate_heat_cool
- CME Henry Hub Natural Gas futures product/specification page: https://www.cmegroup.com/markets/energy/natural-gas/natural-gas.contractSpecs.html
- gridstatus open-source documentation: https://opensource.gridstatus.io/

> **If a link breaks (these hosts drift over time):** NOAA folded NCDC into
> **NCEI** — the CDO `ncdc.noaa.gov/cdo-web/...` endpoints still resolve, but if
> one 404s, search "NOAA CDO web services" or try the `ncei.noaa.gov` equivalent.
> CME and gridstatus pages are bot-protected and may block scripted fetches even
> though they load fine in a browser — open them manually. The EIA series in
> `data/` are already downloaded, so none of these are needed for the core
> (non-collection) modules.

## Source policy

- Prefer official data sources for core assignments.
- Use cached CSVs for reproducibility once a download path is proven.
- Record retrieval date, URL/API route, units, frequency, and any transformations.
- **Never commit API tokens.** Put NOAA/EIA/other keys in a `.env` file or an
  environment variable and keep that file out of git. If a token ever lands in a
  commit, treat it as compromised and rotate it.

## Current local data

The repository already ships a `data/` directory with **16,041 EIA CSVs** plus a
`data/_metadata.csv` index. Every series file has exactly two columns,
`Date,Value`, sorted by date. The frequency is encoded in the series id and
filename suffix: `.D` = daily, `.W` = weekly, `.M` = monthly, `.A` = annual.

The first assignments should use these local files before adding any external
data. Loading one is a one-liner in pandas:

```python
import pandas as pd
# parse_dates makes Date a real datetime; index_col sets it as the row index
hh = pd.read_csv("data/NG.RNGWHHD.D.csv", parse_dates=["Date"], index_col="Date")
hh = hh.sort_index()          # never assume CSV row order; enforce it
hh["Value"]                   # the price column
```

The sections below enumerate the series that are actually present, grouped by
category, with the exact ids/filenames, units, frequency, and coverage. "Use
first" notes point you at the right series for each curriculum stage.

### Henry Hub spot price (the price target)

Henry Hub is the U.S. benchmark spot price for natural gas. It is available at
four frequencies, all derived from the same underlying daily series.

| Series id | Filename | Units | Frequency | Coverage |
|---|---|---|---|---|
| `NG.RNGWHHD.D` | `NG.RNGWHHD.D.csv` | $/MMBtu | Daily | 1997 – 2026 |
| `NG.RNGWHHD.W` | `NG.RNGWHHD.W.csv` | $/MMBtu | Weekly | 1997 – 2026 |
| `NG.RNGWHHD.M` | `NG.RNGWHHD.M.csv` | $/MMBtu | Monthly | 1997 – 2026 |
| `NG.RNGWHHD.A` | `NG.RNGWHHD.A.csv` | $/MMBtu | Annual | 1997 – 2026 |

Which frequency for which module:

- **Calendar baselines and first plots (modules 01–02):** monthly `.M` or weekly
  `.W` — fewer points, clearer seasonality, less noise to fight.
- **Transformations, volatility, returns (module 03):** weekly `.W` — module 03's
  scope is the weekly series (it stays consistent with the weekly target used from
  module 02 onward). Weekly returns already show fat tails and volatility
  clustering clearly. The daily `.D` series is available if you want to *explore*
  finer-grained variation, but it is optional and not what the assignment grades.
- **Backtesting and the ML/capstone forecast (modules 04, 10, 14):** weekly `.W`
  is the recommended default target. It aligns with the weekly storage release
  and gives enough history without daily noise. Use `.D` only if a module
  explicitly calls for it.

### Storage (the most important fundamental)

Working gas in underground storage, reported by EIA every week in billion cubic
feet (Bcf). The Lower-48 total is the headline number the market trades on.

- **Anchor series — use this first:** `NG.NW2_EPG0_SWO_R48_BCF.W`
  (`NG.NW2_EPG0_SWO_R48_BCF.W.csv`), Lower-48 total working gas, **Bcf**,
  **weekly**, from **2010**.

The 8 regional `NW2` series below decompose that total. Use them only after the
Lower-48 anchor when a module asks about regional balances. All are Bcf, weekly,
from 2010 (exact ids are in `data/_metadata.csv`; filenames follow the
`NG.NW2_EPG0_SWO_R<region>_BCF.W.csv` pattern):

- East
- Midwest
- Mountain
- Pacific
- South Central (total)
- South Central — salt
- South Central — nonsalt
- (plus the Lower-48 total above)

Storage is a *stock* (a level at a point in time). The weekly *change* in storage
is the injection (positive, spring–fall) or withdrawal (negative, winter) and is
usually the more informative modeling input — compute it with `.diff()`.

### Supply and demand balance

Monthly and annual physical flows. Monthly `.M` is the right default for
balance work; annual `.A` is for long-run context only.

| Quantity | Series id | Units | Frequency | Notes |
|---|---|---|---|---|
| Dry gas production | `NG.N9070US.M`, `NG.N9070US.A` | MMcf | Monthly / Annual | Total U.S. supply, the biggest driver of the multi-year price trend |
| Total consumption | `NG.N9140US.M`, `NG.N9140US.A` | MMcf | Monthly / Annual | Total U.S. demand |
| Imports | `NG.N9100US.M` (+ `.A`) | MMcf | Monthly / Annual | Mostly pipeline from Canada |
| Exports | `NG.N9130US.M` (+ `.A`) | MMcf | Monthly / Annual | Pipeline + LNG |
| LNG series | 98 separate `NG.*` series | MMcf | Monthly / Annual | LNG exports/imports detail; see `_metadata.csv`. Use only after the core four above. |

A rough monthly balance is `production + imports - consumption - exports`, which
should track the net change in storage. Units are MMcf for these flows but Bcf
for storage — 1 Bcf = 1,000 MMcf, so convert before comparing.

### Power-burn proxy

Natural gas delivered to electric power producers — the single most
weather-sensitive demand component (gas burned to run power plants, especially
for summer air-conditioning load).

- `NG.N3045*` series (`NG.N3045US.M` for the U.S. total, plus state-level
  `N3045<state>` series), **MMcf**, **monthly**. Use the U.S. total first; treat
  it as a proxy for power-sector demand, not an exact burn measurement.

### Futures (market expectations — but STALE locally)

NYMEX Henry Hub futures settlement prices for the first four contract months.

| Series id | Filename | Units | Frequency |
|---|---|---|---|
| `NG.RNGC1` | `NG.RNGC1.{D,W,M,A}.csv` | $/MMBtu | D/W/M/A |
| `NG.RNGC2` | `NG.RNGC2.{D,W,M,A}.csv` | $/MMBtu | D/W/M/A |
| `NG.RNGC3` | `NG.RNGC3.{D,W,M,A}.csv` | $/MMBtu | D/W/M/A |
| `NG.RNGC4` | `NG.RNGC4.{D,W,M,A}.csv` | $/MMBtu | D/W/M/A |

**Two important limitations of the local copy:**

1. **STALE:** the data ends **2024-04-05**. It is not current.
2. **Only 4 contract months** (C1–C4), so you have at most the near 4 months of
   the curve, not the full ~12+ month strip the market actually quotes.

Use these for historical "did the curve anticipate the move?" exercises only.
For any current or full-curve work (module 11), collect fresh data externally —
see below.

## Publication lags & information availability

The single most important discipline in this course is the **what-was-known-then
rule**: when you build a feature or backtest a forecast for some date `t`, you may
only use information that had actually been *published* by `t`. Real data arrives
late. If you join a value to date `t` that was not released until `t + lag`, you
have leaked the future into your model and your backtest is fiction.

Known publication lags for these sources:

- **EIA weekly storage:** released **Thursdays at 10:30am ET** and reports the
  level as of the **prior Friday**. So the storage number you can act on this
  week describes gas in the ground nearly a week earlier — lag the series
  accordingly before using it as a feature.
- **EIA monthly production / consumption / flows (`N9070`, `N9140`, `N9100`,
  `N9130`, `N3045`):** lag roughly **2 months**. The figure for a given month is
  not published until about two months after that month ends, and is revised
  afterward.
- **CME / NYMEX futures settlement:** daily settlement is published around
  **2:30pm CT** each trading day. A given day's settle is not known until after
  the close, so do not use today's settle as an input to a same-day forecast made
  in the morning.
- **NOAA weather (HDD/CDD, observed temperatures):** typically a **1–2 day** lag
  for finalized observations; forecasts are available forward but are themselves
  uncertain.

Translate each lag into a concrete shift on the series (in pandas, `.shift()` on
the appropriately-resampled series) so that every feature value carries a date no
later than when it was actually knowable.

## External data to collect

Three gaps in the local data must be filled from external sources. Download into
`data/` (or a sibling folder), record the retrieval date and exact URL/route, and
keep tokens out of git.

- **Weather (HDD/CDD) — not present in EIA at all.** Collect from NOAA Climate
  Data Online (CDO). API docs: https://www.ncdc.noaa.gov/cdo-web/webservices/v2 —
  requires a free token (env var, never commit). Degree-day definitions:
  https://www.weather.gov/key/climate_heat_cool
- **Current / full futures curve.** The local `RNGC1-4` data is stale to
  2024-04 and only 4 contracts. Get the current strip from CME
  (https://www.cmegroup.com/markets/energy/natural-gas/natural-gas.contractSpecs.html)
  or refresh from EIA (https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm).
- **ISO power-market data (optional, module 13).** Use gridstatus
  (https://opensource.gridstatus.io/). Scope to one ISO and one question.

## EIA data

EIA is the primary source for U.S. natural gas spot prices, storage, production,
consumption, imports, exports, the power-burn proxy, and the (stale) futures
price series — all enumerated above.

## NOAA / NWS weather data

Weather enters through temperature, heating degree days, cooling degree days, and
anomalies versus normals. There is no weather in the local data, so this is the
first external collection task. Keep weather work simple at first.

## CME / futures data

Futures prices should be treated as market prices for contract delivery months,
not guaranteed forecasts. The local copy is stale and shallow; collect a current
full curve before drawing conclusions about today's market expectations.

## gridstatus

Use only for optional power-market extensions. Keep scope to one ISO and one
question.
