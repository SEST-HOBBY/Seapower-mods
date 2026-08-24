#!/usr/bin/env python3
"""Build the SEST Raptor Squadrons patch: real squadrons for the F-22.

The F-22 mod (3418252667) declares NumberOfSquadrons=7 in all three of its
squadron files but only ever defines [Squadron1] - and names it "F-22A" in
the language file, so every Raptor in the game is an anonymous "F-22A" no
matter which squadron a mission asks for. References to Squadron2..7 do not
resolve at all, which is why fix_squadron_refs.py had to rewrite them.

This patch fills in all seven with the type's real operating squadrons and
gives each one a proper name and callsign in the UI.

NO NEW PAINT. The mod's model has no Modex/serial/emblem submodels (the
"#---------- Modex ----------" block in usaf_f-22_s6.ini is empty) and ships
a single f-22_mat.ini texture set, so squadrons differ by identity, nation
flag and callsign rather than by livery. Pointing ResourcesLiveryFolder at
another aircraft's textures would just break the skin, so it is left alone.

The squadron names and basings are the real ones. The callsigns are flavour
derived from each unit's nickname, not documented radio callsigns.

Usage (repo root):  python3 integration/raptor-squadrons/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3418252667"          # F-22 by misaka
OUT = Path(__file__).resolve().parent / "SEST_Raptor_Squadrons"

# Upstream promises seven squadrons, so seven is what we define - existing
# missions asking for any index in range now resolve.
# (display name, basing note for the ini comment, flavour callsign)
SQUADRONS = [
    ("27th FS 'Fighting Eagles'", "1st Fighter Wing, JB Langley-Eustis, Virginia", "Talon"),
    ("94th FS 'Hat in the Ring'", "1st Fighter Wing, JB Langley-Eustis, Virginia", "Ringer"),
    ("90th FS 'Pair O Dice'", "3rd Wing, JB Elmendorf-Richardson, Alaska", "Dice"),
    ("525th FS 'Bulldogs'", "3rd Wing, JB Elmendorf-Richardson, Alaska", "Bulldog"),
    ("199th FS 'Mytai Fighters'", "154th Wing HI ANG, JB Pearl Harbor-Hickam", "Mytai"),
    ("19th FS 'Gamecocks'", "15th Wing, JB Pearl Harbor-Hickam, Hawaii", "Gamecock"),
    ("43rd FS 'Hornets'", "325th Fighter Wing (training unit), Eglin AFB", "Stinger"),
]

# The three Raptor ids the mod ships, all with the same squadron problem.
AIRCRAFT_IDS = ["usaf_f-22", "usaf_f-22_s5", "usaf_f-22_s6"]

# Generic type callsign kept first so the existing "Raptor" flavour survives.
TYPE_CALLSIGN = {"en": "Raptor", "cn": "猛禽"}

SQUADRONS_HEADER = """\
# SEST Raptor Squadrons - squadron definitions for {aircraft_id}.
# Upstream declares NumberOfSquadrons=7 but defines [Squadron1] only, so
# SquadronReference=Squadron2..7 does not resolve. These are the F-22's real
# operating squadrons. The mod has no per-squadron livery textures and its
# model carries no serial/emblem decal submodels, so they differ by identity
# and callsign rather than by paint.
[General]
SerialnumberReferences=AF_Serial
EmblemReference=Emblem
NationFlagReference=Flag1
NumberOfSquadrons={count}

[Default]
Nation=US

"""

INFO_INI = """[Language_en]
Name=SEST Raptor Squadrons
Description=Gives the F-22 its real squadrons. The F-22 mod promises seven squadrons but defines only one, and names it "F-22A" - so every Raptor is anonymous and any mission referencing Squadron2 through Squadron7 fails to resolve. This defines all seven (27th and 94th FS at Langley, 90th and 525th FS at Elmendorf, 199th and 19th FS at Hickam, 43rd FS at Eglin) with proper names and callsigns, for all three Raptor variants the mod ships. Squadrons differ by identity and callsign, not by paint - the mod carries no alternative skins and its model has no decal submodels. Requires the F-22 mod and must sit ABOVE it.

[Compatibility]
ApproximateVersion=0.8.2
"""


def check_upstream(text, path):
    """Refuse to ship if upstream has started defining its own squadrons."""
    live = re.findall(r"^\[Squadron(\d+)\]", text, re.M)
    if [int(i) for i in live] != [1]:
        sys.exit(f"{path.name} now defines squadrons {live} — rebase this patch")
    declared = re.search(r"^NumberOfSquadrons=(\d+)", text, re.M)
    if not declared:
        sys.exit(f"{path.name} has no NumberOfSquadrons — upstream layout changed")
    if int(declared.group(1)) != len(SQUADRONS):
        print(f"note: {path.name} declares {declared.group(1)} squadrons, "
              f"this patch defines {len(SQUADRONS)}")


def rename_squadrons(text, lang):
    """Rewrite the Squadron*/Callsigns lines of every F-22 section in a
    language file, keeping every other line (descriptions included) intact."""
    word = TYPE_CALLSIGN[lang]
    touched = []

    def fix_section(m):
        aircraft_id, body = m.group(1), m.group(2)
        if aircraft_id not in AIRCRAFT_IDS:
            return m.group(0)
        default = re.search(r"^Default=([^,\n]+),([^,\n]*)$", body, re.M)
        if not default:
            sys.exit(f"[{aircraft_id}] has no parsable Default= line")
        long_name, short_name = default.group(1).strip(), default.group(2).strip()
        lines = [f"Squadron{i}={long_name} {name},{short_name}"
                 for i, (name, _, _) in enumerate(SQUADRONS, start=1)]
        lines.append("Callsigns=" + "|".join(
            f"Squadron{i},{word},{call}"
            for i, (_, _, call) in enumerate(SQUADRONS, start=1)))
        # Drop upstream's placeholder squadron/callsign lines, keep the rest.
        kept = [l for l in body.splitlines()
                if not re.match(r"^(Squadron\d+|Callsigns)=", l)]
        while kept and not kept[-1].strip():
            kept.pop()
        touched.append(aircraft_id)
        return f"[{aircraft_id}]\n" + "\n".join(kept + lines) + "\n\n"

    out = re.sub(r"^\[([a-z0-9_\-]+)\]\n(.*?)(?=^\[|\Z)", fix_section, text,
                 flags=re.S | re.M)
    missing = [a for a in AIRCRAFT_IDS if a not in touched]
    if missing:
        sys.exit(f"language_{lang}/aircraft_names.ini has no section for {missing}")
    return out


def main():
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)

    blocks = "".join(
        f"[Squadron{i}]  #{name} - {basing}\nNation=US\n\n"
        for i, (name, basing, _) in enumerate(SQUADRONS, start=1))

    for aircraft_id in AIRCRAFT_IDS:
        src = UPSTREAM / "aircraft" / f"{aircraft_id}_squadrons.ini"
        if not src.exists():
            sys.exit(f"upstream squadrons file missing: {src}")
        check_upstream(src.read_text(encoding="utf-8", errors="replace"), src)
        body = SQUADRONS_HEADER.format(aircraft_id=aircraft_id,
                                       count=len(SQUADRONS)) + blocks
        (OUT / "aircraft" / f"{aircraft_id}_squadrons.ini").write_text(
            body.rstrip("\n") + "\n", encoding="utf-8")

    for lang in ("en", "cn"):
        src = UPSTREAM / f"language_{lang}" / "aircraft_names.ini"
        if not src.exists():
            sys.exit(f"upstream language file missing: {src}")
        text = src.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        out = rename_squadrons(text, lang)
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "aircraft_names.ini").write_text(out.rstrip("\n") + "\n", encoding="utf-8")
        # The descriptions are the bulk of the file; losing them means the
        # section rewrite ate something it should not have.
        if out.count("DefaultDescription=") != text.count("DefaultDescription="):
            sys.exit(f"language_{lang}: descriptions lost during rewrite")

    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")

    written = sorted(p.name for p in (OUT / "aircraft").iterdir())
    print(f"built {OUT.relative_to(ROOT)}: {len(SQUADRONS)} squadrons x "
          f"{len(AIRCRAFT_IDS)} Raptor variants ({', '.join(written)}), "
          "names and callsigns written for en + cn")


if __name__ == "__main__":
    main()
