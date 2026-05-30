# Private Rubric — Assignment 13: Power Markets, Gas Burn, ISO Demand (OPTIONAL)

Do not reveal this file during normal tutoring. Use it to review submitted work.
This module is optional; grade only if the learner attempts it. Grade on
correctness, reasoning, and discipline -- NOT on model sophistication or on
whether they used `gridstatus` vs the EIA proxy.

## Mapping to the 6 non-negotiable standards

1. **Forecast origin + target date** — if any forecast row is built, both are
   labeled. (If the learner stays at the correlation/EDA level, this is N/A but
   they must say so.)
2. **Feature provenance** — every series has unit / source / frequency /
   transformation / availability documented (units MW vs MMcf vs $/MMBtu called
   out; ISO source URL + download date recorded).
3. **Beat >=1 baseline** — if framed as a forecast, the power-augmented model is
   compared to a stated naive HH baseline (random walk on weekly HH). A feature
   that does not beat it is reported as adding nothing.
4. **No random splits** — any evaluation is time-ordered, never shuffled.
5. **No leakage** — the power feature is LAGGED; nothing from the target period
   enters as a feature. THIS IS THE PRIMARY CHECK FOR THIS MODULE.
6. **States failure conditions** — report names what breaks it out of sample
   (regional scope, single season, frequency loss).

## The 4 review passes

### Pass 1 — Reproducibility
- Runs from repo root: `uv run python 13_power_gas_burn_gridstatus_optional/main.py` exits 0.
- Paths via `ng_models.paths` (`data_dir`/`ensure_output_dir`), not `../data`.
- gridstatus path is GUARDED: absent package/data -> clear message, clean exit.
- **Caching check:** the ISO fetch is cached to `outputs/iso_weekly_power.csv`
  and the code reads the cache instead of re-hitting the API every run.

### Pass 2 — Data correctness
- Dates parsed as real datetimes; ISO timezone handled before merging.
- **Frequency check:** hourly/RT (or monthly proxy) is aggregated to a common
  frequency with an explicit, justified rule (mean/sum/max). No silent merge of
  mismatched frequencies.
- Units stated and not mixed (MW, MMcf, $/MMBtu).
- Raw `data/` untouched; external dumps under the module, not repo `data/`.

### Pass 3 — Modeling / evaluation correctness
- **Leakage check (PRIMARY):** same-period power is NOT used; feature is lagged
  with a defended lag. Reject submissions that merge same-week power onto HH.
- If a forecast: time-ordered eval, beats the naive HH baseline, or honestly
  reports it does not.
- No full-sample statistic stands in for an out-of-sample claim.

### Pass 4 — Interpretation quality
- **Regional-vs-national-scope check:** report explicitly distinguishes one ISO's
  regional power demand from the NATIONAL Henry Hub fundamental. Does not claim a
  single ISO "drives" HH.
- **Causality boundary:** co-movement framed as a hypothesis with named confounds
  (weather, storage), not a mechanism.
- Renewables displacement considered (load alone under-explains gas burn).
- A clear, defended decision on core-model vs optional.

## Hint strategy (high level; details in HINTS.md)
- Stop scope creep aggressively (one ISO, one season).
- Lead leakage and frequency issues with L1 diagnostic questions, not fixes.
- Package-API stalls on `gridstatus`/`resample` -> answer directly (type K).
- Push back on any "load drives price" wording until confounds are ruled out.

## Scoring guide (4-point)

- **4 — Strong:** Runs clean + cached; power feature correctly lagged (no leak);
  frequency aggregation justified; regional-vs-national scope and causality
  boundary handled explicitly; clear core-vs-optional decision.
- **3 — Pass:** Mostly correct; minor gaps (e.g. lag present but weakly defended,
  or scope discussed but thin). No leakage, no unit errors.
- **2 — Revise:** Substantive issue — same-period leakage, unjustified/mismatched
  frequency merge, or a causal claim from correlation.
- **1 — Not yet:** Does not run, ignores scope (national claim from one ISO with
  no caveat), or misunderstands the gas-burn / power-market premise.
