#!/usr/bin/env python3
"""Hold the documentation to the numbers the build actually produces.

Every headline figure in this repo's prose is a measurement, and measurements
go stale the moment a builder changes. That has happened repeatedly and it has
usually been a human who spotted it: the mod count sat at 128 for four commits
after it became 132; the launcher figure said 280 hulls when it meant 292 and
was conflating three different populations; the pack's own Mod Manager blurb
still told players it forked RE-power's copies and shipped six modern
auxiliaries, eight commits after it stopped doing either.

So each claim below names a FILE, the PATTERN that carries the number, and the
value recomputed from the built pack. A claim fails two ways, and both matter:

  DRIFTED  - the pattern matched and the number is wrong.
  MISSING  - the pattern did not match at all. Either the sentence was reworded
             (so re-point the claim) or the fact was dropped (so decide whether
             it should have been). Silence is not proof of correctness, which
             is the whole reason this fails rather than skipping.

Numbers are compared as integers after stripping separators, so prose may write
2080, 2,080 or 2 080 as it prefers.

    python3 tools/check_docs.py

Exits non-zero on any drifted or missing claim, so it gates a commit alongside
the other five.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration"))
sys.path.insert(0, str(ROOT / "integration" / "missions"))
sys.path.insert(0, str(ROOT / "integration" / "replenishment"))
from common.ras import CLONES, STORE_FIXES, SUPPLIERS               # noqa: E402

PACK = ROOT / "integration" / "replenishment" / "SEST_Replenishment"
MODS = ROOT / "mods-source"
CODEC = dict(encoding="utf-8", errors="surrogateescape")

RELOAD_MARK = "SEST RAS: without this"


def measure():
    """Recompute every figure the prose quotes, from the built pack."""
    hulls = launchers = 0
    for f in PACK.rglob("*.ini"):
        if f.parent.name not in ("vessels", "submarines"):
            continue
        n = f.read_text(**CODEC).count(RELOAD_MARK)
        if n:
            hulls += 1
            launchers += n

    metered = sum(1 for f in (PACK / "ammunition").glob("*.ini")
                  if re.search(r"^SupplyCategory=SEST_", f.read_text(**CODEC), re.M))

    shipped_suppliers = sum(1 for u in SUPPLIERS if (PACK / "vessels" / f"{u}.ini").exists())
    blocs = [c["bloc"] for c in CLONES.values()]

    return {
        "launchers": launchers,
        "hulls": hulls,
        "clones": len(CLONES),
        "blue": blocs.count("BLUE"),
        "red": blocs.count("RED"),
        "named_ships": sum(len(c["hulls"]) for c in CLONES.values()),
        "upstream_suppliers": shipped_suppliers,
        # every hull that can give: the ten shipped here, the eight clones, and
        # HMAS Supply, which another SEST pack emits from this same table
        "supply_hulls": shipped_suppliers + len(CLONES) + 1,
        "metered": metered,
        "store_fixes": len(STORE_FIXES),
        "exported_mods": sum(1 for d in MODS.iterdir()
                             if d.is_dir() and d.name != "_vanilla"),
    }


# file, human name of the claim, regex with ONE capture group, key in measure()
CLAIMS = [
    ("integration/replenishment/README.md", "launcher fix total",
     r"\*\*([\d,  ]+) launchers made reloadable\*\*", "launchers"),
    ("integration/replenishment/README.md", "clone count in the stage table",
     r"\| \*\*New hulls\*\* \| (\d+) modern replenishment ships", "clones"),
    ("integration/replenishment/README.md", "named ships",
     r"(\d+) named ships, as \*\*new unit ids\*\*", "named_ships"),
    ("integration/replenishment/README.md", "metered rounds",
     r"\| \*\*Metering\*\* \| (\d+) heavy rounds", "metered"),
    ("integration/replenishment/README.md", "repaired store references",
     r"\| \*\*Repairs\*\* \| (\d+) broken upstream ammunition references", "store_fixes"),
    ("integration/replenishment/README.md", "supply-capable hull total",
     r"All (\d+) carry\s*\n?`TargetTypes=Vessel,Submarine`", "supply_hulls"),
    ("integration/replenishment/README.md", "exported mod count",
     r"in the (\d+) exported mods", "exported_mods"),

    ("docs/replenishment-in-play.md", "launcher fix total",
     r"\*\*([\d,  ]+) launchers across", "launchers"),
    ("docs/replenishment-in-play.md", "hull count",
     r"launchers across\s*\n?(\d+) ships\*\*", "hulls"),
    ("docs/replenishment-in-play.md", "supply-capable hull total",
     r"\*\*(?:Nineteen|\d+) supply-capable hulls in all", None),

    ("integration/replenishment/build_patch.py", "Mod Manager blurb, clone count",
     r"(Eight) modern replenishment ships arrive", None),
]

WORDS = {19: "Nineteen"}


def check():
    facts = measure()
    problems, checked = [], 0
    for rel, name, pattern, key in CLAIMS:
        path = ROOT / rel
        if not path.exists():
            problems.append(f"MISSING FILE  {rel}")
            continue
        m = re.search(pattern, path.read_text(**CODEC), re.M)
        if not m:
            problems.append(
                f"MISSING       {rel}: the '{name}' claim no longer matches its pattern. "
                "Re-point the claim in tools/check_docs.py, or restore the fact.")
            continue
        checked += 1
        if key is None:
            continue                      # presence-only claim; the words carry it
        want = facts[key]
        got = m.group(1).replace(",", "").replace(" ", "").replace(" ", "")
        if got != str(want):
            problems.append(f"DRIFTED       {rel}: '{name}' says {m.group(1).strip()}, "
                            f"the build produces {want}")

    # the word-form claims, checked against the same measurement
    play = (ROOT / "docs" / "replenishment-in-play.md")
    if play.exists() and WORDS.get(facts["supply_hulls"]):
        word = WORDS[facts["supply_hulls"]]
        if word not in play.read_text(**CODEC):
            problems.append(f"DRIFTED       docs/replenishment-in-play.md: the guide spells the "
                            f"supply-hull total in words and it is no longer '{word}' "
                            f"({facts['supply_hulls']})")

    print(f"measured from the built pack: {facts['launchers']} launchers on {facts['hulls']} "
          f"hulls, {facts['clones']} clones ({facts['blue']} BLUE / {facts['red']} RED), "
          f"{facts['named_ships']} named ships,\n"
          f"{facts['supply_hulls']} supply-capable hulls, {facts['metered']} metered rounds, "
          f"{facts['store_fixes']} store repairs, {facts['exported_mods']} exported mods")
    print(f"checked {checked}/{len(CLAIMS)} documented claim(s)")
    if problems:
        print(f"\n{len(problems)} claim(s) out of step with the build:\n")
        for p in problems:
            print(f"   {p}")
        sys.exit(1)
    print("every documented figure matches what the build produces")


if __name__ == "__main__":
    check()
