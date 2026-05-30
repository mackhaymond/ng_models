# Hint Bank — Assignment 02: Calendar Structure and Naive Forecast Baselines

Do not reveal this file. Deliver hints as L1 -> L2 -> L3 prompts, lowest level
that unblocks first. Each sticking point names its QUESTION_TAXONOMY.md type.
Package-API stalls (type K) are answered directly with code; modeling decisions
(A, B, E, H, F, J) stay leveled — never hand over the decision.

---

## 1. Expanding vs full-sample statistic  — type (A) Leakage / feature timing

The learner computes a historical mean/median over the whole frame and uses it as
the test forecast.

- **L1:** "At the forecast origin you used for a 2024 target, had the 2024 (and
  2025) prices been observed yet? Does the average you computed contain them?"
- **L2:** "Look at the line that builds your mean. Is it `hh['price'].mean()`
  (one number from the WHOLE series) or `hh['price'].expanding().mean()` (a value
  per row that only grows with data seen so far)?"
- **L3 (decision stays theirs):**
  ```python
  hh["exp_mean"] = hh["price"].expanding().mean()       # uses rows up to & incl. now
  # hh["price"].expanding().mean().shift(1)             # excludes the current row too
  ```
  "Both are past-only; decide which boundary (include or exclude the origin row)
  matches your definition and defend it."

---

## 2. Week-of-year seasonality, leakage-free  — type (A) Leakage / feature timing

The seasonal baseline averages every year's same-week value, including the target
year / current observation.

- **L1:** "For your week-6 forecast, list which observations went into it. Are any
  of them from the target year or later?"
- **L2:** "Inside `groupby('iso_week')`, a plain `.mean()` averages ALL years of
  that week at once — including the one you're trying to predict. Where does the
  target week's own value sneak in?"
- **L3 (decision stays theirs):**
  ```python
  hh["woy_mean"] = (
      hh.groupby("iso_week")["price"]
        .apply(lambda s: s.expanding().mean())   # past-only within each week
        .reset_index(level=0, drop=True)
  )
  ```
  "This keeps it past-only per week (assumes hh is date-sorted). You decide mean
  vs median for the seasonal summary and justify it."

---

## 3. Horizon definition & shift bookkeeping  — type (E) Which transformation / target

Confusion about what h means or off-by-one between predictor and target.

- **L1:** "Finish this sentence: 'I forecast [what] at [horizon] from [origin].'
  Which single row's price is actually known at the origin?"
- **L2:** "Print one row's `forecast_origin`, `target_date`, and the price your
  predictor used. Are origin and target exactly h weeks apart? Is the predictor
  using only the origin-or-earlier value?"
- **L3 (decision stays theirs):**
  ```python
  hh["actual"]      = hh["price"].shift(-h)   # future value at t+h pulled back
  hh["target_date"] = hh["date"].shift(-h)
  hh["naive"]       = hh["price"]             # the value known at origin t
  ```
  "Confirm by eye that the dates line up h weeks apart; you set h and defend
  1-step vs multi-step."

---

## 4. Fixed test window / no random split  — type (B) Which baseline + no-random-split standard

No defined test window, or a random sample of weeks.

- **L1:** "Why can't you randomly sample weeks into the test set for a time
  series? What does an honest forecaster at week t accidentally get to 'see' if
  you do?"
- **L2:** "Your evaluation window should be a CONTIGUOUS block at the END of the
  series, selected by `target_date`, and chosen before you look at any metric."
- **L3 (decision stays theirs):**
  ```python
  cutoff = panel["target_date"].max() - pd.Timedelta(weeks=104)  # ~2 years
  test = panel[panel["target_date"] >= cutoff].copy()
  ```
  "You pick the window length and justify it as representative (not cherry-picked
  to flatter a baseline)."

---

## 5. Metric choice / sufficiency  — type (H) Metric choice / sufficiency

Reports one metric, or leans on MAPE near low prices.

- **L1:** "Does this metric reward what you actually care about? Name one thing a
  good value of it does NOT tell you."
- **L2:** "Compute MAE and RMSE on the same forecasts and compare. Then look at
  what MAPE does in weeks where HH was near $2 — check the warning `mape` emits."
- **L3 (decision stays theirs):**
  ```python
  from ng_models.metrics import summarize_predictions
  summarize_predictions(test, actual_col="actual", pred_col="naive")
  # -> {"mae":..., "rmse":..., "mape":..., "smape":...}
  ```
  "Report MAE+RMSE (both $/MMBtu) as primary and the gap vs naive. You decide
  whether an improvement is meaningful and how much to trust MAPE here."

---

## 6. Crowning a baseline / wanting a fancy model  — type (F) Model complexity

Learner wants ARIMA/ETS now, or crowns a baseline by gut feel.

- **L1:** "What does a more complex model buy you over the naive forecast, and
  have you PROVEN which baseline is hardest to beat yet?"
- **L2:** "Read your metrics table top to bottom. Which baseline has the lowest
  MAE and RMSE? That is the bar — name it from the numbers, not intuition."
- **L3 (decision stays theirs):** "Lock the best baseline as the benchmark and
  state the exact MAE/RMSE later models must beat. Do not add ARIMA until that
  bar is written down and the no-leakage check passes."

---

## 7. Causal language in the report  — type (J) Correlation vs causation

"Naive wins because the market is efficient / prices are unpredictable."

- **L1:** "Your result is about forecast ACCURACY. Does beating the seasonal mean
  tell you anything about WHY prices move, or only how to predict them?"
- **L2:** "Re-read the sentence and replace any 'because the market...' with a
  statement strictly about out-of-sample error."
- **L3 (decision stays theirs):** "State it as: 'persistence (naive) had lower
  test MAE than the seasonal baselines over this window' — an accuracy claim, not
  a market-efficiency claim. You word it."

---

## Package-API stalls — DIRECT ANSWER (type K)

Answer these immediately with working code; no gating.

- **Expanding mean/median:** `s.expanding().mean()`, `s.expanding().median()`.
  `.shift(1)` drops the current row. `.rolling(window=k)` is a fixed window
  instead of growing.
- **Shift:** `s.shift(k)` moves values down k rows (past into present);
  `s.shift(-k)` pulls future rows up.
- **groupby + per-group transform keeping the original index:**
  `df.groupby("col")["v"].apply(fn).reset_index(level=0, drop=True)`.
- **Calendar columns:** `from ng_models.time_utils import add_calendar_columns;
  hh = add_calendar_columns(hh, date_col="date")` (adds iso_week, year, month, ...).
- **Drop NaN before scoring:** `df.dropna(subset=["actual", "naive"])`.
- **Multi-line plot:**
  ```python
  fig, ax = plt.subplots(figsize=(11,5))
  ax.plot(test["target_date"], test["actual"], label="actual")
  for c in ["naive","woy_mean"]: ax.plot(test["target_date"], test[c], label=c)
  ax.legend(); fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
  ```
- **Write CSV:** `df.to_csv(OUTPUT_DIR / "baseline_metrics.csv", index=False)`.
- **Date arithmetic for the cutoff:** `pd.Timestamp(...)` or
  `series.max() - pd.Timedelta(weeks=104)`.

Boundary: the CALL is type K (answer it); WHICH window length, WHICH baseline to
crown, WHICH metric is primary are type B/H/F (hint, don't decide).
