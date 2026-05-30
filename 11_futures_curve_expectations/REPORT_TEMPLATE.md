# Report — Assignment 11: Futures Curve and Market-Implied Expectations

> Copy this file to `REPORT.md` and fill every section. Replace bracketed
> prompts with your own content. Cross-reference `docs/GLOSSARY_SEED.md`.

## 1. Objective

In 2-4 sentences: what are you analyzing, at what horizon, and what is the one
question you want the futures curve to answer? State plainly that futures are a
**benchmark/feature**, not a forecast you trust by default.

## 2. Vocabulary

Write each in your own words (1-2 sentences). Guidance in brackets.

- **futures:** [a price agreed today for delivery in a specified future month]
- **settlement:** [the exchange's official daily reference price; not the last trade, not the spot]
- **contract month:** [the delivery month; each month is a separate instrument; C1 = prompt]
- **basis:** [a price difference — here, prompt futures minus spot on the same day, or a location gap]
- **contango:** [later months priced above nearer months; curve slopes up]
- **backwardation:** [later months priced below nearer months; curve slopes down]
- **curve shape:** [the pattern across C1..C4 on one day; summarized by a front-to-back spread]
- **roll yield:** [gain/loss from rolling an expiring contract into the next as price converges to spot]
- **market-implied expectation:** [what the curve reveals about forward prices; reflects supply/demand AND a risk premium, so noisy]

## 3. Data used

Fill the table. Example rows provided.

| Source / file | Frequency | Units | Date range | Why used |
|---|---|---|---|---|
| `NG.RNGC1.D.csv` (prompt futures) | daily | $/MMBtu | 1994-01-13 .. 2024-04-05 | front-month leg / benchmark |
| `NG.RNGC2..4.D.csv` | daily | $/MMBtu | .. 2024-04-05 | rest of the 4-month curve |
| `NG.RNGWHHD.D.csv` (spot) | daily | $/MMBtu | 1997-01-07 .. 2026-05-18 | realized outcome to evaluate against |

**Overlap window used for all spot-vs-futures comparisons:** [`<= 2024-04-05`]

## 4. Data decisions

State explicitly: how you parsed/sorted dates; how you handled snapshots missing a
contract leg; which front-to-back spread defines "shape" and your "flat"
threshold; **which comparison framing you chose** (same-day basis vs
delivery-month outcome) and **why it is leakage-free** (name your
`forecast_origin` and `target_date`); and any unit checks (all $/MMBtu).

## 5. Outputs checklist

- [ ] `outputs/futures_curve_snapshots.csv`
- [ ] `outputs/curve_shape_plot.png`
- [ ] `outputs/futures_vs_spot_benchmark.csv`
- [ ] `REPORT.md`

## 6. Results

Include: a few snapshot rows (date, C1..C4, spread, shape); the shape
distribution over the sample (how often contango vs backwardation); the plotted
curve and the date/shape it shows; and a baseline comparison table — example:

| Method | RMSE ($/MMBtu) | MAE ($/MMBtu) | Beats baseline? |
|---|---:|---:|---|
| Futures as forecast (Cn at origin) | [ ] | [ ] | [yes/no] |
| Baseline: random-walk spot(t) | [ ] | [ ] | — |

State the horizon and the number of forecast rows behind these numbers.

## 7. Interpretation

What do the results mean for NG modeling? Did the futures benchmark beat the
baseline at your horizon, and what does that imply about using the curve as a
forecast? Keep claims associational, not causal — contango/backwardation
*describe* the curve, they do not *cause* the spot outcome.

## 8. Model or analysis limitations

Address at minimum: the 4-contract / `<= 2024-04-05` scope and what it prevents
you from concluding; the risk premium embedded in futures (why they need not be
unbiased forecasts); roll/continuous-series effects on the prompt leg near
expiry; and **what single change would make the futures benchmark fail out of
sample?**

## 9. Next questions

List 3 concrete questions you would ask next (e.g. deeper curve via
`DATA_COLLECTION.md`, longer horizons, seasonality of the basis).
