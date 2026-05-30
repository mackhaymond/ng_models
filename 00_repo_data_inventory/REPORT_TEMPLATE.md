# Report — Assignment 00: Repository and Natural Gas Data Inventory

> Replace every _italic prompt_ with your own writing. Keep it to ~1 page.

## 1. Objective

In 2-4 sentences: what is this assignment trying to learn? _(Hint: it is data
discovery — building a map of the catalog before any modeling — not forecasting.)_

## 2. Vocabulary

Define each in your own words (1-2 sentences). The italic note is guidance, not the answer.

- **series_id:** _The source's permanent code for one variable (e.g. `NG.RNGWHHD.W`). Contrast it with the filename._
- **filename:** _Where that series is stored on disk; just a location, not the variable's identity._
- **frequency:** _How often the series is sampled — A/M/W/D. Say why this matters when combining series._
- **units:** _What one number means (Bcf, MMcf, $/MMBtu). Note that mixing units silently is an error._
- **observation / row_count:** _One dated data point; row_count is how many a series has. Tie it to coverage as a sanity check._
- **coverage:** _The first-to-last date span the series actually covers; why a series ending early is unusable._
- **data dictionary:** _A document/table that explains what each field and code means — here, the metadata catalog itself._

## 3. Data used

List the catalog plus the candidate files you opened. Example row filled in;
replace with your real choices.

| Source / file | series_id | Frequency | Units | Date range | Why used |
|---|---|---:|---|---|---|
| `_metadata.csv` | — | (catalog) | — | — | Master list of all 16k series |
| `NG.RNGWHHD.W.csv` | `NG.RNGWHHD.W` | W | Dollars per Million Btu | 2010-01 -> 2026-05 | Henry Hub spot — the forecast target later |
| _..._ | _..._ | _..._ | _..._ | _..._ | _..._ |

## 4. Data decisions

Describe: how you parsed dates, what missing values you found, and — the key
decision here — **how you narrowed each broad keyword search down to the headline
series** you kept. State which categories returned thousands of rows and how you chose.

## 5. Outputs checklist

- [ ] `outputs/frequency_counts.csv`
- [ ] `outputs/top_units.csv`
- [ ] `outputs/candidate_series.csv` (with your `why_relevant` notes)
- [ ] At least one plot summarizing the catalog
- [ ] This `REPORT.md` completed

## 6. Results

Reference the saved tables/plot and give the headline numbers. Example: _"Of 16,041
series, ~12,900 are annual (A), ~3,100 monthly (M), and only 13 weekly + 5 daily.
The dominant unit is Million Cubic Feet. My candidate table has N series across 7
categories."_ Then point to `candidate_series.csv` and your frequency bar chart.

## 7. Interpretation

What does the inventory mean for natural-gas modeling? Address at least: the
**frequency mismatch** problem — most fundamentals are monthly/annual while the
Henry Hub price you will forecast is weekly/daily — and what that implies for later
alignment work. Avoid any causal claims; this is description, not inference.

## 8. Limitations

What could be wrong or incomplete? Examples to consider: keyword search can miss
relevant series whose name uses different wording, or over-include irrelevant ones;
`row_count` may not match the actual file length; coverage gaps inside a series are
invisible from the catalog alone.

## 9. Next questions

List 3 concrete questions you would investigate next (e.g. "Which weekly storage
series aligns cleanly with weekly Henry Hub?", "Does every candidate cover 2010-2026
with no internal gaps?").
