"""Plotting helpers for the ng-models curriculum.

Thin wrappers over matplotlib that render a figure straight to a file, so the
notebooks can produce reproducible images without manual figure management.

matplotlib notes:
- ``fig, ax = plt.subplots()`` makes a Figure (the whole canvas) and one Axes
  (the plotting area). You draw on ``ax`` and save/close ``fig``.
- ``fig.savefig(path, dpi=...)`` writes the image; the format is inferred from
  the file extension (``.png``, ``.svg``, ...).
- ``plt.close(fig)`` releases the figure's memory -- important in loops/notebooks
  where un-closed figures otherwise accumulate.
"""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

def save_line_plot(df: pd.DataFrame, x: str, y: str, title: str, output_path: Path) -> Path:
    """Draw a single line plot of ``y`` against ``x`` and save it to disk.

    Parameters
    ----------
    df : pd.DataFrame
        Source data; must contain columns ``x`` and ``y``.
    x : str
        Column for the horizontal axis (e.g. ``"date"``). Also used as the
        x-axis label.
    y : str
        Column for the vertical axis. Also used as the y-axis label.
    title : str
        Figure title.
    output_path : Path
        Where to write the image. The extension sets the format.

    Returns
    -------
    Path
        ``output_path``, returned so callers can chain or log the saved
        location (e.g. ``img = save_line_plot(...)``).
    """
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
