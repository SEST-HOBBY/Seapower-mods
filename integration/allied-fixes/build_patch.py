#!/usr/bin/env python3
"""Build the SEST Allied Fixes patch: the P-8 Poseidon's anti-ship loadout.

usn_p8_2027 declares AvailableLoadouts=ASW,AntiShip - two options - and the
AntiShip one hangs four rounds of usn_agm-84g on WeaponSystem2. Nothing in the
collection defines usn_agm-84g. Not U.S. Navy 2027, which ships the aircraft;
not any of the other 128 mods; not vanilla. There is no real AGM-84G either.
So the Poseidon's only anti-ship fit puts nothing on the wings, and half of
what a maritime patrol aircraft is for quietly does not work.

It is a typo, and the mod answers it itself: U.S. Navy 2027 writes usn_agm-84n
nineteen times and usn_agm-84g four times, and all four are these station
lines. usn_agm-84n is its own Harpoon Block II+ ER - 522 kg, 150 nm - already
carried by its ships and its Super Hornets.

usn_p8 from mod 3602046770 has the identical four-line typo and the identical
ASW,AntiShip pair, so it gets the same substitution.

Not included, having checked each one:
  - usn_e-2d, fr_e2c, fr_e2d, usn_ch-46d, usaf_ac-130a_83, jmsdf_kv_107*
    all declare a loadout with no matching block, but every one of them is an
    unarmed aircraft whose blocks carry zero stores. The picker entry is
    cosmetic and an override would add a dependency for no gameplay change.
  - usn_p-3d is missing only its Recon block; ASW, AntiShip and Empty all
    work, and nothing fields it.
  - rn_merlin_hm1 and the two Lynxes look like they reference undefined
    DateBased_* stores. They do not - DateBased_ is a vanilla mechanic, used
    by stock submarines like usn_ssn_permit.

Usage (repo root):  python3 integration/allied-fixes/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "SEST_Allied_Fixes"

MISSING = "usn_agm-84g"      # defined by nothing, anywhere
REPLACE = "usn_agm-84n"      # U.S. Navy 2027's own Harpoon Block II+ ER

# (workshop id, aircraft file)
TARGETS = [
    ("3606774881", "usn_p8_2027.ini"),   # U.S. Navy 2027 - fielded in NFIII FINAL
    ("3602046770", "usn_p8.ini"),        # same typo, same fix
]

INFO_INI = """\
[Language_en]
Name=SEST Allied Fixes
Description=Small allied corrections: the P-8's anti-ship fit pointed at a \
Harpoon no mod defines (loaded empty), and HMS Ocean could not operate the \
Apache AH1 her sister hulls already support.
"""


def main():
    if not (ROOT / "mods-source" / "3606774881" / "ammunition" / f"{REPLACE}.ini").exists():
        sys.exit(f"{REPLACE} not found - U.S. Navy 2027 must be exported first")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print("SEST_Allied_Fixes")

    built = 0
    for mod, name in TARGETS:
        src = ROOT / "mods-source" / mod / "aircraft" / name
        dst = OUT / "aircraft" / name
        if not src.exists():
            if dst.exists():
                dst.unlink()
                print(f"    removed stale aircraft/{name} (upstream no longer exported)")
            print(f"  {name}  SKIPPED - {mod} not exported")
            continue
        text = src.read_text(encoding="utf-8")
        n = len(re.findall(rf"^Station\d+={re.escape(MISSING)}\s*$", text, re.M))
        if not n:
            sys.exit(f"{name}: no {MISSING} station lines left - upstream fixed it, "
                     f"drop this target")
        out = re.sub(rf"^(Station\d+=){re.escape(MISSING)}(\s*)$", rf"\g<1>{REPLACE}\g<2>",
                     text, flags=re.M)
        if MISSING in out:
            sys.exit(f"{name}: {MISSING} still present after substitution")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out, encoding="utf-8")
        print(f"  aircraft/{name}  ({n}x {MISSING} -> {REPLACE})")
        built += 1

    # HMS Ocean vs the Apache: her own sister hulls in the same mod
    # (rn_lph_ocean_asw_00 and _asw_13) already list uk_ah_mk_1 - the British
    # Army Apache AH1 that really flew from Ocean off Libya in 2011 - but the
    # base rn_lph_ocean only ever got the Lynx. One appended id fixes it.
    src = ROOT / "mods-source" / "3599752717" / "vessels" / "rn_lph_ocean.ini"
    dst = OUT / "vessels" / "rn_lph_ocean.ini"
    if not src.exists():
        if dst.exists():
            dst.unlink()
            print("    removed stale vessels/rn_lph_ocean.ini (upstream gone)")
        print("  rn_lph_ocean.ini  SKIPPED - Modern British Navy not exported")
    else:
        text = src.read_text(encoding="utf-8")
        if "uk_ah_mk_1" in text:
            sys.exit("rn_lph_ocean.ini: upstream now supports the Apache - drop this fix")
        text, n = re.subn(r"^AircraftSupported=raac_lynx_ah7\s*$",
                          "AircraftSupported=raac_lynx_ah7,uk_ah_mk_1",
                          text, flags=re.M)
        if n != 1:
            sys.exit(f"rn_lph_ocean.ini: AircraftSupported line changed upstream ({n} matches)")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        print("  vessels/rn_lph_ocean.ini  (+uk_ah_mk_1 Apache AH1 supported)")
        built += 1

    if not built:
        sys.exit("nothing built - no target mod is exported")


if __name__ == "__main__":
    main()
