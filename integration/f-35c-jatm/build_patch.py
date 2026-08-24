#!/usr/bin/env python3
"""Build the SEST F-35C JATM patch: AIM-260 loadout options for the F-35C the
Gerald R. Ford's air wing flies.

Base file: US Naval Aviation's aircraft/usn_f-35c.ini (the maintained F-35C —
the Ford's JSF variant spawns `usn_f-35c`, resolved by mod order). Adds two
AIM-260 loadouts using the Dingtools Weapon Pack's dts_aim-260, and removes an
upstream bug (an exact duplicate [WeaponSystem1AntiShip] section).

Usage (repo root):  python3 integration/f-35c-jatm/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3737267013"          # US Naval Aviation (misaka)
WEAPON_PACK = ROOT / "mods-source" / "3760871384"       # Dingtools Weapon Pack
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
OUT = Path(__file__).resolve().parent / "SEST_F-35C_JATM"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402

NEW_KEYS = ["Intercept260", "Intercept260Beast", "Malice424"]

NEW_SECTIONS = """\
#--------------- SEST JATM (AIM-260) --------------
# Added by the SEST F-35C JATM patch. dts_aim-260 comes from the Dingtools
# Weapon Pack; everything else resolves from US Naval Aviation / vanilla.

[WeaponSystem1Intercept260]
ReadyUpTime=15               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.

SubmodelsToHide=wing_pyl_inner,wing_pyl_outer,wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right

Station1=dts_aim-260
Station2=dts_aim-260
Station3=dts_aim-260
Station4=dts_aim-260
Station5=dts_aim-260
Station6=dts_aim-260

[WeaponSystem2Intercept260]
Station1=usn_aim-9x
Station2=usn_aim-9x

[WeaponSystem1Intercept260Beast]
ReadyUpTime=25               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.

SubmodelsToHide=pyl_l,pyl_r,wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right

Station1=dts_aim-260
Station2=dts_aim-260
Station3=dts_aim-260
Station4=dts_aim-260
Station5=dts_aim-260
Station6=dts_aim-260

[WeaponSystem2Intercept260Beast]
Station1=usn_aim-9x
Station2=usn_aim-9x
Station3=dts_aim-260_w|AAM260I
Station4=dts_aim-260_w|AAM260I
Station5=dts_aim-260_w|AAM260O
Station6=dts_aim-260_w|AAM260O

[WeaponSystem1Malice424]
ReadyUpTime=20               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.

SubmodelsToHide=pyl_l,pyl_r,wing_pyl_inner,wing_pyl_outer,wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right

# Full-stealth counter-air/SEAD fit: two AIM-424 MALICE on the big bay
# stations (7/8, where JSM/JDAM go) plus two AIM-260 on the bay door rails.
Station3=dts_aim-260
Station4=dts_aim-260
Station7=sest_aim-424
Station8=sest_aim-424

"""

LOADOUT_NAMES = {
    # NOTE: [LoadoutNames] keys are global across mods; the RAAF pack defines
    # Intercept260/Intercept260Beast/Malice424 too, so the strings here are
    # kept identical to that pack's (whichever pack wins load order, both
    # aircraft read correctly). Keep display strings comma-free.
    "en": {
        "Intercept260": "Intercept (6x AIM-260 int)",
        "Intercept260Beast": "Intercept Beast (10x AIM-260)",
        "Malice424": "Intercept MALICE (2x AIM-424 int)",
    },
    "cn": {
        "Intercept260": "截击 (6x AIM-260 内置)",
        "Intercept260Beast": "重挂截击 (10x AIM-260)",
        "Malice424": "马利斯截击 (2x AIM-424 内置)",
    },
}

INFO_INI = """[Language_en]
Name=SEST F-35C JATM
Description=AIM-260 JATM and AIM-424 MALICE loadout options for the US Naval Aviation F-35C (the aircraft the Gerald R. Ford JSF air wing flies): a 6-missile internal stealth intercept fit, a 10-missile beast fit, and a stealth fit with two internal AIM-424 MALICE very-long-range AAMs (AARGM-ER airframe, AIM-174-class reach). Requires US Naval Aviation (also provides the AGM-88G model the MALICE uses) and the Dingtools Weapon Pack. Place ABOVE US Naval Aviation, F-35C Alt. Loadouts, the deprecated MyGo F-35C, and Modern US Navy. Also removes a duplicated AntiShip section from the base file.

[Compatibility]
ApproximateVersion=0.6.8
"""

DUP_ANTISHIP = """[WeaponSystem1AntiShip]
SubmodelsToHide=pyl_l,pyl_r,wing_pyl_inner,wing_pyl_outer,wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right
Station3=usn_aim-120d3
Station4=usn_aim-120d3
Station7=usn_jsm
Station8=usn_jsm
"""


def main():
    src = UPSTREAM / "aircraft" / "usn_f-35c.ini"
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

    # 2. Remove the upstream duplicate [WeaponSystem1AntiShip] block (the copy
    #    without ReadyUpTime). Tolerate line-ending/spacing drift; require
    #    exactly one removal.
    pattern = re.escape(DUP_ANTISHIP).replace(r"\n", r"\s*\n")
    text, n = re.subn(pattern, "", text, count=0)
    if n == 0:
        print("note: upstream duplicate AntiShip block not found (may be fixed upstream) — continuing")
    elif n > 1:
        sys.exit(f"duplicate-AntiShip pattern matched {n} times — refusing to guess")

    # 2b. Position offsets so the external AIM-260s sit flush on the wing
    #     pylons (units: ~7cm per 0.001; +y = up, +z = forward). Split per
    #     pylon pair: inner (WS2 stations 3/4) slightly forward of the outer
    #     (5/6), which keeps the proven aft position. Tune here.
    text, k = re.subn(r"(\[WeaponSystem2\][^\[]*?NumberOfStations=\d+\n)",
                      r"\1AAM260IPositions=0,0.0025,0.0035\nAAM260OPositions=0,0.0025,0.002\n",
                      text, count=1, flags=re.S)
    if k != 1:
        sys.exit("could not inject AAM260 position keys into [WeaponSystem2]")

    # 3. Inject new sections before the WeaponMagazines banner
    marker = "[---------- WeaponMagazines ----------]"
    if marker not in text:
        sys.exit("WeaponMagazines marker not found — upstream layout changed")
    text = text.replace(marker, NEW_SECTIONS + marker, 1)

    # 4. Validate ammo references against the ecosystem
    known = {AIM424_ID}  # provided by this pack itself (written below)
    for d in (UPSTREAM, WEAPON_PACK, VANILLA):
        known |= {p.stem for p in d.rglob("*.ini") if p.parent.name == "ammunition"}
    refs = set(re.findall(r"^Station\d+=([^|\s/]+)", NEW_SECTIONS, re.M))
    missing = sorted(r for r in refs if r not in known)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")

    # 5. Sanity: exactly one [WeaponSystem1AntiShip] remains
    if text.count("[WeaponSystem1AntiShip]") != 1:
        sys.exit("unexpected AntiShip section count after dedupe")

    # 6. Write the mod folder
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "usn_f-35c.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    write_aim424(OUT)
    for lang, names in LOADOUT_NAMES.items():
        src_names = UPSTREAM / f"language_{lang}" / "loadout_names.ini"
        body = src_names.read_text(encoding="utf-8").rstrip("\n")
        body += "\n\n#--------------- SEST F-35C JATM ----------------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: {len(existing) + len(NEW_KEYS)} loadouts "
          f"({len(NEW_KEYS)} new), duplicate AntiShip removed: {bool(n)}, "
          f"{len(refs)} ammo refs validated")


if __name__ == "__main__":
    main()
