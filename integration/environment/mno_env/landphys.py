"""Land and coast terms for the procedural model (v6). BUILD-TESTED.

PROCEDURAL, NOT DATA. Analytic terms fitted by hand to climatology (ERA5, CRU, GPCP as cited by
the land review in docs/environment/ENV-STATUS.md), in the style of the rest of the model:

- continentality: the distance over land, upwind, to the sea (west in the westerlies, east in
  the trades), from a 1-degree raster of the bundled Natural Earth land mask;
- land air temperature: winters colder and summers warmer than the marine formula, by
  continentality, latitude and aridity, on a land phase that lags the sun by about 10 days;
- aridity: the subtropical deserts and the Red Sea / Persian Gulf are dry and mostly clear; the
  Horn of Africa and Bab el-Mandeb do not carry the ITCZ rain belt;
- regional winds where the theatre wind is not geostrophic at the model's resolution: the East
  Asian winter (north-east) and summer (south-west) monsoon over the South China Sea and the
  Taiwan Strait, the Gulf shamal, Hormuz, the Red Sea along-axis wind, the Aegean etesians.

Every function is deterministic and needs no network or optional package.
"""
from __future__ import annotations

import math
from functools import lru_cache

from .geo import lon_delta

RAD = math.pi / 180


def smooth(a: float, b: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def soft_box(lat, lon, la0, la1, lo0, lo1, edge=2.5) -> float:
    """1 inside the box, smooth over `edge` degrees outside it (longitudes may cross 180)."""
    wl = smooth(la0 - edge, la0, lat) * (1 - smooth(la1, la1 + edge, lat))
    span = (lo1 - lo0) % 360
    d = (lon - lo0) % 360
    if d > span:  # outside: distance to the nearer side
        out = min(d - span, 360 - d)
        wo = 1 - smooth(0, edge, out)
    else:
        wo = 1.0
    return wl * wo


@lru_cache(maxsize=1)
def land_raster():
    """1-degree land/sea raster (row 0 = 89.5N, column 0 = 179.5W), about 1 s once per process."""
    from .geo import LandMask
    m = LandMask.from_file()
    return tuple(tuple(m.is_land(89.5 - j, -179.5 + i) for i in range(360)) for j in range(180))


def _is_land_1deg(lat: float, lon: float) -> bool:
    j = min(179, max(0, int(89.5 - lat + 0.5)))
    i = int((lon + 179.5) % 360 + 0.5) % 360
    return land_raster()[j][i]


@lru_cache(maxsize=1 << 16)
def upwind_land_km(lat_r: float, lon_r: float) -> float:
    """Distance over land to the sea, upwind: west poleward of 28 degrees, east equatorward of
    22 degrees, blended between. 0 at sea, capped at 8000 km."""
    if not _is_land_1deg(lat_r, lon_r):
        return 0.0
    def run(step):
        n = 0
        while n < 120 and _is_land_1deg(lat_r, lon_r + step * (n + 1)):
            n += 1
        return (n + 0.5) * 111.2 * max(0.15, math.cos(lat_r * RAD))
    a = abs(lat_r)
    w = smooth(22, 28, a)
    d = w * run(-1) + (1 - w) * run(+1)
    return min(8000.0, d)


def continentality(lat: float, lon: float) -> float:
    """0 at the coast or at sea, about 0.45 at Moscow, 0.9 or more in eastern Siberia."""
    return 1.0 - math.exp(-upwind_land_km(round(lat, 1), round(lon, 1)) / 2500.0)


DESERTS = [  # lat0, lat1, lon0, lon1, weight, active months ('all' or a set)
    (17, 32, -17, 35, 1.0, None),      # Sahara
    (15, 32, 35, 60, 1.0, None),       # Arabia
    (24, 34, 55, 70, 0.8, "winter"),   # Iran / Pakistan (dry outside the monsoon)
    (36, 46, 75, 110, 0.6, None),      # Taklamakan / Gobi
    (25, 37, -118, -105, 0.8, None),   # south-west US / Sonora
    (-30, -17, 12, 25, 0.9, None),     # Kalahari / Namib
    (-30, -15, -75, -68, 1.0, None),   # Atacama
    (-32, -18, 118, 145, 0.8, None),   # Australian interior
]


def aridity(lat: float, lon: float, landf: float, nh_summer: float) -> float:
    """0..1. Deserts on land (scaled by the node's land share) and the Red Sea / Persian Gulf."""
    a = 0.0
    for la0, la1, lo0, lo1, w, when in DESERTS:
        f = w * soft_box(lat, lon, la0, la1, lo0, lo1)
        if when == "winter":
            f *= 1 - 0.8 * nh_summer
        a = max(a, f * landf)
    a = max(a, 0.85 * soft_box(lat, lon, 13, 30, 32, 44, 1.5))                         # Red Sea
    a = max(a, (0.45 + 0.4 * nh_summer) * soft_box(lat, lon, 23, 31, 47, 57, 1.5))    # Persian Gulf
    return a


def horn_dry(lat: float, lon: float) -> float:
    """Horn of Africa, Yemen, Gulf of Aden and Bab el-Mandeb: no ITCZ rain belt (0..0.95)."""
    return 0.95 * smooth(6, 10, lat) * (1 - smooth(28, 32, lat)) * smooth(39, 42, lon) * (1 - smooth(54, 58, lon))


def land_temp_delta(lat: float, lon: float, landf: float, winter_land: float, arid: float) -> float:
    """Degrees C added to the marine air formula on land: continental winters colder, summers
    warmer, deserts hot by day-mean in summer and cooler in winter. winter_land is 1 at the land
    winter peak and 0 at the summer peak (land phase, about 10 days after the sun)."""
    if landf <= 0.0:
        return 0.0
    a = abs(lat)
    c = continentality(lat, lon)
    band = smooth(10, 30, a) * (1 - smooth(60, 75, a))
    summer = 1.0 - winter_land
    cold = -(34.0 * c * smooth(30, 60, a) + 9.0 * arid) * smooth(0.5, 1.0, winter_land) * 2.0 * (winter_land - 0.5)
    warm = ((6.0 + 9.0 * c) * band + 3.0 * arid) * smooth(0.5, 1.0, summer) * 2.0 * (summer - 0.5)
    return landf * (cold + warm)


def roughness(landf: float, lat: float) -> float:
    """10 m wind factor over land (1 at sea): about 0.6-0.75 for interior land."""
    if landf < 0.75:
        return 1.0
    return 1.0 - landf * (0.25 + 0.15 * (1 - smooth(10, 25, abs(lat))))


def _ellipse(lat, lon, la, lo, bearing, s_along, s_across) -> float:
    dx = lon_delta(lon, lo) * math.cos(lat * RAD)
    dy = lat - la
    b = bearing * RAD
    along = dx * math.sin(b) + dy * math.cos(b)
    across = dx * math.cos(b) - dy * math.sin(b)
    return math.exp(-(along / s_along) ** 2 - (across / s_across) ** 2)


def _toward(from_deg: float, speed: float) -> tuple[float, float]:
    """(u, v) of a wind blowing FROM a direction at a speed."""
    b = (from_deg + 180.0) * RAD
    return speed * math.sin(b), speed * math.cos(b)


def regional_wind(lat: float, lon: float, doy: float, nh_summer: float, n_ms: float, n_sh: float, n_et: float,
                  ew: float) -> tuple[float, float, float]:
    """(blend weight 0..1, u, v) of the strongest regional wind regime at this point, or (0, 0, 0).
    The caller blends u,v = (1-w)*u,v + w*target. doy is the day of year; the noises are the
    model's seeded travelling-wave noises (standard deviation about 0.33)."""
    ea_w = smooth(253, 288, doy) if doy >= 200 else 1 - smooth(84, 125, doy)       # East Asian winter monsoon
    ea_s = smooth(135, 161, doy) * (1 - smooth(237, 263, doy))                        # East Asian summer monsoon
    best = (0.0, 0.0, 0.0)

    def take(w, uv):
        nonlocal best
        if w > best[0]:
            best = (min(1.0, w), uv[0], uv[1])

    if ea_w > 0:
        k = 1 + 0.45 * max(-0.6, min(1.6, 1.5 * n_ms / 0.33))      # cold surges
        take(1.5 * ea_w * math.exp(-((lat - 18) / 9) ** 2 - (lon_delta(lon, 116) / 12) ** 2), (-6.5 * k, -6.8 * k))
        take(0.6 * ea_w * math.exp(-((lat - 11) / 3) ** 2 - (lon_delta(lon, 110) / 4) ** 2), (-7.5 * k, -7.8 * k))
        take(0.9 * ea_w * math.exp(-((lat - 3) / 4) ** 2 - (lon_delta(lon, 105) / 8) ** 2), (-1.5, -3.6))
        take(1.2 * ea_w * _ellipse(lat, lon, 24.3, 119.6, 30, 3.0, 1.6), _toward(35, 9.5 * k))       # Taiwan Strait channel
    if ea_s > 0:
        take(1.3 * ea_s * math.exp(-((lat - 23.5) / 5) ** 2 - (lon_delta(lon, 118) / 8) ** 2), (4.0, 3.5))
    # Gulf shamal (north-westerly along the Gulf; stronger in early summer)
    sh = _ellipse(lat, lon, 27.5, 51.0, 135, 6.0, 2.5)
    if sh > 1e-3:
        s = 6.0 + 1.5 * nh_summer + 2.5 * ew + 2.0 * n_sh / 0.33
        take((0.65 + 0.3 * nh_summer) * sh, _toward(320, max(1.5, s)))
    hz = _ellipse(lat, lon, 26.3, 56.3, 100, 4.5, 3.0)
    if hz > 1e-3:
        take(1.0 * hz * (1 - (1 - nh_summer) * smooth(56.5, 57.5, lon)), _toward(290, 5.0 + 1.0 * ew))
    # Red Sea: along the axis; north part from NNW all year, south part from SSE in Oct-May
    rn = _ellipse(lat, lon, 23.0, 37.0, 150, 6.5, 3.2)
    if rn > 1e-3:
        take(1.0 * rn, _toward(330, 6.0 + 1.5 * ew))
    rs = _ellipse(lat, lon, 15.0, 41.5, 150, 4.0, 3.0)
    if rs > 1e-3:
        winter = 1 - smooth(140, 160, doy) * (1 - smooth(255, 275, doy))
        uw, vw = _toward(155, 7.5 + 1.5 * ew)
        us, vs = _toward(330, 4.0 + 1.0 * ew)
        take(1.0 * rs, (winter * uw + (1 - winter) * us, winter * vw + (1 - winter) * vs))
    # Aegean etesians (meltemi), July-August
    s_et = max(0.0, min(1.0, (nh_summer - 0.3) / 0.5))
    if s_et > 0:
        e = 1.0 * s_et * math.exp(-((lat - 38.5) / 4.5) ** 2 - (lon_delta(lon, 25.5) / 6.0) ** 2) * smooth(34.0, 36.0, lat)
        take(e, _toward(15, 8.5 * (1 + n_et / 0.33 * 0.35)))
    return best
