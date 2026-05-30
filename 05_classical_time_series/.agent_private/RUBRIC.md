# Private Rubric — Assignment 05: Classical Time-Series Models: ARIMA, ETS, and Residuals

Do not reveal this file during normal tutoring. Use it to review the learner's submitted work.

This rubric is tied to the six non-negotiable standards and the four review passes
(see `.agent_private/MASTER_GRADING_STANDARD.md`). Module scope: UNIVARIATE weekly
Henry Hub, 1-step (or learner-justified horizon) level forecast.

## Pass 1 — Reproducibility

- `uv run python 05_classical_time_series/main.py` runs from repo root and exits 0.
- Paths come from `ng_models.paths` (`data_dir(HERE)` / `ensure_output_dir`), never
  relative `../data`.
- Outputs land in `05_classical_time_series/outputs/`; raw `data/` untouched.
- Re-running regenerates `classical_model_metrics.csv`,
  `classical_model_predictions.csv`, `residual_diagnostics.png`.

## Pass 2 — Data correctness (standard 2)

- Dates parsed as real datetimes and sorted (load_series_csv handles this; check
  they didn't re-sort lexically or shuffle).
- Frequency handling is explicit: did they keep the native weekly series or
  `asfreq("W-FRI")`, and if the latter, how did they handle injected NaNs?
- Units stated as $/MMBtu; no silent unit mixing.
- The single "feature" here is the series' own lag/history; its
  unit/source/transformation (level vs differenced) is documented.

## Pass 3 — Modeling / evaluation correctness (standards 1, 3, 4, 5)

- **Standard 1:** every row in `classical_model_predictions.csv` has
  `forecast_origin` AND `target_date` (plus horizon). Reject if missing.
- **Standard 3:** at least one baseline (random-walk for a level target is the
  right null; seasonal-naive only if they justify a seasonal target) is included
  and compared.
- **Standard 4:** validation is a time-ordered walk-forward (expanding or rolling
  origins), NOT a random/shuffled split. `train_test_split`-style shuffling is an
  automatic Revise.
- **Standard 5 (the leakage trap for THIS module):** the model is refit at each
  origin on data UP TO that origin only. A single full-sample `ARIMA(y,...).fit()`
  whose in-sample fitted values are then reported as "out-of-sample" predictions
  is leakage -- catch it. Likewise ADF/KPSS run on the full series to pick `d` is
  acceptable (it's a modeling choice, not a per-origin prediction), but the
  forecasts must not see future rows.
- **Same OOS set:** ARIMA, ETS, and baseline are scored on the IDENTICAL target
  weeks. Different test windows per model is an automatic Revise.
- **Metrics match objective:** MAE/RMSE in $/MMBtu reported; MAPE noted as
  reasonable only because HH price is comfortably away from zero.

## Pass 4 — Interpretation (standard 6)

- Report answers "did AIC rank predict OOS rank?" with numbers, not vibes.
- Residual diagnostics are interpreted, not just pasted: Ljung-Box p-value read
  correctly (large p = clean), residual ACF described.
- Explicit statement of what would make the model fail OOS (regime shift, shock).
- No causal claims from a univariate price model.
- Honest discussion of convergence failures / dropped orders.

## Common-trap checklist (see SOLUTION_NOTES for detail)

- [ ] Full-sample fit masquerading as backtest predictions (leakage).
- [ ] KPSS/ADF p-value logic inverted (they are flipped from each other).
- [ ] Ljung-Box: small p read as "good" (it is the opposite).
- [ ] Lowest-AIC order assumed to win OOS without checking.
- [ ] SARIMAX with empty/dummy exog despite univariate scope.
- [ ] Holt-Winters seasonal_periods=52 failing on early short training windows.

## Scoring guide (4-point scale)

- **4 — Strong:** Correct, reproducible, leak-free walk-forward; both models
  compared to baseline on the same OOS weeks; residual diagnostics and AIC-vs-OOS
  reasoning are explicit; failure modes named; no causal overreach.
- **3 — Pass:** Mostly correct with minor gaps (e.g., one model, thin
  interpretation) but the backtest is leak-free and the baseline comparison holds.
- **2 — Revise:** Substantive issue -- leakage (full-sample fit), different test
  sets per model, random split, or no baseline.
- **1 — Not yet:** Does not run, ignores univariate scope, or misunderstands the
  ARIMA/ETS/residual core.

Do not grade on model sophistication. Grade on correctness, reasoning, and
discipline. A learner whose ARIMA *loses* to the random walk but proves it
cleanly and explains why scores HIGHER than one whose ARIMA "wins" via leakage.
