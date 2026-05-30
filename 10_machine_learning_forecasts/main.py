"""
Assignment 10: Machine Learning Forecasts: Linear Models, Trees, and Boosting

Run from repo root:

    uv run python 10_machine_learning_forecasts/main.py

What this module is about
-------------------------
You now have a leakage-safe, model-ready panel from Assignment 09 (one row per
forecast origin, with a `target` column that lives in the future and predictor
columns that were all known at the origin). This module fits *machine-learning*
regressors on that panel and asks the hard question: does any of them actually
beat a cheap baseline out of sample, once you validate honestly?

The three ideas you must get right (all taught in ASSIGNMENT.md):
  1. WALK-FORWARD validation. Random k-fold CV shuffles rows, so a fold can train
     on the future and test on the past -> leakage -> a flattering score that
     evaporates in production. Time series must split in time order.
  2. SCALING + REGULARIZATION for linear models. Ridge/Lasso penalize big
     coefficients to fight overfitting, but the penalty is unfair if features are
     on different numeric scales, so you standardize first. Trees/boosting split
     on thresholds and need no scaling.
  3. IMPORTANCE != CAUSALITY. A high-importance feature predicts the target in
     this sample; it does not prove it *causes* the price.

This file is an INCOMPLETE guided starter. It runs end-to-end out of the box by
demonstrating ONE model (Ridge in a walk-forward loop) on a self-contained demo
panel so you can see the moving parts. The substantive decisions -- which models
to add, what hyperparameters, what target, how to read importance -- are left as
TODOs for you. Search the file for "TODO".
"""
from __future__ import annotations

from pathlib import Path
import sys

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
from ng_models.features import add_lags, add_rolling_stats
from ng_models.time_utils import add_calendar_columns, make_forward_target
from ng_models.metrics import rmse, mae

# scikit-learn pieces this module uses. All ship with the repo env.
#   Pipeline       -- chain steps (scaler -> model) so scaling is refit per fold.
#   StandardScaler -- z-score features: (x - mean) / std. Fit on TRAIN ONLY.
#   Ridge / Lasso  -- L2 / L1 regularized linear regression. `alpha` = penalty.
#   TimeSeriesSplit-- time-ordered CV folds (train = past, test = future).
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.inspection import permutation_importance  # noqa: F401  (you'll use this)

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# The panel this module is meant to consume, produced by Assignment 09.
PANEL_PATH = ROOT / "09_feature_table_leakage" / "outputs" / "model_panel.csv"


# ---------------------------------------------------------------------------
# Demo-panel fallback
# ---------------------------------------------------------------------------
def build_demo_panel() -> tuple[pd.DataFrame, list[str], str]:
    """Build a small leakage-safe demo panel from weekly Henry Hub.

    This stands in for Assignment 09's `model_panel.csv` so the module runs even
    before you've completed 09. It mirrors the same contract: explicit
    `forecast_origin` / `target_date`, a future `target`, and predictors that are
    all strictly-past (lags, shifted rolling stats) or calendar-only.

    Returns
    -------
    (panel, feature_cols, target_col)
    """
    hh = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="hh_price")

    # Predictors: strictly-past values only (no leakage).
    hh = add_lags(hh, columns=["hh_price"], lags=[1, 2, 4])
    hh = add_rolling_stats(hh, columns=["hh_price"], windows=[4, 12])
    hh = add_calendar_columns(hh, date_col="date")

    # Target: the price 4 weeks ahead of the origin. make_forward_target stamps
    # forecast_origin / target_date / horizon_steps so every row is auditable.
    hh = make_forward_target(hh, value_col="hh_price", horizon=4, target_name="target")

    feature_cols = [
        "hh_price_lag_1", "hh_price_lag_2", "hh_price_lag_4",
        "hh_price_roll_mean_4", "hh_price_roll_std_4",
        "hh_price_roll_mean_12", "hh_price_roll_std_12",
        "month", "iso_week",
    ]
    panel = hh.dropna(subset=feature_cols + ["target"]).reset_index(drop=True)
    return panel, feature_cols, "target"


def load_panel() -> tuple[pd.DataFrame, list[str], str, str]:
    """Load Assignment 09's panel if present, else fall back to the demo panel.

    Returns
    -------
    (panel, feature_cols, target_col, source_label)
    """
    if PANEL_PATH.exists():
        panel = pd.read_csv(PANEL_PATH, parse_dates=["forecast_origin", "target_date"])
        # TODO (data decision): which columns of the 09 panel are legitimate
        # PREDICTORS? Exclude the bookkeeping/label columns. Anything that
        # encodes the target or its date is leakage. Justify your include list.
        non_features = {"forecast_origin", "target_date", "horizon_steps", "target", "date"}
        feature_cols = [c for c in panel.columns if c not in non_features
                        and pd.api.types.is_numeric_dtype(panel[c])]
        panel = panel.dropna(subset=feature_cols + ["target"]).reset_index(drop=True)
        return panel, feature_cols, "target", "Assignment 09 model_panel.csv"

    print(
        "NOTE: Assignment 09 output not found at\n"
        f"      {PANEL_PATH}\n"
        "      Complete module 09 first to forecast on the real feature panel.\n"
        "      Falling back to a self-contained demo panel built from weekly\n"
        "      Henry Hub so this module still runs end-to-end.\n"
    )
    panel, feature_cols, target_col = build_demo_panel()
    return panel, feature_cols, target_col, "DEMO (weekly Henry Hub fallback)"


# ---------------------------------------------------------------------------
# One worked end-to-end example: Ridge in a walk-forward loop.
# This is SCAFFOLDING. Read it, run it, then extend it in the TODOs.
# ---------------------------------------------------------------------------
def walk_forward_eval(
    panel: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_name: str,
    estimator,
    n_splits: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate one estimator with time-ordered walk-forward CV.

    For each TimeSeriesSplit fold: fit on the past slice, predict the future
    slice, score it. The estimator is re-fit per fold so a scaler inside a
    Pipeline learns mean/std from TRAIN ONLY (the only leakage-safe way).

    Returns
    -------
    metrics_long : tidy rows -> (model, metric, fold, fold_dates, value)
    predictions  : per-row out-of-sample predictions with origin/target dates
    """
    X = panel[feature_cols].to_numpy(dtype=float)
    y = panel[target_col].to_numpy(dtype=float)
    origins = panel["forecast_origin"]
    targets = panel["target_date"]

    tscv = TimeSeriesSplit(n_splits=n_splits)
    metric_rows: list[dict] = []
    pred_rows: list[pd.DataFrame] = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X), start=1):
        estimator.fit(X[train_idx], y[train_idx])
        y_hat = estimator.predict(X[test_idx])

        test_start = pd.Timestamp(targets.iloc[test_idx[0]]).date()
        test_end = pd.Timestamp(targets.iloc[test_idx[-1]]).date()
        fold_dates = f"{test_start}..{test_end}"

        for metric_name, fn in (("rmse", rmse), ("mae", mae)):
            metric_rows.append({
                "model": model_name,
                "metric": metric_name,
                "fold": fold,
                "fold_dates": fold_dates,
                "value": fn(y[test_idx], y_hat),
            })

        pred_rows.append(pd.DataFrame({
            "model": model_name,
            "fold": fold,
            "forecast_origin": origins.iloc[test_idx].values,
            "target_date": targets.iloc[test_idx].values,
            "actual": y[test_idx],
            "prediction": y_hat,
        }))

    return pd.DataFrame(metric_rows), pd.concat(pred_rows, ignore_index=True)


def main() -> None:
    panel, feature_cols, target_col, source = load_panel()
    print(f"Panel source: {source}")
    print(f"Rows: {len(panel)}   Features ({len(feature_cols)}): {feature_cols}")
    print(panel[["forecast_origin", "target_date", target_col]].head())

    if len(panel) < 60:
        print("Panel too short to walk-forward validate meaningfully; stopping.")
        return

    # --- BASELINE you must beat -------------------------------------------
    # TODO (decision, taxonomy B): your demo target is the price 4 weeks ahead,
    # a LEVEL. The matched naive baseline is "last observed price persists"
    # (random walk): prediction = hh_price_lag_1. Add it to walk_forward_eval as
    # its own "model" so every ML model is compared against it in ml_metrics.csv.
    # If your 09 target is a CHANGE/return instead, the right null differs --
    # pick the baseline that matches YOUR target and say why.

    # --- WORKED EXAMPLE: Ridge in a Pipeline (scaler -> model) ------------
    # Pipeline keeps scaling honest: StandardScaler.fit runs per fold on TRAIN
    # only. alpha is the L2 penalty strength (bigger = simpler = more bias).
    ridge = Pipeline([
        ("scale", StandardScaler()),
        ("model", Ridge(alpha=1.0)),  # TODO: tune alpha (see hyperparameter TODO)
    ])
    ridge_metrics, ridge_preds = walk_forward_eval(
        panel, feature_cols, target_col, model_name="ridge_alpha1", estimator=ridge,
    )
    print("\nRidge walk-forward metrics (one row per metric/fold):")
    print(ridge_metrics.to_string(index=False))

    # --- TODO (decision, taxonomy F): add MORE models, one at a time -------
    # Only after the baseline row exists and Ridge is wired up. Suggested next:
    #   from sklearn.linear_model import Lasso        # L1: can zero out features
    #   from lightgbm import LGBMRegressor            # boosting, NO scaler needed
    #   from xgboost import XGBRegressor
    # Run each through walk_forward_eval, then pd.concat all the metric frames.
    # Question to answer: does any model beat the baseline on RMSE across folds?

    # --- TODO (decision, taxonomy K-call + selection): hyperparameters -----
    # Keep grids SMALL and time-aware. sklearn pattern:
    #   from sklearn.model_selection import GridSearchCV
    #   gs = GridSearchCV(ridge, {"model__alpha": [0.1, 1, 10]},
    #                     cv=TimeSeriesSplit(n_splits=5),
    #                     scoring="neg_root_mean_squared_error")
    #   gs.fit(X, y); print(gs.best_params_)
    # YOU decide the grid and justify each value. Do not grid-search blindly.

    # --- Assemble the deliverable frames ----------------------------------
    # TODO: once you have multiple models + the baseline, concat their metric
    # and prediction frames here instead of just Ridge.
    all_metrics = ridge_metrics
    all_preds = ridge_preds

    metrics_path = OUTPUT_DIR / "ml_metrics.csv"
    preds_path = OUTPUT_DIR / "ml_predictions.csv"
    all_metrics.to_csv(metrics_path, index=False)
    all_preds.to_csv(preds_path, index=False)
    print(f"\nWrote {metrics_path}")
    print(f"Wrote {preds_path}")

    # --- TODO (decision, taxonomy G): feature importance for your BEST model
    # For a linear model, coefficients (after scaling) are comparable; for trees,
    # use the model's importances AND permutation_importance, then compare.
    #   r = permutation_importance(estimator, X_test, y_test, n_repeats=10,
    #                              random_state=0)
    #   imp = pd.DataFrame({"feature": feature_cols,
    #                       "importance": r.importances_mean})
    #   imp.sort_values("importance", ascending=False) \
    #      .to_csv(OUTPUT_DIR / "feature_importance.csv", index=False)
    # Then plot the top features to OUTPUT_DIR / "feature_importance.png".
    # Interpretation question (do NOT skip): is the top feature a CAUSE, a
    # PREDICTOR, or a proxy for something seasonal/collinear? How would you tell?

    print(f"\nOutputs directory: {OUTPUT_DIR}")
    print("Next: add the baseline + more models, tune, then build feature_importance.{csv,png}.")


if __name__ == "__main__":
    main()
