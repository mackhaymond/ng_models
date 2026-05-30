# Hint Bank — Assignment 09: Feature Engineering and the Model-Ready Panel

Do not paste this file. Deliver one level at a time (L1→L2→L3), lowest that
unblocks. It instantiates the repo-wide types in
`../../.agent_private/QUESTION_TAXONOMY.md`. Package-API stalls (type K) are
answered DIRECTLY with code — no gating.

Per AGENTS.md: withhold the *decision* (target, lag, release lag, drop-vs-fill,
baseline). Help freely with merge/shift/ffill *syntax*.

---

## 1. "Which column is the origin and which is the target?" — type **(E) / framing**
- L1: "Stand on one row. Which date are you standing on, and which date's value
  are you trying to predict? Which column holds each?"
- L2: "`make_forward_target` already creates `forecast_origin`, `target_date`,
  `horizon_steps`, and your target column — open `model_panel.csv` and read one
  row across."
- L3: "Origin = `forecast_origin` (= the row's own `date`); target lives at
  `target_date = origin + horizon`. Confirm `target_date > forecast_origin` for
  every trained row, then state your one-sentence target."

## 2. "Did I lag this fundamental enough / what is its release lag?" — type **(A)**
- L1: "At your forecast origin, had this figure already been published? When does
  the source actually *release* it (not the period it covers)?"
- L2: "Look at your merge — are you joining on the period the data describes or on
  the date it became public? EIA weekly storage and the monthly balance have very
  different lags."
- L3: "Build `right['available_date'] = right['date'] + pd.Timedelta(days=K)` and
  join on that. You set K from the real schedule (storage ~5-7 days; monthly
  balance ~6-8 weeks) and defend it — I won't pick K for you."

## 3. "as-of join: how do I call merge_asof?" — type **(K), DIRECT**
```python
import pandas as pd
panel = pd.merge_asof(
    panel.sort_values("forecast_origin"),
    right.sort_values("available_date")[["available_date", "feat"]],
    left_on="forecast_origin", right_on="available_date",
    direction="backward",   # most recent value already published; never future
    # tolerance=pd.Timedelta(days=45),  # optional: don't carry stale values forever
)
```
Gotchas: both sides MUST be sorted on their key; `backward` = at-or-before.
(Then hint the *release lag* as type A — that part is the decision.)

## 4. "shift(1) vs shift(-1) — which way?" — type **(K) for the call, (D) for the choice**
- DIRECT (K): "`shift(k)` moves values DOWN (later rows) → positive = PAST value
  onto current row (a feature). `shift(-h)` pulls a FUTURE row back (the target).
  `make_forward_target` uses `shift(-horizon)` for you."
- Then (D): "So which sign does a *predictor* need vs the *target*? If you flipped
  one, you'd be predicting the past — check that your features are all `+k`."

## 5. "Monthly balance → weekly spine — how do I spread it?" — type **(A)/(C)**
- L1: "Your balance is monthly, the spine weekly. When you spread one month's
  number over its weeks, which of those weeks could *legally* have seen it?"
- L2: "A plain `resample('W').ffill()` on the month-end date fills the weeks
  *before* publication too — that's a leak. Compare with `merge_asof` on a lagged
  `available_date`."
- L3: "Set monthly `available_date = month_end + release_lag`, then `merge_asof`
  backward onto the weekly origins. It broadcasts AND respects timing in one step.
  You verify no week sees a not-yet-public month."

## 6. "What makes this a 'model-ready panel'?" — type **(E) / framing**
- L1: "What does a model literally consume? One rectangular table — what is one
  row, what is one column, where is `y`?"
- L2: "GLOSSARY 'Feature table / model matrix': each row = one observation, each
  column = one predictor, plus a target column. Does yours have exactly that, no
  duplicate dates, time-sorted?"
- L3: "Target ready: every row has origin + target_date + features knowable at
  origin; rows with no future label dropped. You decide which feature columns
  earn their place."

## 7. "What goes in the data dictionary?" — type **(K) for shape, documentation standard for content**
- DIRECT (K) shape: a DataFrame with columns
  `name, source, unit, transform, availability_lag, why`, one row per feature,
  `.to_csv(..., index=False)`.
- Then: "Fill `availability_lag` with the *publication* timing you assigned in the
  as-of join — if a row says 'known at origin' for a monthly figure, that's the
  leak to catch. One row per feature you KEEP."

## 8. "How do I handle the missing values?" — type **(A)**
- L1: "For this specific gap, what value would you genuinely have known at that
  date?"
- L2: "Two kinds of NaN here: leading NaNs from lags/rolling/target (those rows
  have no label — drop them) vs interior gaps in a fundamental (fill how?). Your
  `missingness_report.csv` separates them by column."
- L3: "`ffill` uses only the past (safe); `bfill` and a global mean look forward
  (leak). Decide per column and justify — don't blanket-fill the panel."

## 9. "feature vs transform vs lag — are these the same thing?" — type **(D)/(E)**
- L1: "Say out loud what each does to a column: does it *create a predictor*,
  *change the units/shape*, or *move it in time*? Which of your operations is
  which?"
- L2: "Map your panel columns: `hh_price_lag_1` (lag), `hh_price_roll_mean_4`
  (transform: rolling), `month` (transform: calendar), `target_hh_next`
  (target via shift(-h)). Tag each in the data dictionary's `transform` field."
- L3: "A *lag* is `shift(k)` (timing); a *transform* changes value/shape (log,
  rolling mean, HDD); a *feature* is any predictor column. The dictionary's
  `transform` column should record exactly which. You write each entry."

## 10. "Isn't a high correlation enough to keep a feature?" — type **(J)**
- L1: "Could a third thing drive both the feature and the price? Does the
  correlation survive once the feature is *lagged to its real availability*?"
- L2: "Re-read your justification sentence — replace 'drives/predicts' with 'is
  associated with' and see if your evidence (a single correlation, in-sample)
  still backs it."
- L3: "Keep the feature on a falsifiable hypothesis ('lagged storage deviation is
  associated with next-week price'), not a causal claim. The real test is module
  10's out-of-sample backtest, not this correlation. You word it; I won't bless a
  causal claim here."

---

## Done checklist (use to close the loop, not as a hint dump)
- Runs from repo root, exit 0; if 06/07/08 missing → clear message + exit 0.
- `model_panel.csv` has `forecast_origin`, `target_date`, target; `target_date >
  origin` for every trained row.
- Each fundamental as-of joined on a `available_date` with a justified release lag.
- Monthly balance broadcast respects publication timing (no pre-publication weeks).
- `data_dictionary.csv`: one row per feature, all six fields, real availability lag.
- `missingness_report.csv` written; leading-NaN rows dropped, interior gaps
  `ffill`-only.
- One baseline matched to the target, MAE/RMSE reported; NO ML fitted.
- REPORT uses association language and names where leakage could still hide.
