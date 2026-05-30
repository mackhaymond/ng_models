"""
Assignment 12: Uncertainty, Price Spikes, and Risk Metrics

Run from repo root:

    uv run python 12_uncertainty_spikes_risk/main.py

WHAT THIS MODULE IS ABOUT
-------------------------
Every model so far has produced a POINT forecast: a single number ("I expect
Henry Hub at $3.10 next week"). A point forecast is silently overconfident — it
never says how wrong it could be. This module turns point forecasts into
UNCERTAINTY-AWARE forecasts and adds a second, risk-flavored question on top:

  1. INTERVALS. Instead of one number, produce a [lo, hi] band that should
     contain the actual a stated fraction of the time (e.g. an 80% interval).
     Then HONESTLY CHECK it: empirical coverage (how often the actual landed
     inside) and average width (how wide you had to be to get there).
  2. SPIKES. A price spike is a discrete, rare, large event. RMSE-minimizing
     point models smooth exactly these away, yet they are what matter most for
     risk. You define a spike THRESHOLD, label each row as spike/no-spike, and
     evaluate it as a classification problem (precision / recall).

The two recurring traps this module is built around:
  - LEAKAGE in the spike label. The threshold must be learned from TRAINING data
    only. If you set the threshold on the full sample, the test set "knew" the
    future distribution and your spike detector is cheating.
  - COSMETIC uncertainty. Shading a chart is not a prediction interval. An
    interval is only honest if its empirical coverage is near its nominal level.

DEPENDENCY ON MODULE 09
-----------------------
This module CONSUMES the model-ready panel built in module 09:
  09_feature_table_leakage/outputs/model_panel.csv
That file already carries the curriculum bookkeeping every forecast row needs:
`forecast_origin`, `target_date`, and a future-value target column
(`target_hh_next` in the module-09 starter). If the panel is missing, this
script prints a clear "complete module 09 first" message and exits cleanly — it
does NOT crash.

This file is intentionally INCOMPLETE. The plumbing (loading, checking the
input, a leakage-safe train/test split, saving outputs) is wired for you. The
MODELING DECISIONS are left as TODOs with inline guidance — you make the call
and defend it in REPORT.md.
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

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")

# Input produced by module 09. (path, the module that makes it.)
PANEL_PATH = ROOT / "09_feature_table_leakage" / "outputs" / "model_panel.csv"

# The module-09 starter names its future-value target column `target_hh_next`.
# If you changed the target name in module 09, change it here too.
TARGET_COL = "target_hh_next"


# ---------------------------------------------------------------------------
# Interval metrics — these are mechanical (type K). They are implemented for you
# so you can spend your effort on the DECISIONS, not the arithmetic. Read them:
# you must be able to explain in REPORT.md what each number means.
# ---------------------------------------------------------------------------
def coverage_and_width(y_true, lo, hi) -> dict[str, float]:
    """Empirical coverage and average width of a prediction interval.

    coverage = fraction of actuals that fell inside [lo, hi]   (want ~ nominal)
    width    = mean(hi - lo)                                   (smaller is better
               for the SAME coverage; a wide band trivially covers everything)
    """
    y = np.asarray(y_true, dtype=float)
    lo = np.asarray(lo, dtype=float)
    hi = np.asarray(hi, dtype=float)
    inside = (lo <= y) & (y <= hi)
    return {
        "coverage": float(np.mean(inside)),
        "avg_width": float(np.mean(hi - lo)),
        "n": int(len(y)),
    }


def pinball_loss(y_true, y_pred_quantile, alpha: float) -> float:
    """Pinball / quantile loss for a single quantile level ``alpha`` in (0, 1).

    For the alpha-quantile this penalizes UNDER-prediction with weight alpha and
    OVER-prediction with weight (1 - alpha). Minimizing it yields the alpha
    quantile. Lower is better. (This is the right score for a quantile forecast;
    plain MAE/RMSE do not reward hitting the correct quantile.)
    """
    y = np.asarray(y_true, dtype=float)
    q = np.asarray(y_pred_quantile, dtype=float)
    diff = y - q
    return float(np.mean(np.maximum(alpha * diff, (alpha - 1.0) * diff)))


def classification_counts(y_true_spike, y_pred_spike) -> dict[str, float]:
    """Precision / recall / counts for a binary spike detector.

    precision = TP / (TP + FP)  — of the rows you FLAGGED, how many were real spikes
    recall    = TP / (TP + FN)  — of the REAL spikes, how many you caught
    A false positive is a false alarm; a false negative is a missed spike. Which
    one is worse is a RISK decision you make in the report, not here.
    """
    yt = np.asarray(y_true_spike, dtype=bool)
    yp = np.asarray(y_pred_spike, dtype=bool)
    tp = int(np.sum(yt & yp))
    fp = int(np.sum(~yt & yp))
    fn = int(np.sum(yt & ~yp))
    tn = int(np.sum(~yt & ~yp))
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": precision, "recall": recall}


def main() -> None:
    # --- 0. Load the leakage-safe panel, or stop cleanly ---------------------
    if not PANEL_PATH.exists():
        print("Cannot run module 12 yet — the input panel is missing:")
        print(f"  expected: {PANEL_PATH}")
        print("Complete module 09 first:")
        print("  uv run python 09_feature_table_leakage/main.py")
        return

    panel = pd.read_csv(PANEL_PATH, parse_dates=["forecast_origin", "target_date"])
    panel = panel.sort_values("forecast_origin").reset_index(drop=True)

    if TARGET_COL not in panel.columns:
        print(f"Panel loaded but target column '{TARGET_COL}' is not present.")
        print(f"Columns found: {list(panel.columns)}")
        print("Set TARGET_COL at the top of this file to your module-09 target name.")
        return

    # Keep only rows that actually have a target (drop the trailing NaN target
    # rows that make_forward_target leaves at the end of the sample).
    panel = panel.dropna(subset=[TARGET_COL]).reset_index(drop=True)
    print(f"Loaded panel: {len(panel)} rows, {panel.shape[1]} columns.")

    # --- 1. Train / test split (TIME-ORDERED — never random for time series) --
    # No leakage: the test set is strictly LATER than the train set. We split
    # once here so every threshold and interval below is learned on `train` and
    # judged on `test`. (A full backtest with rolling origins is module 04's
    # job; one honest holdout is enough to demonstrate calibration here.)
    cut = int(len(panel) * 0.7)
    train = panel.iloc[:cut].reset_index(drop=True)
    test = panel.iloc[cut:].reset_index(drop=True)
    print(f"Train: {len(train)} rows  |  Test: {len(test)} rows "
          f"(origin {test['forecast_origin'].min().date()} -> "
          f"{test['forecast_origin'].max().date()})")

    y_train = train[TARGET_COL].to_numpy(dtype=float)
    y_test = test[TARGET_COL].to_numpy(dtype=float)

    # =====================================================================
    # PART A — NAIVE PREDICTION INTERVAL FROM HISTORICAL RESIDUALS
    # =====================================================================
    # The cheapest honest interval: take a POINT forecast, look at how big its
    # errors (residuals) were IN THE TRAINING DATA, and bolt symmetric quantiles
    # of those residuals onto each test-row point forecast.
    #
    # A defensible point baseline for a 1-week-ahead LEVEL target is the
    # random walk: point forecast = last known price at the origin. The
    # module-09 panel keeps the origin-time price in `hh_price`.
    #
    # API you'll use:
    #   point_train = train["hh_price"].to_numpy(float)   # last-value forecast
    #   resid_train = y_train - point_train               # training residuals
    #   lo_q, hi_q  = np.quantile(resid_train, [0.10, 0.90])   # for an 80% band
    #   lo = point_test + lo_q ;  hi = point_test + hi_q
    #
    # TODO(A1) — TARGET/BASELINE DECISION: choose the POINT forecast the interval
    #   wraps. The placeholder below uses last-value (random walk). Is that the
    #   right null for YOUR target? (If you changed the target in module 09 to a
    #   CHANGE/return, last-value is wrong — a zero-change point forecast fits.)
    point_train = train["hh_price"].to_numpy(dtype=float)
    point_test = test["hh_price"].to_numpy(dtype=float)

    # TODO(A2) — COVERAGE LEVEL DECISION: pick your nominal interval level and the
    #   matching residual quantiles. The placeholder builds an 80% band (P10-P90).
    #   Why might 80% be more useful here than 95%? State it in the report.
    nominal = 0.80
    lo_alpha, hi_alpha = (1 - nominal) / 2, 1 - (1 - nominal) / 2  # 0.10, 0.90
    resid_train = y_train - point_train
    lo_q, hi_q = np.quantile(resid_train, [lo_alpha, hi_alpha])
    naive_lo = point_test + lo_q
    naive_hi = point_test + hi_q

    naive_cov = coverage_and_width(y_test, naive_lo, naive_hi)
    print(f"\n[A] Naive residual interval ({nominal:.0%}): "
          f"coverage={naive_cov['coverage']:.3f}  width={naive_cov['avg_width']:.3f}")
    # TODO(A3) — CALIBRATION READING (type L, withheld): is coverage near {nominal}?
    #   If your 80% band only covers ~0.60, it is OVERCONFIDENT. Decide what that
    #   means and what you would change. Do NOT just widen until it "passes".

    # =====================================================================
    # PART B — FITTED QUANTILE INTERVAL (GradientBoostingRegressor)
    # =====================================================================
    # The naive interval has the SAME width everywhere. A quantile model lets the
    # band breathe — wider when the features say uncertainty is high. You fit one
    # regressor per quantile with the pinball objective.
    #
    # API (type K, given to you):
    #   from sklearn.ensemble import GradientBoostingRegressor
    #   m_lo = GradientBoostingRegressor(loss="quantile", alpha=0.10).fit(X_tr, y_tr)
    #   m_hi = GradientBoostingRegressor(loss="quantile", alpha=0.90).fit(X_tr, y_tr)
    #   q_lo = m_lo.predict(X_te) ; q_hi = m_hi.predict(X_te)
    #   # alpha IS the quantile level; fit one model per band edge.
    #
    # TODO(B1) — FEATURE DECISION (type A leakage + inclusion): choose the predictor
    #   columns X. EVERY column you pick must be knowable at forecast_origin. The
    #   module-09 panel's lag/rolling/calendar columns are leakage-safe by
    #   construction; the raw same-date `hh_price` is the origin price (also safe).
    #   Do NOT include `target_date` or the target itself. List your features and
    #   justify each in REPORT.md.
    #
    #   feature_cols = [ ... ]   # <- YOUR choice, leakage-checked
    #   X_train = train[feature_cols].to_numpy(float)
    #   X_test  = test[feature_cols].to_numpy(float)
    #
    # TODO(B2) — fit m_lo and m_hi at YOUR lo_alpha/hi_alpha, predict q_lo/q_hi on
    #   X_test, then score coverage_and_width(y_test, q_lo, q_hi). Compare to the
    #   naive band: did the fitted interval get NARROWER at the same coverage, or
    #   did it lose coverage? That comparison is the point of Part B.
    #
    # TODO(B3) — PINBALL (type L): report pinball_loss(y_test, q_lo, lo_alpha) and
    #   pinball_loss(y_test, q_hi, hi_alpha). Lower is better. Say whether the
    #   fitted quantiles beat the naive ones on pinball, not just on width.
    #
    # Leave B unfilled and the script still runs (Part B outputs stay empty until
    # you implement it). When you do, append rows to `interval_rows` below.

    # =====================================================================
    # PART C — SPIKE EVENT: THRESHOLD, LABELS (NO LEAKAGE), CLASSIFICATION
    # =====================================================================
    # A spike is "target above some threshold". The threshold can be a statistical
    # quantile of price (e.g. the train P90) or an operational level ($/MMBtu the
    # desk cares about). EITHER way the threshold must be set on TRAINING DATA ONLY
    # — otherwise the label uses information from the future.
    #
    # TODO(C1) — THRESHOLD DECISION (type E/H, withheld): choose the spike
    #   threshold. The placeholder uses the TRAIN P90 of the target. Is a quantile
    #   the right definition, or does the desk have a fixed price level in mind?
    #   Justify your choice. Whatever you pick, compute it from `y_train` ONLY:
    spike_threshold = float(np.quantile(y_train, 0.90))  # <- train-only; YOUR call
    print(f"\n[C] Spike threshold (train-only): {spike_threshold:.3f}")

    # Apply the SAME train-derived threshold to label both sets. This is the
    # leakage-safe pattern: the test labels never saw the test distribution.
    train_is_spike = y_train >= spike_threshold
    test_is_spike = y_test >= spike_threshold
    print(f"    spikes in train: {train_is_spike.sum()}/{len(train_is_spike)}  "
          f"| spikes in test: {test_is_spike.sum()}/{len(test_is_spike)}")

    # TODO(C2) — SPIKE PREDICTOR DECISION (type F, withheld): how do you PREDICT a
    #   spike at the origin? Two honest options:
    #     (a) reuse Part B's upper quantile: flag a spike when q_hi >= threshold
    #         (the interval thinks the high case clears the bar);
    #     (b) train a classifier on leakage-safe features for the binary label.
    #   Start simple (a) and only escalate to (b) if you can justify it. Whatever
    #   you choose, produce a boolean `pred_spike` aligned to the test rows, then:
    #       counts = classification_counts(test_is_spike, pred_spike)
    #   and decide: in gas risk, is a MISSED spike (FN) or a FALSE ALARM (FP)
    #   more costly? Your threshold/predictor should reflect that answer.

    # --- Assemble + save outputs --------------------------------------------
    # Every forecast row carries forecast_origin AND target_date (curriculum
    # standard). Part A is filled; add Part B/C columns as you implement them.
    interval_forecasts = pd.DataFrame({
        "forecast_origin": test["forecast_origin"].values,
        "target_date": test["target_date"].values,
        "actual": y_test,
        "point_forecast": point_test,
        "naive_lo": naive_lo,
        "naive_hi": naive_hi,
        "is_spike_actual": test_is_spike,
        # TODO: add q_lo, q_hi (Part B) and pred_spike (Part C) columns here.
    })
    interval_forecasts.to_csv(OUTPUT_DIR / "interval_forecasts.csv", index=False)

    interval_rows = [{
        "method": "naive_residual",
        "nominal": nominal,
        "coverage": naive_cov["coverage"],
        "avg_width": naive_cov["avg_width"],
        "n": naive_cov["n"],
        # TODO(B): append a {"method": "gbr_quantile", ...} row after Part B.
    }]
    pd.DataFrame(interval_rows).to_csv(OUTPUT_DIR / "interval_metrics.csv", index=False)

    # TODO(C): once pred_spike exists, write spike_event_metrics.csv from
    #   classification_counts(...). Placeholder writes the actual-spike base rate
    #   so the file exists and is inspectable.
    spike_rows = [{
        "threshold": spike_threshold,
        "threshold_source": "train_quantile_0.90",  # <- update if you change C1
        "test_spike_base_rate": float(np.mean(test_is_spike)),
        # TODO(C2): "precision", "recall", "tp", "fp", "fn", "tn"
    }]
    pd.DataFrame(spike_rows).to_csv(OUTPUT_DIR / "spike_event_metrics.csv", index=False)

    # --- Plot: actual vs interval band over the test window -----------------
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(test["target_date"], y_test, label="actual", color="black", lw=1.2)
    ax.fill_between(test["target_date"], naive_lo, naive_hi, alpha=0.25,
                    label=f"naive {nominal:.0%} interval")
    ax.axhline(spike_threshold, color="red", ls="--", lw=1, label="spike threshold")
    ax.set_title("Henry Hub: actual vs naive prediction interval (test window)")
    ax.set_xlabel("target_date")
    ax.set_ylabel("$/MMBtu")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "forecast_intervals.png", dpi=150)
    plt.close(fig)

    print(f"\nWrote outputs to: {OUTPUT_DIR}")
    print("  interval_forecasts.csv, interval_metrics.csv, "
          "spike_event_metrics.csv, forecast_intervals.png")
    print("Next: implement Parts B and C (see TODOs) and write REPORT.md.")


if __name__ == "__main__":
    main()
