"""deck.gl map layers for the zone risk map and the incident scatter.

Uses pydeck (the engine behind ``st.map``) with a GeoJsonLayer for zone
polygons and a ScatterplotLayer for individual incidents, so the same map can
show both the aggregated risk surface and the raw points underneath it.
"""

from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd
import pydeck as pdk

from .zones import (
    ORIGIN_LAT,
    ORIGIN_LON,
    ZONES,
    ZONES_BY_ID,
    zone_boundaries_geojson,
)

# Map framing. The study area spans ~28 km, so zoom 11.6 gives a panoramic wide view
# of all zones across Ahmedabad without clipping.
MAP_ZOOM = 11.6
MAP_HEIGHT = 680

# deck.gl keys selection state by layer id, so the map and the click handler
# must agree on this value.
ZONE_LAYER_ID = "zones"

# YlOrRd-like risk ramp, low to high. Kept as explicit RGB so it does not shift
# with the Streamlit theme.
RISK_RAMP = [
    [49, 130, 189],
    [107, 174, 214],
    [253, 219, 199],
    [239, 138, 98],
    [203, 24, 29],
]


def risk_colour(score: float, alpha: int = 150) -> list[int]:
    """Map a 0-100 risk score to an RGBA fill on the risk ramp."""
    if not np.isfinite(score):
        score = 0.0
    t = float(np.clip(score, 0.0, 100.0)) / 100.0
    pos = t * (len(RISK_RAMP) - 1)
    idx = min(int(pos), len(RISK_RAMP) - 2)
    frac = pos - idx
    lo, hi = RISK_RAMP[idx], RISK_RAMP[idx + 1]
    rgb = [int(round(lo[i] + (hi[i] - lo[i]) * frac)) for i in range(3)]
    return [*rgb, alpha]


def _zone_features(
    risk_table: pd.DataFrame, 
    top_n: int, 
    focused_zone_id: Optional[int] = None
) -> list[dict]:
    """Merge risk scores onto the zone boundary features."""
    lookup = risk_table.set_index("zone_id")
    top_ids = set(risk_table.head(top_n)["zone_id"]) if top_n else set()
    features = []
    for feat in zone_boundaries_geojson():
        zone_id = feat["properties"]["zone_id"]
        if zone_id in lookup.index:
            row = lookup.loc[zone_id]
            is_focused = bool(focused_zone_id and zone_id == focused_zone_id)
            feat["properties"].update(
                {
                    "label": row["label"],
                    "incidents": int(row["incidents"]),
                    "per_km2": round(float(row["per_km2"]), 1),
                    "risk_score": round(float(row["risk_score"]), 1),
                    "risk_tier": row["risk_tier"],
                    "night_share": round(float(row["night_share"]) * 100, 1),
                    "mean_severity": round(float(row["mean_severity"]), 2),
                    "trend": row["trend_direction"],
                    "is_top": zone_id in top_ids,
                    "is_focused": is_focused,
                }
            )
        features.append(feat)
    return features


def build_map(
    risk_table: pd.DataFrame,
    incidents: pd.DataFrame,
    top_n: int = 5,
    show_incidents: bool = False,
    show_labels: bool = True,
    height: int = 680,
    focused_zone_id: Optional[int] = None,
    map_style: str = "dark",
    **kwargs,
) -> pdk.Deck:
    """Assemble the deck.gl map of zone risk with optional incident points.

    ``risk_table`` supplies scores, ``incidents`` supplies raw points (ignored
    when ``show_incidents`` is False). The view is framed on the whole study
    area so zones are never off-screen.
    """
    features = _zone_features(risk_table, top_n, focused_zone_id=focused_zone_id)
    scores = [f["properties"].get("risk_score", 0.0) for f in features]
    
    # Custom fills highlighting focused zone if set
    fills = []
    for f in features:
        score = f["properties"].get("risk_score", 0.0)
        if f["properties"].get("is_focused"):
            fills.append([255, 80, 0, 220])
        else:
            fills.append(risk_colour(score, alpha=165))

    top_flags = [bool(f["properties"].get("is_top", False)) for f in features]
    focused_flags = [bool(f["properties"].get("is_focused", False)) for f in features]

    lines = []
    widths = []
    for is_top, is_foc in zip(top_flags, focused_flags):
        if is_foc:
            lines.append([255, 230, 0, 255])  # Brilliant Gold for focused zone
            widths.append(4)
        elif is_top:
            lines.append([255, 255, 255, 240])  # Crisp white for top risk zones
            widths.append(3)
        else:
            if map_style == "dark":
                lines.append([70, 95, 130, 160])
            else:
                lines.append([70, 70, 70, 120])
            widths.append(1)

    layers: list[pdk.Layer] = [
        pdk.Layer(
            "GeoJsonLayer",
            id=ZONE_LAYER_ID,
            data=features,
            stroked=True,
            filled=True,
            get_fill_color=fills,
            get_line_color=lines,
            get_line_width=widths,
            line_width_min_pixels=1,
            pickable=True,
            auto_highlight=True,
            highlight_color=[255, 255, 255, 90],
        )
    ]

    if show_labels:
        # Clean TextLayer WITHOUT sdf fontSettings to avoid black bar rendering bugs
        label_rows = []
        for f, z in zip(features, ZONES):
            props = f["properties"]
            score = props.get("risk_score", 0)
            lbl = props.get("label", z.label)
            is_foc = props.get("is_focused", False)
            if is_foc:
                text_content = f"📍 {lbl}\n[{score:.0f}]"
                color = [255, 230, 0, 255]
                size = 14
            else:
                text_content = f"{lbl}\n{score:.0f}"
                color = [255, 255, 255, 230] if map_style == "dark" else [30, 30, 30, 240]
                size = 11

            label_rows.append(
                {
                    "position": (z.centre_lon, z.centre_lat),
                    "label": text_content,
                    "color": color,
                    "size": size,
                }
            )

        label_data = pd.DataFrame(label_rows)
        layers.append(
            pdk.Layer(
                "TextLayer",
                id="zone-labels",
                data=label_data,
                get_position="position",
                get_text="label",
                get_size="size",
                get_color="color",
                get_text_anchor="middle",
                get_alignment_baseline="center",
            )
        )

    if show_incidents and not incidents.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                id="incident-points",
                data=incidents,
                get_position=["longitude", "latitude"],
                get_radius=70,
                get_fill_color=[244, 63, 94, 180] if map_style == "dark" else [30, 30, 30, 190],
                pickable=False,
            )
        )

    # If focusing on a specific zone, center map camera on that zone
    if focused_zone_id and focused_zone_id in ZONES_BY_ID:
        target_zone = ZONES_BY_ID[focused_zone_id]
        lat_c = target_zone.centre_lat
        lon_c = target_zone.centre_lon
        zoom_val = 12.6
    else:
        lat_c = ORIGIN_LAT
        lon_c = ORIGIN_LON
        zoom_val = MAP_ZOOM

    view = pdk.ViewState(
        latitude=lat_c,
        longitude=lon_c,
        zoom=zoom_val,
        pitch=0,
        min_zoom=9,
        max_zoom=15,
    )

    return pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style=map_style,
        height=height,
        tooltip={
            "text": (
                "<b>{label}</b><br/>"
                "Risk score: {risk_score} ({risk_tier})<br/>"
                "Incidents: {incidents}<br/>"
                "Per km²: {per_km2}<br/>"
                "Mean severity: {mean_severity}<br/>"
                "Night share: {night_share}%<br/>"
                "Trend: {trend}"
            )
        },
    )
