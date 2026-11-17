"""MnoEnvForecast: what a side KNOWS about the weather, separate from the weather. BUILD-TESTED.

The environment state is the truth. A side sees a report whose quality depends on where its
sensors are and how far ahead it looks:

    OBSERVED   a reporting asset (ship, aircraft, station, weather satellite pass) saw the
               point within its radius in the last `valid_hours`;
    FORECAST   no current observation; the value is the truth plus a deterministic error
               that grows with lead time (and shrinks with a fresh nearby observation);
    STALE      lead time beyond the forecast horizon: value withheld, only climatology hint;
    ESTIMATED  the player's own estimate (set by UI), never replaced silently.

Errors are deterministic per (save seed, side, rounded position, valid time, field), so a
reload shows the same forecast. Reconnaissance changes information quality only; it never
writes to the environment. Preview (forecast scrub) never advances the campaign clock.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from .geo import great_circle_nm

# One-sigma forecast error at lead 0 h and growth per 24 h (planning values, not verification
# statistics; ECMWF's published scores are the reference to calibrate against later).
ERROR_MODEL = {
    "msl_pressure_hpa": (0.8, 1.6),
    "wind_u10_ms": (1.0, 1.1),
    "wind_v10_ms": (1.0, 1.1),
    "cloud_fraction_pct": (8.0, 6.0),
    "precip_rate_mm_h": (0.3, 0.6),
    "air_temp_2m_c": (0.7, 0.6),
    "wave_hs_m": (0.2, 0.25),
    "sea_ice_conc_pct": (4.0, 3.0),
}
BOUNDS = {"cloud_fraction_pct": (0, 100), "precip_rate_mm_h": (0, 500), "wave_hs_m": (0, 25), "sea_ice_conc_pct": (0, 100)}
HORIZON_H = 240.0


@dataclass(frozen=True)
class Asset:
    kind: str          # ship | aircraft | station | satellite
    lat: float
    lon: float
    radius_nm: float
    observed_seconds: int
    valid_hours: float = 6.0


@dataclass(frozen=True)
class Report:
    status: str                # OBSERVED | FORECAST | STALE | ESTIMATED
    values: dict
    sigma: dict
    lead_hours: float
    basis: str


def _gauss(seed: str, *parts) -> float:
    h = hashlib.sha256("|".join(str(p) for p in (seed, *parts)).encode()).digest()
    u1 = (int.from_bytes(h[:8], "big") + 1) / (2 ** 64 + 2)
    u2 = int.from_bytes(h[8:16], "big") / 2 ** 64
    return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


class MnoEnvForecast:
    def __init__(self, state, seed: str):
        self.state = state  # clock.MnoEnvState
        self.seed = seed

    def report(self, side: str, now_seconds: int, valid_seconds: int, lat: float, lon: float,
               assets: list[Asset] = (), estimate: dict | None = None) -> Report:
        if valid_seconds < now_seconds:
            raise ValueError("forecasts look ahead; past weather is a separate history query")
        if estimate is not None:
            return Report("ESTIMATED", dict(estimate), {}, 0.0, "player estimate")
        lead_h = (valid_seconds - now_seconds) / 3600.0
        truth = self.state.sample(valid_seconds, lat, lon).values
        fresh = [a for a in assets if 0 <= now_seconds - a.observed_seconds <= a.valid_hours * 3600
                 and great_circle_nm((a.lat, a.lon), (lat, lon)) <= a.radius_nm]
        if lead_h == 0 and fresh:
            return Report("OBSERVED", {k: v for k, v in truth.items() if k in ERROR_MODEL}, {k: 0.0 for k in ERROR_MODEL if k in truth},
                          0.0, "+".join(sorted({a.kind for a in fresh})))
        if lead_h > HORIZON_H:
            return Report("STALE", {}, {}, lead_h, "beyond forecast horizon")
        damp = 0.6 if fresh else 1.0  # a fresh local observation initialises the forecast better
        cell = (round(lat * 4) / 4, round(lon * 4) / 4)
        values, sigma = {}, {}
        for name, (s0, growth) in ERROR_MODEL.items():
            if truth.get(name) is None:
                continue
            s = damp * (s0 + growth * lead_h / 24.0)
            v = truth[name] + s * _gauss(self.seed, side, cell, valid_seconds, name)
            lo, hi = BOUNDS.get(name, (-1e9, 1e9))
            values[name] = round(min(hi, max(lo, v)), 2)
            sigma[name] = round(s, 3)
        return Report("FORECAST", values, sigma, lead_h, "model forecast" + (" + local observation" if fresh else ""))
