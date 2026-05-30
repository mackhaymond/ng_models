# Module HINTS — Assignment 00: Repository and Natural Gas Data Inventory

Instantiates `.agent_private/QUESTION_TAXONOMY.md` for this module. Classify the
learner's question into a type, then deliver the LOWEST level that unblocks them.
Type (K) package-API stalls get direct code; everything else is L1->L2->L3 and the
DECISION stays with the learner. Do not paste this file.

This is a discovery module, so the live types are mostly **(C) unit/frequency
alignment**, **(K) package-API**, and a judgment flavor of **(B)/(E) selection**.

---

## Sticking point 1 — "How do I count series by frequency / units?" — type (K)

Direct answer (API stall):

```python
metadata["frequency"].value_counts(dropna=False)        # tally; keep NaNs visible
metadata["units"].value_counts().head(15)               # top 15
```

To write a clean 2-column CSV (header instead of a bare index):

```python
counts.rename_axis("frequency").reset_index(name="n_series").to_csv(path, index=False)
```

Gotcha: `value_counts()` returns a Series indexed by the value; `reset_index` is what
turns it into a real table.

---

## Sticking point 2 — "How do I filter the catalog by a keyword?" — type (K)

The learner does not need to write this — `search_metadata` already does it. Show:

```python
hits = search_metadata(metadata, ["henry hub", "rngwhhd"])   # OR over keywords
```

If they want to filter one column themselves (e.g. only weekly):

```python
mask = metadata["name"].str.contains("storage", case=False, na=False)
metadata.loc[mask]
# combine: metadata.loc[mask & (metadata["frequency"] == "W")]
```

Gotcha: `na=False` so missing text counts as "no match" instead of raising;
`str.contains` is a substring/regex test (pass `regex=False` for a literal).

If they start re-implementing `load_metadata`/`search_metadata`: STOP them — those
exist in `ng_models.io`. The task is to USE them. (The old TODOs implied otherwise;
this is the fix.)

---

## Sticking point 3 — "Which series should be my candidates?" — judgment, type (B)/(E)

Never hand over the pick. This is the core decision of the module.

- **L1 (diagnostic):** "Your search for 'export' returned ~2000 rows. Which single
  `series_id` would you actually feed a model, and what makes it the headline series
  rather than one regional or sectoral slice?"
- **L2 (point to location):** "Look at `frequency`, `units`, `end_date`, and
  `row_count` on the hits. Sort by those — the headline series is usually national,
  still current, and has the most observations."
- **L3 (small pattern, decision deferred):**
  ```python
  hits = search_metadata(metadata, kws)
  current = hits[hits["end_date"] >= "2025-01-01"]
  current.sort_values("row_count", ascending=False).head(3)
  ```
  "Pick the one or two you'll keep and write the `why_relevant` note yourself — the
  search can't justify the choice for you."

---

## Sticking point 4 — "These series are weekly and those are monthly — so what?" — type (C)

Frequency-misalignment intuition. This is the headline insight of the inventory.

- **L1:** "Your eventual target (Henry Hub) is weekly. Most fundamentals you found are
  monthly or annual. If you tried to put a weekly price and a monthly production figure
  in the same row, what would line up — and what wouldn't?"
- **L2:** "Check the `frequency` column for each candidate. Count how many are W/D vs
  M/A. Notice almost everything except price and storage is M or A."
- **L3:** "Aligning them later means resampling, e.g. `s.resample('W-FRI').last()` or
  forward-filling a monthly value across its weeks — and *each choice changes the
  meaning* (a monthly average is not the same as an end-of-month value). You don't have
  to solve alignment now; just record that this mismatch is the main obstacle for later
  modules and which series it affects."

---

## Sticking point 5 — "Are these two series comparable?" (Bcf vs MMcf vs $/MMBtu) — type (C)

- **L1:** "Are these two series in the same `units`? What is the ratio between Billion
  Cubic Feet and Million Cubic Feet?"
- **L2:** "Pull the `units` column for both candidates from the catalog and compare
  before you ever think about combining them."
- **L3:** "1 Bcf = 1000 MMcf; `$/MMBtu` is a price, not a volume, so it never combines
  with a volume series at all. State the conversion (or the incompatibility) explicitly
  in your report; don't add columns in different units."

---

## Sticking point 6 — "How do I open and verify a series file?" — type (K)

```python
hh = load_series_csv(DATA_DIR, "NG.RNGWHHD.W.csv", value_name="henry_hub")
print(hh.shape, hh["date"].min(), hh["date"].max())
```

Gotcha: `load_series_csv` RAISES if the file lacks `Date,Value`, so a clean load is the
verification. To cross-check the catalog:

```python
row = metadata.loc[metadata["filename"] == "NG.RNGWHHD.W.csv"].iloc[0]
print(row["row_count"], "vs actual", len(hh))
```

Whether a mismatch *matters* is a data-quality judgment the learner states (not type K).

---

## Sticking point 7 — "How do I make a bar chart of the counts?" — type (K)

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 4))
freq_counts.plot(kind="bar", ax=ax)
ax.set_title("Series count by frequency")
ax.set_xlabel("frequency"); ax.set_ylabel("n_series")
fig.tight_layout(); fig.savefig(OUTPUT_DIR / "frequency_bar.png", dpi=150); plt.close(fig)
```

Gotcha: `save_line_plot` in `ng_models.plotting` is for LINES (time series); for a bar
chart of catalog counts use matplotlib directly. After the chart renders, ask the L1
interpretation question below — a chart without a sentence is incomplete here.

Interpretation nudge (type C/I-adjacent, NOT direct): "What does this bar chart show
about which frequencies dominate — and what does it NOT tell you about whether those
series are useful for forecasting weekly Henry Hub?"
