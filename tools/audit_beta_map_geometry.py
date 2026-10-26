#!/usr/bin/env python3
"""Read-only mission geometry inventory for the Sea Power 26-Oct-2026 globe beta.

Old SEST source maps RelativePositionInNM X,Z to longitude/latitude arcminutes;
that is a historical authoring convention, NOT a claim about beta serialization.
This tool never converts or rewrites a mission and cannot verify in-game
play areas, terrain, actual ranges, or map projection behaviour.
"""
import argparse
import csv
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = [ROOT / 'integration/campaign/SEST_Campaign/campaigns',
                 ROOT / 'integration/mission-seeds']
KEY = re.compile(r'^\s*([^=\s]+)\s*=\s*(.*?)\s*$')
SECTION = re.compile(r'^\s*\[([^]]+)\]\s*$')
FIELDS = ('priority', 'mission', 'map_lat', 'map_lon', 'points', 'waypoints',
          'dynamic_waypoints', 'relative_sections', 'lat_max_abs',
          'longitude_span_deg', 'legacy_east_west_nm', 'globe_east_west_nm_est',
          'north_south_nm_est', 'dateline', 'geo_positions', 'play_area_field',
          'notes')


def number(value):
    try:
        if value is None:
            return None
        n = float(value.strip())
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None


def lon_normalize(lon):
    return (lon + 180.0) % 360.0 - 180.0


def longitude_span(lons):
    """Smallest circular longitude interval that includes all points."""
    if len(lons) < 2:
        return 0.0
    values = sorted(v % 360.0 for v in lons)
    gaps = [b - a for a, b in zip(values, values[1:])]
    gaps.append(values[0] + 360 - values[-1])
    return 360 - max(gaps)


def parse_sections(text):
    sections = {}
    current = ''
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', ';', '//')):
            continue
        section = SECTION.match(stripped)
        if section:
            current = section.group(1)
            sections.setdefault(current, {})
            continue
        item = KEY.match(line)
        if item:
            key, value = item.groups()
            sections.setdefault(current, {})[key.casefold()] = value.split(' //', 1)[0].strip()
    return sections


def relative_point(value, center):
    fields = value.split(',')
    if len(fields) < 3:
        return None
    x, z = number(fields[0]), number(fields[2])
    if x is None or z is None:
        return None
    lat, lon = center[0] + z / 60.0, center[1] + x / 60.0
    if not -90 <= lat <= 90:
        return None
    return lat, lon_normalize(lon)


def geo_point(value):
    fields = value.split(',')
    if len(fields) < 2:
        return None
    lat, lon = number(fields[0]), number(fields[1])
    if lat is None or lon is None or not -90 <= lat <= 90:
        return None
    return lat, lon_normalize(lon)


def analyze(path):
    sections = parse_sections(path.read_text(encoding='utf-8-sig', errors='replace'))
    env = next((v for k, v in sections.items() if k.casefold() == 'environment'), {})
    lat = number(env.get('mapcenterlatitude'))
    lon = number(env.get('mapcenterlongitude'))
    if lat is None or lon is None or not -90 <= lat <= 90:
        return None
    center = lat, lon
    points, wp_count, dyn_count, rel_count, geo_count = [], 0, 0, 0, 0
    has_play_area = any('playarea' in name.casefold() or
                        any('playarea' in key for key in keys)
                        for name, keys in sections.items())
    for name, keys in sections.items():
        # The engine can interpret a local offset relative to a parent unit;
        # treating such offsets as global coordinates would fabricate risk.
        if keys.get('positionrelativeto'):
            rel_count += 1
            continue
        if 'geoposition' in keys:
            p = geo_point(keys['geoposition'])
            if p:
                points.append(p)
                geo_count += 1
        elif 'relativepositioninnm' in keys:
            p = relative_point(keys['relativepositioninnm'], center)
            if p:
                points.append(p)
        if 'randomspawncenter' in keys:
            p = relative_point(keys['randomspawncenter'], center)
            if p:
                points.append(p)
        if 'waypoints' in keys:
            for token in keys['waypoints'].split('|'):
                p = relative_point(token, center)
                if p:
                    points.append(p)
                    wp_count += 1
                elif token.strip():
                    dyn_count += 1
    if not points:
        return None
    lats, lons = [p[0] for p in points], [p[1] for p in points]
    lat_span = max(lats) - min(lats)
    lon_span = longitude_span(lons)
    mid_lat = (max(lats) + min(lats)) / 2
    legacy_ew = lon_span * 60.0
    globe_ew = legacy_ew * abs(math.cos(math.radians(mid_lat)))
    north_south = lat_span * 60.0
    dateline = min(lons) < -170 and max(lons) > 170
    max_abs_lat = max(abs(x) for x in lats + [lat])
    # A candidate play-area edge is not derivable from this approximation:
    # editor centre, orientation, triggers, land use and nonnumeric routes matter.
    largest_est = max(globe_ew, north_south)
    priority = 'P1' if dateline or max_abs_lat >= 50 or largest_est >= 4500 else (
        'P2' if max_abs_lat >= 35 or largest_est >= 2500 else 'P3')
    notes = []
    if max_abs_lat >= 50:
        notes.append('high latitude')
    if dateline:
        notes.append('dateline')
    if largest_est >= 4500:
        notes.append('large span; review editor play area')
    if dyn_count:
        notes.append('dynamic routes not georeferenced')
    if rel_count:
        notes.append('parent-relative positions skipped')
    if not has_play_area:
        notes.append('editor auto play area unverified')
    return dict(priority=priority, mission=str(path), map_lat=round(lat, 4),
                map_lon=round(lon, 4), points=len(points), waypoints=wp_count,
                dynamic_waypoints=dyn_count, relative_sections=rel_count,
                lat_max_abs=round(max_abs_lat, 2),
                longitude_span_deg=round(lon_span, 3),
                legacy_east_west_nm=round(legacy_ew, 1),
                globe_east_west_nm_est=round(globe_ew, 1),
                north_south_nm_est=round(north_south, 1),
                dateline=dateline, geo_positions=geo_count,
                play_area_field=has_play_area, notes='; '.join(notes))


def scan(roots):
    paths = set()
    for root in roots:
        if root.is_file() and root.suffix.lower() == '.ini':
            paths.add(root)
        elif root.is_dir():
            paths.update(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() == '.ini')
    rows = []
    for path in sorted(paths):
        result = analyze(path)
        if result:
            try:
                result['mission'] = str(path.relative_to(ROOT))
            except ValueError:
                pass
            rows.append(result)
    return sorted(rows, key=lambda r: (r['priority'], -r['lat_max_abs'], r['mission']))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, action='append', dest='roots',
                        help='INI file or directory to scan; repeatable')
    parser.add_argument('--csv', action='store_true', help='CSV to standard output')
    args = parser.parse_args(argv)
    roots = args.roots or DEFAULT_ROOTS
    absent = [str(p) for p in roots if not p.exists()]
    if absent:
        parser.error('missing input: ' + ', '.join(absent))
    rows = scan(roots)
    if args.csv:
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    else:
        for r in rows:
            print(f"{r['priority']} {r['lat_max_abs']:>5.1f}deg  "
                  f"EW {r['globe_east_west_nm_est']:>7.1f} / old {r['legacy_east_west_nm']:>7.1f} nm  "
                  f"NS {r['north_south_nm_est']:>7.1f} nm  "
                  f"{r['mission']} | {r['notes']}")
        print(f'{len(rows)} authored missions; ' +
              ', '.join(f'{p}: {sum(r["priority"] == p for r in rows)}'
                        for p in ('P1', 'P2', 'P3')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
