#!/usr/bin/env python3
"""Align the offline SEST photo gallery with a mod build's load order.

The gallery (SEST_Modernised_Collection_Gallery, delivered as ZIP parts on a
handoff branch) indexes every unit and ammunition file each exported mod
ships, one record per providing mod, and deliberately leaves `winning_source`
blank: it was compiled against an older load order and would not guess. This
fills it from a real build.

For each record it resolves `<kind>/<unit>.ini` down the build's
data/load-order.tokens.txt (entry 1 wins, as in the Mod Manager), with the
SEST pack at integration/dist/SEST_Integration and the game's own files under
mods-source/_vanilla/original as the floor. Paths match case-insensitively,
as they do on Windows. A winning file that opens with #!extend or #!alias is
recorded with the directive, because what the game shows then also depends
on the provider below it.

It also records which built missions place each unit, so photo work can start
with the units players actually meet, and lists units the SEST pack ships
that the gallery does not index at all.

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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "integration/dist/SEST_Integration/"
VANILLA = "mods-source/_vanilla/original/"
UNIT_DIRS = ("aircraft/", "vessels/", "submarines/", "land_units/", "ammunition/", "weapons/")


def git(*args):
    # core.quotepath=off: otherwise git escapes non-ASCII names (the PLAAF
    # pack's plaaf_130-Ⅱ_rocket) and they never match.
    return subprocess.run(["git", "-C", str(ROOT), "-c", "core.quotepath=off", *args], check=True,
                          capture_output=True).stdout


def cat_files(ref, paths):
    """Contents of many blobs in one `git cat-file --batch` call."""
    if not paths:
        return {}
    req = "".join(f"{ref}:{p}\n" for p in paths).encode()
    out = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch"], input=req,
                         check=True, capture_output=True).stdout
    res, buf, i = {}, io.BytesIO(out), 0
    for p in paths:
        head = buf.readline().decode().split()
        if len(head) < 3 or head[1] == "missing":
            continue
        body = buf.read(int(head[2]))
        buf.read(1)
        res[p] = body.decode("utf-8", "replace")
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gallery", type=Path, required=True)
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    g = a.gallery
    commit = git("rev-parse", a.ref).decode().strip()
    tokens = [l.strip() for l in git("show", f"{a.ref}:data/load-order.tokens.txt").decode().splitlines()
              if l.strip() and not l.lstrip().startswith("#")]
    files = git("ls-tree", "-r", "--name-only", a.ref, "--", "mods-source", PACK.rstrip("/")).decode().splitlines()

    def prefix(tok):
        return PACK if tok == "SEST_Integration" else f"mods-source/{tok}/"
    order = [(t, prefix(t)) for t in tokens] + [("vanilla", VANILLA)]
    index = defaultdict(dict)                  # provider token -> {lower rel: real path}
    pre = {p: t for t, p in order}
    for f in files:
        for p, t in pre.items():
            if f.startswith(p):
                index[t][f[len(p):].lower()] = f
                break

    m = json.loads((g / "manifest.json").read_text(encoding="utf-8"))
    titles = {x["id"]: x["title"] for x in m["mods"]}
    titles.update({"SEST_Integration": "SEST Integration Pack", "vanilla": "Sea Power (base game)"})

    def resolve(rel):
        provs = [t for t, _p in order if rel.lower() in index[t]]
        return provs

    # Which built missions place each unit (Type=), deduplicated by file name:
    # every campaign mission ships twice, under missions/ and campaigns/.
    mission_files = [f for f in files if f.startswith(PACK) and f.endswith(".ini")
                     and ("/missions/" in f) and not f.endswith("_info.ini")]
    used = defaultdict(set)
    for path, text in cat_files(a.ref, mission_files).items():
        name = Path(path).stem
        for t in re.findall(r"^Type=([\w.-]+)", text, re.M):
            used[t.lower()].add(name)

    winners_needed = {}
    rows = []
    for e in m["entries"]:
        rel = re.sub(r"^mods-source/[^/]+/", "", e["source_config"])
        provs = resolve(rel)
        win = provs[0] if provs else ""
        if win:
            winners_needed[win] = index[win][rel.lower()]
        rows.append((e, rel, provs, win))
    heads = cat_files(a.ref, sorted(set(winners_needed.values())))

    def directive(tok, rel):
        text = heads.get(index[tok].get(rel.lower(), ""), "")
        mm = re.search(r"^\s*#!(extend|alias)\s+(\S+)", text, re.M)
        return f"#!{mm.group(1)} {mm.group(2)}" if mm else ""

    win_count = defaultdict(int)
    out_rows = []
    for e, rel, provs, win in rows:
        d = directive(win, rel) if win else ""
        e["winning_source"] = (f"{win} ({titles.get(win, win)})" if win else "not in this build")
        e["load_order_providers"] = provs
        e["winning_directive"] = d
        missions = sorted(used.get(e["unit_id"].lower(), ()))
        e["used_in_missions"] = missions
        mine = e["source_config"].split("/")[1]
        e["is_winning_copy"] = (mine == win)
        if mine == win:
            win_count[mine] += 1
        out_rows.append({
            "entry_id": e["entry_id"], "unit_id": e["unit_id"], "kind": e["kind"], "label": e["label"],
            "this_record_mod": mine, "winning_source": win, "winning_title": titles.get(win, win),
            "is_winning_copy": "yes" if mine == win else "no", "winning_directive": d,
            "providers_in_load_order": " > ".join(provs), "asset_id": e.get("asset_id") or "",
            "mapping_status": e.get("mapping_status", ""), "missions_using_unit": len(missions),
            "missions": "; ".join(missions)})
    for x in m["mods"]:
        x["winning_definition_count"] = win_count.get(x["id"], 0)

    # SEST pack units the gallery does not index under any provider.
    indexed = {e["unit_id"].lower() for e in m["entries"]}
    sest_only = []
    for rel, real in sorted(index["SEST_Integration"].items()):
        if not rel.startswith(("aircraft/", "vessels/", "land_units/", "submarines/")):
            continue
        uid = Path(rel).stem
        if "_squadrons" in uid or "_variants" in uid or uid.startswith("_"):
            continue
        if uid not in indexed:
            sest_only.append({"unit_id": uid, "file": real,
                              "missions_using_unit": len(used.get(uid, ())),
                              "missions": "; ".join(sorted(used.get(uid, ())))})

    m["summary"]["load_order_alignment"] = {
        "build_commit": commit, "load_order_entries": len(tokens),
        "workshop_mods_in_order": sum(t != "SEST_Integration" for t in tokens),
        "records": len(rows), "records_resolved": sum(1 for r in rows if r[3]),
        "winning_copies": sum(win_count.values()),
        "winner_is_sest_pack": sum(1 for r in rows if r[3] == "SEST_Integration"),
        "winner_is_base_game": sum(1 for r in rows if r[3] == "vanilla"),
        "records_used_in_missions": sum(1 for r in out_rows if r["missions_using_unit"]),
        "sest_pack_units_not_indexed": len(sest_only),
        "method": "tools/align_gallery.py: first provider in data/load-order.tokens.txt wins; "
                  "SEST pack = integration/dist/SEST_Integration; base game = mods-source/_vanilla/original; "
                  "case-insensitive paths; #!extend/#!alias recorded, not followed."}
    (g / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    (g / "catalogue.js").write_text("window.CATALOGUE=" + json.dumps(m, ensure_ascii=False, separators=(",", ":")) + ";\n",
                                    encoding="utf-8")

    with (g / "data" / "load_order_alignment_191.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader(); w.writerows(out_rows)
    with (g / "data" / "sest_pack_units_not_indexed.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["unit_id", "file", "missions_using_unit", "missions"])
        w.writeheader(); w.writerows(sest_only)

    # The mapping CSV carries winning_source too; keep it in step.
    mp = g / "data" / "unit_image_mapping.csv"
    with mp.open(encoding="utf-8-sig", newline="") as fh:
        r = list(csv.DictReader(fh))
    byid = {e["entry_id"]: e for e in m["entries"]}
    for row in r:
        row["winning_source"] = byid[row["entry_id"]]["winning_source"]
    with mp.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(r[0]))
        w.writeheader(); w.writerows(r)
    print(json.dumps(m["summary"]["load_order_alignment"], indent=1))


if __name__ == "__main__":
    main()
