# Assignment 09: Feature Engineering and the Model-Ready Panel

**Phase:** Model Design  
**Level:** Intermediate-Advanced  
**Estimated time:** 8-12 hours

## Data scope

This module **assembles** the work of the prior fundamentals modules into one
table. It reads, and depends on, the outputs of modules 06, 07, and 08:

- `06_storage_fundamentals/outputs/storage_panel.csv` (weekly storage)
- `07_supply_demand_balance/outputs/monthly_balance_panel.csv` (monthly fundamentals)
- `08_weather_degree_days/outputs/weather_features.csv` (weekly weather/degree days)

plus the weekly Henry Hub price series from `data/` (`NG.RNGWHHD.W.csv`).

If any upstream output is missing, `main.py` tells you which module to run first
and exits cleanly. **Complete 06, 07, and 08 before this module.**

Expected data inputs (logical):

- `Henry Hub` (weekly spot, the panel spine)
- `storage` (weekly)
- `selected supply-demand fundamentals` (monthly)
- `weather` (weekly degree days)

## Terms to learn

`feature table`, `model matrix`, `target leakage`, `lag`, `release lag`,
`as-of join`, `missingness`, `imputation`, `data dictionary`

Before coding, write one plain-English sentence for each in your own words, then
check yourself against the **Concepts** section below and `docs/GLOSSARY_SEED.md`
(section 7, "Features, data plumbing & leakage").

## Concepts you'll use

- **Feature table / model matrix (design matrix, X).** One rectangular table
  where each row is a single observation (here: one forecast you could have
  made) and each column is one predictor. A separate column holds the target
  `y`. Every model you ever fit consumes this X; building it correctly is most
  of the work. → `docs/GLOSSARY_SEED.md` "Feature table".
- **Forecast origin vs. target date.** The *origin* is the date you stand on and
  make the forecast; the *target date* is the future date whose value you are
  predicting. The curriculum requires BOTH on every row so a reviewer can audit
  timing. `target_date` must always be strictly after `forecast_origin`.
- **Target leakage.** Using any information on a row that would not have been
  known at that row's forecast origin. It makes backtests look brilliant and
  live forecasts fail. The silent killer. → `docs/GLOSSARY_SEED.md` "Leakage".
- **Lag (a modeling choice).** Deliberately using a past value as a feature:
  `series.shift(k)` pulls the value from `k` rows earlier onto the current row.
  Positive shift = past, so lags are leakage-safe by construction.
- **Release / publication lag (a fact about the data).** *When a number becomes
  public* vs. *the period it describes*. EIA weekly storage for the week ending
  Friday is not published until the following Thursday; monthly figures come out
  weeks after the month ends. You must align features to their *publication*
  time, not the period they cover, or you leak. → GLOSSARY "Release lag".
- **As-of join.** A merge that, for each origin date, attaches the most recent
  value that was *actually available by then* and never a value published later.
  This is the disciplined way to combine series with different release schedules.
  `pandas.merge_asof(..., direction="backward")`. → GLOSSARY "As-of join".
- **Monthly → weekly broadcast.** A monthly figure must be spread onto the weekly
  spine. An as-of join naturally carries each month's value forward to the weeks
  after it became public — which also handles the frequency mismatch.
- **Missingness & imputation.** Missingness is which cells are empty and why.
  Imputation fills them with a principled estimate. For time series, only ever
  use information from *before* the gap: forward-fill (`ffill`) is safe;
  back-fill and a global mean both leak the future. Leading NaNs from lags /
  rolling windows / the forward target are *expected* — drop those rows.
- **Data dictionary.** A small auditable table with one row per feature listing
  `name / source / unit / transform / availability lag / why`. A reviewer should
  be able to check every feature's legality from this alone.

## Learning goals

- Build the first serious model-ready panel with explicit origin and target.
- Lag, align, and document features according to *information availability*.
- Produce a data dictionary a reviewer can audit line by line.

## Package guide

Minimal, concrete snippets for the libraries this module needs.

**ng_models helpers (already imported in `main.py`):**

```python
from ng_models.io import load_series_csv
from ng_models.time_utils import make_forward_target, add_calendar_columns
from ng_models.features import add_lags, add_rolling_stats
from ng_models.metrics import summarize_predictions

hh = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="hh_price")

# Attach the future value to predict + bookkeeping. horizon is in ROWS.
panel = make_forward_target(hh, value_col="hh_price", horizon=1,
                            target_name="target_hh_next")
# -> adds: target_hh_next, target_date, forecast_origin, horizon_steps

panel = add_lags(panel, columns=["hh_price"], lags=[1, 4])      # hh_price_lag_1 ...
panel = add_rolling_stats(panel, columns=["hh_price"], windows=[4])  # _roll_mean_4, _roll_std_4
panel = add_calendar_columns(panel, date_col="date")            # month/week/quarter
```

**pandas — as-of join (the core tool here):**

```python
import pandas as pd
right = pd.read_csv(path, parse_dates=["date"]).sort_values("date")
# Build the date on which each right-hand value FIRST became public:
right["available_date"] = right["date"] + pd.Timedelta(days=RELEASE_LAG_DAYS)
panel = pd.merge_asof(
    panel.sort_values("forecast_origin"),
    right[["available_date", "feature_col"]],
    left_on="forecast_origin", right_on="available_date",
    direction="backward",   # only look at values already published
)
```

Gotchas: BOTH inputs must be sorted on the join key; `direction="backward"`
takes the most recent value at-or-before the origin; use `tolerance=` if you do
not want to carry stale values forward forever.

**pandas — missingness & leakage-safe fill:**

```python
miss = panel.isna().sum().rename("n_missing").to_frame()
miss["pct_missing"] = (miss["n_missing"] / len(panel)).round(4)

panel["feat"] = panel["feat"].ffill()   # safe: uses only the past
# panel["feat"].bfill()                 # LEAKS: pulls a future value backward
panel = panel.dropna(subset=["target_hh_next"])   # drop rows with no future label
```

## Tasks

1. **Define the target.** Choose next-week price level, next-week change, or
   next-month average price. Write one sentence: "I forecast [what] at [horizon]
   from [origin]." Build it with `make_forward_target` (and a resample first if
   you go monthly).
2. **Build price features** from prior prices: lags and rolling summaries that
   match your horizon. Justify the lag list and window sizes.
3. **As-of join the fundamentals** (storage, weather, monthly balance), each with
   a documented release lag. Broadcast the monthly balance onto the weekly spine
   via the as-of join. For EVERY feature, answer: "was this public on the
   forecast origin date?"
4. **Create the data dictionary** with source, unit, transformation, and
   availability timing for every feature.
5. **Run ONE baseline** on the panel (no ML yet) and report MAE/RMSE. The model
   you build in module 10 must beat this.

## Deliverables

- `outputs/model_panel.csv` — one row per forecast origin, with `forecast_origin`,
  `target_date`, the target, and all features.
- `outputs/data_dictionary.csv` — one row per feature.
- `outputs/missingness_report.csv` — NaN count and percent per column.
- `REPORT.md` — from `REPORT_TEMPLATE.md`.

> **This panel is the backbone of the rest of the curriculum.** `model_panel.csv`
> is the required input for module 10 (ML forecasts), module 12 (uncertainty &
> spike risk), and the module 14 capstone. Get it clean and leakage-free here —
> every later result inherits its mistakes. Those modules look for it at
> `09_feature_table_leakage/outputs/model_panel.csv` and will tell you to come
> back and run this module if it is missing.

## Rules

- Keep raw data immutable; do not modify anything in `data/`.
- Save generated files under this assignment's `outputs/` folder.
- Write down every assumption about dates, units, frequency conversion, release
  lags, and missing values.
- A chart is not enough. Every chart needs a sentence on what it shows and what
  it does not show.
- Do **not** fit a complex ML model here. The deliverable is the *panel* and one
  honest baseline. ML is module 10.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis (one precise sentence)?
- What dates, units, and frequencies are involved?
- What release lag did you assign each fundamental, and why?
- What was the most important data decision?
- What result surprised you?
- What would you not trust yet (where could leakage still hide)?
- What should the next assignment investigate?
