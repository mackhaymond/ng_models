# Report — Assignment 04: Backtesting and the 'What Was Known Then?' Rule

Copy this file to `REPORT.md` and fill every section. Replace the *italic
guidance* with your own words and numbers.

## 1. Objective

*In 2-4 sentences: what protocol are you validating and on what series? State
the target (a price level or a change?) and the horizon. Make clear the goal is
honest evaluation, not a winning model.*

## 2. Vocabulary

Write 1-2 sentences each, in your own words (not copied from the glossary).

- **rolling origin:** *The point in time you "stand at" to make a forecast; the
  backtest moves it forward one step at a time.*
- **walk-forward validation:** *Fitting/forecasting using only data up to each
  origin, then advancing — the time-series-correct way to estimate skill.*
- **leakage:** *Using any information that would not have been known at the
  forecast origin; it inflates backtest scores and fails live.*
- **forecast origin:** *The date the forecast is made (the last training row).*
- **horizon:** *How far ahead the target sits from the origin (here, in weeks).*
- **expanding window:** *Training set grows from row 0 as the origin advances.*
- **sliding window:** *Fixed-length training set that moves forward, dropping
  the oldest rows.*

## 3. Data used

| Source / file | Frequency | Units | Date range | Why used |
|---|---:|---|---|---|
| `data/NG.RNGWHHD.W.csv` (Henry Hub spot) | Weekly | $/MMBtu | *1997-01-10 → 2026-05-15 (fill from your run)* | *Single, clean series to focus on the backtest protocol* |

## 4. Data decisions

*Describe: how dates were parsed (handled by the loader), how you treated any
missing `hh_price` rows, the chosen `min_train`, `horizon`, `step`, and
expanding vs. sliding. Note the `shift`-aligns-by-position assumption if you use
seasonal-naive. State that raw data was not modified.*

## 5. Leakage checklist (reusable)

*Write a concrete, code-level checklist you will reuse in later modules. Example
entries — make them yours:*

- [ ] Every value feeding a prediction comes from `train_idx` (origin or earlier).
- [ ] No `rolling`/`mean`/`std` computed over the full series, only over training rows.
- [ ] No scaler/normalizer fit on the full sample.
- [ ] `target_date` is strictly after `origin_date` on every row.
- [ ] No row index `>= test_idx` used to build a prediction.

## 6. Outputs checklist

- [ ] `outputs/backtest_metrics.csv`
- [ ] `outputs/backtest_predictions.csv`
- [ ] `outputs/error_by_origin.png`
- [ ] `REPORT.md`

## 7. Results

*Paste your metrics table (one row per model) and reference the error plot.
Example shape — fill with your real numbers:*

| model | mae | rmse | mape | smape | beats naive? |
|---|---:|---:|---:|---:|---|
| naive_last | *0.21* | *0.39* | *...* | *...* | — (this is the null) |
| *seasonal_naive_52* | *...* | *...* | *...* | *...* | *yes/no* |

Example predictions rows (your `backtest_predictions.csv` should look like this):

| origin_date | target_date | horizon | actual | prediction | model |
|---|---|---:|---:|---:|---|
| 2001-12-28 | 2002-01-04 | 1 | 2.13 | 2.18 | naive_last |
| 2001-12-28 | 2002-01-04 | 1 | 2.13 | 2.45 | seasonal_naive_52 |

## 8. Interpretation

*What do the metrics mean for natural gas? Lead with the metric you chose and
why (type H). State which baseline the second model had to beat and whether it
did, RELATIVE to the naive (skill), not just the raw number. Do NOT claim any
causation. Tie the worst error period (from the plot) to a real market event if
you can (e.g., Feb 2021 Winter Storm Uri, 2022 volatility).*

## 9. Model or analysis limitations

*What could be wrong, incomplete, unstable, or leaked? Examples to address: is
`shift(52)` a valid seasonal lag given the weekly grid? Does a single horizon
generalize? Would the result hold in a different sub-period?*

## 10. Next questions

*List 3 concrete questions you would investigate next (e.g., does a multi-step
horizon degrade smoothly? does a sliding window beat expanding post-2010? which
period drives most of the error?).*
