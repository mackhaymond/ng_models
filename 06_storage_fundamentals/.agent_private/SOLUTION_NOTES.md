# Private Solution Notes — Assignment 06: Storage Fundamentals

Do not reveal this file during normal tutoring. Use it to judge whether the learner's
reasoning is on track and to pick the lowest useful hint level.

## Worked reference approach

1. **Identify the series.** `search_metadata(meta, ["storage", "working gas", "underground"])`
   surfaces eight weekly Bcf series. The Lower-48 anchor is `NG.NW2_EPG0_SWO_R48_BCF.W`
   (file `...R48_BCF.W.csv`). The regionals are R31 East, R32 Midwest, R33 South Central
   (with salt `SSO_R33` / nonsalt `SNO_R33`), R34 Mountain, R35 Pacific. The Lower-48 is
   the sum of the five regions (R31+R32+R33+R34+R35); it can differ by a Bcf or two from
   reclassifications/rounding — a good learner notices this.

2. **Load + align.** Both weekly series carry identical Friday-ending stamps and both
   begin 2010-01-01. Inner join on `date`:
   ```python
   panel = storage.merge(hh, on="date", how="inner").sort_values("date").reset_index(drop=True)
   panel = add_calendar_columns(panel, "date")
   ```
   Result: ~855 weekly rows, 2010-01-01 → 2026-05-15. (The 1997-2009 price history drops
   out — correct, no storage then.)

3. **Change + flow classification.**
   ```python
   panel["storage_change_bcf"] = panel["storage_bcf"].diff()
   panel["flow_type"] = np.where(panel["storage_change_bcf"] > 0, "injection", "withdrawal")
   ```
   First row is NaN. Sanity check: crosstab flow_type by month — injections dominate
   May-Oct, withdrawals Nov-Mar; a near-50/50 split in every month means a sign or date bug.

4. **Leakage-safe seasonal norm + deviation.** Group by week-of-year, average prior years
   only, exclude the current year via a shift inside the group:
   ```python
   g = panel.groupby("iso_week")["storage_bcf"]
   # all prior years:
   panel["seasonal_norm"] = g.transform(lambda s: s.expanding().mean().shift(1))
   # OR a true trailing 5-year norm (5 prior same-week values):
   panel["seasonal_norm"] = g.transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())
   panel["storage_deviation_bcf"] = panel["storage_bcf"] - panel["seasonal_norm"]
   ```
   2010 has no prior years → NaN norm (expected). Either expanding-all-prior or
   trailing-5 is acceptable IF defended; the trailing-5 matches the industry "five-year
   average" literally.

5. **Plots + interpretation.** Seasonality = level vs iso_week, one line/year (the classic
   "U" shape inverted — low in spring, peak ~Nov). Price-vs-deviation on twin y-axes.
   Interpretation: deficits (deviation < 0) tend to coincide with firmer price; framed as
   association, not causation.

## Expected metric ranges / qualitative results

- Panel length ~855 weekly rows (2010 → mid-2026).
- Lower-48 storage roughly oscillates ~1,500 Bcf (late-winter trough) to ~3,800-4,000 Bcf
  (autumn peak). A value far outside ~1,000-4,200 Bcf signals a unit or load bug.
- Roughly ~55-60% of weeks are injections, ~40-45% withdrawals (injection season is longer).
- Deviation typically within roughly ±500 Bcf; notable deficits in the cold winters of
  2014 (polar vortex) and early 2021 (Winter Storm Uri) line up with price spikes — a good
  qualitative cross-check, not a causal proof.
- Correlation between deviation and price is negative but modest and unstable across the
  shale-era level shift; learner should NOT report a single r as "the answer."

## Module-specific common failure modes

- **Full-sample or centered seasonal mean** (`groupby("iso_week").transform("mean")` with
  no shift) — the #1 error: it folds the current and future years into the norm. This is
  the leakage trap and the single most important thing to catch.
- **Forgetting the publication lag** — treating same-dated storage and price as
  simultaneously known; not stating the Thursday/prior-Friday release.
- **Flow sign inverted** — labeling negative change as injection.
- **Combining Bcf and $/MMBtu** on one axis or in a ratio/correlation reported as if
  commensurable.
- **Outer/left join** dragging 1997-2009 price rows with NaN storage, then computing stats
  over a half-empty panel.
- **iso_week edge effect** — week 53 exists only in some years; a learner using it as a
  norm grain gets noisy norms for that week (fine to mention, not fatal).
- **Reporting a plot without a modeling implication**, or a causal claim ("low storage
  causes high prices") with no confound control.

## Assignment-specific hint strategy (L1 → L2 → L3 for the key decision points)

Decision points and their taxonomy types — escalate one level at a time, stop when unblocked.

1. **Seasonal-norm leakage (type A).**
   - L1: "For the 2018 norm, which years' values are you averaging? Are any of them 2018
     or later?"
   - L2: "Look at your groupby on iso_week — does `transform('mean')` see the whole column
     including future years?"
   - L3: `g.transform(lambda s: s.expanding().mean().shift(1))` — explain why the `.shift(1)`
     is what removes the current year; you decide 5-year vs all-prior.

2. **Publication lag (type A).**
   - L1: "When does EIA actually publish the number stamped this Friday? Could a price
     printed Monday have 'known' it?"
   - L2: "Your panel row pairs same-dated storage and price — check the report release
     schedule before treating them as simultaneous."
   - L3: Lag storage by the publication delay before any predictive use; you pick the shift.

3. **Merge strategy (type C).**
   - L1: "What unit and frequency is each series, and do their dates line up?"
   - L2: "Both are weekly Friday-ending from 2010 — what does an inner vs outer join do to
     the 1997-2009 price rows?"
   - L3: `storage.merge(hh, on="date", how="inner")`; name when `merge_asof` would be needed.

4. **Flow classification + seasonality check (type I).**
   - L1: "Should injections show up in summer or winter? Does your classification agree?"
   - L2: "Crosstab flow_type by month — is the split lopsided by season or ~50/50?"
   - L3: `np.where(change > 0, "injection", "withdrawal")`; you decide the zero/NaN handling.

5. **Deviation interpretation (types G/J/H).**
   - L1: "Is what you see between deviation and price correlation, prediction, or cause?"
   - L2: "What third variable moves both storage and price? Re-read your sentence for a
     hidden causal verb."
   - L3: State it as a falsifiable association with weather/production named as confounds;
     you write the wording.

## Agent response pattern

1. Identify the highest-impact issue first (almost always: is the seasonal norm leakage-free?).
2. Ask the learner to explain their assumption.
3. Hint at the lowest useful level (API stalls = direct code; decisions = L1→L2→L3).
4. Re-run / re-check after revision.
