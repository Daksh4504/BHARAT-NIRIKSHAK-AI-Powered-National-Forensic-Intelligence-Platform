"""Overview page: the pipeline's headline output at a glance."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from crime import analysis, risk as risk_mod
from app_shared import render_kpis, render_page_header, render_sidebar

ctx = render_sidebar()

render_page_header(
    "Ahmedabad crime concentration",
    "Six months of mock incident records, scored into zone-level risk.",
)

if ctx.filtered.empty:
    st.warning("No incidents match the current filters. Widen the date range or clear a filter.")
    st.stop()

with st.container(horizontal=True):
    render_kpis(ctx)

st.subheader("Top 5 highest-risk zones", icon=":material/leaderboard:")
top = risk_mod.top_zones(ctx.risk_table, ctx.top_n)

st.dataframe(
    top[
        [
            "rank",
            "label",
            "incidents",
            "per_km2",
            "mean_severity",
            "night_share",
            "growth_pct",
            "risk_score",
            "risk_tier",
        ]
    ].rename(
        columns={
            "rank": "Rank",
            "label": "Zone",
            "incidents": "Incidents",
            "per_km2": "Per km²",
            "mean_severity": "Mean severity",
            "night_share": "Night share",
            "growth_pct": "Growth %",
            "risk_score": "Risk score",
            "risk_tier": "Tier",
        }
    ),
    column_config={
        "Per km²": st.column_config.NumberColumn(format="%.1f"),
        "Mean severity": st.column_config.NumberColumn(format="%.2f"),
        "Night share": st.column_config.ProgressColumn(
            "Night share", min_value=0, max_value=1, format="%.0f%%"
        ),
        "Growth %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Risk score": st.column_config.ProgressColumn(
            "Risk score", min_value=0, max_value=100, format="%.1f"
        ),
        "Rank": st.column_config.NumberColumn(format="%d"),
        "Tier": st.column_config.TextColumn(help="Band on the 0-100 composite index"),
    },
    hide_index=True,
)

left, right = st.columns([3, 2])

with left:
    st.subheader("Monthly volume", icon=":material/show_chart:")
    monthly = analysis.temporal_summary(ctx.filtered)["monthly"]
    if not monthly.empty:
        chart = (
            alt.Chart(monthly)
            .mark_bar(color="#4a7ba7", cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("month:N", title="Month", sort=list(monthly["month"])),
                y=alt.Y("incidents:Q", title="Incidents"),
                tooltip=[
                    alt.Tooltip("month:N", title="Month"),
                    alt.Tooltip("incidents:Q", title="Incidents", format=",.0f"),
                    alt.Tooltip("mean_severity:Q", title="Mean severity", format=".2f"),
                    alt.Tooltip("night_share:Q", title="Night share", format=".1%"),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(chart, width="stretch")
    else:
        st.caption("Not enough data for a monthly trend in the current selection.")

with right:
    st.subheader("Offence mix", icon=":material/donut_large:")
    mix = analysis.crime_type_mix(ctx.filtered)
    if not mix.empty:
        pie = (
            alt.Chart(mix)
            .mark_arc(innerRadius=48, outerRadius=88, stroke="#ffffff", strokeWidth=1)
            .encode(
                theta=alt.Theta("incidents:Q"),
                color=alt.Color("crime_type:N", title="Offence"),
                tooltip=[
                    alt.Tooltip("crime_type:N", title="Offence"),
                    alt.Tooltip("incidents:Q", title="Incidents", format=",.0f"),
                    alt.Tooltip("share:Q", title="Share", format=".1%"),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(pie, width="stretch")
    else:
        st.caption("No offence data in the current selection.")

with st.expander("Full zone ranking", icon=":material/table_chart:"):
    st.dataframe(
        ctx.risk_table[
            [
                "rank",
                "label",
                "incidents",
                "per_km2",
                "mean_severity",
                "night_share",
                "growth_pct",
                "risk_score",
                "risk_tier",
            ]
        ],
        column_config={
            "Per km²": st.column_config.NumberColumn(format="%.1f"),
            "Mean severity": st.column_config.NumberColumn(format="%.2f"),
            "Night share": st.column_config.NumberColumn(format="%.1%"),
            "Growth %": st.column_config.NumberColumn(format="%+.1f%%"),
            "Risk score": st.column_config.ProgressColumn(
                min_value=0, max_value=100, format="%.1f"
            ),
        },
        hide_index=True,
        height=420,
    )
