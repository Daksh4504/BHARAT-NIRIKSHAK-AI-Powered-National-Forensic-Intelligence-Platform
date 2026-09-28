"""Spatial and temporal analysis over the incident table.

The functions here are deliberately side-effect free and take a DataFrame, so
they can be called on the full dataset or on any filtered subset the user
selects in the app.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .zones import ZONES, ZONES_BY_ID, latlon_to_xy

# Weekly and monthly aggregation frames used for trend detection.
TREND_MIN_PERIODS = 4


def spatial_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-zone spatial statistics for the given incidents."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "zone_id",
                "label",
                "centre_lat",
                "centre_lon",
                "area_km2",
                "population",
                "incidents",
                "per_km2",
                "per_10k_residents",
                "mean_severity",
                "night_share",
            ]
        )

    grouped = df.groupby("zone_id")
    out = pd.DataFrame(
        {
            "incidents": grouped.size(),
            "mean_severity": grouped["severity_score"].mean(),
            "night_share": grouped["is_night"].mean(),
        }
    ).reset_index()

    zones = pd.DataFrame(
        [
            {
                "zone_id": z.zone_id,
                "label": z.label,
                "centre_lat": z.centre_lat,
                "centre_lon": z.centre_lon,
                "area_km2": z.area_km2,
                "population": z.population,
            }
            for z in ZONES
        ]
    )
    out = zones.merge(out, on="zone_id", how="left")
    out["incidents"] = out["incidents"].fillna(0).astype(int)
    out["mean_severity"] = out["mean_severity"].fillna(0.0)
    out["night_share"] = out["night_share"].fillna(0.0)
    out["per_km2"] = np.where(
        out["area_km2"] > 0, out["incidents"] / out["area_km2"], 0.0
    )
    out["per_10k_residents"] = np.where(
        out["population"] > 0, out["incidents"] / out["population"] * 10_000, 0.0
    )
    return out.sort_values("incidents", ascending=False).reset_index(drop=True)


def temporal_summary(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Monthly, weekday, and hourly incident breakdowns."""
    if df.empty:
        return {"monthly": pd.DataFrame(), "weekday": pd.DataFrame(), "hourly": pd.DataFrame()}

    monthly = (
        df.groupby("month", as_index=False)
        .agg(
            incidents=("incident_id", "size"),
            mean_severity=("severity_score", "mean"),
            night_share=("is_night", "mean"),
        )
        .sort_values("month")
    )

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    weekday = (
        df.groupby("day_of_week", as_index=False)
        .agg(incidents=("incident_id", "size"))
        .assign(
            order=lambda d: d["day_of_week"].map(
                {d_: i for i, d_ in enumerate(weekday_order)}
            )
        )
        .sort_values("order")
        .drop(columns="order")
    )

    hourly = (
        df.groupby("hour", as_index=False)
        .agg(incidents=("incident_id", "size"), mean_severity=("severity_score", "mean"))
        .sort_values("hour")
    )
    return {"monthly": monthly, "weekday": weekday, "hourly": hourly}


def crime_type_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Offence-type counts and shares."""
    if df.empty:
        return pd.DataFrame(columns=["crime_type", "incidents", "share"])
    out = (
        df.groupby("crime_type", as_index=False)
        .agg(
            incidents=("incident_id", "size"),
            mean_severity=("severity_score", "mean"),
            night_share=("is_night", "mean"),
        )
        .sort_values("incidents", ascending=False)
    )
    out["share"] = out["incidents"] / out["incidents"].sum()
    return out.reset_index(drop=True)


def crime_type_by_zone(df: pd.DataFrame) -> pd.DataFrame:
    """Zone x offence-type count matrix, long form, for the heatmap."""
    if df.empty:
        return pd.DataFrame(columns=["zone_id", "label", "crime_type", "incidents"])
    out = (
        df.groupby(["zone_id", "crime_type"], as_index=False)
        .agg(incidents=("incident_id", "size"))
    )
    out["label"] = out["zone_id"].map(lambda z: ZONES_BY_ID[z].label)
    return out


def concentration_metrics(df: pd.DataFrame) -> dict[str, float]:
    """How clustered the incidents are across zones.

    ``top_zone_share``  share of incidents in the single busiest zone
    ``top5_zone_share``  share in the five busiest zones
    ``hhi``              Herfindahl-Hirschman index on zone shares (0-1)
    ``gini``             Gini coefficient over per-zone counts (0 = even)
    """
    spatial = spatial_summary(df)
    counts = spatial["incidents"].to_numpy(dtype=float)
    total = counts.sum()
    if total <= 0:
        return {
            "top_zone_share": 0.0,
            "top5_zone_share": 0.0,
            "hhi": 0.0,
            "gini": 0.0,
            "zones_covered": 0,
        }

    shares = counts / total
    hhi = float((shares**2).sum())
    gini = _gini(counts)
    return {
        "top_zone_share": float(shares.max()),
        "top5_zone_share": float(np.sort(shares)[::-1][:5].sum()),
        "hhi": hhi,
        "gini": gini,
        "zones_covered": int((counts > 0).sum()),
    }


def _gini(values: np.ndarray) -> float:
    """Gini coefficient for non-negative values, normalised to 0-1.

    Uses the exact pairwise form ``G = sum_i (2i-n-1) x_(i) / (n * sum x)`` over
    ascending-sorted values. Note the discretised ceiling for ``n`` observations
    is ``(n-1)/n``, not 1.0, because at least one zone must hold zero.
    """
    v = np.sort(np.asarray(values, dtype=float))
    n = len(v)
    total = v.sum()
    if n < 2 or total <= 0:
        return 0.0
    ranks = 2.0 * np.arange(1, n + 1) - n - 1.0
    g = float(ranks @ v) / (n * total)
    return float(np.clip(g, 0.0, 1.0))


def _linear_slope(values: np.ndarray) -> float:
    """Least-squares slope of values against their index."""
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values), dtype=float)
    x_centred = x - x.mean()
    denom = (x_centred**2).sum()
    if denom == 0:
        return 0.0
    return float((x_centred * (values - values.mean())).sum() / denom)


def _mann_kendall_s(values: np.ndarray) -> tuple[float, float]:
    """Mann-Kendall trend statistic and two-sided p-value.

    Implemented directly (no SciPy dependency) using the normal approximation
    with tie correction. Returns ``(S, p)``.
    """
    n = len(values)
    if n < TREND_MIN_PERIODS:
        return 0.0, 1.0
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = values[j] - values[i]
            s += 1 if diff > 0 else (-1 if diff < 0 else 0)

    # Variance of S with tie correction.
    _, counts = np.unique(values, return_counts=True)
    tie_term = float(np.sum(counts * (counts - 1) * (2 * counts + 5)).sum())
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0
    if var_s <= 0:
        return float(s), 1.0
    z = (s - np.sign(s)) / np.sqrt(var_s)
    from math import erfc, sqrt

    p = erfc(abs(z) / sqrt(2))
    return float(s), float(np.clip(p, 0.0, 1.0))


def zone_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Per-zone monthly trend: slope, growth, and Mann-Kendall p-value."""
    base = spatial_summary(df)[
        ["zone_id", "label", "incidents", "area_km2", "population"]
    ].copy()
    if df.empty:
        base["monthly_slope"] = 0.0
        base["growth_pct"] = 0.0
        base["mk_p"] = 1.0
        base["trend_direction"] = "flat"
        return base

    monthly = df.groupby(["zone_id", "month"], as_index=False).size()
    rows = []
    for zone_id, grp in monthly.groupby("zone_id"):
        grp = grp.sort_values("month")
        counts = grp["size"].to_numpy(dtype=float)
        slope = _linear_slope(counts)
        s_stat, p_val = _mann_kendall_s(counts)
        half = len(counts) // 2
        first = counts[:half].mean() if half else 0.0
        last = counts[half:].mean() if half else 0.0
        growth = (last - first) / first * 100.0 if first > 0 else 0.0
        if p_val < 0.05:
            direction = "rising" if s_stat > 0 else "falling"
        else:
            direction = "flat"
        rows.append(
            {
                "zone_id": zone_id,
                "monthly_slope": slope,
                "growth_pct": growth,
                "mk_s": s_stat,
                "mk_p": p_val,
                "trend_direction": direction,
            }
        )

    trend_df = pd.DataFrame(rows)
    out = base.merge(trend_df, on="zone_id", how="left")
    for col in ("monthly_slope", "growth_pct", "mk_s", "mk_p"):
        out[col] = out[col].fillna(0.0)
    out["trend_direction"] = out["trend_direction"].fillna("flat")
    return out


def spatial_autocorrelation(df: pd.DataFrame) -> float:
    """Moran's I on zone incident counts, using contiguity as row/column adjacency.

    Positive values mean high-count zones cluster together; near zero means
    counts are spatially random; negative means high and low counts alternate.
    """
    if df.empty:
        return 0.0

    spatial = spatial_summary(df)
    lookup = dict(zip(spatial["zone_id"], spatial["incidents"], strict=True))

    pos = {z.zone_id: i for i, z in enumerate(ZONES)}
    values = np.array([lookup.get(z.zone_id, 0) for z in ZONES], dtype=float)
    n = len(ZONES)

    dev = values - values.mean()
    denom = float((dev**2).sum())
    if denom == 0:
        return 0.0

    w_sum = 0.0
    num = 0.0
    for a in ZONES:
        for b in ZONES:
            if a.zone_id == b.zone_id:
                continue
            # Contiguity in the hex tiling: same-row horizontal neighbours, plus
            # the two diagonals in each adjacent row.
            dr = b.row - a.row
            dc = b.col - a.col
            if not ((dr == 0 and abs(dc) == 1) or (abs(dr) == 1 and abs(dc) <= 1)):
                continue
            w_sum += 1.0
            num += dev[pos[a.zone_id]] * dev[pos[b.zone_id]]

    if w_sum == 0:
        return 0.0
    return float((n / w_sum) * (num / denom))


def incident_points(df: pd.DataFrame) -> pd.DataFrame:
    """Per-incident coordinates projected to local metres, for map layers."""
    if df.empty:
        return pd.DataFrame(columns=["x", "y", "severity_score", "is_night"])
    xs, ys = [], []
    for lat, lon in zip(df["latitude"], df["longitude"], strict=True):
        x, y = latlon_to_xy(lat, lon)
        xs.append(x)
        ys.append(y)
    return pd.DataFrame(
        {
            "x": xs,
            "y": ys,
            "severity_score": df["severity_score"].to_numpy(),
            "is_night": df["is_night"].to_numpy(),
            "crime_type": df["crime_type"].to_numpy(),
        },
        index=df.index,
    )
