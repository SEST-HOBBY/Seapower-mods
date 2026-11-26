#!/usr/bin/env python3
"""Rebuild the third-party derivation inventory of the shipped MNO item.

Read-only over the repo. Writes JSON to the scratchpad.
"""
import collections, hashlib, json, re, sys
from pathlib import Path

ROOT = Path("/home/claude/Seapower-mods")
DIST = ROOT / "integration/dist/SEST_Integration"
MS = ROOT / "mods-source"
OUT = Path(sys.argv[1])

# --- reuse check_pack_fidelity's own resolution for the replenishment pack
sys.path.insert(0, str(ROOT / "tools"))
import check_pack_fidelity as fid  # noqa: E402

# --- source index
def info_name(d):
    p = d / "_info.ini"
    if p.is_file():
        m = re.search(r"^Name=(.*)$", p.read_text(encoding="utf-8", errors="replace"), re.M)
        if m:
            return m.group(1).strip()
    return ""

cat = json.loads((ROOT / "data/mod-catalog.json").read_text())
catalog = {m["workshop_id"]: m for m in cat["mods"] if m.get("workshop_id")}

mod_dirs = {}
for d in MS.iterdir():
    if d.is_dir() and d.name.isdigit():
        mod_dirs[d.name] = d
for d in (MS / "_retired").iterdir():
    if d.is_dir() and d.name.isdigit():
        mod_dirs[d.name] = d

SKIP_NAMES = {"_info.ini"}
by_base = collections.defaultdict(list)    # basename.lower() -> [(wid, path)]
by_hash = collections.defaultdict(list)
for wid, d in mod_dirs.items():
    for f in d.rglob("*"):
        if not f.is_file() or f.name in SKIP_NAMES:
            continue
        by_base[f.name.lower()].append((wid, f))
        by_hash[hashlib.sha256(f.read_bytes()).hexdigest()].append((wid, f))

REC = ROOT / "integration/raaf-f-35a-jatm/recovered"
for f in REC.rglob("*"):
    if f.is_file() and f.name != "SHA256SUMS":
        by_hash[hashlib.sha256(f.read_bytes()).hexdigest()].append(("3514484654", f))
vanilla_base = collections.defaultdict(list)
for f in (MS / "_vanilla" / "original").rglob("*"):
    if f.is_file():
        vanilla_base[f.name.lower()].append(f)

def wid_of(path):
    path = Path(path)
    try:
        rel = path.relative_to(MS)
    except ValueError:
        return None
    parts = rel.parts
    if parts[0] == "_retired":
        return parts[1]
    if parts[0].isdigit():
        return parts[0]
    if parts[0] == "_vanilla":
        return "vanilla" if parts[1] == "original" else "old-sest"
    return None

def norm(b):
    return b.replace(b"\r\n", b"\n")

def content_lines(b):
    out = []
    for l in b.decode("utf-8", "replace").splitlines():
        s = l.strip()
        if not s or s.startswith(("#", ";", "//")):
            continue
        out.append(s)
    return out

TRIVIAL = re.compile(r"^\[[^\]]+\]$")

def overlap(shipped, source):
    """share of the shipped file's content lines (excluding bare section
    headers) found in the source, and number of such lines."""
    a = [l for l in content_lines(shipped) if not TRIVIAL.match(l)]
    if not a:
        return 0.0, 0, 0
    s = set(content_lines(source))
    hit = sum(1 for l in a if l in s)
    return hit / len(a), hit, len(a)

EXTEND = re.compile(rb"^#!(extend|copy|alias)\s+(\S+)", re.M)
WID_RE = re.compile(r"\b(3[3-8]\d{8})\b")

# map dist file -> source pack
packs = sorted(p for p in (ROOT / "integration").glob("*/SEST_*")
               if p.is_dir() and p.parent.name != "dist")
pack_of = {}
for p in packs:
    for f in p.rglob("*"):
        if f.is_file():
            pack_of.setdefault(f.relative_to(p).as_posix(), p.parent.name)

repl_variants = {f"{c}_variants" for c in fid.CLONES}

records = []
for f in sorted(DIST.rglob("*")):
    if not f.is_file():
        continue
    rel = f.relative_to(DIST).as_posix()
    pack = pack_of.get(rel, "dist")
    blob = f.read_bytes()
    h = hashlib.sha256(blob).hexdigest()
    rec = {"rel": rel, "pack": pack, "cls": None, "wid": None, "src": None,
           "overlap": None, "how": None}
    # 1. byte-identical to an author file anywhere (any type)
    hits = by_hash.get(h) or []
    if not hits and rel.endswith((".ini", ".txt", ".csv", ".json")):
        # CRLF-normalised identity
        pass
    if hits:
        wid, src = hits[0]
        rec.update(cls="verbatim", wid=wid, src=str(src.relative_to(ROOT)),
                   overlap=1.0, how="sha256 equal to an author file",
                   also=[w for w, _ in hits[1:]])
        records.append(rec)
        continue
    if rel.startswith("Gallery/") or rel.startswith("ui/profiles/") \
            or not rel.lower().endswith((".ini", ".txt")) or rel.startswith(("campaigns/", "missions/", "legacy_campaigns/", "dynamic_campaigns/")):
        # photos, SEST code, campaigns: only byte identity matters here;
        # campaigns/missions are SEST-original scenario text that names units.
        rec["cls"] = "sest"
        rec["how"] = "SEST file type (campaign/mission/gallery/plugin/script); no byte match to any author file"
        records.append(rec)
        continue

    # 2. replenishment pack: exact upstream from the fidelity checker
    if pack == "replenishment" and rel.startswith(("vessels/", "ammunition/")):
        stem = Path(rel).stem
        if stem in repl_variants:
            # generated from scratch; names the clone's ships
            donor_mod = fid.CLONES[stem[:-9]]["donor"][0]
            rec.update(cls="sest", wid=None if donor_mod == "vanilla" else donor_mod,
                       how="generated _variants file for a SEST clone (fidelity: no upstream by design)")
            records.append(rec)
            continue
        src = fid.upstream_for(rel)
        src = Path(src)
        w = wid_of(src)
        ov = overlap(blob, src.read_bytes())
        if stem in fid.CLONES:
            how = "SEST clone: donor file + supply block + refit (check_pack_fidelity)"
        else:
            how = "load-order-winning upstream + RAS insertions only (check_pack_fidelity)"
        if norm(blob) == norm(src.read_bytes()):
            cls = "verbatim"
        else:
            cls = "close"
        if w == "vanilla":
            cls = "vanilla-" + cls
        rec.update(cls=cls, wid=None if w == "vanilla" else w,
                   src=str(src.relative_to(ROOT)), overlap=round(ov[0], 3), how=how,
                   lines=[ov[1], ov[2]])
        records.append(rec)
        continue

    # 3. everything else: candidates by basename and by #!extend target
    cands = []
    base = f.name.lower()
    m = EXTEND.search(blob)
    target_base = None
    if m:
        target_base = Path(m.group(2).decode()).name.lower()
    names = {base}
    if target_base:
        names.add(target_base)
    for n in names:
        for wid, p in by_base.get(n, []):
            cands.append((wid, p))
    best = None
    for wid, p in cands:
        ov = overlap(blob, p.read_bytes())
        if norm(blob) == norm(p.read_bytes()):
            ov = (1.0, ov[1], ov[2])
            best = (2.0, wid, p, ov, "verbatim")
            break
        key = (ov[0], ov[1])
        if best is None or key > (best[3][0], best[3][1]):
            best = (ov[0], wid, p, ov, None)
    vov = (0.0, 0, 0)
    for n in names:
        for p in vanilla_base.get(n, []):
            o = overlap(blob, p.read_bytes())
            if o[0] > vov[0]:
                vov = o
    text = blob.decode("utf-8", "replace")
    named = sorted(set(WID_RE.findall(text)) & set(mod_dirs))
    if best and best[4] == "verbatim":
        rec.update(cls="verbatim", wid=best[1], src=str(best[2].relative_to(ROOT)),
                   overlap=1.0, how="CRLF-normalised equal to the author file")
    elif best and vov[0] >= 0.9 and vov[1] >= best[3][1]:
        rec.update(cls="vanilla-close", wid=None, src=str(best[2].relative_to(ROOT)),
                   overlap=round(best[3][0], 3), vanilla_overlap=round(vov[0], 3),
                   how=f"the game's own file restored or patched: {vov[1]}/{vov[2]} lines are the game's, {best[3][1]} the author's",
                   lines=[best[3][1], best[3][2]], named=named, author_wid=best[1])
    elif best and best[3][0] >= 0.5 and best[3][1] >= 3:
        cls = "close"
        how = f"{best[3][1]}/{best[3][2]} content lines are the author's"
        if vov[0] >= best[3][0] and vov[1] >= best[3][1]:
            how += f"; vanilla has as many ({vov[1]}/{vov[2]})"
        rec.update(cls=cls, wid=best[1], src=str(best[2].relative_to(ROOT)),
                   overlap=round(best[3][0], 3), how=how, lines=[best[3][1], best[3][2]],
                   vanilla_overlap=round(vov[0], 3))
    else:
        wid = best[1] if best else (named[0] if named else None)
        rec.update(cls="sest", wid=wid,
                   src=str(best[2].relative_to(ROOT)) if best else None,
                   overlap=round(best[3][0], 3) if best else None,
                   how=("SEST-written patch; " + (f"{best[3][1]}/{best[3][2]} lines shared with the author file" if best else "no same-name author file"))
                   + (f"; extends {target_base}" if target_base else ""),
                   lines=[best[3][1], best[3][2]] if best else None,
                   vanilla_overlap=round(vov[0], 3), named=named)
    records.append(rec)

OUT.write_text(json.dumps({"records": records,
                           "titles": {w: info_name(d) for w, d in mod_dirs.items()},
                           "catalog": {w: {"title": m.get("title"), "author": m.get("author"),
                                           "status": m.get("status")} for w, m in catalog.items()}},
                          indent=1))
c = collections.Counter(r["cls"] for r in records)
print(len(records), c)
