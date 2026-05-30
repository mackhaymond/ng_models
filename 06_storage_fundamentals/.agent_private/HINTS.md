# Hint Bank — Assignment 06: Storage Fundamentals

Do not paste this file. Deliver hints as L1 → L2 → L3 prompts, lowest level that unblocks.
Each sticking point names its `QUESTION_TAXONOMY.md` TYPE. Type (K) package-API stalls are
answered directly with code; all decision types (A–J, L) escalate one level at a time and
never hand over the decision.

---

## 1. Five-year average / seasonal norm without leakage — TYPE (A)

The defining trap of this module. A full-sample or centered week-of-year mean folds the
current and future years into the norm.

- **L1 (diagnostic):** "Take one week — say ISO week 5 of 2018. Which years' storage values
  go into the 'normal' you compare it against? Is 2018 itself one of them? Is 2019?"
- **L2 (location):** "Look at how you build `seasonal_norm`. A bare
  `groupby('iso_week')['storage_bcf'].transform('mean')` averages the ENTIRE column for that
  week — every year, including the one you're scoring and all later ones. Where does the
  current/future year get excluded?"
- **L3 (pattern):**
  ```python
  g = panel.groupby("iso_week")["storage_bcf"]
  panel["seasonal_norm"] = g.transform(lambda s: s.expanding().mean().shift(1))
  ```
  "The `.shift(1)` inside each week-of-year group is what drops the current year; expanding
  keeps it to prior years only. You still decide: all prior years, or a trailing 5
  (`s.shift(1).rolling(5, min_periods=1).mean()`)? Justify which and what to do for 2010
  where there are no priors."

## 2. EIA publication lag — TYPE (A)

- **L1:** "The number stamped 'Friday this week' — when is it actually public? Could a price
  that printed Monday or Tuesday of that week have reacted to it?"
- **L2:** "Your panel pairs storage and price on the same date row. Before you treat them as
  simultaneously known, check the EIA Weekly Natural Gas Storage Report release schedule."
- **L3:** "EIA releases Thursday ~10:30 ET for the week ending the prior Friday — a ~5-6 day
  lag. So for any predictive use, `panel['storage_pub'] = panel['storage_bcf'].shift(k)` with
  k covering that delay. You pick k from the schedule and defend it; for the descriptive plot
  just STATE the lag in the report."

## 3. Merge / alignment strategy — TYPE (C)

- **L1:** "What unit and frequency is each series in, and do their date stamps actually line
  up week-for-week?"
- **L2:** "Check the first rows of each after loading — both are weekly Friday-ending and both
  start 2010-01-01, but Henry Hub also has 1997-2009. What does an inner join do to those
  early price-only rows vs. an outer/left join?"
- **L3 (mostly K for the call, C for the choice):**
  ```python
  panel = storage.merge(hh, on="date", how="inner").sort_values("date").reset_index(drop=True)
  ```
  "Inner keeps only the overlap (2010+). Name the one situation where you'd reach for
  `pd.merge_asof(..., direction='backward')` instead — and say why you don't need it here."

## 4. Seasonality drivers — TYPE (I)

Why does storage rise and fall on a calendar, and is the pattern seasonal or a regime shift?

- **L1:** "Walk through a year: when is heating demand highest? When is gas going INTO the
  ground vs coming OUT? Does your storage curve match that story?"
- **L2:** "Overlay storage by iso_week with one line per year (the seasonality plot). Does
  every year trace roughly the same shape, or did the LEVEL shift and stay shifted at some
  point (shale era / LNG export growth)?"
- **L3:** "A repeating same-week shape across years is seasonality; a one-time level change
  that persists is a regime shift. You decide which the data shows and say so — don't
  attribute a structural level change to 'seasonality'."

## 5. Deviation economics (deficit/surplus → price) — TYPES (G), (J), (H)

- **L1:** "When the deviation is a deep deficit, what do you expect price to do, and why
  physically? And is what you're seeing correlation, prediction, or cause?"
- **L2:** "What third variable could drive BOTH storage and price at the same time? Re-read
  your interpretation sentence and find the hidden causal verb ('drives', 'causes')."
- **L3:** "Write it as a falsifiable association: 'storage deficits are *associated with*
  firmer prices, but weather and production are uncontrolled confounds.' If you want to claim
  more, name what you'd have to rule out. The agent won't bless a causal claim without an
  identification argument. (Also: don't summarize the relationship with a single correlation
  number — say what that number does NOT tell you.)"

## 6. Computing change / injection-withdrawal — TYPES (K) then (I)

- **API part (K) — answer directly:**
  ```python
  panel["storage_change_bcf"] = panel["storage_bcf"].diff()        # first row is NaN
  panel["flow_type"] = np.where(panel["storage_change_bcf"] > 0, "injection", "withdrawal")
  ```
  Note: `.diff()` is week-over-week here because rows are already weekly and sorted.
- **Decision part (I) — leveled:**
  - L1: "Which sign is an injection — storage going up or down? Does your label agree?"
  - L2: "Crosstab `flow_type` by `month` — are injections concentrated in summer? A roughly
    even split every month means a sign or sort bug."
  - L3: "You decide how to treat an exactly-zero change and the first NaN row, and justify it."

## 7. Metadata search — TYPE (K), answer directly

- "Confirm the series instead of trusting memory:
  ```python
  meta = load_metadata(DATA_DIR)
  hits = search_metadata(meta, ["storage", "working gas", "underground"])
  print(hits[["series_id", "name", "units", "frequency", "filename"]])
  ```
  The Lower-48 anchor is `NG.NW2_EPG0_SWO_R48_BCF.W` (Bcf, weekly). Read units/frequency from
  the printout, not from this hint, when you write the report."

## 8. Vocabulary depth — TYPE (J)-adjacent (precision of claims)

The learner gives shallow or wrong definitions (e.g. "storage = all the gas underground").

- **L1:** "Is *all* gas underground 'working gas'? What about the gas that never comes out?"
- **L2:** "Compare your definition to `docs/GLOSSARY_SEED.md` — working gas vs base/cushion
  gas, injection vs withdrawal, five-year average vs your wording. Where are you imprecise?"
- **L3:** "Tighten each to one sentence that a desk analyst couldn't nitpick: working gas =
  the withdrawable portion above cushion; injection/withdrawal = the SIGN of the weekly
  change; five-year average = same-week mean over PRIOR years only. You write the final wording."
