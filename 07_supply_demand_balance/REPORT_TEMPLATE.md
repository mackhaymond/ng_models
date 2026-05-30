# Report — Assignment 07: Supply-Demand Balance: Production, Consumption, Trade, and LNG

## 1. Objective

In 2-4 sentences: what balance are you assembling, over what date range and unit,
and what question about price regimes are you trying to answer? State the balance
identity (production + imports = consumption + exports + storage change) and which
terms you actually measured vs. inferred.

## 2. Vocabulary

Write 1-2 sentences each, in your own words.

- **dry gas production:** Pipeline-quality gas after liquids/impurities removed; the supply number you usually model.
- **marketed production:** Gross gas removed minus reinjected/vented/flared gas; larger than dry, before NGL stripping.
- **consumption:** Total gas burned/used domestically across sectors in the period.
- **electric power burn:** Gas consumed to generate electricity; the weather- and price-sensitive swing component of demand.
- **industrial demand:** Gas used by industry (feedstock, process heat); relatively steady, less weather-driven.
- **residential/commercial demand:** Gas for heating/cooking in homes and businesses; strongly seasonal (winter peak).
- **exports:** Gas leaving the U.S. (pipeline to Mexico/Canada plus LNG by ship).
- **LNG:** Liquefied natural gas; here it appears split by terminal/destination, with no single national monthly series.
- **balance:** The accounting identity tying supply, demand, and trade to the change in storage over a period.

## 3. Data used

| Source / file | Series ID | Frequency | Units | Date range | Why used |
|---|---|---:|---|---|---|
| `NG.N9070US2.M.csv` | NG.N9070US2.M | Monthly | MMcf | 1997-01 to 2026-02 | Dry production = pipeline-quality supply |
| `NG.N9140US2.M.csv` | NG.N9140US2.M | Monthly | MMcf | 2001-01 to ... | Total demand side of the balance |
| `NG.RNGWHHD.W.csv` | NG.RNGWHHD.W | Weekly->Monthly | $/MMBtu | 1997-01 to ... | Price; aggregated to monthly (mean) |
| _add imports, exports, any LNG you summed_ | | | | | |

## 4. Data decisions

State explicitly:
- **Unit choice:** which unit the whole panel is in (MMcf or Bcf) and any conversion.
- **Price aggregation:** mean vs. last of the month, and why.
- **Join:** inner vs. outer, and what the resulting date range is (driven by the
  latest-starting series).
- **Publication lag:** the lag `k` (months) you applied to fundamentals before
  any comparison to price, and your justification.
- **Missing values / LNG handling:** how you treated gaps and the LNG gap.

## 5. Outputs checklist

- [ ] `outputs/monthly_balance_panel.csv` (one row per month; date, components, price)
- [ ] `outputs/balance_components.png` (with a caption sentence)
- [ ] `outputs/balance_correlations.csv`
- [ ] `REPORT.md`

## 6. Results

Include: (a) a few rows of the panel showing the balance columns and price; (b)
the YoY/MoM comparison for each component over your chosen regime(s); (c) the
correlation table. Reference the saved plot and write one sentence on what it
shows and one on what it does not.

Example panel row (illustrative -- replace with your real numbers):

| date | dry_production_mmcf | consumption_mmcf | imports_mmcf | exports_mmcf | net_exports_mmcf | hh_price |
|---|---:|---:|---:|---:|---:|---:|
| 2021-02-01 | 2,510,000 | 3,420,000 | 230,000 | 540,000 | 310,000 | 5.35 |

## 7. Interpretation

For your selected price regime(s) (e.g. the 2021 winter spike, the 2020 lows,
the 2022 LNG-driven highs), state which side of the balance moved most and by how
much (in level and YoY). Tie it back to the identity: if demand jumped while
production was flat, the implied storage draw should be large. Avoid "because" /
"causes" unless you have named and addressed the confound.

## 8. Model or analysis limitations

What could be wrong, incomplete, unstable, or leaked? Address at least:
- the **publication lag** and whether your price comparison is leak-free,
- EIA **revisions** of monthly data,
- the **missing storage term** (you inferred it, not measured it),
- the **LNG gap** (no clean national monthly series),
- whether any correlation is just a **shared trend** (shale era).

## 9. Next questions

List 3 concrete questions you would ask next (e.g. "Does adding the actual EIA
storage series close the balance residual?", "How does the publication lag change
the price correlation?", "Which sector of consumption drove the 2021 jump?").
