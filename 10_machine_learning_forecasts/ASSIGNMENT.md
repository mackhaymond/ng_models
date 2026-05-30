# Assignment 10: Machine Learning Forecasts: Linear Models, Trees, and Boosting

**Phase:** Advanced Modeling  
**Level:** Advanced  
**Estimated time:** 10-16 hours

## Data scope

Use the leakage-safe, model-ready panel from Assignment 09.

Expected data inputs:

- `09_feature_table_leakage/outputs/model_panel.csv` (one row per forecast
  origin: a future `target`, plus predictor columns all known at `forecast_origin`).

If you have not finished Assignment 09 yet, `main.py` falls back to a
self-contained DEMO panel built from weekly Henry Hub so the module still runs.
The demo target is **the Henry Hub price 4 weeks ahead** (a level). Treat the
demo only as scaffolding to learn the mechanics; your graded work uses the real
09 panel.

## Terms to learn

`regularization`, `cross-validation`, `feature importance`, `permutation importance`,
`gradient boosting`, `overfitting`, `hyperparameter`

Before coding, write one plain-English sentence for each term in your own words.

## Concepts you'll use

Ground-up explanations. Cross-reference `docs/GLOSSARY_SEED.md` for the full
entries (linked terms are anchors there).

- **Regularization (L1 / L2, ridge / lasso).** An unregularized linear model can
  give any feature a huge coefficient if that helps it fit the training noise.
  Regularization adds a penalty on coefficient *size* to the loss, so the model
  pays a price for complexity and stays simpler. **Ridge (L2)** penalizes the sum
  of squared coefficients (shrinks all of them toward zero); **Lasso (L1)**
  penalizes the sum of absolute coefficients (can push some exactly to zero, doing
  feature selection). The strength is `alpha` in scikit-learn: bigger `alpha` =
  more shrinkage = simpler model = less overfitting but more bias. This is the
  main defense against overfitting for linear models.
- **Overfitting.** When a model learns the quirks/noise of the training data
  instead of the real signal: it looks great in-sample and fails out-of-sample.
  The tell is a big gap between training error and validation error. Like
  memorizing the practice-test answers instead of learning the subject.
- **Walk-forward (rolling-origin) cross-validation.** To estimate out-of-sample
  skill you split data into train/test folds. For time series the split must
  respect time order: train only on the *past*, test on the *future*, then roll
  the origin forward and repeat. A plain shuffled **k-fold** puts future rows in
  the training set and past rows in the test set — that is leakage, it inflates
  the score, and the model then disappoints in production. `TimeSeriesSplit` does
  the time-ordered version for you.
- **Feature scaling.** Standardizing each feature to mean 0, std 1 (`z = (x-μ)/σ`).
  **Linear/regularized models need it** — otherwise a feature measured in big
  numbers (say storage in Bcf) dominates the regularization penalty over a feature
  in small numbers (a week index), purely because of units. **Tree models and
  boosting do NOT need it** — they split on thresholds, so any monotonic rescaling
  leaves the splits unchanged. Critical rule: fit the scaler on the *training* fold
  only, then apply it to the test fold; fitting on all the data leaks test
  information into training.
- **Trees vs. boosting (intuition).** A single decision tree splits the feature
  space into boxes and predicts a constant in each box — flexible but high
  variance. A **random forest** averages many trees built on bootstrap samples to
  reduce variance. **Gradient boosting** (LightGBM / XGBoost) instead builds trees
  *sequentially*: each new small tree fits the leftover errors (residuals) of the
  running ensemble, with a `learning_rate` controlling how big each correction is.
  Boosting is usually the strongest model on tabular feature tables and captures
  nonlinearities and interactions for free — but it overfits readily and needs
  honest validation.
- **Feature importance vs. causality.** Importance scores rank how much the model
  *relied* on each feature in this sample. That is association/prediction, not
  cause. A feature can rank high because it genuinely drives the target, because it
  proxies a third variable (seasonality, regime), or because it is collinear with
  the real driver. Built-in tree "gain" importances can also be biased toward
  high-cardinality features and never show *direction*. Never write "feature X
  causes the price" from an importance chart.
- **Hyperparameter.** A setting you choose *before* training that the model does
  not learn from data: `alpha` for ridge/lasso, `max_depth` / `num_leaves` /
  `n_estimators` / `learning_rate` for boosting. You tune these with (time-aware!)
  cross-validation. The model learns *parameters*; you choose *hyperparameters*.

## Package guide

Minimal, copy-pasteable API for the libraries this module needs. (These are the
*calls*; whether to use a given model/penalty/grid is a modeling decision — see
the TODOs in `main.py`.)

**Time-ordered CV — `sklearn.model_selection.TimeSeriesSplit`**
```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for fold, (train_idx, test_idx) in enumerate(tscv.split(X), start=1):
    model.fit(X[train_idx], y[train_idx])
    y_hat = model.predict(X[test_idx])   # train always earlier than test
```

**Scale + regularized linear model in one object — `Pipeline` + `StandardScaler` + `Ridge`/`Lasso`**
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso
pipe = Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=1.0))])
pipe.fit(X_train, y_train)            # scaler is fit on X_train ONLY -> no leakage
preds = pipe.predict(X_test)
# Lasso(alpha=0.1) is the same call with the L1 penalty.
```

**Boosting (no scaler needed) — `lightgbm` / `xgboost`**
```python
from lightgbm import LGBMRegressor
gbm = LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=31)
gbm.fit(X_train, y_train); preds = gbm.predict(X_test)
# xgboost: from xgboost import XGBRegressor; XGBRegressor(n_estimators=..., ...)
```

**Small, time-aware hyperparameter search — `GridSearchCV`**
```python
from sklearn.model_selection import GridSearchCV
gs = GridSearchCV(pipe, {"model__alpha": [0.1, 1, 10]},
                  cv=TimeSeriesSplit(n_splits=5),
                  scoring="neg_root_mean_squared_error")
gs.fit(X, y); print(gs.best_params_)   # keep the grid SMALL and justified
```

**Model-agnostic importance — `sklearn.inspection.permutation_importance`**
```python
from sklearn.inspection import permutation_importance
r = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=0)
# r.importances_mean[i] = how much the score got WORSE when feature i was shuffled
```

**Metrics — use the repo helpers** (`from ng_models.metrics import rmse, mae, summarize_predictions`).
`summarize_predictions(df, actual_col="actual", pred_col="prediction")` returns
all four metrics at once for a predictions frame.

## Learning goals

- Fit ML models only after building baselines and leakage-safe panels.
- Compare model classes under time-series validation, against a baseline.
- Learn how to interpret feature importance cautiously (not causally).

## Tasks

1. Train a regularized linear regression (ridge and/or lasso, **scaled**), a
   tree/forest or gradient-boosting model, and one LightGBM/XGBoost model.
2. Validate with **walk-forward** CV (`TimeSeriesSplit`), never random k-fold.
   Report one metric row per (model, metric, fold).
3. Include the matched **naive baseline** (random walk for a level target;
   seasonal-naive or zero-change for a change target — pick the one that fits your
   09 target) in the comparison table. At least one ML model must beat it.
4. Inspect feature importance OR permutation importance for your **best** model.
   Report it two ways (built-in vs permutation) and explain disagreements.
5. Write a model-risk note: what could make this model fail next winter?

## Deliverables

- `outputs/ml_metrics.csv` — schema: `model, metric, fold, fold_dates, value`
  (one row per model × metric × fold; `fold_dates` is the test window of that
  fold, e.g. `2021-07-23..2026-05-15`).
- `outputs/ml_predictions.csv` — per-row out-of-sample predictions, with
  `model, fold, forecast_origin, target_date, actual, prediction`.
- `outputs/feature_importance.csv`
- `outputs/feature_importance.png`
- `REPORT.md`

## Rules

- Keep raw data immutable; do not edit `data/`.
- Save generated files under this assignment's `outputs/` folder. Resolve paths
  with `ng_models.paths` (`data_dir(HERE)` / `ensure_output_dir(...)`), never
  relative `../data`.
- Write down every assumption about dates, units, frequency, and missing values.
- Every chart needs a sentence saying what it shows AND what it does not show.
- Do not move to a more complex model until the baseline comparison is in place
  and your simpler model is wired up and validated.
- No causal claims from feature importance.

## Questions to answer in `REPORT.md`

- What is the target (level vs change), at what horizon, from what origin?
- What dates and units are involved? Which 09 columns did you include as features
  and why are they all leakage-safe?
- Which baseline did you have to beat, and did any model beat it out of sample?
- What was the most important data decision?
- What result surprised you?
- What would you not trust yet? What would make this model fail next winter?
- What should the next assignment investigate?
