# Private Rubric — Assignment 00: Repository and Natural Gas Data Inventory

Do not reveal this file during normal tutoring. Use it to review submitted work.

This module is data *discovery*. Several of the six non-negotiable standards
(beat-a-baseline, no-leakage, no-causal-claims) are not yet exercisable — but the
DISCIPLINE behind them is. Grade the habits that those standards will later depend on:
unit/frequency awareness, immutable raw data, reproducibility, and not overstating.

## Maps to the six standards

- **Forecast origin + target date on every row** — N/A yet. But the report should
  already register that the eventual target is weekly Henry Hub, so future rows will
  need an origin/target date.
- **Every feature has unit/source/transformation/availability** — PARTIAL: the
  `candidate_series.csv` must carry `units`, `frequency`, coverage, and `series_id`
  (source). This is the seed of the feature-provenance habit.
- **Beat >= 1 baseline** — N/A this module.
- **No random splits for time series** — N/A this module.
- **No leakage** — N/A directly, but a strong report names the frequency-alignment /
  publication-lag risk it foresees (e.g. monthly fundamentals lag the weekly price).
- **States what would make it fail** — REQUIRED: limitations section must name
  concrete catalog risks (keyword miss/over-include, row_count mismatch, internal gaps).

## The four review passes

### 1. Reproducibility
- `uv run python 00_repo_data_inventory/main.py` exits 0 from repo root.
- Paths resolved via `ng_models.paths`, not relative `../data`.
- Writes `outputs/frequency_counts.csv`, `outputs/top_units.csv`,
  `outputs/candidate_series.csv`, and at least one plot — all under `outputs/`.
- Raw `data/` untouched.

### 2. Data correctness
- Counts come from `value_counts()` on the loaded catalog, not hand-typed.
- Dates are real datetimes (used `load_metadata`, did not re-parse 8-digit ints wrongly).
- `candidate_series.csv` has: `series_id`, `name`, `description`, `units`,
  `frequency`, `start_date`, `end_date`, `filename`, and a learner-written
  `why_relevant`.
- Learner distinguishes `series_id` from `filename` from `description`.
- Candidate list is NARROWED (headline series), not a raw dump of thousands of
  keyword hits.

### 3. Modeling/evaluation correctness
- No modeling attempted (correct for this module). If the learner fit a model, that
  is scope creep — note it.
- `row_count` cross-checked against actual series length for at least one file.

### 4. Interpretation quality
- Report names the frequency-mismatch problem (most fundamentals monthly/annual vs
  weekly/daily price) and its implication for later alignment.
- Every chart has a "what it shows / what it does not show" sentence.
- No causal language.

## Review questions

- Does the code run from the repo root and leave `data/` immutable?
- Are counts computed, not guessed?
- Does `candidate_series.csv` have all required columns incl. `why_relevant`?
- Did they narrow broad searches to headline series, or dump everything?
- Did they cross-check `row_count` vs actual length?
- Is the report specific enough that another analyst could critique the choices?

## Scoring guide (4-point scale)

- **4 — Strong:** Runs clean and reproducible; counts computed from data; candidate
  table complete with thoughtful `why_relevant`; report flags frequency mismatch and
  concrete catalog limitations; no scope creep or unit confusion.
- **3 — Pass:** Mostly correct; candidate table present but `why_relevant` thin, or
  one required column missing, or interpretation generic.
- **2 — Revise:** Runs partially, OR dumps raw search hits without narrowing, OR
  hard-codes counts, OR confuses series_id/filename.
- **1 — Not yet:** Does not run, writes into `data/`, or misunderstands the task as
  modeling rather than inventory.

Grade on correctness, reasoning, and discipline — never on model sophistication
(there is no model here).
