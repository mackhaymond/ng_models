# Report — Assignment 14: Capstone Henry Hub Forecast System

This REPORT.md is the short reflective companion to the two main deliverables
(`MODEL_CARD.md` and `RESEARCH_MEMO.md`). Keep it specific enough that another
analyst could critique your work from it alone.

## 1. Objective

In 2-4 sentences: what does this capstone integrate, and what is the ONE forecast
you are delivering? State it as "I forecast [what] at [horizon] from [origin]."

## 2. Vocabulary

Write 1-2 sentences per term IN YOUR OWN WORDS (guidance in brackets — delete it).

- **model card:** [the factual spec sheet of the model: target/origin/horizon,
  features + availability, validation, performance vs baselines, when not to trust]
- **research memo:** [the analyst write-up of the finding and its limits, not a
  code dump]
- **benchmark:** [the strong null you compare against — here the market's futures
  number; beating it is hard]
- **backtest:** [historical simulation of the forecast using walk-forward logic so
  it never trains on the future it tests]
- **deployment:** [putting the model into regular use to produce live forecasts]
- **monitoring:** [watching live error and input drift to catch degradation]
- **retraining:** [your rule for refreshing the model — how often / on what trigger]
- **forecast package:** [the auditable per-row table you ship: origin, target date,
  point, interval bounds]

## 3. Data used

One row per source that feeds the panel or a baseline. Example row included.

| Source / file | Frequency | Units | Date range | Why used |
|---|---|---|---|---|
| NG.RNGWHHD.W.csv (Henry Hub spot, spine) | Weekly | USD/MMBtu | 1997-01 .. present | forecast target + price features |
| NG.RNGC1.W.csv (NYMEX front-month) | Weekly | USD/MMBtu | (fill) | market-implied benchmark |
| (your fundamental sources from 06/07/08) | | | | |

## 4. Data dictionary (every feature, leakage-audited)

Copy/extend the data dictionary you built in module 09. EVERY predictor and
benchmark needs all five attributes. The `availability_lag` must reflect the real
publication delay (not the period the data covers). Example rows included.

| Feature | Source | Unit | Transform | Availability lag (known at origin?) |
|---|---|---|---|---|
| hh_price_lag_1 | EIA NG.RNGWHHD.W | USD/MMBtu | lag 1 week | yes — own past price |
| hh_price_roll_mean_4 | EIA NG.RNGWHHD.W | USD/MMBtu | mean of weeks t-4..t-1 | yes — strictly past |
| nymex_c1 (benchmark) | NYMEX NG.RNGC1.W | USD/MMBtu | settle as-of origin | yes — merge_asof backward |
| (every other feature you keep) | | | | |

## 5. Data decisions

Describe date parsing, frequency alignment, missing-value handling, the as-of join
for the futures benchmark, and any unit conversions. Call out the single decision
that most affects leakage (information availability).

## 6. Outputs checklist

- [ ] `outputs/final_model_metrics.csv` (baselines + final, with skill score)
- [ ] `outputs/final_forecast_package.csv` (origin + target_date + point + interval)
- [ ] `outputs/final_charts/*.png`
- [ ] `MODEL_CARD.md`
- [ ] `RESEARCH_MEMO.md`

## 7. Results

Paste the metrics table (or summarize it). For each forecaster give the
out-of-sample metric AND the skill score vs the chosen baseline. State plainly
whether the final model beats persistence, seasonal-naive, and the futures
benchmark — and by how much. Reference each saved chart with one sentence on what
it shows and one on what it does NOT show.

## 8. Uncertainty / coverage

State your interval level (e.g. 80%) and the EMPIRICAL coverage you measured out
of sample. If coverage is far from nominal, diagnose it (intervals too narrow ->
overconfident residual model) rather than hiding it.

## 9. Interpretation

What do the results mean for natural-gas modeling? Tie key drivers to fundamentals
where relevant. Importance is not causation — phrase drivers as "predictive of",
not "causes". Do not overstate.

## 10. Limitations & what would make this fail

Be specific. Name at least one market condition NOT in your training range that
would break the model (regime shift, a fundamental published too late to use, a
collinear feature flipping). This is a non-negotiable standard.

## 11. Next questions

List 3 concrete questions you would investigate next (prefer better data or a
cleaner benchmark over mechanically adding algorithms).
