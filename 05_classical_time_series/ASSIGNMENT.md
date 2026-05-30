# Assignment 05: Classical Time-Series Models: ARIMA, ETS, and Residuals

**Phase:** Statistical Models
**Level:** Intermediate
**Estimated time:** 6-10 hours

## Data scope

Use **weekly Henry Hub spot price only**. This module is deliberately
**univariate** -- no weather, storage, or production inputs yet. Because there
are no external (exogenous) regressors, a seasonal model here is **SARIMA**, not
SARIMAX. (The "X" in SARIMAX is exogenous variables; you have none, so do not
add the X.)

Expected data inputs:

- `data/NG.RNGWHHD.W.csv` (ships with the repo; `$/MMBtu`, weekly, week-ending Friday)

## Terms to learn

`AR`, `MA`, `ARIMA`, `differencing`, `residual`, `autocorrelation`, `AIC`, `forecast interval`

Before coding, write one plain-English sentence for each term in your own words
(put them in `REPORT.md` section 2). The "Concepts you'll use" section below is
your ground-up reference; cross-check against `docs/GLOSSARY_SEED.md` sections 3-5.

## Learning goals

- Fit classical univariate models **after** establishing baselines (modules 02/04).
- Learn how residual diagnostics detect unmodeled structure.
- Compare model complexity against actual **out-of-sample** performance.

## Tasks

1. **Fit at least one ARIMA-family model and one exponential-smoothing (ETS)
   model.** Pick the differencing order `d` from stationarity tests, and a small
   `(p, q)` grid from the ACF/PACF. For ETS, pick SES / Holt / Holt-Winters and
   justify the choice. Wrap each fit in `try/except` (fits can fail to converge).
2. **Use the backtesting harness idea from Assignment 04**, not one lucky split.
   Refit each model at each forecast origin on data up to that origin only, and
   score every model on the **same** out-of-sample weeks.
3. **Plot residuals and the residual autocorrelation (ACF)** for your selected
   model, and run a Ljung-Box test.
4. **Compare each model against the best baseline from Assignment 02/04** using
   MAE, RMSE, and MAPE computed on the **identical out-of-sample set**. State, in
   numbers, whether ARIMA or ETS beats that baseline.
5. **Write a model-selection memo** explaining whether the added complexity is
   justified (did lower in-sample AIC translate into lower out-of-sample error?).

## Concepts you'll use

Each entry is 2-3 plain-English sentences, written ground-up.

- **AR (autoregressive), the "p":** The model predicts the next value as a
  weighted blend of its own recent past values (`y_{t-1}, y_{t-2}, ...`). The
  number of past values it leans on is `p`. Intuition: "next week looks like a
  mix of the last few weeks."
- **MA (moving average), the "q":** The model predicts the next value from the
  recent forecast *errors* (`ε_{t-1}, ...`), not the raw values. The number of
  past shocks it carries is `q`. Intuition: "a surprise this week echoes forward
  for a few weeks." (This MA *model* is a different thing from a rolling-mean
  smoother also casually called a moving average.)
- **Differencing, the "d":** Replacing each value with its change from the prior
  value (`y_t - y_{t-1}`). Prices wander up and down (non-stationary); their
  week-to-week *changes* are usually much more stable. `d` is how many times you
  difference to get there -- almost always 0 or 1 for a price series.
- **ARIMA(p, d, q):** Difference `d` times to get a stationary series, then
  explain it with `p` past values (AR) and `q` past shocks (MA). It is the
  workhorse for a single series with no external drivers.
- **Stationarity:** A series whose mean, variance, and autocorrelation do not
  drift over time -- "statistically the same wherever you stand on the timeline."
  Classical models assume it (after differencing). You test for it with ADF and
  KPSS.
- **ADF and KPSS tests:** Two stationarity tests with *opposite* null
  hypotheses, run together. ADF's null is "non-stationary," so a small p-value
  (<0.05) is evidence the series *is* stationary. KPSS's null is "stationary," so
  a small p-value is evidence it is *not* (the logic is flipped). Agreement is
  reassuring; disagreement means a borderline case -- difference once and re-test.
- **ACF (autocorrelation function):** How correlated the series is with a copy of
  itself shifted back `k` steps, plotted for each lag `k`. A slow decay signals
  trend/non-stationarity; the lag where it cuts off hints at the MA order `q`.
- **PACF (partial ACF):** The correlation at lag `k` *after removing* the
  influence of all shorter lags -- the *direct* effect of lag `k`. The lag where
  it cuts off hints at the AR order `p`.
- **AIC (Akaike Information Criterion):** A single number scoring a fit =
  (how well it fits) penalized by (how many parameters it uses). Lower is better,
  and it is comparable across orders on the *same* data. Crucial caveat: AIC is an
  **in-sample** score -- the lowest-AIC model is not guaranteed to win out of
  sample, which is exactly why task 4 exists.
- **Out-of-sample (OOS) error vs AIC:** AIC ranks models on the data they were fit
  on; OOS error (your backtest MAE/RMSE/MAPE) ranks them on data they have never
  seen. When they disagree, trust OOS for forecasting claims.
- **Exponential smoothing (SES / Holt / Holt-Winters):** A simpler family that
  forecasts by weighting recent observations more, with weights fading
  exponentially into the past. **SES** = level only (no trend/season); **Holt**
  adds a trend; **Holt-Winters** adds a seasonal cycle. A strong, cheap baseline.
- **Residual:** What the model could *not* explain at each point =
  `actual - fitted`. Residuals are the model's "leftovers."
- **Residual whiteness / Ljung-Box:** If the model captured the structure, the
  residuals should look like **white noise** -- uncorrelated, patternless static.
  The **Ljung-Box test** checks whether residual autocorrelations up to lag `k`
  are jointly zero. Its null is "no leftover autocorrelation," so a **large**
  p-value (>0.05) is *good* (clean residuals); a small one means structure remains.
- **Forecast interval:** A range around the point forecast expressing how
  uncertain it is (e.g., an 80% interval should contain the truth ~80% of the
  time). statsmodels gives it via `get_forecast(...).conf_int(alpha=0.20)`.

## Package guide

Minimal, copy-pasteable snippets for exactly what this module needs.

**Stationarity tests (statsmodels):**

```python
from statsmodels.tsa.stattools import adfuller, kpss
adf_stat, adf_p, *_ = adfuller(y.dropna())                       # null: non-stationary
kpss_stat, kpss_p, *_ = kpss(y.dropna(), regression="c", nlags="auto")  # null: stationary
# Decision: small adf_p AND large kpss_p -> stationary. Disagreement -> difference, retest.
```

**ACF / PACF plots (statsmodels):**

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
fig, axes = plt.subplots(2, 1, figsize=(10, 6))
plot_acf(y.diff().dropna(),  lags=40, ax=axes[0])
plot_pacf(y.diff().dropna(), lags=40, ax=axes[1], method="ywm")  # ywm avoids a known PACF artifact
fig.tight_layout(); fig.savefig(OUTPUT_DIR / "acf_pacf.png", dpi=150); plt.close(fig)
```

**ARIMA fit + forecast + interval (statsmodels):**

```python
from statsmodels.tsa.arima.model import ARIMA
res = ARIMA(y, order=(p, d, q)).fit()    # wrap in try/except -- fits can fail to converge
res.aic                                   # in-sample AIC
fc = res.get_forecast(steps=1)
point  = fc.predicted_mean.iloc[0]        # 1-step point forecast
lo, hi = fc.conf_int(alpha=0.20).iloc[0]  # 80% forecast interval
res.resid                                 # residuals (for diagnostics)
```

**Exponential smoothing (statsmodels):**

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing
ets = ExponentialSmoothing(y, trend="add").fit()                 # Holt (level + trend)
# Holt-Winters: add seasonal="add", seasonal_periods=52 (needs >= 2 full cycles to fit)
yhat = ets.forecast(1)                    # 1-step point forecast
```

**auto_arima (pmdarima) -- optional cross-check, not a substitute for your reasoning:**

```python
import pmdarima as pm
auto = pm.auto_arima(y, seasonal=False, stepwise=True, suppress_warnings=True)
print(auto.order)   # it minimizes AIC; compare to YOUR ACF/PACF choice. m=52 (weekly seasonal) is slow.
```

**Residual whiteness (statsmodels):**

```python
from statsmodels.stats.diagnostic import acorr_ljungbox
lb = acorr_ljungbox(res.resid, lags=[10], return_df=True)  # large lb_pvalue (>0.05) = clean residuals
```

**Metrics (this repo's library) -- compute on the SAME OOS rows for every model:**

```python
from ng_models.metrics import summarize_predictions   # -> {"mae","rmse","mape","smape"}
m = summarize_predictions(group_df)   # group_df has "actual" and "prediction" columns
```

## Deliverables

- `outputs/classical_model_metrics.csv` (one row per model: mae, rmse, mape, smape)
- `outputs/classical_model_predictions.csv` (one row per forecast: model,
  forecast_origin, target_date, horizon, actual, prediction)
- `outputs/residual_diagnostics.png`
- `REPORT.md`

## Rules

- Keep raw data immutable.
- Save generated files under this assignment's `outputs/` folder.
- Every forecast row must carry a **forecast origin** and a **target date**.
- Score every model on the **identical** out-of-sample weeks -- no model gets an
  easier test set.
- **No leakage:** at each origin, fit only on data up to that origin. Never let a
  full-sample fit (or a future value) leak into a prediction for an earlier week.
- Write down every assumption about dates, units, frequency, and missing values.
- A chart is not enough. Every chart needs a sentence saying what it shows and
  what it does *not* show.
- Do not move to a more complex model until the baseline/diagnostic is complete.
- Do not claim causality. A univariate price model can predict; it explains
  nothing about *why* gas moved.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis? (What, at what horizon, from what origin?)
- What dates and units are involved?
- What was the most important data decision (differencing `d`? frequency handling?)?
- Did lower in-sample AIC translate into lower out-of-sample error? Show the numbers.
- What result surprised you?
- What would you not trust yet? What would make this model fail out of sample?
- What should the next assignment investigate (e.g., adding exogenous drivers)?
