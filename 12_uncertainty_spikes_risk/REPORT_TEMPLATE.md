# Report — Assignment 12: Uncertainty, Price Spikes, and Risk Metrics

## 1. Objective

In 2-4 sentences: which target you wrapped in an interval, which coverage level
you aimed for, and how you defined a "spike". State the forecast horizon and that
the test set is strictly later than the train set (no random split).

## 2. Vocabulary

Write each in your own words (1-2 sentences). Cross-check `docs/GLOSSARY_SEED.md` §10.

- **prediction interval:** A range [lo, hi] meant to contain the actual a stated
  fraction of the time; the honesty layer on top of a point forecast.
- **quantile forecast:** A forecast of a specific percentile (e.g. P90) of the
  outcome rather than its average; two quantiles bracket an interval.
- **pinball loss:** The asymmetric score that rewards a quantile forecast for
  landing at the right percentile; lower is better. (Say which direction it
  penalizes harder and why.)
- **coverage:** The out-of-sample fraction of actuals that fell inside your
  interval; the empirical check on the nominal level.
- **calibration:** Whether your stated level matches reality — an 80% interval is
  calibrated if ~80% of actuals fall inside AND it is not needlessly wide.
- **spike classification:** Turning the continuous price into a yes/no "spike"
  label via a threshold and scoring it with precision/recall.
- **threshold event:** The cutoff rule that defines a spike (a price quantile or a
  fixed $/MMBtu level); note that yours was set on TRAINING data only.
- **drawdown:** Peak-to-trough drop; a risk lens on how far the series fell from a
  recent high. (State if/how you used it.)

## 3. Data used

| Source / file | Frequency | Units | Date range | Why used |
|---|---:|---|---|---|
| `09_.../outputs/model_panel.csv` | weekly (W-FRI) | $/MMBtu (price), counts/anomalies (features) | e.g. 2018-01 to 2023-09 | leakage-safe panel: origin, target, features |

## 4. Data decisions

Describe: which column is the target and the point baseline you wrapped; the
train/test split point and why time-ordered; the nominal coverage level you chose
and why; the spike threshold definition and the EXACT statement of how it was
computed on `y_train` only (the leakage guard). Note any unit assumptions.

## 5. Outputs checklist

- [ ] `outputs/interval_forecasts.csv`
- [ ] `outputs/interval_metrics.csv`
- [ ] `outputs/spike_event_metrics.csv`
- [ ] `outputs/forecast_intervals.png`
- [ ] `REPORT.md`

## 6. Results

Fill the interval table (one row per method) and the spike table.

Interval metrics — example rows:

| method | nominal | coverage | avg_width | pinball_lo | pinball_hi |
|---|---:|---:|---:|---:|---:|
| naive_residual | 0.80 | 0.81 | 0.39 | — | — |
| gbr_quantile | 0.80 | 0.78 | 0.31 | 0.04 | 0.05 |

Spike metrics — example row:

| threshold | threshold_source | base_rate | precision | recall | tp | fp | fn | tn |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 4.46 | train_quantile_0.90 | 0.09 | 0.50 | 0.40 | 4 | 4 | 6 | 76 |

For each table add ONE sentence: what the numbers say AND what they do not say.

## 7. Interpretation

State plainly: (a) is your interval calibrated — coverage near nominal, width
reasonable? (b) did the fitted quantile interval beat the naive one, and on which
metric (coverage held while width shrank? lower pinball?) — and if it did NOT,
say so honestly. (c) For spikes: is a false alarm (FP) or a missed spike (FN)
worse for a gas desk, and does your threshold/predictor reflect that tradeoff?
Avoid causal language.

## 8. Model or analysis limitations

What could be wrong, incomplete, unstable, or leaked? Specifically: did your test
window even contain any spikes (rare events make recall noisy)? Is the single
holdout representative, or would a rolling backtest tell a different story? Would
the interval stay calibrated in a regime it never trained on (a supply shock)?

## 9. Next questions

List 3 concrete questions you would ask next (e.g. "does coverage hold under a
rolling-origin backtest?", "does a conformal interval beat both here?", "should
the threshold be operational rather than statistical?").
