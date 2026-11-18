"""Seasonal sea-ice climatology: summer/winter shift of the ice edge in both hemispheres. BUILD-TESTED.

The procedural ice field is calibrated so that its sea-ice EXTENT (area of ocean cells with
concentration >= 15 %, NSIDC's definition) matches the NSIDC Sea Ice Index (G02135 v4.0)
monthly median extent for the campaign date, interpolated between mid-month values. The
table is computed from NSIDC's own monthly CSVs by tools/refresh_seaice_climatology.py and
stored in data/seaice-climatology-nsidc-g02135.json with the files' SHA-256.

Baselines: "2016_2025" (default; the latest ten complete years, the closest observed state
to a 2028-2029 campaign) and "1981_2010" (NSIDC's reference period). Neither is a forecast of
2028. The edge SHAPE (which longitudes reach further from the pole) is procedural.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from functools import lru_cache
from pathlib import Path

from .geo import LandMask, lon_delta

CLIMATOLOGY_FILE = Path(__file__).resolve().parents[1] / "data" / "seaice-climatology-nsidc-g02135.json"
DEFAULT_BASELINE = "2016_2025"


@lru_cache(maxsize=1)
def climatology() -> dict:
    return json.loads(CLIMATOLOGY_FILE.read_text(encoding="utf-8"))


def table(hemisphere: str, baseline: str = DEFAULT_BASELINE) -> list:
    return climatology()["median"][baseline][hemisphere]


EARTH_R_KM = 6371.0
RES = 1.0  # helper grid for extent integration


def target_extent(hemisphere: str, when: dt.datetime, baseline: str = DEFAULT_BASELINE) -> float:
    """Million km2 on a given date: linear between mid-month values (day 15 of each month)."""
    tab = table(hemisphere, baseline)
    mid = dt.datetime(when.year, when.month, 15, tzinfo=when.tzinfo)
    if when >= mid:
        m0, y0 = when.month, when.year
    else:
        m0, y0 = (when.month - 1, when.year) if when.month > 1 else (12, when.year - 1)
    m1, y1 = (m0 + 1, y0) if m0 < 12 else (1, y0 + 1)
    a = dt.datetime(y0, m0, 15, tzinfo=when.tzinfo)
    b = dt.datetime(y1, m1, 15, tzinfo=when.tzinfo)
    f = (when - a).total_seconds() / (b - a).total_seconds()
    return tab[m0 - 1] + f * (tab[m1 - 1] - tab[m0 - 1])


def edge_shape(hemisphere: str, lon: float) -> float:
    """Degrees of latitude added to the base edge at this longitude (towards the equator is
    positive). Southern: Weddell and Ross gyres carry ice further north; Arctic: the Atlantic
    side (Norwegian/Barents Sea, warm inflow) stays freer of ice than the Pacific/Okhotsk side.
    Procedural shape, not data."""
    rad = math.pi / 180
    if hemisphere == "south":
        return (2.5 * math.exp(-(lon_delta(lon, -40) / 30) ** 2) + 2.0 * math.exp(-(lon_delta(lon, -175) / 25) ** 2)
                + 0.8 * math.cos((lon - 5) * rad * 2))
    return (-4.0 * math.exp(-(lon_delta(lon, 20) / 35) ** 2) + 2.5 * math.exp(-(lon_delta(lon, 150) / 30) ** 2)
            + 1.5 * math.exp(-(lon_delta(lon, -60) / 20) ** 2))


def concentration(hemisphere: str, lat: float, lon: float, base_edge: float) -> float:
    """Percent. base_edge is the |latitude| of the 15 % line before shape; ice rises to ~98 %
    over about 4 degrees poleward of it."""
    edge = base_edge - edge_shape(hemisphere, lon)
    z = (abs(lat) - edge) / 1.6 + 1.1  # logistic centred so that conc = 15 % at the edge
    if (hemisphere == "south") != (lat < 0):
        return 0.0
    return 98.0 / (1.0 + math.exp(-max(-35.0, min(35.0, 1.6 * z))))


@lru_cache(maxsize=1)
def _ocean_cells():
    """(lat, lon, area km2) of ocean cells on the 1-degree helper grid, using the bundled
    Natural Earth mask (always the same mask, so results do not depend on optional packages).
    Ice shelves count as ocean in this mask; they are a small, fixed share of both hemispheres."""
    mask = LandMask.from_file()
    cells = []
    for j in range(180):
        lat = -89.5 + j * RES
        if abs(lat) < 40:
            continue
        area = EARTH_R_KM ** 2 * math.radians(RES) * (math.sin(math.radians(lat + RES / 2)) - math.sin(math.radians(lat - RES / 2)))
        for i in range(360):
            lon = -179.5 + i * RES
            if not mask.is_land(lat, lon):
                cells.append((lat, lon, abs(area)))
    return tuple(cells)


def extent(hemisphere: str, base_edge: float) -> float:
    """Million km2 of ocean with >= 15 % concentration for a base edge."""
    total = 0.0
    for lat, lon, area in _ocean_cells():
        if (lat < 0) == (hemisphere == "south") and concentration(hemisphere, lat, lon, base_edge) >= 15.0:
            total += area
    return total / 1e6


@lru_cache(maxsize=800)
def base_edge_for(hemisphere: str, target_mkm2: float) -> float:
    """Bisection for the base edge whose extent matches the target (to about 0.02 million km2)."""
    lo, hi = 45.0, 89.0  # edge near 45 deg = huge extent; near 89 = none
    for _ in range(30):
        mid = (lo + hi) / 2
        if extent(hemisphere, mid) > target_mkm2:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 4)


def edges_on(when: dt.datetime, baseline: str = DEFAULT_BASELINE) -> dict:
    """Base edge per hemisphere for a date. Targets are rounded to 0.05 million km2 so that a
    72-hour campaign window reuses cached solutions."""
    out = {}
    for h in ("north", "south"):
        t = round(target_extent(h, when, baseline) * 20) / 20
        out[h] = base_edge_for(h, t)
    return out


def ice_at(lat: float, lon: float, edges: dict) -> float:
    if abs(lat) < 40:
        return 0.0
    h = "south" if lat < 0 else "north"
    return min(100.0, concentration(h, lat, lon, edges[h]))
