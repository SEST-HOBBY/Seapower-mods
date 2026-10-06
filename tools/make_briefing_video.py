#!/usr/bin/env python3
"""Build the Briefing Room film: the SEST pack's title card for the mission
browser, a slideshow of the collection's forces with the quotation set over
it.

    python3 tools/make_briefing_video.py            # writes the mp4 + credits
    python3 tools/make_briefing_video.py --preview  # one PNG per slide instead

Output goes to integration/campaign/briefing_room/ (sest_briefing_room.mp4
and VIDEO_CREDITS.txt), which integration/campaign/build_pack.py copies into
missions/SEST Briefing Room/_data/ and points a Type=Tutorial entry's
RightPane= at - the hook the game's own Video Tutorials use. The film is
committed, not rebuilt by build_all: ffmpeg's bytes differ between versions
and the regression gate wants the pack byte-identical on every machine.

Frames are drawn with Pillow (slow zoom on each photograph, a dark band with
the quotation, the photo credit in the corner, cross-fades between slides)
and piped raw to ffmpeg, which encodes H.264 in an mp4 with the moov atom in
front - the shape Unity's video player on Windows reads. Every photograph is
from the pack's own gallery, chosen for a public-domain or CC licence, and
VIDEO_CREDITS.txt names the photographer, licence and source page of each.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "integration"))
from common import quotes  # noqa: E402

GALLERY = ROOT / "integration" / "gallery" / "source"
OUT = ROOT / "integration" / "campaign" / "briefing_room"
FONTS = Path("/usr/share/fonts/truetype/dejavu")
W, H, FPS = 1280, 720, 24
SLIDE, FADE, TITLE, END = 5.0, 0.7, 4.0, 6.0

# (gallery asset id, the quote's first words) - the photograph and the line
# over it. Order is the film's: RAAF and RAN first, the coalition, the
# opposition's classes, and the supply ship last with the logistics line.
SLIDES = [
    ("f35a_raaf", "Air superiority is not guaranteed"),
    ("e7_raaf", "It's not enough to talk about deterrence"),
    ("hobart", "Simply stated, strategic deterrence"),
    ("p8a", "Saying so, unfortunately"),
    ("mh60r", "We are not training for our best day"),
    ("ea18g", "Combat is unforgiving"),
    ("ford", "United we fought"),
    ("mogami", "Plans are worthless"),
    ("naresuan", "During deployment, it is too late"),
    ("type054a", "Victory smiles upon those who anticipate"),
    ("supply_us", "There is no strong defence"),
]
TITLE_LINES = ["SEST INTEGRATION PACK",
               "Southern Watch  ·  Southern Reach  ·  Red Line  ·  Sulu Line"]
TITLE_SUB = "Four campaigns, 57 missions, the Indo-Pacific of 2028"


def assets():
    text = (GALLERY / "catalogue.js").read_text(encoding="utf-8")
    cat = json.loads(text[text.index("{"):].rstrip().rstrip(";"))
    return {a["asset_id"]: a for a in cat["assets"]}


def quote_for(start):
    for q in quotes.QUOTES:
        if q["text"].startswith(start):
            return q
    sys.exit(f"no quote begins {start!r}")


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def cover(im, zoom):
    """The photograph filling the frame at `zoom` (1.0 = just covering),
    centred, as an RGB frame."""
    from PIL import Image
    scale = max(W / im.width, H / im.height) * zoom
    w, h = round(im.width * scale), round(im.height * scale)
    big = im.resize((w, h), Image.LANCZOS)
    x, y = (w - W) // 2, (h - H) // 2
    return big.crop((x, y, x + W, y + H))


def overlay(frame, q, credit, fonts):
    """The quotation band and the credit on one frame."""
    from PIL import Image, ImageDraw
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    lines = wrap(d, '"' + q["text"] + '"', fonts["quote"], W - 160)
    who = "- " + quotes.attribution(q)
    lh = fonts["quote"].size + 10
    box_h = 36 + lh * len(lines) + 14 + fonts["who"].size + 36
    top = H - box_h - 40
    # a gradient band, dark at the text and clear above it
    for i in range(box_h + 40):
        a = min(190, int(230 * i / 60))
        d.line([(0, top - 40 + i), (W, top - 40 + i)], fill=(8, 14, 24, a))
    y = top + 36
    for ln in lines:
        d.text((80, y), ln, font=fonts["quote"], fill=(245, 245, 240, 255))
        y += lh
    d.text((80, y + 14), who, font=fonts["who"], fill=(160, 200, 235, 255))
    d.text((W - 24 - d.textlength(credit, font=fonts["credit"]), H - 30), credit,
           font=fonts["credit"], fill=(220, 220, 220, 200))
    return Image.alpha_composite(frame.convert("RGBA"), band).convert("RGB")


def card(lines, sub, fonts, credits=()):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (W, H), (10, 20, 34))
    d = ImageDraw.Draw(im)
    # a faint horizon line, the tactical map's blue
    d.line([(80, H // 2 + 70), (W - 80, H // 2 + 70)], fill=(61, 143, 201), width=2)
    y = H // 2 - 90
    for i, ln in enumerate(lines):
        f = fonts["title"] if i == 0 else fonts["who"]
        d.text(((W - d.textlength(ln, font=f)) // 2, y), ln, font=f, fill=(245, 245, 240))
        y += f.size + 18
    if sub:
        d.text(((W - d.textlength(sub, font=fonts["credit"])) // 2, H // 2 + 90), sub,
               font=fonts["credit"], fill=(160, 200, 235))
    y = H // 2 + 120
    for ln in credits:
        d.text(((W - d.textlength(ln, font=fonts["credit"])) // 2, y), ln,
               font=fonts["credit"], fill=(190, 190, 190))
        y += fonts["credit"].size + 6
    return im


def credit_line(a):
    import re
    raw = a.get("creator") or ""
    who = re.sub(r"https?://\S+", "", raw)
    who = re.sub(r"[\u2e80-\u9fff\uac00-\ud7af\uff00-\uffef]+", "", who)
    who = re.sub(r"\(\s*talk\s*\)", "", who)
    who = re.sub(r"\s+", " ", who).strip(" ,;")
    if not who:
        who = "JMSDF (mod.go.jp)" if "mod.go.jp" in raw else "see VIDEO_CREDITS.txt"
    if len(who) > 60:
        who = who[:57].rstrip() + "..."
    return f"{a['label']}. Photo: {who} \u00b7 {a.get('license', '')}".replace("\u2014", "-")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preview", action="store_true", help="write one PNG per slide, no film")
    args = ap.parse_args()
    from PIL import Image, ImageFont
    fonts = {"quote": ImageFont.truetype(str(FONTS / "DejaVuSerif.ttf"), 30),
             "who": ImageFont.truetype(str(FONTS / "DejaVuSans.ttf"), 20),
             "credit": ImageFont.truetype(str(FONTS / "DejaVuSans.ttf"), 14),
             "title": ImageFont.truetype(str(FONTS / "DejaVuSerif-Bold.ttf"), 44)}
    cat = assets()
    OUT.mkdir(exist_ok=True)
    slides, credits = [], []
    for asset_id, start in SLIDES:
        a = cat[asset_id]
        im = Image.open(GALLERY / a["file"]).convert("RGB")
        slides.append((im, quote_for(start), credit_line(a)))
        credits.append(f"{a['label']}\n  Creator: {a.get('creator', '')}\n"
                       f"  Licence: {a.get('license', '')}\n  Source: {a.get('source_page', '')}\n"
                       f"  Changes: resized and cropped to 1280x720, slow zoom, text overlaid.\n")
    (OUT / "VIDEO_CREDITS.txt").write_text(
        "SEST BRIEFING ROOM - photo credits for sest_briefing_room.mp4\n\n"
        "Every photograph is from the SEST Gallery (Gallery/PHOTO_CREDITS.txt in the pack);\n"
        "the quotations and their sources are listed in docs/quotes.md of the repository.\n\n"
        + "\n".join(credits), encoding="utf-8")

    title = card(TITLE_LINES, TITLE_SUB, fonts)
    end = card(["Briefing ends."], "Photographs: the SEST Gallery, public domain and Creative Commons. "
               "Credits: _data/VIDEO_CREDITS.txt", fonts,
               credits=["Quotations as attributed; maxims labelled as maxims.",
                        "github.com/SEST-HOBBY/Seapower-mods"])

    if args.preview:
        title.save(OUT / "preview_00_title.png")
        for i, (im, q, cr) in enumerate(slides, 1):
            overlay(cover(im, 1.04), q, cr, fonts).save(OUT / f"preview_{i:02d}.png")
        end.save(OUT / "preview_99_end.png")
        print(f"previews in {OUT}")
        return

    target = OUT / "sest_briefing_room.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "25", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(target)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n_fade, n_slide = round(FADE * FPS), round(SLIDE * FPS)

    def emit(frame):
        proc.stdin.write(frame.tobytes())

    def fade_between(a, b):
        for i in range(1, n_fade + 1):
            emit(Image.blend(a, b, i / (n_fade + 1)))

    # the title card holds, then each slide zooms in slowly over its time
    prev = None
    for _ in range(round(TITLE * FPS)):
        emit(title)
    prev = title
    frames = 0
    for im, q, cr in slides:
        rendered = []
        for i in range(n_slide):
            zoom = 1.0 + 0.08 * i / (n_slide - 1)
            rendered.append(overlay(cover(im, zoom), q, cr, fonts))
        fade_between(prev, rendered[0])
        for fr in rendered:
            emit(fr)
        prev = rendered[-1]
        frames += n_slide + n_fade
    fade_between(prev, end)
    for _ in range(round(END * FPS)):
        emit(end)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    total = TITLE + len(slides) * (SLIDE + FADE) + FADE + END
    print(f"{target.relative_to(ROOT)}: {target.stat().st_size // 1024} KB, "
          f"{total:.0f} s, {len(slides)} slides")


if __name__ == "__main__":
    main()
