"""Convert Natural Earth 1:10m Antarctic ice-shelf edge lines into data/ice-shelf-fronts-naturalearth-10m.json.

Offline: give it a file you downloaded yourself. Source (public domain):
https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_antarctic_ice_shelves_lines.geojson

What it does, and nothing more:
- rounds coordinates to 0.001 degree and drops repeated points (the same as the bundled shelf polygons);
- drops closed rings whose inside is not shelf. These are ice rises and islands inside a shelf
  (for example Roosevelt Island and Crary Ice Rise). Their edge is grounded ice, not a front;
- drops degenerate rings (fewer than four distinct points);
- tags each segment with the polygon feature it lies on, by matching its end points to the
  vertices of data/ice-shelves-naturalearth-10m.json. A segment with no match takes the tag of
  the run it sits in.

Usage: python3 tools/convert_ice_shelf_fronts.py PATH_TO_GEOJSON [--downloaded-utc 2026-11-24T20:58:00Z]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mno_env.ice import load_shelves  # noqa: E402

OUT = ROOT / "data" / "ice-shelf-fronts-naturalearth-10m.json"
POLYS = ROOT / "data" / "ice-shelves-naturalearth-10m.json"
URL = "https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_antarctic_ice_shelves_lines.geojson"


def _r(p):
    return (round(p[0], 3), round(p[1], 3))


def convert(src: Path, downloaded_utc: str) -> dict:
    raw = src.read_bytes()
    gj = json.loads(raw)
    shelves = load_shelves(POLYS)
    feats = json.loads(POLYS.read_text(encoding="utf-8"))["shelves"]
    vertex = {}
    for i, f in enumerate(feats):
        for poly in f["polygons"]:
            for x, y in poly[0]:  # outer rings only: holes are islands, not fronts
                vertex.setdefault((x, y), i)
    lines, dropped_rises, dropped_degenerate, unmatched = [], 0, 0, 0
    for feat in gj["features"]:
        g = feat["geometry"]
        parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        for part in parts:
            pts = []
            for p in part:
                q = _r(p)
                if not pts or pts[-1] != q:
                    pts.append(q)
            if len(pts) < 2:
                dropped_degenerate += 1
                continue
            if pts[0] == pts[-1]:
                if len(set(pts)) < 4:
                    dropped_degenerate += 1
                    continue
                lat = sum(p[1] for p in pts) / len(pts)
                lon = sum(p[0] for p in pts) / len(pts)
                if not any(s.contains(lat, lon) for s in shelves):
                    dropped_rises += 1
                    continue
            tags = [vertex.get(p) for p in pts]
            known = [t for t in tags if t is not None]
            if not known:
                unmatched += 1
                continue
            # fill gaps from the nearest earlier tag, then from the first known tag
            last = known[0]
            for k, t in enumerate(tags):
                if t is None:
                    tags[k] = last
                else:
                    last = t
            run, run_tag = [pts[0]], tags[0]
            for p, t in zip(pts[1:], tags[1:]):
                if t != run_tag and len(run) >= 2:
                    lines.append({"feature": run_tag, "name": feats[run_tag]["name"], "line": [list(q) for q in run]})
                    run = [run[-1]]
                run.append(p)
                run_tag = t
            if len(run) >= 2:
                lines.append({"feature": run_tag, "name": feats[run_tag]["name"], "line": [list(q) for q in run]})
    return {
        "schema": "mno.environment.ice-shelf-fronts.v1",
        "status": "PUBLISHED",
        "note": ("Natural Earth 1:10m 'Antarctic Ice Shelf Edge' lines: the seaward fronts of the shelves in "
                 "ice-shelves-naturalearth-10m.json. Coordinates rounded to 0.001 degree, repeated points dropped, "
                 "closed rings around ice rises and islands dropped. Each line is tagged with the index of the polygon "
                 "feature it lies on. Same epoch as the polygons (fronts of about 2003-2012); calving since is not shown."),
        "provider": "Natural Earth",
        "product": "ne_10m_antarctic_ice_shelves_lines",
        "product_version": "natural-earth-vector master, VERSION 5.2.0-pre",
        "source_url": URL,
        "licence": "Public domain (https://www.naturalearthdata.com/about/terms-of-use/)",
        "attribution": "Made with Natural Earth",
        "downloaded_utc": downloaded_utc,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "polygons_file": POLYS.name,
        "conversion": {"tool": "tools/convert_ice_shelf_fronts.py", "dropped_ice_rise_rings": dropped_rises,
                       "dropped_degenerate": dropped_degenerate, "unmatched_lines": unmatched},
        "coordinates": "[lon, lat] degrees WGS84",
        "fronts": lines,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src", type=Path)
    ap.add_argument("--downloaded-utc", default="unknown")
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args(argv)
    doc = convert(a.src, a.downloaded_utc)
    a.out.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{len(doc['fronts'])} front lines -> {a.out}; {doc['conversion']}")


if __name__ == "__main__":
    main()
