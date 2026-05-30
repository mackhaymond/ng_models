"""
Assignment 05: Classical Time-Series Models: ARIMA, ETS, and Residuals
=====================================================================

Goal of this module
-------------------
You already have (from modules 02 and 04) one or more naive baselines and a
time-ordered backtest. Now you fit *classical statistical* models -- an
ARIMA-family model and an exponential-smoothing (ETS) model -- on **weekly
Henry Hub spot price only** (univariate; no weather/storage inputs yet), and
ask the hard question: does the added machinery actually beat the cheap
baseline out of sample?

Scope reminder: this is UNIVARIATE weekly Henry Hub. There are no exogenous
regressors, so if you add a seasonal block use SARIMA (not SARIMAX). See
ASSIGNMENT.md for the concept and package primers and docs/GLOSSARY_SEED.md
for the vocabulary.

Run from the repo root:

    uv run python 05_classical_time_series/main.py

This file is an INCOMPLETE guided starter. The plumbing (paths, loading,
output dir, a try/except ARIMA fit helper, a walk-forward loop skeleton) is
provided. The modeling DECISIONS -- the differencing order d, the (p,q)
grid you keep, which baseline is the right null, whether the residuals are
clean enough, and whether complexity is justified -- are left as TODOs for
you to make and defend. Fill them in.
"""
from __future__ import annotations

from pathlib import Path
import sys
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from ng_models.paths import data_dir, ensure_output_dir
from ng_models.io import load_series_csv
from ng_models.metrics import summarize_predictions

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# Weekly Henry Hub spot price, $/MMBtu. This is the only series this module uses.
HH_FILE = "NG.RNGWHHD.W.csv"


# ---------------------------------------------------------------------------
# Backtest split helper (a minimal expanding-window walk-forward, like mod 04).
# This is COMPLETE -- it just enumerates origins; the modeling is yours.
# ---------------------------------------------------------------------------
def expanding_origins(n_obs: int, n_test: int, horizon: int = 1):
    """Yield (origin_idx, target_idx) integer positions for a walk-forward backtest.

    Mirrors the no-leakage idea from module 04: the model only ever sees rows
    up to ``origin_idx`` (the forecast ORIGIN), then is scored on the row
    ``horizon`` steps later (the TARGET). The window EXPANDS -- each step adds
    one more observation to the training set.

    Parameters
    ----------
    n_obs : int    total number of observations in the series
    n_test : int   how many of the most recent points to score on
    horizon : int  steps ahead being forecast (weeks here)
    """
    first_origin = n_obs - n_test - horizon
    if first_origin < 1:
        raise ValueError("n_test + horizon is larger than the series; pick a smaller n_test.")
    for origin_idx in range(first_origin, n_obs - horizon):
        yield origin_idx, origin_idx + horizon


def main() -> None:
    # ----- Load data -------------------------------------------------------
    if not (DATA_DIR / HH_FILE).exists():
        print(f"Missing input: {DATA_DIR / HH_FILE}")
        print("This weekly Henry Hub series ships with the repo; see "
              "00_repo_data_inventory if it is absent.")
        return

    hh = load_series_csv(DATA_DIR, HH_FILE, value_name="hh_price")
    hh = hh.dropna(subset=["hh_price"]).reset_index(drop=True)
    print(hh.head())
    print(hh.tail())
    print(f"{len(hh)} weekly observations, "
          f"{hh['date'].min().date()} .. {hh['date'].max().date()}")

    # statsmodels models work best with a plain numeric Series; the date order
    # is already guaranteed by load_series_csv. We keep dates alongside for the
    # origin/target bookkeeping the backtest needs.
    #   (If you prefer a DatetimeIndex with explicit frequency, you CAN do
    #    y = hh.set_index("date")["hh_price"].asfreq("W-FRI") -- but asfreq can
    #    inject NaNs on missing weeks, so decide how you'd handle that.)
    y = hh["hh_price"]
    dates = hh["date"]

    # =====================================================================
    # STEP 1 -- STATIONARITY: choose the differencing order d.
    # ---------------------------------------------------------------------
    # The "I" in ARIMA(p, d, q) is how many times you difference to make the
    # series stationary (stable mean/variance). Prices wander; their week-to-
    # week CHANGES usually do not.
    #
    # API (see ASSIGNMENT.md Package guide):
    #   from statsmodels.tsa.stattools import adfuller, kpss
    #   adf_stat, adf_p, *_ = adfuller(y.dropna())
    #   kpss_stat, kpss_p, *_ = kpss(y.dropna(), regression="c", nlags="auto")
    # ADF null = "non-stationary"  -> small p (<0.05) means stationary.
    # KPSS null = "stationary"     -> small p means NON-stationary (flipped!).
    #
    # TODO(you decide d): Run ADF and KPSS on y, then on y.diff().dropna().
    #   Question: at d=0 do the two tests agree? Does one round of differencing
    #   flip them to "stationary"? Pick the SMALLEST d that makes the series
    #   stationary and write down WHY in REPORT.md.
    d = None  # <- set to an int (e.g. 0 or 1) from YOUR test results

    # =====================================================================
    # STEP 2 -- ORDER SELECTION: read ACF/PACF, then pick a SMALL (p,q) grid.
    # ---------------------------------------------------------------------
    # On the DIFFERENCED series:
    #   PACF cutting off after lag p  -> AR(p) term
    #   ACF  cutting off after lag q  -> MA(q) term
    #
    # API:
    #   from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    #   fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    #   plot_acf(y.diff().dropna(),  lags=40, ax=axes[0])
    #   plot_pacf(y.diff().dropna(), lags=40, ax=axes[1], method="ywm")
    #   fig.savefig(OUTPUT_DIR / "acf_pacf.png", dpi=150); plt.close(fig)
    #
    # TODO(you decide the grid): Keep p, d, q each in {0, 1, 2} (small on
    #   purpose -- a blind huge search overfits and is slow). Justify the grid
    #   from what the ACF/PACF show, not from "trying everything".
    p_values: list[int] = []  # e.g. [0, 1, 2]
    q_values: list[int] = []  # e.g. [0, 1, 2]

    # =====================================================================
    # STEP 3 -- FIT THE ARIMA GRID with try/except (fits CAN fail to converge).
    # ---------------------------------------------------------------------
    # The fit_one_arima helper below is COMPLETE -- it wraps a single fit in
    # try/except and returns None on failure so a bad order cannot crash the
    # whole grid. Your job is to USE it and decide what to do with the results.
    from statsmodels.tsa.arima.model import ARIMA  # noqa: F401 (used in helper)

    def fit_one_arima(series: pd.Series, order: tuple[int, int, int]):
        """Fit one ARIMA; return the fitted result or None if it fails.

        res.aic                      # in-sample AIC (lower = better fit+penalty)
        res.get_forecast(steps=1)    # -> .predicted_mean, .conf_int(alpha=0.20)
        res.resid                    # residuals for diagnostics
        """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # convergence chatter is noisy
                return ARIMA(series, order=order).fit()
        except Exception as exc:  # noqa: BLE001 -- log and skip, don't crash the grid
            print(f"  ARIMA{order} failed: {exc}")
            return None

    # TODO(you decide selection): Loop the (p,d,q) grid on the FULL series,
    #   record AIC for each successful fit, and pick a candidate order. But
    #   note: AIC ranks IN-SAMPLE. The real test is STEP 5 (out of sample).
    #
    # Skeleton (you fill the grid + the selection criterion):
    #   aic_by_order = {}
    #   for p in p_values:
    #       for q in q_values:
    #           res = fit_one_arima(y, (p, d, q))
    #           if res is not None:
    #               aic_by_order[(p, d, q)] = res.aic
    #   best_order = min(aic_by_order, key=aic_by_order.get)  # by AIC -- is that right?
    #
    # OPTIONAL cross-check with pmdarima (it minimizes AIC for you):
    #   import pmdarima as pm
    #   auto = pm.auto_arima(y, seasonal=False, stepwise=True, suppress_warnings=True)
    #   print(auto.order)   # compare to YOUR ACF/PACF reasoning -- do they agree?

    # =====================================================================
    # STEP 4 -- AN EXPONENTIAL-SMOOTHING (ETS) MODEL as a second classical model.
    # ---------------------------------------------------------------------
    # API:
    #   from statsmodels.tsa.holtwinters import ExponentialSmoothing
    #   # SES (level only):     ExponentialSmoothing(y).fit()
    #   # Holt (level+trend):   ExponentialSmoothing(y, trend="add").fit()
    #   # Holt-Winters (+seas): ExponentialSmoothing(y, trend="add",
    #   #                            seasonal="add", seasonal_periods=52).fit()
    #   ets.forecast(1)   # 1-step point forecast
    #
    # TODO(you decide the ETS variant): SES vs Holt vs Holt-Winters. Does
    #   weekly HH have a persistent trend? A 52-week seasonal cycle strong
    #   enough to model with ~30 years of weekly data? Pick ONE variant and
    #   justify it in REPORT.md. (Holt-Winters with seasonal_periods=52 needs
    #   at least two full cycles of training data per backtest origin.)

    # =====================================================================
    # STEP 5 -- BACKTEST every model on the SAME out-of-sample weeks (mod 04 rule).
    # ---------------------------------------------------------------------
    # This is where claims are won or lost. Use expanding_origins() so every
    # model is scored on the IDENTICAL set of target weeks, and refit each model
    # at every origin on data UP TO that origin only (NO peeking ahead).
    #
    # You MUST include the baseline you brought from module 02/04 so the
    # comparison is honest. For a 1-step LEVEL forecast the random-walk
    # ("next week = this week") is the natural null:
    #     baseline_pred = train.iloc[-1]
    #
    # TODO(you decide n_test + horizon): how many recent weeks to score on, and
    #   what 1-step-ahead means here. Then build a predictions table with, per
    #   row: model, forecast_origin (date), target_date (date), horizon,
    #   actual, prediction. The origin + target_date columns are REQUIRED
    #   (standard 1: every forecast row is auditable).
    #
    # Skeleton (you fill the model calls + the decisions):
    #   rows = []
    #   horizon = 1
    #   n_test = ...                       # you choose (e.g. last ~104 weeks)
    #   for origin_idx, target_idx in expanding_origins(len(y), n_test, horizon):
    #       train = y.iloc[: origin_idx + 1]
    #       origin_date = dates.iloc[origin_idx]
    #       target_date = dates.iloc[target_idx]
    #       actual = y.iloc[target_idx]
    #       base = {"forecast_origin": origin_date, "target_date": target_date,
    #               "horizon": horizon, "actual": actual}
    #       rows.append({**base, "model": "rw_baseline", "prediction": train.iloc[-1]})
    #       # ARIMA refit on `train` with best_order -> get_forecast(horizon)
    #       # ETS  refit on `train`                  -> forecast(horizon)
    #   preds = pd.DataFrame(rows)

    # =====================================================================
    # STEP 6 -- METRICS per model on the SAME rows, vs the baseline.
    # ---------------------------------------------------------------------
    # summarize_predictions(df) -> {"mae","rmse","mape","smape"} for a table
    # that has "actual" and "prediction" columns. Compute it per model:
    #   metrics_rows = []
    #   for name, g in preds.groupby("model"):
    #       m = summarize_predictions(g)           # same OOS weeks for all models
    #       m["model"] = name
    #       metrics_rows.append(m)
    #   metrics = pd.DataFrame(metrics_rows)
    #
    # TODO(you decide "is it justified?"): Compare ARIMA and ETS to the baseline
    #   on MAE/RMSE/MAPE over the IDENTICAL out-of-sample weeks. Did either beat
    #   the baseline? Did the lowest-AIC model also win out of sample? Write the
    #   answer in REPORT.md -- this is the model-selection memo.

    # =====================================================================
    # STEP 7 -- RESIDUAL DIAGNOSTICS for your selected model.
    # ---------------------------------------------------------------------
    # A good model leaves residuals that look like WHITE NOISE (no leftover
    # structure). Check visually (residual plot + residual ACF) and formally:
    #   from statsmodels.stats.diagnostic import acorr_ljungbox
    #   lb = acorr_ljungbox(res.resid, lags=[10], return_df=True)
    #   # large p-value (>0.05) is GOOD: no remaining autocorrelation.
    #
    # Build outputs/residual_diagnostics.png with at least a residual time plot
    # and a residual ACF (plot_acf(res.resid, ...)). Add a one-sentence caption
    # in the report saying what it shows and what it does NOT show.
    #
    # TODO(you decide): does Ljung-Box say the residuals are clean? If not, what
    #   structure is left, and does that change your order choice?

    # ----- Save the deliverables (uncomment once the steps above are filled) --
    # preds.to_csv(OUTPUT_DIR / "classical_model_predictions.csv", index=False)
    # metrics.to_csv(OUTPUT_DIR / "classical_model_metrics.csv", index=False)
    # (residual_diagnostics.png is saved inside STEP 7)

    print(f"Outputs should be written to: {OUTPUT_DIR}")
    print("Starter is incomplete: work through the STEP 1..7 TODOs above.")


if __name__ == "__main__":
    main()
