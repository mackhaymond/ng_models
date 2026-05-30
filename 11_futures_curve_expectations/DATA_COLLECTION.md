# Data Collection: Current NYMEX Henry Hub Futures Curve

## Why this file exists

The futures series shipped in `data/` (`NG.RNGC1.D` .. `NG.RNGC4.D`) are **stale
and shallow**:

- they **end on 2024-04-05**, and
- they give you only **4 contract months** (~4 months of curve depth).

That is enough to learn the mechanics (snapshot, shape, basis, benchmark) on the
**overlap window `<= 2024-04-05`**. But if you want a *current* or *deeper* curve
(12+ contracts, present day) you must collect it yourself. This document gives
the schema, the sources, and where to save the result so the rest of the module
(and `main.py`) can consume it without changes.

## What "the curve" you want looks like

A curve snapshot is the set of **settlement prices** for the consecutive monthly
contracts as of one trading day. NYMEX Henry Hub natural gas futures (CME symbol
`NG`) list dozens of monthly contracts; for this module collect at least the
nearest **12** (one year of curve) for as many recent trading days as you can.

## Sources (pick one; both are legitimate)

### Option A — CME settlements (deepest, most authoritative)

- CME Group publishes daily **settlement** files for Henry Hub Natural Gas
  Futures (product `NG`). The settlements report lists every listed contract
  month with its settle price for that trading session.
- Start page: search "CME Henry Hub Natural Gas Futures settlements" (product
  page → *Settlements* tab). The site offers a downloadable CSV per session.
- Each row is one contract month (e.g. `JUN 24`, `JUL 24`, ...) with a settle.
- Pros: full curve (many months), official settlements. Cons: one file per day;
  to build a history you download multiple sessions.

### Option B — EIA NYMEX futures page (matches the existing series)

- EIA republishes NYMEX Henry Hub futures for contracts 1–4 as
  `RNGC1`..`RNGC4` (the exact series already in `data/`). The EIA "Natural Gas
  Futures Prices (NYMEX)" page is the source; the API series IDs follow the
  pattern `NG.RNGC{n}.D`.
- Pros: identical schema/units to what you already have, easy to extend the time
  axis. Cons: only **4** contracts — no extra curve depth, just fresher dates.
- If you have an EIA API key, the daily series endpoint returns `period` +
  `value`; map them to the schema below.

## Target schema (so `main.py` can read it unchanged)

Save **either** of these two layouts. The module's reshape step expects the long
layout; the wide layout is the snapshot table it would otherwise build.

### Long layout (preferred — one row per (date, contract))

File: `data_local/ng_futures_curve_current.csv`

| column | type | unit | example | notes |
|---|---|---|---|---|
| `Date` | date `YYYY-MM-DD` | — | `2026-05-18` | the **trading/observation** day |
| `contract` | int | — | `1` | 1 = prompt month, 2..n = next months |
| `delivery_month` | date `YYYY-MM` | — | `2026-06` | the contract's delivery month |
| `Value` | float | $/MMBtu | `3.45` | the **settlement** price |

`Date` + `Value` match `load_series_csv`'s expected columns so you can reuse the
loader per contract if you split files by contract (e.g.
`NG.RNGC1.D.local.csv`). Keep units in **$/MMBtu** to match spot.

### Wide layout (a ready-made snapshot table)

File: `data_local/ng_futures_curve_current_wide.csv`

| `date` | `C1` | `C2` | ... | `C12` |
|---|---|---|---|---|
| `2026-05-18` | 3.45 | 3.52 | ... | 3.98 |

## Where to save it

- Create a **`data_local/`** folder **inside this module** (not in the
  repo-level `data/`, which is immutable raw data you must not modify):
  `11_futures_curve_expectations/data_local/`.
- Point your code at it explicitly, e.g. `LOCAL = HERE / "data_local"`.
- Add a one-line provenance note (source URL + download date) at the top of the
  collected file or in `REPORT.md` — provenance is graded.

## Collection checklist (data hygiene)

- [ ] Record the **source URL** and the **download date** (provenance).
- [ ] Confirm prices are **settlements**, not last-trade, and the **unit** is
      $/MMBtu (convert if the source quotes cents or another unit).
- [ ] Confirm each row's `delivery_month` so contract 1 = the *true* prompt
      month on that date (the prompt rolls near expiry — late in a month the
      "front" may already be next month).
- [ ] Parse `Date` as a real date (`parse_dates=["Date"]`); never sort dates as
      strings.
- [ ] Do not overwrite or edit any file in the repo-level `data/` directory.
- [ ] Note any missing/holiday sessions; do not forward-fill silently — say so.

## Sanity checks after collection

- Prompt-month settlement should be **close to** (not equal to) the same-day
  Henry Hub spot — a few cents to tens of cents of **basis** is normal; a dollar
  gap means a unit or alignment error.
- The curve should be mostly smooth month-to-month; a single contract far off
  the neighbors is usually a parsing/column-shift bug.
- Daily moves of the prompt contract should be in a plausible range (gas can
  move several percent a day, but not 10x).
