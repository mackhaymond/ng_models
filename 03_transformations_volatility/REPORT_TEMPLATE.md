# Report — Assignment 03: Levels, Log Prices, Returns, and Volatility

## 1. Objective

In 2-4 sentences, explain what this assignment is trying to learn.

## 2. Vocabulary

One plain-English sentence each, in your own words. Cross-check `docs/GLOSSARY_SEED.md`.

- **level:** *(example)* The raw weekly Henry Hub price in $/MMBtu — "where the price is right now."
- **log:** 
- **return:** 
- **difference:** 
- **volatility:** 
- **outlier:** 
- **stationarity:** 
- **heteroskedasticity:** 

## 3. Data used

| Source / file | Frequency | Units | Date range | Why used |
|---|---:|---|---|---|
| *(example)* `data/NG.RNGWHHD.W.csv` | weekly | $/MMBtu | 1997-01-10 to 2026-05-15 | the price series to transform |

## 4. Data decisions

Describe date parsing, missing values, joins, aggregation, lags, and any unit
conversions. State explicitly:
- How you handled the **first-row NaN** in `price_diff` / `log_return` (you left it NaN, you did not fill it — say so).
- Your **rolling-volatility window** and one sentence on why (smoothness vs. lag trade-off).
- Your **definition of "move"** for the top-10 table (`abs(log_return)` vs. `abs(price_diff)`) and why.
- Your **volatility units** (per-week log-return std, or annualized × sqrt(52)).
- Confirmation that you asserted `price > 0` before taking logs.

## 5. Outputs checklist

- [ ] `outputs/transformed_hh.csv`
- [ ] `outputs/volatility_plot.png`
- [ ] `outputs/top_moves.csv`
- [ ] `REPORT.md`

## 6. Results

Include:
- The **summary-stats table** for level vs. difference vs. log return. Which has a
  large nonzero mean? Which center near zero? Which has the most stable variance?
- The **top-10 absolute moves table** (must include the date of each move).

Example summary-stats row (yours will differ):

| series | count | mean | std | min | max |
|---|---:|---:|---:|---:|---:|
| `hh_price` (level) | 1531 | ~4.1 | ~2.2 | ~1.3 | ~14.5 |
| `log_return` | 1530 | ~0.00 | ~0.11 | (large negative) | (large positive) |

Example top-move row (yours will differ):

| date | hh_price | log_return | abs_return |
|---|---:|---:|---:|
| *(e.g. a winter-2021 / 2008-spike week)* | 5.xx | 0.4x | 0.4x |

## 7. Interpretation

Explain what the results mean for natural gas modeling:
- Which transformation should later models target for "where will the price be" vs.
  "how big is the next move", and why (tie back to stationarity).
- What the rolling-volatility panel shows about **volatility clustering** — name 1-2
  specific high-volatility periods and 1-2 calm periods.
- What each plot panel does **not** show.
- Avoid causal language: describe associations and patterns, not causes.

## 8. Model or analysis limitations

What could be wrong, incomplete, unstable, or leaked? Consider: window-choice
sensitivity, the leading NaNs, whether "top moves" cluster in a few eras, and whether
weekly sampling hides intra-week spikes.

## 9. Next questions

List 3 concrete questions you would ask next (e.g. seasonality of volatility, formal
stationarity tests, or which baseline a returns model must beat).
