#!/usr/bin/env python3
"""Cut a unit's repeated patrol loop down to a few laps.

A generated or hand-written patrol is often a short loop pasted many times
over so the unit keeps moving for a whole session: a narco submarine with a
four-point loop repeated twelve times carries 48 waypoints, a fishing boat
with a three-point loop repeated four times carries 12. On the map that is
a wall of waypoint markers, and it makes every route edit a chore.

This reads a mission, finds every moving unit whose waypoint list is the
same cycle repeated, and keeps --laps laps of it (one by default). Nothing
else in the unit's block changes: the retained waypoints are the original
strings, depth and speed annotations included, so a leg the source already
routed through water stays exactly where it was. A unit whose list does not
repeat is left alone and reported. Every retained leg is re-checked against
the 1 km land mask when global_land_mask is installed.

The source mission is read, never written; the output is a new file whose
Name= is the output name, and re-running gives the same bytes.

    python3 integration/missions/thin_waypoints.py                   # Living Seas -> Lean v2, narco subs and fishing boats
    python3 integration/missions/thin_waypoints.py --dry-run
    python3 integration/missions/thin_waypoints.py --match narco --match civ_fv --laps 2
    python3 integration/missions/thin_waypoints.py --all             # every unit whose route repeats
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_land_defence import Mission                       # noqa: E402

try:
    from global_land_mask import globe as LAND
except ImportError:
    LAND = None

MISSIONS = Path(__file__).resolve().parent
SIDES = ("Taskforce1", "Taskforce2", "Neutral")
MOVING = ("Vessel", "Submarine", "Aircraft", "Biologic")
SOURCE = "SEST Banda Front Living Seas"
OUT = "SEST Banda Front Lean v2"
DEFAULT_MATCH = ("narco", "civ_fv")
STEP_NM = 0.5                # land-mask sampling along a leg


def period(points):
    """The shortest cycle length p such that the list is that cycle repeated
    at least twice (a trailing partial lap is allowed), or None."""
    n = len(points)
    for p in range(1, n // 2 + 1):
        if all(points[i] == points[i + p] for i in range(n - p)):
            return p
    return None


def xz(point):
    """(x, z) of a waypoint string 'x,y,z' or 'x,y,z/Command,...'."""
    core = point.split("/")[0]
    parts = core.split(",")
    return float(parts[0]), float(parts[2])


def leg_touches_land(geo, a, b):
    if LAND is None:
        return False
    d = geo.dist(a[0], a[1], b[0], b[1])
    n = max(1, int(d / STEP_NM))
    for i in range(n + 1):
        t = i / n
        lat, lon = geo.to_ll(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        if LAND.is_land(lat, lon):
            return True
    return False


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=SOURCE, help=f"mission to read, without .ini (default: {SOURCE!r})")
    ap.add_argument("--out", default=OUT, help=f"mission to write, without .ini (default: {OUT!r})")
    ap.add_argument("--match", action="append", default=None,
                    help="only units whose Type contains this (repeatable; default: narco, civ_fv)")
    ap.add_argument("--all", action="store_true", help="every moving unit whose route repeats")
    ap.add_argument("--laps", type=int, default=1, help="laps of the loop to keep (default 1)")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    return ap.parse_args()


def main():
    a = parse_args()
    if a.laps < 1:
        sys.exit("--laps must be at least 1")
    src = MISSIONS / f"{a.source}.ini"
    out = MISSIONS / f"{a.out}.ini"
    if not src.exists():
        sys.exit(f"no such mission: {src}")
    if out.resolve() == src.resolve() or a.out == a.source:
        sys.exit("the output must be a different mission from the source - the source is never written")
    match = [m.lower() for m in (a.match or DEFAULT_MATCH)]

    mission = Mission(src)
    problems = mission.verify()
    if problems:
        sys.exit(f"{src.name} fails its own checks before anything is done:\n  " + "\n  ".join(problems))
    geo = mission.geo
    print(f"source: {src.name}   ->   {out.name}")
    print(f"laps {a.laps}   units: {'every moving unit' if a.all else 'Type containing ' + ', '.join(match)}"
          f"   land mask: {'on' if LAND else 'OFF (pip install global-land-mask numpy)'}\n")

    changed, skipped, land_hits = [], [], []
    src_bodies = {}
    for side in SIDES:
        for cls in MOVING:
            for name, ty, x, z, body in mission.units(side, cls):
                src_bodies[name] = body
                if not a.all and not any(m in ty.lower() for m in match):
                    continue
                m = re.search(r"^(Waypoints=)(.+?)[ \t]*$", body, re.M)
                if not m:
                    skipped.append((name, ty, 0, "no waypoints"))
                    continue
                points = m.group(2).split("|")
                p = period(points)
                if p is None:
                    skipped.append((name, ty, len(points), "route does not repeat"))
                    continue
                keep = points[:p * a.laps]
                if len(keep) >= len(points):
                    skipped.append((name, ty, len(points), f"loop of {p} already within {a.laps} lap(s)"))
                    continue
                # the retained legs are the source's own; prove they stay in water anyway
                pts = [(x, z)] + [xz(w) for w in keep]
                crossing = sum(leg_touches_land(geo, pts[i], pts[i + 1]) for i in range(len(pts) - 1))
                if crossing:
                    land_hits.append((name, ty, crossing))
                new_body = body[:m.start(2)] + "|".join(keep) + body[m.end(2):]
                for k, (h, b) in enumerate(mission.sections):
                    if h == f"[{name}]":
                        mission.sections[k] = (h, new_body)
                        break
                back = "returns to its start" if xz(keep[-1]) == (round(x, 3), round(z, 3)) or \
                    geo.dist(*xz(keep[-1]), x, z) < 0.01 else "ends away from its start"
                changed.append((name, ty, len(points), len(keep), p, back))

    for side in SIDES:
        rows = [c for c in changed if c[0].startswith(side)]
        if rows:
            print(f"===== {side}")
            for name, ty, before, after, p, back in rows:
                print(f"  {name:22} {ty:28} {before:3} -> {after:2} waypoints  (loop of {p}, {back})")
    if skipped:
        print("===== left alone")
        for name, ty, n, why in skipped:
            print(f"  {name:22} {ty:28} {n:3} waypoints  {why}")
    if land_hits:
        sys.exit("retained legs cross land - the source routed them that way, not writing:\n  "
                 + "\n  ".join(f"{n} ({t}): {c} leg(s)" for n, t, c in land_hits))

    mission.set_name(a.out)
    desc = re.search(r"^Description=(.*)$", mission.body("[Language_en]"), re.M)
    if desc and "one lap" not in desc.group(1):
        mission.set_description(desc.group(1).rstrip(". ") + ". Lean v2: patrol loops cut to one lap.")
    problems = mission.verify()
    if problems:
        sys.exit("NOT written - the result fails its own checks:\n  " + "\n  ".join(problems))
    # every other block is byte for byte the source's
    touched = {c[0] for c in changed}
    for side in SIDES:
        for cls in MOVING + ("LandUnit",):
            for name, ty, x, z, body in mission.units(side, cls):
                if name not in touched and body != src_bodies.get(name, body):
                    sys.exit(f"{name} changed although it was not selected - refusing to write")

    total_before = sum(c[2] for c in changed)
    total_after = sum(c[3] for c in changed)
    print(f"\n{len(changed)} unit(s) thinned: {total_before} waypoints -> {total_after}; "
          f"{len(skipped)} left alone; land-mask check {'passed' if LAND else 'skipped'}")
    if a.dry_run:
        print("dry run - nothing written")
        return
    out.write_bytes(mission.text().encode("utf-8"))
    print(f"written: {out}")
    check = Mission(out).verify()
    if check:
        sys.exit("the written file fails verify() on re-read:\n  " + "\n  ".join(check))


if __name__ == "__main__":
    main()
