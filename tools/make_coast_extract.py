#!/usr/bin/env python3
"""Cut a coastline extract for one theatre out of Natural Earth, for the
campaign builder's geography check.

The Southern Watch builder proves a ship is on water by snapping it to a point
some already-loading mission put a ship on. South of Bass Strait there are no
such points - nothing in this repo has ever sailed Storm Bay, Cook Strait or
the Macquarie Ridge - so a campaign set there needs a different proof, and the
honest one is the coastline itself: Natural Earth 1:10m land and minor
islands, public domain, the same data the briefing maps are drawn from.

This writes integration/campaign/geo/<name>.json: every land polygon that
touches the theatre box, clipped to the box (Sutherland-Hodgman, so the
Antarctic and Australian rings shrink to the part that matters), lightly
simplified (Douglas-Peucker, tolerance in degrees), outer rings only. Lakes
are holes and no ship is placed in one. The extract is committed, so the
build is deterministic and offline; this script is how it was made and how
it would be remade.

    python3 tools/make_coast_extract.py            # the southern theatre
    python3 tools/make_coast_extract.py --box W S E N --name other --tol 0.006
"""
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
import briefing_maps  # noqa: E402  (the Natural Earth fetch/cache lives there)

OUT_DIR = ROOT / "integration" / "campaign" / "geo"


def clip(ring, box):
    """Sutherland-Hodgman: the part of a closed ring inside box (w, s, e, n)."""
    w, s, e, n = box

    def inside(p, edge):
        x, y = p
        return {"w": x >= w, "e": x <= e, "s": y >= s, "n": y <= n}[edge]

    def intersect(a, b, edge):
        (x1, y1), (x2, y2) = a, b
        if edge in ("w", "e"):
            xe = w if edge == "w" else e
            t = (xe - x1) / (x2 - x1) if x2 != x1 else 0.0
            return (xe, y1 + t * (y2 - y1))
        ye = s if edge == "s" else n
        t = (ye - y1) / (y2 - y1) if y2 != y1 else 0.0
        return (x1 + t * (x2 - x1), ye)

    out = [tuple(p[:2]) for p in ring]
    for edge in ("w", "e", "s", "n"):
        if not out:
            break
        src, out = out, []
        prev = src[-1]
        for cur in src:
            if inside(cur, edge):
                if not inside(prev, edge):
                    out.append(intersect(prev, cur, edge))
                out.append(cur)
            elif inside(prev, edge):
                out.append(intersect(prev, cur, edge))
            prev = cur
    return out


def simplify(pts, tol):
    """Douglas-Peucker on a closed ring; keeps at least a triangle."""
    if len(pts) < 5 or tol <= 0:
        return pts

    def dp(seg):
        if len(seg) < 3:
            return seg
        (x1, y1), (x2, y2) = seg[0], seg[-1]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1e-12
        best, at = 0.0, 0
        for i, (x, y) in enumerate(seg[1:-1], 1):
            d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / length
            if d > best:
                best, at = d, i
        if best > tol:
            return dp(seg[:at + 1])[:-1] + dp(seg[at:])
        return [seg[0], seg[-1]]

    out = dp(pts)
    return out if len(out) >= 4 else pts


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--box", nargs=4, type=float, metavar=("W", "S", "E", "N"),
                    default=[100.0, -72.0, 180.0, -25.0])
    ap.add_argument("--name", default="southern_theatre_coast")
    ap.add_argument("--tol", type=float, default=0.006,
                    help="simplification tolerance in degrees (0.006 is ~0.35 NM)")
    args = ap.parse_args()
    box = tuple(args.box)
    geo = briefing_maps.layers(fetch=True)
    rings, source = [], []
    for layer in ("ne_10m_land", "ne_10m_minor_islands"):
        count = 0
        for feat in geo[layer]["features"]:
            g = feat["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                outer = poly[0]
                xs = [p[0] for p in outer]
                ys = [p[1] for p in outer]
                if max(xs) < box[0] or min(xs) > box[2] or max(ys) < box[1] or min(ys) > box[3]:
                    continue
                cut = clip(outer, box)
                if len(cut) < 4:
                    continue
                cut = simplify(cut, args.tol)
                if cut[0] != cut[-1]:
                    cut.append(cut[0])
                rings.append([[round(x, 4), round(y, 4)] for x, y in cut])
                count += 1
        source.append(f"{layer}: {count} rings")
    data = dict(
        source="Natural Earth 1:10m land + minor islands (public domain), "
               "github.com/nvkelso/natural-earth-vector",
        box=list(box), tolerance_deg=args.tol,
        note="Outer rings clipped to the box and simplified; holes (lakes) dropped. "
             "Made by tools/make_coast_extract.py.",
        layers=source, rings=rings)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{args.name}.json"
    out.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
    pts = sum(len(r) for r in rings)
    print(f"wrote {out.relative_to(ROOT)}: {len(rings)} rings, {pts} points, "
          f"{out.stat().st_size // 1024} KB, box {box}")


if __name__ == "__main__":
    main()
