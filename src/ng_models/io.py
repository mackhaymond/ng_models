"""Data loading helpers for the ng-models curriculum.

These functions read the raw EIA-style CSV files in ``data/`` into pandas
DataFrames with predictable column names and dtypes, so the notebooks can
assume a clean starting point.

pandas primer (for coders new to the library):
- A ``DataFrame`` is a 2-D table: named columns, each an arrays-like ``Series``.
- ``pd.read_csv(path)`` parses a CSV into a DataFrame, inferring dtypes per
  column (numbers -> int/float, everything else -> ``object``/string).
- ``pd.to_datetime(...)`` converts a column to real ``datetime64`` timestamps so
  you can sort, resample, and do date arithmetic. Passing ``format=...`` tells
  it the EXACT layout of the input and avoids wrong guesses (the bug below).
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

def load_metadata(data_dir: Path) -> pd.DataFrame:
    """Load the series catalog (``_metadata.csv``) describing every data file.

    Parameters
    ----------
    data_dir : Path
        Directory containing ``_metadata.csv`` (one row per available series:
        ``series_id``, ``name``, ``units``, ``filename``, ``start_date``,
        ``end_date``, ...).

    Returns
    -------
    pd.DataFrame
        The catalog with ``start_date`` / ``end_date`` parsed to real
        ``datetime64`` values.

    Why the dates need a MIXED-RADIX parser
    ---------------------------------------
    In the CSV these columns are integers whose width depends on the series
    frequency: daily/weekly rows store 8 digits (``20100101`` -> 2010-01-01),
    monthly rows store 6 (``202604`` -> 2026-04-01), and annual rows store 4
    (``2025`` -> 2025-01-01). If you hand an integer to ``pd.to_datetime``
    without a format it interprets it as a Unix epoch offset (nanoseconds since
    1970), producing garbage; if you force a single ``format='%Y%m%d'`` then the
    6- and 4-digit (monthly/annual) values fail and become ``NaT`` -- which
    silently empties ~98% of the catalog (annual is the largest group). So we
    convert to a digit string and parse each width with its own format. Monthly
    collapses to the first of the month and annual to Jan-1, which is the
    correct lower bound for coverage filters like ``end_date >= '2025-01-01'``.
    ``errors='coerce'`` turns any genuinely unparseable value into ``NaT``.
    """
    path = data_dir / "_metadata.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing metadata file: {path}")
    df = pd.read_csv(path)
    for col in ["start_date", "end_date"]:
        if col in df.columns:
            df[col] = _parse_eia_dates(df[col])
    return df


def _parse_eia_dates(values: pd.Series) -> pd.Series:
    """Parse EIA catalog date integers of mixed width to ``datetime64``.

    Handles 8-digit ``YYYYMMDD``, 6-digit ``YYYYMM`` (-> first of month), and
    4-digit ``YYYY`` (-> Jan 1) encodings in one column. Anything else becomes
    ``NaT``. See :func:`load_metadata` for why a single format is insufficient.
    """
    # .astype("string") so each integer becomes its literal digit string
    # ("2025", "202604", "20260515") rather than a nanosecond epoch offset.
    raw = values.astype("string").str.strip()
    out = pd.Series(pd.NaT, index=values.index, dtype="datetime64[ns]")
    for width, fmt in ((8, "%Y%m%d"), (6, "%Y%m"), (4, "%Y")):
        mask = raw.str.len() == width
        if mask.any():
            out.loc[mask] = pd.to_datetime(raw[mask], format=fmt, errors="coerce")
    return out

def load_series_csv(data_dir: Path, filename: str, value_name: str = "value") -> pd.DataFrame:
    """Load one time-series CSV into a tidy, date-sorted DataFrame.

    Parameters
    ----------
    data_dir : Path
        Directory containing the series file.
    filename : str
        File name (e.g. the ``filename`` from the metadata catalog). The file
        must have ``Date`` and ``Value`` columns.
    value_name : str, default ``"value"``
        Name to give the value column in the output. Pass something descriptive
        (e.g. ``"henry_hub_spot"``) so the column is self-documenting once you
        join several series together.

    Returns
    -------
    pd.DataFrame
        Two columns: ``date`` (``datetime64``) and ``<value_name>`` (float),
        sorted ascending by date with a fresh 0..n-1 integer index.

    Notes
    -----
    - The input columns are validated up front: a missing ``Date``/``Value``
      raises ``ValueError`` so you fail loudly rather than silently producing
      an empty frame.
    - ``errors='raise'`` on the dates is intentional here: a real series file
      should always have valid dates, so a bad value is a data problem worth
      stopping on (unlike the catalog above, where ``coerce`` is tolerant).
    - ``pd.to_numeric(..., errors='coerce')`` turns non-numeric values into
      ``NaN`` rather than erroring, so a stray blank/"NA" cell becomes a normal
      missing number you can handle downstream.
    - ``sort_values("date")`` then ``reset_index(drop=True)`` guarantees rows
      are in time order with a clean index -- important because lag/rolling
      features assume rows are already chronological.
    """
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing series file: {path}")
    df = pd.read_csv(path)
    expected = {"Date", "Value"}
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"{filename} missing expected columns: {sorted(missing)}")
    out = df.rename(columns={"Date": "date", "Value": value_name}).copy()
    out["date"] = pd.to_datetime(out["date"], errors="raise")
    out[value_name] = pd.to_numeric(out[value_name], errors="coerce")
    return out.sort_values("date").reset_index(drop=True)

def search_metadata(metadata: pd.DataFrame, keywords: list[str]) -> pd.DataFrame:
    """Filter the metadata catalog to rows matching ANY of the keywords.

    Parameters
    ----------
    metadata : pd.DataFrame
        A catalog as returned by :func:`load_metadata`.
    keywords : list[str]
        Case-insensitive substrings. A row matches if any keyword appears in
        its combined ``series_id``/``name``/``description``/``units`` text
        (logical OR). An empty list returns a copy of the whole catalog.

    Returns
    -------
    pd.DataFrame
        The matching rows (a copy, so editing it won't mutate the input).

    pandas notes
    ------------
    - ``Series.str.contains(sub, regex=False)`` does a literal substring test
      per row, returning a boolean ``Series`` (a mask). ``na=False`` treats
      missing text as "no match".
    - ``df.loc[mask]`` selects the rows where the mask is ``True``.
    - The four text columns are concatenated (with spaces) into one searchable
      string per row; ``metadata.get(col, "")`` defaults a missing column to an
      empty string so the search still works on partial catalogs.
    - ``mask`` starts as the scalar ``False`` and is OR-ed with each keyword's
      mask; pandas broadcasts the scalar against the boolean Series.
    """
    if not keywords:
        return metadata.copy()
    text = (
        metadata.get("series_id", "").astype(str) + " " +
        metadata.get("name", "").astype(str) + " " +
        metadata.get("description", "").astype(str) + " " +
        metadata.get("units", "").astype(str)
    ).str.lower()
    mask = False
    for keyword in keywords:
        mask = mask | text.str.contains(keyword.lower(), regex=False, na=False)
    return metadata.loc[mask].copy()
