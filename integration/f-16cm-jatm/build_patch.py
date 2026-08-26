#!/usr/bin/env python3
"""Build the SEST F-16CM JATM patch: AIM-260 and AIM-424 fits for the USAF
F-16CM Block 52 (usaf_f-16cm-bl52d, from Zero Two's F-16C mod).

Two derived loadouts, both on the mod's own proven fits:

  SEST_F16_Intercept260  from AirToAirVLongRange: every AIM-120D becomes an
                         AIM-260. The JATM is built to the AMRAAM footprint,
                         so each round keeps the donor's aim-120d seat key.
  SEST_F16_MALICE        from SEAD: the two AGM-88 HARMs become AIM-424
                         MALICE - the 424 rides the AGM-88G AARGM-ER airframe,
                         so these are literally its stations - and the two
                         AMRAAMs become AIM-260. Sniper pod, HTS pod and all
                         three tanks stay.

Only the USAF CM airframe is touched; the HAF/POL/TUAF/IAF F-16s keep their
stock loadouts.

Usage (repo root):  python3 integration/f-16cm-jatm/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
F16_MOD = ROOT / "mods-source" / "3758320372"      # F-16C Fighting Falcon (Zero Two)
WEAPON_PACK = ROOT / "mods-source" / "3760871384"  # Dingtools (dts_aim-260)
OUT = Path(__file__).resolve().parent / "SEST_F16CM_JATM"
AIRFRAME = "usaf_f-16cm-bl52d"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402

NEW_KEYS = ["SEST_F16_Intercept260", "SEST_F16_MALICE"]

# (new name, donor loadout, [(old store spec, new store spec), ...])
# Store specs are matched whole, pipe seat keys included, so a swap keeps or
# changes the seat deliberately, never by accident.
DERIVATIONS = [
    ("SEST_F16_Intercept260", "AirToAirVLongRange",
     [("usaf_aim-120d|aim-120d-34", "dts_aim-260|aim-120d-34"),
      ("usaf_aim-120d|aim-120d-56", "dts_aim-260|aim-120d-56")]),
    ("SEST_F16_MALICE", "SEAD",
     [("usn_agm-88", AIM424_ID),
      ("usaf_aim-120d|aim-120d-34", "dts_aim-260|aim-120d-34")]),
]

LOADOUT_NAMES = {
    # Comma-free: commas are field separators in language files.
    "en": {
        "SEST_F16_Intercept260": "SEST Intercept (4x AIM-260)",
        "SEST_F16_MALICE": "SEST MALICE (2x AIM-424 + AIM-260)",
    },
}

INFO_INI = """[Language_en]
Name=SEST F-16CM JATM
Description=AIM-260 JATM and AIM-424 MALICE fits for the USAF F-16CM Block 52: a very-long-range intercept with four AIM-260 on the AMRAAM stations, and a MALICE fit with two AIM-424 on the HARM stations (the 424 rides the AGM-88G AARGM-ER airframe - these are its real pylons) plus AIM-260 self-escort, keeping the Sniper and HTS pods. Requires the F-16C Fighting Falcon mod and the Dingtools Weapon Pack; US Naval Aviation provides the AGM-88G model the MALICE uses. Deploys inside the SEST Integration Pack.

[Compatibility]
ApproximateVersion=0.8.2
"""


def derive(text, name, donor, swaps):
    m = re.search(rf"^\[WeaponSystem1{donor}\][^\n]*\n(.*?)(?=^\[)", text, re.M | re.S)
    if not m:
        sys.exit(f"{AIRFRAME}: donor loadout {donor} not found - upstream changed")
    body = m.group(1)
    for old, new in swaps:
        n = len(re.findall(rf"^Station\d+={re.escape(old)}\s*$", body, re.M))
        if n == 0:
            sys.exit(f"{AIRFRAME}/{donor}: no stations carry {old} - upstream changed")
        body = re.sub(rf"^(Station\d+=){re.escape(old)}(\s*)$", rf"\g<1>{new}\g<2>",
                      body, flags=re.M)
    return f"[WeaponSystem1{name}]\n" + body.rstrip("\n") + "\n\n"


def main():
    for mod, need in ((WEAPON_PACK, "ammunition/dts_aim-260.ini"),
                      (F16_MOD, f"aircraft/{AIRFRAME}.ini")):
        if not (mod / need).exists():
            sys.exit(f"missing {mod.name}/{need} - re-export mods-source")

    text = F16_MOD.joinpath("aircraft", f"{AIRFRAME}.ini").read_text(
        encoding="utf-8-sig", errors="replace")

    la = re.search(r"^(AvailableLoadouts=)(.+)$", text, re.M)
    if not la:
        sys.exit(f"{AIRFRAME}: AvailableLoadouts not found")
    if any(k in la.group(2) for k in NEW_KEYS):
        sys.exit(f"{AIRFRAME}: SEST keys already declared upstream")
    text = text[:la.end(2)] + "," + ",".join(NEW_KEYS) + text[la.end(2):]

    blocks = "".join(derive(text, *d) for d in DERIVATIONS)
    marker = "[---------- WeaponMagazines ----------]"
    if marker not in text:
        sys.exit(f"{AIRFRAME}: WeaponMagazines marker missing - upstream changed")
    text = text.replace(marker, blocks + marker, 1)

    # every store the new fits hang must exist somewhere in the ecosystem
    known = {AIM424_ID} | {p.stem for p in (ROOT / "mods-source").rglob("*.ini")
                           if p.parent.name == "ammunition"}
    refs = {s.split("|")[0] for s in re.findall(r"^Station\d+=([A-Za-z]\S*)", blocks, re.M)}
    missing = sorted(refs - known)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")

    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / f"{AIRFRAME}.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    write_aim424(OUT)
    for lang, names in LOADOUT_NAMES.items():
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        body = "[LoadoutNames]\n\n# ---------- SEST F-16CM JATM ----------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: {AIRFRAME} +{len(NEW_KEYS)} loadouts, "
          f"{len(refs)} store refs validated")


if __name__ == "__main__":
    main()
