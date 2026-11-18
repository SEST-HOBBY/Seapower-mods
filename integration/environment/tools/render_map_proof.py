"""ENV-02 static georeferenced map proof, rendered offline. VISUAL DEMO ONLY (not in game).

Writes PNGs: the georeferencing test pattern and a procedural weather/ice overlay on an
equirectangular world, and on south and north polar stereographic windows, with Natural
Earth coastlines, a 10-degree graticule, the Natural Earth 1:10m ice shelves and named check points.
The same pixel<->geography maths (mno_env/overlay.py) is what a game-side layer must
reproduce; this proves the maths and the data, not that Sea Power draws it.

Needs Pillow (already pinned for the repository's builders).

    python3 integration/environment/tools/render_map_proof.py --out docs/environment/map-proof
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from mno_env import ice, overlay, polar, procedural  # noqa: E402
from mno_env.clock import MnoEnvState, to_seconds  # noqa: E402
from mno_env.geo import PROTOTYPE_COAST, wrap_lon  # noqa: E402

POINTS = [("McMurdo Sound", -77.85, 166.67), ("Drake Passage", -58.0, -65.0), ("Strait of Hormuz", 26.57, 56.25),
          ("Weddell Sea", -70.0, -40.0), ("Antimeridian 60S", -60.0, 180.0), ("Kerguelen", -49.35, 70.22),
          ("Svalbard", 78.2, 15.6), ("Bering Strait", 65.8, -168.9)]


def font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_lines(d, view, rings, colour, width=1, wrap_jump=None):
    for ring in rings:
        prev = None
        for lon, lat in ring:
            p = view.geo_to_pixel(lat, lon)
            if prev is not None:
                jump = wrap_jump is not None and abs(p[0] - prev[0]) > wrap_jump
                if not jump:
                    d.line([prev, p], fill=colour, width=width)
            prev = p


def graticule(view, polar_view: bool):
    lines = []
    for lon in range(-180, 181, 10):
        lines.append([(lon, lat / 2) for lat in range(-180 if not polar_view else -178, 181 if not polar_view else 179)])
    for lat in range(-80, 81, 10):
        lines.append([(lon / 2, lat) for lon in range(-360, 361)])
    return lines


def render(view, layers, rings, shelves, title, path, polar_view):
    w, h = overlay.view_dims(view)
    base = Image.new("RGBA", (w, h), (18, 30, 48, 255))
    for buf in layers:
        base = Image.alpha_composite(base, Image.frombytes("RGBA", (w, h), buf))
    d = ImageDraw.Draw(base)
    jump = w / 2 if not polar_view else None
    draw_lines(d, view, graticule(view, polar_view), (120, 140, 160, 110), 1, jump)
    draw_lines(d, view, rings, (250, 214, 120, 255), 1, jump)
    for s in shelves:
        draw_lines(d, view, [list(r) for poly in s.polygons for r in poly], (255, 80, 80, 255), 1, jump)
    f = font(max(11, w // 90))
    for name, lat, lon in POINTS:
        if polar_view and (lat > -50 if view.projection.south else lat < 50):
            continue
        x, y = view.geo_to_pixel(lat, lon)
        if 0 <= x < w and 0 <= y < h:
            d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=(255, 255, 255, 255), width=2)
            d.text((x + 6, y - 6), f"{name} {lat:.2f},{lon:.2f}", fill=(255, 255, 255, 255), font=f)
    d.rectangle([0, 0, w, 22 + w // 90], fill=(0, 0, 0, 170))
    d.text((6, 4), title, fill=(255, 255, 255, 255), font=f)
    base.convert("RGB").save(path, optimize=True)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seed", default="gco-map-proof-1")
    p.add_argument("--when", default="2028-09-15T00:00:00Z")
    p.add_argument("--width", type=int, default=1440)
    p.add_argument("--polar-size", type=int, default=900)
    a = p.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    when = dt.datetime.fromisoformat(a.when.replace("Z", "+00:00"))
    snap = procedural.generate(a.seed, when - dt.timedelta(hours=12), hours=24, res_deg=2.0)
    st = MnoEnvState(snap)
    t = to_seconds(when)
    rings = json.loads(PROTOTYPE_COAST.read_text(encoding="utf-8"))["polygons"]
    shelves = ice.load_shelves()

    def sampler(name):
        return lambda lat, lon: st.sample(t, lat, lon, [name]).values[name]

    stamp = f"PROCEDURAL, NOT REAL WEATHER | seed {a.seed} | valid {a.when} | ice shelves Natural Earth 10m"
    views = {
        "world": (overlay.Equirect(a.width, a.width // 2), False),
        "south-polar-3976": (overlay.PolarWindow(polar.EPSG_3976, a.polar_size, 4_500_000.0), True),
        "north-polar-3413": (overlay.PolarWindow(polar.EPSG_3413, a.polar_size, 4_000_000.0), True),
    }
    receipt = {"snapshot_id": snap["snapshot_id"], "payload_sha256": snap["integrity"]["payload_sha256"], "files": []}
    for key, (view, pv) in views.items():
        dbg = overlay.build_layer(view, None, None)
        render(view, [dbg], rings, shelves, f"MNO ENV-02 georeferencing test pattern ({key}) - VISUAL DEMO ONLY", a.out / f"{key}-debug.png", pv)
        wx = [overlay.build_layer(view, sampler(n), n) for n in ("sea_ice_conc_pct", "wave_hs_m", "cloud_fraction_pct", "precip_rate_mm_h")]
        render(view, wx, rings, shelves, f"MNO ENV-02 overlay ({key}): ice, waves, cloud, rain | {stamp}", a.out / f"{key}-weather.png", pv)
        receipt["files"] += [f"{key}-debug.png", f"{key}-weather.png"]
    (a.out / "RECEIPT.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    print(json.dumps(receipt, indent=1))


if __name__ == "__main__":
    main()
