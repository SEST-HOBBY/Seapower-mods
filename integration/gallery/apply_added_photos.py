#!/usr/bin/env python3
"""Put the SEST author's own photos into the gallery, with their credits.

added/                    the photos as supplied (kept byte for byte)
added-photo-credits.csv   one row per photo: which gallery photo it replaces
                          (asset_id), and the credit to show - creator,
                          licence and source page. Edit the credit columns
                          here, then run this again.

    python3 integration/gallery/apply_added_photos.py

Each photo replaces the gallery photo with the same asset_id (an asset_id the
gallery does not have yet is added as a new photo). The replaced photo's
credit is kept on the record as `replaced_source`, its file leaves source/.
The campaign builder reads source/ for the briefing photos, so rebuild the
packs afterwards (tools/build_all.py). build_patch.py refuses to build a
gallery whose credits no longer match this file.

A blank credit shows as "Credit to be added" - in the gallery and in the
briefing captions - until it is filled in.
"""
import csv
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
ADDED = HERE / "added"
SHEET = HERE / "added-photo-credits.csv"
PENDING = "Credit to be added"
UNRECORDED = "Not recorded"
CAT_DIR = {"Aircraft & helicopters": "aircraft", "Ships": "ships", "Submarines": "submarines",
           "Land units": "land", "Sensors & equipment": "sensors",
           "Bases & installations": "bases", "Weapons & ammunition": "weapons"}
NEW_CATEGORY = {"alconbury": "Bases & installations"}


def rows():
    with SHEET.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def credit_fields(row):
    """The asset fields one sheet row sets: the same function build_patch.py
    uses to check the gallery is up to date."""
    creator = row["creator"].strip() or PENDING
    licence = row["licence"].strip() or UNRECORDED
    page = row["source_page"].strip()
    return {"creator": creator, "license": licence, "source_page": page,
            "license_url": "", "credit_line": f"{creator} · {licence}"
            + (f" · {page}" if page else ""),
            "origin": "sest_author_supplied"}


def load():
    js = SOURCE / "catalogue.js"
    return json.loads(re.match(r"window\.CATALOGUE=(.*);\s*$",
                               js.read_text(encoding="utf-8"), re.S).group(1))


def save(cat):
    (SOURCE / "catalogue.js").write_text(
        "window.CATALOGUE=" + json.dumps(cat, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")


def credits_block(a):
    return "\n".join([
        f"{a['asset_id']} — {a['label']}",
        f"Creator: {a['creator']}",
        f"Licence: {a['license']}",
        f"Source: {a['source_page'] or 'not recorded'}",
        "Supplied by: the SEST author (October 2026)",
        f"Changes: {a['modifications']}",
        f"Reference limits: {a['reference_note']}", ""])


def main():
    cat = load()
    assets = {a["asset_id"]: a for a in cat["assets"]}
    credits = (SOURCE / "PHOTO_CREDITS.txt").read_text(encoding="utf-8")
    mapping = (SOURCE / "data" / "unit_image_mapping.csv").read_text(encoding="utf-8")
    for row in rows():
        aid, src = row["asset_id"].strip(), ADDED / row["file"]
        if not src.is_file():
            sys.exit(f"{SHEET.name}: {row['file']} is not in added/")
        a = assets.get(aid)
        if a is None:
            category = NEW_CATEGORY.get(aid) or sys.exit(f"{aid}: not in the gallery and no category for a new photo")
            a = {"asset_id": aid, "category": category, "label": row["label"].strip() or aid,
                 "reference_note": "Supplied by the SEST author; not mapped to a unit.",
                 "reference_type": "context_reference", "file": ""}
            cat["assets"].append(a)
            assets[aid] = a
            credits = credits.rstrip("\n") + "\n\n"
        old_file = a["file"]
        new_file = f"images/{CAT_DIR[a['category']]}/{aid}_sest{src.suffix.lower()}"
        if old_file != new_file:
            if old_file:
                a["replaced_source"] = {k: a.get(k, "") for k in (
                    "file", "creator", "license", "license_url", "source_page", "sha256", "label")}
            (SOURCE / new_file).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, SOURCE / new_file)
        with Image.open(src) as im:
            a["width"], a["height"], a["format"] = im.width, im.height, im.format
        a["original_width"], a["original_height"] = a["width"], a["height"]
        a["sha256"] = hashlib.sha256(src.read_bytes()).hexdigest()
        a["file"] = new_file
        if row["label"].strip():
            a["label"] = row["label"].strip()
        a.update(credit_fields(row))
        for k in ("download_url", "original_url", "source_file_title", "photo_date", "photo_description"):
            a[k] = ""
        a["retrieved_at"] = "2026-10-05"
        a["modifications"] = "As supplied by the SEST author; no edits."
        a["attribution_required"] = "true"
        a["quality_review"] = {"quality_grade": "-", "subject_visibility_grade": "-", "priority": "P3",
                               "reason": "Replacement supplied by the SEST author (October 2026); not yet graded.",
                               "replacement_brief": "None queued."}
        for e in cat["entries"] + cat["systems"]:
            if e.get("asset_id") == aid:
                e["image_file"] = new_file
        if old_file and old_file != new_file:
            mapping = mapping.replace(f",{aid},{old_file},", f",{aid},{new_file},")
            if not any(x["file"] == old_file for x in cat["assets"]):
                (SOURCE / old_file).unlink(missing_ok=True)
        # the credits file: replace this photo's block, or add one
        block = credits_block(a)
        pat = re.compile(rf"^{re.escape(aid)} — .*?\n\n", re.M | re.S)
        credits = pat.sub(lambda _m: block + "\n", credits, count=1) if pat.search(credits) \
            else credits + block + "\n"
    cat["summary"]["photo_assets"] = len(cat["assets"])
    cat["summary"]["unique_photo_hashes"] = len({a["sha256"] for a in cat["assets"]})
    cat["summary"]["author_supplied_photos"] = len(rows())
    save(cat)
    (SOURCE / "PHOTO_CREDITS.txt").write_text(credits, encoding="utf-8")
    (SOURCE / "data" / "unit_image_mapping.csv").write_text(mapping, encoding="utf-8")
    pending = sum(1 for r in rows() if not r["creator"].strip())
    print(f"applied {len(rows())} author-supplied photos; {pending} still show '{PENDING}'")


if __name__ == "__main__":
    main()
