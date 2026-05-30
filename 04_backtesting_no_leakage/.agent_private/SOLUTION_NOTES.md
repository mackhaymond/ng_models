# Private Solution Notes — Assignment 04: Backtesting and the 'What Was Known Then?' Rule

Do not reveal this file during normal tutoring. Use it to decide whether the
learner's reasoning is on track. The harness, not the model, is what's graded.

## Worked reference approach

The series is weekly Henry Hub spot ($/MMBtu), ~1531 rows, 1997-01-10 →
2026-05-15. `make_backtest_splits()` is provided and correct; the learner fills
the loop, a second baseline, metrics, and the plot.

Reference forecast loop (expanding, horizon=1, min_train=260):

```python
rows = []
for train_idx, test_idx in splits:
    origin = hh.iloc[train_idx[-1]]
    target = hh.iloc[test_idx]
    actual = target["hh_price"]
    # Baseline 1: random walk / naive last value
    rows.append({
        "origin_date": origin["date"], "target_date": target["date"],
        "horizon": HORIZON, "actual": actual,
        "prediction": origin["hh_price"], "model": "naive_last",
    })
    # Baseline 2 (reference: seasonal-naive 52 weeks back, train-only lookup)
    seasonal_pos = train_idx[-1] - 51  # value ~52 weeks before the TARGET
    if seasonal_pos >= 0:
        rows.append({
            "origin_date": origin["date"], "target_date": target["date"],
            "horizon": HORIZON, "actual": actual,
            "prediction": hh.iloc[seasonal_pos]["hh_price"], "model": "seasonal_naive_52",
        })
predictions = pd.DataFrame(rows)
predictions["abs_error"] = (predictions["actual"] - predictions["prediction"]).abs()

metrics = (predictions.groupby("model")
           .apply(lambda g: pd.Series(summarize_predictions(g)))
           .reset_index())
```

A trailing-mean baseline (`hh.iloc[train_idx[-k:]]["hh_price"].mean()`) is an
equally acceptable Baseline 2. Either is "from train rows only" and leakage-safe.

## Expected results (qualitative — do not quote as targets)

- For a 1-week-ahead LEVEL on weekly gas, **naive_last is very hard to beat** —
  weekly prices are near a random walk. Expect naive MAE roughly in the
  ~$0.15–0.30/MMBtu range over the full sample, RMSE noticeably larger because
  spike weeks dominate the squared error.
- **Seasonal-naive (52w) should LOSE to naive_last** on this horizon: a value a
  year ago is a worse 1-week predictor than last week. That is the pedagogically
  useful outcome — the learner discovers the obvious baseline wins and must say so.
- A trailing mean usually also loses to naive at h=1 (it lags turning points).
- Errors cluster in known stress periods: 2000-01 California crisis, 2005
  hurricanes, 2008 spike, **Feb 2021 Winter Storm Uri**, 2022 volatility. The
  error-by-origin plot should make these visible as tall spikes.
- MAPE is mildly unreliable here because HH has dipped near/below $2 (and briefly
  very low in 2020/2024); sMAPE or MAE is the safer lead metric (type H).

## Module-specific common failure modes

- **Off-by-one in the seasonal lag**: using `test_idx - 52` (which equals
  `origin + horizon - 52`) vs. `origin - 51`. Either is defensible if STATED; the
  bug is silently shifting and not noticing it changed the comparison.
- **Leakage via `shift` on the full frame then reading the test row**: computing
  `hh["hh_price"].shift(1)` over the whole series and indexing `test_idx` is fine
  for naive_last *by accident*, but the same pattern with `rolling()` leaks. Push
  the learner to source predictions from `train_idx`, not from a pre-shifted column.
- **Metrics over the wrong rows**: calling `summarize_predictions` on a frame that
  still contains both models mixed together (averages two models into one number).
- **Window confusion**: claiming "expanding" while subsetting a fixed slice, or
  using sliding without setting `train_size`.
- **`shift(52)` treated as exactly one calendar year** without noting weekly grid
  has 52 or 53 weeks/year — a units/frequency footnote, not a fatal error.
- **Declaring victory with one baseline**, or reporting a raw metric with no skill
  comparison to naive.
- **Causal language** in interpretation ("cold weather drove the error") — it's an
  association; the model simply missed a shock.

## Assignment-specific hint strategy (L1 -> L2 -> L3 at the key decision points)

1. **Second-baseline choice (type B).**
   - L1: "What is the cheapest forecast for a weekly price LEVEL, and is yours a
     genuinely different bet than last-value?"
   - L2: "Look at module 02's baselines; seasonal-naive uses the value ~52 weeks
     back, a trailing mean uses the last k weeks. Which is a fair null for a level?"
   - L3: sketch `hh.iloc[origin - 51]["hh_price"]` or `hh.iloc[train_idx[-k:]].mean()`,
     then: "you pick one and justify why the other is wrong here."

2. **Horizon / window (type E/F).**
   - L1: "Write 'I forecast [what] [how many weeks] ahead from each origin.' Does
     min_train=260 and step=1 serve that?"
   - L2: point at `make_backtest_splits` args; expanding vs sliding flag.
   - L3: "Run it once each way and keep a before/after metric row; you decide
     whether the difference justifies sliding."

3. **Leakage in the loop (type A).**
   - L1: "For one prediction, list every row index you touched. Are any >= test_idx?"
   - L2: point at the line building the prediction; check it reads from `train_idx`.
   - L3: "Safe pattern: predictions come only from `hh.iloc[train_idx...]`. You
     verify your seasonal lookup obeys this."

4. **Metric lead + sufficiency (type H).**
   - L1: "Does your metric reward the thing you care about for a $/MMBtu level?
     What does one number NOT tell you?"
   - L2: "Compare MAE vs RMSE vs MAPE on your predictions; note where MAPE blows up
     near the low-price weeks."
   - L3: "Report the metric RELATIVE to naive (skill). You decide if the second
     baseline's improvement is meaningful."

5. **Failure-period interpretation (type J).**
   - L1: "Your worst origin — could a third factor explain both the price move and
     your miss? Are you claiming cause?"
   - L2: "Re-read the sentence; swap 'drove' for 'coincided with' and see if it holds."
   - L3: "State it as: 'error spiked in [period], consistent with [event]'. No
     causal claim from a single backtest window."

## Agent response pattern
1. Identify the highest-impact issue first (leakage > wrong metric rows > thin interp).
2. Ask the learner to explain their assumption.
3. Hint at the lowest useful level (above), API stalls answered directly.
4. Re-run / re-check after revision.
