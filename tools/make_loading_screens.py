#!/usr/bin/env python3
"""Make the SEST loading-screen set: 29 photographs for the game's 80
loading-screen slots.

    python3 tools/make_loading_screens.py

The game draws its loading-screen backgrounds from ui/backgrounds/
loading_screen_1.png .. loading_screen_80.png (data/install-snapshot/
streaming-media.txt, 10 Oct 2026, game 0.8.5) and looks them up through its
FileManager, so a file of the same name in the SEST pack - first in the load
order - stands in for the game's. One collection mod (3491248180) already
ships 30 of the 80 that way.

The set is the 17 media-report photographs (integration/media-pack, cropped
16:9 by build_media.py) and the 12 gallery loading backgrounds
(integration/gallery/source/visuals/loading), interleaved so neighbouring
slots differ. Written to integration/media-pack/loading/ as
sest_loading_01.jpg .. _29.jpg with LOADING_CREDITS.txt; build_pack.py copies
them into the 80 slots in turn. Committed, not rebuilt by build_all, like the
menu film: the encoder's bytes are not stable across Pillow versions.

The slots are named .png and these are JPEG data. The game loads both
(ui/photos and ui/artwork mix .jpg and .png), and a JPEG is a sixth of a
PNG's size - 80 PNG photographs would add 176 MB to the pack.
"""
import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "integration" / "media-pack"
GALLERY = ROOT / "integration" / "gallery" / "source"
OUT = MEDIA / "loading"
W, H, QUALITY = 1920, 1080, 88

# Interleaved: command, sea, air and ISR take turns.
ORDER = ["cspoc", "g:hobart", "p8a_whidbey", "g:f35a_raaf", "lincoln_csg", "g:collins",
         "e2d_philippine_sea", "g:arleigh_burke", "triton", "g:chungmugong", "caoc", "g:maya",
         "kc46_e2d", "g:mh60r", "rc135", "g:virginia_ssn", "te_kaha", "g:p8a", "u2_cockpit",
         "g:patriot", "f35a_hill", "g:leclerc", "kc46_b1", "g:caesar", "rq4", "b2",
         "sm3_decatur", "global_hawk_wide", "cic_vinson"]


def main():
    from PIL import Image
    report = {f["id"]: f for f in json.loads((MEDIA / "source" / "fetched.json").read_text(encoding="utf-8-sig"))["files"]}
    spec = {s["id"]: s for s in json.loads((MEDIA / "sources.json").read_text(encoding="utf-8"))["sources"]}
    with open(GALLERY / "data" / "loading_screen_manifest.csv", encoding="utf-8-sig") as fh:
        gallery = {r["id"]: r for r in csv.DictReader(fh)}
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("sest_loading_*.jpg"):
        old.unlink()
    credits = []
    for n, key in enumerate(ORDER, 1):
        if key.startswith("g:"):
            g = gallery[key[2:]]
            src = GALLERY / g["file"]
            who, lic, page, label = g["creator"], g["license"], g["source_page"], g["label"]
            changes = "fitted to 1920x1080 with dark letterboxing (SEST Gallery)"
        else:
            src = MEDIA / "game_ready" / "loading" / "1080p" / f"{key}.jpg"
            if not src.is_file():
                sys.exit(f"{src} missing - run integration/media-pack/build_media.py first")
            f, s = report[key], spec[key]
            who, lic, page = f.get("artist") or s["creator"], f["license"], f["page"]
            label = s["title"].replace("_", " ").rsplit(".", 1)[0]
            changes = "16:9 crop and resize to 1920x1080 (integration/media-pack/build_media.py)"
        with Image.open(src) as raw:
            im = raw.convert("RGB")
        if im.size != (W, H):
            sys.exit(f"{src}: {im.size}, expected {W}x{H}")
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=False)
        (OUT / f"sest_loading_{n:02d}.jpg").write_bytes(buf.getvalue())
        credits.append(f"sest_loading_{n:02d}  {label}\n  Creator: {who}\n  Licence: {lic}\n"
                       f"  Source: {page}\n  Changes: {changes}; JPEG.\n")
    (OUT / "LOADING_CREDITS.txt").write_text(
        "SEST LOADING SCREENS - photo credits\n\n"
        "The game's 80 loading-screen backgrounds (ui/backgrounds/loading_screen_N.png) are\n"
        f"replaced in turn by these {len(ORDER)} photographs: slot N shows photograph\n"
        f"((N - 1) mod {len(ORDER)}) + 1. Real photographs only; no AI imagery. Use does not imply\n"
        "endorsement by the photographers or any armed service.\n\n" + "\n".join(credits),
        encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.glob("sest_loading_*.jpg"))
    print(f"{OUT.relative_to(ROOT)}: {len(ORDER)} photographs, {size // 1024} KB")


if __name__ == "__main__":
    main()
