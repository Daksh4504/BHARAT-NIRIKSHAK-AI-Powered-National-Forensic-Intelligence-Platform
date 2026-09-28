"""Ahmedabad zone geometry and local metric helpers.

Zones are defined as a hex-grid tessellation over the Ahmedabad metropolitan
area so that every generated incident falls inside exactly one zone and zones
tile the study area without gaps or overlaps. Hexagons are used instead of
square cells because they share borders evenly (no corner-overlap bias), which
keeps per-zone counts comparable.

Coordinates are (latitude, longitude) in WGS84. Internal analysis happens in a
local equirectangular projection (metres east/north of a study-area origin)
because Ahmedabad is small enough (<1 deg across) that projection error is far
below the noise floor of mock data.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

# Geographic bounds of the study area (Ahmedabad municipal + inner suburbs).
LAT_MIN, LAT_MAX = 22.95, 23.20
LON_MIN, LON_MAX = 72.42, 72.72

# Local projection origin and scale constants.
ORIGIN_LAT = (LAT_MIN + LAT_MAX) / 2
ORIGIN_LON = (LON_MIN + LON_MAX) / 2
METRES_PER_DEG_LAT = 111_320.0
METRES_PER_DEG_LON = 111_320.0 * math.cos(math.radians(ORIGIN_LAT))

# Hex tessellation parameters. Spacing follows standard flat-topped hex tiling:
# horizontal centre spacing is 1.5R, vertical is sqrt(3)*R, and odd rows are
# offset by half the horizontal spacing. The row and column counts are then
# chosen so the tiling fills the study area with no gaps.
HEX_ROWS = 7
HEX_COLS = 9
HEX_RADIUS_M = 2_200.0  # circumradius of each hexagon, metres
HEX_COL_SPACING_M = 1.5 * HEX_RADIUS_M
HEX_ROW_SPACING_M = math.sqrt(3) * HEX_RADIUS_M


def latlon_to_xy(lat: float, lon: float) -> tuple[float, float]:
    """Project latitude/longitude to local metres east/north of the origin."""
    x = (lon - ORIGIN_LON) * METRES_PER_DEG_LON
    y = (lat - ORIGIN_LAT) * METRES_PER_DEG_LAT
    return x, y


def xy_to_latlon(x: float, y: float) -> tuple[float, float]:
    """Inverse of :func:`latlon_to_xy`."""
    lat = ORIGIN_LAT + y / METRES_PER_DEG_LAT
    lon = ORIGIN_LON + x / METRES_PER_DEG_LON
    return lat, lon


@dataclass(frozen=True)
class Zone:
    """A single analysis zone."""

    zone_id: int
    label: str
    row: int
    col: int
    centre_lat: float
    centre_lon: float
    polygon: list[list[float]] = field(repr=False)
    area_km2: float = 0.0
    population: int = 0

    def contains(self, lat: float, lon: float) -> bool:
        """Ray-casting point-in-polygon test against the zone boundary."""
        return _point_in_ring(lat, lon, self.polygon)


def _point_in_ring(lat: float, lon: float, ring: list[list[float]]) -> bool:
    """Test whether (lat, lon) falls inside a closed ``[[lat, lon], ...]`` ring."""
    inside = False
    n = len(ring)
    for i in range(n):
        lat_i, lon_i = ring[i]
        lat_j, lon_j = ring[i - 1]
        if (lon_i > lon) != (lon_j > lon):
            # Longitude range straddles the point; interpolate the edge latitude.
            denom = lon_j - lon_i
            if denom != 0:
                lat_at_lon = lat_i + (lon - lon_i) * (lat_j - lat_i) / denom
                if lat < lat_at_lon:
                    inside = not inside
    return inside


def _hexagon_ring(cx: float, cy: float, radius: float) -> list[list[float]]:
    """Build a flat-topped hexagon in local metres, returned as lat/lon pairs."""
    angles = [math.radians(a) for a in range(0, 360, 60)]
    ring: list[list[float]] = []
    for a in angles:
        x = cx + radius * math.cos(a)
        y = cy + radius * math.sin(a)
        lat, lon = xy_to_latlon(x, y)
        ring.append([round(lat, 6), round(lon, 6)])
    ring.append(ring[0])  # close the ring for GeoJSON validity
    return ring


def _regular_hex_area_km2(radius_m: float) -> float:
    """Area of a regular hexagon with the given circumradius."""
    return (3 * math.sqrt(3) / 2) * radius_m**2 / 1_000_000


# Approximate resident population per hexagon, scaled to plausible ward-level
# density variation (market/commercial cores denser than peripheral fringes).
_DENSITY_BY_POSITION = {
    "core": 38_000,
    "inner": 26_000,
    "outer": 16_000,
}


def _population_band(row: int, col: int) -> str:
    """Classify a hex cell into a population-density band."""
    centre_offset = abs(col - (HEX_COLS - 1) / 2) + abs(row - (HEX_ROWS - 1) / 2)
    if centre_offset <= 2.0:
        return "core"
    if centre_offset <= 4.5:
        return "inner"
    return "outer"


def _zone_label(row: int, col: int) -> str:
    """Human-readable zone label derived from its grid position."""
    return f"Zone {chr(ord('A') + row)}{col + 1}"


def build_zones() -> list[Zone]:
    """Construct the full tessellation of analysis zones for the study area."""
    row_lat = HEX_ROW_SPACING_M / METRES_PER_DEG_LAT
    col_lon = HEX_COL_SPACING_M / METRES_PER_DEG_LON
    # Half a row/column of padding keeps the outer hexes fully inside the bounds.
    lat = LAT_MIN + row_lat * 0.5
    lon = LON_MIN + col_lon * 0.5

    zones: list[Zone] = []
    zone_id = 1
    for row in range(HEX_ROWS):
        for col in range(HEX_COLS):
            # Flat-topped hex layout: odd rows are offset by half a column.
            zone_lat = lat + row * row_lat
            zone_lon = lon + col * col_lon + (col_lon * 0.5 if row % 2 else 0.0)
            cx, cy = latlon_to_xy(zone_lat, zone_lon)
            polygon = _hexagon_ring(cx, cy, HEX_RADIUS_M)
            band = _population_band(row, col)
            zones.append(
                Zone(
                    zone_id=zone_id,
                    label=_zone_label(row, col),
                    row=row,
                    col=col,
                    centre_lat=round(zone_lat, 6),
                    centre_lon=round(zone_lon, 6),
                    polygon=polygon,
                    area_km2=round(_regular_hex_area_km2(HEX_RADIUS_M), 4),
                    population=_DENSITY_BY_POSITION[band] + (col * 137) % 900,
                )
            )
            zone_id += 1
    return zones


ZONES: list[Zone] = build_zones()
ZONES_BY_ID: dict[int, Zone] = {z.zone_id: z for z in ZONES}


def zone_lookup_table() -> tuple[list[float], list[float], list[int], list[int]]:
    """Return per-incident assignment arrays for fast nearest-zone binding.

    The hex tiling is a Voronoi diagram of the zone centres, so binding an
    incident to the nearest centre is exact and far cheaper than a polygon test
    per row.
    """
    lats = [z.centre_lat for z in ZONES]
    lons = [z.centre_lon for z in ZONES]
    xs = [latlon_to_xy(z.centre_lat, z.centre_lon)[0] for z in ZONES]
    ys = [latlon_to_xy(z.centre_lat, z.centre_lon)[1] for z in ZONES]
    return lats, lons, xs, ys


def _hexagon_contains_local(px: "np.ndarray", py: "np.ndarray") -> "np.ndarray":
    """Vectorised point-in-regular-hexagon test for a hexagon at the local origin.

    The hexagon has circumradius :data:`HEX_RADIUS_M` with vertices at multiples
    of 60 degrees, so its outward edge normals sit at 30, 90, and 150 degrees
    and the apothem is ``R * cos(30 deg)``. A point is inside when it is within
    the apothem along all three normals.
    """
    apothem = HEX_RADIUS_M * math.cos(math.radians(30))
    normals = np.radians(np.array([30.0, 90.0, 150.0]))
    projections = (
        px[:, None] * np.cos(normals)[None, :]
        + py[:, None] * np.sin(normals)[None, :]
    )
    return (np.abs(projections) <= apothem).all(axis=1)


def zone_boundaries_geojson() -> list[dict]:
    """Return zone polygons as GeoJSON-style feature dicts for deck.gl."""
    return [
        {
            "type": "Feature",
            "properties": {
                "zone_id": z.zone_id,
                "label": z.label,
                "centre_lat": z.centre_lat,
                "centre_lon": z.centre_lon,
                "area_km2": z.area_km2,
                "population": z.population,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[lon, lat] for lat, lon in z.polygon]],
            },
        }
        for z in ZONES
    ]
