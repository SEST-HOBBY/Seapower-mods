#!/usr/bin/env python3
"""Bring the gallery's unit index in step with the current build.

The index (source/catalogue.js and the CSVs under source/data/) was compiled
against one export and load order. Between exports, mods are added and
retired and authors rename units; this applies those changes without
re-running the full index:

- a record whose mod is no longer in data/load-order.tokens.txt is retired.
  If the SEST pack now ships that file and no remaining Workshop mod does,
  the record becomes a SEST_Integration record (its photo mapping carried
  over); otherwise it is dropped, since the other providers keep their own
  records. The RAAF F-35A (3514484654, removed from the Workshop) is the case
  this was written for.
- RENAMES carries a renamed unit's record, photo mapping included, to its new
  id (Modern US Navy v597 renamed usn_dd_spruance_eu_vls).
- every record's providers and winner are recomputed from the current load
  order, mods-source/ and the consolidated pack.
- a load-order mod the index does not list yet is added to the mod table.

    python3 integration/gallery/refresh_index.py          # then: build_patch.py

It stops on a source file it cannot place, rather than guessing.
"""
import csv
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent / "source"
DATA = SRC / "data"
PACK = "SEST_Integration"
PACK_DIR = ROOT / "integration" / "dist" / PACK
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
KINDS = ("aircraft", "vessels", "submarines", "land_units", "ammunition")

#   old entry id -> new unit id
RENAMES = {"3390330875:vessels/usn_dd_spruance_eu_vls": "usn_dd_spruance_vls_lamps3"}


def load_catalogue():
    text = (SRC / "catalogue.js").read_text(encoding="utf-8")
    return json.loads(re.match(r"window\.CATALOGUE=(.*);\s*$", text, re.S).group(1))


def save_catalogue(cat):
    (SRC / "catalogue.js").write_text(
        "window.CATALOGUE=" + json.dumps(cat, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")


def mod_name(token):
    info = ROOT / "mods-source" / token / "_info.ini"
    if info.is_file():
        m = re.search(r"^\[Language_en\][^\[]*?^Name=([^\r\n]+)$",
                      info.read_text(encoding="utf-8-sig", errors="replace"), re.M | re.S)
        if m:
            return m.group(1).strip()
    return token


def build_order():
    tokens = [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt").read_text().splitlines()
              if l.strip() and not l.lstrip().startswith("#")]
    order = []
    for t in tokens:
        order.append((t, PACK_DIR if t == PACK else ROOT / "mods-source" / t))
    order.append(("vanilla", VANILLA))
    index = {}
    for t, d in order:
        index[t] = {p.relative_to(d).as_posix().lower(): p for k in KINDS
                    for p in (d / k).glob("*.ini")} if d.is_dir() else {}
    return tokens, order, index


def label_for(uid, kind):
    """Display name from the names file the game reads, falling back to the id."""
    names = {"vessels": "vessel_names.ini", "submarines": "vessel_names.ini",
             "aircraft": "aircraft_names.ini", "land_units": "land_units_names.ini"}.get(kind)
    if not names:
        return uid
    for f in sorted((ROOT / "mods-source").glob(f"*/language_en/{names}")):
        m = re.search(rf"^\[{re.escape(uid)}\][^\[]*?^Default=([^,\n]+)",
                      f.read_text(encoding="utf-8-sig", errors="replace"), re.M | re.S)
        if m:
            return m.group(1).strip()
    return uid


def main():
    cat = load_catalogue()
    tokens, order, index = build_order()
    live = set(tokens) | {"vanilla"}
    titles = {m["id"]: m["title"] for m in cat["mods"]}
    titles.update({PACK: "SEST Integration Pack", "vanilla": "Sea Power (base game)"})
    for t in tokens:
        titles.setdefault(t, mod_name(t))

    def providers(rel):
        return [t for t, _d in order if rel.lower() in index[t]]

    entries, notes = [], []
    by_id = {e["entry_id"]: e for e in cat["entries"]}
    workshop_units = {}
    for e in cat["entries"]:
        tok = e["entry_id"].split(":", 1)[0]
        if tok in live and tok != PACK:
            workshop_units.setdefault(f'{e["kind"]}/{e["unit_id"]}'.lower(), set()).add(tok)

    for e in cat["entries"]:
        tok, rest = e["entry_id"].split(":", 1)
        kind, uid = rest.split("/", 1)
        if e["entry_id"] in RENAMES:
            new = RENAMES[e["entry_id"]]
            rel = f"{kind}/{new}.ini"
            if rel.lower() not in index.get(tok, {}):
                sys.exit(f"rename target {tok}/{rel} is not in the export")
            e = dict(e, entry_id=f"{tok}:{kind}/{new}", unit_id=new, label=label_for(new, kind),
                     source_config=f"mods-source/{tok}/{rel}")
            notes.append(f"renamed {uid} -> {new} (photo mapping kept)")
        elif tok not in live:
            rel = f"{kind}/{uid}.ini".lower()
            others = workshop_units.get(f"{kind}/{uid}".lower(), set()) - {tok}
            if rel in index[PACK] and not others and f"{PACK}:{rest}" not in by_id:
                e = dict(e, entry_id=f"{PACK}:{rest}", mod_title=titles[PACK], providers=[PACK],
                         source_config=index[PACK][rel].relative_to(ROOT).as_posix())
                e["mapping_note"] = ((e.get("mapping_note") or "") +
                                     f" [Carried by the SEST pack since {tok} left the Workshop.]").strip()
                notes.append(f"{tok}:{rest} -> {PACK} record")
            else:
                notes.append(f"{tok}:{rest} dropped ({'other mods keep their records' if others else 'no copy left'})")
                continue
        entries.append(e)

    # Providers and winner, from the current order.
    changed = 0
    for e in entries:
        tok, rest = e["entry_id"].split(":", 1)
        rel = rest + ".ini"
        prov = providers(rel)
        if not prov:
            sys.exit(f"{e['entry_id']}: no copy of {rel} in the current build")
        win = prov[0]
        new = {"load_order_providers": prov, "winning_source": f"{win} ({titles.get(win, win)})",
               "is_winning_copy": win == tok}
        if [e.get(k) for k in new] != list(new.values()):
            changed += 1
            text = index[win][rel.lower()].read_text(encoding="utf-8", errors="replace")
            if not re.search(r"^\s*#!(alias|extend)\s", text, re.M):
                new.update(base_chain=[f"{rel} @ {win}"], data_from=win, winning_directive="")
            e.update(new)

    # Load-order mods the index does not list yet.
    have = {m["id"] for m in cat["mods"]}
    for t in tokens:
        if t == PACK or t in have:
            continue
        rows = [e for e in entries if e["entry_id"].startswith(t + ":")]
        if rows:
            sys.exit(f"{t} ships unit files; index it properly rather than through this script")
        cat["mods"].append({
            "id": t, "title": titles[t], "new_mod": True,
            "url": f"https://steamcommunity.com/sharedfiles/filedetails/?id={t}",
            "definition_count": 0, "system_sections": 0, "categories": {},
            "scope_note": "No unit or ammunition files: this mod supplies encyclopedia pictures (ui/profiles) only.",
            "photo_mapped_definitions": 0, "unmapped_definitions": 0, "winning_definition_count": 0,
            "system_count": 0, "export_present": True, "data_supplied_count": 0})
        notes.append(f"mod added to the index: {t} {titles[t]}")
    gone = [m["id"] for m in cat["mods"] if m["id"] not in tokens and m["id"] != "3812461539"]
    cat["mods"] = [m for m in cat["mods"] if m["id"] not in gone]
    notes += [f"mod removed from the index: {g}" for g in gone]

    # Per-mod counts, only for the mods whose records moved.
    touched = {PACK}
    for m in cat["mods"]:
        tok = PACK if m["id"] == "3812461539" else m["id"]
        if tok not in touched:
            continue
        rows = [e for e in entries if e["entry_id"].startswith(tok + ":")]
        cats = {}
        for e in rows:
            cats[e["category"]] = cats.get(e["category"], 0) + 1
        mapped = sum(1 for e in rows if e.get("asset_id"))
        m.update(definition_count=len(rows), categories=cats, photo_mapped_definitions=mapped,
                 unmapped_definitions=len(rows) - mapped,
                 winning_definition_count=sum(1 for e in rows if e["is_winning_copy"]))

    # System sections (sensors, guns) of a retired mod: other mods define the
    # same names, so its records go rather than move.
    kept = [x for x in cat["systems"] if x["entry_id"].split(":", 1)[1].split("/", 1)[0] in live]
    if len(kept) != len(cat["systems"]):
        notes.append(f"{len(cat['systems']) - len(kept)} system record(s) of retired mods dropped")
    cat["systems"] = kept

    s = cat["summary"]
    s["compiled"] = date.today().isoformat()
    s["system_records_indexed"] = len(kept)
    s["physical_definitions_indexed"] = len(entries)
    byc, stat = {}, {}
    for e in entries:
        byc[e["category"]] = byc.get(e["category"], 0) + 1
        stat[e["mapping_status"]] = stat.get(e["mapping_status"], 0) + 1
    s["definitions_by_category"] = byc
    s["mapping_statuses"] = stat
    s["definitions_with_candidate_photo"] = sum(1 for e in entries if e.get("asset_id"))
    cat["entries"] = entries
    save_catalogue(cat)
    write_csvs(cat, entries, titles, touched)
    print("\n".join(notes))
    print(f"{len(entries)} records; {changed} with a new winner or provider list")


def rewrite_csv(path, fn):
    data = path.read_bytes()
    bom = data.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in data
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline="")))
    fields = list(rows[0].keys()) if rows else []
    out = [r2 for r in rows for r2 in fn(r)]
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\r\n" if crlf else "\n")
    w.writeheader()
    w.writerows(out)
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + buf.getvalue().encode("utf-8"))


def write_csvs(cat, entries, titles, touched):
    by_id = {e["entry_id"]: e for e in entries}
    retired = {t for t in titles if t.isdigit() and t not in {m["id"] for m in cat["mods"]}}
    old_to_new = {}
    for old, new in RENAMES.items():
        tok, rest = old.split(":", 1)
        old_to_new[old] = f"{tok}:{rest.split('/')[0]}/{new}"

    def resolve(eid):
        eid = old_to_new.get(eid, eid)
        if eid in by_id:
            return by_id[eid]
        tok, rest = eid.split(":", 1)
        retired = tok != PACK and tok not in {m["id"] for m in cat["mods"]}
        return by_id.get(f"{PACK}:{rest}") if retired else None

    def mapping_row(r):
        e = resolve(r["entry_id"])
        if not e:
            return []
        r = dict(r)
        for k in r:
            if k in e:
                v = e[k]
                r[k] = json.dumps(v, ensure_ascii=False) if isinstance(v, list) else ("" if v is None else v)
        return [r]

    def align_row(r):
        e = resolve(r["entry_id"])
        if not e:
            return []
        r = dict(r)
        tok = e["entry_id"].split(":", 1)[0]
        win = e["load_order_providers"][0]
        r.update(entry_id=e["entry_id"], unit_id=e["unit_id"], label=e["label"], this_record_mod=tok,
                 winning_source=win, winning_title=titles.get(win, win),
                 is_winning_copy="yes" if e["is_winning_copy"] else "no",
                 data_from=e.get("data_from", r["data_from"]),
                 this_record_supplies_data="yes" if e.get("data_from") == tok else "no",
                 providers_in_load_order=" > ".join(e["load_order_providers"]))
        for k in ("variants_from", "squadrons_from", "model_owner"):
            if r.get(k) in retired:
                r[k] = PACK         # the pack carries what the retired mod supplied
        return [r]

    def unmapped_row(r):
        # This list leaves winning_source blank on purpose; only a record that
        # moved (renamed, or now carried by the pack) is rewritten.
        e = resolve(r["entry_id"])
        if not e or e.get("asset_id"):
            return []
        return [r] if e["entry_id"] == r["entry_id"] else mapping_row(r)

    rewrite_csv(DATA / "unit_image_mapping.csv", mapping_row)
    rewrite_csv(DATA / "load_order_alignment_191.csv", align_row)
    rewrite_csv(DATA / "unmapped_entries.csv", unmapped_row)
    ids = {m["id"] for m in cat["mods"]}
    mods = {m["id"]: m for m in cat["mods"]}

    def coverage_row(r):
        if r["id"] not in ids:
            return []
        if (PACK if r["id"] == "3812461539" else r["id"]) not in touched:
            return [r]
        r = dict(r)
        for k in r:
            if k in mods[r["id"]] and k != "categories":
                r[k] = mods[r["id"]][k]
        r["categories"] = json.dumps(mods[r["id"]]["categories"], ensure_ascii=False)
        return [r]

    path = DATA / "mod_coverage.csv"
    rewrite_csv(path, coverage_row)
    listed = {r["id"] for r in csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig")))}
    extra = [m for m in cat["mods"] if m["id"] not in listed and "ui/profiles" in m.get("scope_note", "")]
    if extra:
        with path.open("a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\r\n" if b"\r\n" in path.read_bytes() else "\n")
            for m in extra:
                w.writerow([m["id"], m["title"], m["new_mod"], m["url"], 0, 0, "{}", m["scope_note"],
                            0, 0, 0, 0, True])

    def priority_row(r):
        uid = {"usn_dd_spruance_eu_vls": "usn_dd_spruance_vls_lamps3"}.get(r["unit_id"], r["unit_id"])
        r = dict(r, unit_id=uid)
        for e in entries:
            if e["unit_id"] == uid and e["kind"] == r["kind"] and e["is_winning_copy"]:
                r["winning_source"] = e["load_order_providers"][0]
                for k in ("model_owner", "squadrons_from", "data_from"):
                    if r.get(k) in retired:
                        r[k] = PACK
                break
        return [r]

    rewrite_csv(DATA / "photo_priorities_fielded_units_191.csv", priority_row)


if __name__ == "__main__":
    main()
