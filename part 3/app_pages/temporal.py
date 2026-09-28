"""Temporal analysis page: when incidents happen and how that is shifting."""

from __future__ import annotations

import altair as alt
import numpy as np
import streamlit as st

from crime import analysis
from app_shared import render_page_header, render_sidebar

ctx = render_sidebar()

render_page_header(
    "Temporal analysis",
    "Monthly trend, day-of-week shape, and the 24-hour incident profile.",
)

if ctx.filtered.empty:
    st.warning("No incidents match the current filters. Widen the date range or clear a filter.")
    st.stop()

temporal = analysis.temporal_summary(ctx.filtered)
monthly = temporal["monthly"]
weekday = temporal["weekday"]
hourly = temporal["hourly"]
trends = analysis.zone_trends(ctx.filtered)

if monthly.empty:
    st.caption("Not enough data for a temporal breakdown in the current selection.")
    st.stop()

first_half = monthly["incidents"].iloc[: len(monthly) // 2]
second_half = monthly["incidents"].iloc[len(monthly) // 2 :]
overall_change = (
    (second_half.mean() - first_half.mean()) / first_half.mean() * 100.0
    if len(first_half) and first_half.mean() > 0
    else 0.0
)
peak_month = monthly.loc[monthly["incidents"].idxmax()]
peak_hour = hourly.loc[hourly["incidents"].idxmax()]
busiest_weekday = weekday.loc[weekday["incidents"].idxmax()]
quietest_weekday = weekday.loc[weekday["incidents"].idxmin()]
rising = trends[(trends["trend_direction"] == "rising") & (trends["incidents"] > 0)]

with st.container(horizontal=True):
    st.metric(
        "Half-over-half change",
        f"{overall_change:+.1f}%",
        border=True,
        help="Change in average monthly volume, second half of the selection vs first half.",
    )
    st.metric(
        "Busiest month",
        f"{peak_month['month']} ({peak_month['incidents']:,})",
        border=True,
        help="Month with the highest incident count in the current selection.",
    )
    st.metric(
        "Peak hour",
        f"{int(peak_hour['hour']):02d}:00",
        border=True,
        help="Hour of day with the most incidents.",
    )
    st.metric(
        "Busiest / quietest day",
        f"{busiest_weekday['day_of_week']} / {quietest_weekday['day_of_week']}",
        border=True,
        help="Weekday with the most and fewest incidents.",
    )

st.subheader("Monthly volume and severity", icon=":material/show_chart:")
base = (
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
)
severity_line = (
    alt.Chart(monthly)
    .mark_line(color="#d1495b", point=True, strokeWidth=2)
    .encode(
        x=alt.X("month:N", sort=list(monthly["month"])),
        y=alt.Y("mean_severity:Q", title="Mean severity", scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip("month:N", title="Month"),
            alt.Tooltip("mean_severity:Q", title="Mean severity", format=".2f"),
        ],
    )
)
st.altair_chart(
    (base + severity_line).resolve_scale(y="independent").properties(height=280),
    width="stretch",
)

left, right = st.columns(2)

with left:
    st.subheader("By day of week", icon=":material/calendar_view_week:")
    if not weekday.empty:
        day_chart = (
            alt.Chart(weekday)
            .mark_bar(color="#7a9e9f", cornerRadiusEnd=3)
            .encode(
                x=alt.X("day_of_week:N", title=None, sort=list(weekday["day_of_week"])),
                y=alt.Y("incidents:Q", title="Incidents"),
                tooltip=[
                    alt.Tooltip("day_of_week:N", title="Day"),
                    alt.Tooltip("incidents:Q", title="Incidents", format=",.0f"),
                ],
            )
            .properties(height=240)
        )
        st.altair_chart(day_chart, width="stretch")

with right:
    st.subheader("By hour of day", icon=":material/schedule:")
    if not hourly.empty:
        hourly = hourly.copy()
        hourly["period"] = np.where(hourly["hour"] >= 20, "Night", "Day")
        hour_chart = (
            alt.Chart(hourly)
            .mark_bar(cornerRadiusEnd=3)
            .encode(
                x=alt.X("hour:O", title="Hour", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("incidents:Q", title="Incidents"),
                color=alt.Color(
                    "period:N",
                    title=None,
                    scale=alt.Scale(domain=["Day", "Night"], range=["#f0c987", "#2a3f5f"]),
                ),
                tooltip=[
                    alt.Tooltip("hour:O", title="Hour"),
                    alt.Tooltip("incidents:Q", title="Incidents", format=",.0f"),
                    alt.Tooltip("mean_severity:Q", title="Mean severity", format=".2f"),
                ],
            )
            .properties(height=240)
        )
        st.altair_chart(hour_chart, width="stretch")

st.subheader("Zone-level trend", icon=":material/trending_up:")

if not trends.empty:
    chart = (
        alt.Chart(trends)
        .mark_point(size=110, opacity=0.8, filled=True)
        .encode(
            x=alt.X("growth_pct:Q", title="Half-over-half growth"),
            y=alt.Y("incidents:Q", title="Incidents in selection", scale=alt.Scale(type="log")),
            color=alt.Color(
                "trend_direction:N",
                title="Trend (Mann-Kendall)",
                scale=alt.Scale(
                    domain=["rising", "flat", "falling"],
                    range=["#d1495b", "#8d99ae", "#2a9d8f"],
                ),
            ),
            size=alt.Size("incidents:Q", title="Incidents", scale=alt.Scale(range=[40, 600])),
            tooltip=[
                alt.Tooltip("label:N", title="Zone"),
                alt.Tooltip("incidents:Q", title="Incidents", format=",.0f"),
                alt.Tooltip("growth_pct:Q", title="Growth", format="%+.1f%%"),
                alt.Tooltip("mk_p:Q", title="Mann-Kendall p", format=".3f"),
                alt.Tooltip("trend_direction:N", title="Trend"),
            ],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, width="stretch")
    st.caption(
        "Trend is flagged rising or falling only when the Mann-Kendall test "
        "rejects the null of no trend at p < 0.05. Bubble size scales with volume."
    )

    st.dataframe(
        trends.sort_values("growth_pct", ascending=False)[
            [
                "label",
                "incidents",
                "growth_pct",
                "monthly_slope",
                "mk_p",
                "trend_direction",
            ]
        ].rename(
            columns={
                "label": "Zone",
                "incidents": "Incidents",
                "growth_pct": "Growth %",
                "monthly_slope": "Monthly slope",
                "mk_p": "MK p-value",
                "trend_direction": "Trend",
            }
        ),
        column_config={
            "Growth %": st.column_config.NumberColumn(format="%+.1f%%"),
            "Monthly slope": st.column_config.NumberColumn(format="%+.2f"),
            "MK p-value": st.column_config.NumberColumn(format="%.3f"),
        },
        hide_index=True,
        height=320,
    )

if not rising.empty:
    st.caption(
        f"{len(rising)} of {len(trends)} zones show a statistically significant "
        f"rise: {', '.join(rising.sort_values('growth_pct', ascending=False)['label'].head(6))}."
    )
