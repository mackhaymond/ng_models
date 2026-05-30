# Hint Bank — Assignment 08: Weather Demand — Heating and Cooling Degree Days

Do not paste this file to the learner. Deliver hints as L1→L2→L3 prompts, lowest
level first, stopping as soon as they can proceed. Each sticking point below names
its QUESTION_TAXONOMY type. Type (K) = answer directly with code; all others
(A–J, L) = escalate one level at a time and hand the decision back.

---

## 1. "How do I even get weather data?" — data sourcing  · Type (K)

Answer directly; this is mechanics, not a modeling decision.

- Point to `DATA_COLLECTION.md` in this folder — it has the full NOAA CDO recipe.
- Token: free at <https://www.ncdc.noaa.gov/cdo-web/token>, stored in a gitignored
  `.env` as `NOAA_CDO_TOKEN`, read with `os.environ["NOAA_CDO_TOKEN"]`. Never
  hard-code or commit it.
- Minimal pull:
  ```python
  import os, requests, pandas as pd
  r = requests.get("https://www.ncdc.noaa.gov/cdo-web/api/v2/data",
      headers={"token": os.environ["NOAA_CDO_TOKEN"]},
      params={"datasetid":"GHCND","stationid":"GHCND:USW00094846",
              "datatypeid":"TAVG","startdate":"2020-01-01","enddate":"2020-12-31",
              "units":"standard","limit":1000}, timeout=60)
  df = pd.DataFrame(r.json()["results"])   # columns include 'date','value'
  ```
- Gotchas to state: ~1000 rows / 1 year per request (loop years); `units="standard"`
  returns °F (omit it and you get tenths of °C); if TAVG missing, use
  `(TMAX+TMIN)/2`.
- Cache to `data/external/degree_days/weather_daily.csv` as `date,tavg_f`.

## 2. HDD/CDD formula — what is a degree day  · Type (K) for the call, (E) for the base

The *formula and helper call* are direct:
- `from ng_models.features import hdd_cdd_from_tavg; dd = hdd_cdd_from_tavg(s, base_f=65.0)`
  returns a DataFrame with `hdd` and `cdd`. Formula: `HDD=max(65−Tavg,0)`,
  `CDD=max(Tavg−65,0)`.
- Sanity check to offer: a 25°F day → 40 HDD / 0 CDD; a 90°F day → 0 HDD / 25 CDD.

The *choice of base* is a decision (Type E):
- L1: "Where does 65°F come from — physics or industry convention?"
- L2: "See the `base_f=65.0` arg and the docstring of `hdd_cdd_from_tavg`."
- L3: "Keep 65 unless you can name a regional/building-stock reason; if you change
  it, justify it in the report."

## 3. Daily → weekly aggregation: sum or mean?  · Type (C)

THE central trap of this module. Do not answer "sum" outright.
- L1: "Is a degree day a rate or an accumulating total? If a week has seven daily
  HDD values, what single number is the week's total heating need?"
- L2: "Look at `.resample('W-FRI').agg({...})` in main.py step 2 — `AGG` is a
  placeholder set to `'mean'`."
- L3: "`{'hdd':'sum','cdd':'sum'}` totals the week; `'mean'` gives average daily
  intensity. Pick the one that means 'total weekly demand' and defend it in one
  sentence." (The resample *call itself* is Type K — show it freely.)

## 4. Unit / frequency alignment (°C↔°F, W-FRI)  · Type (C)

- °C confusion — L1: "Your summer HDD never hits zero — what units do you think
  TAVG is in?" L2: "NOAA raw TAVG without `units='standard'` is tenths of °C."
  L3 (K, direct): `tavg_f = value/10*9/5 + 32`.
- HH alignment — L1: "Does the Henry Hub date land exactly on your W-FRI week
  boundary? What happens to rows that don't match on a plain merge?" L2: "Compare
  the weekly index of your degree days to the HH `date` after loading." L3 (call
  is K): `pd.merge_asof(left, right, on='date', direction='nearest', tolerance=pd.Timedelta('3D'))`
  or resample HH to `W-FRI` too — you decide which.

## 5. Weather normal & anomaly — and leakage  · Type (E) + Type (A)

- Defining the anomaly (E) — L1: "Write the sentence: 'anomaly = actual minus
  ____.' What is the reference, and over what window?" L2: "Group by `iso_week`
  and subtract the group mean (see step 3)." L3: "`actual - groupby(week).transform('mean')`;
  you decide the window the 'normal' is computed over."
- The leakage twist (A) — L1: "To get 'normal' for week 3 of 2016, are you
  averaging in 2020 data? Would you have had it then?" L2: "Look at what's in the
  `groupby('iso_week')` group for an early-year row — it spans all years." L3:
  "For a *predictor*, use a past-only/expanding normal (`.expanding().mean().shift(1)`
  within the week group); for a *descriptive plot*, full-sample is fine. You
  decide which use this is and justify it."

## 6. Observed vs forecast — what was known then  · Type (A)

- L1: "If you used this HDD to predict next week's price, what did the forecaster
  actually have at that moment — the realized weather, or a *forecast* of it?"
- L2: "Trace where the weather value sits relative to the price's forecast origin
  — is the weather from the future of that origin?"
- L3: "Realized future weather as a predictor is leakage; a real model would use a
  weather *forecast* (itself uncertain). Decide whether your analysis is
  descriptive (observed is fine, just labeled) or predictive (must not use
  realized future)."

## 7. Weather → price: association, not causation  · Type (J)

- L1: "Could storage level or a supply freeze-off move both weather-demand and
  price together? Could price expectations run the other way?"
- L2: "Re-read your conclusion; swap 'causes/drives' for 'is associated with' —
  does the evidence still hold?"
- L3: "State it as a falsifiable hypothesis that names the storage/outage
  confound. The agent will not bless a causal claim without an identification
  argument. You write the wording."

## 8. Single station vs population-weighted national  · interpretation / standard 6

- L1: "Does 10 HDD in metro Chicago mean the same for *national* gas demand as 10
  HDD over the Nevada desert? What drives the difference?"
- L2: "Demand follows people/load, not land — how would you combine several
  stations to reflect that?"
- L3: "A population- (or load-) weighted average of regional degree days is the
  industry standard. Decide whether to build it or just caveat that one station is
  a crude national proxy — and say so in the limitations."

---

## Quick type map for this module

| Sticking point | Type | Regime |
|---|---|---|
| Getting weather data / NOAA API | K | direct |
| HDD/CDD helper call | K | direct |
| Base-temperature choice | E | L1→L3 |
| Sum vs mean aggregation | C | L1→L3 |
| °C↔°F, W-FRI alignment (the call) | C / K | hint choice, show call |
| Anomaly definition | E | L1→L3 |
| Full-sample normal leakage | A | L1→L3 |
| Observed vs forecast | A | L1→L3 |
| Weather→price causal claim | J | L1→L3 |
| Single station vs pop-weighted | std 6 | L1→L3 |
