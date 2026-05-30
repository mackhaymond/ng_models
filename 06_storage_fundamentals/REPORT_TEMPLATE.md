# Report — Assignment 06: Storage Fundamentals: Inventories, Seasonality, and Deviations

## 1. Objective

In 2-4 sentences, explain what this assignment is trying to learn. Name the object of
analysis (weekly Lower-48 working gas in storage), what you compute from it (seasonal
norm, deviation, injection/withdrawal flows), and the question you are probing (how
storage tightness relates to Henry Hub price — as association, not proven cause).

## 2. Vocabulary

Write 1-2 sentences each, in your own words (deepen, don't copy, `docs/GLOSSARY_SEED.md`).

- **working gas:** Gas in storage that can actually be withdrawn and sold, above the
  permanent base/cushion gas left in the ground to keep wells pressurized.
- **underground storage:** Reservoirs (depleted fields, aquifers, salt caverns) where
  gas is held between production and consumption to balance seasonal demand.
- **injection:** A net week-over-week ADD to storage (storage change > 0), typical of
  the low-demand summer season.
- **withdrawal:** A net week-over-week DRAW from storage (storage change < 0), typical of
  winter heating.
- **injection/withdrawal season:** Roughly Apr-Oct (injecting) vs. Nov-Mar (withdrawing);
  state the months you used and why the shoulder months matter.
- **five-year average / seasonal norm:** The average storage level for the same
  week-of-year across PRIOR years — your "normal" reference line. State exactly how many
  prior years you used and that no current/future data entered it.
- **inventory deviation:** Current storage minus the seasonal norm for the same week; the
  surplus (+) or deficit (-) the market actually watches.
- **storage constraint:** The physical ceiling (working-gas capacity) / floor that limits
  how fast gas can be injected or withdrawn; relevant near a full or very low system.

## 3. Data used

| Source / file | Series id | Frequency | Units | Date range | Why used |
|---|---|---:|---|---|---|
| `NG.NW2_EPG0_SWO_R48_BCF.W.csv` | NG.NW2_EPG0_SWO_R48_BCF.W | Weekly (Fri-ending) | Bcf | 2010-01-01 -> 2026-05-15 | Lower-48 working-gas anchor |
| `NG.RNGWHHD.W.csv` | NG.RNGWHHD.W | Weekly | $/MMBtu | (overlap from 2010) | Henry Hub spot price |
| *(optional regionals)* | NG.NW2_EPG0_SWO_R31..R35_BCF.W | Weekly | Bcf | 2010+ | Regional breakdown |

Add a row per series you actually loaded; pull units/frequency from the metadata.

## 4. Data decisions

Describe and JUSTIFY:
- **Join:** which alignment you used (recommended inner join on `date`, 2010+) and why it
  is safe here; note the `ffill` / `merge_asof` alternatives you rejected and when they'd
  be needed.
- **Publication lag:** state that EIA publishes Thursday for the prior-Friday week (~5-6
  day lag) and what that means — today's storage cannot explain an earlier price; if you
  built any predictive feature, how you lagged storage.
- **Seasonal norm window:** 5 prior years vs. all prior; how you handled early years with
  <5 priors; iso_week vs. month grain — and the leakage argument that it uses no
  current/future data.
- Missing values, the first-row NaN from `.diff()`, and any unit notes.

## 5. Outputs checklist

- [ ] `outputs/storage_panel.csv`
- [ ] `outputs/storage_seasonality.png`
- [ ] `outputs/hh_vs_storage_deviation.png`
- [ ] `REPORT.md`

## 6. Results

Report concrete numbers, not just "see the plot". Include at least:
- Count of injection vs. withdrawal weeks, and the months they fall in (table below).
- The size of a notable surplus/deficit (e.g. the largest deficit in Bcf and when).
- A sentence on each plot: what it shows and what it does NOT show.

Example flow-by-season table (fill with YOUR numbers):

| Season | Injection weeks | Withdrawal weeks |
|---|---:|---:|
| Apr-Oct | (e.g.) 372 | (e.g.) 24 |
| Nov-Mar | (e.g.) 31 | (e.g.) 281 |

If the off-season counts are large, your sign or season definition is likely wrong —
investigate before interpreting.

## 7. Interpretation

Explain what the deviation means economically: a deficit (below norm) is conventionally
bullish, a surplus bearish. State explicitly whether you are claiming correlation,
prediction, or causation — and what you would have to rule out (weather, production) to
claim more. One paragraph max; do not overstate.

## 8. Model or analysis limitations

What could be wrong, incomplete, unstable, or leaked? At minimum address: the
publication-lag leakage risk, the small number of prior years for the early-period norm,
Bcf-vs-$/MMBtu incommensurability, and that storage, price, and weather are mutually
confounded.

## 9. Next questions

List 3 concrete questions you would ask next (e.g., does the deviation lead price or lag
it? does adding weather/HDD explain the deviation? does the regional breakdown reveal
where the tightness is?).
