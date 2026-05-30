# Private Solution Notes — Assignment 08: Weather Demand — Heating and Cooling Degree Days

Do not reveal this file during normal tutoring. Use it to judge whether the
learner's reasoning is on track and to calibrate hints.

## Worked reference approach (reference implementation sketch)

1. **Collect** daily TAVG for a demand-center station (e.g. Chicago O'Hare
   `GHCND:USW00094846`) from NOAA CDO, `units="standard"` (°F), looping by year
   to stay under the ~1000-row/1-year request cap. Cache to
   `data/external/degree_days/weather_daily.csv` as `date,tavg_f`. Keep the raw.
2. **Degree days:** `hdd_cdd_from_tavg(daily["tavg_f"], base_f=65.0)`. Base 65°F.
3. **Aggregate daily → weekly with SUM** (degree days are additive):
   ```python
   weekly = (daily.set_index("date").resample("W-FRI")
                  .agg({"hdd": "sum", "cdd": "sum"}).reset_index())
   ```
   W-FRI so it lines up with the weekly Henry Hub series.
4. **Normal & anomaly:** for a descriptive plot, full-sample seasonal mean by ISO
   week is acceptable; if it becomes a predictor, build it expanding/past-only.
   ```python
   weekly["iso_week"] = weekly["date"].dt.isocalendar().week.astype(int)
   weekly["hdd_normal"]  = weekly.groupby("iso_week")["hdd"].transform("mean")
   weekly["hdd_anomaly"] = weekly["hdd"] - weekly["hdd_normal"]
   ```
5. **Compare to price:** load `NG.RNGWHHD.W.csv`, align on the week (resample HH
   to W-FRI or `merge_asof` with a small tolerance), then look at the sign of the
   correlation between HDD anomaly and HH level/change. Report as association.
6. **Outputs:** `weather_features.csv` (weekly hdd, cdd, normal, anomaly) and
   `weather_anomaly_plot.png` via `save_line_plot`.

## Expected / qualitative results

- Weekly summed HDD peaks in deep winter (ISO weeks ~1-6 and ~50-52), order of
  ~150-300 HDD/week for a northern station; CDD peaks mid-summer (weeks ~26-34),
  smaller magnitude for a northern station.
- HDD and CDD are near-mutually-exclusive across the year (one is ~0 when the
  other is large) — a good sanity check that the formula/base is right.
- HDD anomaly vs HH: typically a weak-to-moderate POSITIVE association (cold
  surprises ↔ firmer price), but noisy and regime-dependent; r often in
  ~0.1-0.4 on weekly data and very sensitive to the window and to storage state.
  A learner reporting "huge, clean, causal" relationship is over-claiming.
- A single station explains national demand only loosely; population-weighted
  multi-region degree days track national gas demand materially better.

## Module-specific common failure modes

- **Aggregating with MEAN instead of SUM.** The single most common error. Mean
  daily HDD is not "weekly heating need"; it silently rescales the proxy and
  makes cross-period comparison wrong. main.py ships with `AGG="mean"` as a
  deliberate placeholder — the learner must change it. (Type C.)
- **°C / tenths-°C not converted to °F.** NOAA raw TAVG without `units="standard"`
  is tenths of °C; forgetting the conversion produces absurd degree-days (e.g.
  HDD that never goes to zero in summer). (Type C.)
- **Full-sample normal reused as a model feature.** Defining "normal" with all
  years, then feeding the anomaly to a predictor — leaks future climatology into
  past rows. (Type A.)
- **Observed-vs-forecast confusion.** Using realized future weather to "predict"
  a future price. A real forecaster had only a weather *forecast* at the origin.
  (Type A.)
- **Causal overclaim.** "Cold weather causes the spike" without controlling for
  storage/outages/expectations. (Type J.)
- **Single station presented as national truth** with no population-weighting
  caveat. (Interpretation / standard 6 + limitations.)
- **W-FRI misalignment:** merging HH on raw timestamps that don't equal Friday,
  dropping most rows silently. (Type C.)
- **Token committed** to the repo or hard-coded in main.py. (Reproducibility.)

## Assignment-specific hint strategy (L1→L2→L3 instantiation)

Five key decision points. Deliver the lowest level that unblocks; never hand over
the decision itself (except type-K API mechanics, which you answer directly).

1. **Aggregation operator — sum vs mean (Type C).**
   - L1: "Is a degree day a *rate* or an *accumulating total*? If you had 7 daily
     HDDs, what number represents the whole week's heating need?"
   - L2: "Look at the `.agg({...})` call in main.py step 2 — `AGG` is set to a
     placeholder."
   - L3: "`{'hdd': 'sum', 'cdd': 'sum'}` totals the week; `'mean'` averages it. One
     matches 'total weekly demand.' You pick and justify it in one sentence."

2. **Base temperature (Type E).**
   - L1: "Where does 65°F come from, and is it physics or convention?"
   - L2: "`hdd_cdd_from_tavg` takes `base_f=65.0` — see its docstring."
   - L3: "Keep 65 unless you can name a regional reason to move it; if you change
     it, state the building-stock/climate justification."

3. **Normal / anomaly leakage (Type A).**
   - L1: "When you average all years to get 'normal' for week 3 of 2016, are you
     using data from 2020? Would you have had it at the time?"
   - L2: "Look at the `groupby('iso_week').transform('mean')` in step 3 — what is
     in that group for an early-year row?"
   - L3: "For a predictor, replace the full-sample mean with an expanding/past-only
     mean (e.g. group then `expanding().mean().shift(1)`); for a pure plot the
     full-sample mean is fine. You decide which use this is."

4. **Weather→price as association, not cause (Type J).**
   - L1: "Could storage level or a supply outage move both weather-demand and price
     at once? Could the arrow run price→behavior?"
   - L2: "Re-read your sentence; swap 'causes' for 'is associated with' — does the
     evidence still support it?"
   - L3: "State it as a falsifiable hypothesis naming the storage confound. The
     agent will not bless a causal claim without an identification argument."

5. **Single station vs population-weighted national (interpretation / standard 6).**
   - L1: "Does 10 HDD in Chicago mean the same for national gas demand as 10 HDD in
     the Nevada desert? What drives the difference?"
   - L2: "Look at where your demand actually is — people. How would you weight
     multiple stations?"
   - L3: "A population/load-weighted average of regional degree days is the
     industry standard; note in the report why one station is a crude proxy. You
     decide whether to actually build the weighting or just caveat it."

API-mechanics (Type K — answer directly): NOAA `requests` call + token from env,
`pd.read_csv`/`to_datetime`, `resample('W-FRI')`, `merge_asof`, `save_line_plot`.

## Agent response pattern

1. Identify the highest-impact issue first (usually aggregation operator or a
   leakage/causal claim).
2. Ask the learner to explain their assumption.
3. Provide a hint at the lowest useful level (see HINTS.md).
4. Re-run / re-check after revision.
