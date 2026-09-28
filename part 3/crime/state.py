"""Cached data loading and shared app state helpers.

Keeping the expensive work behind one cached call per dataset means widget
changes only re-run the cheap filtering, so the app stays responsive.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from . import analysis, data as data_mod, risk as risk_mod

TOP_N = 5
MAX_INCIDENT_POINTS = 20_000


@st.cache_data(show_spinner=False, max_entries=4)
def load_incidents(seed: int = 20250101) -> pd.DataFrame:
    """Generate (and cache) the six-month mock incident table."""
    return data_mod.generate_incidents(seed=seed)


@st.cache_data(show_spinner=False, max_entries=4)
def cached_risk_table(incidents: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Cached risk scoring for the full dataset (the unfiltered default)."""
    return risk_mod.build_risk_table(incidents)


def initialise_state() -> None:
    """Set up session state defaults in one place."""
    st.session_state.setdefault("top_n", TOP_N)
    st.session_state.setdefault("show_incidents", False)
    st.session_state.setdefault("show_labels", True)
    st.session_state.setdefault("weights", dict(risk_mod.DEFAULT_WEIGHTS))
    st.session_state.setdefault("selected_zone", None)
    st.session_state.setdefault("seed", 20250101)


def filter_incidents(
    df: pd.DataFrame,
    date_range: tuple[date, date] | None,
    crime_types: list[str] | None,
    severities: list[str] | None,
    periods: list[str] | None,
) -> pd.DataFrame:
    """Apply the sidebar filters. Cheap enough to run on every rerun."""
    out = df
    if date_range and len(date_range) == 2:
        start = pd.Timestamp(date_range[0])
        end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
        out = out[(out["timestamp"] >= start) & (out["timestamp"] < end)]
    if crime_types:
        out = out[out["crime_type"].isin(crime_types)]
    if severities:
        out = out[out["severity"].isin(severities)]
    if periods:
        mask = pd.Series(False, index=out.index)
        if "Day (06:00-19:59)" in periods:
            mask |= ~out["is_night"]
        if "Night (20:00-05:59)" in periods:
            mask |= out["is_night"]
        out = out[mask]
    return out


def risk_table_for(df: pd.DataFrame, weights: risk_mod.RiskWeights) -> pd.DataFrame:
    """Build the risk table for a filtered slice, cheaply enough for a rerun."""
    return risk_mod.build_risk_table(df, weights=weights)


def kpi_row(filtered: pd.DataFrame, all_incidents: pd.DataFrame) -> list[dict]:
    """Assemble the headline metrics shown above the map."""
    conc = analysis.concentration_metrics(filtered)
    total = len(filtered)
    prev_month = _previous_month_count(filtered)
    latest_month = _latest_month_count(filtered)
    delta = None
    if prev_month and latest_month is not None:
        change = (latest_month - prev_month) / prev_month * 100.0
        delta = f"{change:+.1f}% vs previous month"

    return [
        {
            "label": "Incidents in view",
            "value": f"{total:,}",
            "delta": delta,
            "help": f"{len(all_incidents):,} incidents in the full six-month dataset",
        },
        {
            "label": "Night-time share",
            "value": f"{filtered['is_night'].mean() * 100:.1f}%"
            if total
            else "0.0%",
            "delta": None,
            "help": "Share of incidents between 20:00 and 05:59",
        },
        {
            "label": "Top 5 zone share",
            "value": f"{conc['top5_zone_share'] * 100:.1f}%",
            "delta": None,
            "help": "Share of incidents in the five busiest zones",
        },
        {
            "label": "Spatial clustering (Gini)",
            "value": f"{conc['gini']:.3f}",
            "delta": None,
            "help": "Inequality of incident counts across zones. 0 is perfectly even.",
        },
    ]


def _month_counts(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby("month").size()


def _latest_month_count(df: pd.DataFrame) -> float | None:
    counts = _month_counts(df)
    if counts.empty:
        return None
    return float(counts.iloc[-1])


def _previous_month_count(df: pd.DataFrame) -> float:
    counts = _month_counts(df)
    if len(counts) < 2:
        return 0.0
    return float(counts.iloc[-2])
