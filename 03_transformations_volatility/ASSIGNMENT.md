# Assignment 03: Levels, Log Prices, Returns, and Volatility

**Phase:** Foundations  
**Level:** Beginner-Intermediate  
**Estimated time:** 4-6 hours

## Data scope

Use weekly Henry Hub only.

Expected data inputs:

- `data/NG.RNGWHHD.W.csv` — weekly Henry Hub spot price, `$/MMBtu`, one row per week (~1997 to present).

The starter loads this for you via `ng_models.io.load_series_csv` and resolves the
path with `ng_models.paths.data_dir`. If the file is missing, `main.py` prints an
actionable message and exits cleanly — it does not crash.

## Terms to learn

`level`, `log price`, `return`, `difference`, `volatility`, `outlier`, `stationarity`, `heteroskedasticity`

Before coding, write one plain-English sentence for each term in your own words (in
`REPORT.md`). The **Concepts you'll use** section below is your ground-up reference;
cross-check it against `docs/GLOSSARY_SEED.md` (sections 3 and 4).

## Concepts you'll use

- **Level**: The raw price as reported — here, dollars per MMBtu. The level answers
  "where is the price *right now*?" It drifts and trends, so its mean and variance
  change over time.
- **Log price**: The natural log of the price, `np.log(price)`. Taking logs turns
  *multiplicative* moves into *additive* ones (a move from \$2→\$4 and \$4→\$8 are both
  "+0.69 in log space"), which is why log differences are comparable across price eras.
  Logs are only defined for **strictly positive** numbers — always assert `price > 0`
  before calling `np.log`.
- **Difference**: The change from one period to the next, `y_t − y_{t-1}` (pandas
  `.diff()`). It answers "how much did the price *move*, in dollars?" The first row is
  always `NaN` because there is no prior value to subtract — that is correct, not a bug.
- **Return (log return)**: `log(y_t) − log(y_{t-1})`, i.e. the *percentage-style*
  change. A log return of `0.05` is roughly a +5% week. Returns are scale-free, so a
  5% move in 2002 and 2024 are directly comparable even though price levels differed.
- **Stationarity**: A series is (weakly) stationary when its mean, variance, and
  autocorrelation **don't change over time** — no trend, no drift, no shifting spread.
  Most classical models (AR/ARIMA, next modules) *assume* stationarity. Prices are
  non-stationary (they wander); differencing/returns get you much closer to stationary.
  *Why it matters:* fitting a model that assumes stationarity to a non-stationary level
  gives misleading parameters and forecasts that revert to the wrong place.
- **Volatility**: How big the moves are, regardless of direction — operationally the
  rolling standard deviation of returns over a window. High volatility = wide swings.
- **Heteroskedasticity / volatility clustering**: "Hetero-skedastic" just means the
  variance is **not constant** — calm periods and turbulent periods alternate. In
  markets, big moves tend to follow big moves (a spike week is often next to other
  spike weeks): that bunching is *volatility clustering*. The opposite,
  constant-variance, is *homoskedastic*. This is exactly what a rolling-volatility plot
  reveals.
- **Outlier (extreme move)**: A week whose move is far larger than typical. Because
  RMSE squares errors, a handful of extreme moves can dominate it — which is why you
  inventory the largest moves explicitly rather than letting them hide in an average.

## Learning goals

- Learn why price levels, differences, and returns answer different questions.
- Explore volatility clustering and extreme moves.
- Build intuition for transformations before fitting statistical models.

## Tasks

1. In `add_transformations`, create `log_price`, `price_diff`, `log_return`,
   `abs_return`, and a rolling-volatility column `roll_vol`. Handle the first-row /
   leading `NaN`s deliberately (do **not** fill them with 0).
2. Plot price level, weekly changes, and rolling volatility — ideally as a single
   3-panel figure that **shares the x-axis** so the panels line up by date.
3. Identify the **top 10 absolute weekly moves over the full sample**. First **decide
   what "move" means**: `abs(log_return)` (a percentage-style move, comparable across
   eras) or `abs(price_diff)` (a dollar move). State which you chose and why. "Top"
   means largest over the entire series, not within a rolling window.
4. Compare summary stats for level vs. change vs. log return (`df[[...]].describe()`)
   and read what the mean/std differences tell you.
5. State which target transformation later models should use for each forecasting
   objective ("where will price be" vs. "how big is the next move").

### Choices you must make and justify

- **Rolling-volatility window** (`VOL_WINDOW` in `main.py`): pick one (e.g. 13 / 26 /
  52 weeks). A longer window is smoother but lags regime changes; a shorter window
  reacts faster but is noisier. There is no single right answer — defend yours.
- **Definition of "move"** for the top-10 table (see task 3).
- **Volatility units**: weekly log-return std as-is, or annualized (`× sqrt(52)`).
  State which.

## Deliverables

- `outputs/transformed_hh.csv`
- `outputs/volatility_plot.png`
- `outputs/top_moves.csv`
- `REPORT.md`

## Package guide

Minimal, concrete API for the libraries this module needs.

**numpy — logs (assert positivity first):**
```python
import numpy as np
assert (df["hh_price"] > 0).all(), "log undefined for non-positive prices"
df["log_price"] = np.log(df["hh_price"])   # natural log, element-wise
```

**pandas — shift / diff (mind the leading NaN and date alignment):**
```python
# .diff() = y_t - y_{t-1}; equivalent to y - y.shift(1).
df["price_diff"] = df["hh_price"].diff()        # row 0 is NaN (no prior week)
df["log_return"] = df["log_price"].diff()       # == np.log(y/y.shift(1))
df["abs_return"] = df["log_return"].abs()
# .shift(k) moves values DOWN k rows (forward in time). It does NOT realign by
# calendar date -- it works on row position, so the frame must already be sorted
# ascending by date (load_series_csv guarantees this). Do not .dropna() the whole
# frame just to remove one NaN; downstream stats skip NaN automatically.
```

**pandas — rolling volatility (leading NaNs are expected):**
```python
W = 52
df["roll_vol"] = df["log_return"].rolling(W).std()  # sample std, ddof=1
# The first W-1 rows are NaN: not enough history to fill the window. That is
# correct -- do not backfill. rolling(W, min_periods=W) is the default; lowering
# min_periods would compute vol from too few points (noisy, not comparable).
```

**pandas — top-N and summary stats:**
```python
top = (df.dropna(subset=["abs_return"])
         .sort_values("abs_return", ascending=False)
         .head(10)[["date", "hh_price", "log_return", "abs_return"]])
df[["hh_price", "price_diff", "log_return"]].describe()  # count/mean/std/min/quartiles/max
```

**matplotlib — shared-axis multi-panel plot:**
```python
import matplotlib.pyplot as plt
fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
axes[0].plot(df["date"], df["hh_price"]); axes[0].set_ylabel("$/MMBtu")
axes[1].plot(df["date"], df["log_return"]); axes[1].set_ylabel("log return")
axes[2].plot(df["date"], df["roll_vol"]); axes[2].set_ylabel("vol")
fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
```
(For a single line plot you can also use `ng_models.plotting.save_line_plot`.)

## Rules

- Keep raw data immutable (work on a `.copy()`).
- Save generated files under this assignment's `outputs/` folder.
- Write down every assumption about dates, units, frequency, and missing values.
- A chart is not enough. Every chart needs a sentence explaining what it shows **and
  what it does not show**.
- Do not move to a more complex model until the required baseline or diagnostic is
  complete.
- Make no causal claims ("cold weather *caused* the spike"); this module describes and
  transforms, it does not explain causes.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis?
- What dates and units are involved?
- What was the most important data decision?
- What result surprised you?
- What would you not trust yet?
- What should the next assignment investigate?
