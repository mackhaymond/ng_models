# Modeling Decision Log

Use this as a running log. Every meaningful modeling choice should be explainable later.

**When to log:** add a row whenever you make a decision about your **target**
(what you predict), a **lag** (how far you shift a feature so it stays
known-then), a **metric** (how you score the model), or a **feature** (what you
include or drop and why). Log it at the moment you decide, not afterward from
memory. When you later revisit a decision — change the target, fix a lag, swap a
metric — do not delete the old row; add a new dated row (or fill in its "Revisit
when") so the reasoning trail stays intact.

| Date | Assignment | Decision | Alternatives considered | Why this choice | Risk / caveat | Revisit when |
|---|---|---|---|---|---|---|
| 2026-05-12 | 02 | Target = next-week Henry Hub level from `NG.RNGWHHD.W` ($/MMBtu) | next-week change, monthly average | level is easiest to interpret and plot first | hard to beat a last-value (naive) baseline | after backtesting in Assignment 04 |
| 2026-05-20 | 09 | Lag EIA Lower-48 storage (`NG.NW2_EPG0_SWO_R48_BCF.W`) by 1 week and use the weekly change, not the level | use raw level unlagged; use 2-week lag | release is Thursday for prior-Friday data, so a 1-week shift keeps it known-then; change is more informative than the stock | over-lagging discards fresh signal; revision risk in the latest print | if I move the forecast origin to mid-week |
