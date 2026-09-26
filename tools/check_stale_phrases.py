#!/usr/bin/env python3
"""Fail on retired claims that must not come back into shipped text.

Some sentences in this repo stopped being true on a known day, and each one
was written into several places at once - a builder's Mod Manager blurb, a
README, a comment block that the builder copies verbatim into every pack that
carries the weapon. Correcting one copy has repeatedly left its siblings
behind. The AIM-424 respec fixed the missile definition and the F-15EX blurb,
and three sibling packs went on calling it an AARGM-ER derivative; the same
respec left the old reasoning in a comment block that was emitted into all
seven copies of sest_aim-424.ini.

Each entry below is a phrase (a case-insensitive regex), the files it must be
absent from, and why it is retired. Both the SOURCE (builders, the shared
definition, pack READMEs) and the OUTPUT (every emitted _info.ini, ammunition
file and language file, the consolidated dist included) are held, so a stale
sentence cannot survive in either.

    python3 tools/check_stale_phrases.py

Exits non-zero on any hit. Standard library only; reads nothing but the tree.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEC = dict(encoding="utf-8", errors="surrogateescape")

# Every place the AIM-424 is described. integration/*/SEST_*/ also matches the
# consolidated integration/dist/SEST_Integration/.
AIM424_SOURCES = [
    "integration/*/build_*.py",
    "integration/common/aim424.py",
    "integration/*/README.md",
]
AIM424_OUTPUT = [
    "integration/*/SEST_*/_info.ini",
    "integration/*/SEST_*/ammunition/sest_aim-424.ini",
    "integration/*/SEST_*/language_en/ammunition_names.ini",
]
AIM424_ROUND = [
    "integration/common/aim424.py",
    "integration/*/SEST_*/ammunition/sest_aim-424.ini",
]

REVEAL = "retired by the U.S. Navy's AIM-424 reveal, 22 Aug 2026"

# (regex, globs, why)
STALE = [
    (r"AARGM-ER airframe", AIM424_SOURCES + AIM424_OUTPUT,
     f"the AIM-424 is a Raytheon LRAAM, not an AARGM-ER derivative ({REVEAL})"),
    (r"AIM-174-class reach", AIM424_SOURCES + AIM424_OUTPUT,
     f"the AIM-424's own figure is 'in excess of 250 nm' ({REVEAL})"),
    (r"has to fit (inside )?an F-35|fit an F-35 weapons bay", AIM424_SOURCES + AIM424_OUTPUT,
     f"bay fit is not why the AIM-424 reaches 290 nm - it fits the bay and "
     f"makes 250+ anyway ({REVEAL})"),
    (r"no AIM-424 mesh exists", AIM424_SOURCES + AIM424_OUTPUT,
     "false: US Naval Aviation ships aim-424.obj (usn_aim-424) and the YF-23 "
     "mod ships yf23_aim424; the AGM-88G stand-in is kept by choice"),
    (r"what-if[^.\n]*(AIM-424|MALICE)", AIM424_SOURCES + AIM424_OUTPUT,
     f"the AIM-424 is a real weapon now ({REVEAL})"),
    (r"dual-pulse|2030s seeker|Mass[^.\n]*NOT disclosed", AIM424_ROUND,
     "pre-reveal guesses: the motor is reported two-stage and the weight is "
     "published (1,500 lb / 680 kg, U.S. Navy fact file)"),
]


def main():
    hits, files = [], set()
    for pattern, globs, why in STALE:
        rx = re.compile(pattern, re.I)
        seen = set()
        for g in globs:
            for path in sorted(ROOT.glob(g)):
                if path in seen or not path.is_file():
                    continue
                seen.add(path)
                files.add(path)
                for n, line in enumerate(path.read_text(**CODEC).splitlines(), 1):
                    m = rx.search(line)
                    if m:
                        hits.append(f"   {path.relative_to(ROOT)}:{n}: '{m.group(0)}' - {why}")

    print(f"checked {len(STALE)} retired phrase(s) across {len(files)} file(s)")
    if hits:
        print(f"\n{len(hits)} retired claim(s) back in shipped text:\n")
        print("\n".join(hits))
        sys.exit(1)
    print("no retired claim appears in any builder, README or emitted file")


if __name__ == "__main__":
    main()
