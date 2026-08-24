#!/usr/bin/env python3
"""Build the SEST Growler NGJ + MALICE compatibility patch.

The three Growler identifiers in the installed collection come from three
different Workshop mods.  This builder deliberately rebases each identifier
on the file that currently wins the user's canonical load order, then adds
SEST loadouts without changing the original choices.

Targets:
  * usn_ea-18g       - U.S. Navy 2027 Capabilities (upgraded from ALQ-99)
  * usn_ea-18g_2020s - F/A-18E/F (already carries the NGJ meshes)
  * usn_ea-18g_2020  - US Naval Aviation (already carries the NGJ meshes)
  * usn_fa-18f_blk3  - U.S. Navy 2027 Capabilities Block III Super Hornet
  * usn_fa-18f       - U.S. Navy 2027 two-seat Super Hornet (AN/APG-79)
  * usn_fa-18e       - U.S. Navy 2027 single-seat Super Hornet (AN/APG-79(V))

Usage (repo root):  python3 integration/growler-ngj-malice/build_patch.py
"""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NAVY_2027 = ROOT / "mods-source" / "3606774881"
SUPER_HORNET = ROOT / "mods-source" / "3426791311"
US_NAVAL_AVIATION = ROOT / "mods-source" / "3737267013"
OUT = Path(__file__).resolve().parent / "SEST_Growler_NGJ_MALICE"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402


GROWLER_KEYS = ["SEST_MaliceNGJ", "SEST_MaliceNGJHeavy"]
BLOCK_III_KEYS = ["SEST_MaliceBlockIII"]

GROWLER_LOADOUTS = """\
[--------------------------- SEST NGJ + MALICE ---------------------------]
# Added by SEST_Growler_NGJ_MALICE.  The AN/ALQ-249 and NGL-LB pod meshes
# remain fitted; MALICE uses the AGM-88G airframe from US Naval Aviation.

[WeaponSystem1SEST_MaliceNGJ]
ReadyUpTime=25               // minutes to refuel and rearm before takeoff
CoolDownTime=60              // minutes of maintenance after landing
SubModelsToHide=fule_tank_point
Station3=sest_aim-424
Station4=sest_aim-424
Station11=usn_aim-120d3
Station12=usn_aim-120d3
Station27=usn_tank_610_f-18
Station28=usn_tank_610_f-18

[WeaponSystem1SEST_MaliceNGJHeavy]
ReadyUpTime=30               // minutes to refuel and rearm before takeoff
CoolDownTime=60              // minutes of maintenance after landing
SubModelsToHide=fule_tank_point
Station3=sest_aim-424
Station4=sest_aim-424
Station11=usn_aim-120d3
Station12=usn_aim-120d3
Station13=sest_aim-424
Station14=sest_aim-424
Station27=usn_tank_610_f-18
Station28=usn_tank_610_f-18

"""

BLOCK_III_LOADOUT = """\
[--------------------------- SEST Block III MALICE ---------------------------]
# Counter-air / anti-emitter fit based on the proven Murder Hornet
# Interceptor station geometry.  MALICE replaces the four AIM-174Bs.

[WeaponSystem1SEST_MaliceBlockIII]
ReadyUpTime=30               // minutes to refuel and rearm before takeoff
CoolDownTime=60              // minutes of maintenance after landing
SubModelsToHide=aam_point2,aam_pointCRIR,aam_pointCRIL,agm_inner_point,agm_point,gbu_point,Targeting_Pod,fule_tank_point,BRU_55_Left,BRU_55_Right,BRU_55_Left_Inner,BRU_55_Right_Inner,gbu_outer,gbu_inner
Station1=usn_aim-9x
Station2=usn_aim-9x
Station3=usn_aim-120d3
Station4=usn_aim-120d3
Station11=usn_aim-120d3
Station12=usn_aim-120d3
Station29=usn_tank_1200_f-18
Station30=sest_aim-424
Station31=sest_aim-424
Station32=sest_aim-424
Station33=sest_aim-424

"""

NGJ_SENSOR = """\
[AN/ALQ-249]
# Next Generation Jammer Mid-Band.  Stats match the established F/A-18E/F
# implementation so this patch changes availability rather than balance.
Kind=ECM
Frequencies=All
Type=Offensive
PeakPower=75.0
MaxRange=400.0
Gain=7.5
JamConeViewArcs=45.0
JamChance=0.3
"""

LOADOUT_NAMES = {
    "en": {
        "SEST_MaliceNGJ": "NGJ MALICE (2x AIM-424)",
        "SEST_MaliceNGJHeavy": "NGJ MALICE Heavy (4x AIM-424)",
        "SEST_MaliceBlockIII": "Block III MALICE (4x AIM-424)",
    },
    "cn": {
        "SEST_MaliceNGJ": "NGJ MALICE (2x AIM-424)",
        "SEST_MaliceNGJHeavy": "NGJ MALICE 重载 (4x AIM-424)",
        "SEST_MaliceBlockIII": "Block III MALICE (4x AIM-424)",
    },
}

INFO_INI = """[Language_en]
Name=SEST Growler NGJ + MALICE
Description=Adds functional AN/ALQ-249 Next Generation Jammer equipment and two AIM-424 MALICE fits to the modern EA-18G Growlers, plus a four-MALICE counter-air fit for every AN/APG-79 Super Hornet (F/A-18F Block III, F/A-18F and F/A-18E). Requires U.S. Navy 2027 Capabilities, F/A-18E/F, and US Naval Aviation. US Naval Aviation supplies the AGM-88G model used by MALICE. Place this patch ABOVE all three required mods.

[Compatibility]
ApproximateVersion=0.8.2
"""


def normalize_generated_text(text: str) -> str:
    """Remove trailing horizontal whitespace and keep one final newline."""
    body = "\n".join(line.rstrip(" \t") for line in text.splitlines())
    return body.rstrip("\n") + "\n"

def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        sys.exit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def extend_loadouts(text: str, keys: list[str], source_name: str) -> str:
    match = re.search(r"^(AvailableLoadouts=)([^\r\n]+)$", text, re.M)
    if not match:
        sys.exit(f"{source_name}: AvailableLoadouts line not found")
    existing = [key.strip() for key in match.group(2).split(",")]
    clashes = [key for key in keys if key in existing]
    if clashes:
        sys.exit(f"{source_name}: loadout keys already exist: {clashes}")
    replacement = match.group(1) + match.group(2).rstrip() + "," + ",".join(keys)
    return text[: match.start()] + replacement + text[match.end() :]


def inject_loadouts(text: str, sections: str, source_name: str) -> str:
    marker = "[---------- WeaponMagazines ----------]"
    if text.count(marker) != 1:
        sys.exit(f"{source_name}: expected one WeaponMagazines marker")
    return text.replace(marker, sections + marker, 1)


def upgrade_legacy_growler(text: str) -> str:
    """Replace the two ALQ-99 systems/meshes with the modern NGJ set."""
    text = replace_once(
        text,
        "NumberOfSensorSystems=7",
        "NumberOfSensorSystems=6",
        "legacy Growler sensor count",
    )

    sensor = """[SensorSystem5] #AN/ALQ-249 Next Generation Jammer
Type=ECM
SystemName=AN/ALQ-249
Mount=ALQ-249
ModuleType=Sensor

"""
    text, count = re.subn(
        r"(?ms)^\[SensorSystem5\][^\n]*\n.*?(?=^\[SensorSystem7\])",
        sensor,
        text,
        count=1,
    )
    if count != 1:
        sys.exit("legacy Growler: could not replace ALQ-99 sensor blocks")
    text = replace_once(text, "[SensorSystem7] #GPS", "[SensorSystem6] #GPS", "legacy Growler GPS index")

    text = replace_once(
        text,
        "ALQ-99=ALQ-99\nALQ-99_C=ALQ-99_C",
        "NGL-LB=NGL-LB\nALQ-249=ALQ-249",
        "legacy Growler NGJ submodels",
    )
    text = text.replace("SubModelsToHide=fule_tank_point,ALQ-99", "SubModelsToHide=fule_tank_point")

    mesh_pattern = re.compile(
        r"(?ms)^\[ALQ-99\]\n.*?^\[ALQ-99_C\]\n.*?(?=^#{10,}\n# Decals)"
    )
    ngj_meshes = """[NGL-LB]
Mesh=ngllb
ResourcesFolder=assets/models/vechicle/aircraft/ea-18g/
Material=ngllb_mat.ini

[ALQ-249]
Mesh=alq249_open
ResourcesFolder=assets/models/vechicle/aircraft/ea-18g/
Material=alq249_mat.ini

"""
    text, count = mesh_pattern.subn(ngj_meshes, text, count=1)
    if count != 1:
        sys.exit("legacy Growler: could not replace ALQ-99 mesh definitions")

    checks = {
        "AN/ALQ-249 sensor": "SystemName=AN/ALQ-249",
        "NGJ low-band model": "NGL-LB=NGL-LB",
        "NGJ mid-band model": "ALQ-249=ALQ-249",
    }
    for label, token in checks.items():
        if text.count(token) != 1:
            sys.exit(f"legacy Growler: invalid {label}")
    if "SystemName=AN/ALQ-99" in text:
        sys.exit("legacy Growler: an active ALQ-99 sensor remains")
    return text


def verify_station_geometry(text: str, sections: str, source_name: str) -> None:
    hardpoint = re.search(r"(?ms)^\[WeaponSystem1\].*?(?=^\[WeaponSystem\d+\])", text)
    if not hardpoint:
        sys.exit(f"{source_name}: WeaponSystem1 hardpoint block not found")
    defined = {int(value) for value in re.findall(r"^Station(\d+)=", hardpoint.group(0), re.M)}
    used = {int(value) for value in re.findall(r"^Station(\d+)=", sections, re.M)}
    missing = sorted(used - defined)
    if missing:
        sys.exit(f"{source_name}: loadout uses undefined stations {missing}")


def verify_ammunition() -> None:
    expected = {
        AIM424_ID,
        "usn_aim-120d3",
        "usn_aim-9x",
        "usn_tank_610_f-18",
        "usn_tank_1200_f-18",
    }
    found = {path.stem for path in (ROOT / "mods-source").rglob("*.ini") if path.parent.name == "ammunition"}
    found.add(AIM424_ID)  # this pack writes it below
    missing = sorted(expected - found)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")


def build_growler(source: Path, destination_name: str, *, upgrade_ngj: bool) -> None:
    text = source.read_text(encoding="utf-8-sig")
    if upgrade_ngj:
        text = upgrade_legacy_growler(text)
    else:
        required = ("SystemName=AN/ALQ-249", "NGL-LB=NGL-LB", "ALQ-249=ALQ-249")
        missing = [token for token in required if token not in text]
        if missing:
            sys.exit(f"{source.name}: upstream NGJ layout changed; missing {missing}")

    verify_station_geometry(text, GROWLER_LOADOUTS, source.name)
    text = extend_loadouts(text, GROWLER_KEYS, source.name)
    text = inject_loadouts(text, GROWLER_LOADOUTS, source.name)
    for key in GROWLER_KEYS:
        if text.count(f"[WeaponSystem1{key}]") != 1:
            sys.exit(f"{source.name}: invalid generated {key} section count")

    aircraft = OUT / "aircraft"
    aircraft.mkdir(parents=True, exist_ok=True)
    (aircraft / destination_name).write_text(normalize_generated_text(text), encoding="utf-8")


def build_super_hornet(file_name: str) -> None:
    """Add the MALICE fit to an APG-79 Super Hornet.

    Every Navy 2027 Super Hornet that already flies MurderHornetInterceptor
    carries the AIM-174B on stations 30-33, so the same fit transplants
    without geometry changes: usn_fa-18f_blk3 (Block III), plus usn_fa-18f
    and usn_fa-18e, which have the same radar class and station layout.
    """
    source = NAVY_2027 / "aircraft" / file_name
    text = source.read_text(encoding="utf-8-sig")
    verify_station_geometry(text, BLOCK_III_LOADOUT, source.name)
    text = extend_loadouts(text, BLOCK_III_KEYS, source.name)
    text = inject_loadouts(text, BLOCK_III_LOADOUT, source.name)
    if text.count("[WeaponSystem1SEST_MaliceBlockIII]") != 1:
        sys.exit(f"{source.name}: invalid generated MALICE section count")

    aircraft = OUT / "aircraft"
    aircraft.mkdir(parents=True, exist_ok=True)
    (aircraft / file_name).write_text(normalize_generated_text(text), encoding="utf-8")


def write_language_files() -> None:
    for language, names in LOADOUT_NAMES.items():
        folder = OUT / f"language_{language}"
        folder.mkdir(parents=True, exist_ok=True)
        body = "[LoadoutNames]\n\n# ---------- SEST Growler NGJ + MALICE ----------\n"
        body += "".join(f"{key}={value}\n" for key, value in names.items())
        (folder / "loadout_names.ini").write_text(body, encoding="utf-8")


def main() -> None:
    verify_ammunition()
    build_growler(NAVY_2027 / "aircraft" / "usn_ea-18g.ini", "usn_ea-18g.ini", upgrade_ngj=True)
    build_growler(
        SUPER_HORNET / "aircraft" / "usn_ea-18g_2020s.ini",
        "usn_ea-18g_2020s.ini",
        upgrade_ngj=False,
    )
    build_growler(
        US_NAVAL_AVIATION / "aircraft" / "usn_ea-18g_2020.ini",
        "usn_ea-18g_2020.ini",
        upgrade_ngj=False,
    )
    for hornet in ("usn_fa-18f_blk3.ini", "usn_fa-18f.ini", "usn_fa-18e.ini"):
        build_super_hornet(hornet)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    systems = OUT / "systems"
    systems.mkdir(exist_ok=True)
    (systems / "sensors.ini").write_text(NGJ_SENSOR, encoding="utf-8")
    write_aim424(OUT)
    write_language_files()

    outputs = sorted(path for path in OUT.rglob("*") if path.is_file())
    print(
        f"built {OUT.relative_to(ROOT)}: 3 NGJ Growlers, 3 APG-79 Super Hornets, "
        f"3 new loadouts, {len(outputs)} files"
    )


if __name__ == "__main__":
    main()
