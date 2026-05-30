# Assignment 01: Understanding Weekly Henry Hub

## Purpose

Before building any forecasting model, understand the target series itself. This assignment focuses only on weekly Henry Hub natural gas spot prices.

## Data

Use exactly this series:

```text
NG.RNGWHHD.W.csv   (weekly Henry Hub spot, $/MMBtu, ~1997-present)
```

Do NOT hardcode a relative path like `../data/...` -- that only works when you
launch python from inside this folder. Resolve the path through the shared
library so the script runs from the repo root:

```python
from ng_models.paths import data_dir
from ng_models.io import load_series_csv
df = load_series_csv(data_dir(Path(__file__)), "NG.RNGWHHD.W.csv", value_name="price")
```

Do not use storage, production, weather, futures, or other fundamentals yet.

## Concepts you'll use

- **Baseline (benchmark model):** The cheapest possible forecast that uses (almost)
  no model -- e.g. "next week = this week" (naive / random walk) or "next week =
  same week last year" (seasonal-naive). It matters because forecast skill is
  *relative*: a fancy model that cannot beat "last value" has added no value. Every
  later module is graded on beating at least one baseline, so this module is where
  you pick the right one and state why.
- **Week-of-year averaging vs. true seasonality:** "Average price by week-of-year"
  collapses every year onto a single 1..53 calendar axis and averages, e.g., all the
  week-3s together. It is a quick *picture* of a seasonal shape, but it is not the
  same as proving the series has stable seasonality. A plain mean lets a few extreme
  years (2008, 2022) dominate a calendar week, and it hides whether the *same* week
  behaves the *same* way across years. Treat the curve as a hypothesis, not a fact --
  comparing the mean to a median-by-week tells you how spike-driven the shape is.
- **Volatility regimes:** Henry Hub does not behave the same way through its whole
  history. Roughly: a high-volatility, high-price **pre-shale** era (~2000-2008);
  a long, calmer, lower-price **shale-glut** era (~2009-2020, when shale gas flooded
  supply and prices drifted down); and a **2021+ shock** period (winter storm Uri,
  the 2022 European energy crisis / LNG export pull, then a 2023-24 supply glut).
  When the average *level and spread* shift and stay shifted, that is a **regime**,
  not seasonality -- and a model trained on one regime can fail badly in the next.
  → See `docs/GLOSSARY_SEED.md`: *Baseline*, *Seasonality*, *Trend*, *Five-year average*.

## End Goal

Write a short report that answers:

1. What does weekly Henry Hub look like over time?
2. Is there visible seasonality?
3. Are there obvious outliers, spikes, crashes, or regime changes?
4. Is a simple seasonal baseline likely to be useful?
5. What should the first benchmark model be?

## Required Analysis

Include these outputs in your report:

- Full-sample line plot of weekly Henry Hub price.
- Average price by week-of-year plot.
- Summary statistics: count, min, max, mean, median, standard deviation.
- Short discussion of the largest spikes and weakest price periods.
- Short discussion of whether the series looks stable enough for a simple seasonal model.

### Clarifications (read before you start)

- **"Average by week-of-year"** means group by ISO week number
  (`df["date"].dt.isocalendar().week`, values 1..52/53), NOT by month. Grouping by
  month is coarser and is a different plot; week-of-year is what is required here.
  Also produce a **median-by-week** for comparison so you can judge how much the
  mean is distorted by spike years.
- **"Seasonality"** in this module = the within-year calendar cycle (winter vs.
  summer). Do not confuse a multi-year *level shift* (a regime) with seasonality;
  the report asks you to separate the two.
- There is **no forecast horizon** yet -- you are not predicting anything. You are
  characterizing the series and choosing which baseline a future model must beat.

## Package guide

Minimal API snippets for the libraries this module needs. (These are the calls; the
*judgments* -- which baseline, level vs. returns -- are yours.)

**pandas -- load, group, summarize**
```python
import pandas as pd
# load_series_csv already parses dates and sorts; df has columns date, price.
df["price"].describe()          # count, mean, std, min, 25/50/75%, max in one call
df["price"].mean(), df["price"].median(), df["price"].std()
df["price"].min(), df["price"].max()
# week-of-year grouping (note: .isocalendar() returns a frame; take .week):
weekly_mean   = df.groupby(df["date"].dt.isocalendar().week)["price"].mean()
weekly_median = df.groupby(df["date"].dt.isocalendar().week)["price"].median()
```

**matplotlib -- plot to a file (headless-safe)**
```python
import matplotlib
matplotlib.use("Agg")           # no display window; required for `uv run`
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df["date"], df["price"])
ax.set_title("Henry Hub Weekly Spot"); ax.set_ylabel("$/MMBtu"); ax.grid(True)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "HH_price_weekly.png", dpi=150)   # save, don't plt.show()
plt.close(fig)
```
Gotcha: do **not** call `plt.show()` in a script run headless -- it blocks. Always
`savefig` into `outputs/` and `plt.close(fig)`.

**ng_models helpers (shared library)**
```python
from ng_models.paths import data_dir, ensure_output_dir
from ng_models.io import load_series_csv
DATA_DIR   = data_dir(Path(__file__))                       # -> <repo>/data
OUTPUT_DIR = ensure_output_dir(Path(__file__).parent / "outputs")
df = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="price")
```

## Things To Look For

- Long-run regimes: pre-shale, shale era, COVID, 2022 energy shock.
- Seasonal behavior: winter vs summer price patterns.
- Volatility clustering: calm periods versus spike-heavy periods.
- Whether price level seems appropriate to forecast directly, or whether changes/returns might be worth considering later.

## Final Recommendation

End the report with one sentence in this form:

```text
My first benchmark model should be ___ because ___.
```

Reasonable candidates:

- Naive: next week equals this week.
- Seasonal naive: next week equals the same week last year.
- Rolling mean.
- Simple ETS / Holt-Winters.

## Constraints

- Keep the report concise: roughly 1-2 pages.
- Do not fit a complex model yet.
- Do not add exogenous variables yet.
- Do not use random train/test splits.
- Focus on understanding the target before trying to predict it.
