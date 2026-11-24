"""Ice-shelf attributes, fronts, navigation rules and sensor notes. BUILD-TESTED (offline), OFF by default.

Nothing here is wired into routes, GCO or the battle runtime. routes.py still blocks a route
only where it enters a shelf polygon, exactly as before. These functions are for previews,
briefings and a later, PC-tested rule.

Data, all bundled (no network):
- data/ice-shelves-naturalearth-10m.json: Natural Earth 1:10m shelf polygons (public domain).
- data/ice-shelf-fronts-naturalearth-10m.json: Natural Earth 1:10m 'Antarctic Ice Shelf Edge'
  lines, the seaward fronts, made by tools/convert_ice_shelf_fronts.py.
- data/ice-shelf-attributes.json: per-shelf freeboard, draft, area and dated events, each with a
  source and a confidence. Gaps are null, never filled by guesswork.

The Natural Earth fronts are a fixed past position (about 2003-2012, an estimate). Later calvings
and collapses are listed as dated events, and `event_ne_status` says whether the polygon still
shows the ice that was lost. Hydrostatics (ice 917, sea water 1027 kg/m3, BedMachine) turn a
front thickness into freeboard and draft where no measurement exists. Those values are marked
'estimate'.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from .geo import EARTH_RADIUS_NM, great_circle_nm
from .ice import DATA, load_shelves

ATTRIBUTES = DATA / "ice-shelf-attributes.json"
FRONTS = DATA / "ice-shelf-fronts-naturalearth-10m.json"
UNNAMED = "unnamed ice shelf"
PLATFORMS = ("surface", "submarine")


@lru_cache(maxsize=1)
def attributes() -> dict:
    return json.loads(ATTRIBUTES.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _shelves():
    return tuple(load_shelves())


@lru_cache(maxsize=1)
def _attribute_index() -> dict:
    """feature index -> attribute entry. Named shelves match by Natural Earth name; unnamed
    ones by a match_point that must fall inside exactly one polygon with that name."""
    out = {}
    for entry in attributes()["shelves"]:
        cands = [s for s in _shelves() if s.name == entry["ne_name"]]
        if "match_point" in entry:
            cands = [s for s in cands if s.contains(*entry["match_point"])]
            if len(cands) != 1:
                raise ValueError(f"{entry['label']}: match_point must fall in exactly one {entry['ne_name']!r} polygon")
        if not cands:
            raise ValueError(f"{entry['label']}: no Natural Earth shelf named {entry['ne_name']!r}")
        for s in cands:
            if s.feature in out:
                raise ValueError(f"{entry['label']}: feature {s.feature} already has attributes")
            out[s.feature] = entry
    return out


def unattributed_shelves() -> dict:
    """Natural Earth shelves with no attribute entry: names, and a count of unnamed polygons."""
    idx = _attribute_index()
    named = sorted({s.name for s in _shelves() if s.name != UNNAMED} - {e["ne_name"] for e in idx.values()})
    unnamed = sum(1 for s in _shelves() if s.name == UNNAMED and s.feature not in idx)
    return {"named": named, "unnamed_polygons": unnamed}


def _entry_for(shelf):
    return _attribute_index().get(shelf.feature)


def shelf_at(lat: float, lon: float) -> dict | None:
    """The shelf polygon containing the point, with its attributes, or None for open water,
    land or an ice rise (a hole in the polygon)."""
    for s in _shelves():
        if s.contains(lat, lon):
            e = _entry_for(s)
            return {"name": e["label"] if e else s.name, "ne_name": s.name, "feature": s.feature,
                    "attributes": e, "authoritative_outline": s.authoritative}
    return None


# --- fronts -----------------------------------------------------------------------------------

def _vec(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


@lru_cache(maxsize=1)
def front_segments() -> tuple:
    """(feature, A, B, N, (lat, lon) a, (lat, lon) b) per front segment; N is the unit normal of
    the great circle through A and B."""
    doc = json.loads(FRONTS.read_text(encoding="utf-8"))
    out = []
    for f in doc["fronts"]:
        pts = [(p[1], p[0]) for p in f["line"]]
        for a, b in zip(pts, pts[1:]):
            A, B = _vec(*a), _vec(*b)
            n = _cross(A, B)
            m = math.sqrt(_dot(n, n))
            out.append((f["feature"], A, B, (n[0] / m, n[1] / m, n[2] / m) if m > 1e-15 else None, a, b))
    return tuple(out)


def _seg_angle(P, seg) -> float:
    """Great-circle angle (radians) from P to the segment: perpendicular when the foot of the
    perpendicular falls between the end points, else the nearer end point."""
    _, A, B, N, _, _ = seg
    if N is not None:
        foot_inside = _dot(_cross(A, P), N) >= 0 and _dot(_cross(P, B), N) >= 0
        if foot_inside:
            return abs(math.asin(max(-1.0, min(1.0, _dot(P, N)))))
    return min(math.acos(max(-1.0, min(1.0, _dot(P, A)))), math.acos(max(-1.0, min(1.0, _dot(P, B)))))


def nearest_front(lat: float, lon: float) -> dict:
    P = _vec(lat, lon)
    best, best_seg = None, None
    for seg in front_segments():
        ang = _seg_angle(P, seg)
        if best is None or ang < best:
            best, best_seg = ang, seg
    feature = best_seg[0]
    shelf = next(s for s in _shelves() if s.feature == feature)
    e = _entry_for(shelf)
    return {"distance_nm": best * EARTH_RADIUS_NM, "feature": feature, "ne_name": shelf.name,
            "name": e["label"] if e else shelf.name, "segment": (best_seg[4], best_seg[5])}


def distance_to_front_nm(lat: float, lon: float) -> float:
    """Great-circle distance in NM to the nearest Natural Earth ice-shelf front segment. Inside a
    shelf this is the distance out to its front."""
    return nearest_front(lat, lon)["distance_nm"]


# --- front cliff --------------------------------------------------------------------------------

def _pick(entry, key):
    v = (entry or {}).get(key) or {}
    return v if v.get("value") is not None else None


def _range(v):
    val = v["value"]
    return list(val) if isinstance(val, list) else [val, val]


def front_cliff(lat: float, lon: float) -> dict:
    """Freeboard (cliff height above water) and draft of the nearest front. Each comes with a
    range, a single typical value for game use, its basis and a confidence. Where a shelf has no
    value, the generic front (an estimate from the sourced fronts) is used and says so. Water depth
    at the front is unknown everywhere (BedMachine not read); its lower bound is the draft,
    because a front that floats has water under it."""
    nf = nearest_front(lat, lon)
    shelf = next(s for s in _shelves() if s.feature == nf["feature"])
    e = _entry_for(shelf)
    gen = attributes()["generic_front"]
    out = {"shelf": nf["name"], "ne_name": nf["ne_name"], "distance_nm": round(nf["distance_nm"], 2)}
    for key, gkey in (("freeboard_front_m", "freeboard_m"), ("draft_front_m", "draft_m")):
        v, g = _pick(e, key), gen[gkey]
        if v is None:
            out[gkey] = {"range": list(g["value"]), "typical": g["typical"], "basis": "generic front (no value for this shelf)",
                         "source": g["source"], "confidence": "estimate"}
            continue
        rng = _range(v)
        partly = None in rng
        lo = g["value"][0] if rng[0] is None else rng[0]
        hi = g["value"][1] if rng[1] is None else rng[1]
        if v.get("typical_range"):
            typical = sum(v["typical_range"]) / 2
        elif partly:
            typical = min(max(g["typical"], lo), hi)
        else:
            typical = (lo + hi) / 2
        out[gkey] = {"range": [lo, hi], "typical": round(typical), "basis": v.get("basis", "reported"),
                     "source": v["source"], "confidence": v["confidence"], "partly_generic": partly}
    wd = _pick(e, "water_depth_front_m")
    out["water_depth_m"] = ({"range": _range(wd), "source": wd["source"], "confidence": wd["confidence"]} if wd else
                            {"range": None, "lower_bound": out["draft_m"]["range"][0],
                             "gap": "BedMachine Antarctica NSIDC-0756 sea-floor depth along the front"})
    return out


# --- dated events --------------------------------------------------------------------------------

def event_ne_status(event: dict) -> str:
    """'after' if the Natural Earth polygon already shows the loss, 'before' if it still shows
    the ice that was lost, 'unknown' otherwise. An entry's own ne_shows (with evidence) wins."""
    if event.get("ne_shows"):
        return event["ne_shows"]
    lo, hi = attributes()["outline"]["front_epoch_years"]["value"]
    year = int(str(event["date"])[:4])
    if year > hi:
        return "before"
    if year < lo:
        return "after"
    return "unknown"


def shelf_events(lat: float, lon: float) -> list[dict]:
    hit = shelf_at(lat, lon)
    if not hit or not hit["attributes"]:
        return []
    return [dict(ev, ne_status=event_ne_status(ev)) for ev in hit["attributes"].get("events", [])]


# --- navigation -------------------------------------------------------------------------------

def shelf_navigation(lat: float, lon: float, platform: str = "surface") -> dict:
    """Game rule: no surface ship or submarine ever enters a shelf. A submarine also stays
    `standoff_nm` from the front (blocked inside it). A surface ship gets a caution, not a block,
    within `front_caution_nm` (calving and small ice). Both distances are estimates."""
    if platform not in PLATFORMS:
        raise ValueError(f"platform must be one of {PLATFORMS}")
    nav = attributes()["navigation"]
    inside = shelf_at(lat, lon)
    d = distance_to_front_nm(lat, lon)
    if inside:
        return {"status": "blocked", "enter": False, "reason": f"inside {inside['name']}: {nav[platform]['rule']}",
                "distance_to_front_nm": round(d, 2)}
    if platform == "submarine":
        lim = nav["submarine"]["standoff_nm"]["value"]
        if d < lim:
            return {"status": "blocked", "enter": False, "standoff_nm": lim, "distance_to_front_nm": round(d, 2),
                    "reason": f"within the {lim} nm submarine stand-off from an ice-shelf front (estimate): draft and cavity"}
        return {"status": "open", "enter": True, "standoff_nm": lim, "distance_to_front_nm": round(d, 2), "reason": ""}
    lim = nav["surface"]["front_caution_nm"]["value"]
    if d < lim:
        return {"status": "caution", "enter": True, "caution_nm": lim, "distance_to_front_nm": round(d, 2),
                "reason": f"within {lim} nm of an ice-shelf front (estimate): calving, capsizing bergs, growlers"}
    return {"status": "open", "enter": True, "caution_nm": lim, "distance_to_front_nm": round(d, 2), "reason": ""}


def point_features_near(lat: float, lon: float, radius_nm: float) -> list[dict]:
    """Shelves and floating tongues with no outline (mostly Arctic), listed as points. They never
    block a route; a briefing can mention them. Positions are approximate."""
    out = []
    for f in attributes()["point_features"]:
        if f.get("lat") is None:
            continue
        d = great_circle_nm((lat, lon), (f["lat"], f["lon"]))
        if d <= radius_nm:
            out.append(dict(f, distance_nm=round(d, 1)))
    return sorted(out, key=lambda f: f["distance_nm"])


# --- sensors ------------------------------------------------------------------------------------

def face_reflection() -> dict:
    """Normal-incidence pressure reflection coefficient of a sea-water / ice face (estimate)."""
    s = attributes()["sensors"]["sonar"]
    zi = s["rho_ice_kgm3"]["value"] * s["c_ice_ms"]["value"]
    zw = s["rho_water_kgm3"]["value"] * s["c_water_ms"]["value"]
    r = (zi - zw) / (zi + zw)
    return {"coefficient": round(r, 3), "db": round(20 * math.log10(r), 1), "confidence": "estimate"}


def front_sensor_notes(lat: float, lon: float, antenna_m: float = 25.0) -> dict:
    """Radar, sonar and weather notes for the nearest front, with sources from the data file."""
    from .sensors import radar_horizon_km
    cliff = front_cliff(lat, lon)
    s = attributes()["sensors"]
    fb = cliff["freeboard_m"]["typical"]
    return {
        "shelf": cliff["shelf"], "distance_nm": cliff["distance_nm"],
        "radar": {"return": s["radar"]["cliff_return"]["value"], "source": s["radar"]["cliff_return"]["source"],
                  "horizon_nm": round(radar_horizon_km(antenna_m, fb) / 1.852, 1),
                  "horizon_basis": f"{antenna_m:g} m antenna, {fb} m cliff ({cliff['freeboard_m']['confidence']}), 4/3 Earth",
                  "small_ice": s["radar"]["small_ice"]["value"]},
        "sonar": {"face_reflection": face_reflection(), "calving_noise": s["sonar"]["calving_noise_db"]["value"],
                  "ambient": s["sonar"]["ambient"]["value"]},
        "weather": {k: v["value"] for k, v in s["weather"].items()},
    }
