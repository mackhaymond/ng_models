# Private Rubric — Assignment 06: Storage Fundamentals

Do not reveal this file during normal tutoring. Use it to review the learner's submitted
work against the six non-negotiable standards and the four review passes.

## What this module must demonstrate (mapped to the 6 standards)

1. **Forecast origin + target on every row.** This module is mostly descriptive, but the
   panel must still carry `date` (the origin a value is *known as of*), and any deviation
   used predictively must respect it. (Standard: origin+target.)
2. **Every feature documented (unit/source/transformation/availability).** The report's
   data table names series id, units (Bcf, $/MMBtu), frequency, source file, and the
   transformation (diff, seasonal norm, deviation). Bcf-vs-$/MMBtu called out.
3. **Beat >= 1 baseline.** Not a forecasting module, so the relevant discipline is the
   *seasonal norm itself is the baseline* a future forecast must beat; learner should
   frame the norm as the naive reference, not as a result.
4. **No random splits for time series.** N/A to model fitting here, but the seasonal norm
   must be computed in time order (expanding over prior years), never a full-sample mean.
5. **No leakage.** THE central test of this module: (a) the seasonal norm uses prior years
   only, no centering, no current-year value; (b) the report states the EIA Thursday /
   prior-Friday publication lag and that storage cannot explain an earlier price.
6. **No causal claims from correlation; states failure modes.** The price-vs-deviation
   interpretation is framed as association with named confounds (weather, production), and
   the report lists what would make the analysis fail.

## Four review passes

### Pass 1 — Reproducibility
- Runs from repo root via `uv run python 06_storage_fundamentals/main.py`, exit 0.
- Paths via `ng_models.paths`; outputs land in `06_storage_fundamentals/outputs/`.
- Raw `data/` untouched.

### Pass 2 — Data correctness
- Anchor series correctly identified as `NG.NW2_EPG0_SWO_R48_BCF.W` (Lower 48, Bcf, weekly)
  via metadata search, not hard-coded from memory.
- Join is inner on `date` (or a defended alternative); panel is 2010+, weekly, sorted.
- `.diff()` first-row NaN handled; flow_type sign correct (positive = injection).
- Units stated; Bcf and $/MMBtu never combined arithmetically.

### Pass 3 — Modeling / evaluation correctness
- Seasonal norm is leakage-safe: grouped by week-of-year, prior years only, shifted to
  exclude the current year. Spot-check one cell by hand if unsure.
- Norm window choice (5 vs all prior years) and early-year handling are stated and defended.
- Injection/withdrawal classification passes the seasonality sanity check (injections in
  summer, withdrawals in winter).

### Pass 4 — Interpretation quality
- Deviation explained economically (deficit bullish / surplus bearish) WITHOUT a causal
  claim; confounds named.
- Each plot has a what-it-shows / what-it-does-not-show sentence.
- Limitations section names publication-lag risk, thin early-year norm, incommensurability.

## Hint strategy (use HINTS.md for the leveled bank)

- Push on physical meaning of working gas before any feature talk.
- Push on units: Bcf vs MMcf vs cubic feet; $/MMBtu is a different axis entirely.
- Ask whether a storage value published after the price date is legal as a feature.
- The single highest-leverage check is the leakage-safety of the seasonal norm — if it is
  a full-sample or centered mean, that is the first thing to fix.

## Scoring guide (4-point scale)

- **4 — Strong:** Correct anchor series + units; inner-join panel sound; seasonal norm
  provably leakage-free with a defended window; flows pass the seasonality check;
  interpretation is fundamental and non-causal; publication lag stated. Reproducible.
- **3 — Pass:** Mostly correct with minor gaps (e.g. early-year norm handling unjustified,
  or a thin limitations section) but no leakage and no unit error.
- **2 — Revise:** A substantive issue — full-sample/centered norm (leakage), wrong flow
  sign, Bcf/$ combined, or no publication-lag awareness.
- **1 — Not yet:** Does not run, wrong series, or misunderstands storage/deviation entirely.

Grade on correctness, reasoning, and discipline — not on analysis sophistication.
