#!/usr/bin/env python3
"""Build SEST's Antarctic ice-edge table from NSIDC's real monthly ice edges.

    python3 tools/make_sea_ice_antarctic.py --src nsidc-south-2016-2025.zip [--check]

SRC is a ZIP (or a folder) holding NSIDC Sea Ice Index (G02135) v4.0 monthly
extent polylines for 2016-2025, one extent_S_YYYYMM_polyline_v4.0.zip per month
(120 of them), downloaded from
https://noaadata.apps.nsidc.org/NOAA/G02135/south/monthly/shapefiles/shp_extent/
Each polyline is the 15 % edge of that month's mean ice cover; the coast is not
part of it.

Why: the weather branch's seaice.py draws the southern edge as a ring round
Antarctica with a hand-fitted shape (SeaIceModel.EdgeShape, south). GCO is
open to 79S since 28 Nov 2026, so the Southern Ocean routes to the coast are in
play and the ice there should be where it was measured.

Method (deterministic, no third-party packages), as make_sea_ice_arctic.py:
1. Read every polyline in its own projection (NSIDC polar stereographic south,
   Hughes 1980 ellipsoid, true scale 70S, centre meridian 0). Meridians are
   straight rays from the pole there, so each meridian's crossings with the
   edge are exact segment intersections.
2. For each month and year, on each meridian 179.5W, 178.5W ... 179.5E, keep the
   crossing furthest from the pole, between 50S and the pole: the outer edge
   of the pack round Antarctica (inner edges of polynyas and leads are inside it).
3. A meridian with no crossing either has no pack ice that month (open water
   to the coast) or meets land before the edge: the Antarctic Peninsula, whose
   tip is at 63S, blocks the rays from about 57W to 67W while the Weddell pack
   reaches it. A gap of at most GAP_FILL meridians between meridians with ice
   is therefore filled by straight-line interpolation between them; a wider
   gap is NO_ICE (80S, south of every sea GCO can reach), so SeaIceModel finds
   no sea ice there, except on the Peninsula's meridians (PENINSULA), which are
   always interpolated: a ray there that meets no edge has met the Peninsula.
4. The month's edge on each meridian is the lower median of the ten years
   (as in the Arctic table: of the middle two, the edge further from the pole),
   then a triangular smoothing over SMOOTH degrees either side, taken only
   among meridians that have ice (a meridian whose median is NO_ICE stays so).

Outputs (both from the same numbers, one decimal place, degrees South as
positive numbers):
- tools/sea_ice_antarctic_edge.json (read by tools/sea_ice_model.py)
- integration/beta-feature-parity/runtime/SeaIceAntarcticData.g.cs
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
EDGE_JSON = ROOT / 'tools/sea_ice_antarctic_edge.json'
DATA_CS = ROOT / 'integration/beta-feature-parity/runtime/SeaIceAntarcticData.g.cs'
URL = 'https://noaadata.apps.nsidc.org/NOAA/G02135/south/monthly/shapefiles/shp_extent/'
CITATION = ('NSIDC Sea Ice Index, Version 4 (data set G02135), National Snow and Ice Data Center, '
            'Boulder, Colorado USA: https://nsidc.org/data/g02135/versions/4')
YEARS = range(2016, 2026)
MAX_LAT = 50.0   # degrees South: crossings further north are not the Antarctic pack
NO_ICE = 80.0    # degrees South: no pack ice on this meridian
SMOOTH = 4
GAP_FILL = 12
PENINSULA = (-70.0, -54.0)  # meridians whose rays from the pole cross the Antarctic Peninsula

# NSIDC polar stereographic south (the files' .prj)
A = 6378273.0
F = 1 / 298.279411123064
E = math.sqrt(2 * F - F * F)
LAT_TS = math.radians(70.0)
LON0 = 0.0


def _t(phi):
    return math.tan(math.pi / 4 - phi / 2) / ((1 - E * math.sin(phi)) / (1 + E * math.sin(phi))) ** (E / 2)


MC = math.cos(LAT_TS) / math.sqrt(1 - E * E * math.sin(LAT_TS) ** 2)
TC = _t(LAT_TS)


def latitude(x, y):
    """Degrees South (positive) of a projected point."""
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
    """Degrees South of every crossing of the meridian's ray from the South Pole."""
    th = math.radians(lon - LON0)
    dx, dy = math.sin(th), math.cos(th)  # south polar stereographic: x = r sin(lon), y = r cos(lon)
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


def read_source(src, allow_missing=False):
    """{'YYYYMM': shp bytes} for every month of YEARS, from a ZIP of ZIPs or a folder."""
    found = {}

    def take(name, data):
        m = re.search(r'extent_S_(\d{6})_polyline', name)
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
    if missing and not allow_missing:
        raise SystemExit('%d monthly polyline files missing from %s, e.g. %s' % (len(missing), src, ', '.join(missing[:5])))
    return {k: found[k] for k in want if k in found}


def edge_on(lines, lon):
    c = [v for v in crossings(lines, lon) if v >= MAX_LAT]
    return min(c) if c else NO_ICE


def fill(row):
    """Fill NO_ICE gaps up to GAP_FILL meridians wide between ice, and the Peninsula's (circular)."""
    n, out = len(row), list(row)
    known = [i for i, v in enumerate(row) if v < NO_ICE]
    for k, i in enumerate(known):
        j = known[(k + 1) % len(known)]
        gap = (j - i) % n or n
        for s in range(1, gap):
            lon = -179.5 + (i + s) % n
            if gap <= GAP_FILL + 1 or PENINSULA[0] <= lon <= PENINSULA[1]:
                out[(i + s) % n] = row[i] + (row[j] - row[i]) * s / gap
    return out


def smooth(med):
    w = [SMOOTH + 1 - abs(d) for d in range(-SMOOTH, SMOOTH + 1)]
    out = []
    for i, v in enumerate(med):
        if v >= NO_ICE:
            out.append(NO_ICE)
            continue
        pairs = [(med[(i + d) % 360], w[d + SMOOTH]) for d in range(-SMOOTH, SMOOTH + 1) if med[(i + d) % 360] < NO_ICE]
        out.append(sum(a * b for a, b in pairs) / sum(b for _, b in pairs))
    return out


def build(src, allow_missing=False):
    shps = read_source(src, allow_missing)
    digest = hashlib.sha256()
    for k in sorted(shps):
        digest.update(k.encode() + hashlib.sha256(shps[k]).digest())
    lines = {k: polylines(v) for k, v in shps.items()}
    meridians = [-179.5 + i for i in range(360)]
    edges = []
    for m in range(1, 13):
        years = [fill([edge_on(lines[k], lon) for lon in meridians]) for k in ('%d%02d' % (y, m) for y in YEARS) if k in lines]
        if not years:
            edges.append(None)
            continue
        # as the Arctic table: the lower median latitude, i.e. the larger pack of the middle two
        med = [statistics.median_low([yr[i] for yr in years]) for i in range(360)]
        edges.append([round(v, 1) for v in smooth(med)])
    return {
        'note': ('Median 2016-2025 position of the Antarctic pack edge (15 %% monthly mean concentration) on each '
                 'meridian, in degrees South, from NSIDC G02135 v4.0 monthly extent polylines; built by '
                 'tools/make_sea_ice_antarctic.py. Row m-1 is month m; column i is the meridian -179.5 + i degrees. '
                 '%.1f means no pack ice on that meridian that month.' % NO_ICE),
        'source': {'dataset': 'NSIDC Sea Ice Index (G02135) v4.0, monthly extent polylines', 'url': URL,
                   'citation': CITATION, 'years': [YEARS[0], YEARS[-1]], 'files': len(shps),
                   'sha256_of_shp_files': digest.hexdigest()},
        'method': {'max_lat_south': MAX_LAT, 'gap_fill_deg': GAP_FILL, 'peninsula_lon': list(PENINSULA), 'no_ice': NO_ICE, 'smooth_deg': SMOOTH,
                   'median': 'lower median of the ten years'},
        'edges': edges,
    }


def render_json(doc):
    return json.dumps(doc, indent=1, sort_keys=True) + '\n'


def render_cs(doc):
    s = doc['source']
    out = ['// GENERATED by tools/make_sea_ice_antarctic.py from NSIDC G02135 v4.0 monthly extent polylines. Do not edit.',
           '// ' + s['citation'],
           '// %d files, %d-%d; SHA-256 over the .shp files: %s' % (s['files'], s['years'][0], s['years'][1], s['sha256_of_shp_files']),
           '// Row m-1 is month m; column i is the meridian -179.5 + i degrees: the median latitude South of the',
           '// Antarctic pack edge (15 % monthly mean ice) there; %.1f is no pack ice. See SeaIceModel.AntarcticEdge.' % NO_ICE,
           'namespace Sest.RuntimeFixes;',
           '',
           'internal static class SeaIceAntarcticData',
           '{',
           '    internal const string SourceSha256 = "%s";' % s['sha256_of_shp_files'],
           '    internal const double NoIce = %.1f;' % NO_ICE,
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
    ap.add_argument('--preview', action='store_true', help='print a summary from whatever months are present; write nothing')
    a = ap.parse_args()
    doc = build(a.src, allow_missing=a.preview)
    if a.preview:
        for m, row in enumerate(doc['edges'], 1):
            if row is None:
                print('month %2d: no files' % m)
                continue
            at = {lon: row[int(lon + 179.5)] for lon in (-179.5, -120.5, -60.5, -30.5, 0.5, 30.5, 60.5, 90.5, 120.5, 150.5)}
            print('month %2d: ' % m + ' '.join('%+.0f:%s' % (k, '-' if v >= NO_ICE else '%.1f' % v) for k, v in at.items())
                  + '  no-ice meridians %d' % sum(v >= NO_ICE for v in row))
        return
    if any(r is None for r in doc['edges']):
        raise SystemExit('a month has no files')
    outputs = {EDGE_JSON: render_json(doc), DATA_CS: render_cs(doc)}
    if a.check:
        bad = [str(p.relative_to(ROOT)) for p, text in outputs.items() if not p.exists() or p.read_text(encoding='utf-8') != text]
        if bad:
            raise SystemExit('out of date: ' + ', '.join(bad))
        print('sea-ice Antarctic edge table up to date')
        return
    for p, text in outputs.items():
        p.write_text(text, encoding='utf-8', newline='\n')
        print('wrote', p.relative_to(ROOT))


if __name__ == '__main__':
    sys.exit(main())
