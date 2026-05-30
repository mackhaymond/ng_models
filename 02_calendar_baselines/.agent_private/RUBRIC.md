# Private Rubric — Assignment 02: Calendar Structure and Naive Forecast Baselines

Do not reveal this file during normal tutoring. Use it to review the learner's
submitted work.

This module's job is to establish HONEST, leakage-free baselines that all later
models must beat. Grade the discipline (no leakage, fixed test window, defensible
metric choice, baseline must be beaten) far above any specific winning baseline.

## Mapping to the six non-negotiable standards

| Standard | What to check in this submission |
|---|---|
| Forecast origin + target date on every row | `test_forecasts.csv` has `forecast_origin`, `target_date`, `horizon_steps`; they are consistent (target_date = origin + h weeks). |
| Every feature has unit/source/transformation/availability | Report §3-§4 state $/MMBtu, weekly, the file, and that baselines are past-only transforms of price. |
| Beat >= 1 baseline | N/A as a model here, BUT the learner must NAME the baseline future models must beat and justify from metrics, not vibes (task 5). |
| No random splits for time series | Test window is a CONTIGUOUS final block selected by date, never a random sample. |
| No leakage | Every baseline is past-only: expanding (not full-sample) means/medians; seasonal stat uses prior-year same-week only; naive uses shift. |
| Report states what would make the model fail | Report §8 names a failure mode (regime break, unrepresentative window). |

## The four review passes (see MASTER_GRADING_STANDARD.md)

1. **Reproducibility.** Runs from repo root via `uv run python 02_calendar_baselines/main.py`,
   exits 0, writes the three output files plus REPORT.md. Paths via `ng_models.paths`,
   not `../data`. Raw data untouched.
2. **Data correctness.** Dates parsed as datetime (not lexicographic strings);
   weekly frequency understood; NaN warm-up (early expanding rows) and tail (last
   h rows have no actual) handled explicitly, not silently mis-scored.
3. **Modeling/evaluation correctness.** THE crux. No full-sample statistics. The
   seasonal week-of-year stat excludes the current/future same-week observations.
   The naive shift matches the chosen horizon. Test window fixed before metrics
   seen. MAE/RMSE computed via `ng_models.metrics`, on the test window only.
4. **Interpretation quality.** Report distinguishes MAE vs RMSE winners and
   explains disagreement; names the baseline to beat with a metric-based reason;
   notes the MAPE-near-zero caveat; makes no causal claim about price drivers.

## Review questions

- Does the code run from the repo root and exit 0?
- Does it avoid modifying raw data and save outputs in `outputs/`?
- Are date, unit, frequency, and horizon assumptions explicit in the report?
- Is EVERY baseline provably past-only? (Re-derive the worst-case origin by hand.)
- Is the test window contiguous, final, and chosen before metrics?
- Does the learner crown a baseline with a metric-grounded argument?
- Does the report say what would make even the naive baseline fail out of sample?

## Hint strategy (lowest useful level first; see HINTS.md for full L1->L3)

- Full-sample week-of-year/historical mean used for the test forecast → type (A)
  leakage: ask what would have been known at the forecast origin (L1).
- No fixed test window or a random sample → type (B)/standard "no random split":
  ask why the test block must be the most recent contiguous weeks.
- Reports only one metric, or MAPE as primary → type (H): ask what a good value of
  that metric does NOT tell them, and what MAPE does near $2.
- Allow direct help with plotting/CSV-writing/pandas API (type K). Withhold the
  decision on which baseline to crown and which horizon to use until they compare.

## Scoring guide (4-point scale)

- **4 — Strong:** Correct, reproducible, no leakage, fixed test window, MAE+RMSE
  reported with the MAPE caveat, a metric-grounded crowned baseline, and a stated
  failure mode.
- **3 — Pass:** Mostly correct; minor gaps (e.g. crowned baseline reasoning thin,
  or MAPE caveat missing) but no leakage and the test window is sound.
- **2 — Revise:** A substantive issue — a full-sample/leaky baseline, a random or
  non-contiguous test split, or metrics computed over the wrong rows.
- **1 — Not yet:** Does not run, ignores scope, or misunderstands baselines vs a
  real model (e.g. jumps to a complex model with no honest baseline).

Grade on correctness, reasoning, and discipline — never on model sophistication.
