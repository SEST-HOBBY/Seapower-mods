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

    python3 tools/preflight.py [mission name]   # the active mission by default;
                                                # also finds a campaign mission
    python3 tools/preflight.py --all            # every mission the installer deploys

Exits non-zero if anything dangles; --all is narrower, see below.

The installer copies every .ini under integration/missions/ into the game
(drafts and scenarios included; only the old "<name> backup-<stamp>"
snapshots are skipped), and each opens in the editor - so a defect that
crashes the editor is live in every file that carries it, not just the one
the tooling refreshes. --all is the sweep for that. It lists every dangling
reference in every deployed mission, but only the editor crash (and a SEST
pylon store with no file, as in the default run) fails it. The older saves
also name units and fits that mods have since dropped or renamed, which the
game survives (the unit spawns with a default fit, or not at all), and
holding the sweep to those would keep it red for good.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MISSIONS = ROOT / "integration" / "missions"
sys.path.insert(0, str(MISSIONS))
sys.path.insert(0, str(ROOT / "integration"))
from refine_civ_traffic import winning_file  # noqa: E402
from fix_loadout_variants import deployed_missions  # noqa: E402
from common.snapshot import stale_mods  # noqa: E402

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


def stale_note():
    """The paragraph that follows a failure while mods-source is behind the catalog.

    This tool resolves ids against the files on disk, so a mod that is not
    exported looks exactly like a typo: nothing is left in mods-source to
    attribute the id to, and the lines above will say "no enabled mod defines
    it" about a unit sitting in the user's game working perfectly.

    The 2026-09-13 export pruned four mods whose folders it did not find. Two, the
    B-52H (3741944366) and the B-1B (3652097318), were known to be back the
    same day. The other two, the SAAB AEW&C pack (3673250557) and the Type 003
    Fujian (3663564190), were judged gone for good and their references were
    repaired by hand - nine dangling references became six. The 2026-09-16
    export then returned all four. The judgement was wrong, and the hand repair
    had removed content that was about to resolve again.

    That is the case for not guessing. Nothing here can separate a mod that is
    coming back from one that is not while the window is open: the catalog's
    status field is edited after an export, not during it, and an absent
    folder proves nothing about the Steam account. So this deliberately does
    NOT say which reference belongs to which mod, does NOT soften the exit
    code, and does NOT promise that re-exporting will fix anything. It names
    what is missing and both ways out, and leaves the reading to a person.

    The opposite drift is invisible here: a file mods-source still holds after
    the mod stopped shipping it resolves, and the reference passes while the
    game cannot find it. tools/check_inventory.py is what catches that.
    """
    # Reading the catalog is new work on a path that used to need none, so it
    # fails soft: a malformed catalog costs the note, never the report above it.
    try:
        stale = stale_mods()
    except Exception as exc:
        return f"   (could not read data/mod-catalog.json: {exc})\n"
    if not stale:
        return ""
    names = "\n".join(f"      {t} ({i})"
                      for i, t in sorted(stale.items(), key=lambda kv: kv[1]))
    return (
        "   mods-source is behind data/mod-catalog.json. The catalog counts these\n"
        "   mods as installed (active, deprecated or wip) but they are not exported,\n"
        "   so anything they define dangles above whether or not it is really\n"
        "   missing from the game:\n\n"
        f"{names}\n\n"
        "   Still installed? Re-run tools/export-mod-configs.ps1. If deliberately\n"
        "   removed, set status to unsubscribed and review affected references.\n"
        "   An absent local folder does not prove Steam account unsubscription.\n")


def check_mission(mission):
    """-> (problems, the editor-crash subset of them, references checked)."""
    problems, crashes, checked = [], [], 0
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
                crashes.append(
                    f"line {ln}: {uid} names no LoadoutVariant and its winning file "
                    f"offers no 'Default' to fall back on\n"
                    f"        has: {', '.join(avail)}\n"
                    f"        fix: integration/missions/fix_loadout_variants.py --all --write")
                problems.append(crashes[-1])
        pending = None
        saw_variant = False

    for n, line in enumerate(mission.read_text(encoding="utf-8",
                                               errors="replace").splitlines(), 1):
        line = line.strip()
        if line.startswith("["):
            close_block()
            in_aircraft = bool(re.match(r"^\[Taskforce\d+(?:Aircraft|Helicopter)\d+\]", line))
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
    return problems, crashes, checked


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
                    help="every mission the installer deploys; only the editor crash fails it")
    args = ap.parse_args()

    if args.all:
        missions = deployed_missions()
    else:
        name = " ".join(args.mission) or active_mission()
        mission = MISSIONS / f"{name}.ini"
        if not mission.exists():
            # Campaign missions live inside their pack rather than in
            # integration/missions, so name one ("01 White Water") and it is
            # found there too - the checks are the same and the campaign
            # deserves them.
            found = sorted((ROOT / "integration" / "campaign").rglob(f"{name}.ini"))
            if not found:
                sys.exit(f"no such mission: {mission}")
            mission = found[0]
        missions = [mission]

    total_problems, total_crashes, total_checked, bad_missions = [], [], 0, 0
    for mission in missions:
        base = MISSIONS if MISSIONS in mission.parents else ROOT
        label = mission.relative_to(base).with_suffix("").as_posix()
        problems, crashes, checked = check_mission(mission)
        total_checked += checked
        if args.all:
            status = f"{len(problems)} dangling" if problems else "clean"
            if crashes:
                status += f", {len(crashes)} CRASH"
            print(f"  {status:>22}  {label}")
        else:
            print(f"mission: {label}\n")
        if problems:
            bad_missions += 1
            total_problems += [f"{label}: {p}" if args.all else p for p in problems]
            total_crashes += [f"{label}: {p}" for p in crashes]

    pack_problems, pack_checked = check_packs()
    total_checked += pack_checked
    total_problems += pack_problems

    print(f"\nresolved {total_checked} reference(s) across {len(missions)} mission(s), "
          f"{bad_missions} with dangling references\n" if args.all else
          f"resolved {total_checked} reference(s)\n")

    if args.all:
        if total_problems:
            print(f"{len(total_problems)} DANGLING reference(s):\n")
            for p in total_problems:
                print(f"   {p}\n")
            print(stale_note(), end="")
        if total_crashes or pack_problems:
            print(f"FAILED: {len(total_crashes)} aircraft would crash the editor's map panel "
                  f"and {len(pack_problems)} SEST pylon store(s) have no file")
            sys.exit(1)
        print("no deployed mission carries the editor crash and every pylon store resolves"
              + ("; the other references above are listed for information only"
                 if total_problems else ""))
        return

    if total_problems:
        print(f"{len(total_problems)} DANGLING reference(s):\n")
        for p in total_problems:
            print(f"   {p}\n")
        print(stale_note(), end="")
        sys.exit(1)
    print("every unit, air group, loadout variant, hull variant and pylon store resolves")


if __name__ == "__main__":
    main()
