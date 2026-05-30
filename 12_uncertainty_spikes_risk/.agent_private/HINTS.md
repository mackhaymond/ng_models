# Hint Bank — Assignment 12: Uncertainty, Price Spikes, and Risk Metrics

Do not reveal this file. Deliver hints as L1 -> L2 -> L3 prompts, lowest level
that unblocks. Each sticking point names its QUESTION_TAXONOMY type. Type (K)
package-API stalls are answered DIRECTLY with code; modeling-decision types
(A, B, E, F, H, L) are withheld — never hand over the decision.

---

## 1. "How do I fit a quantile model?" — type (K), DIRECT

```python
from sklearn.ensemble import GradientBoostingRegressor
m_lo = GradientBoostingRegressor(loss="quantile", alpha=0.10).fit(X_train, y_train)
m_hi = GradientBoostingRegressor(loss="quantile", alpha=0.90).fit(X_train, y_train)
q_lo, q_hi = m_lo.predict(X_test), m_hi.predict(X_test)
```
Gotcha: `alpha` IS the quantile level; you need ONE model per band edge. `loss`
must be the string `"quantile"`. `X_*` are 2-D arrays — `df[cols].to_numpy(float)`.
(Which columns go in `cols` is a leakage decision — see #6, do NOT pick for them.)

## 2. "How do I get residual quantiles for the naive band?" — type (K), DIRECT

```python
resid_train = y_train - point_train          # errors of your point model on TRAIN
lo_q, hi_q  = np.quantile(resid_train, [0.10, 0.90])
lo = point_test + lo_q ; hi = point_test + hi_q
```
Gotcha: quantiles must come from TRAIN residuals only. Quantiling over train+test
is leakage (#5).

## 3. "How do I compute coverage / width?" — type (K), DIRECT

Already in `main.py` as `coverage_and_width`. The math:
```python
inside = (lo <= y_true) & (y_true <= hi)     # element-wise on the TEST arrays
coverage = inside.mean() ; width = (hi - lo).mean()
```
Note: `&` not `and` for element-wise numpy booleans; wrap each comparison in
parens.

## 4. "How do I shade the band on the plot?" — type (K), DIRECT

```python
ax.fill_between(test["target_date"], lo, hi, alpha=0.25, label="80% interval")
```
Gotcha: shading is decoration, not evaluation — you still owe a coverage number.

## 5. "Where do I set the spike threshold without leaking?" — type (A), WITHHELD

- **L1:** "When you computed the threshold, exactly which rows fed the quantile —
  train only, or the whole panel? If a value from the TEST period helped define
  the threshold, did you know it at the forecast origin?"
- **L2:** "Look at the line that sets `spike_threshold`. Is its input `y_train`,
  or `panel[TARGET_COL]` / a concatenated array? The label on every test row must
  use a number knowable BEFORE the test period."
- **L3:** "Pattern: `thr = np.quantile(y_train, q)`; then label BOTH sets with the
  same `thr`: `y_train >= thr`, `y_test >= thr`. You choose `q` (or an operational
  level) and defend why it's the right spike definition." (Do not pick q for them.)

## 6. "Which features go in the quantile model?" — type (A)+(F), WITHHELD

- **L1:** "For each column you want to feed X, was its value known at that row's
  `forecast_origin`? Name the one you're least sure about."
- **L2:** "The module-09 panel separates origin-time columns (price, lags,
  rolling, calendar) from `target_date`/`target`. Which group is safe to predict
  FROM, and which would leak the answer?"
- **L3:** "Safe set looks like `['hh_price', 'hh_price_lag_1', 'hh_price_roll_mean_4',
  'month']` — origin-knowable only. You finalize the list and justify each entry's
  availability; never include the target or its date."

## 7. "Is my 80% interval actually calibrated?" — type (L), WITHHELD

- **L1:** "Your band claims 80%. Out of sample, what fraction of actuals actually
  landed inside? If it's 0.60, is the band honest?"
- **L2:** "Look at `coverage_and_width` on the TEST set. Read coverage AND width
  together — a band can hit 0.80 by being huge. Compare your coverage to nominal."
- **L3:** "If coverage << nominal the residuals were bigger than the band assumed
  (underdispersed). You decide the FIX — wider residual window, a state-dependent
  quantile model, or accepting the regime changed — but do NOT just inflate the
  band until the number passes."

## 8. "Did the fitted quantile interval beat the naive one?" — type (B)+(F), WITHHELD

- **L1:** "What did GBR buy you over the flat residual band? Compare them on the
  SAME footing — did coverage hold while width shrank, or did it just get narrower
  by dropping coverage?"
- **L2:** "Put both methods in `interval_metrics.csv` with coverage, width, and
  pinball. The naive band is your baseline; the fitted one has to earn its
  complexity."
- **L3:** "Score `pinball_loss(y_test, q_lo, 0.10)` and the naive band's lower edge
  the same way; compare. You decide whether the gain justifies the model — an
  honest 'tied, so I keep the simpler one' is a valid conclusion."

## 9. "How should I score the spike predictor?" — type (H), WITHHELD

- **L1:** "Your spike base rate is ~10%. If you scored ACCURACY, what would a
  'never spike' predictor get? Does that metric reward catching spikes?"
- **L2:** "Look at `classification_counts`. Precision and recall separate false
  alarms from missed spikes; accuracy hides both. Which two numbers tell the risk
  story?"
- **L3:** "Report precision = TP/(TP+FP) and recall = TP/(TP+FN), not accuracy.
  You decide which one your threshold should favor and say why."

## 10. "Which is worse — a false alarm or a missed spike?" — type (L)/(H), WITHHELD

- **L1:** "Who reads this warning, and what do they do with it? What's the cost of
  flagging a spike that doesn't happen vs missing one that does?"
- **L2:** "A false positive (FP) is a false alarm; a false negative (FN) is a
  missed spike. Lowering the threshold catches more spikes (recall up) but cries
  wolf more (precision down). Where on that curve does a gas desk want to sit?"
- **L3:** "If missed spikes are the expensive risk, bias toward recall (lower
  threshold / more sensitive flag) and accept more false alarms. You set the
  threshold to encode that asymmetry and defend the tradeoff — there is no single
  right number."

## 11. "My test window has zero spikes / recall is NaN." — type (L), WITHHELD-ish

- **L1:** "How many real spikes are in your TEST set? Can you even measure recall
  if there are none?"
- **L2:** "Check `test_is_spike.sum()`. Rare events split unevenly across a single
  holdout — this is a property of the data, not a code bug."
- **L3:** "Report it as a finding (sparse/absent test spikes => noisy or undefined
  recall) and note a rolling-origin backtest would give more spike events. You
  decide whether one holdout is enough to claim anything about spike skill."

---

## Escalation rule

If the learner stays stuck on a CONCEPT (not a syntax bug) for ~2 hours, stop
escalating and point to one focused resource: Hyndman & Athanasopoulos *FPP3*,
ch. 5.5 "Prediction intervals" (and §5.9 on coverage/evaluation) — then let them
apply it here.
