# START HERE

You are a capable programmer, but this curriculum assumes you are new to the *specific* tools of applied forecasting — pandas, matplotlib, statsmodels, pmdarima, scikit-learn, lightgbm, xgboost, scipy — and that your stats, time-series, and ML intuition is still basic. That is exactly the right starting point. You will learn the concepts from the ground up, with inline API guidance whenever you touch an unfamiliar package.

## What you are building

By the time you finish Assignment 14, **you will have built a reproducible Henry Hub natural gas price forecast system and a research memo to go with it.** It will beat market and seasonal baselines, report honest uncertainty (not just a single number), and include a documented failure analysis — a clear statement of the conditions under which your model would break. That memo is the deliverable a real analyst would defend. Everything before 14 exists to get you there honestly.

## The shape of the journey

The work is sequenced into five phases. The full breakdown lives in the table in `CURRICULUM.md`; here is the map:

| Phase | Assignments | What you build |
|---|---|---|
| **Foundations** | 00–04 | Data literacy, understanding the target, naive baselines, price transformations, and a leakage-safe backtesting harness. These are the habits that prevent bad modeling. |
| **Statistical models** | 05 | Classical univariate models (ARIMA, ETS) and residual diagnostics — only *after* baselines exist. |
| **Gas fundamentals** | 06–09 | Storage, supply-demand balance, weather (degree days), and your first model-ready feature panel. This is where market reasoning is really learned. |
| **Advanced & markets** | 10–12 | Machine learning (linear, trees, boosting), the futures curve as a market-implied benchmark, and uncertainty / spike risk. |
| **Optional power** | 13 | A bridge connecting gas demand to power markets and ISO load. |
| **Capstone** | 14 | The end-to-end forecast system and research memo. |

Do them in order. Each phase assumes the one before it.

## How to work each assignment

Every module folder follows the same rhythm:

1. **Read `ASSIGNMENT.md`.** It now includes a *"Concepts you'll use"* section (the ideas, explained plainly) and a *"Package guide"* (the specific API calls you'll need). Read both before coding.
2. **Run the starter from the repo root:** `uv run python <module>/main.py` (for example `uv run python 00_repo_data_inventory/main.py`). Always run from the repo root so paths resolve.
3. **Fill in the TODOs yourself.** The starter is scaffolding. The modeling decisions are yours.
4. **Write `REPORT.md`** (start from the module's `REPORT_TEMPLATE.md`). The report is where you explain what your result *means*, not just what the code printed.
5. **Have the AI tutor review you.** Walk through your reasoning; let it ask hard questions; revise.

Generated plots and CSVs go in each module's `outputs/` folder. Raw data is never modified.

## How the AI tutor behaves

The tutor will explain concepts and package APIs as much as you want — syntax, file paths, plotting, refactors, why an ARIMA residual plot looks the way it does. Ask freely.

What it will **not** do is make your modeling decisions for you: how you define the target, which features to include, what lag to use, how to interpret a result, or whether a metric is good enough. Those are the whole point. When you're stuck on one of these, it gives **leveled hints**:

- **L1** — a diagnostic question to get you thinking.
- **L2** — a pointer to the exact object, function, or plot to look at.
- **L3** — a small pattern, with the final decision left to you.

Useful things to say: **"explain X"**, **"give me a hint"**, **"review my work"**.

## Non-negotiable habits

These are not style preferences. Internalize them now:

- **No leakage, ever.** Never use information you wouldn't have had at the forecast moment. Never evaluate a model on data you used to build its features or benchmark. No random train/test splits for time series.
- **Always beat a baseline.** A forecast is only meaningful relative to a simple alternative. Every model must beat at least one. Every forecast row carries a forecast origin *and* a target date.
- **Document feature timing.** Every feature gets a unit, a source, a transformation, and an information-availability assumption (when was this knowable?).
- **Correlation is not causation**, and your report must state what would make the model fail.

## Where to look

- `docs/GLOSSARY_SEED.md` — terms you'll encounter, defined.
- `docs/MODELING_PLAYBOOK.md` — the recurring how-to for baselines, backtesting, and evaluation.
- `docs/DATA_SOURCE_NOTES.md` — where the data comes from and what to trust.

Some modules need data you must collect yourself (futures, weather, power). When a module needs it, it will tell you via a `DATA_COLLECTION.md` in that folder — follow it before running `main.py`.

## Start now

Open `00_repo_data_inventory/ASSIGNMENT.md` and run `uv run python 00_repo_data_inventory/main.py`. That's your first step.
