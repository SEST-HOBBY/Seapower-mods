"""Seeded procedural weather: the offline fallback for any campaign date. BUILD-TESTED.

PROCEDURAL, NOT REAL WEATHER. Version 7 ("mno.env.procedural.7"; v6 added land and coast, v7 land
rain: continental lows, summer land storms, southern monsoons, wet and dry spells) builds each frame from the
parts below. v5 answers a 38-point independent critique of v4 (storm-track rain 3-5x too high
and the tropics too dry, storm tracks and the Southern Ocean westerlies about 10 degrees too far
equatorward, no monsoon winds, tropical cyclones re-intensifying after crossing land, waves
under pack ice, Arctic temperatures, regional sea ice in the wrong seas, a noise seam at 25
degrees, strictly periodic background variability).

1. A seasonal sea-level-pressure climatology: equatorial trough following the ITCZ,
   subtropical highs near 30 degrees, subpolar lows near 62-65 degrees (the Southern Ocean
   trough deepest), and the main semi-permanent centres - Aleutian and Icelandic lows (northern
   winter), Siberian high, Azores and North Pacific highs, the three southern subtropical
   highs, and the South Asian monsoon low (northern summer).
2. Synoptic systems that are BORN, MOVE and DIE, enumerated deterministically from the seed
   in 6-hour slots, so weather evolves for any length of campaign and never runs out:
   - extratropical cyclones: genesis 38-51 N (favoured off the east coasts of North America
     and Asia) and 46-58 S, deepening over about the first 1-2 days of a 5-9 day life and
     filling after, moving east 9-15 degrees of longitude a day and poleward (Atlantic lows
     2.6-4.2 degrees a day, so they mature near 55 N and die near Iceland; others 1.4-3.0), with
     a travelling ridge and clearing skies behind each; more frequent in each hemisphere's winter;
   - tropical cyclones: per basin and season (North Atlantic, East and West Pacific, North
     Indian, South Indian, Australia/South Pacific), born over the sea, moving west, then
     recurving poleward and east; they decay over land irreversibly (e-folding 0.6 day of
     cumulative land time) and beyond about 32 degrees of latitude.
3. Wind from the pressure field: geostrophic balance on the grid (f = 2 Omega sin(lat)),
   reduced to 88 % in the subtropics rising to 100 % poleward of 50 degrees, turned 11 degrees
   towards low pressure, plus sub-synoptic gustiness; equatorward of about 15 degrees it blends
   into trade winds converging on the ITCZ (calm over the warm pool), with the South Asian,
   South China Sea and Australian monsoons reversing them in season. Lows therefore turn
   anticlockwise in the north and clockwise in the south, by construction.
4. Waves: wind sea (fully developed Pierson-Moskowitz height 0.0214 U^2, scaled for limited
   duration and fetch) combined with swell radiating from active storms and a Southern Ocean
   swell belt; both are damped by sea ice (none above about 80 % concentration).
5. Cloud, rain and convective risk from the ITCZ, SPCZ, warm pool, monsoons, fronts and storm
   cores (storm rain combined in quadrature, dry most hours); marine stratocumulus off the
   subtropical west coasts; air temperature from latitude, lagged season, warm ocean currents
   and the ice surface; sea ice from the NSIDC-calibrated climatology (seaice.py), calibrated
   for the grid resolution the game samples.
6. Background variability: travelling waves whose amplitudes and phases are re-drawn every
   72 hours and blended smoothly, so weather never repeats on a fixed period; tropical
   (westward) and mid-latitude (eastward) regimes blend over 18-32 degrees.

Determinism: the only randomness is SHA-256 of (seed, label); results do not depend on the
machine, the Python version or the order frames are generated in.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import math
from functools import lru_cache

from . import landphys, seaice, visibility
from .geo import lon_delta, wrap_lon
from .grid import LatLonGrid
from .snapshot import SCHEMA, iso, pack_int16, seal

VERSION = "mno.env.procedural.7"
PACK = {  # field -> int16 scale
    "msl_pressure_hpa": 0.1, "wind_u10_ms": 0.01, "wind_v10_ms": 0.01, "cloud_fraction_pct": 0.1,
    "precip_rate_mm_h": 0.01, "air_temp_2m_c": 0.01, "wave_hs_m": 0.01, "sea_ice_conc_pct": 0.1,
    "convective_risk_idx": 0.001, "visibility_km": 0.01, "snowfall_rate_mm_h": 0.01,
}
RAD = math.pi / 180
EPOCH = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
SLOT_H = 6
OMEGA = 7.2921e-5
RHO = 1.225
DEG_M = 111_195.0
NOISE_SLOT_H = 72.0

# Tropical cyclone basins: genesis box (lat0, lat1), (lon0, lon1), monthly weight (Jan..Dec),
# storms per year (approximate long-term climatology), recurvature latitude, westward speed
# (min, span) and poleward speed before recurvature (min, span), degrees a day.
TC_BASINS = {
    "NATL": ((10, 22), (-80, -25), [0, 0, 0, 0, .1, .4, .8, 1.6, 2.4, 1.6, .5, .1], 14, 23, (4, 3), (1.0, 1.0)),
    "ENP": ((10, 18), (-120, -95), [0, 0, 0, 0, .5, 1.5, 2, 2.2, 1.8, 1, .3, 0], 16, 20, (4, 3), (1.0, 0.8)),
    "WPAC": ((8, 22), (125, 160), [.3, .2, .2, .4, .7, 1.2, 2, 2.3, 2.1, 1.7, 1, .5], 26, 21, (4, 3), (1.0, 1.0)),
    "NIO": ((8, 18), (62, 92), [.1, 0, .1, .4, 1, .6, .3, .3, .4, 1.1, 1.3, .6], 5, 18, (1.5, 1.5), (1.5, 1.0)),
    "SIO": ((-20, -8), (50, 100), [2, 2.2, 2, 1.2, .5, .1, 0, 0, .1, .3, 1, 1.8], 10, -20, (3, 3), (1.0, 1.0)),
    "SPAC": ((-20, -10), (145, 190), [2.4, 2.4, 2, 1.2, .4, .1, 0, 0, 0, .2, .8, 1.8], 10, -15, (1, 2), (1.0, 1.0)),
}
TC_LAND_EFOLD_D = 0.6
CELL_A = 1.4        # convective-cell contrast: lognormal sigma about 1.0
CELL_Z_SD = 0.92    # measured spread of the normalised cell noise over places and times (tropics and mid-latitudes)


def unit(seed: str, label: str) -> float:
    """Deterministic number in [0, 1)."""
    h = hashlib.sha256(f"{seed}|{label}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64


def _hours(t: dt.datetime) -> float:
    return (t - EPOCH).total_seconds() / 3600.0


def smoothstep(a: float, b: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


TROPICAL_YEAR_D = 365.2422
SEASON_REF = dt.datetime(2000, 1, 15, tzinfo=dt.timezone.utc)  # a mid-January reference


def _season(t: dt.datetime, lag_days: float = 0.0) -> float:
    """+1 at the northern winter peak (mid January), -1 at the northern summer peak (mid July).
    Continuous across year boundaries (no jump on 1 January). lag_days delays the cycle, as
    the ocean-coupled features (ITCZ, pressure centres, sea temperature) lag the sun by about
    six weeks."""
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
    """Seasonal climatological sea-level pressure, hPa (smooth analytic fit, not data). The
    passing storms supply the rest of the subpolar troughs."""
    nh_winter = 0.5 + 0.5 * season       # 1 in January, 0 in July
    sh_winter = 1.0 - nh_winter
    a = abs(lat)
    winter = nh_winter if lat >= 0 else sh_winter
    p = 1012.0
    phi_sub = 30.0 + 4.0 * (1 - winter)
    ridge = (5.0 + 3.0 * (1 - nh_winter)) if lat >= 0 else (3.5 + 2.5 * sh_winter)
    p += ridge * math.exp(-((a - phi_sub) / 11.0) ** 2)
    p -= 4.0 * math.exp(-((lat - itcz_lat(lon, season)) / 7.0) ** 2)
    if lat < 0:
        p -= (18.0 + 3.0 * sh_winter) * math.exp(-((lat + 63.0) / 11.0) ** 2)
    else:
        p -= (4.0 + 5.0 * nh_winter) * math.exp(-((lat - 62.0) / 9.0) ** 2)
    feats = [  # (lat, lon, amplitude hPa, lat scale, lon scale)
        (54, 180, -3 * nh_winter, 9, 30),             # Aleutian low (time-mean of passing storms: mostly supplied by them)
        (63, -30, -7 * nh_winter, 8, 28),             # Icelandic low (likewise)
        (52, 95, 14 * nh_winter, 12, 35),             # Siberian high (northern winter)
        (36, -35, 5 + 5 * (1 - nh_winter), 9, 28),    # Azores high
        (36, -150, 3 + 7 * (1 - nh_winter), 9, 32),   # North Pacific high
        (28, 72, -9 * (1 - nh_winter), 10, 25),       # South Asian monsoon low
        (-29, -12, 4 + 2 * sh_winter, 8, 25),         # South Atlantic high
        (-31, 78, 4 + 2 * sh_winter, 8, 30),          # South Indian high
        (-32, -100, 4 + 2 * sh_winter, 8, 32),        # South Pacific high
    ]
    for la, lo, amp, sy, sx in feats:
        if amp:
            p += amp * math.exp(-((lat - la) / sy) ** 2 - (lon_delta(lon, lo) / sx) ** 2)
    return p


@lru_cache(maxsize=1 << 16)
def _continental(seed: str, slot: int, hemi: int, tag: str, winter: float):
    """Lows that form over or next to land: lee cyclogenesis (Colorado/Alberta, Patagonia), Gulf
    coast and Mediterranean (Genoa) lows in winter, East Asian (Mongolia, Yangtze) and European
    lows. Smaller and shorter-lived than the ocean storms; they carry rain over the continents."""
    rate = (0.13 + 0.05 * winter) if hemi > 0 else (0.07 + 0.03 * winter)
    if unit(seed, tag + ".p") >= rate:
        return None
    u = lambda s: unit(seed, f"{tag}.{s}")  # noqa: E731
    r = u("where")
    if hemi > 0:
        if r < 0.32:
            lat0, lon0 = 36 + 14 * u("lat"), -110 + 10 * u("lon")      # Colorado / Alberta lee lows
        elif r < 0.45:
            if u("gw") > 0.25 + 0.75 * winter:
                return None
            lat0, lon0 = 26 + 6 * u("lat"), -100 + 12 * u("lon")       # Texas / Gulf coast lows (winter)
        elif r < 0.72:
            lat0, lon0 = 28 + 17 * u("lat"), 100 + 22 * u("lon")       # East Asia: Mongolia, Yangtze (Meiyu)
        elif r < 0.86:
            if u("med") > 0.3 + 0.7 * winter:
                return None
            lat0, lon0 = 37 + 7 * u("lat"), 0 + 25 * u("lon")          # Mediterranean (Genoa) lows, winter
        else:
            return None  # Europe is fed by the Atlantic and Mediterranean lows
        vlat = 0.8 + 1.0 * u("vlat")
    else:
        if r < 0.45:
            lat0, lon0 = -(35 + 10 * u("lat")), -70 + 8 * u("lon")      # Patagonian lee lows
        elif r < 0.7:
            lat0, lon0 = -(32 + 6 * u("lat")), 12 + 18 * u("lon")       # south-west Africa / Cape cut-off lows
        else:
            lat0, lon0 = -(32 + 6 * u("lat")), 112 + 35 * u("lon")      # southern Australia
        vlat = -(0.8 + 1.0 * u("vlat"))
    return {"kind": "extratropical", "t0": slot * SLOT_H, "lat0": lat0, "lon0": lon0,
            "life_d": 3.0 + 3.0 * u("life"), "deficit": 8 + 14 * u("deficit") + 3 * winter,
            "radius": 7.0 + 5.0 * u("radius"), "vlon": 8 + 5 * u("vlon"), "vlat": vlat}


def _extratropical(seed: str, slot: int, hemi: int, k: int, season: float):
    tag = f"x{hemi}.{slot}.{k}"
    winter = (0.5 + 0.5 * season) if hemi > 0 else (0.5 - 0.5 * season)
    if k == 2:
        return _continental(seed, slot, hemi, tag, winter)
    rate = (0.11 + 0.06 * winter) if hemi > 0 else (0.17 + 0.04 * winter)  # per 6 h per candidate
    if unit(seed, tag + ".p") >= rate:
        return None
    u = lambda s: unit(seed, f"{tag}.{s}")  # noqa: E731
    if hemi > 0:
        r = u("where")
        if r < 0.4:      # off North America: the Atlantic track runs Hatteras -> Iceland
            lon0, vlat = -78 + 30 * u("lon"), 2.6 + 1.6 * u("vlat")
        elif r < 0.8:    # off Asia: the Pacific track ends in the Aleutian low
            lon0, vlat = 125 + 40 * u("lon"), 1.6 + 1.4 * u("vlat")
        else:
            lon0, vlat = -180 + 360 * u("lon"), 1.6 + 1.4 * u("vlat")
        lat0 = 38 + 10 * u("lat") + 3 * (1 - winter)
        deficit = 12 + 21 * u("deficit") + 4 * winter
    else:
        lon0, lat0, vlat = -180 + 360 * u("lon"), -(46 + 12 * u("lat")), -(1.4 + 1.4 * u("vlat"))
        deficit = 14 + 26 * u("deficit") + 5 * winter
    return {"kind": "extratropical", "t0": slot * SLOT_H, "lat0": lat0, "lon0": lon0,
            "life_d": 5.0 + 4.0 * u("life"), "deficit": deficit,
            "radius": 10.0 + 7.0 * u("radius"), "vlon": 9 + 6 * u("vlon"), "vlat": vlat}


@lru_cache(maxsize=1 << 16)
def _tropical(seed: str, slot: int, basin: str, month: int):
    (la0, la1), (lo0, lo1), weights, per_year, recurve, (vw0, vw1), (vp0, vp1) = TC_BASINS[basin]
    w = weights[month - 1] / (sum(weights) / 12.0)
    rate = per_year / (365.25 * 24 / SLOT_H) * w
    tag = f"t{basin}.{slot}"
    if rate <= 0 or unit(seed, tag + ".p") >= rate:
        return None
    u = lambda s: unit(seed, f"{tag}.{s}")  # noqa: E731
    lat0 = la0 + (la1 - la0) * u("lat")
    lon0 = wrap_lon(lo0 + (lo1 - lo0) * u("lon"))
    if _land().is_land(lat0, lon0):
        return None  # tropical cyclones form over warm sea
    return {"kind": "tropical", "basin": basin, "t0": slot * SLOT_H, "lat0": lat0, "lon0": lon0,
            "life_d": 5 + 5 * u("life"), "deficit": 15 + 50 * u("deficit") ** 1.5, "radius": 2.5 + 2.0 * u("radius"),
            "vwest": vw0 + vw1 * u("vw"), "vpole": vp0 + vp1 * u("vp"), "recurve": recurve}


def _track(s: dict, age_d: float) -> tuple[float, float]:
    """(lat, lon) of a tropical cyclone at an age in days (no intensity)."""
    sign = 1 if s["recurve"] > 0 else -1
    t_rec = max(0.0, (abs(s["recurve"]) - abs(s["lat0"])) / s["vpole"])
    if age_d <= t_rec:
        lat = s["lat0"] + sign * s["vpole"] * age_d
        lon = s["lon0"] - s["vwest"] * age_d
    else:
        a2 = age_d - t_rec
        lat = s["lat0"] + sign * (s["vpole"] * t_rec + 2.6 * s["vpole"] * a2)
        lon = s["lon0"] - s["vwest"] * t_rec + (2.0 * a2 + 1.2 * a2 * a2)
    return lat, wrap_lon(lon)


def _position(s: dict, age_d: float) -> tuple[float, float, float]:
    """(lat, lon, intensity 0..1) of a storm at an age in days, before any land decay."""
    x = age_d / s["life_d"]
    if not 0.0 <= x <= 1.0:
        return 0.0, 0.0, 0.0
    if s["kind"] == "extratropical":
        lat = s["lat0"] + s["vlat"] * age_d * (1 - 0.3 * x)  # poleward drift slows as the low occludes
        lat = max(-72.0, min(72.0, lat))
        lon = wrap_lon(s["lon0"] + s["vlon"] * age_d * min(2.5, 1 / max(0.35, math.cos(lat * RAD))) * 0.7)
        inten = math.sin(math.pi * x ** 0.85) * smoothstep(0.0, 0.2, x)  # deepens over 1-2 days, then fills
        return lat, lon, inten
    lat, lon = _track(s, age_d)
    inten = math.sin(math.pi * min(1.0, x ** 0.8)) * smoothstep(0.0, 0.2, x)
    if abs(lat) > 32:  # extratropical transition / cool water: weaken
        inten *= math.exp(-(abs(lat) - 32) / 8.0)
    return lat, lon, inten


@lru_cache(maxsize=1 << 14)
def _tc_land_flags(seed: str, slot: int, basin: str, month: int) -> tuple:
    """Over land (1) or sea (0) at the middle of each 6-hour step of a cyclone's life."""
    s = _tropical(seed, slot, basin, month)
    n = int(s["life_d"] * 4) + 2
    return tuple(1 if _land().is_land(*_track(s, (i + 0.5) * 0.25)) else 0 for i in range(n))


def _land_days(flags: tuple, age_d: float) -> float:
    """Cumulative days over land up to this age (continuous in age; never decreases)."""
    n = int(age_d / 0.25)
    done = 0.25 * sum(flags[:min(n, len(flags))])
    part = (age_d - 0.25 * n) * (flags[n] if n < len(flags) else 0)
    return done + part


def active_storms(seed: str, t: dt.datetime) -> list[dict]:
    """Every storm alive at time t, with its current position and strength."""
    h = _hours(t)
    now_slot = int(math.floor(h / SLOT_H))
    out = []
    for slot in range(now_slot - int(10 * 24 / SLOT_H), now_slot + 1):
        ts = EPOCH + dt.timedelta(hours=slot * SLOT_H)
        season = _season(ts)
        cands = [_extratropical(seed, slot, hemi, k, season) for hemi in (1, -1) for k in range(3)]
        cands += [_tropical(seed, slot, b, ts.month) for b in TC_BASINS]
        for s in cands:
            if s is None:
                continue
            age = (h - s["t0"]) / 24.0
            lat, lon, inten = _position(s, age)
            if s["kind"] == "tropical" and inten > 0.02:
                # a tropical cyclone loses its energy source over land, for good
                inten *= math.exp(-_land_days(_tc_land_flags(seed, slot, s["basin"], ts.month), age) / TC_LAND_EFOLD_D)
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


@lru_cache(maxsize=8)
def _land_nodes(grid: LatLonGrid) -> tuple:
    """Is each grid node on land (the same test seaice uses to calibrate extent)?"""
    m = _land()
    return tuple(m.is_land(max(-89.9, min(89.9, grid.lat(j))), grid.lon(i)) for j in range(grid.ny) for i in range(grid.nx))


@lru_cache(maxsize=4096)
def _noise_plan(seed: str, kind: str, hours: float) -> tuple:
    """Per-frame constants of the travelling-wave noise for both regimes (tropical waves move
    west, mid-latitude ones east). Each mode's amplitude and phase are re-drawn every 72 h and
    blended with a cosine ramp, so the field never repeats on a fixed period."""
    sf = hours / NOISE_SLOT_H
    s0 = math.floor(sf)
    b = 0.5 - 0.5 * math.cos(math.pi * (sf - s0))
    plan = []
    for regime, base in (("t", -6.0), ("m", 9.0)):
        modes = []
        for k in range(4):
            lab = f"n.{kind}.{regime}.{k}"
            a = unit(seed, lab + ".a") * 2 * math.pi
            wn = 2 + 2 * k + int(4 * unit(seed, lab + ".w"))
            speed = base * (0.7 + 0.6 * unit(seed, lab + ".s"))
            amp0, ph0 = 0.35 + 1.3 * unit(seed, f"{lab}.A{s0}"), 2 * math.pi * unit(seed, f"{lab}.P{s0}")
            amp1, ph1 = 0.35 + 1.3 * unit(seed, f"{lab}.A{s0 + 1}"), 2 * math.pi * unit(seed, f"{lab}.P{s0 + 1}")
            shift = a - wn * speed * hours / 24.0 * RAD
            modes.append((wn * RAD, shift + ph0, (1 - b) * amp0 / 4, shift + ph1, b * amp1 / 4, (1.7 + k) * 2 * RAD))
        plan.append(tuple(modes))
    return tuple(plan)


def _waves_noise(seed: str, lat: float, lon: float, hours: float, kind: str) -> float:
    """Deterministic smooth variability, zero mean, standard deviation about 0.35 (|v| < 1.4).
    Tropical and mid-latitude regimes blend over 18-32 degrees (no seam)."""
    trop, mid = _noise_plan(seed, kind, hours)
    bm = smoothstep(18.0, 32.0, abs(lat))
    v = 0.0
    for weight, modes in ((1.0 - bm, trop), (bm, mid)):
        if weight <= 0.0:
            continue
        acc = 0.0
        for wn, p0, a0, p1, a1, tilt in modes:
            th = wn * lon + tilt * lat
            acc += a0 * math.sin(th + p0) + a1 * math.sin(th + p1)
        v += weight * acc
    return v


def _soft_cap(c: float) -> float:
    """Cloud cover saturates gradually above 70 % instead of clipping at 100 %."""
    return c if c <= 70.0 else 70.0 + 30.0 * (1.0 - math.exp(-(c - 70.0) / 30.0))


def _frame(seed: str, t: dt.datetime, grid: LatLonGrid, edges: dict, tick: float) -> dict:
    season = _season(t)
    lag = _season(t, 42.0)  # ocean-coupled features lag the sun by about six weeks
    mons = _season(t, 20.0)  # monsoons
    storms = active_storms(seed, t)
    hrs = _hours(t)
    nh_winter = 0.5 + 0.5 * season
    sh_summer = 0.5 + 0.5 * season
    m_n, m_s = max(0.0, -mons) ** 0.8, max(0.0, mons) ** 0.8
    landf = _land_fraction(grid)
    nh_summer = 1.0 - nh_winter
    land_phase = _season(t, 10.0)
    doy = t.timetuple().tm_yday + t.hour / 24.0
    mfrac = t.month + (t.day - 1) / 30.0
    meiyu = max(0.0, 1.0 - abs(mfrac - 6.6) / 1.2)  # mid-June to late July
    sh_winter = 0.5 - 0.5 * season
    P, BG, CL, PR, CV, SW, TA, TCW, AR = [], [], [], [], [], [], [], [], []
    for j in range(grid.ny):
        lat = grid.lat(j)
        alat = abs(lat)
        for i in range(grid.nx):
            lon = grid.lon(i)
            bg = background_pressure(lat, lon, lag)
            noise_p = _waves_noise(seed, lat, lon, hrs, "p")
            noise_c = _waves_noise(seed, lat, lon, hrs, "c")
            lf_k = landf[j * grid.nx + i]
            # over Africa and South America the rain belt swings much further south in southern
            # summer than over the ocean; it also shifts south over the Mozambique Channel
            w_cont = min(1.0, landphys.soft_box(0.0, lon, -90, 90, -15, 45, 10) + landphys.soft_box(0.0, lon, -90, 90, -75, -35, 10)
                         + landphys.soft_box(0.0, lon, -90, 90, 112, 152, 8))  # Africa, South America, Australia
            itcz_r = itcz_lat(lon, lag) + lf_k * w_cont * (-14.0 * m_s - 1.0 * m_n) - 10.0 * m_s * math.exp(-(lon_delta(lon, 40) / 10) ** 2)
            itcz = math.exp(-((lat - itcz_r) / (5.0 + lf_k * w_cont * (1.5 + 3.0 * m_s))) ** 2)  # broader over the southern-summer continents
            p = bg + 3.0 * noise_p * min(1.0, alat / 25 + 0.3)
            arid = landphys.aridity(lat, lon, landf[j * grid.nx + i], nh_summer)
            horn = landphys.horn_dry(lat, lon)
            dry = (1.0 - horn) * (1.0 - 0.95 * arid)   # deserts, Red Sea / Gulf, Horn of Africa: no background rain
            cloud = 54 + 28 * itcz + 24 * (1.0 - 0.5 * arid) * noise_c
            rain = 0.42 * itcz ** 1.5 * (1 + 0.8 * noise_c)
            conv = 0.7 * itcz * (0.7 + 0.3 * noise_c)
            # warm pool, SPCZ and monsoon rain (mm/h); trade-wind showers
            lon_e = lon % 360.0
            spcz_lat = -5.0 - 25.0 * (lon_e - 150.0) / 70.0
            tropical_rain = (0.24 * math.exp(-((lat - 3) / 10) ** 2 - (lon_delta(lon, 130) / 35) ** 2)
                             + (0.22 + 0.12 * sh_summer) * math.exp(-((lat - spcz_lat) / 5) ** 2 - ((lon_e - 185) / 38) ** 2)
                             + m_n * (0.38 * math.exp(-((lat - 16) / 6) ** 2 - (lon_delta(lon, 88) / 14) ** 2)
                                      + 0.30 * math.exp(-((lat - 14) / 5) ** 2 - (lon_delta(lon, 73) / 6) ** 2)
                                      + 0.25 * math.exp(-((lat - 15) / 7) ** 2 - (lon_delta(lon, 132) / 25) ** 2))
                             + m_s * 0.55 * math.exp(-((lat + 14) / 6) ** 2 - (lon_delta(lon, 133) / 22) ** 2)       # Australian monsoon
                             + m_s * 0.18 * math.exp(-((lat - (-15 - 0.6 * (lon + 50))) / 5) ** 2 - (lon_delta(lon, -45) / 15) ** 2)  # SACZ
                             + m_n * 0.18 * math.exp(-((lat - 26) / 4) ** 2 - (lon_delta(lon, 72) / 6) ** 2)          # Thar / Sindh fringe
                             + m_n * 0.15 * math.exp(-((lat - 21) / 5) ** 2 - (lon_delta(lon, 80) / 8) ** 2)          # central India
                             + m_n * 0.20 * math.exp(-((lat - 24) / 5) ** 2 - (lon_delta(lon, 112) / 10) ** 2)        # south China summer rains
                             + m_n * 0.12 * math.exp(-((lat - 3) / 4) ** 2 - (lon_delta(lon, 101) / 5) ** 2)          # Sumatra squalls (Malacca)
                             + 0.15 * math.exp(-(((doy - 305 + 182) % 365 - 182) / 35) ** 2 - ((lat - 3) / 5) ** 2 - (lon_delta(lon, 101) / 7) ** 2)  # Malacca inter-monsoon
                             + 0.45 * meiyu * math.exp(-((lat - (27 + 3 * (mfrac - 5.5))) / 3.5) ** 2 - (lon_delta(lon, 122) / 22) ** 2)  # Meiyu / Baiu front
                             + (0.15 * (0.5 + 0.5 * nh_summer) * math.exp(-((lat - 29) / 5) ** 2 - (lon_delta(lon, -88) / 10) ** 2)
                                + 0.10 * nh_winter * math.exp(-((lat - 31) / 6) ** 2 - (lon_delta(lon, -88) / 14) ** 2))  # Gulf of Mexico
                             + 0.18 * sh_winter * math.exp(-((lat + 35) / 4) ** 2)
                                    * (math.exp(-(lon_delta(lon, 20) / 8) ** 2) + math.exp(-(lon_delta(lon, 117) / 8) ** 2)))  # Cape, SW Australia winter
            rain += tropical_rain * (1 + 0.8 * noise_c)
            cloud += 120 * tropical_rain
            conv = max(conv, min(0.8, 1.5 * tropical_rain) * (0.7 + 0.3 * noise_c))
            if alat < 30:
                rain += 0.12 * max(0.0, noise_c + 0.2) * (1.0 - arid)
            if alat < 30 and lf_k > 0:  # tropical land away from the rain belt is dry in its dry season
                rain *= max(0.1, 1.0 - lf_k * landphys.smooth(4, 10, abs(lat - itcz_r)))
            # summer showers and thunderstorms over humid land (intermittent)
            summer_l = (0.5 - 0.5 * land_phase) if lat >= 0 else (0.5 + 0.5 * land_phase)
            land_conv = (lf_k * (1.0 - arid) * landphys.smooth(10, 25, alat) * (1 - landphys.smooth(60, 70, alat))
                         * summer_l ** 1.5 * 0.19 * max(0.0, noise_c + 0.12) / 0.45)
            rain += land_conv
            conv = max(conv, min(0.9, 4.0 * land_conv))
            cloud += 60 * land_conv
            rain *= dry
            conv *= dry
            rain += 0.22 * m_n * lf_k * math.exp(-((lat - 10) / 4) ** 2 - (lon_delta(lon, 38) / 3) ** 2)  # Ethiopian highlands (kiremt)
            # convective rain comes in wet and dry spells: a moving lognormal multiplier with mean 1
            # (two crossing, sheared noises on scales of hundreds to a few thousand km, lasting days), so
            # the climate mean is kept while a place sees dry days and wet days. Individual storm cells
            # are far below the grid and are not represented. Thunderstorm risk follows the wet spells.
            zc = (_waves_noise(seed, lat, 4 * lon + 3 * lat, hrs, "rc") + _waves_noise(seed, lat, 7 * lon - 5 * lat, hrs, "rd")) / (math.sqrt(2.0) * 0.33)
            cellf = (math.exp(CELL_A * zc - 0.5 * (CELL_A * CELL_Z_SD) ** 2)
                     / (1.15 - 0.2 * math.exp(-((alat - 22) / 6) ** 2)))  # measured mean by latitude: the multiplier averages 1
            rain *= cellf
            conv *= min(1.6, 0.5 + 0.5 * cellf)
            cloud -= 25 * horn * (itcz + 0.5)
            cloud -= 12 * math.exp(-((alat - 26) / 9) ** 2)        # subtropical subsidence
            cloud += 22 * math.exp(-((alat - 60) / 12) ** 2)       # subpolar oceans
            sc = 0.0
            for la, lo in ((-20, -90), (-18, 5), (25, -125), (20, -22)):  # marine stratocumulus decks
                sc += 40 * math.exp(-((lat - la) / 10) ** 2 - (lon_delta(lon, lo) / 30) ** 2)
            cloud += sc * (1.0 - 0.8 * landf[j * grid.nx + i])
            cloud -= 20 * arid * (1.0 - min(1.0, sc / 15.0))  # desert skies are mostly clear
            sh_winter = 0.5 - 0.5 * season
            belt = (2.0 + 0.9 * sh_winter) if lat < 0 else (0.5 + 0.8 * nh_winter)
            if m_n > 0:  # south-west monsoon swell in the Arabian Sea
                belt_m = 2.2 * m_n * math.exp(-((lat - 13) / 7) ** 2 - (lon_delta(lon, 62) / 12) ** 2)
            else:
                belt_m = 0.0
            swell = 0.5 + belt * math.exp(-((alat - 50) / 15) ** 2) + 1.0 * math.exp(-((lat + 5) / 25) ** 2) + belt_m
            ssq = 0.0
            temp_anom = 1.2 * noise_p
            dsq = rsq = ridge = tcw = 0.0
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
                    tcw = max(tcw, min(1.0, 1.5 * inten) * math.exp(-0.5 * (d / (2.0 * r)) ** 2))
                else:
                    hemi = 1 if st["lat"] > 0 else -1
                    east = lon_delta(lon, st["lon"]) * math.cos(lat * RAD)
                    equatorward = (st["lat"] - lat) * hemi
                    ang = math.atan2(equatorward, east)
                    side = 0.5 + 0.5 * math.sin(ang + 0.6)            # fronts on the equatorward-east side
                    front = math.exp(-((d - 0.8 * r) / (0.2 * r)) ** 2) * side
                    rfront = math.exp(-((d - 0.8 * r) / (0.1 * r)) ** 2) * side * side  # the rain band is narrower than the cloud band
                    # travelling ridge behind (west of) each low, with clearing skies
                    rlat = st["lat"] - hemi * 0.2 * r
                    rlon = st["lon"] - 1.4 * r / max(0.35, math.cos(st["lat"] * RAD))
                    rshape = math.exp(-0.5 * (_dist_deg(lat, lon, rlat, rlon) / (0.6 * r)) ** 2)
                    ridge += 0.3 * st["deficit"] * inten * rshape
                    cloud += inten * (45 * math.exp(-0.5 * (d / r) ** 2) + 25 * front - 40 * rshape)
                    rcore = math.exp(-0.5 * (d / (0.22 * r)) ** 2)
                    rsq += (inten * (1.6 * rcore + 1.5 * rfront) * (1.0 - 0.4 * landf[j * grid.nx + i])) ** 2
                    if abs(st["lat"]) < 48:
                        conv = max(conv, 0.55 * inten * front)
                    # warm sector ahead (east), cold air behind (west)
                    temp_anom += inten * 3.5 * math.tanh(east / max(1.0, r)) * math.exp(-0.5 * (d / (1.2 * r)) ** 2)
                ssq += (2.0 * inten * st["deficit"] / 40.0 * math.exp(-d / 15.0)) ** 2
            p -= math.sqrt(dsq)  # quadratic sum: overlapping lows deepen each other far less than linearly
            p += ridge
            swell += math.sqrt(ssq)  # storm swell trains combine in quadrature
            rain += max(0.0, math.sqrt(rsq) - 0.14)  # storm rain in quadrature; light amounts dry out (rain ~30 % of hours)
            P.append(p)
            BG.append(bg)
            CL.append(max(0.0, min(100.0, _soft_cap(cloud))))
            PR.append(max(0.0, min(30.0, rain)))
            CV.append(max(0.0, min(1.0, conv)))
            SW.append(min(6.0, swell) * (1.0 - 0.85 * landf[j * grid.nx + i]))
            TA.append(temp_anom)
            TCW.append(tcw)
            AR.append(arid)
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
    land_nodes = _land_nodes(grid)
    U, V = _winds(grid, P, lag, seed, hrs, mons, TCW, t=t, landf=landf, land_nodes=land_nodes)
    ICE = []
    for j in range(grid.ny):
        lat = grid.lat(j)
        for i in range(grid.nx):
            k = j * grid.nx + i
            wobble = 0.35 * math.sin(tick * 0.4 + grid.lon(i) * RAD * 2)
            ICE.append(0.0 if land_nodes[k] else seaice.ice_at(lat - (wobble if lat < 0 else -wobble), grid.lon(i), edges))
    # Pole rows are single points: scalars averaged, wind calm.
    for j in (0, grid.ny - 1):
        if abs(grid.lat(j)) >= 90 - 1e-9:
            row = slice(j * grid.nx, (j + 1) * grid.nx)
            for arr in (P, CL, PR, CV, SW, TA, ICE):
                m = sum(arr[row]) / grid.nx
                arr[row] = [m] * grid.nx
            U[row] = [0.0] * grid.nx
            V[row] = [0.0] * grid.nx
    out = {n: [] for n in PACK}
    land_phase = _season(t, 10.0)  # land responds to the sun within about ten days
    for j in range(grid.ny):
        lat = grid.lat(j)
        alat = abs(lat)
        winter_land = (0.5 + 0.5 * land_phase) if lat >= 0 else (0.5 - 0.5 * land_phase)
        if lat >= 0:
            winter_here = 0.5 + 0.5 * lag
            amp = 9.0 + 21.0 * max(0.0, min(1.0, (lat - 55) / 25))
        else:
            winter_here = 0.5 - 0.5 * lag
            amp = 9.0 + 12.0 * max(0.0, min(1.0, (alat - 50) / 20)) if lag < 0 else 9.0  # cold winters over the pack, mild ocean summers
        base_t = -16 + 44 * max(0.0, math.cos(lat * RAD)) ** 1.3 - amp * (winter_here - 0.5) * min(1.0, alat / 50)
        for i in range(grid.nx):
            k = j * grid.nx + i
            lon = grid.lon(i)
            ice = ICE[k]
            spd = math.hypot(U[k], V[k])
            fetch = 1.0 - 0.6 * landf[k]
            damp = max(0.0, 1.0 - ice / 80.0)                  # pack ice damps wind sea and swell
            wind_sea = 0.0214 * spd * spd * 0.8 * fetch * damp  # limited duration and fetch
            hs = min(13.0, math.hypot(wind_sea, SW[k] * math.sqrt(damp)))
            ocean_t = (5.0 * math.exp(-((lat - 52) / 12) ** 2 - (lon_delta(lon, -25) / 30) ** 2)   # North Atlantic Drift
                       + 3.0 * math.exp(-((lat - 36) / 8) ** 2 - (lon_delta(lon, 145) / 15) ** 2)  # Kuroshio
                       + (2.0 + 6.0 * (1 - (0.5 + 0.5 * lag))) * math.exp(-((lat - 25) / 8) ** 2 - (lon_delta(lon, 55) / 15) ** 2)  # Arabian Sea / Gulf
                       + 2.0 * math.exp(-((lat - 8) / 12) ** 2 - (lon_delta(lon, 140) / 30) ** 2))  # warm pool
            temp = base_t + ocean_t + TA[k]
            if land_nodes[k]:
                temp += landphys.land_temp_delta(lat, lon, landf[k], winter_land, AR[k])
            if ice >= 15.0:
                melt = (lag < 0) if lat >= 0 else (lag > 0)
                if melt:  # a melting ice surface holds the air near 0 C
                    temp = max(-1.5, min(1.0, temp))
            elif not land_nodes[k] and alat > 40:
                temp = max(temp, -6.0)  # open water colder than this would freeze
            out["msl_pressure_hpa"].append(min(1060.0, max(920.0, P[k])))
            out["wind_u10_ms"].append(U[k])
            out["wind_v10_ms"].append(V[k])
            out["cloud_fraction_pct"].append(CL[k])
            out["precip_rate_mm_h"].append(PR[k])
            out["air_temp_2m_c"].append(max(-60.0, min(45.0, temp)))
            out["wave_hs_m"].append(hs if ice >= 15.0 else max(0.1, hs))
            out["sea_ice_conc_pct"].append(min(100.0, ice))
            out["convective_risk_idx"].append(CV[k])
            out["snowfall_rate_mm_h"].append(PR[k] * max(0.0, min(1.0, (1.5 - temp) / 3.0)))
            out["visibility_km"].append(visibility.visibility_km(
                lat=lat, lon=lon, t=t, wind_ms=spd, v_ms=V[k], rain_mm_h=PR[k], temp_c=temp, ice_pct=ice,
                land=land_nodes[k],
                # two crossing, sheared components: fog banks are patches, not meridional stripes
                fog_noise=(_waves_noise(seed, lat, 3 * lon + 5 * lat, hrs, "f") + _waves_noise(seed, lat, 5 * lon - 6 * lat, hrs, "g")) / math.sqrt(2.0),
                dust_noise=_waves_noise(seed, lat, 4 * lon, hrs, "d")))
    # Sea-surface fields on land nodes carry the neighbouring sea value, so a ship sampled
    # between a land and a sea node does not see land-damped waves or ice-free coasts.
    for name in ("wave_hs_m", "sea_ice_conc_pct"):
        out[name] = sea_fill(grid, out[name], land_nodes)
    return out


@lru_cache(maxsize=8)
def _fill_plan(grid: LatLonGrid, land_nodes: tuple) -> tuple:
    """For each land node: the sea nodes in the first ring of neighbours that has any (rings 1
    and 2), else none. Shared with seaice.extent_on_grid so the extent calibration matches."""
    return seaice.fill_plan(grid.nx, grid.ny, land_nodes, grid.global_lon)


def sea_fill(grid: LatLonGrid, values: list, land_nodes: tuple) -> list:
    plan = _fill_plan(grid, land_nodes)
    out = list(values)
    for k, nb in enumerate(plan):
        if nb is not None:
            out[k] = sum(values[q] for q in nb) / len(nb) if nb else 0.0
    return out


def _winds(grid: LatLonGrid, P: list, season: float, seed: str = "", hrs: float = 0.0,
           mons: float | None = None, tcw: list | None = None, t: dt.datetime | None = None,
           landf: tuple | None = None, land_nodes: tuple | None = None) -> tuple[list, list]:
    """10 m wind from the pressure grid: geostrophic, reduced to 88 % in the subtropics rising
    to 100 % poleward of 50 degrees (a 4-degree grid already smooths the gradients), turned 11
    degrees towards low pressure, with sub-synoptic gustiness, softly capped (a coarse-grid
    geostrophic wind overstates winds in tight lows) and tapered to calm at the poles. Near the
    equator it blends into trade winds (weak over the warm pool) with travelling easterly-wave
    variability, reversed by the monsoons in season; inside tropical cyclones the pressure
    field's own circulation wins."""
    U, V = [0.0] * len(P), [0.0] * len(P)
    nx, ny = grid.nx, grid.ny
    mons = season if mons is None else mons
    doy = (t.timetuple().tm_yday + t.hour / 24.0) if t is not None else None
    nh_summer = 0.5 - 0.5 * _season(t) if t is not None else 0.5
    m_n, m_s = max(0.0, -mons) ** 0.8, max(0.0, mons) ** 0.8
    for j in range(ny):
        lat = grid.lat(j)
        alat = abs(lat)
        jn, js = min(j + 1, ny - 1), max(j - 1, 0)
        dy = (grid.lat(jn) - grid.lat(js)) * DEG_M
        coslat = max(0.05, math.cos(lat * RAD))
        dx = 2 * grid.lon_step * DEG_M * coslat
        f = 2 * OMEGA * math.sin(lat * RAD)
        fac = (0.88 + 0.12 * max(0.0, min(1.0, (alat - 35) / 15))) * min(1.0, (90 - alat) / 8)
        turn = 11 * RAD * (1 if lat >= 0 else -1)
        ct, sn = math.cos(turn), math.sin(turn)
        w_geo = smoothstep(11.0, 23.0, alat)
        gust = smoothstep(8.0, 20.0, alat)
        for i in range(nx):
            ie = (i + 1) % nx if grid.global_lon else min(i + 1, nx - 1)
            iw = (i - 1) % nx if grid.global_lon else max(i - 1, 0)
            dpdx = (P[j * nx + ie] - P[j * nx + iw]) * 100.0 / dx
            dpdy = (P[jn * nx + i] - P[js * nx + i]) * 100.0 / dy if dy else 0.0
            ug, vg = 0.0, 0.0
            if alat >= 5:
                ug, vg = -dpdy / (RHO * f), dpdx / (RHO * f)
            us = fac * (ug * ct - vg * sn)
            vs = fac * (ug * sn + vg * ct)
            lon = grid.lon(i)
            if seed and gust > 0:
                g = gust * (7.5 + 4.0 * math.exp(-((alat - 30) / 8) ** 2))
                us += g * _waves_noise(seed, lat, lon, hrs, "wu")
                vs += g * _waves_noise(seed, lat, lon, hrs, "wv")
            itcz = itcz_lat(lon, season)
            ew = _waves_noise(seed, lat, lon, hrs, "w") if seed else 0.0
            walker = 1.0 - 0.75 * math.exp(-(lon_delta(lon, 125) / 32) ** 2)  # weak winds over the warm pool
            dl = abs(lat - itcz)
            trade_u = -7.0 * math.exp(-((dl - 16) / 13) ** 2) * walker + 3.0 * ew
            trade_v = 2.5 * math.tanh((itcz - lat) / 6.0) * walker + 2.0 * ew
            w = w_geo
            if tcw:
                w = max(w, tcw[j * nx + i])
            u = w * us + (1 - w) * trade_u
            v = w * vs + (1 - w) * trade_v
            # monsoons: blend towards the seasonal monsoon flow (south-west over the Arabian Sea,
            # Bay of Bengal and South China Sea in northern summer; north-west over northern
            # Australia in southern summer)
            mw, mu, mv = 0.0, 0.0, 0.0
            if m_n > 0:
                a = 1.4 * m_n * math.exp(-((lat - 12) / 9) ** 2 - (lon_delta(lon, 75) / 28) ** 2)
                b = 0.8 * m_n * math.exp(-((lat - 13) / 7) ** 2 - (lon_delta(lon, 115) / 14) ** 2)
                if a >= b and a > 0:
                    mw = a
                    mu = 7.5 + 4.5 * math.exp(-((lat - 11) / 5) ** 2 - (lon_delta(lon, 62) / 12) ** 2)
                    mv = 3.0 + 4.0 * math.exp(-((lat - 6) / 6) ** 2 - (lon_delta(lon, 54) / 9) ** 2)
                elif b > 0:
                    mw, mu, mv = b, 5.5, 3.0
            if m_s > 0:
                c = 1.4 * m_s * math.exp(-((lat + 10) / 6) ** 2 - (lon_delta(lon, 128) / 24) ** 2)
                if c > mw:
                    mw, mu, mv = c, 5.5, -2.0
            if mw > 0:
                mw = min(1.0, mw) * (1 - (tcw[j * nx + i] if tcw else 0.0))
                u = (1 - mw) * u + mw * (mu + 1.5 * ew)
                v = (1 - mw) * v + mw * (mv + 1.0 * ew)
            if doy is not None and seed:
                rw, ru, rv = landphys.regional_wind(
                    lat, lon, doy, nh_summer, _waves_noise(seed, lat, lon, hrs, "ms"),
                    _waves_noise(seed, lat, lon, hrs, "sh"), _waves_noise(seed, lat, lon, hrs, "et"), ew)
                if rw > 0:
                    rw *= 1 - (tcw[j * nx + i] if tcw else 0.0)
                    u = (1 - rw) * u + rw * ru
                    v = (1 - rw) * v + rw * rv
            else:
                rw = 0.0
            if land_nodes is not None and land_nodes[j * nx + i]:
                # land is rougher: lighter 10 m wind, except where a regional sea wind (a narrow sea
                # the grid cannot resolve: Red Sea, Aegean, Gulf, Taiwan Strait) sets the value
                r = landphys.roughness(landf[j * nx + i], lat)
                r = 1.0 - (1.0 - r) * (1.0 - min(1.0, rw / 0.3))
                u, v = u * r, v * r
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
        edges = seaice.edges_on(t, res=res_deg)
        cols = _frame(seed, t, grid, edges, _hours(t) / 6.0)
        times.append({"valid_utc": iso(t), "lead_hours": None,
                      "values": {n: pack_int16(cols[n], PACK[n]) for n in PACK}})
    from .snapshot import FIELDS
    fields = {n: {"units": FIELDS[n][0], "fill_value": None, "kind": "procedural",
                  "uncertainty": {"type": "not_applicable", "note": "procedural; no observation"}} for n in PACK}
    fields["convective_risk_idx"] = {"units": FIELDS["convective_risk_idx"][0], "fill_value": None, "kind": "derived_risk",
                                     "derivation": "ITCZ, tropical-cyclone cores and warm-sector fronts of the procedural model; not lightning",
                                     "uncertainty": {"type": "not_applicable"}}
    fields["visibility_km"] = {"units": FIELDS["visibility_km"][0], "fill_value": None, "kind": "procedural",
                               "derivation": "visibility.py: climatological sea-fog frequency (after Dorman et al., ICOADS ship fog) "
                                             "modulated by wind, rain and warm advection; rain/snow, dust haze and sea smoke",
                               "uncertainty": {"type": "not_applicable"}}
    snap = {
        "schema": SCHEMA,
        "snapshot_id": f"procedural-{hashlib.sha256(seed.encode()).hexdigest()[:12]}-{iso(start)}-{hours}h-{step_hours}hstep-{res_deg}deg-v{VERSION.rsplit('.', 1)[-1]}",
        "created_utc": iso(created or start),
        "data_class": "procedural",
        "provenance": {"provider": "MNO", "product": "PROCEDURAL seasonal climatology with evolving storms (not real weather)",
                       "product_version": f"{VERSION} (sea-ice extent: NSIDC G02135 v4.0 2016-2025 monthly medians, calibrated for a {res_deg}-degree grid)",
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
