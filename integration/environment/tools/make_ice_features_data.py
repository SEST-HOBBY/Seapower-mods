#!/usr/bin/env python3
"""Generate the C# data and golden files of the ice-features runtime drop-in.

    python3 integration/environment/tools/make_ice_features_data.py [--check]

Writes (deterministic; --check rebuilds both in memory and fails on any difference):
- integration/environment/runtime-drop-in/ice-features/IceFeaturesData.g.cs
- integration/environment/runtime-drop-in/ice-features/tests/IceFeaturesGolden.g.cs

Inputs (all bundled, no network):
- data/ice-shelves-naturalearth-10m.json: Natural Earth 1:10m Antarctic ice-shelf polygons
  (public domain). Simplified here for the runtime with Douglas-Peucker, tolerance
  SHELF_TOLERANCE_KM, in a local equirectangular plane per ring (see simplify()).
- data/ice-shelf-fronts-naturalearth-10m.json: Natural Earth 1:10m front lines. NOT simplified:
  the runtime front distance is the same as mno_env.iceshelves.distance_to_front_nm.
- data/ice-shelf-attributes.json: per-shelf labels and front freeboard/draft (mno_env.iceshelves),
  the navigation stand-off and caution distances (estimates).
- data/iceberg-climatology.json: the iceberg climatology (mno_env.icebergs).
- prototype-20261118/data/coastlines.json: Natural Earth low-resolution land rings, the same land
  mask mno_env.geo.LandMask uses (MNO_ENV_LAND_MASK=naturalearth). The C# generator uses it so it
  places the same bergs as icebergs.generate with that mask.

Golden points come from the Python modules themselves:
- shelves and fronts: mno_env.ice.IceShelf.contains on the SIMPLIFIED rings (exact parity) and on
  the full rings (agreement; every disagreement must lie within the tolerance of the full outline),
  mno_env.iceshelves.distance_to_front_nm and shelf_navigation;
- bergs: icebergs.density, radar/visual/sonar hooks, melt_rates, remaining_life_days, and
  icebergs.generate over a few boxes (land mask: Natural Earth rings; shelves: the simplified rings,
  as the runtime uses), and geo.displace for the drift step.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import random
import struct
import sys
from pathlib import Path

ENV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENV))

from mno_env import geo, ice, icebergs, iceshelves  # noqa: E402

DROP = ENV / "runtime-drop-in" / "ice-features"
DATA_CS = DROP / "IceFeaturesData.g.cs"
GOLDEN_CS = DROP / "tests" / "IceFeaturesGolden.g.cs"
SHELVES = ENV / "data" / "ice-shelves-naturalearth-10m.json"
FRONTS = ENV / "data" / "ice-shelf-fronts-naturalearth-10m.json"
ATTRS = ENV / "data" / "ice-shelf-attributes.json"
CLIM = ENV / "data" / "iceberg-climatology.json"
COAST = ENV / "prototype-20261118" / "data" / "coastlines.json"
SOURCES = {"Shelves": SHELVES, "Fronts": FRONTS, "Attributes": ATTRS, "Climatology": CLIM, "Coast": COAST,
           "IcebergsPy": ENV / "mno_env" / "icebergs.py", "IceShelvesPy": ENV / "mno_env" / "iceshelves.py",
           "IcePy": ENV / "mno_env" / "ice.py", "GeoPy": ENV / "mno_env" / "geo.py"}

# Douglas-Peucker tolerance for the shelf polygons, km. Natural Earth 1:10m is itself generalised
# at roughly this scale or coarser (a 1:10,000,000 map line is about 1-2 km wide on the ground), so
# the runtime outline moves by at most this much from the bundled outline. Choice, not data.
SHELF_TOLERANCE_KM = 0.5
KM_PER_DEG = 111.32


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- simplification
def simplify(ring, tol_km: float):
    """Douglas-Peucker on a closed ring (first point == last point, both kept) in a local
    equirectangular plane (cos of the ring's mean latitude). Keeps at least 4 points."""
    pts = list(ring)
    if len(pts) <= 4:
        return pts
    lat0 = sum(p[1] for p in pts) / len(pts)
    k = math.cos(math.radians(lat0))
    xy = [(p[0] * KM_PER_DEG * k, p[1] * KM_PER_DEG) for p in pts]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = xy[a]
        bx, by = xy[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = xy[i]
            d = abs(dx * (ay - py) - (ax - px) * dy) / L if L > 0 else math.hypot(px - ax, py - ay)
            if d > best:
                best, bi = d, i
        if bi >= 0 and best > tol_km:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    out = [p for p, kp in zip(pts, keep) if kp]
    if len(out) < 4:  # a closed ring needs 3 distinct corners: keep the farthest points too
        idx = sorted({0, len(pts) // 3, 2 * len(pts) // 3, len(pts) - 1})
        out = [pts[i] for i in idx]
    return out


def simplified_shelves():
    out = []
    for s in ice.load_shelves():
        polys = tuple(tuple(tuple(simplify(r, SHELF_TOLERANCE_KM)) for r in poly) for poly in s.polygons)
        out.append(ice.IceShelf(s.name, polys, s.valid_from, s.authoritative, s.bbox, s.feature))
    return tuple(out)


def boundary_km(shelf, lat, lon) -> float:
    """Distance (local plane, km) from a point to the nearest edge of the shelf's full rings."""
    k = math.cos(math.radians(lat))
    best = float("inf")
    for poly in shelf.polygons:
        for r in poly:
            for (x1, y1), (x2, y2) in zip(r, r[1:]):
                if abs(x2 - x1) > 180:
                    continue
                ax, ay = geo.lon_delta(x1, lon) * KM_PER_DEG * k, (y1 - lat) * KM_PER_DEG
                bx, by = geo.lon_delta(x2, lon) * KM_PER_DEG * k, (y2 - lat) * KM_PER_DEG
                dx, dy = bx - ax, by - ay
                L2 = dx * dx + dy * dy
                t = 0.0 if L2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L2))
                best = min(best, math.hypot(ax + t * dx, ay + t * dy))
    return best


# ----------------------------------------------------------------------------- C# writing
def milli(v: float) -> int:
    m = round(v * 1000)
    if m / 1000.0 != v:
        raise ValueError(f"coordinate {v!r} is not on the 0.001 degree grid")
    return m


def centi(v: float) -> int:
    m = round(v * 100)
    if m / 100.0 != v:
        raise ValueError(f"coordinate {v!r} is not on the 0.01 degree grid")
    return m


def num(v) -> str:
    if v is None:
        return "double.NaN"
    v = float(v)
    if math.isnan(v):
        return "double.NaN"
    r = repr(v)
    return r if ("." in r or "e" in r or "inf" in r) else r + ".0"


def cs_str(s) -> str:
    return "null" if s is None else '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def arr(kind: str, values, per_line: int = 16) -> str:
    vals = [str(v) for v in values]
    lines = []
    for i in range(0, len(vals), per_line):
        lines.append("            " + ", ".join(vals[i:i + per_line]) + ",")
    return "new " + kind + "[] {\n" + "\n".join(lines) + "\n        }"


def bits(v: float) -> str:
    """The IEEE-754 bit pattern of a double as a signed C# long literal (exact round trip)."""
    v = float(v)
    if math.isnan(v):
        v = float("nan")
    return str(struct.unpack(">q", struct.pack(">d", v))[0]) + "L"


# ----------------------------------------------------------------------------- cliffs
def cliff_for(entry, gen):
    """The typical freeboard and draft of a shelf's front: the same rule as iceshelves.front_cliff."""
    out = {}
    for key, gkey in (("freeboard_front_m", "freeboard_m"), ("draft_front_m", "draft_m")):
        v, g = iceshelves._pick(entry, key), gen[gkey]
        if v is None:
            out[gkey] = (g["typical"], "generic front (no value for this shelf)", "estimate")
            continue
        rng = iceshelves._range(v)
        partly = None in rng
        lo = g["value"][0] if rng[0] is None else rng[0]
        hi = g["value"][1] if rng[1] is None else rng[1]
        if v.get("typical_range"):
            typical = sum(v["typical_range"]) / 2
        elif partly:
            typical = min(max(g["typical"], lo), hi)
        else:
            typical = (lo + hi) / 2
        out[gkey] = (round(typical), v.get("basis", "reported") + ("; partly generic" if partly else ""), v["confidence"])
    return out


FRONT_SIDE_OFFSET_KM = 0.3  # test points either side of a segment's middle (choice, under the 0.5 km tolerance)


def front_side_of(shelf, a, b) -> int:
    """+1 when the shelf's FULL outline holds the point left of segment a->b ((lat, lon) pairs),
    -1 when it holds the point to the right, 0 when neither or both (very short or odd segments)."""
    if shelf is None:
        return 0
    mid = geo.intermediate(a, b, 0.5)
    k = math.cos(math.radians(mid[0]))
    dx, dy = geo.lon_delta(b[1], a[1]) * k, b[0] - a[0]
    if dx == 0 and dy == 0:
        return 0
    bearing = math.degrees(math.atan2(dx, dy)) % 360
    off = FRONT_SIDE_OFFSET_KM / 1.852
    left = shelf.contains(*geo.destination(mid, (bearing - 90) % 360, off))
    right = shelf.contains(*geo.destination(mid, (bearing + 90) % 360, off))
    return 1 if left and not right else (-1 if right and not left else 0)


# ----------------------------------------------------------------------------- data file
def build_data() -> str:
    shelves = simplified_shelves()
    attrs = iceshelves.attributes()
    index = iceshelves._attribute_index()
    gen = attrs["generic_front"]
    fronts = json.loads(FRONTS.read_text(encoding="utf-8"))["fronts"]
    clim = icebergs.climatology()
    coast = json.loads(COAST.read_text(encoding="utf-8"))["polygons"]
    nav = attrs["navigation"]

    # cliffs checked against the Python function at one front vertex of each attributed feature
    for f in fronts:
        if f["feature"] in index:
            lon, lat = f["line"][len(f["line"]) // 2]
            if iceshelves.nearest_front(lat, lon)["feature"] == f["feature"]:
                c = iceshelves.front_cliff(lat, lon)
                mine = cliff_for(index[f["feature"]], gen)
                assert c["freeboard_m"]["typical"] == mine["freeboard_m"][0], f
                assert c["draft_m"]["typical"] == mine["draft_m"][0], f

    shelf_feature, shelf_name, shelf_label, poly_start, ring_start, pts = [], [], [], [0], [0], []
    fb, dr, basis, conf = [], [], [], []
    shelf_poly = [0]
    for s in shelves:
        shelf_feature.append(str(s.feature))
        shelf_name.append(cs_str(s.name))
        e = index.get(s.feature)
        shelf_label.append(cs_str(e["label"] if e else ""))
        c = cliff_for(e, gen)
        fb.append(num(c["freeboard_m"][0]))
        dr.append(num(c["draft_m"][0]))
        basis.append(cs_str("freeboard: " + c["freeboard_m"][1] + "; draft: " + c["draft_m"][1]))
        conf.append(cs_str(c["freeboard_m"][2] + " / " + c["draft_m"][2]))
        for poly in s.polygons:
            for r in poly:
                for x, y in r:
                    pts += [str(milli(x)), str(milli(y))]
                ring_start.append(str(len(pts) // 2))
            poly_start.append(str(len(ring_start) - 1))
        shelf_poly.append(str(len(poly_start) - 1))

    front_feature, front_start, front_pts, front_side = [], [0], [], []
    full_by_feature = {s.feature: s for s in ice.load_shelves()}
    sides = {1: 0, -1: 0, 0: 0}
    for f in fronts:
        front_feature.append(str(f["feature"]))
        for x, y in f["line"]:
            front_pts += [str(milli(x)), str(milli(y))]
        front_start.append(str(len(front_pts) // 2))
        shelf = full_by_feature.get(f["feature"])
        for (x1, y1), (x2, y2) in zip(f["line"], f["line"][1:]):
            sd = front_side_of(shelf, (y1, x1), (y2, x2))
            sides[sd] += 1
            front_side.append(str(sd))

    coast_start, coast_pts = [0], []
    for r in coast:
        for x, y in r:
            coast_pts += [str(centi(x)), str(centi(y))]
        coast_start.append(str(len(coast_pts) // 2))

    cats = list(icebergs.CATEGORIES)
    cdoc = clim["categories"]
    geom, melt, counting, sens = clim["geometry"], clim["melt"], clim["counting"], clim["sensors"]
    iip = clim["iip"]
    regions = clim["regions"]
    mixes = list(counting["mix"].keys())
    mixes = [m for m in mixes if m != "source" and m != "confidence"]
    reg_boxes, reg_box_start, reg_monthly = [], [0], []
    for r in regions:
        for b in r["boxes"]:
            reg_boxes += [num(v) for v in b]
        reg_box_start.append(str(len(reg_boxes) // 4))
        reg_monthly += [num(v) for v in (r["monthly"] or [0.0] * 12)]

    L = []
    w = L.append
    w("// <auto-generated> by integration/environment/tools/make_ice_features_data.py. Do not edit.")
    w("// Sources (sha256 below; all bundled, public domain or this repository's own estimates):")
    w("// - Natural Earth 1:10m Antarctic ice shelves (polygons) and ice-shelf edge lines (fronts),")
    w("//   naturalearthdata.com, public domain. Fronts are a fixed past position, about 2003-2012 (estimate).")
    w("// - data/ice-shelf-attributes.json (status ESTIMATE): labels, front freeboard and draft, stand-off.")
    w("// - data/iceberg-climatology.json (status ESTIMATE): IIP/MANICE size classes, regional densities.")
    w("// - Natural Earth low-resolution land rings (prototype-20261118/data/coastlines.json).")
    w("// Shelf rings are simplified (Douglas-Peucker, " + num(SHELF_TOLERANCE_KM) + " km); fronts and land rings are not.")
    w("// Coordinates are integers: shelves and fronts in 0.001 degree, land in 0.01 degree, [lon, lat] pairs.")
    w("namespace Sest.RuntimeFixes")
    w("{")
    w("    internal static class IceFeaturesData")
    w("    {")
    for k, p in SOURCES.items():
        w(f"        internal const string {k}Sha256 = \"{sha(p)}\";")
    w(f"        internal const double ShelfToleranceKm = {num(SHELF_TOLERANCE_KM)};")
    w(f"        internal const string ShelfStatus = {cs_str(attrs['status'])};")
    w(f"        internal const string ClimatologyStatus = {cs_str(clim['status'])};")
    lo, hi = attrs["outline"]["front_epoch_years"]["value"]
    w(f"        internal const int FrontEpochFrom = {lo}, FrontEpochTo = {hi}; // estimate (ice-shelf-attributes.json outline)")
    w("        // navigation (ice-shelf-attributes.json; both distances are estimates, no authoritative figure found)")
    w(f"        internal const double SubmarineStandoffNm = {num(nav['submarine']['standoff_nm']['value'])};")
    w(f"        internal const double SurfaceCautionNm = {num(nav['surface']['front_caution_nm']['value'])};")
    w("        // install-time self-check (IceFeaturesBattle.SelfCheck): Python's own values")
    w(f"        internal const double SelfCheckRandom = {num(random.Random('mno-icebergs-selfcheck').random())}; // random.Random('mno-icebergs-selfcheck').random()")
    w(f"        internal const double SelfCheckDensitySmall = {num(icebergs.density(45.0, -49.0, 5.0)['small'])}; // icebergs.density(45, -49, 5)['small']")
    w(f"        internal const double GenericFreeboardM = {num(gen['freeboard_m']['typical'])}, GenericDraftM = {num(gen['draft_m']['typical'])}; // estimate")
    w("")
    w("        // ---- shelves (load order of mno_env.ice.load_shelves) ----")
    w("        internal static readonly int[] ShelfFeature = " + arr("int", shelf_feature) + ";")
    w("        internal static readonly string[] ShelfName = " + arr("string", shelf_name, 4) + ";")
    w("        internal static readonly string[] ShelfLabel = " + arr("string", shelf_label, 4) + ";")
    w("        // typical front freeboard and draft, m (iceshelves.front_cliff 'typical'; generic front where no value)")
    w("        internal static readonly double[] ShelfFreeboardM = " + arr("double", fb) + ";")
    w("        internal static readonly double[] ShelfDraftM = " + arr("double", dr) + ";")
    w("        internal static readonly string[] ShelfCliffBasis = " + arr("string", basis, 1) + ";")
    w("        internal static readonly string[] ShelfCliffConfidence = " + arr("string", conf, 4) + ";")
    w("        // shelf s has polygons ShelfPoly[s]..ShelfPoly[s+1]; polygon p has rings PolyRing[p]..PolyRing[p+1]")
    w("        // (the first is the outer ring, the rest holes); ring r has points RingStart[r]..RingStart[r+1].")
    w("        internal static readonly int[] ShelfPoly = " + arr("int", shelf_poly) + ";")
    w("        internal static readonly int[] PolyRing = " + arr("int", [str(x) for x in poly_start]) + ";")
    w("        internal static readonly int[] RingStart = " + arr("int", [str(x) for x in ring_start]) + ";")
    w("        internal static readonly int[] ShelfPts = " + arr("int", pts, 20) + ";")
    w("")
    w("        // ---- fronts (unsimplified) ----")
    w("        internal static readonly int[] FrontFeature = " + arr("int", front_feature) + ";")
    w("        internal static readonly int[] FrontStart = " + arr("int", [str(x) for x in front_start]) + ";")
    w("        internal static readonly int[] FrontPts = " + arr("int", front_pts, 20) + ";")
    w(f"        // per segment (line order): +1 when the shelf (full outline) lies left of A->B, -1 right, 0 unknown;")
    w(f"        // {sides[1]} left, {sides[-1]} right, {sides[0]} unknown. The speed rule reads the side here near a front,")
    w(f"        // so the simplified outline cannot flip it.")
    w("        internal static readonly sbyte[] FrontSide = " + arr("sbyte", front_side, 40) + ";")
    w("")
    w("        // ---- land rings (0.01 degree) ----")
    w("        internal static readonly int[] CoastStart = " + arr("int", [str(x) for x in coast_start]) + ";")
    w("        internal static readonly int[] CoastPts = " + arr("int", coast_pts, 20) + ";")
    w("")
    w("        // ---- icebergs (iceberg-climatology.json; see docs/environment/ICEBERGS.md for every source) ----")
    w("        internal static readonly string[] Categories = " + arr("string", [cs_str(c) for c in cats]) + ";")
    w("        internal static readonly string[] Bands = " + arr("string", [cs_str(clim["bands_map"][c]) for c in cats]) + ";")
    w("        // per category: length min, max, height min, max (m)")
    w("        internal static readonly double[] CategoryDims = " + arr("double", [num(v) for c in cats for v in (cdoc[c]["length_m"] + cdoc[c]["height_m"])], 4) + ";")
    w(f"        internal const double DraftToLengthMin = {num(geom['draft_to_length']['value'][0])}, DraftToLengthMax = {num(geom['draft_to_length']['value'][1])};")
    w(f"        internal const double DraftMaxM = {num(geom['draft_max_m']['value'])};")
    w(f"        internal const double WidthToLengthMin = {num(geom['width_to_length']['value'][0])}, WidthToLengthMax = {num(geom['width_to_length']['value'][1])}; // estimate")
    w(f"        internal const double BlockCoefficient = {num(geom['block_coefficient']['value'])}; // estimate")
    w(f"        internal const double GlacierIceDensity = {num(geom['glacier_ice_density_kgm3']['value'])}, ShelfIceDensity = {num(geom['shelf_ice_density_kgm3']['value'])};")
    w(f"        internal const double TabularFreeboardMin = {num(geom['tabular_freeboard_fraction']['value'][0])}, TabularFreeboardMax = {num(geom['tabular_freeboard_fraction']['value'][1])}; // estimate")
    w("        internal static readonly double[] WindFactor = " + arr("double", [num(clim["drift"]["wind_factor"][c]) for c in cats]) + ";")
    w(f"        internal const double FreezingPointC = {num(melt['freezing_point_c']['value'])};")
    w(f"        internal const double DefaultRelativeWaterMs = {num(melt['default_relative_water_speed_ms']['value'])}; // estimate")
    w(f"        internal const int MaxLifeDays = {int(melt['max_life_days']['value'])};")
    w(f"        internal const double GrowlersPerBerg = {num(counting['growlers_per_berg']['value'])}, BergyBitsPerBerg = {num(counting['bergy_bits_per_berg']['value'])}; // estimates")
    w("        internal static readonly string[] Mixes = " + arr("string", [cs_str(m) for m in mixes]) + ";")
    w("        // per mix, in BergClasses order (small, medium, large, very_large, tabular); estimates")
    w("        internal static readonly double[] MixShares = " + arr("double", [num(counting["mix"][m][c]) for m in mixes for c in icebergs.BERG_CLASSES], 5) + ";")
    w("        internal static readonly double[] IipCrossings48N = " + arr("double", [num(v) for v in iip["crossings_48n_monthly"]["value"]], 12) + ";")
    w(f"        internal const double IipResidenceMonths = {num(iip['residence_months_south_of_48n']['value'])}, IipAreaKm2 = {num(iip['area_south_of_48n_km2']['value'])}; // estimates")
    w("        internal static readonly string[] RegionId = " + arr("string", [cs_str(r["id"]) for r in regions], 4) + ";")
    w("        internal static readonly int[] RegionMix = " + arr("int", [str(mixes.index(r["mix"])) for r in regions]) + ";")
    w("        internal static readonly bool[] RegionIip = " + arr("bool", ["true" if r.get("density_from") == "iip" else "false" for r in regions]) + ";")
    w("        internal static readonly double[] RegionDensity = " + arr("double", [num(r["density"] if r["density"] is not None else 0.0) for r in regions]) + ";")
    w("        internal static readonly double[] RegionMonthly = " + arr("double", reg_monthly, 12) + ";")
    w("        // [lat min, lat max, lon min, lon max] per box; region r has boxes RegionBoxStart[r]..RegionBoxStart[r+1]")
    w("        internal static readonly double[] RegionBoxes = " + arr("double", reg_boxes, 4) + ";")
    w("        internal static readonly int[] RegionBoxStart = " + arr("int", [str(x) for x in reg_box_start]) + ";")
    w("        internal static readonly double[] RegionCurrent = " + arr("double", [num(v) for r in regions for v in r["current_ms"]], 2) + "; // [east, north] m/s, estimates")
    w("        // sensors (estimates except the growler radar range; see the JSON)")
    w("        internal static readonly double[] RadarCalmNm = " + arr("double", [num(sens["radar_calm_nm"]["conventional"][c]) for c in cats]) + ";")
    w("        internal static readonly double[] RadarCalmEnhancedNm = " + arr("double", [num(sens["radar_calm_nm"]["enhanced"][c]) for c in cats]) + ";")
    w("        // per category, WMO sea state 0..9")
    w("        internal static readonly double[] RadarSeaStateFactor = " + arr("double", [num(v) for c in cats for v in sens["radar_sea_state_factor"][c]], 10) + ";")
    w("        internal static readonly double[] VisualDayCapNm = " + arr("double", [num(sens["visual_day_cap_nm"].get(c)) for c in cats]) + "; // NaN: no cap")
    w(f"        internal const double VisualNightFactor = {num(sens['visual_night_factor']['value'])}; // estimate")
    w(f"        internal const double GeographicRangeCoefficient = {num(sens['geographic_range_coefficient']['value'])}; // Bowditch")
    w("        internal static readonly double[] SonarFalseContactIndex = " + arr("double", [num(sens["sonar_false_contact_index"][c]) for c in cats]) + "; // DESIGN INDEX, not a probability")
    w("    }")
    w("}")
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- golden file
class NoLand:
    def is_land(self, lat, lon):
        return False


def build_golden() -> str:
    simp = simplified_shelves()
    full = ice.load_shelves()
    rng = random.Random("ice-features-golden")
    fronts = json.loads(FRONTS.read_text(encoding="utf-8"))["fronts"]
    pts = []
    for _ in range(300):
        pts.append((-82.0 + 22.0 * rng.random(), -180.0 + 360.0 * rng.random()))
    for _ in range(300):
        f = fronts[rng.randrange(len(fronts))]
        lon, lat = f["line"][rng.randrange(len(f["line"]))]
        p = geo.destination((lat, lon), 360.0 * rng.random(), 6.0 * rng.random())
        pts.append(p)
    # named checks: inside Ross, at sea north of Ross front, Amery, McMurdo Sound, open Southern Ocean
    pts += [(-80.0, -175.0), (-77.5, -170.0), (-70.0, 71.0), (-77.6, 166.0), (-60.0, 0.0), (-78.2, 180.0), (-78.2, -180.0)]
    shelf_rows, agree, worst_mismatch = [], 0, 0.0
    for lat, lon in pts:
        f_s = next((s.feature for s in simp if s.contains(lat, lon)), -1)
        f_f = next((s.feature for s in full if s.contains(lat, lon)), -1)
        if f_s == f_f:
            agree += 1
        else:
            s = next(x for x in full if x.feature == (f_f if f_f >= 0 else f_s))
            b = boundary_km(s, lat, lon)
            worst_mismatch = max(worst_mismatch, b)
            if b > SHELF_TOLERANCE_KM * 1.05 + 0.01:
                raise SystemExit(f"simplified outline differs from the full one {b:.3f} km from its edge at {lat}, {lon}")
        d = iceshelves.distance_to_front_nm(lat, lon)
        # navigation on the SIMPLIFIED outline (what the runtime does), from the same rule as
        # iceshelves.shelf_navigation: inside -> blocked; submarine within stand-off -> blocked;
        # surface within caution -> caution
        nav = iceshelves.attributes()["navigation"]
        surf = "blocked" if f_s >= 0 else ("caution" if d < nav["surface"]["front_caution_nm"]["value"] else "open")
        sub = "blocked" if f_s >= 0 or d < nav["submarine"]["standoff_nm"]["value"] else "open"
        if f_s == f_f:  # the Python function itself must agree where the outlines agree
            assert iceshelves.shelf_navigation(lat, lon, "surface")["status"] == surf, (lat, lon)
            assert iceshelves.shelf_navigation(lat, lon, "submarine")["status"] == sub, (lat, lon)
        st = {"open": 0, "caution": 1, "blocked": 2}
        shelf_rows.append((lat, lon, f_s, f_f, d, st[surf], st[sub]))

    # densities
    dens_rows = []
    dpts = [(45.0, -49.0), (44.0, -50.0), (55.0, -55.0), (50.0, -50.0), (49.5, -63.0), (70.0, -60.0), (65.0, -30.0),
            (75.0, -90.0), (75.0, 30.0), (80.5, 50.0), (-55.0, -40.0), (-65.0, -45.0), (-70.0, -100.0), (-72.0, 175.0),
            (-72.0, -170.0), (-65.0, 100.0), (-50.0, 0.0), (-55.0, 120.0), (0.0, -30.0), (35.0, 18.0), (-61.0, -180.0)]
    for lat, lon in dpts:
        for m in (1.0, 2.5, 4.0, 5.0, 5.49, 7.0, 12.0, 12.6, 0.7):
            d = icebergs.density(lat, lon, m)
            dens_rows.append((lat, lon, m, [d[c] for c in icebergs.CATEGORIES]))
    fm_rows = [(y, mo, d, icebergs.fractional_month(dt.date(y, mo, d))) for y, mo, d in
               ((2028, 1, 15), (2028, 2, 29), (2029, 2, 28), (2028, 12, 31), (2029, 7, 1), (2028, 5, 15))]

    # sensors
    radar_rows = []
    for c in icebergs.CATEGORIES:
        for ss in (-1, 0, 3, 4, 5, 9, 12):
            radar_rows.append((c, ss, icebergs.radar_range_factor(c, ss), icebergs.radar_detection_nm(c, ss),
                               icebergs.radar_detection_nm(c, ss, antenna_m=40.0, height_m=2.0, enhanced=True)))
    vis_rows = []
    for c in icebergs.CATEGORIES:
        for vis, night in ((20.0, False), (2.0, False), (50.0, True)):
            vis_rows.append((c, vis, night, icebergs.visual_detection_nm(c, vis, night=night)))
    sonar_rows = []
    for c in icebergs.CATEGORIES:
        for draft, depth in ((None, None), (50.0, 200.0), (180.0, 200.0)):
            sonar_rows.append((c, draft, depth, icebergs.sonar_false_contact_index(c, draft, depth)))

    # melt
    melt_rows = []
    for L, W, H, D, sst, ss, wind, frac in ((100, 80, 30, 70, 2.0, None, 10.0, 0.0), (4, 3, 0.8, 4, 0.0, 2.0, None, 0.0),
                                            (300, 250, 60, 200, -1.0, 1.0, None, 0.5), (1500, 1200, 35, 250, 1.0, 4.0, None, 0.0),
                                            (40, 30, 10, 30, 8.0, None, 5.0, 0.0), (20, 15, 3, 12, -1.8, 0.0, None, 0.0)):
        r = icebergs.remaining_life_days(L, W, H, D, sst, ss, wind, frac)
        mr = icebergs.melt_rates(sst, L, ss if ss is not None else icebergs.sea_state_from_wind(wind or 0.0), frac)
        melt_rows.append((L, W, H, D, sst, ss, wind, frac, r["days"], r["capped"], mr["basal"], mr["convection"], mr["wave"]))

    # generator
    icebergs._shelves.cache_clear()
    saved = icebergs._shelves
    icebergs._shelves = lambda: simp
    land = geo.LandMask.from_file()
    gen_cases = [((44.0, 46.0, -50.0, -47.0), dt.date(2028, 5, 15), "0", 2.0),
                 ((-66.0, -64.0, -55.0, -50.0), dt.date(2029, 1, 10), "7", 0.0),
                 ((-74.0, -72.5, 178.0, -178.0), dt.date(2029, 2, 1), "x", -1.0),
                 ((66.0, 69.0, -62.0, -53.0), dt.date(2028, 8, 20), "0", 3.0),
                 ((-78.5, -76.0, 160.0, 175.0), dt.date(2029, 1, 20), "ross", -1.5)]
    gen_rows = []
    try:
        for bbox, when, seed, sst in gen_cases:
            bergs = icebergs.generate(bbox, when, seed, land_mask=land, sst_c=sst)
            gen_rows.append((bbox, when, seed, sst, bergs))
    finally:
        icebergs._shelves = saved
    # drift step (geo.displace)
    disp_rows = []
    for (lat, lon), e, n in (((45.0, -49.0), 1.2, -3.4), ((-72.0, 179.9), 2.0, 0.5), ((70.0, -60.0), -0.3, 0.0), ((-60.0, 0.0), 0.0, 0.0)):
        disp_rows.append((lat, lon, e, n) + tuple(geo.displace((lat, lon), e, n)))

    L = []
    w = L.append
    w("// <auto-generated> by integration/environment/tools/make_ice_features_data.py. Do not edit.")
    w("// Golden values from the Python modules (mno_env.ice / iceshelves / icebergs / geo).")
    w("// Doubles are IEEE-754 bit patterns (long), so the comparison is exact where it should be.")
    w("internal static class IceFeaturesGolden")
    w("{")
    w(f"    internal const int ShelfAgree = {agree}, ShelfPoints = {len(shelf_rows)};")
    w(f"    internal const double ShelfWorstMismatchKm = {num(worst_mismatch)};")
    w("    // lat, lon, feature on simplified rings, feature on full rings, distance to front nm, surface status, submarine status (0 open, 1 caution, 2 blocked)")
    w("    internal static readonly long[] Shelf = " + arr("long", [x for r in shelf_rows for x in (bits(r[0]), bits(r[1]), str(r[2]) + "L", str(r[3]) + "L", bits(r[4]), str(r[5]) + "L", str(r[6]) + "L")], 7) + ";")
    w("    // lat, lon, month, then the 7 categories")
    w("    internal static readonly long[] Density = " + arr("long", [bits(x) for r in dens_rows for x in (r[0], r[1], r[2], *r[3])], 10) + ";")
    w("    internal static readonly long[] FractionalMonth = " + arr("long", [x for r in fm_rows for x in (str(r[0]) + "L", str(r[1]) + "L", str(r[2]) + "L", bits(r[3]))], 4) + ";")
    w("    internal static readonly string[] RadarCategory = " + arr("string", [cs_str(r[0]) for r in radar_rows], 8) + ";")
    w("    // sea state, factor, detection nm (20 m antenna, mid-class height, conventional), detection nm (40 m, 2 m target, enhanced)")
    w("    internal static readonly long[] Radar = " + arr("long", [x for r in radar_rows for x in (str(r[1]) + "L", bits(r[2]), bits(r[3]), bits(r[4]))], 4) + ";")
    w("    internal static readonly string[] VisualCategory = " + arr("string", [cs_str(r[0]) for r in vis_rows], 8) + ";")
    w("    internal static readonly long[] Visual = " + arr("long", [x for r in vis_rows for x in (bits(r[1]), "1L" if r[2] else "0L", bits(r[3]))], 3) + ";")
    w("    internal static readonly string[] SonarCategory = " + arr("string", [cs_str(r[0]) for r in sonar_rows], 8) + ";")
    w("    internal static readonly long[] Sonar = " + arr("long", [x for r in sonar_rows for x in (bits(r[1] if r[1] is not None else float("nan")), bits(r[2] if r[2] is not None else float("nan")), bits(r[3]))], 3) + ";")
    w("    // L, W, H, D, sst, sea state (NaN: from wind), wind (NaN), ice fraction, days, capped (0/1), basal, convection, wave")
    w("    internal static readonly long[] Melt = " + arr("long", [bits(float(x)) if not isinstance(x, bool) else ("1L" if x else "0L") for r in melt_rows for x in [float("nan") if v is None else v for v in r]], 13) + ";")
    w("    internal static readonly long[] Displace = " + arr("long", [bits(x) for r in disp_rows for x in r], 6) + ";")
    w("    internal sealed class Case { internal double Lat0, Lat1, Lon0, Lon1, Sst; internal int Y, M, D; internal string Seed; internal string[] Id, Cat, Region; internal long[] Num; }")
    w("    // Num per berg: lat, lon, length, width, height, draft, mass t, drift u, drift v (m/s), life days, capped (0/1)")
    w("    internal static readonly Case[] Generate = new Case[] {")
    for bbox, when, seed, sst, bergs in gen_rows:
        w("        new Case { Lat0 = %s, Lat1 = %s, Lon0 = %s, Lon1 = %s, Sst = %s, Y = %d, M = %d, D = %d, Seed = %s," % (
            num(bbox[0]), num(bbox[1]), num(bbox[2]), num(bbox[3]), num(sst), when.year, when.month, when.day, cs_str(seed)))
        w("            Id = " + arr("string", [cs_str(b.berg_id) for b in bergs], 4) + ",")
        w("            Cat = " + arr("string", [cs_str(b.category) for b in bergs], 8) + ",")
        w("            Region = " + arr("string", [cs_str(b.region) for b in bergs], 8) + ",")
        w("            Num = " + arr("long", [bits(float(x)) if not isinstance(x, bool) else ("1L" if x else "0L")
                                          for b in bergs for x in (b.lat, b.lon, b.length_m, b.width_m, b.height_m, b.draft_m, b.mass_t,
                                                                   b.drift_u_ms, b.drift_v_ms, b.life_days, b.life_capped)], 11) + " },")
    w("    };")
    w("}")
    return "\n".join(L) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true", help="fail if the files on disk are not what this script writes")
    a = p.parse_args()
    outputs = {DATA_CS: build_data(), GOLDEN_CS: build_golden()}
    if a.check:
        stale = [str(path.relative_to(ENV)) for path, text in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != text]
        if stale:
            raise SystemExit("out of date (run tools/make_ice_features_data.py): " + ", ".join(stale))
        print("ice features data up to date")
        return
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ENV)} ({len(text) // 1024} KB)")


if __name__ == "__main__":
    main()
