"""Seeded procedural weather: the offline fallback for any campaign date. BUILD-TESTED.

PROCEDURAL, NOT REAL WEATHER. Version 3 ("mno.env.procedural.3") builds each frame from:

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

from . import seaice
from .geo import lon_delta, wrap_lon
from .grid import LatLonGrid
from .snapshot import SCHEMA, iso, pack_int16, seal

VERSION = "mno.env.procedural.3"
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


def _season(t: dt.datetime) -> float:
    """+1 at the northern winter peak (mid January), -1 at the northern summer peak (mid July)."""
    doy = (t - dt.datetime(t.year, 1, 1, tzinfo=t.tzinfo)).total_seconds() / 86400.0
    return math.cos(2 * math.pi * (doy - 15) / 365.25)


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
        p -= (24.0 + 6.0 * sh_winter) * math.exp(-((lat + 65.0) / 11.0) ** 2)
    else:
        p -= (4.0 + 6.0 * nh_winter) * math.exp(-((lat - 62.0) / 9.0) ** 2)
    feats = [  # (lat, lon, amplitude hPa, lat scale, lon scale)
        (52, 180, -12 * nh_winter, 9, 30),            # Aleutian low
        (61, -32, -14 * nh_winter, 9, 30),            # Icelandic low
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
        lat0 = 36 + 13 * u("lat") + 4 * (1 - winter)
    else:
        lon0, lat0 = -180 + 360 * u("lon"), -(38 + 14 * u("lat"))
    return {"kind": "extratropical", "t0": slot * SLOT_H, "lat0": lat0, "lon0": lon0,
            "life_d": 3.5 + 3.5 * u("life"), "deficit": 14 + 32 * u("deficit") + 6 * winter,
            "radius": 7.5 + 6.0 * u("radius"), "vlon": 8 + 6 * u("vlon"), "vlat": hemi * (0.3 + 0.9 * u("vlat"))}


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
        lat = s["lat0"] + s["vlat"] * age_d
        lat = max(-74.0, min(74.0, lat))
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
        lat = s["lat0"] + sign * (s["vpole"] * t_rec + 1.6 * s["vpole"] * a2)
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
            if inten <= 0.02:
                continue
            out.append({**s, "lat": lat, "lon": lon, "intensity": inten, "age_d": age})
    return out


def _dist_deg(lat1, lon1, lat2, lon2) -> float:
    dlat = lat1 - lat2
    dlon = lon_delta(lon1, lon2) * math.cos(0.5 * (lat1 + lat2) * RAD)
    return math.hypot(dlat, dlon)


def _frame(seed: str, t: dt.datetime, grid: LatLonGrid, edges: dict, tick: float) -> dict:
    season = _season(t)
    storms = active_storms(seed, t)
    nh_winter = 0.5 + 0.5 * season
    P, CL, PR, CV, SW = [], [], [], [], []
    for j in range(grid.ny):
        lat = grid.lat(j)
        for i in range(grid.nx):
            lon = grid.lon(i)
            p = background_pressure(lat, lon, season)
            itcz = math.exp(-((lat - itcz_lat(lon, season)) / 5.0) ** 2)
            cloud = 34 + 40 * itcz
            rain = 0.6 * itcz ** 2
            conv = 0.7 * itcz
            # subtropical subsidence clears skies; subpolar troughs are cloudy
            cloud -= 12 * math.exp(-((abs(lat) - 28) / 8) ** 2)
            cloud += 35 * math.exp(-((abs(lat) - 58) / 10) ** 2)
            for la, lo in ((-20, -80), (-18, 8), (25, -125), (20, -22)):  # marine stratocumulus decks
                cloud += 35 * math.exp(-((lat - la) / 8) ** 2 - (lon_delta(lon, lo) / 14) ** 2)
            swell = 0.8 + (1.3 if lat < 0 else 0.4 + 0.5 * nh_winter) * math.exp(-((abs(lat) - 50) / 13) ** 2)
            for s in storms:
                d = _dist_deg(lat, lon, s["lat"], s["lon"])
                if d > 45:
                    continue
                r, inten = s["radius"], s["intensity"]
                core = math.exp(-0.5 * (d / (0.6 * r)) ** 2)
                p -= s["deficit"] * inten * core
                if s["kind"] == "tropical":
                    cloud += 70 * inten * math.exp(-0.5 * (d / (1.6 * r)) ** 2)
                    rain += 14 * inten * core + 3 * inten * math.exp(-0.5 * (d / (1.4 * r)) ** 2)
                    conv = max(conv, inten * math.exp(-0.5 * (d / (1.4 * r)) ** 2))
                else:
                    # warm/cold front: a band ~0.8 r from the centre, on the equatorward-east side
                    ang = math.atan2(lat - s["lat"], lon_delta(lon, s["lon"]) * math.cos(lat * RAD))
                    side = 0.5 + 0.5 * math.sin(ang * (1 if s["lat"] > 0 else -1) * -1 + 0.6)
                    front = math.exp(-((d - 0.8 * r) / (0.3 * r)) ** 2) * side
                    cloud += inten * (60 * math.exp(-0.5 * (d / r) ** 2) + 30 * front)
                    rain += inten * (1.8 * core + 3.5 * front)
                    if abs(s["lat"]) < 48:
                        conv = max(conv, 0.6 * inten * front)
                swell += 2.2 * inten * s["deficit"] / 40.0 * math.exp(-d / 15.0)
            P.append(p)
            CL.append(max(0.0, min(100.0, cloud)))
            PR.append(max(0.0, min(40.0, rain)))
            CV.append(max(0.0, min(1.0, conv)))
            SW.append(min(8.0, swell))
    U, V = _winds(grid, P, season)
    out = {n: [] for n in PACK}
    for j in range(grid.ny):
        lat = grid.lat(j)
        winter_here = (0.5 + 0.5 * season) if lat >= 0 else (0.5 - 0.5 * season)
        for i in range(grid.nx):
            k = j * grid.nx + i
            lon = grid.lon(i)
            spd = math.hypot(U[k], V[k])
            wind_sea = 0.0214 * spd * spd * 0.75
            hs = min(15.0, math.hypot(wind_sea, SW[k]))
            temp = -20 + 48 * max(0.0, math.cos(lat * RAD)) ** 1.5 - 6 * (winter_here - 0.5) * min(1.0, abs(lat) / 60)
            wobble = 0.35 * math.sin(tick * 0.4 + lon * RAD * 2)
            ice = seaice.ice_at(lat - (wobble if lat < 0 else -wobble), lon, edges)
            out["msl_pressure_hpa"].append(min(1060.0, max(900.0, P[k])))
            out["wind_u10_ms"].append(U[k])
            out["wind_v10_ms"].append(V[k])
            out["cloud_fraction_pct"].append(CL[k])
            out["precip_rate_mm_h"].append(PR[k])
            out["air_temp_2m_c"].append(max(-60.0, min(45.0, temp)))
            out["wave_hs_m"].append(max(0.2, hs))
            out["sea_ice_conc_pct"].append(min(100.0, ice))
            out["convective_risk_idx"].append(CV[k])
    return out


def _winds(grid: LatLonGrid, P: list, season: float) -> tuple[list, list]:
    """10 m wind from the pressure grid: geostrophic, reduced and turned towards low pressure;
    blended into trade winds near the equator."""
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
            # surface: 70 % of geostrophic, turned 20 deg towards low pressure
            turn = 20 * RAD * (1 if lat >= 0 else -1)
            us = 0.7 * (ug * math.cos(turn) - vg * math.sin(turn))
            vs = 0.7 * (ug * math.sin(turn) + vg * math.cos(turn))
            lon = grid.lon(i)
            itcz = itcz_lat(lon, season)
            trade_u = -6.5 * math.exp(-((abs(lat - itcz) - 12) / 9) ** 2) - 1.0
            trade_v = 2.5 * math.tanh((itcz - lat) / 6.0)
            w = max(0.0, min(1.0, (abs(lat) - 8) / 10.0))
            u = w * us + (1 - w) * trade_u
            v = w * vs + (1 - w) * trade_v
            spd = math.hypot(u, v)
            if spd > 45:
                u, v = u * 45 / spd, v * 45 / spd
            U[j * nx + i], V[j * nx + i] = u, v
    return U, V


def generate(seed: str, start: dt.datetime, hours: int = 72, step_hours: int = 6, res_deg: float = 4.0,
             created: dt.datetime | None = None) -> dict:
    if start.tzinfo is None:
        raise ValueError("start must be UTC")
    if not (1 <= step_hours <= 24 and 0 <= hours <= 24 * 60 and res_deg in (1.0, 2.0, 2.5, 4.0, 5.0)):
        raise ValueError("unsupported procedural request")
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
