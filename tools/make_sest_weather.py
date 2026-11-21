#!/usr/bin/env python3
"""Write and check sest-weather.json, SEST's placed-storms sidecar for
Dynamic Campaign Mod 1.0.0 campaigns (20 Nov 2026).

    python3 tools/make_sest_weather.py SPEC.json OUT/sest-weather.json
    python3 tools/make_sest_weather.py --check OUT/sest-weather.json [--campaign campaign.json]

The sidecar sits beside a campaign's campaign.json. SEST's runtime
(integration/beta-feature-parity/runtime/WorldStorms.cs, WorldStorms=1 in
[Runtime], default on) turns each storm into a Dynamic Campaign Mod
WeatherSystem with a 6-hourly track interpolated from the waypoints, so the
storm is on DCM's weather layer and storm list, on the contact screen and in
battle [Environment]. A campaign without the file is unchanged.

A spec is short: per storm an id, a name, a kind word and a track of
[utc, lat, lon, wind kn, radius nm] rows (optionally a sixth, rmw nm):

    {"storms": [{"id": "darya", "name": "DARYA", "kind": "Cyclone",
                 "track": [["2028-01-15T00:00Z", 19.8, 64.6, 70, 220], ...]}]}

kind: Cyclone, Typhoon or Hurricane make a tropical system whose DCM category
reads "<kind> (category n)" (labels "<kind> NAME"; under 64 kn DCM says
"Tropical storm", under 34 kn "Tropical depression"); Storm makes an
extratropical gale (DCM labels it Gale 34-47 kn, Storm 48-63 kn,
Hurricane-force low 64+ kn). wind is the maximum sustained wind; radius is the
outer edge of the wind field (DCM's reach), rmw the radius of maximum wind
(default radius / 10, clamped 8-45 nm). rmw is all or nothing per storm: give
it on every row of a storm or on none.

The rules here are the runtime's (StormSidecar.Parse): a file that passes
check_bytes() is accepted there, and one it rejects is rejected there whole.
check_bytes() reads the file the way the runtime does (File.ReadAllText's
byte-order-mark detection, then a strict JSON reader: no repeated keys, no
NaN or Infinity, nesting at most 16 deep). tools/tests/sest_weather_cases.json
holds edge cases both sides must accept or reject alike; the Python test and
the runtime's managed test (WorldStormsTests) run that same file.
"""
import argparse
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

FORMAT = "sest-weather/1"
FILE_NAME = "sest-weather.json"
KINDS = ("Cyclone", "Typhoon", "Hurricane", "Storm")
STEP_HOURS = 6
ID = re.compile(r"[a-z0-9-]{1,32}")      # used with fullmatch: "$" would let a trailing newline through
UTC = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")   # ASCII digits, as DateTime.ParseExact
MAX_DEPTH = 16                             # the runtime Json reader's nesting limit
TIME = "%Y-%m-%dT%H:%M:%SZ"
LIMITS = {"lat": (-80, 85), "lon": (-180, 360), "wind": (10, 185), "radius": (30, 600), "rmw": (5, 80)}


class SpecError(ValueError):
    pass


def parse_time(text):
    """2028-01-15T04:00Z or 2028-01-15T04:00:00Z, UTC only."""
    if not isinstance(text, str):
        raise SpecError(f"time {text!r} is not a string")
    for fmt in (TIME, "%Y-%m-%dT%H:%MZ"):
        try:
            t = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if not 1901 <= t.year <= 2099:
            raise SpecError(f"time {text} is outside 1901-2099")
        return t
    raise SpecError(f"time {text!r} must read like 2028-01-15T04:00:00Z")


def build(spec):
    """Spec (see the module text) to the sidecar document; checked."""
    if not isinstance(spec, dict) or not isinstance(spec.get("storms"), list):
        raise SpecError("a spec is an object with a storms list")
    storms = []
    for s in spec["storms"]:
        if not isinstance(s, dict) or not isinstance(s.get("track"), list):
            raise SpecError("each storm needs id, name, kind and a track list")
        points = []
        for row in s["track"]:
            if not isinstance(row, (list, tuple)) or len(row) not in (5, 6):
                raise SpecError(f"storm {s.get('id')}: a track row is [utc, lat, lon, wind, radius(, rmw)]")
            p = {"utc": parse_time(row[0]).strftime(TIME), "lat": row[1], "lon": row[2], "wind": row[3], "radius": row[4]}
            if len(row) == 6:
                p["rmw"] = row[5]
            points.append(p)
        row = {"id": s.get("id"), "name": s.get("name"), "kind": s.get("kind"), "waypoints": points}
        if "note" in s:
            row["note"] = s["note"]
        storms.append(row)
    doc = {"format": FORMAT}
    if "note" in spec:
        doc["note"] = spec["note"]
    doc["storms"] = storms
    errors = check(doc)
    if errors:
        raise SpecError("; ".join(errors))
    return doc


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check(doc):
    """Every reason the runtime would reject this document (empty when fine)."""
    errors = []
    if not isinstance(doc, dict):
        return ["the file is not a JSON object"]
    extra = set(doc) - {"format", "storms", "note"}
    if extra:
        errors.append(f"file: unknown field(s) {sorted(extra)}")
    if doc.get("format") != FORMAT:
        errors.append(f'format is not "{FORMAT}"')
    storms = doc.get("storms")
    if not isinstance(storms, list) or not 1 <= len(storms) <= 16:
        return errors + ["storms must hold 1 to 16 storms"]
    ids = set()
    for s in storms:
        if not isinstance(s, dict):
            errors.append("a storm is not an object")
            continue
        sid = s.get("id")
        where = f"storm {sid}"
        before = len(errors)
        extra = set(s) - {"id", "name", "kind", "waypoints", "note"}
        if extra:
            errors.append(f"{where}: unknown field(s) {sorted(extra)}")
        if not isinstance(sid, str) or not ID.fullmatch(sid):
            errors.append(f"{where}: id must be 1-32 of a-z, 0-9 and -")
        elif sid in ids:
            errors.append(f"{where}: id is used twice")
        ids.add(sid)
        name = s.get("name")
        name = name.strip(" \t\r\n") if isinstance(name, str) else name   # the runtime trims exactly these
        if not isinstance(name, str) or not 1 <= len(name) <= 24 or not all(" " <= c <= "~" for c in name):
            errors.append(f"{where}: name must be 1-24 printable characters")
        if s.get("kind") not in KINDS:
            errors.append(f"{where}: kind must be Cyclone, Typhoon, Hurricane or Storm")
        points = s.get("waypoints")
        if not isinstance(points, list) or not 2 <= len(points) <= 64:
            errors.append(f"{where}: 2 to 64 waypoints are needed")
            continue
        last = None
        for p in points:
            if not isinstance(p, dict):
                errors.append(f"{where}: a waypoint is not an object")
                continue
            extra = set(p) - {"utc", "lat", "lon", "wind", "radius", "rmw"}
            if extra:
                errors.append(f"{where}: unknown waypoint field(s) {sorted(extra)}")
            try:
                if not isinstance(p.get("utc"), str) or not UTC.fullmatch(p["utc"]):
                    raise SpecError("utc must read like 2028-01-15T04:00:00Z")
                t = parse_time(p["utc"])
            except SpecError as e:
                errors.append(f"{where}: {e}")
                continue
            for key, (lo, hi) in LIMITS.items():
                if key == "rmw" and key not in p:
                    continue
                if not _number(p.get(key)) or not lo <= p[key] <= hi:
                    errors.append(f"{where}: {key} must be between {lo} and {hi}")
            if _number(p.get("rmw")) and _number(p.get("radius")) and p["rmw"] >= p["radius"]:
                errors.append(f"{where}: rmw must be less than radius")
            if last is not None and t <= last:
                errors.append(f"{where}: waypoint times must increase")
            last = t
        with_rmw = sum(1 for p in points if isinstance(p, dict) and "rmw" in p)
        if 0 < with_rmw < len(points):
            errors.append(f"{where}: rmw must be on every waypoint of the storm or on none")
        if len(errors) == before and (parse_time(points[-1]["utc"]) - parse_time(points[0]["utc"])) > timedelta(days=30):
            errors.append(f"{where}: a storm may last at most 30 days")
    return errors


class _Strict(ValueError):
    pass


def _no_repeats(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise _Strict(f'JSON repeats key "{k}"')
        seen[k] = v
    return seen


def _no_constant(name):
    raise _Strict(f"JSON {name} is not a number the runtime reads")


def _depth(value, depth=0):
    if depth > MAX_DEPTH:
        raise _Strict("JSON nesting too deep")
    if isinstance(value, dict):
        for v in value.values():
            _depth(v, depth + 1)
    elif isinstance(value, list):
        for v in value:
            _depth(v, depth + 1)


def decode(data):
    """The text File.ReadAllText gives the runtime: a UTF-32, UTF-16 or UTF-8
    byte-order mark picks the encoding and is dropped, otherwise UTF-8; bytes
    that are not valid in it become U+FFFD."""
    for bom, codec in ((b"\xff\xfe\x00\x00", "utf-32-le"), (b"\x00\x00\xfe\xff", "utf-32-be"),
                       (b"\xef\xbb\xbf", "utf-8"), (b"\xff\xfe", "utf-16-le"), (b"\xfe\xff", "utf-16-be")):
        if data.startswith(bom):
            return data[len(bom):].decode(codec, errors="replace")
    return data.decode("utf-8", errors="replace")


def load(text):
    """The runtime's strict JSON reader on text: (doc, None) or (None, reason)."""
    if text.startswith("\ufeff"):
        text = text[1:]
    try:
        doc = json.loads(text, object_pairs_hook=_no_repeats, parse_constant=_no_constant)
        _depth(doc)
    except (ValueError, RecursionError) as e:
        return None, str(e)
    return doc, None


def check_bytes(data):
    """Every reason the runtime would reject these file bytes (empty when fine)."""
    doc, error = load(decode(data))
    return [error] if error else check(doc)


def dumps(doc):
    """The exact bytes written: deterministic, LF, trailing newline."""
    return json.dumps(doc, indent=1, ensure_ascii=True) + "\n"


def write(doc, path):
    errors = check(doc)
    if errors:
        raise SpecError("; ".join(errors))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(dumps(doc).encode("ascii"))
    return path


def position(storm, when):
    """(lat, lon, wind, radius) at a UTC time, interpolated as the runtime
    does; None outside the storm's life."""
    pts = storm["waypoints"]
    times = [parse_time(p["utc"]) for p in pts]
    if when < times[0] or when > times[-1]:
        return None
    k = 0
    while k < len(pts) - 2 and times[k + 1] <= when:
        k += 1
    a, b = pts[k], pts[k + 1]
    f = (when - times[k]) / (times[k + 1] - times[k])
    f = max(0.0, min(1.0, f))
    return tuple(a[key] + (b[key] - a[key]) * f for key in ("lat", "lon", "wind", "radius"))


def distance_nm(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 3440.065 * math.asin(math.sqrt(h))


def closest_approach(storm, lat, lon, step_minutes=30):
    """(distance nm, utc, wind kn, radius nm) at the storm's closest pass."""
    t = parse_time(storm["waypoints"][0]["utc"])
    end = parse_time(storm["waypoints"][-1]["utc"])
    best = None
    while t <= end:
        p = position(storm, t)
        d = distance_nm(p[0], p[1], lat, lon)
        if best is None or d < best[0]:
            best = (d, t, p[2], p[3])
        t += timedelta(minutes=step_minutes)
    return best


def check_campaign(doc, campaign):
    """Warnings (not errors) about a sidecar against its campaign.json: DCM
    lists a storm only while its centre is inside the bounds plus 5 degrees,
    and a storm that ends before the campaign starts is never seen."""
    notes = []
    b = campaign.get("bounds") or {}
    start = parse_time(campaign["start"].replace("+00:00", "Z")) if campaign.get("start") else None
    for s in doc["storms"]:
        times = [parse_time(p["utc"]) for p in s["waypoints"]]
        if start and times[-1] < start:
            notes.append(f"storm {s['id']} ends before the campaign starts ({start:%Y-%m-%d %H:%MZ})")
        if b and not any(b["latMin"] - 5 <= p["lat"] <= b["latMax"] + 5 and b["lonMin"] - 5 <= p["lon"] <= b["lonMax"] + 5
                         for p in s["waypoints"]):
            notes.append(f"storm {s['id']} never comes within 5 degrees of the campaign bounds; DCM will not list it")
    return notes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?", type=Path, help="storm spec JSON")
    ap.add_argument("out", nargs="?", type=Path, help="sest-weather.json to write")
    ap.add_argument("--check", type=Path, help="check an existing sest-weather.json instead")
    ap.add_argument("--campaign", type=Path, help="campaign.json to check the storms against")
    a = ap.parse_args(argv)
    if a.check:
        doc, error = load(decode(a.check.read_bytes()))
        errors = [error] if error else check(doc)
    elif a.spec and a.out:
        try:
            doc = build(json.loads(a.spec.read_text(encoding="utf-8")))
        except SpecError as e:
            print(f"REJECTED: {e}")
            return 1
        write(doc, a.out)
        errors = []
        print(f"wrote {a.out}")
    else:
        ap.error("give SPEC OUT, or --check FILE")
    for e in errors:
        print("REJECTED:", e)
    if errors:
        return 1
    if a.campaign:
        for n in check_campaign(doc, json.loads(a.campaign.read_text(encoding="utf-8"))):
            print("WARNING:", n)
    for s in doc["storms"]:
        print(f"  sest-{s['id']}: {s['kind']} {s['name']}, {len(s['waypoints'])} waypoints, "
              f"{s['waypoints'][0]['utc']} to {s['waypoints'][-1]['utc']}, peak {max(p['wind'] for p in s['waypoints'])} kn")
    return 0


if __name__ == "__main__":
    sys.exit(main())
