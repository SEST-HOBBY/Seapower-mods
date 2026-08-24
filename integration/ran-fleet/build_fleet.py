#!/usr/bin/env python3
"""Build the SEST RAN Fleet: Royal Australian Navy vessels cloned from their
real European design donors in the Euromod packs.

The RAN sails European designs, so the clones are honest: Hobart-class = the
Spanish F-100 (ae_ffg_alvaro_bazan), Canberra-class LHD = Juan Carlos I,
Collins stand-in = S-80, Anzac stand-in = Type 23 MLU, plus Galicia (Choules),
Teide (Supply) and Meteoro (Arafura) stand-ins. Each clone gets Australian
nation/flag, real HMAS hull names, transparent hull numbers (no Spanish
pennants), and MH-60R / S-70B-2 air groups.

Clones are NEW unit ids — nothing overrides the donors, so both fleets coexist.

Usage (repo root):  python3 integration/ran-fleet/build_fleet.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
OUT = Path(__file__).resolve().parent / "SEST_RAN_Fleet"

SPA_MODERN = "3731208477"   # Spanish Navy Mod (Modern)
SPA_COLDWAR = "3630495619"  # Spanish Navy Mod (Cold War)
RN_MODERN = "3599752717"    # Modern British Navy - Euromod

HELOS = "usn_mh-60r,S-70B-2_Seahawk"

FLEET = {
    "ran_ddg_hobart": {
        "donor": (SPA_MODERN, "ae_ffg_alvaro_bazan"),
        "class_name": "Hobart-class DDG",
        "type_line": "DDG,Destroyer",
        "short": "Hobart",
        "desc": ("Royal Australian Navy air warfare destroyer, built to the Spanish F-100 "
                 "Alvaro de Bazan design with Aegis and SPY-1D(V).\\n\\nEmbarks an MH-60R. "
                 "Home port Fleet Base East, Sydney."),
        "service": "2017|2055",
        "hulls": [("DDG 39 HMAS Hobart", "Hobart"),
                  ("DDG 41 HMAS Brisbane", "Brisbane"),
                  ("DDG 42 HMAS Sydney", "Sydney")],
        "airgroup": ["usn_mh-60r=Squadron1,1"],
    },
    "ran_ffh_anzac": {
        "donor": (RN_MODERN, "rn_ff_type23_mlu"),
        "class_name": "Anzac-class FFH (stand-in)",
        "type_line": "FFH,Frigate",
        "short": "Anzac",
        "desc": ("Royal Australian Navy long-range ASW/patrol frigate. Stand-in hull: the "
                 "Type 23 MLU stands in for the MEKO 200 Anzac (no MEKO in the collection) — "
                 "comparable size, towed array, point-defence SAM and a single helicopter."),
        "service": "1996|2045",
        "hulls": [("FFH 150 HMAS Anzac", "Anzac"),
                  ("FFH 151 HMAS Arunta", "Arunta"),
                  ("FFH 152 HMAS Warramunga", "Warramunga"),
                  ("FFH 153 HMAS Stuart", "Stuart"),
                  ("FFH 154 HMAS Parramatta", "Parramatta"),
                  ("FFH 155 HMAS Ballarat", "Ballarat"),
                  ("FFH 156 HMAS Toowoomba", "Toowoomba"),
                  ("FFH 157 HMAS Perth", "Perth")],
        "airgroup": ["usn_mh-60r=Squadron1,1"],
    },
    "ran_lhd_canberra": {
        "donor": (SPA_MODERN, "ae_lhd_juan_carlos"),
        "class_name": "Canberra-class LHD",
        "type_line": "LHD,Amphibious",
        "short": "Canberra",
        "desc": ("Royal Australian Navy landing helicopter dock, built to the Spanish Juan "
                 "Carlos I design. The RAN operates no fixed-wing aviation from them — the "
                 "air group is MH-60R and S-70B-2 Seahawks.\\n\\nHome port Fleet Base East."),
        "service": "2014|2060",
        "hulls": [("L02 HMAS Canberra", "Canberra"),
                  ("L01 HMAS Adelaide", "Adelaide")],
        "airgroup": ["usn_mh-60r=Squadron1,4", "S-70B-2_Seahawk=Squadron1,4"],
    },
    "ran_lsd_choules": {
        "donor": (SPA_MODERN, "ae_lpd_galicia"),
        "class_name": "HMAS Choules LSD (stand-in)",
        "type_line": "LSD,Amphibious",
        "short": "Choules",
        "desc": ("Royal Australian Navy dock landing ship. Stand-in hull: the Galicia-class "
                 "LPD stands in for the Bay-class."),
        "service": "2011|2050",
        "hulls": [("L100 HMAS Choules", "Choules")],
        "airgroup": ["usn_mh-60r=Squadron1,2"],
    },
    "ran_aor_supply": {
        "donor": (SPA_COLDWAR, "ae_ao_teide"),
        "class_name": "Supply-class AOR (stand-in)",
        "type_line": "AOR,Replenishment",
        "short": "Supply",
        "desc": ("Royal Australian Navy fleet replenishment ship. Stand-in hull: the Teide-"
                 "class oiler stands in for the Cantabria-derived Supply-class (no Cantabria "
                 "in the collection)."),
        "service": "2021|2060",
        "hulls": [("A195 HMAS Supply", "Supply"),
                  ("A304 HMAS Stalwart", "Stalwart")],
        "airgroup": None,
    },
    "ran_ssg_collins": {
        "donor": (SPA_MODERN, "ae_ssk_s80"),
        "class_name": "Collins-class SSG (stand-in)",
        "type_line": "SSG,Submarine",
        "short": "Collins",
        "desc": ("Royal Australian Navy long-range diesel-electric attack submarine. "
                 "Stand-in hull: the S-80 Plus family stands in for the Collins — a large, "
                 "modern conventional boat of comparable role."),
        "service": "1996|2040",
        "hulls": [("SSG 73 HMAS Collins", "Collins"),
                  ("SSG 74 HMAS Farncomb", "Farncomb"),
                  ("SSG 75 HMAS Waller", "Waller"),
                  ("SSG 76 HMAS Dechaineux", "Dechaineux"),
                  ("SSG 77 HMAS Sheean", "Sheean"),
                  ("SSG 78 HMAS Rankin", "Rankin")],
        "airgroup": None,
    },
    "ran_opv_arafura": {
        "donor": (SPA_MODERN, "ae_opv_meteoro"),
        "class_name": "Arafura-class OPV (stand-in)",
        "type_line": "OPV,Patrol",
        "short": "Arafura",
        "desc": ("Royal Australian Navy offshore patrol vessel. Stand-in hull: the "
                 "Meteoro-class BAM stands in for the Arafura (Luerssen OPV 80)."),
        "service": "2022|2060",
        "hulls": [("OPV 203 HMAS Arafura", "Arafura"),
                  ("OPV 204 HMAS Eyre", "Eyre"),
                  ("OPV 205 HMAS Pilbara", "Pilbara"),
                  ("OPV 206 HMAS Gippsland", "Gippsland")],
        "airgroup": None,
    },
}

INFO_INI = """[Language_en]
Name=SEST RAN Fleet
Description=Royal Australian Navy fleet cloned from its real European design donors: Hobart-class DDG (F-100), Canberra-class LHD (Juan Carlos I), Anzac stand-in (Type 23 MLU), Collins stand-in (S-80), HMAS Choules (Galicia), Supply-class (Teide), Arafura OPV (Meteoro). New unit ids - donors are untouched. Requires Euromod Main, the Modern + Cold War Spanish Navy packs, Modern British Navy, and an MH-60R / S-70B-2 source. Place below the Euromod packs.

[Compatibility]
ApproximateVersion=0.8.2
"""

DEFAULT_VARIANT = """ResourcesHullnumberFolder=textures/Misc/
HullnumberTexture=transparent
ResourcesFlagFolder=ships/materials/textures/
FlagTexture=flag_australia
Nation=Australia
"""


def main():
    problems = []
    for ship_id, ship in FLEET.items():
        mod, donor = ship["donor"]
        for suffix in (".ini", "_variants.ini"):
            if not (MODS / mod / "vessels" / f"{donor}{suffix}").exists():
                problems.append(f"{ship_id}: donor file missing: {mod}/vessels/{donor}{suffix}")
    for helo in HELOS.split(","):
        if not list(MODS.glob(f"*/aircraft/{helo}.ini")):
            problems.append(f"helo not found in any mod: {helo}")
    if problems:
        sys.exit("validation failed:\n  " + "\n  ".join(problems))

    (OUT / "vessels").mkdir(parents=True, exist_ok=True)
    (OUT / "language_en").mkdir(exist_ok=True)
    names = ["﻿[****************************** Australia — SEST RAN Fleet ******************************]", ""]

    for ship_id, ship in FLEET.items():
        mod, donor = ship["donor"]
        text = (MODS / mod / "vessels" / f"{donor}.ini").read_text(encoding="utf-8", errors="replace")

        text, n = re.subn(r"^DisplayClassName=.*$", f"DisplayClassName={ship['class_name']}",
                          text, count=1, flags=re.M)
        if n == 0:
            print(f"note: {donor} has no DisplayClassName line; relying on language names")

        if ship["airgroup"]:
            new_ag = "[AirGroup]\n" + "\n".join(ship["airgroup"]) + "\n\n"
            text, n = re.subn(r"\[AirGroup\].*?(?=\n\[)", new_ag.rstrip("\n") + "\n", text,
                              count=1, flags=re.S)
            if n == 0:
                sys.exit(f"{ship_id}: donor {donor} has no [AirGroup] block to replace")
            text, n = re.subn(r"^(AircraftSupported=.*)$", rf"\1,{HELOS}", text,
                              count=1, flags=re.M)
            if n == 0:
                sys.exit(f"{ship_id}: donor {donor} has no AircraftSupported line")

        (OUT / "vessels" / f"{ship_id}.ini").write_text(text, encoding="utf-8")

        # Variants: keep the donor's [General] block (texture/reference wiring must
        # match the donor mesh), then emit Australian variants with clean hull numbers.
        vtext = (MODS / mod / "vessels" / f"{donor}_variants.ini").read_text(encoding="utf-8",
                                                                             errors="replace")
        g = re.search(r"\[General\].*?(?=\[Default\])", vtext, re.S)
        if not g:
            sys.exit(f"{ship_id}: [General] block not found in donor variants")
        general = re.sub(r"^NumberOfVariants=.*$", f"NumberOfVariants={len(ship['hulls'])}",
                         g.group(0).rstrip() + "\n", flags=re.M)
        parts = [general, "", "[Default]", DEFAULT_VARIANT.rstrip()]
        for i in range(1, len(ship["hulls"]) + 1):
            parts += ["", f"[Variant{i}]", DEFAULT_VARIANT.rstrip(),
                      f"ServiceDate={ship['service']}"]
        (OUT / "vessels" / f"{ship_id}_variants.ini").write_text("\n".join(parts) + "\n",
                                                                 encoding="utf-8")

        names += [f"[{ship_id}]", f"Type={ship['type_line']}",
                  f"Default={ship['class_name']},{ship['short']}",
                  f"DefaultDescription={ship['desc']}"]
        names += [f"Variant{i}={full},{shrt}"
                  for i, (full, shrt) in enumerate(ship["hulls"], start=1)]
        names.append("")

    (OUT / "language_en" / "vessel_names.ini").write_text("\n".join(names), encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")

    n_hulls = sum(len(s["hulls"]) for s in FLEET.values())
    print(f"built {OUT.relative_to(ROOT)}: {len(FLEET)} classes, {n_hulls} named hulls, "
          "all donors and helos validated")


if __name__ == "__main__":
    main()
