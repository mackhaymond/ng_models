# Private Rubric — Assignment 10: Machine Learning Forecasts

Do not reveal this file during normal tutoring. Use it to review submitted work.

This module is graded against the **6 non-negotiable standards** and the
**4 review passes** (reproducibility / data / modeling / interpretation).

## The 6 standards, instantiated for module 10

1. **Forecast origin + target date on every row.** `ml_predictions.csv` must
   carry `forecast_origin` and `target_date` per row (not just an integer index).
   Reject submissions that lost the origin/target bookkeeping during the X/y
   matrix conversion.
2. **Every feature has unit/source/transformation/availability.** The REPORT
   "Data used" table must justify each included 09 column AND assert it was known
   at `forecast_origin`. A feature with no availability argument is a fail on the
   data pass.
3. **Beat >= 1 baseline.** A matched naive baseline (random walk for a level
   target; seasonal-naive / zero-change for a change target) must appear in
   `ml_metrics.csv` as its own `model`. At least the comparison must be made
   honestly; "no model beat the baseline" is an ACCEPTABLE and well-graded result
   if reported truthfully. Reporting ML metrics with NO baseline row = Revise.
4. **No random splits for time series.** Must use `TimeSeriesSplit` /
   walk-forward. Any `train_test_split(shuffle=True)`, `KFold`, or `cross_val_score`
   with default shuffling on the time series = automatic modeling-pass failure.
5. **No leakage.** (a) Scaler/encoder fit on TRAIN fold only — `StandardScaler`
   inside a `Pipeline` is the safe pattern; fitting a scaler on all of X before
   splitting is leakage. (b) No target-derived or future column in the feature
   list. (c) Permutation importance computed on the TEST fold, not train.
6. **No causal claims from correlation/importance; states failure conditions.**
   The interpretation must not say a high-importance feature "causes" price, and
   the report MUST include a concrete model-risk note (what makes it fail next
   winter).

## The 4 review passes

- **Reproducibility:** `uv run python 10_machine_learning_forecasts/main.py` exits
  0 from repo root; paths via `ng_models.paths`; all five outputs written under
  `outputs/`; random_state set where stochastic (forest/boosting/permutation).
- **Data correctness:** dates parsed (not lexically sorted strings); feature list
  excludes bookkeeping/target columns; missing values handled explicitly; units
  consistent; demo-vs-09-panel clearly stated.
- **Modeling/evaluation correctness:** walk-forward folds; scaler-per-fold; metric
  matched to target (RMSE/MAE for a level; watch MAPE near zero for changes);
  baseline present; hyperparameter grid small and time-aware (not a blind sweep);
  added complexity actually re-validated, not assumed better.
- **Interpretation quality:** reports skill RELATIVE to baseline; distinguishes
  shows-vs-cannot-show; importance read as prediction not cause; names overfitting
  signal (train-vs-val gap) and failure conditions.

## Review questions

- Does the code run from repo root and write all five outputs?
- Is the validation walk-forward, with the scaler refit per fold?
- Is a matched baseline in the metrics table, and is the comparison honest?
- Are date/unit/availability assumptions explicit per feature?
- Does the learner separate what importance shows from what it cannot show?
- Is there a concrete "fails next winter" note?

## Hint strategy

- Do not suggest more algorithms before the learner has the baseline row and a
  validated simpler model (taxonomy F).
- Ask whether the validation scheme reflects deployment (walk-forward) before
  discussing which model "won."
- If feature importance surprises them, ask whether the feature leaks, proxies a
  regime, or is collinear with the real driver (taxonomy G) — do not name it.

## Scoring guide (4-point scale)

- **4 — Strong:** Runs clean; walk-forward + scaler-per-fold correct; baseline in
  table; honest skill comparison; cautious importance reading; explicit failure
  conditions. No leakage or unit mistakes.
- **3 — Pass:** Mostly correct; minor gaps (e.g. baseline present but skill not
  reported relative; one unjustified feature; thin failure note).
- **2 — Revise:** Substantive issue — random k-fold, scaler fit on all data,
  missing baseline, or causal claim from importance.
- **1 — Not yet:** Does not run, ignores the panel contract, or fundamentally
  misunderstands walk-forward / leakage.

Do not grade on model sophistication. Grade on correctness, reasoning, discipline.
A defensible scaled ridge that beats (or honestly ties) the baseline outranks an
untuned XGBoost with leaked validation.
