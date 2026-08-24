#!/usr/bin/env python3
"""Build the SEST RAAF Wedgetail patch: real squadrons for the E-7A.

The E-7A Wedgetail mod (3499239964) ships only a [Default] squadron; its
[Squadron1] block is commented out and points at placeholder civ_707 art.
Anything asking for SquadronReference=Squadron1 therefore fails to resolve.

This patch defines the aircraft's real operators as squadrons. The mod
carries no alternative livery textures - its skin is baked into per-part
material files - so these squadrons differ by NATION (which drives the flag,
IFF and nation sorting) and identity rather than by paint. Overriding
ResourcesLiveryFolder here would point the Wedgetail at another aircraft's
texture, which is why it is deliberately left alone.

Usage (repo root):  python3 integration/raaf-wedgetail/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3499239964"          # E-7A Wedgetail
OUT = Path(__file__).resolve().parent / "SEST_RAAF_Wedgetail"

# The real Wedgetail/AEW&C operators. Squadron1 is No. 2 Squadron RAAF, the
# type's launch and primary operator, so existing missions that already ask
# for Squadron1 get the correct Australian aircraft.
SQUADRONS = [
    ("No. 2 Squadron RAAF - Williamtown", "Australia"),
    ("No. 42 Wing RAAF - Williamtown", "Australia"),
    ("No. 8 Squadron RAF - Lossiemouth", "UK"),
    ("Turkish Air Force 131 Filo - Konya", "Turkey"),
    ("ROKAF 51st Air Control Group - Gimhae", "South_Korea"),
]

SQUADRONS_INI = """\
# SEST RAAF Wedgetail - squadron definitions for the E-7A.
# Upstream ships [Default] only, so SquadronReference=Squadron1 does not
# resolve. These add the type's real operators. The mod has no per-squadron
# livery textures, so they differ by nation rather than by paint.
[General]
SerialnumberReferences=
EmblemReference=Emblem
NationFlagReference=Flag1
AllVariantsAreOfSameNation=False
NumberOfSquadrons={count}

[Default]
Nation=Australia

{blocks}"""


def main():
    src = UPSTREAM / "aircraft" / "E7A_Wedgetail_squadrons.ini"
    if not src.exists():
        sys.exit(f"upstream squadrons file missing: {src}")
    upstream = src.read_text(encoding="utf-8", errors="replace")

    live = re.findall(r"^\[(Squadron\d+)\]", upstream, re.M)
    if live:
        sys.exit(f"upstream now defines {live} — rebase this patch before shipping")

    blocks = "".join(
        f"[Squadron{i}]  {label}\nNation={nation}\n\n"
        for i, (label, nation) in enumerate(SQUADRONS, start=1)
    )
    body = SQUADRONS_INI.format(count=len(SQUADRONS), blocks=blocks).rstrip("\n") + "\n"

    # Every nation must be one the game knows, or the aircraft sorts oddly.
    known = set(re.findall(r"^([A-Za-z][\w \-']*)=",
                           (ROOT / "mods-source" / "_vanilla" / "original" /
                            "language_en" / "nations.ini").read_text(
                               encoding="utf-8", errors="replace"), re.M))
    used = {n for _, n in SQUADRONS}
    unknown = sorted(u for u in used if u not in known)
    if unknown:
        sys.exit(f"nations not recognised by the game: {unknown}")

    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "E7A_Wedgetail_squadrons.ini").write_text(body, encoding="utf-8")
    (OUT / "_info.ini").write_text(
        "[Language_en]\n"
        "Name=SEST RAAF Wedgetail\n"
        "Description=Defines the E-7A Wedgetail's real operating squadrons "
        "(No. 2 Squadron and No. 42 Wing RAAF, No. 8 Squadron RAF, Turkish 131 Filo "
        "and the ROKAF 51st Air Control Group). Upstream ships a Default squadron only, "
        "so any mission asking for SquadronReference=Squadron1 fails to resolve. "
        "Squadrons differ by nation rather than livery because the mod carries no "
        "alternative skin textures. Requires the E-7A Wedgetail mod and must sit ABOVE it.\n\n"
        "[Compatibility]\nApproximateVersion=0.8.2\n", encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: {len(SQUADRONS)} squadrons "
          f"({', '.join(sorted(used))}), nations validated")


if __name__ == "__main__":
    main()
