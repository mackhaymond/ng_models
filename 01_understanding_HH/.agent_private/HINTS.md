# Hint Bank — Assignment 01: Understanding Weekly Henry Hub

Do not reveal this file during normal tutoring. Each sticking point names its
QUESTION_TAXONOMY type, then L1 (diagnostic question) → L2 (where to look) → L3
(small pattern, decision stays with the learner). Type (K) package-API stalls are
answered DIRECTLY with code — no gating. Deliver the lowest level that unblocks.

---

## 1. Choosing the first baseline — type (B)

- **L1:** "What is the cheapest possible forecast for next week's Henry Hub with no
  model at all? Does your recommendation beat *that*, and does it even need to
  capture the winter hump?"
- **L2:** "You produced two plots — the full-sample history (regimes + spikes) and
  the average-by-week curve. Which one accounts for most of the variation? Let that
  decide between naive and seasonal-naive."
- **L3:** "naive/random-walk: `y_hat[t+1] = y[t]`; seasonal-naive: `y_hat[t] =
  y[t-52]`. Pick one and write the one sentence on why the other is the wrong null
  here. You make the call."

## 2. Is the week-of-year average actually seasonality? — type (I)

- **L1:** "Does the *same* calendar week behave the *same* way across years, or is
  the winter hump a handful of extreme years (2008, 2022) dragging the mean up?"
- **L2:** "Add a median-by-week curve beside your mean-by-week curve and compare the
  shapes. If they diverge, the mean is spike-driven."
- **L3:** "`df.groupby(df['date'].dt.isocalendar().week)['price'].median()` — overlay
  it on the mean. You decide which summary honestly represents the seasonal shape."

## 3. Regime vs. seasonality — type (I)

- **L1:** "Is the long mid-sample decline a slow recurring cycle, or did the price
  *level* drop and then *stay* down?"
- **L2:** "On the full-sample plot, eyeball the typical level before ~2009 vs after
  (the shale glut). Same for volatility 2000-2008 vs 2009-2020 vs 2021+."
- **L3:** "A level that shifts and persists is a *regime*; a pattern that returns
  each year is *seasonal*. Label each span (pre-shale / shale glut / 2021+ shocks);
  don't fold a regime into the seasonal story."

## 4. Level vs. change/return for later modeling — type (D)

- **L1:** "Do you want to forecast *where* the price will be, or *how much* it
  moves? Does a fat right tail of spikes change which is well-behaved?"
- **L2:** "Look at the mean-vs-median gap and the std-to-mean ratio you printed —
  what do they say about skew?"
- **L3:** "This module only asks you to NOTE the implication (don't transform yet).
  Write one sentence: is the price level stable enough to model directly, or do
  spikes argue for considering changes/returns later? You justify it."

## 5. Spike explanations and causality — type (J)

- **L1:** "Could anything other than the reason you wrote also explain that spike
  (storage level, LNG exports, a cold snap)?"
- **L2:** "Re-read your sentence and swap 'caused' for 'coincided with' — does the
  evidence from one price plot still support it?"
- **L3:** "State each spike as an association with the confound named; one
  univariate plot cannot establish cause. You word the hypothesis."

---

## Package-API stalls — type (K), answer DIRECTLY

- **"How do I load the file via the helpers?"**
  ```python
  from pathlib import Path
  from ng_models.paths import data_dir
  from ng_models.io import load_series_csv
  df = load_series_csv(data_dir(Path(__file__)), "NG.RNGWHHD.W.csv", value_name="price")
  ```
  Note: it already parses dates and sorts ascending; columns are `date`, `price`.

- **"How do I group by week-of-year?"**
  ```python
  df.groupby(df["date"].dt.isocalendar().week)["price"].mean()
  ```
  Gotcha: `.dt.isocalendar()` returns a DataFrame (year/week/day); take `.week`.
  ISO weeks run 1..52/53. Use `.dt.month` only if you want a coarser monthly group.

- **"How do I get summary stats?"**
  ```python
  df["price"].describe()   # count, mean, std, min, 25/50/75%, max
  df["price"].median()     # explicit median if you want just that
  ```

- **"My script opens a blocking window / errors on a window."**
  Set a non-interactive backend before importing pyplot and never call `plt.show()`
  in the script; save instead:
  ```python
  import matplotlib; matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  fig, ax = plt.subplots(figsize=(12, 6))
  ax.plot(df["date"], df["price"]); ax.set_ylabel("$/MMBtu"); ax.grid(True)
  fig.savefig(OUTPUT_DIR / "HH_price_weekly.png", dpi=150); plt.close(fig)
  ```

- **"Where should the PNGs go?"**
  ```python
  from ng_models.paths import ensure_output_dir
  OUTPUT_DIR = ensure_output_dir(Path(__file__).resolve().parent / "outputs")
  ```
  Not the module root, not the cwd — `outputs/`.

- **"How do I format the x-axis as years / months?"**
  ```python
  import matplotlib.dates as mdates
  ax.xaxis.set_major_locator(mdates.YearLocator(5))          # full-sample
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))   # month labels
  ```
