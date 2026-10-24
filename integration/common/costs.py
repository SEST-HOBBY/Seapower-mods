"""Data-only compatibility with the captured CombatCosts 0.7.1 catalogs.

Never convert Task Force purchase points or ammo_prices.csv scores to USD.
Prices come from the author's catalogs, copied exactly, or from a SEST
researched estimate (23 Oct 2026): an explicit figure with its method, year
and sources, labelled as SEST's in the shipped catalog. Missing values stay
unknown. The field precedence below was checked against CostRules.ResolveField
in the captured DLL. It deliberately distinguishes a missing key from a blank key.
SEST's runtime plugin ports the same rules (integration/runtime-fixes/
CombatPrices.cs); both are checked against integration/runtime-fixes/tests/
cost_precedence.tsv, and costs.py also against cost_field_origin.tsv and
cost_exclusion.tsv.

cost_list() renders docs/combat-costs/cost-list.md and cost-list.csv: every
unit SEST ships or its missions field, with its price and where the price
comes from, the gaps and the next research batch.
"""
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
import csv
import io
import json
import re

TRACKER_ID = "3807187341"
KINDS = {
    "weapon": ("ammunition", "weaponcosts", "WeaponCosts", "WeaponCostCategory"),
    "vessel": ("vessels", "vesselcosts", "VesselCosts", "VesselCostCategory"),
    "aircraft": ("aircraft", "aircraftcosts", "AircraftCosts", None),
}
MAX_PRICE = Decimal("1000000000000000")
# How a researched figure was reached, in the tracker README's order of
# preference for CurrentYearCost, plus the two the catalog itself uses.
METHODS = ("published price", "comparable recent purchase", "documented replacement estimate",
           "CPI conversion", "model estimate")
ESTIMATE_KEYS = {"historical", "historical_year", "historical_method",
                 "current", "current_year", "current_method", "note"}
# The campaign pack's own output; the list never reads the consolidated dist.
CAMPAIGN = Path("integration/campaign/SEST_Campaign")


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


def field_origin(inline, catalog, reference, field, inline_field=None):
    """(value, "inline" or "list"): the value the tracker selects, and its side."""
    entry = catalog.get(reference.casefold(), {})
    prefer_list = preference(catalog.get("costs", {}), "OverrideInline", False)
    prefer_list = preference(entry, "OverrideInline", prefer_list)
    prefer_list = preference(entry, "Override" + field, prefer_list)
    own = (inline.get((inline_field or field).casefold()), "inline")
    listed = (entry.get(field.casefold()), "list")
    first, second = (listed, own) if prefer_list else (own, listed)
    return first if first[0] is not None else second


def resolve_field(inline, catalog, reference, field, inline_field=None):
    return field_origin(inline, catalog, reference, field, inline_field)[0]


def price(value):
    """CostRules.ParsePrice: ASCII digits and one point (decimal.TryParse, AllowDecimalPoint), 0 to 1e15."""
    if value is None or not re.fullmatch(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", value):
        return None
    try:
        amount = Decimal(value)
    except InvalidOperation:
        return None
    return amount if amount.is_finite() and 0 <= amount <= MAX_PRICE else None


# CostRules.Resolve's fallback table: with no category of their own, only these
# types (and Missile, which always gets one) leave the tracker's default, Ignore.
FALLBACK_TYPES = ("asroc", "rbu", "airdepthcharge", "torpedo", "bomb", "projectile", "aerialrocket", "mlrs")


def valid_category(category):
    """CostRules.ValidCategory: 1 to 20 UTF-16 units of A-Z, a-z, decimal digits, space, '-' or '_'."""
    return (bool(category) and not category.isspace() and len(category) <= 20
            and all("A" <= c <= "Z" or "a" <= c <= "z" or c in " -_" or (ord(c) <= 0xFFFF and c.isdecimal())
                    for c in category))


def weapon_excluded(category, ammo_type):
    """True when CombatCosts 0.7.1 leaves a round at its default category, Ignore.

    Such a round is not counted at all: no price and no "+ ?". `category` is
    the resolved Category/WeaponCostCategory value (None or blank for none);
    `ammo_type` is the game's Ammunition.Type name.
    """
    if category:
        return not valid_category(category) or category.casefold() == "ignore"
    if ammo_type.casefold() == "missile":
        return False
    return ammo_type.lower() not in FALLBACK_TYPES


def normal_reference(reference):
    """Catalog spelling only: no fuzzy matching or removal of variant suffixes."""
    stem = reference.replace("\\", "/").rsplit("/", 1)[-1]
    return re.sub(r"[^a-z0-9]", "", stem.casefold())


def providers(root):
    """[(owner, folder)] in winning order: SEST source packs, ordered Workshop mods, vanilla."""
    root = Path(root)
    registry = json.loads((root / "data/mod-catalog.json").read_text(encoding="utf-8"))
    found = [(p["folder"], root / p["source"] / p["folder"])
             for p in registry["local_packs"] if p["folder"] != "SEST_Combat_Costs"]
    tokens = (root / "data/load-order.tokens.txt").read_text(encoding="utf-8").splitlines()
    found += [(t.strip(), root / "mods-source" / t.strip()) for t in tokens if t.strip().isdigit()]
    found.append(("vanilla", root / "mods-source/_vanilla/original"))
    return found


def land_inventory(root):
    """{uid: {"id", "owner"}}: the winning land unit files, in the same order as inventory().

    The tracker prices no land platform. This only names the land units a
    research.json record may describe (24 Oct 2026).
    """
    found = {}
    for owner, base in providers(root):
        for path in sorted((base / "land_units").glob("*.ini")):
            if not path.stem.casefold().endswith(("_variants", "_squadrons", "_loadouts")):
                found.setdefault(path.stem.casefold(), {"id": path.stem, "owner": owner})
    return found


def inventory(root):
    """Winning unit configs: SEST source packs, ordered Workshop mods, vanilla."""
    units = {kind: {} for kind in KINDS}
    for owner, base in providers(root):
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


def _one_line(text):
    return isinstance(text, str) and bool(text.strip()) and not set(text) & {"\n", "\r"}


def estimate_fields(kind, item, kind_info=None):
    """Catalog fields of a SEST researched estimate, or ValueError.

    An estimate is SEST's own figure, so it has to say how it was reached:
    each price it gives parses as positive USD and carries a four-digit year
    and a method from METHODS; it has a basis and at least one source with a
    title and a URL. It names no tracker catalog section, because a figure
    copied from one is a reviewed mapping and must stay one. Every text field
    is a single line: it is rendered into INI comments, where a line break
    would turn the rest of the text into a key.
    """
    where = f"{kind} {item.get('target')}"
    kind_info = kind_info or KINDS[kind]
    if "source" in item:
        raise ValueError(where + ": an estimate must not name a source catalog section; "
                         "a copied catalog price is a reviewed mapping")
    est = item.get("estimate")
    if not isinstance(est, dict) or set(est) - ESTIMATE_KEYS:
        raise ValueError(where + ": estimate keys must be among " + ", ".join(sorted(ESTIMATE_KEYS)))
    if not _one_line(item.get("basis")):
        raise ValueError(where + ": an estimate needs a one-line basis")
    sources = item.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(where + ": an estimate needs at least one source")
    for source in sources:
        if not isinstance(source, dict) or not (_one_line(source.get("title"))
                                                and _one_line(source.get("url"))):
            raise ValueError(where + ": every source needs a one-line title and URL")
    if "note" in est and not _one_line(est["note"]):
        raise ValueError(where + ": the note must be one line")
    fields = {}
    for label, key in (("historical", kind_info[2]), ("current", "CurrentYearCost")):
        value = est.get(label, "")
        if value != "":
            amount = price(value) if isinstance(value, str) else None
            if not amount:
                raise ValueError(f"{where}: {label} price {value!r} is not a positive USD amount")
            if not re.fullmatch(r"(?:19|20)\d\d", str(est.get(label + "_year", ""))):
                raise ValueError(f"{where}: the {label} price needs a four-digit year")
            if est.get(label + "_method") not in METHODS:
                raise ValueError(f"{where}: the {label} method must be one of: " + ", ".join(METHODS))
        elif label + "_year" in est or label + "_method" in est:
            raise ValueError(f"{where}: a {label} year or method without a {label} price")
        fields[key] = value
    if not any(fields.values()):
        raise ValueError(where + ": an estimate needs at least one price")
    if kind_info[3]:
        category = item.get("category")
        if not _one_line(category) or not re.fullmatch(r"[A-Za-z0-9 _-]{1,20}", category, re.ASCII):
            raise ValueError(where + ": an estimate needs a category of at most 20 characters, using ASCII letters, digits, spaces, underscore or hyphen")
        fields["Category"] = category
    return fields


def _build(root, mappings):
    root = Path(root)
    units = inventory(root)
    catalogs = {kind: read_ini(root / "mods-source" / TRACKER_ID / "systems" / (info[1] + ".ini"))
                for kind, info in KINDS.items()}
    extensions, receipts, coverage, merged_all = {}, [], {}, {}
    for kind, (_, _, historical, category_key) in KINDS.items():
        catalog = catalogs[kind]
        manual = {m["target"].casefold(): m for m in mappings.get(kind, [])}
        if len(manual) != len(mappings.get(kind, [])):
            raise ValueError(kind + ": duplicate reviewed mappings")
        unused = manual.keys() - units[kind].keys()
        if unused:
            raise ValueError(kind + ": reviewed targets no longer exist: " + ", ".join(sorted(unused)))
        # Every estimate is checked, even one an author entry now overrides.
        estimates = {uid: estimate_fields(kind, m) for uid, m in manual.items() if "estimate" in m}
        normalized = defaultdict(list)
        for key, fields in catalog.items():
            if historical.casefold() in fields or "currentyearcost" in fields:
                normalized[normal_reference(key)].append(key)
        extra = {}
        for uid, unit in sorted(units[kind].items()):
            if uid in catalog:
                continue  # An existing author entry, including blanks, is authoritative.
            if uid in estimates:
                item = manual[uid]
                extra[uid] = estimates[uid]
                receipts.append({"kind": kind, "target": unit["id"], "source": None,
                                 "origin": "estimate", "basis": item["basis"],
                                 "fields": estimates[uid], "estimate": item["estimate"],
                                 "sources": item["sources"]})
                continue
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
                             "origin": "mapping" if uid in manual else "normalized",
                             "basis": basis, "fields": fields})
        extensions[kind] = extra
        merged = {k: dict(v) for k, v in catalog.items()}
        merged.update({uid: {k.casefold(): v for k, v in fields.items()} for uid, fields in extra.items()})
        merged_all[kind] = merged
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
    result = {"extensions": extensions, "entries": receipts, "coverage": coverage}
    context = {"root": root, "units": units, "catalogs": catalogs, "merged": merged_all,
               "receipts": {(e["kind"], e["target"].casefold()): e for e in receipts}}
    return result, context


def build(root, mappings):
    return _build(root, mappings)[0]


def estimate_comments(kind, entry, kind_info=None):
    """Comment lines naming an estimate's methods, years and sources."""
    est = entry["estimate"]
    lines = []
    for label, key in (("Historical", (kind_info or KINDS[kind])[2]), ("Current", "CurrentYearCost")):
        part = label.casefold()
        if est.get(part):
            year = "reference year" if part == "historical" else "source year"
            lines.append(f"; {label} ({key}): {est[part + '_method']}, {year} {est[part + '_year']}")
        else:
            lines.append(f"; {label} ({key}): unknown")
    if est.get("note"):
        lines.append("; Note: " + est["note"])
    seen = set()
    for source in entry["sources"]:
        if source["url"] not in seen:   # one line per page, under its first title
            seen.add(source["url"])
            lines.append(f"; Source: {source['title']} - {source['url']}")
    return lines


def render_catalog(kind, result):
    lines = [f"#!extend systems/{KINDS[kind][1]}.ini",
             "; Generated SEST compatibility. Mapped USD values retain the author's reference basis.",
             "; SEST researched estimates are SEST's figures, each with its method, year and sources.",
             "; Blank prices are unknown. Existing catalogs and inline preferences are preserved."]
    by_target = {(e["kind"], e["target"].casefold()): e for e in result["entries"]}
    for uid, fields in sorted(result["extensions"][kind].items()):
        entry = by_target[(kind, uid)]
        if entry.get("estimate"):
            lines += ["", "; SEST researched estimate, not a tracker author price: " + entry["basis"]]
            lines += estimate_comments(kind, entry)
            lines += ["; Source catalog section: none", "[" + entry["target"] + "]"]
        else:
            lines += ["", "; " + entry["basis"],
                      "; Source catalog section: " + (entry["source"] or "none; intentionally unknown"),
                      "[" + entry["target"] + "]"]
        lines += [f"{key}={value}" for key, value in fields.items()]
    return "\n".join(lines) + "\n"


# --- the cost list --------------------------------------------------------

# Next-batch groups by the round's [General] Type, in the order the owner
# asked for them; anything else falls under "Other".
GROUPS = (
    ("Missiles", ("missile", "asroc")),
    ("Bombs and depth charges", ("bomb", "airdepthcharge")),
    ("Torpedoes", ("torpedo",)),
    ("Guns and projectiles", ("projectile",)),
    ("Rockets", ("aerialrocket", "mlrs", "rbu")),
    ("Fuel tanks", ("fueltank",)),
    ("Containers", ("container",)),
    ("Chaff", ("chaff",)),
    ("Noisemakers and decoys", ("noisemaker", "moss")),
    ("Sonobuoys", ("sonobuoy",)),
)
LAND_NOTE = "not priced: the tracker does not price land platforms"


def fielded_units(root, units):
    """{"vessel"|"aircraft": {uid: [where, ...]}} that SEST_Campaign's output places.

    A mission names a unit as Type=<id> or, for an air group on a deck or a
    field, <id>=SquadronN,count; a campaign roster as <id>=... . The label is
    the mission folder or campaign the file sits in.
    """
    base = Path(root) / CAMPAIGN
    files = []
    for sub in ("missions", "campaigns"):
        if not (base / sub).is_dir():
            raise FileNotFoundError(f"{CAMPAIGN / sub} is missing: build SEST_Campaign first")
        files += sorted((base / sub).rglob("*.ini"))
    found = {"vessel": defaultdict(set), "aircraft": defaultdict(set)}
    for path in files:
        rel = path.relative_to(base)
        where = rel.parts[1] if len(rel.parts) > 2 else path.stem
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        names = re.findall(r"^\s*Type\s*=\s*([^\s/;#|,]+)", text, re.M)
        names += re.findall(r"^\s*([A-Za-z0-9_.\-]+)\s*=\s*Squadron\d+", text, re.M)
        if path.name.casefold().endswith("_roster.ini"):
            names += re.findall(r"^\s*([A-Za-z0-9_.\-]+)\s*=", text, re.M)
        for name in names:
            for kind in found:
                if name.casefold() in units[kind]:
                    found[kind][name.casefold()].add(where)
                    break
    return {kind: {uid: sorted(w) for uid, w in sorted(v.items())} for kind, v in found.items()}


def unit_sections(unit, units_kind, depth=0):
    """A unit file's sections, laid over its #!alias base key by key."""
    sections = read_ini(unit["path"])
    if not unit["alias"] or depth > 4:
        return sections
    donor = units_kind.get(Path(unit["alias"].replace("\\", "/")).stem.casefold())
    if donor is None or donor["id"].casefold() == unit["id"].casefold():
        return sections
    merged = unit_sections(donor, units_kind, depth + 1)
    for name, keys in sections.items():
        merged[name] = dict(merged.get(name, {}), **keys)
    return merged


def carried_stores(unit, units_kind):
    """Every store a unit's file can load, across all the fits it offers.

    The spellings follow integration/campaign/build_pack.py stores():
    Station<n>=, Ammunition<n>= and a bare Ammunition= in WeaponSystem and
    magazine sections, a fit's sections only when the unit offers the fit,
    and a DateBased_<name> pylon expanded to every round its dates name. A
    magazine is any section a weapon system names as its AssociatedMagazine
    or that declares NumberOfAmmunitionTypes: hulls call them TorpedoRoom,
    NoisemakerMagazine or ChaffMagazine as often as WeaponMagazine<x>.
    """
    sections = unit_sections(unit, units_kind)
    offered = next(([f.strip().casefold() for f in keys["availableloadouts"].split(",") if f.strip()]
                    for keys in sections.values() if "availableloadouts" in keys), [])
    dated = {key: [part.split(",", 1)[1].strip() for part in value.split("|") if "," in part]
             for keys in sections.values() for key, value in keys.items()
             if key.startswith("datebased_")}
    magazines = {keys["associatedmagazine"].casefold() for keys in sections.values()
                 if keys.get("associatedmagazine")}
    out = set()
    for name, keys in sections.items():
        if not (name.startswith(("weaponsystem", "weaponmagazine")) or name in magazines
                or "numberofammunitiontypes" in keys):
            continue
        fit = next((f for f in sorted(offered, key=len, reverse=True) if name.endswith(f)), None)
        if fit is None and re.fullmatch(r"weaponsystem\d+[a-z][a-z0-9_-]*", name):
            continue    # a fit this unit does not offer
        for key, value in keys.items():
            if re.fullmatch(r"station\d+|ammunition\d*", key):
                store = value.split("|")[0].strip()
                out.update(dated.get(store.casefold(), [store]))
    return sorted(s for s in out if s)


def pod_rounds(weapon, weapons):
    """The rounds a Container (a rocket or gun pod) holds: its [Ammunition] entries.

    The tracker charges the rounds a pod fires, not the pod, so the rounds
    inside a carried pod are carried too.
    """
    if effective_general(weapon, weapons).get("type", "").casefold() != "container":
        return []
    held = unit_sections(weapon, weapons).get("ammunition", {})
    return sorted(value.split("|")[0].strip() for key, value in held.items()
                  if re.fullmatch(r"ammunition\d*", key) and value.strip())


def price_status(context, kind, uid):
    """Prices, category and where the tracker's selected prices come from."""
    units = context["units"][kind]
    unit, merged = units[uid], context["merged"][kind]
    own = effective_general(unit, units)
    values, origins = {}, {}
    for label, field in (("historical", KINDS[kind][2]), ("current", "CurrentYearCost")):
        value, origin = field_origin(own, merged, uid, field)
        known = price(value) is not None
        values[label] = value if known else None
        origins[label] = origin if known else (origin if value is not None else None)
    category = ""
    if KINDS[kind][3]:
        category = resolve_field(own, merged, uid, "Category", KINDS[kind][3]) or ""
    receipt = context["receipts"].get((kind, uid))
    in_catalog = uid in context["catalogs"][kind]

    def side(origin):
        if origin == "inline":
            return "inline in unit file"
        if in_catalog:
            return "tracker catalog"
        if receipt and receipt["origin"] == "estimate":
            return "SEST researched estimate"
        return "SEST mapping from " + receipt["source"]

    known = [origins[label] for label in ("historical", "current") if values[label] is not None]
    if known:
        source = " / ".join(sorted({side(o) for o in known}))
    elif "inline" in origins.values():
        source = "unknown: the unit file's inline price is blank or invalid"
    elif in_catalog:
        source = "unknown: the tracker entry is blank"
    elif receipt and receipt["source"]:
        source = f"unknown: SEST mapping keeps {receipt['source']}'s blank"
    elif receipt:
        source = "unknown: SEST records no supported price"
    else:
        source = "unknown: no tracker entry"
    return {"id": unit["id"], "kind": kind, "owner": unit["owner"], "category": category,
            "type": effective_general(unit, units).get("type", ""),
            "historical": values["historical"], "current": values["current"], "from": source}


def land_units(root):
    """[(id, pack)] for the land units SEST's packs ship, by id."""
    root = Path(root)
    registry = json.loads((root / "data/mod-catalog.json").read_text(encoding="utf-8"))
    found = {}
    for pack in registry["local_packs"]:
        for path in sorted((root / pack["source"] / pack["folder"] / "land_units").glob("*.ini")):
            if not path.stem.casefold().endswith(("_variants", "_squadrons", "_loadouts")):
                found.setdefault(path.stem.casefold(), (path.stem, pack["folder"]))
    return [found[k] for k in sorted(found)]


def _usd(value):
    if value is None:
        return "unknown"
    amount = Decimal(value)
    return "0 (free)" if amount == 0 else f"{amount:,}"


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def _table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]
    return out


def _gap(row):
    return [label for label in ("historical", "current") if row[label] is None]


def _priced(entry):
    return any(entry["fields"].get(k) for k in (KINDS[entry["kind"]][2], "CurrentYearCost"))


def _sources(sources):
    return "; ".join(f"{s['title']}: {s['url']}" for s in sources)


def cost_list(root, mappings, research, built=None):
    """(markdown, csv) for docs/combat-costs/: deterministic for the same tree."""
    root = Path(root)
    result, context = built or _build(root, mappings)
    units = context["units"]
    registry = json.loads((root / "data/mod-catalog.json").read_text(encoding="utf-8"))
    titles = {str(m["workshop_id"]): m["title"] for m in registry.get("mods", []) if m.get("workshop_id")}

    def owner(name):
        if name == "vanilla":
            return "Sea Power (stock)"
        return f"{titles[name]} ({name})" if name in titles else name

    # A land research record is kept for reference only: the tracker prices
    # no land platform, so nothing for it is ever shipped.
    land_known = land_inventory(root) if any(i["kind"] == "land" for i in research["items"]) else {}
    researched = {}
    for item in research["items"]:
        kind, uid = item["kind"], item["target"].casefold()
        if not (uid in land_known if kind == "land" else kind in KINDS and uid in units[kind]):
            raise ValueError(f"research.json: {kind} {item['target']} no longer exists")
        if not (_one_line(item.get("why")) and _one_line(item.get("candidate"))
                and _one_line(item.get("decision"))):
            raise ValueError(f"research.json: {item['target']} needs one-line decision, candidate and why")
        if (kind, uid) in researched:
            raise ValueError(f"research.json: {kind} {item['target']} is listed twice")
        if kind in KINDS:
            fields = result["extensions"][kind].get(uid, {})
            if any(fields.get(k) for k in (KINDS[kind][2], "CurrentYearCost")):
                raise ValueError(f"research.json: {item['target']} is shipped with a price")
        researched[(kind, uid)] = item

    owned = {kind: [price_status(context, kind, uid) for uid, u in sorted(units[kind].items())
                    if u["owner"].startswith("SEST_")] for kind in KINDS}
    placed = fielded_units(root, units)
    fielded = {kind: [dict(price_status(context, kind, uid), where=where)
                      for uid, where in placed[kind].items()] for kind in placed}
    carried = defaultdict(set)
    for kind in placed:
        for uid in placed[kind]:
            queue = carried_stores(units[kind][uid], units[kind])
            while queue:
                store = queue.pop().casefold()
                if store in units["weapon"] and units[kind][uid]["id"] not in carried[store]:
                    carried[store].add(units[kind][uid]["id"])
                    queue += pod_rounds(units["weapon"][store], units["weapon"])
    batch = [dict(price_status(context, "weapon", uid), carried_by=sorted(by, key=str.casefold))
             for uid, by in sorted(carried.items())]
    batch = [row for row in batch if _gap(row)]
    land = land_units(root)
    shipped = sorted((e for e in result["entries"] if e.get("estimate")),
                     key=lambda e: (e["kind"], e["target"].casefold()))

    lists = [("Weapons SEST ships", "sest", owned["weapon"]),
             ("Vessels SEST ships", "sest", owned["vessel"]),
             ("Aircraft SEST ships", "sest", owned["aircraft"]),
             ("Vessels SEST's missions field", "missions", fielded["vessel"]),
             ("Aircraft SEST's missions field", "missions", fielded["aircraft"])]
    md = [
        "# SEST combat cost list",
        "",
        f"Research reviewed {research['reviewed']}. Generated by "
        "`integration/combat-costs/build_pack.py` from the cost builder "
        "(`integration/common/costs.py`): the Combat Cost Tracker's captured catalogs, "
        "SEST's reviewed mappings and researched estimates "
        "(`integration/combat-costs/mappings.json`), the research record "
        "(`integration/combat-costs/research.json`) and SEST_Campaign's built missions and "
        "rosters. Do not edit it by hand: `tools/build_all.py` rebuilds it after the campaign. "
        "`cost-list.csv` beside it holds the same rows.",
        "",
        "- **Some sources could not be read.** This environment's network policy blocked "
        "them (proxy 403 and DNS failures). No price that rests on such a page is shipped; "
        "the figures are listed under Gaps as candidates.",
        "- **Researched estimates are SEST's**, not the tracker author's. Each is labelled "
        "with its method, year and sources, below and in the comment above its section in "
        "the shipped catalog.",
        "- **Historical** is the tracker's rounded service-entry-era USD "
        "(`WeaponCosts`, `VesselCosts`, `AircraftCosts`). **Current** is the explicit "
        "`CurrentYearCost` in 2026 USD; it never falls back to the historical price. Ships "
        "are priced fitted, without ammunition or embarked aircraft. Unknown is never free, "
        "and purchase points are never converted to USD.",
        "- **Price from**: `tracker catalog` (the author's entry), `inline in unit file`, "
        "`SEST mapping from <id>` (an author price copied exactly from that entry), "
        "`SEST researched estimate`, or `unknown` with the reason.",
        "- Aircraft have no tracker category; the tracker splits planes and helicopters itself.",
        "",
        "## Summary",
        "",
    ]
    summary = []
    for title, _, rows in lists:
        both = sum(1 for r in rows if not _gap(r))
        hist = sum(1 for r in rows if _gap(r) == ["current"])
        curr = sum(1 for r in rows if _gap(r) == ["historical"])
        summary.append([title, len(rows), both, hist, curr, len(rows) - both - hist - curr])
    summary.append(["Land units SEST ships", len(land), "-", "-", "-", LAND_NOTE])
    summary.append(["Weapons carried by fielded units with a missing price", len(batch),
                    "-", sum(1 for r in batch if _gap(r) == ["current"]),
                    sum(1 for r in batch if _gap(r) == ["historical"]),
                    sum(1 for r in batch if len(_gap(r)) == 2)])
    md += _table(["list", "items", "both prices", "historical only", "current only", "neither"],
                 summary)
    copied = {origin: sum(1 for e in result["entries"] if e["origin"] == origin and _priced(e))
              for origin in ("mapping", "normalized")}
    md += ["", f"Shipped by SEST: {len(shipped)} researched estimates, {copied['mapping']} reviewed "
           f"mappings and {copied['normalized']} spelling matches that copy an author price."]
    csv_rows = []
    for title, key, rows in lists:
        missions = key == "missions"
        md += ["", "## " + title, ""]
        header = ["id", "owner", "category", "historical USD", "current USD", "price from"]
        md += _table(header + (["fielded in"] if missions else []),
                     [[r["id"], owner(r["owner"]), r["category"] or "-", _usd(r["historical"]),
                       _usd(r["current"]), r["from"]] + ([", ".join(r["where"])] if missions else [])
                      for r in rows])
        csv_rows += [[key, r["kind"], r["id"], r["owner"], r["category"], r["historical"] or "",
                      r["current"] or "", r["from"], "; ".join(r.get("where", []))] for r in rows]

    md += ["", "## Land units SEST ships", "",
           f"{len(land)} land units, all {LAND_NOTE}.", ""]
    md += _table(["id", "pack", "price"], [[uid, pack, LAND_NOTE] for uid, pack in land])
    csv_rows += [["land", "land", uid, pack, "", "", "", LAND_NOTE, ""] for uid, pack in land]

    md += ["", "## SEST researched estimates", "",
           f"{len(shipped)} shipped. Methods: " + ", ".join(METHODS) + ". A CPI conversion uses the "
           "CPI-U series of the named source; a model estimate is a comparison, not a "
           "published price.", ""]
    for e in shipped:
        est, hist = e["estimate"], KINDS[e["kind"]][2]
        h = (f"historical {_usd(est['historical'])} ({est['historical_method']}, reference year "
             f"{est['historical_year']})" if est.get("historical") else "historical unknown")
        c = (f"current {_usd(est['current'])} ({est['current_method']}, source year "
             f"{est['current_year']})" if est.get("current") else "current unknown")
        category = f", {e['fields']['Category']}" if "Category" in e["fields"] else ""
        md += [f"- **{e['target']}** ({e['kind']}{category}): {h}; {c}. {e['basis']}."
               + (f" {est['note']}." if est.get("note") else "")
               + f" Sources: {_sources(e['sources'])}."]
        assert e["fields"][hist] == est.get("historical", "")

    unknown = {}
    for _, _, rows in lists:
        for r in rows:
            if _gap(r):
                unknown.setdefault((r["kind"], r["id"].casefold()), r)
    md += ["", "## Gaps", "", "### Still unknown", "",
           "Every unit above with a missing price, once each. `researched` points to the "
           "candidate figures below; `not researched yet` has had no price research.", ""]
    md += _table(["kind", "still unknown"],
                 [[kind, sum(1 for k, _ in unknown if k == kind)] for kind in KINDS])
    md += [""]
    md += _table(["id", "kind", "owner", "missing", "research"],
                 [[r["id"], r["kind"], owner(r["owner"]), " and ".join(_gap(r)),
                   ("researched: " + researched[key]["decision"]) if key in researched
                   else "researched: the SEST estimate leaves it unknown"
                   if context["receipts"].get(key, {}).get("origin") == "estimate"
                   else "not researched yet"]
                  for key, r in sorted(unknown.items(), key=lambda kv: (kv[0][0], kv[0][1]))])
    md += ["", "### Researched, not shipped", "",
           f"{len(researched)} items from the {research['reviewed']} research. A refuted row "
           "failed the adversarial check; `left unknown` means the check agreed that no "
           "defensible figure exists yet. `Re-run` marks an item whose research stopped because "
           "the session's web search allowance ran out or the source host was blocked. Land "
           "items are kept for reference only: the tracker does not price land platforms.", ""]
    for (kind, uid), item in sorted(researched.items()):
        if kind == "land":
            who, now = land_known[uid]["owner"], " Never shipped: the tracker does not price land platforms."
        else:
            status = price_status(context, kind, uid)
            who = status["owner"]
            now = "" if _gap(status) else f" Now priced: {status['from']}."
        md += [f"- **{item['target']}** ({kind}, {owner(who)}) - {item['decision']}. "
               f"Candidate: {item['candidate']}. Why not shipped: {item['why']}{now}"
               + (f" Sources: {_sources(item['sources'])}." if item["sources"] else "")]

    md += ["", "## Next batch: weapons carried by fielded units with a missing price", "",
           "Every store the fielded vessels' and aircraft's files can load, across all the fits "
           "they offer (a superset of what any one mission flies), and every round inside a "
           "carried pod, that lacks a price. "
           "Grouped by the round's type; counts first.", ""]
    grouped = defaultdict(list)
    for r in batch:
        kind_type = r["type"].casefold()
        grouped[next((g for g, types in GROUPS if kind_type in types), "Other")].append(r)
    order = [g for g, _ in GROUPS] + ["Other"]
    md += _table(["group", "missing a price", "neither price", "researched"],
                 [[g, len(grouped[g]), sum(1 for r in grouped[g] if len(_gap(r)) == 2),
                   sum(1 for r in grouped[g] if ("weapon", r["id"].casefold()) in researched)]
                  for g in order if grouped[g]])
    for g in order:
        if not grouped[g]:
            continue
        md += ["", f"### {g} ({len(grouped[g])})", ""]
        md += _table(["id", "type", "owner", "historical USD", "current USD", "carried by"],
                     [[r["id"], r["type"] or "-", owner(r["owner"]), _usd(r["historical"]),
                       _usd(r["current"]),
                       f"{len(r['carried_by'])}: " + ", ".join(r["carried_by"][:4])
                       + (", ..." if len(r["carried_by"]) > 4 else "")
                       + ("; researched" if ("weapon", r["id"].casefold()) in researched else "")]
                      for r in grouped[g]])
        csv_rows += [["next-batch", "weapon", r["id"], r["owner"], r["type"], r["historical"] or "",
                      r["current"] or "", r["from"], "; ".join(r["carried_by"])] for r in grouped[g]]

    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["list", "kind", "id", "owner", "category_or_type", "historical_usd",
                     "current_usd", "price_from", "fielded_in_or_carried_by"])
    writer.writerows(csv_rows)
    return "\n".join(md) + "\n", out.getvalue()
