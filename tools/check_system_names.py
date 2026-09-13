#!/usr/bin/env python3
"""Which SystemName references could silently bind to another mod's definition.

systems/ files merge KEY BY KEY across the load order: the highest-ranked mod
defining [Litening] owns that key for everyone. A unit file naming it gets the
winner, not the copy shipped beside it. That is invisible - no error, no log
line, the aircraft simply flies with a different sensor than the pack's author
measured.

SEST A-10C+ shipped with exactly this defect. It referenced SystemName=Litening
intending the A-10C mod's pod (2.2/4.0 multipliers, night vision 1.0) and got
Euromod JMSDF's instead (3.0/3.4, night vision 0.5), because six mods define
that name and the A-10C's copy ranks sixth. The upgrade was worse after dark
than the sensor it replaced, and the pack's own README quoted figures the
aircraft never had. Fixed by shipping SEST_A10C_FLIR under a name nothing else
uses.

Two distinctions decide whether a reference is a problem, and both are
computed rather than listed:

  INHERITED vs INTRODUCED. A forked hull that names what its upstream named is
  harmless - the original had the same ambiguity and resolved the same way.
  Only a name the pack ADDS reflects a choice its author made, and only that
  choice can be silently overridden.

  AGREEING vs DIFFERING rivals. If every mod defining a name gives it the same
  values, whoever wins is irrelevant. Only a name whose definitions materially
  disagree can change how the unit behaves.

A reference that is both introduced and contested is worth a look. It is not
automatically wrong: picking "Type 382" by name usually means wanting a Type
382, and the winner is still one. It IS wrong when the pack was tuned around
particular numbers, which is the case this tool exists to surface.

    python3 tools/check_system_names.py

Always exits 0: a report, not a gate.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS = ROOT / "mods-source"
VANILLA = MODS / "_vanilla" / "original"
UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units")
CODEC = dict(encoding="utf-8", errors="replace")


def load_order():
    lines = (ROOT / "data" / "load-order.tokens.txt").read_text(encoding="utf-8").splitlines()
    toks = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
    return {t: i for i, t in enumerate(toks)}


def definitions():
    """name -> {mod: {key: value}}, comments stripped so formatting is not a diff."""
    out = collections.defaultdict(dict)
    for f in list(MODS.glob("*/systems/*.ini")) + list(VANILLA.glob("systems/*.ini")):
        mod = "vanilla" if "_vanilla" in f.parts else f.parts[-3]
        for m in re.finditer(r"^\[([^\]\n]+)\][^\n]*\n((?:(?!^\[).*\n)*)",
                             f.read_text(**CODEC), re.M):
            kv = {}
            for line in m.group(2).splitlines():
                line = re.sub(r"//.*|#.*", "", line).strip()
                if "=" in line:
                    k, _, v = line.partition("=")
                    kv[k.strip()] = v.strip()
            out[m.group(1)][mod] = kv
    return out


def names_in(path):
    return set(re.findall(r"^SystemName=(\S+)", path.read_text(**CODEC), re.M))


def main():
    rank = load_order()
    defs = definitions()

    own = set()
    for f in ROOT.glob("integration/*/SEST_*/systems/*.ini"):
        if "dist" not in f.parts:
            own |= set(re.findall(r"^\[([^\]\n]+)\]", f.read_text(**CODEC), re.M))

    findings, inherited, agreed = [], 0, 0
    for f in sorted(ROOT.glob("integration/*/SEST_*/**/*.ini")):
        if "dist" in f.parts or f.parent.name not in UNIT_DIRS:
            continue
        rel = f"{f.parent.name}/{f.name}"
        cands = sorted(MODS.glob(f"*/{rel}"), key=lambda p: rank.get(p.parts[-3], 999))
        if (VANILLA / rel).exists():
            cands.append(VANILLA / rel)
        upstream = names_in(cands[0]) if cands else set()

        for name in sorted(names_in(f) - upstream - own):
            d = defs.get(name, {})
            if len(d) < 2:
                continue
            if name in upstream:
                inherited += 1
                continue
            ranked = sorted(d, key=lambda m: rank.get(m, 999))
            winner = ranked[0]
            contested = [o for o in ranked[1:]
                         if any(d[winner].get(k) != d[o].get(k)
                                for k in set(d[winner]) | set(d[o]))]
            if not contested:
                agreed += 1
                continue
            findings.append((f.parts[-3], rel, name, winner, len(d), contested))

    print(f"{len(findings)} introduced-and-contested reference(s); "
          f"{agreed} introduced but every rival agrees; {inherited} inherited\n")
    by_pack = collections.defaultdict(list)
    for pack, rel, name, winner, n, contested in findings:
        by_pack[pack].append((rel, name, winner, n))
    for pack in sorted(by_pack):
        print(f"{pack}")
        seen = {}
        for rel, name, winner, n in by_pack[pack]:
            seen.setdefault((name, winner, n), []).append(rel)
        for (name, winner, n), rels in sorted(seen.items()):
            where = rels[0] + (f" +{len(rels)-1}" if len(rels) > 1 else "")
            print(f"   {name:28} {n} definers, binds to {winner:12} {where}")
        print()
    print("Not necessarily defects: naming a sensor usually means wanting that KIND of\n"
          "sensor, and the winner is still one. It IS a defect where a pack was tuned\n"
          "around particular values - ship your own copy under a unique name, as\n"
          "integration/a10c-plus does with SEST_A10C_FLIR.")


if __name__ == "__main__":
    main()
    sys.exit(0)
