"""MnoEnvIceOperations: sea ice, ice shelves and icebergs as three distinct classes. BUILD-TESTED (offline).

- Sea ice: a concentration field in the snapshot (sea_ice_conc_pct). Access depends on a
  ship's ice capability, which comes ONLY from an explicit table the owner fills
  (data/ice-capability.json); a unit not listed is "none". No ice class is inferred.
- Ice shelves: floating glacier fronts attached to land. Static polygons, optionally dated;
  never advected. A route may not cross one. The bundled geometry is SCHEMATIC until an
  authoritative dataset (e.g. MEaSUREs Antarctic Boundaries, NSIDC-0709, or SCAR ADD) is
  imported; the loader refuses to call schematic data authoritative.
- Icebergs: individual objects with an observed position and time, a size band, and a drift
  of ocean current plus a wind fraction; position uncertainty grows with time since the last
  observation, and the berg disappears after its size band's lifetime.

All thresholds are DESIGN values for game rules, NOT the IMO Polar Code / POLARIS method and
not navigational advice. Collision or hull damage is not modelled anywhere.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from .geo import _ring_contains, displace, wrap_lon

DATA = Path(__file__).resolve().parents[1] / "data"

# capability -> (open below, caution below, restricted below); at or above the last: blocked
ACCESS_THRESHOLDS = {
    "none": (10.0, 30.0, 60.0),
    "ice_strengthened": (30.0, 60.0, 80.0),
    "polar_class": (60.0, 90.0, 101.0),
    "icebreaker": (90.0, 101.0, 101.0),
}
ACCESS_SPEED = {"open": 1.0, "caution": 0.7, "restricted": 0.4, "blocked": 0.0}
ACCESS_ORDER = ["open", "caution", "restricted", "blocked"]


def access(conc_pct: float | None, capability: str = "none") -> str:
    if capability not in ACCESS_THRESHOLDS:
        raise ValueError(f"unknown ice capability {capability!r}")
    if conc_pct is None:
        return "caution"  # unknown ice is not open water
    o, c, r = ACCESS_THRESHOLDS[capability]
    if conc_pct < o:
        return "open"
    if conc_pct < c:
        return "caution"
    if conc_pct < r:
        return "restricted"
    return "blocked"


def load_capabilities(path: Path | None = None) -> dict:
    path = path or DATA / "ice-capability.json"
    if not Path(path).exists():
        return {}
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    caps = {}
    for unit, entry in doc.get("units", {}).items():
        if entry.get("capability") not in ACCESS_THRESHOLDS:
            raise ValueError(f"{unit}: unknown capability {entry.get('capability')!r}")
        if not entry.get("source"):
            raise ValueError(f"{unit}: an ice capability needs a source (it is never inferred)")
        caps[unit] = entry["capability"]
    return caps


@dataclass(frozen=True)
class IceShelf:
    name: str
    rings: tuple
    valid_from: str | None
    authoritative: bool

    def contains(self, lat: float, lon: float) -> bool:
        lon = wrap_lon(lon)
        return any(_ring_contains(r, lat, lon) for r in self.rings)


def load_shelves(path: Path | None = None) -> list[IceShelf]:
    path = path or DATA / "ice-shelf-fronts-SCHEMATIC.json"
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    status = doc.get("status", "")
    authoritative = status == "AUTHORITATIVE" and bool(doc.get("source_url")) and bool(doc.get("licence"))
    return [IceShelf(s["name"], tuple(tuple(map(tuple, r)) for r in s["rings"]), s.get("valid_from"), authoritative)
            for s in doc["shelves"]]


# size band -> (footprint radius NM, wind drift fraction, lifetime days)
BERG_BANDS = {
    "growler": (0.05, 0.03, 20),
    "small": (0.3, 0.025, 120),
    "medium": (1.5, 0.02, 400),
    "large": (8.0, 0.015, 1500),
    "giant": (25.0, 0.01, 4000),
}
UNCERTAINTY_NM_PER_H = 0.4   # growth of 1-sigma position error after the last observation
MS_TO_KNOTS = 1.943844


@dataclass(frozen=True)
class Iceberg:
    berg_id: str
    band: str
    lat: float
    lon: float
    observed_seconds: int
    initial_sigma_nm: float = 1.0
    source: str = "fixture"

    def predict(self, state, campaign_seconds: int, step_s: int = 6 * 3600) -> dict | None:
        """Advect with current + wind fraction, stepping through the environment. Returns
        None once the berg has outlived its band."""
        if campaign_seconds < self.observed_seconds:
            raise ValueError("predict() goes forward from the last observation")
        radius, windage, life_days = BERG_BANDS[self.band]
        age = campaign_seconds - self.observed_seconds
        if age > life_days * 86400:
            return None
        pos, t = (self.lat, self.lon), self.observed_seconds
        while t < campaign_seconds:
            dt_s = min(step_s, campaign_seconds - t)
            v = state.sample(t, pos[0], pos[1]).values
            cu, cv = v.get("current_u_ms") or 0.0, v.get("current_v_ms") or 0.0
            wu, wv = v.get("wind_u10_ms") or 0.0, v.get("wind_v10_ms") or 0.0
            u, w = cu + windage * wu, cv + windage * wv
            pos = displace(pos, u * MS_TO_KNOTS * dt_s / 3600, w * MS_TO_KNOTS * dt_s / 3600)
            t += dt_s
        sigma = self.initial_sigma_nm + UNCERTAINTY_NM_PER_H * age / 3600
        return {"berg_id": self.berg_id, "band": self.band, "lat": round(pos[0], 4), "lon": round(pos[1], 4),
                "footprint_nm": radius, "sigma_nm": round(sigma, 2), "hazard_radius_nm": round(radius + 2 * sigma, 2),
                "age_hours": round(age / 3600, 1), "source": self.source}


def load_icebergs(path: Path) -> list[Iceberg]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for b in doc["icebergs"]:
        if b["band"] not in BERG_BANDS:
            raise ValueError(f"{b['berg_id']}: unknown size band")
        out.append(Iceberg(b["berg_id"], b["band"], b["lat"], b["lon"], int(b["observed_seconds"]),
                           float(b.get("initial_sigma_nm", 1.0)), doc.get("source", "fixture")))
    return out


def worst(a: str, b: str) -> str:
    return a if ACCESS_ORDER.index(a) >= ACCESS_ORDER.index(b) else b


def hs_speed_factor(hs: float | None) -> float:
    """Planning speed factor in a seaway (bounded 0.55..1). Not a seakeeping model."""
    if hs is None:
        return 1.0
    for upper, f in ((2.5, 1.0), (4.0, 0.95), (6.0, 0.85), (9.0, 0.7)):
        if hs < upper:
            return f
    return 0.55


def hav_nm(a, b) -> float:
    from .geo import great_circle_nm
    return great_circle_nm(a, b)


def nearest_berg(pt, bergs_now) -> tuple[float, dict] | None:
    best = None
    for b in bergs_now:
        d = hav_nm(pt, (b["lat"], b["lon"]))
        if best is None or d < best[0]:
            best = (d, b)
    return best


def _is_finite(x) -> bool:
    return x is not None and not (isinstance(x, float) and math.isnan(x))
