# Private Solution Notes — Assignment 01: Understanding Weekly Henry Hub Before Modeling

Do not reveal this file during normal tutoring. Use it to judge whether the
learner's reasoning is on track and to calibrate hints.

## Worked reference approach (sketch — do NOT hand to the learner)

1. Load weekly Henry Hub via `load_series_csv(data_dir(Path(__file__)),
   "NG.RNGWHHD.W.csv", value_name="price")`. Confirm ~1531 rows, 1997-01-10 to
   2026-05-15, weekly, $/MMBtu.
2. Full-sample line plot of `price` vs `date`. The defining visual: NOT a steady
   trend, but distinct regimes with very different levels and volatility.
3. Average-by-week-of-year using `df["date"].dt.isocalendar().week` groupby mean,
   AND a median-by-week. The mean curve shows a winter > summer hump; the median
   curve is flatter, revealing the mean hump is partly a few spike years.
4. Summary stats from `.describe()`. The mean (~4.10) sits well above the median
   (~3.37) and std (~2.16) is ~half the mean → right-skewed, spike-driven.
5. Recommend a baseline, justified by the plots, and state failure modes.

## Expected numbers / qualitative results

- count ≈ 1531; min ≈ 1.34; max ≈ 14.49; mean ≈ 4.10; median ≈ 3.37; std ≈ 2.16.
- Mean > median by ~$0.7 → right skew from spikes (the key stat-level observation).
- Regime structure the report should land on:
  - **Pre-shale (~2000-2008):** high and volatile, big 2005 (hurricanes) / 2008 spike.
  - **Shale glut (~2009-2020):** lower level, calmer; structural supply increase
    pushed prices down and kept them there — a level shift, not a seasonal dip.
  - **2021+ shocks (~2021-present):** winter storm Uri (Feb 2021), the 2022
    European energy crisis / LNG-export pull (~$9-10), then a 2023-24 glut.
- A defensible benchmark sentence: "A naive (last-week) or seasonal-naive baseline
  is the first benchmark, but treat seasonal-naive as a WEAK standalone model
  because Henry Hub variation is dominated by regimes and shocks rather than a
  stable weekly seasonal cycle." Either naive or seasonal-naive is acceptable IF
  justified; seasonal-naive should be flagged as weak here, not strong.

## Why seasonal-naive is weak here (the crux)

Seasonal-naive ("same week last year") only works if the same calendar week behaves
the same way across years. Henry Hub fails this: (a) the LEVEL shifts across regimes
(a 2010 January and a 2022 January are different worlds), so last-year's same-week
value can be anchored in a dead regime; (b) the big moves are weather/supply SHOCKS
that don't repeat on the calendar — a cold-snap spike in one February says nothing
about the next. The week-of-year average looks seasonal mostly because winter heating
demand is real, but the seasonal AMPLITUDE is small relative to regime gaps and spike
magnitudes. So seasonal-naive is an easy null, not a strong one.

## Module-specific common failure modes

- Hardcoding `../data/NG.RNGWHHD.W.csv` (the original bug) → fails from repo root.
  Fix: `data_dir(Path(__file__))`.
- Saving PNGs to the module root or cwd instead of `outputs/`.
- `plt.show()` left in → blocks/errs on headless `uv run`.
- Calling `.dt.isocalendar()` and using the whole frame instead of `.week`.
- Reporting the MEAN-by-week as "the seasonality" without checking the median →
  overstates a spike-driven hump (taxonomy I).
- Calling a regime "seasonality" (or vice versa): treating the shale-era level drop
  as a slow seasonal trend rather than a structural break (taxonomy I).
- Writing causal claims for spikes ("cold weather caused the 2022 spike") without
  noting storage/LNG confounds (taxonomy J).
- Picking seasonal-naive and calling it strong without acknowledging regimes/shocks.
- Recommending ARIMA / adding fundamentals here (out of scope, taxonomy F).

## Assignment-specific hint strategy (L1 → L2 → L3)

Five key decision points. Keep modeling decisions leveled; answer pure API directly.

**1. Which baseline to recommend (taxonomy B)**
- L1: "What is the cheapest forecast for next week's price with no model? Does it
  even need to capture the winter hump?"
- L2: "You have two plots — the full-sample (regimes/spikes) and the week-of-year
  curve. Which one dominates the variance? Let that pick naive vs seasonal-naive."
- L3: "naive: `y_hat[t+1]=y[t]`; seasonal-naive: `y_hat[t]=y[t-52]`. Pick one and
  write why the other is the wrong null here." (Don't pick for them.)

**2. Is the week-of-year average real seasonality? (taxonomy I)**
- L1: "Does the same calendar week behave the same across years, or is the hump a
  few extreme years pulling the average up?"
- L2: "Add a median-by-week curve next to the mean-by-week and compare the shapes."
- L3: "`df.groupby(df['date'].dt.isocalendar().week)['price'].median()` — overlay
  it; you decide which summary tells the honest seasonality story."

**3. Regime vs seasonality (taxonomy I)**
- L1: "Is the long mid-sample drop a slow recurring cycle, or did the level move
  down and STAY down?"
- L2: "Look at the full-sample plot's rolling level pre- vs post-2009 (shale)."
- L3: "A level that shifts and persists is a regime; a cycle returns each year. Name
  each span and label it; don't merge the two stories."

**4. Level vs returns for later modeling (taxonomy D)**
- L1: "Do you want to forecast WHERE price is or HOW MUCH it moves? Does the fat
  right tail change that?"
- L2: "Compare mean vs median and the std-to-mean ratio you printed."
- L3: "This module only asks you to NOTE the implication, not transform yet — write
  one sentence on whether the level is well-behaved enough to model directly."

**5. Spike explanations / causality (taxonomy J)**
- L1: "Could something other than the reason you wrote also explain that spike?"
- L2: "Re-read your sentence; swap 'caused' for 'coincided with' — does the evidence
  still hold?"
- L3: "State it as an association with the confound named (storage, LNG, weather);
  one plot cannot establish cause."

## Agent response pattern

1. Identify the highest-impact issue first (run/reproducibility before nuance).
2. Ask the learner to explain their assumption.
3. Hint at the lowest useful level.
4. Re-run / re-check after revision.
