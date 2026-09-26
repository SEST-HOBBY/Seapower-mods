#!/usr/bin/env python3
"""Produce two matched deployable builds that differ ONLY in the winning
ammunition/damage.ini, so the global intercept table can be tested as a single
variable.

Why this exists. The deployable is one consolidated pack, SEST_Integration, and
it is the only SEST entry in data/load-order.tokens.txt. SEST_Intercept_Model is
a build unit, not a load-order entry, so there is nothing to toggle in the Mod
Manager: disabling the consolidated pack would change every SEST override at
once, and leaving it enabled keeps the restored table active. Comparing "with
and without the pack" is therefore not a thing the installed game can express.
Two builds are.

    A_restored    SEST_Integration exactly as built, carrying vanilla's table
                  with the impact tier this repo ships.
    B_suppressed  byte-identical to A except ammunition/damage.ini, which
                  carries the Tu-95/AS-15 mod's truncated copy - the state the
                  collection was in before SEST_Intercept_Model.

Everything else is held fixed on purpose, including the SM-6, K-SAM II and
Stunner altitude fixes and the VeryLarge impact tier. If B dropped those too it
would differ from A in several ways and no result would be attributable.

B ships the truncated table itself rather than simply omitting the file. Both
reach the same effective content, but omitting it would make the result depend
on the Tu-95 mod being installed and correctly ordered on the test machine,
which is a second variable. This way the winning bytes are guaranteed by the
build, and the tool verifies they match that mod's copy exactly.

    python3 tools/make_intercept_ab_builds.py [--out DIR]

Deploy one, run the engagement, deploy the other, run it again. Read the
displayed intercept percentage rather than the outcome, and repeat enough shots
that a difference is distinguishable from a bad roll.

WHAT A RESULT MEANS. A difference between A and B shows the deleted globals
were doing something. NO difference is weaker: it shows no effect under the
conditions tested, which is not the same as "the engine already supplies
vanilla's values". The penalty may be inactive for that geometry, or masked by
another cap, or the round may not inherit what you think. Vary the engagement
before concluding, and pick the round with tools/survey_attack_altitudes.py,
which lists the anti-air rounds that inherit BOTH penalties and carry a closed
band.
"""
import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "integration" / "dist" / "SEST_Integration"
TU95 = ROOT / "mods-source" / "3395022688" / "ammunition" / "damage.ini"
TABLE = "ammunition/damage.ini"


def tree_files(root):
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "build" / "intercept-ab"),
                    help="output directory (default: build/intercept-ab, gitignored)")
    args = ap.parse_args()

    if not DIST.is_dir():
        sys.exit(f"no consolidated pack at {DIST} - run tools/build_all.py first")
    if not (DIST / TABLE).is_file():
        sys.exit(f"{DIST / TABLE} missing - is SEST_Intercept_Model registered and built?")
    if not TU95.is_file():
        sys.exit(f"donor missing: {TU95} - re-export mod 3395022688")

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    a = out / "A_restored" / "SEST_Integration"
    b = out / "B_suppressed" / "SEST_Integration"
    shutil.copytree(DIST, a)
    shutil.copytree(DIST, b)

    # B carries the truncated table verbatim.
    shutil.copyfile(TU95, b / TABLE)

    # Verify the experiment: exactly one differing path, and it is the table.
    fa, fb = tree_files(a), tree_files(b)
    if fa != fb:
        sys.exit(f"builds do not contain the same paths: {fa ^ fb}")
    differing = sorted(p for p in fa if not filecmp.cmp(a / p, b / p, shallow=False))
    if differing != [TABLE]:
        sys.exit(f"builds differ in {differing}, expected exactly ['{TABLE}'] - "
                 "the comparison would not be attributable, do not use these")
    if not filecmp.cmp(b / TABLE, TU95, shallow=False):
        sys.exit("B's table is not byte-identical to the donor - do not use these")

    keys = ("InterceptOutOfAltitudePenalty", "InterceptSpeedPenaltyMultiplier",
            "InterceptChanceOutOfAltitudeOverride")
    ta = (a / TABLE).read_text(encoding="utf-8-sig", errors="replace")
    tb = (b / TABLE).read_text(encoding="utf-8-sig", errors="replace")
    in_a = [k for k in keys if f"\n{k}=" in "\n" + ta]
    in_b = [k for k in keys if f"\n{k}=" in "\n" + tb]
    if in_b or len(in_a) != len(keys):
        sys.exit(f"sanity check failed: A defines {in_a}, B defines {in_b}; "
                 "expected A to define all three and B none")

    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    print(f"  A_restored/SEST_Integration    {len(fa)} files, table defines {len(in_a)}/"
          f"{len(keys)} intercept keys")
    print(f"  B_suppressed/SEST_Integration  {len(fb)} files, table defines 0/"
          f"{len(keys)} - matches {TU95.parts[-3]} byte for byte")
    print(f"  verified: the trees differ in exactly one file, {TABLE}")
    print("\nDeploy one folder's SEST_Integration, run the engagement, then the other.")
    print("Pick the round with tools/survey_attack_altitudes.py - it lists the anti-air")
    print("rounds that inherit BOTH penalties. The SM-3 is NOT one of them: it declares")
    print("both itself (SEST_Collection_Fixes sets them), so it cannot probe what a missing")
    print("global falls back to.")


if __name__ == "__main__":
    main()
