# Hint Bank — Assignment 14: Capstone Forecast System + Memo

Do not reveal this file. Deliver hints as L1 -> L2 -> L3 prompts, lowest level
that unblocks. Each sticking point names its `QUESTION_TAXONOMY.md` TYPE.
Type (K) package-API stalls get DIRECT working code; modeling decisions (A-J, L)
stay leveled and never hand over the decision. This is the capstone: most stalls
are integration/discipline, not new technique.

---

## 1. Target / origin / horizon (TYPE D & E — target definition)

Sticking point: learner is unsure which column is the target or whether to model a
level vs a change in the capstone.

- **L1:** "Write one sentence: 'I forecast [what] at [horizon] from [origin].'
  Which single panel column is the [what], and is it a level, a change, or a return?"
- **L2:** "The panel already carries `forecast_origin`, `target_date`, and the
  target column you defined in module 09. Look at how that column was built —
  `make_forward_target` on the price (level) vs on a change column. Set `TARGET_COL`
  in Stage 2 to match."
- **L3:** "Confirm `TARGET_COL = 'target_hh_next'` (or your renamed target), then
  state which baseline FAMILY that target implies (random walk for a level,
  zero-change for a change). You make and defend the call."

## 2. Baseline selection incl. futures benchmark (TYPE B)

Sticking point: only one baseline, or no market/futures benchmark, or unsure how a
futures price can be a benchmark.

- **L1:** "What is the cheapest no-model forecast for THIS target? And what number
  does the MARKET itself imply for the same horizon — could you compare to that?"
- **L2:** "Three honest comparisons are required here: persistence (last known
  level), seasonal-naive (52 weeks back), and the NYMEX front-month settle as the
  market benchmark. `NG.RNGC1.W.csv` is in `data/`. Module 02 has the naive nulls."
- **L3:** "Prediction-column shapes (you pick which is the right null and justify):
  ```python
  df['pred_persistence'] = df['hh_price_lag_1']           # last known level
  # seasonal-naive: value 52 weekly rows back, aligned to the origin
  # futures benchmark: merge_asof NG.RNGC1.W on forecast_origin (see hint 4)
  ```
  Then say WHY each is right/wrong for your target — and that the futures price is a
  *benchmark to beat*, not itself a forecast (it carries risk premia)."

## 3. Walk-forward, replacing the in-sample placeholder (TYPE A — leakage)

Sticking point: reports the starter's in-sample numbers, or reaches for a shuffled
split.

- **L1:** "The starter scores baselines IN-SAMPLE just so the file exists. Are
  those numbers honest about next year? If you shuffled rows into folds, could a
  fold train on dates LATER than the dates it tests?"
- **L2:** "Replace the Stage-5 placeholder loop. You want every training index
  earlier than every test index — `TimeSeriesSplit` guarantees that; plain `KFold`
  / `train_test_split(shuffle=True)` does not. Score baselines AND the model on the
  SAME test rows."
- **L3 (loop shape is type-K — give it; n_splits/window is the decision):**
  ```python
  from sklearn.model_selection import TimeSeriesSplit
  for tr, te in TimeSeriesSplit(n_splits=5).split(df):
      model.fit(X.iloc[tr], y.iloc[tr])
      df.loc[df.index[te], 'pred_final'] = model.predict(X.iloc[te])
      # baselines need no fit — just read their column on the same te rows
  ```
  "You choose `n_splits` and expanding vs sliding window, and justify it."

## 4. Futures as-of join / feature timing (TYPE A — leakage / availability)

Sticking point: how to attach the futures settle without looking forward.

- **L1:** "On a given forecast_origin, which futures settle had ALREADY printed?
  The one dated that day, or one dated later?"
- **L2:** "Use `merge_asof` with `direction='backward'` keyed on `forecast_origin`
  so each origin gets the most recent settle AT OR BEFORE it — never a future one."
- **L3 (type-K API — give it; the column choice C1 vs C2 is the decision):**
  ```python
  fut = load_series_csv(DATA_DIR, "NG.RNGC1.W.csv", value_name="nymex_c1")
  df = pd.merge_asof(
      df.sort_values("forecast_origin"),
      fut.rename(columns={"date": "fut_asof"}).sort_values("fut_asof"),
      left_on="forecast_origin", right_on="fut_asof", direction="backward")
  ```
  "Decide whether the FRONT month (C1) matches your horizon or you need C2, and
  defend it."

## 5. Final model — should I add LightGBM yet (TYPE F — complexity)

Sticking point: jumping to boosting before a linear model beats the baseline; or
not knowing when to stop adding features.

- **L1:** "What does LightGBM buy you over a Ridge — and have you PROVEN Ridge beats
  persistence out of sample yet?"
- **L2:** "Before boosting: is the baseline row in `final_model_metrics.csv`, and
  does your linear model beat it across folds? Add ONE model, re-run the IDENTICAL
  walk-forward loop, keep a before/after row."
- **L3:** "Stop adding features/complexity when the next addition does not improve
  OUT-OF-SAMPLE skill over the baseline. At a 1-week horizon, a model that only
  ties persistence is the EXPECTED result and a valid finding — not a failure to
  fix by piling on trees. You decide whether the gain justifies the complexity."

## 6. Metric / skill score (TYPE H — metric sufficiency)

Sticking point: one full-sample RMSE reported as success.

- **L1:** "Does that single RMSE tell you whether you BEAT the cheap baseline? What
  does it hide about a model that's great in calm years and awful in 2021/2022?"
- **L2:** "Report the metric RELATIVE to the baseline (a skill score), and look at
  per-fold RMSE — one spike fold can dominate the mean."
- **L3:** "`skill = 1 - model_rmse / baseline_rmse` (positive = beats baseline).
  Show per-fold spread, not just the mean. You decide whether the improvement is
  real or noise."

## 7. Uncertainty / coverage (TYPE L)

Sticking point: a point forecast with no interval, or an interval never validated.

- **L1:** "If you say 'I expect X', how often should the truth fall inside your
  stated band? Have you checked whether it actually does?"
- **L2:** "Build the interval from your BACKTEST residual spread, then compare its
  width to reality out of sample — count how many actuals land inside."
- **L3 (calc is type-K; the judgement is the decision):**
  ```python
  sigma = resid_oos.std()
  lower, upper = pred - 1.28*sigma, pred + 1.28*sigma          # ~80%
  coverage = ((y_true >= lower) & (y_true <= upper)).mean()    # want ~0.80
  ```
  "If coverage is 0.55, your intervals are overconfident. You decide what that
  means and whether to widen / use quantiles."

## 8. Feature importance is NOT causation (TYPE G + TYPE J)

Sticking point: memo says a feature "drives" or "causes" price.

- **L1:** "Does a high importance mean the feature CAUSES price, PREDICTS it, or
  just CORRELATES with a real driver the model could also use?"
- **L2:** "Check correlation among your top features and how importance shifts if
  you drop one. Storage and HDD are collinear and seasonal — they trade ranks."
- **L3:** "Phrase every driver as 'predictive of', not 'causes'. State it as a
  falsifiable hypothesis with the confound named. The agent will not bless a causal
  claim without an identification argument — you write the wording."

## 9. What would make this FAIL (TYPE J + standard 6)

Sticking point: card/memo has no explicit failure-mode statement.

- **L1:** "Name one specific market condition NOT in your training range that would
  break this next winter. Would a feature you rely on even be available in time?"
- **L2:** "Re-read your conclusion — replace 'the model predicts' with 'in this
  backtest the model would have'. Think regime shifts (2021/2022), a fundamental
  published too late, a collinear feature flipping sign."
- **L3:** "Write the failure condition as a concrete, checkable statement in the
  model card AND memo (required by the standard). You name it; the agent will not
  sign off on a card that omits it."

## 10. Reproducibility / package structure (TYPE K — answer directly)

Sticking point: re-deriving the panel here, or path/output issues.

- **Direct:** Do NOT rebuild features in module 14 — load module 09's validated
  panel (`09_feature_table_leakage/outputs/model_panel.csv`); that module owns the
  leakage-safe construction. Resolve paths with `data_dir(HERE)` /
  `ensure_output_dir(HERE/'outputs')` from `ng_models.paths`, never relative
  `../data`. Write every artifact under `outputs/` (and `outputs/final_charts/`).
  Verify the prereq path: temporarily rename the panel and confirm the script
  prints "complete module 09 first" and exits 0 instead of crashing.
