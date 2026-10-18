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

# SEST Collection Fixes' #!extend stubs over the collection's other AIM-424s
# (build_aim424 in integration/collection-fixes/build_patch.py), and the docs
# that tell a player which AIM-424 flies how. The decision log,
# docs/conflicts-and-load-order.md, keeps the dated record of each retired
# decision, so the patterns below match the claims as present-tense
# statements only; the log words its history so that it does not.
AIM424_STUBS = ["integration/*/SEST_*/ammunition_overwrite/*.ini"]
AIM424_DOCS = [
    "README.md",
    "docs/FEATURES.md",
    "docs/conflicts-and-load-order.md",
    "data/mod-catalog.json",
    "docs/mod-catalog.md",
]
ONE_AIM424 = ("retired by the player's decision of 14 Oct 2026: every AIM-424 in the "
              "collection flies SEST's own flight model on SEST's model block "
              "(build_aim424 in integration/collection-fixes/build_patch.py)")
# A fourth element WRAPPED also matches a phrase that a Markdown paragraph
# breaks over two lines. Both claims below were first written that way.
WRAPPED = "wrapped"

# (regex, globs, why[, WRAPPED])
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
    (r"U\.S\. Navy 2027'?s flight model for every AIM-424"
     r"|every AIM-424[^.\n]*\bflies U\.S\. Navy 2027"
     r"|flies U\.S\. Navy 2027'?s AIM-424 flight model",
     AIM424_SOURCES + AIM424_OUTPUT + AIM424_STUBS + AIM424_DOCS,
     "the 13 Oct plan (feature/aim424-usn2027-flight-model) was never merged; " + ONE_AIM424,
     WRAPPED),
    (r"YF-23 (still )?(keeps|fires) its author's (own )?round"
     r"|yf23_aim424_internal is not SEST's"
     r"|yf23_aim424_internal on its own mesh"
     r"|author's own round \(the current state",
     AIM424_SOURCES + AIM424_OUTPUT + AIM424_STUBS + AIM424_DOCS,
     "the YF-23's round flies SEST's figures on SEST's model block now; " + ONE_AIM424,
     WRAPPED),
]


def main():
    hits, files = [], set()
    for pattern, globs, why, *opt in STALE:
        rx = re.compile(pattern, re.I)
        wrapped = WRAPPED in opt
        seen = set()
        for g in globs:
            for path in sorted(ROOT.glob(g)):
                if path in seen or not path.is_file():
                    continue
                seen.add(path)
                files.add(path)
                lines = path.read_text(**CODEC).splitlines()
                for n, line in enumerate(lines, 1):
                    m = rx.search(line)
                    if not m and wrapped and n < len(lines):
                        # A Markdown paragraph wraps, so the phrase may run on
                        # to the next line. Only a match that crosses the
                        # break counts here; one wholly on the next line is
                        # reported there.
                        head = line.rstrip()
                        m = next((x for x in rx.finditer(head + " " + lines[n].strip())
                                  if x.start() < len(head) < x.end()), None)
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
