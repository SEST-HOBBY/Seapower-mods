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

# Language AND systems files MERGE key-by-key rather than replacing the file.
# Two mods shipping language_en/ammunition_names.ini or systems/sensors.ini is
# normal and costs nothing; only keys they both define are contested.
#
# The proof for systems/ is that 89 mods ship systems/sensors.ini ranging from
# 8 lines to 8141. If the winner replaced the file, an 8-line one would delete
# every sensor in the game. It does not, and SEST_Growler_NGJ_MALICE's own
# 11-line sensors.ini adds the AN/ALQ-249 without removing anything.
#
# UNIT files are the opposite - aircraft/, vessels/, land_units/, ammunition/
# are whole-file overrides where the loser is simply gone. That asymmetry is
# the whole point of this script, and conflating the two overstates conflicts
# badly: a small SAM mod looks like it is fighting the Custom Loadout Editor
# when all it does is add its own sensor entry.
def merges(rel):
    return rel.startswith(("language_", "language\\", "systems/", "systems\\"))


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


def other_owners(rel, me):
    """Every source other than <me> that ships <rel>, highest-ranked first.

    winning_file() answers "who loads" - which is not the same question. A mod
    placed last still SHIPS its copies; they just lose. Classifying on the
    winner alone made those copies look like content nothing else ships, and
    made files the mod loses look like files it takes over.
    """
    global _OWNERS
    if _OWNERS is None:
        _OWNERS = collections.defaultdict(list)
        for d in (ROOT / "mods-source").iterdir():
            if d.is_dir() and d.name[0].isdigit():
                for f in d.rglob("*.ini"):
                    _OWNERS[f.relative_to(d).as_posix().lower()].append(d.name)
        for pack in (ROOT / "integration").glob("*/SEST_*"):
            for f in pack.rglob("*.ini"):
                _OWNERS[f.relative_to(pack).as_posix().lower()].append(pack.name)
    rank = {t: i for i, t in enumerate(load_order())}
    owners = [t for t in _OWNERS.get(rel.lower(), []) if t != me]
    return sorted(owners, key=lambda t: rank.get(t, 10**6))


_OWNERS = None


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

    sest_hits, mission_hits, other = [], [], collections.defaultdict(list)
    merging, solo, outranked, sest_beaten = [], [], [], []
    used = units_in_play()
    for rel in sorted(ships):
        rivals = other_owners(rel, args.mod)
        if not rivals:
            solo.append(rel)
            continue
        owner = rivals[0]
        stem = Path(rel).stem
        if merges(rel):
            merging.append((rel, owner))
            continue
        w = winning_file(rel)
        i_win = w is not None and w.resolve() == ships[rel].resolve()
        if owner.startswith("SEST_"):
            # Only a risk if this mod actually beats the pack. Sitting below
            # one and sharing a file is the arrangement working as intended.
            (sest_beaten if i_win else sest_hits).append((rel, owner))
        elif not i_win:
            outranked.append((rel, owner))     # it ships this, but loses it
        elif stem in used:
            mission_hits.append((rel, owner))
        else:
            other[owner].append(rel)

    print("=" * 70)
    print(f"1. COLLIDES WITH A SEST PACK ({len(sest_hits) + len(sest_beaten)})"
          + (f" - {len(sest_beaten)} BREAKING" if sest_beaten else " - all safely below"))
    print("=" * 70)
    if sest_hits or sest_beaten:
        for rel, owner in sest_beaten:
            print(f"   {rel:<44} BREAKS {owner}")
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
    n_other = sum(len(v) for v in other.values())
    print(f"3. OTHER WHOLE-FILE COLLISIONS ({n_other})")
    print("=" * 70)
    if other:
        for owner, files in sorted(other.items(), key=lambda x: -len(x[1])):
            print(f"   vs {mod_name(owner)}:")
            for rel in sorted(files)[:10]:
                print(f"        {rel}")
            if len(files) > 10:
                print(f"        ... and {len(files)-10} more")
    else:
        print("   none")

    print("\n" + "=" * 70)
    print(f"   MERGING files shared ({len(merging)}) - NOT a conflict")
    print("=" * 70)
    if merging:
        for rel, owner in sorted(merging)[:8]:
            print(f"   {rel:<40} also in {mod_name(owner)[:26]}")
        if len(merging) > 8:
            print(f"   ... and {len(merging)-8} more")
        print("\n   Language and systems files merge key-by-key, so both mods coexist.")
    else:
        print("   none")

    print("\n" + "=" * 70)
    print(f"4. SHIPPED BUT OUTRANKED ({len(outranked)}) - it loses these, no action")
    print("=" * 70)
    if outranked:
        by_owner = collections.defaultdict(list)
        for rel, owner in outranked:
            by_owner[owner].append(rel)
        for owner, rels in sorted(by_owner.items(), key=lambda kv: -len(kv[1])):
            print(f"   {len(rels):>4} file(s) kept by {mod_name(owner)}")
        print("\n   Its copies never load. That is the point of its position.")
    else:
        print("   none")

    print("\n" + "=" * 70)
    print(f"5. GENUINELY NEW CONTENT ({len(solo)} files nothing else ships)")
    print("=" * 70)
    by_kind = collections.Counter(Path(r).parent.name for r in solo)
    for kind, n in by_kind.most_common():
        print(f"   {n:>4}  {kind}")

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    if sest_beaten:
        packs = sorted({o for _, o in sest_beaten})
        print(f"   BREAKS {len(sest_beaten)} file(s) in {', '.join(packs)}.")
        print("   That patch is silently doing nothing. Move it BELOW the pack.")
    if sest_hits:
        print(f"   Shares {len(sest_hits)} file(s) with a SEST pack and loses all of")
        print("   them - correct as placed. Keep it below the packs.")
    if mission_hits:
        print(f"   {len(mission_hits)} unit(s) you field would change hands. Review before enabling.")
    if n_other and not sest_hits and not mission_hits:
        print(f"   {n_other} whole-file collision(s), none with anything you field.")
    if outranked and not sest_hits and not mission_hits and not n_other:
        print(f"   Contests {len(outranked)} file(s) and loses every one at its current")
        print(f"   position. Nothing changes hands; only its {len(solo)} unique file(s) load.")
    if not (sest_hits or mission_hits or n_other or outranked):
        print("   No whole-file collision with anything. Position is forgiving.")
    if listed:
        print(f"\n   Already at position {order.index(args.mod)+1} of {len(order)}. To change it, edit")
        print("   data/load-order.tokens.txt then run tools\\set-mod-order.ps1 -AddMissing.")
    else:
        print(f"\n   Add '{args.mod}' to data/load-order.tokens.txt at the position you choose,")
        print("   then run tools\\set-mod-order.ps1 -AddMissing.")


if __name__ == "__main__":
    main()
