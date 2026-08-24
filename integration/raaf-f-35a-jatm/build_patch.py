#!/usr/bin/env python3
"""Build the SEST RAAF F-35A JATM patch: AIM-260 loadout options for Greene's
RAAF F-35A, following the mod's own Stealth / non-Stealth loadout convention.

Usage (repo root):  python3 integration/raaf-f-35a-jatm/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3514484654"          # RAAF F-35A (Greene)
WEAPON_PACK = ROOT / "mods-source" / "3760871384"       # Dingtools Weapon Pack
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
OUT = Path(__file__).resolve().parent / "SEST_RAAF_F-35A_JATM"

NEW_KEYS = ["Intercept260Stealth", "Intercept260", "Intercept260Beast"]

NEW_SECTIONS = """\
#--------------- SEST JATM (AIM-260) --------------
# Added by the SEST RAAF F-35A JATM patch. dts_aim-260 comes from the
# Dingtools Weapon Pack; everything else resolves from this mod / vanilla.

[WeaponSystem1Intercept260Stealth]
SubmodelsToHide=pyl_l,pyl_r,wing_pyl_inner,wing_pyl_outer,wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right

Station1=dts_aim-260
Station2=dts_aim-260
Station3=dts_aim-260
Station4=dts_aim-260
Station5=dts_aim-260
Station6=dts_aim-260

[WeaponSystem1Intercept260]
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
Station3=dts_aim-260_w|AAM260
Station4=dts_aim-260_w|AAM260
Station5=dts_aim-260_w|AAM260
Station6=dts_aim-260_w|AAM260

"""

LOADOUT_NAMES = {
    "en": {
        "Intercept260Stealth": "Intercept Stealth (AIM-260)",
        "Intercept260": "Intercept (AIM-260)",
        "Intercept260Beast": "Intercept Beast (10x AIM-260)",
    },
}

INFO_INI = """[Language_en]
Name=SEST RAAF F-35A JATM
Description=AIM-260 JATM loadout options for the RAAF F-35A: a 6-missile internal stealth fit, the same with wingtip AIM-9X, and a 10-missile beast fit. Requires the RAAF F-35A mod and the Dingtools Weapon Pack. Place ABOVE the RAAF F-35A mod in the Mod Manager.

[Compatibility]
ApproximateVersion=0.6.8
"""


def main():
    src = UPSTREAM / "aircraft" / "raaf_f-35a.ini"
    text = src.read_text(encoding="utf-8")

    # 1. Extend AvailableLoadouts — the upstream line carries a trailing
    #    '#'-comment, so insert before it rather than appending to the line.
    m = re.search(r"^(AvailableLoadouts=)([^#\n]*)(#[^\n]*)?$", text, re.M)
    if not m:
        sys.exit("AvailableLoadouts line not found — upstream layout changed")
    existing = [k.strip() for k in m.group(2).split(",") if k.strip()]
    clash = [k for k in NEW_KEYS if k in existing]
    if clash:
        sys.exit(f"loadout keys already exist upstream: {clash}")
    keys = ",".join(existing + NEW_KEYS)
    tail = (" " + m.group(3)) if m.group(3) else ""
    text = text[: m.start()] + m.group(1) + keys + tail + text[m.end():]

    # 1b. Position offset so the external AIM-260 sits flush on this airframe's
    #     wing pylons (units: ~7cm per 0.001; +y = up, +z = forward). Tune here.
    text, k = re.subn(r"(\[WeaponSystem2\][^\[]*?NumberOfStations=\d+\n)",
                      r"\1AAM260Positions=0,0.0025,0.008\n", text, count=1, flags=re.S)
    if k != 1:
        sys.exit("could not inject AAM260Positions into [WeaponSystem2]")

    # 2. Inject new sections before the WeaponMagazines banner
    marker = "[---------- WeaponMagazines ----------]"
    if marker not in text:
        sys.exit("WeaponMagazines marker not found — upstream layout changed")
    text = text.replace(marker, NEW_SECTIONS + marker, 1)

    # 3. Validate ammo references against the ecosystem
    known = set()
    for d in (UPSTREAM, WEAPON_PACK, VANILLA):
        known |= {p.stem for p in d.rglob("*.ini") if p.parent.name == "ammunition"}
    refs = set(re.findall(r"^Station\d+=([^|\s/]+)", NEW_SECTIONS, re.M))
    missing = sorted(r for r in refs if r not in known)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")

    # 4. Write the mod folder
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "raaf_f-35a.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    for lang, names in LOADOUT_NAMES.items():
        src_names = UPSTREAM / f"language_{lang}" / "loadout_names.ini"
        body = src_names.read_text(encoding="utf-8").rstrip("\n")
        body += "\n\n#--------------- SEST RAAF F-35A JATM ----------------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: {len(existing) + len(NEW_KEYS)} loadouts "
          f"({len(NEW_KEYS)} new), {len(refs)} ammo refs validated")


if __name__ == "__main__":
    main()
