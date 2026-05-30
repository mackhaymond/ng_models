# Private Solution Notes — Assignment 05: Classical Time-Series Models: ARIMA, ETS, and Residuals

Do not reveal this file during normal tutoring. Use it to decide whether the
learner's reasoning is on track and to calibrate hints.

Module scope: UNIVARIATE weekly Henry Hub (`data/NG.RNGWHHD.W.csv`, $/MMBtu,
W-FRI, ~1531 weekly obs, 1997-2026). 1-step-ahead level forecast (learner may
justify a different horizon). No exogenous regressors -> SARIMA, never SARIMAX.

## Worked reference approach (one correct path)

1. **Stationarity / `d`.** Load, drop NaNs. On the LEVEL series: ADF p is
   typically NOT small (fails to reject unit root) and KPSS rejects stationarity
   -> non-stationary. On the once-differenced series `y.diff().dropna()`: ADF p
   becomes very small and KPSS no longer rejects -> stationary. Conclusion:
   **d = 1**. (Log-differencing is also defensible given the level-dependent
   variance; either is fine if justified. d=0 on the raw level is wrong.)

2. **Order grid from ACF/PACF.** On the differenced series the ACF/PACF are
   mostly inside the bands with a small spike at lag 1 -> low orders. Search
   p,q in {0,1,2} with fixed d=1. Likely AIC-competitive orders: (0,1,1),
   (1,1,0), (1,1,1). Differenced HH is close to white noise, so ARIMA gains
   little over a random walk -- that is the expected, honest result.

3. **ETS.** Holt (trend="add") or SES are reasonable; Holt-Winters with
   seasonal_periods=52 is defensible but heavy and often does NOT help weekly HH
   (the annual cycle is weak relative to price shocks). Any choice is fine if
   justified and it fits without error across the backtest windows.

4. **Walk-forward backtest** (the crux). Expanding origins over the last ~104
   weeks (learner chooses n_test). At each origin: train = y up to origin, refit
   ARIMA(best_order) and ETS, take a 1-step forecast; baseline = last training
   value (random walk). Same target weeks for all three. Build the predictions
   table with forecast_origin, target_date, horizon, model, actual, prediction.

5. **Metrics + memo.** `summarize_predictions` per model group. Compare to
   baseline. Residual diagnostics + Ljung-Box on the selected ARIMA fit (full or
   final-window fit is fine for the diagnostic plot, distinct from the backtest).

## Expected / qualitative results (NOT targets to hand over)

- On 1-step weekly HH levels, the **random walk is very hard to beat**. Expect
  ARIMA and ETS to land within a few percent of the baseline's MAE/RMSE, often
  slightly WORSE. MAE roughly on the order of ~0.15-0.30 $/MMBtu depending on the
  window's volatility; MAPE single-digit percent. Exact numbers vary with n_test
  and era -- do not grade against a fixed number.
- **AIC vs OOS frequently disagree**: a slightly richer order wins AIC but ties or
  loses OOS. Recognizing and reporting this disagreement is the main learning win.
- Ljung-Box on a sensible ARIMA's residuals usually gives a LARGE p (residuals
  near white noise) -- consistent with "differenced HH is nearly unpredictable."

## Module-specific common failure modes

1. **Full-sample-fit leakage.** Fits `ARIMA(y, order).fit()` ONCE on the whole
   series and reports `.fittedvalues` / `.predict()` in-sample as the "forecast."
   This is the signature leakage bug here -- it makes the model look like it beats
   the random walk. The backtest MUST refit per origin on past-only data.
2. **Inverted test logic.** Reads ADF and KPSS with the same rule (both p<0.05 =
   stationary) -- their nulls are OPPOSITE. Or reads Ljung-Box small p as "good"
   (it means leftover autocorrelation = bad).
3. **Lowest-AIC = best, unchecked.** Picks the order by AIC and never verifies it
   OOS, or claims complexity is "justified" purely from AIC.
4. **SARIMAX with no exog.** Wires up `SARIMAX(..., exog=...)` with a dummy/empty
   exog despite the univariate scope. Should be plain ARIMA/SARIMA.
5. **Holt-Winters convergence on short windows.** seasonal_periods=52 needs >= 2
   full cycles; early backtest origins (if n_test reaches far back) can error.
   Either start the backtest later or wrap in try/except and log skips.
6. **Different OOS sets per model.** ARIMA scored on one window, ETS on another --
   the comparison is then meaningless.
7. **Plot-without-implication.** "Here is the residual ACF" with no sentence on
   what it implies for the order choice.
8. **Causal overreach.** "ARIMA shows prices are driven by..." -- univariate, no
   drivers, no causality.

## Assignment-specific hint strategy (L1 -> L2 -> L3)

Five key decision points; instantiate the taxonomy types. Full leveled snippets
live in HINTS.md -- this is the grading-side summary of where each should land.

- **Choosing `d` (type E).** L1: do the two tests agree at d=0? L2: re-run on
  `y.diff().dropna()`. L3: remind nulls are flipped; learner picks smallest d.
  Correct landing: d=1.
- **Choosing (p,q) (type E/F).** L1: what does the differenced PACF/ACF cut-off
  suggest? L2: point at the acf_pacf plot. L3: confine grid to {0,1,2}; learner
  defends from the plot, not from "trying everything."
- **Backtest vs single fit (type A — leakage).** L1: at origin t, did your fit
  see week t+1? L2: point at where they call `.fit()` -- once or per origin? L3:
  show the refit-in-loop skeleton; learner keeps the no-peek rule.
- **AIC vs OOS (type H/F).** L1: does lower AIC guarantee lower backtest error?
  L2: line up the AIC table against the OOS metric table. L3: report skill vs
  baseline; learner decides if complexity is justified.
- **Baseline choice (type B).** L1: cheapest no-model forecast for a 1-week level?
  L2: module 02/04 naive baselines. L3: random-walk `y_hat=y[t]`; learner says
  why seasonal-naive is the wrong null for a level target.

## Agent response pattern

1. Identify the highest-impact issue first (leakage > inverted tests > everything).
2. Ask the learner to explain their assumption before correcting.
3. Deliver the lowest hint level that unblocks; package-API stalls (type K) get
   direct code.
4. Re-run / re-check after revision.
