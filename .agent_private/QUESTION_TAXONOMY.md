# Question Taxonomy — Repo-Wide Hint System

This file defines the recurring question and decision *types* a learner hits while
working through the curriculum. It is the shared vocabulary that every module's
`.agent_private/HINTS.md` plugs into.

## How this is used

- This taxonomy is **repo-wide and stable**. It names the categories of sticking
  point and gives a reusable hint template for each.
- Each module's `.agent_private/HINTS.md` **instantiates** these types for that
  module's specific content. For example, the leakage type (A) in module
  `06_storage_fundamentals` instantiates as "the EIA storage report is published
  Thursday for the week ending the prior Friday"; in `09_feature_table_leakage`
  it instantiates as "your rolling mean includes the target row." The HINTS.md
  references the type letter so feedback stays consistent across modules.
- When the learner is stuck, the agent: (1) classifies the question into one of
  the types below, (2) checks the module HINTS.md for the instantiated version,
  (3) delivers help at the lowest level that unblocks them — L1 first.

## The two help regimes

There are two and only two regimes, and the type determines which applies:

1. **Direct-answer regime — type (K), package-API stalls only.** When the learner
   does not know how to *call a library* (pandas, matplotlib, statsmodels,
   pmdarima, scikit-learn, lightgbm, xgboost, scipy), answer **directly with
   working code**. This is allowed help. The learner is a strong general
   programmer who is simply unfamiliar with these specific interfaces; making them
   guess API surface area teaches nothing about gas markets or modeling.

2. **L1 → L2 → L3 hint regime — every modeling-decision type (A–J, L).** For any
   question that embeds a *modeling decision* — target definition, feature
   inclusion, lag choice, transformation, complexity, interpretation, metric
   sufficiency, causal claim, uncertainty adequacy — **never hand over the
   decision**. Escalate hints one level at a time and stop as soon as the learner
   can proceed:
   - **L1 — diagnostic question.** Make the learner surface the issue themselves.
   - **L2 — point to the location/object.** Name the file, function, column, or
     plot where the answer lives. Still no decision.
   - **L3 — small pattern.** Give a minimal code or reasoning skeleton, then hand
     the actual decision back: "you fill in / you justify."

A single learner message can mix both regimes. Split it: answer the API part
directly, hint the decision part. Example: "How do I shift this column and is a
1-week lag enough?" → show `.shift(1)` directly (K), then L1 the lag adequacy (D).

### (M) "I'm lost" — no articulable question (TRIAGE, not a hint level)

Sometimes the learner cannot name a sticking point at all ("I don't know what to
ask", "where do I start", a blank stare at the assignment). This is a *meta* type:
do not push a hint yet — first localize the gap.
- **Step 1 — locate:** "Which module and which numbered Task are you on?"
- **Step 2 — restate:** "In one sentence, what are you trying to predict, and what
  do you have so far (data loaded? a plot? a number)?"
- **Step 3 — probe with the Standard questions** (AGENTS.md) one at a time —
  target? origin? what-was-known? unit? baseline to beat? — until one lands on the
  real gap. *That* gap has a type (A–L); switch to its L1→L2→L3.
The deliverable of (M) is a specific, answerable question — never a lecture or a
solution. If the learner is *between* assignments, point them at the current
module's `ASSIGNMENT.md` "Concepts you'll use" and the "what should the next
assignment investigate" line of their last report.

---

## The types

### (A) Leakage / feature timing

The learner is building a feature or benchmark from data that would not have been
available at the forecast origin.

- **L1:** "At your forecast origin, had this value already been published? When
  does the source actually release it?"
- **L2:** "Look at the merge in `<build fn>` — the price row and the `<feature>`
  row share a date, but check the publication lag of each source."
- **L3:** "A safe pattern is `panel['<feat>_lagged'] = panel['<feat>'].shift(k)`
  where `k` covers the publication delay. You decide `k` from the source's release
  schedule and defend it."
- **Worked example 1:** Storage feature merged on the report's *week-ending* date,
  but EIA publishes ~5 days later → L1 asks when EIA releases; learner discovers
  the lag and chooses the shift.
- **Worked example 2:** A 4-week rolling mean used as a feature that includes the
  target week → L2 points to the `.rolling()` window boundary; learner fixes the
  window to end before the target.

### (B) Which baseline must I beat

The learner has a model but no honest comparison, or picked a baseline that is too
weak.

- **L1:** "What is the cheapest forecast someone could make for this target with no
  model? Does yours beat *that*?"
- **L2:** "Your target is a `<horizon>`-ahead `<level/change>`. Look at module 02's
  naive baselines — which one is the right null for *this* target?"
- **L3:** "Random walk for a level is `y_hat[t+h] = y[t]`; seasonal-naive is
  `y_hat[t+h] = y[t+h-52]`. Pick the one matched to your target and say why the
  other is wrong here."
- **Worked example:** Learner reports RMSE without a baseline → L1; if still stuck,
  L2 points at `02_calendar_baselines/`; learner selects random-walk vs seasonal.

### (C) Unit / frequency alignment

Series being combined are in different units or sampled at different frequencies.

- **L1:** "What unit and frequency is each series in? What happens at the merge
  when one is weekly and one is daily/monthly?"
- **L2:** "Check `_metadata.csv` for the unit of `<series>` and the index frequency
  after you load it; compare to `<other series>`."
- **L3:** "Resampling looks like `s.resample('W-FRI').mean()` (mean vs last vs sum
  changes the meaning). You choose the aggregation and justify it for this
  variable."
- **Worked example:** Daily HDD summed to weekly vs averaged → L1 surfaces that sum
  preserves total degree-days; learner picks sum and states why.

### (D) Level vs change vs return

The learner is unsure whether to model the price level, a difference, a percentage
change, an anomaly, or a lag — and these answer different questions.

- **L1:** "Are you trying to forecast *where the price will be* or *how much it will
  move*? Which transformation matches that question?"
- **L2:** "Look at your target column construction — is it `y`, `y.diff()`,
  `np.log(y).diff()`, or an anomaly vs a seasonal mean?"
- **L3:** "Log return is `np.log(y).diff()`; level is `y`. Each implies a different
  baseline and metric. State which question you're answering, then choose."
- **Worked example:** Learner fits ARIMA on raw price and gets a near-random-walk →
  L1 asks level vs change; learner reconsiders differencing intent.

### (E) Which transformation / target

Related to (D) but about the *target definition itself*: stationarity, log vs
linear, horizon, what "the forecast" even is.

- **L1:** "Write one sentence: 'I forecast [what] at [horizon] from [origin].' Does
  your transformation serve that sentence?"
- **L2:** "Look at the ACF/variance of your series — does the spread grow with the
  level? That points to log vs linear."
- **L3:** "If variance scales with level, `np.log1p` stabilizes it. Decide whether
  log is appropriate for *this* economic quantity and defend it."
- **Worked example:** Volatility module — learner must choose realized vol on
  returns vs level range; L2 points to the variance-vs-level plot.

### (F) Model complexity (should I add X yet)

The learner wants to jump to a fancier model (boosting, more features) before the
simpler layer is proven.

- **L1:** "What does adding this buy you over what you have, and have you *proven*
  the simpler layer is correct yet?"
- **L2:** "Before LightGBM, is your backtest in `04_backtesting_no_leakage` passing
  and does your linear/baseline beat naive?"
- **L3:** "Add complexity one axis at a time and re-run the same backtest; keep a
  before/after metric row. You decide whether the gain justifies it."
- **Worked example:** Learner adds XGBoost in module 10 before linear beats naive →
  L1; answer is to lock the baseline first. Do not add it for them.

### (G) Interpreting feature importance

The learner reads importance/coefficients as truth or as causation.

- **L1:** "Does a high importance mean the feature *causes* the price, *predicts*
  it, or just *correlates* with another feature? How would you tell?"
- **L2:** "Look at the correlation among your top features and how importance shifts
  if you drop one — `permutation_importance` vs split-gain disagree for a reason."
- **L3:** "Compute importance two ways (gain and permutation) and compare. You
  interpret why they differ; don't report a single number as the story."
- **Worked example:** Storage and HDD both rank high and are collinear → L2 points
  at their correlation; learner reasons about shared seasonality.

### (H) Metric choice / sufficiency

The learner picked a metric that doesn't match the target, or thinks one number
proves success.

- **L1:** "Does this metric reward the thing you actually care about? What does a
  good value of it *not* tell you?"
- **L2:** "Your target is a `<change/level>`; compare RMSE vs MAE vs MAPE on it and
  note where MAPE blows up near zero."
- **L3:** "Report the metric *relative to the baseline* (skill score), not just the
  raw value. You decide whether the improvement is meaningful."
- **Worked example:** MAPE on returns that cross zero explodes → L1 surfaces the
  zero-crossing problem; learner switches metric and explains.

### (I) Seasonality vs regime

The learner attributes a pattern to seasonality when it may be a regime shift (or
vice versa).

- **L1:** "Is this pattern repeating on a fixed calendar cycle, or did the *level/
  behavior* shift and stay shifted? How would you distinguish them?"
- **L2:** "Overlay the series by year (seasonal plot) and look at a rolling mean —
  does the same month behave the same across years?"
- **L3:** "Seasonal-subseries or month-of-year groupby separates calendar effects;
  a break test flags a regime. You decide which story the data supports."
- **Worked example:** Shale-era price-level drop looks like trend but is structural
  → L2 points to the rolling mean; learner names it a regime, not seasonality.

### (J) Correlation vs causation

The learner writes a causal claim the evidence does not support.

- **L1:** "Could a third variable drive both? Could the arrow point the other way?
  What would you need to *rule out* to claim cause?"
- **L2:** "Re-read your sentence — replace 'drives/causes' with 'is associated with'
  and see if the evidence still backs it."
- **L3:** "State it as a falsifiable hypothesis with the confound named. You decide
  the wording; the agent will not bless a causal claim without an identification
  argument."
- **Worked example:** "Cold weather causes price spikes" with no control for storage
  → L1 asks about the storage confound; learner rewrites as association.

### (K) Package-API stall — DIRECT ANSWER ALLOWED

The learner knows *what* they want but not *how to call the library*.

- **This type is answered directly with working code.** No L1/L2/L3 gating.
  Show the call, the relevant args, and a one-line note on the gotcha. Keep it
  minimal and scoped to what they asked.
- **Worked example 1:** "How do I parse the Date column as dates on load?" →
  `pd.read_csv(path, parse_dates=['Date'], index_col='Date')` and note it must be
  sorted: `.sort_index()`.
- **Worked example 2:** "How do I get an auto-ARIMA?" →
  `import pmdarima as pm; m = pm.auto_arima(y, seasonal=True, m=52)` with a note
  that `m=52` is weekly seasonality and large `m` is slow.
- **Boundary:** the *call* is type K (answer it); *whether to use that model, those
  args, that seasonality* is type E/F (hint it). Answer the call, hint the choice.

### (L) Uncertainty / coverage

The learner has a point forecast and is unsure how to quantify or validate
uncertainty.

- **L1:** "If you say 'I expect X,' how wrong could you be, and how often should the
  truth fall inside your interval?"
- **L2:** "Look at your residuals on the backtest — do their spread and your stated
  interval agree? Check empirical coverage of your 80% band."
- **L3:** "Empirical coverage is `(lower <= y_true) & (y_true <= upper)` averaged;
  it should be near the nominal level. You decide whether your intervals are
  honest and what to do if coverage is off."
- **Worked example:** 80% interval covers only 55% out of sample → L2 points at the
  coverage calc; learner diagnoses underdispersed residuals.

---

## Quick reference

| Type | Name | Regime |
|---|---|---|
| A | Leakage / feature timing | L1→L2→L3 |
| B | Which baseline must I beat | L1→L2→L3 |
| C | Unit / frequency alignment | L1→L2→L3 |
| D | Level vs change vs return | L1→L2→L3 |
| E | Which transformation / target | L1→L2→L3 |
| F | Model complexity (add X yet) | L1→L2→L3 |
| G | Interpreting feature importance | L1→L2→L3 |
| H | Metric choice / sufficiency | L1→L2→L3 |
| I | Seasonality vs regime | L1→L2→L3 |
| J | Correlation vs causation | L1→L2→L3 |
| K | Package-API stall | DIRECT answer |
| L | Uncertainty / coverage | L1→L2→L3 |

The decision types (A–J, L) map one-to-one onto the "Do not immediately solve for"
list in `AGENTS.md` and the six non-negotiable modeling standards in
`CURRICULUM.md`, which together are the grading foundation.
