# Assignment 12: Uncertainty, Price Spikes, and Risk Metrics

**Phase:** Advanced Modeling
**Level:** Advanced
**Estimated time:** 10-16 hours

## What you're building

Every model so far gave you a single number per forecast. That is silently
overconfident — it never says how wrong it could be. Here you do two things:

1. Turn point forecasts into **prediction intervals** ([lo, hi] bands) and
   then HONESTLY check them: how often did the actual land inside, and how wide
   did you have to be.
2. Add a **spike** view: a price spike is a rare, large event. You define a
   threshold, label rows spike/no-spike, and score it as a classification
   problem (precision / recall) — because the moves that matter most for risk
   are exactly the ones an RMSE model smooths away.

## Data scope

Single required input, produced by module 09:

- `09_feature_table_leakage/outputs/model_panel.csv` — the leakage-safe
  model-ready panel. Each row already carries `forecast_origin`, `target_date`,
  the future-value target (`target_hh_next` in the module-09 starter), the
  origin-time price (`hh_price`), and leakage-safe lag/rolling/calendar features.

If that file is missing, `main.py` prints "complete module 09 first" and exits
cleanly. **Run module 09 before this one.** You do not need any new raw data.

## Concepts you'll use

Read these ground-up before coding. Cross-reference `docs/GLOSSARY_SEED.md`
section 10 ("Uncertainty, intervals & risk").

- **Prediction interval.** Instead of one number, a range [lo, hi] that is
  *meant* to contain the actual a stated fraction of the time. An "80% interval"
  claims the truth lands inside 80% of the time. The point forecast is your best
  guess; the interval is your honesty about how unsure you are.
- **Quantile forecast.** A forecast OF a specific percentile of the outcome, not
  the average. The 10th-percentile forecast is a value the actual should fall
  below only ~10% of the time. Stack two quantiles (P10 and P90) and the gap
  between them IS an 80% prediction interval.
- **Pinball / quantile loss.** The score that rewards a quantile forecast for
  hitting the right percentile. It punishes under- and over-shooting by
  DIFFERENT weights: for the 90th percentile it penalizes coming in too low much
  harder than too high, which pushes the forecast up to where only ~10% of
  outcomes exceed it. Plain MAE/RMSE cannot do this — they only reward the
  middle. Lower pinball is better.
- **Empirical coverage.** The reality check: the fraction of actuals that
  *actually* fell inside your interval, measured OUT OF SAMPLE. If your "80%"
  interval only covers 60%, it is too narrow (overconfident). Worked coverage
  example: you make 50 test forecasts with 80% intervals; the actual lands inside
  41 of them. Empirical coverage = 41/50 = 0.82, close to the nominal 0.80 — that
  interval is roughly honest. If it had landed inside only 30 (0.60), the band is
  underdispersed and you should NOT just paint it wider until it passes — you
  should understand why your residuals were bigger than the band assumed.
- **Calibration.** Being right about how often you're right. A well-calibrated
  80% interval has ~80% empirical coverage AND is no wider than it needs to be. A
  band that covers 100% by being absurdly wide is useless even though coverage
  "looks great" — that is why you always report coverage AND average width
  together.
- **Spike / threshold event.** A discrete event defined by a cutoff: "the price
  was a spike if it exceeded THRESHOLD." Turning a continuous price into a yes/no
  label lets you ask a different question (did a dangerous move happen?) and score
  it with precision/recall instead of RMSE.
- **Precision vs recall (for spikes).** Precision = of the rows you flagged as
  spikes, how many really were (low precision = many false alarms). Recall = of
  the real spikes, how many you caught (low recall = many missed spikes). A
  **false positive** is a false alarm; a **false negative** is a missed spike.
  Which is worse is a risk judgment you must make and defend.
- **Drawdown.** The peak-to-trough drop in a series — a risk lens on how far
  something fell from its recent high. (Optional here; mentioned for the report
  vocabulary.)

### The one leakage trap to internalize

**The spike threshold must be computed from TRAINING data only.** If you set the
threshold using the whole sample (train + test), your test labels were defined
using knowledge of the future test distribution — that is leakage, and it makes
your spike detector look better than it could ever be in real life. Compute the
threshold on `y_train`, then apply that same fixed number to label both train and
test. The starter does this; do not "improve" it by using the full sample.

## Package guide

Concrete minimal snippets for the libraries this module needs. The interval
metrics (`coverage_and_width`, `pinball_loss`, `classification_counts`) are
already implemented in `main.py` — read them, you must be able to explain each.

**Naive interval from residual quantiles (numpy):**
```python
resid_train = y_train - point_train          # training-set errors of a point model
lo_q, hi_q  = np.quantile(resid_train, [0.10, 0.90])   # 80% band edges
lo = point_test + lo_q                        # bolt the residual spread onto
hi = point_test + hi_q                        # each test point forecast
```

**Fitted quantile interval (scikit-learn):**
```python
from sklearn.ensemble import GradientBoostingRegressor
# alpha IS the quantile level. Fit ONE model per band edge.
m_lo = GradientBoostingRegressor(loss="quantile", alpha=0.10).fit(X_train, y_train)
m_hi = GradientBoostingRegressor(loss="quantile", alpha=0.90).fit(X_train, y_train)
q_lo = m_lo.predict(X_test)
q_hi = m_hi.predict(X_test)
# X_train / X_test are 2-D arrays of your chosen LEAKAGE-SAFE feature columns.
```

**Coverage (the formula behind the helper):**
```python
inside   = (lo <= y_true) & (y_true <= hi)    # element-wise boolean array
coverage = inside.mean()                       # fraction True == empirical coverage
width    = (hi - lo).mean()                    # average band width
```

**Train-only spike threshold + leakage-safe labels (numpy):**
```python
spike_threshold = np.quantile(y_train, 0.90)   # learned on TRAIN ONLY
train_is_spike  = y_train >= spike_threshold    # same fixed number applied to both
test_is_spike   = y_test  >= spike_threshold
```

**Time-ordered split (NEVER random for time series):**
```python
cut   = int(len(panel) * 0.7)
train = panel.iloc[:cut]      # earlier rows
test  = panel.iloc[cut:]      # strictly later rows
```

## Tasks

Work through the lettered TODOs in `main.py` (A = naive interval, B = fitted
quantile interval, C = spike events).

1. **Naive prediction interval** from historical residual quantiles (Part A is
   wired; you choose the point baseline and the nominal coverage level).
2. **Fitted quantile interval** with `GradientBoostingRegressor(loss="quantile")`
   (Part B; you choose the leakage-safe feature set, fit both edges, and compare
   width/coverage/pinball against the naive band).
3. **Spike threshold** set on TRAINING data only — a statistical quantile or an
   operational $/MMBtu level (Part C; you justify the definition).
4. **Evaluate** coverage, average width, pinball loss, and spike
   precision/recall. Beat at least one baseline: the fitted interval should be
   narrower than the naive one at comparable coverage, or you must explain why
   not.
5. **Risk memo** in `REPORT.md`: what the model can and cannot warn about.

## Deliverables

- `outputs/interval_forecasts.csv` — one row per test forecast with
  `forecast_origin`, `target_date`, `actual`, `point_forecast`, band edges, and
  spike columns.
- `outputs/interval_metrics.csv` — coverage / width / pinball per interval method.
- `outputs/spike_event_metrics.csv` — threshold + precision/recall/counts.
- `outputs/forecast_intervals.png` — actual vs interval band with the threshold.
- `REPORT.md` — from `REPORT_TEMPLATE.md`.

## Rules (non-negotiable standards)

- Keep raw data immutable; save generated files under this assignment's
  `outputs/`.
- Every forecast row carries `forecast_origin` AND `target_date`.
- No random splits — the test set is strictly later than train.
- No leakage: the spike threshold and every feature use only what was known at
  the forecast origin.
- Beat at least one baseline (naive interval is the baseline for the fitted one).
- A chart is not enough. Every chart and metric needs a sentence on what it shows
  AND what it does not show.
- No causal claims from correlation. State what would make the model fail.

## Questions to answer in `REPORT.md`

- What is the target, and what is the spike threshold (and how did you set it
  WITHOUT leakage)?
- What dates and units are involved?
- Is your 80% interval actually ~80% covered out of sample? Is it well calibrated?
- Did the fitted quantile interval beat the naive one? On what metric?
- For spikes, is a false alarm or a missed spike worse here — and does your
  threshold reflect that?
- What would you not trust yet, and what would make this model fail?
