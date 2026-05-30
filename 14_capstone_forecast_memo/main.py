"""
Assignment 14 (CAPSTONE): End-to-End Henry Hub Forecast System + Research Memo

Run from the repo root:

    uv run python 14_capstone_forecast_memo/main.py

WHAT THIS MODULE IS ABOUT
-------------------------
This is the capstone. You are not learning one new technique here; you are
ASSEMBLING the whole pipeline you built across modules 02-13 into a single,
reproducible forecast system and then DOCUMENTING it like an applied energy
analyst would: a model card (what the model is, how it is validated, when it
breaks) and a research memo (what you found and what you would not yet trust).

The point of a capstone is process discipline, not algorithmic novelty. A clean
pipeline whose final model BARELY beats (or honestly fails to beat) a strong
baseline, with the reasoning written down, scores higher than a fancy model with
a leaky backtest. There is NO single correct final model.

The end-to-end stages this script scaffolds (each is a staged TODO):
  STAGE 1  Load / rebuild the model panel (reuse module 09's output).
  STAGE 2  Define the forecast target, origin, and horizon (ONE sentence).
  STAGE 3  Build 2-3 baselines + an optional market/futures benchmark.
  STAGE 4  Fit ONE final model (your choice — only after baselines exist).
  STAGE 5  Evaluate everything with the SAME walk-forward loop (no leakage).
  STAGE 6  Save the forecast package, metrics, and charts to outputs/.
  STAGE 7  Fill in MODEL_CARD.md and RESEARCH_MEMO.md from those results.

DEPENDENCY ON EARLIER MODULES (kept on purpose)
-----------------------------------------------
This module CONSUMES the model-ready panel you produced in module 09:
    09_feature_table_leakage/outputs/model_panel.csv
If it is missing, this script prints a clear "complete module 09 first" message
and exits cleanly (exit 0) — it does NOT crash. The capstone is meant to sit on
top of work you already validated; rebuilding the panel is module 09's job.

This file is intentionally INCOMPLETE. The plumbing (path resolution, input
check, output writing) is wired for you. Every MODELING DECISION is a TODO with
inline guidance — you make the call and defend it in MODEL_CARD.md / the memo.
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

# Shared library (importable once src/ is on the path). See each module's
# docstring for the API. You will mostly use metrics + plotting here; the panel
# already carries forecast_origin / target_date / target from module 09.
from ng_models.paths import data_dir, ensure_output_dir
from ng_models.io import load_series_csv
from ng_models.metrics import mae, rmse, smape, summarize_predictions

DATA_DIR = data_dir(HERE)
OUTPUT_DIR = ensure_output_dir(HERE / "outputs")
CHART_DIR = ensure_output_dir(OUTPUT_DIR / "final_charts")

# Prereq produced by module 09. Keep this dependency — do not re-derive the panel.
PANEL_PATH = ROOT / "09_feature_table_leakage" / "outputs" / "model_panel.csv"


def load_panel() -> pd.DataFrame | None:
    """Load module 09's model_panel.csv, or return None after an actionable
    message. Returning None (not raising) is what keeps this script exit-0 when a
    dependency has not been run yet."""
    if not PANEL_PATH.exists():
        print("Cannot run the capstone yet — the model panel is missing.")
        print(f"  expected: {PANEL_PATH}")
        print("  fix: complete module 09 first, e.g.")
        print("       uv run python 09_feature_table_leakage/main.py")
        print(f"\nWhen the panel exists, outputs will be written to: {OUTPUT_DIR}")
        return None
    # Module 09 writes forecast_origin / target_date as real dates — parse them
    # so date arithmetic and sorting are correct (a string sort is a classic bug).
    panel = pd.read_csv(PANEL_PATH, parse_dates=["forecast_origin", "target_date"])
    return panel.sort_values("forecast_origin").reset_index(drop=True)


def main() -> None:
    panel = load_panel()
    if panel is None:
        return  # clean exit; nothing to do until module 09 has run

    print(f"Loaded panel: {len(panel)} rows, {panel.shape[1]} columns "
          f"({panel['forecast_origin'].min().date()} .. "
          f"{panel['forecast_origin'].max().date()}).")

    # ==================================================================
    # STAGE 2 — DEFINE THE FORECAST (taxonomy types D & E — modeling decision).
    # Write ONE sentence first: "I forecast [what] at [horizon] from [origin]."
    # Module 09 already attached the bookkeeping columns:
    #   forecast_origin  -> the date the forecast is made
    #   target_date      -> the date the predicted value belongs to
    #   target_hh_next   -> the value to predict (rename if you chose another)
    # Decide: which column is your TARGET, and is it a LEVEL, a CHANGE, or a
    # return? That choice dictates which baselines are valid (Stage 3) and which
    # metric is honest (Stage 5).
    #
    # TODO: set TARGET_COL to the target column you defined in module 09, and
    #       write the one-sentence forecast definition into MODEL_CARD.md.
    TARGET_COL = "target_hh_next"  # <- confirm/replace with YOUR target column
    if TARGET_COL not in panel.columns:
        print(f"\nTarget column '{TARGET_COL}' is not in the panel. The columns are:")
        print("  " + ", ".join(panel.columns))
        print("Set TARGET_COL (STAGE 2) to your module-09 target, then re-run.")
        return

    # Train only on rows whose future is actually known (target not NaN). Keep the
    # bookkeeping columns so every output row stays auditable (origin + target).
    df = panel.dropna(subset=[TARGET_COL]).reset_index(drop=True)
    print(f"Usable rows (target known): {len(df)}")

    # ==================================================================
    # STAGE 3 — BASELINES + OPTIONAL FUTURES BENCHMARK (taxonomy type B).
    # You must beat at least one HONEST baseline. Required for the capstone:
    #   - persistence / random walk:  y_hat[t+h] = last known level (y at origin)
    #   - seasonal-naive:             y_hat[t+h] = value one season (52 wk) ago
    #   - (optional) market/futures benchmark: the NYMEX front-month settle as the
    #     "market's implied expectation" — a STRONG null for a price LEVEL.
    #
    # IMPORTANT (type A leakage): a baseline is a forecast too. It may only use
    # information known at forecast_origin. Persistence uses the origin-date price
    # (a *_lag_1 column or the spine price), NOT the target. The futures benchmark
    # must use the contract settle AS OF the origin, not later.
    #
    # Futures benchmark data is available: NG.RNGC1.W.csv (front-month, weekly).
    #   fut = load_series_csv(DATA_DIR, "NG.RNGC1.W.csv", value_name="nymex_c1")
    #   # then merge_asof on forecast_origin (direction="backward") so each origin
    #   # gets the most recent settle KNOWN by then. Decide whether the front month
    #   # is the right benchmark for YOUR horizon (1-wk? then maybe; 1-mo? maybe C2).
    #
    # TODO: construct each baseline as a prediction column on `df`. Sketch for the
    #       persistence baseline (uses last known level — find the lag-1 column
    #       module 09 created, or the spine price at the origin):
    #   if "hh_price_lag_1" in df.columns:
    #       df["pred_persistence"] = df["hh_price_lag_1"]
    #   # seasonal-naive needs the value 52 weekly rows back — build it from the
    #   # spine before dropping rows, or shift the price column by 52.
    #
    # Leave these as TODOs: pick the baselines that MATCH your target and justify
    # why the others are wrong here. The block below is just an illustrative
    # persistence placeholder so the script runs end to end.
    predictions: dict[str, pd.Series] = {}
    if "hh_price_lag_1" in df.columns:
        predictions["persistence"] = df["hh_price_lag_1"]
        print("Added placeholder persistence baseline from hh_price_lag_1.")
    else:
        print("No hh_price_lag_1 column found — build your baselines in STAGE 3.")

    # ==================================================================
    # STAGE 4 — FINAL MODEL (taxonomy types F & E — decision; do NOT rush this).
    # Only fit a model AFTER the baselines above exist and are scored. The capstone
    # does not require a specific algorithm. Reasonable choices, simplest first:
    #   - Ridge/Lasso on your leakage-safe features (sklearn.linear_model)
    #   - LightGBM / XGBoost if a linear model already beats the baseline
    # WHEN TO STOP adding features/complexity: stop when the next addition does not
    # improve OUT-OF-SAMPLE skill over the baseline in the SAME walk-forward loop.
    # Adding a model that loses to persistence is a finding, not a failure.
    #
    # API reminder (type K — fine to use directly), trees need no scaling:
    #   from sklearn.linear_model import Ridge
    #   feature_cols = [c for c in df.columns if c not in
    #                   {TARGET_COL, "forecast_origin", "target_date",
    #                    "horizon_steps", "date"}]
    #   model = Ridge(alpha=1.0)   # alpha is YOUR tuning decision (type F)
    #
    # TODO: choose feature_cols (which leakage-safe predictors?), choose a model,
    #       and produce predictions["final_model"] via the walk-forward loop below
    #       (NOT a single in-sample fit). Justify the feature set and model choice.

    # ==================================================================
    # STAGE 5 — WALK-FORWARD EVALUATION (taxonomy type A — no leakage, no shuffle).
    # Every forecaster (baselines AND the final model) must be scored on the SAME
    # time-ordered held-out rows. NEVER use a random split for time series.
    #   from sklearn.model_selection import TimeSeriesSplit
    #   for tr, te in TimeSeriesSplit(n_splits=5).split(df):
    #       # fit a model on df.iloc[tr], predict df.iloc[te]; baselines need no fit
    # The baselines above are computable per-row without fitting, so you can score
    # them on the same test rows your model is evaluated on. Decide n_splits and
    # whether to use an expanding or sliding window — justify it.
    #
    # TODO: run the walk-forward loop, collect out-of-sample predictions for each
    #       forecaster on the held-out rows, and compute metrics RELATIVE to the
    #       baseline (a skill score), not just raw RMSE (taxonomy type H).
    #
    # Below we score whatever full-row baselines exist, in-sample, JUST so the
    # script produces a metrics file on a fresh checkout. Replace this with the
    # walk-forward, out-of-sample scoring described above before you draw any
    # conclusion — in-sample numbers flatter every model.
    metric_rows = []
    actual = df[TARGET_COL]
    for name, pred in predictions.items():
        valid = pred.notna() & actual.notna()
        if valid.sum() == 0:
            continue
        metric_rows.append({
            "forecaster": name,
            "n": int(valid.sum()),
            "mae": mae(actual[valid], pred[valid]),
            "rmse": rmse(actual[valid], pred[valid]),
            "smape": smape(actual[valid], pred[valid]),
            "evaluation": "IN-SAMPLE placeholder — replace with walk-forward",
        })

    # ==================================================================
    # STAGE 6 — SAVE THE FORECAST PACKAGE, METRICS, AND CHARTS.
    # Standard 1: every forecast row must carry its forecast_origin AND target_date
    # so a reviewer can audit timing. The forecast package is that auditable table.
    #
    # final_model_metrics.csv — one row per forecaster (baselines + final model),
    #   with the metric AND a skill-vs-baseline column once you add walk-forward.
    metrics_df = pd.DataFrame(metric_rows)
    metrics_path = OUTPUT_DIR / "final_model_metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)
    print(f"Wrote {metrics_path.name} ({len(metrics_df)} forecaster rows).")

    # final_forecast_package.csv — the auditable per-row forecasts. Keep origin +
    # target_date on EVERY row. Add point forecast, and (STAGE: uncertainty) the
    # lower/upper bound of a prediction interval once you have walk-forward
    # residuals (taxonomy type L — "uncertainty estimates" = a calibrated interval,
    # e.g. point +/- z * residual_std, and you CHECK empirical coverage, not just
    # quote a band you never validated).
    pkg_cols = ["forecast_origin", "target_date", TARGET_COL]
    if "horizon_steps" in df.columns:  # present only if you added it in module 09
        pkg_cols.insert(2, "horizon_steps")
    pkg = df[pkg_cols].copy()
    pkg = pkg.rename(columns={TARGET_COL: "actual"})
    for name, pred in predictions.items():
        pkg[f"pred_{name}"] = pred.values
    # TODO (type L): add pred_final, plus pred_lower / pred_upper from your
    #   backtest residual spread, then verify coverage:
    #   cover = ((pkg["actual"] >= pkg["pred_lower"]) &
    #            (pkg["actual"] <= pkg["pred_upper"])).mean()
    #   # an 80% interval should cover ~0.80 out of sample; if not, say so.
    pkg_path = OUTPUT_DIR / "final_forecast_package.csv"
    pkg.to_csv(pkg_path, index=False)
    print(f"Wrote {pkg_path.name} ({len(pkg)} forecast rows).")

    # A chart is not enough on its own — every saved chart needs a sentence in the
    # memo saying what it shows AND what it does not show.
    if not pkg.empty:
        fig, ax = plt.subplots(figsize=(11, 5))
        ax.plot(pkg["target_date"], pkg["actual"], label="actual", linewidth=1.2)
        for name in predictions:
            ax.plot(pkg["target_date"], pkg[f"pred_{name}"], label=f"pred_{name}",
                    linewidth=1.0, alpha=0.8)
        ax.set_title("Actual vs forecasts (replace with walk-forward out-of-sample)")
        ax.set_xlabel("target_date")
        ax.set_ylabel(TARGET_COL)
        ax.legend()
        fig.tight_layout()
        chart_path = CHART_DIR / "actual_vs_forecasts.png"
        fig.savefig(chart_path, dpi=150)
        plt.close(fig)
        print(f"Wrote chart: {chart_path}")

    # ==================================================================
    # STAGE 7 — WRITE-UP (no code). Fill in MODEL_CARD.md and RESEARCH_MEMO.md
    # from these outputs: target/origin/horizon, the data dictionary, baseline vs
    # final results, error analysis (when does it miss?), key drivers (importance
    # is NOT causation — taxonomy types G/J), limitations + what would make it
    # FAIL out of sample (standard 6), and a retraining/monitoring plan.
    print("\nReproducible artifacts written to:", OUTPUT_DIR)
    print("Next: replace the in-sample placeholders with walk-forward scoring,")
    print("then complete MODEL_CARD.md and RESEARCH_MEMO.md.")


if __name__ == "__main__":
    main()
