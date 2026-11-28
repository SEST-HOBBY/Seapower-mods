#!/usr/bin/env python3
"""Build SEST's Arctic ice-edge table from NSIDC's real monthly ice edges.

    python3 tools/make_sea_ice_arctic.py --src nsidc-edges-2016-2025.zip [--check]

SRC is a ZIP (or a folder) holding NSIDC Sea Ice Index (G02135) v4.0 monthly
extent polylines for 2016-2025, one extent_N_YYYYMM_polyline_v4.0.zip per month
(120 of them), downloaded from
https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/shapefiles/shp_extent/
Each polyline is the 15 % edge of that month's mean ice cover; the coast is not
part of it.

Why: the weather branch's seaice.py turns NSIDC's hemispheric extent into a
concentration field with an edge shape "fitted by eye ... not data". Its
northern edge is a ring round the pole in autumn and puts winter pack in the
southern Barents Sea, where the 2016-2025 record has open water. This table
replaces the shape, between the Greenland Sea and the Beaufort Sea, with the
measured edge.

Method (deterministic, no third-party packages):
1. Read every polyline in its own projection (NSIDC polar stereographic north,
   Hughes 1980 ellipsoid, true scale 70N, centre meridian 45W). Meridians are
   straight rays from the pole there, so each meridian's crossings with the
   edge are exact segment intersections.
2. For each month and year, on each meridian 179.5W, 178.5W ... 179.5E, keep the
   northernmost crossing north of 66N: the edge of the pack that reaches the
   pole.
3. A meridian with no crossing is blocked: the ice reaches land first. When
   the gap is at most GAP_FILL degrees of longitude wide (an island group such
   as Franz Josef Land, Severnaya Zemlya or the New Siberian Islands), fill it
   by straight-line interpolation between the meridians either side; a wider
   gap means the ice reaches the mainland coast (COAST, i.e. ice everywhere
   north of it).
4. The month's edge on each meridian is the lower median of the ten years, then
   a triangular smoothing over SMOOTH degrees either side.

Outputs (both from the same numbers, one decimal place):
- tools/sea_ice_arctic_edge.json (read by tools/sea_ice_model.py)
- integration/beta-feature-parity/runtime/SeaIceArcticData.g.cs
With --check the outputs are built again in memory and compared.
"""
import argparse
import hashlib
import io
import json
import math
import re
import statistics
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDGE_JSON = ROOT / 'tools/sea_ice_arctic_edge.json'
DATA_CS = ROOT / 'integration/beta-feature-parity/runtime/SeaIceArcticData.g.cs'
URL = 'https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/shapefiles/shp_extent/'
CITATION = ('NSIDC Sea Ice Index, Version 4 (data set G02135), National Snow and Ice Data Center, '
            'Boulder, Colorado USA: https://nsidc.org/data/g02135/versions/4')
YEARS = range(2016, 2026)
MIN_LAT = 66.0
GAP_FILL = 30
COAST = 60.0
SMOOTH = 4

# NSIDC polar stereographic north (the files' .prj)
A = 6378273.0
F = 1 / 298.279411123064
E = math.sqrt(2 * F - F * F)
LAT_TS = math.radians(70.0)
LON0 = -45.0


def _t(phi):
    return math.tan(math.pi / 4 - phi / 2) / ((1 - E * math.sin(phi)) / (1 + E * math.sin(phi))) ** (E / 2)


MC = math.cos(LAT_TS) / math.sqrt(1 - E * E * math.sin(LAT_TS) ** 2)
TC = _t(LAT_TS)


def latitude(x, y):
    t = math.hypot(x, y) * TC / (A * MC)
    phi = math.pi / 2 - 2 * math.atan(t)
    for _ in range(12):
        phi = math.pi / 2 - 2 * math.atan(t * ((1 - E * math.sin(phi)) / (1 + E * math.sin(phi))) ** (E / 2))
    return math.degrees(phi)


def polylines(shp):
    """Every part of every PolyLine record, as projected (x, y) lists."""
    out, pos = [], 100
    while pos + 8 <= len(shp):
        _, words = struct.unpack('>2i', shp[pos:pos + 8])
        rec, pos = shp[pos + 8:pos + 8 + words * 2], pos + 8 + words * 2
        if struct.unpack('<i', rec[:4])[0] != 3:
            continue
        nparts, npoints = struct.unpack('<2i', rec[36:44])
        parts = list(struct.unpack('<%di' % nparts, rec[44:44 + 4 * nparts])) + [npoints]
        o = 44 + 4 * nparts
        pts = [struct.unpack('<2d', rec[o + 16 * i:o + 16 * i + 16]) for i in range(npoints)]
        out += [pts[a:b] for a, b in zip(parts, parts[1:])]
    return out


def crossings(lines, lon):
    th = math.radians(lon - LON0)
    dx, dy = math.sin(th), -math.cos(th)  # the meridian's ray from the pole
    lats = []
    for line in lines:
        for (x1, y1), (x2, y2) in zip(line, line[1:]):
            ex, ey = x2 - x1, y2 - y1
            den = ex * dy - ey * dx
            if den == 0:
                continue
            t, s = (dx * y1 - dy * x1) / den, (ex * y1 - ey * x1) / den
            if 0 <= t < 1 and s > 0:
                lats.append(latitude(x1 + t * ex, y1 + t * ey))
    return lats


def read_source(src):
    """{'YYYYMM': shp bytes} for every month of YEARS, from a ZIP of ZIPs or a folder."""
    found = {}

    def take(name, data):
        m = re.search(r'extent_N_(\d{6})_polyline', name)
        if not m:
            return
        if name.lower().endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(data)) as inner:
                for n in inner.namelist():
                    if n.lower().endswith('.shp'):
                        found[m.group(1)] = inner.read(n)
        elif name.lower().endswith('.shp'):
            found[m.group(1)] = data
    src = Path(src)
    if src.is_dir():
        for p in sorted(src.rglob('*')):
            if p.is_file():
                take(p.name, p.read_bytes())
    else:
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                take(n.replace('\\', '/').rsplit('/', 1)[-1], z.read(n))
    want = ['%d%02d' % (y, m) for y in YEARS for m in range(1, 13)]
    missing = [k for k in want if k not in found]
    if missing:
        raise SystemExit('%d monthly polyline files missing from %s, e.g. %s' % (len(missing), src, ', '.join(missing[:5])))
    return {k: found[k] for k in want}


def fill(row):
    """Fill gaps up to GAP_FILL meridians wide (circular); wider gaps are COAST."""
    n, out = len(row), list(row)
    known = [i for i, v in enumerate(row) if v is not None]
    if not known:
        return [COAST] * n
    for k, i in enumerate(known):
        j = known[(k + 1) % len(known)]
        gap = (j - i) % n or n
        if gap <= 1:
            continue
        for s in range(1, gap):
            out[(i + s) % n] = row[i] + (row[j] - row[i]) * s / gap if gap - 1 <= GAP_FILL else COAST
    return out


def build(src):
    shps = read_source(src)
    digest = hashlib.sha256()
    for k in sorted(shps):
        digest.update(k.encode() + hashlib.sha256(shps[k]).digest())
    lines = {k: polylines(v) for k, v in shps.items()}
    meridians = [-179.5 + i for i in range(360)]
    edges = []
    for m in range(1, 13):
        years = []
        for y in YEARS:
            row = []
            for lon in meridians:
                c = [v for v in crossings(lines['%d%02d' % (y, m)], lon) if v >= MIN_LAT]
                row.append(max(c) if c else None)
            years.append(fill(row))
        med = [statistics.median_low([yr[i] for yr in years]) for i in range(360)]
        w = [SMOOTH + 1 - abs(d) for d in range(-SMOOTH, SMOOTH + 1)]
        smooth = [sum(med[(i + d) % 360] * w[d + SMOOTH] for d in range(-SMOOTH, SMOOTH + 1)) / sum(w) for i in range(360)]
        edges.append([round(v, 1) for v in smooth])
    return {
        'note': ('Median 2016-2025 position of the Arctic pack edge (15 % monthly mean concentration) on each meridian, '
                 'from NSIDC G02135 v4.0 monthly extent polylines; built by tools/make_sea_ice_arctic.py. '
                 'Row m-1 is month m; column i is the meridian -179.5 + i degrees. SeaIceModel uses it between '
                 'the Greenland Sea and the Beaufort Sea (SeaIceModel.ArcticWeight).'),
        'source': {'dataset': 'NSIDC Sea Ice Index (G02135) v4.0, monthly extent polylines', 'url': URL,
                   'citation': CITATION, 'years': [YEARS[0], YEARS[-1]], 'files': len(shps),
                   'sha256_of_shp_files': digest.hexdigest()},
        'method': {'min_lat': MIN_LAT, 'gap_fill_deg': GAP_FILL, 'coast_edge': COAST, 'smooth_deg': SMOOTH,
                   'median': 'lower median of the ten years'},
        'edges': edges,
    }


def render_json(doc):
    return json.dumps(doc, indent=1, sort_keys=True) + '\n'


def render_cs(doc):
    s = doc['source']
    out = ['// GENERATED by tools/make_sea_ice_arctic.py from NSIDC G02135 v4.0 monthly extent polylines. Do not edit.',
           '// ' + s['citation'],
           '// %d files, %d-%d; SHA-256 over the .shp files: %s' % (s['files'], s['years'][0], s['years'][1], s['sha256_of_shp_files']),
           '// Row m-1 is month m; column i is the meridian -179.5 + i degrees: the median latitude of the',
           '// Arctic pack edge (15 % monthly mean ice) there. See SeaIceModel.ArcticEdge.',
           'namespace Sest.RuntimeFixes;',
           '',
           'internal static class SeaIceArcticData',
           '{',
           '    internal const string SourceSha256 = "%s";' % s['sha256_of_shp_files'],
           '    internal static readonly double[] Edge =',
           '    {']
    for m, row in enumerate(doc['edges'], 1):
        out.append('        // month %d' % m)
        for i in range(0, 360, 20):
            out.append('        ' + ' '.join('%.1f,' % v for v in row[i:i + 20]))
    out += ['    };', '}', '']
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--src', required=True, help='ZIP or folder of the 120 monthly extent polyline files')
    ap.add_argument('--check', action='store_true', help='build in memory and fail on any difference')
    a = ap.parse_args()
    doc = build(a.src)
    outputs = {EDGE_JSON: render_json(doc), DATA_CS: render_cs(doc)}
    if a.check:
        bad = [str(p.relative_to(ROOT)) for p, text in outputs.items() if not p.exists() or p.read_text(encoding='utf-8') != text]
        if bad:
            raise SystemExit('out of date: ' + ', '.join(bad))
        print('sea-ice Arctic edge table up to date')
        return
    for p, text in outputs.items():
        p.write_text(text, encoding='utf-8', newline='\n')
        print('wrote', p.relative_to(ROOT))


if __name__ == '__main__':
    sys.exit(main())
