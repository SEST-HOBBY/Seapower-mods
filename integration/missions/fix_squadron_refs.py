#!/usr/bin/env python3
"""Repair unresolved squadron references in a mission's airbase AirGroups.

An airbase [AirGroup] line reads

    <aircraft_id>=Squadron4,6|Squadron5,6

where each SquadronN must be a real section in that aircraft's
<id>_squadrons.ini. Missions built in the editor can name squadrons the
providing mod does not define (e.g. usaf_f-22_s6 offers only Default and
Squadron1, but a mission asks for Squadron4-7), which leaves those aircraft
without a livery at spawn.

This remaps every unresolved SquadronN to one the winning mod actually
defines (preferring Squadron1, else Default) and folds duplicates together
so the TOTAL AIRCRAFT COUNT on the line is preserved exactly. Nothing else
in the mission is touched.

Squadron files are resolved through the canonical Mod Manager order, so the
check matches the copy the game really loads.

Usage (repo root):
    python3 integration/missions/fix_squadron_refs.py                  # report only
    python3 integration/missions/fix_squadron_refs.py --write          # apply
    python3 integration/missions/fix_squadron_refs.py --mission "NORTHERN FRONT III" --write
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_civ_traffic import winning_file  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = Path(__file__).resolve().parent

AIRGROUP_LINE = re.compile(r"^([A-Za-z0-9_.\-]+)=((?:Squadron\d+,\d+\|?)+)$")


def available(type_id):
    """Squadron section names the winning <type_id>_squadrons.ini defines."""
    f = winning_file(f"aircraft/{type_id}_squadrons.ini")
    if f is None:
        return None
    return set(re.findall(r"^\[(Squadron\d+|Default)\]", f.read_text(
        encoding="utf-8", errors="replace"), re.M))


def fallback(have):
    """Which squadron an unresolved reference should become."""
    if "Squadron1" in have:
        return "Squadron1"
    if "Default" in have:
        return "Default"
    return sorted(have)[0] if have else None


def fix_line(type_id, spec, have):
    """Return (new_spec, remaps) preserving the total aircraft count."""
    target = fallback(have)
    if target is None:
        return spec, []
    order, counts, remaps = [], {}, []
    for sq, n in re.findall(r"(Squadron\d+),(\d+)", spec):
        n = int(n)
        if sq not in have:
            remaps.append(f"{sq}->{target}")
            sq = target
        if sq not in counts:
            order.append(sq)
            counts[sq] = 0
        counts[sq] += n
    return "|".join(f"{sq},{counts[sq]}" for sq in order), remaps


def process(path, write):
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    out, changed, total_before, total_after = [], 0, 0, 0
    for line in text.split("\n"):
        m = AIRGROUP_LINE.match(line)
        if not m:
            out.append(line)
            continue
        type_id, spec = m.group(1), m.group(2)
        have = available(type_id)
        if have is None:
            out.append(line)
            continue
        new_spec, remaps = fix_line(type_id, spec, have)
        before = sum(int(n) for n in re.findall(r",(\d+)", spec))
        after = sum(int(n) for n in re.findall(r",(\d+)", new_spec))
        total_before += before
        total_after += after
        if remaps:
            assert before == after, f"{type_id}: aircraft count changed {before}->{after}"
            print(f"  {path.name} {type_id}: {', '.join(remaps)}  "
                  f"({spec} -> {new_spec}, {after} aircraft kept)")
            changed += 1
            out.append(f"{type_id}={new_spec}")
        else:
            out.append(line)
    if changed and write:
        path.write_text("\n".join(out), encoding="utf-8", newline="\n")
    return changed, total_before, total_after


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", default=None,
                    help="mission name without .ini (default: every mission)")
    ap.add_argument("--write", action="store_true", help="apply the fixes")
    args = ap.parse_args()

    targets = ([MISSIONS / f"{args.mission}.ini"] if args.mission
               else sorted(MISSIONS.glob("*.ini")))
    total = 0
    for p in targets:
        if not p.exists():
            sys.exit(f"no such mission: {p}")
        changed, before, after = process(p, args.write)
        total += changed
        if changed:
            print(f"  {p.name}: {changed} line(s), aircraft total {before} -> {after}")
    if not total:
        print("all squadron references already resolve")
    elif not args.write:
        print(f"\n{total} line(s) would change - re-run with --write to apply")


if __name__ == "__main__":
    main()
