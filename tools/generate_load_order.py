#!/usr/bin/env python3
"""Generate docs/load-order-full.md — every active subscription plus the SEST
Integration Pack, grouped by the tier rules the Mod Manager order follows.

It is NOT the load order. The canonical order is data/load-order.tokens.txt,
which tools/set-mod-order.ps1 applies and the pack ships as LOAD-ORDER.txt
for SETUP to write; this page explains that order tier by tier, and its
numbering counts entries within the grouping, not canonical positions.

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

# Tier 0 - the consolidated SEST pack, alone at the very top.
#
# A SEST patch is a whole-file replacement of some mod's unit file. If ANYTHING
# outranks it the patch silently does nothing - no error, nothing in the log,
# the edits just never load. That is exactly how SEST Growler NGJ + MALICE went
# inert: U.S. Navy 2027 was moved up one tier and happened to jump over it.
#
# Fifteen separate packs meant fifteen chances to repeat that on every
# reshuffle. They now deploy as ONE pack (integration/dist/SEST_Integration,
# built by tools/consolidate_packs.py), so tier 0 is a single entry and the
# failure class is gone by construction. tools/check_load_order.py enforces it.
TIER0 = [
    ("SEST Integration Pack", "ALL SEST content consolidated into one entry by "
     "tools/consolidate_packs.py - one Mod Manager slot at the very top carries "
     "every patch, so nothing can jump over an individual pack again"),
]

# Explicit sequences (order within these lists is the recommendation)
TIER1 = [("anchor-chain", "loader — SeaLifter loads via its preloader alongside")]
TIER1B = [
    ("custom-loadout-editor", "code mod — position not order-sensitive"),
    ("better-tacmap", "code mod — UI"),
    ("coordinated-strike-tool", "code mod — time-on-target planner (F8); no game data, one _info.ini"),
    ("automatic-sar", "code mod — right-click SAR; the campaign pays for survivors"),
    ("identify-expanded", "code mod — identification and challenge orders; reads its own ini"),
]
TIER2 = [
    ("sam-pack", 'author: "top of TOE"'),
    ("pla-land-unit-pack", 'author: "above any other PLA-related mods"'),
    ("dingtools-weapon-pack", 'author: "above any of my mods"'),
    ("us-navy-2027", "above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's"),
    ("euromod-main", "above all Euromod addons"),
    ("modern-plan-systems", "above PLAN ships"),
]
TIER3 = [
    ("f-35c-alt-loadouts", "KEEP — SEST F-35C JATM is built from it and loadouts hang a round it ships; must stay below the SEST pack"),
    ("murder-hornet", "above other F/A-18E/F sources"),
    ("b-52g-agm-86", "patches the vanilla B-52G"),
    ("tu-95-as-15", "global munition edits — treat as a patch, not an aircraft"),
    ("flight-deck-ops", "above carriers"),
    ("ado-nimitz-2000s", "KEEP — the campaigns place its carrier (Flight Deck Day)"),
    ("ground-upgrade-spaa", "edits ground-unit values"),
]
TIER4_EXTRA = []   # SEST RAN Fleet moved to TIER0
TIER6_EXTRA = []   # SEST RAAF Bases moved to TIER0

# Tier 7 - bulk arsenals that duplicate better definitions. Red Storm Arsenal
# is 1062 files, 638 of them unique, but the other 13 are copies of files that
# specialist mods do better: its usn_aim_120d runs 1600 kt / 80 nm against
# Murder Hornet's 2667 / 97, with the DragCoefficient=-1 back-solve that cost
# the AIM-424 a third of its range. At the bottom (only RE-power, which shares
# none of its files, sits below it) it keeps its unique content and loses every
# duplicate.
TIER7 = [
    ("red-storm-arsenal", "bottom of the order, above only RE-power (no shared files) - 638 unique files kept, 13 duplicated ones all lose"),
]

explicit = {mid for mid, _ in TIER0 + TIER1 + TIER1B + TIER2 + TIER3 + TIER7}
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
    "rn-type23-old": "verified additive — position free",
    "rn-lynx-has3-old": "verified additive — position free",
    "e-7a-wedgetail": "KEEP — the only source of E7A_Wedgetail, which the campaigns place; SEST RAAF Wedgetail and SEST RAAF Bases depend on it",
    "anzac-class-frigate": "KEEP — the only source of the RAN Anzac hull the campaigns use; since 20 Sep 2026 SEST RAN Fleet patches this mod's own vessels/ran_ffh_anzac.ini, so its real ASMD hull is what loads",
    "pla-plan-plaaf-aep": "Anchorchain expansion — below the loader, with the Euromod one",
    "j-16-multirole": "duplicate platform with Shenyang J-16A — different unit ids, both load",
    "s-70b-2-seahawk": "KEEP — the only source of S-70B-2_Seahawk, which the campaigns place; SEST RAN Fleet and SEST RAAF Bases depend on it",
    "tu-95ms-x-101": "watchlist: order vs the other Tu-95 mods decides shared files",
    "tu-95k-22": "watchlist: see Tu-95 row",
    "mh-60r-2154545636": "keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027",
    "sa-21-s400": "watchlist: land air-defense overlap",
    "rc-135-rivet-joint": "above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges",
    "mig-29-family": "watchlist: MiG-29/R-series overlap",
    "french-air-force": "canonical order puts it at the bottom, above only the PLAAF Aircraft Pack, Red Storm Arsenal and RE-power: its 12 shared rounds are identical or older copies of the MQ-9 Reaper's, the French Navy pack's and the Soviet AEW&C pack's, and it loses every one; the Rafale and Mirage 2000 families load from it alone",
    "plaaf-aircraft-pack": "canonical order puts it third from last, above only Red Storm Arsenal and RE-power: 56 shared files all lost to the specialist PLAAF mods above it, so only its H-6 family, J-7s, J-10A and 39 rounds load; SEST Collection Fixes restores the English loading tips its language_en folder overwrites",
    "armed-merchantmen": "beside Merchants Expanded; no collision with anything, position free",
    "mv-75-cheyenne-ii": "beside the MV-22B; no collision with anything, position free",
    "re-power-resupply": "canonical order puts it last, below Red Storm Arsenal, with which it shares no files",
}

# The canonical order this page explains but does not reproduce.
TOKENS = [t.strip() for t in (ROOT / "data" / "load-order.tokens.txt").read_text(encoding="utf-8").splitlines()
          if t.strip() and not t.lstrip().startswith("#")]
TOKEN_LOCAL = [t for t in TOKENS if not t.isdigit()]
TOKEN_TITLES = {m["workshop_id"]: m["title"] for m in catalog["mods"] if m.get("workshop_id")}
LAST_FOUR = [TOKEN_TITLES.get(t, t) for t in TOKENS[-4:]]

lines = [
    "# Mod tiers — every active mod by tier",
    "",
    f"Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — "
    f"{len(mods)} active subscriptions plus the SEST Integration Pack "
    f"({len(catalog['local_packs'])} packs consolidated). "
    "Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.",
    "",
    "This is a tier grouping, NOT the load order. The canonical Mod Manager order is "
    f"`data/load-order.tokens.txt` ({len(TOKENS)} entries: {' and '.join(TOKEN_LOCAL)} plus the "
    f"{len(TOKENS) - len(TOKEN_LOCAL)} Workshop mods); the pack ships it as LOAD-ORDER.txt and "
    "SETUP writes it. Where the numbering below differs, the canonical order wins (for example, "
    f"its last four are {', '.join(f'**{t}**' for t in LAST_FOUR[:-1])} and **{LAST_FOUR[-1]}**).",
    "",
    "Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are "
    "ordered deliberately (position changes behavior). Tiers 4–6 are listed "
    "alphabetically here — within them, order only matters between mods flagged in the "
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


emit("Tier 0 — the consolidated SEST pack (must stay above everything)", TIER0)
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
emit("Tier 7 — bulk arsenals, below everything they duplicate", TIER7)
for mid, note in TIER6_EXTRA:
    n += 1
    lines.insert(len(lines) - 1, f"{n}. **{mid}** — {note}")

out = ROOT / "docs" / "load-order-full.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {out} — {n} entries")


# data/load-order.preview.txt: the canonical order as the Mod Manager will show
# it, one line per token with the name from that mod's own _info.ini. It reads
# data/load-order.tokens.txt itself, so it cannot fall behind the order the PC
# applies (it was hand-made once and sat at 143 entries while the order grew).
def info_name(token):
    for d in (ROOT / "mods-source" / token, ROOT / "integration" / "dist" / token):
        f = d / "_info.ini"
        if f.exists():
            for line in f.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                if line.startswith("Name="):
                    return line[5:].strip()
    # A mod with no _info.ini of its own (the P-8 Poseidon ships none): the
    # catalog's title is the best name available.
    by_id = {m.get("workshop_id"): m["title"] for m in catalog["mods"]}
    return by_id.get(token, "(not exported)")


tokens = [t.strip() for t in (ROOT / "data" / "load-order.tokens.txt")
          .read_text(encoding="utf-8").splitlines()
          if t.strip() and not t.startswith("#")]
preview = ["# Mod Manager order preview — what data/load-order.tokens.txt applies.",
           "# Generated by tools/generate_load_order.py; do not edit by hand.",
           "# Names come from each mod's own _info.ini (what the Mod Manager shows).",
           ""]
preview += [f"{i:4}. {t:<18}{info_name(t)}" for i, t in enumerate(tokens, 1)]
pout = ROOT / "data" / "load-order.preview.txt"
pout.write_bytes(("\n".join(preview) + "\n").encode("utf-8"))
print(f"wrote {pout} — {len(tokens)} entries")
