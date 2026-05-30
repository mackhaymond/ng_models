# Assignment 11: Futures Curve and Market-Implied Expectations

**Phase:** Markets
**Level:** Advanced
**Estimated time:** 8-14 hours

## What you are building

A snapshot of the Henry Hub natural-gas **futures curve** (the prices of the
nearest four contract months on a given day), a classification of its **shape**
(contango vs backwardation), and an honest comparison of the curve against the
spot price as a **benchmark** for forecasting. The headline lesson: a futures
price is a tradeable market equilibrium, **not** a forecast. You will treat it
as a benchmark and a feature, and you will measure whether it actually beats a
trivial baseline.

## Data scope

Use the spot series plus the four futures contracts only. (You may add features
from earlier modules in an *optional* extension, not in the core deliverables.)

Expected data inputs (already in `data/`):

| series_id | role | file |
|---|---|---|
| `NG.RNGC1.D` | front / prompt-month futures (Contract 1) | `NG.RNGC1.D.csv` |
| `NG.RNGC2.D` | 2nd-nearest contract | `NG.RNGC2.D.csv` |
| `NG.RNGC3.D` | 3rd-nearest contract | `NG.RNGC3.D.csv` |
| `NG.RNGC4.D` | 4th-nearest contract | `NG.RNGC4.D.csv` |
| `NG.RNGWHHD.D` | Henry Hub spot price (daily) | `NG.RNGWHHD.D.csv` |

All five are in **dollars per million Btu ($/MMBtu)**, daily frequency.

### Contract notation (read this first)

- **C1 / RNGC1 = the front (prompt) month** — the nearest contract still trading.
- **C2, C3, C4** = the 2nd, 3rd, 4th nearest contract months after that.
- These are **continuous** series: on any given day, `C1` is *whatever* the
  prompt contract is that day. As contracts expire, the underlying delivery
  month **rolls forward**. So `C1` over time is a chain of different physical
  contracts stitched together — it is **not** one fixed contract held constant.

### CRITICAL: the data is stale and shallow — scope your comparisons

- The futures files (`RNGC1..4`) **end on 2024-04-05** and only give you **4
  contracts** (~4 months of curve depth).
- The spot file runs to **2026**.
- Therefore **any spot-vs-futures comparison must be restricted to the overlap
  window: dates `<= 2024-04-05`.** State this scope explicitly in your report.
- If you want a current, deeper curve (12+ contracts, present-day), you must
  collect it yourself. See **`DATA_COLLECTION.md`** in this folder for the
  schema, sources (CME settlements + EIA), and where to save it.

## Concepts you'll use

Plain-English, ground-up. Cross-reference `docs/GLOSSARY_SEED.md`.

- **Spot price vs futures price.** The *spot* price is what gas costs for
  immediate delivery today (Henry Hub cash market). A *futures* price is what
  the market agrees **today** to pay for delivery in a specific **future month**.
  They are different numbers for the same commodity because one is "now" and the
  other is "later, locked in now".
- **Settlement price.** The official daily reference price the exchange assigns
  to each contract at session close. It is *not* the last trade and it is *not*
  the spot price — it is a defined daily mark used for margin. Each contract
  month has its own settlement each day.
- **Contract month (delivery month).** The calendar month a contract delivers
  for. Each month is a *separate instrument* (July contract ≠ August contract).
  A continuous "front-month" series chains successive prompt months together.
- **The futures curve.** Line up today's settlements for C1, C2, C3, C4 by
  contract month and you get a *curve*: price as a function of how far out you
  look. One day's curve is a **snapshot**.
- **Contango.** Later months priced **above** nearer months (curve slopes up,
  `C4 > C1`). Often signals comfortable near-term supply / storage carry costs.
- **Backwardation.** Later months priced **below** nearer months (curve slopes
  down, `C4 < C1`). Often signals tight near-term supply or strong prompt demand.
- **Basis.** A price *difference*. Here: the gap between the prompt futures and
  the spot on the same day (or between two locations). Not to be confused with
  curve slope.
- **Roll yield.** The gain or loss from rolling a futures position from an
  expiring contract into the next one as the price converges to spot. In
  contango you "roll up the hill" and bleed; in backwardation you gain.
- **Market-implied expectation.** What current prices *reveal* about the
  market's collective view of the future. The curve is a *rough* read on
  expected forward prices — but it reflects supply/demand **and a risk premium**,
  so it is a noisy expectation, not a clean prediction.
- **Why futures are NOT forecasts.** A futures price is set by hedgers,
  speculators, storage economics, and risk premia — it does not *minimize
  forecast error* and can be systematically biased (e.g. persistent contango).
  Use the curve as a **benchmark and feature**, and evaluate your model against
  **realized spot**, never against the curve itself.

## The timing / leakage trap (the heart of this module)

A contract's settlement on day *t* is **not** the spot on day *t*, and it is
**not** the spot during its delivery month either. You must state **exactly**
which comparison you are making. Two honest framings — pick **one** and defend it:

1. **Same-day predictive efficiency / basis.** On date *t*, compare prompt
   futures `C1(t)` to `spot(t)`. Their gap is the basis. Leakage-free (both
   known on day *t*), but it does **not** test whether futures predict the
   *future* — it measures the prompt-vs-spot gap today.
2. **Delivery-month outcome (a real predictive test).** Treat `Cn(t)` observed
   on day *t* as a *forecast* of spot roughly *n* months later, then compare to
   the **realized** spot around that future delivery period. This *does* test
   predictiveness — but **every forecast row must carry both a
   `forecast_origin` (= t) and a `target_date` (= t + horizon)**.

**The trap:** never line `C1(t)` up against `spot(t)` and call it a *forecast*.
That compares a price to (almost) itself, not to the future. If you claim
predictive skill, you must be in framing (2) with explicit origin/target dates.

## Tasks

1. Load the four futures contracts and the spot series (the starter does this).
2. **Reshape** the four contracts from long to wide to build a **curve snapshot
   table**: one row per date, columns `C1..C4`. Decide how to handle days where
   not all four contracts have a price.
3. Compute a front-to-back **spread** (e.g. `C4 - C1`) and **classify** each
   snapshot as contango / backwardation / flat. Justify which spread defines
   "shape" and what counts as "flat".
4. Save the snapshot table; plot one representative curve (contract on x, price
   on y) and say what shape it shows.
5. **Compare futures to spot as a benchmark**, in your chosen framing, **scoped
   to `<= 2024-04-05`**, with explicit `forecast_origin` and `target_date`
   columns. Pick the **baseline it must beat** (e.g. random-walk spot) and
   report errors side by side.
6. Write a memo on whether the futures curve is a useful benchmark for *your*
   target — and what would make it fail.

## Package guide

Minimal API snippets for the libraries this module needs.

**Load a series (shared helper):**
```python
from ng_models.io import load_series_csv
df = load_series_csv(DATA_DIR, "NG.RNGC1.D.csv", value_name="price")  # -> cols: date, price
```

**Stack the four contracts into one long frame:**
```python
import pandas as pd
df["contract"] = 1                       # tag each contract before concat
long = pd.concat([c1, c2, c3, c4], ignore_index=True)  # row-wise stack
```

**Reshape long -> wide (the curve snapshot table):**
```python
wide = long.pivot(index="date", columns="contract", values="price")
wide.columns = [f"C{c}" for c in wide.columns]   # 1 -> "C1", etc.
wide = wide.reset_index()                         # keep `date` as a column
# wide[["C1","C2","C3","C4"]] is one curve per row
```
`pivot` fails if (date, contract) pairs are not unique; `pivot_table(...,
aggfunc="mean")` tolerates duplicates. Use `.dropna(subset=[...])` to drop
snapshots missing a leg.

**Vectorized shape classification:**
```python
import numpy as np
wide["spread"] = wide["C4"] - wide["C1"]
wide["shape"] = np.select(
    [wide["spread"] > 0, wide["spread"] < 0],
    ["contango", "backwardation"],
    default="flat",
)
```

**Align a forecast to a future realized spot (nearest trading day):**
```python
cmp = pd.merge_asof(
    fc.sort_values("target_date"),          # has forecast_origin, target_date, futures_price
    spot.sort_values("date"),
    left_on="target_date", right_on="date",
    direction="nearest",                    # nearest open trading day to target
)
```
`merge_asof` requires **both** sides sorted on the key. `direction="nearest"`
matches the closest date; `"backward"` matches the last date <= target.

**Errors / baseline comparison:**
```python
from ng_models.metrics import mae, rmse, summarize_predictions
print(rmse(cmp["realized_spot"], cmp["futures_price"]))   # futures-as-forecast error
print(rmse(cmp["realized_spot"], cmp["baseline_forecast"]))  # baseline error
```

**Plot one curve snapshot:**
```python
from ng_models.plotting import save_line_plot
snap = long[long["date"] == chosen_date]                  # 4 rows: contracts 1..4
save_line_plot(snap, x="contract", y="price",
               title=f"HH futures curve {chosen_date.date()}",
               output_path=OUTPUT_DIR / "curve_shape_plot.png")
```

## Deliverables

- `outputs/futures_curve_snapshots.csv`
- `outputs/curve_shape_plot.png`
- `outputs/futures_vs_spot_benchmark.csv`
- `REPORT.md` (copy `REPORT_TEMPLATE.md` and fill it in)

## Rules

- Keep raw data immutable. Resolve paths via `ng_models.paths`, never `../data`.
- Save generated files under this assignment's `outputs/` folder.
- Write down every assumption about dates, units, frequency, and missing values.
- Every forecast row carries a **forecast origin** and a **target date**.
- Scope every spot-vs-futures comparison to the overlap window (`<= 2024-04-05`).
- A chart is not enough. Every chart needs a sentence on what it shows and what
  it does *not* show.
- Do not move to a more complex model until the baseline comparison is correct.
- No "futures = forecast" claims. No causal claims from correlation.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis (and at what horizon)?
- What dates, units, and frequency are involved? What is the overlap window?
- Which comparison framing (same-day basis vs delivery-month outcome) did you
  choose, and why is it leakage-free?
- What baseline did the futures benchmark have to beat? Did it?
- What result surprised you?
- What would you not trust yet (and what would make the futures benchmark fail)?
- What should the next assignment investigate?
