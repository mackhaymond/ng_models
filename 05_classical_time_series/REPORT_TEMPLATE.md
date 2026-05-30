# Report — Assignment 05: Classical Time-Series Models: ARIMA, ETS, and Residuals

> Copy this file to `REPORT.md` and fill it in. Replace every bracketed prompt.

## 1. Objective

In 2-4 sentences: state the target precisely as "I forecast [what] at [horizon]
from [origin]" (e.g., "the 1-week-ahead weekly Henry Hub spot price level, from
each week's reported value"), and say which baseline this model must beat.

## 2. Vocabulary

Write each in your own words (1 sentence each). Definitions in ASSIGNMENT.md are
your reference, but rephrase -- copying is not learning.

- **AR:** The next value as a weighted blend of its own recent past values; `p` = how many.
- **MA:** The next value as a blend of recent forecast *errors* (shocks); `q` = how many.
- **ARIMA:** Difference `d` times to make the series stationary, then model it with AR(`p`) and MA(`q`).
- **differencing:** Modeling the change `y_t - y_{t-1}` instead of the level, to remove trend / induce stationarity.
- **residual:** The leftover the model could not explain at each point, `actual - fitted`.
- **autocorrelation:** How much the series resembles a lagged copy of itself; the ACF plots it per lag.
- **AIC:** An in-sample fit-quality score penalized for parameter count; lower is better, comparable across orders on the same data.
- **forecast interval:** A range around the point forecast quantifying its uncertainty (e.g., an 80% band).

## 3. Data used

| Source / file | Frequency | Units | Date range | Why used |
|---|---:|---|---|---|
| `data/NG.RNGWHHD.W.csv` (EIA Henry Hub spot) | Weekly (W-FRI) | $/MMBtu | [first..last in your run] | The only series; univariate target |

## 4. Data decisions

Describe: date parsing/sorting, how you handled any missing weeks, what
differencing order `d` you chose and the ADF/KPSS evidence for it, whether you
modeled the level or the differenced series, and your forecast horizon (in
weeks). State explicitly that no exogenous inputs are used (univariate scope).

## 5. Outputs checklist

- [ ] `outputs/classical_model_metrics.csv`
- [ ] `outputs/classical_model_predictions.csv`
- [ ] `outputs/residual_diagnostics.png`
- [ ] `REPORT.md`

## 6. Results

Include the model-comparison metrics table, computed on the **same**
out-of-sample weeks for every model. Example shape (numbers are illustrative,
not targets):

| model | mae | rmse | mape | n_oos_weeks |
|---|---:|---:|---:|---:|
| rw_baseline | 0.18 | 0.27 | 0.058 | 104 |
| arima(1,1,1) | 0.19 | 0.28 | 0.061 | 104 |
| holt | 0.21 | 0.31 | 0.067 | 104 |

Also report: your selected ARIMA order and its in-sample AIC, the AIC of the
runner-up order, and the Ljung-Box p-value on the selected model's residuals.
Reference `outputs/residual_diagnostics.png` with a one-sentence caption stating
what it shows (e.g., "residuals scatter around zero; residual ACF bars sit inside
the confidence band, so no obvious leftover autocorrelation") and what it does
**not** show (e.g., "it does not reveal whether variance is stable across
regimes").

## 7. Interpretation

This is the model-selection memo. Answer directly: did ARIMA or ETS beat the
baseline out of sample, and by how much? Did the lowest-AIC model also win out of
sample, or did in-sample and out-of-sample rankings disagree? Is the added
complexity justified? Keep it predictive -- a univariate model says nothing about
*why* gas moved, so make no causal claims.

## 8. Model or analysis limitations

Be specific. State explicitly **what would make this model fail out of sample**
(e.g., a structural regime shift like the shale glut or a demand shock the past
cannot anticipate; thin/missing weeks; a fixed order chosen once but refit on a
changing series). Note any convergence failures and which orders you dropped.

## 9. Next questions

Three concrete questions, e.g.: Would adding exogenous drivers (HDD, storage) via
SARIMAX in a later module beat this univariate ceiling? Does a longer horizon
break the random-walk's advantage? Do the residual spikes line up with known
weather/storage shocks?
