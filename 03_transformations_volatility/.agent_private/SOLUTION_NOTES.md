# Private Solution Notes — Assignment 03: Levels, Log Prices, Returns, and Volatility

Do not reveal this file during normal tutoring. Use it to decide whether the learner's
reasoning is on track and to deliver the right level of hint.

## Reference approach (worked sketch)

Input: `data/NG.RNGWHHD.W.csv`, weekly Henry Hub spot, $/MMBtu, ~1997-01-10 to present
(~1531 rows). load_series_csv returns `date` (datetime64) + `hh_price` (float), sorted.

`add_transformations` (the reference fill-in of the TODOs):
```python
df = hh.copy()
assert (df["hh_price"] > 0).all()
df["log_price"]  = np.log(df["hh_price"])
df["price_diff"] = df["hh_price"].diff()          # row 0 NaN, leave it
df["log_return"] = df["log_price"].diff()         # == np.log(y/y.shift(1))
df["abs_return"] = df["log_return"].abs()
df["roll_vol"]   = df["log_return"].rolling(VOL_WINDOW).std()   # first W-1 NaN
```

`top_absolute_moves` (reference): rank on `abs_return` over the full sample:
```python
out = (df.dropna(subset=["abs_return"])
         .sort_values("abs_return", ascending=False)
         .head(n)[["date", "hh_price", "log_return", "abs_return"]])
```
`abs(log_return)` is the defensible default because it is comparable across price eras;
`abs(price_diff)` is also acceptable IF the learner states it favors high-price years.

`plot_volatility_panels` (reference): `plt.subplots(3, 1, sharex=True)` with level,
log_return, roll_vol stacked; titles + y-labels; tight_layout; savefig dpi=150; close.

## Expected results / ranges (Henry Hub weekly, full sample)

Concrete numbers on the shipped full sample (1997-01-10 .. 2026-05-15, 1531 rows):

- **Level (`hh_price`)**: mean ~$4.10/MMBtu, std ~$2.16, min ~$1.34, max ~$14.49. Big
  nonzero mean, clearly drifting — non-stationary.
- **`price_diff`**: mean ~0.00, std ~$0.63, but the dollar-move std is NOT constant
  across eras (moves were bigger when price was high) — itself heteroskedastic.
- **`log_return`**: mean ~0.000, weekly std ~0.11. Extreme weeks reach |log_return| ~
  0.6-1.45 (the Feb-2021 winter storm Uri weeks and a Jan/Feb-2026 cold snap are the
  largest). Much closer to stationary in mean; spread still clusters — the point of the
  vol plot.
- **`roll_vol` (52w)**: exactly 52 leading NaNs (window not yet full), then visibly
  time-varying — elevated around 2001, 2003, 2008-09, 2021, 2026; calmer in long
  stretches of the 2010s. This IS the volatility-clustering evidence.
- **Top absolute moves** (on `abs_return`) cluster in winter cold-snap weeks — the top
  few are 2021-02-26, 2026-01-23, 2026-02-06, 2021-02-19, 2024-01-12. Clustered in a
  few eras, not spread evenly.

If the learner's numbers are wildly off (e.g. level mean ~0, or log_return std ~0.5+
with no spike weeks), suspect: returns computed on raw price instead of log; NaN filled
with 0; or sorting/parsing error.

## Module-specific common failure modes

- **First-row NaN filled with 0** — invents a zero-change week and biases stats; the
  correct move is to leave it NaN (describe() skips it).
- **Log return computed as `df["hh_price"].pct_change()` and called "log return"** —
  that's a simple return, not a log return; they diverge for large moves and don't add
  cleanly over time. Acceptable only if relabeled honestly.
- **`np.log` without the positivity assert** — fine on this series (all positive) but
  it's the discipline being taught; dock if missing.
- **Rolling vol with `min_periods=1`** (or otherwise back-filled) so early weeks get a
  vol from 1-2 points — noisy and not comparable; this is the leakage/edge-case trap.
- **Top moves ranked within a window or without dates** — must be full-sample and must
  carry the date.
- **Annualization confusion** — multiplying by 52 instead of sqrt(52), or annualizing
  silently without stating the unit.
- **Interpretation conflates targets** — saying "use returns" for a "where will price
  be in 12 weeks" question, or "use the level" for a "how risky" question.
- **Causal overreach** — "the cold snap caused the spike." This module only describes.
- **Reading volatility off the LEVEL plot** — a high price level is not high volatility;
  the learner must look at the return/vol panels.

## Assignment-specific hint strategy (L1 -> L2 -> L3)

The 5 key decision points and how to escalate (see QUESTION_TAXONOMY types in brackets):

1. **Which transformation is the target for which objective? [E/D]**
   - L1: "Are you forecasting *where the price will be* or *how big the move will be*?
     Which of level / log-price / return / vol matches that question?"
   - L2: "Compare your describe() table — which column has a stable mean near zero?
     That property is what classical models want."
   - L3: "Level/log-price answer 'where'; returns answer 'how much it moves'; rolling
     vol answers 'how risky'. Map each objective to one and justify — don't pick for them."

2. **Rolling-vol window size [E]**
   - L1: "What does a longer vs shorter window trade off? What do you lose with each?"
   - L2: "Plot roll_vol with two windows (e.g. 13 and 52) and look at how fast each
     reacts to 2008 / 2021."
   - L3: "`df['log_return'].rolling(W).std()`; longer W = smoother but lags regime
     shifts, shorter = noisier but timely. You pick W and defend it."

3. **Definition of 'move' for top-10 [D/E]**
   - L1: "Should a 50-cent move in a $2 market count the same as in a $12 market?"
   - L2: "You have both `abs_return` (scale-free) and the dollar `price_diff`. Rank by
     each and look at which decades dominate."
   - L3: "`abs(log_return)` is comparable across eras; `abs(price_diff)` is dollars and
     favors high-price years. Choose one, state why, rank full-sample with date."

4. **First-row / leading NaN handling [K then A-flavored discipline]**
   - K (direct): ".diff() and .rolling() produce leading NaNs because there's no prior
     value / not enough history."
   - Then ask (decision): "Should you fill those? What would filling the first diff with
     0 imply about that week?" Steer to leaving NaN; describe() skips them.

5. **Volatility clustering interpretation [I, seasonality vs regime]**
   - L1: "Is the elevated volatility a fixed-calendar thing, or did it cluster in
     particular years/events?"
   - L2: "Look at the roll_vol panel — point to specific high-vol periods and check if
     they line up with known dislocations (2008, 2021) vs every winter."
   - L3: "Name 1-2 high-vol and 1-2 calm eras and describe the clustering as an
     observation; do NOT claim a cause."

Type **K (package-API) questions** — how to call `np.log`, `.diff()`, `.shift()`,
`.rolling().std()`, `subplots(sharex=True)`, `.describe()` — are answered directly with
code (see HINTS.md). Everything in the 5 points above stays leveled.

## Agent response pattern

1. Identify the highest-impact issue first (data correctness > interpretation > style).
2. Ask the learner to explain their assumption.
3. Provide a hint at the lowest useful level (K = direct code; A-J/L = L1 first).
4. Re-run / re-check after revision.
