"""MnoEnvGlobeLayer reference maths: pixel <-> geography for overlay rasters. BUILD-TESTED.

Three views, the ones a Sea Power or DCM map is likely to need (ENV-00 records which the
game actually uses):
- Equirectangular (plate carree) world texture, the usual input to a textured sphere mesh:
  u = (lon - lon0) / 360, v = (90 - lat) / 180, sampled at pixel centres. A texture whose
  lon0 is -180 has its seam at the antimeridian; texels either side sample longitudes
  -180 + 0.5/W*360 and 180 - 0.5/W*360, so the raster is continuous across the seam.
- Polar stereographic window (EPSG:3976 south / 3413 north), square, centred on the pole.
- A layer is built from immutable inputs (snapshot frame, field, palette) into a new RGBA
  buffer; nothing is mutated in place, so a renderer can double-buffer by reference.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .geo import wrap_lon


@dataclass(frozen=True)
class Equirect:
    width: int
    height: int
    lon0: float = -180.0

    def pixel_to_geo(self, px: float, py: float) -> tuple[float, float]:
        lon = self.lon0 + (px + 0.5) / self.width * 360.0
        lat = 90.0 - (py + 0.5) / self.height * 180.0
        return lat, wrap_lon(lon)

    def geo_to_pixel(self, lat: float, lon: float) -> tuple[float, float]:
        px = ((lon - self.lon0) % 360.0) / 360.0 * self.width - 0.5
        py = (90.0 - lat) / 180.0 * self.height - 0.5
        return px, py


@dataclass(frozen=True)
class PolarWindow:
    projection: object
    size: int
    half_extent_m: float

    def pixel_to_geo(self, px: float, py: float):
        x = ((px + 0.5) / self.size * 2 - 1) * self.half_extent_m
        y = (1 - (py + 0.5) / self.size * 2) * self.half_extent_m
        return self.projection.inverse(x, y)

    def geo_to_pixel(self, lat: float, lon: float):
        x, y = self.projection.forward(lat, lon)
        return ((x / self.half_extent_m + 1) / 2 * self.size - 0.5, (1 - y / self.half_extent_m) / 2 * self.size - 0.5)


def debug_colour(lat: float, lon: float) -> tuple[int, int, int, int]:
    """Georeferencing test pattern: hue follows longitude continuously (no break at +-180),
    10-degree checker in brightness, a magenta band on the antimeridian, cyan at the equator,
    and white rings at 60 and 80 degrees of latitude."""
    if abs(wrap_lon(lon + 180.0)) < 1.0:
        return (255, 0, 255, 255)
    if abs(lat) < 0.6:
        return (0, 255, 255, 255)
    if any(abs(abs(lat) - r) < 0.35 for r in (60.0, 80.0)):
        return (255, 255, 255, 255)
    h = ((lon + 180.0) / 360.0) % 1.0
    checker = (math.floor((lon + 180) / 10) + math.floor((lat + 90) / 10)) % 2
    v = 0.85 if checker else 0.6
    i = int(h * 6) % 6
    f = h * 6 - math.floor(h * 6)
    p_, q, t = v * 0.35, v * (1 - 0.65 * f), v * (1 - 0.65 * (1 - f))
    r, g, b = [(v, t, p_), (q, v, p_), (p_, v, t), (p_, q, v), (t, p_, v), (v, p_, q)][i]
    return (int(r * 255), int(g * 255), int(b * 255), 160)


PALETTES = {
    # field -> (min, max, colour at max, alpha at max); linear ramp from transparent
    "cloud_fraction_pct": (20.0, 100.0, (235, 238, 245), 200),
    "precip_rate_mm_h": (0.2, 8.0, (40, 110, 255), 220),
    "sea_ice_conc_pct": (15.0, 100.0, (225, 245, 255), 235),
    "wave_hs_m": (2.0, 10.0, (255, 120, 30), 190),
}


def field_colour(name: str, value) -> tuple[int, int, int, int]:
    if value is None:
        return (0, 0, 0, 0)
    lo, hi, rgb, amax = PALETTES[name]
    f = (value - lo) / (hi - lo)
    if f <= 0:
        return (0, 0, 0, 0)
    f = min(1.0, f)
    return (*rgb, int(amax * f))


def build_layer(view, sampler, name: str | None) -> bytes:
    """New RGBA buffer for one view. sampler(lat, lon) -> value; name None = debug pattern.
    Pixels outside the projection domain (none for these views) stay transparent."""
    out = bytearray(view_size(view) * 4)
    w, h = view_dims(view)
    k = 0
    for py in range(h):
        for px in range(w):
            lat, lon = view.pixel_to_geo(px, py)
            c = debug_colour(lat, lon) if name is None else field_colour(name, sampler(lat, lon))
            out[k:k + 4] = bytes(c)
            k += 4
    return bytes(out)


def view_dims(view) -> tuple[int, int]:
    return (view.width, view.height) if isinstance(view, Equirect) else (view.size, view.size)


def view_size(view) -> int:
    w, h = view_dims(view)
    return w * h


def layer_bytes(width: int, height: int, fmt: str = "RGBA32") -> int:
    return width * height * {"RGBA32": 4, "R8": 1, "RG16": 2}[fmt]
