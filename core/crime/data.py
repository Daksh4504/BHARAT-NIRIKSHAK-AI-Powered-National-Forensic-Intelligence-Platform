"""Synthetic six-month crime incident records for Ahmedabad.

The generator is intentionally structured so that the analysis downstream has
something real to find: a handful of persistent spatial hotspots, a mild upward
trend, weekday/weekend structure, a realistic diurnal profile per offence type,
and severity that correlates with both offence type and hour.

Everything is seeded, so the same seed always yields the same dataset.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .zones import (
    HEX_RADIUS_M,
    ZONES,
    _hexagon_contains_local,
    latlon_to_xy,
    xy_to_latlon,
)

# Six-month window ending 2025-06-30.
PERIOD_START = pd.Timestamp("2025-01-01")
PERIOD_END = pd.Timestamp("2025-06-30 23:59:59")

CRIME_TYPES = [
    "Snatching",
    "Cheating",
    "Burglary",
    "Vehicle theft",
    "Assault",
    "Robbery",
    "Cyber fraud",
    "Vandalism",
    "Murder",
    "Kidnapping",
]

# Offence-level base rates per 30 days, before zone and temporal multipliers.
CRIME_BASE_RATE = {
    "Snatching": 26.0,
    "Cheating": 18.0,
    "Burglary": 15.0,
    "Vehicle theft": 13.0,
    "Assault": 11.0,
    "Robbery": 7.0,
    "Cyber fraud": 6.0,
    "Vandalism": 5.0,
    "Murder": 1.2,
    "Kidnapping": 0.8,
}

# Fraction of each offence type occurring in the 20:00-05:59 night window.
NIGHT_SHARE = {
    "Snatching": 0.55,
    "Cheating": 0.10,
    "Burglary": 0.62,
    "Vehicle theft": 0.48,
    "Assault": 0.52,
    "Robbery": 0.66,
    "Cyber fraud": 0.22,
    "Vandalism": 0.70,
    "Murder": 0.60,
    "Kidnapping": 0.50,
}

# Base severity mix per offence type (low, medium, high).
SEVERITY_MIX = {
    "Snatching": (0.30, 0.50, 0.20),
    "Cheating": (0.35, 0.45, 0.20),
    "Burglary": (0.25, 0.50, 0.25),
    "Vehicle theft": (0.20, 0.55, 0.25),
    "Assault": (0.15, 0.45, 0.40),
    "Robbery": (0.10, 0.35, 0.55),
    "Cyber fraud": (0.40, 0.45, 0.15),
    "Vandalism": (0.55, 0.38, 0.07),
    "Murder": (0.0, 0.05, 0.95),
    "Kidnapping": (0.0, 0.15, 0.85),
}

# Time-of-day profile per offence type, expressed as 24 relative weights. Peaks
# sit where you would expect: street crime late evening, fraud during office
# hours, vandalism overnight.
HOUR_PROFILE = {
    "Snatching": [2, 2, 2, 2, 2, 3, 5, 8, 9, 8, 7, 8, 9, 9, 9, 10, 12, 15, 18, 20, 19, 16, 11, 6],
    "Cheating": [3, 2, 2, 2, 2, 2, 3, 5, 8, 12, 15, 16, 15, 15, 16, 16, 15, 13, 10, 7, 5, 4, 4, 3],
    "Burglary": [6, 5, 4, 4, 4, 5, 7, 8, 7, 6, 6, 7, 8, 8, 9, 10, 12, 15, 17, 17, 15, 12, 9, 7],
    "Vehicle theft": [5, 4, 4, 3, 3, 4, 6, 9, 11, 11, 10, 10, 10, 10, 11, 12, 14, 15, 15, 14, 12, 9, 7, 6],
    "Assault": [4, 3, 3, 3, 3, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11, 12, 14, 16, 18, 20, 19, 15, 9, 6],
    "Robbery": [5, 4, 4, 3, 3, 4, 6, 8, 9, 9, 9, 10, 11, 11, 12, 13, 14, 15, 16, 17, 15, 11, 8, 6],
    "Cyber fraud": [5, 4, 3, 3, 3, 3, 4, 6, 9, 13, 16, 17, 16, 16, 16, 16, 15, 13, 11, 9, 8, 7, 6, 5],
    "Vandalism": [7, 6, 5, 5, 5, 6, 8, 9, 8, 7, 7, 7, 8, 8, 9, 10, 12, 14, 15, 15, 13, 11, 9, 8],
    "Murder": [4, 3, 3, 3, 3, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 10, 12, 14, 15, 15, 13, 9, 6, 5],
    "Kidnapping": [4, 3, 3, 3, 3, 4, 5, 6, 7, 8, 9, 9, 10, 10, 10, 11, 12, 13, 14, 13, 11, 8, 6, 5],
}

SEVERITY_ORDER = ["Low", "Medium", "High"]
SEVERITY_SCORE = {"Low": 1.0, "Medium": 2.0, "High": 3.0}

# City-wide incidents per day before the month and weekday multipliers apply.
TARGET_DAILY_INCIDENTS = 65.0


def _zone_intensity(seed: int) -> tuple[np.ndarray, list[int]]:
    """Per-zone relative incident intensity.

    A few zones are made deliberately hot so the pipeline has a real
    concentration signal: a commercial core, two transit/market nodes, and a
    nightlife pocket, with the rest of the city at a low, near-uniform baseline.
    """
    rng = np.random.default_rng(seed)
    n = len(ZONES)
    # Tight baseline: the city outside the hotspots is fairly uniform, which is
    # what makes the hotspot structure legible rather than swamped by noise.
    intensity = rng.uniform(0.85, 1.10, n)

    # Deliberate hotspots, addressed by grid position (row, col). Adjacent cells
    # share a boost so the pattern clusters, which is what a spatial
    # autocorrelation test should detect.
    hotspots = {
        (3, 4): 6.0,  # central commercial core
        (3, 3): 2.2,  # its neighbour
        (3, 5): 2.4,  # its neighbour
        (4, 4): 2.0,  # its neighbour
        (2, 6): 4.0,  # rail / bus transit node
        (2, 5): 1.5,
        (2, 7): 1.6,
        (4, 2): 3.2,  # old market
        (4, 3): 1.3,
        (4, 1): 1.4,
        (3, 7): 2.8,  # nightlife pocket
        (2, 8): 1.3,
        (4, 7): 1.2,
        (5, 5): 1.9,  # mixed-use fringe
    }
    for zone in ZONES:
        boost = hotspots.get((zone.row, zone.col))
        if boost is not None:
            intensity[zone.zone_id - 1] *= boost
    # Scale so a typical day yields roughly 60-70 incidents city-wide, which
    # matches the order of magnitude of a metropolitan crime count per day.
    intensity *= TARGET_DAILY_INCIDENTS / intensity.sum()
    return intensity, list(range(1, n + 1))


def _monthly_trend() -> np.ndarray:
    """Relative multiplier per month across the six-month window.

    Encodes a modest upward trend plus a post-festival (Diwali-adjacent
    November is out of window, so a generic seasonal bump) summer peak.
    """
    return np.array([0.92, 0.95, 1.00, 1.06, 1.12, 1.08])


def _weekday_factors() -> np.ndarray:
    """Relative incident volume by day of week (Monday=0)."""
    return np.array([0.94, 0.92, 0.95, 1.00, 1.08, 1.22, 1.15])


def _pick_severity(
    rng: np.random.Generator, types: np.ndarray, night: np.ndarray
) -> np.ndarray:
    """Draw severities, biasing serious offences toward night hours.

    Night incidents are markedly more likely to be high severity, so a slice of
    the low and medium mass is shifted into the high bucket.
    """
    n = len(types)
    probs = np.empty((n, 3), dtype=float)
    for crime_type, (low, medium, high) in SEVERITY_MIX.items():
        mask = types == crime_type
        if not mask.any():
            continue
        shift = np.where(night[mask], 0.35, 0.0)
        low_adj = np.clip(low - shift, 0.0, 1.0)
        medium_adj = np.clip(medium - shift * 0.6, 0.0, 1.0)
        high_adj = np.clip(high + shift, 0.0, 1.0)
        probs[mask] = np.column_stack([low_adj, medium_adj, high_adj])

    probs /= probs.sum(axis=1, keepdims=True)
    draws = rng.random(n)
    return (draws[:, None] > probs.cumsum(axis=1)).sum(axis=1).astype(int)


def _sample_points(
    rng: np.random.Generator, zone_idx: int, n: int
) -> tuple[np.ndarray, np.ndarray]:
    """Sample incident coordinates inside a zone hexagon.

    Points are drawn by rejection sampling inside the hexagon, with a share of
    them pulled toward the centre. This keeps every point genuinely inside the
    zone (so zone attribution and geometry always agree) while still producing
    sub-zone clustering rather than a flat spread.
    """
    zone = ZONES[zone_idx]
    cx, cy = latlon_to_xy(zone.centre_lat, zone.centre_lon)

    xs = np.empty(n)
    ys = np.empty(n)
    filled = 0
    while filled < n:
        batch = max(64, int((n - filled) * 2.0))
        # 35% of points are drawn from a centre-weighted inner hexagon so the
        # cell shows sub-zone clustering; the rest are uniform over the cell.
        scale = rng.choice([0.45, 1.0], size=batch, p=[0.35, 0.65])
        px = rng.uniform(-1.0, 1.0, batch) * HEX_RADIUS_M * scale
        py = rng.uniform(-1.0, 1.0, batch) * HEX_RADIUS_M * scale
        keep = _hexagon_contains_local(px, py)

        take = min(int(keep.sum()), n - filled)
        if take == 0:
            continue
        xs[filled : filled + take] = cx + px[keep][:take]
        ys[filled : filled + take] = cy + py[keep][:take]
        filled += take

    out_lat = np.empty(n)
    out_lon = np.empty(n)
    for i in range(n):
        lat, lon = xy_to_latlon(xs[i], ys[i])
        out_lat[i] = lat
        out_lon[i] = lon
    return out_lat, out_lon


def generate_incidents(seed: int = 20250101) -> pd.DataFrame:
    """Generate a six-month synthetic incident table.

    Returns a DataFrame with one row per incident, carrying timestamp, zone,
    coordinates, offence type, severity, and derived time parts.
    """
    rng = np.random.default_rng(seed)
    intensity, zone_ids = _zone_intensity(seed)
    month_factors = _monthly_trend()
    weekday_factors = _weekday_factors()

    start = PERIOD_START
    end = PERIOD_END
    days = pd.date_range(start=start, end=end, freq="D")
    n_days = len(days)

    crime_types = list(CRIME_TYPES)
    base_rates = np.array([CRIME_BASE_RATE[c] for c in crime_types])
    # Offence mix shares, derived from base rates so the mix and the totals agree.
    mix = base_rates / base_rates.sum()

    frames: list[pd.DataFrame] = []
    incident_no = 1

    for day_idx, day in enumerate(days):
        month_idx = (day.month - PERIOD_START.month) % 12
        day_factor = (
            month_factors[month_idx % len(month_factors)]
            * weekday_factors[day.dayofweek]
        )
        # Per-zone counts for the day: Poisson draws scaled by zone intensity.
        lam = intensity * day_factor
        counts = rng.poisson(lam)
        total = int(counts.sum())
        if total == 0:
            continue

        zone_idx = rng.choice(len(zone_ids), size=total, p=counts / counts.sum())

        types = rng.choice(crime_types, size=total, p=mix)

        # Hour of day from the offence-specific profile.
        hours = np.empty(total, dtype=int)
        for ct in crime_types:
            mask = types == ct
            n_ct = int(mask.sum())
            if n_ct == 0:
                continue
            p = np.array(HOUR_PROFILE[ct], dtype=float)
            hours[mask] = rng.choice(24, size=n_ct, p=p / p.sum())

        minutes = rng.integers(0, 60, size=total)
        timestamps = (
            day.normalize()
            + pd.to_timedelta(hours * 3600 + minutes * 60, unit="s")
        )

        night = (hours >= 20) | (hours < 6)
        severities = np.array(SEVERITY_ORDER, dtype=object)[
            _pick_severity(rng, types, night)
        ]

        lats = np.empty(total)
        lons = np.empty(total)
        for zi in np.unique(zone_idx):
            mask = zone_idx == zi
            zlats, zlons = _sample_points(rng, int(zi), int(mask.sum()))
            lats[mask] = zlats
            lons[mask] = zlons

        frames.append(
            pd.DataFrame(
                {
                    "incident_id": np.arange(incident_no, incident_no + total),
                    "timestamp": timestamps,
                    "zone_id": [zone_ids[i] for i in zone_idx],
                    "latitude": np.round(lats, 6),
                    "longitude": np.round(lons, 6),
                    "crime_type": types,
                    "severity": severities,
                    "is_night": night,
                }
            )
        )
        incident_no += total

    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if df.empty:
        raise RuntimeError("Incident generation produced no rows; check the rates.")

    df = df.sort_values("timestamp").reset_index(drop=True)
    df["date"] = df["timestamp"].dt.normalize()
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["timestamp"].dt.day_name()
    df["hour"] = df["timestamp"].dt.hour
    df["severity_score"] = df["severity"].map(SEVERITY_SCORE)
    return df


def summarise(df: pd.DataFrame) -> dict:
    """Basic integrity summary used by the app header and by tests."""
    return {
        "rows": int(len(df)),
        "start": df["timestamp"].min(),
        "end": df["timestamp"].max(),
        "zones_touched": int(df["zone_id"].nunique()),
        "crime_types": int(df["crime_type"].nunique()),
        "night_share": float(df["is_night"].mean()),
    }
