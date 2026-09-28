"""Zone risk scoring.

The risk index is a transparent weighted sum of four normalised components:

1. **Volume**  - incidents per km^2, the raw pressure a zone puts on policing.
2. **Severity** - mean severity score, so a zone with few but grave incidents
   is not dismissed.
3. **Night share** - proportion of incidents between 20:00 and 05:59, the
   component most tied to resident-perceived risk.
4. **Trend** - month-over-month growth, normalised from -20% to +20% and
   shifted to 0-1, so a zone that is deteriorating outranks an equally busy
   but stable one.

Every component is min-max normalised across the zones present in the data,
weighted, and rescaled to 0-100. Weights are exposed as arguments so the app
can let a user re-weight them, and every zone's component values are carried
through to the output so the final number can always be explained.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .analysis import spatial_summary, zone_trends

DEFAULT_WEIGHTS: dict[str, float] = {
    "volume": 0.35,
    "severity": 0.25,
    "night_share": 0.20,
    "trend": 0.20,
}

COMPONENT_LABELS: dict[str, str] = {
    "volume": "Volume per km²",
    "severity": "Mean severity",
    "night_share": "Night-time share",
    "trend": "Recent trend",
}

# Trend growth is clipped to this band before normalisation so a single wild
# month cannot dominate the index.
TREND_BAND = (-20.0, 20.0)

# Incidents per month at which the trend estimate is trusted fully. Below this,
# observed growth is shrunk toward zero because a handful of extra incidents in
# a quiet zone otherwise reads as a dramatic surge.
TREND_CONFIDENCE_INCIDENTS = 60.0

# Risk tiers used for labelling in the UI and the map. Bands are absolute on the
# 0-100 composite, calibrated so the highest-risk zone of a well-separated
# dataset lands in "Critical" and the quiet bulk lands in "Low".
TIERS = [
    (70.0, "Critical", "red"),
    (55.0, "High", "orange"),
    (40.0, "Moderate", "yellow"),
    (0.0, "Low", "green"),
]


@dataclass(frozen=True)
class RiskWeights:
    """Validated weight set for the risk index."""

    volume: float = 0.35
    severity: float = 0.25
    night_share: float = 0.20
    trend: float = 0.20

    def normalised(self) -> dict[str, float]:
        """Return weights rescaled so they sum to exactly 1."""
        raw = {
            "volume": max(self.volume, 0.0),
            "severity": max(self.severity, 0.0),
            "night_share": max(self.night_share, 0.0),
            "trend": max(self.trend, 0.0),
        }
        total = sum(raw.values())
        if total <= 0:
            return dict(DEFAULT_WEIGHTS)
        return {k: v / total for k, v in raw.items()}


def _min_max(series: pd.Series) -> pd.Series:
    """Min-max normalise to 0-1; a constant series becomes all zeros."""
    lo = float(series.min())
    hi = float(series.max())
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo <= 1e-12:
        return pd.Series(np.zeros(len(series)), index=series.index, dtype=float)
    return (series - lo) / (hi - lo)


def _tier(score: float) -> tuple[str, str]:
    """Map a 0-100 risk score to its tier label and Streamlit colour name."""
    for threshold, label, color in TIERS:
        if score >= threshold:
            return label, color
    return "Low", "green"


def build_risk_table(
    df: pd.DataFrame, weights: RiskWeights | None = None
) -> pd.DataFrame:
    """Score every zone and rank them by composite risk.

    Returns one row per zone including the normalised component values, the
    weighted contribution of each, and the final 0-100 score.
    """
    weights = weights or RiskWeights()
    w = weights.normalised()

    spatial = spatial_summary(df)
    trends = zone_trends(df)[["zone_id", "growth_pct", "mk_p", "trend_direction"]]
    out = spatial.merge(trends, on="zone_id", how="left")

    out["c_volume"] = _min_max(out["per_km2"])
    out["c_severity"] = _min_max(out["mean_severity"])
    out["c_night_share"] = _min_max(out["night_share"])

    # Shrink the observed growth toward zero for zones with too few incidents to
    # estimate a trend from, then clip to the band and normalise. Without this,
    # a quiet zone with 20 incidents that happened to gain 3 reads as surging.
    confidence = (out["incidents"] / TREND_CONFIDENCE_INCIDENTS).clip(0.0, 1.0)
    lo, hi = TREND_BAND
    growth = (out["growth_pct"] * confidence).clip(lower=lo, upper=hi)
    out["c_trend"] = (growth - lo) / (hi - lo)

    out["risk_score"] = 100.0 * (
        out["c_volume"] * w["volume"]
        + out["c_severity"] * w["severity"]
        +         out["c_night_share"] * w["night_share"]
        + out["c_trend"] * w["trend"]
    )
    out["rank"] = (
        out["risk_score"].rank(method="min", ascending=False).astype(int)
    )
    out["risk_tier"] = [t[0] for t in out["risk_score"].map(_tier)]
    out["tier_color"] = [t[1] for t in out["risk_score"].map(_tier)]
    out["weights_used"] = str(w)

    for comp in ("volume", "severity", "night_share", "trend"):
        out[f"w_{comp}"] = out[f"c_{comp}"] * w[comp] * 100.0

    cols = [
        "rank",
        "zone_id",
        "label",
        "centre_lat",
        "centre_lon",
        "incidents",
        "per_km2",
        "mean_severity",
        "night_share",
        "growth_pct",
        "trend_direction",
        "risk_score",
        "risk_tier",
        "tier_color",
        # Normalised components and their weighted contributions, kept so any
        # score can be recomputed and audited from the table alone.
        "c_volume",
        "c_severity",
        "c_night_share",
        "c_trend",
        "w_volume",
        "w_severity",
        "w_night_share",
        "w_trend",
    ]
    return out[cols].sort_values("rank").reset_index(drop=True)


def top_zones(risk_table: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """The ``n`` highest-risk zones, best first."""
    return risk_table.head(n).reset_index(drop=True)


def component_breakdown(
    risk_table: pd.DataFrame, weights: RiskWeights | None = None
) -> pd.DataFrame:
    """Long-form table of weighted component contributions, for the chart."""
    weights = weights or RiskWeights()
    w = weights.normalised()
    frames = []
    for comp in ("volume", "severity", "night_share", "trend"):
        col = "c_night_share" if comp == "night_share" else f"c_{comp}"
        frames.append(
            pd.DataFrame(
                {
                    "zone_id": risk_table["zone_id"],
                    "label": risk_table["label"],
                    "component": COMPONENT_LABELS[comp],
                    "weight": w[comp],
                    "score": risk_table[col] * 100.0,
                    "contribution": risk_table[f"w_{comp}"],
                }
            )
        )
    return pd.concat(frames, ignore_index=True)
