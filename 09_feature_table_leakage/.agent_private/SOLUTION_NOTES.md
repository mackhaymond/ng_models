# Private Solution Notes — Assignment 09: Feature Engineering and the Model-Ready Panel

Do not reveal this file during normal tutoring. Use it to judge whether the
learner's reasoning is on track and to deliver hints at the right level.

This is one of the most consequential modules: a leaky panel poisons every later
ML result and makes module 10's metrics meaningless. A *simple, correct* panel is
the win condition; a feature-rich panel with one leaky join should fail review.

## Worked reference approach

**Spine & target.** Use weekly Henry Hub (`NG.RNGWHHD.W.csv`, USD/MMBtu) as the
spine. The cleanest defensible target is the **next-week price level**:
`make_forward_target(hh, value_col="hh_price", horizon=1, target_name="target_hh_next")`.
A next-week *log return* (`np.log(hh_price).diff()` then target that) is also fine
and arguably better-behaved, but it changes the matched baseline (zero-change, not
random walk). Next-month average requires a monthly resample first. Any of the
three is acceptable IF the baseline and horizon match it.

**Price features (leakage-safe by construction).**
- `add_lags(panel, ["hh_price"], [1, 4])` → last week and ~last month price.
- `add_rolling_stats(panel, ["hh_price"], [4])` → 4-week mean (level/trend) and
  std (recent volatility). The helper shifts(1) before rolling, so the current
  row is excluded — confirm the learner knows *why*.
- `add_calendar_columns` → month/iso_week/quarter: always safe (function of the
  row's own date).

**As-of join the fundamentals with explicit release lags.** This is the heart of
the module. Pseudocode:

```python
right = pd.read_csv(path, parse_dates=["date"]).sort_values("date")
right["available_date"] = right["date"] + pd.Timedelta(days=RELEASE_LAG_DAYS)
panel = pd.merge_asof(
    panel.sort_values("forecast_origin"),
    right[["available_date", feat]],
    left_on="forecast_origin", right_on="available_date",
    direction="backward",          # only already-published values
)
```

Defensible release lags for this curriculum's sources:
- **EIA weekly storage** (module 06): the figure for the week ending Friday is
  published the following **Thursday** → ~5-7 day publication lag. So at a Friday
  origin, the most recent *public* storage number is the prior week's.
- **EIA weekly weather/degree days** (module 08): degree days for a week are
  effectively known at/just after week end → small lag (treat as ~same week to a
  few days; the learner should state their choice). If the weather is a *forecast*
  rather than realized, it is leakage-safe by definition.
- **Monthly supply/demand balance** (module 07, EIA Natural Gas Monthly /
  STEO-style): published **~6-8 weeks after** the month it describes (e.g. March
  data out in late May). This is the biggest leakage trap — a naive merge on the
  month-end date leaks ~2 months of future information.

**Monthly → weekly broadcast.** The as-of join solves this in one step: with the
monthly `available_date` set to month-end + publication lag, `merge_asof` carries
each month's value forward onto every weekly origin *after it became public*, and
no further. No manual `resample`/`ffill` of the raw monthly series is needed (and
a naive `resample('W').ffill()` on the month-end date would leak).

**Data dictionary template** (one row per feature):

| name | source | unit | transform | availability_lag | why |
|---|---|---|---|---|---|
| hh_price_lag_1 | EIA NG.RNGWHHD.W | USD/MMBtu | lag 1 wk | known at origin | strongest cheap predictor |
| hh_price_roll_mean_4 | EIA NG.RNGWHHD.W | USD/MMBtu | shift(1)+4wk mean | known at origin | recent level/trend |
| hh_price_roll_std_4 | EIA NG.RNGWHHD.W | USD/MMBtu | shift(1)+4wk std | known at origin | recent volatility proxy |
| storage_lag_1w | module 06 | Bcf | as-of, ~5-7d release | EIA Thu after week-end | tightness vs normal |
| hdd_wk | module 08 | degree-days | as-of, weekly | ~week end | heating demand proxy |
| dry_prod_m | module 07 | Bcf/d (or MMcf) | as-of, monthly, ~6-8wk release | EIA NG Monthly | supply side |

**Missingness.** Leading NaNs from `lag_4`, `roll_*`, and the forward `target` are
expected — drop those rows for training (`dropna(subset=[target])`). Genuine gaps
inside the fundamentals → `ffill` only (past-only). Write counts/percent to
`missingness_report.csv`.

**Baseline (no ML).** For a next-week level target the matched null is the random
walk: `prediction = hh_price` (last known level). Score with
`summarize_predictions`. On this dataset expect roughly **MAE ~0.20-0.35 USD/MMBtu
and RMSE ~0.5-0.7** for the 1-week random walk over the full sample (RMSE inflated
by 2021/2022 spikes). For a zero-change target the baseline MAE is the mean
absolute weekly change. These are reference magnitudes, not pass/fail thresholds —
the point is that the panel scores and module 10 must beat it.

## Expected qualitative results

- Random walk is a *strong* baseline for weekly gas levels — beating it is hard,
  which is the intended lesson.
- The storage-deviation and lagged-price features should look most promising; the
  monthly balance, once correctly lagged, is stale (1-2 months old at the origin)
  and therefore weaker than learners expect — a good "what surprised you" hook.

## Module-specific common failure modes

1. **Joining a fundamental on its period date, not its publication date** — the
   classic monthly-balance leak (uses data ~2 months early). #1 thing to catch.
2. **`resample('W').ffill()` on the raw month-end series** — fills the *weeks
   before* publication with the not-yet-public value. Subtle leak.
3. **`bfill` or global-mean imputation** — pulls future info backward.
4. **Rolling/expanding stats computed on the full series, including the target
   row** — using `rolling(w).mean()` without the leading `shift(1)` (the helper
   does shift; a hand-rolled version often doesn't).
5. **`shift(1)` vs `shift(-1)` confusion** — features want `+k` (past); the target
   wants `-h` (future). A sign flip silently predicts the past.
6. **Target/horizon/baseline mismatch** — e.g. modeling a level but comparing to a
   zero-change baseline, or horizon in days vs the weekly spine's rows.
7. **Dropping the origin/target bookkeeping** after a merge that reorders/renames
   columns — must keep `forecast_origin`/`target_date`.
8. **No release lag at all** — treating "I lagged it 1 row" as sufficient without
   asking what was actually public.

## Assignment-specific hint strategy (L1→L2→L3)

Five key decision points. Always L1 first; stop when unblocked. Pure API/syntax
(merge_asof args, ffill call) = answer directly (type K).

**DP1 — Target definition (types D/E).**
- L1: "Write one sentence: 'I forecast [what] at [horizon] from [origin].' Does
  your `make_forward_target` call match that sentence?"
- L2: "Look at your `value_col`/`target_name` and `horizon` — horizon is in ROWS;
  on a weekly spine, is 1 the week you mean?"
- L3: "Level = target the price column; change = build `np.log(y).diff()` first
  then target THAT. Pick one and say which question it answers — you decide."

**DP2 — Release lag per fundamental (type A) — THE core decision.**
- L1: "At a Friday forecast origin, had this month's/week's figure already been
  published? When does the source actually release it?"
- L2: "Look at your merge: are you joining on the period the data *covers* or the
  date it became *public*? Build an `available_date = period_end + release_lag`."
- L3: "`right['available_date'] = right['date'] + pd.Timedelta(days=K)`; you set K
  from the source's real schedule (EIA storage ~5-7d; monthly balance ~6-8 weeks)
  and defend it."

**DP3 — Monthly → weekly broadcast (types A/C).**
- L1: "Your balance panel is monthly, your spine weekly. When you spread a month's
  number across its weeks, which weeks could legally see it?"
- L2: "A plain `resample('W').ffill()` fills the weeks *before* the release too —
  check the timing. Compare to what `merge_asof(direction='backward')` on the
  lagged available_date does instead."
- L3: "Set the monthly `available_date` to month-end + publication lag, then
  `merge_asof` backward; it broadcasts AND respects timing. You confirm no week
  sees a not-yet-published month."

**DP4 — Missing-value handling (type A).**
- L1: "For this gap, what value would you actually have known at that date?"
- L2: "Separate the two kinds of NaN: leading NaNs from lags/target (drop those
  rows) vs interior gaps in a fundamental (fill how?)."
- L3: "`ffill` uses only the past and is safe; `bfill`/global mean look forward.
  You choose per column and justify it."

**DP5 — Baseline choice (types B/H).**
- L1: "What is the cheapest no-model forecast for THIS target, and does the panel
  let you compute it?"
- L2: "Module 02's naive baselines — random walk for a level, zero-change for a
  change, seasonal-naive for a seasonal level. Which matches your target?"
- L3: "Random walk = `prediction = hh_price` (last level). Pick the one matched to
  your target, say why the others are wrong here, and report MAE/RMSE."

## Agent response pattern

1. Identify the highest-impact issue first (almost always a leakage/timing one).
2. Ask the learner to explain their assumption (release lag, target sentence).
3. Hint at the lowest useful level; answer pure API directly.
4. Re-run / re-check `target_date > forecast_origin` and the merge timing after
   the revision.
