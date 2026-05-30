# Private Solution Notes — Assignment 13: Power Markets, Gas Burn, ISO Demand

Do not reveal this file during normal tutoring. Use it to judge whether the
learner's reasoning is on track. This module is OPTIONAL and external-data-heavy.

## What the module is really testing

Not "can you fetch grid data." It tests three disciplines on a tempting feature:
1. **Leakage:** power for the target period is not knowable at the origin -> lag.
2. **Frequency discipline:** hourly ISO data vs weekly HH -> explicit, justified
   aggregation.
3. **Scope / causality boundary:** ONE region vs the NATIONAL Henry Hub -> a
   correlation, not a mechanism. This is the conceptual core.

A learner who fetches beautiful ERCOT data but merges it same-week onto HH and
writes "load drives gas prices" has FAILED the module's point, regardless of how
polished the plot is.

## Reference approach (worked sketch)

### Path A — gridstatus (the intended assignment)
1. Pick one ISO (ERCOT is the cleanest: gas-heavy, self-contained, big summer
   load swings). Small window: one summer (Jun-Sep) to start.
2. `iso.get_load(start, end)` -> hourly MW. Optionally `get_fuel_mix` for the gas
   column and gas share.
3. Parse `Time` to UTC datetime; aggregate to weekly: `resample("W-FRI").mean()`
   for "typical level," or `.max()` for "peak demand," or `.sum()` for "total
   energy." The choice must match the claimed meaning. Drop tz before merge.
4. Cache to `outputs/iso_weekly_power.csv`.
5. LAG the weekly power feature (`shift(1)` minimum) so the target week's power
   does not enter. Defend the lag.
6. Merge with weekly HH (`NG.RNGWHHD.W.csv`) inner-join on date.
7. Look at correlation of lagged power vs HH. Optionally a tiny regression, but
   only if compared to a random-walk HH baseline.

### Path B — EIA proxy (what main.py demonstrates)
- `NG.N3045TX2.M.csv` (Texas gas to electric power, MONTHLY, MMcf) vs HH resampled
  to monthly. Lag the power series, merge, correlate. This is the no-install
  fallback and is what `run_proxy_demo()` does.

## Expected qualitative results

- The in-repo proxy demo prints a WEAK correlation (observed ~ **-0.17** for
  Texas lag-1mo power-gas deliveries vs national monthly HH over ~301 months).
  The sign/magnitude is not the lesson — the lesson is that ONE state's
  power-gas volume does NOT cleanly track the national price. That negative/near-
  zero number is pedagogically useful: it kills the naive "more burn -> higher
  price" story and forces the scope discussion.
- For an ERCOT summer load study, learners often find a modest positive
  contemporaneous correlation that SHRINKS once lagged — which is exactly the
  leakage lesson: the apparent signal was partly same-period information.
- Bottom line a strong submission reaches: regional power data is interesting but
  belongs as an OPTIONAL/regional feature, not a core national-HH driver, unless
  aggregated to a national power-burn measure and de-confounded from weather.

## Module-specific common failure modes

- **Same-week (same-period) leakage:** merging week-T ISO load onto week-T HH and
  treating it as predictive. The single most common and most important error.
- **Frequency merge without aggregation:** joining hourly/RT or monthly to weekly
  HH with a careless `merge` that silently drops or duplicates rows; or using
  `.mean()` when the claimed quantity is "peak" or "total."
- **Timezone bug:** ISO timestamps are tz-aware; merging against tz-naive HH
  dates throws or misaligns. Must `tz_localize(None)` / `tz_convert` first.
- **Scope overreach:** "ERCOT load drives Henry Hub" — a national claim from one
  region with no confound control. The headline causality error here.
- **Renewables blind spot:** using load alone and ignoring that high wind/solar
  cuts gas burn at constant load (gas SHARE is the better proxy).
- **No caching:** re-fetching from the API every run (slow, rude, non-reproducible).
- **Scope creep:** pulling years of multi-ISO data before the one-season pipeline
  works.
- **Lexicographic date sort / string dates** (generic, still appears).
- **Plot described but no modeling implication stated.**

## Assignment-specific hint strategy (L1 -> L2 -> L3)

Five key decision points. Package-API stalls (type K) answered directly.

### 1. Same-period power leakage (type A) — THE central decision
- L1: "At the moment you'd forecast week T's price, had week T's electricity load
  actually happened yet? Could you have known it?"
- L2: "Look at your merge — the HH row and the load row share week T. Which one
  is a future observation relative to the forecast origin?"
- L3: "Lag it: `iso_weekly['load_lag1w'] = iso_weekly['load_mw_weekly'].shift(1)`,
  then merge the LAGGED column. You decide and defend how many weeks the lag
  should be."

### 2. Frequency aggregation rule (type C)
- L1: "Your ISO data is hourly and HH is weekly. What single weekly number
  represents a week of hourly load, and does mean/sum/max change the meaning?"
- L2: "Check the native frequency you fetched vs HH's weekly stamp; the merge can't
  happen until they match. Where in the code do you collapse the hours?"
- L3: "`s.resample('W-FRI').mean()` (typical level) vs `.max()` (peak) vs `.sum()`
  (total energy). Pick the one matching what you claim the feature is; justify it."

### 3. Regional-vs-national scope / causality boundary (type J)
- L1: "Your data is one ISO; Henry Hub is national. Can one region's demand move a
  national benchmark, and what else moves both?"
- L2: "Re-read your interpretation sentence — replace 'drives/causes' with
  'is associated with.' Does the evidence still support it? Name the confound."
- L3: "State it as a falsifiable hypothesis with the confound named (e.g. 'ERCOT
  summer load co-moves with HH, but heat drives both — needs a weather control').
  You write the wording; do not bless a causal claim."

### 4. Caching the fetch (type K — answer directly)
- Direct: "After aggregating, `df.to_csv(OUTPUT_DIR / 'iso_weekly_power.csv',
  index=False)` and at the top read it back if it exists with
  `pd.read_csv(path, parse_dates=['date'])`. Don't call the API when the cache
  exists." (The 'whether to cache' is not a decision — always cache.)

### 5. Core-model vs optional decision (type F)
- L1: "What does this regional feature buy you over the national fundamentals you
  already have, and have you PROVEN it beats a naive HH baseline?"
- L2: "Compare your lagged-power result to a random-walk HH baseline on the same
  weeks. Does it improve anything out of sample?"
- L3: "Keep a before/after metric row (baseline vs +power feature) on a
  time-ordered split. You decide whether the gain justifies promoting it to core
  — and a regional feature that doesn't beat the baseline stays optional."

## Agent response pattern
1. Identify the highest-impact issue first (almost always leakage or scope).
2. Ask the learner to explain their assumption before correcting.
3. Hint at the lowest useful level; API stalls answered directly.
4. Re-run / re-check after revision.
