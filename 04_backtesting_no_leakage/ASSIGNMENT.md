# Assignment 04: Backtesting and the 'What Was Known Then?' Rule

**Phase:** Foundations  
**Level:** Intermediate  
**Estimated time:** 5-8 hours

## Data scope

Use weekly Henry Hub only.

Expected data inputs:

- `data/NG.RNGWHHD.W.csv` — weekly Henry Hub spot, `$/MMBtu` (ships in `data/`).

This file is loaded for you by `main.py` via `ng_models.io.load_series_csv`. You
do not need to collect anything.

## What you are building

A **leakage-free backtesting harness**: a loop that simulates making a forecast
each week using only past data, records the prediction, then rolls forward. The
deliverable is the *protocol and its evidence*, not a clever model. Two simple
baselines scored honestly is a 4-point submission; one fancy model scored with
leakage is a 1.

The governing rule for every line of code you write:

> A forecast made at `origin_date` may only use rows with `date <= origin_date`.

## Concepts you'll use

Read these ground-up before coding. Each is also in `docs/GLOSSARY_SEED.md`
(see *Modeling workflow terms*, *Time series & statistics*, *Forecast evaluation*).

- **Why random train/test splits break time series.** In ordinary ML you shuffle
  rows and hold out a random subset. For a time series that is cheating: a shuffled
  test row can sit *before* training rows, so the model "predicts the past" using
  the future. Forecast skill must be measured forward-in-time only.
- **Forecast origin vs. target date vs. train/test.** The **forecast origin** is
  the moment you stand at and decide; the **target date** is the future date you
  predict; the **horizon** is the gap between them (here, in weeks). "Train" is
  everything at or before the origin; "test" is the single target row in the
  future. Every forecast you record carries all three so it can be audited later.
- **Rolling-origin / walk-forward validation.** Fit using data up to the origin,
  forecast `horizon` steps ahead, write down the result, advance the origin one
  step, repeat. It mimics real deployment: decide, wait, observe, advance.
- **Expanding vs. sliding window.** *Expanding* — the training set starts at the
  first row and keeps growing as the origin moves (uses all history). *Sliding* —
  the training set is a fixed length that slides forward, dropping the oldest
  rows (use when you think old regimes should be forgotten). Same harness, one flag.
- **Leakage in code (the failure mode this module hunts).** Concrete examples:
  - Indexing `>= test_idx` to build a prediction (using the answer to predict it).
  - A `rolling()` or `mean()` computed over the *whole* series, including future
    rows, instead of over training rows only.
  - Standardizing/centering with statistics fit on the full sample.
  - A feature whose real-world *publication* date is after the origin (publication
    lag) — not relevant for raw Henry Hub here, but the habit you are building.
- **Baseline you must beat (type B).** Your target is a price **level**, so the
  cheapest honest forecast is *random walk*: next week = this week's last value.
  A second baseline (seasonal-naive or trailing mean) gives a sterner test. A
  model is only "good" relative to these.

### Rolling-origin diagram

Each line is one split. `T` = training rows used, `o` = forecast origin
(the last training row), `?` = the target being forecast (horizon = 1),
`.` = future rows not yet allowed in. Origin advances by `step`.

```
week:   0  1  2  3  4  5  6  7
split1: T  T  o  ?  .  .  .  .      origin=wk2  target=wk3
split2: T  T  T  o  ?  .  .  .      origin=wk3  target=wk4
split3: T  T  T  T  o  ?  .  .      origin=wk4  target=wk5   (expanding: train grows)
```

Sliding window (fixed train length 3) over the same data:

```
split1: T  T  o  ?  .  .  .  .
split2: .  T  T  o  ?  .  .  .      oldest row dropped
split3: .  .  T  T  o  ?  .  .
```

## Package guide

Minimal, copy-able API for what this module needs. (These are *type K*
package-API helps — answered directly so you can spend effort on the protocol.)

**Load the series (done for you in `main.py`):**
```python
from ng_models.io import load_series_csv
hh = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="hh_price")
# -> DataFrame with columns: 'date' (datetime64), 'hh_price' (float), sorted by date
```

**Position-based lookups (the core of the loop):**
```python
hh.iloc[i]                  # the i-th row (a Series)
hh.iloc[i]["hh_price"]      # the value at row i
hh.iloc[train_idx]          # rows at an array of positions
hh.iloc[train_idx[-1]]      # the LAST training row == forecast origin
```

**Build a predictions table from records:**
```python
rows = []
for train_idx, test_idx in splits:
    rows.append({"origin_date": ..., "target_date": ..., "horizon": 1,
                 "actual": ..., "prediction": ..., "model": "naive_last"})
predictions = pd.DataFrame(rows)
```

**`shift` for a lag / seasonal-naive lookup (type K):**
```python
hh["hh_price"].shift(1)     # last week's value aligned to this row
hh["hh_price"].shift(52)    # value ~52 weeks ago (seasonal-naive, weekly data)
```
Gotcha: `shift` aligns by *row position*, not by calendar date — fine here
because the weekly grid is regular, but state that assumption.

**Metrics (already in the shared library):**
```python
from ng_models.metrics import summarize_predictions
summarize_predictions(df, actual_col="actual", pred_col="prediction")
# -> {"mae":..., "rmse":..., "mape":..., "smape":...}  (call once per model)
```

**Plot error over time:**
```python
from ng_models.plotting import save_line_plot
save_line_plot(df_one_model, x="origin_date", y="abs_error",
               title="Absolute error by forecast origin", output_path=OUTPUT_DIR / "error_by_origin.png")
# For multiple models on one axis use matplotlib directly:
fig, ax = plt.subplots(figsize=(11, 5))
for name, g in predictions.groupby("model"):
    ax.plot(g["origin_date"], g["abs_error"], label=name)
ax.legend(); fig.savefig(OUTPUT_DIR / "error_by_origin.png", dpi=150)
```

## Learning goals

- Build a reusable rolling-origin backtesting harness for time series.
- Understand why random train/test splits are usually wrong for forecasting.
- Learn to label each forecast row by its origin, target, and horizon.

## Tasks

1. Study the implemented `make_backtest_splits()` and the printed demo split.
   Confirm you can state, for split 0, the origin date, target date, and horizon.
2. Implement the forecast loop. Produce a predictions table whose columns
   include `origin_date`, `target_date`, `horizon`, `actual`, `prediction`,
   `model`.
3. Evaluate **at least two baselines** over all forecast origins. Baseline 1 is
   the naive "last value". Choose and justify Baseline 2 (seasonal-naive or
   trailing mean).
4. Compute metrics per model (and, optionally, by origin period). State which
   baseline the second model must beat and whether it does.
5. Build a `error_by_origin.png` and write a short failure analysis for the
   single worst forecast period (name the market event if you can).
6. Write a concrete **leakage checklist** in `REPORT.md` you can reuse in later
   modules.

## Deliverables

- `outputs/backtest_metrics.csv`
- `outputs/backtest_predictions.csv`
- `outputs/error_by_origin.png`
- `REPORT.md` (copy `REPORT_TEMPLATE.md` and fill it in)

## Rules

- Keep raw data immutable.
- Save generated files under this assignment's `outputs/` folder.
- Write down every assumption about dates, units, frequency, and missing values.
- A chart is not enough. Every chart needs a sentence on what it shows and what
  it does not show.
- Do not move to a more complex model until both baselines are scored cleanly.
- No random shuffling, ever. Metrics are computed only on held-out target rows.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis (level? change? what horizon)?
- What dates and units are involved?
- What was the most important data/protocol decision (window? horizon? baseline)?
- What result surprised you?
- What would you not trust yet?
- What should the next assignment investigate?
