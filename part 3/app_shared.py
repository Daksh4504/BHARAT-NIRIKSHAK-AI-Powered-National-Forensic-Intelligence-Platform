"""Shared sidebar controls and page scaffolding.

Pages import :func:`render_sidebar` so filters, weights, and cached data are set
up identically everywhere, and the filtered frame plus the risk table are
computed once per rerun.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from crime import risk as risk_mod
from crime.map_view import ZONE_LAYER_ID
from crime.state import (
    MAX_INCIDENT_POINTS,
    filter_incidents,
    initialise_state,
    kpi_row,
    load_incidents,
    risk_table_for,
)

TIME_BANDS = ["Day (06:00-19:59)", "Night (20:00-05:59)"]

WEIGHT_LABELS = {
    "volume": "Volume per km²",
    "severity": "Mean severity",
    "night_share": "Night-time share",
    "trend": "Recent trend",
}


@dataclass
class PageContext:
    """Everything a page needs, computed once per rerun."""

    incidents: pd.DataFrame
    filtered: pd.DataFrame
    risk_table: pd.DataFrame
    weights: risk_mod.RiskWeights
    top_n: int

    @property
    def kpis(self) -> list[dict]:
        return kpi_row(self.filtered, self.incidents)

    @property
    def map_incidents(self) -> pd.DataFrame:
        """Filtered incidents, capped for the map layer."""
        if len(self.filtered) <= MAX_INCIDENT_POINTS:
            return self.filtered
        return self.filtered.sample(MAX_INCIDENT_POINTS, random_state=0)


def render_sidebar() -> PageContext:
    """Draw the sidebar controls and return the page's data context."""
    initialise_state()
    incidents = load_incidents(st.session_state["seed"])

    st.sidebar.header("Filters", icon=":material/filter_alt:")

    date_range = st.sidebar.date_input(
        "Date range",
        value=(
            incidents["timestamp"].min().date(),
            incidents["timestamp"].max().date(),
        ),
        min_value=incidents["timestamp"].min().date(),
        max_value=incidents["timestamp"].max().date(),
        format="DD/MM/YYYY",
        key="date_range",
    )
    if isinstance(date_range, tuple) and len(date_range) == 1:
        date_range = (date_range[0], date_range[0])

    all_types = sorted(incidents["crime_type"].unique())
    crime_types = st.sidebar.pills(
        "Offence type",
        options=all_types,
        selection_mode="multi",
        key="crime_types",
    )

    severities = st.sidebar.pills(
        "Severity",
        options=["Low", "Medium", "High"],
        selection_mode="multi",
        key="severities",
    )

    periods = st.sidebar.pills(
        "Time of day",
        options=TIME_BANDS,
        selection_mode="multi",
        default=TIME_BANDS,
        key="periods",
    )

    st.sidebar.subheader("Risk weighting", icon=":material/tune:")
    st.sidebar.caption(
        "Weights are rescaled to sum to 1. Each is applied to a min-max "
        "normalised component, so the composite stays comparable."
    )
    w_volume = st.sidebar.slider(
        WEIGHT_LABELS["volume"], 0.0, 1.0, value=0.35, step=0.05, key="w_volume"
    )
    w_severity = st.sidebar.slider(
        WEIGHT_LABELS["severity"], 0.0, 1.0, value=0.25, step=0.05, key="w_severity"
    )
    w_night = st.sidebar.slider(
        WEIGHT_LABELS["night_share"], 0.0, 1.0, value=0.20, step=0.05, key="w_night"
    )
    w_trend = st.sidebar.slider(
        WEIGHT_LABELS["trend"],
        0.0,
        1.0,
        value=0.20,
        step=0.05,
        key="w_trend",
    )
    weights = risk_mod.RiskWeights(
        volume=w_volume, severity=w_severity, night_share=w_night, trend=w_trend
    )

    st.sidebar.subheader("Map layers", icon=":material/layers:")
    top_n = st.sidebar.slider(
        "Highlight top zones", 3, 15, value=5, step=1, key="top_n"
    )
    st.sidebar.toggle("Show zone labels", value=True, key="show_labels")
    st.sidebar.toggle(
        "Overlay individual incidents", value=False, key="show_incidents"
    )

    st.sidebar.caption(
        "Synthetic data: 6 months of mock incidents across a 63-zone hex "
        "tessellation of Ahmedabad."
    )

    filtered = filter_incidents(
        incidents,
        date_range if isinstance(date_range, tuple) else None,
        crime_types or None,
        severities or None,
        periods or None,
    )
    risk_table = risk_table_for(filtered, weights)

    return PageContext(
        incidents=incidents,
        filtered=filtered,
        risk_table=risk_table,
        weights=weights,
        top_n=top_n,
    )


def render_kpis(ctx: PageContext) -> None:
    """Render the headline metric row, warning if the filters exclude everything."""
    if ctx.filtered.empty:
        st.warning("No incidents match the current filters. Widen the date range or clear a filter.")
        return
    for metric in ctx.kpis:
        st.metric(
            metric["label"],
            metric["value"],
            metric["delta"],
            help=metric["help"],
            border=True,
        )


def render_page_header(title: str, caption: str) -> None:
    """Consistent page title block."""
    st.title(title, icon=":material/location_on:")
    st.caption(caption)


def picked_zone_id(event) -> int | None:
    """Resolve a clicked zone id from a pydeck selection payload.

    ``PydeckSelectionState`` is ``{"indices": {layer_id: [...]}, "objects":
    {layer_id: [...]}}``. For a GeoJsonLayer the selected object is the raw
    feature, so ``zone_id`` lives under its ``properties``. Anything else falls
    back to the feature index, which matches the zone ordering used everywhere
    else in the app.
    """
    selection = getattr(event, "selection", None)
    if not selection:
        return None

    objects = getattr(selection, "objects", None) or {}
    for layer_id, picked in objects.items():
        if layer_id != ZONE_LAYER_ID:
            continue
        for feature in picked or []:
            if isinstance(feature, dict):
                props = feature.get("properties")
                if isinstance(props, dict) and "zone_id" in props:
                    return int(props["zone_id"])

    indices = getattr(selection, "indices", None) or {}
    for layer_id, positions in indices.items():
        if layer_id == ZONE_LAYER_ID and positions:
            return int(positions[0])
    return None


def zone_detail_panel(
    risk_table: pd.DataFrame, top: pd.DataFrame, picked: int | None
) -> None:
    """Show figures for the pinned zone, or for the top zone when nothing is pinned."""
    focus = risk_table if picked is not None else top
    if focus.empty:
        st.caption("Select a zone on the map to see its figures.")
        return

    row = focus.iloc[0]
    st.metric(
        f"{row['label']} risk score",
        f"{row['risk_score']:.1f}",
        row["risk_tier"],
        delta_color="off",
        border=True,
        help="Composite 0-100 index built from the four weighted components.",
    )
    st.table(
        {
            "Metric": [
                "Rank",
                "Incidents",
                "Incidents per km²",
                "Mean severity",
                "Night share",
                "Half-over-half growth",
                "Trend test",
            ],
            "Value": [
                f"#{int(row['rank'])} of {len(risk_table)}",
                f"{int(row['incidents']):,}",
                f"{row['per_km2']:.1f}",
                f"{row['mean_severity']:.2f}",
                f"{row['night_share'] * 100:.1f}%",
                f"{row['growth_pct']:+.1f}%",
                str(row["trend_direction"]),
            ],
        },
        width="stretch",
    )
    if picked is None:
        st.caption("Click a zone on the map to pin its details here.")

    st.markdown(f"**Top {len(top)} zones**")
    st.dataframe(
        top[["rank", "label", "incidents", "risk_score", "risk_tier"]],
        column_config={
            "rank": st.column_config.NumberColumn("Rank", format="%d"),
            "label": "Zone",
            "incidents": st.column_config.NumberColumn("Incidents", format="%.0f"),
            "risk_score": st.column_config.ProgressColumn(
                "Risk score", min_value=0, max_value=100, format="%.1f"
            ),
            "risk_tier": "Tier",
        },
        hide_index=True,
        height=240,
    )
