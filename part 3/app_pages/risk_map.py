"""Risk map page: the interactive map and the scoring behind it."""

from __future__ import annotations

import altair as alt
import streamlit as st

from crime import risk as risk_mod
from crime.map_view import MAP_HEIGHT, build_map
from app_shared import (
    picked_zone_id,
    render_page_header,
    render_sidebar,
    zone_detail_panel,
)

ctx = render_sidebar()

render_page_header(
    "Risk map",
    "Zone risk index on a 0-100 scale. Hover a zone for its breakdown, click to pin it.",
)

if ctx.filtered.empty:
    st.warning(
        "No incidents match the current filters. Widen the date range or clear a filter."
    )
    st.stop()

top = risk_mod.top_zones(ctx.risk_table, ctx.top_n)

# Reserve the map and detail slots before building the deck so a slow build does
# not blank out the page, then fill the map slot with the chart.
map_slot, detail_col = st.columns([3, 2], gap="medium")
with map_slot:
    map_placeholder = st.container()

with detail_col:
    st.subheader("Zone detail", icon=":material/info:")
    detail_slot = st.container()

deck = build_map(
    ctx.risk_table,
    ctx.map_incidents,
    top_n=ctx.top_n,
    show_incidents=st.session_state["show_incidents"],
    show_labels=st.session_state["show_labels"],
    height=MAP_HEIGHT,
)
with map_placeholder:
    event = st.pydeck_chart(
        deck,
        selection_mode="single-object",
        on_select="rerun",
        key="risk_map",
        height=MAP_HEIGHT,
    )
    st.caption(
        "Fill colour encodes the risk index (blue = low, red = high). The top "
        f"{ctx.top_n} zones are outlined in white. Turn on the incident "
        "overlay in the sidebar to inspect individual points."
    )

picked = picked_zone_id(event)
st.session_state["selected_zone"] = picked

with detail_slot:
    zone_detail_panel(ctx.risk_table, top, picked)

st.subheader("How each top score is built", icon=":material/stacked_bar_chart:")

focus_ids = [picked] if picked else top["zone_id"].tolist()
breakdown = risk_mod.component_breakdown(ctx.risk_table, ctx.weights)
breakdown = breakdown[breakdown["zone_id"].isin(focus_ids)]
if not breakdown.empty:
    st.caption(
        "Stacked contributions to the composite score. Weights come from the "
        "sidebar and are rescaled to sum to 1."
    )
    ranked = ctx.risk_table.set_index("zone_id")["rank"]
    breakdown = breakdown.assign(
        rank=breakdown["zone_id"].map(ranked)
    )
    stacked = (
        alt.Chart(breakdown)
        .mark_bar()
        .encode(
            x=alt.X(
                "contribution:Q",
                title="Points contributed to risk score (max 100)",
                stack="zero",
            ),
            y=alt.Y(
                "label:N",
                title="Zone",
                sort=alt.EncodingSortField("rank", order="ascending"),
            ),
            color=alt.Color(
                "component:N",
                title="Component",
                scale=alt.Scale(
                    range=["#4a7ba7", "#d1495b", "#7a9e9f", "#e0a458"]
                ),
            ),
            tooltip=[
                alt.Tooltip("label:N", title="Zone"),
                alt.Tooltip("component:N", title="Component"),
                alt.Tooltip("weight:Q", title="Weight", format=".0%"),
                alt.Tooltip("contribution:Q", title="Contribution", format="%.1f"),
            ],
        )
        .properties(height=max(200, 62 * breakdown["label"].nunique()))
    )
    st.altair_chart(stacked, width="stretch")

st.subheader("All zones by risk score", icon=":material/leaderboard:")

chart = (
    alt.Chart(ctx.risk_table)
    .mark_bar(cornerRadiusEnd=3)
    .encode(
        x=alt.X(
            "risk_score:Q", title="Risk score", scale=alt.Scale(domain=[0, 100])
        ),
        y=alt.Y(
            "label:N",
            title="Zone",
            sort=alt.EncodingSortField("risk_score", order="descending"),
        ),
        color=alt.Color(
            "risk_tier:N",
            title="Tier",
            scale=alt.Scale(
                domain=["Critical", "High", "Moderate", "Low"],
                range=["#cb181d", "#ef8a62", "#fdd0a2", "#a8cfe0"],
            ),
        ),
        tooltip=[
            alt.Tooltip("label:N", title="Zone"),
            alt.Tooltip("risk_score:Q", title="Risk score", format="%.1f"),
            alt.Tooltip("risk_tier:N", title="Tier"),
            alt.Tooltip("incidents:Q", title="Incidents", format=",.0f"),
            alt.Tooltip("per_km2:Q", title="Per km²", format=",.1f"),
            alt.Tooltip("mean_severity:Q", title="Mean severity", format=".2f"),
            alt.Tooltip("night_share:Q", title="Night share", format=".1%"),
            alt.Tooltip("growth_pct:Q", title="Growth", format="%+.1f%%"),
        ],
    )
    .properties(height=420)
)
st.altair_chart(chart, width="stretch")
