# Report 01: Understanding Weekly Henry Hub

## Data Used

- File: NG.RNGWHHD.W.csv
- Unit: $/MMBtu
- Frequency: Weekly
- Date range: 1997-01-10 - 2026-05-15
- Number of observations: 1531

> Fill `Date range` and `Number of observations` from your own run
> (`df["date"].min()/.max()`, `len(df)`), not from memory.

## Summary Statistics

> Paste the values your script prints (`df["price"].describe()`). Then add one
> sentence on what the mean-vs-median gap implies (a fat right tail of spikes
> pulls the mean above the median). Example row shown; replace with your numbers.

| Statistic | Value |
| --- | ---: |
| Count | 1531 |
| Min | 1.34 |
| Max | 14.49 |
| Mean | 4.10 |
| Median | 3.37 |
| Standard deviation | 2.16 |

## Full-Sample Price Behavior

![Weekly Henry Hub price](HH_price_weekly.png)

Notes:

- Data has no general trend but generally stays low with spikes for periods of time
- Abnormal periods can be seen from around 2001 until 2003, and then again at the beginning of 2004, as well as 2006-2007, and 2008-2009, at the beginning of 2022, and most recently at the beginning of 2026, each of which showed a spike.
- Periods of high volatility are from 2000-2010, and then again from 2021-presentPeriods of high volatility are from 2000-2010, and then again from 2021-presentPeriods of high volatility are from 2000-2010, and then again from 2021-present

## Seasonality

![Averaged Price by Week of Year](./HH_average_price_by_week.png)

Notes:

- Average prices are higher in winter months and lower/flatter in summer months
- A median-by-week graph could be useful to see if spike years as described above impact this graph
-

## Outliers And Regimes

> List the 2-4 most extreme weeks/periods you can see on the full-sample plot, each
> with an approximate date and price, and a one-line candidate explanation (cold-
> weather demand, supply shock, etc.). State it as an observation, not a proven cause.
> Example: `~Aug 2022, ~$9-10/MMBtu -- coincides with the European energy crisis /
> strong LNG export pull (association, not a proven cause).`

Largest spikes / unusual periods:

- 
-
-

> A regime is a period where the average LEVEL and the VOLATILITY shift and stay
> shifted (different from the within-year seasonal cycle). Give each one a rough
> date range and a one-line label.

Possible regimes:

- 2000-2010 - pre-shale 
- 2010-2020 - shale era
- 2021-present - non-regime, colored by relatively constant supply/demand shocks

## Modeling Implications

Does forecasting price level directly seem reasonable?
Yes, but only within periods of about 10 years, as that tends to be how often an HH price regime changes and the model needs to change.

Does a seasonal baseline seem promising?
Yes, as a benchmark - natural gas demand is seasonal, and regardless of the data shown here, longer term data demonstrates that HH prices move seasonally with NG demand.

What risks might make a simple seasonal model fail?
Training on an old regime is the largest I'd guess.

## First Benchmark Recommendation

> One sentence, in the exact form below. Name a specific baseline (naive / random
> walk, seasonal-naive, rolling mean, or simple ETS) and justify it from YOUR two
> plots -- e.g. tie it to whether the seasonal shape is robust and how much variation
> is spike/regime-driven. This is the baseline your later models must beat.

My first benchmark model should be ___ because ___.

## Questions For Review

> List 2-3 things you are unsure about or want a reviewer to challenge -- e.g. "is
> the week-of-year mean misleading because of 2008/2022?" or "should I model returns
> instead of the price level?".

-
-
-
