#!/usr/bin/env python3
"""Keep civil air traffic flying its airway instead of circling.

In Sea Power an aircraft with no Waypoints is held in an orbit over where it
spawned, and one that reaches its last waypoint orbits that point. Airliners
circling over the sea are the most visible thing wrong in a long mission.

For every civil aircraft (Type=civ_...) that is NOT the player's own
(Neutral... or Taskforce2... sections), this tool:

  - leaves every waypoint the mission already has exactly as it is,
    including any per-leg commands after a slash;
  - if the route is shorter than MIN_ROUTE_NM in total, appends ONE waypoint
    that carries on along the last leg's bearing (or the aircraft's heading,
    if it had no route), at the last leg's altitude, far enough that the
    whole route is ROUTE_NM long.

ROUTE_NM is about four hours at airliner cruise (470 kn), so the aircraft is
still en route however long the mission is played. That is the stock
pattern: Charlies.ini's DC-10 flies a single waypoint 500 NM off the map.

Idempotent: a route already long enough is untouched, so running it again
changes nothing. Backups (files with "backup-" in the name) are skipped.

Usage (repo root):
    python3 integration/missions/extend_civil_airways.py            # report only
    python3 integration/missions/extend_civil_airways.py --write    # apply
    python3 integration/missions/extend_civil_airways.py --mission "NORTHERN FRONT III" --write
"""
import argparse
import math
import re
import sys
from pathlib import Path

MISSIONS = Path(__file__).resolve().parent
CRUISE_KN = 470
MIN_ROUTE_NM = 3 * CRUISE_KN          # shorter than three hours of flying: extend
ROUTE_NM = 4 * CRUISE_KN              # ...to about four

SECTION = re.compile(r"^\[((?:Neutral|Taskforce2)(?:Aircraft)\d+)\]\s*$")


def point(text):
    """'x,alt,z[/Command...]' -> (x, alt, z) with alt kept as written."""
    bits = text.split("/")[0].split(",")
    return float(bits[0]), bits[1].strip(), float(bits[2])


def fix_section(lines):
    """Return (new_lines, note or None) for one [..Aircraft..] section body."""
    keys = {}
    for i, line in enumerate(lines):
        m = re.match(r"^(\w+)=(.*)$", line.rstrip("\r\n"))
        if m:
            keys[m.group(1)] = (i, m.group(2).strip())
    typ = keys.get("Type", (None, ""))[1]
    if not typ.startswith("civ_") or "RelativePositionInNM" not in keys:
        return lines, None
    x0, alt0, z0 = point(keys["RelativePositionInNM"][1])
    wps = [w for w in keys.get("Waypoints", (None, ""))[1].split("|") if w.strip()]

    path, px, pz, alt = 0.0, x0, z0, alt0
    lx = lz = None
    for w in wps:
        wx, walt, wz = point(w)
        path += math.hypot(wx - px, wz - pz)
        lx, lz = wx - px, wz - pz
        px, pz, alt = wx, wz, walt
    if path >= MIN_ROUTE_NM:
        return lines, None

    if lx is None or math.hypot(lx, lz) < 0.01:
        heading = float(keys.get("Heading", (None, "0"))[1] or 0)
        lx, lz = math.sin(math.radians(heading)), math.cos(math.radians(heading))
    norm = math.hypot(lx, lz)
    extra = ROUTE_NM - path
    nx, nz = px + lx / norm * extra, pz + lz / norm * extra
    new_wp = f"{nx:.2f},{alt},{nz:.2f}"

    out = list(lines)
    newline = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"
    if "Waypoints" in keys:
        i, value = keys["Waypoints"]
        out[i] = f"Waypoints={value}|{new_wp}{newline}"
    else:
        # after the position line, where the editor writes it
        i = keys["RelativePositionInNM"][0]
        out.insert(i + 1, f"Waypoints={new_wp}{newline}")
        if "Telegraph" not in keys:
            out.insert(i + 2, f"Telegraph=3{newline}")
    return out, f"{typ}: route {path:.0f} NM -> {ROUTE_NM} NM"


def fix_file(path, write):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig", errors="replace")
    bom = raw.startswith(b"\xef\xbb\xbf")
    lines = text.splitlines(keepends=True)
    out, notes, i = [], [], 0
    while i < len(lines):
        m = SECTION.match(lines[i].rstrip("\r\n"))
        if not m:
            out.append(lines[i])
            i += 1
            continue
        tag = m.group(1)
        out.append(lines[i])
        j = i + 1
        while j < len(lines) and not lines[j].startswith("["):
            j += 1
        body, note = fix_section(lines[i + 1:j])
        out.extend(body)
        if note:
            notes.append(f"[{tag}] {note}")
        i = j
    if notes and write:
        data = "".join(out).encode("utf-8")
        path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)
    return notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mission", help="one mission name (without .ini)")
    ap.add_argument("--write", action="store_true", help="apply the changes")
    args = ap.parse_args()
    if args.mission:
        files = [MISSIONS / f"{args.mission}.ini"]
        if not files[0].exists():
            sys.exit(f"no such mission: {files[0]}")
    else:
        files = sorted(p for p in MISSIONS.glob("*.ini")
                       if "backup-" not in p.name and p.name != "_info.ini")
    total = 0
    for f in files:
        notes = fix_file(f, args.write)
        if notes:
            total += len(notes)
            print(f"{f.name}")
            for n in notes:
                print(f"    {n}")
    verb = "extended" if args.write else "would extend"
    print(f"\n{verb} {total} civil aircraft route(s) in {len(files)} mission file(s)")


if __name__ == "__main__":
    main()
