#!/usr/bin/env python3
"""Align the offline SEST photo gallery with a mod build's load order.

The gallery (SEST_Modernised_Collection_Gallery, delivered as ZIP parts on a
handoff branch) indexes every unit and ammunition file each exported mod
ships, one record per providing mod, and deliberately leaves `winning_source`
blank: it was compiled against an older load order and would not guess. This
fills it from a real build, and says where else a unit's looks come from,
because the winning unit file is often not the whole answer:

- winning_source: the first entry in the build's data/load-order.tokens.txt
  that ships <kind>/<id>.ini (entry 1 wins, as in the Mod Manager), with SEST
  packs under integration/*/<token> and the base game under
  mods-source/_vanilla/original as the floor. Paths match case-insensitively,
  as on Windows.
- base_chain / data_from: a winning file that carries #!alias <path> loads
  that path's own winner first; one that carries #!extend of its own path
  layers onto the next copy down (tools/check_alias_bases.py). The chain is
  followed to the file that has no directive, whose provider supplies most of
  the unit (often its model). A base nobody ships is flagged: such a round
  never loads. The directive is accepted anywhere in the file, as
  build_pack.py reads it; directive_line says where it sat.
- overwrites: Anchor Chain's <kind>_overwrite/ files that #!extend this id
  and apply on top of whichever copy wins; overwrite_sets_model says whether
  one of them changes the model.
- variants_from / squadrons_from: <id>_variants.ini and <id>_squadrons.ini
  resolve on their own, and they decide the nation, hull number, livery and
  squadron a placed unit shows.
- model_folder / model_owner: the effective ResourcesFolder= and the first
  provider whose exported files sit under it (the export is text-only, so
  this is evidence, not the mesh itself; a folder the base game also uses is
  reported as base game).
- missions / in_rosters: built missions that place the unit (Type=) and
  campaign rosters that sell it, so photo work can start with what players
  meet.

It also lists units the SEST pack ships that the gallery does not index,
and writes the photo priorities for every unit the campaigns field.

Read-only against git: everything comes from `git ls-tree`/`git cat-file` at
--ref, so the working tree does not have to be on that build. Writes only
inside --gallery.

    python3 tools/align_gallery.py --gallery <extracted gallery> --ref origin/sest-dev/loving-bell-3cnvvw
"""
import argparse
import csv
import io
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
VANILLA = "mods-source/_vanilla/original/"
DIRECTIVE = re.compile(r"^\s*#!(extend|alias)\s+(\S+)", re.M)
FOLDER = re.compile(r"^\s*ResourcesFolder\s*=\s*([^\s#]+)", re.M)
UNIT_KINDS = ("aircraft/", "vessels/", "submarines/", "land_units/")


def git(*args):
    # core.quotepath=off: otherwise git escapes non-ASCII names (the PLAAF
    # pack's plaaf_130-Ⅱ_rocket) and they never match.
    return subprocess.run(["git", "-C", str(ROOT), "-c", "core.quotepath=off", *args],
                          check=True, capture_output=True).stdout


def cat_files(ref, paths):
    """Contents of many blobs in one `git cat-file --batch` call."""
    paths = list(paths)
    if not paths:
        return {}
    req = "".join(f"{ref}:{p}\n" for p in paths).encode()
    out = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch"], input=req,
                         check=True, capture_output=True).stdout
    res, buf = {}, io.BytesIO(out)
    for p in paths:
        head = buf.readline().decode().split()
        if len(head) < 3 or head[1] == "missing":
            continue
        body = buf.read(int(head[2]))
        buf.read(1)
        res[p] = body.decode("utf-8-sig", "replace")
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gallery", type=Path, required=True)
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--restore-from", type=Path,
                    help="the earlier gallery's manifest.json: SEST pack units the current index "
                         "dropped come back with their reviewed photo mapping")
    a = ap.parse_args()
    g, ref = a.gallery, a.ref
    commit = git("rev-parse", ref).decode().strip()
    tokens = [l.strip() for l in git("show", f"{ref}:data/load-order.tokens.txt").decode().splitlines()
              if l.strip() and not l.lstrip().startswith("#")]
    files = git("ls-tree", "-r", "--name-only", ref, "--", "mods-source", "integration").decode().splitlines()

    # Each token's folder: a SEST pack is integration/<anything>/<token>
    # (the consolidated pack is integration/dist/SEST_Integration), a
    # Workshop mod is mods-source/<id>.
    sest_dirs = {}
    for f in files:
        parts = f.split("/")
        if parts[0] == "integration" and len(parts) > 3 and parts[2].startswith("SEST_"):
            sest_dirs.setdefault(parts[2], "/".join(parts[:3]) + "/")
    order = []
    for t in tokens:
        if t.startswith("SEST_"):
            if t in sest_dirs:
                order.append((t, sest_dirs[t]))
        else:
            order.append((t, f"mods-source/{t}/"))
    order.append(("vanilla", VANILLA))
    rank = {t: i for i, (t, _p) in enumerate(order)}
    pre = sorted(((p, t) for t, p in order), key=lambda x: -len(x[0]))
    index = defaultdict(dict)                   # token -> {lower rel: real path}
    for f in files:
        for p, t in pre:
            if f.startswith(p):
                index[t][f[len(p):].lower()] = f
                break

    def providers(rel):
        return [t for t, _p in order if rel.lower() in index[t]]

    m = json.loads((g / "manifest.json").read_text(encoding="utf-8"))
    titles = {x["id"]: x["title"] for x in m["mods"]}
    titles.update({"SEST_Integration": "SEST Integration Pack", "vanilla": "Sea Power (base game)"})

    # The 190 update re-keyed the index one record per providing Workshop mod
    # and so dropped every file only the SEST pack ships - the RAN hulls, the
    # RAAF bases, the Triton, the pack's own rounds - with the photo mappings
    # the earlier gallery had already reviewed for them. Put them back as
    # SEST_Integration records, carrying that review unchanged.
    restored = 0
    if a.restore_from:
        old_m = json.loads(a.restore_from.read_text(encoding="utf-8"))
        prior = {e["entry_id"].lower(): e for e in old_m["entries"]}
        have = {e["unit_id"].lower() for e in m["entries"]}
        pack = sest_dirs.get("SEST_Integration", "integration/dist/SEST_Integration/")
        for rel, real in sorted(index["SEST_Integration"].items()):
            kind = rel.split("/")[0]
            if kind not in ("aircraft", "vessels", "submarines", "land_units", "ammunition") \
                    or rel.count("/") != 1 or not rel.endswith(".ini"):
                continue
            uid = PurePosixPath(real).stem
            if uid.lower().endswith(("_squadrons", "_variants")) or uid.startswith("_") or uid.lower() in have:
                continue
            old_e = prior.get(f"{kind}/{uid}".lower(), {})
            e = {k: old_e.get(k, "") for k in m["entries"][0]} if old_e else {k: "" for k in m["entries"][0]}
            e.update(entry_id=f"SEST_Integration:{kind}/{uid}", unit_id=uid, kind=kind,
                     source_config=f"{pack}{kind}/{PurePosixPath(real).name}", providers=["SEST_Integration"],
                     mod_title="SEST Integration Pack")
            if old_e:
                e["mapping_note"] = ((old_e.get("mapping_note") or "") +
                                     " [Restored from the earlier gallery's reviewed mapping; the 190 update had dropped this SEST pack record.]").strip()
            else:
                e.update(label=uid, mapping_status="photo_gap", asset_id="", image_file="",
                         integration_review="pending",
                         mapping_note="SEST pack record added at alignment; no photo assigned.")
            m["entries"].append(e)
            have.add(uid.lower())
            restored += 1

    # Every unit-file copy any record can reach, fetched once.
    want = set()
    for e in m["entries"]:
        rel = re.sub(r"^(mods-source/[^/]+|integration/[^/]+/SEST_[^/]+)/", "", e["source_config"]).lower()
        for t in providers(rel):
            want.add(index[t][rel])
    text = cat_files(ref, sorted(want))

    def fetch(path):
        if path not in text:
            text.update(cat_files(ref, [path]))
        return text.get(path, "")

    def chain(rel, start=0):
        """[(rel, token, directive, line)] from the winner down to the copy
        with no directive; ('', '', 'missing', 0) ends a broken chain."""
        out, seen = [], set()
        provs = providers(rel)
        i = start
        while len(out) < 8:
            if i >= len(provs):
                out.append((rel, "", "missing", 0))
                break
            tok = provs[i]
            if (rel, tok) in seen:
                break
            seen.add((rel, tok))
            body = fetch(index[tok][rel.lower()])
            mm = DIRECTIVE.search(body)
            if not mm:
                out.append((rel, tok, "", 0))
                break
            line = body[:mm.start()].count("\n") + 1
            out.append((rel, tok, f"#!{mm.group(1)} {mm.group(2)}", line))
            target = str(PurePosixPath(mm.group(2).replace("\\", "/")))
            if mm.group(1) == "extend" and target.lower() == rel.lower():
                i += 1                                   # the next copy down
            else:
                rel, provs, i = target, providers(target), 0
        return out

    # Anchor Chain overwrite files: <kind>_overwrite/*.ini that #!extend a
    # unit or round, applied on top of whichever copy wins.
    ow_paths = [(t, rel, real) for t, _p in order for rel, real in index[t].items()
                if re.match(r"^[a-z_]+_overwrite/", rel) and rel.endswith(".ini")]
    ow_text = cat_files(ref, [r for _t, _rel, r in ow_paths])
    overwrites = defaultdict(list)
    for t, rel, real in ow_paths:
        body = ow_text.get(real, "")
        mm = DIRECTIVE.search(body)
        if mm and mm.group(1) == "extend":
            overwrites[mm.group(2).lower()].append((t, real, bool(FOLDER.search(body))))

    # Exported files under a folder, by first provider: model-folder evidence.
    folder_owner = {}
    seen_rel = set()
    for t, _p in order:
        for rel in index[t]:
            if rel in seen_rel:
                continue
            seen_rel.add(rel)
            parts = rel.split("/")
            for i in range(2, len(parts)):
                folder_owner.setdefault("/".join(parts[:i]), t)

    # Missions (Type=) and rosters that field each unit.
    mission_files = [f for f in index["SEST_Integration"].values()
                     if "/missions/" in f.lower() and f.endswith(".ini") and not f.endswith("_info.ini")]
    roster_files = [f for f in index["SEST_Integration"].values()
                    if f.endswith(("player_task_force_roster.ini", "campaign.ini"))]
    used, rostered = defaultdict(set), defaultdict(set)
    for path, body in cat_files(ref, mission_files).items():
        for t in re.findall(r"^Type=([^\r\n#;]+?)\s*$", body, re.M):
            used[t.lower()].add(Path(path).stem)
    for path, body in cat_files(ref, roster_files).items():
        camp = path.split("/campaigns/")[1].split("/")[0]
        if path.endswith("player_task_force_roster.ini"):
            for k in re.findall(r"^([^;\[\s=][^=\r\n]*?)\s*=", body, re.M):
                rostered[k.lower()].add(camp)
        for line in re.findall(r"^TaskForceModeAllowedRosterUnits=(.*)$", body, re.M):
            for item in line.split("|"):
                if item.strip():
                    rostered[item.split(",")[0].strip().lower()].add(camp)

    rows, win_count, data_count = [], defaultdict(int), defaultdict(int)
    for e in m["entries"]:
        rel = re.sub(r"^(mods-source/[^/]+|integration/[^/]+/SEST_[^/]+)/", "", e["source_config"])
        mine = (e["source_config"].split("/")[2] if e["source_config"].startswith("integration/")
                else e["source_config"].split("/")[1])
        provs = providers(rel)
        win = provs[0] if provs else ""
        ch = chain(rel) if win else []
        top_dir, top_line = (ch[0][2], ch[0][3]) if ch else ("", 0)
        base = ch[-1] if ch else ("", "", "", 0)
        missing = bool(ch) and base[2] == "missing"
        data_from = "" if missing else base[1]
        # Effective model folder: the topmost file in the chain that sets one,
        # then any overwrite that sets one on top.
        folder = ""
        for crel, ctok, _d, _l in ch:
            if ctok:
                mm = FOLDER.search(fetch(index[ctok][crel.lower()]))
                if mm:
                    folder = mm.group(1).strip().rstrip("/")
                    break
        ows = overwrites.get(rel.lower(), [])
        for t, real, sets_model in sorted(ows, key=lambda x: rank[x[0]], reverse=True):
            if sets_model:
                mm = FOLDER.search(ow_text.get(real, ""))
                if mm:
                    folder = mm.group(1).strip().rstrip("/")
        owner = folder_owner.get(folder.lower(), "") if folder else ""
        stem = Path(rel).stem
        var = providers(str(Path(rel).with_name(stem + "_variants.ini")))
        sq = providers(str(Path(rel).with_name(stem + "_squadrons.ini")))
        missions = sorted(used.get(e["unit_id"].lower(), ()))
        rosters = sorted(rostered.get(e["unit_id"].lower(), ()))

        e["winning_source"] = f"{win} ({titles.get(win, win)})" if win else "not in this build"
        e["load_order_providers"] = provs
        e["winning_directive"] = top_dir
        e["base_chain"] = [f"{c[0]} @ {c[1] or 'nobody'}" for c in ch]
        e["data_from"] = data_from or ("base file missing" if missing else "")
        e["used_in_missions"] = missions
        e["in_rosters"] = rosters
        e["is_winning_copy"] = (mine == win)
        if mine == win:
            win_count[mine] += 1
        if mine == data_from:
            data_count[mine] += 1
        rows.append({
            "entry_id": e["entry_id"], "unit_id": e["unit_id"], "kind": e["kind"], "label": e["label"],
            "this_record_mod": mine, "winning_source": win, "winning_title": titles.get(win, win),
            "is_winning_copy": "yes" if mine == win else "no",
            "winning_directive": top_dir, "directive_line": top_line or "",
            "base_chain": " -> ".join(f"{c[0]}@{c[1] or 'nobody'}" for c in ch[1:]) if len(ch) > 1 else "",
            "data_from": data_from or ("BASE MISSING" if missing else ""),
            "this_record_supplies_data": "yes" if mine == data_from else "no",
            "overwrites": "; ".join(f"{t}:{r}" for t, r, _s in ows),
            "overwrite_sets_model": "yes" if any(s for _t, _r, s in ows) else "",
            "variants_from": var[0] if var else "", "squadrons_from": sq[0] if sq else "",
            "model_folder": folder, "model_owner": owner,
            "providers_in_load_order": " > ".join(provs), "asset_id": e.get("asset_id") or "",
            "mapping_status": e.get("mapping_status", ""),
            "missions_using_unit": len(missions), "missions": "; ".join(missions),
            "in_rosters": "; ".join(rosters)})
    for x in m["mods"]:
        x["winning_definition_count"] = win_count.get(x["id"], 0)
        x["data_supplied_count"] = data_count.get(x["id"], 0)

    # SEST pack units the gallery does not index under any provider.
    indexed = {e["unit_id"].lower() for e in m["entries"]}
    sest_only = []
    for rel, real in sorted(index["SEST_Integration"].items()):
        if not rel.startswith(UNIT_KINDS) or rel.count("/") != 1 or not rel.endswith(".ini"):
            continue
        uid = PurePosixPath(real).stem                    # the real case, as Type= names it
        if uid.lower().endswith(("_squadrons", "_variants")) or uid.startswith("_"):
            continue
        if uid.lower() not in indexed:
            sest_only.append({"unit_id": uid, "file": real,
                              "missions_using_unit": len(used.get(uid.lower(), ())),
                              "missions": "; ".join(sorted(used.get(uid.lower(), ()))),
                              "in_rosters": "; ".join(sorted(rostered.get(uid.lower(), ())))})

    m["summary"]["load_order_alignment"] = {
        "build_commit": commit, "load_order_entries": len(tokens),
        "workshop_mods_in_order": sum(not t.startswith("SEST_") for t in tokens),
        "records": len(rows), "records_resolved": sum(1 for r in rows if r["winning_source"]),
        "winning_copies": sum(win_count.values()),
        "winner_is_sest_pack": sum(1 for r in rows if r["winning_source"] == "SEST_Integration"),
        "winner_has_directive": sum(1 for r in rows if r["winning_directive"]),
        "base_missing": sum(1 for r in rows if r["data_from"] == "BASE MISSING"),
        "data_from_other_mod_than_winner": sum(1 for r in rows if r["data_from"] and r["data_from"] != r["winning_source"]),
        "records_with_overwrites": sum(1 for r in rows if r["overwrites"]),
        "records_used_in_missions": sum(1 for r in rows if r["missions_using_unit"]),
        "records_in_rosters": sum(1 for r in rows if r["in_rosters"]),
        "sest_pack_records_restored": restored,
        "sest_pack_units_not_indexed": len(sest_only),
        "method": "tools/align_gallery.py at the build: first provider in data/load-order.tokens.txt "
                  "wins; #!alias/#!extend followed to data_from; *_overwrite extends, variants, "
                  "squadrons and model folders resolved separately; missions = Type= in built "
                  "missions; rosters = campaign roster and allowed-roster lists."}
    (g / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    (g / "catalogue.js").write_text("window.CATALOGUE=" + json.dumps(m, ensure_ascii=False, separators=(",", ":")) + ";\n",
                                    encoding="utf-8")
    with (g / "data" / "load_order_alignment_191.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    with (g / "data" / "sest_pack_units_not_indexed.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["unit_id", "file", "missions_using_unit", "missions", "in_rosters"])
        w.writeheader(); w.writerows(sest_only)
    mp = g / "data" / "unit_image_mapping.csv"
    with mp.open(encoding="utf-8-sig", newline="") as fh:
        r = list(csv.DictReader(fh))
    byid = {e["entry_id"]: e for e in m["entries"]}
    for row in r:
        row["winning_source"] = byid[row["entry_id"]]["winning_source"]
    listed = {row["entry_id"] for row in r}
    for e in m["entries"]:                      # restored SEST pack records
        if e["entry_id"] not in listed:
            r.append({k: (json.dumps(e.get(k)) if isinstance(e.get(k), list) else e.get(k, "")) for k in r[0]})
    with mp.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(r[0]))
        w.writeheader(); w.writerows(r)
    write_priorities(g, rows, sest_only)
    print(json.dumps(m["summary"]["load_order_alignment"], indent=1))


def write_priorities(g, rows, sest_only):
    """data/photo_priorities_fielded_units_191.csv: every unit a built
    mission places or a campaign roster sells, once, with its photo status -
    NO PHOTO, NOT IN GALLERY (a SEST pack unit the gallery does not index) or
    WEAK PHOTO (the gallery's own P1/P2 quality tasks) - ordered by how often
    players meet it."""
    qa_path = g / "data" / "image_quality_audit.json"
    qa = ({p["asset_id"]: p for p in json.loads(qa_path.read_text(encoding="utf-8"))["photos"]}
          if qa_path.is_file() else {})
    cands = defaultdict(list)
    for r in rows:
        if (r["is_winning_copy"] == "yes" or r["winning_source"] == "SEST_Integration") \
                and (r["missions_using_unit"] or r["in_rosters"]):
            cands[r["unit_id"].lower()].append(r)
    units = {}
    for u, rs in cands.items():
        # The winning copy's record first; among SEST-won units, a record
        # that carries a photo, so a unit is not reported bare when one
        # provider's record has its picture.
        rs.sort(key=lambda r: (r["is_winning_copy"] != "yes", not r["asset_id"]))
        r = rs[0]
        a = r["asset_id"] or next((x["asset_id"] for x in rs if x["asset_id"]), "")
        q = qa.get(a, {})
        units[u] = dict(unit_id=r["unit_id"], kind=r["kind"], label=r["label"],
                        missions=r["missions_using_unit"], rosters=r["in_rosters"], asset_id=a,
                        mapping_status=r["mapping_status"],
                        photo_grade=(q.get("quality_grade", "") + q.get("subject_visibility_grade", "")) if a else "",
                        photo_priority=q.get("priority", ""),
                        need="NO PHOTO" if not a else ("WEAK PHOTO" if q.get("priority") in ("P1", "P2") else ""),
                        winning_source=r["winning_source"], data_from=r["data_from"],
                        model_owner=r["model_owner"], squadrons_from=r["squadrons_from"])
    for s in sest_only:
        u = s["unit_id"].lower()
        if u not in units:
            units[u] = dict(unit_id=s["unit_id"], kind=s["file"].split("/")[-2],
                            label="(SEST pack unit, not in gallery)", missions=s["missions_using_unit"],
                            rosters=s["in_rosters"], asset_id="", mapping_status="not_indexed", photo_grade="",
                            photo_priority="", need="NOT IN GALLERY", winning_source="SEST_Integration",
                            data_from="SEST_Integration", model_owner="", squadrons_from="")
    lst = sorted(units.values(), key=lambda x: (x["need"] == "", -int(x["missions"]), -len(x["rosters"]), x["unit_id"]))
    with (g / "data" / "photo_priorities_fielded_units_191.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lst[0]))
        w.writeheader(); w.writerows(lst)


if __name__ == "__main__":
    main()
