"""Regular lat/lon grids, seam-safe sampling, and regridding from polar grids. BUILD-TESTED."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .geo import wrap_lon


@dataclass(frozen=True)
class LatLonGrid:
    """Cell-centre grid. Row j has latitude lat_min + j*lat_step (south to north);
    column i has longitude lon_min + i*lon_step. Values are row-major, length nx*ny.
    A grid is global in longitude when nx*lon_step >= 360 (a duplicated seam column,
    nx*lon_step == 360 + lon_step, is accepted and handled)."""

    lon_min: float
    lat_min: float
    lon_step: float
    lat_step: float
    nx: int
    ny: int

    @classmethod
    def from_dict(cls, d: dict) -> "LatLonGrid":
        return cls(float(d["lon_min"]), float(d["lat_min"]), float(d["lon_step"]), float(d["lat_step"]), int(d["nx"]), int(d["ny"]))

    def to_dict(self) -> dict:
        return {"type": "regular_latlon", "crs": "EPSG:4326", "lon_min": self.lon_min, "lat_min": self.lat_min,
                "lon_step": self.lon_step, "lat_step": self.lat_step, "nx": self.nx, "ny": self.ny}

    @property
    def size(self) -> int:
        return self.nx * self.ny

    @property
    def global_lon(self) -> bool:
        return self.nx * self.lon_step >= 360.0 - 1e-9

    @property
    def period_cols(self) -> int:
        """Number of distinct columns around the globe (drops a duplicated seam column)."""
        return int(round(360.0 / self.lon_step)) if self.global_lon else self.nx

    def lat(self, j: int) -> float:
        return self.lat_min + j * self.lat_step

    def lon(self, i: int) -> float:
        return self.lon_min + i * self.lon_step

    def bounds(self) -> dict:
        return {"lat_min": self.lat_min, "lat_max": self.lat(self.ny - 1), "lon_min": self.lon_min, "lon_max": self.lon(self.nx - 1)}


def _is_missing(v, fill) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or (fill is not None and v == fill)


def bilinear(grid: LatLonGrid, values: Sequence, lat: float, lon: float, fill=None):
    """Bilinear sample. Longitude wraps across +-180 on global grids; latitude clamps at the
    grid edge. Missing corners are dropped and the weights renormalised; returns None when all
    four corners are missing, or when a regional grid does not contain the point."""
    y = (min(max(lat, grid.lat_min), grid.lat(grid.ny - 1)) - grid.lat_min) / grid.lat_step
    if grid.global_lon:
        x = ((lon - grid.lon_min) % 360.0) / grid.lon_step
    else:
        span_lon = grid.lon_min + (wrap_lon(lon - grid.lon_min) % 360.0)
        x = (span_lon - grid.lon_min) / grid.lon_step
        if x < -1e-9 or x > grid.nx - 1 + 1e-9:
            return None
    j0 = min(max(int(math.floor(y)), 0), grid.ny - 1)
    j1 = min(j0 + 1, grid.ny - 1)
    fy = y - j0 if j1 != j0 else 0.0
    i0 = int(math.floor(x))
    fx = x - i0
    if grid.global_lon:
        p = grid.period_cols
        i0 %= p
        i1 = (i0 + 1) % p
    else:
        i0 = min(max(i0, 0), grid.nx - 1)
        i1 = min(i0 + 1, grid.nx - 1)
        if i1 == i0:
            fx = 0.0
    acc = wsum = 0.0
    for ii, jj, w in ((i0, j0, (1 - fx) * (1 - fy)), (i1, j0, fx * (1 - fy)), (i0, j1, (1 - fx) * fy), (i1, j1, fx * fy)):
        if w <= 0:
            continue
        v = values[jj * grid.nx + ii]
        if _is_missing(v, fill):
            continue
        acc += w * v
        wsum += w
    return acc / wsum if wsum > 0 else None


@dataclass(frozen=True)
class ProjectedGrid:
    """Grid in a projected CRS (metres). x0,y0 are the centre of cell (0,0); rows run in
    the direction of dy (OSI SAF files store the top row first, so dy is negative)."""

    projection: object
    x0: float
    y0: float
    dx: float
    dy: float
    nx: int
    ny: int

    def sample(self, values: Sequence, lat: float, lon: float, fill=None):
        x, y = self.projection.forward(lat, lon)
        fi = (x - self.x0) / self.dx
        fj = (y - self.y0) / self.dy
        if fi < -0.5 or fj < -0.5 or fi > self.nx - 0.5 or fj > self.ny - 0.5:
            return None
        i0, j0 = int(math.floor(fi)), int(math.floor(fj))
        ax, ay = fi - i0, fj - j0
        acc = wsum = 0.0
        for ii, jj, w in ((i0, j0, (1 - ax) * (1 - ay)), (i0 + 1, j0, ax * (1 - ay)), (i0, j0 + 1, (1 - ax) * ay), (i0 + 1, j0 + 1, ax * ay)):
            if w <= 0 or not (0 <= ii < self.nx and 0 <= jj < self.ny):
                continue
            v = values[jj * self.nx + ii]
            if _is_missing(v, fill):
                continue
            acc += w * v
            wsum += w
        return acc / wsum if wsum > 0 else None


def regrid_polar_to_latlon(src: ProjectedGrid, values: Sequence, target: LatLonGrid, fill=None, out_fill=None) -> list:
    """Resample a polar grid onto a lat/lon grid by inverse mapping each target cell centre.
    Cells the polar grid does not cover, or covers only with missing values, get out_fill."""
    out = []
    for j in range(target.ny):
        lat = target.lat(j)
        for i in range(target.nx):
            v = src.sample(values, lat, wrap_lon(target.lon(i)), fill)
            out.append(out_fill if v is None else v)
    return out
