# Private Solution Notes — Assignment 00: Repository and Natural Gas Data Inventory

Do not reveal during normal tutoring. Use to judge whether the learner's reasoning
is on track. This module is data discovery; the loaders already exist, so the work
is USING them well, narrowing candidates with judgment, and noting the frequency-
mismatch problem.

## Reference approach (sketch)

The starter already loads the catalog and writes `frequency_counts.csv` and
`top_units.csv`. The learner adds:

1. **Candidate selection** — loop over categories, search, narrow to headline series:

   ```python
   CATEGORY_KEYWORDS = {
       "price":       ["rngwhhd", "henry hub"],
       "storage":     ["working gas", "underground storage"],
       "production":  ["dry production", "marketed production", "gross withdrawals"],
       "consumption": ["total consumption", "delivered to consumers", "electric power"],
       "imports":     ["imports"],
       "exports":     ["exports"],
       "lng":         ["lng", "liquefied"],
   }
   keep_cols = ["series_id","name","description","units","frequency",
                "start_date","end_date","filename"]
   rows = []
   for cat, kws in CATEGORY_KEYWORDS.items():
       hits = search_metadata(metadata, kws)
       # narrow: prefer a national, monthly-or-finer headline series with full coverage
       hits = hits[hits["end_date"] >= "2025-01-01"]          # still current
       head = hits.sort_values("row_count", ascending=False).head(2)  # learner's judgment
       for _, r in head.iterrows():
           rows.append({**{c: r[c] for c in keep_cols}, "category": cat,
                        "why_relevant": "<<learner writes this>>"})
   candidates = pd.DataFrame(rows)
   candidates.to_csv(OUTPUT_DIR / "candidate_series.csv", index=False)
   ```

   The narrowing rule is a JUDGMENT call — do not hand them one. The point is they
   defend why a given `series_id` is the headline vs the hundreds of regional/sectoral
   variants.

2. **Verify file shape** — `load_series_csv` for 3-5 picks; print shape + min/max date;
   compare `len(series)` to the catalog `row_count`.

3. **One plot** — `freq_counts.plot(kind="bar")` saved to `outputs/`.

## Keyword searches that actually work (verified against this data/)

Against the shipped catalog (16,041 series): `search_metadata` ORs over
series_id/name/description/units, lowercased substring.

- `["rngwhhd"]` -> 4 rows: the Henry Hub spot price at W/D/M/A. **This is THE price series.**
- `["henry hub"]` -> 4 (same family).
- `["storage", "working gas"]` -> ~1076 (broad — many regional storage series).
- `["working gas", "underground storage"]` -> narrower storage set.
- `["dry", "production"]` -> ~1525 (broad — narrow to "Dry Natural Gas Production").
- `["consumption"]` -> ~575.
- `["export"]` -> ~2193 (very broad).
- `["lng"]` -> ~256.

The headline Henry Hub ids: `NG.RNGWHHD.W` (weekly), `.D` (daily), `.M`, `.A`. Weekly
is the natural target frequency for this curriculum. Units = `Dollars per Million Btu`.

## Expected catalog facts (qualitative — recompute, don't hard-require)

- ~16,041 series total. Frequency split is heavily annual: A ~12,911, M ~3,112,
  W = 13, D = 5. **Almost no weekly/daily series exist** — only price and storage live
  at high frequency. This is the single most important takeaway.
- Top units: Million Cubic Feet (~6,648), Billion Cubic Feet (~3,507), Dollars per
  Thousand Cubic Feet (~2,117), Million Barrels, Percent, BTU per Cubic Foot, etc.
  Note Bcf vs MMcf differ by 1000x; the price unit `$/MMBtu` appears only ~22 times.

## Expected columns of candidate_series.csv

`series_id, name, description, units, frequency, start_date, end_date, filename,
why_relevant` (a `category` column is a nice extra). `why_relevant` is learner-authored
and cannot come from the search.

## Module-specific common failure modes

- **Dumps all keyword hits** (thousands of rows) into candidate_series.csv instead of
  narrowing to headline series — misses the judgment that is the whole point.
- **Confuses `series_id` with `filename`** — treats the `.csv` name as the identity, or
  vice versa.
- **Misses the frequency-mismatch insight** — fails to notice that the price target is
  weekly/daily but nearly all fundamentals are monthly/annual, which is the headline
  modeling implication of the whole inventory.
- **Hard-codes counts** from eyeballing instead of `value_counts()`.
- **Ignores coverage** — keeps a series that ends years ago as a "candidate."
- **No `row_count` cross-check** — never verifies catalog row_count vs actual file length.
- **Re-implements the loaders** — the old TODOs implied writing load_metadata/
  search_metadata; they EXIST. If the learner reinvents them, redirect: use the helpers.
- **Scope creep** — tries to fit/forecast something; this module is discovery only.

## Assignment-specific hint strategy (L1->L2->L3 per decision point)

Decision points and their taxonomy types:

1. **Which series are the headline candidates? (type B/E-flavored judgment)**
   - L1: "Your search returned ~2000 rows for 'export'. Which ONE would you actually
     feed a model, and what makes it the headline vs a regional sub-series?"
   - L2: "Look at `frequency`, `units`, coverage (`end_date`), and `row_count` in the
     hits — sort by those to find the national, current, full-coverage series."
   - L3: filter to `end_date >= recent` and sort by `row_count`; pick top 1-2 and write
     `why_relevant` yourself. Don't hand them the pick.

2. **Frequency mismatch implication (type C)** — see HINTS.md type C. L1 asks what
   happens when a weekly price meets a monthly fundamental; L3 names resampling exists
   but defers the alignment decision to a later module.

3. **units sanity (type C)** — Bcf vs MMcf vs $/MMBtu; L1: "Are these two series in the
   same unit? What's the ratio between Bcf and MMcf?"

4. **row_count trust (type K + data hygiene)** — verifying file shape is type K (show
   `load_series_csv` call directly); whether the mismatch matters is a data-quality
   judgment they state.

## Agent response pattern

1. Name the highest-impact issue first (usually: did they narrow candidates, and did
   they catch the frequency mismatch).
2. Ask them to explain their narrowing rule before critiquing it.
3. Hint at the lowest useful level.
4. Re-run the script after revision and re-check outputs.
