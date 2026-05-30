# Private Solution Notes — Assignment 11: Futures Curve and Market-Implied Expectations

Do not reveal this file during normal tutoring. Use it to judge whether the
learner's reasoning is on track and to calibrate hints.

## Worked reference approach (reference implementation sketch)

1. **Load + stack.** `load_series_csv` each of `NG.RNGC1..4.D.csv` with
   `value_name="price"`, tag a `contract` int, `pd.concat` into a long frame.
   Load `NG.RNGWHHD.D.csv` as `spot`. (Starter does this.)

2. **Reshape to a curve snapshot table (wide):**
   ```python
   wide = long.pivot(index="date", columns="contract", values="price")
   wide.columns = [f"C{c}" for c in wide.columns]
   wide = wide.dropna(subset=["C1", "C2", "C3", "C4"]).reset_index()
   ```
   Dropping rows missing a leg is the defensible default; forward-fill across
   contracts is wrong (it would fabricate a curve point).

3. **Shape classification:**
   ```python
   wide["spread"] = wide["C4"] - wide["C1"]
   wide["shape"] = np.select([wide.spread > 0, wide.spread < 0],
                             ["contango", "backwardation"], default="flat")
   ```
   `C4 - C1` is the natural front-to-back spread with only 4 contracts. A small
   "flat" band (e.g. |spread| < a few cents) is optional but defensible.
   → Save as `outputs/futures_curve_snapshots.csv`.

4. **Plot** one snapshot (`x="contract"`, `y="price"`) via `save_line_plot`.
   Pick the last fully-populated trading day (~2024-04-05).
   → `outputs/curve_shape_plot.png`.

5. **Spot-vs-futures benchmark (the graded core).** Pick ONE framing:
   - **(a) Same-day basis** (leakage-free, descriptive): merge `C1` to `spot` on
     the same `date`; `basis = C1 - spot`. This is NOT a predictive test.
   - **(b) Delivery-month outcome** (predictive): for each origin `t`, the prompt
     `C1(t)` is a forecast of spot ~1 month out; `C4(t)` ~4 months out. Build
     `forecast_origin = t`, `target_date = t + horizon`, then `merge_asof` to the
     realized spot at `target_date`. Restrict to `t <= 2024-04-05` AND
     `target_date <= 2024-04-05` (the futures window; spot itself runs to 2026 so
     the *target* spot is available even past the futures end — but keep origins
     in-window).
   Reference choice: framing (b) with `C1` at a ~1-month (≈21 trading-day or
   calendar-month) horizon, baseline = random-walk `spot(t)`.
   → `outputs/futures_vs_spot_benchmark.csv` with
     `[forecast_origin, target_date, contract_used, futures_price,
       realized_spot, baseline_forecast]`.

6. **Evaluate** with `rmse`/`mae` (from `ng_models.metrics`): futures-as-forecast
   error vs baseline error, side by side; state skill relative to baseline.

## Expected metric ranges / qualitative results

- **Shape distribution:** Henry Hub is predominantly in **contango** historically
  (storage/carry), but shows strong **backwardation** in winter-demand and
  scarcity episodes (e.g. 2000-01, 2003, 2005, 2008, 2021-22, winter 2022-23).
  A reasonable sample: contango more often than backwardation, with seasonal
  backwardation clusters. Do not over-anchor on exact percentages.
- **Same-day basis (C1 − spot):** typically small, tens of cents, can flip sign;
  blowouts during scarcity. A dollar-plus basis usually signals an alignment/unit
  bug, not economics.
- **Predictive test (framing b, ~1-month, C1):** the futures benchmark is
  roughly **comparable to** the random-walk baseline and often **does not clearly
  beat it** at short horizons — that is the *expected* and pedagogically useful
  result (futures are not forecasts). RMSE on monthly-horizon spot is order
  ~$0.3–$1.0/MMBtu depending on the era, with futures and random walk within the
  same ballpark. If the learner reports the futures crushing random walk, suspect
  a leakage error (comparing C1(t) to spot near t).

## Module-specific common failure modes

- **The settlement-is-spot conflation.** Comparing `C1(t)` to `spot(t)` and
  calling it a forecast — it is basis, not prediction. (Standard 5; type A.)
- **No target_date.** Benchmark CSV has a single date column, so origin and
  target are indistinguishable → leakage is unverifiable. (Standard 1.)
- **Forgetting the scope.** Running spot-vs-futures past 2024-04-05 where futures
  don't exist, or not stating the overlap window. (Audit's headline issue.)
- **Treating continuous series as a fixed contract.** Assuming `C1` is one
  contract held constant; it rolls — relevant near expiry and for roll yield.
- **Wrong shape sign.** Labeling `C4 > C1` as backwardation (it's contango).
- **No baseline.** Reporting futures RMSE with nothing to beat. (Standard 3.)
- **Causal/over-strong claim.** "Contango causes prices to rise" — it describes
  the curve, it doesn't cause the outcome. (Standard 6; type J.)
- **String-sorted dates** breaking the merge_asof ordering requirement.

## Assignment-specific hint strategy (L1→L2→L3 for the key decisions)

Five decision points; full instantiation in HINTS.md.

1. **Contract notation / what C1..C4 mean** (concept; supports A,B). L1: "Is C1 a
   fixed July contract or whatever's nearest today?" L2: metadata names +
   continuous-series note. L3: explain roll, hand back the implication.

2. **Curve shape classification** (decision E-ish). L1: "If later months cost
   more, is that contango or backwardation — and what does that say about
   near-term supply?" L2: point at the `C4 - C1` sign. L3: the `np.select`
   skeleton, learner picks the spread pair and flat band.

3. **Comparison framing & leakage** (type A, the big one). L1: "On day t, is the
   prompt settlement the same thing as today's spot? Is it next month's spot?"
   L2: point at where origin and target dates must both appear. L3: the
   `target_date = origin + horizon` + `merge_asof` skeleton; learner picks
   framing and horizon and defends leakage-freeness.

4. **Baseline to beat** (type B). L1: "Cheapest no-model forecast of spot h ahead?"
   L2: module 02 naive baselines; random walk for a level. L3: `yhat = spot(t)`
   skeleton; learner states why random walk is the right null here.

5. **Futures-as-benchmark interpretation** (type J/G). L1: "Does the curve
   *minimize forecast error*, or is it an equilibrium price with a risk premium?"
   L2: glossary "Why futures are NOT forecasts". L3: frame as a hypothesis with
   the risk-premium confound named; do not bless "futures predict spot".

## Agent response pattern

1. Identify the highest-impact issue first (usually framing/leakage or scope).
2. Ask the learner to state their assumption (origin, target, horizon).
3. Give the lowest useful hint level; answer pure API stalls directly (type K).
4. Re-run/re-check after revision; confirm exit 0 and the two date columns exist.
