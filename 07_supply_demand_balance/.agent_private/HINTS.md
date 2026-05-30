# Leveled Hint Bank — Assignment 07: Supply-Demand Balance

Instantiates the repo-wide types in `../../.agent_private/QUESTION_TAXONOMY.md`
for this module's specific sticking points. Classify the learner's question into a
type, then deliver the LOWEST level that unblocks them (L1 first). Type (K)
package-API stalls get direct working code — no gating. All other types (A, C, D,
E, I, J) stay L1->L2->L3 and never hand over the decision.

Do not paste this file to the learner. Deliver hints as prompts.

---

## Sticking point 1 — "Which production / consumption / LNG series do I use?"  [Type E]

- **L1:** "Which production number actually meets pipeline demand — gross
  withdrawals, marketed, or dry? Which one belongs on the supply side?"
- **L2:** "In `_metadata.csv` compare `NG.N9050US2.M` (marketed) and
  `NG.N9070US2.M` (dry). Read the dry-vs-marketed glossary entry
  (`docs/GLOSSARY_SEED.md#marketed-vs-dry`)."
- **L3:** "Dry = marketed minus NGLs and impurities, so dry is the gas that
  actually reaches demand. Pick one and write a one-line reason. For LNG: there is
  no clean national monthly LNG export series here — check whether total exports
  `NG.N9130US2.M` already contains it before you go summing terminal files. You
  decide how to handle LNG and justify it."

## Sticking point 2 — "My balance numbers look off by a factor of ~1000."  [Type C]

- **L1:** "What unit is each column in? What does a subtraction do if one series
  is in Bcf and the others are in MMcf?"
- **L2:** "Look at the `units` field for `NG.N9070US1.M` vs `NG.N9070US2.M` — same
  dry-production data, different unit (Bcf vs MMcf)."
- **L3:** "1 Bcf = 1000 MMcf. Put the entire panel in ONE unit before any
  subtraction; you choose MMcf or Bcf and convert the odd one out."

## Sticking point 3 — "How do I turn weekly Henry Hub into a monthly series?"  [Type K, then C]

- **API (direct, type K):**
  ```python
  hh_monthly = (hh_weekly.set_index("date")["hh_price"]
                .resample("MS").mean()      # "MS" = month start, matches YYYY-MM-01
                .reset_index())
  ```
  Note: `resample` needs a DatetimeIndex (hence `set_index`); `"MS"` aligns to the
  first-of-month stamps the monthly fundamentals use.
- **The CHOICE is type C (hint, do not decide):**
  - L1: "Does the monthly price mean the *average* of the month's weeks, or the
    *last* week's level? Those answer different questions."
  - L2: "`.mean()` vs `.last()` on the resample — which matches a balance month?"
  - L3: "Mean smooths the month; last() is an end-of-month snapshot. Pick one and
    say why it fits a monthly balance."

## Sticking point 4 — "How do I join series that start in different years?"  [Type K, then C]

- **API (direct, type K):**
  ```python
  panel = (prod.merge(cons, on="date", how="inner")
               .merge(imp,  on="date", how="inner")
               .merge(exp,  on="date", how="inner"))
  ```
- **The CHOICE (inner vs outer) is type C:**
  - L1: "With an outer join, what fills the months where consumption (starts 2001)
    has no data but imports (from 1973) do?"
  - L2: "Inner keeps only the overlap; outer keeps all dates and leaves NaNs.
    Check which keeps your balance columns aligned without inventing values."
  - L3: "Inner join is the safe default here. If you outer-join, do NOT fill the
    pre-2001 consumption gap — that manufactures data. You justify the choice."

## Sticking point 5 — "Can I just put January's fundamentals next to January's price?"  [Type A — THE key leakage check]

- **L1:** "At the end of January, had EIA actually published January's consumption
  figure yet? When does the Natural Gas Monthly release a month's data?"
- **L2:** "Look at where you join fundamentals to price. The January price row and
  the January fundamentals row share a date — but check each source's *release*
  timing, not the period it describes. Did you forward-fill the monthly value onto
  weekly price rows?" (See `docs/GLOSSARY_SEED.md#release-lag` and `#as-of-join`.)
- **L3:** "EIA publishes a month's data ~2 months later. Shift the fundamentals by
  the publication delay before any price comparison:
  `panel[col].shift(k)` (k in months) — or do an as-of join keyed on the
  publication date. You choose `k` from EIA's schedule and defend it. For pure
  within-fundamentals balance (all same vintage), no lag is needed."

## Sticking point 6 — "Consumption jumped 60% from October to January — big news?"  [Types D + I]

- **L1 (D):** "Gas demand roughly doubles every winter for heating. Is a
  month-over-month jump measuring news, or the calendar?"
- **L2 (D):** "Compare `consumption.diff()` (MoM) against `consumption.diff(12)`
  (YoY). Which one removes the seasonal cycle?"
- **L3 (D):** "`diff(12)` compares to the same month last year and cancels
  seasonality — use it as your headline comparison. You pick it and explain why
  raw MoM misleads here."
- **For net exports (I):**
  - L1: "Is the post-2017 rise in net exports a repeating yearly cycle, or did the
    level shift and stay there?"
  - L2: "Overlay net exports by year and look at a rolling mean — does the same
    month behave the same across years, or did 2017+ break the pattern?"
  - L3: "A sustained level change after LNG terminals opened is a *regime shift*,
    not seasonality. You name which story the data supports."

## Sticking point 7 — "Production is up and price is down, so production drives prices."  [Type J]

- **L1:** "Could a third factor push production up AND price down at the same time?
  Could the arrow point the other way (low prices curbing drilling)?"
- **L2:** "Re-read your sentence and replace 'drives' with 'is associated with.'
  Does the evidence still hold? What about the shale-era trend in both series?"
- **L3:** "State it as a falsifiable hypothesis with the confound named: 'The shale
  boom raised production and depressed price together, so the negative correlation
  is consistent with a shared trend, not identified causation.' You write the final
  wording; the agent will not bless a causal claim without an identification
  argument."

## Sticking point 8 — "How do I build the YoY / correlation columns?"  [Type K]

- **API (direct):**
  ```python
  panel["cons_yoy"]     = panel["consumption_mmcf"].diff(12)      # 12 monthly rows = 1 year
  panel["cons_yoy_pct"] = panel["consumption_mmcf"].pct_change(12)
  corr = panel[["dry_production_mmcf", "net_exports_mmcf", "hh_price"]].corr()
  corr.to_csv(OUTPUT_DIR / "balance_correlations.csv")
  ```
  Note: `diff(12)`/`pct_change(12)` produce NaN for the first 12 rows (no prior
  year) — expected, drop or ignore them. What the correlation *means* is type J
  (hint it), not type K.
