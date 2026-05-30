# Assignment 00: Repository and Natural Gas Data Inventory

**Phase:** Foundations  
**Level:** Beginner  
**Estimated time:** 2-4 hours

## Data scope

Use only `data/_metadata.csv` (the catalog) plus a small number of individual
series files you select from it.

Expected data inputs:

- `data/_metadata.csv` — one row per available series.
- 3-5 individual series CSVs (each has `Date,Value` columns), chosen from the catalog.

You do **not** download anything. Everything is already in `data/`.

## Concepts you'll use

Read these once before you start; you will define them in your own words in the report.

- **Metadata catalog.** A single table (`_metadata.csv`) that describes every data
  file without you having to open thousands of files. Each row is one *series*
  (one measured quantity over time) and the columns tell you its id, name, units,
  frequency, date span, file name, and how many observations it has.
- **`series_id` vs `filename`.** The `series_id` is the source's permanent code for
  the variable (e.g. `NG.RNGWHHD.W` = Henry Hub spot price, weekly). The `filename`
  is just where that series is stored on disk (`NG.RNGWHHD.W.csv`). Two different
  ids never share a file; think "id = identity, filename = location."
- **Frequency.** How often the variable is sampled: `A`=annual, `M`=monthly,
  `W`=weekly, `D`=daily. Two series at different frequencies cannot be lined up
  row-for-row — a weekly price and a monthly production figure need *alignment*
  (a later-module problem) before they can sit in one table.
- **Units.** What one number actually means. Billion Cubic Feet (Bcf) and Million
  Cubic Feet (MMcf) differ by 1000x; `Dollars per Million Btu` ($/MMBtu) is a price,
  not a volume. Adding or comparing series in different units without converting is
  a classic silent error.
- **Coverage / date span.** The first and last dates a series actually has data for
  (`start_date`, `end_date`). A series that ends in 2019 is useless for a 2026
  forecast no matter how relevant it looks.
- **`row_count` (observation count).** How many dated observations the series has.
  Combined with frequency it is a quick sanity check: ~16 years of weekly data
  should be ~830 rows; if `row_count` says 40, something is off.

## Package guide

This module only needs **pandas** and **matplotlib**, plus three `ng_models`
helpers. You CALL the helpers — you do not re-implement them.

### `ng_models` helpers (already written — just import and use)

```python
from ng_models.io import load_metadata, search_metadata, load_series_csv
from ng_models.paths import data_dir, ensure_output_dir

meta = load_metadata(data_dir(HERE))      # catalog with start_date/end_date as real datetimes
hits = search_metadata(meta, ["henry hub", "storage"])   # rows matching ANY keyword (OR, case-insensitive substring)
hh   = load_series_csv(data_dir(HERE), "NG.RNGWHHD.W.csv", value_name="henry_hub")  # tidy date/value frame, sorted
```

`load_metadata` already fixes the date bug — the catalog stores mixed-width
integer dates (`20100101` daily/weekly, `202604` monthly, `2025` annual) and the
helper parses all three to real datetimes, so `end_date >= "2025-01-01"` filters
work across every frequency. `load_series_csv` raises if a file lacks
`Date,Value`, so a clean load is itself a verification.

For the headline series ids per category (the anchors you are hunting for), see
[`docs/DATA_SOURCE_NOTES.md`](../docs/DATA_SOURCE_NOTES.md) — use it to check your
candidate picks, not as a substitute for doing the search yourself.

### pandas you'll use

```python
df.columns, df.dtypes, df.shape          # structure
df.head(); df.isna().sum()               # peek; missing-value counts per column
df["frequency"].value_counts(dropna=False)        # tally distinct values (keep NaNs visible)
df["units"].value_counts().head(15)               # top 15 units
mask = df["name"].str.contains("storage", case=False, na=False)   # boolean filter
df.loc[mask]                                       # rows where mask is True
df.to_csv(path, index=False)                       # write without the integer index
```

Turning a `value_counts()` Series into a 2-column CSV with headers:

```python
counts.rename_axis("frequency").reset_index(name="n_series").to_csv(path, index=False)
```

### matplotlib (a bar chart)

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 4))
counts.plot(kind="bar", ax=ax)           # Series.plot is the shortest path
ax.set_title("Series count by frequency"); ax.set_xlabel("frequency"); ax.set_ylabel("n_series")
fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
```

> The `save_line_plot` helper in `ng_models.plotting` draws *lines* (good for a
> time series). For a bar chart of catalog counts, use matplotlib directly as above.

## Terms to learn

`series_id`, `filename`, `frequency`, `units`, `observation`, `coverage`,
`row_count`, `data dictionary` — see also `docs/GLOSSARY_SEED.md` (sections 11
"Modeling workflow terms" and 12 "Python / package cheat-sheet").

Before coding, write one plain-English sentence for each in your own words.

## Learning goals

- Learn how the repository is organized and how to navigate a large data directory
  (16k+ series) without opening files manually.
- Build a small metadata audit that counts series by frequency and units, and
  selects candidate series by keyword.
- Practice asking the three foundational questions: what is this variable, what
  unit is it in, and at what frequency is it observed?

## Tasks

1. Load `data/_metadata.csv` and inspect columns, dtypes, missing values
   (`isna().sum()`), and date coverage (`start_date`/`end_date` min/max). *(The
   starter already loads it and prints frequency/units counts — extend from there.)*
2. Create tables of counts **by frequency** and the **top 15 units**. *(Done in the
   starter as a worked example; understand it, you'll reuse the pattern.)*
3. **Find candidate series** for: price, storage, production, consumption, imports,
   exports, and LNG, using `search_metadata` over the catalog. Broad keywords return
   thousands of rows — narrow each category down to the **one or two headline
   `series_id`s** you would actually feed a model, and record a `why_relevant` note.
   This is a judgment call, not a search dump.
4. **Open 3-5 candidate files** with `load_series_csv` and verify they have
   `Date,Value` and sensible coverage. Cross-check `row_count` vs actual length.
5. Write a one-page inventory memo: which data seems most useful for future
   modeling, and which questions remain ambiguous (e.g. frequency mismatch).

## Deliverables

- A reproducible script that writes `outputs/frequency_counts.csv`,
  `outputs/top_units.csv`, and `outputs/candidate_series.csv`.
- At least one plot summarizing the catalog (e.g. series count by frequency).
- `REPORT.md` completed from the template.

## Rules

- Keep raw data immutable — never write into `data/`.
- Save generated files under this assignment's `outputs/` folder (the starter
  resolves it via `ensure_output_dir`).
- Write down every assumption about dates, units, and frequency.
- A chart is not enough. Every chart needs a sentence on what it shows AND what it
  does not show.
- This is data *discovery*, not modeling. Do not fit anything yet.

## Questions to answer in `REPORT.md`

- What is the object of analysis (the catalog) and what will it feed later?
- What dates, units, and frequencies dominate the catalog?
- What was the most important data decision (e.g. how you narrowed candidates)?
- What result surprised you?
- What would you not trust yet (e.g. a `row_count` that doesn't match)?
- What should the next assignment investigate?
