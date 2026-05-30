# Report — Assignment 10: Machine Learning Forecasts: Linear Models, Trees, and Boosting

## 1. Objective

In 2-4 sentences: state the target (level vs change), the horizon, the forecast
origin, and which model classes you compared. Name the baseline every model must
beat. Example opener: "I forecast the Henry Hub price 4 weeks ahead (a level)
from each weekly origin, comparing scaled ridge, lasso, and LightGBM against a
random-walk baseline under walk-forward validation."

## 2. Vocabulary

Write 1-2 sentences each, in your own words (cross-check `docs/GLOSSARY_SEED.md`):

- **regularization:** _A penalty on coefficient size that keeps a linear model
  simple so it generalizes; `alpha` controls strength. Say which (L1/L2) you used._
- **cross-validation:** _Splitting data into train/test folds to estimate
  out-of-sample skill; for time series it must be time-ordered (walk-forward)._
- **feature importance:** _A score for how much the model relied on each feature;
  note it is association, not causation, and built-in tree scores show no direction._
- **permutation importance:** _Importance measured by shuffling one feature's
  column and seeing how much the out-of-sample score degrades; model-agnostic._
- **gradient boosting:** _An ensemble of small trees built sequentially, each
  fitting the residual errors of the running ensemble; learning_rate sizes each step._
- **overfitting:** _Learning training noise instead of signal; great in-sample,
  poor out-of-sample. Tell: large train-vs-validation error gap._
- **hyperparameter:** _A setting chosen before training (alpha, max_depth,
  learning_rate) that the model does not learn; tuned via time-aware CV._

## 3. Data used

One row per series/column group you fed the models. Example row shown.

| Source / file | Frequency | Units | Date range | Why used |
|---|---|---|---|---|
| `09 model_panel.csv` (e.g. `hh_price_lag_4`) | Weekly | $/MMBtu | 2010-01 .. 2026-05 | Strictly-past price lag; leakage-safe predictor |
| | | | | |

## 4. Data decisions

State: which 09 columns you included as features and why each is known at
`forecast_origin` (leakage-safe); how you handled missing values (e.g.
`dropna` on features+target); whether you scaled (and that the scaler was fit on
train folds only); your target definition (level vs change) and horizon. If you
used the demo fallback, say so and note it is not graded work.

## 5. Outputs checklist

- [ ] `outputs/ml_metrics.csv` (`model, metric, fold, fold_dates, value`)
- [ ] `outputs/ml_predictions.csv` (`model, fold, forecast_origin, target_date, actual, prediction`)
- [ ] `outputs/feature_importance.csv`
- [ ] `outputs/feature_importance.png`
- [ ] `REPORT.md`

## 6. Results

Show the model-vs-baseline comparison aggregated across folds. Report each metric
*relative to the baseline* (a skill score), not just the raw number. Example:

| model | mean RMSE | mean MAE | beats baseline? |
|---|---:|---:|---|
| baseline (random walk) | 1.08 | 0.71 | — |
| ridge (alpha=1) | 1.08 | 0.71 | ~tie |
| lightgbm | _fill_ | _fill_ | _yes/no_ |

State per-fold spread too (one fold can dominate the mean). Reference the saved
`feature_importance.png` and say what its top features are.

## 7. Interpretation

What do the results mean for natural-gas forecasting? Address: did added model
complexity actually buy out-of-sample skill over the baseline, or not? For your
top feature(s), explicitly say whether it is a cause, a predictor, or a proxy for
seasonality/another collinear feature — and how you could tell. **No causal
claims from importance.**

## 8. Model or analysis limitations

What could be wrong, incomplete, unstable, or leaked? Required: the model-risk
note — what specific conditions (a price regime not in training, a cold-snap
beyond historical range, a feature that stops being available in time) would make
this model fail next winter. Note any train-vs-validation gap (overfitting signal).

## 9. Next questions

List 3 concrete questions you would ask next (e.g. quantile/interval forecasts,
adding a fundamentals feature, testing on a held-out winter only).
