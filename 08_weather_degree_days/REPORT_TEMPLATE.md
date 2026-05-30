# Report — Assignment 08: Weather Demand — Heating and Cooling Degree Days

## 1. Objective

In 2-4 sentences, explain what this assignment is trying to learn. Name the
object of analysis (e.g. "weekly HDD/CDD as a demand proxy and how its anomaly
lines up with Henry Hub"), and say explicitly that this is descriptive
feature-building, not yet a forecast.

## 2. Vocabulary

One or two sentences each, in your own words (see ASSIGNMENT "Concepts" and
`docs/GLOSSARY_SEED.md` §6).

- **HDD:** Heating Degree Days = max(65 − Tavg, 0); how many degrees of heating a cold day demanded.
- **CDD:** Cooling Degree Days = max(Tavg − 65, 0); how many degrees of cooling a hot day demanded.
- **population weighting:** Averaging regional degree days by population/load, because demand follows people, not area.
- **weather normal:** The typical (climatological) value for a location and point in the calendar; the reference line.
- **temperature anomaly:** Actual minus normal — the "warmer/colder than usual" surprise that moves markets.
- **load proxy:** A weather-derived stand-in for actual gas demand (we cannot observe demand directly here).
- **heating demand:** Winter gas use for space heating; rises with HDD.
- **cooling demand:** Summer power-sector gas use for air conditioning; rises with CDD.

## 3. Data used

| Source / file | Frequency | Units | Date range | Why used |
|---|---|---|---|---|
| NOAA CDO GHCND station GHCND:USW00094846 (Chicago O'Hare), TAVG | daily | °F | 2015-01-01 to 2023-12-31 | weather demand proxy |
| `data/.../weather_daily.csv` (derived hdd, cdd) | weekly (W-FRI) | degree-days | same | aggregated feature |
| `NG.RNGWHHD.W.csv` (Henry Hub spot) | weekly (W-FRI) | $/MMBtu | 1997-present | price comparison |

(Replace with your actual station, range, and any storage series you used.)

## 4. Data decisions

State each concrete choice and one sentence of justification:
- Station / region chosen and why it is (or is not) representative.
- Base temperature (65°F default) and whether you changed it.
- Temperature units and any °C→°F conversion (NOAA TAVG can be tenths of °C).
- Daily→weekly aggregation operator (sum vs mean) and why.
- How you aligned weather to the Henry Hub week (resample / merge_asof).
- Missing-value handling (dropped days? interpolated? how many?).
- Whether your anomaly normal is full-sample (descriptive) or past-only (predictor).

## 5. Outputs checklist

- [ ] `outputs/weather_features.csv`
- [ ] `outputs/weather_anomaly_plot.png`
- [ ] `REPORT.md`

## 6. Results

Include: (a) a small table of summary stats for weekly HDD and CDD (min, max,
mean, peak week), (b) the anomaly plot reference with one sentence on what it
shows, (c) if you compared to price, the association you observed (e.g. a
correlation coefficient between weekly HDD anomaly and HH change) stated as a
number with sign. Example sentence: "Weekly HDD peaks near ISO week 2-4 (deep
winter) at ~X HDD; the HDD-anomaly vs HH-change correlation over 2015-2023 was
r = 0.NN (positive but modest)."

## 7. Interpretation

Explain what the results mean for natural-gas modeling: cold anomalies are
*associated with* heating-demand strength and *often* price firmness, but name
the confounders (storage level, supply/freeze-off outages, expectations) and do
NOT claim weather "causes" the price move. Distinguish what the analysis shows
(co-movement) from what it cannot (a causal or tradable signal).

## 8. Model or analysis limitations

What could be wrong, incomplete, unstable, or leaked? At minimum address: single
station vs population-weighted national; full-sample normal leaking future years
if reused as a feature; observed weather vs the forecast a real trader would have
had at the origin; W-FRI alignment slippage.

## 9. Next questions

List 3 concrete questions you would ask next (e.g. "Does a population-weighted
multi-region HDD track price better than one station?", "How much does using a
past-only normal change the anomaly?", "What does the HDD–price relationship look
like once storage level is conditioned on?").
