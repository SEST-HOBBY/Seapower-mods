#!/usr/bin/env python3
"""Build the SEST Gallery pack: the offline photo gallery, shipped as files.

The gallery is a set of web pages (gallery.html, visual_overhaul.html) with
the real photographs, flags and loading backgrounds they show, plus the
credits that have to travel with them. It is copied into the pack under
Gallery/ so a subscriber can open it from the pack's folder. The game reads
nothing here: no unit file has an image key, and none is invented. The one
in-game place for photos is the mission briefing, and the campaign builder
puts them there itself (recognition() in integration/campaign/build_pack.py,
reading source/ directly).

source/ is the player-facing part of the gallery handoff, aligned to the
build's load order by tools/align_gallery.py. The developer files (quality
report, source records, handoff notes, tools) stay out of the pack.

    python3 integration/gallery/build_patch.py
"""
import hashlib
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
OUT = HERE / "SEST_Gallery"

INFO = """[Language_en]
Name=SEST Gallery
Description=An offline photo gallery of the collection's units: open Gallery/gallery.html in a web browser. The same photos appear in the SEST mission briefings.

[Compatibility]
ApproximateVersion=0.8.4
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not (SOURCE / "gallery.html").is_file():
        sys.exit(f"{SOURCE} has no gallery.html")
    if OUT.exists():
        shutil.rmtree(OUT)
    target = OUT / "Gallery"
    shutil.copytree(SOURCE, target)
    (OUT / "_info.ini").write_text(INFO, encoding="utf-8")

    src = {p.relative_to(SOURCE): p for p in SOURCE.rglob("*") if p.is_file()}
    bad = [rel for rel, p in src.items() if digest(p) != digest(target / rel)]
    if bad:
        sys.exit(f"{len(bad)} gallery files differ after the copy, e.g. {bad[0]}")

    # Every file a page points at must be in the pack.
    import json
    import re
    text = (SOURCE / "catalogue.js").read_text(encoding="utf-8")
    cat = json.loads(re.match(r"window\.CATALOGUE=(.*);\s*$", text, re.S).group(1))
    wanted = {a["file"] for a in cat["assets"]}
    wanted |= {e["image_file"] for e in cat["entries"] + cat["systems"] if e.get("image_file")}
    missing = sorted(f for f in wanted if not (target / f).is_file())
    if missing:
        sys.exit(f"{len(missing)} photos the gallery shows are missing, e.g. {missing[0]}")

    print(f"built {OUT.name}: {len(src)} files, {len(cat['assets'])} photos")


if __name__ == "__main__":
    main()
