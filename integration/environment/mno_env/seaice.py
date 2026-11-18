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
EDGE_X15 = math.log(98.0 / 15.0 - 1.0)  # logistic offset that puts 15 % on the edge


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


def edge_shape(hemisphere: str, lon: float, sh_summer: float = 0.0) -> float:
    """Degrees of latitude added to the base edge at this longitude (towards the equator is
    positive). Arctic: the Norwegian/Barents Sea (warm Atlantic inflow) stays open while
    Hudson Bay, the Baltic, Okhotsk, the Bering Sea and Labrador freeze far south; the
    Irminger Sea stays open apart from a narrow East Greenland strip. Antarctic, blended by
    sh_summer (1 at the February minimum, 0 in winter): in winter the Weddell and Ross gyres
    carry ice furthest north; at the summer minimum the surviving pack is in the western
    Weddell and the Bellingshausen/Amundsen Seas while the Ross Sea opens. Procedural shape
    fitted by eye to NSIDC/NIC climatology maps, not data."""
    rad = math.pi / 180
    if hemisphere == "south":
        winter = (4.0 * math.exp(-(lon_delta(lon, -40) / 28) ** 2)     # Weddell gyre carries ice north
                  + 2.5 * math.exp(-(lon_delta(lon, -175) / 25) ** 2)  # Ross gyre
                  - 1.5 * math.exp(-(lon_delta(lon, -100) / 25) ** 2)  # Amundsen/Bellingshausen
                  + 0.8 * math.cos((lon - 5) * rad * 2))
        summer = (6.0 * math.exp(-(lon_delta(lon, -55) / 15) ** 2)     # western Weddell pack survives
                  + 4.0 * math.exp(-(lon_delta(lon, -95) / 28) ** 2)   # Amundsen/Bellingshausen pack
                  - 3.0 * math.exp(-(lon_delta(lon, -178) / 15) ** 2))  # Ross Sea opens
        return (1.0 - sh_summer) * winter + sh_summer * summer
    return (-9.0 * math.exp(-(lon_delta(lon, 8) / 24) ** 2)       # Norwegian Sea: warm Atlantic inflow, open water
            - 3.0 * math.exp(-(lon_delta(lon, 38) / 14) ** 2)      # southern Barents Sea
            + 13.0 * math.exp(-(lon_delta(lon, 22) / 5) ** 2)      # Baltic (Bothnian Bay, Gulf of Finland)
            + 21.0 * math.exp(-(lon_delta(lon, 147) / 9) ** 2)     # Sea of Okhotsk
            + 5.0 * math.exp(-(lon_delta(lon, -175) / 14) ** 2)    # Bering Sea
            + 12.0 * math.exp(-(lon_delta(lon, -85) / 12) ** 2)    # Hudson Bay and Foxe Basin
            + 19.0 * math.exp(-(lon_delta(lon, -63) / 5) ** 2)     # Gulf of St Lawrence / Labrador coast
            + 3.0 * math.exp(-(lon_delta(lon, -58) / 14) ** 2)     # Labrador Sea / Baffin Bay
            + 2.5 * math.exp(-(lon_delta(lon, -25) / 4) ** 2))     # narrow East Greenland Current strip


NORTH_EDGE_CAP = 80.5  # the central Arctic stays ice-covered even at the record minimum


def concentration(hemisphere: str, lat: float, lon: float, base_edge: float, sh_summer: float = 0.0) -> float:
    """Percent. base_edge is the |latitude| of the 15 % line before shape (concentration is
    exactly 15 % there); ice reaches about 90 % some 4 degrees poleward of it. In the north the
    shaped edge never retreats beyond NORTH_EDGE_CAP, so the pole keeps its pack."""
    edge = base_edge - edge_shape(hemisphere, lon, sh_summer)
    if hemisphere == "north":
        edge = min(edge, NORTH_EDGE_CAP)
    if (hemisphere == "south") != (lat < 0):
        return 0.0
    # 98 / (1 + exp(-x)) = 15 exactly at x = -ln(98/15 - 1); ice reaches ~90 % about 4 degrees poleward
    x = (abs(lat) - edge) * 1.0 - EDGE_X15
    return 98.0 / (1.0 + math.exp(-max(-35.0, min(35.0, x))))


@lru_cache(maxsize=1)
def _ocean_cells():
    """(lat, lon, area km2) of ocean cells on the 1-degree helper grid, using the bundled
    Natural Earth mask (always the same mask, so results do not depend on optional packages).
    That mask reads Antarctic ice shelves as water, but NSIDC extent is SEA ice only, so cells
    inside the Natural Earth 1:10m ice-shelf polygons (about 1.3 million km2) are left out."""
    from .ice import load_shelves
    mask = LandMask.from_file()
    shelves = load_shelves()
    cells = []
    for j in range(180):
        lat = -89.5 + j * RES
        if abs(lat) < 40:
            continue
        area = EARTH_R_KM ** 2 * math.radians(RES) * (math.sin(math.radians(lat + RES / 2)) - math.sin(math.radians(lat - RES / 2)))
        for i in range(360):
            lon = -179.5 + i * RES
            if mask.is_land(lat, lon):
                continue
            if lat < -79.0:  # behind the shelf fronts (Ross ~78.5S at most): grounded ice the coarse mask calls water
                continue
            if lat < -60 and any(sh.contains(lat, lon) for sh in shelves):
                continue
            cells.append((lat, lon, abs(area)))
    return tuple(cells)


def extent(hemisphere: str, base_edge: float, sh_summer: float = 0.0) -> float:
    """Million km2 of ocean with >= 15 % concentration for a base edge (1-degree cells)."""
    total = 0.0
    for lat, lon, area in _ocean_cells():
        if (lat < 0) == (hemisphere == "south") and concentration(hemisphere, lat, lon, base_edge, sh_summer) >= 15.0:
            total += area
    return total / 1e6


@lru_cache(maxsize=8)
def _sampling(hemisphere: str, res: float):
    """How a game-side bilinear sample of a res-degree global grid sees each 1-degree ocean
    cell: the grid nodes of the hemisphere (lat, lon, is_land) and, per cell, its four node
    indices and weights. Land nodes carry no ice (procedural.py writes 0 there)."""
    mask = LandMask.from_file()
    nx = int(round(360 / res))
    ny = int(round(180 / res)) + 1
    nodes, index = [], {}
    for j in range(ny):
        lat = -90.0 + j * res
        if abs(lat) < 40 - res or (lat < 0) != (hemisphere == "south"):
            continue
        for i in range(nx):
            lon = -180.0 + i * res
            index[(j, i)] = len(nodes)
            nodes.append((lat, lon, mask.is_land(max(-89.9, min(89.9, lat)), lon)))
    cells = []
    for lat, lon, area in _ocean_cells():
        if (lat < 0) != (hemisphere == "south"):
            continue
        fj, fi = (lat + 90.0) / res, (lon + 180.0) / res
        j0, i0 = int(math.floor(fj)), int(math.floor(fi))
        ty, tx = fj - j0, fi - i0
        j1 = min(j0 + 1, ny - 1)
        corners = [(j0, i0 % nx, (1 - ty) * (1 - tx)), (j0, (i0 + 1) % nx, (1 - ty) * tx),
                   (j1, i0 % nx, ty * (1 - tx)), (j1, (i0 + 1) % nx, ty * tx)]
        if all((j, i) in index for j, i, _ in corners):
            cells.append((tuple((index[(j, i)], w) for j, i, w in corners), area))
    return tuple(nodes), tuple(cells)


def extent_on_grid(hemisphere: str, base_edge: float, res: float, sh_summer: float = 0.0) -> float:
    """Million km2 with >= 15 % as the game sees it: the res-degree grid sampled bilinearly
    at the 1-degree ocean cells (coarse grids otherwise overshoot NSIDC by up to 20 %)."""
    nodes, cells = _sampling(hemisphere, res)
    vals = [0.0 if land else concentration(hemisphere, lat, lon, base_edge, sh_summer) for lat, lon, land in nodes]
    total = 0.0
    for corners, area in cells:
        if sum(vals[k] * w for k, w in corners) >= 15.0:
            total += area
    return total / 1e6


@lru_cache(maxsize=800)
def base_edge_for(hemisphere: str, target_mkm2: float, sh_summer: float = 0.0, res: float | None = None) -> float:
    """Bisection for the base edge whose extent matches the target (to about 0.02 million km2).
    With res, the extent is measured as a game-side bilinear sample of a res-degree grid."""
    def ext(edge):
        return extent(hemisphere, edge, sh_summer) if res is None else extent_on_grid(hemisphere, edge, res, sh_summer)
    lo, hi = 40.0, 95.0  # an edge beyond the pole (95) leaves almost no ice; 40 is far beyond any real extent
    if not ext(hi) <= target_mkm2 <= ext(lo):
        raise ValueError(f"{hemisphere} extent target {target_mkm2} outside what the edge model can produce")
    for _ in range(30):
        mid = (lo + hi) / 2
        if ext(mid) > target_mkm2:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 4)


def sh_summer_on(when: dt.datetime) -> float:
    """Antarctic summer weight: 1 at the February minimum (about 20 Feb), 0 from June to
    October, rounded to 0.05 so windows reuse cached edges."""
    days = (when - dt.datetime(when.year, 2, 20, tzinfo=when.tzinfo)).total_seconds() / 86400.0
    days = (days + 182.6) % 365.2422 - 182.6   # -182..+182 days from the minimum
    w = max(0.0, math.cos(math.pi * days / 200.0)) ** 1.5 if abs(days) < 100 else 0.0
    return round(w * 20) / 20


def edges_on(when: dt.datetime, baseline: str = DEFAULT_BASELINE, res: float | None = None) -> dict:
    """Base edge per hemisphere for a date. Targets are rounded to 0.05 million km2 so that a
    72-hour campaign window reuses cached solutions. Pass res (degrees) to calibrate for the
    grid the game will sample."""
    shw = sh_summer_on(when)
    out = {"sh_summer": shw}
    for h in ("north", "south"):
        t = round(target_extent(h, when, baseline) * 20) / 20
        out[h] = base_edge_for(h, t, shw if h == "south" else 0.0, res)
    return out


def ice_at(lat: float, lon: float, edges: dict) -> float:
    if abs(lat) < 40:
        return 0.0
    h = "south" if lat < 0 else "north"
    return min(100.0, concentration(h, lat, lon, edges[h], edges.get("sh_summer", 0.0) if h == "south" else 0.0))
