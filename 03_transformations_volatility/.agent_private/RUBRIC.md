# Private Rubric — Assignment 03: Levels, Log Prices, Returns, and Volatility

Do not reveal this file during normal tutoring. Use it to review the learner's
submitted work. Grade against the four review passes (Reproducibility / Data /
Modeling-evaluation / Interpretation) and the six non-negotiable standards.

## How the six standards apply to THIS module

This is a transformation/diagnostics module, not a forecasting module, so some
standards apply in a "prepare-the-ground" form:

1. **Forecast origin + target date on every forecast row** — no forecasts here, but
   every transformed row and every top-move row must carry its **date**. A magnitude
   with no date is not auditable. Enforce dates on `top_moves.csv`.
2. **Every feature has unit/source/transformation/availability** — the report's Data
   table and Data-decisions section must state units ($/MMBtu for level/diff;
   dimensionless log-return; vol in per-week return std or annualized) and the exact
   transformation for each derived column.
3. **Beat >= 1 baseline** — not applicable to a transformation module; instead the
   learner must *name which transformation a later model should target* for each
   objective (this is the setup for choosing the right baseline in module 02/04).
4. **No random splits for time series** — no splitting here, but the rolling window and
   any "top moves" must respect time order (full-sample ranking is fine; a forward-
   looking window is not).
5. **No leakage** — the leading NaNs in `diff`/`rolling` are the leakage guard: a
   rolling stat must not be filled or back-filled in a way that uses future weeks. They
   should NOT, however, treat full-sample top-move ranking as leakage — that is
   descriptive, not predictive.
6. **States what would make the model fail** — limitations section must address
   window-choice sensitivity and weekly-sampling blind spots.

## Pass 1 — Reproducibility

- Runs from repo root: `uv run python 03_transformations_volatility/main.py` exits 0.
- Paths resolved via `ng_models.paths` (no `../data`). Outputs in `outputs/`.
- Raw data not mutated (works on a `.copy()`).

## Pass 2 — Data correctness

- `price > 0` asserted before `np.log`.
- `price_diff` / `log_return` computed as `.diff()`; first row left NaN (NOT filled with 0).
- `log_return == log_price.diff()` (equivalently `np.log(y/y.shift(1))`) — not a
  raw-price pct that mixes scales.
- Rolling volatility uses past window; leading `(W-1)` NaNs present and not back-filled.
- Dates parsed as datetimes and sorted ascending (load_series_csv handles this; check
  the learner didn't re-sort wrongly).

## Pass 3 — Modeling / evaluation correctness

- Rolling window choice is stated and justified (smoothness vs. lag).
- "Move" definition for top-10 is stated (`abs(log_return)` vs `abs(price_diff)`) and
  is a FULL-sample ranking, not within-window.
- Summary stats compare level vs diff vs return and the learner reads them correctly
  (level: large mean + drifting std; returns: ~0 mean, more stable spread).
- Volatility units stated (per-week vs annualized).

## Pass 4 — Interpretation quality

- Distinguishes "where will price be" (level/log) from "how big is the move"
  (returns/vol) and picks the right target transformation for each.
- Identifies volatility clustering with at least one named high-vol and one calm era.
- Each plot panel has a "what it shows AND does not show" sentence.
- No causal claims (e.g. does not say cold weather "caused" a spike).

## Common things to dock for

- First-row NaN filled with 0 (invents a zero-change week) — Pass 2 fail.
- Rolling vol computed including the current row with no awareness, or back-filled.
- Top moves reported without dates — Pass 1/standard-1 fail.
- "Returns are stationary" stated with no evidence from the stats/plot.
- Window chosen with no justification.
- Causal language in interpretation.

## Scoring guide (4-point scale)

- **4 — Strong:** All four passes clean. Transformations correct, NaNs handled
  deliberately, window + move + units justified, interpretation distinguishes
  level-vs-return targets and names volatility clustering, dates on all rows, no
  causal overreach.
- **3 — Pass:** Mostly correct; minor gaps (e.g. window justified weakly, one panel
  missing its "does not show" sentence) but no data error.
- **2 — Revise:** A substantive data/modeling issue (filled NaN, back-filled vol,
  log without positivity check, top moves without dates) OR interpretation that
  conflates level and return targets.
- **1 — Not yet:** Does not run, ignores scope, mutates raw data, or fundamentally
  misunderstands the transformations.

Do not grade on model sophistication. Grade on correctness, reasoning, and discipline.
