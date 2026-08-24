#!/usr/bin/env python3
"""Build the SEST F-15EX Revamp patch mod from the exported upstream files.

Reads the original F-15EX (F-15SE) mod out of mods-source/, injects four new
loadouts, and writes a ready-to-install mod folder. Re-run after re-exporting
mods-source/ to rebase the patch onto an upstream update.

Usage (repo root):  python3 integration/f-15ex-revamp/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3636386513"          # F-15SE (F-15EX) by dingtools
WEAPON_PACK = ROOT / "mods-source" / "3760871384"       # Dingtools Weapon Pack
MURDER_HORNET = ROOT / "mods-source" / "3430135740"     # Murder Hornet (AIM-174B)
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
OUT = Path(__file__).resolve().parent / "SEST_F-15EX_Revamp"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402

NEW_KEYS = ["AntiShipHeavy", "Quicksink", "BigStick174", "BigStick174ER",
            "Truck174", "Malice6", "MaliceER", "MaliceTruck"]

NEW_SECTIONS = """\
[--------------------------- SEST Revamp loadouts ---------------------------]
# Added by the SEST F-15EX Revamp patch. Requires the Dingtools Weapon Pack
# (dts_ weapons); the BigStick174 loadout additionally requires Murder Hornet
# (usn_aim-174b). The 610 gal tank is vanilla.

[WeaponSystem1AntiShipHeavy]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station15=usaf_tank_610_f-15|WT
Station26=dts_anaaq-33
Station27=dts_anaaq-13
[WeaponSystem2AntiShipHeavy]
Station1=dts_agm-158c-3|JDAM32
Station2=dts_agm-158c-3|JDAM32
Station3=dts_agm-158c-3|JDAM32
Station4=dts_agm-158c-3|JDAM32
Station13=dts_agm-158c-3|WW
Station14=dts_agm-158c-3|WW

[WeaponSystem1Quicksink]
ReadyUpTime=25               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=dts_gbu-31|JDAM31
Station12=dts_gbu-31|JDAM31
Station13=dts_gbu-31|JDAM31
Station14=dts_gbu-31|JDAM31
Station15=usaf_tank_610_f-15|WT
Station26=dts_anaaq-33
Station27=dts_anaaq-13

[WeaponSystem1BigStick174]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=usn_aim-174b|AGM
Station12=usn_aim-174b|AGM
Station13=usn_aim-174b|AGM
Station14=usn_aim-174b|AGM
Station15=usaf_tank_610_f-15|WT
Station16=usn_aim-174b|WW
Station17=usn_aim-174b|WW

[WeaponSystem1BigStick174ER]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# AAMs ride the inner wing pylons' shoulder rails (same pylons as the wing
# tanks); the outer wing pylon stations 7-10 stay empty so the pylons that
# come in with the _w weapon models never render.
Station1=dts_aim-120d-3_w|120
Station2=dts_aim-120d-3_w|120
Station5=dts_aim-9x
Station6=dts_aim-9x
Station11=usn_aim-174b|AGM
Station12=usn_aim-174b|AGM
Station13=usn_aim-174b|AGM
Station14=usn_aim-174b|AGM
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|WT
Station17=usaf_tank_610_f-15|WT

[WeaponSystem1Truck174]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# 8-round AIM-174B missile truck: 4 under the fuselage (Bottom1 wells) and
# 4 on the inner wing pylons' shoulder rails, centreline fuel only.
Station1=usn_aim-174b|120
Station2=usn_aim-174b|120
Station5=usn_aim-174b|120
Station6=usn_aim-174b|120
Station11=usn_aim-174b|AGM
Station12=usn_aim-174b|AGM
Station13=usn_aim-174b|AGM
Station14=usn_aim-174b|AGM
Station15=usaf_tank_610_f-15|WT

[WeaponSystem1Malice6]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# MALICE mirror of BigStick174: 6x AIM-424 (fuselage + wing stations).
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=sest_aim-424|AGM
Station12=sest_aim-424|AGM
Station13=sest_aim-424|AGM
Station14=sest_aim-424|AGM
Station15=usaf_tank_610_f-15|WT
Station16=sest_aim-424|WW
Station17=sest_aim-424|WW

[WeaponSystem1MaliceER]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# MALICE mirror of BigStick174ER: 4x AIM-424 under, 3 tanks, AAMs inboard.
Station1=dts_aim-120d-3_w|120
Station2=dts_aim-120d-3_w|120
Station5=dts_aim-9x
Station6=dts_aim-9x
Station11=sest_aim-424|AGM
Station12=sest_aim-424|AGM
Station13=sest_aim-424|AGM
Station14=sest_aim-424|AGM
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|WT
Station17=usaf_tank_610_f-15|WT

[WeaponSystem1MaliceTruck]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# MALICE mirror of Truck174: 8x AIM-424, centreline fuel only.
Station1=sest_aim-424|120
Station2=sest_aim-424|120
Station5=sest_aim-424|120
Station6=sest_aim-424|120
Station11=sest_aim-424|AGM
Station12=sest_aim-424|AGM
Station13=sest_aim-424|AGM
Station14=sest_aim-424|AGM
Station15=usaf_tank_610_f-15|WT

"""

LOADOUT_NAMES = {
    "en": {
        "AntiShipHeavy": "AntiShipLRASM6",
        "Quicksink": "StrikeQuicksink",
        "BigStick174": "Intercept174",
        "BigStick174ER": "Intercept174 LongRange",
        "Truck174": "Intercept174 Truck (8x)",
        "Malice6": "InterceptMALICE (6x AIM-424)",
        "MaliceER": "InterceptMALICE LongRange",
        "MaliceTruck": "InterceptMALICE Truck (8x)",
    },
    "cn": {
        "AntiShipHeavy": "重型反舰LRASM×6",
        "Quicksink": "快沉反舰JDAM",
        "BigStick174": "超远程截击174",
        "BigStick174ER": "超远程截击174 (远程)",
        "Truck174": "超远程截击174 (8联卡车)",
        "Malice6": "马利斯截击 (6x AIM-424)",
        "MaliceER": "马利斯截击 (远程)",
        "MaliceTruck": "马利斯截击 (8联卡车)",
    },
}

INFO_INI = """[Language_en]
Name=SEST F-15EX Revamp
Description=Eight extra F-15EX loadouts: 6x LRASM anti-ship surge, 4x GBU-31 Quicksink, and a what-if very-long-range family - 6x/4x+fuel/8x-truck AIM-174B fits plus matching 6x/4x+fuel/8x-truck AIM-424 MALICE fits. Requires the F-15SE (F-15EX) mod and Dingtools Weapon Pack; AIM-174B fits also need Murder Hornet, and the MALICE model comes from US Naval Aviation. Place ABOVE the F-15EX mod in the Mod Manager.

[Compatibility]
ApproximateVersion=0.8.2
"""


def main():
    src = UPSTREAM / "aircraft" / "usaf_f-15ex_SEII.ini"
    text = src.read_text(encoding="utf-8")

    # 1. Extend AvailableLoadouts
    m = re.search(r"^(AvailableLoadouts=)(.+)$", text, re.M)
    if not m:
        sys.exit("AvailableLoadouts line not found — upstream layout changed")
    existing = [k.strip() for k in m.group(2).split(",")]
    clash = [k for k in NEW_KEYS if k in existing]
    if clash:
        sys.exit(f"loadout keys already exist upstream: {clash}")
    text = text[: m.start(2)] + m.group(2).rstrip() + "," + ",".join(NEW_KEYS) + text[m.end(2):]

    # 2. Inject new sections just before the WeaponMagazines banner
    marker = "[---------- WeaponMagazines ----------]"
    if marker not in text:
        sys.exit("WeaponMagazines marker not found — upstream layout changed")
    text = text.replace(marker, NEW_SECTIONS + marker, 1)

    # 3. Validate: every referenced ammo id must exist in the ecosystem
    search_dirs = [UPSTREAM, WEAPON_PACK, MURDER_HORNET, VANILLA]
    known = {AIM424_ID}  # provided by this pack itself (written below)
    for d in search_dirs:
        known |= {p.stem for p in d.rglob("*.ini") if p.parent.name == "ammunition"}
    refs = set(re.findall(r"^Station\d+=([^|\s/]+)", NEW_SECTIONS, re.M))
    missing = sorted(r for r in refs if r not in known)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")

    # 4. Validate: every position key used exists in the hardpoint sections
    pos_keys = set(re.findall(r"^([\w\-]+)Positions=", src.read_text(encoding='utf-8'), re.M))
    used = set(re.findall(r"\|([\w\-]+)$", NEW_SECTIONS, re.M))
    bad = sorted(k for k in used if k not in pos_keys)
    if bad:
        sys.exit(f"unknown position keys: {bad}")

    # 5. Write the mod folder
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "usaf_f-15ex_SEII.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    write_aim424(OUT)
    for lang, names in LOADOUT_NAMES.items():
        src_names = UPSTREAM / f"language_{lang}" / "loadout_names.ini"
        body = src_names.read_text(encoding="utf-8").rstrip("\n")
        body += "\n# ---------- SEST Revamp ----------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    n_loadouts = len(existing) + len(NEW_KEYS)
    print(f"built {OUT.relative_to(ROOT)}: {n_loadouts} loadouts ({len(NEW_KEYS)} new), "
          f"{len(refs)} ammo refs validated, {len(used)} position keys validated")


if __name__ == "__main__":
    main()
