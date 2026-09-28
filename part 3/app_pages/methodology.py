"""Methodology page: how the pipeline works and what the numbers mean."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from crime import analysis, risk as risk_mod
from crime.data import (
    CRIME_BASE_RATE,
    HOUR_PROFILE,
    NIGHT_SHARE,
    SEVERITY_MIX,
)
from crime.state import load_incidents
from crime.zones import HEX_RADIUS_M, LAT_MAX, LAT_MIN, LON_MAX, LON_MIN, ZONES
from app_shared import render_page_header, render_sidebar

ctx = render_sidebar()

render_page_header(
    "Methodology",
    "What the pipeline computes, in order, and why each step is there.",
)

st.header("The pipeline", icon=":material/account_tree:")

steps = pd.DataFrame(
    [
        {
            "Step": "1. Mock data",
            "What": f"{len(load_incidents()):,} synthetic incidents over six months "
            f"({ctx.incidents['timestamp'].min():%d %b %Y} to "
            f"{ctx.incidents['timestamp'].max():%d %b %Y}).",
        },
        {
            "Step": "2. Spatial + temporal analysis",
            "What": "Per-zone counts, density, severity, night share; monthly "
            "trend, weekday shape, and 24-hour profile.",
        },
        {
            "Step": "3. Crime concentration",
            "What": "Share of incidents in the top zones, Herfindahl index, "
            "Gini coefficient, and Moran's I for spatial clustering.",
        },
        {
            "Step": "4. Risk calculation",
            "What": "Four normalised components combined into a weighted 0-100 "
            "index per zone.",
        },
        {
            "Step": "5. Top 5 zones",
            "What": "The five highest composite scores, with every component "
            "retained so the ranking can be audited.",
        },
        {
            "Step": "6. Interactive map",
            "What": "deck.gl choropleth of zone risk with hover detail and "
            "click-to-pin selection.",
        },
    ]
)
st.dataframe(steps, hide_index=True, width="stretch")

st.header("Risk index", icon=":material/functions:")

st.markdown(
    "The score is a weighted sum of four components, each min-max normalised "
    "across the zones in the current selection and rescaled to 0-100:"
)

w = ctx.weights.normalised()
st.table(
    {
        "Component": [
            "Volume per km²",
            "Mean severity",
            "Night-time share",
            "Recent trend",
        ],
        "Definition": [
            "Incidents divided by zone area (each hex is "
            f"{HEX_RADIUS_M / 1000:.1f} km circumradius, "
            f"{ZONES[0].area_km2:.1f} km²).",
            "Mean severity score: Low = 1, Medium = 2, High = 3.",
            "Share of incidents between 20:00 and 05:59.",
            "Half-over-half growth, clipped to ±20% and shrunk toward zero for "
            "zones with fewer than 60 incidents so sampling noise cannot read as a surge.",
        ],
        "Weight": [f"{w['volume']:.0%}", f"{w['severity']:.0%}", f"{w['night_share']:.0%}", f"{w['trend']:.0%}"],
    },
    width="stretch",
)

st.markdown(
    "Normalisation is relative to the zones currently in view, so scores shift "
    "when filters narrow the selection. The weights are exposed in the sidebar "
    "and rescaled to sum to 1, so any combination is valid."
)

st.markdown("**Tiers**")
tier_df = pd.DataFrame(
    [
        {"Tier": label, "Band": f"score ≥ {threshold:g}" if threshold else "score < 40", "Meaning": meaning}
        for threshold, label, _ in risk_mod.TIERS
        for meaning in [
            {
                "Critical": "Highest priority for deployment.",
                "High": "Sustained above-average pressure.",
                "Moderate": "Around the city baseline.",
                "Low": "Below the city baseline.",
            }[label]
        ]
    ]
)
st.dataframe(tier_df, hide_index=True, width="stretch")

st.header("Concentration measures", icon=":material/query_stats:")

st.table(
    {
        "Measure": ["Top zone share", "HHI", "Gini", "Moran's I", "Mann-Kendall"],
        "What it answers": [
            "How much of the city's crime sits in its worst zone?",
            "How dominated is the city by a few zones? (0 = even, 1 = one zone)",
            "How unequal are counts across zones? (0 = even, 1 = total)",
            "Do busy zones sit next to busy zones? (positive = clustered)",
            "Is a zone's monthly series genuinely trending, or is that noise?",
        ],
        "Caution": [
            "Sensitive to a single outlier zone.",
            "Rises quickly with concentration; compare like-for-like zone counts.",
            "A Gini of 0 is not the same as safety.",
            "Contiguity here is hex adjacency, not real ward boundaries.",
            "Needs roughly 4+ monthly points; flags trend only at p < 0.05.",
        ],
    },
    width="stretch",
)

st.header("Zone definitions", icon=":material/grid_view:")

st.markdown(
    f"The study area spans **{LAT_MIN}° to {LAT_MAX}° N** and "
    f"**{LON_MIN}° to {LON_MAX}° E**, covering Ahmedabad's municipal area and "
    f"inner suburbs. It is tiled with **{len(ZONES)} hexagonal zones** of "
    f"{ZONES[0].area_km2:.1f} km² each. Hexagons tile without gaps or overlaps, "
    "so per-zone counts are directly comparable."
)
st.caption(
    "Zone labels (Zone A1, Zone B4, ...) are positional identifiers, not real "
    "ward names. Resident populations are modelled, since the incidents here are "
    "synthetic."
)

with st.expander("How the mock data is generated", icon=":material/science:"):
    st.markdown(
        "The generator is seeded, so results are reproducible. Offence types are "
        "drawn from a fixed mix; each has its own diurnal profile, night share, "
        "and severity mix. Night incidents are biased toward higher severity. "
        "Zone intensity includes a tight baseline plus deliberate clustered "
        "hotspots, and month and weekday multipliers add a mild upward trend and "
        "a weekend lift."
    )
    profile = pd.DataFrame(
        {
            "Offence": list(CRIME_BASE_RATE),
            "Base rate / 30 days": [CRIME_BASE_RATE[c] for c in CRIME_BASE_RATE],
            "Night share": [NIGHT_SHARE[c] for c in CRIME_BASE_RATE],
            "Severity mix (L/M/H)": [
                "/".join(f"{p:.2f}" for p in SEVERITY_MIX[c]) for c in CRIME_BASE_RATE
            ],
            "Peak hour": [
                f"{HOUR_PROFILE[c].index(max(HOUR_PROFILE[c])):02d}:00"
                for c in CRIME_BASE_RATE
            ],
        }
    )
    st.dataframe(
        profile,
        column_config={
            "Base rate / 30 days": st.column_config.NumberColumn(format="%.1f"),
            "Night share": st.column_config.NumberColumn(format="%.0%"),
        },
        hide_index=True,
    )

st.header("Limitations", icon=":material/warning:")

st.markdown(
    "- The data is synthetic. The pipeline is real, the incidents are not, so "
    "no conclusion here describes actual crime in Ahmedabad.\n"
    "- Risk scores are relative to the zones in the current filter selection.\n"
    "- Density uses modelled populations, so per-capita figures are indicative "
    "only.\n"
    "- Zones are equal-area hexagons, not police station or ward boundaries, so "
    "they do not align with how policing is actually organised."
)
