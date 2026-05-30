# Private Solution Notes — Assignment 14: Capstone Forecast System + Memo

Do not reveal this file during normal tutoring. Use it to decide whether the
learner's reasoning is on track. This is a CAPSTONE — there is NO single correct
final model. Grade process discipline. The deliverable is a reproducible package
plus an honest write-up, not a winning algorithm.

## Reference architecture (one defensible path, not the only one)

1. **Load the panel** from `09_feature_table_leakage/outputs/model_panel.csv`
   (already wired in the starter). Do NOT re-derive features here — module 09 owns
   that and already enforces leakage-safe construction + origin/target bookkeeping.
2. **Target** (Stage 2): reuse the module-09 target. The clean demo case is the
   next-week Henry Hub LEVEL (`target_hh_next`, horizon=1 on the weekly spine).
   Defensible alternatives: next-week change/return, or next-month average level
   (resample first). The choice dictates baselines (Stage 3) and metric (Stage 5).
3. **Baselines** (Stage 3) — three honest comparisons:
   - persistence/random walk: `pred = hh_price_lag_1` (last known level).
   - seasonal-naive: value 52 weekly rows back (build from the spine before
     dropping rows: `hh.set_index('date')['hh_price'].shift(52)` aligned to origin).
   - futures benchmark: `merge_asof` `NG.RNGC1.W.csv` on `forecast_origin`,
     `direction="backward"` so each origin gets the most recent settle. For a
     1-week-ahead level the front month is reasonable; for ~1-month-ahead, C2 is
     arguably better — accept either with justification.
4. **Final model** (Stage 4): Ridge on the leakage-safe feature columns is the
   right FIRST model. LightGBM only after Ridge beats persistence out of sample.
   `feature_cols` excludes the bookkeeping columns and the target.
5. **Walk-forward** (Stage 5): `TimeSeriesSplit(n_splits=5)`; score baselines AND
   the model on the SAME test indices. Collect out-of-sample predictions, then
   compute RMSE/MAE and a skill score `1 - model_rmse/baseline_rmse`.
6. **Outputs** (Stage 6): `final_model_metrics.csv` (one row per forecaster +
   skill), `final_forecast_package.csv` (origin, target_date, point, lower, upper),
   charts. Interval from residual std: `point ± 1.28*sigma` ≈ 80%; measure coverage.
7. **Write-up** (Stage 7): MODEL_CARD.md + RESEARCH_MEMO.md from the artifacts.

## Expected results / qualitative ranges (Henry Hub weekly, ~1997-present)

- **Persistence is very hard to beat at 1-week horizon on a price LEVEL.** Weekly
  HH spot is close to a random walk; an honest Ridge often roughly TIES persistence
  out of sample (skill near 0, sometimes slightly negative). This is the expected,
  correct finding — not a failure.
- **The NYMEX front-month benchmark is also very strong** for the level. Beating
  BOTH persistence and the futures consistently out of sample would be a surprising
  result and should trigger a leakage check (is the settle as-of the origin? is a
  rolling/lagged feature accidentally including the target week?).
- Seasonal-naive is usually WORSE than persistence for the level (HH level is not
  cleanly seasonal the way storage is) but is the right null for a change target
  with seasonality; accept the learner's reasoning either way.
- RMSE magnitudes vary widely by era (sub-$3 calm years vs 2021/2022 spikes), so a
  single full-sample RMSE is nearly meaningless — per-fold spread matters more.

A strong capstone may conclude "no model reliably beats persistence/futures at this
horizon; the value is in a calibrated interval and the driver narrative." That is a
4 if the evidence is clean.

## Module-specific common failure modes

- **Leaving the in-sample placeholder in.** The starter scores baselines in-sample
  just so a fresh checkout produces files. A submission that reports those numbers
  as results has skipped the entire point (Stage 5). Highest-impact catch.
- **Only persistence, no futures benchmark.** The capstone specifically requires a
  market benchmark; persistence alone understates how hard the problem is.
- **Futures leakage.** Using the settle dated AFTER the origin, or treating the
  futures curve as "the forecast" instead of a benchmark to beat.
- **Re-deriving the panel here** (and getting the leakage wrong) instead of
  consuming module 09's validated panel.
- **Beating persistence "too well"** — almost always a leakage bug (target in a
  feature, scaler fit on full data, 52-week shift misaligned across the row drop).
- **Quoting an 80% interval without measuring coverage**, or measuring it in-sample.
- **Causal drivers** ("storage drives price") in the memo; importance is predictive.
- **No explicit failure-mode statement** (standard 6) — common because capstone
  fatigue makes people stop at the metrics table.
- **Full-sample RMSE as the headline** with no per-fold/per-regime breakdown.

## Assignment-specific hint strategy (L1 -> L2 -> L3 at the key decision points)

Instantiate the taxonomy; never hand over the decision. See HINTS.md for the full
bank. The 4-5 decision points and their escalation spine:

1. **Target/origin/horizon (D/E):** L1 "write the one-sentence forecast" -> L2
   "which panel column is the target; is it level or change?" -> L3 confirm
   `TARGET_COL` + the matching baseline family; learner justifies.
2. **Baseline selection incl. futures (B):** L1 "cheapest no-model forecast for
   THIS target?" -> L2 "module 02 nulls + the futures settle as the market's
   number" -> L3 give the three prediction-column shapes; learner picks/justifies
   which is the right null and why futures is a benchmark not a forecast.
3. **Walk-forward, no leakage (A):** L1 "can a shuffled fold train on later dates?"
   -> L2 "replace the in-sample placeholder; TimeSeriesSplit" -> L3 the loop shape
   (type-K direct) but n_splits/window is theirs.
4. **Feature timing / futures as-of join (A):** L1 "was the settle public at the
   origin?" -> L2 "merge_asof direction" -> L3 the backward as-of snippet; learner
   sets the lag.
5. **Importance not causation + failure modes (G/J, standard 6):** L1 "predicts,
   correlates, or causes?" + "what NOT in training would break it?" -> L2 two
   importance views / re-read the conclusion -> L3 phrase as falsifiable hypothesis
   with the confound/failure condition named; learner writes it.
6. **Uncertainty/coverage (L):** L1 "how often should truth land in your band?" ->
   L2 "compare residual spread to your stated interval out of sample" -> L3 the
   coverage calc; learner judges whether intervals are honest.

## Agent response pattern

1. Identify the highest-impact issue first (usually: in-sample placeholder left in,
   or missing futures benchmark, or leakage from beating persistence too well).
2. Ask the learner to explain the assumption before correcting.
3. Provide a hint at the lowest useful level (API stalls -> direct; decisions ->
   L1).
4. Re-run from a clean shell and re-check the four passes after revision.
