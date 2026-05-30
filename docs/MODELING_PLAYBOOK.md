# Modeling Playbook

## Before modeling

1. Define the target.
2. Define the forecast origin.
3. Define the horizon.
4. List every candidate feature.
5. For each feature, write:
   - source
   - unit
   - frequency
   - transformation
   - publication/availability assumption
   - **feature timing:** state *when* this feature was known (its publication
     lag) and check that the lag aligns with your forecast timing. Example: to
     forecast next week's Henry Hub price using storage, you may only use the
     storage release that was already public at your forecast origin — Thursday's
     release describes the prior Friday, so shift it before joining. If a feature
     would only be known *after* the moment you forecast, you cannot use it.
6. Choose a baseline.
7. Choose metrics.

## Forecasting checklist

- Is this a level, change, return, event, or interval forecast?
  - **level:** predict the price itself, e.g. "next week HH = $3.10/MMBtu".
  - **change:** predict the difference from now, e.g. "+$0.20/MMBtu vs this week".
  - **return:** predict the percent change, e.g. "+6.5%" (a $3.00 → $3.195 move).
  - **event:** predict a yes/no or category, e.g. "P(weekly price spike > +15%)".
  - **interval:** predict a range, e.g. "80% chance next week lands in
    $2.90–$3.40/MMBtu" rather than a single point.
- Is the split time ordered?
- Are all rolling statistics computed using only past data?
- Are exogenous features lagged enough to be known?
- Are missing values explained?
- Does the model beat a simple baseline?
- Does performance hold across seasons/regimes?
- What is the largest error and why did it happen?
- For interval forecasts: judge **coverage vs width** together. Coverage = how
  often the true value lands inside the interval (an 80% interval should contain
  the actual ~80% of the time); width = how wide the interval is. A wide interval
  trivially gets high coverage but says little; aim for the narrowest interval
  that still hits its target coverage.

## Natural-gas analysis checklist

- What happened to storage relative to normal?
- Was the market in injection or withdrawal season?
- Was weather unusually hot/cold?
- Did production, LNG exports, or power burn shift?
- Is the move local/regional or broad U.S.?
- Did the futures curve already price the move?
