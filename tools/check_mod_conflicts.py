#!/usr/bin/env python3
"""Report what a newly-added mod would collide with, before you enable it.

Adding a large mod to a 137-entry load order is not a question of whether it
works on its own - it is a question of which files it takes over and which it
loses, and whether any of those are files a SEST pack depends on winning.

Run it AFTER subscribing and re-exporting, so the mod is in mods-source:

    powershell -ExecutionPolicy Bypass -File .\\tools\\export-mod-configs.ps1
    python3 tools/check_mod_conflicts.py 3413868677

It reports, in order of how much they matter:

  1. Files that a SEST pack currently wins and the new mod also ships. These
     are the dangerous ones: place the new mod above a SEST pack and the patch
     silently stops applying.
  2. Unit types your missions actually field that the new mod would take over.
  3. Everything else it collides with, summarised by the mod it would fight.
  4. Files it alone ships - the actual new content.

Nothing is changed. This only reads.
"""
import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import winning_file, load_order  # noqa: E402

UNIT_DIRS = {"aircraft", "vessels", "submarines", "land_units", "ammunition",
             "biologic", "systems", "weapons"}


def mod_name(token):
    if token.startswith("SEST_"):
        return token
    info = ROOT / "mods-source" / token / "_info.ini"
    if info.exists():
        m = re.search(r"^Name=(.+)$", info.read_text(encoding="utf-8", errors="replace"), re.M)
        if m:
            return m.group(1).strip()
    return token


def units_in_play():
    """Unit ids your missions field and your SEST packs roster."""
    used = set()
    for f in (ROOT / "integration" / "missions").glob("*.ini"):
        t = f.read_text(encoding="utf-8", errors="replace")
        used |= set(re.findall(r"^Type=(\S+)", t, re.M))
        used |= set(re.findall(r"^([A-Za-z0-9_.\-]+)=Squadron\d+,\d+", t, re.M))
    for f in (ROOT / "integration").glob("*/SEST_*/**/*.ini"):
        if f.parent.name not in UNIT_DIRS:
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        used |= set(re.findall(r"^([A-Za-z0-9_.\-]+)=Squadron\d+,\d+", t, re.M))
        used |= {a.split("|")[0] for a in re.findall(r"^Station\d+=([A-Za-z]\S*)", t, re.M)}
    return used


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mod", help="workshop id, as exported into mods-source/")
    args = ap.parse_args()

    d = ROOT / "mods-source" / args.mod
    if not d.is_dir():
        sys.exit(f"not exported: {d}\n"
                 "Subscribe in Steam, then run tools\\export-mod-configs.ps1")

    ships = {p.relative_to(d).as_posix(): p for p in d.rglob("*.ini")
             if p.parent.name in UNIT_DIRS or p.parent.parent.name == "language_en"}
    print(f"{mod_name(args.mod)}  ({args.mod})")
    print(f"ships {len(ships)} files the load order can fight over\n")

    order = load_order()
    listed = args.mod in order
    print(f"in data/load-order.tokens.txt : {'yes, position ' + str(order.index(args.mod)+1) if listed else 'NO - it has no assigned position yet'}\n")

    sest_hits, mission_hits, other = [], [], collections.Counter()
    solo = []
    used = units_in_play()
    for rel in sorted(ships):
        w = winning_file(rel)
        if w is None or w.resolve() == ships[rel].resolve():
            solo.append(rel)
            continue
        owner = w.parts[-3]
        stem = Path(rel).stem
        if owner.startswith("SEST_"):
            sest_hits.append((rel, owner))
        elif stem in used:
            mission_hits.append((rel, owner))
        else:
            other[owner] += 1

    print("=" * 70)
    print(f"1. COLLIDES WITH A SEST PACK ({len(sest_hits)}) - the dangerous ones")
    print("=" * 70)
    if sest_hits:
        for rel, owner in sest_hits:
            print(f"   {rel:<44} currently won by {owner}")
        print("\n   Put this mod ABOVE any of those packs and that patch stops applying.")
        print("   The SEST packs must stay above it.")
    else:
        print("   none - no SEST pack is at risk")

    print("\n" + "=" * 70)
    print(f"2. TAKES OVER SOMETHING YOU ACTUALLY FIELD ({len(mission_hits)})")
    print("=" * 70)
    if mission_hits:
        for rel, owner in mission_hits[:30]:
            print(f"   {rel:<44} from {mod_name(owner)[:24]}")
        if len(mission_hits) > 30:
            print(f"   ... and {len(mission_hits)-30} more")
        print("\n   These are units in your missions or SEST rosters. Whichever mod sits")
        print("   higher decides what you get - worth deciding deliberately.")
    else:
        print("   none")

    print("\n" + "=" * 70)
    print(f"3. OTHER COLLISIONS, by the mod it would fight")
    print("=" * 70)
    if other:
        for owner, n in other.most_common():
            print(f"   {n:>4} files  vs  {mod_name(owner)}")
    else:
        print("   none")

    print("\n" + "=" * 70)
    print(f"4. GENUINELY NEW CONTENT ({len(solo)} files nothing else ships)")
    print("=" * 70)
    by_kind = collections.Counter(Path(r).parent.name for r in solo)
    for kind, n in by_kind.most_common():
        print(f"   {n:>4}  {kind}")

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    if sest_hits:
        print(f"   {len(sest_hits)} SEST-pack file(s) at risk. Place it BELOW every SEST pack.")
    if mission_hits:
        print(f"   {len(mission_hits)} unit(s) you field would change hands. Review before enabling.")
    if not sest_hits and not mission_hits:
        print("   No collision with anything you use. Position is forgiving.")
    print(f"\n   Add '{args.mod}' to data/load-order.tokens.txt at the position you choose,")
    print("   then run tools\\set-mod-order.ps1 -AddMissing.")


if __name__ == "__main__":
    main()
