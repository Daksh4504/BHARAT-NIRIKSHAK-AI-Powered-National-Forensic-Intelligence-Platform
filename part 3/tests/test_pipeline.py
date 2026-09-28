"""Tests for the analysis pipeline (no Streamlit runtime required)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from crime import analysis, data, map_view, risk, zones


@pytest.fixture(scope="module")
def incidents() -> pd.DataFrame:
    return data.generate_incidents(seed=20250101)


# --------------------------------------------------------------------------
# Zone geometry
# --------------------------------------------------------------------------


def test_zones_tile_without_overlap():
    """Every zone centre falls inside its own polygon and no other."""
    for zone in zones.ZONES:
        assert zone.contains(zone.centre_lat, zone.centre_lon), zone.label
        for other in zones.ZONES:
            if other.zone_id == zone.zone_id:
                continue
            if other.contains(zone.centre_lat, zone.centre_lon):
                pytest.fail(f"{zone.label} centre also inside {other.label}")


def test_projection_round_trips():
    lat, lon = 23.05, 72.57
    x, y = zones.latlon_to_xy(lat, lon)
    back_lat, back_lon = zones.xy_to_latlon(x, y)
    assert back_lat == pytest.approx(lat, abs=1e-9)
    assert back_lon == pytest.approx(lon, abs=1e-9)


def test_polygons_close_the_ring():
    for zone in zones.ZONES:
        assert zone.polygon[0] == zone.polygon[-1], zone.label
        assert len(zone.polygon) == 7


def test_area_matches_hexagon_geometry():
    area = zones._regular_hex_area_km2(zones.HEX_RADIUS_M)
    assert zones.ZONES[0].area_km2 == pytest.approx(area, rel=1e-3)


# --------------------------------------------------------------------------
# Data generation
# --------------------------------------------------------------------------


def test_generator_is_deterministic():
    a = data.generate_incidents(seed=7)
    b = data.generate_incidents(seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_different_seeds_differ(incidents):
    a = data.generate_incidents(seed=7)
    b = data.generate_incidents(seed=8)
    assert list(a.columns) == list(b.columns)
    assert not a["latitude"].equals(b["latitude"])
    assert not a["zone_id"].equals(b["zone_id"])


def test_incidents_fall_inside_the_six_month_window(incidents):
    assert incidents["timestamp"].min() >= data.PERIOD_START
    assert incidents["timestamp"].max() <= data.PERIOD_END
    span_days = (incidents["timestamp"].max() - incidents["timestamp"].min()).days
    assert 175 <= span_days <= 182


def test_every_incident_lands_in_its_assigned_zone(incidents):
    """Sampling must not push points outside the zone they are attributed to."""
    by_id = {z.zone_id: z for z in zones.ZONES}
    sample = incidents.sample(400, random_state=0)
    for row in sample.itertuples():
        zone = by_id[row.zone_id]
        assert zone.contains(row.latitude, row.longitude), (
            f"{zone.label} does not contain its own incident"
        )


def test_no_duplicate_incident_ids(incidents):
    assert incidents["incident_id"].is_unique


def test_all_crime_types_and_severities_present(incidents):
    assert incidents["crime_type"].nunique() == len(data.CRIME_TYPES)
    assert set(incidents["severity"].unique()) <= set(data.SEVERITY_ORDER)


def test_night_flag_matches_hour(incidents):
    expected = (incidents["hour"] >= 20) | (incidents["hour"] < 6)
    assert (incidents["is_night"] == expected).all()


def test_hotspots_concentrate_incidents(incidents):
    """The designed hotspot zones should sit well above the median zone."""
    counts = incidents["zone_id"].value_counts()
    top_zone = counts.index[0]
    hotspot = next(
        z for z in zones.ZONES if (z.row, z.col) == (3, 4)
    )
    assert hotspot.zone_id == top_zone
    assert counts.iloc[0] > 2 * counts.median()


def test_monthly_volume_rises_over_the_window(incidents):
    monthly = incidents.groupby("month").size()
    assert len(monthly) == 6
    assert monthly.iloc[-1] > monthly.iloc[0]


# --------------------------------------------------------------------------
# Spatial + temporal analysis
# --------------------------------------------------------------------------


def test_spatial_summary_covers_every_zone(incidents):
    out = analysis.spatial_summary(incidents)
    assert len(out) == len(zones.ZONES)
    assert out["incidents"].sum() == len(incidents)
    assert (out["per_km2"] >= 0).all()


def test_density_is_consistent_with_counts(incidents):
    out = analysis.spatial_summary(incidents)
    expected = out["incidents"] / out["area_km2"]
    np.testing.assert_allclose(out["per_km2"], expected, rtol=1e-9)


def test_temporal_summary_shapes(incidents):
    t = analysis.temporal_summary(incidents)
    assert len(t["monthly"]) == 6
    assert len(t["weekday"]) == 7
    assert list(t["weekday"]["day_of_week"])[:2] == ["Monday", "Tuesday"]
    assert list(t["hourly"]["hour"]) == list(range(24))


def test_crime_type_mix_shares_sum_to_one(incidents):
    mix = analysis.crime_type_mix(incidents)
    assert mix["share"].sum() == pytest.approx(1.0)
    assert (mix["share"] >= 0).all()


def test_concentration_metrics_are_bounded(incidents):
    conc = analysis.concentration_metrics(incidents)
    assert 0.0 <= conc["top_zone_share"] <= 1.0
    assert 0.0 <= conc["top5_zone_share"] <= 1.0
    assert conc["top5_zone_share"] >= conc["top_zone_share"]
    assert 0.0 <= conc["hhi"] <= 1.0
    assert 0.0 <= conc["gini"] <= 1.0


def test_concentration_detects_a_single_hot_zone(incidents):
    """A dataset pushed entirely into one zone must score as near-maximal."""
    one = zones.ZONES[0]
    forced = incidents.copy()
    forced["zone_id"] = one.zone_id
    conc = analysis.concentration_metrics(forced)
    n_zones = len(zones.ZONES)
    assert conc["top_zone_share"] == pytest.approx(1.0)
    # The discretised Gini ceiling with one non-empty zone is (n-1)/n.
    assert conc["gini"] == pytest.approx((n_zones - 1) / n_zones, abs=1e-6)


def test_even_distribution_has_low_gini(incidents):
    """Counts spread round-robin across zones should read as near-perfectly even."""
    spread = incidents.head(len(zones.ZONES) * 10).copy()
    spread["zone_id"] = np.tile(
        [z.zone_id for z in zones.ZONES], len(spread) // len(zones.ZONES) + 1
    )[: len(spread)]
    conc = analysis.concentration_metrics(spread)
    assert conc["gini"] < 0.01
    assert conc["top_zone_share"] == pytest.approx(1 / len(zones.ZONES), rel=0.05)


def test_morans_i_detects_clustering(incidents):
    """Deliberate clustered hotspots should give a positive autocorrelation."""
    assert analysis.spatial_autocorrelation(incidents) > 0.05


def test_morans_i_is_near_zero_without_spatial_signal(incidents):
    """Averaging over permutations washes out the real spatial structure."""
    real = analysis.spatial_autocorrelation(incidents)
    rng = np.random.default_rng(0)
    null = []
    for _ in range(20):
        shuffled = incidents.copy()
        shuffled["zone_id"] = rng.permutation(shuffled["zone_id"].to_numpy())
        null.append(analysis.spatial_autocorrelation(shuffled))
    assert real > 3 * float(np.std(null)) + 0.05


def test_zone_trends_reports_direction(incidents):
    trends = analysis.zone_trends(incidents)
    assert len(trends) == len(zones.ZONES)
    assert set(trends["trend_direction"]) <= {"rising", "flat", "falling"}
    assert trends["mk_p"].between(0.0, 1.0).all()


def test_incident_points_projection(incidents):
    pts = analysis.incident_points(incidents)
    assert len(pts) == len(incidents)
    # Study area is ~28 km across, so |x|,|y| must be in the low tens of km.
    assert pts["x"].abs().max() < 30_000
    assert pts["y"].abs().max() < 30_000


# --------------------------------------------------------------------------
# Risk index
# --------------------------------------------------------------------------


def test_risk_scores_are_bounded_and_ordered(incidents):
    table = risk.build_risk_table(incidents)
    assert len(table) == len(zones.ZONES)
    assert table["risk_score"].between(0.0, 100.0).all()
    assert table["rank"].tolist() == sorted(table["rank"].tolist())
    assert table["risk_score"].is_monotonic_decreasing


def test_risk_score_equals_weighted_components(incidents):
    table = risk.build_risk_table(incidents)
    recomputed = (
        table["c_volume"] * 0.35
        + table["c_severity"] * 0.25
        + table["c_night_share"] * 0.20
        + table["c_trend"] * 0.20
    ) * 100.0
    np.testing.assert_allclose(table["risk_score"], recomputed, rtol=1e-9)


def test_weights_are_rescaled_to_one():
    w = risk.RiskWeights(volume=2.0, severity=0.0, night_share=0.0, trend=0.0)
    assert w.normalised()["volume"] == pytest.approx(1.0)


def test_all_zero_weights_fall_back_to_default():
    w = risk.RiskWeights(volume=0.0, severity=0.0, night_share=0.0, trend=0.0)
    assert w.normalised() == risk.DEFAULT_WEIGHTS


def test_volume_only_weighting_ranks_by_density(incidents):
    table = risk.build_risk_table(
        incidents,
        risk.RiskWeights(volume=1.0, severity=0.0, night_share=0.0, trend=0.0),
    )
    expected = table.sort_values("per_km2", ascending=False)
    assert table["label"].tolist() == expected["label"].tolist()


def test_severity_only_weighting_ranks_by_severity(incidents):
    table = risk.build_risk_table(
        incidents,
        risk.RiskWeights(volume=0.0, severity=1.0, night_share=0.0, trend=0.0),
    )
    expected = table.sort_values("mean_severity", ascending=False)
    assert table["label"].tolist() == expected["label"].tolist()


def test_trend_shrinks_low_volume_noise(incidents):
    """A quiet zone with high raw growth must not outscore a busy one on trend."""
    table = risk.build_risk_table(incidents)
    quiet = table[table["incidents"] < 60]
    busy = table[table["incidents"] > 300]
    if not quiet.empty and not busy.empty:
        assert quiet["c_trend"].max() <= busy["c_trend"].max() + 0.2


def test_top_zones_returns_requested_count(incidents):
    table = risk.build_risk_table(incidents)
    assert len(risk.top_zones(table, 5)) == 5
    assert risk.top_zones(table, 5)["rank"].tolist() == [1, 2, 3, 4, 5]


def test_component_breakdown_matches_weighted_contributions(incidents):
    weights = risk.RiskWeights()
    table = risk.build_risk_table(incidents, weights)
    long = risk.component_breakdown(table, weights)
    for comp in ("volume", "severity", "night_share", "trend"):
        chunk = long[long["component"] == risk.COMPONENT_LABELS[comp]]
        merged = chunk.merge(table, on="zone_id", suffixes=("_b", "_t"))
        np.testing.assert_allclose(
            merged["contribution"],
            merged[f"w_{comp}"],
            rtol=1e-9,
        )


def test_empty_selection_scores_zero(incidents):
    table = risk.build_risk_table(incidents.head(0))
    assert (table["risk_score"] == 0.0).all()
    assert (table["incidents"] == 0).all()


# --------------------------------------------------------------------------
# Map
# --------------------------------------------------------------------------


def test_risk_colour_endpoints():
    assert map_view.risk_colour(0)[:3] == map_view.RISK_RAMP[0]
    assert map_view.risk_colour(100)[:3] == map_view.RISK_RAMP[-1]
    assert map_view.risk_colour(50)[3] == 150


def test_risk_colour_clamps_out_of_range():
    assert map_view.risk_colour(-40)[:3] == map_view.RISK_RAMP[0]
    assert map_view.risk_colour(400)[:3] == map_view.RISK_RAMP[-1]
    assert map_view.risk_colour(float("nan"))[:3] == map_view.RISK_RAMP[0]


def test_map_serialises_with_expected_layers(incidents):
    import json

    table = risk.build_risk_table(incidents)
    deck = map_view.build_map(table, incidents.head(500), top_n=5, show_incidents=True)
    payload = json.loads(deck.to_json())
    types = [layer["@@type"] for layer in payload["layers"]]
    assert types[0] == "GeoJsonLayer"
    assert "TextLayer" in types
    assert "ScatterplotLayer" in types
    assert len(payload["layers"][0]["data"]) == len(zones.ZONES)


def test_map_flags_top_zones(incidents):
    table = risk.build_risk_table(incidents)
    deck = map_view.build_map(table, incidents.head(10), top_n=5, show_incidents=False)
    payload = deck.to_json()
    assert '"is_top": true' in payload or '"is_top":true' in payload


def test_map_omits_incident_layer_when_disabled(incidents):
    import json

    table = risk.build_risk_table(incidents)
    deck = map_view.build_map(table, incidents, top_n=5, show_incidents=False)
    types = [l["@@type"] for l in json.loads(deck.to_json())["layers"]]
    assert "ScatterplotLayer" not in types


def test_map_layers_share_one_coordinate_system(incidents):
    """deck.gl reads get_position as [lon, lat], so no layer may use local metres."""
    import json

    table = risk.build_risk_table(incidents)
    deck = map_view.build_map(
        table, incidents.head(200), top_n=5, show_incidents=True, show_labels=True
    )
    layers = {l["@@type"]: l for l in json.loads(deck.to_json())["layers"]}

    ring = layers["GeoJsonLayer"]["data"][0]["geometry"]["coordinates"][0][0]
    zone_lon, zone_lat = ring[0], ring[1]
    assert 72.0 < zone_lon < 73.0 and 22.0 < zone_lat < 24.0, "zones must be lon/lat"

    label_lon, label_lat = layers["TextLayer"]["data"][0]["position"]
    assert 72.0 < label_lon < 73.0 and 22.0 < label_lat < 24.0, "labels must be lon/lat"

    point = layers["ScatterplotLayer"]["data"][0]
    assert 72.0 < point["longitude"] < 73.0, "incident overlay must be lon/lat"
    assert 22.0 < point["latitude"] < 24.0, "incident overlay must be lon/lat"


def test_map_tooltip_is_forwarded_to_streamlit(incidents):
    """Streamlit drops non-dict tooltips, which would silently kill hover text."""
    from streamlit.elements.deck_gl_json_chart import _get_pydeck_tooltip

    table = risk.build_risk_table(incidents)
    deck = map_view.build_map(table, incidents, top_n=5, show_incidents=False)
    tooltip = _get_pydeck_tooltip(deck)
    assert tooltip, "Streamlit would render no tooltip"
    assert "{label}" in tooltip["text"]
    assert "{risk_tier}" in tooltip["text"]


def test_map_incident_layer_is_not_pickable(incidents):
    """Clicks are reserved for zones; the overlay has no zone fields to show."""
    import json

    table = risk.build_risk_table(incidents)
    deck = map_view.build_map(
        table, incidents.head(50), top_n=5, show_incidents=True, show_labels=False
    )
    layers = {l["@@type"]: l for l in json.loads(deck.to_json())["layers"]}
    assert layers["GeoJsonLayer"]["pickable"] is True
    assert layers["ScatterplotLayer"].get("pickable") is False
