#!/usr/bin/env python3
"""Build the SEST RAAF F-35A JATM patch: AIM-260 loadout options for Greene's
RAAF F-35A, following the mod's own Stealth / non-Stealth loadout convention.

Since October 2026 this pack also CARRIES the RAAF F-35A. Greene's mod
(Workshop 3514484654) was removed from the Workshop, so no new player can
download it, and the campaigns fly it. Its text files survive in
mods-source/_retired/3514484654; its model, textures and weapon meshes went with it.
The pack ships every file of the mod that won the load order (the aircraft,
its squadrons and animations, the gun pod and five rounds, and the three
language keys only it defined).

The airframe is the mod's own: recovered/ holds its F-35A model, the model's
three textures and the RAAF livery, recovered from a copy of the mod on
5 October 2026 and pinned by recovered/SHA256SUMS; they ship at the paths
the mod used. The mod's weapon meshes were not recovered, so those model
references move to models still in the collection:

- JSM and JSM land-attack onto US Naval Aviation's JSM model;
- GBU-53 onto US Naval Aviation's GBU-53 model;
- the GBU-31 v1 onto the GBU-31 model a live round in the collection uses;
- the BRU-61A rack material (the rack mesh is part of the F-35A model)
  onto the copy in the collection's gbu-39 folder.
The AIM-120C-7 keeps its path: another mod in the collection ships the same
model and material.

Without recovered/ (or with a file that no longer matches its checksum) the
build stops rather than ship an aircraft with no model.

The stats, loadouts, squadrons and names are Greene's, unchanged.

Usage (repo root):  python3 integration/raaf-f-35a-jatm/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "_retired" / "3514484654"  # RAAF F-35A (Greene), removed from the Workshop
USNA = ROOT / "mods-source" / "3737267013"              # US Naval Aviation (F-35C EW suite)
WEAPON_PACK = ROOT / "mods-source" / "3760871384"       # Dingtools Weapon Pack
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
GBU31_DONOR = ROOT / "mods-source" / "3430135740"       # a live usn_gbu-31 on the GBU-31 model
RECOVERED = Path(__file__).resolve().parent / "recovered"   # the mod's own model, textures, livery
OUT = Path(__file__).resolve().parent / "SEST_RAAF_F-35A_JATM"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402
from common.registry import restore_vanilla  # noqa: E402

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
Description=Carries Greene's RAAF F-35A, which was removed from the Workshop: the aircraft with its own model and RAAF paint, its RAAF squadrons, its gun pod and rounds. Brings the RAAF F-35A's electronic-warfare suite up to F-35C standard (AN/APG-81 OECM, AN/ASQ-239A RWR and ESM, AN/ALQ-239A DECM, AAQ-40 EOTS, AAQ-37 EODAS, Link-16 and GPS receivers, replacing the F-22 legacy ALR-94/ALQ-94 pair) and adds AIM-260 JATM and AIM-424 MALICE loadout options: a 6-missile internal stealth fit, the same with wingtip AIM-9X, a 10-missile beast fit, and a stealth fit with two internal AIM-424 MALICE very-long-range AAMs (Raytheon's LRAAM, in excess of 250 nm). Requires the Dingtools Weapon Pack and US Naval Aviation (which supplies the JSM and GBU-53 models, defines the EW sensor types, and the model the MALICE borrows as a rendering stand-in).

[Compatibility]
ApproximateVersion=0.8.4
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


# --- taking in the removed mod ---------------------------------------------
# Files of 3514484654 that won the load order, shipped with their model
# references moved (see the module docstring). Each entry: the file, and
# where its resource block now comes from (None = keep as it is).
INTAKE = {
    "aircraft/raaf_f-35a_squadrons.ini": None,
    "animations/animations_raaf_f-35a.ini": None,
    "ammunition/raaf_f-35_gun_pod.ini": None,          # its mesh is in the recovered model
    "ammunition/usaf_aim-120c7.ini": None,
    "ammunition/usaf_gbu-31_v1.ini": GBU31_DONOR / "ammunition" / "usn_gbu-31.ini",
    "ammunition/usaf_gbu-53.ini": USNA / "ammunition" / "usn_gbu-53.ini",
    "ammunition/usaf_jsm.ini": USNA / "ammunition" / "usn_jsm.ini",
    "ammunition/usaf_jsm_land.ini": USNA / "ammunition" / "usn_jsm_land.ini",
}
# language keys only this mod defined (the rest are defined higher up)
INTAKE_NAMES = {"ammunition_names.ini": ["usaf_aim-120c7", "usaf_gbu-31_v1", "usaf_gbu-53"]}

AIRFRAME_MOVES = [
    ("ResourcesMaterialFolder=assets/models/weapon/ammunition/gbu-39/",
     "ResourcesMaterialFolder=assets/models/ammunition/gbu-39/"),
]
RES_BLOCK = re.compile(r"(?m)^(?:Resources\w*=.*\n)+")


def move_airframe(text, label):
    for old, new in AIRFRAME_MOVES:
        text = text.replace(old, new)
    left = [m for m in ("weapon/ammunition/gbu-39/",) if m in text]
    if left:
        sys.exit(f"{label}: still points at the removed mod's assets: {left}")
    return text


def swap_resources(text, donor, label):
    """Replace the first block of Resources*= lines with the donor's."""
    mine = RES_BLOCK.search(text)
    theirs = RES_BLOCK.search(donor.read_text(encoding="utf-8-sig"))
    if not mine or not theirs:
        sys.exit(f"{label}: no Resources block to swap")
    return text[:mine.start()] + theirs.group(0) + text[mine.end():]


def write_intake():
    for rel, donor in INTAKE.items():
        text = (UPSTREAM / rel).read_text(encoding="utf-8-sig")
        if donor is not None:
            text = swap_resources(text, donor, rel)
        if "assets/models/weapon/ammunition/jsm/" in text or "weapon/ammunition/gbu-53/" in text:
            sys.exit(f"{rel}: still points at the removed mod's assets")
        out = OUT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    for name, keys in INTAKE_NAMES.items():
        body = (UPSTREAM / "language_en" / name).read_text(encoding="utf-8-sig")
        lines = [l for l in body.splitlines()
                 if re.match(r"^([^=#;\s][^=]*?)\s*=", l)
                 and re.match(r"^([^=]+?)\s*=", l).group(1) in keys]
        if len(lines) != len(keys):
            sys.exit(f"language_en/{name}: expected {keys}")
        d = OUT / "language_en"
        d.mkdir(parents=True, exist_ok=True)
        target = d / name
        if target.exists():      # the AIM-424's name is already here: add below it
            target.write_text(target.read_text(encoding="utf-8").rstrip("\n")
                              + "\n# ---------- taken in from the RAAF F-35A ----------\n"
                              + "".join(l + "\n" for l in lines), encoding="utf-8")
        else:
            head = re.search(r"^\[[^\]]+\]", body, re.M).group(0)
            target.write_text(head + "\n" + "".join(l + "\n" for l in lines), encoding="utf-8")
    # aircraft_names is sectioned: the aircraft's own section (its name,
    # squadron names and callsigns) is the one no other mod defines
    body = (UPSTREAM / "language_en" / "aircraft_names.ini").read_text(encoding="utf-8-sig")
    sec = re.search(r"(?ms)^\[raaf_f-35a\]\n.*?(?=^\[|\Z)", body)
    if not sec:
        sys.exit("language_en/aircraft_names.ini: no [raaf_f-35a] section")
    (OUT / "language_en" / "aircraft_names.ini").write_text(
        "[General]\n\n" + sec.group(0).rstrip() + "\n", encoding="utf-8")
    return len(INTAKE) + write_recovered()


def write_recovered():
    """The mod's own model, textures and livery, checked against SHA256SUMS,
    plus the model's material file from the export."""
    import hashlib
    sums = RECOVERED / "SHA256SUMS"
    if not sums.is_file():
        sys.exit(f"{sums} missing - the F-35A's model and paint are not in this checkout")
    n = 0
    for line in sums.read_text(encoding="utf-8").splitlines():
        digest, rel = line.split(None, 1)
        src = RECOVERED / rel
        if not src.is_file() or hashlib.sha256(src.read_bytes()).hexdigest() != digest:
            sys.exit(f"recovered/{rel} is missing or does not match SHA256SUMS")
        out = OUT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(src.read_bytes())
        n += 1
    mat = "assets/models/vehicle/aircraft/f-35/f-35a_mat.ini"
    (OUT / mat).write_text((UPSTREAM / mat).read_text(encoding="utf-8-sig"), encoding="utf-8")
    return n + 1


INTERNAL_ONLY_KITS = ("StrikeLongRangeStealth",)


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

    # 1b2. Internal-only kits fly clean. Upstream's StrikeLongRangeStealth
    #      (two JSM in the bays, nothing outside) hides the fuselage pylons
    #      but not the wing ones, so the "stealth" JSM kit showed four empty
    #      wing pylons; its twin AntiShip (the same bay load) hides them.
    for kit in INTERNAL_ONLY_KITS:
        text, k = re.subn(rf"(\[WeaponSystem1{kit}\]\nSubmodelsToHide=)pyl_l,pyl_r,wing_rail_inner,",
                          r"\1pyl_l,pyl_r,wing_pyl_inner,wing_pyl_outer,wing_rail_inner,", text, count=1)
        if k != 1:
            sys.exit(f"{kit}: upstream hide list changed - re-check the wing pylons")
        if re.search(rf"^\[WeaponSystem2{kit}\]", text, re.M):
            sys.exit(f"{kit}: now carries external stores - it needs its wing pylons")

    # 1c. Bring the EW suite up to F-35C standard
    text, sensor_count, sensor_names = transplant_ew_suite(text)

    # 2. Inject new sections before the WeaponMagazines banner
    marker = "[---------- WeaponMagazines ----------]"
    if marker not in text:
        sys.exit("WeaponMagazines marker not found — upstream layout changed")
    text = text.replace(marker, NEW_SECTIONS + marker, 1)

    # 3. Validate ammo references against the ecosystem
    known = {AIM424_ID}  # provided by this pack itself (written below)
    # all of mods-source (incl. _vanilla): most stores have several providers,
    # and a narrow donor list would hard-bind the build to one of them
    known |= {p.stem for p in (ROOT / "mods-source").rglob("*.ini")
              if p.parent.name == "ammunition"}
    refs = set(re.findall(r"^Station\d+=([^|\s/]+)", NEW_SECTIONS, re.M))
    missing = sorted(r for r in refs if r not in known)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")

    # 1d. The airframe onto US Naval Aviation's F-35C model
    text = move_airframe(text, "aircraft/raaf_f-35a.ini")

    # 4. Write the mod folder
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "raaf_f-35a.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    write_aim424(OUT)
    taken = write_intake()
    for lang, names in LOADOUT_NAMES.items():
        src_names = UPSTREAM / f"language_{lang}" / "loadout_names.ini"
        body = src_names.read_text(encoding="utf-8-sig").rstrip("\n")
        # The upstream renames generic loadout ids to suit its own
        # aircraft. Those ids belong to every aircraft in the game, and
        # this pack sits at the top of the load order, so carrying the
        # rename forward would guarantee it wins. See common/registry.
        body, _ = restore_vanilla(
            body, VANILLA / f"language_{lang}" / "loadout_names.ini",
            keep=names, label=f"language_{lang}/loadout_names.ini")
        body += "\n\n#--------------- SEST RAAF F-35A JATM ----------------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: {len(existing) + len(NEW_KEYS)} loadouts "
          f"({len(NEW_KEYS)} new), {len(refs)} ammo refs validated, "
          f"EW suite {sensor_count} sensors: {', '.join(sensor_names)}; "
          f"{taken} more files taken in from the removed mod")


if __name__ == "__main__":
    main()
