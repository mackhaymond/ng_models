# Report — Assignment 13: Power Markets, Gas Burn, and ISO Demand (OPTIONAL)

## 1. Objective

In 2-4 sentences: which ISO/region you examined, which power metric (load or gas
generation), what gas series you compared it against, and the one question you
were testing (e.g. "does ERCOT summer load, lagged, co-move with weekly HH?").

## 2. Vocabulary

Write 1-2 sentences each, in your own words (see `docs/GLOSSARY_SEED.md`).

- **ISO:** The operator/market for one grid *region* (a set of states), e.g.
  ERCOT = Texas. Defines the regional scope of your data.
- **load:** Electricity demand in MW; swings with weather and time of day.
- **generation mix:** Which fuels are generating now (gas, wind, solar, ...).
- **gas burn:** Gas consumed to make electricity; a major, swing component of
  gas demand.
- **spark spread:** A gas plant's rough margin: `power_price - heat_rate*gas_price`;
  wide spread -> plants run -> more burn.
- **power demand:** Same idea as load; the electricity the grid must serve.
- **renewables displacement:** Wind/solar pushing gas off the dispatch stack,
  cutting gas burn even at constant load.
- **dispatch:** The order plants are turned on (cheapest first); gas is often
  the marginal unit absorbing swings.

## 3. Data used

| Source / file | Frequency | Units | Date range | Why used |
|---|---|---|---|---|
| `gridstatus ERCOT get_load` | hourly (native) | MW | 2023-06-01 .. 2023-09-01 | regional power-demand signal |
| `NG.RNGWHHD.W.csv` | weekly | $/MMBtu | overlap window | national price benchmark |
| *(example proxy row)* `NG.N3045TX2.M.csv` | monthly | MMcf | 2001-01 .. 2026-02 | EIA power-gas proxy if no gridstatus |

Replace the example rows with what you actually used. Record source URL +
download date for any external (`gridstatus`) data.

## 4. Data decisions

Describe, with justification:
- Date parsing and timezone handling for ISO timestamps.
- The frequency aggregation chosen (mean / sum / max) and *why* for this quantity.
- The **lag** applied to the power feature and the reasoning (what was knowable at
  the forecast origin / publication delay for EIA data).
- Joins (inner vs outer) and how you handled missing weeks (no silent fill).

## 5. Outputs checklist

- [ ] `outputs/iso_weekly_power.csv` (or `outputs/proxy_power_gas_vs_hh.csv`)
- [ ] `outputs/power_load_or_fuelmix.png`
- [ ] `REPORT.md`

## 6. Results

Report the co-movement you found: the correlation between the **lagged** power
metric and HH, the number of overlapping periods, and the plot reference. State
the number plainly, e.g. "lagged ERCOT weekly load vs weekly HH: r = +0.2X over
N = __ weeks." If you built any forecast, give the metric **relative to a stated
baseline** (skill score), not a raw number alone.

## 7. Interpretation

What does the co-movement mean for gas modeling -- and what does it NOT mean?
Address the **causality boundary** explicitly: a regional series correlating with
the national price is a hypothesis; name the confounds (weather, storage) that
could drive both. Note whether renewables displacement (load vs gas-share)
changes the story.

## 8. Model or analysis limitations

What could be wrong, incomplete, unstable, or leaked? Required to address:
- **Leakage:** did any same-period power data sneak into the feature?
- **Scope:** one region vs a national benchmark -- why might it not generalize?
- **Frequency:** information lost by aggregating hourly to weekly.
- **Sample size:** a single season is a small, regime-specific window.

## 9. Next questions

List 3 concrete questions you would ask next (e.g. "Does gas *share* of
generation beat raw load as a feature?", "Does the relationship hold in winter?",
"Would a national power-burn aggregate beat one ISO?").

## 10. Decision: core model or stay optional?

State your call and defend it in 2-3 sentences. A regional feature that does not
beat a national naive baseline, or that risks leakage, should stay optional.
