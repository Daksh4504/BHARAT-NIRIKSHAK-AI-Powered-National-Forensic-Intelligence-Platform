"""Spatial analysis page: where incidents sit and how clustered they are."""

from __future__ import annotations

import altair as alt
import numpy as np
import streamlit as st

from crime import analysis
from crime.state import load_incidents
from app_shared import render_page_header, render_sidebar

ctx = render_sidebar()

render_page_header(
    "Spatial analysis",
    "Zone-level density, hotspot structure, and how concentrated the incidents are.",
)

if ctx.filtered.empty:
    st.warning("No incidents match the current filters. Widen the date range or clear a filter.")
    st.stop()

spatial = analysis.spatial_summary(ctx.filtered)
active = spatial[spatial["incidents"] > 0]

conc = analysis.concentration_metrics(ctx.filtered)
moran = analysis.spatial_autocorrelation(ctx.filtered)

with st.container(horizontal=True):
    st.metric(
        "Zones with incidents",
        f"{conc['zones_covered']} / {len(spatial)}",
        border=True,
        help="Zones that recorded at least one incident in the current selection.",
    )
    st.metric(
        "Busiest zone share",
        f"{conc['top_zone_share'] * 100:.1f}%",
        border=True,
        help="Share of all incidents occurring in the single busiest zone.",
    )
    st.metric(
        "Top 5 zone share",
        f"{conc['top5_zone_share'] * 100:.1f}%",
        border=True,
        help="Share of all incidents in the five busiest zones.",
    )
    st.metric(
        "Clustering (Moran's I)",
        f"{moran:+.3f}",
        border=True,
        help="Spatial autocorrelation of zone counts. Positive means busy zones cluster.",
    )

st.subheader("Incidents per zone", icon=":material/bar_chart:")
chart = (
    alt.Chart(active)
    .mark_bar(color="#4a7ba7", cornerRadiusEnd=3)
    .encode(
        x=alt.X("incidents:Q", title="Incidents"),
        y=alt.Y(
            "label:N",
            title="Zone",
            sort=alt.EncodingSortField("incidents", order="descending"),
        ),
        color=alt.Color(
            "night_share:Q",
            title="Night share",
            scale=alt.Scale(range=["#a8cfe0", "#2c4f6b"]),
        ),
        tooltip=[
            alt.Tooltip("label:N", title="Zone"),
            alt.Tooltip("incidents:Q", title="Incidents", format=",.0f"),
            alt.Tooltip("per_km2:Q", title="Per km²", format=",.1f"),
            alt.Tooltip("mean_severity:Q", title="Mean severity", format=".2f"),
            alt.Tooltip("night_share:Q", title="Night share", format=".1%"),
        ],
    )
    .properties(height=max(240, 16 * len(active)))
)
st.altair_chart(chart, width="stretch")

st.subheader("Concentration and clustering", icon=":material/equalizer:")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Where the incidents sit**")
    st.dataframe(
        active[
            [
                "label",
                "incidents",
                "per_km2",
                "per_10k_residents",
                "mean_severity",
                "night_share",
            ]
        ].rename(
            columns={
                "label": "Zone",
                "incidents": "Incidents",
                "per_km2": "Per km²",
                "per_10k_residents": "Per 10k residents",
                "mean_severity": "Mean severity",
                "night_share": "Night share",
            }
        ),
        column_config={
            "Per km²": st.column_config.NumberColumn(format="%.1f"),
            "Per 10k residents": st.column_config.NumberColumn(format="%.0f"),
            "Mean severity": st.column_config.NumberColumn(format="%.2f"),
            "Night share": st.column_config.NumberColumn(format="%.1%"),
        },
        hide_index=True,
        height=360,
    )

with col_b:
    st.markdown("**How uneven the distribution is**")
    st.table(
        {
            "Metric": [
                "Busiest zone share",
                "Top 5 zone share",
                "Herfindahl index (HHI)",
                "Gini coefficient",
                "Moran's I (autocorrelation)",
            ],
            "Value": [
                f"{conc['top_zone_share'] * 100:.1f}%",
                f"{conc['top5_zone_share'] * 100:.1f}%",
                f"{conc['hhi']:.4f}",
                f"{conc['gini']:.3f}",
                f"{moran:+.3f}",
            ],
            "Reading": [
                "Share in the single busiest zone",
                "Share in the five busiest zones",
                "Higher means more concentrated (1.0 = one zone)",
                "0 = perfectly even, 1 = all in one zone",
                "Positive = busy zones sit next to busy zones",
            ],
        },
        width="stretch",
    )

    top_ten = float(np.sort(active["incidents"].to_numpy())[::-1][:10].sum())
    total = float(active["incidents"].sum())
    share_ten = top_ten / total if total else 0.0
    st.metric(
        "Top 10 zones share",
        f"{share_ten * 100:.1f}%",
        border=True,
        help="Share of incidents in the ten busiest zones, out of all zones with incidents.",
    )

st.subheader("Offence type by zone", icon=":material/grid_on:")

by_zone = analysis.crime_type_by_zone(ctx.filtered)
if not by_zone.empty:
    heat = (
        alt.Chart(by_zone)
        .mark_rect()
        .encode(
            x=alt.X(
                "crime_type:N",
                title="Offence type",
                sort="-y",
            ),
            y=alt.Y(
                "label:N",
                title="Zone",
                sort=alt.EncodingSortField(
                    field="incidents", op="sum", order="descending"
                ),
            ),
            color=alt.Color(
                "incidents:Q",
                title="Incidents",
                scale=alt.Scale(range=["#f7fbff", "#08306b"]),
            ),
            tooltip=[
                alt.Tooltip("label:N", title="Zone"),
                alt.Tooltip("crime_type:N", title="Offence"),
                alt.Tooltip("incidents:Q", title="Incidents", format=",.0f"),
            ],
        )
        .properties(height=max(240, 14 * by_zone["label"].nunique()))
    )
    st.altair_chart(heat, width="stretch")
else:
    st.caption("No offence data in the current selection.")

full = load_incidents()
st.caption(
    f"Selection covers {len(ctx.filtered):,} of {len(full):,} incidents "
    "in the underlying six-month dataset."
)
