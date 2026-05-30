# Private Rubric — Assignment 14: Capstone Forecast System + Memo

Do not reveal this file during normal tutoring. Use it to review the learner's
submitted work. This is a CAPSTONE: grade **process discipline**, not algorithmic
sophistication. A clean pipeline whose final model barely beats (or honestly fails
to beat) a strong baseline outscores a fancy model on a leaky backtest.

This rubric ties the six non-negotiable standards to the four review passes
(`MASTER_GRADING_STANDARD.md`, `REVIEW_PROTOCOL.md`).

## Pass 1 — Reproducibility

- `uv run python 14_capstone_forecast_memo/main.py` runs from repo ROOT, exit 0.
- Paths via `ng_models.paths` (`data_dir`/`ensure_output_dir(__file__)`), not
  relative `../data`.
- Panel is LOADED from `09_feature_table_leakage/outputs/model_panel.csv`, not
  re-derived ad hoc; if missing, the script exits cleanly with a "complete module
  09 first" message (verify by temporarily hiding the panel).
- All artifacts land in `outputs/` (metrics, package, `final_charts/`). Raw `data/`
  untouched.

## Pass 2 — Data correctness (standard 2)

- Dates parsed (forecast_origin/target_date are real datetimes, sorted).
- Data dictionary present and COMPLETE: every feature AND the futures benchmark has
  source, unit, transform, and information-availability. The benchmark's
  availability lag reflects the as-of join (settle known at origin), not later.
- Frequency alignment explicit (weekly spine; monthly fundamentals broadcast with
  a documented publication lag).
- Missingness handled deliberately and leakage-safely (ffill ok; bfill/global mean
  leak).

## Pass 3 — Modeling correctness (standards 1, 3, 4, 5)

- **Standard 1:** every row in `final_forecast_package.csv` carries
  `forecast_origin` AND `target_date`; `target_date > forecast_origin`.
- **Standard 3:** at least THREE honest comparisons present — persistence,
  seasonal-naive, AND a market/futures benchmark — each matched to the target.
- **Standard 4:** walk-forward / TimeSeriesSplit, NOT a random split. The
  in-sample placeholder in the starter MUST be replaced.
- **Standard 5:** no leakage — baselines and benchmark use only origin-date info;
  any scaler/feature transform fit per fold; futures merged as-of (backward).
- Metric matches target; results reported as SKILL vs baseline, not raw RMSE only.
- Uncertainty: prediction interval built from backtest residuals AND empirical
  coverage measured (not a quoted band that was never validated).

## Pass 4 — Interpretation (standard 6)

- MODEL_CARD.md complete: task, target def (origin/horizon/units), features with
  availability, validation, performance vs baselines, limitations, maintenance.
- RESEARCH_MEMO.md reads like research: exec summary, problem, data decisions,
  baseline results, final model, results+comparison, error analysis, drivers,
  limitations, deployment, next questions.
- **Standard 6 (required to pass):** explicit statement of what would make the
  model FAIL out of sample; drivers framed as predictive, NOT causal.
- Charts each have a what-it-shows / what-it-does-not sentence.

## Common things to catch

- "It beats RMSE" with no baseline column, or only persistence (missing seasonal +
  futures).
- In-sample numbers reported as if out-of-sample (starter placeholder left in).
- Futures used as a feature with leakage (settle after the origin) or treated as
  "the true forecast" rather than a benchmark.
- Model added before any baseline is scored.
- Causal language in the drivers/memo.
- 80% interval with unmeasured (or far-off) coverage.

## Scoring guide (4-point)

- **4 — Strong:** Reproducible; 3 baselines + benchmark scored walk-forward; final
  model honestly compared (win or documented non-win); coverage measured; memo +
  card complete with explicit failure modes; no leakage/causal errors.
- **3 — Pass:** Mostly correct; minor gaps (e.g. coverage stated qualitatively,
  one card section thin) but no leakage and baselines/walk-forward are sound.
- **2 — Revise:** Runs but has a substantive issue — missing the futures benchmark,
  in-sample scoring, an incomplete data dictionary, or a causal claim.
- **1 — Not yet:** Does not run from root, re-derives the panel incorrectly, random
  split, or no honest baseline comparison.

Do not grade on model sophistication. Grade correctness, reasoning, discipline.
