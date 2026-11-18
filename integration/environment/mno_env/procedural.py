"""Seeded procedural weather: the offline fallback for any campaign date. BUILD-TESTED.

PROCEDURAL, NOT REAL WEATHER. Version 4 ("mno.env.procedural.4") builds each frame from the
parts below. v4 answers a 36-point independent critique of v3 (storm stacking, tracks too far
equatorward, rain 3x too high, cloud too low, extreme winds and waves too common, no calm seas,
tropical cyclones crossing land, no tropical or temperature variability, season jump at the
year boundary, global mass drifting with storm count).

1. A seasonal sea-level-pressure climatology: equatorial trough following the ITCZ,
   subtropical highs near 30 degrees, subpolar lows near 60-65 degrees (the Southern Ocean
   trough deepest), and the main semi-permanent centres - Aleutian and Icelandic lows (northern
   winter), Azores and North Pacific highs (northern summer), the three southern subtropical
   highs, and the South Asian monsoon low (northern summer).
2. Synoptic systems that are BORN, MOVE and DIE, enumerated deterministically from the seed
   in 6-hour slots, so weather evolves for any length of campaign and never runs out:
   - extratropical cyclones: genesis 32-52 degrees (favoured off the east coasts of Asia and
     North America in the north; all longitudes in the south), deepening for about the first
     third of a 3.5-7 day life and filling after, moving east 8-14 degrees of longitude a day
     and poleward 0.3-1.2 degrees a day; more frequent in each hemisphere's winter;
   - tropical cyclones: per basin and season (North Atlantic, East and West Pacific, North
     Indian, South Indian, Australia/South Pacific), moving west, then recurving poleward and
     east, decaying beyond about 32 degrees of latitude.
3. Wind from the pressure field: geostrophic balance on the grid (f = 2 Omega sin(lat)),
   reduced to 70 % and turned 20 degrees towards low pressure for the 10 m wind; equatorward of
   15 degrees it blends into trade winds converging on the ITCZ. Lows therefore turn
   anticlockwise in the north and clockwise in the south, by construction.
4. Waves: wind sea (fully developed Pierson-Moskowitz height 0.0214 U^2, scaled for limited
   duration) combined with swell radiating from active storms and a Southern Ocean swell belt.
5. Cloud, rain and convective risk from the ITCZ, monsoon, fronts and storm cores; marine
   stratocumulus off the subtropical west coasts; temperature from latitude and season; sea
   ice from the NSIDC-calibrated climatology (seaice.py).

Determinism: the only randomness is SHA-256 of (seed, label); results do not depend on the
machine, the Python version or the order frames are generated in.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import math
from functools import lru_cache

from . import seaice
from .geo import lon_delta, wrap_lon
from .grid import LatLonGrid
from .snapshot import SCHEMA, iso, pack_int16, seal

VERSION = "mno.env.procedural.4"
PACK = {  # field -> int16 scale
    "msl_pressure_hpa": 0.1, "wind_u10_ms": 0.01, "wind_v10_ms": 0.01, "cloud_fraction_pct": 0.1,
    "precip_rate_mm_h": 0.01, "air_temp_2m_c": 0.01, "wave_hs_m": 0.01, "sea_ice_conc_pct": 0.1,
    "convective_risk_idx": 0.001,
}
RAD = math.pi / 180
EPOCH = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
SLOT_H = 6
OMEGA = 7.2921e-5
RHO = 1.225
DEG_M = 111_195.0

# Tropical cyclone basins: genesis box (lat0, lat1, lon0, lon1), monthly weight (Jan..Dec),
# storms per year (approximate long-term climatology), recurvature latitude.
TC_BASINS = {
    "NATL": ((10, 22), (-80, -25), [0, 0, 0, 0, .1, .4, .8, 1.6, 2.4, 1.6, .5, .1], 14, 27),
    "ENP": ((10, 18), (-120, -95), [0, 0, 0, 0, .5, 1.5, 2, 2.2, 1.8, 1, .3, 0], 16, 22),
    "WPAC": ((8, 22), (125, 160), [.3, .2, .2, .4, .7, 1.2, 2, 2.3, 2.1, 1.7, 1, .5], 26, 25),
    "NIO": ((8, 18), (62, 92), [.1, 0, .1, .4, 1, .6, .3, .3, .4, 1.1, 1.3, .6], 5, 22),
    "SIO": ((-20, -8), (50, 100), [2, 2.2, 2, 1.2, .5, .1, 0, 0, .1, .3, 1, 1.8], 10, -22),
    "SPAC": ((-20, -10), (145, 190), [2.4, 2.4, 2, 1.2, .4, .1, 0, 0, 0, .2, .8, 1.8], 10, -24),
}


def unit(seed: str, label: str) -> float:
    """Deterministic number in [0, 1)."""
    h = hashlib.sha256(f"{seed}|{label}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64


def _hours(t: dt.datetime) -> float:
    return (t - EPOCH).total_seconds() / 3600.0


TROPICAL_YEAR_D = 365.2422
SEASON_REF = dt.datetime(2000, 1, 15, tzinfo=dt.timezone.utc)  # a mid-January reference


def _season(t: dt.datetime, lag_days: float = 0.0) -> float:
    """+1 at the northern winter peak (mid January), -1 at the northern summer peak (mid July).
    Continuous across year boundaries (no jump on 1 January). lag_days delays the cycle, as
    the ocean-coupled features (ITCZ, pressure centres) lag the sun by about six weeks."""
    days = (t - SEASON_REF).total_seconds() / 86400.0 - lag_days
    return math.cos(2 * math.pi * days / TROPICAL_YEAR_D)


def itcz_lat(lon: float, season: float) -> float:
    """ITCZ latitude: about 2N in northern winter, 10N in summer; pulled north over the Indian
    Ocean / South Asia in the summer monsoon and south over the Indian Ocean in winter."""
    base = 6.0 - 4.0 * season
    monsoon = 10.0 * max(0.0, -season) * math.exp(-(lon_delta(lon, 80) / 35) ** 2)
    sw_ind = -8.0 * max(0.0, season) * math.exp(-(lon_delta(lon, 70) / 40) ** 2)
    return base + monsoon + sw_ind


def background_pressure(lat: float, lon: float, season: float) -> float:
    """Seasonal climatological sea-level pressure, hPa (smooth analytic fit, not data)."""
    nh_winter = 0.5 + 0.5 * season       # 1 in January, 0 in July
    sh_winter = 1.0 - nh_winter
    a = abs(lat)
    winter = nh_winter if lat >= 0 else sh_winter
    p = 1012.0
    phi_sub = 30.0 + 4.0 * (1 - winter)
    p += (5.0 + 3.0 * (1 - winter if lat >= 0 else winter)) * math.exp(-((a - phi_sub) / 11.0) ** 2)
    p -= 4.0 * math.exp(-((lat - itcz_lat(lon, season)) / 7.0) ** 2)
    if lat < 0:
        p -= (19.0 + 5.0 * sh_winter) * math.exp(-((lat + 66.0) / 12.0) ** 2)  # the storms supply the rest of the trough
    else:
        p -= (2.0 + 3.0 * nh_winter) * math.exp(-((lat - 62.0) / 9.0) ** 2)
    feats = [  # (lat, lon, amplitude hPa, lat scale, lon scale)
        (52, 180, -5 * nh_winter, 9, 30),             # Aleutian low (time-mean of passing storms: mostly supplied by them)
        (61, -32, -6 * nh_winter, 9, 30),             # Icelandic low (likewise)
        (52, 95, 14 * nh_winter, 12, 35),             # Siberian high (northern winter)
        (36, -38, 2 + 7 * (1 - nh_winter), 9, 28),    # Azores high
        (36, -150, 2 + 8 * (1 - nh_winter), 9, 32),   # North Pacific high
        (28, 72, -9 * (1 - nh_winter), 10, 25),       # South Asian monsoon low
        (-29, -12, 5 + 2 * sh_winter, 8, 25),         # South Atlantic high
        (-31, 78, 5 + 2 * sh_winter, 8, 30),          # South Indian high
        (-32, -100, 5 + 2 * sh_winter, 8, 32),        # South Pacific high
    ]
    for la, lo, amp, sy, sx in feats:
        if amp:
            p += amp * math.exp(-((lat - la) / sy) ** 2 - (lon_delta(lon, lo) / sx) ** 2)
    return p


def _extratropical(seed: str, slot: int, hemi: int, k: int, season: float):
    tag = f"x{hemi}.{slot}.{k}"
    winter = (0.5 + 0.5 * season) if hemi > 0 else (0.5 - 0.5 * season)
    rate = (0.13 + 0.09 * winter) if hemi > 0 else (0.20 + 0.05 * winter)  # per 6 h per candidate (~8-10 lows alive per hemisphere)
    if unit(seed, tag + ".p") >= rate:
        return None
    u = lambda s: unit(seed, f"{tag}.{s}")  # noqa: E731
    if hemi > 0:
        r = u("where")
        lon0 = (-75 + 30 * u("lon")) if r < 0.4 else (125 + 40 * u("lon")) if r < 0.8 else (-180 + 360 * u("lon"))
        lat0 = 37 + 12 * u("lat") + 3 * (1 - winter)
    else:
        lon0, lat0 = -180 + 360 * u("lon"), -(39 + 13 * u("lat"))
    # lows travel poleward through life and die near the subpolar troughs (55-68 degrees)
    return {"kind": "extratropical", "t0": slot * SLOT_H, "lat0": lat0, "lon0": lon0,
            "life_d": 4.0 + 3.0 * u("life"), "deficit": 14 + 28 * u("deficit") + 5 * winter,
            "radius": 7.5 + 6.0 * u("radius"), "vlon": 8 + 6 * u("vlon"), "vlat": hemi * (1.6 + 1.8 * u("vlat"))}


def _tropical(seed: str, slot: int, basin: str, month: int):
    (la0, la1), (lo0, lo1), weights, per_year, recurve = TC_BASINS[basin]
    w = weights[month - 1] / (sum(weights) / 12.0)
    rate = per_year / (365.25 * 24 / SLOT_H) * w
    tag = f"t{basin}.{slot}"
    if rate <= 0 or unit(seed, tag + ".p") >= rate:
        return None
    u = lambda s: unit(seed, f"{tag}.{s}")  # noqa: E731
    lat0 = la0 + (la1 - la0) * u("lat")
    return {"kind": "tropical", "basin": basin, "t0": slot * SLOT_H, "lat0": lat0, "lon0": lo0 + (lo1 - lo0) * u("lon"),
            "life_d": 5 + 5 * u("life"), "deficit": 15 + 50 * u("deficit") ** 1.5, "radius": 2.5 + 2.0 * u("radius"),
            "vwest": 4 + 3 * u("vw"), "vpole": 0.6 + 0.8 * u("vp"), "recurve": recurve}


def _position(s: dict, age_d: float) -> tuple[float, float, float]:
    """(lat, lon, intensity 0..1) of a storm at an age in days."""
    x = age_d / s["life_d"]
    if not 0.0 <= x <= 1.0:
        return 0.0, 0.0, 0.0
    if s["kind"] == "extratropical":
        lat = s["lat0"] + s["vlat"] * age_d * (1 - 0.3 * x)  # poleward drift slows as the low occludes
        lat = max(-72.0, min(72.0, lat))
        lon = wrap_lon(s["lon0"] + s["vlon"] * age_d * min(2.5, 1 / max(0.35, math.cos(lat * RAD))) * 0.7)
        inten = math.sin(math.pi * x ** 0.7)
        return lat, lon, inten
    sign = 1 if s["recurve"] > 0 else -1
    t_rec = max(0.0, (abs(s["recurve"]) - abs(s["lat0"])) / s["vpole"])
    if age_d <= t_rec:
        lat = s["lat0"] + sign * s["vpole"] * age_d
        lon = s["lon0"] - s["vwest"] * age_d
    else:
        a2 = age_d - t_rec
        lat = s["lat0"] + sign * (s["vpole"] * t_rec + 2.6 * s["vpole"] * a2)
        lon = s["lon0"] - s["vwest"] * t_rec + (2.0 * a2 + 1.2 * a2 * a2)
    inten = math.sin(math.pi * min(1.0, x ** 0.8))
    if abs(lat) > 32:  # extratropical transition / cool water: weaken
        inten *= math.exp(-(abs(lat) - 32) / 6.0)
    return lat, wrap_lon(lon), inten


def active_storms(seed: str, t: dt.datetime) -> list[dict]:
    """Every storm alive at time t, with its current position and strength."""
    h = _hours(t)
    now_slot = int(math.floor(h / SLOT_H))
    out = []
    for slot in range(now_slot - int(10 * 24 / SLOT_H), now_slot + 1):
        ts = EPOCH + dt.timedelta(hours=slot * SLOT_H)
        season = _season(ts)
        cands = [_extratropical(seed, slot, hemi, k, season) for hemi in (1, -1) for k in range(2)]
        cands += [_tropical(seed, slot, b, ts.month) for b in TC_BASINS]
        for s in cands:
            if s is None:
                continue
            age = (h - s["t0"]) / 24.0
            lat, lon, inten = _position(s, age)
            if s["kind"] == "tropical" and inten > 0.02 and _land().is_land(lat, lon):
                inten *= 0.3  # a tropical cyclone loses its energy source over land
            if inten <= 0.02:
                continue
            out.append({**s, "lat": lat, "lon": lon, "intensity": inten, "age_d": age})
    return out


def _dist_deg(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance in degrees (correct across the poles and the antimeridian)."""
    a = math.sin((lat2 - lat1) * RAD / 2) ** 2 + math.cos(lat1 * RAD) * math.cos(lat2 * RAD) * math.sin(lon_delta(lon2, lon1) * RAD / 2) ** 2
    return 2 * math.asin(math.sqrt(min(1.0, a))) / RAD


@lru_cache(maxsize=1)
def _land():
    from .geo import LandMask
    return LandMask.from_file()  # always the bundled mask, so output does not depend on optional packages


@lru_cache(maxsize=8)
def _land_fraction(grid: LatLonGrid) -> tuple:
    """Share of land within about one grid cell of each cell centre (sheltered seas get less swell)."""
    m = _land()
    out = []
    for j in range(grid.ny):
        lat = grid.lat(j)
        for i in range(grid.nx):
            lon = grid.lon(i)
            pts = [(lat + dy * grid.lat_step * 0.5, lon + dx * grid.lon_step * 0.5) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
            out.append(sum(m.is_land(max(-89.9, min(89.9, a)), b) for a, b in pts) / 9.0)
    return tuple(out)


def _waves_noise(seed: str, lat: float, lon: float, hours: float, kind: str) -> float:
    """Deterministic smooth variability in [-1, 1]: a few travelling waves (easterly waves in
    the tropics move west about 6 degrees a day; mid-latitude ones east). Zero mean."""
    v = 0.0
    for k in range(3):
        a = unit(seed, f"n.{kind}.{k}.a") * 2 * math.pi
        wn = 3 + 3 * k + int(4 * unit(seed, f"n.{kind}.{k}.w"))
        speed = (-6.0 if abs(lat) < 25 else 9.0) * (0.7 + 0.6 * unit(seed, f"n.{kind}.{k}.s"))
        v += math.sin(wn * (lon - speed * hours / 24.0) * RAD + a + (1.7 + k) * lat * RAD * 2) / 3.0
    return v


def _frame(seed: str, t: dt.datetime, grid: LatLonGrid, edges: dict, tick: float) -> dict:
    season = _season(t)
    lag = _season(t, 42.0)  # ocean-coupled features lag the sun by about six weeks
    storms = active_storms(seed, t)
    hrs = _hours(t)
    nh_winter = 0.5 + 0.5 * season
    landf = _land_fraction(grid)
    P, BG, CL, PR, CV, SW, TA = [], [], [], [], [], [], []
    for j in range(grid.ny):
        lat = grid.lat(j)
        for i in range(grid.nx):
            lon = grid.lon(i)
            bg = background_pressure(lat, lon, lag)
            noise_p = _waves_noise(seed, lat, lon, hrs, "p")
            noise_c = _waves_noise(seed, lat, lon, hrs, "c")
            itcz = math.exp(-((lat - itcz_lat(lon, lag)) / 5.0) ** 2)
            p = bg + 1.5 * noise_p * min(1.0, abs(lat) / 20 + 0.3)
            cloud = 50 + 32 * itcz + 22 * noise_c
            rain = 0.32 * itcz ** 2 * (1 + 0.6 * noise_c)
            conv = 0.7 * itcz * (0.7 + 0.3 * noise_c)
            cloud -= 26 * math.exp(-((abs(lat) - 26) / 9) ** 2)        # subtropical subsidence
            cloud += 34 * math.exp(-((abs(lat) - 60) / 12) ** 2)       # subpolar oceans
            for la, lo in ((-20, -80), (-18, 8), (25, -125), (20, -22)):  # marine stratocumulus decks
                cloud += 30 * math.exp(-((lat - la) / 8) ** 2 - (lon_delta(lon, lo) / 14) ** 2)
            sh_winter = 0.5 - 0.5 * season
            belt = (2.0 + 0.9 * sh_winter) if lat < 0 else (0.8 + 1.0 * nh_winter)
            swell = 0.5 + belt * math.exp(-((abs(lat) - 50) / 15) ** 2) + 1.0 * math.exp(-((lat + 5) / 25) ** 2)
            temp_anom = 1.2 * noise_p
            dsq = 0.0
            for st in storms:
                if abs(lat - st["lat"]) > 45:
                    continue
                d = _dist_deg(lat, lon, st["lat"], st["lon"])
                if d > 45:
                    continue
                r, inten = st["radius"], st["intensity"]
                core = math.exp(-0.5 * (d / (0.6 * r)) ** 2)
                dsq += (st["deficit"] * inten * core) ** 2
                if st["kind"] == "tropical":
                    cloud += 65 * inten * math.exp(-0.5 * (d / (1.6 * r)) ** 2)
                    rain += 8.0 * inten * core + 1.2 * inten * math.exp(-0.5 * (d / (1.4 * r)) ** 2)
                    conv = max(conv, inten * math.exp(-0.5 * (d / (1.4 * r)) ** 2))
                else:
                    east = lon_delta(lon, st["lon"]) * math.cos(lat * RAD)
                    equatorward = (st["lat"] - lat) * (1 if st["lat"] > 0 else -1)
                    ang = math.atan2(equatorward, east)
                    side = 0.5 + 0.5 * math.sin(ang + 0.6)            # fronts on the equatorward-east side
                    front = math.exp(-((d - 0.8 * r) / (0.3 * r)) ** 2) * side
                    cloud += inten * (50 * math.exp(-0.5 * (d / r) ** 2) + 25 * front)
                    rain += inten * (0.7 * core + 1.3 * front)
                    if abs(st["lat"]) < 48:
                        conv = max(conv, 0.55 * inten * front)
                    # warm sector ahead (east), cold air behind (west)
                    temp_anom += inten * 3.5 * math.tanh(east / max(1.0, r)) * math.exp(-0.5 * (d / (1.2 * r)) ** 2)
                swell += 2.0 * inten * st["deficit"] / 40.0 * math.exp(-d / 15.0)
            p -= math.sqrt(dsq)  # quadratic sum: overlapping lows deepen each other far less than linearly
            P.append(p)
            BG.append(bg)
            CL.append(max(0.0, min(100.0, cloud)))
            PR.append(max(0.0, min(30.0, rain)))
            CV.append(max(0.0, min(1.0, conv)))
            SW.append(min(6.0, swell) * (1.0 - 0.85 * landf[j * grid.nx + i]))
            TA.append(temp_anom)
    # Conserve mass: storms and noise move air around but do not remove it (area-weighted).
    wsum = dsum = 0.0
    for j in range(grid.ny):
        w = max(0.0, math.cos(grid.lat(j) * RAD))
        for i in range(grid.nx):
            k = j * grid.nx + i
            wsum += w
            dsum += w * (P[k] - BG[k])
    shift = dsum / wsum if wsum else 0.0
    P = [v - shift for v in P]
    # Pole rows are single points.
    for j in (0, grid.ny - 1):
        if abs(grid.lat(j)) >= 90 - 1e-9:
            row = slice(j * grid.nx, (j + 1) * grid.nx)
            for arr in (P, CL, PR, CV, SW, TA):
                m = sum(arr[row]) / grid.nx
                arr[row] = [m] * grid.nx
    U, V = _winds(grid, P, lag, seed, hrs)
    out = {n: [] for n in PACK}
    for j in range(grid.ny):
        lat = grid.lat(j)
        winter_here = (0.5 + 0.5 * season) if lat >= 0 else (0.5 - 0.5 * season)
        for i in range(grid.nx):
            k = j * grid.nx + i
            lon = grid.lon(i)
            spd = math.hypot(U[k], V[k])
            fetch = 1.0 - 0.6 * landf[k]
            wind_sea = 0.0214 * spd * spd * 0.8 * fetch      # limited duration and fetch
            hs = min(13.0, math.hypot(wind_sea, SW[k]))
            temp = -20 + 48 * max(0.0, math.cos(lat * RAD)) ** 1.5 - 9 * (winter_here - 0.5) * min(1.0, abs(lat) / 50) + TA[k]
            wobble = 0.35 * math.sin(tick * 0.4 + lon * RAD * 2)
            ice = seaice.ice_at(lat - (wobble if lat < 0 else -wobble), lon, edges)
            out["msl_pressure_hpa"].append(min(1060.0, max(920.0, P[k])))
            out["wind_u10_ms"].append(U[k])
            out["wind_v10_ms"].append(V[k])
            out["cloud_fraction_pct"].append(CL[k])
            out["precip_rate_mm_h"].append(PR[k])
            out["air_temp_2m_c"].append(max(-60.0, min(45.0, temp)))
            out["wave_hs_m"].append(max(0.1, hs))
            out["sea_ice_conc_pct"].append(min(100.0, ice))
            out["convective_risk_idx"].append(CV[k])
    return out


def _winds(grid: LatLonGrid, P: list, season: float, seed: str = "", hrs: float = 0.0) -> tuple[list, list]:
    """10 m wind from the pressure grid: geostrophic, reduced to 80 % (a 4-degree grid already
    smooths the gradients) and turned 20 degrees
    towards low pressure, softly capped (a coarse-grid geostrophic wind overstates winds in tight
    lows); near the equator it blends into trade winds with travelling easterly-wave variability."""
    U, V = [0.0] * len(P), [0.0] * len(P)
    nx, ny = grid.nx, grid.ny
    for j in range(ny):
        lat = grid.lat(j)
        jn, js = min(j + 1, ny - 1), max(j - 1, 0)
        dy = (grid.lat(jn) - grid.lat(js)) * DEG_M
        coslat = max(0.05, math.cos(lat * RAD))
        dx = 2 * grid.lon_step * DEG_M * coslat
        f = 2 * OMEGA * math.sin(lat * RAD)
        for i in range(nx):
            ie = (i + 1) % nx if grid.global_lon else min(i + 1, nx - 1)
            iw = (i - 1) % nx if grid.global_lon else max(i - 1, 0)
            dpdx = (P[j * nx + ie] - P[j * nx + iw]) * 100.0 / dx
            dpdy = (P[jn * nx + i] - P[js * nx + i]) * 100.0 / dy if dy else 0.0
            ug, vg = 0.0, 0.0
            if abs(lat) >= 5:
                ug, vg = -dpdy / (RHO * f), dpdx / (RHO * f)
            turn = 20 * RAD * (1 if lat >= 0 else -1)
            us = 0.8 * (ug * math.cos(turn) - vg * math.sin(turn))
            vs = 0.8 * (ug * math.sin(turn) + vg * math.cos(turn))
            lon = grid.lon(i)
            itcz = itcz_lat(lon, season)
            ew = _waves_noise(seed, lat, lon, hrs, "w") if seed else 0.0
            trade_u = -6.5 * math.exp(-((abs(lat - itcz) - 12) / 11) ** 2) - 1.5 + 1.5 * ew
            trade_v = 2.5 * math.tanh((itcz - lat) / 6.0) + 1.0 * ew
            w = max(0.0, min(1.0, (abs(lat) - 10) / 12.0))
            u = w * us + (1 - w) * trade_u
            v = w * vs + (1 - w) * trade_v
            spd = math.hypot(u, v)
            if spd > 1e-6:
                cap = 30.0 * math.tanh(spd / 30.0)
                u, v = u * cap / spd, v * cap / spd
            U[j * nx + i], V[j * nx + i] = u, v
    return U, V


def generate(seed: str, start: dt.datetime, hours: int = 72, step_hours: int = 6, res_deg: float = 4.0,
             created: dt.datetime | None = None) -> dict:
    if start.tzinfo is None:
        raise ValueError("start must be UTC")
    if not (1 <= step_hours <= 24 and 0 <= hours <= 24 * 60 and res_deg in (1.0, 2.0, 2.5, 4.0, 5.0)):
        raise ValueError("unsupported procedural request")
    if hours % step_hours:
        raise ValueError("hours must be a whole number of steps")
    grid = LatLonGrid(-180.0, -90.0, res_deg, res_deg, int(360 / res_deg), int(180 / res_deg) + 1)
    times = []
    for k in range(hours // step_hours + 1):
        t = start + dt.timedelta(hours=k * step_hours)
        edges = seaice.edges_on(t)
        cols = _frame(seed, t, grid, edges, _hours(t) / 6.0)
        times.append({"valid_utc": iso(t), "lead_hours": None,
                      "values": {n: pack_int16(cols[n], PACK[n]) for n in PACK}})
    from .snapshot import FIELDS
    fields = {n: {"units": FIELDS[n][0], "fill_value": None, "kind": "procedural",
                  "uncertainty": {"type": "not_applicable", "note": "procedural; no observation"}} for n in PACK}
    fields["convective_risk_idx"] = {"units": FIELDS["convective_risk_idx"][0], "fill_value": None, "kind": "derived_risk",
                                     "derivation": "ITCZ, tropical-cyclone cores and warm-sector fronts of the procedural model; not lightning",
                                     "uncertainty": {"type": "not_applicable"}}
    snap = {
        "schema": SCHEMA,
        "snapshot_id": f"procedural-{hashlib.sha256(seed.encode()).hexdigest()[:12]}-{iso(start)}-{hours}h-{res_deg}deg-v3",
        "created_utc": iso(created or start),
        "data_class": "procedural",
        "provenance": {"provider": "MNO", "product": "PROCEDURAL seasonal climatology with evolving storms (not real weather)",
                       "product_version": f"{VERSION} (sea-ice extent: NSIDC G02135 v4.0 2016-2025 monthly medians)",
                       "licence": "same as MNO source", "attribution": "SEST-DEV", "source_url": None, "downloaded_utc": None,
                       "source_time_utc": None, "forecast_issue_utc": None, "seed": seed},
        "campaign_mapping": {"mode": "procedural", "offset_seconds": 0, "campaign_start_utc": iso(start),
                             "statement": "Procedural weather generated for the campaign; not a forecast of any real date."},
        "grid": grid.to_dict(),
        "fields": fields,
        "times": times,
        "integrity": {},
    }
    return seal(snap)
