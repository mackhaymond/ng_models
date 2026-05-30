# Private Solution Notes — Assignment 12: Uncertainty, Price Spikes, and Risk Metrics

Do not reveal this file during normal tutoring. Use it to decide whether the
learner's reasoning is on track and to gauge expected results.

## Worked reference approach

Input: `09_feature_table_leakage/outputs/model_panel.csv`, weekly (W-FRI),
target `target_hh_next` (next-week HH level, $/MMBtu), origin price `hh_price`,
plus leakage-safe lag/rolling/calendar features. Drop NaN-target rows; sort by
`forecast_origin`; time-ordered 70/30 split (provided in starter).

**Part A — naive residual interval (baseline).**
- Point forecast = last value (random walk): `point = hh_price` at the origin. For
  a 1-week level target this is the correct null.
- Training residuals `resid = y_train - point_train`; for an 80% band take
  `np.quantile(resid, [0.10, 0.90])`; add those offsets to `point_test`.
- Score `coverage_and_width(y_test, lo, hi)`.

**Part B — fitted quantile interval (the thing that must beat A).**
- Features X: a leakage-safe subset of the panel — e.g. `hh_price` (origin price),
  one or two lags, a rolling mean, `month`. Explicitly exclude `target_date`,
  `forecast_origin`, and the target.
- `GradientBoostingRegressor(loss="quantile", alpha=0.10)` and another at
  `alpha=0.90`, fit on `(X_train, y_train)`, predict `q_lo`, `q_hi` on `X_test`.
- Score coverage/width AND `pinball_loss(y_test, q_lo, 0.10)`,
  `pinball_loss(y_test, q_hi, 0.90)`.
- Expected: a state-dependent band that, at comparable coverage, is somewhat
  NARROWER than the flat naive band in calm stretches and wider near volatile
  ones. On a short, quiet HH window the gain can be marginal — an honest "barely
  beat / tied" is acceptable and often correct.

**Part C — spike events (leakage-safe).**
- Threshold = `np.quantile(y_train, 0.90)` (train-only) OR an operational level
  (e.g. $5/MMBtu) if the desk has one. Apply the SAME number to label both sets.
- Predict spikes from `q_hi >= threshold` (reuse Part B) as the simple route, or a
  classifier on leakage-safe features. Score with `classification_counts`.

## Expected metric ranges (HH weekly, leakage-safe, single holdout)

These are sanity bands, not targets. Wide ranges because the test window matters.

- Naive 80% interval coverage: roughly **0.72-0.88** (near 0.80 if residuals are
  stable across the split; lower if the test window is more volatile than train).
- Fitted 80% coverage: similar; aim for coverage held while **avg_width drops**
  vs naive. If width drops but coverage falls to ~0.60, it OVER-narrowed — not a
  win.
- Pinball loss: small positive numbers (order ~0.02-0.10 in $/MMBtu for HH);
  compare relatively (fitted vs naive), not the absolute value.
- Spike base rate in test: by construction near the train P90 tail, often
  **0.05-0.15** — and sometimes the test window has ZERO spikes, which makes
  recall undefined. That is a finding to discuss, not a bug.
- A genuinely-tradable spike detector is NOT expected; modest precision/recall is
  normal and the point is the FP/FN reasoning.

## Module-specific common failure modes

1. **Threshold leakage (the headline error).** Computing `np.quantile(y, 0.90)`
   on the FULL panel, then splitting. The test labels now know the future
   distribution. Tell: same threshold quoted but derived after concatenation, or
   threshold equals the full-sample P90 not the train P90.
2. **Full-sample residual quantiles.** Same disease in Part A — taking the
   residual quantiles over train+test. The naive band then looks better calibrated
   than it earned.
3. **Coverage without width (or vice versa).** Reporting "my interval covers 96%!"
   from a band so wide it is useless, or reporting a tiny width that covers 50%.
   The two must be read together.
4. **MAE/RMSE used to score quantiles.** A P90 forecast scored with MAE rewards
   the median, not the 90th percentile — must use pinball.
5. **Accuracy for spikes.** With a ~10% base rate, "never predict spike" scores
   ~90% accuracy. Must use precision/recall.
6. **Random split / shuffled CV.** Destroys the time order; any random_state in a
   train_test_split is a red flag here.
7. **Cosmetic uncertainty.** Shading the chart with `fill_between` but never
   computing empirical coverage. The plot is not the evaluation.
8. **Cranking the band until coverage hits 0.80.** Widening to pass the check is
   not calibration; the residual quantiles already define the honest width.

## Assignment-specific hint strategy (L1 -> L2 -> L3)

Five key DECISION points (all withheld; escalate one level at a time). Full
prompts live in HINTS.md.

1. **Spike-threshold leakage (type A/E).** L1: "When you computed the threshold,
   which rows fed the quantile?" L2: point at the line, ask train vs full sample.
   L3: `np.quantile(y_train, q)` then apply to both — they pick q and defend it.
2. **Spike-threshold definition (type E/H).** Statistical quantile vs operational
   $/MMBtu. Never pick for them; make them tie it to who consumes the warning.
3. **Coverage reading / calibration (type L).** Is 80% really ~80%? L3 gives the
   coverage formula; the learner decides whether it is honest and what to change
   (NOT just widen).
4. **Fitted vs naive comparison (type B/F).** Did GBR earn its complexity? Force a
   coverage-held, width-or-pinball comparison; an honest "tied" is fine.
5. **FP vs FN tradeoff (type L/H).** Is a missed spike or a false alarm worse for
   a gas desk? Make them state the asymmetry and reflect it in the threshold.

Package-API stalls (sklearn quantile fit, np.quantile, fill_between) are type K —
answer directly with code.

## Agent response pattern

1. Identify the highest-impact issue first (almost always threshold leakage).
2. Ask the learner to explain their assumption before correcting.
3. Provide a hint at the lowest useful level.
4. Re-run / re-check coverage and width after revision.
