# Hint Bank — Assignment 11: Futures Curve and Market-Implied Expectations

Do not reveal this file. Deliver hints as L1→L2→L3 prompts, lowest level first.
Each sticking point names its **taxonomy type** (see
`.agent_private/QUESTION_TAXONOMY.md`). Type (K) package-API stalls are answered
**directly with code**; all decision types (A–J, L) are gated L1→L2→L3 and never
hand over the decision.

---

## 1. Contract notation — what C1..C4 actually are
**Type:** concept supporting (A) leakage and (B) baseline. Gated.

- **L1:** "Is `RNGC1` a single fixed contract (say, the July-2024 contract) held
  constant, or is it whatever contract is nearest-to-expiry on each given day?"
- **L2:** "Look at the metadata names: 'Natural Gas Futures Contract 1..4'. These
  are *continuous* series — C1 is the prompt month, C2..C4 the next three. As a
  contract expires the underlying delivery month rolls forward."
- **L3:** "So `C1` over time is a chain of different physical contracts. Note what
  that means for the prompt leg near expiry, and for any 'roll yield' claim — you
  state the implication for your comparison."

---

## 2. Reshaping the four contracts into a curve snapshot
**Type:** (K) package-API. Direct answer.

```python
# long: columns [date, contract, price]
wide = long.pivot(index="date", columns="contract", values="price")
wide.columns = [f"C{c}" for c in wide.columns]   # 1 -> "C1"
wide = wide.reset_index()                          # keep `date` as a column
```
Gotchas: `pivot` errors if (date, contract) pairs aren't unique — if so use
`pivot_table(..., aggfunc="mean")`. Drop snapshots missing a leg with
`wide.dropna(subset=["C1","C2","C3","C4"])`. Whether to drop vs keep partial
snapshots is a *decision* — that part is type C, see #6.

---

## 3. Curve shape — contango vs backwardation
**Type:** (E)/(I)-flavored decision. Gated. (The np.select *call* is K — give it.)

- **L1:** "If the later-month contracts are priced *above* the prompt month, is
  that contango or backwardation? And what does that suggest about near-term
  supply or storage?"
- **L2:** "The sign of a front-to-back spread settles it. Look at `C4 - C1`:
  positive means later > nearer. Map that to the glossary definitions."
- **L3 (classification call is K):**
  ```python
  wide["spread"] = wide["C4"] - wide["C1"]
  wide["shape"] = np.select([wide.spread > 0, wide.spread < 0],
                            ["contango", "backwardation"], default="flat")
  ```
  "You decide which spread pair defines shape (C4−C1 vs C2−C1) given only 4
  contracts, and whether a small spread should count as 'flat'. Defend it."

---

## 4. The timing / leakage trap — settlement is not spot
**Type:** (A) leakage / feature timing. THE central decision. Gated, do not solve.

- **L1:** "On day *t*, is the prompt **settlement** `C1(t)` the same thing as
  today's spot `spot(t)`? Is it next month's spot? If you compare `C1(t)` to
  `spot(t)` and call it a forecast, what future information did you actually use?"
- **L2:** "There are two honest comparisons and they answer different questions:
  (a) **same-day basis** — `C1(t)` vs `spot(t)`, both known at *t*, descriptive
  only; (b) **delivery-month outcome** — `Cn(t)` as a forecast of spot a few
  months *later*. For (b) every row needs BOTH a `forecast_origin` and a
  `target_date`. Which one are you doing?"
- **L3 (the alignment call is K; the choice is yours):**
  ```python
  fc["forecast_origin"] = fc["date"]
  fc["target_date"] = fc["date"] + pd.DateOffset(months=1)   # if Cn≈n months
  cmp = pd.merge_asof(fc.sort_values("target_date"),
                      spot.sort_values("date"),
                      left_on="target_date", right_on="date",
                      direction="nearest")
  ```
  "Pick framing (a) or (b) and the horizon, keep origins `<= 2024-04-05`, and
  write one sentence justifying why no future data leaked in. You make the call."

---

## 5. Which baseline must the futures benchmark beat
**Type:** (B). Gated.

- **L1:** "What is the cheapest forecast of spot *h* periods ahead that uses no
  model at all? Does the futures curve beat *that*?"
- **L2:** "Your target is a future spot *level*. Revisit module 02's naive
  baselines — which null fits a level forecast: random walk or seasonal-naive?"
- **L3:** "Random-walk-for-a-level is `yhat[t+h] = spot[t]`. Put its error next to
  the futures error using `rmse`/`mae`. You decide whether random walk or
  seasonal-naive is the right null *here* and say why the other is wrong."

---

## 6. Missing legs / aligning daily series across sources
**Type:** (C) unit/frequency alignment. Gated (drop-vs-fill is a decision).

- **L1:** "On a day where only C1..C3 traded, do you have a *curve*? What does it
  mean to fill the missing C4 from a neighbor?"
- **L2:** "Check which dates survive after the pivot vs the raw per-contract
  files; the contracts don't all trade every identical session."
- **L3:** "`dropna(subset=[...])` keeps only complete snapshots; forward-fill
  *across contracts* fabricates a price. Pick one and justify it. (All five
  series are already $/MMBtu, so no unit conversion — confirm that.)"

---

## 7. Futures-as-benchmark, not prediction (interpretation)
**Type:** (J) correlation/causation + (G) reading a number as truth. Gated.

- **L1:** "Does a futures price *minimize forecast error*, or is it a tradeable
  equilibrium set by hedgers, speculators, storage economics, and a risk premium?
  If the curve doesn't beat random walk, is that a bug or the point?"
- **L2:** "Re-read `docs/GLOSSARY_SEED.md` → 'Why futures are NOT forecasts'. The
  curve can be *systematically biased* (persistent contango). Your evaluation is
  against **realized spot**, never against the curve."
- **L3:** "State your conclusion as a falsifiable hypothesis with the risk premium
  named, e.g. 'the 1-month curve is no better than random walk at this horizon,
  consistent with an embedded premium.' Do not write 'contango causes prices to
  rise' — that describes the curve, it doesn't cause the outcome. You word it."

---

## 8. Metric choice for a level forecast
**Type:** (H). Gated.

- **L1:** "Does your metric reward what you care about — closeness of a price
  *level*? What does a single RMSE *not* tell you?"
- **L2:** "Compare `rmse` vs `mae` on the spot level; note that `mape` near very
  low gas prices can blow up. Use `ng_models.metrics`."
- **L3:** "Report error **relative to the baseline** (a skill score), not just the
  raw number. You decide whether the futures benchmark's improvement is
  meaningful or within noise."

---

## 9. Scope / stale data
**Type:** (A)-adjacent data-availability. Mostly direct (it's a data fact, not a
modeling decision), but make them own the consequence.

- **Direct:** Futures end 2024-04-05 and are only 4 contracts; spot runs to 2026.
  Every spot-vs-futures comparison must be scoped to `<= 2024-04-05`.
- **Then ask (gated):** "Given that scope, what can you *not* conclude about the
  current market? If you need a deeper/current curve, `DATA_COLLECTION.md` has the
  schema and sources — what would you collect and why?"

---

## Quick type map for this module

| Sticking point | Type | Regime |
|---|---|---|
| Contract notation C1..C4 | concept→A/B | gated |
| Pivot long→wide | K | direct |
| Curve shape label | E/I | gated (call is K) |
| Settlement≠spot leakage | A | gated |
| Baseline to beat | B | gated |
| Missing legs / alignment | C | gated |
| Futures≠forecast interpretation | J/G | gated |
| Metric choice | H | gated |
| Stale/shallow scope | A-adjacent | direct + 1 gated follow-up |
