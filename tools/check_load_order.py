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

Since 14 Oct 2026 it also reads the LIVE order when the capture holds one
(data/install-snapshot/load-order.live.txt, written by capture-context.ps1):
it reports where that differs from the canonical order and whether every SEST
override still outranks its target there. SEST's slot in the live list is the
local SEST_Integration or SEST's own Workshop item, 3812461539, which the PC
runs as a subscriber since 14 Oct. A disabled entry does not load, so it
cannot outrank anything, and a disabled or missing SEST entry loses every
override. The exit code stays the canonical check's; a live order that
breaks a SEST override: then it says so and fails too.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "data" / "install-snapshot" / "load-order.live.txt"
OVERRIDE_DIRS = {"aircraft", "vessels", "submarines", "land_units",
                 "ammunition", "biologic", "ui"}
# Source packs deploy consolidated as SEST_Integration, so a pack whose own
# folder name is not a token takes the consolidated token's position; on a
# PC that runs the published pack as a subscriber, the live list carries SEST's
# own Workshop item instead (lib/common.ps1 $SestOwnWorkshopIds).
DIST_TOKEN = "SEST_Integration"
SEST_OWN = {"3812461539"}


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


def contested_text(shared):
    return (f"contested: {', '.join(sorted(shared)[:3])}"
            + (f" +{len(shared)-3} more" if len(shared) > 3 else ""))


def overlaps():
    """[(pack, mod, shared override files)] for every SEST source pack and
    every exported mod that ships one of its override files, plus the packs
    that ship override files (the dist folder is the union of the sources and
    is skipped, so the messages stay per pack)."""
    # What each workshop mod ships, restricted to whole-file-override kinds.
    # systems/ and language_*/ merge, so sharing those implies no ordering rule.
    ships = collections.defaultdict(set)
    for d in (ROOT / "mods-source").iterdir():
        if not (d.is_dir() and d.name[0].isdigit()):
            continue
        for p in d.rglob("*.ini"):
            if p.parent.name in OVERRIDE_DIRS:
                ships[d.name].add(p.relative_to(d).as_posix().lower())
    out, packs = [], []
    for pack_dir in sorted((ROOT / "integration").glob("*/SEST_*")):
        if pack_dir.parent.name == "dist":
            continue
        # Case-folded: the game runs on case-insensitive NTFS, so
        # Shahed_136_white.ini and shahed_136_white.ini are one file.
        mine = {p.relative_to(pack_dir).as_posix().lower() for p in pack_dir.rglob("*.ini")
                if p.parent.name in OVERRIDE_DIRS}
        if not mine:
            continue
        packs.append(pack_dir.name)
        for mod, theirs in ships.items():
            shared = mine & theirs
            if shared:
                out.append((pack_dir.name, mod, shared))
    return out, packs


def read_live(path=LIVE):
    """[(token, enabled)] in the game's order from the capture's numbered
    lines, and the capture time from its first line; None, None without a
    capture."""
    if not path.is_file():
        return None, None
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    rows = re.findall(r"^\s*\d+\.\s+(\S+)\s+(on|OFF)\b", text, re.M)
    when = re.search(r"captured (\S+?)\.?\s*$", text.splitlines()[0] if text else "", re.M)
    return [(tok, state == "on") for tok, state in rows], (when.group(1) if when else "date unknown")


def live_check(tokens, live, overlap_rules):
    """The live order against the canonical one, and the SEST overrides it loses.

    tokens: the canonical order. live: [(token, enabled)] as read_live gives
    it. overlap_rules: [(pack, mod, shared)] from overlaps(). Returns
    (lines, broken): lines describe the drift; broken names every SEST
    override the live order loses, empty when none is lost. SEST's slot is
    SEST_Integration or SEST's own Workshop item; an entry the player has
    disabled does not load and so cannot outrank anything.
    """
    live_tokens = [t for t, _ in live]
    enabled = {t for t, on in live if on}
    pos = {t: i for i, t in enumerate(live_tokens)}
    canon = set(tokens)
    missing = [t for t in tokens if t not in pos]
    extra = [t for t in live_tokens if t not in canon]
    shared_canon = [t for t in tokens if t in pos]
    shared_live = [t for t in live_tokens if t in canon]
    off = [t for t, on in live if not on]
    lines = [f"canonical but not live ({len(missing)}): {', '.join(missing) or '-'}",
             f"live but not canonical ({len(extra)}): {', '.join(extra) or '-'}",
             "order of shared entries: " + ("same as canonical" if shared_canon == shared_live
                                            else "DIFFERENT - the game has reordered them"),
             f"disabled in game ({len(off)}): {', '.join(off) or '-'}"]
    is_sest = lambda t: t.startswith("SEST_") or t in SEST_OWN   # noqa: E731
    sest = [t for t in live_tokens if t == DIST_TOKEN or t in SEST_OWN]
    sest_on = [t for t in sest if t in enabled]
    if not sest_on:
        return lines, ["no enabled SEST entry in the live order"
                       + (f" ({', '.join(sest)} listed but disabled)" if sest else
                          f" (neither {DIST_TOKEN} nor {', '.join(sorted(SEST_OWN))} is listed)")
                       + " - every SEST override is lost"]
    spos = min(pos[t] for t in sest_on)
    lines.append(f"SEST in the live order: {', '.join(sest_on)} at #{spos+1}"
                 + (" (SEST's own Workshop item stands in for SEST_Integration)"
                    if sest_on[0] in SEST_OWN else ""))
    broken, named = [], set()
    for pack, mod, shared in overlap_rules:
        if mod in enabled and pos[mod] < spos:
            named.add(mod)
            broken.append(f"{pack} (live #{spos+1}, as {sest_on[0]}) is BELOW {mod_name(mod)} (live #{pos[mod]+1})\n"
                          f"        {contested_text(shared)}")
    for t in live_tokens:
        if t in enabled and pos[t] < spos and not is_sest(t) and t not in named:
            broken.append(f"{mod_name(t)} (live #{pos[t]+1}) sits above SEST (live #{spos+1})\n"
                          f"        SEST must be first in the live list too")
    return lines, broken


def main():
    tokens = [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt")
              .read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.startswith("#")]
    rank = {t: i for i, t in enumerate(tokens)}

    problems, checked = global_renames(), 0
    rules, override_packs = overlaps()
    for pack in override_packs:
        if rank.get(pack, rank.get(DIST_TOKEN)) is None:
            problems.append(f"{pack} ships override files but is in the load order "
                            f"neither directly nor via {DIST_TOKEN}")
    for pack, mod, shared in rules:
        pos = rank.get(pack, rank.get(DIST_TOKEN))
        if pos is None or mod not in rank:
            continue
        checked += 1
        if pos > rank[mod]:
            problems.append(f"{pack} (#{pos+1}) is BELOW {mod_name(mod)} (#{rank[mod]+1})\n"
                            f"        {contested_text(shared)}")

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
    else:
        print("every SEST pack outranks every mod it shares an override file with")

    # The live order, when the capture holds one. Drift alone is reported;
    # only a lost SEST override fails the check.
    live, when = read_live()
    if live is None:
        print(f"\nlive order: no {LIVE.relative_to(ROOT)} - canonical order checked only")
    else:
        lines, broken = live_check(tokens, live, rules)
        print(f"\nlive order ({LIVE.relative_to(ROOT)}, captured {when}, {len(live)} entries):")
        for line in lines:
            print(f"   {line}")
        if broken:
            print(f"\n{len(broken)} SEST override(s) LOST in the live order:\n")
            for b in broken:
                print(f"   {b}\n")
            print("The PC is running an order in which a SEST patch does nothing. Run\n"
                  "tools\\set-mod-order.ps1 -AddMissing with the game closed, then capture again.")
            if "--strict-live" in sys.argv[1:]:
                sys.exit(1)
            print("(the captured PC's order, not the repo's: reported, failing only with --strict-live)")
        else:
            print("   every SEST override still outranks its target in the live order")
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
