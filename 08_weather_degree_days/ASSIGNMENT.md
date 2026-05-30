# Assignment 08: Weather Demand — Heating and Cooling Degree Days

**Phase:** Gas Fundamentals
**Level:** Intermediate
**Estimated time:** 8-14 hours

## Data scope

Use weather data (which you collect — see below), the in-repo weekly Henry Hub
spot series (`NG.RNGWHHD.W.csv`), and optionally storage from Assignment 06. Do
not use ML models yet — this is a fundamentals/feature-building module.

**Weather is EXTERNAL data and is NOT in `data/`.** Before you write any code,
read `DATA_COLLECTION.md` in this folder and collect a cached daily weather file
to `data/external/degree_days/weather_daily.csv`. `main.py` detects that file: if
it is missing it prints a pointer and exits cleanly; if present it runs the demo.

Expected data inputs:

- A cached daily weather CSV (`date,tavg_f` **or** `date,hdd,cdd`) — you collect this.
- Henry Hub weekly spot: `NG.RNGWHHD.W.csv` (already in `data/`).
- Optional: storage series from Assignment 06.

## Concepts you'll use

Read these before coding. Each is also in `docs/GLOSSARY_SEED.md` (section 6,
"Weather & degree days") — cross-reference it.

- **Heating Degree Day (HDD) / Cooling Degree Day (CDD).** A degree day measures
  how far a day's temperature pushes energy demand away from a comfort point. Using
  daily average temperature `Tavg`: **HDD = max(65 − Tavg, 0)** (cold days need
  heating) and **CDD = max(Tavg − 65, 0)** (hot days need cooling). A 25°F day is
  40 HDD and 0 CDD; a 90°F day is 0 HDD and 25 CDD; a 65°F day is 0 of both.
- **Why base 65°F.** 65°F is the long-standing U.S. industry "balance point" —
  the rough outdoor temperature at which a typical building needs neither heating
  nor cooling. It is a convention, not physics; some analysts tune the base by
  region or building stock. Keep 65 unless you can justify otherwise.
- **Daily → weekly aggregation (SUM, not mean).** Degree days are an *additive*
  quantity — they accumulate. Total heating need over a week is the SUM of the
  daily HDDs, the same way energy used is the sum of daily energy, not the average.
  Taking the mean would silently rescale your demand proxy and break comparisons.
  (This is the trap the assignment wants you to notice and decide deliberately.)
- **Population weighting.** National gas demand follows *people*, not land area.
  10 HDD over a dense metro drives far more furnace demand than 10 HDD over empty
  desert. A "population-weighted degree day" averages regional degree days using
  population (or gas-consuming load) as weights. One unweighted station is a crude
  national proxy — that limitation is exactly what you must write up.
- **Weather normal & temperature anomaly.** A *normal* is the typical value for a
  given location and point in the calendar (climatology, often a 30-year average).
  An *anomaly* is actual minus normal — "how much colder/hotter than usual." The
  anomaly, not the raw level, is what *surprises* the market and moves price.
- **Observed vs forecast — "what was known then".** Realized (observed) weather is
  only known *after* the fact. If you ever use weather to predict a future price,
  the forecaster at that origin had only a *weather forecast*, not the realized
  value — using realized future weather is leakage. For this descriptive module
  you use observed history; just be explicit that a real forecast could not.

## Package guide

Minimal API snippets for the libraries this module needs. These are
package-mechanics help — use them freely.

```python
# ng_models helper: temperature -> degree days (already imported in main.py)
from ng_models.features import hdd_cdd_from_tavg
dd = hdd_cdd_from_tavg(daily["tavg_f"], base_f=65.0)   # -> DataFrame: hdd, cdd

# pandas: roll a DAILY series up to weeks ending Friday (matches HH weekly W-FRI)
weekly = (daily.set_index("date")
                .resample("W-FRI")
                .agg({"hdd": "sum", "cdd": "sum"})   # operator is YOUR decision
                .reset_index())

# pandas: week-of-year, for grouping into a seasonal "normal"
weekly["iso_week"] = weekly["date"].dt.isocalendar().week.astype(int)
normal = weekly.groupby("iso_week")["hdd"].transform("mean")   # full-sample mean
anomaly = weekly["hdd"] - normal

# pandas: align two weekly series on the week (HH date may not be exactly Friday)
merged = pd.merge_asof(left.sort_values("date"), right.sort_values("date"),
                       on="date", direction="nearest", tolerance=pd.Timedelta("3D"))

# ng_models helper: load the in-repo weekly Henry Hub price
from ng_models.io import load_series_csv
hh = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="hh_spot")

# ng_models helper: one-line line plot to a file
from ng_models.plotting import save_line_plot
save_line_plot(weekly, x="date", y="hdd_anomaly",
               title="Weekly HDD anomaly", output_path=OUTPUT_DIR / "weather_anomaly_plot.png")

# reading a secret token from the environment (NEVER hard-code it)
import os
token = os.environ["NOAA_CDO_TOKEN"]
```

## Terms to learn

`HDD`, `CDD`, `population weighting`, `weather normal`, `temperature anomaly`,
`load proxy`, `heating demand`, `cooling demand`

Before coding, write one plain-English sentence for each term in your own words
(the "Concepts" section above and `docs/GLOSSARY_SEED.md` are your references).

## Learning goals

- Learn how weather drives gas demand through heating and power-sector cooling load.
- Compute simple HDD/CDD features from temperatures or ingest degree-day data.
- Understand why regional/population weighting matters.
- Practice the observed-vs-forecast distinction that governs weather leakage.

## Tasks

1. **Collect the data.** Follow `DATA_COLLECTION.md`: get a NOAA CDO token (stored
   in an env var, never committed), pull daily temperature for a representative
   station, and cache it to `data/external/degree_days/weather_daily.csv`.
2. **Compute HDD/CDD** with a 65°F base from daily average temperature (use
   `hdd_cdd_from_tavg`), or ingest pre-computed degree days. Decide and document
   the base.
3. **Aggregate daily → weekly** (and/or monthly). Decide the aggregation operator
   (sum vs mean) and defend it — degree days are additive.
4. **Build a normal and an anomaly**, and decide whether the anomaly is purely
   descriptive or a future predictor (the latter forces a past-only normal — no
   leakage).
5. **Compare weather anomalies against price (and storage) moves.** Report any
   relationship as an association, naming the confounders — not as causation.
6. **Write the limitation note:** why a single-station or U.S.-average degree-day
   series is too crude for trading-quality modeling (population weighting).

## Deliverables

- `outputs/weather_features.csv`
- `outputs/weather_anomaly_plot.png`
- `REPORT.md` (fill in from `REPORT_TEMPLATE.md`)

## Rules

- Keep raw data immutable; never edit the raw download by hand.
- Never commit API tokens — read them from an environment variable / `.env`.
- Save generated files under this assignment's `outputs/` folder.
- Resolve paths through `ng_models.paths` (already wired in `main.py`), not `../data`.
- Write down every assumption about dates, units, frequency conversion, and missing values.
- A chart is not enough. Every chart needs a sentence on what it shows AND what it does not show.
- Do not move to a more complex model until the required baseline or diagnostic is complete.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis?
- What dates and units are involved? (°F? degree-days? what frequency?)
- What was the most important data decision (station choice, base temp, aggregation)?
- What result surprised you?
- What would you not trust yet? (single station, full-sample normal, observed vs forecast)
- What should the next assignment investigate?
