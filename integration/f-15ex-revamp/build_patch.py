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

NEW_KEYS = ["AntiShipHeavy", "AntiShipHarpoon", "Quicksink", "BigStick174"]

NEW_SECTIONS = """\
[--------------------------- SEST Revamp loadouts ---------------------------]
# Added by the SEST F-15EX Revamp patch. Requires the Dingtools Weapon Pack
# (dts_ weapons); the BigStick174 loadout additionally requires Murder Hornet
# (usn_aim-174b). AGM-84D and the 610 gal tank are vanilla.

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

[WeaponSystem1AntiShipHarpoon]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=usn_agm-84d|AGM
Station12=usn_agm-84d|AGM
Station15=usaf_tank_610_f-15|WT
Station16=usn_agm-84d|WW
Station17=usn_agm-84d|WW
Station26=dts_anaaq-33
Station27=dts_anaaq-13

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

"""

LOADOUT_NAMES = {
    "en": {
        "AntiShipHeavy": "AntiShipLRASM6",
        "AntiShipHarpoon": "AntiShipHarpoon",
        "Quicksink": "StrikeQuicksink",
        "BigStick174": "Intercept174",
    },
    "cn": {
        "AntiShipHeavy": "重型反舰LRASM×6",
        "AntiShipHarpoon": "鱼叉反舰",
        "Quicksink": "快沉反舰JDAM",
        "BigStick174": "超远程截击174",
    },
}

INFO_INI = """[Language_en]
Name=SEST F-15EX Revamp
Description=Four extra F-15EX loadouts: 6x LRASM anti-ship surge, 4x AGM-84D Harpoon, 4x GBU-31 Quicksink, and a what-if 4x AIM-174B interceptor. Requires the F-15SE (F-15EX) mod and Dingtools Weapon Pack; the AIM-174B loadout also requires the Murder Hornet mod. Place ABOVE the F-15EX mod in the Mod Manager.

[Compatibility]
ApproximateVersion=0.6.8
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
    known = set()
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
