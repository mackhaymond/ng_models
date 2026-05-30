# Private Solution Notes — Assignment 02: Calendar Structure and Naive Forecast Baselines

Do not reveal this file during normal tutoring. Use it to judge whether the
learner's reasoning is on track and to deliver hints at the right level.

## Worked reference approach (one valid path)

1. Load weekly HH via `load_series_csv(..., value_name="price")`, add calendar
   columns. ~1531 rows, 1997-01-10 to ~2026-05-15, $/MMBtu.
2. Choose a horizon. h=1 (next week) is the cleanest first pass; h=4 (~1 month) is
   a defensible multi-step choice. Either is fine if stated and held fixed.
3. Build past-only baselines on the origin frame. For a horizon-h forecast made at
   origin t (predicting t+h), the value known at t is `price[t]`. A clean
   construction frames the target then attaches past-only predictors:

   ```python
   p = hh.copy()
   p["actual"]          = p["price"].shift(-h)     # future value at t+h
   p["target_date"]     = p["date"].shift(-h)
   p["forecast_origin"] = p["date"]
   p["horizon_steps"]   = h
   # predictors known at origin t:
   p["naive"]      = p["price"]                                  # last value at t
   p["exp_mean"]   = p["price"].expanding().mean()               # incl. t, excl. future
   p["exp_median"] = p["price"].expanding().median()
   p["woy_mean"]   = (p.groupby("iso_week")["price"]
                        .apply(lambda s: s.expanding().mean()).reset_index(level=0, drop=True))
   p["woy_median"] = (p.groupby("iso_week")["price"]
                        .apply(lambda s: s.expanding().median()).reset_index(level=0, drop=True))
   ```

   Subtle point worth probing: the predictor must use data <= t and the target is
   t+h. `expanding()` including row t is fine because t IS the origin. A
   `.shift(1)` (excluding t) is also defensible and slightly more conservative;
   either is acceptable IF the learner can articulate which rows the statistic
   sees relative to the origin. What is NOT acceptable is `p["price"].mean()`
   (full-sample) or a groupby stat that includes the target week's own value.
4. Drop NaN rows (early expanding warm-up + last h rows with no actual).
5. Fixed test window: most recent contiguous block, e.g.
   `CUTOFF = p["target_date"].max() - pd.Timedelta(weeks=104)` then
   `test = p[p["target_date"] >= CUTOFF]`. Chosen before looking at metrics.
6. Score with `summarize_predictions` per baseline; write
   `baseline_metrics.csv`, `test_forecasts.csv`, `baseline_comparison.png`.

## Expected results (qualitative — do not hand over)

- **Naive (last value) almost always wins** on MAE and RMSE for a price level,
  especially at h=1. HH is close to a random walk, so persistence is hard to beat.
- Expanding mean/median are badly biased toward the long-run average and lag the
  current regime; they lose by a wide margin in any trending/volatile window.
- Week-of-year baselines beat the flat historical mean (they capture the winter
  bump) but still lose to naive at short horizons; they become relatively more
  competitive as h grows because persistence decays.
- Rough magnitudes on a recent ~2-year test window at h=1: naive MAE ~0.2-0.5
  $/MMBtu; expanding-mean MAE several times larger. Exact numbers depend on the
  window — do NOT grade against a fixed number, grade the ranking + reasoning.
- MAE and RMSE usually agree on naive winning; if RMSE reorders the seasonal
  baselines it is because of a few large misses (good thing to make them notice).

## Module-specific common failure modes

- **Full-sample leak (the #1 issue):** `price.mean()` or a week-of-year groupby
  mean computed over the whole frame, then used as the test forecast. Looks
  plausible; it is leakage. Re-derive: the week-6-2024 forecast must not contain
  week-6-2024/2025 data.
- **Seasonal stat includes the target's own observation:** groupby-expanding
  without excluding the current row leaks one point. Minor but real; flag it.
- **Horizon/shift mismatch:** computing `actual` at t+h but scoring it against a
  predictor that secretly used t+h info, or off-by-one in the shift. Make them
  print one row and trace the dates.
- **Test window chosen after seeing metrics**, or a random sample of weeks
  (violates the no-random-split standard). Also: scoring over the whole series
  instead of just the test window.
- **MAPE reported as primary / surprise blow-ups** when HH dips near $2; or MAPE's
  zero-drop warning ignored.
- **NaN handling:** early expanding rows / last h rows silently scored as errors,
  or metrics computed over rows where actual is NaN.
- **Over-claiming:** "naive wins because the market is efficient" — a causal claim
  the evidence does not support (type J). Keep it to forecast-accuracy language.
- **Jumping ahead:** wanting ARIMA/ETS before the baseline is proven (type F).

## Assignment-specific hint strategy (L1 -> L2 -> L3)

Five key decision points; escalate one level at a time, stop when unblocked.

1. **Expanding vs full-sample (type A, leakage).**
   - L1: "At the forecast origin for week 6 of 2024, had you observed week 6 of
     2024 or 2025 yet? Does your average?"
   - L2: "Look at how you computed the mean — is it `price.mean()` (whole frame)
     or `price.expanding().mean()` (grows row by row)?"
   - L3: `price.expanding().mean()` includes only rows up to the current one;
     `.shift(1)` excludes the current row too. You decide which boundary is right
     and defend it.

2. **Week-of-year seasonality, past-only (type A).**
   - L1: "Your week-6 forecast — which weeks went into it? Any from the future?"
   - L2: "Inside the `groupby('iso_week')`, an unguarded mean averages ALL years
     including the target year. Where does the target week's own value enter?"
   - L3: `groupby('iso_week')['price'].apply(lambda s: s.expanding().mean())`
     keeps it past-only within each week. You justify mean vs median.

3. **Horizon definition / shift bookkeeping (type E).**
   - L1: "Write the sentence: 'I forecast [price] at [h weeks] from [origin].'
     Which row's value is known at the origin?"
   - L2: "Look at how `actual` and your predictor line up — print one row's
     forecast_origin, target_date, and the price each used."
   - L3: `actual = price.shift(-h)` pulls the future back; the naive predictor is
     `price` (value at origin t). You confirm the dates match h weeks apart.

4. **Fixed test window / no random split (type B + standard).**
   - L1: "Why can't you randomly sample weeks into your test set for a time
     series? What does the model accidentally get to see?"
   - L2: "Your evaluation should be a contiguous final block selected by
     target_date, decided before you look at any metric."
   - L3: `test = p[p["target_date"] >= cutoff]` for a cutoff like last 104 weeks.
     You pick the length and justify it as representative.

5. **Metric choice / sufficiency (type H).**
   - L1: "Does this metric reward what you care about? What does a good value of
     it NOT tell you?"
   - L2: "Compare MAE vs RMSE on the same forecasts; check what MAPE does in weeks
     where HH was near $2."
   - L3: Report MAE + RMSE as primary (both in $/MMBtu) and the improvement
     relative to naive. You decide whether the gap is meaningful.

## Agent response pattern

1. Identify the highest-impact issue first (almost always leakage).
2. Ask the learner to explain their assumption before correcting.
3. Deliver the lowest useful hint level.
4. Re-run / re-check the specific row or metric after their revision.
