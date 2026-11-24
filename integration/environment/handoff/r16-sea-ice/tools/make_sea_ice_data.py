#!/usr/bin/env python3
"""Generate SEST's battle sea-ice table from the weather branch's seaice.py.

    python3 tools/make_sea_ice_data.py [--env DIR] [--check]

DIR is the weather branch's integration/environment folder (default: the
read-only checkout /home/user/sest-env-read/integration/environment, or
$SEST_ENV_DIR). The builder imports mno_env.seaice and, for every calendar
date of a common year (2029) and of a leap year (2028), at 12:00 UTC, solves
seaice.edges_on(date) -> {north, south, sh_summer} (baseline 2016_2025, the
weather branch's default). Those 731 rows are the only data the battle model
needs: the edge SHAPE (seaice.edge_shape) and the logistic (seaice.concentration)
are ported line for line to runtime/SeaIceModel.cs and to tools/sea_ice_model.py.

Marginal seas (weather branch change B1, docs/environment/SEA-ICE-MARGINAL-SEAS.md):
seaice.edges_on now also returns edges["marginal"] = {okhotsk, bering, chukchi},
the regional edges of the Sea of Okhotsk, the Bering Sea and the Chukchi Sea, each
solved against the NSIDC G02135 regional monthly extent. Those three numbers per
date go into SeaIceData.CommonMarginal / LeapMarginal (stride 3: Okhotsk, Bering,
Chukchi) so the
3-number rows (Common / Leap) keep their layout. The sea masks
(seaice._MARGINAL_ROWS) and constants are generated too; seaice.ice_order is
ported by hand to SeaIceModel.IceOrder.

The rows are indexed by (leap year?, month, day), never by day of year, so a
date after 28 February is never shifted by a day; and they are the noon value
of that date (no interpolation), because edges_on rounds its extent target to
0.05 million km2 and sh_summer to 0.05, so the weather branch's edges are step
functions of time (adversarial review C-ice, wrong claim 7).

Solving the 731 rows takes about 5 minutes on 4 cores; a rerun reuses the rows
in tools/sea_ice_edges.json when the source hashes are unchanged (--full forces
the solve). ice-capability.json's units go in too, through ice.load_capabilities,
which refuses an entry without a source.

Outputs (deterministic; --check solves everything again and fails on any difference):
- tools/sea_ice_edges.json: the rows, the source hashes, the units and the review points.
- integration/beta-feature-parity/runtime/SeaIceData.g.cs: the same rows as C#.
- integration/beta-feature-parity/tests/SeaIceGolden.g.cs: golden points
  (utc noon date, lat, lon, seaice.ice_at percent) for the managed test.

The NSIDC file holds monthly hemispheric extents only; the regional edge shape
in seaice.py is fitted by eye (its own docstring says "not data"). This table
inherits both facts: it is a seasonal climatology for game rules, not a chart.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV = Path(os.environ.get('SEST_ENV_DIR', '/home/user/sest-env-read/integration/environment'))
EDGES_JSON = ROOT / 'tools/sea_ice_edges.json'
DATA_CS = ROOT / 'integration/beta-feature-parity/runtime/SeaIceData.g.cs'
GOLDEN_CS = ROOT / 'integration/beta-feature-parity/tests/SeaIceGolden.g.cs'
BASELINE = '2016_2025'
YEARS = (2029, 2028)  # common year first, then leap year
SOURCES = ('mno_env/seaice.py', 'mno_env/geo.py', 'mno_env/ice.py',
           'data/seaice-climatology-nsidc-g02135.json', 'data/ice-shelves-naturalearth-10m.json',
           'data/ice-capability.json')
GOLDEN_DATES = [(2029, m, 15) for m in range(1, 13)] + [(2029, 3, 10), (2029, 1, 12), (2028, 2, 29), (2028, 3, 10), (2028, 9, 20)]
GOLDEN_LATS = [-85, -80, -77.5, -75, -72.5, -70, -68, -66, -64, -62, -60, -58, -55, -50, -45, -40.5, -39,
               39, 40.5, 45, 50, 55, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80, 82.5, 85, 89]
GOLDEN_LONS = [-180, -175, -168, -160, -100, -63, -55, -42, -25, 8, 22, 36, 120.5, 138, 141, 143.6, 147, 152, 162.5]
MARGINAL = ('okhotsk', 'bering', 'chukchi')  # order of the per-date marginal edges (CommonMarginal / LeapMarginal)
# The adversarial review's own points (it ran seaice.py): 10 March 36E 72N 18.7 %, 74N 62.3 %.
REVIEW_POINTS = [((2029, 3, 10), 72.0, 36.0), ((2029, 3, 10), 74.0, 36.0), ((2029, 3, 10), 75.0, 36.0),
                 ((2029, 3, 10), 76.8, 36.0), ((2029, 3, 10), 67.0, 6.0), ((2029, 1, 12), -68.0, -42.0),
                 ((2029, 1, 12), -62.8, -58.5)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _import(env):
    sys.path.insert(0, str(env))
    from mno_env import seaice  # noqa: E402
    return seaice


def _rows(args):
    env, year, dates = args
    seaice = _import(env)
    out = []
    for (m, d) in dates:
        e = seaice.edges_on(dt.datetime(year, m, d, 12, tzinfo=dt.timezone.utc), BASELINE)
        out.append([m, d, e['north'], e['south'], e['sh_summer']] + [e['marginal'][n] for n in MARGINAL])
    return out


def build(env, full=True):
    env = Path(env)
    missing = [s for s in SOURCES if not (env / s).exists()]
    if missing:
        raise SystemExit('weather branch sources missing under ' + str(env) + ': ' + ', '.join(missing))
    sources = {s: sha(env / s) for s in SOURCES}
    previous = json.loads(EDGES_JSON.read_text(encoding='utf-8')) if EDGES_JSON.exists() else None
    if not full and previous and previous.get('sources') == sources and previous.get('baseline') == BASELINE:
        tables = {str(YEARS[0]): [r + m for r, m in zip(previous['common'], previous['common_marginal'])],
                  str(YEARS[1]): [r + m for r, m in zip(previous['leap'], previous['leap_marginal'])]}
        print('edge rows reused from tools/sea_ice_edges.json (same source hashes); --full solves them again')
        return finish(env, sources, tables)
    jobs = []
    for year in YEARS:
        day, dates = dt.date(year, 1, 1), []
        while day.year == year:
            dates.append((day.month, day.day))
            day += dt.timedelta(days=1)
        # four contiguous blocks per year keep each worker's lru_cache warm
        q = (len(dates) + 3) // 4
        jobs += [(str(env), year, dates[i:i + q]) for i in range(0, len(dates), q)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(_rows, jobs))
    tables = {str(y): [] for y in YEARS}
    for (env_s, year, _), rows in zip(jobs, results):
        tables[str(year)] += rows
    return finish(env, sources, tables)


def finish(env, sources, tables):
    seaice = _import(env)
    from mno_env import ice  # noqa: E402
    capabilities = ice.load_capabilities()  # raises on an entry without a source or with an unknown class
    golden = []
    edges_cache = {}

    def edges(y, m, d):
        rows = tables[str(y)]
        for r in rows:
            if r[0] == m and r[1] == d:
                return {'north': r[2], 'south': r[3], 'sh_summer': r[4], 'marginal': dict(zip(MARGINAL, r[5:5 + len(MARGINAL)]))}
        raise KeyError((y, m, d))
    for (y, m, d) in GOLDEN_DATES:
        e = edges_cache.setdefault((y, m, d), edges(y, m, d))
        for lat in GOLDEN_LATS:
            for lon in GOLDEN_LONS:
                golden.append([y, m, d, lat, lon, seaice.ice_at(lat, lon, e)])
    review = []
    for (y, m, d), lat, lon in REVIEW_POINTS:
        review.append([y, m, d, lat, lon, seaice.ice_at(lat, lon, edges(y, m, d))])
    return {
        'format': 'sest-sea-ice-edges/1',
        'baseline': BASELINE,
        'note': 'seaice.edges_on(date 12:00 UTC) per calendar date; common year = 2029, leap year = 2028. '
                'Monthly hemispheric NSIDC extents with a regional edge shape fitted by eye (seaice.py); game rules, not a chart.',
        'sources': sources,
        'units': {k: capabilities[k] for k in sorted(capabilities)},
        'common': [r[:5] for r in tables[str(YEARS[0])]],
        'leap': [r[:5] for r in tables[str(YEARS[1])]],
        'common_marginal': [r[5:5 + len(MARGINAL)] for r in tables[str(YEARS[0])]],
        'leap_marginal': [r[5:5 + len(MARGINAL)] for r in tables[str(YEARS[1])]],
        'marginal': {'seas': list(MARGINAL),
                     'rows': {n: [[j, a, b] for j, spans in sorted(seaice.MARGINAL_SEAS[n]['rows'].items()) for a, b in spans]
                              for n in MARGINAL},
                     'no_ice': seaice.MARGINAL_NO_ICE, 'width': seaice.MARGINAL_WIDTH, 'max': seaice.MARGINAL_MAX},
        'review_points': review,
    }, golden


def r(x):
    return repr(float(x))


def data_cs(doc):
    lines = ['// GENERATED by tools/make_sea_ice_data.py from the weather branch\'s seaice.py. Do not edit.',
             '// Source SHA-256:']
    lines += ['//   ' + k + ' ' + v for k, v in sorted(doc['sources'].items())]
    lines += ['// Rows: seaice.edges_on(date at 12:00 UTC, baseline ' + doc['baseline'] + ') for each calendar date;',
              '// [north base edge, south base edge, sh_summer]. Common year (365 rows) then leap year (366 rows).',
              'namespace Sest.RuntimeFixes;', '',
              'internal static class SeaIceData', '{',
              '    internal const string Baseline = "' + doc['baseline'] + '";',
              '    internal const string SourceSeaIcePy = "' + doc['sources']['mno_env/seaice.py'] + '";',
              '    internal const string SourceClimatology = "' + doc['sources']['data/seaice-climatology-nsidc-g02135.json'] + '";',
              '    // ice-capability.json "units" is empty on purpose: no unit has a sourced ice class, so every ship is "none".',
              '    internal const string SourceCapability = "' + doc['sources']['data/ice-capability.json'] + '";']
    lines.append('    // ice-capability.json units: ini name, capability, source ("sourced": load_capabilities refused any without one).')
    lines.append('    internal static readonly string[] Units =')
    lines.append('    {')
    for k, v in doc['units'].items():
        lines.append('        ' + json.dumps(k) + ', ' + json.dumps(v) + ', "sourced",')
    lines.append('    };')
    for name, rows in (('Common', doc['common']), ('Leap', doc['leap'])):
        lines.append('    internal static readonly double[] ' + name + ' =')
        lines.append('    {')
        for row in rows:
            lines.append('        ' + r(row[2]) + ', ' + r(row[3]) + ', ' + r(row[4]) + ', // ' + '%02d-%02d' % (row[0], row[1]))
        lines.append('    };')
    mg = doc['marginal']
    lines.append('    // Marginal seas (seaice.MARGINAL_SEAS): per-date regional edges, stride ' + str(len(mg['seas'])) + ' (' + ', '.join(mg['seas']) + ');')
    lines.append('    // ' + r(mg['no_ice']) + ' = ice-free on that date. Masks: (row = floor(lat), first floor(lon), last floor(lon)).')
    lines.append('    internal const double MarginalNoIce = ' + r(mg['no_ice']) + ';')
    lines.append('    internal const double MarginalWidth = ' + r(mg['width']) + ';')
    lines.append('    internal const double MarginalMax = ' + r(mg['max']) + ';')
    for i, n in enumerate(mg['seas']):
        lines.append('    internal static readonly int[] MarginalRows' + n.capitalize() + ' =')
        lines.append('    {')
        for j, a, b in mg['rows'][n]:
            lines.append('        %d, %d, %d,' % (j, a, b))
        lines.append('    };')
    for name, key in (('CommonMarginal', 'common_marginal'), ('LeapMarginal', 'leap_marginal')):
        lines.append('    internal static readonly double[] ' + name + ' =')
        lines.append('    {')
        rows = doc['common' if key == 'common_marginal' else 'leap']
        for row, mrow in zip(rows, doc[key]):
            lines.append('        ' + ', '.join(r(v) for v in mrow) + ', // ' + '%02d-%02d' % (row[0], row[1]))
        lines.append('    };')
    lines.append('}')
    return '\n'.join(lines) + '\n'


def golden_cs(doc, golden):
    lines = ['// GENERATED by tools/make_sea_ice_data.py: seaice.ice_at(lat, lon, edges_on(date 12:00 UTC)). Do not edit.',
             'static class SeaIceGolden', '{',
             '    // year, month, day, lat, lon, percent']
    for name, rows in (('Points', golden), ('Review', doc['review_points'])):
        lines.append('    internal static readonly double[] ' + name + ' =')
        lines.append('    {')
        for row in rows:
            lines.append('        ' + ', '.join(str(int(v)) for v in row[:3]) + ', ' + ', '.join(r(v) for v in row[3:]) + ',')
        lines.append('    };')
    lines.append('}')
    return '\n'.join(lines) + '\n'


def render(built):
    doc, golden = built
    return {EDGES_JSON: json.dumps(doc, indent=0, sort_keys=True) + '\n', DATA_CS: data_cs(doc), GOLDEN_CS: golden_cs(doc, golden)}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--env', type=Path, default=DEFAULT_ENV)
    p.add_argument('--check', action='store_true', help='solve everything again in memory and compare with the committed files')
    p.add_argument('--full', action='store_true', help='solve the edge rows again even when the source hashes are unchanged')
    a = p.parse_args()
    out = render(build(a.env, full=a.full or a.check))
    if a.check:
        bad = [str(k.relative_to(ROOT)) for k, v in out.items() if not k.exists() or k.read_text(encoding='utf-8') != v]
        if bad:
            raise SystemExit('stale generated sea-ice files: ' + ', '.join(bad))
        print('sea-ice generated files match the weather branch sources')
        return
    for k, v in out.items():
        k.write_bytes(v.encode('utf-8'))
        print('wrote', k.relative_to(ROOT))


if __name__ == '__main__':
    main()
