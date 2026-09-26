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

  vessels/   the supply block (suppliers), ReloadableWithoutMagazine lines,
             and the STORE_FIXES repair of a broken upstream ammunition id
  ammunition/ one SupplyCategory line (metered rounds), a synthesised
             [General] header on alias files, AmmoPoints/SupplyCategory
             restorations
  clones     the donor, plus the supply block, the refit's renamed systems
             and rounds, and the reload lines; _variants files are generated
             from scratch and only counted

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
from common.ras import (CLONES, RESTORE_ROUNDS, SUPPLIERS,  # noqa: E402
                        apply_refit, apply_store_fix, render_supply_block)

# The emitted supply block is not matched by pattern, it is RE-RENDERED from
# the tuning table and removed literally. A regex that ran "to the next line
# starting with [" was correct on nine hulls and wrong on the Algol, whose
# block is followed by a ### banner rather than the mesh divider: the strip ate
# the banner, the file then differed from vanilla by three missing lines, and
# the gate reported a fidelity failure that did not exist. Removing the exact
# rendered string cannot over-reach, and it proves something stronger on the
# way past - that what shipped is byte-for-byte what ras.py's table says.
def emitted_block(stem):
    spec = SUPPLIERS[stem] if stem in SUPPLIERS else CLONES[stem]["supply"]
    return render_supply_block(spec).encode("utf-8", "surrogateescape")

# Upstream supply blocks the builder strips (active or commented, either name).
UPSTREAM_BLOCK = re.compile(
    rb"^\[-+ Supply Systems -+\][^\n]*\n"
    rb"(?:#[^\n]*\n|\n|\[SupplySystem\d+\][^\n]*\n(?:(?!^\[).*\n)*)*", re.M)
RELOAD_LINE = b"SEST RAS: without this"
CATEGORY_LINE = re.compile(rb"^SupplyCategory=SEST_[^\n]*\n", re.M)


def donor_path(clone):
    mod, donor = clone["donor"]
    base = builder.VANILLA if mod == "vanilla" else builder.MODS / mod
    return base / "vessels" / f"{donor}.ini"


def upstream_for(rel):
    stem = Path(rel).stem
    if rel.startswith("ammunition/"):
        _, path = builder.winning_ammo(stem)
        return path
    if stem in SUPPLIERS:
        return builder.supplier_source(stem, SUPPLIERS[stem]["source"])
    if stem in CLONES:
        return donor_path(CLONES[stem])
    for hull_rel, mod, _ in builder.modern_hulls():
        if hull_rel == rel:
            return builder.MODS / mod / rel
    return None


def undo_refit(stem, blob):
    """Put a clone's refitted system names back to the donor's, so the rest of
    the file can be required to equal the donor byte for byte.

    The clone body was exempt from this gate until the refit landed, on the
    grounds that a clone has no upstream. It has one: its donor. What it did
    not have was a way to describe the difference, and the refit is that
    description - eight named slots, each resolving to exactly one name.

    The reversal is built from the TABLE, not from the build: for every slot,
    ask the resolver what it would pick and invert the arrow. That is what
    keeps this a check rather than a tautology - it re-derives the mapping
    independently and then requires the shipped bytes to match it. If the
    builder rewrote a line the table does not account for, the reversal cannot
    put it back and the diff surfaces.
    """
    clone = CLONES[stem]
    inverse, seen = {}, {}
    for slot, prefs in clone["refit"].items():
        new = builder.resolve_system(prefs, stem, slot)
        section, _, old = slot.rpartition(":")
        old = old.lstrip("@")
        key = f"{section}:{new}" if section else ("@" + new if slot.startswith("@") else new)
        if key in inverse:
            raise SystemExit(f"{stem}: refit slots {seen[key]} and {slot} both resolve to "
                             f"{new}, so the mapping cannot be inverted - give one of them "
                             "a distinct system")
        inverse[key], seen[key] = [old], slot
    text = blob.decode("utf-8", "surrogateescape")
    text, _ = apply_refit(text, inverse, lambda prefs, *_: prefs[0], stem)
    return text.encode("utf-8", "surrogateescape")


def strip_insertions(rel, blob):
    stem = Path(rel).stem
    if rel.startswith("vessels/"):
        if stem in SUPPLIERS or stem in CLONES:
            block = emitted_block(stem)
            if block not in blob:
                return b"<the pack's supply block is not the one ras.py renders>"
            blob = blob.replace(block, b"", 1)
        if stem in CLONES:
            blob = undo_refit(stem, blob)
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

    # A clone HULL is now checked - it is its donor plus a supply block, a
    # refit and the reload lines, and undo_refit() can put all three back. Its
    # _variants file still is not: clone_variants() writes that one from
    # scratch (a fresh [Default] and one [VariantN] per named ship), so there
    # is no upstream to diff it against, only the generator.
    variants = {f"{c}_variants" for c in CLONES}
    problems, checked, clone_files = [], 0, 0

    for f in sorted(PACK.rglob("*.ini")):
        rel = f.relative_to(PACK).as_posix()
        if rel == "_info.ini" or rel.startswith("language_"):
            continue
        if Path(rel).stem in variants:
            clone_files += 1
            continue
        src = upstream_for(rel)
        if src is None or not Path(src).exists():
            problems.append(f"{rel}: no upstream resolves - the builder should not have "
                            "shipped this file")
            continue
        checked += 1
        want = Path(src).read_bytes().replace(b"\r\n", b"\n")
        if Path(rel).stem in SUPPLIERS or Path(rel).stem in CLONES:
            want = UPSTREAM_BLOCK.sub(b"", want)
        elif rel.startswith("vessels/"):
            # Store repairs are applied FORWARD to the upstream copy rather
            # than reversed out of the shipped one, because the reversal is
            # genuinely ambiguous: usn_cg_kansas_late already carries a
            # legitimate usn_rim_162a beside the broken usn_rim_162essm, and
            # the Gorshkov three real wp_ss_n_27 beside one wp_ss-n-27.
            # Mapping the new id back would have rewritten the upstream
            # author's own correct lines and called the result a match.
            want = apply_store_fix(
                want.decode("utf-8", "surrogateescape"),
                lambda prefs, *_: builder.resolve_system(prefs, "fidelity", "@x"),
                Path(rel).stem)[0].encode("utf-8", "surrogateescape")
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

    if clone_files != len(CLONES):
        problems.append(f"{clone_files} clone _variants file(s) shipped, expected "
                        f"{len(CLONES)}")

    print(f"checked {checked} shipped files against their load-order-winning upstream "
          f"({clone_files} generated _variants file(s) have none by design)")
    if problems:
        print(f"\n{len(problems)} FIDELITY problem(s):")
        for p in problems:
            print(f"   {p}")
        sys.exit(1)
    print("every byte difference is an intended insertion")


if __name__ == "__main__":
    main()
