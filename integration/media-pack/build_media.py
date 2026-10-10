#!/usr/bin/env python3
"""Build the SEST media pack: loading-screen and menu crops from the Commons
photographs, a solid fallback, the manifest and the credits.

    python3 integration/media-pack/build_media.py

Reads sources.json (the 10 Oct 2026 media report's 24 items) and
source/fetched.json (what tools/fetch-media-pack.ps1 brought down on the PC,
with the licence each file page gave). Writes:

  game_ready/loading/<1080p|1440p|2160p>/<id>.jpg   16:9 loading backgrounds
  game_ready/menu/static/<res>/<id>.jpg             the menu candidates, darkened
  game_ready/menu/fallback/solid/solid_0b1115_<res>.png
  media_manifest.csv                                 one row per source
  ATTRIBUTION.md                                     credits for what ships

game_ready/ is not committed: it is rebuilt from the committed photographs.
The manifest and the credits are, so a review sees what the pack holds.

The rules are the report's. A crop is cut from the photograph, never
stretched, and a size the photograph cannot fill is not made - no upscaling,
so a 2100 px master gives 1080p only. A portrait photograph (the SM-3 launch)
is set to one side of a dark panel at full height instead of being cropped
to a sliver. The menu versions are the same crops under a 30% darkening, the
report's 25-40%, so the game's buttons stay the brightest thing on screen.
Nothing is generated or retouched: crop, resize, darken, and for the portrait
a plain dark panel. No text is burned in; the game draws its own.

Which folder the game reads loading backgrounds from is not yet known (the
loading screen fetches them through the game's FileManager, but the repo's
copy of the game's files is text only); tools/capture-context.ps1 now lists
the game's pictures in data/install-snapshot/streaming-media.txt, and the
pack wires game_ready/loading/ in once that says where.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIZES = {"1080p": (1920, 1080), "1440p": (2560, 1440), "2160p": (3840, 2160)}
SOLID = (0x0B, 0x11, 0x15)          # the report's near-black slate, #0B1115
MENU_DARKEN = 0.30
QUALITY = 90
LICENCE_TEXT = {
    "LicenseRef-PD-USGov": "Public domain in the United States as a work of the U.S. federal "
                           "government produced in the course of official duties "
                           "(17 U.S.C. 105). Wikimedia Commons: Public Domain Mark 1.0.",
    "CC0-1.0": "Creative Commons Zero v1.0 Universal (CC0 1.0), "
               "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-3.0": "Creative Commons Attribution 3.0 Unported (CC BY 3.0), "
                 "https://creativecommons.org/licenses/by/3.0/",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(root):
    spec = json.loads((root / "sources.json").read_text(encoding="utf-8"))
    rec = root / "source" / "fetched.json"
    fetched = {"files": [], "refused": []}
    if rec.is_file():
        fetched = json.loads(rec.read_text(encoding="utf-8-sig"))
    files = {f["id"]: f for f in fetched.get("files") or []}
    refused = {r["id"]: r["reason"] for r in fetched.get("refused") or []}
    return spec, files, refused


def crop_16x9(im, focus):
    """The largest 16:9 window of `im`, centred on `focus` (fractions of
    width and height) and kept inside the frame."""
    w, h = im.size
    cw = min(w, h * 16 / 9)
    ch = cw * 9 / 16
    fx, fy = focus
    x = min(max(fx * w - cw / 2, 0), w - cw)
    y = min(max(fy * h - ch / 2, 0), h - ch)
    return im.crop((round(x), round(y), round(x + cw), round(y + ch)))


def loading_frame(im, focus, size):
    """The photograph as a `size` loading background, or None when it cannot
    fill `size` without upscaling."""
    from PIL import Image
    tw, th = size
    w, h = im.size
    if w / h < 1.0:
        # portrait: full height on a dark panel, on the side focus[0] names
        if h < th:
            return None
        pw = round(w * th / h)
        photo = im.resize((pw, th), Image.LANCZOS)
        frame = Image.new("RGB", size, SOLID)
        x = round((tw - pw) * (0.82 if focus[0] >= 0.5 else 0.18))
        frame.paste(photo, (x, 0))
        return frame
    window = crop_16x9(im, focus)
    if window.size[0] < tw * 0.99:      # 1% short (the P-8A's 3813 px) is not upscaling
        return None
    return window.resize(size, Image.LANCZOS)


def darken(im, amount):
    from PIL import Image
    return Image.blend(im, Image.new("RGB", im.size, (0, 0, 0)), amount)


def save_jpg(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=False, subsampling=0)
    path.write_bytes(buf.getvalue())


def build(root, out, quiet=False):
    from PIL import Image
    spec, files, refused = load(root)
    rows, shipped, deferred = [], [], []
    for s in spec["sources"]:
        f = files.get(s["id"])
        row = {"id": s["id"], "priority": s["priority"], "kind": s["kind"],
               "category": s["category"], "original_filename": s["title"],
               "source_url": s["page"], "creator": s["creator"],
               "license_expression": s["license"],
               "license_as_published": f.get("license", "") if f else "",
               "attribution_required": "true" if s["license"].startswith("CC-BY") else "false",
               "original_width": f.get("original_width", "") if f else "",
               "original_height": f.get("original_height", "") if f else "",
               "duration_seconds": "", "game_use": "+".join(s["uses"]),
               "derivative_filename": "", "modifications": "", "sha256": "", "status": ""}
        if s["stage"] != "ship":
            row["status"] = "deferred: stage two (menu video)"
            deferred.append((s, row))
            rows.append(row)
            continue
        if s["id"] in refused:
            row["status"] = "refused: " + refused[s["id"]]
            rows.append(row)
            continue
        src = root / f["file"] if f else None
        if not f or not src.is_file():
            row["status"] = "awaiting download (tools/fetch-media-pack.ps1)"
            rows.append(row)
            continue
        if sha256(src) != f["sha256"]:
            row["status"] = "sha256 mismatch - re-fetch"
            rows.append(row)
            continue
        with Image.open(src) as raw:
            im = raw.convert("RGB")
        made, menu = [], []
        for label, size in SIZES.items():
            frame = loading_frame(im, s["focus"], size)
            if frame is None:
                continue
            rel = f"loading/{label}/{s['id']}.jpg"
            save_jpg(frame, out / rel)
            made.append(rel)
            if "menu" in s["uses"]:
                mrel = f"menu/static/{label}/{s['id']}.jpg"
                save_jpg(darken(frame, MENU_DARKEN), out / mrel)
                menu.append(mrel)
        portrait = im.size[0] < im.size[1]
        mods = ["set at full height on a dark #0B1115 panel" if portrait else
                "16:9 crop from the photograph", "resized (Lanczos)", "re-encoded as JPEG"]
        if menu:
            mods.append(f"menu versions darkened {round(MENU_DARKEN * 100)}%")
        row.update(derivative_filename="; ".join(made + menu), modifications="; ".join(mods),
                   sha256=f["sha256"],
                   status="ready" if made else "too small for 1080p - not shipped")
        rows.append(row)
        if made:
            shipped.append((s, f, row, mods))
    for label, size in SIZES.items():
        p = out / f"menu/fallback/solid/solid_0b1115_{label}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        buf = io.BytesIO()
        Image.new("RGB", size, SOLID).save(buf, "PNG", optimize=True)
        p.write_bytes(buf.getvalue())
    write_manifest(root / "media_manifest.csv", rows)
    write_attribution(root / "ATTRIBUTION.md", shipped, deferred, spec)
    if not quiet:
        ready = sum(1 for r in rows if r["status"] == "ready")
        waiting = sum(1 for r in rows if r["status"].startswith("awaiting"))
        print(f"media pack: {ready} photograph(s) ready, {waiting} awaiting download, "
              f"{sum(1 for r in rows if r['status'].startswith('refused'))} refused, "
              f"{len(deferred)} video(s) deferred -> {out}")
    return rows


def write_manifest(path, rows):
    cols = ["id", "priority", "kind", "category", "original_filename", "source_url", "creator",
            "license_expression", "license_as_published", "attribution_required",
            "original_width", "original_height", "duration_seconds", "game_use",
            "derivative_filename", "modifications", "sha256", "status"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    path.write_text(buf.getvalue(), encoding="utf-8")


def write_attribution(path, shipped, deferred, spec):
    out = ["# SEST media pack - attribution", "",
           "Photographs from Wikimedia Commons used for the SEST loading screens and menu "
           "backgrounds. Every file's licence was read from its own Commons page when it was "
           "downloaded (integration/media-pack/source/fetched.json records what the page said). "
           "No NonCommercial, NoDerivatives, fair-use or unclear-rights file is included.", "",
           "Use of these images does not imply endorsement by the photographers, the U.S. Navy, "
           "the U.S. Air Force, the U.S. Space Force, the U.S. Department of Defense or any "
           "other government. No seal or insignia is used as SEST branding.", "",
           "`LicenseRef-PD-USGov` in the manifest means: public-domain U.S. federal-government "
           "work under 17 U.S.C. 105; the Commons file page marks it public domain. "
           "Attribution is kept for provenance.", ""]
    if not shipped:
        out += ["_No photograph has been downloaded yet: run tools/fetch-media-pack.ps1 on the PC._", ""]
    for s, f, row, mods in shipped:
        who = f.get("artist") or s["creator"]
        out += [f"## {s['title'].replace('_', ' ').rsplit('.', 1)[0]}", "",
                f"- Creator: {who}",
                f"- Source: {f.get('page') or s['page']}",
                f"- Licence: {LICENCE_TEXT[s['license']]}",
                f"- As published on Commons: {f.get('license', '')}"
                + (f" ({f['license_url']})" if f.get("license_url") else ""),
                f"- Retrieved: {f.get('retrieved_at', '')}",
                f"- SEST modifications: {'; '.join(mods)}.", ""]
    out += ["## Not shipped yet: the menu films (stage two)", "",
            "The main menu's film is inside the game's Unity data, not a file a mod can "
            "replace, so these are held back until a hook exists. Each would be excerpted, "
            "cropped to 16:9, muted and re-encoded as H.264 MP4.", ""]
    for s, row in deferred:
        lic = "CC BY 3.0 - attribution required" if s["license"] == "CC-BY-3.0" else s["license"]
        out.append(f"- {s['title']} - {s['creator']} - {lic} - {s['page']}")
    out += ["", "## Rejected", ""]
    for r in spec.get("rejected", []):
        out.append(f"- {r['title']}: {r['reason']}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=HERE,
                    help="folder holding sources.json and source/ (default: this one)")
    ap.add_argument("--out", type=Path, help="game-ready output (default: <root>/game_ready)")
    args = ap.parse_args()
    build(args.root, args.out or args.root / "game_ready")


if __name__ == "__main__":
    sys.exit(main())
