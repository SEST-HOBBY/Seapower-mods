#!/usr/bin/env python3
"""Cut the SEST main-menu film from the gallery photographs.

    python3 tools/make_menu_film.py            # writes the mp4 + credits
    python3 tools/make_menu_film.py --preview  # a contact sheet instead

The photographs of the retired Briefing Room film (tools/make_briefing_video.py
SLIDES, in the same order), recut to sit behind the game's menu buttons, as
the 10 Oct 2026 media report advises for a menu background:
  - no text at all: no title card, no quotation band, no credit line - the
    menu draws its own buttons on top;
  - darkened 30% (the report's 25-40%) so the buttons stay the brightest
    thing on screen;
  - a slow drift on every shot, alternately pushing in and easing out with a
    little sideways travel, and a long cross-fade between shots;
  - a seamless loop: the last shot fades into the first, so the join is a
    cross-fade like every other;
  - no sound track;
  - 1280x720, the photographs' own width - never upscaled.

Output: integration/menu-background/sest_menu.mp4 and MENU_CREDITS.txt. The
film is committed, not rebuilt by build_all: ffmpeg's bytes differ between
versions and the regression gate wants the pack byte-identical. Encoded
H.264 High in an mp4 with the moov atom in front, the shape Unity's video
player on Windows reads (the game's own menu clip is High profile too).
"""
import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "integration" / "menu-background"
_spec = importlib.util.spec_from_file_location("briefing", ROOT / "tools" / "make_briefing_video.py")
briefing = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(briefing)

W, H, FPS = 1280, 720, 30
SHOT, FADE = 6.0, 1.5            # seconds on screen, seconds of cross-fade
DARKEN = 0.30
STEP = SHOT - FADE


def motion(i):
    """(zoom at start, zoom at end, pan at start, pan at end) for shot i:
    even shots push in drifting right, odd ones ease out drifting left."""
    if i % 2 == 0:
        return 1.02, 1.10, -0.35, 0.35
    return 1.10, 1.02, 0.35, -0.35


def shot_frame(im, i, u):
    """Shot i at u seconds into its SHOT seconds, darkened, W x H."""
    from PIL import Image, ImageEnhance
    z0, z1, p0, p1 = motion(i)
    f = max(0.0, min(1.0, u / SHOT))
    f = f * f * (3 - 2 * f)          # ease in and out
    zoom, pan = z0 + (z1 - z0) * f, p0 + (p1 - p0) * f
    w, h = im.size
    base = max(W / w, H / h)
    rw, rh = W / (base * zoom), H / (base * zoom)
    cx = w / 2 + pan * (w - rw) / 2
    cy = h / 2
    box = (cx - rw / 2, cy - rh / 2, cx + rw / 2, cy + rh / 2)
    frame = im.transform((W, H), Image.EXTENT, box, Image.BICUBIC)
    return ImageEnhance.Brightness(frame).enhance(1 - DARKEN)


def frame_at(images, t):
    """The film at t seconds: shot i, and the next shot fading in over its
    last FADE seconds; the last shot's successor is the first."""
    from PIL import Image
    n = len(images)
    i = int(t // STEP) % n
    local = t - (t // STEP) * STEP
    cur = shot_frame(images[i], i, local + FADE)
    if local < STEP - FADE:
        return cur
    j = (i + 1) % n
    u = local - (STEP - FADE)
    return Image.blend(cur, shot_frame(images[j], j, u), u / FADE)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--preview", type=Path, metavar="PNG",
                    help="write a contact sheet of the film to PNG instead")
    args = ap.parse_args()
    from PIL import Image
    cat = briefing.assets()
    shots, credits = [], []
    for asset_id, _ in briefing.SLIDES:
        a = cat[asset_id]
        shots.append(Image.open(briefing.GALLERY / a["file"]).convert("RGB"))
        credits.append(f"{a['label']}\n  Creator: {a.get('creator', '')}\n"
                       f"  Licence: {a.get('license', '')}\n  Source: {a.get('source_page', '')}\n"
                       "  Changes: cropped to 1280x720, slow zoom and pan, darkened 30%, "
                       "cross-faded into the next photograph.\n")
    length = STEP * len(shots)

    if args.preview:
        cols, tw = 4, 320
        times = [k * length / 12 for k in range(12)]
        sheet = Image.new("RGB", (cols * tw, 3 * (tw * 9 // 16)), (11, 17, 21))
        for k, t in enumerate(times):
            fr = frame_at(shots, t).resize((tw, tw * 9 // 16), Image.LANCZOS)
            sheet.paste(fr, ((k % cols) * tw, (k // cols) * (tw * 9 // 16)))
        sheet.save(args.preview)
        print(f"{args.preview}: 12 frames across {length:.0f} s")
        return

    OUT.mkdir(exist_ok=True)
    (OUT / "MENU_CREDITS.txt").write_text(
        "SEST MENU FILM - photo credits for sest_menu.mp4\n\n"
        "The film behind the main menu: eleven SEST Gallery photographs, cut with\n"
        "no text, darkened, as a loop. Every photograph is from the SEST Gallery\n"
        "(Gallery/PHOTO_CREDITS.txt in the pack). Use does not imply endorsement by the\n"
        "photographers or any armed service.\n\n" + "\n".join(credits), encoding="utf-8")
    target = OUT / "sest_menu.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-profile:v", "high",
           "-g", str(FPS * 2), "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(target)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frames = round(length * FPS)
    for k in range(frames):
        proc.stdin.write(frame_at(shots, k / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    print(f"{target.relative_to(ROOT)}: {target.stat().st_size // 1024} KB, "
          f"{length:.1f} s, {len(shots)} shots, loops seamlessly")


if __name__ == "__main__":
    main()
