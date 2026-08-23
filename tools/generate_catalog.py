#!/usr/bin/env python3
"""Render docs/mod-catalog.md from data/mod-catalog.json.

Keeps the human-readable catalog mechanically in sync with the machine-readable
one. Run from the repo root:  python3 tools/generate_catalog.py
"""
import json
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACTION_ORDER = [
    ("usa", "United States"),
    ("russia", "Russia / USSR"),
    ("china", "China (PLA/PLAN/PLAAF)"),
    ("europe", "Europe (multinational / Euromod)"),
    ("france", "France"),
    ("italy", "Italy"),
    ("spain", "Spain"),
    ("japan", "Japan"),
    ("australia", "Australia"),
    ("iran", "Iran"),
    ("multi", "Multi-nation packs"),
    ("civilian", "Civilian"),
    ("utility", "Utility / frameworks"),
]
STATUS_BADGE = {"active": "", "deprecated": " ⚠️ **DEPRECATED**", "wip": " 🚧 WIP"}


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def main():
    data = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))
    mods = data["mods"]

    by_faction = OrderedDict((key, []) for key, _ in FACTION_ORDER)
    for mod in mods:
        if mod["faction"] not in by_faction:
            raise ValueError(f"unknown faction {mod['faction']!r} for {mod['title']!r}")
        by_faction[mod["faction"]].append(mod)

    lines = [
        "# Sea Power Mod Catalog",
        "",
        f"{len(mods)} subscribed Workshop mods, grouped by faction. "
        "Generated from `data/mod-catalog.json` by `tools/generate_catalog.py` — edit the JSON, not this file.",
        "",
        "See `docs/conflicts-and-load-order.md` for the conflict watchlist, dependency audit, and recommended mod order.",
        "",
    ]

    for key, label in FACTION_ORDER:
        group = by_faction.get(key, [])
        if not group:
            continue
        lines.append(f"## {label} ({len(group)})")
        lines.append("")
        lines.append("| Mod | Author | Type | Notes |")
        lines.append("|---|---|---|---|")
        for mod in sorted(group, key=lambda m: (m["type"], m["title"].lower())):
            title = cell(mod["title"]) + STATUS_BADGE.get(mod.get("status", "active"), "")
            extra = []
            if mod.get("requires"):
                extra.append("**Requires:** " + "; ".join(mod["requires"]))
            if mod.get("load_order"):
                extra.append("**Load order:** " + mod["load_order"])
            if mod.get("overlaps"):
                extra.append("**Overlaps:** " + "; ".join(mod["overlaps"]))
            note = " ".join([cell(mod.get("notes", ""))] + [cell(e) for e in extra]).strip()
            lines.append(f"| {title} | {cell(mod['author'])} | {cell(mod['type'])} | {note} |")
        lines.append("")

    missing = data.get("known_missing_dependencies", [])
    if missing:
        lines.append("## ⚠️ Known missing / manual dependencies")
        lines.append("")
        for item in missing:
            lines.append(f"- {item}")
        lines.append("")

    out = ROOT / "docs" / "mod-catalog.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out} ({len(mods)} mods)")


if __name__ == "__main__":
    main()
