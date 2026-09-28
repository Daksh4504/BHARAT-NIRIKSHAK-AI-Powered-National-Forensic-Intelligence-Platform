# Ahmedabad Crime Risk Dashboard

An interactive Streamlit dashboard that takes **six months of synthetic crime
data** for Ahmedabad through a full analytical pipeline: spatial and temporal
pattern detection, crime concentration measurement, a transparent weighted risk
index, a top-5 zone ranking, and a clickable map.

Everything runs locally. No data is downloaded, and no external services are
required at runtime.

> **The data is synthetic.** Incidents are generated from a seeded statistical
> model, not from police records. The zones are a synthetic hex tessellation,
> not real Ahmedabad neighbourhoods. Treat the dashboard as a demonstration of
> analytical method, not as a factual crime picture of the city.

## Quick start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app opens at `http://localhost:8501`. Data generation takes a couple of
seconds on first load and is then cached for the session.

## Running the tests

```bash
python -m pytest tests/ -q
```

The suite has two layers:

| File | What it covers |
| --- | --- |
| `tests/test_pipeline.py` | Zone geometry, data generation, analysis maths, risk scoring, map serialisation |
| `tests/test_app.py` | The real Streamlit app end-to-end via `AppTest`, plus map selection handling |

## How it works

### 1. Data generation (`crime/data.py`)

`generate_incidents()` builds a reproducible panel for **2025-01-01 through
2025-06-30**, producing roughly **12,400 incidents** from a default seed of
`20250101`. Each offence type carries its own profile, so the aggregate pattern
is not uniform noise:

- **10 offence types** with distinct base rates, from *Snatching* and *Burglary*
  down to rarer *Murder* and *Kidnapping*.
- **Spatial clustering.** A handful of zones are made deliberately hot with
  explicit multipliers — a central commercial core, a rail/bus transit node, an
  old market, and a nightlife pocket — with their neighbours given smaller
  boosts so the structure genuinely clusters. Everything else sits on a tight
  near-uniform baseline, which is what keeps the hotspot pattern legible instead
  of being swamped by noise.
- **Daily, weekly, and seasonal rhythm.** Weekends run hotter than weekdays,
  months drift upward, and a seasonal bump peaks in November (outside the
  window) so the six months show a realistic curve.
- **Time-of-day profiles.** Street offences like *Vandalism* (70% night) and
  *Burglary* (62% night) peak after dark, while *Cheating* (10% night) and
  *Cyber fraud* (22% night) are daytime phenomena. `is_night` is
  20:00–05:59.
- **Severity mixes** per offence, scored Low = 1, Medium = 2, High = 3.

Incidents are placed inside their zone polygon in a local equirectangular
projection, so every point is guaranteed to fall within the zone it is
attributed to.

### 2. Spatial analysis (`crime/analysis.py`)

- Incidents per zone, with **density per km²** so zones of different sizes
  compare fairly.
- **Crime concentration:** share of all incidents in the top zone and top 5
  zones, **Herfindahl-Hirschman index**, and **Gini coefficient**.
- **Moran's I** over hex contiguity, to say whether high-count zones cluster
  together or sit at random. The app reports the value and its sign; the test
  suite builds a 20-draw permutation null to confirm the observed value is far
  above chance, which keeps the significance check out of the interactive path.

### 3. Temporal analysis (`crime/analysis.py`)

- Monthly volume with mean severity and night share.
- Weekday shape and a 24-hour profile.
- **Mann-Kendall** trend test with a least-squares slope per zone, which report a
  direction and a p-value rather than just a slope.

### 4. The risk index (`crime/risk.py`)

The score is a **weighted sum of four components**, each min-max normalised
across the zones in the *current* selection and rescaled to 0–100:

| Component | Weight | Definition |
| --- | --- | --- |
| Volume per km² | 0.35 | Incidents divided by zone area |
| Mean severity | 0.25 | Mean severity score (1–3) |
| Night-time share | 0.20 | Fraction of incidents 20:00–05:59 |
| Recent trend | 0.20 | Half-over-half growth, clipped to ±20% |

Trend is **shrunk by a confidence factor** based on incident count, so a zone
showing +200% growth on four incidents cannot outrank a consistently high zone.
The four sidebar sliders reweight the index live; weights are renormalised to sum
to 1 and every per-component contribution is retained so the ranking stays fully
auditable.

Tiers: **Critical** ≥ 70, **High** ≥ 55, **Moderate** ≥ 40, **Low** below 40.

### 5. The map (`crime/map_view.py`)

A deck.gl map built with `st.pydeck_chart` and PyDeck:

- A **GeoJsonLayer** of the 63 zone hexagons, filled from a fixed blue-to-red
  risk ramp. The top *N* zones get a thicker white outline.
- A **TextLayer** of zone labels and scores, and an optional **ScatterplotLayer**
  of individual incident points.
- Hover tooltips show the full zone breakdown; clicking a zone pins it and
  filters the detail panel and score-contribution chart beneath the map.

All three layers share one coordinate system (`[longitude, latitude]`), which is
what deck.gl expects for `get_position`.

## Pages

| Page | Contents |
| --- | --- |
| **Overview** | KPIs, top 5 risk zones, monthly volume, offence mix, full ranking table |
| **Spatial analysis** | Per-zone counts, concentration metrics, Moran's I, offence-by-zone heatmap |
| **Temporal analysis** | Monthly, weekday, hourly, and per-zone trend views |
| **Risk map** | Interactive map, click-to-pin zone detail, score contribution breakdown |
| **Methodology** | The full pipeline, formulas, data-generation details, and limitations |

The sidebar carries the shared controls: date range, offence type, severity,
day/night band, the four risk-weight sliders, top-*N* selector, and map layer
toggles. Every page recomputes from the same filtered frame, so the whole app
stays consistent with whatever is selected.

## Project layout

```
streamlit_app.py        Entry point and page navigation
app_shared.py           Sidebar, page scaffolding, map selection handling
app_pages/              One module per page
crime/
  zones.py              Study bounds, hex tessellation, projection, GeoJSON
  data.py               Seeded incident generator and offence profiles
  analysis.py           Spatial, temporal, and concentration analysis
  risk.py               Risk weighting, ranking, component breakdown
  map_view.py           deck.gl layers and risk colour ramp
  state.py              Cached loading, filtering, and session state
.streamlit/config.toml  Dark analytical theme
```

## Limitations

- The data is generated, so findings demonstrate method rather than reality.
- Zones are equal-area hexagons chosen for clean adjacency, not administrative
  or neighbourhood boundaries. Labels are positional (`Zone A1`, `Zone B4`).
- The 10 offence types and their profiles are plausible but invented.
- Moran's I uses a contiguity-based hex neighbourhood. The dashboard shows the
  value and its sign, not a significance test, so read it as a description of
  spatial structure rather than a hypothesis verdict.
- The risk index is a **weighted composite**, not a prediction. It has no
  exposure, population, repeat-victimisation, or reporting-propensity data, and
  a high score means "high on these four measures", not "dangerous".
- Min-max normalisation means scores are relative to the current selection.
  Filtering to a narrow window will rescale the whole index.
