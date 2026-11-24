"""Iceberg climatology and a deterministic iceberg generator. BUILD-TESTED (offline). OFF by default.

What it does:
- density(lat, lon, month): bergs per 10,000 km2 for each size class, from the regional
  monthly table in data/iceberg-climatology.json.
- generate(bbox, when, seed): a repeatable list of bergs for an area and a date. Each berg has
  a class, waterline length, height, draft, mass, position (never on land, never on an ice
  shelf), drift velocity and, given a sea temperature, its expected remaining life.
- Sensor hooks: radar range by class and sea state, visual range by visibility, and a sonar
  false-contact design index.

Realism notes:
- The size classes are the published IIP / MANICE scale (high confidence).
- The North Atlantic season comes from IIP counts of bergs crossing 48N (high confidence).
- Almost every DENSITY is an order-of-magnitude ESTIMATE. No citable per-area iceberg density
  table was found. Each number in the JSON carries its source and a confidence label.
- Giant tabular bergs (NIC tracking size, 10 nmi or more) are never generated. They are real,
  named objects; load them with ice.load_icebergs from an observation file.

Nothing here makes a network call. The game does not load this module. It is used only when
the owner sets the environment feature flag (mno_env.FEATURE_FLAG); see docs/environment/ICEBERGS.md.
"""
from __future__ import annotations

import calendar
import json
import math
import random
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

from .geo import wrap_lon

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "iceberg-climatology.json"
CATEGORIES = ("growler", "bergy_bit", "small", "medium", "large", "very_large", "tabular")
BERG_CLASSES = ("small", "medium", "large", "very_large", "tabular")  # the IIP-countable classes
EARTH_R_KM = 6371.0
MS_TO_KNOTS = 1.943844
KM_PER_NM = 1.852


@lru_cache(maxsize=1)
def climatology() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _in_box(lat: float, lon: float, box) -> bool:
    la0, la1, lo0, lo1 = box
    if not (la0 <= lat <= la1):
        return False
    lon = wrap_lon(lon)
    if lo0 <= lo1:
        return lo0 <= lon <= lo1
    return lon >= lo0 or lon <= lo1  # box crosses 180


def region_at(lat: float, lon: float) -> dict | None:
    """The first region of the table that holds the point, or None (no modelled bergs)."""
    for r in climatology()["regions"]:
        if any(_in_box(lat, lon, b) for b in r["boxes"]):
            return r
    return None


def _monthly_peak(region: dict) -> list[float]:
    """Bergs (small and larger) per 10,000 km2 for each month."""
    if region.get("density_from") == "iip":
        iip = climatology()["iip"]
        res = iip["residence_months_south_of_48n"]["value"]
        units = iip["area_south_of_48n_km2"]["value"] / 1e4
        return [c * res / units for c in iip["crossings_48n_monthly"]["value"]]
    return [region["density"] * f for f in region["monthly"]]


def _month_value(series: list[float], month: float) -> float:
    """month 1..12 is mid-month; fractions interpolate to the next month (cyclic)."""
    m = (float(month) - 1.0) % 12.0
    i = int(m)
    f = m - i
    return series[i] * (1 - f) + series[(i + 1) % 12] * f


def fractional_month(when) -> float:
    """1.0 on the 15th of January (mid-month), 1.5 at the turn of January to February."""
    days = calendar.monthrange(when.year, when.month)[1]
    return when.month + (when.day - 15.0) / days


def density(lat: float, lon: float, month: float) -> dict:
    """Bergs per 10,000 km2 of water for each size class (ESTIMATE; see the JSON sources).
    Land is not checked here. Zero everywhere outside the listed regions."""
    out = dict.fromkeys(CATEGORIES, 0.0)
    r = region_at(lat, lon)
    if r is None:
        return out
    doc = climatology()["counting"]
    total = _month_value(_monthly_peak(r), month)
    mix = doc["mix"][r["mix"]]
    for c in BERG_CLASSES:
        out[c] = total * mix[c]
    out["bergy_bit"] = total * doc["bergy_bits_per_berg"]["value"]
    out["growler"] = total * doc["growlers_per_berg"]["value"]
    return out


# ------------------------------------------------------------------ geometry
def _dims(category: str, rng: random.Random) -> dict:
    doc = climatology()
    cat, geo = doc["categories"][category], doc["geometry"]
    t = rng.random()
    l0, l1 = cat["length_m"]
    h0, h1 = cat["height_m"]
    if category == "tabular":
        length = math.exp(math.log(l0) + t * (math.log(l1) - math.log(l0)))  # many small, few big (estimate)
        height = h0 + rng.random() * (h1 - h0)
        f0, f1 = geo["tabular_freeboard_fraction"]["value"]
        thick = height / (f0 + rng.random() * (f1 - f0))
        draft = thick - height
        width = length * (0.6 + 0.3 * rng.random())
        mass_t = length * width * thick * geo["shelf_ice_density_kgm3"]["value"] / 1000
    else:
        length = l0 + t * (l1 - l0)
        u = min(1.0, max(0.0, t + 0.3 * (rng.random() - 0.5)))  # height loosely follows length
        height = h0 + u * (h1 - h0)
        r0, r1 = geo["draft_to_length"]["value"]
        draft = min(geo["draft_max_m"]["value"], max(1.2 * height, length * (r0 + rng.random() * (r1 - r0))))
        w0, w1 = geo["width_to_length"]["value"]
        width = length * (w0 + rng.random() * (w1 - w0))
        mass_t = (geo["block_coefficient"]["value"] * length * width * (height + draft)
                  * geo["glacier_ice_density_kgm3"]["value"] / 1000)
    return {"length_m": round(length, 1), "width_m": round(width, 1), "height_m": round(height, 2),
            "draft_m": round(draft, 1), "mass_t": float(f"{mass_t:.2g}")}  # two significant figures


# ------------------------------------------------------------------ melt
def sea_state_from_wind(wind_ms: float) -> float:
    """Martin and Adcroft 2010 sea-state proxy from the air-water speed difference."""
    w = abs(wind_ms)
    return 1.5 * math.sqrt(w) + 0.1 * w


def melt_rates(sst_c: float, length_m: float, sea_state: float, ice_frac: float = 0.0,
               rel_water_ms: float | None = None) -> dict:
    """Melt rates in m/day: basal, buoyant side convection and wave erosion (Bigg et al. 1997 /
    Martin and Adcroft 2010 form; coefficients recalled, see the JSON 'melt' block)."""
    m = climatology()["melt"]
    tf = m["freezing_point_c"]["value"]
    du = m["default_relative_water_speed_ms"]["value"] if rel_water_ms is None else abs(rel_water_ms)
    tw = sst_c
    basal = 0.58 * du ** 0.8 * max(0.0, tw - tf) / max(1.0, length_m) ** 0.2
    conv = max(0.0, 7.62e-3 * tw + 1.29e-3 * tw * tw) if tw > 0 else 0.0
    a = min(1.0, max(0.0, ice_frac))
    wave = max(0.0, (1 / 12) * sea_state * (1 + math.cos(math.pi * a ** 3)) * (tw + 2))
    return {"basal": basal, "convection": conv, "wave": wave}


def remaining_life_days(length_m: float, width_m: float, height_m: float, draft_m: float, sst_c: float,
                        sea_state: float | None = None, wind_ms: float | None = None, ice_frac: float = 0.0,
                        rel_water_ms: float | None = None) -> dict:
    """Days until the berg is gone (side under 1 m or thickness under 1 m) at a constant sea
    temperature and sea state. Capped at the JSON max life (about 5 years, Bigg et al. 1997).
    Roll-over and break-up are not modelled, so small bergs may last longer than here only if
    the water is near freezing and calm."""
    cap = climatology()["melt"]["max_life_days"]["value"]
    if sea_state is None:
        sea_state = sea_state_from_wind(wind_ms or 0.0)
    L, W, T = length_m, width_m, height_m + draft_m
    day = 0
    while day < cap:
        r = melt_rates(sst_c, L, sea_state, ice_frac, rel_water_ms)
        side = r["convection"] + r["wave"]
        L -= 2 * side
        W -= 2 * side
        T -= r["basal"]
        day += 1
        if min(L, W, T) < 1.0:
            return {"days": day, "capped": False}
        if side == 0 and r["basal"] == 0:
            break
    return {"days": cap, "capped": True}


# ------------------------------------------------------------------ generator
@dataclass(frozen=True)
class GeneratedBerg:
    berg_id: str
    category: str
    band: str                  # ice.py BERG_BANDS name (coarser game band)
    lat: float
    lon: float
    length_m: float
    width_m: float
    height_m: float
    draft_m: float
    mass_t: float
    region: str
    drift_u_ms: float
    drift_v_ms: float
    sea_ice_pct: float | None
    embedded_in_sea_ice: bool
    life_days: int | None
    life_capped: bool | None
    grounded: bool | None      # None when no water depth was given
    source: str = "mno_env.icebergs procedural (ESTIMATE densities)"

    def to_dict(self) -> dict:
        return asdict(self)


def _poisson(lam: float, rng: random.Random) -> int:
    if lam <= 0:
        return 0
    if lam > 50:  # normal approximation keeps big cells cheap
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    k, p, limit = 0, 1.0, math.exp(-lam)
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


@lru_cache(maxsize=1)
def _shelves():
    from .ice import load_shelves
    return tuple(load_shelves())


def _blocked(lat, lon, land) -> bool:
    if land.is_land(lat, lon):
        return True
    if lat < -60:
        return any(s.contains(lat, lon) for s in _shelves())
    return False


def _value_at(v, lat, lon):
    return v(lat, lon) if callable(v) else v


def generate(bbox, when, seed, cell_deg: float = 0.5, wind_ms=None, sst_c=None, current_ms=None,
             sea_state=None, edges: dict | None = None, land_mask=None, water_depth_m=None, max_bergs: int = 20000,
             categories=CATEGORIES) -> list[GeneratedBerg]:
    """Deterministic bergs inside bbox = (lat_min, lat_max, lon_min, lon_max) for a date.

    Bergs are drawn per global grid cell (cell_deg) with a random stream seeded by (seed, date,
    cell), so the same cell always holds the same bergs whatever the bbox. wind_ms, sst_c and
    current_ms may be values ((u, v) for vectors) or callables f(lat, lon). Without a current the
    region's current proxy (ESTIMATE) is used. Without an SST no life is computed. Pass edges
    from seaice.edges_on(when) to mark bergs frozen into sea ice (they are kept, not removed).
    Pass water_depth_m (value or callable; mno_env has no bathymetry of its own) to mark bergs
    whose draft reaches the sea bed as grounded, with zero drift (bergs do ground on the Grand
    Banks and on the Jakobshavn sill, about 250 m).
    lon_min > lon_max means the box crosses 180. Raises ValueError if max_bergs is exceeded."""
    from . import geo as _geo
    land = land_mask or _geo.default_land_mask()
    doc = climatology()
    lat0, lat1, lon0, lon1 = bbox
    if lat0 > lat1:
        raise ValueError("bbox lat_min > lat_max")
    span = (lon1 - lon0) % 360 or (360.0 if lon1 != lon0 else 0.0)
    month = fractional_month(when)
    date_key = when.strftime("%Y-%m-%d")
    wf = doc["drift"]["wind_factor"]
    bands = doc["bands_map"]
    out: list[GeneratedBerg] = []
    j0, j1 = math.floor(lat0 / cell_deg), math.floor(lat1 / cell_deg)
    i_start = math.floor(lon0 / cell_deg)
    i_count = int(math.ceil(span / cell_deg)) + 1
    seen = set()
    for j in range(j0, j1 + 1):
        clat0 = j * cell_deg
        clat_c = clat0 + cell_deg / 2
        for di in range(i_count):
            i_raw = i_start + di
            clon0 = wrap_lon(i_raw * cell_deg)
            i = math.floor(clon0 / cell_deg + 1e-9)
            if (j, i) in seen:
                continue
            seen.add((j, i))
            r = region_at(clat_c, clon0 + cell_deg / 2)
            if r is None:
                continue
            area = (EARTH_R_KM * math.radians(cell_deg)) ** 2 * math.cos(math.radians(clat_c))
            dens = density(clat_c, clon0 + cell_deg / 2, month)
            rng = random.Random(f"mno-icebergs|{seed}|{date_key}|{j}|{i}")
            for cat in CATEGORIES:  # fixed order keeps the stream stable
                n = _poisson(dens[cat] * area / 1e4, rng)
                for k in range(n):
                    plat = plon = None
                    for _ in range(8):  # a few tries to land in water
                        la = clat0 + rng.random() * cell_deg
                        lo = wrap_lon(clon0 + rng.random() * cell_deg)
                        if not _blocked(la, lo, land):
                            plat, plon = la, lo
                            break
                    dims = _dims(cat, rng)
                    if plat is None or cat not in categories:
                        continue
                    if not (lat0 <= plat <= lat1 and (plon - lon0) % 360 <= span):
                        continue
                    if region_at(plat, plon) is None:
                        continue
                    cur = _value_at(current_ms, plat, plon) if current_ms is not None else r["current_ms"]
                    wind = _value_at(wind_ms, plat, plon) if wind_ms is not None else (0.0, 0.0)
                    du = cur[0] + wf[cat] * wind[0]
                    dv = cur[1] + wf[cat] * wind[1]
                    grounded = None
                    if water_depth_m is not None:
                        depth = _value_at(water_depth_m, plat, plon)
                        grounded = depth is not None and dims["draft_m"] >= depth
                        if grounded:
                            du = dv = 0.0
                    conc = None
                    if edges is not None:
                        from .seaice import ice_at
                        conc = round(ice_at(plat, plon, edges), 1)
                    life = capped = None
                    sst = _value_at(sst_c, plat, plon) if sst_c is not None else None
                    if sst is not None:
                        ss = _value_at(sea_state, plat, plon) if sea_state is not None else None
                        res = remaining_life_days(dims["length_m"], dims["width_m"], dims["height_m"], dims["draft_m"],
                                                  sst, ss, math.hypot(*wind), (conc or 0.0) / 100)
                        life, capped = res["days"], res["capped"]
                    out.append(GeneratedBerg(
                        f"gen-{date_key}-{j}-{i}-{cat}-{k}", cat, bands[cat], round(plat, 4), round(plon, 4),
                        dims["length_m"], dims["width_m"], dims["height_m"], dims["draft_m"], dims["mass_t"],
                        r["id"], round(du, 3), round(dv, 3), conc, bool(conc is not None and conc >= 15.0),
                        life, capped, grounded))
                    if len(out) > max_bergs:
                        raise ValueError(f"more than {max_bergs} bergs: use a smaller bbox or fewer categories")
    return out


# ------------------------------------------------------------------ sensor hooks
def radar_range_factor(category: str, sea_state: int) -> float:
    """0..1 multiplier on calm-sea radar range; 0 means lost in sea clutter (ESTIMATE)."""
    f = climatology()["sensors"]["radar_sea_state_factor"][category]
    return f[max(0, min(9, int(sea_state)))]


def radar_detection_nm(category: str, sea_state: int, antenna_m: float = 20.0, height_m: float | None = None,
                       enhanced: bool = False) -> float:
    """Expected radar detection range in nm: the class's calm-sea range times the sea-state
    factor, capped by the radar horizon to the berg top (4/3 earth)."""
    from .sensors import radar_horizon_km
    s = climatology()["sensors"]
    base = s["radar_calm_nm"]["enhanced" if enhanced else "conventional"][category]
    if height_m is None:
        h0, h1 = climatology()["categories"][category]["height_m"]
        height_m = (h0 + h1) / 2
    horizon = radar_horizon_km(antenna_m, max(0.1, height_m)) / KM_PER_NM
    return round(min(base * radar_range_factor(category, sea_state), horizon), 2)


def visual_detection_nm(category: str, visibility_km: float, eye_m: float = 15.0, height_m: float | None = None,
                        night: bool = False) -> float:
    """Visual detection range in nm: the least of visibility, the geographic range (Bowditch) and,
    for growlers and bergy bits, a small-ice cap (ESTIMATE). Night without moon scales it down."""
    s = climatology()["sensors"]
    if height_m is None:
        h0, h1 = climatology()["categories"][category]["height_m"]
        height_m = (h0 + h1) / 2
    geo_nm = s["geographic_range_coefficient"]["value"] * (math.sqrt(eye_m) + math.sqrt(max(0.0, height_m)))
    rng_nm = min(max(0.0, visibility_km) / KM_PER_NM, geo_nm, s["visual_day_cap_nm"].get(category, geo_nm))
    if night:
        rng_nm *= s["visual_night_factor"]["value"]
    return round(rng_nm, 2)


def sonar_false_contact_index(category: str, draft_m: float | None = None, sonar_depth_m: float | None = None) -> float:
    """0..1 DESIGN INDEX of how likely a berg is to give a false submarine contact. Not a
    probability: no citable rates were found. Raised by keel depth; if a sonar depth is given,
    a keel that does not reach within 50 m of it (estimate) halves the index."""
    base = climatology()["sensors"]["sonar_false_contact_index"][category]
    if draft_m is not None and sonar_depth_m is not None and draft_m + 50.0 < sonar_depth_m:
        base *= 0.5
    return round(base, 3)


def drift_knots(berg: GeneratedBerg) -> tuple[float, float]:
    return berg.drift_u_ms * MS_TO_KNOTS, berg.drift_v_ms * MS_TO_KNOTS
