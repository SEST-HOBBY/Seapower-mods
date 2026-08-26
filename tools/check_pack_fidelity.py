#!/usr/bin/env python3
"""Prove every SEST_Replenishment file is its upstream plus only the intended
edits.

The pack ships ~330 whole-file overrides, each a copy of the load-order
winner with lines inserted. Any OTHER byte difference is a silent edit to
somebody else's mod riding along at tier 0 - the class of defect that
motivated this checker: errors="replace" once rewrote a stray 0xFF and six
0xA0 bytes as U+FFFD in three upstream files, and an iteration-order bug once
forked the losing copy of plan_cv_fujian. Neither was visible in any other
gate.

For every file in the built pack this recomputes the upstream the builder
should have used - through the builder's own resolution functions, so checker
and builder can never disagree about what "upstream" means - normalises CRLF
to LF (the one transformation the builder makes on purpose, affecting exactly
one genuinely-CRLF upstream file), strips the deliberate insertions, and
requires byte equality:

  vessels/   the supply block (suppliers), ReloadableWithoutMagazine lines
  ammunition/ one SupplyCategory line (metered rounds), a synthesised
             [General] header on alias files, AmmoPoints/SupplyCategory
             restorations
  clones     no upstream by design - checked for exactly the expected count

    python3 tools/check_pack_fidelity.py

Exits non-zero on any unexplained byte, so it can gate a commit alongside
check_load_order and friends.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "integration" / "replenishment" / "SEST_Replenishment"

sys.path.insert(0, str(ROOT / "integration"))
sys.path.insert(0, str(ROOT / "integration" / "missions"))
sys.path.insert(0, str(ROOT / "integration" / "replenishment"))
import build_patch as builder  # noqa: E402
from common.ras import CLONES, RESTORE_ROUNDS, SUPPLIERS  # noqa: E402

# The emitted supply block: divider + [SupplySystem1] section.
EMITTED_BLOCK = re.compile(
    rb"^\[-+ Supply Systems -+\]\n\[SupplySystem1\]\n(?:(?!^\[).*\n)*", re.M)
# Upstream supply blocks the builder strips (active or commented, either name).
UPSTREAM_BLOCK = re.compile(
    rb"^\[-+ Supply Systems -+\][^\n]*\n"
    rb"(?:#[^\n]*\n|\n|\[SupplySystem\d+\][^\n]*\n(?:(?!^\[).*\n)*)*", re.M)
RELOAD_LINE = b"SEST RAS: without this"
CATEGORY_LINE = re.compile(rb"^SupplyCategory=SEST_[^\n]*\n", re.M)


def upstream_for(rel):
    stem = Path(rel).stem
    if rel.startswith("ammunition/"):
        _, path = builder.winning_ammo(stem)
        return path
    if stem in SUPPLIERS:
        return builder.winning_vessel(stem, SUPPLIERS[stem]["source"])
    for hull_rel, mod, _ in builder.modern_hulls():
        if hull_rel == rel:
            return builder.MODS / mod / rel
    return None


def strip_insertions(rel, blob):
    stem = Path(rel).stem
    if rel.startswith("vessels/"):
        if stem in SUPPLIERS:
            blob = EMITTED_BLOCK.sub(b"", blob)
        lines = [l for l in blob.split(b"\n") if RELOAD_LINE not in l]
        return b"\n".join(lines)
    if rel.startswith("ammunition/"):
        if stem in RESTORE_ROUNDS:
            # the two restored keys are the insertion
            lines = [l for l in blob.split(b"\n")
                     if not (l.startswith(b"AmmoPoints=") or l.startswith(b"SupplyCategory="))]
            return b"\n".join(lines)
        blob = CATEGORY_LINE.sub(b"", blob)
        # ONLY alias files can carry a synthesised [General]: the builder adds
        # one when the alias target has no [General] of its own to anchor the
        # category to. A plain file with "[General]" followed by blank lines
        # must keep them - stripping unconditionally once ate plan_yj-18c's
        # real section header.
        if blob.lstrip().startswith(b"#!alias"):
            return blob.replace(b"\n[General]\n\n", b"\n", 1)
        return blob
    return blob


def main():
    if not PACK.is_dir():
        sys.exit("pack not built - run integration/replenishment/build_patch.py first")

    clones = {c for c in CLONES} | {f"{c}_variants" for c in CLONES}
    problems, checked, clone_files = [], 0, 0

    for f in sorted(PACK.rglob("*.ini")):
        rel = f.relative_to(PACK).as_posix()
        if rel == "_info.ini" or rel.startswith("language_"):
            continue
        if Path(rel).stem in clones:
            clone_files += 1
            continue
        src = upstream_for(rel)
        if src is None or not Path(src).exists():
            problems.append(f"{rel}: no upstream resolves - the builder should not have "
                            "shipped this file")
            continue
        checked += 1
        want = Path(src).read_bytes().replace(b"\r\n", b"\n")
        if Path(rel).stem in SUPPLIERS or Path(rel).stem in RESTORE_ROUNDS:
            want = UPSTREAM_BLOCK.sub(b"", want) if Path(rel).stem in SUPPLIERS else want
        got = strip_insertions(rel, f.read_bytes())
        if Path(rel).stem in RESTORE_ROUNDS:
            # the upstream lacks the restored keys by definition; nothing to strip there
            pass
        if got != want:
            a, b = want.split(b"\n"), got.split(b"\n")
            at = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y),
                      f"length {len(a)} vs {len(b)}")
            problems.append(f"{rel}: differs from {Path(src).relative_to(ROOT)} beyond the "
                            f"intended insertions, first at line {at}")

    expected_clone_files = len(CLONES) * 2
    if clone_files != expected_clone_files:
        problems.append(f"clone file count is {clone_files}, expected {expected_clone_files}")

    print(f"checked {checked} shipped files against their load-order-winning upstream "
          f"({clone_files} clone files have none by design)")
    if problems:
        print(f"\n{len(problems)} FIDELITY problem(s):")
        for p in problems:
            print(f"   {p}")
        sys.exit(1)
    print("every byte difference is an intended insertion")


if __name__ == "__main__":
    main()
