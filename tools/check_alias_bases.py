#!/usr/bin/env python3
"""Resolve every #!alias base in the collection and flag what the game would choke on.

A unit file that starts with `#!alias vessels/x.ini` is a patch layered on
another mod's hull: the game loads the base, then applies the patch's sections.
Two mods can drift apart between Steam updates - the base mod renames a hull,
the patch mod has not caught up - and the result is not a warning but a hard
crash at startup: "KeyNotFoundException: The given key 'AirGroup' was not
present in the dictionary", because the patch's own [FlightDeck] section asks
for an air group the missing base would have supplied. That is exactly what
Modern US Navy v567 (Flight III renamed to usn_ddg_burke_125, 18 Sep 2026) did
to U.S. Navy 2027's usn_ddg_arleigh_flt3_2027, and the game's own log names the
symptom, not the file.

So this walks the aliases the way the game does, through the load order and
across chains (an alias whose base is itself an alias), and reports:

  MISSING BASE   the alias target is not provided by any enabled mod
  NO AIRGROUP    the resolved hull has a [FlightDeck] but no [AirGroup]
  MISSING AMMO   an Ammunition= id the resolved hull fires has no file
                 (the "Could not find ini file path" spam in Player.log;
                 not fatal, the launcher just spawns empty)

    python3 tools/check_alias_bases.py          # exit 1 on MISSING BASE / NO AIRGROUP

Run it after every export. It only knows what mods-source/ knows, so a stale
export passes while the game crashes - export first, then check.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import winning_file  # noqa: E402

UNIT_DIRS = ("vessels", "submarines", "land_units", "aircraft")
ALIAS = re.compile(r"^﻿?#!alias\s+(\S+)")
AIRGROUP = re.compile(r"^\[AirGroup\]", re.M)
FLIGHTDECK = re.compile(r"^\[FlightDeck\]", re.M)
AMMO = re.compile(r"^Ammunition\d*=([A-Za-z0-9_.\-]+)", re.M)


def provider(path):
    parts = path.parts
    if "mods-source" in parts:
        return parts[parts.index("mods-source") + 1]
    if "integration" in parts:
        return parts[parts.index("integration") + 2]
    return "?"


def resolve(path, depth=0):
    """(text of the whole chain, [chain names], missing target or None)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    names = [path.name]
    m = ALIAS.match(text)
    if not m:
        return text, names, None
    target = m.group(1).replace("\\", "/")
    if depth >= 8:
        return text, names, f"{target} (alias chain deeper than 8)"
    base = winning_file(target)
    if base is None:
        return text, names, target
    bt, bnames, missing = resolve(base, depth + 1)
    return text + "\n" + bt, names + bnames, missing


def main():
    fatal, soft, checked = [], [], 0
    seen = set()
    roots = list((ROOT / "mods-source").glob("*/*")) + list((ROOT / "integration").glob("*/SEST_*/*"))
    for d in sorted(roots):
        if not d.is_dir() or d.name.lower() not in UNIT_DIRS:
            continue
        for f in sorted(d.glob("*.ini")):
            if f.name.endswith("_variants.ini"):
                continue
            key = f"{d.name}/{f.name}".lower()
            if key in seen:
                continue
            seen.add(key)
            win = winning_file(f"{d.name}/{f.name}")
            if win is None:
                continue
            text, chain, missing = resolve(win)
            if not ALIAS.match(text):
                continue            # plain hulls are the base mod's business
            checked += 1
            where = f"{provider(win)}/{d.name}/{f.name}"
            if missing:
                fatal.append(f"MISSING BASE  {where}: alias chain {' -> '.join(chain)} -> {missing}")
                continue
            if FLIGHTDECK.search(text) and not AIRGROUP.search(text):
                fatal.append(f"NO AIRGROUP   {where}: {' -> '.join(chain)} has a flight deck and no air group")
            for ammo in sorted(set(AMMO.findall(text))):
                if winning_file(f"ammunition/{ammo}.ini") is None:
                    soft.append(f"MISSING AMMO  {where}: fires {ammo} and no enabled mod defines it")
    print(f"checked {checked} alias unit(s)")
    for line in soft:
        print("   " + line)
    if fatal:
        print(f"\n{len(fatal)} alias(es) the game cannot load:\n")
        for line in fatal:
            print("   " + line)
        sys.exit(1)
    print("every alias base resolves and every aliased flight deck has an air group")


if __name__ == "__main__":
    main()
