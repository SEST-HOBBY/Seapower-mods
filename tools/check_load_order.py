#!/usr/bin/env python3
"""Verify every SEST pack still wins the files it has to win.

A SEST pack works by shipping a replacement copy of a file and sitting ABOVE
the mod it replaces. Move anything above it and the patch silently stops
applying - no error, no warning, it just quietly does nothing. That is exactly
what happened when U.S. Navy 2027 was moved above Euromod: it jumped over
SEST_Growler_NGJ_MALICE at the same time, and the Growler pack went inert.

The rules are COMPUTED, not listed. For each SEST pack, every mod that also
ships one of its files is a mod it must outrank. Nothing to keep in sync and
nothing to forget.

    python3 tools/check_load_order.py

Exits non-zero if any rule is violated, so it can gate a commit.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERRIDE_DIRS = {"aircraft", "vessels", "submarines", "land_units",
                 "ammunition", "biologic", "ui"}


def mod_name(token):
    info = ROOT / "mods-source" / token / "_info.ini"
    if info.exists():
        m = re.search(r"^Name=(.+)$", info.read_text(encoding="utf-8", errors="replace"), re.M)
        if m:
            return m.group(1).strip()
    return token


# Registry files that have exactly ONE section, so every key in them is a
# GLOBAL id rather than one unit's property. Overriding a key here changes the
# name of that thing on every unit in the game that uses it - and a SEST pack
# sits at the top of the order, so its copy is the one that wins.
#
# aircraft_names.ini and vessel_names.ini are NOT in this list: they are
# sectioned per unit, so `Squadron1` under [raaf_f-35a] is a different key from
# `Squadron1` under [ru_mi-14pl] and collisions there are imaginary.
GLOBAL_REGISTRIES = ("loadout_names.ini",)


def single_section_values(path):
    out = {}
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        s = line.strip()
        if s.startswith(("#", ";", "[")) or "=" not in s:
            continue
        key, _, value = s.partition("=")
        out[key.strip()] = value.split("//")[0].strip()
    return out


def global_renames():
    """Any SEST pack key that silently renames a base-game one, game-wide.

    The RAAF F-35A upstream renames `AntiShip` to "Anti-Ship JMS (Internal
    Only)". `AntiShip` is the anti-ship loadout of 159 aircraft files in this
    collection - a French Alouette II included - and a pack that carries that
    rename to the top of the load order renames it on all of them.
    """
    vanilla = ROOT / "mods-source" / "_vanilla" / "original"
    out = []
    for pack_dir in sorted((ROOT / "integration").glob("*/SEST_*")):
        if pack_dir.parent.name == "dist":
            continue
        for f in sorted(pack_dir.rglob("language_*/*.ini")):
            if f.name not in GLOBAL_REGISTRIES:
                continue
            base = vanilla / f.relative_to(pack_dir)
            if not base.exists():
                continue
            van, mine = single_section_values(base), single_section_values(f)
            for key, value in mine.items():
                if key in van and van[key] != value:
                    out.append(
                        f"{pack_dir.name}: {f.relative_to(pack_dir).as_posix()} "
                        f"sets {key}={value!r}, renaming the base game's "
                        f"{van[key]!r} on every unit that uses it")
    return out


def main():
    tokens = [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt")
              .read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.startswith("#")]
    rank = {t: i for i, t in enumerate(tokens)}

    # What each workshop mod ships, restricted to whole-file-override kinds.
    # systems/ and language_*/ merge, so sharing those implies no ordering rule.
    ships = collections.defaultdict(set)
    for d in (ROOT / "mods-source").iterdir():
        if not (d.is_dir() and d.name[0].isdigit()):
            continue
        for p in d.rglob("*.ini"):
            if p.parent.name in OVERRIDE_DIRS:
                ships[d.name].add(p.relative_to(d).as_posix().lower())

    problems, checked = global_renames(), 0
    # Source packs deploy consolidated as SEST_Integration, so a pack whose own
    # folder name is not a token takes the consolidated token's position. The
    # dist folder itself is skipped: it is the union of the sources, and
    # checking the sources keeps the per-pack messages.
    DIST_TOKEN = "SEST_Integration"
    for pack_dir in sorted((ROOT / "integration").glob("*/SEST_*")):
        if pack_dir.parent.name == "dist":
            continue
        pack = pack_dir.name
        # Case-folded: the game runs on case-insensitive NTFS, so
        # Shahed_136_white.ini and shahed_136_white.ini are one file.
        mine = {p.relative_to(pack_dir).as_posix().lower() for p in pack_dir.rglob("*.ini")
                if p.parent.name in OVERRIDE_DIRS}
        if not mine:
            continue
        pos = rank.get(pack, rank.get(DIST_TOKEN))
        if pos is None:
            problems.append(f"{pack} ships override files but is in the load order "
                            f"neither directly nor via {DIST_TOKEN}")
            continue
        for mod, theirs in ships.items():
            shared = mine & theirs
            if not shared or mod not in rank:
                continue
            checked += 1
            if pos > rank[mod]:
                problems.append(
                    f"{pack} (#{pos+1}) is BELOW {mod_name(mod)} (#{rank[mod]+1})\n"
                    f"        contested: {', '.join(sorted(shared)[:3])}"
                    + (f" +{len(shared)-3} more" if len(shared) > 3 else ""))

    # Structural backstop. The overlap rules above only fire for mods whose
    # files we actually have exported under mods-source/. A stale or partial
    # export would let a pack sink without anything noticing, so also require
    # the blunt invariant: no workshop mod ever outranks a SEST pack.
    packs = [t for t in tokens if t.startswith("SEST_")]
    if packs:
        last_pack = max(rank[p] for p in packs)
        jumpers = [t for t in tokens
                   if not t.startswith("SEST_") and rank[t] < last_pack]
        for t in jumpers:
            problems.append(
                f"{mod_name(t)} (#{rank[t]+1}) sits above a SEST pack\n"
                f"        SEST packs must occupy the top of the list, unbroken")

    print(f"checked {checked} pack/mod file overlaps across {len(tokens)} "
          f"load-order entries, and every global registry key\n")
    if problems:
        print(f"{len(problems)} BROKEN rule(s):\n")
        for p in problems:
            print(f"   {p}\n")
        print("An ordering rule means the patch is silently doing nothing - move the\n"
              "SEST pack above it. A rename means the pack is silently changing the\n"
              "base game for every unit - see integration/common/registry.py.")
        sys.exit(1)
    print("every SEST pack outranks every mod it shares an override file with")


if __name__ == "__main__":
    main()
