# Private Rubric — Assignment 11: Futures Curve and Market-Implied Expectations

Do not reveal this file during normal tutoring. Use it to review submitted work.

This module's grade hangs on three things specific to futures: (1) correct
contract/curve mechanics, (2) the timing/leakage discipline of the spot-vs-futures
comparison, and (3) refusing to treat futures as a forecast. Map every check to
the 6 non-negotiable standards and the 4 review passes.

## The 6 standards, instantiated for this module

1. **Forecast origin + target date on every forecast row.** The
   `futures_vs_spot_benchmark.csv` MUST carry `forecast_origin` and `target_date`
   columns. A file with only one date column = automatic Revise on the predictive
   framing.
2. **Every feature/series has unit/source/transformation/availability.** All five
   series are $/MMBtu daily; the report states this and the C1..C4 = prompt..4th
   contract meaning and that prices are *settlements*.
3. **Beat >= 1 baseline.** The futures benchmark is compared against an explicit
   baseline (random-walk spot is the natural null). Errors reported side by side.
4. **No random splits for time series.** Comparison is time-ordered and scoped to
   the overlap window (`<= 2024-04-05`); no shuffling.
5. **No leakage / never use data not known at origin.** The settlement-is-not-spot
   trap is handled: either same-day basis (both known at t) or delivery-month
   outcome with `target_date = origin + horizon` matched to *future* realized spot.
6. **Report states what would make the model fail.** Names the risk premium,
   the 4-contract/stale-data scope, and a concrete failure condition.

## The 4 review passes

### Pass 1 — Reproducibility
- `uv run python 11_futures_curve_expectations/main.py` runs from repo root, exit 0.
- Paths via `ng_models.paths` (`data_dir`/`ensure_output_dir`), not `../data`.
- Outputs land in `outputs/`. Missing-input path prints an actionable message and
  exits cleanly (does not crash).

### Pass 2 — Data correctness
- Dates parsed as real datetimes and sorted (not lexicographic).
- Curve reshape (long→wide) is correct; missing-leg snapshots handled deliberately.
- Units consistent ($/MMBtu); spot vs futures not silently mixed.
- Comparisons scoped to `<= 2024-04-05`; learner acknowledges the stale/shallow data.

### Pass 3 — Modeling / evaluation correctness
- Curve-shape classification correct for the chosen contract ordering (C4>C1 →
  contango). Spread choice and "flat" threshold justified.
- Comparison framing (same-day basis vs delivery-month outcome) is stated and is
  internally leakage-free.
- Baseline present and beaten-or-honestly-not; skill stated relative to baseline.

### Pass 4 — Interpretation quality
- Distinguishes futures price, expected spot, risk premium, basis, roll yield.
- No "futures = forecast" claim. No causal claim from curve shape.
- States the scope limits and a concrete out-of-sample failure mode.

## Hint strategy (high level; details in HINTS.md)
- Make the learner explain what a contract settles to and what delivery month
  means before any benchmark claim (decision E/A).
- Push them to write the one-sentence forecast statement (target + horizon +
  origin) before comparing to spot.
- Help freely with pivot/reshape and merge_asof API (type K). Withhold the
  framing, baseline, and interpretation decisions (types A/B/E/J).

## Scoring guide (4-point scale)

- **4 — Strong:** Correct curve mechanics; leakage-free comparison with explicit
  origin+target; beats (or honestly fails) a stated baseline; interpretation
  separates price/expectation/risk premium and names a failure mode. Scoped to
  overlap window.
- **3 — Pass:** Mostly correct with minor gaps (e.g. baseline present but skill
  not framed relative to it, or scope mentioned but loosely).
- **2 — Revise:** A substantive data/modeling issue — e.g. settlement compared to
  same-day spot but called a forecast, or missing origin/target dates, or no
  baseline.
- **1 — Not yet:** Does not run, ignores the overlap-window scope, or treats
  futures as a forecast with no evaluation.

Grade on correctness, reasoning, and discipline — not model sophistication.
