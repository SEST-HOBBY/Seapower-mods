#!/usr/bin/env python3
"""Build the SEST JMSDF Mogami patch: give the Mogami-class frigate its real
JMSDF air group.

The standalone Mogami mod embarks a USN SH-2F Seasprite; the real FFMs fly the
SH-60 family, and the Euromod JMSDF pack ships jp_sh-60k/jp_sh-60j. This patch
overrides the vessel to embark an SH-60K and accept both JMSDF Seahawks (the
SH-2F stays supported for compatibility).

Usage (repo root):  python3 integration/jmsdf-mogami/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOGAMI = ROOT / "mods-source" / "3456859157"    # Mogami-class frigate
JMSDF = ROOT / "mods-source" / "3695809489"     # Euromod JMSDF (jp_sh-60j/k)
OUT = Path(__file__).resolve().parent / "SEST_JMSDF_Mogami"

INFO_INI = """[Language_en]
Name=SEST JMSDF Mogami
Description=Gives the Mogami-class frigate its real JMSDF air group: embarks an SH-60K and supports both JMSDF Seahawks from the Euromod JMSDF pack (SH-2F kept for compatibility). Requires the Mogami-class Frigate mod and Euromod JMSDF. Place ABOVE the Mogami mod in the Mod Manager.

[Compatibility]
ApproximateVersion=0.8.2
"""


def main():
    src = MOGAMI / "vessels" / "js_ffg_mogami.ini"
    if not src.exists():
        sys.exit("Mogami donor vessel not found — re-export mods-source")
    for helo in ("jp_sh-60k", "jp_sh-60j"):
        if not (JMSDF / "aircraft" / f"{helo}.ini").exists():
            sys.exit(f"JMSDF helo not found: {helo}")

    text = src.read_text(encoding="utf-8", errors="replace")

    text, n = re.subn(r"\[AirGroup\].*?(?=\n\[)", "[AirGroup]\njp_sh-60k=Default,1\n",
                      text, count=1, flags=re.S)
    if n == 0:
        sys.exit("no [AirGroup] block found — upstream layout changed")
    text, n = re.subn(r"^AircraftSupported=.*$",
                      "AircraftSupported=jp_sh-60k,jp_sh-60j,usn_sh-2f",
                      text, count=1, flags=re.M)
    if n == 0:
        sys.exit("no AircraftSupported line found — upstream layout changed")

    (OUT / "vessels").mkdir(parents=True, exist_ok=True)
    (OUT / "vessels" / "js_ffg_mogami.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)}: Mogami now embarks jp_sh-60k, "
          "supports jp_sh-60k/jp_sh-60j/usn_sh-2f")


if __name__ == "__main__":
    main()
