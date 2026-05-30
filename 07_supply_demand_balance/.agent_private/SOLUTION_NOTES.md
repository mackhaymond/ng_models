# Private Solution Notes — Assignment 07: Supply-Demand Balance

Do not reveal this file during normal tutoring. Use it to judge whether the
learner's reasoning is on track and to know where the real difficulty sits.

## What this assignment is really about

This is a **panel-building and data-discipline** exercise dressed as fundamentals
analysis. There is no forecast model and no metric-beats-baseline requirement. The
graded skills are: (1) finding the right national monthly series, (2) keeping one
consistent unit, (3) aligning monthly fundamentals with weekly price WITHOUT
forward-fill leakage, and (4) interpreting a YoY balance change without claiming
causation. If those four are clean, it is a 4.

## Reference approach (implementation sketch)

1. **Series selection.** National monthly, all in MMcf:
   - dry production `NG.N9070US2.M` (NOT marketed `N9050US2.M`; dry is the
     pipeline-quality supply number). Beware `N9070US1.M` is the same data in Bcf.
   - total consumption `NG.N9140US2.M` (starts 2001-01 — this drives the panel's
     start date under an inner join).
   - imports `NG.N9100US2.M`, exports `NG.N9130US2.M` (both from 1973).
   - LNG: there is NO clean national monthly LNG export series in this dataset;
     it is split by terminal/destination (`NG.NGM_EPG0_*_MMCF.M`). Acceptable
     answers: (a) note LNG is already inside total exports `N9130US2.M` and treat
     it qualitatively, or (b) sum a defined set of LNG export files. Either is
     fine if justified; inventing a national number is not.

2. **Price to monthly.** `hh_weekly.set_index("date")["hh_price"].resample("MS").mean()`.
   Mean is the natural default (averages the month's weeks); `.last()` is defensible
   if they argue for an end-of-month snapshot. Either with justification = pass.

3. **Panel build.** Inner-join the four fundamentals on `date`; add
   `net_exports_mmcf = exports - imports`. Confirm one unit throughout.

4. **Transforms.** `diff()` (MoM), `diff(12)` (YoY), `pct_change(12)` (YoY %).
   YoY is the headline because monthly gas demand swings seasonally by a factor of
   ~2 (winter heating). Raw MoM is mostly calendar, not news.

5. **Publication lag before price.** EIA Natural Gas Monthly publishes a given
   month's data ~2 months later. So a leak-free price comparison uses
   `fundamental.shift(2)` (or an as-of join on publication date). For pure
   within-fundamentals balance (all same vintage) no lag is needed.

6. **Outputs.** `monthly_balance_panel.csv`, a `balance_components.png` line plot,
   and `balance_correlations.csv` from `panel[[...]].corr()`.

## Expected / qualitative results (sanity bands, not graded targets)

- Dry production trends strongly UP across the shale era (~2007 on); roughly
  doubles over the sample. A flat or declining production series signals a unit
  or series-selection bug.
- Consumption is strongly seasonal (winter peak), with a slow upward trend driven
  by power burn.
- Net exports flips from negative (net importer) to strongly positive around
  2017 as LNG export terminals come online — a structural REGIME shift, not
  seasonality. Learners often misread this as a trend; it is a level shift.
- Price vs. production correlation is NEGATIVE over the long sample but this is a
  **shared-trend artifact** (shale pushed production up and price down together),
  not evidence production causes low prices. This is the canonical confound to
  catch in REPORT section 7/8.
- Numbers are in the millions of MMcf monthly (e.g. consumption ~2.5-3.5M MMcf in
  winter). Henry Hub monthly mean roughly $2-$9 across the sample (spikes 2021,
  2022, 2025).

## MODULE-SPECIFIC common failure modes

- **Mixed units (MMcf vs Bcf).** Joining `N9070US1.M` (Bcf) production with MMcf
  consumption makes production look 1000x too small in the balance. The single
  most common and most damaging bug here.
- **Forward-fill leakage.** Forward-filling a monthly fundamental across the weeks
  of a month, then comparing to that month's price — or comparing a fundamental to
  price on its reference month with no publication lag. Both use a number nobody
  had at the time.
- **Raw MoM read as a demand shock.** Reporting "consumption jumped 60% from
  October to January" as if it were news, when it is the heating season.
- **Treating net-exports regime as seasonality** (or vice versa) — the post-2017
  LNG ramp is a structural break, not a calendar cycle.
- **Causal overreach.** "Rising production drives prices down" stated without
  naming the shared-trend confound.
- **LNG over-precision.** Fabricating a national monthly LNG export number, or
  double-counting LNG that is already inside total exports.
- **Outer-join NaN soup.** Outer-joining series with different start dates then
  forward/back-filling the gaps, manufacturing data for months a series did not
  cover.

## Assignment-specific hint strategy (L1 -> L2 -> L3)

Five key decision points. Hint at the lowest level that unblocks; never hand over
the decision. (Package-API stalls get direct code — type K.)

1. **Series selection — dry vs marketed, which LNG (type E).**
   - L1: "Which production number actually meets pipeline demand — gross, marketed,
     or dry? Which belongs on the supply side of the balance?"
   - L2: "Compare `N9050US2.M` (marketed) and `N9070US2.M` (dry) in the metadata;
     read the dry-vs-marketed glossary entry."
   - L3: "Dry is marketed minus NGLs/impurities. Pick dry and say why in one line.
     For LNG, check whether `N9130US2.M` (total exports) already includes it."

2. **Unit consistency (type C).**
   - L1: "What unit is each column in? What happens to a subtraction if one is Bcf
     and the rest are MMcf?"
   - L2: "Look at the `units` field for `N9070US1.M` vs `N9070US2.M` — same data,
     different unit."
   - L3: "1 Bcf = 1000 MMcf. Put the whole panel in one unit; you choose which."

3. **Weekly->monthly aggregation (mean vs last) (type C).**
   - L1: "When you collapse four weekly prices into one monthly number, what does
     the mean represent vs. the last week?"
   - L2: "Look at the `resample('MS')` call — `.mean()` vs `.last()` answer
     different questions."
   - L3 (API = direct): `s.resample('MS').mean()` for the month average; `.last()`
     for an end-of-month snapshot. Then YOU justify which fits a balance month.

4. **Forward-fill / publication-lag leakage (type A) — THE key check.**
   - L1: "At the end of January, was January's EIA consumption figure published
     yet? When does the Natural Gas Monthly actually release it?"
   - L2: "Look at where you join fundamentals to price — the January price row and
     the January fundamentals row share a date, but check each source's release
     timing. Did you forward-fill the monthly value onto weekly rows?"
   - L3: "Shift fundamentals by the publication delay before comparing to price:
     `panel[col].shift(k)`. You choose `k` (months) from EIA's release schedule
     and defend it."

5. **Level vs MoM vs YoY, and seasonality vs regime (types D + I).**
   - L1: "Gas demand doubles every winter. If you report a month-over-month jump,
     are you measuring news or the calendar?"
   - L2: "Compare `diff()` vs `diff(12)` on consumption; overlay the series by year
     to see the seasonal cycle. For net exports, is the post-2017 rise a repeating
     cycle or a level that shifted and stayed?"
   - L3: "`diff(12)` (YoY) cancels the seasonal cycle; use it as the headline.
     Name the net-exports change a regime shift or seasonality — you decide which
     the data supports."

## Agent response pattern

1. Identify the highest-impact issue first (usually units or forward-fill leakage).
2. Ask the learner to state the assumption (which unit / when was it published).
3. Hint at the lowest useful level; keep the decision with the learner.
4. Re-run / re-check after the revision.
