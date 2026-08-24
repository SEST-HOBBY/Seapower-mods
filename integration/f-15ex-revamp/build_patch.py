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
            "Truck174", "Malice6", "MaliceER", "MaliceTruck",
            "AAMT120Tanks", "AAMT260Tanks"]

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
# AIM-260 on the inner wing pylon rails, which this fit used to leave empty.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
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
# The outer wing pylons are baked into the airframe model and render whether
# or not they carry anything, so use them: AMRAAM on the pylon2 inner
# stations, AIM-9X outboard of them on the outermost pair.
# AIM-260 on the inner wing pylon rails alongside the tanks.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
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
# 4 on the inner wing pylons' shoulder rails, with the outer wing pylons
# carrying self-escort AAMs and centreline fuel only.
Station1=usn_aim-174b|120
Station2=usn_aim-174b|120
Station5=usn_aim-174b|120
Station6=usn_aim-174b|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=usn_aim-174b|AGM
Station12=usn_aim-174b|AGM
Station13=usn_aim-174b|AGM
Station14=usn_aim-174b|AGM
Station15=usaf_tank_610_f-15|WT

[WeaponSystem1Malice6]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# MALICE mirror of BigStick174: 6x AIM-424 plus AIM-260 on the inner rails.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
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
# MALICE mirror of BigStick174ER: 4x AIM-424 under, 3 tanks, AAMs on the
# outer wing pylons.
# AIM-260 on the inner wing pylon rails alongside the tanks.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=sest_aim-424|AGM
Station12=sest_aim-424|AGM
Station13=sest_aim-424|AGM
Station14=sest_aim-424|AGM
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|WT
Station17=usaf_tank_610_f-15|WT

[WeaponSystem1AAMT120Tanks]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,Py13,Py33,33Glass
# Upstream's AAMT120 missile truck with the wing stations carrying FUEL
# instead of the twin AMRAAM racks: 16 missiles and three 610 gal tanks
# rather than 20 missiles and one. The AAMT rack mesh stays visible.
Station1=dts_aim-120d-3_w|120
Station2=dts_aim-120d-3_w|120
Station5=dts_aim-120d-3_w|120
Station6=dts_aim-120d-3_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-120d-3_w|120
Station10=dts_aim-120d-3_w|120
Station11=dts_aim-120d-3|MTH
Station12=dts_aim-120d-3|MTH
Station13=dts_aim-120d-3|MTH
Station14=dts_aim-120d-3|MTH
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|WT
Station17=usaf_tank_610_f-15|WT

[WeaponSystem1AAMT260Tanks]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,Py13,Py33,33Glass
# The same trade on the AIM-260 truck.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-260_w|120
Station8=dts_aim-260_w|120
Station9=dts_aim-260_w|120
Station10=dts_aim-260_w|120
Station11=dts_aim-260|MTH
Station12=dts_aim-260|MTH
Station13=dts_aim-260|MTH
Station14=dts_aim-260|MTH
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|WT
Station17=usaf_tank_610_f-15|WT

[WeaponSystem1MaliceTruck]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# MALICE mirror of Truck174: 8x AIM-424 plus self-escort AAMs on the outer
# wing pylons, centreline fuel only.
Station1=sest_aim-424|120
Station2=sest_aim-424|120
Station5=sest_aim-424|120
Station6=sest_aim-424|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
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
        "AAMT120Tanks": "AAMT120 LongRange (3 tanks)",
        "AAMT260Tanks": "AAMT260 LongRange (3 tanks)",
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
        "AAMT120Tanks": "AMRAAM卡车 (远程 3副油箱)",
        "AAMT260Tanks": "AIM-260卡车 (远程 3副油箱)",
    },
}

# ---------------------------------------------------------------------------
# Squadrons
# ---------------------------------------------------------------------------
# Upstream defines two squadrons - the 44th and 67th FS at Kadena, each with
# its own livery texture. A mission that wants more than two distinct F-15EX
# units has nothing to reference, so this adds the type's other announced
# operators. The mod ships only those two skins, so the added squadrons reuse
# them in rotation and differ by identity and callsign rather than by paint.
#
# The first two entries MUST stay byte-identical to upstream's (checked at
# build time) so nothing that already references Squadron1/2 changes.
#
# (display name, basing note, livery texture, callsigns)
F15EX_SQUADRONS = [
    ("44th FS 'Vampires'", "18th Wing, Kadena AB, Japan",
     "44_fs.jpg", ["Dusk", "Lazarus"]),
    ("67th FS 'Fighting Cocks'", "18th Wing, Kadena AB, Japan",
     "67_fs.jpg", ["Gobbler", "Rooster"]),
    ("85th TES", "53rd Wing, Eglin AFB - first F-15EX operator",
     "44_fs.jpg", ["Bench"]),
    ("40th FLTS", "96th Test Wing, Eglin AFB",
     "67_fs.jpg", ["Probe"]),
    ("123rd FS 'Redhawks'", "142nd Wing OR ANG, Portland - first ANG F-15EX unit",
     "44_fs.jpg", ["Redhawk"]),
    ("194th FS 'Griffins'", "144th FW CA ANG, Fresno",
     "67_fs.jpg", ["Griffin"]),
    ("131st FS", "104th FW MA ANG, Barnes",
     "44_fs.jpg", ["Minuteman"]),
    ("114th FS 'Eagles'", "173rd FW OR ANG, Kingsley Field",
     "67_fs.jpg", ["Talon"]),
]

LIVERY_FOLDER = "assets/textures/F-15EX/"

SQUADRONS_HEADER = """\
# SEST F-15EX Revamp - squadron definitions for the F-15EX.
# Upstream ships the two Kadena squadrons and their liveries; these add the
# type's other announced operators so a mission can field more than two
# distinct F-15EX units. The mod carries only those two skins, so the added
# squadrons reuse them in rotation and differ by identity and callsign.
[General]
SerialnumberReferences=AF_Serial
EmblemReference=Emblem
NationFlagReference=Flag1
NumberOfSquadrons={count}

[Default]
Nation=US

"""


def build_squadrons():
    """Complete replacement usaf_f-15ex_SEII_squadrons.ini (whole-file override)."""
    src = UPSTREAM / "aircraft" / "usaf_f-15ex_SEII_squadrons.ini"
    upstream = src.read_text(encoding="utf-8", errors="replace")

    # Guard: upstream's own two squadrons must still be what we think they are,
    # or we would silently change which jet wears which paint.
    for i, (_, _, livery, _) in enumerate(F15EX_SQUADRONS[:2], start=1):
        m = re.search(rf"^\[Squadron{i}\].*?^LiveryTexture=(\S+)", upstream, re.S | re.M)
        if not m or m.group(1) != livery:
            sys.exit(f"upstream Squadron{i} livery changed "
                     f"({m.group(1) if m else 'missing'} != {livery}) — rebase this patch")
    if len(re.findall(r"^\[Squadron\d+\]", upstream, re.M)) != 2:
        sys.exit("upstream no longer defines exactly 2 squadrons — rebase this patch")

    blocks = "".join(
        f"[Squadron{i}]  #{name} - {basing}\n"
        f"ResourcesLiveryFolder={LIVERY_FOLDER}\n"
        f"LiveryTexture={livery}\n"
        f"Nation=US\n\n"
        for i, (name, basing, livery, _) in enumerate(F15EX_SQUADRONS, start=1))
    body = SQUADRONS_HEADER.format(count=len(F15EX_SQUADRONS)) + blocks
    return body.rstrip("\n") + "\n"


def build_aircraft_names(lang):
    """Upstream's aircraft_names.ini with the new squadrons appended.

    Upstream's existing Squadron1/2 lines and its Callsigns value are kept
    verbatim - including the Chinese ones - so nothing already translated is
    replaced by English text; only the new units are added.
    """
    src = UPSTREAM / f"language_{lang}" / "aircraft_names.ini"
    text = src.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

    m = re.search(r"^Default=([^,\n]+),([^,\n]*)$", text, re.M)
    if not m:
        sys.exit(f"language_{lang}/aircraft_names.ini has no parsable Default= line")
    short = m.group(2).strip()

    kept = [l for l in text.rstrip("\n").splitlines()
            if not re.match(r"^(Squadron\d+|Callsigns)=", l)]
    existing_sq = re.findall(r"^Squadron\d+=.*$", text, re.M)
    if len(existing_sq) != 2:
        sys.exit(f"language_{lang}: expected 2 upstream squadron names, "
                 f"found {len(existing_sq)} — rebase this patch")
    calls = re.search(r"^Callsigns=(.*)$", text, re.M)
    if not calls:
        sys.exit(f"language_{lang}: no Callsigns line — rebase this patch")

    new_sq = [f"Squadron{i}=F-15EX {name},{short}"
              for i, (name, _, _, _) in enumerate(F15EX_SQUADRONS[2:], start=3)]
    new_calls = "|".join(f"Squadron{i}," + ",".join(c)
                         for i, (_, _, _, c) in enumerate(F15EX_SQUADRONS[2:], start=3))
    lines = kept + existing_sq + new_sq + [f"{calls.group(1)}|{new_calls}"
                                           if calls.group(1).startswith("Callsigns=")
                                           else f"Callsigns={calls.group(1)}|{new_calls}"]
    return "\n".join(lines) + "\n"


INFO_INI = """[Language_en]
Name=SEST F-15EX Revamp
Description=Ten extra F-15EX loadouts: 6x LRASM anti-ship surge, 4x GBU-31 Quicksink, and a what-if very-long-range family - 6x/4x+fuel/8x-truck AIM-174B fits plus matching 6x/4x+fuel/8x-truck AIM-424 MALICE fits, plus long-range versions of the AMRAAM and AIM-260 missile trucks that trade the wing twin-racks for fuel. Requires the F-15SE (F-15EX) mod and Dingtools Weapon Pack; AIM-174B fits also need Murder Hornet, and the MALICE model comes from US Naval Aviation. Place ABOVE the F-15EX mod in the Mod Manager.

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
    (OUT / "aircraft" / "usaf_f-15ex_SEII_squadrons.ini").write_text(
        build_squadrons(), encoding="utf-8")
    for lang in ("en", "cn"):
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "aircraft_names.ini").write_text(build_aircraft_names(lang),
                                              encoding="utf-8")
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
          f"{len(F15EX_SQUADRONS)} squadrons ({len(F15EX_SQUADRONS) - 2} new), "
          f"{len(refs)} ammo refs validated, {len(used)} position keys validated")


if __name__ == "__main__":
    main()
