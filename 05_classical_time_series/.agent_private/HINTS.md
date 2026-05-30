# Hint Bank — Assignment 05: Classical Time-Series Models (ARIMA, ETS, Residuals)

Do not reveal this file. Deliver hints as L1 -> L2 -> L3, lowest level that
unblocks. Each sticking point names its `QUESTION_TAXONOMY.md` type. Type (K)
package-API stalls are answered DIRECTLY with code; all modeling decisions
(A-J, L) stay leveled and never hand over the decision.

Module scope reminder: univariate weekly Henry Hub, 1-step level forecast, no
exogenous inputs (SARIMA not SARIMAX).

---

## 1. Stationarity & choosing the differencing order `d` — type (E)

- **L1:** "Run ADF and KPSS on the raw level. Their null hypotheses are
  opposite -- do they agree the level is stationary? What does that tell you?"
- **L2:** "Now run the same two tests on `y.diff().dropna()`. Compare the
  before/after p-values. Which `d` is the *smallest* that makes both tests agree
  on stationary?"
- **L3:** "Decision rule: ADF small-p = stationary; KPSS small-p = NON-stationary
  (flipped). If the level fails and one difference fixes both, that argues for
  `d=1`. You pick `d` and write the one-line justification -- I won't pick it."

## 2. Reading ACF/PACF to bound the (p, q) grid — type (E/F)

- **L1:** "On the *differenced* series, at which lag do the PACF bars fall inside
  the confidence band and stay there? Same question for the ACF. What do those
  cut-off lags suggest for `p` and `q`?"
- **L2:** "Look at `outputs/acf_pacf.png`. PACF cut-off after lag `p` -> AR(p);
  ACF cut-off after lag `q` -> MA(q). The differenced HH series is close to noise
  -- expect small orders."
- **L3:** "Confine the search to `p, q in {0,1,2}` with your chosen `d`. Justify
  the grid from what the plot shows, not from 'try everything.' You set
  `p_values`/`q_values` and defend them."
- **Type (K) sub-part (answer directly):**
  ```python
  from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
  fig, ax = plt.subplots(2, 1, figsize=(10, 6))
  plot_acf(y.diff().dropna(), lags=40, ax=ax[0])
  plot_pacf(y.diff().dropna(), lags=40, ax=ax[1], method="ywm")
  fig.tight_layout(); fig.savefig(OUTPUT_DIR / "acf_pacf.png", dpi=150); plt.close(fig)
  ```

## 3. Convergence failures / running the grid safely — type (K), DIRECT

This is a package-API stall: answer with code. The `fit_one_arima` helper in
`main.py` already wraps the fit in try/except. If they ask why a fit warns or
errors:

```python
from statsmodels.tsa.arima.model import ARIMA
import warnings
def fit_one_arima(y, order):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")   # convergence chatter
            return ARIMA(y, order=order).fit()
    except Exception as exc:
        print(f"ARIMA{order} failed: {exc}")
        return None
```

Note: non-convergence is usually a too-rich order or a near-non-invertible MA
term; log it and skip rather than crashing the grid. Choosing *which* orders to
keep after that is a modeling decision -> hint 2, not here.

## 4. Backtest vs a single fit (the leakage trap) — type (A), LEVELED

- **L1:** "At forecast origin week `t`, when you fit your model, did it get to see
  week `t+1` -- the value you are about to predict? How would you guarantee it
  did not?"
- **L2:** "Look at where you call `.fit()`. Is it called ONCE on the whole series,
  or once per origin on data up to that origin? Reporting in-sample fitted values
  as 'forecasts' is leakage and will look like it beats the random walk."
- **L3:** "Pattern -- refit inside the walk-forward loop on past-only data:
  ```python
  for origin_idx, target_idx in expanding_origins(len(y), n_test, horizon):
      train = y.iloc[: origin_idx + 1]          # past only
      res = fit_one_arima(train, best_order)
      pred = res.get_forecast(horizon).predicted_mean.iloc[-1]
  ```
  You decide `n_test`/`horizon` and confirm no row after the origin is used."

## 5. Residual whiteness / reading Ljung-Box — type (L)

- **L1:** "If your model captured the structure, what should the residuals look
  like? If a sentence said 'large p-value means residuals still have a pattern,'
  would that be right?"
- **L2:** "Run `acorr_ljungbox(res.resid, lags=[10], return_df=True)` and look at
  `lb_pvalue`. Its null is 'no leftover autocorrelation.' So which direction of
  p-value is the *good* one? Cross-check against the residual ACF plot."
- **L3:** "Large p (>0.05) = residuals look like white noise = good. A small p
  means structure remains -- then ask whether a different `p`/`q` would absorb it.
  You interpret what your p-value implies for your order choice."
- **Type (K) sub-part (answer directly):**
  ```python
  from statsmodels.stats.diagnostic import acorr_ljungbox
  lb = acorr_ljungbox(res.resid, lags=[10], return_df=True)
  ```

## 6. AIC vs out-of-sample performance — type (H/F)

- **L1:** "AIC is computed on the data the model was fit on. Does the lowest-AIC
  order automatically have the lowest *backtest* error? How would you check
  rather than assume?"
- **L2:** "Put your `{order: AIC}` table next to your per-model OOS MAE/RMSE
  table. Do the rankings match? If they disagree, which one supports a forecasting
  claim?"
- **L3:** "Report each model's error *relative to the baseline* (a skill score),
  not just raw AIC. Then you decide: is the complexity justified? AIC alone does
  not justify it -- OOS does. You write the verdict."

## 7. Picking the ETS variant (SES / Holt / Holt-Winters) — type (E/F)

- **L1:** "Does weekly HH show a persistent trend? A strong, repeatable 52-week
  seasonal cycle relative to its price shocks? Which ETS component does each of
  those call for?"
- **L2:** "SES = level only; Holt adds trend; Holt-Winters adds season
  (`seasonal_periods=52`, which needs >= 2 full cycles of training data per
  origin). Look at the series plot and the seasonal strength before reaching for
  Holt-Winters."
- **L3:** "Pick ONE and justify it; if you go Holt-Winters, guard the early
  backtest windows (try/except or start the test later). You choose the variant
  and defend it -- don't just fit all three and keep the lucky one."
- **Type (K) sub-part (answer directly):**
  ```python
  from statsmodels.tsa.holtwinters import ExponentialSmoothing
  ExponentialSmoothing(y, trend="add").fit().forecast(1)                 # Holt
  # Holt-Winters: ExponentialSmoothing(y, trend="add", seasonal="add",
  #                   seasonal_periods=52).fit()
  ```

## 8. Forecast intervals & coverage — type (L)

- **L1:** "Your point forecast says 'I expect X.' How wrong could it be, and how
  often should the truth land inside an 80% interval if it's honest?"
- **L2:** "`res.get_forecast(steps=h).conf_int(alpha=0.20)` gives the 80% band.
  On your backtest, what fraction of actuals actually fell inside it? Compare that
  empirical coverage to 80%."
- **L3:** "Coverage check:
  ```python
  inside = (lower <= y_true) & (y_true <= upper)
  coverage = inside.mean()   # should sit near 0.80
  ```
  If coverage is far below nominal, the residuals are underdispersed (intervals
  too tight). You diagnose and state whether the intervals are trustworthy."

---

## Which baseline must this beat (cross-cutting) — type (B)

- **L1:** "What is the cheapest forecast for next week's *level* with no model?
  Does your ARIMA/ETS beat that?"
- **L2:** "Bring the baseline from module 02/04. For a 1-step level the
  random-walk (`y_hat = last observed`) is the natural null."
- **L3:** "`baseline_pred = train.iloc[-1]`. Seasonal-naive (`y[t+1-52]`) is the
  wrong null for a level target here -- say why. You pick and justify."
