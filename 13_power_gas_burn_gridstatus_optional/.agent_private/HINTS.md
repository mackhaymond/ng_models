# Leveled Hint Bank — Assignment 13: Power Markets, Gas Burn, ISO Demand

Do not paste this file to the learner. Deliver hints as L1 -> L2 -> L3 prompts,
lowest level that unblocks them first. Each sticking point names its taxonomy
TYPE (see `../../.agent_private/QUESTION_TAXONOMY.md`). Type (K) package-API
stalls are answered DIRECTLY with code; all decision types use the L1->L2->L3
ladder and never hand over the decision.

---

## Sticking point 1 — Same-period power leakage  [Type A]  ** the core check **

Symptom: learner merges week-T (or month-T) ISO load/burn onto the HH value for
that same period and treats it as predictive.

- **L1 (diagnostic):** "At the forecast origin for week T's price, had week T's
  electricity load already happened? Could you have observed it then?"
- **L2 (location):** "Look at your `pd.merge(...)` — the HH row and the power row
  carry the same week. Relative to the forecast origin, which of those two is a
  *future* observation?"
- **L3 (pattern):** "Lag before merging:
  `iso_weekly['load_lag1w'] = iso_weekly['load_mw_weekly'].shift(1)` and merge the
  lagged column. You decide how many periods the lag must be and defend it from
  what was knowable at the origin." (For the EIA monthly proxy, also flag EIA's
  multi-month publication delay — a 1-month shift may be too short.)

---

## Sticking point 2 — Frequency mismatch / aggregation rule  [Type C]

Symptom: trying to merge hourly/RT ISO data (or monthly EIA proxy) directly onto
weekly HH, or using `.mean()` without thinking about what it means.

- **L1 (diagnostic):** "What frequency is each series in? When you join a weekly
  series to an hourly one, what happens to the extra rows?"
- **L2 (location):** "Find where you collapse the hours to one number per week.
  Until both sides share a frequency the merge is meaningless — check the index
  frequency right after you load each series."
- **L3 (pattern):** "`s.set_index('ts')['load_mw'].resample('W-FRI').mean()` —
  mean = typical level, `.max()` = peak demand, `.sum()` = total energy. Pick the
  aggregator that matches what you claim the feature represents, and justify it."

---

## Sticking point 3 — gridstatus install / fetch / method names  [Type K — DIRECT]

Answer directly with working code; do not gate this.

- Install: `uv add gridstatus` (or `uv pip install gridstatus`).
- Fetch load: `iso = gridstatus.Ercot(); df = iso.get_load(start="2023-06-01",
  end="2023-09-01")` -> columns `Time`, `Load` (MW). Fuel mix:
  `iso.get_fuel_mix(start, end)` -> `Time` + per-fuel MW columns.
- Gotcha: method/column names drift across ISOs and versions. If something 404s
  or a column is missing, `dir(iso)` and the ISO's docs page
  (https://opensource.gridstatus.io/) are authoritative — don't guess.
- Timezone: `df['Time']` is tz-aware; before merging with tz-naive HH dates do
  `df['Time'] = pd.to_datetime(df['Time'], utc=True)` then after resampling
  `... .dt.tz_localize(None)`.

---

## Sticking point 4 — Caching the fetch  [Type K — DIRECT]

Whether to cache is not a decision (always cache); the how is API.

- Write: `agg.to_csv(OUTPUT_DIR / "iso_weekly_power.csv", index=False)`.
- Read back if present:
  `if path.exists(): df = pd.read_csv(path, parse_dates=["date"])` and skip the
  API call. `main.py` already looks for this exact cache path.

---

## Sticking point 5 — Regional vs national scope / causality boundary  [Type J]

Symptom: "ERCOT load drives Henry Hub," or treating one ISO's correlation with
the national price as a mechanism.

- **L1 (diagnostic):** "Your data covers one ISO; Henry Hub is a *national* price.
  Could one region's demand move a national benchmark — and what third thing could
  move both?"
- **L2 (location):** "Re-read your interpretation sentence. Swap 'drives/causes'
  for 'is associated with.' Does the evidence still hold? Which confound (weather?
  storage?) did you leave uncontrolled?"
- **L3 (pattern):** "Write it as a falsifiable hypothesis with the confound named:
  'ERCOT summer load co-moves with weekly HH, but heat drives both, so this needs
  a weather control before any causal reading.' You choose the wording — the agent
  will not bless a causal claim without an identification argument."

---

## Sticking point 6 — Load alone vs gas share (renewables displacement)  [Type G]

Symptom: using raw load as the gas-burn proxy and ignoring that wind/solar cut
burn at constant load.

- **L1 (diagnostic):** "If load is flat but wind doubles, what happens to gas
  burn? Does raw load capture that?"
- **L2 (location):** "Look at your fuel-mix columns — compare the gas column and
  total generation, not just the load series. How does the gas *share* move vs
  load on high-renewable days?"
- **L3 (pattern):** "`gas_share = mix['Natural Gas'] / mix.sum(axis=1)` is a
  closer burn proxy than load. You decide which feature your question needs and
  justify it; don't report load as if it were burn."

---

## Sticking point 7 — Should this enter the core model?  [Type F]

Symptom: wanting to promote the regional feature (or add a model) before proving
it beats a baseline.

- **L1 (diagnostic):** "What does this regional feature add over the national
  fundamentals you already have, and have you proven it beats a naive HH
  forecast?"
- **L2 (location):** "Compare your lagged-power result to a random-walk weekly-HH
  baseline on the same weeks (see `02_calendar_baselines`). Does it improve
  anything out of sample?"
- **L3 (pattern):** "Keep a before/after metric row (baseline vs +power feature)
  on a time-ordered split. You decide if the gain justifies promotion — a
  regional feature that doesn't beat the baseline stays optional."

---

## Decision-journal nudge (use throughout)

This module has many small judgment calls (which ISO, window, aggregator, lag,
core-vs-optional). Encourage a running decision journal: for each, record the
choice, the alternative rejected, and the one-line reason. Cross-reference
`docs/MODELING_DECISION_LOG.md`. When the learner is stuck on *which* decision to
defend first, point them at the highest-impact one — almost always leakage
(point 1) or scope (point 5).
