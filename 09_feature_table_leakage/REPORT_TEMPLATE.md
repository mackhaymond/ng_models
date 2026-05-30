# Report — Assignment 09: Feature Engineering and the Model-Ready Panel

## 1. Objective

In 2-4 sentences, explain what this assignment builds and why it matters. Name
the panel's spine, the target you chose, and the forecast horizon.

## 2. Vocabulary

Write 1-2 sentences each, in your own words (cross-check `docs/GLOSSARY_SEED.md`).

- **feature table / model matrix:** The one table where each row = one observation and each column = one predictor, plus the target column.
- **target leakage:** Using information on a row that was not knowable at that row's forecast origin; it inflates backtests and fails live.
- **lag:** A deliberate modeling choice to use a value from `k` rows in the past (`shift(k)`).
- **release lag:** A fact about the data — when a number becomes public vs. the period it describes.
- **as-of join:** A merge attaching, for each origin, only the most recent value already published by then (`merge_asof`, backward).
- **missingness:** Which cells are empty and why (leading NaNs from lags vs. genuine gaps).
- **imputation:** Filling missing cells with a principled, past-only estimate (e.g. `ffill`); never a future value.
- **data dictionary:** An auditable per-feature table of name / source / unit / transform / availability lag / why.

## 3. Data used

| Source / file | Frequency | Units | Date range | Why used |
|---|---|---|---|---|
| `NG.RNGWHHD.W.csv` (Henry Hub spot) | Weekly | USD/MMBtu | e.g. 1997-01-10 .. 2026-05-15 | panel spine + price features + target |
| `06/.../storage_panel.csv` | Weekly | Bcf | _fill in_ | storage tightness feature |
| `07/.../monthly_balance_panel.csv` | Monthly | _fill in_ | _fill in_ | supply/demand balance feature |
| `08/.../weather_features.csv` | Weekly | HDD/CDD | _fill in_ | weather-driven demand feature |

## 4. Data decisions

Describe, for each fundamental: the **release lag** you assigned and your
justification; how you handled the **monthly -> weekly** broadcast; the join
direction; and your missing-value policy (drop vs. `ffill`) per column. State the
target definition and horizon explicitly.

## 5. Outputs checklist

- [ ] `outputs/model_panel.csv` (has `forecast_origin`, `target_date`, target, features)
- [ ] `outputs/data_dictionary.csv` (one row per feature)
- [ ] `outputs/missingness_report.csv`
- [ ] `REPORT.md`

## 6. Results

Include the data dictionary (or a summary) and the baseline metrics. Example:

| feature | source | unit | transform | availability_lag | why |
|---|---|---|---|---|---|
| `hh_price_lag_1` | EIA NG.RNGWHHD.W | USD/MMBtu | lag 1 week | known at origin | strongest cheap predictor |
| `storage_lag_1w` | module 06 | Bcf | lag 1 week (publication) | EIA ~Thu after week-end | tightness signal |

| baseline | MAE | RMSE | notes |
|---|---|---|---|
| random walk (last week's price) | e.g. 0.27 | e.g. 0.63 | the null any model must beat |

## 7. Interpretation

What does the panel let you do that the raw series did not? Which feature do you
expect to matter and why? Avoid causal language — these are *associations* until
a model with an honest backtest says otherwise.

## 8. Model or analysis limitations

Where could leakage still hide? Which release lags are guesses? What breaks if a
source's publication schedule differs from your assumption? Which columns have
heavy missingness?

## 9. Next questions

List 3 concrete questions for module 10 (e.g. "does a linear model on this panel
beat the random walk out of sample?").
