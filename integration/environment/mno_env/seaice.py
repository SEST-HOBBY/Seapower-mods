"""Seasonal sea-ice climatology: summer/winter shift of the ice edge in both hemispheres. BUILD-TESTED.

The procedural ice field is calibrated so that its sea-ice EXTENT (area of ocean cells with
concentration >= 15 %, NSIDC's definition) matches the NSIDC Sea Ice Index (G02135 v4.0)
monthly median extent for the campaign date, interpolated between mid-month values. The
table is computed from NSIDC's own monthly CSVs by tools/refresh_seaice_climatology.py and
stored in data/seaice-climatology-nsidc-g02135.json with the files' SHA-256.

Baselines: "2016_2025" (default; the latest ten complete years, the closest observed state
to a 2028-2029 campaign) and "1981_2010" (NSIDC's reference period). Neither is a forecast of
2028. The edge SHAPE (which longitudes reach further from the pole) is procedural.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from functools import lru_cache
from pathlib import Path

from .geo import LandMask, lon_delta

CLIMATOLOGY_FILE = Path(__file__).resolve().parents[1] / "data" / "seaice-climatology-nsidc-g02135.json"
DEFAULT_BASELINE = "2016_2025"


@lru_cache(maxsize=1)
def climatology() -> dict:
    return json.loads(CLIMATOLOGY_FILE.read_text(encoding="utf-8"))


def table(hemisphere: str, baseline: str = DEFAULT_BASELINE) -> list:
    return climatology()["median"][baseline][hemisphere]


EARTH_R_KM = 6371.0
RES = 1.0  # helper grid for extent integration
EDGE_X15 = math.log(98.0 / 15.0 - 1.0)  # logistic offset that puts 15 % on the edge


def target_extent(hemisphere: str, when: dt.datetime, baseline: str = DEFAULT_BASELINE) -> float:
    """Million km2 on a given date: linear between mid-month values (day 15 of each month)."""
    tab = table(hemisphere, baseline)
    mid = dt.datetime(when.year, when.month, 15, tzinfo=when.tzinfo)
    if when >= mid:
        m0, y0 = when.month, when.year
    else:
        m0, y0 = (when.month - 1, when.year) if when.month > 1 else (12, when.year - 1)
    m1, y1 = (m0 + 1, y0) if m0 < 12 else (1, y0 + 1)
    a = dt.datetime(y0, m0, 15, tzinfo=when.tzinfo)
    b = dt.datetime(y1, m1, 15, tzinfo=when.tzinfo)
    f = (when - a).total_seconds() / (b - a).total_seconds()
    return tab[m0 - 1] + f * (tab[m1 - 1] - tab[m0 - 1])


def edge_shape(hemisphere: str, lon: float, sh_summer: float = 0.0, lat: float | None = None) -> float:
    """Degrees of latitude added to the base edge at this longitude (towards the equator is
    positive). Arctic: the Norwegian/Barents Sea (warm Atlantic inflow) stays open while
    Hudson Bay, the Baltic, Okhotsk, the Bering Sea and Labrador freeze far south; the
    Irminger Sea stays open apart from a narrow East Greenland strip. Antarctic, blended by
    sh_summer (1 at the February minimum, 0 in winter): in winter the Weddell and Ross gyres
    carry ice furthest north; at the summer minimum the surviving pack is in the western
    Weddell and the Bellingshausen/Amundsen Seas while the Ross Sea opens. Procedural shape
    fitted by eye to NSIDC/NIC climatology maps, not data.

    The marginal-sea terms (Baltic, Gulf of Finland, White Sea, Bohai, Okhotsk, Bering, Hudson,
    St Lawrence) act only within their
    own latitude band when lat is given, and the Canadian Archipelago/Beaufort term only north of
    about 68 N, so they do not spill ice into the Arctic seas that
    share their longitudes (Barents, Laptev/East Siberian, Chukchi, Parry Channel, Baffin)."""
    rad = math.pi / 180
    if hemisphere == "south":
        winter = (4.0 * math.exp(-(lon_delta(lon, -40) / 28) ** 2)     # Weddell gyre carries ice north
                  + 2.5 * math.exp(-(lon_delta(lon, -175) / 25) ** 2)  # Ross gyre
                  - 1.5 * math.exp(-(lon_delta(lon, -100) / 25) ** 2)  # Amundsen/Bellingshausen
                  + 0.8 * math.cos((lon - 5) * rad * 2))
        summer = (6.0 * math.exp(-(lon_delta(lon, -55) / 15) ** 2)     # western Weddell pack survives
                  + 4.0 * math.exp(-(lon_delta(lon, -95) / 28) ** 2)   # Amundsen/Bellingshausen pack
                  - 3.0 * math.exp(-(lon_delta(lon, -178) / 15) ** 2))  # Ross Sea opens
        return (1.0 - sh_summer) * winter + sh_summer * summer
    def below(a: float, b: float) -> float:  # 1 south of a, 0 north of b
        if lat is None:
            return 1.0
        t = max(0.0, min(1.0, (lat - a) / (b - a)))
        return 1.0 - t * t * (3 - 2 * t)
    return (-9.0 * math.exp(-(lon_delta(lon, 8) / 24) ** 2)       # Norwegian Sea: warm Atlantic inflow, open water
            - 3.0 * math.exp(-(lon_delta(lon, 38) / 14) ** 2)      # southern Barents Sea
            + 13.0 * math.exp(-(lon_delta(lon, 22) / 5) ** 2) * below(66.5, 68.0)    # Baltic (Bothnian Bay, Gulf of Finland)
            + 21.0 * math.exp(-(lon_delta(lon, 147) / 9) ** 2) * below(61.0, 64.0)   # Sea of Okhotsk
            + 5.0 * math.exp(-(lon_delta(lon, -175) / 14) ** 2) * below(64.0, 67.0)   # Bering Sea
            + 12.0 * math.exp(-(lon_delta(lon, -85) / 12) ** 2) * below(65.0, 68.0)   # Hudson Bay and Foxe Basin
            + 19.0 * math.exp(-(lon_delta(lon, -63) / 5) ** 2) * below(52.0, 56.0)    # Gulf of St Lawrence
            + 3.0 * math.exp(-(lon_delta(lon, -58) / 14) ** 2)     # Labrador Sea / Baffin Bay
            + 2.5 * math.exp(-(lon_delta(lon, -25) / 4) ** 2)      # narrow East Greenland Current strip
            + 12.5 * math.exp(-(lon_delta(lon, 28) / 4) ** 2) * below(61.5, 63.5)    # Gulf of Finland
            + 12.0 * math.exp(-(lon_delta(lon, 38) / 5) ** 2) * below(67.5, 68.5)    # White Sea
            + 31.5 * math.exp(-(lon_delta(lon, 120.5) / 3) ** 2) * below(42.0, 44.0)  # Bohai / Liaodong Bay
            + 6.0 * math.exp(-(lon_delta(lon, -108) / 26) ** 2) * (1.0 - below(66.0, 70.0)))  # Canadian Archipelago / Beaufort: old ice survives summer


NORTH_EDGE_CAP = 80.5  # the central Arctic stays ice-covered even at the record minimum


def concentration(hemisphere: str, lat: float, lon: float, base_edge: float, sh_summer: float = 0.0) -> float:
    """Percent. base_edge is the |latitude| of the 15 % line before shape (concentration is
    exactly 15 % there); ice reaches about 90 % some 4 degrees poleward of it. In the north the
    shaped edge never retreats beyond NORTH_EDGE_CAP, so the pole keeps its pack."""
    edge = base_edge - edge_shape(hemisphere, lon, sh_summer, lat)
    if hemisphere == "north":
        edge = min(edge, NORTH_EDGE_CAP)
    if (hemisphere == "south") != (lat < 0):
        return 0.0
    # 98 / (1 + exp(-x)) = 15 exactly at x = -ln(98/15 - 1); ice reaches ~90 % about 4 degrees poleward
    x = (abs(lat) - edge) * 1.0 - EDGE_X15
    return 98.0 / (1.0 + math.exp(-max(-35.0, min(35.0, x))))


@lru_cache(maxsize=1)
def _ocean_cells():
    """(lat, lon, area km2) of ocean cells on the 1-degree helper grid, using the bundled
    Natural Earth mask (always the same mask, so results do not depend on optional packages).
    That mask reads Antarctic ice shelves as water, but NSIDC extent is SEA ice only, so cells
    inside the Natural Earth 1:10m ice-shelf polygons (about 1.3 million km2) are left out."""
    from .ice import load_shelves
    mask = LandMask.from_file()
    shelves = load_shelves()
    cells = []
    for j in range(180):
        lat = -89.5 + j * RES
        if abs(lat) < 40:
            continue
        area = EARTH_R_KM ** 2 * math.radians(RES) * (math.sin(math.radians(lat + RES / 2)) - math.sin(math.radians(lat - RES / 2)))
        for i in range(360):
            lon = -179.5 + i * RES
            if mask.is_land(lat, lon):
                continue
            if lat < -79.0:  # behind the shelf fronts (Ross ~78.5S at most): grounded ice the coarse mask calls water
                continue
            if lat < -60 and any(sh.contains(lat, lon) for sh in shelves):
                continue
            cells.append((lat, lon, abs(area)))
    return tuple(cells)


def extent(hemisphere: str, base_edge: float, sh_summer: float = 0.0) -> float:
    """Million km2 of ocean with >= 15 % concentration for a base edge (1-degree cells)."""
    total = 0.0
    for lat, lon, area in _ocean_cells():
        if (lat < 0) == (hemisphere == "south") and concentration(hemisphere, lat, lon, base_edge, sh_summer) >= 15.0:
            total += area
    return total / 1e6


def fill_plan(nx: int, ny: int, land_nodes, global_lon: bool = True, pole_rows: bool = True) -> tuple:
    """Sea-fill plan of a node grid (row-major, row 0 south): None for a sea node; for a land
    node, the indices of the sea nodes in its first ring of neighbours that has any (rings 1
    and 2), or () when there is none. The first and last rows are the poles when pole_rows is
    set: a land pole is never filled. procedural.py writes sea-surface fields on land nodes as
    the mean over these, and extent_on_grid mirrors it."""
    plan = []
    for j in range(ny):
        for i in range(nx):
            k = j * nx + i
            if not land_nodes[k]:
                plan.append(None)
                continue
            if pole_rows and j in (0, ny - 1):
                plan.append(())
                continue
            found = ()
            for ring in (1, 2):
                nb = []
                for dj in range(-ring, ring + 1):
                    for di in range(-ring, ring + 1):
                        if max(abs(dj), abs(di)) != ring:
                            continue
                        jj, ii = j + dj, i + di
                        if not 0 <= jj < ny:
                            continue
                        if global_lon:
                            ii %= nx
                        elif not 0 <= ii < nx:
                            continue
                        q = jj * nx + ii
                        if not land_nodes[q]:
                            nb.append(q)
                if nb:
                    found = tuple(sorted(set(nb)))
                    break
            plan.append(found)
    return tuple(plan)


@lru_cache(maxsize=8)
def _sampling(hemisphere: str, res: float):
    """How a game-side bilinear sample of a res-degree global grid sees each 1-degree ocean
    cell: every node of the grid (lat, lon, is_land), the sea-fill plan of the land nodes, the
    nodes that can carry ice in this hemisphere, and per cell its four node indices and weights."""
    mask = LandMask.from_file()
    nx = int(round(360 / res))
    ny = int(round(180 / res)) + 1
    nodes = []
    for j in range(ny):
        lat = -90.0 + j * res
        for i in range(nx):
            lon = -180.0 + i * res
            nodes.append((lat, lon, mask.is_land(max(-89.9, min(89.9, lat)), lon)))
    plan = fill_plan(nx, ny, [n[2] for n in nodes], True)
    active = tuple(k for k, (lat, _lo, _l) in enumerate(nodes)
                   if abs(lat) >= 40 - 3 * res and (lat < 0) == (hemisphere == "south"))
    cells = []
    for lat, lon, area in _ocean_cells():
        if (lat < 0) != (hemisphere == "south"):
            continue
        fj, fi = (lat + 90.0) / res, (lon + 180.0) / res
        j0, i0 = int(math.floor(fj)), int(math.floor(fi))
        ty, tx = fj - j0, fi - i0
        j1 = min(j0 + 1, ny - 1)
        corners = ((j0 * nx + i0 % nx, (1 - ty) * (1 - tx)), (j0 * nx + (i0 + 1) % nx, (1 - ty) * tx),
                   (j1 * nx + i0 % nx, ty * (1 - tx)), (j1 * nx + (i0 + 1) % nx, ty * tx))
        cells.append((corners, area))
    return tuple(nodes), plan, active, tuple(cells)


def extent_on_grid(hemisphere: str, base_edge: float, res: float, sh_summer: float = 0.0) -> float:
    """Million km2 with >= 15 % as the game sees it: the res-degree grid (land nodes sea-filled
    as procedural.py writes them) sampled bilinearly at the 1-degree ocean cells (coarse grids
    otherwise overshoot NSIDC by up to 20 %)."""
    nodes, plan, active, cells = _sampling(hemisphere, res)
    vals = [0.0] * len(nodes)
    for k in active:
        lat, lon, land = nodes[k]
        if not land:
            vals[k] = concentration(hemisphere, lat, lon, base_edge, sh_summer)
    for k in active:
        nb = plan[k]
        if nb:
            vals[k] = sum(vals[q] for q in nb) / len(nb)
    total = 0.0
    for corners, area in cells:
        if sum(vals[k] * w for k, w in corners) >= 15.0:
            total += area
    return total / 1e6


@lru_cache(maxsize=800)
def base_edge_for(hemisphere: str, target_mkm2: float, sh_summer: float = 0.0, res: float | None = None) -> float:
    """Bisection for the base edge whose extent matches the target (to about 0.02 million km2).
    With res, the extent is measured as a game-side bilinear sample of a res-degree grid."""
    def ext(edge):
        return extent(hemisphere, edge, sh_summer) if res is None else extent_on_grid(hemisphere, edge, res, sh_summer)
    lo, hi = 40.0, 95.0  # an edge beyond the pole (95) leaves almost no ice; 40 is far beyond any real extent
    if not ext(hi) <= target_mkm2 <= ext(lo):
        raise ValueError(f"{hemisphere} extent target {target_mkm2} outside what the edge model can produce")
    for _ in range(30):
        mid = (lo + hi) / 2
        if ext(mid) > target_mkm2:
            lo = mid
        else:
            hi = mid
    # a coarse grid makes extent jump as whole rows of nodes cross 15 %: take the closer side
    return lo if abs(ext(lo) - target_mkm2) < abs(ext(hi) - target_mkm2) else hi  # unrounded: rounding can step back across a jump


def sh_summer_on(when: dt.datetime) -> float:
    """Antarctic summer weight: 1 at the February minimum (about 20 Feb), 0 from June to
    October, rounded to 0.05 so windows reuse cached edges."""
    days = (when - dt.datetime(when.year, 2, 20, tzinfo=when.tzinfo)).total_seconds() / 86400.0
    days = (days + 182.6) % 365.2422 - 182.6   # -182..+182 days from the minimum
    w = max(0.0, math.cos(math.pi * days / 200.0)) ** 1.5 if abs(days) < 100 else 0.0
    return round(w * 20) / 20


def edges_on(when: dt.datetime, baseline: str = DEFAULT_BASELINE, res: float | None = None) -> dict:
    """Base edge per hemisphere for a date. Targets are rounded to 0.05 million km2 so that a
    72-hour campaign window reuses cached solutions. Pass res (degrees) to calibrate the
    HEMISPHERIC edges for the grid the game will sample. "marginal" holds the regional ice-order
    edge of each marginal sea (see MARGINAL_SEAS below; MARGINAL_NO_ICE when the sea is ice-free
    on that date). The marginal edges ignore res: they are always solved on the 1-degree ocean
    cells, so on a coarse game grid the regional seas are not grid-calibrated (each sea spans
    only a few 2.5-4 degree nodes)."""
    shw = sh_summer_on(when)
    out = {"sh_summer": shw}
    for h in ("north", "south"):
        t = round(target_extent(h, when, baseline) * 20) / 20
        out[h] = base_edge_for(h, t, shw if h == "south" else 0.0, res)
    out["marginal"] = {name: marginal_edge_for(name, round(marginal_target(name, when, baseline) / MARGINAL_TARGET_STEP_KKM2)
                                               * MARGINAL_TARGET_STEP_KKM2)
                       for name in MARGINAL_SEAS}
    return out


def ice_at(lat: float, lon: float, edges: dict) -> float:
    if abs(lat) < 40:
        return 0.0
    h = "south" if lat < 0 else "north"
    if h == "north":
        name = marginal_sea(lat, lon)
        if name is not None:
            if "marginal" not in edges:
                raise ValueError("edges has no 'marginal' entry: build it with seaice.edges_on "
                                 "(the Sea of Okhotsk, Bering Sea and Chukchi Sea use their own regional calibration)")
            return min(100.0, marginal_concentration(name, lat, lon, edges["marginal"][name]))
    return min(100.0, concentration(h, lat, lon, edges[h], edges.get("sh_summer", 0.0) if h == "south" else 0.0))


# ---------------------------------------------------------------------------------------------
# Marginal seas with their own regional calibration: Sea of Okhotsk (with the Sea of Japan and
# Tatar Strait, as NSIDC counts them), the Bering Sea and the Chukchi Sea.
#
# Why: the hemispheric model above moves one edge for the whole Arctic, and the Arctic Basin
# melts out in September. The Sea of Okhotsk is out of phase with it: ice peaks in late
# February to early March and is gone by early July (NSIDC regional extent below; Kimura and
# Wakatsuchi 1999, JGR 104(C5):11137, on the advance and retreat processes). The old constant
# 21-degree Okhotsk term kept the northern basin iced through August (93 % at 59N 145E on
# 15 July, 44 % on 15 August, baseline 2016_2025) and refroze it in October. The Bering Sea was
# under-iced by about half in winter (0.27 vs 0.62 million km2 in March). Before/after tables
# and every source are in docs/environment/SEA-ICE-MARGINAL-SEAS.md.
# The Chukchi Sea was added because the Bering calibration left a hard seam at Bering Strait:
# 95 % on the Bering side against 9-58 % on the Chukchi side in January to April (2016_2025),
# while the NSIDC regional series has the Chukchi Sea fully ice-covered December to April.
#
# How: inside each sea, concentration is a logistic in an "ice order" field s(lat, lon) (higher
# s = freezes earlier and melts later). Each date has one regional edge s_e, solved so that the
# sea's extent (1-degree ocean cells with >= 15 %) matches the NSIDC regional monthly median
# extent, interpolated between mid-month values exactly like target_extent. The hemispheric base
# edge is solved exactly as before (with the old shape), so every cell outside these seas is
# unchanged (tests/fixtures/seaice-hemispheric-golden.json pins that). The cost is that the
# hemispheric total now differs from NSIDC by the old error in these seas (table in the doc).
# The s field is a procedural shape whose terms are fitted to NSIDC monthly extent polygons
# (see ice_order); it is not itself data.
# ---------------------------------------------------------------------------------------------

# NSIDC Sea Ice Index G02135 v4.0 regional monthly extent (Meier, Stroeve and Fetterer 2007, "Whither
# Arctic sea ice? A clear signal of decline regionally, seasonally and extending beyond the
# satellite record", Annals of Glaciology 46:428-434;
# regions "Okhotsk" = Sea of Okhotsk and Sea of Japan, "Bering" and "Chukchi"); file
# N_Sea_Ice_Index_Regional_Monthly_Data_G02135_v4.0.xlsx from
# https://noaadata.apps.nsidc.org/NOAA/G02135/seaice_analysis/ , downloaded 2026-11-24,
# sha256 557eed67f84961fb017827b23c88aceeb6fc9bd5a33fe5e4f8078d860c9db084.
# Median of each month over the baseline years, thousand km2, January to December.
NSIDC_REGIONAL_MEDIAN_KKM2 = {
    "okhotsk": {"1981_2010": (778.3, 1100.9, 1091.7, 787.7, 232.6, 83.0, 0.0, 0.0, 0.0, 36.9, 66.1, 299.6),
                "2016_2025": (670.1, 1005.1, 1054.9, 551.2, 170.8, 74.7, 0.0, 0.0, 0.0, 43.8, 66.9, 281.7)},
    "bering": {"1981_2010": (609.4, 709.4, 766.9, 662.9, 345.0, 55.4, 4.3, 0.0, 1.9, 16.8, 84.6, 317.6),
               "2016_2025": (469.3, 583.1, 621.6, 542.4, 211.9, 34.0, 2.9, 0.0, 0.9, 11.5, 37.4, 180.9)},
    # same file, sheet "Chukchi-Extent-km^2" (region code 12 of the mask below). The region is about
    # 830 thousand km2, so December to April is fully ice-covered in both baselines.
    "chukchi": {"1981_2010": (830.3, 830.3, 830.3, 830.3, 823.9, 743.5, 572.5, 418.6, 352.1, 438.5, 658.4, 830.1),
                "2016_2025": (830.3, 830.3, 830.3, 830.3, 810.8, 680.8, 493.5, 190.9, 48.6, 176.6, 454.1, 766.3)},
}
# Seas whose NSIDC series has real summer ice: _marginal_targets keeps July-October as published.
_MARGINAL_SUMMER_ICE = ("chukchi",)
# NSIDC area of a region that is fully ice-covered every winter (the series maximum, thousand
# km2, reached every January-April 1979-2025). For these seas the target is used as a FRACTION of
# the region: the 1-degree cells hold a slightly different area (Chukchi: about 834 against
# 830.3), and an absolute target would leave the southern cells open in midwinter.
NSIDC_REGION_FULL_KKM2 = {"chukchi": 830.3}


def _marginal_targets(raw: tuple, summer_ice: bool = False) -> tuple:
    """Monthly targets from the NSIDC medians. With summer_ice (the Chukchi Sea) they are the
    medians as published. Otherwise (Okhotsk, Bering), two corrections (ESTIMATES, see the doc).
    July to October are set to 0: in every recent year the NSIDC regional series is exactly 0
    from about 1-3 July to 1 October (the valid-ice mask), and the October value (10-50 thousand
    km2, nearly the same every year) looks like coastal land spill-over, not ice. That October
    floor is also taken off November."""
    t = list(raw)
    if summer_ice:
        return tuple(t)
    t[10] = max(0.0, t[10] - t[9])
    t[6] = t[7] = t[8] = t[9] = 0.0
    return tuple(t)


# 1-degree cells (row = floor(lat), (floor lon first, floor lon last) inclusive, lon -180..179)
# whose centre falls in, or within 3 pixels (about 75 km) of, the NSIDC region in the Meier et al.
# (2007) Arctic region mask Arctic_region_mask_Meier_AnnGlaciol2007.txt (304 x 448 polar
# stereographic 25 km grid, sha256 56afd20963c5dd5f424a9ab4ba812e87b6a0ef1993eb67af1aedf42add4ac26e,
# downloaded 2026-11-24 from https://noaadata.apps.nsidc.org/NOAA/G02135/seaice_analysis/
# Arctic_region_mask_Meier_AnnGlaciol2007.txt, the folder of the G02135 regional files); codes
# 2 = Okhotsk and Japan, 3 = Bering, 12 = Chukchi. Cells are tested on every 1-degree cell,
# land included, and each cell gets the commonest sea code within the 3 pixels.
_MARGINAL_ROWS = {
    "okhotsk": {40: ((127, 141),), 41: ((129, 140),), 42: ((129, 139),), 43: ((131, 141), (144, 145)), 44: ((135, 145),),
                45: ((136, 148),), 46: ((137, 149),), 47: ((138, 151),), 48: ((138, 153),), 49: ((139, 154),),
                50: ((140, 155),), 51: ((140, 156),), 52: ((140, 156),), 53: ((136, 157),), 54: ((134, 156),),
                55: ((134, 156),), 56: ((136, 156),), 57: ((137, 159),), 58: ((139, 160),), 59: ((141, 161),),
                60: ((148, 148), (153, 163)), 61: ((155, 165),), 62: ((157, 159), (162, 165))},
    "bering": {52: ((-180, -175), (177, 179)), 53: ((-180, -169), (172, 179)), 54: ((-180, -166), (168, 179)),
               55: ((-180, -163), (165, 179)), 56: ((-180, -160), (163, 179)), 57: ((-180, -158), (161, 179)),
               58: ((-180, -157), (161, 179)), 59: ((-180, -159), (-157, -157), (162, 179)),
               60: ((-180, -162), (164, 179)), 61: ((-180, -165), (168, 168), (171, 179)),
               62: ((-180, -163), (173, 179)), 63: ((-180, -160), (177, 179)), 64: ((-180, -160), (175, 179)),
               65: ((-180, -169), (-167, -167), (-162, -161), (177, 179)), 66: ((-180, -177), (179, 179))},
    "chukchi": {65: ((-168, -168), (-166, -166), (-164, -163)), 66: ((-176, -161),), 67: ((-179, -162),),
                68: ((-180, -164),), 69: ((-179, -162),), 70: ((-178, -157),), 71: ((-178, -156),),
                72: ((-177, -156),), 73: ((-177, -155),), 74: ((-176, -156),), 75: ((-175, -156),),
                76: ((-175, -156),), 77: ((-174, -156),), 78: ((-172, -156),), 79: ((-171, -171), (-169, -169))},
}

MARGINAL_SEAS = {name: {"targets": {b: _marginal_targets(v, name in _MARGINAL_SUMMER_ICE)
                                    for b, v in NSIDC_REGIONAL_MEDIAN_KKM2[name].items()},
                        "rows": _MARGINAL_ROWS[name]} for name in ("okhotsk", "bering", "chukchi")}
MARGINAL_NO_ICE = 99.0          # regional edge meaning "ice-free on this date": ice_at returns exactly 0
MARGINAL_WIDTH = 0.45           # logistic width in s units: 15 % to 90 % over about 2.3 units; fitted, not data
MARGINAL_MAX = 95.0             # pack concentration inside the edge (%); polynyas keep it below 100 (estimate)
MARGINAL_TARGET_STEP_KKM2 = 5.0  # targets rounded to 5 thousand km2 so nearby dates reuse cached edges


def marginal_sea(lat: float, lon: float):
    """Name of the regionally calibrated sea at this point, or None."""
    if not 40.0 <= lat < 80.0:
        return None
    j = math.floor(lat)
    i = math.floor(lon_delta(lon, 0.0))
    for name, sea in MARGINAL_SEAS.items():
        for a, b in sea["rows"].get(j, ()):
            if a <= i <= b:
                return name
    return None


def ice_order(name: str, lat: float, lon: float) -> float:
    """The s field: higher freezes earlier and melts later (roughly degrees of latitude).
    Only the ORDER of s matters: the regional edge is solved per date to match NSIDC extent.

    Sea of Okhotsk. The terms are physical; their sizes are FITTED to NSIDC data: the G02135 v4.0
    monthly extent polygons (north/monthly/shapefiles/shp_extent, extent_N_YYYYMM_polygon_v4.0.zip,
    https://noaadata.apps.nsidc.org/NOAA/G02135/, downloaded 2026-11-24) for 2016-2025. For each
    1-degree cell the count of years with >= 15 % in each month December-June was compared with
    the model's >= 15 % cells (edge solved to the regional median extent, as below), and the
    mismatch area was minimised (weighting June x6 and May x2 so the melt-out order counts).
    Unweighted mismatch, summed over those months: 2,358 thousand km2 for the old hand-fitted
    field, 1,413 for this one.
    - Ice forms first on the north-west shelf and spreads east and south by drift (Kimura and
      Wakatsuchi 1999, JGR 104(C5):11137). Warm Pacific water enters the south-east through the
      Kuril straits and the West Kamchatka Current runs north along Kamchatka, so the order
      falls towards the east: s = lat - 0.35 * (lon - 140).
    - The last ice is in the Shantar Islands and Sakhalin Gulf corner (NSIDC polygons: ice there
      in June in 5-9 of 10 years; Britannica, 'Sea of Okhotsk', climate section, a secondary
      source not re-read this session: floes stay into July "in the Sakhalin gulfs and around
      Shantar Island"): +3.0 x exp(-((lat - 54.5)/0.8)^2 - ((lon - 139.7)/2.5)^2).
    - Shelikhov Gulf (Gizhiga and Penzhina bays) also keeps June ice (NSIDC polygons: 8-10 of 10
      years at 61-62N 163-164E): +4.0 x exp(-((lat - 61.5)/1.0)^2 - ((lon - 162.5)/2.0)^2).
    - The north coast off Okhotsk town clears early (NSIDC polygons: no June ice at 57-59N
      138-146E in 2016-2025; Kimura and Wakatsuchi 1999 describe early retreat there):
      -2.5 x smoothstep((lat - 56.5)/1.5) x exp(-((lon - 143)/8)^2).
    - The East Sakhalin Current carries a tongue of ice south along Sakhalin to Hokkaido
      (Kimura and Wakatsuchi 1999). s = 52.9 + 0.3 (lat - 44.5) - ((lon - 143.6)/2.5)^2 there.
      Check against Abashiri (44.0N 144.3E): Japan Meteorological Agency (JMA) normals, as named
      by a review of this file: first drift ice 22 January (1991-2020; JMA Abashiri Local
      Meteorological Observatory, seaice_report2025-1.pdf, data.jma.go.jp/abashiri/shosai/
      seaice_report/), last ice 11 April and sea opening 20 March (1981-2010; news20210326_
      seaice_umiake.pdf, jma-net.go.jp/abashiri/news/). Confidence medium: the two PDFs could not
      be reached from this session. The model (15 % at 44.5N 144.5E) gives about 24 January to
      8 April (1981_2010) and 1 February to 27 March (2016_2025).
    - March edge check: the NSIDC 1981-2010 median ice edge (shp_median, median_extent_N_03_
      1981-2010_polyline_v4.0.zip) crosses 150E at 54.8N, 152E at 55.8N, 154.5E at 57.5N; the
      model's 15 % line (baseline 1981_2010) is at 55.1N, 55.8N and 56.7N.
    - Sea of Japan part (west of Sakhalin and Hokkaido): only the northern Tatar Strait freezes
      (December-April); the warm Tsushima Current keeps the rest open. s = lat + 4.0 north of
      48.5N and falls a further 3 per degree south of it, so ice stops near 48N (ESTIMATE of
      47-48N; no edge-latitude source found).
    Bering Sea: ice forms first in Norton Sound, near Bering Strait and in the Gulf of Anadyr
    and is carried south over the wide eastern shelf; the deep Aleutian Basin in the south-west
    stays open. s = lat + 0.235 * (degrees east of 180) + 0.12 * (degrees west of 180), so the
    March edge runs from about 57-58N on the eastern shelf to about 61N at 178E (shape after
    NSIDC/NIC climatology maps; fitted, not data).
    Chukchi Sea: s = lat - 0.05 * (lon + 160). The ice retreats north in summer and returns
    from the north in autumn; the west (Wrangel Island side) keeps it slightly longer than the
    Alaskan side. Checked against the same NSIDC polygons (May-December 2016-2025): latitude
    alone fits about as well (mismatch 497 against 517 thousand km2), but it puts whole rows of
    cells on the same s, so the solved extent misses its target by up to 42 thousand km2; the
    small west term (an ESTIMATE) brings that under 4. A Bering Strait term made the fit worse.
    December to April the whole sea is ice-covered (NSIDC regional series, every year).
    Southern rim (Bering Strait, Kotzebue Sound and the Chukotka coast, south of 67.5N):
    +3.0 x (1 - smoothstep(lat - 66.5)), full south of 66.5N and zero from 67.5N, plus
    +2.0 x (1 - smoothstep(lat - 65.0)) in the strait itself (zero from 66N), so the cells that
    touch the Bering Sea stay close to its 95 %. ESTIMATES, not refitted to the polygons. Without it the rim had the lowest s, so whenever the target was a
    little below the full region (early January and early May, interpolating from the December
    and May medians) the strait and Kotzebue Sound opened first while the Bering cells next to
    them read 95 % (2-14 % at 65.5-66.5N 167.5-168.5W on 1 January 2016_2025), and Kotzebue Sound
    opened in early May. NWS Alaska Sea Ice Program break-up outlooks (FZAK80 PAFC) expect Kotzebue
    Sound ice to stay shorefast until about the end of May or early June; with the term the rim
    first falls under 15 % in late May to early June (2016_2025) and in June (1981_2010). The
    small deficits now open first at 67.5-68.5N (December is still a seam, see the doc)."""
    if name == "okhotsk":
        if lat < 52.0 and lon < (142.0 if lat >= 46.0 else 141.5):  # Sea of Japan and Tatar Strait
            return lat + 4.0 - 3.0 * max(0.0, 48.5 - lat)
        s = lat - 0.35 * (lon - 140.0)
        s += 3.0 * math.exp(-((lat - 54.5) / 0.8) ** 2 - ((lon - 139.7) / 2.5) ** 2)  # Shantar Islands, Sakhalin Gulf
        s += 4.0 * math.exp(-((lat - 61.5) / 1.0) ** 2 - ((lon - 162.5) / 2.0) ** 2)  # Shelikhov Gulf
        t = max(0.0, min(1.0, (lat - 56.5) / 1.5))
        s -= 2.5 * t * t * (3.0 - 2.0 * t) * math.exp(-((lon - 143.0) / 8.0) ** 2)  # north coast clears early
        if 44.0 <= lat <= 54.5:  # East Sakhalin Current ice tongue
            s = max(s, 52.9 + 0.3 * (lat - 44.5) - ((lon - 143.6) / 2.5) ** 2)
        return s
    if name == "bering":
        east = lon_delta(lon, 180.0)  # negative west of 180
        return lat + 0.235 * max(0.0, east) + 0.12 * max(0.0, -east)
    if name == "chukchi":
        t = max(0.0, min(1.0, lat - 66.5))
        u = max(0.0, min(1.0, lat - 65.0))
        return (lat - 0.05 * (lon_delta(lon, 0.0) + 160.0) + 3.0 * (1.0 - t * t * (3.0 - 2.0 * t))  # southern rim
                + 2.0 * (1.0 - u * u * (3.0 - 2.0 * u)))  # Bering Strait narrows
    raise KeyError(name)


def marginal_concentration(name: str, lat: float, lon: float, s_edge: float) -> float:
    """Percent: exactly 15 % where ice_order == s_edge, MARGINAL_MAX deep inside the edge."""
    if s_edge >= MARGINAL_NO_ICE:
        return 0.0
    x = (ice_order(name, lat, lon) - s_edge) / MARGINAL_WIDTH - _MARGINAL_X15
    return MARGINAL_MAX / (1.0 + math.exp(-max(-35.0, min(35.0, x))))


_MARGINAL_X15 = math.log(MARGINAL_MAX / 15.0 - 1.0)


@lru_cache(maxsize=4)
def _marginal_cells(name: str) -> tuple:
    """(lat, lon, area km2) of the 1-degree ocean cells (the same cells as extent()) in this sea."""
    return tuple(c for c in _ocean_cells() if c[0] > 0 and marginal_sea(c[0], c[1]) == name)


# Bisection range of the regional edge per sea, s units. s spans about 34-59 (Okhotsk), 53-69
# (Bering) and 66-82 (Chukchi).
_MARGINAL_S_RANGE = {"chukchi": (40.0, 100.0)}


def marginal_extent(name: str, s_edge: float) -> float:
    """Thousand km2 of the sea's ocean cells with >= 15 %."""
    return sum(a for lat, lon, a in _marginal_cells(name) if marginal_concentration(name, lat, lon, s_edge) >= 15.0) / 1e3


def marginal_target(name: str, when: dt.datetime, baseline: str = DEFAULT_BASELINE) -> float:
    """Thousand km2 on a date: linear between mid-month targets, as target_extent."""
    tab = MARGINAL_SEAS[name]["targets"][baseline]
    mid = dt.datetime(when.year, when.month, 15, tzinfo=when.tzinfo)
    if when >= mid:
        m0, y0 = when.month, when.year
    else:
        m0, y0 = (when.month - 1, when.year) if when.month > 1 else (12, when.year - 1)
    m1, y1 = (m0 + 1, y0) if m0 < 12 else (1, y0 + 1)
    a = dt.datetime(y0, m0, 15, tzinfo=when.tzinfo)
    b = dt.datetime(y1, m1, 15, tzinfo=when.tzinfo)
    f = (when - a).total_seconds() / (b - a).total_seconds()
    return tab[m0 - 1] + f * (tab[m1 - 1] - tab[m0 - 1])


@lru_cache(maxsize=1024)
def marginal_edge_for(name: str, target_kkm2: float) -> float:
    """Bisection for the regional edge whose extent matches the target; MARGINAL_NO_ICE for 0."""
    if target_kkm2 <= 0.0:
        return MARGINAL_NO_ICE
    lo, hi = _MARGINAL_S_RANGE.get(name, (20.0, 80.0))
    if name in NSIDC_REGION_FULL_KKM2:  # as a fraction of the region (see NSIDC_REGION_FULL_KKM2)
        full = round(NSIDC_REGION_FULL_KKM2[name] / MARGINAL_TARGET_STEP_KKM2) * MARGINAL_TARGET_STEP_KKM2  # targets are rounded too
        target_kkm2 = min(1.0, target_kkm2 / full) * marginal_extent(name, lo)
    if marginal_extent(name, lo) <= target_kkm2:
        return lo
    for _ in range(40):
        mid = (lo + hi) / 2
        if marginal_extent(name, mid) > target_kkm2:
            lo = mid
        else:
            hi = mid
    return lo if abs(marginal_extent(name, lo) - target_kkm2) < abs(marginal_extent(name, hi) - target_kkm2) else hi


def extent_with_marginal(hemisphere: str, edges: dict) -> float:
    """Million km2 with >= 15 % on the 1-degree ocean cells as ice_at reports it (regional seas
    included). For the south this equals extent(); for the north it differs from the NSIDC
    target by the old model's error in the regional seas (see the doc)."""
    total = 0.0
    for lat, lon, area in _ocean_cells():
        if (lat < 0) == (hemisphere == "south") and ice_at(lat, lon, edges) >= 15.0:
            total += area
    return total / 1e6
