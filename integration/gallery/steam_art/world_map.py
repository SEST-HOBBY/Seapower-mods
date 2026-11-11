#!/usr/bin/env python3
"""Draw the world campaign's chart for its Steam card: world-map.png.

The four authored campaigns' cards inset the campaign screen's backdrop.
Global Maritime Operations 2028 runs in Dynamic Campaign Mod, whose map is
drawn by the plugin in game, so its card insets this chart instead: every
base and patrol route in the campaign file, by coalition, over a 1 km land
mask (global-land-mask), in the Steam cards' palette. 1920x1080 like the
backdrops, so render.js downscales it the same way.

    pip install global-land-mask numpy pillow
    python3 integration/gallery/steam_art/world_map.py

The counts printed on it are read from the campaign file, not typed.
"""
import json
from pathlib import Path

import numpy as np
from global_land_mask import globe
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CAMPAIGN = (ROOT / "integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns"
            / "sest-world-regions-2028/campaign.json")
OUT = HERE / "world-map.png"

W, H = 1920, 1080
SEA, LAND, GRID = (14, 22, 31), (44, 54, 66), (26, 36, 48)
SIDE = {"blue": (74, 154, 216), "red": (224, 96, 79)}
TEXT, DIM = (232, 237, 243), (150, 160, 172)
FONTS = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def main():
    c = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    b = c["bounds"]
    lon0, lon1, lat0, lat1 = b["lonMin"], b["lonMax"], b["latMin"], b["latMax"]
    scale = W / (lon1 - lon0)                     # px per degree, both axes
    top = 40                                      # chart band; title below it
    ch = round((lat1 - lat0) * scale)

    def xy(lat, lon):
        lon = lon if lon >= lon0 else lon + 360
        return (lon - lon0) * scale, top + (lat1 - lat) * scale

    # Land: sample the mask at every pixel centre of the chart band.
    xs = lon0 + (np.arange(W) + 0.5) / scale
    ys = lat1 - (np.arange(ch) + 0.5) / scale
    lon_g, lat_g = np.meshgrid(((xs + 180) % 360) - 180, ys)
    land = globe.is_land(lat_g, lon_g)
    rgb = np.empty((ch, W, 3), np.uint8)
    rgb[:] = SEA
    rgb[land] = LAND
    img = Image.new("RGB", (W, H), SEA)
    img.paste(Image.fromarray(rgb), (0, top))
    d = ImageDraw.Draw(img, "RGBA")

    for lat in range(-60, 75, 30):                # graticule under the data
        y = xy(lat, lon0)[1]
        d.line([(0, y), (W, y)], fill=GRID + (255,), width=1)
    for lon in range(-90, 260, 30):
        x = xy(0, lon)[0]
        d.line([(x, top), (x, top + ch)], fill=GRID + (255,), width=1)

    side_of = {f["name"]: f["side"] for f in c["forces"]}
    for p in c["patrols"]:
        pts = [xy(lat, lon) for lat, lon in p["points"]]
        col = SIDE.get(side_of.get(p["force"]), DIM)
        d.line(pts + pts[:1], fill=col + (190,), width=4)

    for base in sorted(c["bases"], key=lambda x: x["side"] == "blue"):
        x, y = xy(base["lat"], base["lon"])
        col = SIDE[base["side"]]
        r = 11 if base["kind"] == "AirBase" else 10
        if base["kind"] == "AirBase":
            d.ellipse([x - r, y - r, x + r, y + r], fill=col + (235,), outline=(8, 10, 15, 255), width=2)
        else:
            d.rectangle([x - r, y - r, x + r, y + r], fill=col + (235,), outline=(8, 10, 15, 255), width=2)

    # Title band, like the authored campaigns' backdrops.
    by = top + ch + 30
    d.text((48, by), "GLOBAL MARITIME OPERATIONS", font=font("DejaVuSans-Bold.ttf", 62), fill=TEXT)
    sides = {s["id"]: s for s in c["sides"]}
    n = {k: sum(1 for x in c["bases"] if x["side"] == k) for k in SIDE}
    line = (f"2028  ·  {len(c['bases'])} BASES  ·  {len(c['forces'])} FORCE GROUPS  ·  "
            f"{len(c['patrols'])} PATROLS")
    d.text((50, by + 88), line, font=font("DejaVuSansMono.ttf", 32), fill=DIM)
    lx = W - 620
    for i, k in enumerate(("blue", "red")):
        y = by + 18 + i * 56
        d.ellipse([lx, y, lx + 26, y + 26], fill=SIDE[k])  # legend dot
        d.text((lx + 44, y - 4), f"{sides[k]['name']} ({n[k]})",
               font=font("DejaVuSans.ttf", 28), fill=TEXT)
    img.save(OUT, optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(c['bases'])} bases, "
          f"{len(c['patrols'])} patrols")


if __name__ == "__main__":
    main()
