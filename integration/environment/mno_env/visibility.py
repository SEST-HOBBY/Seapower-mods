"""Visibility for the procedural model: sea fog, mist, rain and snow, dust haze, sea smoke. BUILD-TESTED.

PROCEDURAL, NOT OBSERVED. The game's Fog flag is visibility below 1 km (WMO), so this module
is what makes procedural weather foggy at all. visibility_km is the minimum of:

- sea fog: a climatological fog frequency for the place and season (advection fog over cold
  currents and shelf seas, summer fog over the Arctic and Southern Ocean ice margins, winter
  fog in the Gulf and the head of the Bay of Bengal), modulated by the weather (fog needs
  light to moderate wind, no real rain, and is favoured by poleward warm advection) and drawn
  from slowly moving noise so fog banks come and go over hours to days. Frequencies are
  approximate peak-month values of ship-reported fog (Dorman et al. 2017/2020, "World marine
  fog analysis based on 58 years of ship observations", ICOADS); fitted by hand, not data;
- rain and snow: visibility falls with rate (moderate rain ~4 km, heavy ~2 km, heavy snow
  below 1 km);
- dust and sand haze downwind of the Arabian, Red Sea, Saharan and Gobi sources, worse in
  their seasons and in strong wind (shamal, harmattan), with rare sub-1 km dust storms;
- Arctic sea smoke (steam fog) where very cold air crosses open water;
- clear-air background: about 20 km in the humid tropics, rising to about 38 km in polar air.

Deterministic: the only randomness is the seeded noise of procedural.py.
"""
from __future__ import annotations

import datetime as dt
import math

from .geo import lon_delta

# name, lat, lon, lat scale, lon scale, peak frequency of visibility < 1 km (6-hourly), peak day
# of year, seasonal half-width (days, Gaussian sigma), off-season share of the peak.
FOG_REGIONS = [
    ("Grand Banks / Newfoundland", 45, -50, 5, 10, 0.34, 190, 55, 0.08),
    ("Gulf of Maine / Nova Scotia", 43, -66, 3, 6, 0.25, 190, 50, 0.10),
    ("Gulf of St Lawrence / Labrador", 50, -58, 4, 8, 0.15, 195, 45, 0.05),
    ("Kuril / Oyashio / Okhotsk", 46, 152, 6, 12, 0.42, 200, 45, 0.08),
    ("Bering Sea / Aleutians", 56, -178, 6, 18, 0.36, 205, 50, 0.10),
    ("Yellow Sea", 35.5, 123.5, 3.5, 4.5, 0.17, 170, 40, 0.10),
    ("East China Sea / Taiwan Strait", 25, 120, 3, 4, 0.16, 95, 35, 0.10),
    ("California coast", 37, -124, 5, 4, 0.16, 215, 50, 0.20),
    ("Peru / Humboldt", -15, -78, 6, 5, 0.13, 225, 65, 0.30),
    ("Namib / Benguela", -23, 12, 6, 5, 0.15, 200, 80, 0.40),
    ("Canary / north-west Africa", 24, -17, 4, 4, 0.04, 200, 70, 0.30),
    ("North Sea", 55, 3, 4, 6, 0.06, 120, 50, 0.40),
    ("Baltic", 57, 19, 4, 7, 0.06, 130, 45, 0.30),
    ("Western Approaches / Channel", 49, -5, 3, 5, 0.05, 150, 60, 0.40),
    ("Barents / Norwegian Sea", 74, 30, 7, 30, 0.10, 200, 40, 0.10),
    ("Iceland / Faroes", 63, -10, 4, 12, 0.10, 200, 45, 0.20),
    ("Persian Gulf winter", 27.5, 51.5, 3, 5, 0.06, 15, 45, 0.10),
    ("Head of the Bay of Bengal winter", 21, 89, 2, 4, 0.03, 15, 40, 0.0),
]

# name, lat, lon, lat scale, lon scale, peak strength, peak day, half-width, off-season share
DUST_SOURCES = [
    ("Persian Gulf / shamal", 27.5, 51, 3, 8, 1.0, 175, 50, 0.4),
    ("Strait of Hormuz / Gulf of Oman", 25, 57, 3, 5, 0.8, 175, 50, 0.3),
    ("Gulf of Oman / northern Arabian Sea", 22, 60, 4, 8, 0.7, 180, 40, 0.1),
    ("Red Sea / Bab el-Mandeb", 18, 40, 6, 4, 0.7, 190, 60, 0.3),
    ("Harmattan off West Africa", 12, -18, 6, 10, 0.8, 15, 45, 0.0),
    ("Levant / Egypt (khamsin)", 32, 31, 3, 6, 0.4, 100, 30, 0.1),
    ("Yellow Sea Asian dust", 36, 123, 4, 6, 0.4, 100, 25, 0.0),
]

NOISE_SIGMA = 0.325  # spread of the procedural travelling-wave noise (measured)


def _doy(t: dt.datetime) -> float:
    return t.timetuple().tm_yday + t.hour / 24.0


def _seasonal(doy: float, peak: float, width: float, base: float) -> float:
    d = (doy - peak + 182.6) % 365.25 - 182.6
    return base + (1.0 - base) * math.exp(-(d / width) ** 2)


def _smooth(a: float, b: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def fog_frequency(lat: float, lon: float, t: dt.datetime) -> float:
    """Climatological share of 6-hourly samples with visibility below 1 km (0..1)."""
    doy = _doy(t)
    clear = 1.0
    for _n, la, lo, sy, sx, peak, pd, w, base in FOG_REGIONS:
        g = math.exp(-((lat - la) / sy) ** 2 - (lon_delta(lon, lo) / sx) ** 2)
        if g > 1e-3:
            clear *= 1.0 - peak * g * _seasonal(doy, pd, w, base)
    a = abs(lat)
    if lat > 0:  # summer fog over the Arctic ice margin and open polar seas
        clear *= 1.0 - 0.17 * _smooth(64, 74, a) * _seasonal(doy, 200, 45, 0.05)
    else:
        clear *= 1.0 - 0.24 * _smooth(55, 65, a) * _seasonal(doy, 20, 50, 0.2)
    clear *= 1.0 - 0.01 * _smooth(30, 45, a)  # occasional warm-sector fog anywhere in mid-latitudes
    return 1.0 - clear


def dust_strength(lat: float, lon: float, t: dt.datetime) -> float:
    doy = _doy(t)
    s = 0.0
    for _n, la, lo, sy, sx, peak, pd, w, base in DUST_SOURCES:
        g = math.exp(-((lat - la) / sy) ** 2 - (lon_delta(lon, lo) / sx) ** 2)
        if g > 1e-3:
            s += peak * g * _seasonal(doy, pd, w, base)
    return s


def _uniform(n: float, alat: float) -> float:
    """Map the (roughly Gaussian) noise to a roughly uniform 0..1 value."""
    sigma = NOISE_SIGMA - 0.04 * math.exp(-((alat - 25) / 6) ** 2)
    return 0.5 * (1.0 + math.erf(n / (sigma * math.sqrt(2.0))))


FOG_COND_MEAN = 0.8  # mean of the weather modulation, so the climatological frequency is kept


def fog_probability(*, lat: float, lon: float, t: dt.datetime, wind_ms: float, v_ms: float, rain_mm_h: float,
                    land: bool) -> float:
    """Chance of visibility below 1 km now: the climatological frequency modulated by the weather."""
    f = fog_frequency(lat, lon, t) * (0.8 if land else 1.0)  # coastal land nodes: the game samples sea between them
    if f <= 0.0:
        return 0.0
    cw = (0.6 + 0.4 * _smooth(0.5, 2.0, wind_ms)) * (1.0 - 0.8 * _smooth(11.0, 18.0, wind_ms))  # strong wind lifts most fog to stratus
    cr = 1.0 - _smooth(0.3, 1.5, rain_mm_h)                                            # rain washes it out
    cv = 1.0 + 0.6 * math.tanh(v_ms * (1 if lat >= 0 else -1) / 4.0)                    # warm air moving poleward over cold water
    return min(0.95, f * cw * cr * cv / FOG_COND_MEAN)


def visibility_km(*, lat: float, lon: float, t: dt.datetime, wind_ms: float, v_ms: float, rain_mm_h: float,
                  temp_c: float, ice_pct: float, land: bool, fog_noise: float, dust_noise: float) -> float:
    a = abs(lat)
    vis = 20.0 + 18.0 * _smooth(25, 65, a)  # clear-air background
    # sea fog
    p = fog_probability(lat=lat, lon=lon, t=t, wind_ms=wind_ms, v_ms=v_ms, rain_mm_h=rain_mm_h, land=land)
    if p > 0.0:
        u = _uniform(fog_noise, a)
        if u < p:
            vis = min(vis, 0.1 + 0.85 * (u / p) ** 0.7)
        elif u < p + 0.12 * p + 0.04:  # mist at the edge of the bank
            vis = min(vis, 1.0 + 5.0 * (u - p) / (0.12 * p + 0.04))
    # rain and snow
    if rain_mm_h > 0.05:
        if temp_c <= 0.5:
            vis = min(vis, 1.6 * rain_mm_h ** -0.8)
        else:
            vis = min(vis, 12.0 * rain_mm_h ** -0.65)
    # dust and sand haze: episodic (log-normal in the noise), worse in strong wind
    s = dust_strength(lat, lon, t)
    if s > 0.01:
        lift = 0.4 + 0.6 * _smooth(4.0, 12.0, wind_ms)
        d = s * lift * math.exp(1.1 * dust_noise / NOISE_SIGMA) * (1.0 - _smooth(0.5, 3.0, rain_mm_h))
        vis = min(vis, max(1.2, 35.0 / (1.0 + 5.0 * d)))  # haze: the game's Fog flag is for fog, not dust
    # Arctic sea smoke: very cold air over open water
    if not land and ice_pct < 15.0 and temp_c < -12.0:
        vis = min(vis, max(0.5, 1.5 + 0.45 * (temp_c + 28.0)))
    return max(0.05, min(50.0, vis))
