"""Data-only compatibility with the captured CombatCosts 0.7.1 catalogs.

Never convert Task Force purchase points or ammo_prices.csv scores to USD.
Prices come only from the author's catalogs; missing values stay unknown.
The field precedence below was checked against CostRules.ResolveField in the
captured DLL. It deliberately distinguishes a missing key from a blank key.
"""
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
import json
import re

TRACKER_ID = "3807187341"
KINDS = {
    "weapon": ("ammunition", "weaponcosts", "WeaponCosts", "WeaponCostCategory"),
    "vessel": ("vessels", "vesselcosts", "VesselCosts", "VesselCostCategory"),
    "aircraft": ("aircraft", "aircraftcosts", "AircraftCosts", None),
}
MAX_PRICE = Decimal("1000000000000000")


def read_ini(path):
    """Read scalar fields while tolerating decorative lines in equipment INIs."""
    return parse_ini(Path(path).read_text(encoding="utf-8-sig", errors="replace"))


def parse_ini(text):
    sections, current = {}, ""
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("[") and "]" in line:
            current = line[1:line.index("]")].casefold()
            sections.setdefault(current, {})
        elif "=" in line:
            key, _, value = line.partition("=")
            sections.setdefault(current, {})[key.strip().casefold()] = value.strip()
    return sections


def preference(section, key, fallback):
    value = section.get(key.casefold())
    if value is None or value.casefold() not in ("true", "false"):
        return fallback
    return value.casefold() == "true"


def resolve_field(inline, catalog, reference, field, inline_field=None):
    entry = catalog.get(reference.casefold(), {})
    prefer_list = preference(catalog.get("costs", {}), "OverrideInline", False)
    prefer_list = preference(entry, "OverrideInline", prefer_list)
    prefer_list = preference(entry, "Override" + field, prefer_list)
    own = inline.get((inline_field or field).casefold())
    listed = entry.get(field.casefold())
    first, second = (listed, own) if prefer_list else (own, listed)
    return first if first is not None else second


def price(value):
    if value is None or not re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", value):
        return None
    try:
        amount = Decimal(value)
    except InvalidOperation:
        return None
    return amount if amount.is_finite() and 0 <= amount <= MAX_PRICE else None


def normal_reference(reference):
    """Catalog spelling only: no fuzzy matching or removal of variant suffixes."""
    stem = reference.replace("\\", "/").rsplit("/", 1)[-1]
    return re.sub(r"[^a-z0-9]", "", stem.casefold())


def inventory(root):
    """Winning unit configs: SEST source packs, ordered Workshop mods, vanilla."""
    root = Path(root)
    registry = json.loads((root / "data/mod-catalog.json").read_text())
    providers = [(p["folder"], root / p["source"] / p["folder"])
                 for p in registry["local_packs"] if p["folder"] != "SEST_Combat_Costs"]
    tokens = (root / "data/load-order.tokens.txt").read_text().splitlines()
    providers += [(t.strip(), root / "mods-source" / t.strip()) for t in tokens
                  if t.strip().isdigit()]
    providers.append(("vanilla", root / "mods-source/_vanilla/original"))
    units = {kind: {} for kind in KINDS}
    for owner, base in providers:
        for kind, (folder, _, _, _) in KINDS.items():
            for path in sorted((base / folder).glob("*.ini")):
                uid = path.stem
                if uid.casefold().endswith(("_variants", "_squadrons", "_loadouts")):
                    continue
                data = read_ini(path)
                text = path.read_text(encoding="utf-8-sig", errors="replace")
                alias = re.search(r"^#!alias\s+([^\r\n]+)", text, re.M)
                if "general" not in data and not alias:
                    continue
                if kind == "weapon" and not data.get("general", {}).get("type") and not alias:
                    continue
                units[kind].setdefault(uid.casefold(), {
                    "id": uid, "owner": owner, "path": path,
                    "general": data.get("general", {}),
                    "alias": alias[1].strip() if alias else None,
                })
    return units


def effective_general(unit, units, seen=()):
    own = unit["general"]
    if not unit["alias"]:
        return own
    if unit["id"].casefold() in seen:
        raise ValueError("Equipment alias cycle: " + " -> ".join((*seen, unit["id"])))
    donor = Path(unit["alias"].replace("\\", "/")).stem.casefold()
    # A self alias means the next provider down the native order. Its inline
    # fields cannot be inferred from the already collapsed winning index.
    # None of the emitted mappings depend on such an alias's inline fields.
    if donor not in units or donor == unit["id"].casefold():
        return own
    return dict(effective_general(units[donor], units, (*seen, unit["id"].casefold())), **own)


def build(root, mappings):
    root = Path(root)
    units = inventory(root)
    catalogs = {kind: read_ini(root / "mods-source" / TRACKER_ID / "systems" / (info[1] + ".ini"))
                for kind, info in KINDS.items()}
    extensions, receipts, coverage = {}, [], {}
    for kind, (_, _, historical, category_key) in KINDS.items():
        catalog = catalogs[kind]
        manual = {m["target"].casefold(): m for m in mappings.get(kind, [])}
        if len(manual) != len(mappings.get(kind, [])):
            raise ValueError(kind + ": duplicate reviewed mappings")
        unused = manual.keys() - units[kind].keys()
        if unused:
            raise ValueError(kind + ": reviewed targets no longer exist: " + ", ".join(sorted(unused)))
        normalized = defaultdict(list)
        for key, fields in catalog.items():
            if historical.casefold() in fields or "currentyearcost" in fields:
                normalized[normal_reference(key)].append(key)
        extra = {}
        for uid, unit in sorted(units[kind].items()):
            if uid in catalog:
                continue  # An existing author entry, including blanks, is authoritative.
            source, basis, category = None, None, None
            if uid in manual:
                item = manual[uid]
                source, basis, category = item.get("source"), item["basis"], item.get("category")
                if source and source.casefold() not in catalog:
                    raise ValueError(kind + ": reviewed source disappeared: " + source)
            else:
                candidates = normalized.get(normal_reference(uid), [])
                # Two different prices for the same normalized spelling are
                # ambiguous. Keep them unknown rather than choose one.
                signatures = {tuple(catalog[k].get(f.casefold()) for f in
                              (historical, "CurrentYearCost", "Category")) for k in candidates}
                if candidates and len(signatures) == 1:
                    source = sorted(candidates)[0]
                    basis = "Same catalog reference after path/punctuation normalization"
            if basis is None:
                continue
            donor = catalog[source.casefold()] if source else {}
            fields = {}
            for key in (historical, "CurrentYearCost"):
                value = donor.get(key.casefold(), "")
                if value and price(value) is None:
                    raise ValueError(f"{source}: invalid source {key}={value!r}")
                fields[key] = value
            if category_key:
                fields["Category"] = category or donor.get("category", "Other")
            extra[uid] = fields
            receipts.append({"kind": kind, "target": unit["id"], "source": source,
                             "basis": basis, "fields": fields})
        extensions[kind] = extra
        merged = {k: dict(v) for k, v in catalog.items()}
        merged.update({uid: {k.casefold(): v for k, v in fields.items()} for uid, fields in extra.items()})
        counts = {"eligible": len(units[kind]), "historical_known": 0, "current_known": 0,
                  "sest_eligible": 0, "sest_historical_known": 0, "sest_current_known": 0}
        unknown = []
        for uid, unit in sorted(units[kind].items()):
            own = effective_general(unit, units[kind])
            is_sest = unit["owner"].startswith("SEST_")
            counts["sest_eligible"] += int(is_sest)
            known = []
            for label, field in (("historical", historical), ("current", "CurrentYearCost")):
                ok = price(resolve_field(own, merged, uid, field)) is not None
                known.append(ok)
                counts[label + "_known"] += int(ok)
                counts["sest_" + label + "_known"] += int(ok and is_sest)
            if not all(known):
                unknown.append({"id": unit["id"], "owner": unit["owner"],
                                "historical_unknown": not known[0], "current_unknown": not known[1]})
        coverage[kind] = {**counts, "unknown": unknown}
    return {"extensions": extensions, "entries": receipts, "coverage": coverage}


def render_catalog(kind, result):
    lines = [f"#!extend systems/{KINDS[kind][1]}.ini",
             "; Generated SEST compatibility. USD values retain the author's reference basis.",
             "; Blank prices are unknown. Existing catalogs and inline preferences are preserved."]
    by_target = {(e["kind"], e["target"].casefold()): e for e in result["entries"]}
    for uid, fields in sorted(result["extensions"][kind].items()):
        entry = by_target[(kind, uid)]
        lines += ["", "; " + entry["basis"], "; Source catalog section: " + (entry["source"] or "none; intentionally unknown"),
                  "[" + entry["target"] + "]"]
        lines += [f"{key}={value}" for key, value in fields.items()]
    return "\n".join(lines) + "\n"
