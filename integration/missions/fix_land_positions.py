#!/usr/bin/env python3
"""Move any neutral vessel or sea life that sits on land into the water.

Ships and whales placed by hand or by generator can end up over a coastline
or an island, where they either fail to spawn or look absurd. This checks
every spawn position, every waypoint leg and every biologic RandomSpawnCenter
in a mission against a real land/sea mask, and relocates only the offending
points to the nearest water.

The relocation is a spiral search outward from the bad point in 0.05-degree
steps, so a unit moves the shortest distance that gets it wet and stays where
the designer meant it to be. A biologic's RandomSpawnRange is also clamped so
its wander circle cannot reach back onto the shore.

Everything else in the mission is untouched: only the coordinate numbers on
offending lines are rewritten.

Requires the global-land-mask package (pip install global-land-mask numpy).

Usage (repo root):
    python3 integration/missions/fix_land_positions.py                  # report
    python3 integration/missions/fix_land_positions.py --write          # apply
    python3 integration/missions/fix_land_positions.py --mission "NORTHERN FRONT III" --write
"""
import argparse
import math
import re
import sys
from pathlib import Path

try:
    from global_land_mask import globe
except ImportError:
    sys.exit("needs the land mask: pip install global-land-mask numpy")

MISSIONS = Path(__file__).resolve().parent

STEP = 0.05          # degrees per spiral ring (~3 nm)
MAX_RINGS = 40       # give up beyond ~120 nm
CLEARANCE = 0.05     # a moved point must also be clear this far around


def water(lat, lon, clearance=0.0):
    """True when the point is sea, optionally with a margin of sea around it."""
    if globe.is_land(lat, lon):
        return False
    if clearance:
        for dla, dlo in ((clearance, 0), (-clearance, 0), (0, clearance), (0, -clearance)):
            if globe.is_land(lat + dla, lon + dlo):
                return False
    return True


def nearest_water(lat, lon):
    """Closest sea point to (lat, lon), searched outward in rings."""
    for ring in range(1, MAX_RINGS + 1):
        r = ring * STEP
        best = None
        for deg in range(0, 360, 10):
            a = math.radians(deg)
            cand_lat = lat + r * math.cos(a)
            cand_lon = lon + r * math.sin(a)
            if water(cand_lat, cand_lon, CLEARANCE):
                d = math.hypot(cand_lat - lat, cand_lon - lon)
                if best is None or d < best[0]:
                    best = (d, cand_lat, cand_lon)
        if best:
            return best[1], best[2]
    return None


def process(path, write):
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    text = text.replace("\r\n", "\n")

    clat = float(re.search(r"^MapCenterLatitude=([-\d.]+)", text, re.M).group(1))
    clon = float(re.search(r"^MapCenterLongitude=([-\d.]+)", text, re.M).group(1))

    def to_ll(x, z):
        return clat + z / 60.0, clon + x / 60.0

    def to_xz(lat, lon):
        return round((lon - clon) * 60.0, 1), round((lat - clat) * 60.0, 1)

    chunks = re.split(r"(?=^\[)", text, flags=re.M)
    moves = []

    for i, chunk in enumerate(chunks):
        h = re.match(r"^\[(Neutral(?:Vessel|Biologic)\d+)\]", chunk)
        if not h:
            continue
        name = h.group(1)
        ty_m = re.search(r"^Type=(\S+)", chunk, re.M)
        ty = ty_m.group(1) if ty_m else "?"
        new_chunk = chunk

        # --- spawn position (and a biologic's matching spawn centre) ---
        pos = re.search(r"^RelativePositionInNM=([-\d.]+),([^,\n]*),([-\d.]+)$", new_chunk, re.M)
        if pos:
            x, mid, z = float(pos.group(1)), pos.group(2), float(pos.group(3))
            lat, lon = to_ll(x, z)
            if not water(lat, lon):
                fixed = nearest_water(lat, lon)
                if fixed:
                    nx, nz = to_xz(*fixed)
                    for key in ("RelativePositionInNM", "RandomSpawnCenter"):
                        new_chunk = re.sub(
                            rf"^{key}={re.escape(pos.group(1))},{re.escape(mid)},{re.escape(pos.group(3))}$",
                            lambda _, k=key, nx=nx, nz=nz, mid=mid: f"{k}={nx},{mid},{nz}",
                            new_chunk, flags=re.M)
                    moves.append(f"{name} ({ty}) spawn {lat:.2f},{lon:.2f} -> "
                                 f"{fixed[0]:.2f},{fixed[1]:.2f}")
                else:
                    moves.append(f"{name} ({ty}) spawn {lat:.2f},{lon:.2f} -> NO WATER FOUND")

        # --- waypoint legs ---
        wp = re.search(r"^Waypoints=(.+)$", new_chunk, re.M)
        if wp:
            legs, changed = [], False
            for leg in wp.group(1).split("|"):
                head, sep, action = leg.partition("/")
                parts = head.split(",")
                if len(parts) >= 3:
                    x, mid, z = float(parts[0]), parts[1], float(parts[2])
                    lat, lon = to_ll(x, z)
                    if not water(lat, lon):
                        fixed = nearest_water(lat, lon)
                        if fixed:
                            nx, nz = to_xz(*fixed)
                            head = f"{nx},{mid},{nz}"
                            changed = True
                            moves.append(f"{name} ({ty}) waypoint {lat:.2f},{lon:.2f} -> "
                                         f"{fixed[0]:.2f},{fixed[1]:.2f}")
                legs.append(head + sep + action)
            if changed:
                new_line = "Waypoints=" + "|".join(legs)
                new_chunk = re.sub(r"^Waypoints=.+$", lambda _: new_line,
                                   new_chunk, count=1, flags=re.M)

        # --- keep a biologic's wander circle off the beach ---
        centre = re.search(r"^RandomSpawnCenter=([-\d.]+),([^,\n]*),([-\d.]+)$", new_chunk, re.M)
        rng = re.search(r"^RandomSpawnRange=(\d+)$", new_chunk, re.M)
        if centre and rng:
            lat, lon = to_ll(float(centre.group(1)), float(centre.group(3)))
            limit = int(rng.group(1))
            while limit > 4:
                r = limit / 60.0
                if all(water(lat + r * math.cos(math.radians(d)),
                             lon + r * math.sin(math.radians(d)))
                       for d in range(0, 360, 30)):
                    break
                limit -= 2
            if limit != int(rng.group(1)):
                new_chunk = re.sub(r"^RandomSpawnRange=\d+$",
                                   lambda _, l=limit: f"RandomSpawnRange={l}",
                                   new_chunk, count=1, flags=re.M)
                moves.append(f"{name} ({ty}) spawn range {rng.group(1)} -> {limit} nm "
                             f"(wander circle reached land)")

        chunks[i] = new_chunk

    if moves and write:
        path.write_text("".join(chunks), encoding="utf-8", newline="\n")
    return moves


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", default=None, help="mission name without .ini")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    targets = ([MISSIONS / f"{args.mission}.ini"] if args.mission
               else sorted(MISSIONS.glob("*.ini")))
    total = 0
    for p in targets:
        if not p.exists():
            sys.exit(f"no such mission: {p}")
        moves = process(p, args.write)
        total += len(moves)
        print(f"=== {p.name}: {len(moves)} fix(es)")
        for m in moves:
            print("   ", m)
    if not total:
        print("every neutral vessel and biologic is already in water")
    elif not args.write:
        print("\nre-run with --write to apply")


if __name__ == "__main__":
    main()
