# Assignment 07: Supply-Demand Balance: Production, Consumption, Trade, and LNG

**Phase:** Gas Fundamentals  
**Level:** Intermediate  
**Estimated time:** 8-12 hours

## What you are building

A first-principles monthly natural-gas **balance panel**: one row per month, one
column per balance component (supply, demand, trade, LNG), plus Henry Hub price.
You then study which side of the balance moved during selected price regimes.
The whole assignment is organized by one accounting identity:

> **production + imports = consumption + exports + storage change**
>
> equivalently: **production + imports − consumption − exports = storage change**

Gas cannot vanish. Anything produced or imported that is not consumed or exported
must move into or out of storage. You assemble the pieces you can measure and
reason about what the residual implies.

## Data scope

Use the EIA-style natural-gas fundamentals already in `data/`. Weather is excluded
in this module (it returns in module 08). All series are loaded through
`ng_models.io` (never read `../data` directly).

**Candidate national monthly series (verify units/frequency in `_metadata.csv`):**

| Component | Series ID | File | Units |
|---|---|---|---|
| Dry production | `NG.N9070US2.M` | `NG.N9070US2.M.csv` | Million Cubic Feet (MMcf) |
| Dry production (same data, Bcf) | `NG.N9070US1.M` | `NG.N9070US1.M.csv` | **Billion** Cubic Feet (Bcf) |
| Marketed production | `NG.N9050US2.M` | `NG.N9050US2.M.csv` | MMcf |
| Total consumption | `NG.N9140US2.M` | `NG.N9140US2.M.csv` | MMcf |
| Imports (total) | `NG.N9100US2.M` | `NG.N9100US2.M.csv` | MMcf |
| Exports (total) | `NG.N9130US2.M` | `NG.N9130US2.M.csv` | MMcf |
| Henry Hub spot (weekly) | `NG.RNGWHHD.W` | `NG.RNGWHHD.W.csv` | $/MMBtu |
| LNG flows (by terminal/country) | `NG.NGM_EPG0_*_MMCF.M` | many | MMcf |

These are *suggestions to evaluate*, not a locked answer. The U.S. has no single
clean "LNG exports, national monthly" series in this dataset — LNG appears split
by terminal and destination. Decide whether to sum a set of LNG export files,
fold LNG into total exports, or treat LNG qualitatively, and justify it.

> **Unit trap:** `NG.N9070US1.M` (Bcf) and `NG.N9070US2.M` (MMcf) are the *same
> quantity in different units* (1 Bcf = 1000 MMcf). Pick one unit for the whole
> panel. Mixing MMcf and Bcf silently breaks every balance subtraction.

## Concepts you'll use

- **Supply-demand balance identity.** The accounting rule that production +
  imports = consumption + exports + storage change. It always holds over a period
  because gas is conserved. You will not have every term measured, so treat the
  identity as a check and a way to *infer* the missing piece (often the implied
  storage change). See [Supply-demand balance](../docs/GLOSSARY_SEED.md#supply-demand-balance).
- **Dry vs. marketed production.** *Marketed* production is the gross gas removed
  from wells minus what is reinjected, vented, or flared. *Dry* production is
  marketed production *after* the natural gas liquids and impurities are stripped
  out — it is the pipeline-quality gas that actually meets demand, so it is
  usually the number you put on the supply side. See
  [Marketed vs. dry](../docs/GLOSSARY_SEED.md#marketed-vs-dry).
- **Net exports.** Exports minus imports (pipeline plus LNG). A positive, rising
  figure means the U.S. is sending more gas abroad, which tightens the domestic
  balance. See [Net exports](../docs/GLOSSARY_SEED.md#net-exports).
- **Frequency alignment.** Fundamentals are **monthly**; Henry Hub spot is
  **weekly** (and daily). To compare them you must put them on the same clock —
  here, aggregate the weekly price up to monthly. The aggregation you choose
  (mean of the month vs. last week of the month) changes what the number means.
- **Publication / release lag (vs. a modeling lag).** A *modeling lag*
  (`shift(k)`) is your deliberate choice to use a past value. A *publication lag*
  is a fact about the data: EIA monthly fundamentals for a given month are not
  released until roughly two months later. Aligning a fundamental to *price* on
  the period it describes — rather than the date it was published — leaks future
  information. See [Lag vs. release lag](../docs/GLOSSARY_SEED.md#release-lag).
- **Level vs. MoM vs. YoY vs. anomaly.** The same series answers different
  questions depending on the transform: the *level* (raw MMcf), the
  *month-over-month* change (`diff()`), the *year-over-year* change (`diff(12)`,
  which cancels the seasonal cycle), or an *anomaly* (deviation from a seasonal
  norm). Gas demand has a huge winter/summer swing, so a raw MoM jump is mostly
  seasonality, not news. See [YoY](../docs/GLOSSARY_SEED.md#yoy) and
  [Anomaly](../docs/GLOSSARY_SEED.md#anomaly).
- **Correlation is not causation.** A price–fundamentals correlation can be driven
  by a shared trend (e.g. the shale era pushed production up and price down at the
  same time). Name the confound before writing any "because." See
  [Correlation vs. causation](../docs/GLOSSARY_SEED.md#correlation-causation).

## Package guide

Minimal API snippets for the libraries this module needs. (These are the *calls*;
the *choices* they encode — mean vs. last, inner vs. outer, lag size — are yours.)

**Load a series and the catalog (ng_models):**
```python
from ng_models.io import load_metadata, load_series_csv, search_metadata
meta = load_metadata(DATA_DIR)                       # start_date/end_date parsed for you
cand = search_metadata(meta, ["production", "lng"])  # OR over keywords
prod = load_series_csv(DATA_DIR, "NG.N9070US2.M.csv", value_name="dry_production_mmcf")
# -> columns: date (datetime64), dry_production_mmcf (float), sorted by date
```

**Resample weekly price to monthly (pandas):**
```python
hh_monthly = (
    hh_weekly.set_index("date")["hh_price"]   # need a DatetimeIndex to resample
    .resample("MS").mean()                    # "MS" = month start (YYYY-MM-01); .last() = end-of-month snapshot
    .reset_index()
)
```

**Join heterogeneous monthly series (pandas):**
```python
panel = (prod
         .merge(cons, on="date", how="inner")   # inner = keep overlap only
         .merge(imp,  on="date", how="inner")
         .merge(exp,  on="date", how="inner"))
panel["net_exports_mmcf"] = panel["exports_mmcf"] - panel["imports_mmcf"]
```

**Level / MoM / YoY transforms (pandas):**
```python
panel["cons_mom"]    = panel["consumption_mmcf"].diff()        # vs last month
panel["cons_yoy"]    = panel["consumption_mmcf"].diff(12)      # vs same month last year (12 monthly rows)
panel["cons_yoy_pct"]= panel["consumption_mmcf"].pct_change(12)
```

**Publication-lag shift before comparing to price (pandas):**
```python
# k = publication delay in MONTHS for the EIA fundamentals (you choose & defend k)
for col in ["dry_production_mmcf", "consumption_mmcf"]:
    panel[col + "_asof"] = panel[col].shift(k)
```

**Correlation table and a plot (pandas + ng_models):**
```python
corr = panel[["dry_production_mmcf", "net_exports_mmcf", "hh_price"]].corr()
corr.to_csv(OUTPUT_DIR / "balance_correlations.csv")
from ng_models.plotting import save_line_plot
save_line_plot(panel, x="date", y="dry_production_mmcf",
               title="U.S. Dry Gas Production (MMcf)",
               output_path=OUTPUT_DIR / "balance_components.png")
```

## Tasks

0. **Sketch your panel first (on paper).** Write the balance identity at the top.
   Draw the monthly table: one row per month, one column per component, plus
   price. Decide what each column means and its unit *before* writing code.
1. Use the metadata to identify candidate national monthly series for production,
   consumption, imports, exports, and (where it exists) LNG. Record each pick's
   `series_id`, units, frequency, and date range in a short `series_selection`
   note, with one sentence on why you chose it (e.g. dry vs. marketed).
2. Create a monthly Henry Hub series from the weekly data; state mean vs. last.
3. Build the monthly panel with supply, demand, net exports/trade, and price.
   Confirm every quantity column shares one unit (MMcf or Bcf, not both).
4. Compute level, MoM, and YoY comparisons for each major component. Choose one
   headline comparison and explain why the others mislead given seasonality.
5. Before comparing any fundamental to price, apply the EIA publication lag.
   State the lag in months and defend it.
6. Write the memo: which side of the balance changed most during selected price
   regimes, and what you would *not* yet conclude from a correlation.

## Deliverables

- `outputs/monthly_balance_panel.csv`
- `outputs/balance_components.png`
- `outputs/balance_correlations.csv`
- `REPORT.md` (fill in from `REPORT_TEMPLATE.md`)

## Rules

- Keep raw data immutable; never read `../data` directly — go through `ng_models`.
- Save generated files under this assignment's `outputs/` folder.
- Write down every assumption about dates, units, frequency conversion, missing
  values, joins, and publication lags.
- A chart is not enough. Every chart needs a sentence on what it shows **and what
  it does not show**.
- Do not move to a more complex comparison until the balance panel and its units
  are verified correct.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis, in what units, over what dates?
- What was the most important data decision (units? aggregation? join? lag?)
- Which side of the balance moved most in your chosen regime?
- What result surprised you?
- What would you not trust yet (publication lags, revisions, the missing storage
  term, the LNG gap)?
- What should the next assignment investigate?
