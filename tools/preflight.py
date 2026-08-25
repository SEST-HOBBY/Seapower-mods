#!/usr/bin/env python3
"""Resolve every reference the active mission and the SEST packs make.

The load order decides which copy of a file loads; it says nothing about
whether the thing you asked for is in that copy. A mission can name a unit no
enabled mod defines, or a LoadoutVariant the winning unit file does not list,
and Sea Power will not complain - the unit spawns with a default fit, or not at
all. Adding or reordering a mod can introduce that silently, because the file
still exists, it is just a different file now.

So this walks the references instead of the files:

  1. Type=<unit>            in the mission -> a winning unit file defines it
  2. <unit>=Squadron1,12    air groups     -> a winning aircraft file defines it
  3. LoadoutVariant=<name>  -> listed in that unit's AvailableLoadouts
  4. Station<N>=<store>     in SEST packs  -> a winning ammunition file

    python3 tools/preflight.py [mission name]

Exits non-zero if anything dangles.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import winning_file  # noqa: E402

UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units", "biologic")


def find_unit(uid):
    for kind in UNIT_DIRS:
        f = winning_file(f"{kind}/{uid}.ini")
        if f:
            return f
    return None


def available_loadouts(path):
    m = re.search(r"^AvailableLoadouts=(.+)$",
                  path.read_text(encoding="utf-8", errors="replace"), re.M)
    return [x.strip() for x in m.group(1).split(",")] if m else None


def main():
    name = " ".join(sys.argv[1:]) or next(
        l.strip() for l in (ROOT / "data" / "active-mission.txt")
        .read_text(encoding="utf-8").splitlines()
        if l.strip() and not l.startswith("#"))
    mission = ROOT / "integration" / "missions" / f"{name}.ini"
    if not mission.exists():
        sys.exit(f"no such mission: {mission}")

    problems, checked = [], 0
    print(f"mission: {name}\n")

    # --- 1 + 2 + 3: everything the mission names -----------------------------
    cur_unit = cur_file = None
    for n, line in enumerate(mission.read_text(encoding="utf-8",
                                               errors="replace").splitlines(), 1):
        line = line.strip()
        if m := re.match(r"^Type=(\S+)$", line):
            cur_unit = m.group(1)
            cur_file = find_unit(cur_unit)
            checked += 1
            if cur_file is None:
                problems.append(f"line {n}: Type={cur_unit} - no enabled mod defines it")
        elif m := re.match(r"^LoadoutVariant=(.+)$", line):
            want = m.group(1).strip()
            if cur_file is None:
                continue
            checked += 1
            avail = available_loadouts(cur_file)
            if avail is not None and want not in avail:
                problems.append(
                    f"line {n}: {cur_unit} LoadoutVariant={want} not offered by the "
                    f"winning file\n        has: {', '.join(avail)}\n"
                    f"        from: {cur_file.parts[-3]}")
        elif m := re.match(r"^([a-z0-9_.\-]+)=Squadron\d+,\d+", line):
            uid = m.group(1)
            checked += 1
            if find_unit(uid) is None:
                problems.append(f"line {n}: air group {uid} - no enabled mod defines it")

    # --- 4: every store the SEST loadouts hang on a pylon --------------------
    for pack in sorted((ROOT / "integration").glob("*/SEST_*")):
        for f in sorted(pack.rglob("*.ini")):
            if f.parent.name not in UNIT_DIRS:
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            for store in sorted({s.split("|")[0] for s in
                                 re.findall(r"^Station\d+=([A-Za-z]\S*)", text, re.M)}):
                checked += 1
                if winning_file(f"ammunition/{store}.ini") is None:
                    problems.append(
                        f"{pack.name}/{f.name}: Station store '{store}' has no "
                        f"ammunition file")

    print(f"resolved {checked} reference(s)\n")
    if problems:
        print(f"{len(problems)} DANGLING reference(s):\n")
        for p in problems:
            print(f"   {p}\n")
        sys.exit(1)
    print("every unit, air group, loadout variant and pylon store resolves")


if __name__ == "__main__":
    main()
