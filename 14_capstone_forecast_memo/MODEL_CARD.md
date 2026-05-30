# Model Card — Henry Hub Forecast (Capstone)

A factual, one-page spec of the model. Fill every section; replace bracketed
prompts. A reviewer should be able to audit timing and trust from this alone.

## 1. Task

- **What it predicts (one sentence):** [I forecast ____ at ____ horizon from
  the ____ forecast origin.]
- **Intended use:** [e.g. weekly directional view for an analyst, NOT a trading
  signal]
- **Out of scope:** [what this model is NOT for]

## 2. Target definition

| Attribute | Value |
|---|---|
| Target variable | [e.g. next-week Henry Hub spot level] |
| Level / change / return | [pick one] |
| Units | [USD/MMBtu] |
| Frequency | [weekly] |
| Forecast origin | [the date the forecast is made — column `forecast_origin`] |
| Horizon | [e.g. 1 week = 1 panel row; column `horizon_steps`] |
| Target date column | [`target_date`] |

## 3. Features

EVERY feature needs source, unit, transform, and information-availability. The
availability lag must reflect real publication delay. Example rows included.

| Feature | Source | Unit | Transform | Available at origin? |
|---|---|---|---|---|
| hh_price_lag_1 | EIA NG.RNGWHHD.W | USD/MMBtu | lag 1 week | yes (own past) |
| storage_lag_Nw | EIA weekly storage | Bcf | lag N weeks for release delay | yes after publication lag |
| (every feature kept) | | | | |

## 4. Validation approach

- **Method:** walk-forward / rolling-origin (NOT a random split). [n_splits =
  ____ ; expanding or sliding window? justify]
- **Metric(s):** [RMSE/MAE + skill score vs baseline; why this metric matches the
  target]
- **Leakage controls:** [scaler/feature fit per fold; benchmark uses as-of join;
  rolling features shifted before the window]

## 5. Performance vs baselines

Out-of-sample numbers from `outputs/final_model_metrics.csv`. Example rows shown.

| Forecaster | RMSE | MAE | Skill vs persistence |
|---|---:|---:|---:|
| persistence (random walk) | [x.xx] | [x.xx] | 0.00 |
| seasonal-naive | [x.xx] | [x.xx] | [+/-] |
| futures benchmark (NYMEX C1) | [x.xx] | [x.xx] | [+/-] |
| final model | [x.xx] | [x.xx] | [+/-] |

- **Verdict:** [does the final model beat ALL three out of sample? by how much?]

## 6. Uncertainty

- **Interval level:** [e.g. 80%]
- **Construction:** [point +/- z * backtest residual std, or quantile model]
- **Empirical coverage (out of sample):** [measured fraction — should be ~level]

## 7. Limitations & failure modes

- **What would make this FAIL out of sample (required):** [name a specific regime
  shift / data-availability break / collinearity flip not in the training range]
- **Known weaknesses:** [thin data regimes, spike behavior, etc.]
- **Causality caveat:** drivers are *predictive*, not proven causal.

## 8. Maintenance plan

- **Retraining trigger:** [cadence or error-based rule]
- **Monitoring:** [live error vs baseline, input drift, data-availability checks]
- **Decommission condition:** [what would convince you to STOP using it]
