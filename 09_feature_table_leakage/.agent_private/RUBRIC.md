# Private Rubric — Assignment 09: Feature Engineering and the Model-Ready Panel

Do not reveal this file during normal tutoring. Use it to review submitted work.

This module's whole point is a LEAKAGE-FREE model-ready panel with auditable
feature timing. A simple correct panel beats a rich leaky one — every time.

## Mapping to the 6 non-negotiable standards

1. **Origin + target date on every row** — `model_panel.csv` has
   `forecast_origin`, `target_date`, `target`, and `target_date > origin` for
   every trained row. This is the standard that makes the whole module audit-able.
2. **Every feature documented (unit/source/transform/availability)** —
   `data_dictionary.csv` has one row per feature with all six fields; the
   `availability_lag` reflects real publication timing, not the period covered.
3. **Beat >= 1 baseline** — one honest baseline is scored on the panel (random
   walk for a level, zero-change for a change target, seasonal-naive for seasonal
   level). No ML required or wanted here; module 10 must beat this number.
4. **No random splits** — N/A to building the panel, but the panel must be
   time-ordered and leave time-series CV possible (no shuffling, sorted by date).
5. **No leakage** — every fundamental is as-of joined with a release lag; rolling
   features shift before windowing; imputation is past-only (`ffill`, never
   `bfill`/global mean); monthly→weekly broadcast respects publication date.
6. **No causal claims; states failure modes** — REPORT uses "associated with",
   names where leakage could still hide, and flags which release lags are guesses.

## The 4 review passes

**Pass 1 — Reproducibility**
- Runs from repo root: `uv run python 09_feature_table_leakage/main.py`, exit 0.
- If 06/07/08 outputs are absent, it prints the "complete module 0X first"
  message and exits 0 (does not crash).
- Paths via `ng_models.paths`; outputs land in `09_.../outputs/`; `data/` untouched.

**Pass 2 — Data correctness**
- Units stated per series; monthly balance correctly broadcast to weekly.
- Dates parsed as datetime (no lexical sorting); spine is time-sorted.
- Missingness report present; leading-NaN rows dropped, not filled.

**Pass 3 — Modeling/evaluation correctness**
- Target defined in one precise sentence and matches `horizon`.
- Release lag assigned and justified per fundamental; as-of join is `backward`.
- Baseline matches the target; metrics reported relative to it.

**Pass 4 — Interpretation quality**
- REPORT distinguishes what the panel enables from what it proves.
- Limitations name concrete leakage risks and lag assumptions.

## Hint strategy (see HINTS.md for leveled bank)

- Every time the learner adds a feature, ask for unit, timestamp, and publication
  timing before anything else.
- Debugging joins / merge_asof syntax = direct help (type K).
- Choosing the lag, the release lag, drop-vs-ffill, target, baseline = learner-led
  (types A/B/D/E/H), L1→L2→L3.

## Scoring guide (4-point)

- **4 — Strong:** Runs clean; origin+target on every row; data dictionary complete
  with real availability lags; as-of joins leakage-free; baseline matched and
  reported; limitations name where leakage could hide.
- **3 — Pass:** Mostly correct; minor gaps (one feature under-documented, a lag
  weakly justified) but no leakage and a valid baseline.
- **2 — Revise:** A substantive issue — a fundamental joined on its period date
  (leak), monthly figure broadcast without publication lag, target/horizon
  mismatch, or `bfill`/global-mean imputation.
- **1 — Not yet:** Does not run, modifies raw data, no origin/target columns, or
  no data dictionary.

Do not grade on model sophistication. Grade on correctness, timing discipline,
and the auditability of the panel.
