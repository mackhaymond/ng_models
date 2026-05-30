# Report — Assignment 02: Calendar Structure and Naive Forecast Baselines

> Copy this file to `REPORT.md` and fill it in. Keep it to ~1-2 pages. Every
> chart needs a sentence on what it shows AND what it does not show.

## 1. Objective

In 2-4 sentences, explain what this assignment is trying to learn. State your
chosen forecast horizon h and whether it is 1-step or multi-step (e.g. "I forecast
the weekly Henry Hub spot price h=4 weeks ahead, a multi-step forecast, to
establish baselines later models must beat").

## 2. Vocabulary

Write each in your own words (1-2 sentences). Cross-check `docs/GLOSSARY_SEED.md`.

- **forecast horizon:** how far ahead you predict; here, how many weekly rows
  between the forecast origin and the target date.
- **forecast origin / target date:** the date you stand on (only past data
  allowed) vs. the future date you are predicting.
- **baseline:** a cheap, no-model forecast your real model must beat to matter.
- **naive forecast:** "the future equals the last observed value" (`y_hat=y[t]`).
- **seasonal naive:** "the future equals the same week one cycle (~52 weeks) ago."
- **expanding window:** a statistic that at each origin uses only data up to that
  origin (and grows over time) — the leakage-safe alternative to full-sample.
- **train/test split (chronological):** train on the earlier block, test on a
  contiguous later block; never a random shuffle for time series.
- **MAE:** average absolute error in $/MMBtu; robust, easy to read.
- **RMSE:** root-mean-square error in $/MMBtu; punishes large misses more.
- **MAPE:** average percentage error; unit-free but unstable when price is near 0.

## 3. Data used

| Source / file | Frequency | Units | Date range | Why used |
|---|---:|---|---|---|
| `data/NG.RNGWHHD.W.csv` | Weekly | $/MMBtu | 1997-01-10 to 2026-05-15 | Target series (weekly Henry Hub spot) |

## 4. Data decisions

Describe date parsing, missing values, the calendar columns you added, your chosen
horizon h and the exact shift each baseline uses to stay past-only, and how you
excluded warm-up / tail NaN rows. State explicitly which statistics are expanding
(not full-sample) and why that matters here.

## 5. Outputs checklist

- [ ] `outputs/baseline_metrics.csv`
- [ ] `outputs/test_forecasts.csv`
- [ ] `outputs/baseline_comparison.png`
- [ ] `REPORT.md`

## 6. Results

State your exact test window (start and end target_date) and paste the metrics
table. Example shape (numbers illustrative — fill with yours):

| baseline | mae | rmse | mape |
|---|---:|---:|---:|
| naive | 0.31 | 0.45 | 0.11 |
| exp_mean | 1.20 | 1.55 | 0.42 |
| woy_median | 1.05 | 1.38 | 0.37 |

Then one sentence per chart: what `baseline_comparison.png` shows and what it does
not (e.g. "shows the test-window fit of three baselines but not their behavior in
the 2021-22 spike, which is outside this window").

## 7. Interpretation

Which baseline wins on MAE? On RMSE? Do they agree, and if not, what does the
disagreement tell you (RMSE penalizing a few big misses)? Which baseline would you
force later models to beat, and why? Avoid causal language about *why* price moved
— this is about forecast accuracy, not cause.

## 8. Model or analysis limitations

What could be wrong, incomplete, unstable, or leaked? Address: did you verify no
full-sample statistic crept in? Is the test window representative or unusually
calm/volatile? What would make even the naive baseline fail (regime change,
structural break)?

## 9. Next questions

List 3 concrete questions you would ask next (e.g. "does differencing / log returns
change which baseline wins?", "how does the ranking change at h=1 vs h=8?", "would
a rolling-window mean beat the expanding mean?").
