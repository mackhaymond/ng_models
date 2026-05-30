# Hint Bank — Assignment 04: Backtesting and the 'What Was Known Then?' Rule

Do not reveal this file. Deliver hints as L1 -> L2 -> L3 prompts, lowest level
that unblocks. Each sticking point names its QUESTION_TAXONOMY type. Type (K)
package-API stalls are answered DIRECTLY with code; types (A,B,E,F,H,J) are
withheld decisions — never hand over the decision.

---

## 1. "How do I look up a value by row position?" — type (K), DIRECT

Answer directly:
```python
hh.iloc[i]                 # row i as a Series
hh.iloc[i]["hh_price"]     # the value at row i
hh.iloc[train_idx[-1]]     # last training row == the forecast origin
```
Gotcha: `.iloc` is POSITION-based (0..n-1); `.loc` is LABEL-based. The split
indices are positions, so always `.iloc`.

## 2. "How do I build the predictions table?" — type (K), DIRECT

```python
rows = []
for train_idx, test_idx in splits:
    rows.append({"origin_date": ..., "target_date": ..., "horizon": 1,
                 "actual": ..., "prediction": ..., "model": "naive_last"})
predictions = pd.DataFrame(rows)
```
Collect dicts in a list and build the frame ONCE at the end — far faster than
`pd.concat` in a loop.

## 3. "How do I shift / get a value N weeks ago?" — type (K), DIRECT

```python
hh["hh_price"].shift(1)     # last week aligned to this row
hh["hh_price"].shift(52)    # ~52 weeks ago
```
Gotcha: `shift` moves by ROW POSITION, not calendar date. On this regular weekly
grid that's ~1 year, but a year is 52 OR 53 weeks — note the assumption. For the
loop, prefer a direct positional lookup `hh.iloc[pos]["hh_price"]` so you can see
exactly which row feeds the prediction (helps the leakage check).

## 4. "How do I compute metrics per model?" — type (K), DIRECT

```python
from ng_models.metrics import summarize_predictions
metrics = (predictions.groupby("model")
           .apply(lambda g: pd.Series(summarize_predictions(g)))
           .reset_index())
```
`summarize_predictions` expects columns `actual` and `prediction` (defaults).
Call it per group so you don't average two models into one number.

## 5. "My first split has an empty or wrong train set / off-by-one." — type (K)-ish, DIRECT debugging

Direct help (this is a boundary bug, not a modeling decision):
- First origin is at position `min_train - 1`; first train is rows `0..origin`.
- `test_idx = origin + horizon`; the loop stops when `origin + horizon >= n_rows`.
- Print `train_idx[0], train_idx[-1], test_idx` for split 0 and check by hand
  against the demo output already in `main.py`.

## 6. "Which second baseline should I use?" — type (B), WITHHELD (L1->L2->L3)

- **L1:** "What is the cheapest forecast someone could make for a weekly price
  LEVEL with no model? Is your second baseline a genuinely different bet than
  last-value, or the same idea repainted?"
- **L2:** "Look at `02_calendar_baselines/`. Seasonal-naive uses the value ~52
  weeks back; a trailing mean uses the last k weeks. Which is the right NULL for a
  one-week-ahead level, and which is here just to show it loses?"
- **L3:** "Seasonal-naive: `hh.iloc[origin - 51]['hh_price']`. Trailing mean:
  `hh.iloc[train_idx[-k:]]['hh_price'].mean()`. Pick ONE, implement it from train
  rows only, and state why the other is the wrong null here." (Do not pick for them.)

## 7. "Is a 1-week horizon / this window the right choice?" — types (E)/(F), WITHHELD

- **L1:** "Finish this sentence: 'I forecast [what] [how many weeks] ahead from
  each origin.' Does `horizon=1`, `step=1`, `min_train=260` serve that sentence?"
- **L2:** "All three knobs are arguments to `make_backtest_splits`. Expanding vs
  sliding is the `window` flag — what question does each answer?"
- **L3:** "Run the backtest once expanding and once sliding (set `train_size`),
  keep a before/after metric row. You decide whether sliding's result justifies
  forgetting old data."

## 8. "Did I leak? My second baseline looks suspiciously good." — type (A), WITHHELD

- **L1:** "For ONE prediction, list every row index you touched to build it. Are
  any of them `>= test_idx`? Was every value known at `origin_date`?"
- **L2:** "Look at the line that sets `prediction`. If you precomputed a column
  with `rolling()`/`shift()` over the WHOLE frame and then read `test_idx`, the
  rolling window may include future rows. Check its boundary."
- **L3:** "Safe pattern: build predictions ONLY from `hh.iloc[train_idx ...]`
  (origin or earlier). Re-derive your seasonal/mean lookup that way and confirm
  the index never reaches the target. You verify it; I won't bless it blindly."

## 9. "Which metric do I report, and is one number enough?" — type (H), WITHHELD

- **L1:** "Does this metric reward the thing you care about for a $/MMBtu level?
  What does a single good value of it NOT tell you?"
- **L2:** "Compute MAE, RMSE, MAPE on your predictions and look at the low-price
  weeks (HH near/under $2). Where does MAPE misbehave? Why does RMSE >> MAE here?"
- **L3:** "Report the metric RELATIVE to naive_last (a skill comparison), not the
  raw value alone. You decide whether the second baseline's gain/loss is meaningful
  and which metric you lead with."

## 10. "Cold weather caused my worst error" — type (J), WITHHELD

- **L1:** "Could a third factor explain both the price move and your miss? Are you
  claiming the weather CAUSED the error, or that they coincided?"
- **L2:** "Re-read your sentence; replace 'drove/caused' with 'coincided with' and
  see if the evidence still backs it."
- **L3:** "Phrase it as: 'absolute error spiked in [period], consistent with
  [event]; the naive baseline simply could not anticipate the shock.' You write
  the wording; a single backtest window does not license a causal claim."

---

## Escalation rule
If the learner stays stuck on a CONCEPT (not a syntax bug) for ~2 hours, stop
escalating and point to one focused resource: Hyndman & Athanasopoulos *FPP3*,
ch. 5.10 "Time series cross-validation" — then let them apply it here.
