#!/usr/bin/env python3
"""Move a mission's U.S. Navy 2027 alias hulls onto the Modern US Navy hulls they alias.

U.S. Navy 2027 (3606774881) has no hulls of its own: every ship is a
`#!alias` patch over a Modern US Navy (3390330875) hull, and Modern US Navy
renames hulls almost daily. A mission that fields the 2027 id inherits every
rename as a startup crash or a ship that never spawns (19 Sep 2026: the
Flight III's base was retired and the game died on KeyNotFoundException
'AirGroup' before the menu). A mission that fields the Modern US Navy hull
directly only depends on the mod that actually owns the model.

So this rewrites, inside [TaskforceNVesselM] blocks only:
  Type=usn_ddg_arleigh_flt2A_119_2027  ->  Type=usn_ddg_burke_f2a_113   (the alias base's complete sister)
  Type=usn_ddg_arleigh_flt3_2027       ->  Type=usn_ddg_burke_f3_125    (the current Flight III)
and any other 2027 alias hull to the base its own file names, when that base
exists. VariantReference is kept when the target's variants file has it, else
Variant1. LoadoutVariant is kept when the target offers it, else dropped (the
Modern US Navy Burkes offer Default and BattleFlag; 2027's MST/AA/... do not
exist on them). Positions, headings, formations, names: untouched.

The Ticonderoga (usn_cg_ticonderoga_vls_2027) is a full hull, not an alias,
and stays. The Nimitz alias is left alone too: it carries the mission's
custom air group and its base has not moved.

Idempotent - a retargeted mission has nothing left to rewrite.

    python3 integration/missions/retarget_usn2027_hulls.py                     # dry run, active mission
    python3 integration/missions/retarget_usn2027_hulls.py --mission "NORTHERN FRONT III FINAL NEWEST" --write
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_civ_traffic import active_mission, winning_file  # noqa: E402

MISSIONS = Path(__file__).resolve().parent
ROOT = MISSIONS.parents[1]
USN2027 = ROOT / "mods-source" / "3606774881" / "vessels"

# Where an alias base has itself been retired, the hull that replaced it.
RETIRED = {"usn_ddg_burke_f3": "usn_ddg_burke_f3_125"}
# Modern US Navy hulls that cannot be fielded as shipped, and the sister hull
# to stand on instead. usn_ddg_burke_f2a_119 (v564, 17 Sep 2026): its Phalanx
# names WeaponMagazineCIWS_3, which the file never defines - the gun would
# never fire (tools/check_weapon_employment.py). DDG-113 is the same 113/119
# group, complete, six variants.
BROKEN = {"usn_ddg_burke_f2a_119": "usn_ddg_burke_f2a_113"}
LEAVE = {"usn_cvn_nimitz_2027s_adou"}


def target_for(type_id):
    """Modern US Navy hull id for a 2027 alias hull, or None to leave it."""
    if type_id in LEAVE:
        return None
    if type_id in BROKEN and winning_file(f"vessels/{BROKEN[type_id]}.ini"):
        return BROKEN[type_id]
    f = USN2027 / f"{type_id}.ini"
    if not f.exists():
        return None
    m = re.match(r"^﻿?#!alias\s+(\S+)", f.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return None
    base = Path(m.group(1).replace("\\", "/")).stem
    base = RETIRED.get(base, base)
    base = BROKEN.get(base, base)
    return base if winning_file(f"vessels/{base}.ini") else None


def variants_of(type_id):
    vf = winning_file(f"vessels/{type_id}_variants.ini")
    if not vf:
        return set()
    return set(re.findall(r"^\[(Variant\d+)\]", vf.read_text(encoding="utf-8", errors="replace"), re.M))


def loadouts_of(type_id):
    f = winning_file(f"vessels/{type_id}.ini")
    m = re.search(r"^AvailableLoadouts=(.+)$", f.read_text(encoding="utf-8", errors="replace"), re.M)
    return {x.strip() for x in m.group(1).split(",")} if m else set()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", default=None)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    name = args.mission or active_mission()
    path = MISSIONS / f"{name}.ini"
    if not path.exists():
        sys.exit(f"no such mission: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")

    changes = []

    def fix(block):
        head, body = block.group(1), block.group(2)
        ty = re.search(r"^Type=(.+?)\s*$", body, re.M)
        if not ty:
            return block.group(0)
        new = target_for(ty.group(1))
        if not new:
            return block.group(0)
        body = body[:ty.start(1)] + new + body[ty.end(1):]
        vm = re.search(r"^VariantReference=(.+?)\s*$", body, re.M)
        if vm and vm.group(1) != "Default" and vm.group(1) not in variants_of(new):
            body = body[:vm.start(1)] + "Variant1" + body[vm.end(1):]
        lm = re.search(r"^LoadoutVariant=(.+?)\s*$\n?", body, re.M)
        note = ""
        if lm and lm.group(1) not in loadouts_of(new):
            body = body[:lm.start()] + body[lm.end():]
            note = f", loadout {lm.group(1)} dropped (target offers {', '.join(sorted(loadouts_of(new)))})"
        changes.append(f"{head}: {ty.group(1)} -> {new}{note}")
        return head + "\n" + body

    text = re.sub(r"^(\[Taskforce[12]Vessel\d+\])\n(.*?)(?=^\[|\Z)", fix, text, flags=re.M | re.S)
    for c in changes:
        print("  " + c)
    if not changes:
        print("nothing to retarget")
        return
    if args.write:
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"written: {path.name} ({len(changes)} hull(s))")
    else:
        print("dry run - pass --write to apply")


if __name__ == "__main__":
    main()
