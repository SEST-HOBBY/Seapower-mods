#!/usr/bin/env python3
"""Resolve every reference the active mission and the SEST packs make.

The load order decides which copy of a file loads; it says nothing about
whether the thing you asked for is in that copy. A mission can name a unit no
enabled mod defines, a LoadoutVariant the winning unit file does not list,
an aircraft with no variant and no 'Default' to fall back on, a hull variant
the winning _variants.ini does not declare, and Sea Power will not complain -
the unit spawns with a default fit, or not at all, or the editor shows
"MISSING: <unit> name or squadron reference". Adding or reordering a mod can
introduce that silently, because the file still exists, it is just a
different file now.

So this walks the references instead of the files:

  1. Type=<unit>            in the mission -> a winning unit file defines it
  2. <unit>=Squadron1,12    air groups     -> a winning aircraft file defines it
  3. LoadoutVariant=<name>  -> listed in that unit's AvailableLoadouts
  4. VariantReference=<v>   -> declared by the winning <unit>_variants.ini
  5. Station<N>=<store>     in SEST packs  -> a winning ammunition file

    python3 tools/preflight.py [mission name]   # the active mission by default
    python3 tools/preflight.py --all            # every mission the installer deploys

The installer copies every .ini under integration/missions/ into the game,
backups and scenarios included, and each opens in the editor - so a defect
that crashes the editor is live in every file that carries it, not just the
one the tooling refreshes. --all is the sweep for that.

Exits non-zero if anything dangles.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MISSIONS = ROOT / "integration" / "missions"
sys.path.insert(0, str(MISSIONS))
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


def variant_check(unit_file, uid, want):
    """None if VariantReference=<want> is valid for the winning unit, else why not.

    The engine pools only the first NumberOfVariants sections, so a [VariantN]
    block past the declared count is present in the file yet unselectable -
    the (2000s) Nimitz shipped exactly that, and AUS DEF's Carl Vinson came up
    "MISSING: usn_cvn_nimitz_2000s name or squadron reference".
    """
    if want == "Default":
        return None
    vf = winning_file(f"{unit_file.parent.name}/{uid}_variants.ini")
    if vf is None:
        return (f"{uid} VariantReference={want} but the winning unit has no "
                f"_variants.ini - only Default is valid\n        from: {unit_file.parts[-3]}")
    body = vf.read_text(encoding="utf-8", errors="replace")
    sections = re.findall(r"^\[(Variant\d+)\]", body, re.M)
    declared = re.search(r"^NumberOfVariants=(\d+)", body, re.M)
    n = int(want[7:]) if re.fullmatch(r"Variant\d+", want) else None
    ok = want in sections and (declared is None or (n is not None and n <= int(declared.group(1))))
    if ok:
        return None
    return (f"{uid} VariantReference={want} is outside the winning variants file\n"
            f"        declares: NumberOfVariants={declared.group(1) if declared else '?'}, "
            f"sections: {len(sections)}\n        from: {vf.parts[-3]}")


def check_mission(mission):
    """-> (problems, references checked) for one mission file."""
    problems, checked = [], 0
    cur_unit = cur_file = None
    # An aircraft entry with NO LoadoutVariant makes the game resolve a default
    # loadout at display time. If the winning unit file's AvailableLoadouts does
    # not list "Default" there is nothing to resolve to, and the map panel's
    # IniToPlanConverter dies with "An item with the same key has already been
    # added. Key: <aircraft id>" - confirmed in game on plaaf_kj-500, and
    # confirmed fixed once the variants were made explicit. Track each aircraft
    # block and judge it when the next section starts.
    pending = None          # (line, unit, file) awaiting a verdict
    saw_variant = False
    in_aircraft = False

    def close_block():
        nonlocal pending, saw_variant
        if pending and not saw_variant:
            ln, uid, f = pending
            avail = available_loadouts(f)
            if avail is not None and "Default" not in avail:
                problems.append(
                    f"line {ln}: {uid} names no LoadoutVariant and its winning file "
                    f"offers no 'Default' to fall back on\n"
                    f"        has: {', '.join(avail)}\n"
                    f"        fix: integration/missions/fix_loadout_variants.py --all --write")
        pending = None
        saw_variant = False

    for n, line in enumerate(mission.read_text(encoding="utf-8",
                                               errors="replace").splitlines(), 1):
        line = line.strip()
        if line.startswith("["):
            close_block()
            in_aircraft = bool(re.match(r"^\[Taskforce\d+Aircraft\d+\]", line))
            cur_unit = cur_file = None
        # \S+ would miss ids with spaces ("plaf_j16a block3" is a real file)
        # and leave cur_unit stale - six J-16 variant errors were blamed on
        # the B-52O above them before this handled spaces.
        if m := re.match(r"^Type=(.+?)\s*$", line):
            cur_unit = m.group(1)
            cur_file = find_unit(cur_unit)
            checked += 1
            if cur_file is None:
                problems.append(f"line {n}: Type={cur_unit} - no enabled mod defines it")
            elif in_aircraft:
                pending = (n, cur_unit, cur_file)
                checked += 1
        elif m := re.match(r"^LoadoutVariant=(.+)$", line):
            want = m.group(1).strip()
            saw_variant = True
            if cur_file is None:
                continue
            checked += 1
            avail = available_loadouts(cur_file)
            if avail is not None and want not in avail:
                problems.append(
                    f"line {n}: {cur_unit} LoadoutVariant={want} not offered by the "
                    f"winning file\n        has: {', '.join(avail)}\n"
                    f"        from: {cur_file.parts[-3]}")
        elif m := re.match(r"^VariantReference=(\S+)", line):
            # Only judged when the unit itself resolved: an unknown Type is
            # already reported above, and has no variants file to consult.
            if cur_file is None or in_aircraft:
                continue
            checked += 1
            why = variant_check(cur_file, cur_unit, m.group(1))
            if why:
                problems.append(f"line {n}: {why}")
        elif m := re.match(r"^([a-z0-9_.\-]+)=Squadron\d+,\d+", line):
            uid = m.group(1)
            checked += 1
            if find_unit(uid) is None:
                problems.append(f"line {n}: air group {uid} - no enabled mod defines it")

    close_block()   # the mission's last aircraft block has no following section
    return problems, checked


def check_packs():
    """-> (problems, checked): every store the SEST loadouts hang on a pylon."""
    problems, checked = [], 0
    for pack in sorted((ROOT / "integration").glob("*/SEST_*")):
        if pack.parent.name == "dist":   # dist = the consolidated deployable; its content is checked via the source packs
            continue
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
    return problems, checked


def active_mission():
    return next(
        l.strip() for l in (ROOT / "data" / "active-mission.txt")
        .read_text(encoding="utf-8").splitlines()
        if l.strip() and not l.startswith("#"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mission", nargs="*", help="mission name without .ini (default: the active mission)")
    ap.add_argument("--all", action="store_true",
                    help="every .ini under integration/missions/, i.e. everything the installer deploys")
    args = ap.parse_args()

    if args.all:
        missions = sorted(MISSIONS.rglob("*.ini"))
    else:
        name = " ".join(args.mission) or active_mission()
        missions = [MISSIONS / f"{name}.ini"]
        if not missions[0].exists():
            sys.exit(f"no such mission: {missions[0]}")

    total_problems, total_checked, bad_missions = [], 0, 0
    for mission in missions:
        label = mission.relative_to(MISSIONS).with_suffix("").as_posix()
        problems, checked = check_mission(mission)
        total_checked += checked
        if args.all:
            status = f"{len(problems)} dangling" if problems else "clean"
            print(f"  {status:>14}  {label}")
        else:
            print(f"mission: {label}\n")
        if problems:
            bad_missions += 1
            total_problems += [f"{label}: {p}" if args.all else p for p in problems]

    pack_problems, pack_checked = check_packs()
    total_checked += pack_checked
    total_problems += pack_problems

    print(f"\nresolved {total_checked} reference(s)"
          + (f" across {len(missions)} mission(s), {bad_missions} with dangling references"
             if args.all else "") + "\n")
    if total_problems:
        print(f"{len(total_problems)} DANGLING reference(s):\n")
        for p in total_problems:
            print(f"   {p}\n")
        sys.exit(1)
    print("every unit, air group, loadout variant, hull variant and pylon store resolves")


if __name__ == "__main__":
    main()
