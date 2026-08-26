#!/usr/bin/env python3
"""Build the SEST Zumwalt CPS patch: make the IRCPS launcher actually exist.

The Zumwalt CPS variant in Modern US Navy (3390330875) ships with its
hypersonic launcher wired to nothing. Two defects, both introduced the same
way - the CPS hull was derived from the base usn_ddg-1000.ini by inserting the
LMVLS and consolidating the nav radars, and the renumbering was left half done:

  1. [WeaponSystem1] IS DECLARED TWICE - once as "# LMVLS" (the Advanced
     Payload Module carrying 12 rounds of usn_ircps) and again as "# MK57 1".
     [WeaponSystem2] does not exist. Every other MK57 was correctly bumped by
     one (MK57 2 is WeaponSystem3, ... MK57 20 is WeaponSystem21), so the first
     MK57 is the single block the author forgot. Whichever way the ini parser
     resolves the clash, one of those two launchers is discarded.

     This is not a tolerated quirk: a sweep of all 734 units in mods-source
     that declare weapon systems found this file to be THE ONLY ONE with a
     duplicate section number. Gaps, by contrast, appear in 83 shipped units
     that work, so the missing [WeaponSystem2] is harmless on its own - it is
     the duplicate that costs a launcher.

  2. The LMVLS's only AssociatedSensors entry is SensorSystem12, which does
     not exist - the CPS hull declares 11. The base hull has 13 sensors with
     the SM Datalink at 13 and wires its VLS to "SensorSystem3,SensorSystem13"
     (SPY-3 + datalink); the CPS hull dropped two nav radars, moving the SM
     Datalink to 11, and 12 became the old towed-array slot. So the LMVLS is
     left with NO valid fire-control sensor at all.

     A dangling sensor reference is by itself tolerated - 30 units have one,
     including the whole US Navy 2027 Arleigh Burke fleet - but those all keep
     at least one VALID sensor alongside it. The LMVLS has exactly one entry
     and it dangles.

The MK57s carry the same stale SensorSystem12 as a third entry, which the game
ignores because SensorSystem3 and SensorSystem11 are both valid. That is
tidied here too, but it was never the bug.

Everything else checks out and is deliberately left alone: eu_lmvls_apm and
eu_lmvls are defined in Euromod's systems/weapons.ini, the magazine holds
12x usn_ircps, and 4 containers x 3 attachments matches that count exactly.

Usage (repo root):  python3 integration/zumwalt-cps/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3390330875"          # Modern US Navy
EUROMOD = ROOT / "mods-source" / "3629144864"           # Euromod (IRCPS + LMVLS)
OUT = Path(__file__).resolve().parent / "SEST_Zumwalt_CPS"
REL = "vessels/usn_ddg-1000_cps.ini"

# The hull's own convention for a VLS, taken from the base usn_ddg-1000.ini:
# SPY-3 for the picture, SM Datalink for midcourse guidance.
SPY3 = "SensorSystem3"
DATALINK = "SensorSystem11"          # "#SM Datalink" in the CPS numbering
STALE = "SensorSystem12"             # does not exist on this hull

INFO_INI = """[Language_en]
Name=SEST Zumwalt CPS Fix
Description=Makes the Zumwalt's hypersonic launcher work. The DDG-1000 CPS variant in Modern US Navy declares [WeaponSystem1] twice - once as the LMVLS Advanced Payload Module holding 12 IRCPS rounds and again as the first MK57 - with no [WeaponSystem2], so one of the two launchers is discarded by the ini parser. It is the only unit out of 734 in this collection with a duplicate weapon-system number. The LMVLS is also wired to SensorSystem12 for fire control on a hull that only has 11 sensors, leaving it with no valid sensor at all. This renumbers the first MK57 to WeaponSystem2 (matching the scheme every other MK57 already follows) and points the LMVLS at the SPY-3 and SM Datalink, as the base hull wires its own VLS. Requires Modern US Navy and Euromod, and must sit ABOVE Modern US Navy.

[Compatibility]
ApproximateVersion=0.8.2
"""


def sections(text, family):
    return [int(n) for n in re.findall(rf"^\[{family}(\d+)\]", text, re.M)]


def check_upstream(text):
    """Refuse to ship if Modern US Navy has fixed this itself."""
    nums = sections(text, "WeaponSystem")
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    if dupes != [1]:
        sys.exit(f"upstream weapon-system duplicates are now {dupes} (expected [1]) — "
                 "rebase this patch, it may already be fixed")
    labels = re.findall(r"^\[WeaponSystem1\]([^\n]*)", text, re.M)
    if len(labels) != 2 or "LMVLS" not in labels[0] or "MK57 1" not in labels[1]:
        sys.exit(f"the two [WeaponSystem1] blocks are not LMVLS then MK57 1: {labels} — rebase")
    if re.search(r"^\[WeaponSystem2\]", text, re.M):
        sys.exit("upstream now has a [WeaponSystem2] — rebase this patch")


def fix_numbering(text):
    """Second [WeaponSystem1] (the first MK57) becomes [WeaponSystem2]."""
    first = text.index("[WeaponSystem1]")
    second = text.index("[WeaponSystem1]", first + 1)
    return text[:second] + "[WeaponSystem2]" + text[second + len("[WeaponSystem1]"):]


def fix_sensors(text):
    """Give the LMVLS real fire control, and drop the stale ref from the MK57s."""
    lmvls, mk57 = 0, 0

    def repl(m):
        nonlocal lmvls, mk57
        refs = m.group(1).split(",")
        if refs == [STALE]:                       # the LMVLS
            lmvls += 1
            return f"AssociatedSensors={SPY3},{DATALINK}"
        if STALE in refs:                         # the MK57s
            mk57 += 1
            return "AssociatedSensors=" + ",".join(r for r in refs if r != STALE)
        return m.group(0)

    text = re.sub(r"^AssociatedSensors=(\S+)", repl, text, flags=re.M)
    if lmvls != 1:
        sys.exit(f"expected exactly 1 LMVLS sensor line to fix, found {lmvls} — rebase")
    if not mk57:
        sys.exit("no MK57 blocks carried the stale sensor reference — rebase")
    return text, lmvls, mk57


def system_names(kind):
    """Every [name] defined in systems/<kind>.ini across the whole ecosystem."""
    names = set()
    for f in list(ROOT.glob(f"mods-source/*/systems/{kind}.ini")) + \
             list(ROOT.glob(f"mods-source/_vanilla/original/systems/{kind}.ini")):
        names |= set(re.findall(r"^\[([^\]]+)\]", f.read_text(encoding="utf-8-sig", errors="replace"), re.M))
    return names


def blocks_of(text, family):
    """(number, label, body) for each [<family>N] section."""
    return [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(
        rf"^\[{family}(\d+)\]([^\n]*)\n(.*?)(?=^\[|\Z)", text, re.S | re.M)]


def validate(text):
    """Everything the fixed file references must resolve.

    Note the two distinct namespaces, which are easy to conflate:
      SystemName= in a weapon block  -> systems/weapons.ini
      SystemName= in a sensor block  -> systems/sensors.ini
      ContainerBase=/Collider=/Mount= -> a submodel section in THIS file
        (eu_mk46_barrel_1, for instance, is defined inside the ship ini, not
        in weapons.ini), or the literal Dummy.
    """
    problems = []

    nums = sections(text, "WeaponSystem")
    declared = int(re.search(r"^NumberOfWeaponSystems=(\d+)", text, re.M).group(1))
    if sorted(nums) != list(range(1, declared + 1)):
        problems.append(f"weapon systems are {sorted(nums)}, expected 1..{declared}")

    have_sensors = set(sections(text, "SensorSystem"))
    declared_sensors = int(re.search(r"^NumberOfSensorSystems=(\d+)", text, re.M).group(1))
    if sorted(have_sensors) != list(range(1, declared_sensors + 1)):
        problems.append(f"sensor systems are {sorted(have_sensors)}, expected 1..{declared_sensors}")
    for m in re.finditer(r"^AssociatedSensors=(\S+)", text, re.M):
        for s in m.group(1).split(","):
            if s.startswith("SensorSystem") and int(s[len("SensorSystem"):]) not in have_sensors:
                problems.append(f"AssociatedSensors points at missing {s}")

    mags = set(re.findall(r"^\[(WeaponMagazine[^\]]*)\]", text, re.M))
    for m in re.finditer(r"^AssociatedMagazine=(\S+)", text, re.M):
        if m.group(1) not in mags:
            problems.append(f"AssociatedMagazine points at missing [{m.group(1)}]")

    # Every launcher must have at least ONE resolvable sensor. A dangling entry
    # alongside a valid one is tolerated - 30 units in this collection ship that
    # way - but a launcher whose ONLY entry dangles has no fire control, which
    # is half of what was wrong here.
    for num, label, body in blocks_of(text, "WeaponSystem"):
        a = re.search(r"^AssociatedSensors=(\S+)", body, re.M)
        if not a:
            continue
        valid = [s for s in a.group(1).split(",")
                 if s.startswith("SensorSystem") and int(s[len("SensorSystem"):]) in have_sensors]
        if not valid:
            problems.append(f"[WeaponSystem{num}]{label} has no resolvable AssociatedSensors")

    known_ammo = set()
    for d in (UPSTREAM, EUROMOD, ROOT / "mods-source" / "_vanilla" / "original"):
        known_ammo |= {p.stem for p in d.rglob("*.ini") if p.parent.name == "ammunition"}
    for m in re.finditer(r"^Ammunition\d+=(\S+)", text, re.M):
        if m.group(1) not in known_ammo:
            problems.append(f"ammunition id does not resolve: {m.group(1)}")

    weapons, sensors = system_names("weapons"), system_names("sensors")
    for family, pool in (("WeaponSystem", weapons), ("SensorSystem", sensors)):
        for num, label, body in blocks_of(text, family):
            s = re.search(r"^SystemName=(\S+)", body, re.M)
            if s and s.group(1) not in pool:
                problems.append(f"[{family}{num}]{label} SystemName={s.group(1)} "
                                f"is not defined in any systems/{family[:-6].lower()}s.ini")

    # Submodel-space references: a section defined in THIS file, a placeholder,
    # or a primitive collider shape. Collider= also takes a comma-separated list.
    here = set(re.findall(r"^\[([^\]]+)\]", text, re.M))
    primitives = {"Dummy", "Box", "Sphere", "Capsule", "Mesh", "Cylinder", "None", ""}
    for key in ("ContainerBase", "Collider"):
        for m in re.finditer(rf"^{key}=(\S*)", text, re.M):
            for ref in m.group(1).split(","):
                if ref not in here and ref not in primitives:
                    problems.append(f"{key}={ref} has no submodel section in this file")

    if problems:
        sys.exit("validation failed:\n  " + "\n  ".join(sorted(set(problems))))


def main():
    src = UPSTREAM / REL
    if not src.exists():
        sys.exit(f"upstream file missing (re-export mods-source?): {src}")
    if not (EUROMOD / "systems" / "weapons.ini").exists():
        sys.exit("Euromod is not exported — the LMVLS and IRCPS come from it")

    # usn_ircps declares Launcher1=eu_lmvls_apm, i.e. the LMVLS is the ONLY
    # thing that can fire it. That is why losing that block to the duplicate
    # section number takes the weapon off the ship entirely.
    ircps = (EUROMOD / "ammunition" / "usn_ircps.ini").read_text(encoding="utf-8-sig", errors="replace")
    if "Launcher1=eu_lmvls_apm" not in ircps:
        sys.exit("usn_ircps no longer binds to eu_lmvls_apm — rebase this patch")

    text = src.read_text(encoding="utf-8-sig", errors="replace")
    original_lines = len(text.splitlines())

    check_upstream(text)
    text = fix_numbering(text)
    text, lmvls, mk57 = fix_sensors(text)
    # Both Mk46 gun mounts are labelled "GWS 1"; they are different mounts
    # (eu_mk46_turret_1 vs _2). Comment only, but this file is confusing enough.
    text = text.replace("[WeaponSystem23]  #Mk46 GWS 1", "[WeaponSystem23]  #Mk46 GWS 2")
    validate(text)

    # Whole-file override: the game replaces unit files, it never merges keys.
    if len(text.splitlines()) != original_lines:
        sys.exit("line count changed — the patch should be edits in place, not insertions")

    (OUT / "vessels").mkdir(parents=True, exist_ok=True)
    (OUT / REL).write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: MK57 1 renumbered to WeaponSystem2, "
          f"LMVLS fire control -> {SPY3}+{DATALINK}, "
          f"stale {STALE} dropped from {mk57} MK57 blocks, "
          f"{original_lines} lines (complete file), all references validated")


if __name__ == "__main__":
    main()
