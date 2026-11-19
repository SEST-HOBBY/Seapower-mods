"""Sensor environment derived from the weather: sonar, radar, EO/IR, night, flight deck. BUILD-TESTED.

PLANNING PRODUCT, NOT IN-GAME TESTED. derive(values, lat, lon, when, theatre) turns one weather
sample (the fields of a snapshot sample) into a SensorEnv: what the real ocean and atmosphere would
do to sensors at that place and time. The game models only part of this (see docs/environment/
SENSOR-PC-TESTS.md): it adds +5 dB passive ambient per sea state and +15 dB in rain, and computes
its own thermal layer, surface duct and floe-ice terms. Radar, EO/IR and visual weather effects are
inside the game code and cannot be set from files. So every output here carries a label:

- game:  what the game itself will apply, quoted from its files (environment.ini [Sonar]);
- suggest: a value a per-mission [Sonar] override could carry (UNTESTED; mno_env never writes it
  unless the owner's PC test passes);
- real:  a real-world planning note the simulator does not model.

Each value also names its source ('snapshot', 'derived', 'table', 'climatology') and a confidence.
No network, no optional packages; deterministic.

References: Pollard, Rhines & Thompson 1973 (mixed layer); Urick, Principles of Underwater Sound
(surface-duct cutoff); Ma & Nystuen 2005 (rain noise); Paulus 1985 / NPS bulk evaporation-duct
model; ITU-R P.838-3 (rain attenuation); Gregers-Hansen & Mital 2012 (NRL sea clutter);
Miller, Brown & Vegh 1984 (rough-sea reflection); ITU-R P.1814 (rain extinction, optical);
Krisciunas & Schaefer 1991 (moonlight); Meeus, Astronomical Algorithms (moon and sun positions).
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field

RAD = math.pi / 180
G = 9.81

# --- game constants quoted from mods-source/_vanilla/original/environment.ini [Sonar] (0.9.0 export) ---
GAME_SONAR = {"BaseAmbientOceanNoise": 60.0, "PerSeaStateNoise": 5.0, "RainNoise": 15.0,
              "ConvergenceZoneDist1": 30.0, "ConvergenceZoneDist2": 60.0, "MinDepthForConvergenceZones_ft": 3000.0,
              "SofarAxisDepthM": 800.0, "MinXLayerAttenuation": 6.0, "MaxXLayerAttenuation": 12.0}

# --- theatre tables (hand-set; see docs/environment/SENSOR-PC-TESTS.md "Sources") ---
# shipping: dB added to the distant-shipping ambient term (capped +6); depth: 'shallow' (< 150 m)
# or 'deep'; cz: real-world convergence zones (None = none: no depth excess or shallow water),
# else (first-zone range nm, second-zone nm). rh: typical relative humidity Sep-Mar (%).
# air_sea: typical air minus sea temperature (C). Approximate climatology for planning, not data.
THEATRES = {
    "hormuz": {"name": "Strait of Hormuz / Gulf of Oman", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
               "cz": None, "cz_note": "strait < 100 m; Gulf of Oman deep but no depth excess in warm months",
               "rh": 65.0, "air_sea": -0.5, "merchants": "high"},
    "bab-el-mandeb": {"name": "Bab el-Mandeb / Gulf of Aden", "shipping": 4.0, "shallow_strait": True, "depth": "shallow",
                      "cz": None, "cz_note": "Hanish sill about 140 m; warm Red Sea outflow, no depth excess",
                      "rh": 70.0, "air_sea": -0.5, "merchants": "medium"},
    "malacca": {"name": "Strait of Malacca / Singapore", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "strait 25-100 m: no convergence zones",
                "rh": 80.0, "air_sea": -0.5, "merchants": "high"},
    "cape-of-good-hope": {"name": "Cape of Good Hope", "shipping": 2.0, "shallow_strait": False, "depth": "deep",
                          "cz": (32.0, 64.0), "cz_note": "deep Cape Basin; zones about every 32 nm",
                          "rh": 75.0, "air_sea": -0.5, "merchants": "medium"},
    "drake-passage": {"name": "Drake Passage", "shipping": -3.0, "shallow_strait": False, "depth": "deep",
                      "cz": (27.0, 54.0), "cz_note": "north of the Polar Front; south of it the sound channel "
                                                    "reaches the surface (half-channel), no zones",
                      "rh": 85.0, "air_sea": -0.5, "merchants": "low"},
    "taiwan-strait": {"name": "Taiwan Strait", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "strait 60-80 m: no convergence zones",
                "rh": 78.0, "air_sea": -0.5, "merchants": "high"},
    "luzon-strait": {"name": "Luzon Strait / Bashi Channel", "shipping": 4.0, "shallow_strait": False, "depth": "deep",
                "cz": (34.0, 68.0), "cz_note": "deep tropical water; zones about every 34 nm",
                "rh": 80.0, "air_sea": -0.5, "merchants": "medium"},
    "miyako-strait": {"name": "Miyako Strait", "shipping": 3.0, "shallow_strait": False, "depth": "deep",
                "cz": (33.0, 66.0), "cz_note": "zones in the Philippine Sea east of the Ryukyus; none on the East China Sea shelf",
                "rh": 78.0, "air_sea": -0.5, "merchants": "medium"},
    "korea-strait": {"name": "Korea / Tsushima Strait", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "strait about 100 m: no convergence zones",
                "rh": 75.0, "air_sea": -0.5, "merchants": "high"},
    "suez-north-red-sea": {"name": "Suez / northern Red Sea", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "Gulf of Suez shallow; the deep Red Sea is near-isothermal below 200 m: no zones",
                "rh": 55.0, "air_sea": -0.5, "merchants": "high"},
    "mozambique-channel": {"name": "Mozambique Channel", "shipping": 3.0, "shallow_strait": False, "depth": "deep",
                "cz": (32.0, 64.0), "cz_note": "deep channel; zones about every 32 nm",
                "rh": 75.0, "air_sea": -0.5, "merchants": "medium"},
    "sunda-strait": {"name": "Sunda Strait", "shipping": 4.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "strait 20-100 m: no convergence zones",
                "rh": 80.0, "air_sea": -0.5, "merchants": "medium"},
    "lombok-makassar": {"name": "Lombok Strait / Makassar approach", "shipping": 3.0, "shallow_strait": False, "depth": "deep",
                "cz": None, "cz_note": "Lombok sill about 250 m; zones only in the deep Makassar Strait to the north",
                "rh": 80.0, "air_sea": -0.5, "merchants": "medium"},
    "ombai-wetar": {"name": "Ombai-Wetar Strait", "shipping": 0.0, "shallow_strait": False, "depth": "deep",
                "cz": (35.0, 70.0), "cz_note": "deep passage (over 3000 m) into the Banda Sea; zones about every 35 nm",
                "rh": 78.0, "air_sea": -0.5, "merchants": "low"},
    "gibraltar": {"name": "Strait of Gibraltar", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "sill about 300 m with the Mediterranean outflow below: no zones in the strait",
                "rh": 70.0, "air_sea": -0.5, "merchants": "high"},
    "turkish-straits": {"name": "Turkish Straits / north Aegean", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "Bosporus and Dardanelles shallow; strong two-layer flow",
                "rh": 70.0, "air_sea": -0.5, "merchants": "high"},
    "danish-straits": {"name": "Danish Straits / Baltic approaches", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "20-60 m with a strong halocline: no zones",
                "rh": 82.0, "air_sea": -0.5, "merchants": "high"},
    "english-channel": {"name": "English Channel / Dover Strait", "shipping": 6.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "under 120 m: no convergence zones",
                "rh": 82.0, "air_sea": -0.5, "merchants": "high"},
    "giuk-gap": {"name": "GIUK gap", "shipping": 0.0, "shallow_strait": False, "depth": "deep",
                "cz": (28.0, 56.0), "cz_note": "zones in the deep basins either side of the Iceland-Faroe ridge (sill 400-600 m)",
                "rh": 85.0, "air_sea": -0.5, "merchants": "low"},
    "bering-strait": {"name": "Bering Strait", "shipping": -3.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "strait about 50 m: no zones; ice much of the year",
                "rh": 85.0, "air_sea": -0.5, "merchants": "low"},
    "kola-barents": {"name": "Kola / Barents approaches", "shipping": 2.0, "shallow_strait": False, "depth": "shallow",
                "cz": None, "cz_note": "Barents shelf 200-350 m: no convergence zones",
                "rh": 85.0, "air_sea": -0.5, "merchants": "medium"},
    "panama": {"name": "Panama Canal approaches", "shipping": 6.0, "shallow_strait": False, "depth": "deep",
                "cz": (32.0, 64.0), "cz_note": "zones offshore in the deep Pacific and Caribbean basins",
                "rh": 80.0, "air_sea": -0.5, "merchants": "high"},
    "bass-strait": {"name": "Bass Strait", "shipping": 3.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "strait 50-80 m: no convergence zones",
                "rh": 75.0, "air_sea": -0.5, "merchants": "medium"},
    "torres-strait": {"name": "Torres Strait", "shipping": 2.0, "shallow_strait": True, "depth": "shallow",
                "cz": None, "cz_note": "under 15 m in places: no zones, navigation-limited",
                "rh": 78.0, "air_sea": -0.5, "merchants": "low"},
}


@dataclass(frozen=True)
class Item:
    value: object
    unit: str
    tag: str          # 'game' | 'suggest' | 'real'
    source: str       # 'snapshot' | 'derived' | 'table' | 'climatology'
    confidence: str   # 'high' | 'med' | 'low'
    note: str = ""


@dataclass(frozen=True)
class SensorEnv:
    lat: float
    lon: float
    when: str
    theatre: str | None
    items: dict = field(default_factory=dict)

    def __getitem__(self, k):
        return self.items[k]


# ------------------------------------------------------------------ helpers
def es_hpa(t_c: float) -> float:
    """Saturation vapour pressure over water (Magnus/Bolton), hPa."""
    return 6.112 * math.exp(17.67 * t_c / (t_c + 243.5))


def dewpoint_c(t_c: float, rh_pct: float) -> float:
    g = math.log(max(1e-6, rh_pct) / 100.0) + 17.67 * t_c / (t_c + 243.5)
    return 243.5 * g / (17.67 - g)


def abs_humidity_gm3(t_c: float, rh_pct: float) -> float:
    e = es_hpa(t_c) * rh_pct / 100.0
    return 216.7 * e / (t_c + 273.15)


def refractivity(t_c: float, e_hpa: float, p_hpa: float = 1013.25) -> float:
    tk = t_c + 273.15
    return 77.6 * p_hpa / tk + 3.73e5 * e_hpa / tk ** 2


def wmo_sea_state(hs: float) -> int:
    for code, upper in enumerate((0.0, 0.1, 0.5, 1.25, 2.5, 4.0, 6.0, 9.0, 14.0)):
        if hs <= upper:
            return code
    return 9


# ------------------------------------------------------------------ sonar
def mixed_layer_m(lat: float, when: dt.datetime, u10: float, depth: str = "deep") -> tuple[float, float]:
    """(climatological, wind-deepened) mixed-layer depth, m. Climatology: a seasonal analytic fit
    (shallow summer layers of 10-30 m in mid-latitudes, deep winter ones of 80-150 m; 30-60 m in the
    tropics); wind deepening after Pollard-Rhines-Thompson, h = 1.7 u*/sqrt(N f)."""
    a = abs(lat)
    doy = when.timetuple().tm_yday
    summer = 0.5 + 0.5 * math.cos(2 * math.pi * (doy - (196 if lat >= 0 else 15)) / 365.25)  # 1 in local summer
    if a < 20:
        h_clim = 45.0 - 10.0 * summer
    else:
        w = min(1.0, (a - 20) / 30)
        h_clim = (45.0 - 10.0 * summer) * (1 - w) + (20.0 + 110.0 * (1 - summer)) * w
    f = 2 * 7.2921e-5 * math.sin(max(5.0, a) * RAD)
    cd = 1.3e-3 if u10 < 11 else (0.49 + 0.065 * u10) * 1e-3
    ustar = u10 * math.sqrt(1.225 * cd / 1025.0)
    n = max(0.005, 0.02 * (0.4 + 0.6 * summer) * (1 - min(1.0, max(0.0, (a - 40) / 30))))
    h_wind = 1.7 * ustar / math.sqrt(n * f)
    cap = 0.8 * (100.0 if depth == "shallow" else 5000.0)
    return min(h_clim, cap), min(max(h_clim, h_wind), 150.0, cap)


def layer_class(lat: float, when: dt.datetime, depth: str) -> tuple[str, tuple[float, float]]:
    """Real-world layer strength and the cross-layer loss (dB) it would suggest (game default 6/12)."""
    a = abs(lat)
    doy = when.timetuple().tm_yday
    summer = 0.5 + 0.5 * math.cos(2 * math.pi * (doy - (196 if lat >= 0 else 15)) / 365.25)
    if depth == "shallow":
        return "mixed or weak (shallow water)", (3.0, 7.0)
    if a < 25:
        return "strong (tropical thermocline)", (10.0, 18.0)
    if a > 55:
        return ("weak" if summer > 0.5 else "isothermal (winter mixing)"), ((3.0, 7.0) if summer > 0.5 else (1.0, 3.0))
    return ("strong (seasonal thermocline)" if summer > 0.6 else "medium" if summer > 0.3 else "weak (winter)"), \
        ((10.0, 18.0) if summer > 0.6 else (6.0, 12.0) if summer > 0.3 else (3.0, 7.0))


def duct_cutoff_hz(h_m: float) -> float:
    """Lowest frequency trapped by a surface duct of thickness h (m): 9.74e4 / h^1.5 Hz."""
    return 9.74e4 / max(1.0, h_m) ** 1.5


def ambient_suggest(shipping_db: float, sea_state: int, shallow_strait: bool) -> float:
    """BaseAmbientOceanNoise a per-mission override could carry. Wind, sea state and rain are NOT
    added: the game adds PerSeaStateNoise x SeaState and RainNoise itself."""
    d = min(6.0, shipping_db) - (4.0 if shallow_strait else 0.0)
    if sea_state > 2:
        d = max(0.0, d - 1.5 * (sea_state - 2)) if d > 0 else d
    return max(57.0, min(66.0, GAME_SONAR["BaseAmbientOceanNoise"] + d))


def rain_noise_suggest(rain_mm_h: float, sea_state: int) -> float:
    """RainNoise as a power sum over wind noise at 5 kHz (Ma & Nystuen 2005), clamped 3-20 dB."""
    if rain_mm_h < 0.5:  # no Rain flag (mission_adapter.RAIN_FLAG_ON_MM_H): the game's own value stands
        return GAME_SONAR["RainNoise"]
    l_rain = 42.4 + 15.4 * math.log10(max(0.05, rain_mm_h))
    l_wind = {0: 45.0, 1: 48.0, 2: 53.0, 3: 56.0, 4: 59.0}.get(sea_state, 61.0)
    return max(3.0, min(20.0, 10 * math.log10(1 + 10 ** ((l_rain - l_wind) / 10))))


# ------------------------------------------------------------------ radar
def _psi_m(zeta):  # Businger-Dyer integrated stability functions (momentum not needed; scalar)
    if zeta < 0:
        x = (1 - 16 * zeta) ** 0.5
        return 2 * math.log((1 + x) / 2)
    return -5 * zeta


def _phi(zeta):
    return (1 - 16 * zeta) ** -0.5 if zeta < 0 else 1 + 5 * zeta


def evaporation_duct_m(sst_c: float, t_c: float, rh_pct: float, u10: float, z_r: float = 2.0,
                       z0: float = 1.5e-4) -> tuple[float | None, str]:
    """Evaporation duct height (m) by a bulk Monin-Obukhov profile of potential refractivity
    (Paulus/NPS style) from 2 m air temperature and humidity. A simplified bulk method: it runs
    about 30 % low against Paulus-Jeske in hot, humid unstable air (Gulf summer). Returns (height, flag): flag 'stable' when the air is warmer than the sea
    (Ri_b > 0.1; height unreliable, often 30 m or more, a surface-based duct is possible)."""
    e_s = 0.98 * es_hpa(sst_c)
    e_a = es_hpa(t_c) * rh_pct / 100.0
    if e_a >= e_s:  # moist air over cooler water: no evaporation, no duct
        return 0.0, "none"
    n_s = refractivity(sst_c, e_s)
    n_a = refractivity(t_c, e_a) + 0.0  # potential refractivity at z_r; pressure change over 10 m ignored
    dn = n_a - n_s                       # negative: refractivity falls with height
    u = max(1.0, u10)
    tv_a = (t_c + 273.15) * (1 + 0.61 * 0.622 * e_a / 1013.25)
    tv_s = (sst_c + 273.15) * (1 + 0.61 * 0.622 * e_s / 1013.25)
    rib = G * z_r * (tv_a - tv_s) / (0.5 * (tv_a + tv_s) * u * u)
    if rib > 0.1 or t_c - sst_c > 0.5:  # air warmer than the sea: stable surface layer
        return None, "stable"
    lnz = math.log(z_r / z0)
    zeta_r = rib * lnz if rib < 0 else rib * lnz / max(0.2, 1 - 5 * rib)
    big_l = z_r / zeta_r if abs(zeta_r) > 1e-9 else 1e12
    denom = lnz - _psi_m(z_r / big_l)

    def grad(z):  # dN/dz + 0.157 (the modified-refractivity gradient)
        return dn * _phi(z / big_l) / (denom * z) + 0.157
    lo, hi = 0.05, 40.0
    if grad(hi) < 0:
        return 40.0, "capped"
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if grad(mid) < 0:
            lo = mid
        else:
            hi = mid
    return round(0.5 * (lo + hi), 1), "ok"


def duct_trap_ghz(h_m: float) -> float:
    """Lowest frequency an evaporation duct of height h traps (approximate lower bound, 130 h^-1.5 GHz;
    the literature spread is 130-360)."""
    return 130.0 * max(0.5, h_m) ** -1.5


# ITU-R P.838-3, horizontal polarisation: f GHz -> (k, alpha)
P838 = {3.0: (1.390e-4, 1.2322), 5.5: (3.906e-4, 1.6430), 10.0: (1.217e-2, 1.2571), 15.0: (4.481e-2, 1.1233),
        35.0: (0.3374, 0.9047)}
BANDS = {"S": 3.0, "C": 5.5, "X": 10.0, "Ku": 15.0, "Ka": 35.0}


def rain_atten_db_km(rain_mm_h: float, band: str) -> float:
    k, a = P838[BANDS[band]]
    return k * max(0.0, rain_mm_h) ** a


def sea_clutter_db(sea_state: int, grazing_deg: float, f_ghz: float = 10.0) -> float:
    """NRL sea-clutter reflectivity sigma0 (dB m2/m2), horizontal polarisation."""
    psi = max(0.1, grazing_deg)
    return (-73.00 + 20.78 * math.log10(math.sin(psi * RAD)) + (27.5 + 7.351 * psi) * math.log10(f_ghz) / (1 + 0.95 * psi)
            + 25.65 * (sea_state + 1) ** (1 / (2 + 0.085 * psi + 0.033 * sea_state)) + 0.00540 * psi * psi)


def _i0(x):
    s, t = 1.0, 1.0
    for k in range(1, 30):
        t *= (x / 2) ** 2 / (k * k)
        s += t
    return s


def multipath(hs_m: float, f_ghz: float, h_radar: float = 20.0, h_target: float = 5.0) -> dict:
    """Rough-sea reflection coefficient (Miller-Brown-Vegh) at 1 and 0.1 degree grazing, and the
    flat-earth range of the outermost lobe peak R1 = 4 h_r h_t / lambda."""
    lam = 0.2998 / f_ghz
    out = {"R1_km": 4 * h_radar * h_target / lam / 1000.0}
    sig = hs_m / 4.0
    for psi in (1.0, 0.115):
        x = 2 * (2 * math.pi * sig * math.sin(psi * RAD) / lam) ** 2
        out[f"rho_{psi:g}deg"] = math.exp(-x) * _i0(x) if x < 50 else (1 / math.sqrt(2 * math.pi * x))
    return out


# ------------------------------------------------------------------ EO/IR
def ir_range_factor(t_c: float, rh_pct: float, rain_mm_h: float, vis_km: float, band: str = "LWIR",
                    ref_km: float = 10.0) -> float:
    """Detection range relative to a reference atmosphere (water vapour 7.5 g/m3, 23 km visibility)
    for a point target: solves exp(-s R)/R^2 = exp(-s0 R0)/R0^2."""
    def ext(rho, rain, vis):
        k_wv = (0.10 + 0.0017 * rho * rho + 0.04 * rho) if band == "LWIR" else (0.15 + 0.03 * rho)
        k_rain = 1.076 * rain ** 0.67 if rain > 0 else 0.0
        k_aer = 4.34 * 3.912 / max(0.05, vis) * 0.3
        return (k_wv + k_rain + k_aer) / 4.343  # 1/km
    s0 = ext(7.5, 0.0, 23.0)
    s = ext(abs_humidity_gm3(t_c, rh_pct), rain_mm_h, vis_km)
    target = -s0 * ref_km - 2 * math.log(ref_km)
    lo, hi = 0.01, 200.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if -s * mid - 2 * math.log(mid) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi) / ref_km


def _jd(t: dt.datetime) -> float:
    return (t - dt.datetime(2000, 1, 1, 12, tzinfo=dt.timezone.utc)).total_seconds() / 86400.0 + 2451545.0


def sun_moon(t: dt.datetime) -> dict:
    """Low-precision sun and moon (Meeus / Astronomical Almanac): ecliptic longitudes, the moon's
    right ascension and declination, and the illuminated fraction (good to about 1 %)."""
    d = _jd(t) - 2451545.0
    # sun
    g = (357.529 + 0.98560028 * d) * RAD
    q = 280.459 + 0.98564736 * d
    lam_s = (q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360
    # moon (main periodic terms)
    lp = (218.3165 + 13.17639648 * d) % 360
    dm = (297.8502 + 12.19074912 * d) * RAD
    ms = (357.5291 + 0.98560028 * d) * RAD
    mm = (134.9634 + 13.06499295 * d) * RAD
    ff = (93.2721 + 13.22935024 * d) * RAD
    lam_m = (lp + 6.289 * math.sin(mm) + 1.274 * math.sin(2 * dm - mm) + 0.658 * math.sin(2 * dm)
             + 0.214 * math.sin(2 * mm) - 0.186 * math.sin(ms) - 0.114 * math.sin(2 * ff)) % 360
    beta = 5.128 * math.sin(ff) + 0.281 * math.sin(mm + ff) + 0.278 * math.sin(mm - ff) + 0.173 * math.sin(2 * dm - ff)
    eps = (23.439 - 0.0000004 * d) * RAD
    lr, br = lam_m * RAD, beta * RAD
    ra = math.atan2(math.sin(lr) * math.cos(eps) - math.tan(br) * math.sin(eps), math.cos(lr))
    dec = math.asin(math.sin(br) * math.cos(eps) + math.cos(br) * math.sin(eps) * math.sin(lr))
    elong = math.acos(math.cos(br) * math.cos((lam_m - lam_s) * RAD))
    phase_angle = math.pi - elong  # adequate for illumination
    frac = (1 + math.cos(phase_angle)) / 2
    waxing = ((lam_m - lam_s) % 360) < 180
    return {"moon_ra": ra, "moon_dec": dec, "illum": frac, "waxing": waxing, "phase_angle_deg": phase_angle / RAD, "d": d}


def moon_light(t: dt.datetime, lat: float, lon: float, cloud_pct: float) -> dict:
    """Moon altitude and illuminance on the ground (lux) with a cloud factor."""
    sm = sun_moon(t)
    gmst = (280.46061837 + 360.98564736629 * sm["d"]) % 360
    ha = (gmst + lon) * RAD - sm["moon_ra"]
    alt = math.asin(math.sin(lat * RAD) * math.sin(sm["moon_dec"]) + math.cos(lat * RAD) * math.cos(sm["moon_dec"]) * math.cos(ha))
    a = sm["phase_angle_deg"]
    okta = max(0.0, min(8.0, cloud_pct / 100 * 8))
    cloud = max(0.15, 1 - 0.75 * (okta / 8) ** 3.4)
    floor = 1e-3 if okta < 6 else 1e-4
    if alt <= 0:
        lux = floor
    else:
        airmass = 1 / max(0.05, math.sin(alt))
        lux = 0.27 * 10 ** (-0.4 * (0.026 * a + 4e-9 * a ** 4)) * math.sin(alt) * 10 ** (-0.4 * 0.2 * airmass) * cloud
        lux = max(floor, lux)
    return {"illum": sm["illum"], "waxing": sm["waxing"], "alt_deg": alt / RAD, "lux": lux}


def sun_alt_deg(t: dt.datetime, lat: float, lon: float) -> float:
    d = _jd(t) - 2451545.0
    g = (357.529 + 0.98560028 * d) * RAD
    lam = (280.459 + 0.98564736 * d + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) * RAD
    eps = 23.439 * RAD
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps) * math.sin(lam))
    gmst = (280.46061837 + 360.98564736629 * d) % 360
    ha = (gmst + lon) * RAD - ra
    return math.asin(math.sin(lat * RAD) * math.sin(dec) + math.cos(lat * RAD) * math.cos(dec) * math.cos(ha)) / RAD


# ------------------------------------------------------------------ derive
def derive(values: dict, lat: float, lon: float, when: dt.datetime, theatre: str | None = None) -> SensorEnv:
    """SensorEnv for one weather sample. Missing inputs fall back to the theatre table or
    climatology at lower confidence; nothing raises on a sparse sample."""
    th = THEATRES.get(theatre or "", {})
    it = {}
    u, v = values.get("wind_u10_ms"), values.get("wind_v10_ms")
    u10 = math.hypot(u, v) if u is not None and v is not None else 7.0
    hs = values.get("wave_hs_m")
    ss = wmo_sea_state(hs) if hs is not None else 4
    rain = values.get("precip_rate_mm_h") or 0.0
    t_air = values.get("air_temp_2m_c")
    t_air = 15.0 if t_air is None else t_air
    sst = values.get("sst_c")
    sst_src = "snapshot"
    if sst is None:
        sst, sst_src = t_air - th.get("air_sea", -0.5), "derived (air temperature + typical air-sea difference)"
    td = values.get("dewpoint_2m_c")
    if td is not None:
        rh, rh_src = min(100.0, 100 * es_hpa(td) / es_hpa(t_air)), "snapshot"
    else:
        rh, rh_src = th.get("rh", 78.0), "table"
    vis = values.get("visibility_km")
    cloud = values.get("cloud_fraction_pct")
    cloud = 50.0 if cloud is None else cloud
    depth = th.get("depth", "deep")

    # sonar
    it["game_ambient_db"] = Item(GAME_SONAR["BaseAmbientOceanNoise"] + GAME_SONAR["PerSeaStateNoise"] * ss
                                 + (GAME_SONAR["RainNoise"] if rain >= 0.5 else 0.0), "dB", "game", "derived", "high",
                                 f"base 60 + 5 x SeaState {ss}" + (" + rain 15" if rain >= 0.5 else ""))
    h_clim, h = mixed_layer_m(lat, when, u10, depth)
    it["mixed_layer_m"] = Item(round(h), "m", "real", "derived", "low", f"seasonal climatology {round(h_clim)} m, wind-deepened")
    cls, (xmin, xmax) = layer_class(lat, when, depth)
    it["layer"] = Item(cls, "", "real", "climatology", "low", "the game computes its own layer: its depth readout governs")
    it["layer_loss_suggest_db"] = Item((xmin, xmax), "dB", "suggest", "climatology", "low", "Min/MaxXLayerAttenuation (game 6/12)")
    it["duct_cutoff_hz"] = Item(round(duct_cutoff_hz(h)), "Hz", "real", "derived", "low", "surface duct traps sound above about 3x this")
    it["ambient_suggest_db"] = Item(round(ambient_suggest(th.get("shipping", 0.0), ss, th.get("shallow_strait", False)), 1),
                                    "dB", "suggest", "table", "med", "BaseAmbientOceanNoise (game 60); shipping only")
    it["rain_noise_suggest_db"] = Item(round(rain_noise_suggest(rain, ss), 1), "dB", "suggest", "derived", "med",
                                       "RainNoise (game 15) scaled to the rain rate and the wind noise")
    cz = th.get("cz", "unknown") if th else "unknown"
    it["convergence_zones"] = Item(cz, "nm", "real", "table", "med" if th else "low",
                                   th.get("cz_note", "theatre unknown: deep water needed (game: depth > 3000 ft, 30 and 60 nm)"))
    # radar
    edh, flag = evaporation_duct_m(sst, t_air, rh, u10)
    it["evap_duct_m"] = Item(edh, "m", "real", "derived", "low" if sst_src != "snapshot" or rh_src != "snapshot" else "med",
                             {"stable": "air warmer than sea: duct unreliable, surface-based duct possible",
                              "none": "no evaporation duct", "capped": "40 m or more"}.get(flag, ""))
    if edh:
        it["evap_duct_traps_above_ghz"] = Item(round(duct_trap_ghz(edh), 1), "GHz", "real", "derived", "low",
                                               "approximate lower bound; X-band and above are trapped when this is below 10")
    it["rain_atten_db_km"] = Item({b: round(rain_atten_db_km(rain, b), 4) for b in BANDS}, "dB/km one way", "real", "derived",
                                  "med", "ITU-R P.838-3, horizontal; two-way is double")
    it["sea_clutter_x_1deg_db"] = Item(round(sea_clutter_db(min(ss, 6), 1.0), 1), "dB", "real", "derived", "med", "NRL model, X band")
    it["multipath_x"] = Item({k: round(val, 3) for k, val in multipath(hs or 1.5, 10.0).items()}, "", "real", "derived", "low",
                             "20 m radar, 5 m target: outermost lobe R1 and reflection coefficients")
    # EO/IR, night, decks
    it["visibility_km"] = Item(None if vis is None else round(vis, 2), "km", "game" if vis is not None and vis < 1 else "real",
                               "snapshot", "med", "the game's Fog flag is visibility < 1 km without rain")
    it["ir_range_factor_lwir"] = Item(round(ir_range_factor(t_air, rh, rain, vis or 23.0, "LWIR"), 2), "x", "real", "derived", "low",
                                      "vs a 7.5 g/m3, 23 km reference at 10 km")
    it["ir_range_factor_mwir"] = Item(round(ir_range_factor(t_air, rh, rain, vis or 23.0, "MWIR"), 2), "x", "real", "derived", "low", "")
    ml = moon_light(when, lat, lon, cloud)
    sun = sun_alt_deg(when, lat, lon)
    it["sun_alt_deg"] = Item(round(sun, 1), "deg", "real", "derived", "high", "night below -12 (game lighting presets)")
    it["moon"] = Item({"illum_pct": round(100 * ml["illum"]), "waxing": ml["waxing"], "alt_deg": round(ml["alt_deg"], 1),
                       "lux": float(f"{ml['lux']:.2g}")}, "", "real", "derived", "high", "")
    tdew = td if td is not None else dewpoint_c(t_air, rh)
    base = max(30.0, 125.0 * (t_air - tdew))
    it["cloud_base_m"] = Item(round(base) if cloud >= 62.5 else None, "m", "real", "derived",
                              "med" if td is not None else "low", "ceiling (5 oktas or more); the game draws its deck at 3000-4000 ft")
    it["game_sea_state"] = Item(ss, "", "game", "derived", "high", "drives ambient noise and the helicopter landing limit")
    return SensorEnv(lat, lon, when.isoformat(), theatre, it)
