"""MNO/GCO environment prototype: deterministic demonstration, NOT a weather forecast.
All coordinates WGS84 and times UTC. Public interface is a JSON v0.1 world grid.
Uses only the Python standard library; intended to be reusable beyond Sea Power.
"""
from __future__ import annotations
import datetime as dt
import json
import math
from pathlib import Path

UTC = dt.timezone.utc
DEFAULT_EPOCH = dt.datetime(2028, 9, 14, 6, tzinfo=UTC)
GRID = {"lon_min": -180, "lat_min": -90, "lon_step": 4, "lat_step": 4, "nx": 91, "ny": 46}
FIELD_UNITS = {"cloud_pct": "%", "precip_mm_h": "mm/h", "wind_ms": "m/s", "pressure_hpa": "hPa", "wave_m": "m significant", "ice_pct": "%", "wind_u_ms": "m/s", "wind_v_ms": "m/s"}
STORMS = [
    # Initial lat, lon; trajectory in degrees / 6h; core deficit, breadth, wind contribution
    (-54, -49, -0.15, 2.9, 41, 12.0, 16.0),
    (-48, 14, -0.05, 2.5, 31, 13.0, 12.0),
    (-52, 100, 0.05, 2.1, 37, 12.0, 13.0),
    (47, -49, 0.11, 2.6, 30, 10.0, 10.0),
    (-18, 147, -0.05, -0.65, 18, 7.0, 10.0),
]

def wrap_lon(value: float) -> float:
    """Wrap to [-180, 180); correctly handles anti-meridian crossings."""
    return (value + 180) % 360 - 180


def lon_distance(a: float, b: float) -> float:
    return wrap_lon(a - b)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def logistic(value: float) -> float:
    return 1 / (1 + math.exp(-clamp(value, -35, 35)))


def field_at(lat: float, lon: float, tick: int, season: str = "winter") -> dict[str, float]:
    """Illustrative bounded dynamic storm/ice field; not physically assimilated or validated."""
    rad = math.pi / 180
    u = 2.0 + 8.0 * math.exp(-((abs(lat) - 51) / 16) ** 2)
    v = 1.5 * math.sin(lon * rad * 1.8)
    p = 1016.0 - 3.0 * math.sin(lat * rad) ** 2
    cloud = 18.0 + 17.0 * math.sin((lon + lat * 0.75 + tick * 2) * rad * 2) ** 2
    rain = 0.02
    swell = 0.9 + 0.5 * math.exp(-((abs(lat) - 50) / 18) ** 2)
    for start_lat, start_lon, v_lat, v_lon, deficit, radius, wind in STORMS:
        cy = start_lat + tick * v_lat
        cx = wrap_lon(start_lon + tick * v_lon)
        dx = lon_distance(lon, cx) * max(0.22, math.cos(lat * rad))
        dy = lat - cy
        dist = math.hypot(dx, dy)
        bell = math.exp(-0.5 * (dist / radius) ** 2)
        core = math.exp(-0.5 * (dist / (radius * 0.68)) ** 2)
        p -= deficit * core
        # Southern Hemisphere cyclones rotate clockwise; North counter-clockwise.
        rot = -1 if cy < 0 else 1
        shear = wind * bell * (dist / max(1.0, radius * 0.55)) / (1 + (dist / max(1.0, radius * 0.55)) ** 2) * 2.25
        u += rot * -dy / max(1, dist) * shear
        v += rot * dx / max(1, dist) * shear
        # Frontal rain bands shifted to the east (with a narrow centre and broader wrap).
        angle = math.atan2(dy, dx)
        front = math.exp(-((dist - radius * 0.85) / (radius * 0.32)) ** 2)
        band = 0.55 + 0.45 * math.sin(2 * angle - tick * 0.18 + 0.6) ** 2
        cloud += 71 * bell + 20 * front * band
        rain += 4.8 * front * band + 1.8 * core
        swell += 4.4 * bell
    wind_ms = math.hypot(u, v)
    wave = clamp(0.6 + 0.15 * wind_ms + 0.30 * swell, 0.2, 13.5)
    # Two schematic seasonal curves; not derived from observed ice data.
    # Higher concentration poleward of the moving ice edge. Longitude encodes geography.
    if season == "summer":
        south_edge = -72.5 + 2.2 * math.cos((lon - 8) * rad * 1.3)
        north_edge = 68.5 + 3.2 * math.cos((lon + 35) * rad)
    else:
        south_edge = -61.0 + 3.0 * math.cos((lon - 5) * rad * 1.4)
        north_edge = 78.0 + 2.3 * math.cos((lon + 45) * rad)
    south_drift = 0.36 * math.sin(tick * 0.4 + lon * rad * 2)
    north_drift = 0.25 * math.cos(tick * 0.35 + lon * rad)
    ice_south = 98 * logistic((south_edge + south_drift - lat) / 2.2)
    ice_north = 98 * logistic((lat - north_edge - north_drift) / 2.4)
    # Illustrative Weddell and Ross tongues; raster is masked by coastlines for visualisation.
    ice_south += 8 * math.exp(-((lon_distance(lon, -34) / 18) ** 2)) * math.exp(-((lat + 64) / 5) ** 2)
    ice = clamp(max(ice_south, ice_north), 0, 100)
    # Broad cloud coverage from fronts, not pixel-accurate observed clouds.
    return {
        "cloud_pct": round(clamp(cloud, 0, 100)),
        "precip_mm_h": round(clamp(rain, 0, 35), 1),
        "wind_ms": round(clamp(wind_ms, 0, 55), 1),
        "pressure_hpa": round(clamp(p, 925, 1060), 1),
        "wave_m": round(wave, 1),
        "ice_pct": round(ice),
        "wind_u_ms": round(clamp(u, -55, 55), 1),
        "wind_v_ms": round(clamp(v, -55, 55), 1),
    }


def generate_grid(ticks: int = 13, hours_step: int = 6, *, epoch: dt.datetime = DEFAULT_EPOCH, season: str = "winter") -> dict:
    assert 1 <= ticks <= 256 and 1 <= hours_step <= 24
    assert epoch.tzinfo is not None
    frames = []
    for tick in range(ticks):
        fields = {key: [] for key in FIELD_UNITS}
        for j in range(GRID["ny"]):
            lat = GRID["lat_min"] + j * GRID["lat_step"]
            for i in range(GRID["nx"]):
                lon = GRID["lon_min"] + i * GRID["lon_step"]
                data = field_at(lat, lon, tick * hours_step / 6.0, season)
                for key in fields:
                    fields[key].append(data[key])
        frames.append({"time_utc": (epoch + dt.timedelta(hours=hours_step * tick)).isoformat().replace("+00:00", "Z"), "fields": fields})
    return {"schema": "mno.env.grid.v0.1", "source": {"type": "SYNTHETIC_DEMONSTRATION_NOT_REAL_WEATHER", "seed": "mno-env-1", "method": "bounded cyclonic analytic fields; unvalidated", "intended_use": "UI/serialization/mission weather trigger integration tests only"}, "grid": GRID, "field_units": FIELD_UNITS, "time_step_hours": hours_step, "season": season, "frames": frames}


def bilinear(grid: dict, frame_index: int, lat: float, lon: float, field: str) -> float:
    g = grid["grid"]
    if field not in FIELD_UNITS:
        raise KeyError(field)
    latitude = clamp(lat, -90, 90)
    long_normal = wrap_lon(lon)
    x = (long_normal - g["lon_min"]) / g["lon_step"]
    y = (latitude - g["lat_min"]) / g["lat_step"]
    i = min(g["nx"] - 2, max(0, int(math.floor(x))))
    j = min(g["ny"] - 2, max(0, int(math.floor(y))))
    fx, fy = x - i, y - j
    values = grid["frames"][frame_index]["fields"][field]
    def get(ix, iy):
        return values[iy * g["nx"] + ix]
    return ((1 - fy) * ((1 - fx) * get(i, j) + fx * get(i + 1, j)) +
            fy * ((1 - fx) * get(i, j + 1) + fx * get(i + 1, j + 1)))


def great_circle_nm(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    x = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 3440.065 * 2 * math.asin(math.sqrt(clamp(x, 0, 1)))


def eval_route(grid: dict, points: list[list[float]], frame: int = 0, ice_capable: bool = False) -> dict:
    """Illustrative navigation risk index for GCO preview. NOT route planning advice."""
    assert 2 <= len(points) <= 30
    nm, ice_peak, wave_peak, severe = 0, 0, 0, 0
    for a, b in zip(points, points[1:]):
        dist = great_circle_nm(tuple(a), tuple(b))
        nm += dist
        n = max(3, math.ceil(dist / 55))
        for step in range(n + 1):
            q = step / n
            lat = a[0] + (b[0] - a[0]) * q
            lon = wrap_lon(a[1] + lon_distance(b[1], a[1]) * q)
            ice = bilinear(grid, frame, lat, lon, "ice_pct")
            wave = bilinear(grid, frame, lat, lon, "wave_m")
            ice_peak = max(ice_peak, ice)
            wave_peak = max(wave_peak, wave)
            severe += int(ice > (50 if ice_capable else 15) or wave > 7)
    return {"distance_nm": round(nm), "peak_sea_ice_pct": round(ice_peak), "peak_wave_m": round(wave_peak, 1), "hazard_samples": severe,
            "access": "restricted" if ice_peak > (75 if ice_capable else 15) else ("caution" if severe else "open"),
            "disclaimer": "Illustrative index, not a vessel-certified ice route decision"}


def build_demo(path: Path, season: str = "winter") -> dict:
    data = generate_grid(season=season)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    return data
