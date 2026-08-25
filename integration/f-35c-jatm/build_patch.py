#!/usr/bin/env python3
"""Build the SEST F-35C JATM patch: AIM-260 loadout options for the F-35C the
Gerald R. Ford's air wing flies.

Base file: F-35C Lightning II Alt. Loadouts' aircraft/usn_f-35c.ini. That mod
ships the richest F-35C in the collection (20 loadouts incl. AirToAirJATM,
SEADJATM, the AGM-158C/D heavy fits and the JSOW family). Unit inis are
whole-file overrides and this pack sits ABOVE it, so rebasing here keeps all
of those fits instead of silently replacing them with the leaner US Naval
Aviation file. Adds the AIM-260 and AIM-424 MALICE loadouts on top.

Usage (repo root):  python3 integration/f-35c-jatm/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3607989779"          # F-35C Alt. Loadouts (richest F-35C)
USNA = ROOT / "mods-source" / "3737267013"              # US Naval Aviation (ammo + AGM-88G model)
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

# pyl_l/pyl_r are the WINGTIP launch rails and [WeaponSystem2Intercept260Beast]
# puts AIM-9X on the wingtip stations, so they must stay visible or the
# missiles float unattached.
SubmodelsToHide=wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right

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
        "Intercept260": "SEST Intercept (6x AIM-260 int)",
        "Intercept260Beast": "SEST Intercept Beast (10x AIM-260)",
        "Malice424": "SEST Intercept MALICE (2x AIM-424 int)",
    },
    "cn": {
        "Intercept260": "SEST 截击 (6x AIM-260 内置)",
        "Intercept260Beast": "SEST 重挂截击 (10x AIM-260)",
        "Malice424": "SEST 马利斯截击 (2x AIM-424 内置)",
    },
}

INFO_INI = """[Language_en]
Name=SEST F-35C JATM
Description=AIM-260 JATM and AIM-424 MALICE loadout options for the F-35C the Gerald R. Ford JSF air wing flies: a 6-missile internal stealth intercept fit, a 10-missile beast fit, and a stealth fit with two internal AIM-424 MALICE very-long-range AAMs (AARGM-ER airframe, AIM-174-class reach). Built on the F-35C Alt. Loadouts file so all 20 of its loadouts are kept. Requires F-35C Lightning II Alt. Loadouts, US Naval Aviation (supplies the AGM-88G model the MALICE uses) and the Dingtools Weapon Pack. Place ABOVE F-35C Alt. Loadouts, US Naval Aviation, the deprecated MyGo F-35C, and Modern US Navy.

[Compatibility]
ApproximateVersion=0.8.2
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
    # (the AvailableLoadouts line is extended in step 2 once the carried
    #  keys are known, then again with the SEST keys)

    # 2. Carry over the loadouts only US Naval Aviation defines. The two F-35C
    #    files share just one loadout key, so neither is a superset: Alt.
    #    Loadouts brings the JATM/SEAD/JSOW/QCSK families, USNA brings the
    #    basics (AirToAir, AntiShip, Ferry, CAS, Strike...). Whole-file
    #    override means whichever we ship is ALL the player gets, so merge.
    usna_text = (USNA / "aircraft" / "usn_f-35c.ini").read_text(encoding="utf-8")
    usna_keys = [k.strip() for k in
                 re.search(r"^AvailableLoadouts=([^#\n]*)", usna_text, re.M).group(1).split(",")
                 if k.strip()]
    carried, carried_sections = [], []
    for key in usna_keys:
        if key in existing or key in NEW_KEYS:
            continue
        blocks = []
        for ws in (1, 2):
            # USNA ships an exact duplicate [WeaponSystem1AntiShip] (the second
            # copy lacks ReadyUpTime) - take the FIRST, more complete section
            # only, or the merge would define the loadout twice.
            m2 = re.search(rf"^\[WeaponSystem{ws}{re.escape(key)}\]\n(.*?)(?=^\[)",
                           usna_text, re.M | re.S)
            if m2:
                blocks.append(f"[WeaponSystem{ws}{key}]\n{m2.group(1).rstrip()}\n")
        if not blocks:
            sys.exit(f"USNA lists loadout {key} but defines no section for it")
        carried.append(key)
        carried_sections.append("\n".join(blocks))
    if not carried:
        sys.exit("no USNA-only loadouts found — did the upstream files change?")

    # Validate the carried sections against THIS airframe's hardpoints: every
    # position key they use must exist in the Alt. Loadouts file.
    pos_keys = set(re.findall(r"^([\w\-]+)Positions=", text, re.M))
    used = set(re.findall(r"\|([\w\-]+)$", "\n".join(carried_sections), re.M))
    unknown = sorted(u for u in used if u not in pos_keys)
    if unknown:
        sys.exit(f"carried loadouts need position keys this airframe lacks: {unknown}")

    m = re.search(r"^(AvailableLoadouts=)(.+)$", text, re.M)
    text = (text[: m.start(2)] + m.group(2).rstrip() + ","
            + ",".join(carried + NEW_KEYS) + text[m.end(2):])

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
    carried_block = ("#--------------- Carried over from US Naval Aviation --------------\n"
                     "# Loadouts the Alt. Loadouts base does not define, kept so this\n"
                     "# whole-file override loses nothing the player had before.\n\n"
                     + "\n".join(carried_sections) + "\n")
    text = text.replace(marker, carried_block + NEW_SECTIONS + marker, 1)

    # 4. Validate ammo references against the ecosystem
    known = {AIM424_ID}  # provided by this pack itself (written below)
    for d in (UPSTREAM, USNA, WEAPON_PACK, VANILLA):
        known |= {p.stem for p in d.rglob("*.ini") if p.parent.name == "ammunition"}
    refs = set(re.findall(r"^Station\d+=([^|\s/]+)",
                          NEW_SECTIONS + "\n".join(carried_sections), re.M))
    missing = sorted(r for r in refs if r not in known)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")

    # 5. Sanity: no loadout section got defined twice by the merge
    heads = re.findall(r"^\[WeaponSystem[12][A-Za-z0-9_.\-]+\]$", text, re.M)
    dupes = sorted({h for h in heads if heads.count(h) > 1})
    if dupes:
        sys.exit(f"merge produced duplicate loadout sections: {dupes}")
    keys_final = re.search(r"^AvailableLoadouts=([^#\n]*)", text, re.M).group(1).split(",")
    if len(keys_final) != len(set(k.strip() for k in keys_final)):
        sys.exit("merge produced a duplicate key in AvailableLoadouts")

    # 6. Write the mod folder
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "usn_f-35c.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    write_aim424(OUT)
    for lang, names in LOADOUT_NAMES.items():
        # Alt. Loadouts ships English only; fall back to US Naval Aviation for
        # any other language so its names are not lost by the override.
        src_names = UPSTREAM / f"language_{lang}" / "loadout_names.ini"
        if not src_names.exists():
            src_names = USNA / f"language_{lang}" / "loadout_names.ini"
        if not src_names.exists():
            continue
        body = src_names.read_text(encoding="utf-8").rstrip("\n")
        body += "\n\n#--------------- SEST F-35C JATM ----------------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: "
          f"{len(existing) + len(carried) + len(NEW_KEYS)} loadouts "
          f"({len(existing)} from Alt. Loadouts + {len(carried)} carried from "
          f"US Naval Aviation + {len(NEW_KEYS)} SEST), {len(refs)} ammo refs validated")


if __name__ == "__main__":
    main()
