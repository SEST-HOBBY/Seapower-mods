#!/usr/bin/env python3
"""Which ship- and submarine-carried rounds can still NOT be replenished, and why.

The replenishment pack's headline claim is that it makes a modern fleet
resupplyable. This is the other half of that sentence: what is left over, named
and reasoned. It reads the SHIPPED state - SEST_Integration wins, then the mod
load order, then vanilla - so it answers "in my install, today", not "in
theory".

A round is reloadable if there is at least one supplier and one carrying hull
where all five gates pass. The gates, and which of them this can decide:

  1. TargetTypes vs the receiver's UnitType.  Every SEST supplier declares
     Vessel,Submarine, so for ship/sub rounds this never discriminates. Checked
     anyway, because a mod's supplier may be narrower.
  2. SupplyRange / MaxOwnVelocity / MaxTargetVelocity / MaxTargets.  SITUATIONAL
     - it depends where the two ships are and how fast they are going, so it is
     deliberately NOT evaluated here. Nothing is reported as blocked by it.
  3. the round's AmmoPoints vs the supplier's MaxAmmoPoints. An ABSENT
     MaxAmmoPoints means no cap, so a round is only blocked when every supplier
     that stocks its category has a ceiling below its price.
  4. the round's SupplyCategory vs the supplier's AccountableAmmunitionCategory
     list. An uncategorised round bypasses this gate entirely.
  5. the receiving launcher: AssociatedMagazine= or ReloadableWithoutMagazine=True.

FLIGHT DECKS ARE A SEPARATE MECHANISM and are deliberately out of scope. Ships
and airbases stock aircraft ordnance through FlightDeck_AccountableAmmunitionCategory_N
- a DIFFERENT key from the supply system's AccountableAmmunitionCategory_N, and
easy to miss because an anchored grep for the latter does not match it. Phoenix,
Ovod, AdvancedARM and PGM are stocked by flight decks and by no supply block at
all; they are not orphans, they are simply not a ship-replenishment question.
This tool only considers rounds a vessel or submarine carries.

    python3 tools/check_reloadable.py

Always exits 0: it is a report, not a gate. Nothing here is necessarily a
defect - the SS-N-19 Granit is blocked on purpose.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration"))
sys.path.insert(0, str(ROOT / "integration" / "missions"))
sys.path.insert(0, str(ROOT / "integration" / "replenishment"))
import build_patch as builder                                    # noqa: E402
from common.ras import _WEAPON_BLOCK, _HAS_MAGAZINE              # noqa: E402
from refine_civ_traffic import winning_file                      # noqa: E402

DIST = ROOT / "integration" / "dist" / "SEST_Integration"
MODS = ROOT / "mods-source"
VANILLA = MODS / "_vanilla" / "original"
CODEC = dict(encoding="utf-8", errors="surrogateescape")

SECTION = re.compile(r"^\[([^\]\n]*)\][^\n]*\n((?:(?!^\[).*(?:\n|$))*)", re.M)
FLAGGED = re.compile(r"^ReloadableWithoutMagazine\s*=\s*True", re.M)


def read(path):
    return Path(path).read_text(**CODEC)


def shipped_hulls():
    """Every vessel/submarine file the game loads, SEST's copy winning."""
    out = {}
    for sub in ("vessels", "submarines"):
        for f in sorted((DIST / sub).glob("*.ini")):
            if not f.stem.endswith("_variants"):
                out[(sub, f.stem)] = f
        for d in sorted(MODS.iterdir()):
            if not d.is_dir():
                continue
            p = d / sub if d.name != "_vanilla" else VANILLA / sub
            if not p.is_dir():
                continue
            for f in sorted(p.glob("*.ini")):
                if not f.stem.endswith("_variants"):
                    out.setdefault((sub, f.stem), f)
    return out


def mod_title(mod):
    """A readable name for a workshop id, from the catalog rather than from
    MODERN_SOURCES - the two mods with the most blocked launchers are exactly
    the ones MODERN_SOURCES does NOT cover, so looking there names nothing."""
    if mod in ("vanilla", "?"):
        return mod
    if mod in builder.MODERN_SOURCES:
        return f"{builder.MODERN_SOURCES[mod]}  ({mod})"
    import json
    cat = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))
    for m in cat["mods"]:
        if m.get("workshop_id") == mod:
            flag = "" if m.get("status") == "active" else f", {m.get('status')}"
            return f"{m['title']}  ({mod}{flag}) - NOT in MODERN_SOURCES"
    return mod


def owner_of(stem):
    for d in sorted(MODS.iterdir()):
        if not d.is_dir():
            continue
        for sub in ("vessels", "submarines"):
            p = d / sub if d.name != "_vanilla" else VANILLA / sub
            if (p / f"{stem}.ini").exists():
                return "vanilla" if d.name == "_vanilla" else d.name
    return "?"


def suppliers():
    """Every live [SupplySystemN] the game loads, with its gates."""
    out, seen = [], set()
    for root in (DIST, MODS):
        for f in sorted(root.rglob("*.ini")):
            if f.parent.name not in ("vessels", "submarines", "land_units"):
                continue
            if f.stem in seen:
                continue
            text = read(f)
            blocks = re.findall(r"^\[SupplySystem\d+\][^\n]*\n((?:(?!^\[).*(?:\n|$))*)",
                                text, re.M)
            if not blocks:
                continue
            seen.add(f.stem)
            for body in blocks:
                targets = re.search(r"^TargetTypes=([^\n/]*)", body, re.M)
                cap = re.search(r"^MaxAmmoPoints=([\d.]+)", body, re.M)
                out.append(dict(
                    unit=f.stem,
                    targets={t.strip() for t in (targets.group(1) if targets else "").split(",")
                             if t.strip()},
                    cap=float(cap.group(1)) if cap else None,
                    cats=set(re.findall(r"^AccountableAmmunitionCategory_\d+=([^,\n]+)",
                                        body, re.M))))
    return out


def facts(rid):
    """(AmmoPoints, SupplyCategory) for the copy the game loads.

    Checks the pack's own ammunition/ first: the metering adds SupplyCategory
    and the restorations add AmmoPoints, and both are invisible to
    winning_ammo(), which only ever looks at mods-source.
    """
    own = DIST / "ammunition" / f"{rid}.ini"
    base = builder.ammo_facts(rid)
    points = base[0] if base else None
    category = None
    if base and base[3]:
        src = winning_file(f"ammunition/{rid}.ini")
        m = re.search(r"^SupplyCategory\s*=\s*([^\s/]+)", read(src), re.M) if src else None
        category = m.group(1) if m else "?"
    if own.exists():
        text = read(own)
        p = re.search(r"^AmmoPoints\s*=\s*([^\s/]+)", text, re.M)
        c = re.search(r"^SupplyCategory\s*=\s*([^\s/]+)", text, re.M)
        points = p.group(1) if p else points
        category = c.group(1) if c else category
    return points, category, base is not None


def carried_rounds(hulls):
    """rid -> how it is held, across every ship and submarine.

    A round counts as REACHABLE if any holder anywhere is magazine-fed or
    carries the reload flag; gate 5 blocks it only when every holder in the
    whole collection is a bare, unflagged launcher.
    """
    held = collections.defaultdict(lambda: {"ok": 0, "bare": 0, "hulls": set(), "sub": False})
    for (sub, stem), f in hulls.items():
        text = read(f)
        for name, body in SECTION.findall(text):
            declared = re.search(r"^NumberOfAmmunitionTypes=(\d+)", body, re.M)
            for slot, rid in re.findall(r"^Ammunition(\d+)=(\S+)", body, re.M):
                if declared and int(slot) > int(declared.group(1)):
                    continue          # past the declared count: the engine never reads it
                held[rid]["ok"] += 1
                held[rid]["hulls"].add(stem)
                held[rid]["sub"] |= sub == "submarines"
        for m in _WEAPON_BLOCK.finditer(text):
            block = m.group(0)
            for rid in re.findall(r"^Ammunition=(\S+)", block, re.M):
                key = "ok" if (_HAS_MAGAZINE.search(block) or FLAGGED.search(block)) else "bare"
                held[rid][key] += 1
                held[rid]["hulls"].add(stem)
                held[rid]["sub"] |= sub == "submarines"
    return held


def main():
    if not DIST.is_dir():
        sys.exit("packs not built - run python3 tools/build_all.py first")
    hulls, sup = shipped_hulls(), suppliers()
    ship_sup = [s for s in sup if s["targets"] & {"Vessel", "Submarine"}]
    held = carried_rounds(hulls)

    blocked = collections.defaultdict(list)
    reloadable = 0
    for rid, d in sorted(held.items()):
        points, category, exists = facts(rid)
        if not exists:
            continue              # dangling store; check_dependencies owns it
        row = (rid, points, category, d)
        if not d["ok"]:
            blocked["gate 5 - every launcher is a bare tube with no magazine"].append(row)
            continue
        need = "Submarine" if d["sub"] else "Vessel"
        able = [s for s in ship_sup
                if (need in s["targets"] or "Vessel" in s["targets"])
                and (category is None or category in s["cats"])]
        if not able:
            blocked["gate 4 - no supplier stocks this ordnance category"].append(row)
            continue
        price = float(points) if points else 0.0
        if not any(s["cap"] is None or s["cap"] >= price for s in able):
            blocked["gate 3 - dearer than the ceiling of every supplier that stocks it"] \
                .append(row)
            continue
        reloadable += 1

    total = reloadable + sum(len(v) for v in blocked.values())
    print(f"{len(hulls)} ship/submarine hull files, {len(ship_sup)} live supply system(s)")
    print(f"{total} distinct rounds carried by a ship or submarine")
    print(f"   RELOADABLE                 {reloadable}")
    for why in sorted(blocked):
        print(f"   NOT reloadable  ({len(blocked[why]):>2})  {why.split(' - ', 1)[1]}")

    for why in sorted(blocked):
        rows = sorted(blocked[why], key=lambda r: -r[3]["bare"])
        print(f"\n{why.upper()}  ({len(rows)} round(s))")
        by_owner = collections.defaultdict(list)
        for rid, points, category, d in rows:
            owners = collections.Counter(owner_of(h) for h in d["hulls"])
            by_owner[owners.most_common(1)[0][0]].append((rid, points, category, d))
        for mod in sorted(by_owner, key=lambda m: -sum(r[3]["bare"] for r in by_owner[m])):
            title = mod_title(mod)
            n = sum(r[3]["bare"] for r in by_owner[mod])
            print(f"   {title}  -  {len(by_owner[mod])} round(s), {n} unflagged launcher(s)")
            for rid, points, category, d in by_owner[mod]:
                where = ", ".join(sorted(d["hulls"])[:3])
                more = f" +{len(d['hulls']) - 3}" if len(d["hulls"]) > 3 else ""
                print(f"      {rid:24} {str(points or 'unpriced'):>9}  "
                      f"{(category or '-'):<18} {where}{more}")

    print("\nGate 2 (range, speed, target slots) is situational and is not evaluated: it "
          "depends on\nwhere the two ships are, not on what the round is. Flight-deck "
          "rearming is a separate\nmechanism and is out of scope - see this file's "
          "docstring.")


if __name__ == "__main__":
    main()
