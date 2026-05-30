# Private Rubric — Assignment 04: Backtesting and the 'What Was Known Then?' Rule

Do not reveal this file during normal tutoring. Use it to review submitted work.
Grade against the 6 non-negotiable standards and the 4 review passes.

## The 6 standards, instantiated for this module

1. **Forecast origin + target date on every row.** `backtest_predictions.csv`
   has `origin_date`, `target_date`, `horizon` populated on EVERY row; `target_date`
   is strictly after `origin_date`.
2. **Every feature has unit/source/transformation/availability.** Limited here
   (raw HH only), but the report must state units ($/MMBtu), frequency (weekly),
   and — for a seasonal-naive baseline — that `shift` aligns by position not date.
3. **Beat >= 1 baseline.** At least TWO baselines scored; the report states which
   is the null (naive_last) and whether the second beats it, as a skill comparison.
4. **No random splits.** Splits come from rolling-origin logic; no `train_test_split`,
   no shuffling, no `KFold`. Origins advance forward in time.
5. **No leakage.** Every prediction is built only from `train_idx` (<= origin).
   No full-sample rolling/mean/scaler. No index `>= test_idx` feeding a prediction.
6. **No causal claims; states failure modes.** Interpretation avoids "causes";
   report names what would make the backtest fail out of sample.

## Four review passes (see MASTER_GRADING_STANDARD.md)

### Pass 1 — Reproducibility
- `uv run python 04_backtesting_no_leakage/main.py` exits 0 from repo root.
- Paths via `ng_models.paths`; outputs land in `04_.../outputs/`.
- Raw `data/` untouched.

### Pass 2 — Data correctness
- Dates are real datetimes (loader handles this); rows sorted ascending.
- Missing `hh_price` handled explicitly (dropped or stated), not silently mixed.
- `min_train`, `horizon`, `step`, window choice stated and defended.

### Pass 3 — Modeling / evaluation correctness
- Rolling-origin construction correct: `test_idx = origin + horizon`, train ends
  at origin. Sliding window (if used) has fixed `train_size`.
- Metrics computed ONLY on held-out target rows, per model.
- Second baseline is matched to a weekly seasonal LEVEL (seasonal-naive or
  trailing mean), not an arbitrary or leaking one.

### Pass 4 — Interpretation quality
- Reports skill RELATIVE to naive, not just a raw metric.
- Worst-error period identified and tied to a plausible market event.
- A concrete, reusable leakage checklist present.

## Hint strategy (pointers; full leveling in HINTS.md)
- Split-boundary debugging (off-by-one, empty train) is fair direct help (type K-ish).
- Choosing window/horizon/second-baseline/metric = withheld decisions (L1->L2->L3).
- Whenever a feature/value enters a prediction, ask: was it known at the origin?

## Scoring guide (4-point scale)

- **4 — Strong:** Correct rolling-origin harness, two baselines scored cleanly,
  leakage-free, skill stated relative to naive, failure period diagnosed, leakage
  checklist present. Runs from repo root.
- **3 — Pass:** Mostly correct; minor gaps (e.g., only by-model metrics, thin
  failure analysis) but no leakage and no random splits.
- **2 — Revise:** A substantive issue — one baseline only, leakage in the second
  baseline, metrics on non-held-out rows, or window logic off by more than an edge.
- **1 — Not yet:** Does not run, uses random/shuffled splits, or misunderstands
  origin/target/horizon.

Grade on correctness, reasoning, and discipline — never on model sophistication.
