#!/usr/bin/env python3
"""Give every mission aircraft an explicit LoadoutVariant when its type has no
usable default.

An aircraft entry with no LoadoutVariant= makes the game resolve a default
loadout at display time. When the type's AvailableLoadouts does NOT list
"Default", there is nothing to resolve to, and the UI's IniToPlanConverter -
which runs inside MapPanel.MeasureOverride - throws

    ArgumentException: An item with the same key has already been added.
    Key: <aircraft id>

naming the first such aircraft it reaches (plaaf_kj-500 in NORTHERN FRONT III,
which declares AvailableLoadouts=AEW yet still carries a [WeaponSystem1Default]
block - the mismatch the converter cannot resolve).

The pass writes the type's first declared loadout into the entry, which is what
the editor would have stored had the loadout ever been picked by hand. It is
idempotent: entries that already name a variant are left alone, so it is safe
in the refresh chain after every editor round-trip.

The refresh chain only ever runs it on the active mission, but the installer
deploys EVERY .ini under integration/missions/ (backups and scenarios
included), and each of those opens in the editor. The KJ-500 crash came back
that way: fixed in the active mission, still live in the sibling missions the
game lists right next to it. --all sweeps them all.

Usage (repo root):
    python3 integration/missions/fix_loadout_variants.py            # active mission, report
    python3 integration/missions/fix_loadout_variants.py --write    # active mission, apply
    python3 integration/missions/fix_loadout_variants.py --mission "NORTHERN FRONT III" --write
    python3 integration/missions/fix_loadout_variants.py --all --write   # every deployed mission
"""
import argparse
import glob
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = ROOT / "integration" / "missions"


def active_mission() -> str:
    for line in (ROOT / "data" / "active-mission.txt").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    sys.exit("no active mission recorded in data/active-mission.txt")


_LOADOUTS = {}


def available_loadouts(unit_type: str):
    """AvailableLoadouts of the file that wins the load order for this type."""
    if unit_type in _LOADOUTS:
        return _LOADOUTS[unit_type]
    order = [t.strip() for t in (ROOT / "data" / "load-order.tokens.txt").read_text().splitlines() if t.strip()]
    rank = {tok: i for i, tok in enumerate(order)}
    best = None
    for path in (glob.glob(str(ROOT / f"integration/*/SEST_*/aircraft/{unit_type}.ini"))
                 + glob.glob(str(ROOT / f"mods-source/*/aircraft/{unit_type}.ini"))
                 + glob.glob(str(ROOT / f"mods-source/_vanilla/original/aircraft/{unit_type}.ini"))):
        token = Path(path).parent.parent.name
        r = rank.get(token, 10_000)
        if best is None or r < best[0]:
            best = (r, path)
    result = None
    if best is not None:
        text = Path(best[1]).read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^AvailableLoadouts=(.*)$", text, re.M)
        if m:
            result = [x.strip() for x in m.group(1).split(",") if x.strip()]
    _LOADOUTS[unit_type] = result
    return result


def process(path: Path, write: bool) -> int:
    """Return the number of aircraft entries given a loadout (written if asked)."""
    text = path.read_text(encoding="utf-8", errors="replace")

    fixed = []
    out = []
    for chunk in re.split(r"(?=^\[)", text, flags=re.M):
        m = re.match(r"^\[(Taskforce\d+Aircraft\d+)\]", chunk)
        if m and not re.search(r"^LoadoutVariant=", chunk, re.M):
            tm = re.search(r"^Type=(.+?)\s*$", chunk, re.M)
            if tm:
                avail = available_loadouts(tm.group(1))
                if avail and "Default" not in avail:
                    chunk = re.sub(r"^(Type=.+?\s*)$", rf"\g<1>\nLoadoutVariant={avail[0]}",
                                   chunk, count=1, flags=re.M)
                    fixed.append((m.group(1), tm.group(1), avail[0]))
        out.append(chunk)
    new = "".join(out)

    name = path.relative_to(MISSIONS).with_suffix("").as_posix()
    if not fixed:
        print(f"{name}: every aircraft resolves a loadout - nothing to do")
        return 0
    for entry, unit, variant in fixed:
        print(f"  {entry}: {unit} -> LoadoutVariant={variant}")
    if write:
        # LF, whatever the host: the repo's .ini contract (see .gitattributes).
        path.write_text(new, encoding="utf-8", newline="\n")
        print(f"{name}: {len(fixed)} aircraft given an explicit loadout")
    else:
        print(f"{name}: {len(fixed)} entry(s) would change - re-run with --write to apply")
    return len(fixed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", help="mission name without .ini (default: the active mission)")
    ap.add_argument("--all", action="store_true",
                    help="every .ini under integration/missions/, i.e. everything the installer deploys")
    ap.add_argument("--write", action="store_true", help="apply the fixes")
    args = ap.parse_args()

    if args.all:
        targets = sorted(MISSIONS.rglob("*.ini"))
    else:
        name = args.mission or active_mission()
        targets = [MISSIONS / f"{name}.ini"]
        if not targets[0].exists():
            sys.exit(f"no such mission: {targets[0]}")

    total = sum(process(p, args.write) for p in targets)
    if args.all:
        touched = "given" if args.write else "would be given"
        print(f"\n{len(targets)} mission(s) checked: {total} aircraft {touched} an explicit loadout")
    if total and not args.write:
        sys.exit(1)


if __name__ == "__main__":
    main()
