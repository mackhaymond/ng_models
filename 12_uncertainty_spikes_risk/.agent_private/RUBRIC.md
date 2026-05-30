# Private Rubric — Assignment 12: Uncertainty, Price Spikes, and Risk Metrics

Do not reveal this file during normal tutoring. Use it to review submitted work
against the four review passes (reproducibility / data / modeling / interpretation)
and the six non-negotiable standards.

## The six standards, instantiated for this module

1. **Origin + target date on every forecast row.** `interval_forecasts.csv` must
   carry `forecast_origin` AND `target_date` on every row (not just an index).
2. **Every feature has unit/source/transformation/availability.** Any feature fed
   to the quantile model (Part B) must be leakage-safe and documented; the price
   is $/MMBtu. The learner inherits module-09 features — they must still state
   which they used and that each was knowable at the origin.
3. **Beat >= 1 baseline.** The naive residual interval IS the baseline; the fitted
   quantile interval must be compared to it (narrower at comparable coverage, or
   lower pinball — or an honest statement that it did NOT win).
4. **No random splits.** Train/test must be time-ordered (test strictly later).
5. **No leakage.** THE module-defining check: the spike threshold is computed from
   `y_train` ONLY and applied unchanged to label test. Same for the quantile-model
   features. Any full-sample threshold or full-sample residual quantile fails.
6. **No causal claims; states failure modes.** The report must not claim weather
   "causes" spikes from correlation, and must say what would make the intervals
   miscalibrate (regime change, sparse spikes).

## Review pass 1 — Reproducibility

- Runs from repo root: `uv run python 12_uncertainty_spikes_risk/main.py` exits 0.
- With module-09 panel absent, prints the "complete module 09 first" message and
  exits 0 (does not crash).
- Outputs land in `12_uncertainty_spikes_risk/outputs/`, not the repo root.
- Paths resolve via `ng_models.paths`, not relative `../data`.

## Review pass 2 — Data correctness

- Dates parsed (not lexicographic strings); panel sorted by `forecast_origin`.
- Target rows with NaN target are dropped before metrics.
- Units consistent ($/MMBtu); no silent mixing.
- Train/test split is time-ordered and disjoint.

## Review pass 3 — Modeling / evaluation correctness

- Coverage computed as `mean((lo <= y) & (y <= hi))` on the TEST set only.
- Coverage AND width reported together (width alone or coverage alone is a fail —
  a 100%-coverage band that is enormous is not a win).
- Pinball loss used to score quantiles (not MAE/RMSE on the quantile).
- Spike threshold demonstrably train-only; same number applied to both sets.
- Spike scored with precision/recall, not accuracy (accuracy is misleading for a
  ~10% base-rate event — a "never spike" predictor scores ~90% accuracy).

## Review pass 4 — Interpretation quality

- States whether the interval is calibrated, with the actual coverage number.
- Compares fitted vs naive honestly.
- Names the FP-vs-FN tradeoff for a gas desk and ties the threshold choice to it.
- Acknowledges rare-event difficulty: sparse spikes make recall noisy; one
  holdout may not be representative.
- Uncertainty is QUANTIFIED (coverage/width/pinball), not just cosmetic shading.

## Hint strategy (see HINTS.md for L1->L2->L3)

- Lead with the leakage check on the spike threshold — it is the highest-impact
  module-specific error.
- Help implement metrics directly (type K); make the learner interpret the
  coverage/width and FP/FN tradeoffs (type L).
- Push on threshold: statistical quantile vs operational level — their call.

## Scoring guide (4-point scale)

- **4 — Strong:** Time-ordered split; threshold provably train-only; coverage AND
  width reported and discussed; fitted-vs-naive comparison honest; FP/FN tradeoff
  named and tied to the threshold; failure modes stated. No leakage.
- **3 — Pass:** Mostly correct; e.g. intervals evaluated out of sample and
  threshold train-only, but the fitted-vs-naive comparison or calibration reading
  is thin.
- **2 — Revise:** A substantive issue — threshold or residual quantiles computed
  on the full sample, coverage without width, or accuracy used for spikes.
- **1 — Not yet:** Does not run, uses a random split, or treats the interval as
  chart shading with no coverage number.

Do not grade on model sophistication. Grade on leakage discipline, honest
evaluation, and calibrated interpretation.
