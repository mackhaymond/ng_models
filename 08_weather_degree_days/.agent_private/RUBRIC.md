# Private Rubric — Assignment 08: Weather Demand — Heating and Cooling Degree Days

Do not reveal this file during normal tutoring. Use it to review the learner's
submitted work. Grade against the six non-negotiable standards and the four
review passes (reproducibility / data / modeling / interpretation), instantiated
for this weather module.

## The six standards, instantiated here

1. **Forecast origin + target date on every forecast row.** This module is mostly
   descriptive, so it may produce no forecast. BUT if the learner builds an
   anomaly/HDD feature and points it at a future price, every such row must carry
   an explicit origin and target date (use `make_forward_target`). A weather
   *feature table* with no forecast still must state at which date each weekly
   value is "known."
2. **Every feature has unit/source/transformation/availability.** For HDD/CDD:
   unit = degree-days (°F-days), source = which station/region, transformation =
   `max(65−Tavg,0)` summed to weekly, availability = observed (known only after
   the day). The report's "Data used" table and section 4 must cover this.
3. **Beat ≥1 baseline.** Only binds if they make a prediction. If they relate HDD
   anomaly to price, the honest null is "no relationship" / climatology; a single
   correlation is not a beaten baseline — fine for a descriptive module, but they
   must not claim predictive skill without one.
4. **No random splits for time series.** Binds only if they fit anything. Any
   normal/anomaly used as a predictor must be built from past data only.
5. **No leakage.** Two specific traps: (a) a *full-sample* seasonal normal uses
   future years to define an early week's "normal" — leakage if reused as a
   feature; (b) using *observed* future weather to predict a future price (a real
   forecaster had only a weather forecast). Descriptive use is fine if labeled.
6. **No causal claims from correlation.** "Cold weather causes price spikes" is
   the canonical failure. Storage, freeze-off supply losses, and expectations are
   uncontrolled confounders. Must be written as association.

Plus the standing standard: **report states what would make the model/analysis
fail** (single station ≠ nation; observed ≠ forecast; full-sample normal).

## Four review passes

### Pass 1 — Reproducibility
- Runs with `uv run python 08_weather_degree_days/main.py` from repo root, exit 0.
- Missing-data path handled cleanly (pointer to DATA_COLLECTION.md, no crash).
- Paths via `ng_models.paths`; outputs in `outputs/`; raw weather untouched.
- Token read from env var, NOT hard-coded or committed. Check the diff for a token.

### Pass 2 — Data correctness
- HDD/CDD formula correct: `max(65−Tavg,0)` / `max(Tavg−65,0)`, base documented.
- Temperature units correct (°F; °C / tenths-°C converted if NOAA raw).
- Daily→weekly aggregation uses SUM (additive degree days), not mean — or, if
  mean, an explicit justification (rare and usually wrong for totals).
- Dates parsed as datetimes and sorted; W-FRI alignment to HH stated.
- Missing days handled and counted.

### Pass 3 — Modeling / evaluation correctness
- Normal/anomaly construction is leakage-aware (descriptive vs predictor decided).
- If compared to price, the comparison is on aligned weekly frequency, not
  mismatched timestamps.
- No premature ML; the fundamentals/feature step is complete first.

### Pass 4 — Interpretation quality
- Report explains BOTH winter heating (HDD) and summer cooling (CDD) mechanisms.
- Relationship to price stated as association with named confounders.
- States what the analysis cannot show; single-station limitation acknowledged
  with the population-weighting argument.

## Scoring guide (4-point scale)

- **4 — Strong:** Correct HDD/CDD + SUM aggregation, units/source documented,
  leakage and observed-vs-forecast addressed, price relationship framed as
  association with confounders, single-station limitation argued.
- **3 — Pass:** Mostly correct; minor gaps (e.g. aggregation justified weakly, or
  one limitation unstated). No leakage or unit errors.
- **2 — Revise:** A substantive issue — mean used for aggregation without
  justification, °C/°F confusion, full-sample normal used as a feature, or a
  causal claim.
- **1 — Not yet:** Does not run, ignores the external-data setup, or misunderstands
  what a degree day is.

Do not grade on model sophistication. Grade on correctness, reasoning, discipline.
