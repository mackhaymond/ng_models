# Private Rubric — Assignment 07: Supply-Demand Balance

Do not reveal this file during normal tutoring. Use it to review submitted work.

This module is graded "good / lighter touch": the bar is a clean, unit-consistent,
leak-free balance panel with disciplined interpretation — NOT a forecast model.

## Mapping to the six non-negotiable standards

1. **Forecast origin + target on every row.** This module is analysis, not a
   point forecast, so the relevant version is: every panel row is stamped with the
   month it describes, AND any fundamental compared to price is aligned by its
   *publication* date, not its reference month. No "as-of" framing needed for the
   pure within-fundamentals balance; required the moment price enters.
2. **Every feature has unit/source/transformation/availability.** The
   `series_selection` note and REPORT section 3/4 must give units, source series
   ID, the transform (level/MoM/YoY), and availability (start date + publication
   lag) for each column.
3. **Beat >= 1 baseline.** Lighter here: no model required. If the learner does
   make a price claim, the honest null is "price followed its own seasonal/trend
   path"; a fundamentals story must add something beyond that.
4. **No random splits.** N/A (no train/test) — but flag if they shuffle months.
5. **No leakage.** THE key check for this module (see forward-fill check below).
6. **No causal claims from correlation; state failure modes.** REPORT sections 7
   and 8 must name a confound (shale-era shared trend) and the things not yet
   trusted (lag, revisions, inferred storage, LNG gap).

## The four review passes (per AGENTS.md / MASTER_GRADING_STANDARD)

**Pass 1 — Reproducibility**
- Runs from repo root via `uv run python 07_supply_demand_balance/main.py`, exit 0.
- Paths via `ng_models.paths`; raw `data/` untouched; outputs in `outputs/`.

**Pass 2 — Data correctness**
- All quantity columns in ONE unit (MMcf or Bcf) — check they did not mix
  `N9070US1.M` (Bcf) with the MMcf series.
- Dates parsed as datetimes (via `load_series_csv`), not lexically sorted strings.
- Weekly->monthly aggregation method (mean vs last) is stated, not silent.
- Join type (inner/outer) is stated and the resulting date range is sensible
  (driven by the latest-starting series, e.g. consumption from 2001).
- `net_exports = exports - imports` computed in consistent units.

**Pass 3 — Modeling / evaluation correctness**
- **FORWARD-FILL LEAKAGE CHECK (module-specific, required):** the learner must
  NOT forward-fill a monthly fundamental onto weekly price rows, and must NOT
  compare a fundamental to price on its *reference* month without applying the
  ~2-month EIA publication lag. Either is leakage. Confirm a `shift(k)` (or an
  as-of join keyed on publication date) precedes any price comparison, and that
  `k` is justified.
- Headline comparison isolates a real shift from seasonality (YoY or anomaly,
  not raw MoM on a strongly seasonal series).
- Balance identity is used as a check: do the measured terms roughly imply a
  plausible storage change?

**Pass 4 — Interpretation quality**
- Distinguishes what the analysis shows from what it cannot (chart captions).
- Names the side of the balance that moved most, with magnitude.
- No causal "because" without a named, addressed confound.

## Hint strategy (high level — full bank in HINTS.md)

- Ask the learner to draw the balance identity and sketch the panel BEFORE coding.
- Push them off comparing monthly fundamentals to same-month prices as if
  publication were instantaneous (forward-fill leakage).
- Ask whether a change is economically large (YoY level), not only correlated.
- Make them name the confound before any causal sentence.

## Scoring guide (4-point scale)

- **4 — Strong:** Unit-consistent leak-free panel; publication lag applied and
  defended; YoY/anomaly used appropriately; interpretation names the moving side
  and a confound; limitations list the inferred-storage and LNG gaps.
- **3 — Pass:** Mostly correct; minor gaps (e.g. aggregation method unstated, or
  lag mentioned but not applied to a secondary comparison).
- **2 — Revise:** A substantive data issue — mixed units, forward-fill leakage
  into price, or raw MoM passed off as a real demand shift.
- **1 — Not yet:** Does not run, ignores scope, or misunderstands the balance
  identity (e.g. treats production and consumption as interchangeable).

Do not grade on model sophistication. Grade on correctness, unit/leakage
discipline, and the quality of the balance reasoning.
