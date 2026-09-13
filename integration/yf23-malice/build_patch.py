#!/usr/bin/env python3
"""Build the SEST YF-23 MALICE patch: an AIM-424 MALICE loadout for the F-23A
Block 40, the 2025 configuration of the YF-23 Black Widow II mod.

Base file: the mod's aircraft/yf23_f23a_block40_2025.ini - the only one of its
six variants that carries the AIM-260A, and the only file this pack touches.
The mod is the sole provider of every yf23_* stem in the collection, so this
whole-file override has exactly one mod to outrank.

The mod carries its rounds as its own internal-bay variants
(yf23_aim260a_internal, yf23_aim9x2_internal), each a self-contained missile
pointing at the author's own model. Nothing in those files is bay-specific -
"_internal" is the author's convention for "my model, sized for my bay" - so
the MALICE goes on the bay stations as the bare sest_aim-424 every other SEST
pack uses, rendering on its usual stand-in. A yf23_aim424_internal clone would
be a name with no model behind it.

The fit mirrors the F-35C pack's stealth MALICE loadout: two AIM-424 on the
bottom pair of the main bay (stations 1-2, the lowest seats, where a 4.11 m
round releases cleanest), four AIM-260A above them, two AIM-9X Block II in
the side bays. The Malice424 loadout key and its display strings are the
ones the F-35C and RAAF packs already define - [LoadoutNames] keys are global
across mods, so reusing them keeps every SEST MALICE fit reading the same.

Usage (repo root):  python3 integration/yf23-malice/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3796349767"      # YF-23 Black Widow II (Alpine)
USNA = ROOT / "mods-source" / "3737267013"          # US Naval Aviation: AGM-88G stand-in model
OUT = Path(__file__).resolve().parent / "SEST_YF23_MALICE"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402

AIRCRAFT = "yf23_f23a_block40_2025"
NEW_KEYS = ["Malice424"]

NEW_SECTIONS = """\
#--------------- SEST MALICE (AIM-424) --------------
# Added by the SEST YF-23 MALICE patch. sest_aim-424 is this pack's own round;
# the AIM-260A and AIM-9X are the mod's internal-bay variants, unchanged.
# Stations 1-2 are the bottom pair of the main bay; 3-6 the four above; 7-8
# the side bays - the same seats [WeaponSystem1AirToAir] uses.

[WeaponSystem1Malice424]
ReadyUpTime=25
CoolDownTime=55
Station1=sest_aim-424
Station2=sest_aim-424
Station3=yf23_aim260a_internal
Station4=yf23_aim260a_internal
Station5=yf23_aim260a_internal
Station6=yf23_aim260a_internal
Station7=yf23_aim9x2_internal
Station8=yf23_aim9x2_internal

"""

LOADOUT_NAMES = {
    # Identical to the F-35C and RAAF F-35A packs' strings: the key is global,
    # whichever pack wins the merge every MALICE fit reads the same. Comma-free.
    "en": {"Malice424": "SEST Intercept MALICE (2x AIM-424 int)"},
    "cn": {"Malice424": "SEST 马利斯截击 (2x AIM-424 内置)"},
}

INFO_INI = """[Language_en]
Name=SEST YF-23 MALICE
Description=An AIM-424 MALICE loadout for the F-23A Block 40, the 2025 configuration of the YF-23 Black Widow II mod: two internal AIM-424 MALICE very-long-range AAMs (Raytheon's two-stage LRAAM, in excess of 250 nm) on the bottom pair of the main bay, four AIM-260A above them and two AIM-9X Block II in the side bays. The mod's own three loadouts are kept. Built on the mod's Block 40 file, the only one of its six variants that carries the AIM-260A. Requires the YF-23 Black Widow II mod and US Naval Aviation (supplies the model the MALICE borrows as a rendering stand-in). Place ABOVE the YF-23 Black Widow II mod.

[Compatibility]
ApproximateVersion=0.8.2
"""


def main():
    src = UPSTREAM / "aircraft" / f"{AIRCRAFT}.ini"
    if not src.exists():
        sys.exit(f"{src.relative_to(ROOT)} not found - the YF-23 Black Widow II mod "
                 "(3796349767) is not in mods-source; re-run tools/export-mod-configs.ps1")
    # The export copies text configs only, never .obj meshes, so the model's
    # presence is proven by its material ini - the one file of the model set
    # that does reach mods-source.
    if not (USNA / "assets" / "models" / "ammunition" / "agm-88" / "usn_agm-88g_mat.ini").exists():
        sys.exit("US Naval Aviation (3737267013) does not ship the AGM-88G model set - "
                 "the MALICE stand-in has no source")
    text = src.read_text(encoding="utf-8-sig")

    # 1. Extend AvailableLoadouts
    m = re.search(r"^(AvailableLoadouts=)(.+)$", text, re.M)
    if not m:
        sys.exit("AvailableLoadouts line not found - upstream layout changed")
    existing = [k.strip() for k in m.group(2).split(",") if k.strip()]
    clash = [k for k in NEW_KEYS if k in existing]
    if clash:
        sys.exit(f"loadout keys already exist upstream: {clash}")
    text = (text[: m.start(2)] + m.group(2).rstrip() + "," + ",".join(NEW_KEYS)
            + text[m.end(2):])

    # 2. The fit must only use seats the bay declares
    ws1 = re.search(r"^\[WeaponSystem1\]\n(.*?)(?=^\[)", text, re.M | re.S)
    if not ws1:
        sys.exit("[WeaponSystem1] not found - upstream layout changed")
    n = re.search(r"^NumberOfStations=(\d+)", ws1.group(1), re.M)
    if not n:
        sys.exit("[WeaponSystem1] declares no NumberOfStations")
    used = [int(s) for s in re.findall(r"^Station(\d+)=", NEW_SECTIONS, re.M)]
    if max(used) > int(n.group(1)):
        sys.exit(f"the fit uses station {max(used)} but the bay declares {n.group(1)}")

    # 3. Inject the new section before the WeaponMagazines banner
    marker = "[---------- WeaponMagazines ----------]"
    if marker not in text:
        sys.exit("WeaponMagazines marker not found - upstream layout changed")
    text = text.replace(marker, NEW_SECTIONS + marker, 1)

    # 4. Validate ammo references against the ecosystem
    known = {AIM424_ID}  # provided by this pack itself (written below)
    known |= {p.stem for p in (ROOT / "mods-source").rglob("*.ini")
              if p.parent.name == "ammunition"}
    refs = set(re.findall(r"^Station\d+=([^|\s/]+)", NEW_SECTIONS, re.M))
    missing = sorted(r for r in refs if r not in known)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")

    # 5. Sanity: nothing defined twice
    heads = re.findall(r"^\[WeaponSystem1[A-Za-z0-9_.\-]+\]$", text, re.M)
    dupes = sorted({h for h in heads if heads.count(h) > 1})
    if dupes:
        sys.exit(f"duplicate loadout sections: {dupes}")
    keys_final = [k.strip() for k in
                  re.search(r"^AvailableLoadouts=([^#\n]*)", text, re.M).group(1).split(",")]
    if len(keys_final) != len(set(keys_final)):
        sys.exit("duplicate key in AvailableLoadouts")

    # 6. Write the mod folder
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / f"{AIRCRAFT}.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    write_aim424(OUT)
    for lang, names in LOADOUT_NAMES.items():
        # The mod ships no loadout_names.ini in any language, so these are
        # partial files: language_* merges key-by-key, so a file holding only
        # the SEST key adds it without touching the game's stock names.
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        body = ("[LoadoutNames]\n#--------------- SEST YF-23 MALICE ----------------\n"
                + "".join(f"{k}={v}\n" for k, v in names.items()))
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: {len(existing) + len(NEW_KEYS)} loadouts "
          f"({len(existing)} from the mod + {len(NEW_KEYS)} SEST) on {AIRCRAFT}, "
          f"{len(refs)} ammo refs validated, {n.group(1)} bay seats")


if __name__ == "__main__":
    main()
