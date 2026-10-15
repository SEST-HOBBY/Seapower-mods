#!/usr/bin/env python3
"""Bring reviewed Wikimedia Commons photos into the gallery, with their
credits, and make them the units' encyclopedia pictures.

The photos come from the acquisition kit in tools/image-acquisition, run on
the gaming PC (Commons is not reachable from the build machine). Its output -
downloaded/ and ACQUIRED_IMAGES.csv - is pushed to a branch of its own and
never merged; only the photos a reviewer approves are copied here.

    commons/                 the approved photos, byte for byte as downloaded
    commons-photos.csv       one row per approved photo: the units it shows,
                             the review verdict and the Commons credit

Two steps:

    python3 integration/gallery/commons_photos.py intake <kit folder> <review.csv>
        copies every row of review.csv marked "approve" from the kit's
        downloaded/ into commons/ and writes its row into commons-photos.csv,
        with the credit from the kit's ACQUIRED_IMAGES.csv. The file's
        SHA-256 must match the kit's record.

    python3 integration/gallery/commons_photos.py apply
        puts every row of commons-photos.csv into source/ (catalogue.js,
        PHOTO_CREDITS.txt, data/unit_image_mapping.csv) and profiles.tsv.
        Run it again after editing the sheet; it only ever rewrites its own
        records. Then rebuild (tools/build_all.py). build_patch.py refuses
        to build a gallery this sheet is not applied to.

review.csv columns: asset_group, decision (approve or reject), verdict
(same_type, same_family or context), category (optional: a gallery
category, else taken from the units' folder), also_units (optional: more
unit ids, separated by ;, that the photo shows too), note. A group whose id
the gallery already uses for another photo is refused: an existing photo,
the SEST author's own above all, is never replaced from here. same_type and
same_family make the photo the units' encyclopedia picture (same_family is
labelled "Class photo"); context puts it in the gallery only.
"""
import csv
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "source"
STORE = HERE / "commons"
SHEET = HERE / "commons-photos.csv"
PROFILES = HERE / "profiles.tsv"
COLUMNS = ["file", "asset_id", "unit_ids", "label", "category", "verdict", "reference_type",
           "creator", "licence", "licence_url", "source_page", "source_file_title",
           "direct_url", "downloaded_url", "width", "height", "sha256", "changes",
           "date_checked", "note"]
CAT_DIR = {"Aircraft & helicopters": "aircraft", "Ships": "ships", "Submarines": "submarines",
           "Land units": "land", "Sensors & equipment": "sensors",
           "Bases & installations": "bases", "Weapons & ammunition": "weapons"}
VERDICTS = {"same_type": "exact_class_photo", "same_family": "family_reference",
            "context": "context_reference"}
UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units")
SUB = re.compile(r"(?i)(^|_)(ss|ssk|ssn|ssg|ssgn|ssbn)(_|-|$)|submarine|_sub_")
BASE = re.compile(r"(?i)airbase|airfield|^fob$|tent|govu|silo|powerplant|oil_pump|liberty|rig")


def unit_folders():
    """unit id (lower case) -> the folder its file is in, from the pack and
    mods-source, so a photo is only mapped to a unit the game has."""
    out = {}
    for base in [ROOT / "integration" / "dist" / "SEST_Integration"] + \
            sorted((ROOT / "mods-source").glob("*")) + [ROOT / "mods-source" / "_vanilla" / "original"]:
        for d in UNIT_DIRS:
            for f in (base / d).glob("*.ini") if (base / d).is_dir() else ():
                out.setdefault(f.stem.lower(), d)
    return out


def category_for(units, folders, given=""):
    if given:
        if given not in CAT_DIR:
            sys.exit(f"category {given!r} is not a gallery category ({', '.join(CAT_DIR)})")
        return given
    kinds = {folders.get(u.lower()) for u in units}
    if kinds == {"aircraft"}:
        return "Aircraft & helicopters"
    if kinds <= {"vessels", "submarines"}:
        return "Submarines" if any(SUB.search(u) for u in units) or "submarines" in kinds else "Ships"
    if kinds == {"land_units"}:
        return "Bases & installations" if all(BASE.search(u) for u in units) else "Land units"
    sys.exit(f"{', '.join(units)}: cannot tell the category ({kinds}); give one in review.csv")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_sheet(rows):
    with SHEET.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["asset_id"]))


def sheet():
    return read(SHEET) if SHEET.is_file() else []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --- intake --------------------------------------------------------------------

def intake(kit, review_path):
    kit = Path(kit)
    acquired = {r["asset_group"]: r for r in read(kit / "ACQUIRED_IMAGES.csv")}
    folders = unit_folders()
    rows = {r["asset_id"]: r for r in sheet()}
    existing = {a["asset_id"]: a["file"] for a in load_catalogue()["assets"]
                if a.get("origin") != "wikimedia_commons_reviewed"}
    taken = 0
    for rv in read(review_path):
        group = rv["asset_group"].strip()
        if rv["decision"].strip().lower() != "approve":
            continue
        a = acquired.get(group) or sys.exit(f"{group}: not in {kit / 'ACQUIRED_IMAGES.csv'}")
        verdict = rv["verdict"].strip()
        if verdict not in VERDICTS:
            sys.exit(f"{group}: verdict {verdict!r} is not one of {', '.join(VERDICTS)}")
        src = kit / a["local_file"]
        if not src.is_file():
            sys.exit(f"{group}: {src} is missing")
        if sha(src) != a["sha256"]:
            sys.exit(f"{group}: {src.name} does not match the kit's SHA-256 - re-download it")
        if group in existing:
            sys.exit(f"{group}: the gallery already has a photo by that id ({existing[group]}); "
                     "reject it in review.csv, or rename the group")
        units = [u.strip() for u in a["unit_ids"].split(";") + rv.get("also_units", "").split(";")
                 if u.strip()]
        known = [u for u in units if u.lower() in folders]
        if not known:
            sys.exit(f"{group}: none of {units} is a unit in the build")
        STORE.mkdir(exist_ok=True)
        name = f"{group}{src.suffix.lower()}"
        shutil.copyfile(src, STORE / name)
        rows[group] = {
            "file": name, "asset_id": group, "unit_ids": ";".join(known),
            "label": a["unit_labels"].split(";")[0].strip(),
            "category": category_for(known, folders, rv.get("category", "").strip()),
            "verdict": verdict, "reference_type": VERDICTS[verdict],
            "creator": a["author"], "licence": a["licence"], "licence_url": a["licence_url"],
            "source_page": a["source_page"], "source_file_title": a["source_file_title"],
            "direct_url": a["direct_url"], "downloaded_url": a["downloaded_url"],
            "width": a["width"], "height": a["height"], "sha256": a["sha256"],
            "changes": a["changes"], "date_checked": a["date_checked"],
            "note": rv.get("note", "").strip()}
        taken += 1
    write_sheet(rows.values())
    print(f"took in {taken} approved photo(s); commons-photos.csv holds {len(rows)}")


# --- apply ---------------------------------------------------------------------

def load_catalogue():
    text = (SOURCE / "catalogue.js").read_text(encoding="utf-8")
    return json.loads(re.match(r"window\.CATALOGUE=(.*);\s*$", text, re.S).group(1))


def gallery_file(row):
    return f"images/{CAT_DIR[row['category']]}/{row['asset_id']}_commons{Path(row['file']).suffix}"


def asset_fields(row):
    """The asset record one sheet row sets: the same function build_patch.py
    uses to check the gallery is up to date."""
    licence = row["licence"].strip()
    creator = row["creator"].strip() or "see source page"
    return {"label": row["label"], "category": row["category"], "file": gallery_file(row),
            "sha256": row["sha256"], "creator": creator, "license": licence,
            "license_url": row["licence_url"], "source_page": row["source_page"],
            "source_file_title": row["source_file_title"],
            "original_url": row["direct_url"], "download_url": row["downloaded_url"],
            "credit_line": f"{creator} · {licence} · {row['source_page']}",
            "attribution_required": "false" if licence in ("Public domain", "CC0") else "true",
            "reference_type": row["reference_type"], "origin": "wikimedia_commons_reviewed",
            "modifications": row["changes"] or "unmodified original",
            "retrieved_at": row["date_checked"],
            "reference_note": ("Reviewed against the unit: " + row["verdict"].replace("_", " ")
                               + (f". {row['note']}" if row["note"] else "."))}


def credits_block(row, a):
    return "\n".join([
        f"{a['asset_id']} — {a['label']}",
        f"Creator: {a['creator']}",
        f"Licence: {a['license']}" + (f" ({a['license_url']})" if a["license_url"] else ""),
        f"Source: {a['source_page']}",
        f"File: {a['source_file_title']}",
        f"Changes: {a['modifications']}",
        f"Reference limits: {a['reference_note']}", ""])


def remap(text, units, aid, file, status):
    """unit_image_mapping.csv with the rows of these units pointed at the
    photo; every other line is left byte for byte."""
    import io
    lines = text.split("\n")
    head = next(csv.reader([lines[0].lstrip("﻿")]))
    col = {k: i for i, k in enumerate(head)}
    for i, line in enumerate(lines[1:], 1):
        if not line.strip():
            continue
        cells = next(csv.reader([line]))
        if cells[col["unit_id"]].lower() not in units:
            continue
        cells[col["asset_id"]], cells[col["image_file"]] = aid, file
        cells[col["mapping_status"]] = status
        buf = io.StringIO()
        csv.writer(buf, lineterminator="").writerow(cells)
        lines[i] = buf.getvalue()
    return "\n".join(lines)


def apply():
    from PIL import Image
    rows = sheet()
    cat = load_catalogue()
    assets = {a["asset_id"]: a for a in cat["assets"]}
    credits = (SOURCE / "PHOTO_CREDITS.txt").read_text(encoding="utf-8")
    mapping = (SOURCE / "data" / "unit_image_mapping.csv").read_text(encoding="utf-8")
    profile_lines = PROFILES.read_text(encoding="utf-8").splitlines()
    for row in rows:
        src = STORE / row["file"]
        if not src.is_file() or sha(src) != row["sha256"]:
            sys.exit(f"commons-photos.csv: {row['file']} is missing from commons/ or its bytes changed")
        aid = row["asset_id"]
        a = assets.get(aid)
        if a is None:
            a = {"asset_id": aid}
            cat["assets"].append(a)
            assets[aid] = a
        elif a.get("origin") != "wikimedia_commons_reviewed" and a.get("file"):
            a["replaced_source"] = {k: a.get(k, "") for k in (
                "file", "creator", "license", "license_url", "source_page", "sha256", "label")}
        old = a.get("file", "")
        a.update(asset_fields(row))
        (SOURCE / a["file"]).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, SOURCE / a["file"])
        with Image.open(src) as im:
            a["width"], a["height"], a["format"] = im.width, im.height, im.format
        a["original_width"], a["original_height"] = row["width"], row["height"]
        a.setdefault("quality_review", {"quality_grade": "-", "subject_visibility_grade": "-",
                                        "priority": "P3",
                                        "reason": "Commons photo reviewed against the unit (October 2026).",
                                        "replacement_brief": "None queued."})
        units = {u.lower() for u in row["unit_ids"].split(";") if u}
        for e in cat["entries"]:
            if (e.get("unit_id") or "").lower() in units:
                e["asset_id"], e["image_file"] = aid, a["file"]
                e["mapping_status"] = row["reference_type"]
        if old and old != a["file"]:
            if not any(x.get("file") == old for x in cat["assets"]):
                (SOURCE / old).unlink(missing_ok=True)
        mapping = remap(mapping, units, aid, a["file"], row["reference_type"])
        block = credits_block(row, a)
        pat = re.compile(rf"^{re.escape(aid)} — .*?\n\n", re.M | re.S)
        credits = pat.sub(lambda _m: block + "\n", credits, count=1) if pat.search(credits) \
            else credits.rstrip("\n") + "\n\n" + block + "\n"
        # the encyclopedia picture: a reviewed photo takes a unit with no
        # row, or a row whose photo was judged wrong or unusable; a same_type
        # photo also takes a same_family row. A reviewed same_type row is
        # never replaced.
        if row["verdict"] in ("same_type", "same_family"):
            for uid in [u for u in row["unit_ids"].split(";") if u]:
                hit = next((i for i, l in enumerate(profile_lines)
                            if l.split("\t")[0].lower() == uid.lower()), None)
                new = f"{uid}\t{aid}\t{row['verdict']}\tWikimedia Commons, reviewed 15 Oct 2026"
                if hit is None:
                    profile_lines.append(new)
                else:
                    have = profile_lines[hit].split("\t")
                    if (have[1] == aid or have[2] not in ("same_type", "same_family")
                            or (have[2] == "same_family" and row["verdict"] == "same_type")):
                        profile_lines[hit] = new
    cat["summary"]["photo_assets"] = len(cat["assets"])
    cat["summary"]["unique_photo_hashes"] = len({a["sha256"] for a in cat["assets"]})
    cat["summary"]["commons_reviewed_photos"] = len(rows)
    (SOURCE / "catalogue.js").write_text(
        "window.CATALOGUE=" + json.dumps(cat, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")
    (SOURCE / "PHOTO_CREDITS.txt").write_text(credits, encoding="utf-8")
    (SOURCE / "data" / "unit_image_mapping.csv").write_text(mapping, encoding="utf-8")
    PROFILES.write_text("\n".join(profile_lines) + "\n", encoding="utf-8")
    print(f"applied {len(rows)} Commons photo(s)")


def stale(cat):
    """Sheet rows the catalogue does not carry as written: build_patch.py
    stops on any."""
    by = {a["asset_id"]: a for a in cat["assets"]}
    out = []
    for row in sheet():
        a = by.get(row["asset_id"])
        want = asset_fields(row)
        if not a or any(a.get(k) != v for k, v in want.items()):
            out.append(row["asset_id"])
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["intake"] and len(sys.argv) == 4:
        intake(sys.argv[2], sys.argv[3])
    elif sys.argv[1:] == ["apply"]:
        apply()
    else:
        sys.exit(__doc__)
