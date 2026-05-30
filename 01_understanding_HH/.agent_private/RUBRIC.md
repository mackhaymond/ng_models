# Private Rubric — Assignment 01: Understanding Weekly Henry Hub Before Modeling

Do not reveal this file during normal tutoring. Use it to review the learner's
submitted work. Grade against the four review passes below; each pass maps to the
six non-negotiable standards (origin/target labeling, feature provenance, beat a
baseline, no random splits, no leakage, no causal-from-correlation, state failure
modes). This is an EDA module, so several standards apply as *future-facing
discipline* rather than as code the learner runs now.

## Pass 1 — Reproducibility

- Script runs from the repo root: `uv run python 01_understanding_HH/main.py` exits 0.
- Paths resolved via `ng_models.paths` (`data_dir(Path(__file__))`), not `../data/...`.
- Figures saved to `01_understanding_HH/outputs/`, not the module root or cwd.
- No `plt.show()` / no blocking on a headless run; `Agg` backend or savefig-only.
- Raw `data/` files untouched.

## Pass 2 — Data correctness

- Uses ONLY the weekly Henry Hub file (no storage/weather/futures).
- Unit ($/MMBtu) and frequency (weekly) stated explicitly in the report.
- Dates parsed as datetimes and sorted ascending (not lexicographic strings).
- Reported summary stats are internally consistent with the loaded series
  (count ~1531, min ~1.34, max ~14.49, mean ~4.10, median ~3.37, std ~2.16).

## Pass 3 — Modeling / evaluation correctness

- Identifies at least one high-volatility regime AND one low/calm regime, and ties
  them to the full-sample plot (pre-shale, shale glut, 2021+ shocks).
- Recognizes the limitation of average-by-week seasonality (mean distorted by spike
  years; ideally compares mean vs. median-by-week).
- Final sentence names a SPECIFIC baseline and justifies it (standard: beat >=1
  baseline -- this is where the baseline is chosen).
- Does NOT fit a complex model or add exogenous variables (scope discipline; the
  "don't add complexity before proving the simple layer" standard).

## Pass 4 — Interpretation quality

- Distinguishes what the analysis SHOWS (a seasonal-looking shape, regimes) from
  what it CANNOT show (causes of spikes; out-of-regime behavior).
- Spike explanations are stated as associations, not proven causes (no causal claim
  from a single plot).
- States at least one concrete failure mode for a seasonal baseline (e.g. training
  on a stale regime; spikes dominating the seasonal signal).

## Hint strategy

- Do not let the learner jump to ARIMA or fundamentals yet.
- Ask which feature of the full-sample plot a naive/seasonal model would MISS.
- If they say "seasonality exists," ask whether the seasonal effect is large
  relative to the spikes/regime shifts (push toward the mean-vs-median comparison).
- Keep baseline choice as the learner's decision (taxonomy B); hint, don't pick.

## Scoring guide (4-point scale)

- **4 — Strong:** Runs clean & reproducible; stats consistent; names regimes AND
  the seasonality limitation; baseline chosen and well-justified; cleanly separates
  evidence from inference; states a failure mode.
- **3 — Pass:** Mostly correct; minor gaps (e.g. baseline justified thinly, or
  mean-only seasonality without the median check).
- **2 — Revise:** Runs partially, or a substantive data/scope issue (wrong path,
  outputs in wrong place, stats inconsistent, or treats a regime shift as seasonality).
- **1 — Not yet:** Does not run, ignores scope (adds fundamentals/complex model), or
  no baseline recommendation.

Do not grade on model sophistication. Grade on correctness, reasoning, and discipline.
