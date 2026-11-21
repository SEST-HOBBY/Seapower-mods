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
NORTH_EDGE_CAP = 80.5
EDGE_X15 = math.log(98.0 / 15.0 - 1.0)


@lru_cache(maxsize=1)
def table():
    return json.loads(EDGES_JSON.read_text(encoding='utf-8'))


def edges_on(day):
    """{north, south, sh_summer} for a calendar date (the noon row; leap years have their own table)."""
    leap = day.year % 4 == 0 and (day.year % 100 != 0 or day.year % 400 == 0)
    rows = table()['leap' if leap else 'common']
    index = (date(2028 if leap else 2029, day.month, day.day) - date(2028 if leap else 2029, 1, 1)).days
    m, d, north, south, sh = rows[index]
    assert (m, d) == (day.month, day.day)
    return {'north': north, 'south': south, 'sh_summer': sh}


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


def concentration(lat, lon, day):
    """Percent (0..98) on the calendar date `day` (a date or datetime)."""
    if abs(lat) < 40:
        return 0.0
    e = edges_on(day if isinstance(day, date) else day.date())
    south = lat < 0
    edge = (e['south'] if south else e['north']) - edge_shape(south, lon, e['sh_summer'] if south else 0.0, lat)
    if not south:
        edge = min(edge, NORTH_EDGE_CAP)
    x = abs(lat) - edge - EDGE_X15
    return min(100.0, 98.0 / (1.0 + math.exp(-max(-35.0, min(35.0, x)))))
