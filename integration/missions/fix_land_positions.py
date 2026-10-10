#!/usr/bin/env python3
"""Move any neutral vessel or sea life that sits on land into the water, and
any land unit that stands in the sea onto firm ground.

Ships and whales placed by hand or by generator can end up over a coastline
or an island, where they either fail to spawn or look absurd. This checks
every spawn position, every waypoint leg and every biologic RandomSpawnCenter
in a mission against a real land/sea mask, and relocates only the offending
points to the nearest water.

The relocation is a spiral search outward from the bad point in 0.05-degree
steps, so a unit moves the shortest distance that gets it wet and stays where
the designer meant it to be. A biologic's RandomSpawnRange is also clamped so
its wander circle cannot reach back onto the shore.

Land units get the opposite check. The game draws its coast from a 30
arc-second (about 1 km) elevation grid and floats a land unit at one metre
wherever the ground under it is lower (terrain.ini MinHeightForLandUnits=1.0,
docs/design-notes.md), so a radar the mask puts a few hundred metres inside
the coast can still stand in the sea in game. A land unit therefore needs
land all round it out to FIRM_KM; one that has less moves the shortest
distance that gives it that, keeping clear of the other land units. Ports and
oil rigs belong at the water's edge and airbases carry their own ground, so
those stay where they are. On a reef the game's terrain does not have (the
Spratly and Paracel bases), there is no ground to move to: the base's own
model is the island, so a vehicle or radar there moves onto the base's
pavement - a taxiway or apron, off the runway and off the parking stands -
while a site that brings its own ground (a SAM site, a fuel farm) stays.

Everything else in the mission is untouched: only the coordinate numbers on
offending lines are rewritten.

Requires the global-land-mask package (pip install global-land-mask numpy).

Usage (repo root):
    python3 integration/missions/fix_land_positions.py                  # report
    python3 integration/missions/fix_land_positions.py --write          # apply
    python3 integration/missions/fix_land_positions.py --mission "NORTHERN FRONT III" --write
"""
import argparse
import functools
import math
import re
import sys
from pathlib import Path

try:
    from global_land_mask import globe
except ImportError:
    sys.exit("needs the land mask: pip install global-land-mask numpy")

MISSIONS = Path(__file__).resolve().parent
sys.path.insert(0, str(MISSIONS))
from refine_civ_traffic import winning_file  # noqa: E402

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


# --- land units ----------------------------------------------------------
FIRM_KM = 0.6            # land all round a land unit, this far
RINGS_KM = (0.15, 0.3, 0.45, 0.6)
SEARCH_NM = 6.0          # the furthest a land unit is moved to reach firm ground
SPACING_NM = 0.05        # about 90 m between land units
PAVE_SPACING_NM = 0.015  # about 28 m between units on a reef base's pavement
PLATE_M2 = 50000         # a unit this large brings its own ground: a SAM site, a fuel farm
UNIT_NM = 100 / 1852     # a land unit's own layout is in 100 m units (BottomArea agrees)
STAYS = {"OilRig", "Port", "Airbase"}


def wrap(lon):
    return ((lon + 180.0) % 360.0) - 180.0


def ground(lat, lon):
    """How far land reaches all round (lat, lon), in km: -1 when the point
    itself is sea, else the widest ring of RINGS_KM that is land all round."""
    if not globe.is_land(lat, wrap(lon)):
        return -1.0
    k = 111.32 * max(0.2, math.cos(math.radians(lat)))
    best = 0.0
    for r in RINGS_KM:
        for deg in range(0, 360, 30):
            a = math.radians(deg)
            if not globe.is_land(lat + r / 111.32 * math.cos(a), wrap(lon + r / k * math.sin(a))):
                return best
        best = r
    return best


def firm_ground(lat, lon, avoid=(), spacing_nm=SPACING_NM):
    """The nearest point to (lat, lon) within SEARCH_NM that has FIRM_KM of
    land all round and is spacing_nm from every (lat, lon) in avoid, rounded
    to 4 places; (lat, lon) itself when it already qualifies; None when
    nothing does. For a builder placing one land unit at a time."""
    k = max(0.2, math.cos(math.radians(lat)))
    for ring in range(0, int(SEARCH_NM / 0.1) + 1):
        r = ring * 0.1
        for deg in (range(0, 360, 15) if ring else (0,)):
            a = math.radians(deg)
            p = (round(lat + r * math.cos(a) / 60.0, 4), round(lon + r * math.sin(a) / (60.0 * k), 4))
            if ground(*p) >= FIRM_KM and all(
                    math.hypot((p[0] - q[0]) * 60.0, (p[1] - q[1]) * 60.0 * k) >= spacing_nm for q in avoid):
                return p
    return None


@functools.lru_cache(maxsize=None)
def land_unit(ty):
    """(LandUnitSubType, BottomArea in m2, unit file text) of a land unit type."""
    f = winning_file(f"land_units/{ty}.ini")
    if f is None:
        return "", 0, ""
    text = f.read_text(encoding="utf-8", errors="replace")
    sub = re.search(r"^LandUnitSubType=(\w+)", text, re.M)
    area = re.search(r"^BottomArea=(\d+)", text, re.M)
    return (sub.group(1) if sub else ""), (int(area.group(1)) if area else 0), text


def _xz(v):
    a = v.split("/")[0].split(",")
    return (float(a[0]), float(a[2])) if len(a) >= 3 else None


@functools.lru_cache(maxsize=None)
def pavement(ty):
    """Points on an airbase model's pavement, in its own 100 m units (x east,
    z north at heading 0): the taxi points, the taxi paths every 30 m, and the
    middle of every pair of them closer than 100 m, leaving out anything
    within 80 m of the runway or 15 m of a parking stand."""
    text = land_unit(ty)[2]
    runway, stands, paved, named, paths = [], [], [], {}, []
    for chunk in re.split(r"(?=^\[)", text, flags=re.M):
        head = re.match(r"^\[((\w+?)\d*)\]", chunk)
        if not head:
            continue
        label, name = head.groups()
        keys = dict(re.findall(r"^(\w+)=([^\n/]*?)\s*(?://.*)?$", chunk, re.M))
        here = _xz(keys.get("RidePosition") or keys.get("Position") or "")
        if here:
            named[label] = here
        if name in ("LaunchPoint", "RecoveryPoint") and here:
            runway.append(here)
        elif name == "Elevator" and _xz(keys.get("SpawnPosition", "")):
            stands.append(_xz(keys["SpawnPosition"]))
        elif name == "TaxiPoint" and here:
            paved.append(here)
        elif name == "TaxiPath":
            m = re.search(r"^Waypoints=(.+)$", chunk, re.M)
            paths.append((keys.get("From", "").strip(), [q for q in (_xz(leg) for leg in m.group(1).split("|")) if q]
                          if m else [], keys.get("To", "").strip()))
    paved += [leg for _, legs, _ in paths for leg in legs]
    paved += [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for i, a in enumerate(paved) for b in paved[i + 1:]
              if math.dist(a, b) < 1.0]
    for start, legs, end in paths:          # From, the waypoints, To - every 30 m along the taxiway
        line = [named[start]] * (start in named) + legs + [named[end]] * (end in named)
        for a, b in zip(line, line[1:]):
            n = max(1, int(math.dist(a, b) / 0.3))
            paved += [(a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n) for j in range(1, n)]
    runway = [p for p in runway if p]
    ends = max(((a, b) for a in runway for b in runway), key=lambda ab: math.dist(*ab), default=None)

    def off_runway(p):
        if not ends or math.dist(*ends) < 1.0:
            return True
        (ax, az), (bx, bz) = ends
        t = max(-0.1, min(1.1, ((p[0] - ax) * (bx - ax) + (p[1] - az) * (bz - az)) / math.dist(*ends) ** 2))
        return math.dist(p, (ax + t * (bx - ax), az + t * (bz - az))) >= 0.8

    out, seen = [], set()
    for p in paved:
        key = (round(p[0], 1), round(p[1], 1))
        if key in seen or not off_runway(p) or any(math.dist(p, s) < 0.15 for s in stands if s):
            continue
        seen.add(key)
        out.append(p)
    return tuple(out)


def process_land(chunks, to_ll, clat):
    """Move land units in `chunks` onto firm ground; returns the move lines."""
    def nm(a, b):
        k = math.cos(math.radians(clat + (a[1] + b[1]) / 120.0))
        return math.hypot((a[0] - b[0]) * k, a[1] - b[1])

    units = []    # (chunk index, section, type, x, mid, z, heading)
    for i, chunk in enumerate(chunks):
        h = re.match(r"^\[((Taskforce\d+|Neutral)LandUnit\d+)\]", chunk)
        if not h:
            continue
        ty = re.search(r"^Type=(\S+)", chunk, re.M)
        pos = re.search(r"^RelativePositionInNM=([-\d.]+),([^,\n]*),([-\d.]+)$", chunk, re.M)
        hdg = re.search(r"^Heading=([-\d.]+)", chunk, re.M)
        if ty and pos:
            units.append([i, h.group(1), h.group(2), ty.group(1), float(pos.group(1)), pos.group(2),
                          float(pos.group(3)), float(hdg.group(1)) if hdg else 0.0])
    occupied = {u[1]: (u[4], u[6]) for u in units}
    moves = []

    def clear(p, me, gap):
        return all(nm(p, q) >= gap for k, q in occupied.items() if k != me)

    def firm_near(u):
        """The nearest firm ground within SEARCH_NM, and failing that the
        widest land within 2 nm (a small island): ((x, z), km) or None each."""
        x, z = u[4], u[6]
        k = max(0.2, math.cos(math.radians(clat + z / 60.0)))
        some = None
        for ring in range(1, int(SEARCH_NM / 0.1) + 1):
            r = ring * 0.1
            for deg in range(0, 360, 15):
                a = math.radians(deg)
                p = (round(x + r * math.sin(a) / k, 2), round(z + r * math.cos(a), 2))   # as written
                g = ground(*to_ll(*p))
                if g >= FIRM_KM and clear(p, u[1], SPACING_NM):
                    return (p, g), None
                if g >= 0.15 and r <= 2.0 and clear(p, u[1], SPACING_NM) and (some is None or g > some[1]):
                    some = (p, g)
        return None, some

    def on_pavement(u):
        """The nearest free pavement point of a same-side airbase within
        SEARCH_NM that stands on a reef itself."""
        best = None
        for b in units:
            if b[2] != u[2] or land_unit(b[3])[0] != "Airbase" or nm((b[4], b[6]), (u[4], u[6])) > SEARCH_NM:
                continue
            if ground(*to_ll(b[4], b[6])) >= FIRM_KM:
                continue
            h = math.radians(b[7])
            k = max(0.2, math.cos(math.radians(clat + b[6] / 60.0)))
            for px, pz in pavement(b[3]):
                east = (px * math.cos(h) + pz * math.sin(h)) * UNIT_NM
                north = (-px * math.sin(h) + pz * math.cos(h)) * UNIT_NM
                p = (round(b[4] + east / k, 2), round(b[6] + north, 2))
                d = nm(p, (u[4], u[6]))
                if (best is None or d < best[0]) and clear(p, u[1], PAVE_SPACING_NM):
                    best = (d, p, b)
        return best

    for u in units:
        sub, area, _ = land_unit(u[3])
        if sub in STAYS:
            continue
        lat, lon = to_ll(u[4], u[6])
        g = ground(lat, lon)
        if g >= FIRM_KM:
            continue
        where = "in the sea" if g < 0 else f"{g * 1000:.0f} m from the sea"
        firm, some = firm_near(u)
        if firm:
            p, how = firm[0], f"onto land ({firm[1] * 1000:.0f} m all round)"
        elif area >= PLATE_M2 and g < 0:
            moves.append(f"{u[1]} ({u[3]}) {lat:.3f},{lon:.3f} {where}: no firm land within "
                         f"{SEARCH_NM:.0f} nm; left, it brings its own ground")
            continue
        else:
            # No firm ground: a reef base's pavement is surer than a sliver of
            # island the mask has and the game may not.
            pave = None if area >= PLATE_M2 else on_pavement(u)
            if pave and pave[0] < 0.01:
                continue                      # already on the base's pavement
            if pave:
                p, how = pave[1], f"onto the pavement of {pave[2][1]} ({pave[2][3]})"
            elif some and some[1] > max(g, 0):
                p, how = some[0], f"onto the widest land near ({some[1] * 1000:.0f} m all round)"
            elif g > 0:
                moves.append(f"{u[1]} ({u[3]}) {lat:.3f},{lon:.3f} {where}: the widest land within "
                             "2 nm (a small island); left")
                continue
            else:
                moves.append(f"{u[1]} ({u[3]}) {lat:.3f},{lon:.3f} {where}: NO FIRM GROUND within "
                             f"{SEARCH_NM:.0f} nm and no reef base to stand on; left")
                continue
        nx, nz = round(p[0], 2), round(p[1], 2)
        chunk = chunks[u[0]]
        chunks[u[0]] = re.sub(r"^RelativePositionInNM=[-\d.]+,([^,\n]*),[-\d.]+$",
                              lambda m, nx=nx, nz=nz: f"RelativePositionInNM={nx:.2f},{m.group(1)},{nz:.2f}",
                              chunk, count=1, flags=re.M)
        occupied[u[1]] = (nx, nz)
        moved = nm((nx, nz), (u[4], u[6]))
        nlat, nlon = to_ll(nx, nz)
        moves.append(f"{u[1]} ({u[3]}) {lat:.3f},{lon:.3f} {where} -> {nlat:.3f},{nlon:.3f}, "
                     f"{moved:.2f} nm {how}")
    return moves


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

    moves += process_land(chunks, to_ll, clat)

    if moves and write:
        path.write_text("".join(chunks), encoding="utf-8", newline="\n")
    return moves


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", default=None, help="mission name without .ini")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    targets = ([MISSIONS / f"{args.mission}.ini"] if args.mission
               else sorted(MISSIONS.glob("*.ini")) + sorted((MISSIONS / "scenarios").glob("*.ini")))
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
        print("every neutral vessel and biologic is in water, every land unit on firm ground")
    elif not args.write:
        print("\nre-run with --write to apply")


if __name__ == "__main__":
    main()
