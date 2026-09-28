"""End-to-end app tests using Streamlit's headless AppTest runner.

These exercise the real Streamlit script path (navigation, widgets, charts, map
serialisation) without launching a browser, so a broken page fails here rather
than in front of a user.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "streamlit_app.py")
PAGES = [
    "app_pages/overview.py",
    "app_pages/spatial.py",
    "app_pages/temporal.py",
    "app_pages/risk_map.py",
    "app_pages/methodology.py",
]
PAGE_TITLES = {
    "app_pages/overview.py": "Overview",
    "app_pages/spatial.py": "Spatial analysis",
    "app_pages/temporal.py": "Temporal analysis",
    "app_pages/risk_map.py": "Risk map",
    "app_pages/methodology.py": "Methodology",
}


@pytest.fixture
def app() -> AppTest:
    """A freshly loaded app per test, so widget changes never leak between them."""
    at = AppTest.from_file(APP, default_timeout=180)
    at.run()
    assert not at.exception, at.exception
    return at


def _go(app: AppTest, page: str) -> AppTest:
    """Switch to a page and rerun, surfacing any exception as a test failure."""
    app.switch_page(page)
    app.run()
    assert not app.exception, f"{PAGE_TITLES[page]} raised: {app.exception}"
    return app


def _charts(at: AppTest) -> list:
    """Altair charts, which AppTest 1.63 exposes as untyped elements."""
    return list(at.get("vega_lite_chart"))


def _all_text(at: AppTest) -> str:
    """Every piece of prose on the page, so assertions don't depend on layout."""
    parts = [m.value for m in at.markdown] + [c.value for c in at.caption]
    parts += [s.value for s in at.subheader] + [h.value for h in at.header]
    parts += [t.value for t in at.title] + [c.value for c in at.caption]
    for frame in [*at.table, *at.dataframe]:
        parts.append(" ".join(map(str, frame.value.to_numpy().ravel())))
    return " ".join(str(p) for p in parts)


def test_app_loads(app: AppTest):
    assert app.title[0].value.startswith("Ahmedabad")


def test_every_page_renders(app: AppTest):
    for page in PAGES:
        _go(app, page)


def test_overview_shows_kpis_and_charts(app: AppTest):
    at = _go(app, "app_pages/overview.py")
    labels = {m.label for m in at.metric}
    assert "Incidents in view" in labels
    assert "Top 5 zone share" in labels
    assert at.dataframe, "expected the zone ranking table"
    # Monthly volume plus offence mix.
    assert len(_charts(at)) >= 2, f"expected >=2 charts, got {len(_charts(at))}"


def test_overview_top_five_table_has_five_rows(app: AppTest):
    at = _go(app, "app_pages/overview.py")
    assert len(at.dataframe[0].value) == 5


def test_spatial_page_reports_concentration(app: AppTest):
    at = _go(app, "app_pages/spatial.py")
    labels = {m.label for m in at.metric}
    assert "Clustering (Moran's I)" in labels
    assert "Top 5 zone share" in labels
    # Zone bar chart plus the offence-by-zone heatmap.
    assert len(_charts(at)) >= 2, f"expected >=2 charts, got {len(_charts(at))}"


def test_temporal_page_covers_all_three_breakdowns(app: AppTest):
    at = _go(app, "app_pages/temporal.py")
    labels = {m.label for m in at.metric}
    assert "Half-over-half change" in labels
    assert "Peak hour" in labels
    assert "Busiest / quietest day" in labels
    # Monthly, weekday, hourly, and the zone trend scatter.
    assert len(_charts(at)) >= 4, f"expected >=4 charts, got {len(_charts(at))}"


def test_risk_map_renders_breakdown_and_ranking(app: AppTest):
    """PyDeck charts have no AppTest accessor, so assert on the surrounding UI.

    A blank map still produces no exception, so the meaningful check is that the
    page's non-map elements (breakdown, ranking, zone detail) all resolve from
    the same filtered dataset.
    """
    at = _go(app, "app_pages/risk_map.py")
    assert not at.exception
    # Component breakdown plus the all-zones ranking scatter.
    assert len(_charts(at)) >= 2, f"expected >=2 charts, got {len(_charts(at))}"
    assert at.dataframe, "expected the all-zones ranking table"
    assert any("Zone detail" in s.value for s in at.subheader), (
        "expected the zone detail panel"
    )


def test_risk_map_survives_an_overlay_toggle(app: AppTest):
    """Turning on the incident overlay re-runs build_map with a scatter layer."""
    at = _go(app, "app_pages/risk_map.py")
    toggles = {t.label: t for t in app.sidebar.toggle}
    toggles["Overlay individual incidents"].set_value(True)
    app.run()
    assert not app.exception, app.exception
    # Same page content still present, meaning the extra layer built cleanly.
    assert app.dataframe, "expected the ranking table after enabling the overlay"


def test_risk_table_ranks_are_contiguous(app: AppTest):
    at = _go(app, "app_pages/overview.py")
    ranking = at.dataframe[0].value
    assert list(ranking["Rank"]) == [1, 2, 3, 4, 5]
    scores = list(ranking["Risk score"])
    assert scores == sorted(scores, reverse=True)


def test_methodology_documents_the_formula(app: AppTest):
    at = _go(app, "app_pages/methodology.py")
    text = _all_text(at)
    assert "weighted sum" in text
    assert "min-max normalised" in text
    # The four components and the concentration measures are both spelled out.
    for component in ("Volume per km", "Mean severity", "Night-time share"):
        assert component in text, f"missing component: {component}"
    for measure in ("Gini", "HHI", "Moran's I"):
        assert measure in text, f"missing concentration measure: {measure}"


def test_incident_filter_shrinks_the_view(app: AppTest):
    """Selecting a single offence type must reduce the incident count."""
    at = _go(app, "app_pages/overview.py")
    baseline = next(m for m in at.metric if m.label == "Incidents in view").value

    app.sidebar.pills[0].set_value(["Snatching"])
    app.run()
    assert not app.exception, app.exception
    after = next(m for m in app.metric if m.label == "Incidents in view").value
    assert int(after.replace(",", "")) < int(baseline.replace(",", ""))


def test_weight_sliders_change_the_ranking(app: AppTest):
    """Pushing all weight onto volume must reorder the table by density."""
    at = _go(app, "app_pages/overview.py")
    before = list(at.dataframe[0].value["Zone"])

    sliders = {s.label: s for s in app.sidebar.slider}
    sliders["Volume per km²"].set_value(1.0)
    sliders["Mean severity"].set_value(0.0)
    sliders["Night-time share"].set_value(0.0)
    sliders["Recent trend"].set_value(0.0)
    app.run()
    assert not app.exception, app.exception

    after = list(app.dataframe[0].value["Zone"])
    assert after != before, "expected the ranking to react to re-weighting"


def test_narrow_date_range_keeps_the_page_alive(app: AppTest):
    app.sidebar.date_input[0].set_value(("2025-06-01", "2025-06-07"))
    app.run()
    assert not app.exception, app.exception
    at = _go(app, "app_pages/temporal.py")
    assert at.metric, "expected metrics for the narrowed window"


def test_narrow_selection_to_nothing_is_handled(app: AppTest):
    """An impossible filter combination must warn, not crash."""
    app.sidebar.pills[0].set_value(["Robbery"])
    app.sidebar.pills[2].set_value([])
    app.sidebar.date_input[0].set_value(("2025-06-01", "2025-06-01"))
    app.run()
    app.run()
    assert not app.exception, app.exception


def test_map_layers_carry_ids_for_selections():
    """st.pydeck_chart keys selection state by layer id, so ids are mandatory."""
    from crime import data, risk
    from crime.map_view import ZONE_LAYER_ID, build_map

    table = risk.build_risk_table(data.generate_incidents())
    payload = json.loads(
        build_map(table, table.head(1), show_incidents=True, show_labels=True).to_json()
    )
    ids = {layer["@@type"]: layer.get("id") for layer in payload["layers"]}
    assert ids["GeoJsonLayer"] == ZONE_LAYER_ID
    assert all(value for value in ids.values()), f"every layer needs an id: {ids}"


def test_picked_zone_id_reads_a_real_selection_event():
    """The click handler must match PydeckSelectionState's real shape.

    ``objects`` maps layer id to a *list* of features, so a handler that assumes
    a bare dict silently returns None and click-to-pin never works.
    """
    from streamlit.elements.deck_gl_json_chart import PydeckState

    from app_shared import picked_zone_id
    from crime.map_view import ZONE_LAYER_ID

    event = PydeckState(
        {
            "selection": {
                "indices": {ZONE_LAYER_ID: [17]},
                "objects": {
                    ZONE_LAYER_ID: [
                        {
                            "type": "Feature",
                            "properties": {"zone_id": 17, "label": "Zone D2"},
                            "geometry": None,
                        }
                    ]
                },
            }
        }
    )
    assert picked_zone_id(event) == 17


def test_picked_zone_id_falls_back_to_index():
    from streamlit.elements.deck_gl_json_chart import PydeckState

    from app_shared import picked_zone_id
    from crime.map_view import ZONE_LAYER_ID

    event = PydeckState({"selection": {"indices": {ZONE_LAYER_ID: [4]}, "objects": {}}})
    assert picked_zone_id(event) == 4


def test_picked_zone_id_ignores_other_layers_and_empty_state():
    from streamlit.elements.deck_gl_json_chart import PydeckState

    from app_shared import picked_zone_id

    other = PydeckState(
        {"selection": {"indices": {"incident-points": [3]}, "objects": {}}}
    )
    assert picked_zone_id(other) is None
    assert picked_zone_id(None) is None
    assert picked_zone_id(PydeckState({"selection": {}})) is None
