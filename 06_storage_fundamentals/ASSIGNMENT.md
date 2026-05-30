# Assignment 06: Storage Fundamentals: Inventories, Seasonality, and Deviations

**Phase:** Gas Fundamentals  
**Level:** Intermediate  
**Estimated time:** 6-10 hours

## Data scope

Use Henry Hub and EIA weekly working-gas storage only. No weather or production yet.

Expected data inputs (already in `data/`, do not modify):

- **Anchor storage series:** `NG.NW2_EPG0_SWO_R48_BCF.W` — *Lower 48 States Natural Gas
  Working Underground Storage, Weekly*, in **Bcf**, file
  `NG.NW2_EPG0_SWO_R48_BCF.W.csv`. This is your primary series.
- **Regional storage series** (optional, for the deviation discussion — the Lower-48
  total is the sum of these regions):
  - `NG.NW2_EPG0_SWO_R31_BCF.W` — East
  - `NG.NW2_EPG0_SWO_R32_BCF.W` — Midwest
  - `NG.NW2_EPG0_SWO_R33_BCF.W` — South Central (with salt `NG.NW2_EPG0_SSO_R33_BCF.W`
    and nonsalt `NG.NW2_EPG0_SNO_R33_BCF.W` sub-regions)
  - `NG.NW2_EPG0_SWO_R34_BCF.W` — Mountain
  - `NG.NW2_EPG0_SWO_R35_BCF.W` — Pacific
- **Price series:** `NG.RNGWHHD.W.csv` — weekly Henry Hub spot, in **$/MMBtu**.

Both weekly series share the same Friday-ending date stamps and both run from
2010-01-01 onward (Henry Hub goes back to 1997, but storage starts 2010). Build your
panel on the **2010+ overlap**.

## Terms to learn

`working gas`, `underground storage`, `injection`, `withdrawal`, `injection/withdrawal
season`, `five-year average`, `inventory deviation`, `storage constraint`

Before coding, write one plain-English sentence for each term in your own words.
Cross-reference `docs/GLOSSARY_SEED.md` — it has seed definitions you should deepen,
not copy.

## Learning goals

- Learn why storage is the central balancing item in natural-gas fundamentals.
- Construct a storage seasonal norm and deviation from normal **using only past data**.
- Relate price levels and changes to storage tightness **without overclaiming causality**.

## Concepts you'll use

- **Working gas in storage.** Gas held in underground storage that can actually be
  withdrawn and sold, sitting on top of permanent "base/cushion gas" that stays in the
  ground to keep wells pressurized. EIA reports it weekly in **Bcf** (billion cubic
  feet). It is the market's running tally of "how much gas is in the bank."
- **Injection vs. withdrawal season.** From roughly **April–October** heating demand is
  low, so net gas flows *into* storage (injections, inventory rises). From roughly
  **November–March** winter heating pulls gas *out* (withdrawals, inventory falls). A
  positive week-over-week change is an injection; a negative one is a withdrawal. The
  "shoulder" months around the turn are where surprises move price the most.
- **Storage tightness vs. price.** When inventories sit far *below* the seasonal norm
  (a deficit), the market worries about running short in a cold snap, which tends to be
  bullish for price; a large *surplus* tends to be bearish. This is an *association*,
  confounded by weather and production — it is not a clean causal law.
- **Five-year average / seasonal norm.** The industry's default "normal" line: the
  average level of storage for the *same week-of-year* across prior years. Because gas
  is intensely seasonal, comparing today to "this week historically" is far more
  meaningful than comparing to last week. CRITICAL: for any forecasting use the norm
  must be built from **prior** years only (see the leakage warning below).
- **Inventory deviation (surplus / deficit).** Current working gas minus the seasonal
  norm for the same week. This is the number traders actually watch — it strips out the
  predictable seasonal swing and leaves the "are we tighter or looser than usual?" signal.
- **Bcf vs. $/MMBtu — incommensurability.** Storage is a *volume* (Bcf); price is a
  *rate* ($/MMBtu). You cannot add, subtract, or directly ratio them. They live on
  different axes and need different y-scales on any shared plot. Relating them means
  comparing *shapes and turning points*, not arithmetic.

## The five-year-average leakage trap (read before task 4)

The five-year average is the easiest place in this whole curriculum to leak the future.
Two rules:

1. **Not centered.** A symmetric/centered seasonal mean (e.g. averaging weeks on both
   sides of the target week, or a full-sample groupby-by-week mean) uses weeks that come
   *after* your forecast origin. That is future data. Define the norm operationally as
   the **expanding, lagged seasonal norm**: for week-of-year *w* in year *Y*, average the
   value at week *w* over years strictly **before** *Y* (e.g. the prior 5 years, or all
   prior years if you have fewer than 5). No data from year *Y* or later enters the norm
   for year *Y*.
2. **No future data, ever.** Even the current year's own week must not be in its own
   norm. The deviation for a week = that week's actual minus a norm computed only from
   earlier years' same-week values.

(For a purely descriptive seasonality *plot* a full-sample average is fine — just label
it as descriptive and never feed it into a forecast feature.)

## The EIA publication lag (read before any price/storage merge)

EIA releases the Weekly Natural Gas Storage Report on **Thursday around 10:30 ET, for
the week ending the prior Friday**. So the storage number stamped "Friday week W" is not
public until the following Thursday — roughly **5–6 days later**.

Consequence for modeling: **today's storage reading cannot explain or predict a price
that printed earlier in the week.** If you ever use storage to say something about price,
you must **lag the storage series** so that on any given date you only use the most
recent storage figure that was *already published*. A storage value and a price value
sharing the same date row is a leakage red flag — check who published when. (This module
is mostly descriptive, but you must state this rule in your report and respect it if you
build any predictive feature.)

## Date-alignment strategy

Both the weekly Henry Hub series and the weekly storage series carry the same
Friday-ending date stamps, so alignment is unusually clean here:

- **Recommended: inner join on `date`, 2010+.** Keep only weeks present in both series.
  This drops the 1997–2009 price history (no storage then) and gives a clean panel.
- **Alternatives to know (and when they bite):**
  - *`ffill` / forward-fill:* if you had a daily price and weekly storage, you would
    forward-fill the last *published* storage onto each price day — but only after
    lagging for the publication delay, or you forward-fill future knowledge.
  - *`pd.merge_asof`:* joins each row to the most recent earlier row of the other series
    (`direction="backward"`). This is the correct tool when dates do *not* line up and
    you want "latest value known as of date X" — and it naturally respects the
    publication lag if you offset correctly.
  - For this module the inner join is enough; mention the alternatives in your report and
    say why you chose the join you chose.

## Tasks

1. Use `search_metadata` to confirm the U.S. weekly working-gas series and identify the
   Lower-48 anchor (`NG.NW2_EPG0_SWO_R48_BCF.W`) and the regional series. Record the
   units and frequency from the metadata, not from memory.
2. Load the Lower-48 storage series and align it to weekly Henry Hub dates with an inner
   join on `date` (2010+). Document your join choice and why.
3. Compute **weekly storage change** (`diff`) and classify each week as an injection
   (change > 0) or withdrawal (change < 0). Sanity-check that injections cluster in
   summer and withdrawals in winter.
4. Compute the **storage deviation from a seasonal norm using only past data** (the
   expanding, lagged five-year-average defined above). Decide and defend: 5 prior years
   vs. all prior years, and what to do for the early years where you have fewer than 5.
   *(This is your call to make and justify — there is no single right answer.)*
5. Plot (a) storage seasonality (level by week-of-year, overlaid by year) and (b) Henry
   Hub price vs. storage deviation on a shared time axis (two y-axes — they are in
   different units). Write an economic interpretation of what the deviation does and does
   not tell you.

## Package guide

Minimal API snippets for the libraries this module needs. These cover *how to call* the
library; the modeling *decisions* (which norm, which join, how to interpret) are yours.

```python
# --- ng_models helpers (already importable; see main.py for the sys.path setup) ---
from ng_models.io import load_metadata, load_series_csv, search_metadata
from ng_models.time_utils import add_calendar_columns
from ng_models.plotting import save_line_plot

meta = load_metadata(DATA_DIR)                       # series catalog (dates parsed)
hits = search_metadata(meta, ["storage", "working gas"])  # OR-match on keywords
stor = load_series_csv(DATA_DIR, "NG.NW2_EPG0_SWO_R48_BCF.W.csv", value_name="storage_bcf")
df   = add_calendar_columns(df, date_col="date")     # adds year, month, iso_week, ...

# --- pandas: merge two weekly series on date (inner join keeps the overlap) ---
panel = stor.merge(hh, on="date", how="inner").sort_values("date").reset_index(drop=True)

# --- pandas: week-over-week change, then classify the sign ---
panel["storage_change_bcf"] = panel["storage_bcf"].diff()        # NaN on first row
panel["flow_type"] = np.where(panel["storage_change_bcf"] >= 0, "injection", "withdrawal")

# --- pandas: same-week-of-year mean over PRIOR years only (expanding, lagged) ---
# .groupby(...).expanding().mean() then .shift(1) inside each week-of-year group so the
# current year's own value is excluded. You decide the exact window; see ASSIGNMENT task 4.
g = panel.groupby("iso_week")["storage_bcf"]
panel["seasonal_norm"] = g.transform(lambda s: s.expanding().mean().shift(1))
panel["storage_deviation_bcf"] = panel["storage_bcf"] - panel["seasonal_norm"]

# --- matplotlib: two series, two y-axes (different units) ---
fig, ax1 = plt.subplots(figsize=(11, 5))
ax1.plot(panel["date"], panel["hh_price"], color="tab:blue", label="HH $/MMBtu")
ax2 = ax1.twinx()                                    # second y-axis sharing the x-axis
ax2.plot(panel["date"], panel["storage_deviation_bcf"], color="tab:red", label="dev Bcf")
ax1.set_ylabel("Henry Hub ($/MMBtu)"); ax2.set_ylabel("Storage deviation (Bcf)")
fig.savefig(OUTPUT_DIR / "hh_vs_storage_deviation.png", dpi=120, bbox_inches="tight")
plt.close(fig)

# --- pandas: seasonal plot, one line per year ---
for yr, sub in panel.groupby("year"):
    ax.plot(sub["iso_week"], sub["storage_bcf"], label=str(yr), alpha=0.6)
```

> The `seasonal_norm` snippet shows the *shape* of a leakage-safe norm. You still must
> decide whether to cap it at 5 prior years, how to handle the first years, and whether
> `iso_week` or `month` is the right grain — and defend it in the report.

## Deliverables

- `outputs/storage_panel.csv` — date, storage_bcf, hh_price, storage_change_bcf,
  flow_type, seasonal_norm, storage_deviation_bcf (plus your calendar columns).
- `outputs/storage_seasonality.png`
- `outputs/hh_vs_storage_deviation.png`
- `REPORT.md` (start from `REPORT_TEMPLATE.md`).

## Rules

- Keep raw data immutable. Save generated files under this assignment's `outputs/` folder.
- Resolve paths via `ng_models.paths` (`data_dir(HERE)` / `ensure_output_dir`), never
  hard-coded relative `../data`.
- Write down every assumption about dates, units, frequency conversion, missing values,
  and **publication lag**.
- A chart is not enough. Every chart needs a sentence on what it shows and what it does
  not show.
- Do not move to a more complex analysis until the seasonal norm is provably
  leakage-free.

## Questions to answer in `REPORT.md`

- What is the target or object of analysis?
- What dates and units are involved? (Name the Bcf-vs-$/MMBtu incommensurability.)
- What was the most important data decision (join, norm window, lag)?
- How did you make the five-year average leakage-safe?
- What result surprised you?
- What would you not trust yet?
- What should the next assignment investigate?
