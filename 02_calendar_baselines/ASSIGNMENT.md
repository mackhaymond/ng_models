# Assignment 02: Calendar Structure and Naive Forecast Baselines

**Phase:** Foundations
**Level:** Beginner
**Estimated time:** 4-6 hours

## Data scope

Use weekly Henry Hub only.

Expected data inputs:

- `data/NG.RNGWHHD.W.csv` — Henry Hub spot price, weekly, dollars per MMBtu, 1997-01-10 to present.

The starter loads this for you via `ng_models.io.load_series_csv`. If the file is
missing, the script prints an actionable message and exits cleanly.

## Learning goals

- Learn why a forecast must be evaluated against simple alternatives.
- Build naive and seasonal-naive baseline forecasts **without leaking the future**.
- Understand that a model is not useful unless it beats a defensible benchmark
  **out of sample**.

## Concepts you'll use

Read these once before coding. Each is a ground-up plain-English explanation;
fuller entries live in `docs/GLOSSARY_SEED.md`.

- **Forecast origin, target date, horizon.** The *forecast origin* is the moment
  you stand at and make a prediction — you may only use data known on or before
  that date. The *target date* is the future date you are predicting. The
  *horizon* is the distance between them. For this weekly series, a horizon of 1
  means "predict next week"; a horizon of 4 means "predict the value 4 weeks
  out." Every forecast row in your output must record all three so a reviewer can
  audit it.

- **1-step vs multi-step (for this weekly data).** A *1-step* forecast predicts
  the very next observation (next week, h=1). A *multi-step* forecast predicts
  further out (h=4 means 4 weeks ahead). The horizon counts *rows* of this weekly
  frame, so h=4 is roughly one month. Pick one horizon, state it in your report,
  and keep it fixed across all baselines so the comparison is fair.

- **Naive forecast (random walk).** The cheapest possible forecast: "the future
  equals the last value I observed." For horizon h that is
  `y_hat[t+h] = y[t]`. It is shockingly hard to beat for prices, because prices
  behave a lot like a random walk.

- **Seasonal-naive forecast.** "The future equals the same point in the previous
  cycle." For a weekly series with a yearly cycle, that is roughly
  `y_hat[t+h] = y[t+h-52]` (the value about one year earlier). It encodes the
  belief that the calendar week matters (winter vs summer demand).

- **Expanding-window mean/median vs full-sample mean.** A *full-sample* statistic
  uses the ENTIRE series — including data after the forecast origin — to compute
  one number. That is **leakage**: at the moment you forecast, you could not have
  known the future values that went into the average. An *expanding-window*
  statistic, at each origin date, uses ONLY the data up to and including that
  date, and grows as time advances. Always use expanding (or otherwise
  past-only) statistics for a forecast. See the pitfall box below.

- **Week-of-year (seasonal) statistic.** Group history by ISO week number (1-53)
  and summarize each week across years — e.g. "the median price observed in week
  6 across all prior years." It captures the seasonal shape. To stay leakage-free,
  the statistic for a target in week 6 of 2024 must be built only from week-6
  observations strictly *before* that origin, not from all of history.

- **Why no random train/test split for time series.** Randomly shuffling rows
  into train/test lets the model "see" future weeks while predicting past ones,
  which is leakage and inflates the score. Time series must be split
  *chronologically*: train on the earlier portion, test on a contiguous later
  window.

- **MAE, RMSE, MAPE — what each rewards.** *MAE* (mean absolute error) is the
  average size of the miss, in dollars/MMBtu; robust and easy to read. *RMSE*
  (root mean squared error) is also in dollars/MMBtu but squares errors, so it
  punishes a few large misses much harder — use it when big errors are especially
  costly. *MAPE* (mean absolute percentage error) is unit-free (a percent), handy
  for comparing across price levels — but **it explodes when actual values are
  near zero** and is undefined at exactly zero. Henry Hub stays positive, but it
  has dipped near \$1.5-2, so MAPE will be noisier in those stretches; report MAE
  and RMSE as your primary metrics and treat MAPE as secondary.

## Common pitfall — leakage (READ THIS)

> The single most common way to fake a good baseline here is to compute a
> statistic over the whole dataset and then "predict" the test period with it.
> Example of the BUG: `df["price"].mean()` (or a week-of-year mean over the full
> frame) used as the forecast for 2024 — that average already contains 2024 (and
> 2025) data you could not have known.
>
> The fix: at each forecast origin, the statistic may only use rows whose date is
> on or before the origin. In pandas, an expanding mean known-at-time-t is
> `df["price"].expanding().mean().shift(1)` (the `.shift(1)` drops the current row
> so the mean reflects only the *past*). For a 1-step naive forecast the
> leakage-safe value is simply `df["price"].shift(1)`. You will decide the exact
> shift for your chosen horizon and defend it.

## Tasks

1. Construct a clean weekly target frame with `date`, `price`, and calendar
   columns (`iso_week`, `year`, `month`). Use
   `ng_models.time_utils.add_calendar_columns` for the calendar fields.

2. Choose ONE forecast horizon `h` (state whether it is 1-step or multi-step and
   what `h` weeks means) and build these five baselines as columns of per-origin
   forecasts, all **leakage-free (past-only)**:
   - last observed value (naive / random walk),
   - **expanding** historical mean,
   - **expanding** historical median,
   - week-of-year mean (seasonal, using only prior-year same-week data),
   - week-of-year median (seasonal, using only prior-year same-week data).

   "Expanding" means the statistic at each origin uses all data up to that origin
   and no further — never the full sample.

3. Pick a **fixed final test window** (a contiguous block at the end of the
   series, chosen *before* you look at the metrics — e.g. the most recent 104
   weeks ≈ 2 years) and compute MAE and RMSE for each baseline over that window.
   State the exact start/end dates of the test window in your report.

4. Plot actual vs forecast over the test window for at least three baselines (one
   line for actual, one per baseline).

5. Write which baseline you would force all later models to beat, and why.

## Deliverables

- `outputs/baseline_metrics.csv`
- `outputs/test_forecasts.csv` (must include `forecast_origin`, `target_date`,
  `horizon_steps`, `actual`, and one column per baseline forecast)
- `outputs/baseline_comparison.png`
- `REPORT.md` (copy `REPORT_TEMPLATE.md` and fill it in)

## Package guide

Minimal, concrete snippets for the libraries this module needs. (Concept choices
— which horizon, which baseline to crown — are yours to make and defend.)

**Load the series (ng_models + pandas):**
```python
from ng_models.io import load_series_csv
from ng_models.paths import data_dir, ensure_output_dir
hh = load_series_csv(data_dir(HERE), "NG.RNGWHHD.W.csv", value_name="price")
# -> columns: date (datetime64), price (float), sorted ascending, fresh index
```

**Calendar columns (ng_models):**
```python
from ng_models.time_utils import add_calendar_columns
hh = add_calendar_columns(hh, date_col="date")   # adds year, month, iso_week, ...
```

**Leakage-safe past-only statistics (pandas):**
```python
hh["naive"]      = hh["price"].shift(h)                      # last value, h steps back
hh["exp_mean"]   = hh["price"].expanding().mean().shift(1)   # mean of strictly past rows
hh["exp_median"] = hh["price"].expanding().median().shift(1)
# .expanding() = a window that grows to include all rows so far;
# .shift(1) drops the current row so "now" is excluded.
```

**Week-of-year seasonal stat (pandas groupby + expanding):**
```python
# For each iso_week group, take an expanding stat down its own (time-sorted) rows,
# then shift(1) so the current obs is excluded. groupby preserves the original index.
hh["woy_mean"] = (
    hh.groupby("iso_week")["price"]
      .apply(lambda s: s.expanding().mean().shift(1))
      .reset_index(level=0, drop=True)
)
# NOTE: this assumes hh is sorted by date. You decide whether mean or median is
# the better seasonal summary and justify it.
```

**Metrics (ng_models — use these, don't re-implement):**
```python
from ng_models.metrics import mae, rmse, mape, summarize_predictions
row = summarize_predictions(test_df, actual_col="actual", pred_col="naive")
# -> {"mae": ..., "rmse": ..., "mape": ..., "smape": ...}
```

**Plot (matplotlib directly, since you have multiple lines):**
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(test["target_date"], test["actual"], label="actual")
for col in ["naive", "woy_mean", "exp_mean"]:
    ax.plot(test["target_date"], test[col], label=col)
ax.legend(); ax.set_title("Baselines vs actual (test window)")
fig.tight_layout(); fig.savefig(OUTPUT_DIR / "baseline_comparison.png", dpi=150)
plt.close(fig)
```

**Save a CSV (pandas):**
```python
metrics_df.to_csv(OUTPUT_DIR / "baseline_metrics.csv", index=False)
```

## Rules

- Keep raw data immutable.
- Save generated files under this assignment's `outputs/` folder.
- Write down every assumption about dates, units, frequency conversion, and
  missing values.
- A chart is not enough. Every chart needs a sentence explaining what it shows
  and what it does not show.
- Do not move to a more complex model until the required baseline or diagnostic
  is complete.
- Every forecast row must carry `forecast_origin`, `target_date`, and
  `horizon_steps`.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis, and at what horizon?
- What dates and units are involved? What is your exact test window?
- What was the most important data decision (especially around leakage)?
- What result surprised you?
- What would you not trust yet?
- What should the next assignment investigate?
