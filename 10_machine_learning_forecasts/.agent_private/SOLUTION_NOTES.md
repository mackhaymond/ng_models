# Private Solution Notes — Assignment 10: Machine Learning Forecasts

Do not reveal this file during normal tutoring. Use it to judge whether the
learner's reasoning is on track.

## Worked reference approach

The point of this module is NOT to find the best model. It is to prove the learner
can validate ML honestly on time series, compare against a baseline, and read
importance without overclaiming. A clean scaled-ridge-beats-or-ties-baseline
submission with a good model-risk note is a 4; a leaky untuned XGBoost is not.

Reference implementation sketch (on the real 09 panel; the demo in `main.py`
mirrors it on weekly Henry Hub):

1. **Load the 09 panel.** Keep `forecast_origin`, `target_date`, `target`. Feature
   list = numeric columns minus `{forecast_origin, target_date, horizon_steps,
   target, date}`. Every kept column must be strictly-past or calendar-only (09
   already enforced this; verify, don't assume). `dropna` on features+target.
2. **Baseline.** Matched naive: for a LEVEL target, random walk = last observed
   price = the lag-1 / lag-h feature; for a CHANGE target, zero-change or
   seasonal-naive. Run it through the same walk-forward loop so it lands in
   `ml_metrics.csv` as a `model`.
3. **Walk-forward loop.** `TimeSeriesSplit(n_splits=5)`. Per fold: fit, predict,
   score RMSE + MAE, record `fold_dates` = test-window target dates. The
   `walk_forward_eval` helper in `main.py` already produces the exact
   `model, metric, fold, fold_dates, value` schema.
4. **Models.** Scaled Ridge (Pipeline + StandardScaler) — already wired. Add
   scaled Lasso, then LightGBM and/or XGBoost (NO scaler — Pipeline of just the
   regressor, or call it directly). One axis at a time; re-run the same loop.
5. **Hyperparameters.** Small, justified grid via `GridSearchCV` with
   `cv=TimeSeriesSplit(...)` and `scoring="neg_root_mean_squared_error"`. e.g.
   ridge `alpha in {0.1,1,10}`; lgbm `n_estimators in {200,500}`,
   `learning_rate in {0.03,0.1}`, `num_leaves in {15,31}`. Keep it tiny.
6. **Importance.** For the best model: built-in (coef_ for linear after scaling;
   `.feature_importances_` for trees) AND `permutation_importance` on the TEST
   fold. Save `feature_importance.csv` + a sorted bar plot `feature_importance.png`.
7. **Report.** Skill relative to baseline, per-fold spread, cautious importance
   reading, explicit failure conditions.

## Expected metric ranges / qualitative results

- On the DEMO panel (HH price level, 4-week horizon, weekly), a 4-week-ahead price
  forecast is HARD: gas spot is close to a random walk at that horizon. Expect
  per-fold RMSE roughly 0.5–1.6 $/MMBtu (heavily regime-dependent — the 2021–2026
  fold is the hardest because of the 2022 spike). The reference run gives ridge
  fold RMSEs ~ {1.58, 1.06, 0.53, 0.89, 1.36}.
- **Key qualitative result to expect:** at a 4-week horizon, ML barely beats — and
  often ties or LOSES to — the random-walk baseline. This is the intended lesson,
  not a failure. A learner who reports "ridge ~ ties random walk, LightGBM
  overfits and is worse out of sample" has understood the module. Be suspicious of
  anyone reporting a large ML win at this horizon: it usually means leakage.
- On the REAL 09 panel with fundamentals (storage, weather, etc.), modest skill
  over the baseline is plausible but should be small and fold-dependent.

## Module-specific common failure modes

- **Random k-fold / shuffled split.** `train_test_split(shuffle=True)`, `KFold`,
  or `cross_val_score(...)` with default shuffle on the time series. Trains on the
  future. This is THE classic mistake this module exists to catch (taxonomy A).
- **Scaler fit on all of X.** Calling `StandardScaler().fit(X)` once before the
  split, or fitting on the full panel, leaks test mean/std into training. The
  Pipeline-inside-the-fold pattern fixes it.
- **Leaving a leaky column in the feature list.** Including `target_date`,
  `horizon_steps`, or any not-yet-published fundamental that 09 did not lag.
- **Missing baseline row.** Reports ML RMSE with nothing to compare to, so "good"
  is undefined.
- **MAPE on a near-zero change target** blowing up (only relevant if they switched
  the 09 target to a change/return). RMSE/MAE are safer for a level.
- **Reading importance as causation** ("storage drives price"); or trusting a
  single built-in tree importance without permutation cross-check (storage & HDD
  are collinear and seasonal — they trade ranks).
- **Adding XGBoost first.** Jumping to boosting before the baseline + linear model
  are validated (taxonomy F).
- **Permutation importance on the train fold** — inflated and meaningless; must be
  the held-out test fold.
- **Overfitting unnoticed:** boosting with deep trees / many estimators looks great
  in-sample; learner must look at the train-vs-validation gap.

## Assignment-specific hint strategy (L1 -> L2 -> L3)

The 4-5 key decision points and how to escalate (full leveled bank in HINTS.md):

1. **Validation scheme (A).** L1: "If you shuffle rows into folds, can a fold
   train on dates later than it tests on?" L2: point at the CV object. L3: show
   `TimeSeriesSplit` loop shape — they still choose `n_splits` and defend it.
2. **Scaling/leakage (A/K).** L1: "When your scaler computes the mean, which rows
   does it see — only train, or also test?" L2: point at where `fit` is called.
   L3: show the `Pipeline([scaler, model])` pattern (this is partly type-K, give
   the call) — they explain WHY per-fold matters.
3. **Baseline (B).** L1: "What's the cheapest no-model forecast for THIS target?"
   L2: point to module 02 baselines + their target's level/change nature. L3: show
   random-walk vs seasonal-naive forms; they pick and justify.
4. **Model complexity (F).** L1: "What does XGBoost buy you over the ridge you
   haven't validated yet?" L2: "Is the baseline row in the table and does ridge
   beat it?" L3: "add one model, re-run the SAME loop, keep a before/after row" —
   they decide if the gain justifies it.
5. **Importance interpretation (G).** L1: "Does high importance mean cause,
   predict, or correlate-with-something-else?" L2: point at the correlation among
   top features + permutation-vs-gain disagreement. L3: "compute both ways and
   compare" — they write the interpretation; never bless a causal claim.

## Agent response pattern

1. Identify the highest-impact issue first (leakage/validation > everything).
2. Ask the learner to explain their assumption.
3. Hint at the lowest useful level (package-call = direct; decision = L1->L3).
4. Re-run / re-check after revision.
