#!/usr/bin/env python3
"""Build the SEST Gallery pack: the offline photo gallery, shipped as files.

The gallery is a set of web pages (gallery.html, visual_overhaul.html) with
the real photographs, flags and loading backgrounds they show, plus the
credits that have to travel with them. It is copied into the pack under
Gallery/ so a subscriber can open it from the pack's folder. The game does
not read Gallery/.

It also writes encyclopedia PROFILE PICTURES: the game shows
ui/profiles/<unit id>.png as a unit's picture, found by file name (the
convention 2,359 profile images across the collection use, and the
real-photos mod 3796706214 relies on). The SEST pack is first in the order,
so its picture is the one shown. Pictures come only from profiles.tsv: unit
and photo pairs two reviewers looked at and passed (same type, or same
family - labelled "class photo" on the picture). A checked SEST photo
replaces whatever picture the unit had (the base game's, a mod's render),
with one exception: where the unit's picture comes from the real-photos mod
(existing-profiles.tsv, listed on the gaming PC by tools/list-profiles.ps1)
and SEST only has a class photo, that mod's exact photo stays. Each is 1024x310, the
3.3:1 strip the collection's aircraft and ship profiles use: the whole photo
centred over a darkened, blurred copy of itself, with its credit.

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

    # The author-supplied photos: every row of the credits sheet must already
    # be in the catalogue, with the same credit and the same bytes.
    sys.path.insert(0, str(HERE))
    import apply_added_photos as added
    by_id = {a["asset_id"]: a for a in cat["assets"]}
    for row in added.rows():
        a = by_id.get(row["asset_id"].strip())
        want = added.credit_fields(row)
        if (not a or any(a.get(k) != v for k, v in want.items())
                or a["sha256"] != digest(added.ADDED / row["file"])):
            sys.exit(f"{row['file']}: added-photo-credits.csv is not applied - run "
                     "python3 integration/gallery/apply_added_photos.py, then rebuild")

    profiles = write_profiles(cat)

    print(f"built {OUT.name}: {len(src)} files, {len(cat['assets'])} photos, "
          f"{profiles} profile pictures")


PROFILES = HERE / "profiles.tsv"
EXISTING = HERE / "existing-profiles.tsv"
PROFILE_SIZE = (1024, 310)
REAL_PHOTOS = "3796706214"
CREDIT_NAMES = {"hobart": "Japan Maritime Self-Defense Force", "type003": "China News Service"}


def credit_line(asset, family):
    import re
    if asset.get("origin") == "sest_author_supplied" and asset.get("creator") == "Credit to be added":
        who = "supplied by the SEST author"
    else:
        who = CREDIT_NAMES.get(asset["asset_id"]) or re.sub(r"https?://\S+", "", asset.get("creator") or "")
        who = re.sub(r"[\u2e80-\u9fff\uac00-\ud7af\uff00-\uffef]+", "", who)
        # "U.S. Navy photo by Mass Communication Specialist 1st Class X" -> "U.S. Navy, MC1 X"
        who = re.sub(r"\s+photo by\s+", ", ", who)
        who = re.sub(r"Mass Communication Specialist (\d)\w* Class", r"MC\1", who)
        who = re.sub(r"Mass Communication Specialist Seaman", "MCSN", who)
        who = re.sub(r"Senior Airman", "SrA", who)
        who = re.sub(r"Staff Sgt\.|Staff Sergeant", "SSgt", who)
        who = re.sub(r"Tech(nical)? Sgt\.|Technical Sergeant", "TSgt", who)
        who = re.sub(r"\s+", " ", who).strip(" ,;") or "see Gallery/PHOTO_CREDITS.txt"
        if len(who) > 60:
            who = who[:57].rstrip() + "..."
    lic = (asset.get("license") or "").strip()
    text = f"Photo: {who}" + (f" · {lic}" if lic and lic != "Not recorded" else "")
    return ("Class photo · " if family else "") + text


def profile_png(path, credit):
    import io
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
    W, H = PROFILE_SIZE
    im = Image.open(path).convert("RGB")
    # Trim sky and sea: a side-on ship or aircraft sits in the middle band of
    # most photos, and the 3.3:1 strip would otherwise shrink it to a sliver.
    if im.width / im.height < 2.0:
        h = round(im.width / 2.0)
        top = (im.height - h) // 2
        im = im.crop((0, top, im.width, top + h))
    bg = im.copy()
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((max(W, round(bg.width * s)), max(H, round(bg.height * s))), Image.LANCZOS)
    x, y = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    s = min(W / im.width, H / im.height)
    fg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    d = ImageDraw.Draw(bg, "RGBA")
    try:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except OSError:
        fnt = ImageFont.load_default()
    tw = d.textlength(credit, font=fnt)
    d.rectangle([W - tw - 16, H - 24, W, H], fill=(0, 0, 0, 170))
    d.text((W - 8, H - 4), credit, font=fnt, fill=(225, 230, 235), anchor="rd")
    buf = io.BytesIO()
    bg.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def write_profiles(cat):
    """ui/profiles/<unit id>.png for the reviewed pairs in profiles.tsv."""
    if not PROFILES.is_file():
        return 0
    order = {l.strip() for l in (HERE.parents[1] / "data" / "load-order.tokens.txt")
             .read_text().splitlines() if l.strip().isdigit()}
    real_photo = set()       # units the real-photos mod pictures
    for line in EXISTING.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or line.startswith("id\t") or "\t" not in line:
            continue
        uid, mod, _size = line.split("\t")
        if mod == REAL_PHOTOS and mod in order:
            real_photo.add(uid.lower())
    assets = {a["asset_id"]: a for a in cat["assets"]}
    out = OUT / "ui" / "profiles"
    n = 0
    for line in PROFILES.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or line.startswith("unit_id\t") or not line.strip():
            continue
        uid, aid, verdict = line.split("\t")[:3]
        if verdict not in ("same_type", "same_family"):
            continue
        if verdict == "same_family" and uid.lower() in real_photo:
            continue          # that mod's exact photo beats a class photo
        a = assets.get(aid)
        if not a:
            sys.exit(f"profiles.tsv: {uid} names photo {aid}, which the gallery does not have")
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{uid}.png").write_bytes(
            profile_png(SOURCE / a["file"], credit_line(a, verdict == "same_family")))
        n += 1
    return n


if __name__ == "__main__":
    main()
