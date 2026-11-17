"""Geodesy helpers: longitude wrapping, great circles, land test. BUILD-TESTED.

All latitudes and longitudes are WGS84 degrees. Distances use a sphere of mean radius
3440.065 NM, which is adequate for campaign routing (error well under 0.5 %), not survey work.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

EARTH_RADIUS_NM = 3440.065
PROTOTYPE_COAST = Path(__file__).resolve().parents[1] / "prototype-20261118" / "data" / "coastlines.json"


def wrap_lon(lon: float) -> float:
    """Wrap to [-180, 180)."""
    return (lon + 180.0) % 360.0 - 180.0


def to_0_360(lon: float) -> float:
    return lon % 360.0


def lon_delta(a: float, b: float) -> float:
    """Signed shortest difference a - b in degrees, in [-180, 180)."""
    return wrap_lon(a - b)


def campaign_lon(lon: float, lo: float, hi: float) -> float:
    """Return the copy of lon (mod 360) inside [lo, hi] if one exists, else the nearest copy.

    GCO writes longitudes in a continuous frame (-100..258 today); this maps a [-180,180)
    value into that frame the way the builder does.
    """
    mid = (lo + hi) / 2.0
    v = mid + lon_delta(lon, mid)
    return v


def great_circle_nm(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_NM * math.asin(math.sqrt(min(1.0, max(0.0, h))))


def intermediate(a: tuple[float, float], b: tuple[float, float], f: float) -> tuple[float, float]:
    """Point at fraction f along the great circle from a to b."""
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    d = great_circle_nm(a, b) / EARTH_RADIUS_NM
    if d < 1e-12:
        return a
    s = math.sin(d)
    k1 = math.sin((1 - f) * d) / s
    k2 = math.sin(f * d) / s
    x = k1 * math.cos(lat1) * math.cos(lon1) + k2 * math.cos(lat2) * math.cos(lon2)
    y = k1 * math.cos(lat1) * math.sin(lon1) + k2 * math.cos(lat2) * math.sin(lon2)
    z = k1 * math.sin(lat1) + k2 * math.sin(lat2)
    return (math.degrees(math.atan2(z, math.hypot(x, y))), wrap_lon(math.degrees(math.atan2(y, x))))


def sample_leg(a, b, max_step_nm: float = 10.0) -> list[tuple[float, float]]:
    dist = great_circle_nm(a, b)
    n = max(1, math.ceil(dist / max_step_nm))
    return [intermediate(a, b, i / n) for i in range(n + 1)]


def destination(start: tuple[float, float], bearing_deg: float, dist_nm: float) -> tuple[float, float]:
    lat1, lon1 = map(math.radians, start)
    brg = math.radians(bearing_deg)
    d = dist_nm / EARTH_RADIUS_NM
    lat2 = math.asin(math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(brg))
    lon2 = lon1 + math.atan2(math.sin(brg) * math.sin(d) * math.cos(lat1), math.cos(d) - math.sin(lat1) * math.sin(lat2))
    return (math.degrees(lat2), wrap_lon(math.degrees(lon2)))


def displace(pos: tuple[float, float], east_nm: float, north_nm: float) -> tuple[float, float]:
    dist = math.hypot(east_nm, north_nm)
    if dist == 0:
        return pos
    return destination(pos, math.degrees(math.atan2(east_nm, north_nm)) % 360, dist)


def _ring_contains(ring, lat: float, lon: float) -> bool:
    inside = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        if abs(x2 - x1) > 180:  # an edge that wraps the seam is not part of a lon/lat ring
            continue
        if (y1 > lat) != (y2 > lat):
            xi = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if xi > lon:
                inside = not inside
    return inside


class LandMask:
    """Point-in-polygon land test over lon/lat rings (Natural Earth low resolution).

    Coarse: rings are simplified to about 0.25 degree, so straits narrower than about
    15 NM can read as land and small islands can be missing. Good enough to stop a route
    crossing a continent; not good enough for a harbour approach. BUILD-TESTED.
    """

    def __init__(self, polygons: list[list[list[float]]]):
        self.rings = []
        for ring in polygons:
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            self.rings.append((min(xs), max(xs), min(ys), max(ys), ring))

    @classmethod
    def from_file(cls, path: Path = PROTOTYPE_COAST) -> "LandMask":
        return cls(json.loads(Path(path).read_text(encoding="utf-8"))["polygons"])

    def is_land(self, lat: float, lon: float) -> bool:
        lon = wrap_lon(lon)
        if lat <= -85.0:
            return True  # interior Antarctica; low-res rings stop short of the pole
        for x0, x1, y0, y1, ring in self.rings:
            if y0 <= lat <= y1 and x0 <= lon <= x1 and _ring_contains(ring, lat, lon):
                return True
        return False


class GlobeLandMask:
    """1 km GLOBE land mask through the optional `global-land-mask` package, the same optional
    dependency the world-sandbox and showcase builders use. Better for straits and harbours;
    like Natural Earth it treats Antarctic ice shelves as water."""

    def __init__(self):
        from global_land_mask import globe  # noqa: PLC0415 (optional)
        self._globe = globe

    def is_land(self, lat: float, lon: float) -> bool:
        return bool(self._globe.is_land(max(-89.99, min(89.99, lat)), wrap_lon(lon)))


@lru_cache(maxsize=1)
def default_land_mask():
    """GlobeLandMask when global-land-mask is installed, else the bundled Natural Earth rings.
    Set MNO_ENV_LAND_MASK=naturalearth to force the bundled mask (tests do)."""
    import os
    if os.environ.get("MNO_ENV_LAND_MASK", "") != "naturalearth":
        try:
            return GlobeLandMask()
        except ImportError:
            pass
    return LandMask.from_file()
