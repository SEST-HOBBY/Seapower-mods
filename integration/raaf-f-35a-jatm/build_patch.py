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
USNA = ROOT / "mods-source" / "3737267013"              # US Naval Aviation (F-35C EW suite)
WEAPON_PACK = ROOT / "mods-source" / "3760871384"       # Dingtools Weapon Pack
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
OUT = Path(__file__).resolve().parent / "SEST_RAAF_F-35A_JATM"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402

NEW_KEYS = ["Intercept260Stealth", "Intercept260", "Intercept260Beast", "Malice424"]

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
SubmodelsToHide=pyl_l,pyl_r,wing_pyl_inner,wing_pyl_outer,wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right

# Full-stealth counter-air/SEAD fit: two AIM-424 MALICE on the big bay
# stations (7/8, where JSM/JDAM go) plus two AIM-260 on the bay door rails.
Station3=dts_aim-260
Station4=dts_aim-260
Station7=sest_aim-424
Station8=sest_aim-424

"""

LOADOUT_NAMES = {
    # Intercept260/Intercept260Beast/Malice424 are also defined by the F-35C
    # pack — keep the shared keys' strings identical across both packs.
    "en": {
        "Intercept260Stealth": "SEST Intercept Stealth (AIM-260)",
        "Intercept260": "SEST Intercept (6x AIM-260 int)",
        "Intercept260Beast": "SEST Intercept Beast (10x AIM-260)",
        "Malice424": "SEST Intercept MALICE (2x AIM-424 int)",
    },
}

INFO_INI = """[Language_en]
Name=SEST RAAF F-35A JATM
Description=Brings the RAAF F-35A's electronic-warfare suite up to F-35C standard (AN/APG-81 OECM, AN/ASQ-239A RWR and ESM, AN/ALQ-239A DECM, AAQ-40 EOTS, AAQ-37 EODAS, Link-16 and GPS receivers, replacing the F-22 legacy ALR-94/ALQ-94 pair) and adds AIM-260 JATM and AIM-424 MALICE loadout options: a 6-missile internal stealth fit, the same with wingtip AIM-9X, a 10-missile beast fit, and a stealth fit with two internal AIM-424 MALICE very-long-range AAMs (AARGM-ER airframe, AIM-174-class reach). Requires the RAAF F-35A mod, the Dingtools Weapon Pack, and US Naval Aviation (which defines the EW sensor types and the AGM-88G model the MALICE uses). Place ABOVE the RAAF F-35A mod in the Mod Manager.

[Compatibility]
ApproximateVersion=0.8.2
"""


SENSOR_BANNER = "[---------- Weapon Systems ----------]"


def transplant_ew_suite(text):
    """Give the RAAF F-35A the F-35C's electronic-warfare suite.

    Upstream ships a 6-sensor fit whose EW half is F-22 legacy kit
    (AN/ALR-94 + ALQ-94). The maintained F-35C carries the real F-35 suite:
    AN/APG-81 OECM, AN/ASQ-239A RWR and ESM, AN/ALQ-239A DECM, the AAQ-40
    EOTS pair, AAQ-37 EODAS, Link-16 and GPS receivers.

    SensorSystem1 (Eyes) and SensorSystem2 (AN/APG-81) are left in place
    because AssociatedSensors= lines point at SensorSystem2 by index; only
    systems 3+ are replaced, and the F-35C numbers them 3-12 exactly as they
    land here, so no reference has to be renumbered.
    """
    donor = (USNA / "aircraft" / "usn_f-35c.ini").read_text(encoding="utf-8-sig")
    m = re.search(r"(?ms)^\[SensorSystem3\].*?(?=^\[-+ Weapon Systems -+\])", donor)
    if not m:
        sys.exit("could not extract the F-35C sensor block — upstream layout changed")
    block = m.group(0).rstrip() + "\n\n"

    count = len(re.findall(r"^\[SensorSystem\d+\]", block, re.M)) + 2  # + Eyes and radar
    text, n = re.subn(r"(?ms)^\[SensorSystem3\].*?(?=^\[-+ Weapon Systems -+\])", block, text)
    if n != 1:
        sys.exit(f"sensor block replacement matched {n} times — refusing to guess")
    text, k = re.subn(r"^NumberOfSensorSystems=\d+$",
                      f"NumberOfSensorSystems={count}", text, count=1, flags=re.M)
    if k != 1:
        sys.exit("could not update NumberOfSensorSystems")

    # Every sensor type named must be defined by a mod that will be loaded.
    defined = set()
    for f in (ROOT / "mods-source").rglob("systems/sensors.ini"):
        defined |= set(re.findall(r"^\[([^\]]+)\]", f.read_text(encoding="utf-8-sig", errors="replace"), re.M))
    used = set(re.findall(r"^SystemName=(.+?)\s*$", block, re.M))
    unknown = sorted(u for u in used if u not in defined)
    if unknown:
        sys.exit(f"sensor types not defined by any installed mod: {unknown}")
    return text, count, sorted(used)


def main():
    src = UPSTREAM / "aircraft" / "raaf_f-35a.ini"
    text = src.read_text(encoding="utf-8-sig")

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

    # 1b. Position offsets so the external AIM-260s sit flush on this
    #     airframe's wing pylons (units: ~7cm per 0.001; +y = up, +z =
    #     forward). Split per pylon pair: inner (WS2 stations 3/4) slightly
    #     forward of the outer (5/6), which keeps the proven aft position.
    text, k = re.subn(r"(\[WeaponSystem2\][^\[]*?NumberOfStations=\d+\n)",
                      r"\1AAM260IPositions=0,0.0025,0.0035\nAAM260OPositions=0,0.0025,0.002\n",
                      text, count=1, flags=re.S)
    if k != 1:
        sys.exit("could not inject AAM260 position keys into [WeaponSystem2]")

    # 1c. Bring the EW suite up to F-35C standard
    text, sensor_count, sensor_names = transplant_ew_suite(text)

    # 2. Inject new sections before the WeaponMagazines banner
    marker = "[---------- WeaponMagazines ----------]"
    if marker not in text:
        sys.exit("WeaponMagazines marker not found — upstream layout changed")
    text = text.replace(marker, NEW_SECTIONS + marker, 1)

    # 3. Validate ammo references against the ecosystem
    known = {AIM424_ID}  # provided by this pack itself (written below)
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
    write_aim424(OUT)
    for lang, names in LOADOUT_NAMES.items():
        src_names = UPSTREAM / f"language_{lang}" / "loadout_names.ini"
        body = src_names.read_text(encoding="utf-8-sig").rstrip("\n")
        body += "\n\n#--------------- SEST RAAF F-35A JATM ----------------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: {len(existing) + len(NEW_KEYS)} loadouts "
          f"({len(NEW_KEYS)} new), {len(refs)} ammo refs validated, "
          f"EW suite {sensor_count} sensors: {', '.join(sensor_names)}")


if __name__ == "__main__":
    main()
