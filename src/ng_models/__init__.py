"""Shared helper library for the ng-models Henry Hub forecasting curriculum.

This package collects small, leakage-aware utilities the notebooks reuse so each
lesson can focus on modeling decisions rather than plumbing. Nothing here makes
modeling choices for you (target definition, feature inclusion, lag/window
selection, metric sufficiency) -- it only provides correct, well-documented
building blocks.

Modules and their helpers
-------------------------
``ng_models.io``
    load_metadata        - read the series catalog ``_metadata.csv`` (dates fixed).
    load_series_csv      - read one Date/Value series into a tidy date-sorted frame.
    search_metadata      - keyword-filter the catalog (OR over keywords).

``ng_models.features``
    add_lags             - add past-value lag columns (leakage-safe shift).
    add_rolling_stats    - add rolling mean/std over PAST values (shift(1) first).
    hdd_cdd_from_tavg    - heating/cooling degree days from avg temperature.

``ng_models.time_utils``
    add_calendar_columns - year/month/iso-week/quarter from a date column.
    make_forward_target  - attach the future target + forecast-origin bookkeeping.

``ng_models.metrics``
    mae, rmse            - error in the series' own units.
    mape                 - percentage error (warns when zero actuals are dropped).
    smape                - symmetric percentage error, bounded.
    summarize_predictions- all of the above as one dict for a comparison table.

``ng_models.plotting``
    save_line_plot       - render a line chart to a file and return its path.
"""
