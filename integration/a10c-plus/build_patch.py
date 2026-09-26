#!/usr/bin/env python3
"""Build SEST A-10C+: the Warthog the A-10C mod's own file was reaching for.

A NEW unit id, usaf_a-10c_plus, cloned from the A-10C mod (3459682829). The
base A-10C is left alone - SEST Allied Fixes repairs its defects in place -
so this is a selectable upgrade sitting beside it, not a replacement.

WHY A NEW UNIT AND NOT A LOADOUT. Sensors are declared per aircraft file.
A loadout can change what hangs on the pylons and nothing else, so an
"upgraded variant" carrying a targeting pod has to be its own unit id.

THE AUTHOR ALREADY DESIGNED THIS AIRCRAFT AND DID NOT FINISH IT. The A-10C's
hardpoint declares

    AssociatedSensors=SensorSystem2,SensorSystem5

while the file declares three sensors. SensorSystem5 has never existed. The
mod also ships, in its own systems/sensors.ini, a Litening pod and an
AN/AAQ-28 laser designator that NO aircraft in the collection references -
defined, complete, unused. The dangling slot 5 and the two orphaned sensor
definitions are the same unfinished thought. This pack finishes it: the
Litening at 4, the designator at 5, and the author's existing reference
resolves without being touched.

Three defects are fixed in the clone, and the first and third are fixed in the
base aircraft by SEST Allied Fixes as well, because they are bugs rather than
upgrades:

  1. [SensorSystem2], the Maverick IR head, carries no ModuleType=Sensor and
     no Mount. Of 2308 aircraft sensor blocks in this collection, vanilla
     included, 2263 declare ModuleType=Sensor; this is one of the 45 that do
     not, and the A-10A from the same author is another. That is why the
     aircraft reads as having no infrared sensor at all.
  2. AssociatedSensors names SensorSystem5, which does not exist.
  3. usa_a-10c_squadrons.ini declares NumberOfSquadrons=7 and defines two.
     The language file names two. Livery selection has five squadrons with no
     texture to resolve, which is the likeliest cause of the aircraft only
     ever appearing in one scheme.

NO GROUND-SEARCH RADAR IS ADDED. The real A-10C has no radar, and inventing
one would be the only figure in this pack with nothing behind it. The
Litening pod IS the ground sensor: at 2.2/4.0 VID and range multipliers
against the Maverick head's 1.8/3.2, and 0.95 against 0.7 looking down at
ground clutter, it is a large improvement in exactly the role asked for.

Usage (repo root):  python3 integration/a10c-plus/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3459682829"      # A-10C
OUT = Path(__file__).resolve().parent / "SEST_A10C_Plus"

sys.path.insert(0, str(ROOT / "integration"))
from common.a10c import fix_squadron_count, register_ir_head  # noqa: E402

UNIT = "usaf_a-10c_plus"
BASE = "usa_a-10c"

# THE SENSOR NAMES MUST BE OURS, NOT THE DONOR'S. systems/ files merge key by
# key across the whole load order and the highest mod wins each key, so a bare
# SystemName=Litening does NOT get the A-10C mod's Litening - five mods define
# that name and the A-10C's copy sits third. Referencing it by name silently
# binds this aircraft to the Italian Navy Mod's pod (3505420313), which
# outranks it: 3.0/3.4 multipliers against the intended 2.2/4.0, and night
# vision 0.5 against 1.0 - WORSE at night than the Maverick head it was meant
# to beat. AN/AAQ-28 is defined by the same five, and the substitute is a
# 15 nm designator rather than 20. Until the 2026-09-21 export it was Euromod
# JMSDF that held both keys, with the same figures. The winner changes as mods
# come and go, which is why the aircraft must not depend on it.
#
# So the pack defines its own uniquely named copies, lifted verbatim from the
# A-10C mod, and the aircraft references those. Nothing can outrank a name
# nothing else uses.
FLIR = "SEST_A10C_FLIR"
LASER = "SEST_A10C_LASER"

NEW_SENSORS = f"""\
[SensorSystem4] #Litening targeting pod - SEST A-10C+
# Kind=Visual in the donor, declared Type=Infrared here exactly as the A-10C
# mod declares its other electro-optical head (A-10_IR).
Type=Infrared
SystemName={FLIR}
Mount=Dummy
ViewArcs=-140,140|-90,20
ModuleType=Sensor

[SensorSystem5] #AN/AAQ-28 laser designator - SEST A-10C+
# The slot [WeaponSystem1] has named since the mod shipped. Block shape is the
# vanilla laser-designator convention (usn_a-6e, raaf_f-111c, wp_su-24m).
Type=LaserDesignator
SystemName={LASER}
Mount=Dummy
ModuleType=Sensor

"""

# Added to the FLIR copy only. Not a performance key - the engine's own comment
# says it affects the encyclopedia's type display - but the donor pod is
# Kind=Visual and reads as an optical sight without it, and 108 sensors across
# the collection set it for exactly this reason.
IR_DISPLAY = ("UseIRValues=True                 "
              "// Affects only Encyclopedia. For correct type display")


def write_sensors():
    """Copy the donor's two sensors under names nothing else defines."""
    src = (UPSTREAM / "systems" / "sensors.ini").read_text(encoding="utf-8-sig")
    defined_elsewhere = set()
    for other in (ROOT / "mods-source").glob("*/systems/*.ini"):
        defined_elsewhere |= set(re.findall(
            r"^\[([^\]\n]+)\]", other.read_text(encoding="utf-8", errors="replace"), re.M))
    out = ["# SEST A-10C+ sensors. Lifted verbatim from the A-10C mod (3459682829),\n"
           "# under names nothing else defines: five mods declare [Litening] and\n"
           "# [AN/AAQ-28], the highest wins the key, so referencing them by name\n"
           "# binds to whichever mod outranks - not to the values tuned for here."]
    for donor, name, extra in (("Litening", FLIR, IR_DISPLAY),
                               ("AN/AAQ-28", LASER, "")):
        if name in defined_elsewhere:
            sys.exit(f"{UNIT}: {name} is already defined upstream - it would collide too, "
                     "pick another name")
        m = re.search(rf"^\[{re.escape(donor)}\][^\n]*\n((?:(?!^\[).*\n)*)", src, re.M)
        if not m:
            sys.exit(f"{UNIT}: the A-10C mod no longer defines [{donor}] - rebase")
        body = m.group(1).rstrip("\n")
        if extra:
            body, k = re.subn(r"^(Kind=\S+[^\n]*)$", r"\1\n" + extra, body,
                              count=1, flags=re.M)
            if k != 1:
                sys.exit(f"{UNIT}: no Kind= line in [{donor}] to mark for IR display")
        out.append(f"[{name}]\n{body}\n")
    d = OUT / "systems"
    d.mkdir(parents=True, exist_ok=True)
    (d / "sensors.ini").write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    src = UPSTREAM / "aircraft" / f"{BASE}.ini"
    if not src.exists():
        sys.exit(f"{src.relative_to(ROOT)} not found - the A-10C mod (3459682829) "
                 "is not exported; run tools/export-mod-configs.ps1")
    text = src.read_text(encoding="utf-8-sig")

    # 1. the IR head becomes a real sensor module
    text = register_ir_head(text, UNIT)

    # 2. the author's dangling slot 5, and the pod at 4
    m = re.search(r"^NumberOfSensorSystems=(\d+)", text, re.M)
    if not m or m.group(1) != "3":
        sys.exit(f"{UNIT}: NumberOfSensorSystems is {m and m.group(1)!r}, expected '3' - rebase")
    hard = re.search(r"^AssociatedSensors=SensorSystem2,SensorSystem5\s*$", text, re.M)
    if not hard:
        sys.exit(f"{UNIT}: the hardpoint no longer names SensorSystem2,SensorSystem5 - "
                 "re-check which slots this pack should fill")
    text = text[:m.start(1)] + "5" + text[m.end(1):]
    anchor = re.search(r"^\[-+ Weapon Systems -+\]", text, re.M)
    if not anchor:
        sys.exit(f"{UNIT}: no Weapon Systems banner to insert the sensors before")
    text = text[:anchor.start()] + NEW_SENSORS + text[anchor.start():]

    # 3. AIM-9X wherever the AIM-9M sits, keeping the mod's own seat key.
    #    Not just the air-to-air fit: the Warthog carries a Sidewinder rail
    #    on station 2 of EVERY loadout, and a second on station 1 in AirToAir,
    #    eleven station lines across the ten loadouts. Upgrading the aircraft
    #    means upgrading all of them - a variant that flew AIM-9X only when
    #    configured for air-to-air would be the odd one out.
    text, n = re.subn(r"^(Station[12]=)usn_aim-9m(\|AIM-9_CH)\s*$", r"\1usn_aim-9x\2",
                      text, flags=re.M)
    if n != 11:
        sys.exit(f"{UNIT}: expected 11 AIM-9M stations to upgrade, found {n} - upstream "
                 "changed its loadout table, re-check which fits carry the rails")
    if not (ROOT / "mods-source" / "3606774881" / "ammunition" / "usn_aim-9x.ini").exists():
        sys.exit(f"{UNIT}: usn_aim-9x is not defined by U.S. Navy 2027 - re-check the provider")

    # 4. sanity: every AssociatedSensors entry now resolves
    have = {int(x) for x in re.findall(r"^\[SensorSystem(\d+)\]", text, re.M)}
    for a in re.findall(r"^AssociatedSensors=(\S+)", text, re.M):
        for s in a.split(","):
            if s.startswith("SensorSystem") and int(s[len("SensorSystem"):]) not in have:
                sys.exit(f"{UNIT}: {s} still does not resolve")
    declared = int(re.search(r"^NumberOfSensorSystems=(\d+)", text, re.M).group(1))
    if sorted(have) != list(range(1, declared + 1)):
        sys.exit(f"{UNIT}: sensors are {sorted(have)}, expected 1..{declared}")

    write_sensors()
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / f"{UNIT}.ini").write_text(text, encoding="utf-8")

    # 5. squadrons: the count matches what is actually defined, here and in the
    #    language file. Cloned so the new unit has its own liveries.
    sq = (UPSTREAM / "aircraft" / f"{BASE}_squadrons.ini").read_text(encoding="utf-8-sig")
    sq, was, defined = fix_squadron_count(sq, UNIT)
    (OUT / "aircraft" / f"{UNIT}_squadrons.ini").write_text(sq, encoding="utf-8")

    # 6. names. Comma-free description: commas separate fields in these files.
    for lang in ("en", "cn"):
        srcn = UPSTREAM / f"language_{lang}" / "aircraft_names.ini"
        if not srcn.exists():
            continue
        body = srcn.read_text(encoding="utf-8-sig")
        b = re.search(rf"^\[{BASE}\]\n((?:(?!^\[).*\n)*)", body, re.M)
        if not b:
            sys.exit(f"{UNIT}: no [{BASE}] entry in language_{lang} to base the name on")
        entry = re.sub(r"^Default=[^\n]*$", "Default=A-10C+ SEST,A-10C+", b.group(1), flags=re.M)
        entry = re.sub(r"^DefaultDescription=[^\n]*$",
                       "DefaultDescription=A-10C upgraded by the SEST A-10C+ pack with the "
                       "Litening targeting pod and AN/AAQ-28 laser designator the A-10C mod "
                       "defines but never fits to an aircraft - filling the sensor slot its "
                       "hardpoint has always named - plus AIM-9X on every self-defence rail. The "
                       "Maverick infrared head is registered as a sensor module so it works "
                       "at all. No radar: the real aircraft has none and the pod is the "
                       "ground sensor.", entry, flags=re.M)
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "aircraft_names.ini").write_text(f"[AircraftNames]\n[{UNIT}]\n{entry}",
                                              encoding="utf-8")

    (OUT / "_info.ini").write_text(
        "[Language_en]\n"
        "Name=SEST A-10C+\n"
        "Description=A selectable upgraded A-10C as a new unit beside the standard one. "
        "The A-10C mod ships a Litening targeting pod and an AN/AAQ-28 laser designator in "
        "its own systems file that no aircraft ever uses - and its Warthog's hardpoint names "
        "a SensorSystem5 the aircraft never declares. This fits those two sensors into that "
        "slot and the one beside it so the reference resolves. It also registers the Maverick "
        "infrared head as a sensor module - it lacks ModuleType=Sensor upstream which is why "
        "the aircraft reads as having no infrared at all - corrects a squadron count of seven "
        "against two defined liveries which is the likeliest reason only one scheme appears - "
        "and upgrades every self-defence rail from AIM-9M to AIM-9X across all ten loadouts. No radar is added: the "
        "real A-10C has none and the Litening pod is the ground sensor. Requires the A-10C "
        "mod. Deploys inside the SEST Integration Pack.\n"
        "\n[Compatibility]\nApproximateVersion=0.8.2\n", encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: {UNIT} - IR head registered, "
          f"{FLIR} + {LASER} at slots 4/5 (hardpoint ref now resolves), AIM-9X x{n}, squadrons {was}->{defined}")


if __name__ == "__main__":
    main()
