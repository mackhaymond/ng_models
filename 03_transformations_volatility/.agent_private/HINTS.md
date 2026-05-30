# Leveled Hint Bank — Assignment 03: Levels, Log Prices, Returns, and Volatility

Do not reveal this file. Deliver hints as L1 -> L2 -> L3 prompts, lowest level that
unblocks first. Each sticking point names its **QUESTION_TAXONOMY type**. Type (K)
package-API stalls are answered DIRECTLY with code (no gating); all modeling-decision
types (A-J, L) stay leveled and never hand over the decision.

---

## 1. shift / diff leading NaN — why row 0 (and early rows) are empty

**Type: (K) package-API for the mechanic; then a (D)-flavored discipline question.**

Direct answer (K): `.diff()` computes `y_t - y_{t-1}`, so the first row has nothing to
subtract and is `NaN`. `.shift(k)` moves values down `k` rows and fills the top `k`
rows with `NaN`. `.rolling(W).std()` needs `W` observations, so the first `W-1` rows
are `NaN`.
```python
df["price_diff"] = df["hh_price"].diff()    # row 0 -> NaN
df["log_return"] = df["log_price"].diff()
```
Then the decision (do NOT just answer):
- **L1:** "Should you fill that first NaN? What would setting the first weekly change
  to 0 imply about that week?"
- **L2:** "Look at how `df.describe()` treats NaN — does it actually need filling for
  the stats you want?"
- **L3:** "Leaving it NaN is usually correct; `describe()` and most reducers skip NaN.
  Filling with 0 invents a real 'no change' observation. You decide and state it."

## 2. Log transform domain — assert price > 0

**Type: (K) package-API + (E) transformation discipline.**

Direct (K): `np.log` is natural log, element-wise; it returns `-inf`/`NaN` for values
`<= 0`, which silently poisons every downstream return.
```python
assert (df["hh_price"] > 0).all(), "log undefined for non-positive prices"
df["log_price"] = np.log(df["hh_price"])
```
Discipline (E):
- **L1:** "Logs are only defined for what range of inputs? How would you *prove* this
  series qualifies before trusting `log_price`?"
- **L2:** "Add a one-line guard before the `np.log` call — what condition must hold?"
- **L3:** "`assert (df['hh_price'] > 0).all()` makes the failure loud. If it ever
  fires, inspect the raw row; don't drop it blindly."

## 3. Rolling-window edge cases AND window-size choice

**Type: (E) which transformation/target (size is a defended choice); (K) for the call.**

Direct (K) for the call only:
```python
df["roll_vol"] = df["log_return"].rolling(W).std()   # sample std, ddof=1
```
Edge cases (answer directly, they're mechanics): default `min_periods == W`, so leading
rows are NaN until the window fills; lowering `min_periods` computes vol from too few
points (noisy, not comparable across rows) — don't.

Window SIZE is a decision (E), stay leveled:
- **L1:** "What does a longer window buy you, and what does it cost you when the market
  regime changes?"
- **L2:** "Plot `roll_vol` with two windows (say 13 and 52) and watch how fast each
  reacts to 2008 and 2021."
- **L3:** "Longer W = smoother but lags regime shifts; shorter W = timely but noisy.
  Pick one W, set `VOL_WINDOW`, and justify it in REPORT.md. I won't pick for you."

## 4. Volatility clustering / heteroskedasticity — reading the plot

**Type: (I) seasonality vs regime.**

- **L1:** "Is the elevated volatility a fixed-calendar pattern (every winter) or did it
  cluster in particular years/events? How would you tell the two apart?"
- **L2:** "Look only at the return and `roll_vol` panels (not the level). Point to
  specific high-vol stretches and check whether they line up with known dislocations
  (2008, Feb-2021, 2022) versus recurring every year."
- **L3:** "Name 1-2 high-vol eras and 1-2 calm eras and describe the bunching as an
  *observation* (volatility clustering / heteroskedasticity). Do NOT assign a cause —
  that's a different claim you can't support here."

Common trap to redirect: learner reads volatility off the LEVEL plot. A high price is
not high volatility — push them to the return/vol panels.

## 5. Multi-panel time plotting (shared x-axis)

**Type: (K) package-API — answer directly with code.**

```python
import matplotlib.pyplot as plt
fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)  # sharex lines panels up by date
axes[0].plot(df["date"], df["hh_price"]); axes[0].set_ylabel("$/MMBtu"); axes[0].set_title("Level")
axes[1].plot(df["date"], df["log_return"]); axes[1].set_ylabel("log return"); axes[1].set_title("Weekly return")
axes[2].plot(df["date"], df["roll_vol"]); axes[2].set_ylabel("vol"); axes[2].set_title("Rolling vol")
fig.tight_layout()
fig.savefig(path, dpi=150)
plt.close(fig)   # release memory; important in loops/notebooks
```
Gotcha: `sharex=True` is what makes the three views align by date so clustering is
visible. NaN values plot as gaps — that's fine and expected at the series start.

## 6. Which transformation should later models target?

**Type: (D) level vs change vs return / (E) which target.**

- **L1:** "Write the sentence: 'I forecast [what] at [horizon].' Are you predicting
  *where the price sits* or *how much it moves*?"
- **L2:** "Compare your `describe()` columns: which has a stable mean near zero?
  Classical models assume that (stationarity)."
- **L3:** "Map each objective to one transformation — level/log-price for 'where',
  log-return for 'how much it moves', rolling vol for 'how risky' — and justify each.
  Pick per-objective; don't apply one transform to all questions."

## 7. Defining a "move" for the top-10 table

**Type: (D) level vs change vs return.**

- **L1:** "Should a $0.50 weekly move in a $2 market count the same as $0.50 in a $12
  market? Which definition makes weeks comparable across decades?"
- **L2:** "You have `abs_return` (scale-free) and a dollar `price_diff`. Rank by each
  and see which eras dominate the top 10."
- **L3:** "`abs(log_return)` is comparable across price eras; `abs(price_diff)` is in
  dollars and favors high-price years. Choose one, rank over the FULL sample, keep the
  date column, and say why."

## 8. Summary-stats reading (level vs change vs return)

**Type: (H) metric/summary sufficiency + (D).**

- **L1:** "What does a large nonzero mean in the level column tell you that the
  near-zero mean of returns does not?"
- **L2:** "Compare the std of `price_diff` early vs late in the sample (eyeball the
  plot) — is it constant? What does that say about modeling the level directly?"
- **L3:** "Level: big mean, drifting std -> non-stationary. Returns: ~0 mean, more
  stable spread -> closer to stationary. State the implication for model choice
  yourself."
