# Assignment 14: Capstone — End-to-End Henry Hub Forecast System and Research Memo

**Phase:** Capstone
**Level:** Advanced
**Estimated time:** 15-30 hours

This is the capstone. You are not learning a new technique — you are assembling
everything from modules 02-13 into ONE reproducible forecast system and writing
it up the way an applied energy analyst would: a model card and a research memo.
You are graded on **process discipline**, not on how fancy the final model is. A
clean pipeline whose final model barely beats (or honestly fails to beat) a
strong baseline — with the reasoning written down — outscores a fancy model on a
leaky backtest. **There is no single correct final model.**

## Data scope

This module SITS ON TOP of module 09's validated, leakage-safe panel:

- **Required input:** `09_feature_table_leakage/outputs/model_panel.csv`
  (one row per forecast: `forecast_origin`, `target_date`, `target`, and
  leakage-safe predictor columns). If it is missing, `main.py` prints a
  "complete module 09 first" message and exits cleanly — run module 09 first.
- **Optional benchmark data (already in `data/`):** `NG.RNGC1.W.csv` is the
  weekly NYMEX **front-month** natural-gas futures settle. Use it as a
  market-implied benchmark for a price-LEVEL target. (Contracts 1-4 are
  `NG.RNGC1..4` at `.D/.W/.M/.A` frequencies.)

Do not modify anything in `data/`. Save every generated file under this
assignment's `outputs/`.

## The open choices you must make and DEFEND

The audit flagged these as ambiguous on purpose — they are yours to decide:

1. **Target, frequency, and horizon.** Reuse the target you defined in module 09
   (set `TARGET_COL` in `main.py`). State it as ONE sentence:
   *"I forecast [what] at [horizon] from [origin]."* Is it a price **level**, a
   **change**, or a **return**? The horizon is in panel ROWS — on a weekly spine
   `horizon=1` means one week ahead. Your answer here dictates which baselines
   are valid and which metric is honest.
2. **Required baselines.** You must include **at least three honest comparisons**:
   - **Persistence / random walk** — `y_hat[t+h] = last known level` (the
     origin-date price, e.g. the `*_lag_1` column). The right null for a level.
   - **Seasonal-naive** — `y_hat[t+h] = value one season (52 weeks) ago`. The
     right null when the series has a strong calendar cycle.
   - **Market / futures benchmark** — the NYMEX front-month settle KNOWN at the
     origin (`merge_asof` on `forecast_origin`, `direction="backward"`). This is
     a *strong* null: it is what the market itself implies. Beating it is hard,
     and that is the point. (A futures price is NOT a forecast — it is a
     tradeable equilibrium with risk premia — but it is a fair benchmark.)
3. **Final model + when to stop.** Fit ONE final model only AFTER the baselines
   exist. Simplest first (Ridge/Lasso), boosting (LightGBM/XGBoost) only if the
   linear model already beats the baseline. **Stop adding features/complexity when
   the next addition does not improve OUT-OF-SAMPLE skill over the baseline in the
   same walk-forward loop.**
4. **"Uncertainty estimates" — what they actually mean.** A point forecast plus a
   **calibrated prediction interval**, not a band you never checked. Build the
   interval from your backtest residual spread (e.g. point ± z·residual_std) and
   then **verify empirical coverage**: an 80% interval should contain ~80% of
   out-of-sample actuals. If it covers 55%, your intervals are overconfident —
   say so.

## Tasks

1. Confirm your final forecast target and horizon (Stage 2 in `main.py`).
2. Load the model panel with one command (Stage 1 — already wired).
3. Build the 3 baselines above (Stage 3) — each a leakage-safe prediction column.
4. Fit ONE final model (Stage 4) — only after baselines are scored.
5. Evaluate ALL forecasters with the SAME walk-forward loop (Stage 5) — no random
   split, no leakage. Report metrics relative to the baseline (a skill score).
6. Produce point forecasts, calibrated uncertainty, and a driver summary (Stage 6).
7. Write `MODEL_CARD.md` and `RESEARCH_MEMO.md` from those outputs (Stage 7).

## Deliverables

- `outputs/final_model_metrics.csv` — one row per forecaster (baselines + final),
  with metric and skill-vs-baseline.
- `outputs/final_forecast_package.csv` — auditable per-row forecasts; every row
  carries `forecast_origin` + `target_date` + point + interval bounds.
- `outputs/final_charts/*.png`
- `MODEL_CARD.md` — fill in the provided template.
- `RESEARCH_MEMO.md` — fill in the provided template.
- `REPORT.md` — answer the questions at the bottom (see `REPORT_TEMPLATE.md`).

## Rules

- Keep raw data immutable; save generated files under `outputs/`.
- Write down every assumption about dates, units, frequency conversion, missing
  values, and **information availability** (was each value public at the origin?).
- A chart is not enough. Every chart needs a sentence saying what it shows AND
  what it does not show.
- Do not move to a more complex model until the required baseline is complete and
  scored out of sample.
- No random train/test split for time series. No leakage — never evaluate on data
  used to build a feature or benchmark. No causal claims from correlation.

## Concepts you'll use

- **Model card** — a one-page factual spec of a model: what it predicts, the
  target/origin/horizon/units, the features and their availability, how it was
  validated, how it performs vs baselines, and when it should NOT be trusted.
  Think of it as the label on the bottle.
- **Research memo** — a short analyst write-up of the *finding*: the problem, the
  data decisions, baseline vs final results, error analysis, key drivers, limits,
  and next questions. It reads like applied research, not a code dump.
- **Baseline / benchmark** — the cheapest honest forecast your model must beat. A
  *baseline* is a no-model rule (persistence, seasonal-naive). A *benchmark* here
  is the market's own implied number (the futures settle). If you cannot beat
  these, you do not have a useful model — and saying so clearly is a valid result.
- **Backtest / walk-forward validation** — simulating how the forecast would have
  performed historically by always training on the past and testing on the future,
  rolling the origin forward. It mimics real deployment: make a call, wait, see
  what happened, advance. The opposite of a random shuffle, which would leak.
- **Skill score** — a metric expressed RELATIVE to a baseline, e.g.
  `1 - model_RMSE / baseline_RMSE`. Positive means you beat the baseline; the raw
  RMSE alone never tells you that.
- **Prediction interval & empirical coverage** — the interval is your stated
  uncertainty (e.g. an 80% band); coverage is the fraction of actuals that
  *actually* fell inside it out of sample. A well-calibrated 80% interval covers
  ~80%. This is the honesty check on "uncertainty estimates".
- **Feature importance is not causation** — a high importance means the feature
  *helped predict* in this sample, possibly only because it correlates with a real
  driver. It does not prove the feature *causes* price moves.
- **Deployment / monitoring / retraining** — deployment is putting the model into
  regular use; monitoring is watching live error and input drift to catch when it
  degrades; retraining is the rule for refreshing the model (how often, on what
  trigger). The model card states all three so the model can be maintained.
- **Forecast package** — the auditable table of forecasts you ship: one row per
  forecast with origin, target date, point forecast, and interval bounds, so any
  reviewer can check timing and outcome.

Cross-reference `docs/GLOSSARY_SEED.md` for: *Walk-forward*, *Backtest*,
*Leakage*, *In-sample vs out-of-sample*, *Prediction interval*,
*Empirical coverage*, *Calibration*, *Why futures are NOT forecasts*,
*Forecast origin*, *Cross-validation for time series*.

## Package guide

Minimal API snippets for the libraries this module needs. These are the *calls*;
the *choices* (which baseline, which model, n_splits) are yours to defend.

**pandas — load the panel, merge the futures benchmark as-of the origin**
```python
import pandas as pd
panel = pd.read_csv(path, parse_dates=["forecast_origin", "target_date"])
# Attach the front-month settle KNOWN at each origin (never look forward):
fut = load_series_csv(DATA_DIR, "NG.RNGC1.W.csv", value_name="nymex_c1")
merged = pd.merge_asof(
    panel.sort_values("forecast_origin"),
    fut.rename(columns={"date": "fut_asof"}).sort_values("fut_asof"),
    left_on="forecast_origin", right_on="fut_asof",
    direction="backward",   # most recent settle at or before the origin
)
```

**ng_models — metrics (already importable)**
```python
from ng_models.metrics import mae, rmse, smape, summarize_predictions
summarize_predictions(df, actual_col="actual", pred_col="prediction")
# -> {"mae":..., "rmse":..., "mape":..., "smape":...}  (one comparison row)
```

**scikit-learn — time-ordered walk-forward (NEVER a shuffled split)**
```python
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge
oos = []
for tr, te in TimeSeriesSplit(n_splits=5).split(df):       # te is always future
    model = Ridge(alpha=1.0).fit(X.iloc[tr], y.iloc[tr])
    pred = model.predict(X.iloc[te])                        # baselines need no fit
    oos.append(pd.DataFrame({"idx": te, "pred": pred}))
```

**scikit-learn — driver summary (importance is NOT causation)**
```python
from sklearn.inspection import permutation_importance
r = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=0)
# importances_mean[i] = how much score WORSENED when feature i was shuffled.
# Run on a HELD-OUT fold, not training data.
```

**LightGBM (optional, only after a linear model beats the baseline)**
```python
import lightgbm as lgb
model = lgb.LGBMRegressor(n_estimators=400, learning_rate=0.03,
                          num_leaves=31, random_state=0)
# Trees need NO feature scaling. Validate in the SAME walk-forward loop.
```

**Prediction interval + empirical coverage (your honesty check)**
```python
resid = y_oos_true - y_oos_pred           # backtest residuals
sigma = resid.std()
lower, upper = y_oos_pred - 1.28 * sigma, y_oos_pred + 1.28 * sigma  # ~80%
coverage = ((y_oos_true >= lower) & (y_oos_true <= upper)).mean()    # want ~0.80
```

## Questions to answer in `REPORT.md`

- What is the forecast target, horizon, and origin (one sentence)?
- What dates, units, and frequencies are involved?
- What was the most important data / information-availability decision?
- Does the final model beat persistence, seasonal-naive, AND the futures
  benchmark out of sample? By how much (skill score)?
- Is your 80% interval actually 80% (empirical coverage)?
- What would make this model FAIL out of sample?
- What should the next experiment investigate?
