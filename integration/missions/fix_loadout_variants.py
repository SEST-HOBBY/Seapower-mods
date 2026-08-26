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


def available_loadouts(unit_type: str):
    """AvailableLoadouts of the file that wins the load order for this type."""
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
    if best is None:
        return None
    text = Path(best[1]).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^AvailableLoadouts=(.*)$", text, re.M)
    if not m:
        return None
    return [x.strip() for x in m.group(1).split(",") if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mission")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    name = args.mission or active_mission()
    path = MISSIONS / f"{name}.ini"
    if not path.exists():
        sys.exit(f"no such mission: {path}")
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

    if not fixed:
        print(f"{name}: every aircraft resolves a loadout - nothing to do")
        return
    for entry, unit, variant in fixed:
        print(f"  {entry}: {unit} -> LoadoutVariant={variant}")
    if args.write:
        path.write_text(new, encoding="utf-8")
        print(f"{name}: {len(fixed)} aircraft given an explicit loadout")
    else:
        print(f"{len(fixed)} entry(s) would change - re-run with --write to apply")


if __name__ == "__main__":
    main()
