"""Seeded procedural environment: the offline fallback and the demo. BUILD-TESTED.

PROCEDURAL, NOT REAL WEATHER. The storm model is the prototype's bounded analytic cyclone
field (prototype-20261118/src/environment_model.py), re-expressed so that the storm tracks
come from a seed instead of a fixed table. It is deterministic across machines and Python
versions: the only randomness is SHA-256 of (seed, label). Its purpose is that a GCO save
is playable with plausible-looking, moving weather when no real snapshot is installed.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import math

from . import seaice
from .geo import lon_delta, wrap_lon
from .grid import LatLonGrid
from .snapshot import SCHEMA, iso, pack_int16, seal

PACK = {  # field -> int16 scale
    "msl_pressure_hpa": 0.1, "wind_u10_ms": 0.01, "wind_v10_ms": 0.01, "cloud_fraction_pct": 0.1,
    "precip_rate_mm_h": 0.01, "air_temp_2m_c": 0.01, "wave_hs_m": 0.01, "sea_ice_conc_pct": 0.1,
    "convective_risk_idx": 0.001,
}


def unit(seed: str, label: str) -> float:
    """Deterministic number in [0, 1)."""
    h = hashlib.sha256(f"{seed}|{label}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64


def storms(seed: str, n: int = 7) -> list[tuple]:
    out = []
    for k in range(n):
        u = lambda tag: unit(seed, f"storm{k}.{tag}")  # noqa: E731
        hemi = -1 if u("hemi") < 0.65 else 1  # Southern Ocean bias, as in the prototype
        lat0 = hemi * (38 + 22 * u("lat"))
        lon0 = -180 + 360 * u("lon")
        out.append((lat0, lon0, hemi * (0.02 + 0.12 * u("vlat")), 1.6 + 1.6 * u("vlon"),
                    18 + 26 * u("deficit"), 8 + 6 * u("radius"), 9 + 8 * u("wind")))
    return out


def field_at(lat: float, lon: float, hours: float, storm_list, month: int, ice_edges: dict | None = None) -> dict:
    rad = math.pi / 180
    tick = hours / 6.0
    u = 2.0 + 8.0 * math.exp(-((abs(lat) - 51) / 16) ** 2) * (1 if abs(lat) > 30 else -0.6)
    v = 1.5 * math.sin(lon * rad * 1.8)
    p = 1013.0 + 6.0 * math.cos(2 * (abs(lat) - 30) * rad) - 3.0 * math.sin(lat * rad) ** 2
    cloud = 18.0 + 17.0 * math.sin((lon + lat * 0.75 + tick * 2) * rad * 2) ** 2
    rain, swell, convect = 0.02, 0.9 + 0.5 * math.exp(-((abs(lat) - 50) / 18) ** 2), 0.0
    for lat0, lon0, vlat, vlon, deficit, radius, wind in storm_list:
        cy = max(-75.0, min(75.0, lat0 + tick * vlat))
        cx = wrap_lon(lon0 + tick * vlon)
        dx = lon_delta(lon, cx) * max(0.22, math.cos(lat * rad))
        dy = lat - cy
        dist = math.hypot(dx, dy)
        bell = math.exp(-0.5 * (dist / radius) ** 2)
        core = math.exp(-0.5 * (dist / (radius * 0.68)) ** 2)
        p -= deficit * core
        rot = -1 if cy < 0 else 1
        r = dist / max(1.0, radius * 0.55)
        shear = wind * bell * r / (1 + r * r) * 2.25
        u += rot * -dy / max(1, dist) * shear
        v += rot * dx / max(1, dist) * shear
        angle = math.atan2(dy, dx)
        front = math.exp(-((dist - radius * 0.85) / (radius * 0.32)) ** 2)
        band = 0.55 + 0.45 * math.sin(2 * angle - tick * 0.18 + 0.6) ** 2
        cloud += 71 * bell + 20 * front * band
        rain += 4.8 * front * band + 1.8 * core
        swell += 4.4 * bell
        convect = max(convect, front * band * (1.0 if abs(cy) < 45 else 0.5))
    speed = math.hypot(u, v)
    wave = min(13.5, max(0.2, 0.6 + 0.15 * speed + 0.30 * swell))
    # Season from campaign month: 1.0 at the hemisphere's ice maximum, 0 at its minimum.
    south_winter = 0.5 + 0.5 * math.cos((month - 9) * math.pi / 6)
    north_winter = 0.5 + 0.5 * math.cos((month - 3) * math.pi / 6)
    if ice_edges is not None:
        # Seasonal extent calibrated to NSIDC Sea Ice Index monthly medians (seaice.py), with a
        # small deterministic wobble so the edge moves between frames.
        wobble = 0.35 * math.sin(tick * 0.4 + lon * rad * 2)
        ice = seaice.ice_at(lat - (wobble if lat < 0 else -wobble), lon, ice_edges)
    else:  # legacy shape, kept only for callers that pass no edges
        south_edge = -72.5 + 11.5 * south_winter + 2.5 * math.cos((lon - 5) * rad * 1.4)
        north_edge = 79.0 - 9.0 * north_winter + 2.7 * math.cos((lon + 40) * rad)
        logistic = lambda z: 1 / (1 + math.exp(-max(-35, min(35, z))))  # noqa: E731
        ice = max(98 * logistic((south_edge - lat) / 2.2), 98 * logistic((lat - north_edge) / 2.4))
    winter_here = south_winter if lat < 0 else north_winter
    temp = -20 + 48 * max(0.0, math.cos(lat * rad)) ** 1.5 - 6 * (winter_here - 0.5) * min(1.0, abs(lat) / 60)
    return {
        "msl_pressure_hpa": min(1060.0, max(925.0, p)),
        "wind_u10_ms": max(-55.0, min(55.0, u)),
        "wind_v10_ms": max(-55.0, min(55.0, v)),
        "cloud_fraction_pct": min(100.0, max(0.0, cloud)),
        "precip_rate_mm_h": min(35.0, max(0.0, rain)),
        "air_temp_2m_c": max(-60.0, min(45.0, temp)),
        "wave_hs_m": wave,
        "sea_ice_conc_pct": min(100.0, ice),
        "convective_risk_idx": min(1.0, convect),
    }


def generate(seed: str, start: dt.datetime, hours: int = 72, step_hours: int = 6, res_deg: float = 4.0,
             created: dt.datetime | None = None) -> dict:
    if start.tzinfo is None:
        raise ValueError("start must be UTC")
    if not (1 <= step_hours <= 24 and 0 <= hours <= 24 * 60 and res_deg in (1.0, 2.0, 2.5, 4.0, 5.0)):
        raise ValueError("unsupported procedural request")
    grid = LatLonGrid(-180.0, -90.0, res_deg, res_deg, int(360 / res_deg), int(180 / res_deg) + 1)
    sl = storms(seed)
    times = []
    for k in range(hours // step_hours + 1):
        t = start + dt.timedelta(hours=k * step_hours)
        edges = seaice.edges_on(t)
        cols = {name: [] for name in PACK}
        for j in range(grid.ny):
            lat = grid.lat(j)
            for i in range(grid.nx):
                f = field_at(lat, grid.lon(i), k * step_hours, sl, t.month, edges)
                for name in PACK:
                    cols[name].append(f[name])
        times.append({"valid_utc": iso(t), "lead_hours": None,
                      "values": {n: pack_int16(cols[n], PACK[n]) for n in PACK}})
    kind = {"kind": "procedural", "uncertainty": {"type": "not_applicable", "note": "procedural; no observation"}}
    fields = {}
    from .snapshot import FIELDS
    for n in PACK:
        fields[n] = {"units": FIELDS[n][0], "fill_value": None, **kind}
    fields["convective_risk_idx"] = {"units": FIELDS["convective_risk_idx"][0], "fill_value": None, "kind": "derived_risk",
                                     "derivation": "frontal-band intensity of the procedural cyclones; not lightning",
                                     "uncertainty": {"type": "not_applicable"}}
    snap = {
        "schema": SCHEMA,
        "snapshot_id": f"procedural-{hashlib.sha256(seed.encode()).hexdigest()[:12]}-{iso(start)}-{hours}h-{res_deg}deg",
        "created_utc": iso(created or start),
        "data_class": "procedural",
        "provenance": {"provider": "MNO", "product": "PROCEDURAL seeded cyclone field (not real weather)",
                       "product_version": "mno.env.procedural.2 (sea-ice extent: NSIDC G02135 v4.0 2016-2025 monthly medians)", "licence": "same as MNO source",
                       "attribution": "SEST-DEV", "source_url": None, "downloaded_utc": None,
                       "source_time_utc": None, "forecast_issue_utc": None, "seed": seed},
        "campaign_mapping": {"mode": "procedural", "offset_seconds": 0, "campaign_start_utc": iso(start),
                             "statement": "Procedural weather generated for the campaign; not a forecast of any real date."},
        "grid": grid.to_dict(),
        "fields": fields,
        "times": times,
        "integrity": {},
    }
    return seal(snap)
