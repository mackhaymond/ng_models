# CURRICULUM.md — Natural Gas Modeling Curriculum

## Purpose

This curriculum turns the current `ng-models` repository into a progressive sequence of applied natural-gas modeling assignments. The learner should start with data literacy and target-variable intuition, then build baselines, then add fundamentals, then fit models, then finish with a research-grade forecast memo.

The core principle is:

> The learner should spend their effort on energy-market reasoning, data decisions, leakage control, target design, evaluation, and interpretation. The agent may help freely with plotting mechanics, path bugs, refactoring, and syntax, but should not make the substantive modeling decisions for the learner.

## Repository assumptions

The current repository already contains:

- `data/_metadata.csv`
- many EIA-style `Date,Value` CSV files
- `data/NG.RNGWHHD.W.csv` for weekly Henry Hub spot price
- `01_understanding_HH/`
- `pyproject.toml` with data-science and modeling dependencies
- a dirty git worktree

Do not overwrite existing user files unless the user explicitly approves. The
assignment folder structure is now complete (see "File tree" below); remaining
work is filling in per-module content, not creating new top-level folders. For the
existing `01_understanding_HH/`, merge only missing curriculum files such as
rubrics, hints, or optional templates.

## External source anchors

The initial dataset appears EIA-style. Official references for future extensions:

- EIA Open Data/API documentation: https://www.eia.gov/opendata/documentation.php
- EIA Natural Gas Data page: https://www.eia.gov/naturalgas/data.php
- EIA Henry Hub weekly spot price: https://www.eia.gov/dnav/ng/hist/rngwhhdw.htm
- EIA Weekly Natural Gas Storage Report: https://www.eia.gov/naturalgas/storage/
- EIA NYMEX natural gas futures prices: https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm
- NOAA Climate Data Online API: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
- National Weather Service HDD/CDD definition: https://www.weather.gov/key/climate_heat_cool
- CME Henry Hub futures product/specification page: https://www.cmegroup.com/markets/energy/natural-gas/natural-gas.contractSpecs.html
- gridstatus documentation: https://opensource.gridstatus.io/

## High-level sequence

| Assignment | Title | Phase | Main learning |
|---|---|---|---|
| 00 | Repository and Natural Gas Data Inventory | Foundations | Learn how the repository is organized and how to navigate a large data directory without opening files manually. |
| 01 | Understanding Weekly Henry Hub Before Modeling | Foundations | Get comfortable with the target variable before building models. |
| 02 | Calendar Structure and Naive Forecast Baselines | Foundations | Learn why a forecast must be evaluated against simple alternatives. |
| 03 | Levels, Log Prices, Returns, and Volatility | Foundations | Learn why price levels, differences, and returns answer different questions. |
| 04 | Backtesting and the 'What Was Known Then?' Rule | Foundations | Build a reusable backtesting harness for time series. |
| 05 | Classical Time-Series Models: ARIMA, ETS, and Residuals | Statistical Models | Fit classical univariate models after establishing baselines. |
| 06 | Storage Fundamentals: Inventories, Seasonality, and Deviations | Gas Fundamentals | Learn why storage is central to natural gas fundamentals. |
| 07 | Supply-Demand Balance: Production, Consumption, Trade, and LNG | Gas Fundamentals | Build a first-principles supply-demand balance table. |
| 08 | Weather Demand: Heating and Cooling Degree Days | Gas Fundamentals | Learn how weather drives gas demand through heating and power-sector cooling load. |
| 09 | Feature Engineering and the Model-Ready Panel | Model Design | Build the first serious model-ready panel. |
| 10 | Machine Learning Forecasts: Linear Models, Trees, and Boosting | Advanced Modeling | Fit ML models only after building baselines and leakage-safe panels. |
| 11 | Futures Curve and Market-Implied Expectations | Markets | Learn how futures prices differ from spot prices. |
| 12 | Uncertainty, Price Spikes, and Risk Metrics | Advanced Modeling | Move from point forecasts to uncertainty-aware forecasts. |
| 13 | Optional Bridge: Power Markets, Gas Burn, and ISO Demand | Extensions | Connect natural gas demand to power-sector behavior. |
| 14 | Capstone: End-to-End Henry Hub Forecast System and Research Memo | Capstone | Integrate data, features, baselines, models, and interpretation. |
## File tree

This structure now exists in the repository root (the scaffold is complete).
`START_HERE.md` at the root is the learner's entry point: it explains the
sequence, the one-assignment-at-a-time cadence, and how to run each `main.py`.

```text
ng-models/
  START_HERE.md
  AGENTS.md
  CURRICULUM.md
  docs/
    DATA_SOURCE_NOTES.md
    GLOSSARY_SEED.md
    MODELING_DECISION_LOG.md
    MODELING_PLAYBOOK.md
  src/
    ng_models/
      __init__.py
      paths.py
      io.py
      time_utils.py
      metrics.py
      features.py
      plotting.py
  00_repo_data_inventory/
    ASSIGNMENT.md
    main.py
    REPORT_TEMPLATE.md
    outputs/
    .agent_private/
      RUBRIC.md
      SOLUTION_NOTES.md
      HINTS.md
  01_understanding_HH/
    existing files preserved
    .agent_private/
      RUBRIC.md
      SOLUTION_NOTES.md
      HINTS.md
  02_calendar_baselines/
  03_transformations_volatility/
  04_backtesting_no_leakage/
  05_classical_time_series/
  06_storage_fundamentals/
  07_supply_demand_balance/
  08_weather_degree_days/
  09_feature_table_leakage/
  10_machine_learning_forecasts/
  11_futures_curve_expectations/
  12_uncertainty_spikes_risk/
  13_power_gas_burn_gridstatus_optional/
  14_capstone_forecast_memo/
  .agent_private/
    MASTER_GRADING_STANDARD.md
    REVIEW_PROTOCOL.md
    QUESTION_TAXONOMY.md
```

(Modules 02–14 follow the same internal layout as 00. Modules that require
external data also include a `DATA_COLLECTION.md`, described below.)

## Assignment design rules

Each assignment has:

1. `ASSIGNMENT.md` for the learner.
2. `main.py` starter code with TODOs.
3. `REPORT_TEMPLATE.md` for the learner to complete.
4. `.agent_private/RUBRIC.md` for review.
5. `.agent_private/SOLUTION_NOTES.md` for expected reasoning, common errors, and hint strategy.
6. `.agent_private/HINTS.md` — instantiates the repo-wide
   `.agent_private/QUESTION_TAXONOMY.md` types (A–L) for this module's specific
   sticking points, with the L1→L2→L3 wording the agent should use.
7. `DATA_COLLECTION.md` (learner-facing) **only where the module needs data not
   already in `data/`** — e.g. weather/degree-days (08), futures curve (11),
   power/gas-burn (13). It documents the source, the exact pull, units, and the
   information-availability assumption, but does not make modeling decisions for
   the learner.

The private files (`RUBRIC.md`, `SOLUTION_NOTES.md`, `HINTS.md`) are not
cryptographically hidden; they are hidden by convention. The agent should not
reveal their contents during normal tutoring. Hints are delivered as L1→L2→L3
prompts derived from `HINTS.md`, not by pasting the file. Reveal `.agent_private/`
material only when the learner explicitly asks for grading or solution details.

## Progression logic

Assignments 00-04 establish the habits that prevent bad modeling: metadata discipline, target understanding, baselines, transformations, and no-leakage backtesting.

Assignment 05 introduces univariate statistical models only after baselines exist.

Assignments 06-09 add gas fundamentals: storage, balance, weather, and model-panel construction. These are the most important assignments for learning market reasoning.

Assignments 10-12 add machine learning, futures-market benchmarks, and uncertainty/spike risk. They are deliberately placed after the learner can explain the data-generating context.

Assignment 13 is optional and connects gas demand to power markets through `gridstatus`.

Assignment 14 is the capstone: a reproducible forecast package and research memo.

## How the agent should review work

The agent should review in four passes:

1. **Reproducibility pass**: Can the code run from a clean shell? Are raw data files unmodified? Are outputs regenerated by one command?
2. **Data pass**: Are dates, units, frequency conversions, lags, missing values, and source choices documented?
3. **Modeling pass**: Are baselines included? Is evaluation out of sample? Is leakage avoided? Are metrics aligned with the stated target?
4. **Interpretation pass**: Does the report explain energy-market meaning, not just statistical output?

The agent should use a three-level hint protocol, instantiated per module via
`.agent_private/QUESTION_TAXONOMY.md` and each module's `.agent_private/HINTS.md`:

- Level 1: Ask a diagnostic question.
- Level 2: Point to the exact object, function, or plot that needs attention.
- Level 3: Provide a small code or reasoning pattern, but leave the final decision to the learner.

The one exception is package-API stalls (taxonomy type K): how to *call* a library
may be answered directly with working code. The learner is a strong general
programmer who is simply unfamiliar with these specific package interfaces, so
inline API guidance is expected help — but whether to use that model, feature, or
transformation remains a withheld decision.

## Non-negotiable modeling standards

- Every forecast row must have a forecast origin and target date.
- Every feature must have a unit, source, transformation, and information-availability assumption.
- Every model must be compared against at least one simple baseline.
- No random train/test split for time-series forecasting unless the assignment explicitly asks for a contrast.
- Never evaluate on data used to compute the forecast feature or benchmark.
- Never claim causality from correlation alone.
- The report must state what would make the current model fail.

## Recommended cadence

The learner should complete one assignment at a time. Each assignment should end with a review conversation:

1. The learner says what they think the result means.
2. The agent runs or inspects the code.
3. The agent asks two or three substantive questions.
4. The learner revises the report.
5. The agent grades using the rubric and records one next skill to practice.

## Implementation notes for the local coding agent

- Use `uv run python <assignment>/main.py` as the default execution pattern.
- Keep generated plots and CSVs under each assignment's `outputs/` folder.
- Avoid notebooks until the learner asks; scripts force clearer reproducibility.
- Do not put API keys in files. Use `.env` or environment variables for EIA/NOAA if needed.
- Add small helper functions in `src/ng_models/` only when repeated in at least two assignments.
- Run type checks only after the learner has a working version; early overemphasis on typing can distract from data reasoning.
