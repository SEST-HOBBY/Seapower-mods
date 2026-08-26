#!/usr/bin/env python3
"""Work out what each SEST pack needs installed alongside it, and check it is.

The packs ship 99 files and every one is a .ini - not a single model, texture
or asset bundle among them. That is deliberate (the repo stays small and the
patches stay readable) but it means NO pack is standalone. Each one is a set of
edits to files whose geometry lives in somebody else's mod, so installing a
pack without its upstream leaves the game with a unit definition pointing at a
mesh that is not there.

Two kinds of dependency, both derived rather than declared:

  OVERRIDE  - the pack ships its own copy of a file a workshop mod provides.
              That mod supplies the model the .ini refers to.
  REFERENCE - a loadout hangs a store, or a roster names a unit, that is
              defined in another mod entirely.

Anything vanilla already provides is not a dependency and is not listed.

    python3 tools/check_dependencies.py

Exits non-zero if a pack hangs a store or rosters a unit that nothing
defines (a pruned or never-exported provider), or depends on a mod missing
from the load order.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import winning_file, load_order  # noqa: E402

UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units", "ammunition", "biologic")
MODS = ROOT / "mods-source"


def mod_name(t):
    f = MODS / t / "_info.ini"
    if f.exists():
        m = re.search(r"^Name=(.+)$", f.read_text(encoding="utf-8", errors="replace"), re.M)
        if m:
            return m.group(1).strip()
    return t


def owners_index():
    idx = collections.defaultdict(set)
    for d in MODS.iterdir():
        if d.is_dir() and d.name[0].isdigit():
            for f in d.rglob("*.ini"):
                idx[f.relative_to(d).as_posix().lower()].add(d.name)
    return idx


def main():
    idx, order = owners_index(), load_order()
    problems, rows = [], []

    for pack_dir in sorted((ROOT / "integration").glob("*/SEST_*")):
        if pack_dir.parent.name == "dist":   # dist = the consolidated deployable; its content is checked via the source packs
            continue
        pack = pack_dir.name
        override, reference = collections.Counter(), collections.Counter()
        sest_dep = collections.Counter()

        for f in pack_dir.rglob("*.ini"):
            rel = f.relative_to(pack_dir).as_posix()
            if f.parent.name in UNIT_DIRS:
                for owner in idx.get(rel.lower(), ()):
                    override[owner] += 1
                text = f.read_text(encoding="utf-8", errors="replace")
                stores = {s.split("|")[0] for s in
                          re.findall(r"^Station\d+=([A-Za-z]\S*)", text, re.M)}
                stores |= set(re.findall(r"^Ammunition\d*=(\S+)", text, re.M))
                for s in stores:
                    w = winning_file(f"ammunition/{s}.ini")
                    if w is None:
                        # nothing anywhere ships this store: the reference is
                        # dangling. Before this check a pruned provider made
                        # the dependency vanish from the report instead of
                        # failing it.
                        problems.append(f"{pack}: {rel} hangs {s} but no mod, "
                                        "pack or vanilla file defines it")
                    # vanilla and the pack itself are not dependencies
                    elif w.parts[-3].isdigit() and w.parts[-3] != pack:
                        reference[w.parts[-3]] += 1
                # Units the pack rosters - an airbase that spawns E-7As needs
                # whatever mod defines the E-7A just as much as a loadout needs
                # its missile. Missing this reported SEST_RAAF_Bases, which
                # rosters an entire wing, as standalone.
                for uid in set(re.findall(r"^([A-Za-z0-9_.\-]+)=Squadron\d+,\d+",
                                          text, re.M)):
                    for kind in UNIT_DIRS:
                        w = winning_file(f"{kind}/{uid}.ini")
                        if w:
                            if w.parts[-3].isdigit() and w.parts[-3] != pack:
                                reference[w.parts[-3]] += 1
                            elif w.parts[-3].startswith("SEST_") and w.parts[-3] != pack:
                                sest_dep[w.parts[-3]] += 1
                            break
                    else:
                        problems.append(f"{pack}: {rel} rosters {uid} but no "
                                        "mod, pack or vanilla file defines it")

        needed = set(override) | set(reference)
        detail = [(t, "SEST pack", n) for t, n in sest_dep.most_common()]
        if not needed and not detail:
            rows.append((pack, []))
            continue
        for t in sorted(needed, key=lambda t: (-override[t], -reference[t])):
            kind = ("overrides" if override[t] else "references")
            n = override[t] or reference[t]
            detail.append((t, kind, n))
            # t always names an existing export: owners come from
            # owners_index(), which only iterates directories on disk. A
            # pruned provider therefore surfaces as a dangling-reference
            # problem above, never as a missing directory here.
            if t not in order:
                problems.append(f"{pack} needs {mod_name(t)} ({t}) - not in the load order")
        rows.append((pack, detail))

    for pack, detail in rows:
        print(f"\n{pack}")
        if not detail:
            print("   standalone - needs nothing but the base game")
        for t, kind, n in detail:
            print(f"   {kind:<10} {n:>3} file(s)  {mod_name(t)}  ({t})")

    print()
    if problems:
        print(f"{len(problems)} MISSING dependency(ies):\n")
        for p in problems:
            print(f"   {p}")
        sys.exit(1)
    print("every SEST pack has its upstream mods exported and ordered")


if __name__ == "__main__":
    main()
