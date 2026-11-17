"""Polar map projections for sea-ice grids. BUILD-TESTED against PROJ 9.8.1 reference values.

Implemented from Snyder, "Map Projections: A Working Manual" (USGS PP 1395, 1987):
- ellipsoidal polar stereographic with a true-scale latitude (eqs. 15-9, 21-33..21-40):
  EPSG:3411/3412 (NSIDC, Hughes 1980 ellipsoid; the OSI SAF OSI-401 family grids) and
  EPSG:3413/3976 (WGS 84);
- ellipsoidal polar Lambert azimuthal equal-area (eqs. 3-12, 24-..): EPSG:6931/6932
  (EASE-Grid 2.0, the OSI SAF OSI-450/430 climate records).
Coordinates are metres; longitudes in degrees east. No third-party dependency.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

WGS84 = (6378137.0, 1 / 298.257223563)
HUGHES80_A, HUGHES80_B = 6378273.0, 6356889.449


@dataclass(frozen=True)
class PolarStereographic:
    name: str
    a: float
    e: float
    lat_ts: float  # degrees, signed; sign selects the pole
    lon0: float

    @property
    def south(self) -> bool:
        return self.lat_ts < 0

    def _t(self, phi: float) -> float:
        es = self.e * math.sin(phi)
        return math.tan(math.pi / 4 - phi / 2) / ((1 - es) / (1 + es)) ** (self.e / 2)

    def _m(self, phi: float) -> float:
        return math.cos(phi) / math.sqrt(1 - (self.e * math.sin(phi)) ** 2)

    def forward(self, lat: float, lon: float) -> tuple[float, float]:
        sgn = -1.0 if self.south else 1.0
        phi = math.radians(sgn * lat)
        lam = math.radians(sgn * (lon - self.lon0))
        phic = math.radians(abs(self.lat_ts))
        rho = self.a * self._m(phic) * self._t(phi) / self._t(phic)
        x, y = rho * math.sin(lam), -rho * math.cos(lam)
        return (sgn * x, sgn * y)

    def inverse(self, x: float, y: float) -> tuple[float, float]:
        sgn = -1.0 if self.south else 1.0
        x, y = sgn * x, sgn * y
        phic = math.radians(abs(self.lat_ts))
        rho = math.hypot(x, y)
        t = rho * self._t(phic) / (self.a * self._m(phic))
        phi = math.pi / 2 - 2 * math.atan(t)
        for _ in range(15):
            es = self.e * math.sin(phi)
            nxt = math.pi / 2 - 2 * math.atan(t * ((1 - es) / (1 + es)) ** (self.e / 2))
            if abs(nxt - phi) < 1e-13:
                phi = nxt
                break
            phi = nxt
        lam = math.atan2(x, -y) if rho > 0 else 0.0
        lat = sgn * math.degrees(phi)
        lon = sgn * math.degrees(lam) + self.lon0
        return (lat, (lon + 180) % 360 - 180)


@dataclass(frozen=True)
class PolarLAEA:
    name: str
    a: float
    e: float
    south: bool
    lon0: float = 0.0

    def _q(self, phi: float) -> float:
        e, s = self.e, math.sin(phi)
        return (1 - e * e) * (s / (1 - (e * s) ** 2) - (1 / (2 * e)) * math.log((1 - e * s) / (1 + e * s)))

    def forward(self, lat: float, lon: float) -> tuple[float, float]:
        qp = self._q(math.pi / 2)
        if self.south:
            rho = self.a * math.sqrt(max(0.0, qp + self._q(math.radians(lat))))
            lam = math.radians(lon - self.lon0)
            return (rho * math.sin(lam), rho * math.cos(lam))
        rho = self.a * math.sqrt(max(0.0, qp - self._q(math.radians(lat))))
        lam = math.radians(lon - self.lon0)
        return (rho * math.sin(lam), -rho * math.cos(lam))

    def inverse(self, x: float, y: float) -> tuple[float, float]:
        e = self.e
        qp = self._q(math.pi / 2)
        rho = math.hypot(x, y)
        q = (qp - (rho / self.a) ** 2) * (-1 if self.south else 1)
        # beta (authalic latitude) then series to geodetic latitude (Snyder 3-18)
        beta = math.asin(max(-1.0, min(1.0, q / qp)))
        e2, e4, e6 = e * e, e ** 4, e ** 6
        phi = (beta + (e2 / 3 + 31 * e4 / 180 + 517 * e6 / 5040) * math.sin(2 * beta)
               + (23 * e4 / 360 + 251 * e6 / 3780) * math.sin(4 * beta)
               + (761 * e6 / 45360) * math.sin(6 * beta))
        lam = math.atan2(x, y) if self.south else math.atan2(x, -y)
        lon = math.degrees(lam) + self.lon0
        return (math.degrees(phi), (lon + 180) % 360 - 180)


def _e_from_ab(a: float, b: float) -> float:
    return math.sqrt(1 - (b / a) ** 2)


def _e_from_f(f: float) -> float:
    return math.sqrt(2 * f - f * f)


EPSG_3411 = PolarStereographic("EPSG:3411 NSIDC Sea Ice Polar Stereographic North", HUGHES80_A, _e_from_ab(HUGHES80_A, HUGHES80_B), 70.0, -45.0)
EPSG_3412 = PolarStereographic("EPSG:3412 NSIDC Sea Ice Polar Stereographic South", HUGHES80_A, _e_from_ab(HUGHES80_A, HUGHES80_B), -70.0, 0.0)
EPSG_3413 = PolarStereographic("EPSG:3413 WGS 84 / NSIDC Sea Ice Polar Stereographic North", WGS84[0], _e_from_f(WGS84[1]), 70.0, -45.0)
EPSG_3976 = PolarStereographic("EPSG:3976 WGS 84 / NSIDC Sea Ice Polar Stereographic South", WGS84[0], _e_from_f(WGS84[1]), -70.0, 0.0)
EPSG_6931 = PolarLAEA("EPSG:6931 WGS 84 / NSIDC EASE-Grid 2.0 North", WGS84[0], _e_from_f(WGS84[1]), False)
EPSG_6932 = PolarLAEA("EPSG:6932 WGS 84 / NSIDC EASE-Grid 2.0 South", WGS84[0], _e_from_f(WGS84[1]), True)

PROJECTIONS = {p.name.split()[0]: p for p in (EPSG_3411, EPSG_3412, EPSG_3413, EPSG_3976, EPSG_6931, EPSG_6932)}
