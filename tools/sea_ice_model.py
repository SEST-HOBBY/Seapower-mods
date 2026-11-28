"""SEST's battle sea-ice model in Python: the same formula and the same table
as integration/beta-feature-parity/runtime/SeaIceModel.cs, read from
tools/sea_ice_edges.json (written by tools/make_sea_ice_data.py from the
weather branch's mno_env/seaice.py). Used by the test campaigns to place
groups where the runtime will find ice, without the weather branch checked out.

    from sea_ice_model import concentration
    concentration(74.0, 36.0, date(2029, 3, 10))  # -> 62.3 (percent)
"""
import json
import math
from datetime import date
from functools import lru_cache
from pathlib import Path

EDGES_JSON = Path(__file__).resolve().parent / 'sea_ice_edges.json'
ARCTIC_JSON = Path(__file__).resolve().parent / 'sea_ice_arctic_edge.json'  # tools/make_sea_ice_arctic.py
ANTARCTIC_JSON = Path(__file__).resolve().parent / 'sea_ice_antarctic_edge.json'  # tools/make_sea_ice_antarctic.py
NORTH_EDGE_CAP = 80.5
# SEST soft knee over NORTH_EDGE_CAP (SeaIceModel.NorthEdge): no perfect circle at the minimum.
NORTH_KNEE_RATIO = 0.35
NORTH_KNEE_WIDTH = 1.0
CHUKCHI_ARCTIC_FROM = 70.5  # SeaIceModel.ChukchiArcticFrom


def north_edge(edge):
    x = (edge - NORTH_EDGE_CAP) / NORTH_KNEE_WIDTH
    softplus = x if x > 30 else math.log(1.0 + math.exp(x))
    return edge - (1.0 - NORTH_KNEE_RATIO) * NORTH_KNEE_WIDTH * softplus
EDGE_X15 = math.log(98.0 / 15.0 - 1.0)


@lru_cache(maxsize=1)
def table():
    return json.loads(EDGES_JSON.read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def arctic_table():
    return json.loads(ARCTIC_JSON.read_text(encoding='utf-8'))['edges']


@lru_cache(maxsize=1)
def antarctic_table():
    return json.loads(ANTARCTIC_JSON.read_text(encoding='utf-8'))['edges']


def antarctic_edge(lon, day):
    """SeaIceModel.AntarcticEdge: the measured 2016-2025 Antarctic pack edge (NSIDC), degrees South."""
    lon = wrap_lon(lon)
    m0, ft = arctic_month(day)
    m1 = (m0 + 1) % 12
    p = lon + 179.5
    pf = math.floor(p)
    f = p - pf
    i0 = int(pf % 360)
    i1 = (i0 + 1) % 360
    d = antarctic_table()
    a = d[m0][i0] + (d[m0][i1] - d[m0][i0]) * f
    b = d[m1][i0] + (d[m1][i1] - d[m1][i0]) * f
    return a + (b - a) * ft


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _trapezoid(x, a, b, c, d):
    return _smooth((x - a) / (b - a)) * (1.0 - _smooth((x - c) / (d - c)))


def arctic_month(day):
    """(month index 0-11, fraction to the next): the Arctic rows are mid-month values (SeaIceModel.EdgesOn)."""
    days = (date(day.year + day.month // 12, day.month % 12 + 1, 1) - date(day.year, day.month, 1)).days
    t = day.month - 1 + (day.day - 0.5) / days - 0.5
    f = math.floor(t)
    return int(f % 12), t - f


def arctic_weight(lon):
    """SeaIceModel.ArcticWeight: 1 from 15W east to 135W, easing to 0 by 25W and 125W."""
    u = (lon + 25.0) % 360.0
    return _smooth(u / 10.0) * (1.0 - _smooth((u - 250.0) / 10.0))


def arctic_floor(lon):
    """SeaIceModel.ArcticFloor."""
    lon = wrap_lon(lon)
    return 72.0 - 2.5 * _trapezoid(lon, 24, 28, 42, 45) - 1.0 * _trapezoid(lon, 42, 45, 55, 58)


def arctic_edge(lon, day):
    """SeaIceModel.ArcticEdge: the measured 2016-2025 Arctic pack edge (NSIDC), or None outside its sector."""
    lon = wrap_lon(lon)
    if arctic_weight(lon) <= 0:
        return None
    m0, ft = arctic_month(day)
    m1 = (m0 + 1) % 12
    p = lon + 179.5
    pf = math.floor(p)
    f = p - pf
    i0 = int(pf % 360)
    i1 = (i0 + 1) % 360
    d = arctic_table()
    a = d[m0][i0] + (d[m0][i1] - d[m0][i0]) * f
    b = d[m1][i0] + (d[m1][i1] - d[m1][i0]) * f
    return a + (b - a) * ft


def arctic_from(lon, arctic):
    """SeaIceModel.ArcticFrom: never south of 67N, nor south of 77N behind Novaya Zemlya (59-69E)."""
    return max(67.0 + 10.0 * _trapezoid(wrap_lon(lon), 55, 59, 69, 72), min(arctic_floor(lon), arctic - 1.0))


def arctic_mix(edge, lat, lon, arctic):
    """SeaIceModel.ArcticMix."""
    start = arctic_from(lon, arctic)
    w = arctic_weight(wrap_lon(lon)) * _smooth((lat - (start - 1.5)) / 1.5)
    return edge + w * (arctic - edge)


def edges_on(day):
    """{north, south, sh_summer, marginal} for a calendar date (the noon row; leap years have their own table)."""
    leap = day.year % 4 == 0 and (day.year % 100 != 0 or day.year % 400 == 0)
    rows = table()['leap' if leap else 'common']
    index = (date(2028 if leap else 2029, day.month, day.day) - date(2028 if leap else 2029, 1, 1)).days
    m, d, north, south, sh = rows[index]
    assert (m, d) == (day.month, day.day)
    marginal = table()['leap_marginal' if leap else 'common_marginal'][index]
    return {'north': north, 'south': south, 'sh_summer': sh, 'marginal': dict(zip(table()['marginal']['seas'], marginal))}


def marginal_sea(lat, lon):
    """seaice.marginal_sea: 'okhotsk', 'bering', 'chukchi' or None."""
    if not 40.0 <= lat < 80.0:
        return None
    j, i = math.floor(lat), math.floor(wrap_lon(lon))
    for name in table()['marginal']['seas']:
        for row, a, b in table()['marginal']['rows'][name]:
            if row == j and a <= i <= b:
                return name
    return None


def ice_order(name, lat, lon):
    """seaice.ice_order (procedural shape, not data)."""
    if name == 'okhotsk':
        if lat < 52.0 and lon < (142.0 if lat >= 46.0 else 141.5):  # Sea of Japan and Tatar Strait
            return lat + 4.0 - 3.0 * max(0.0, 48.5 - lat)
        s = lat - 0.35 * (lon - 140.0)
        s += 3.0 * math.exp(-((lat - 54.5) / 0.8) ** 2 - ((lon - 139.7) / 2.5) ** 2)  # Shantar Islands, Sakhalin Gulf
        s += 4.0 * math.exp(-((lat - 61.5) / 1.0) ** 2 - ((lon - 162.5) / 2.0) ** 2)  # Shelikhov Gulf
        t = max(0.0, min(1.0, (lat - 56.5) / 1.5))
        s -= 2.5 * t * t * (3.0 - 2.0 * t) * math.exp(-((lon - 143.0) / 8.0) ** 2)  # north coast clears early
        if 44.0 <= lat <= 54.5:
            s = max(s, 52.9 + 0.3 * (lat - 44.5) - ((lon - 143.6) / 2.5) ** 2)
        return s
    if name == 'chukchi':
        t, u = max(0.0, min(1.0, lat - 66.5)), max(0.0, min(1.0, lat - 65.0))  # southern rim and Bering Strait terms
        return lat - 0.05 * (wrap_lon(lon) + 160.0) + 3.0 * (1.0 - t * t * (3.0 - 2.0 * t)) + 2.0 * (1.0 - u * u * (3.0 - 2.0 * u))
    east = wrap_lon(lon - 180.0)
    return lat + 0.235 * max(0.0, east) + 0.12 * max(0.0, -east)


def marginal_concentration(name, lat, lon, s_edge):
    mg = table()['marginal']
    if s_edge >= mg['no_ice']:
        return 0.0
    x = (ice_order(name, lat, lon) - s_edge) / mg['width'] - math.log(mg['max'] / 15.0 - 1.0)
    return mg['max'] / (1.0 + math.exp(-max(-35.0, min(35.0, x))))


def wrap_lon(lon):
    return (lon + 180.0) % 360.0 - 180.0


def _g(lon, centre, width):
    return math.exp(-(wrap_lon(lon - centre) / width) ** 2)


def _below(lat, a, b):
    t = max(0.0, min(1.0, (lat - a) / (b - a)))
    return 1.0 - t * t * (3 - 2 * t)


def edge_shape(south, lon, sh_summer, lat):
    if south:
        winter = 4.0 * _g(lon, -40, 28) + 2.5 * _g(lon, -175, 25) - 1.5 * _g(lon, -100, 25) + 0.8 * math.cos((lon - 5) * (math.pi / 180) * 2)
        summer = 6.0 * _g(lon, -55, 15) + 4.0 * _g(lon, -95, 28) - 3.0 * _g(lon, -178, 15)
        return (1.0 - sh_summer) * winter + sh_summer * summer
    return (-9.0 * _g(lon, 8, 24) - 3.0 * _g(lon, 38, 14)
            + 13.0 * _g(lon, 22, 5) * _below(lat, 66.5, 68.0)
            + 21.0 * _g(lon, 147, 9) * _below(lat, 61.0, 64.0)
            + 5.0 * _g(lon, -175, 14) * _below(lat, 64.0, 67.0)
            + 12.0 * _g(lon, -85, 12) * _below(lat, 65.0, 68.0)
            + 19.0 * _g(lon, -63, 5) * _below(lat, 52.0, 56.0)
            + 3.0 * _g(lon, -58, 14)
            + 2.5 * _g(lon, -25, 4)
            + 12.5 * _g(lon, 28, 4) * _below(lat, 61.5, 63.5)
            + 12.0 * _g(lon, 38, 5) * _below(lat, 67.5, 68.5)
            + 31.5 * _g(lon, 120.5, 3) * _below(lat, 42.0, 44.0)
            + 6.0 * _g(lon, -108, 26) * (1.0 - _below(lat, 66.0, 70.0)))


def concentration(lat, lon, day, hard_cap=False):
    """Percent (0..98; 0..95 in the marginal seas) on the calendar date `day` (a date or datetime)."""
    if abs(lat) < 40:
        return 0.0
    lon = wrap_lon(lon)  # ice_order's Okhotsk branch uses raw lon (a map grid west of -180 read 95 % pack)
    e = edges_on(day if isinstance(day, date) else day.date())
    south = lat < 0
    sea = None if south else marginal_sea(lat, lon)
    if sea is not None:
        regional = marginal_concentration(sea, lat, lon, e['marginal'][sea])
        # SeaIceModel.IceAt: the northern Chukchi Sea follows the measured Arctic edge (no seam at 180 and 155W)
        to_arctic = _smooth((lat - CHUKCHI_ARCTIC_FROM) / 1.5) if sea == 'chukchi' and not hard_cap else 0.0
        if to_arctic > 0:
            arctic = arctic_edge(lon, day if isinstance(day, date) else day.date())
            edge = arctic_mix(north_edge(e['north'] - edge_shape(False, lon, 0.0, lat)), lat, lon, arctic)
            regional += to_arctic * (min(100.0, 98.0 / (1.0 + math.exp(-max(-35.0, min(35.0, lat - edge - EDGE_X15))))) - regional)
        return min(100.0, regional)
    edge = (e['south'] if south else e['north']) - edge_shape(south, lon, e['sh_summer'] if south else 0.0, lat)
    if not south:
        edge = min(edge, NORTH_EDGE_CAP) if hard_cap else north_edge(edge)
        arctic = None if hard_cap else arctic_edge(lon, day if isinstance(day, date) else day.date())
        if arctic is not None:
            edge = arctic_mix(edge, lat, lon, arctic)
    elif not hard_cap:
        edge = antarctic_edge(lon, day if isinstance(day, date) else day.date())
    x = abs(lat) - edge - EDGE_X15
    return min(100.0, 98.0 / (1.0 + math.exp(-max(-35.0, min(35.0, x)))))
