#!/usr/bin/env python3
"""Add an eastern-axis red air package to a mission.

The NORTHERN FRONT scenarios push the red air threat down from the north and
north-west. This appends a second axis coming in from the EAST - through the
Coral Sea and the Torres Strait - so the defence cannot simply face one way.

The package is a proper one rather than a lone flight: a J-20A sweep out
front, a JH-7A maritime strike element behind it, and a KJ-500 AEW aircraft
orbiting back east with a J-16D electronic-attack escort.

Every unit is APPENDED past the highest Taskforce2 aircraft index already in
use, with new formations added after the existing ones and the counts bumped
to match. No existing section is read back out and rewritten, so hand-placed
units keep their positions exactly.

It is also a REPAIR tool. Idempotence is per formation, not per package, and
before creating anything it looks for aircraft of the right type that already
exist but belong to no formation - deleting a formation line in the mission
editor leaves the aircraft behind, flying its route with no label on the
tacmap, which reads as "the AEW is gone" when it is still very much there.
Those orphans are adopted back into the restored formation instead of a
duplicate being spawned next to them.

Positions come from the mission's own MapCenter, using the same lat/lon
mapping as the other mission tools.

Usage (repo root):
    python3 integration/missions/add_red_air_group.py --mission "NORTHERN FRONT III FINAL"
    python3 integration/missions/add_red_air_group.py --mission "..." --write
"""
import argparse
import math
import re
import sys
from pathlib import Path

MISSIONS = Path(__file__).resolve().parent

# (type, count, altitude ft, start lat/lon, route lat/lon points, formation name)
PACKAGE = [
    ("plaaf_j-20a", 4, 38000, (-10.50, 147.50),
     [(-10.80, 143.50), (-11.20, 140.00)], "Eastern Sweep"),
    ("plaaf_jh7a", 4, 30000, (-9.80, 148.60),
     [(-10.00, 144.00), (-10.80, 141.00)], "Eastern Strike"),
    ("plaaf_kj-500", 1, 33000, (-9.00, 149.00),
     [(-9.50, 147.00), (-8.60, 148.60), (-9.00, 149.00)], "Eastern AEW"),
    ("plaf_j16d", 2, 33000, (-9.20, 148.80),
     [(-9.60, 147.20), (-8.80, 148.40), (-9.20, 148.80)], "Eastern AEW"),
]

AIRCRAFT_TEMPLATE = """[Taskforce2Aircraft{n}]
Type={type}
SquadronReference={squadron}
UnlimitedFuel=False
WeaponStatus=Free
RadarsActive={radars}
CrewSkill=Veteran
Morale=3
RelativePositionInNM={x},{alt},{z}
Telegraph=3
Heading={heading}
Waypoints={waypoints}
"""


def make_ll(text):
    lat = re.search(r"^MapCenterLatitude=([-\d.]+)", text, re.M)
    lon = re.search(r"^MapCenterLongitude=([-\d.]+)", text, re.M)
    if not (lat and lon):
        sys.exit("mission has no MapCenter")
    clat, clon = float(lat.group(1)), float(lon.group(1))

    def ll(la, lo):
        return round((lo - clon) * 60.0, 1), round((la - clat) * 60.0, 1)
    return ll


def squadron_for(type_id):
    """A squadron the winning provider actually defines, else Default."""
    sys.path.insert(0, str(MISSIONS))
    from refine_civ_traffic import winning_file
    f = winning_file(f"aircraft/{type_id}_squadrons.ini")
    if f is None:
        return "Default"
    have = re.findall(r"^\[(Squadron\d+)\]",
                      f.read_text(encoding="utf-8", errors="replace"), re.M)
    return have[0] if have else "Default"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", required=True)
    ap.add_argument("--group", action="append", default=None,
                    help="restore only this formation (repeatable). Without it every "
                         "missing formation is restored - which is wrong if you replaced "
                         "one deliberately, e.g. swapping the J-20A Eastern Sweep for a "
                         "J-50 Eastern Stealth Cover. Name what you want back.")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    path = MISSIONS / f"{args.mission}.ini"
    if not path.exists():
        sys.exit(f"no such mission: {path}")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    text = text.replace("\r\n", "\n")

    ll = make_ll(text)

    # Which of the package's formations already exist, by NAME. A formation the
    # editor removed comes back; one that is present is left completely alone.
    have_forms = set(re.findall(r"^Taskforce2_Formation\d+=[^|]*\|([^|]*)\|", text, re.M))

    # Aircraft that exist but are in no formation, by type. These are what a
    # deleted formation line leaves behind.
    in_formation = set()
    for m in re.finditer(r"^Taskforce2_Formation\d+=([^|]*)\|", text, re.M):
        in_formation.update(m.group(1).split(","))
    orphans = {}
    for m in re.finditer(r"^\[(Taskforce2Aircraft\d+)\]\n(.*?)(?=^\[|\Z)", text, re.S | re.M):
        if m.group(1) in in_formation:
            continue
        ty = re.search(r"^Type=(\S+)", m.group(2), re.M)
        if ty:
            orphans.setdefault(ty.group(1), []).append(m.group(1))

    wanted = {g for _, _, _, _, _, g in PACKAGE}
    if args.group:
        unknown = sorted(set(args.group) - wanted)
        if unknown:
            sys.exit(f"not formations this package defines: {unknown}\n"
                     f"  known: {', '.join(sorted(wanted))}")
        wanted &= set(args.group)
    missing = sorted(wanted - have_forms)
    if not missing:
        print(f"{args.mission}: nothing to restore — "
              f"{', '.join(sorted(wanted))} already present")
        return
    skipped = sorted((set(g for _, _, _, _, _, g in PACKAGE) - have_forms) - set(missing))
    if skipped:
        print(f"{args.mission}: leaving {', '.join(skipped)} alone (not requested)")
    print(f"{args.mission}: restoring {', '.join(missing)}")
    idx = [int(m) for m in re.findall(r"^\[Taskforce2Aircraft(\d+)\]", text, re.M)]
    n = max(idx) if idx else 0
    form_idx = [int(m) for m in re.findall(r"^Taskforce2_Formation(\d+)=", text, re.M)]
    fnum = max(form_idx) if form_idx else 0

    blocks, formations, added, adopted = [], {}, 0, 0
    for type_id, count, alt, start, route, group in PACKAGE:
        if group not in missing:
            continue
        # Re-use what is already flying before creating anything new.
        take = orphans.get(type_id, [])[:count]
        for unit in take:
            orphans[type_id].remove(unit)
            adopted += 1
            formations.setdefault(group, []).append(unit)
        count -= len(take)
        if not count:
            continue
        sq = squadron_for(type_id)
        sx, sz = ll(*start)
        pts = [ll(*p) for p in route]
        legs = "|".join(f"{x},{alt},{z}" for x, z in pts)
        hdg = int(round(math.degrees(math.atan2(pts[0][0] - sx, pts[0][1] - sz))))
        for i in range(count):
            n += 1
            added += 1
            # Fan the flight out slightly so they do not spawn stacked.
            blocks.append(AIRCRAFT_TEMPLATE.format(
                n=n, type=type_id, squadron=sq,
                radars="False" if "j-20" in type_id else "True",
                x=round(sx + i * 1.5, 1), alt=alt, z=round(sz + i * 1.5, 1),
                heading=hdg, waypoints=legs))
            formations.setdefault(group, []).append(f"Taskforce2Aircraft{n}")

    # Keep each formation's members in index order, so an adopted aircraft and
    # a newly created one do not read as two separate flights.
    for group, members in formations.items():
        fnum += 1
        formations[group] = (fnum, sorted(
            members, key=lambda u: int(u.split("Aircraft")[1])))

    # Insert the new formation lines after the last Taskforce2 formation.
    lines = []
    for group, (fnum_, members) in formations.items():
        lines.append(f"Taskforce2_Formation{fnum_}={','.join(members)}|{group}|Vic|0.1|OverrideSpawnPositions")
    last_form = list(re.finditer(r"^Taskforce2_Formation\d+=.*$", text, re.M))[-1]
    text = text[:last_form.end()] + "\n" + "\n".join(lines) + text[last_form.end():]

    # Bump the counts.
    if added:
        text = re.sub(r"^NumberOfTaskforce2Aircraft=\d+$",
                      lambda _: f"NumberOfTaskforce2Aircraft={n}", text, count=1, flags=re.M)
    nf = re.search(r"^Taskforce2_NumberOfFormations=(\d+)$", text, re.M)
    if nf:
        text = re.sub(r"^Taskforce2_NumberOfFormations=\d+$",
                      lambda _: f"Taskforce2_NumberOfFormations={fnum}", text,
                      count=1, flags=re.M)

    if blocks:
        text = text.rstrip("\n") + "\n\n" + "\n".join(blocks)

    for group, (fnum_, members) in formations.items():
        print(f"  Formation{fnum_} '{group}': {len(members)} aircraft")
    print(f"{args.mission}: {adopted} existing aircraft re-formed, "
          f"+{added} created (Taskforce2 now {n})")
    if args.write:
        path.write_text(text, encoding="utf-8", newline="\n")
        print("  written")
    else:
        print("  re-run with --write to apply")


if __name__ == "__main__":
    main()
