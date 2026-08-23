#!/usr/bin/env python3
"""Generate docs/load-order-full.md — the complete, name-by-name recommended
Mod Manager order for every active subscription plus the SEST local packs.

Tier rules: explicit sequences for tiers 1-3 (where order changes behavior),
type-based assignment for tiers 4-6 (alphabetical within tier — order there
only matters between watchlist entries).

Run from the repo root:  python3 tools/generate_load_order.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
catalog = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))
mods = {m["id"]: m for m in catalog["mods"] if m.get("status") != "unsubscribed"}

# Explicit sequences (order within these lists is the recommendation)
TIER1 = [("anchor-chain", "loader — SeaLifter loads via its preloader alongside")]
TIER1B = [
    ("custom-loadout-editor", "code mod — position not order-sensitive"),
    ("ai-doctrine-overhaul", "code mod — changes AI globally"),
    ("better-tacmap", "code mod — UI"),
]
TIER2 = [
    ("sam-pack", 'author: "top of TOE"'),
    ("pla-land-unit-pack", 'author: "above any other PLA-related mods"'),
    ("dingtools-weapon-pack", 'author: "above any of my mods"'),
    ("euromod-main", "above all Euromod addons"),
    ("modern-plan-systems", "above PLAN ships"),
]
TIER3 = [
    ("us-navy-2027", "above the US mods it edits"),
    ("SEST F-15EX Revamp", "LOCAL — above the F-15EX mod (\"F-15SE\")"),
    ("SEST F-35C JATM", "LOCAL — above every other usn_f-35c source (the four below it here)"),
    ("f-35c-alt-loadouts", "kept for now — MUST stay below SEST F-35C JATM"),
    ("SEST RAAF F-35A JATM", "LOCAL — above the RAAF F-35A mod"),
    ("SEST JMSDF Mogami", "LOCAL — above the Mogami-class Frigate mod"),
    ("murder-hornet", "above other F/A-18E/F sources"),
    ("b-52g-agm-86", "patches the vanilla B-52G"),
    ("tu-95-as-15", "global munition edits — treat as a patch, not an aircraft"),
    ("flight-deck-ops", "above carriers"),
    ("ado-nimitz-2000s", "if kept after the FDO test"),
    ("ground-upgrade-spaa", "edits ground-unit values"),
]
TIER4_EXTRA = [("SEST RAN Fleet", "LOCAL — below the Euromod packs it clones from")]
TIER6_EXTRA = [("SEST RAAF Bases", "LOCAL — additive; bottom by convention")]

explicit = {mid for mid, _ in TIER1 + TIER1B + TIER2 + TIER3}
TIER4_TYPES = {"ship", "submarine"}
TIER4_FORCE = {"us-naval-aviation"}
TIER6_TYPES = {"airbase"}


def title(mid):
    return mods[mid]["title"] if mid in mods else mid


def bucket():
    t4, t5, t6 = [], [], []
    for mid, m in mods.items():
        if mid in explicit:
            continue
        if m["type"] in TIER6_TYPES:
            t6.append(mid)
        elif m["type"] in TIER4_TYPES or mid in TIER4_FORCE:
            t4.append(mid)
        else:
            t5.append(mid)
    key = lambda i: mods[i]["title"].lower()
    return sorted(t4, key=key), sorted(t5, key=key), sorted(t6, key=key)


t4, t5, t6 = bucket()

NOTES = {
    "f-35c-mygo": "kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)",
    "f-a-18ef-mygo": "kept for now — below Murder Hornet",
    "rn-type23-old": "verified additive — position free",
    "rn-lynx-has3-old": "verified additive — position free",
    "e-7a-wedgetail": "KEEP — SEST RAAF Bases dependency",
    "s-70b-2-seahawk": "KEEP — SEST RAN Fleet / RAAF Bases dependency",
    "tu-95ms-x-101": "watchlist: order vs the other Tu-95 mods decides shared files",
    "tu-95k-22": "watchlist: see Tu-95 row",
    "mh-60r-2154545636": "watchlist: order vs other MH-60 sources decides which wins",
    "sa-21-s400": "watchlist: land air-defense overlap",
    "mig-29-family": "watchlist: MiG-29/R-series overlap",
}

lines = [
    "# Full Load Order — every active mod, top to bottom",
    "",
    f"Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — "
    f"{len(mods)} active subscriptions plus 6 SEST local packs. "
    "Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.",
    "",
    "Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are "
    "alphabetical — within them, order only matters between mods flagged in the "
    "conflict watchlist (`docs/conflicts-and-load-order.md`).",
    "",
]

n = 0


def emit(header, entries, annotated=True):
    global n
    lines.append(f"## {header}")
    lines.append("")
    for item in entries:
        n += 1
        if annotated:
            mid, note = item
            lines.append(f"{n}. **{title(mid)}** — {note}")
        else:
            mid = item
            note = NOTES.get(mid)
            lines.append(f"{n}. {title(mid)}" + (f" — *{note}*" if note else ""))
    lines.append("")


emit("Tier 1 — loader", TIER1)
emit("Tier 1b — code mods (Anchor Chain family; position among themselves is free)", TIER1B)
emit("Tier 2 — weapon/system databases (this exact order)", TIER2)
emit("Tier 3 — patches, each above what it modifies (this exact order)", TIER3)
emit("Tier 4 — fleets, ships, submarines", [(m, NOTES[m]) if m in NOTES else m for m in []] or t4, annotated=False)
# insert SEST RAN Fleet right after the Euromod block alphabetically — simplest: append labeled
for mid, note in TIER4_EXTRA:
    n += 1
    lines.insert(len(lines) - 1, f"{n}. **{mid}** — {note}")
emit("Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian", t5, annotated=False)
emit("Tier 6 — airbases last", t6, annotated=False)
for mid, note in TIER6_EXTRA:
    n += 1
    lines.insert(len(lines) - 1, f"{n}. **{mid}** — {note}")

out = ROOT / "docs" / "load-order-full.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {out} — {n} entries")
