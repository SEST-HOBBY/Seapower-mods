#!/usr/bin/env python3
"""Build the SEST RAAF Bases pack: five Australian airbases populated with the
collection's relevant aircraft (RAAF F-35A, E-7A, P-8A + F-15EX, E-3G, tankers,
B-2, B-1B, B-52H rotations).

Each base clones the proven Modern US Airbase unit (which itself reuses the
vanilla Reykjavik airbase scenery and flight-deck geometry) and swaps in RAAF
identity and air groups. Aircraft resolve from their own mods — see README for
the dependency list.

Usage (repo root):  python3 integration/raaf-bases/build_pack.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
TEMPLATE = MODS / "3592460366" / "land_units" / "airbase_us.ini"
OUT = Path(__file__).resolve().parent / "SEST_RAAF_Bases"

BASES = {
    "airbase_raaf_williamtown": {
        "name": "RAAF Base Williamtown",
        "desc": "Fighter and AEW&C home base: 3 SQN / 77 SQN F-35A, 2 SQN E-7A Wedgetail",
        "airgroup": [
            ("raaf_f-35a", "Squadron1,12|Squadron2,12"),
            ("E7A_Wedgetail", "Squadron1,3"),
        ],
    },
    "airbase_raaf_tindal": {
        "name": "RAAF Base Tindal",
        "desc": "Northern deterrence base with USAF bomber rotation: 75 SQN F-35A, B-52H, B-2, tankers, MQ-9",
        "airgroup": [
            ("raaf_f-35a", "Squadron3,12"),
            ("dts_b-52h", "Squadron1,4"),
            ("usaf_b-2_spirit", "Squadron1,2"),
            ("usaf_kc-135a", "Squadron1,2"),
            ("usaf_mq-9a", "Squadron1,4"),
        ],
    },
    "airbase_raaf_amberley": {
        "name": "RAAF Base Amberley",
        "desc": "Heavy and tanker hub: F-15EX Eagle II wing, B-1B rotation, KC-46A/KC-10A, E-3G",
        "airgroup": [
            ("usaf_f-15ex_SEII", "Squadron1,12"),
            ("usaf_b-1b_dts", "Squadron1,2"),
            ("usaf_kc-46a_boom", "Squadron1,3"),
            ("usaf_kc-10a_extender", "Squadron1,2"),
            ("usaf_e-3g", "Squadron1,2"),
        ],
    },
    "airbase_raaf_edinburgh": {
        "name": "RAAF Base Edinburgh",
        "desc": "ISR and maritime patrol: No.12 SQN P-8A Poseidon, MQ-9",
        "airgroup": [
            ("usn_p8", "Squadron3,8"),
            ("usaf_mq-9a", "Squadron2,4"),
        ],
    },
    "airbase_raaf_darwin": {
        "name": "RAAF Base Darwin",
        "desc": "Forward operating base: F-35A and F-15EX dets, probe-drogue tanker, P-8A, MH-60R",
        "airgroup": [
            ("raaf_f-35a", "Squadron4,8"),
            ("usaf_f-15ex_SEII", "Squadron2,6"),
            ("usaf_kc-46a_warp", "Squadron1,2"),
            ("usn_p8", "Squadron3,2"),
            ("usn_mh-60r", "Squadron1,4"),
        ],
    },
    "airbase_raaf_east_sale": {
        "name": "RAAF Base East Sale",
        "desc": "Training base: lead-in F-35A det, MQ-9 training flight",
        "airgroup": [
            ("raaf_f-35a", "Squadron1,4"),
            ("usaf_mq-9a", "Squadron3,4"),
        ],
    },
    "airbase_raaf_pearce": {
        "name": "RAAF Base Pearce",
        "desc": "Western Australia training hub: F-35A conversion unit, KC-46A",
        "airgroup": [
            ("raaf_f-35a", "Squadron2,8"),
            ("usaf_kc-46a_boom", "Squadron2,2"),
        ],
    },
    "airbase_raaf_gingin": {
        "name": "RAAF Base Gingin",
        "desc": "Pearce satellite field: F-35A det, SAR helicopters",
        "airgroup": [
            ("raaf_f-35a", "Squadron1,4"),
            ("usn_mh-60r", "Squadron1,2"),
        ],
    },
    "airbase_raaf_richmond": {
        "name": "RAAF Base Richmond",
        "desc": "Air mobility home: Hercules fleet (KC-130T stand-in), SAR helicopters",
        "airgroup": [
            ("usmc_kc-130t", "Squadron1,6"),
            ("usn_mh-60r", "Squadron2,2"),
        ],
    },
    "airbase_raaf_townsville": {
        "name": "RAAF Base Townsville",
        "desc": "Joint army aviation base: AH-64E Apache, MH-60R, S-70B-2, Hercules det",
        "airgroup": [
            ("usa_ah-64e", "Squadron1,8"),
            ("usn_mh-60r", "Squadron1,4"),
            ("S-70B-2_Seahawk", "Squadron1,4"),
            ("usmc_kc-130t", "Squadron2,2"),
        ],
    },
    "airbase_raaf_learmonth": {
        "name": "RAAF Base Learmonth (Bare Base)",
        "desc": "Activated bare base, ISR posture: P-8A det, U-2, KC-135",
        "airgroup": [
            ("usn_p8", "Squadron3,4"),
            ("usaf_u-2", "Squadron1,2"),
            ("usaf_kc-135a", "Squadron2,2"),
        ],
    },
    "airbase_raaf_curtin": {
        "name": "RAAF Base Curtin (Bare Base)",
        "desc": "Activated bare base, fighter posture: F-35A det, drogue tanker",
        "airgroup": [
            ("raaf_f-35a", "Squadron3,8"),
            ("usaf_kc-46a_warp", "Squadron2,2"),
        ],
    },
    "airbase_raaf_scherger": {
        "name": "RAAF Base Scherger (Bare Base)",
        "desc": "Activated bare base, Cape York: F-35A det, F-15EX det, MQ-9 ER",
        "airgroup": [
            ("raaf_f-35a", "Squadron4,8"),
            ("usaf_f-15ex_SEII", "Squadron2,6"),
            ("usaf_mq-9_er", "Squadron1,4"),
        ],
    },
    "airbase_raaf_woomera": {
        "name": "RAAF Woomera Airfield",
        "desc": "Test and evaluation range: U-2, MQ-9 ER, B-2 test det",
        "airgroup": [
            ("usaf_u-2", "Squadron1,2"),
            ("usaf_mq-9_er", "Squadron2,4"),
            ("usaf_b-2_spirit", "Squadron2,2"),
        ],
    },
    "airbase_raaf_butterworth": {
        "name": "RAAF Base Butterworth",
        "desc": "Forward presence, Malaysia: F-35A det, P-8A rotation, KC-135",
        "airgroup": [
            ("raaf_f-35a", "Squadron1,6"),
            ("usn_p8", "Squadron3,3"),
            ("usaf_kc-135a", "Squadron3,2"),
        ],
    },
}

INFO_INI = """[Language_en]
Name=SEST RAAF Bases
Description=Five Australian airbases populated from the mod collection: Williamtown (F-35A, E-7A), Tindal (F-35A, B-52H, B-2, KC-135, MQ-9), Amberley (F-15EX, B-1B, KC-46A, KC-10A, E-3G), Edinburgh (P-8A, MQ-9), Darwin (F-35A, F-15EX, KC-46A, P-8A, MH-60R). Aircraft come from their own mods - see the repo README for the dependency list. Place BELOW the aircraft mods in the Mod Manager.

[Compatibility]
ApproximateVersion=0.8.2
"""

VARIANTS_INI = """[General]
AllVariantsAreOfSameNation=true
NumberOfVariants=1

[Default]
Nation=Australia

[Variant1]
Nation=Australia
"""


def squadron_limit(aircraft_id):
    """Max squadron index defined for an aircraft, searching modded dirs then vanilla."""
    hits = sorted(MODS.glob(f"*/aircraft/{aircraft_id}_squadrons.ini")) + \
        sorted(MODS.glob(f"_vanilla/original/aircraft/{aircraft_id}_squadrons.ini"))
    best = 0
    for h in hits:
        text = h.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"NumberOfSquadrons\s*=\s*(\d+)", text)
        n = int(m.group(1)) if m else 0
        real = len(re.findall(r"^\s*\[Squadron\d+\]", text, re.M))
        best = max(best, n, real)
    return best, len(hits)


def main():
    template = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"\[AirGroup\].*?(?=\[FlightDeck\])", template, re.S)
    if not m:
        sys.exit("AirGroup block not found in template — upstream layout changed")

    # Validate every referenced aircraft and squadron index
    problems, warnings = [], []
    for base_id, base in BASES.items():
        for aircraft_id, assignment in base["airgroup"]:
            exists = list(MODS.glob(f"*/aircraft/{aircraft_id}.ini")) + \
                list(MODS.glob(f"_vanilla/original/aircraft/{aircraft_id}.ini"))
            if not exists:
                problems.append(f"{base_id}: aircraft ini not found for {aircraft_id}")
                continue
            limit, sq_files = squadron_limit(aircraft_id)
            for part in assignment.split("|"):
                sq, _, cnt = part.partition(",")
                if not cnt.isdigit():
                    problems.append(f"{base_id}: malformed assignment {part!r} for {aircraft_id}")
                idx = int(re.sub(r"\D", "", sq) or 0)
                if sq_files and idx > limit:
                    if limit == 0:
                        warnings.append(f"{base_id}: {aircraft_id} squadrons file defines no "
                                        f"[SquadronN] sections (Default only) — verify {sq} "
                                        "falls back to the default livery in-game")
                    else:
                        problems.append(f"{base_id}: {aircraft_id} {sq} exceeds defined "
                                        f"squadrons ({limit})")
    if problems:
        sys.exit("validation failed:\n  " + "\n  ".join(problems))
    for w in warnings:
        print("warning:", w)

    # Emit the five base units
    (OUT / "land_units").mkdir(parents=True, exist_ok=True)
    names = ["﻿[****************************** Australia ******************************]",
             "[ -------------------- Airbases, airfields ----------------]", ""]
    for base_id, base in BASES.items():
        airgroup = "[AirGroup]\n# " + base["desc"] + "\n"
        airgroup += "".join(f"{a}={s}\n" for a, s in base["airgroup"])
        airgroup += "\n\n"
        text = template[: m.start()] + airgroup + template[m.end():]
        text = re.sub(r"^DisplayClassName=.*$", f"DisplayClassName={base['name']}",
                      text, count=1, flags=re.M)
        (OUT / "land_units" / f"{base_id}.ini").write_text(text, encoding="utf-8")
        (OUT / "land_units" / f"{base_id}_variants.ini").write_text(VARIANTS_INI, encoding="utf-8")
        names += [f"[{base_id}]", "Type=Airbase", f"Default={base['name']}",
                  f"Variant1={base['name']},Airbase", ""]

    (OUT / "language_en").mkdir(exist_ok=True)
    (OUT / "language_en" / "land_units_names.ini").write_text("\n".join(names), encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")

    n_aircraft = sum(int(p.split(",")[1]) for b in BASES.values()
                     for _, s in b["airgroup"] for p in s.split("|"))
    print(f"built {OUT.relative_to(ROOT)}: {len(BASES)} bases, {n_aircraft} aircraft total, "
          "all references validated")


if __name__ == "__main__":
    main()
