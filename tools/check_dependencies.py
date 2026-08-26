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
VANILLA = MODS / "_vanilla" / "original"

# A system entry, and the SystemName it names. Sensors, weapons and modules all
# resolve against systems/*.ini, which MERGE section by section rather than one
# mod winning the file - so a name is available if any exported mod defines it.
SYSTEM_SECTION = re.compile(
    r"^\[(?:Sensor|Weapon)System\d+[A-Za-z]*\][^\n]*\n(?:(?!^\[).*(?:\n|$))*", re.M)
SYSTEM_NAME = re.compile(r"^SystemName[ \t]*=[ \t]*([^\n]*)$", re.M)


def mod_name(t):
    f = MODS / t / "_info.ini"
    if f.exists():
        m = re.search(r"^Name=(.+)$", f.read_text(encoding="utf-8", errors="replace"), re.M)
        if m:
            return m.group(1).strip()
    return t


def system_index():
    """Every system name vanilla or an exported mod defines, and who defines it.

    A hull's radars and guns are references exactly as its ammunition is - a
    SystemName that nothing defines is a sensor that does not exist - but until
    the replenishment pack started REFITTING its clones, nothing here chose a
    system name, so nothing checked them. It does now: the Tide asks for
    Artisan, the Type 901 for a Type 730, and both live in somebody else's mod.
    """
    idx = collections.defaultdict(set)
    # The SEST packs' own systems/ files count. Two packs define sensors that
    # exist nowhere else - the Triton's AN/ZPY-3 and the Growler's NGJ pods -
    # and leaving them out made this check report a pack for naming a system it
    # ships itself, one directory away. systems/*.ini merge section by section,
    # so a pack's definitions are as available as vanilla's.
    sest = sorted((ROOT / "integration").glob("*/SEST_*/systems/*.ini"))
    for path in list(MODS.glob("*/systems/*.ini")) + list(VANILLA.glob("systems/*.ini")) + sest:
        if VANILLA in path.parents:
            mod = "vanilla"
        elif path.parts[-3].startswith("SEST_"):
            mod = path.parts[-3]
        else:
            mod = path.parts[-3]
        for m in re.finditer(r"^\[([^\]\n]+)\]",
                             path.read_text(encoding="utf-8", errors="replace"), re.M):
            idx[m.group(1)].add(mod)
    return idx


def systems_named(text):
    """SystemName values inside system sections only.

    Scoped, because the same key appears in MESH sections - vanilla's [SPS_40]
    block carries SystemName=SPS-40 beside its Mesh= line - and those are
    decorative labels rather than references: 757 of the mesh sections a vanilla
    sensor mounts carry no SystemName at all and eleven carry one that names a
    mesh instead of a system. Counting them would manufacture dependencies that
    do not exist.
    """
    for block in SYSTEM_SECTION.finditer(text):
        m = SYSTEM_NAME.search(block.group(0))
        if m:
            name = m.group(1).split("//")[0].strip()
            if name:
                yield name


def upstream_system_names():
    """Every SystemName any vanilla or workshop unit file references.

    Not what systems/ DEFINES - what unit files USE. The two differ by more
    than typos: Hardpoint, WingHardpoint and BombBay are named by two dozen
    upstream aircraft and defined nowhere, because the engine handles them
    itself. Membership here is what separates "upstream does this" from "we
    made this up".
    """
    names = set()
    for d in list(MODS.iterdir()) + [VANILLA]:
        if not d.is_dir():
            continue
        for sub in UNIT_DIRS:
            if not (d / sub).is_dir():
                continue
            for f in (d / sub).glob("*.ini"):
                names.update(systems_named(f.read_text(encoding="utf-8", errors="replace")))
    return names


def owners_index():
    idx = collections.defaultdict(set)
    for d in MODS.iterdir():
        if d.is_dir() and d.name[0].isdigit():
            for f in d.rglob("*.ini"):
                idx[f.relative_to(d).as_posix().lower()].add(d.name)
    return idx


def main():
    idx, order = owners_index(), load_order()
    systems = system_index()
    upstream_systems = upstream_system_names()
    problems, rows, inherited = [], [], collections.defaultdict(set)

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
                # Systems the file names. An unresolved one is only THIS
                # repo's if no upstream unit file names it either: a name the
                # collection uses widely and systems/ never defines is an
                # engine keyword or an upstream convention, not a typo here.
                # That distinction is the whole check. "Is the file one we
                # invented?" was the first rule and it was wrong twice over -
                # it blamed this repo for Hardpoint, WingHardpoint and BombBay,
                # which 24 upstream aircraft use and nothing defines, and for
                # the Choules' Aldebaran, which came in with the Galicia the
                # hull is cloned from.
                for name in set(systems_named(text)):
                    owners = systems.get(name)
                    if not owners:
                        if name in upstream_systems:
                            inherited[name].add(rel)
                        else:
                            problems.append(f"{pack}: {rel} names system {name}, which "
                                            "nothing defines and no upstream unit file "
                                            "uses - this one is ours")
                    elif not any(o == "vanilla" or o.startswith("SEST_") for o in owners):
                        reference[sorted(owners)[0]] += 1

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

    if inherited:
        hulls = len({r for rels in inherited.values() for r in rels})
        print(f"\n{len(inherited)} system name(s) on {hulls} FORKED hull(s) resolve to "
              "nothing anywhere in the collection.")
        print("   Upstream's, not this repo's - the packs ship those files unchanged "
              "apart from the")
        print("   documented insertions. Listed because each one is a sensor or mount "
              "that will not")
        print("   work in game for anyone running that mod, with or without SEST.")
        for name in sorted(inherited):
            rels = sorted(inherited[name])
            more = f" (+{len(rels) - 2} more)" if len(rels) > 2 else ""
            print(f"      {name:<28} {', '.join(Path(r).stem for r in rels[:2])}{more}")

    print()
    if problems:
        print(f"{len(problems)} MISSING dependency(ies):\n")
        for p in problems:
            print(f"   {p}")
        sys.exit(1)
    print("every SEST pack has its upstream mods exported and ordered")


if __name__ == "__main__":
    main()
