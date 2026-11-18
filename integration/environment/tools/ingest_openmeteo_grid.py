"""Real weather for a region and date from official models (via Open-Meteo) into the local cache.

    # The weather that happened over the Drake Passage on 14 Sep 2025, replayed from campaign 14 Sep 2028
    python3 integration/environment/tools/ingest_openmeteo_grid.py --source era5 --start 2025-09-14T00:00:00Z \
        --hours 72 --step 3 --bbox -66,-50,-80,-50 --res 1 --campaign-start 2028-09-14T00:00:00Z --cache out/env-cache

    # Today's ECMWF forecast, same area
    python3 integration/environment/tools/ingest_openmeteo_grid.py --source ifs --start 2026-11-18T00:00:00Z \
        --hours 72 --step 3 --bbox -66,-50,-80,-50 --res 1 --campaign-start 2028-11-18T00:00:00Z --cache out/env-cache

Requests: one weather and one wave call per 50 grid points (a 1-degree 16x30 box is 20 calls).
The free API allows 10,000 calls a day per internet address; keep grids modest. --raw-dir saves
the responses so a rebuild needs no network (--offline).
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mno_env import openmeteo  # noqa: E402
from mno_env.cache import MnoEnvDataProvider  # noqa: E402
from mno_env.grid import LatLonGrid  # noqa: E402


def utc(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", choices=("era5", "ifs"), required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--hours", type=int, default=72)
    p.add_argument("--step", type=int, default=3)
    p.add_argument("--bbox", required=True, help="lat_min,lat_max,lon_min,lon_max (lon -180..180; lon_max may exceed 180 to cross the antimeridian)")
    p.add_argument("--res", type=float, default=1.0)
    p.add_argument("--campaign-start", required=True)
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--raw-dir", type=Path)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--no-waves", action="store_true")
    a = p.parse_args(argv)
    la0, la1, lo0, lo1 = (float(x) for x in a.bbox.split(","))
    nx, ny = int(round((lo1 - lo0) / a.res)) + 1, int(round((la1 - la0) / a.res)) + 1
    if nx * ny > 2500:
        p.error(f"{nx * ny} points is too many for one run; use a coarser --res or a smaller --bbox")
    grid = LatLonGrid(lo0, la0, a.res, a.res, nx, ny)
    print(f"{nx}x{ny} points, about {2 * -(-nx * ny // openmeteo.BATCH)} requests", file=sys.stderr)
    try:
        snap = openmeteo.fetch_snapshot(a.source, grid, utc(a.start), a.hours, a.step, campaign_start=utc(a.campaign_start),
                                        waves=not a.no_waves, raw_dir=a.raw_dir, offline=a.offline)
    except openmeteo.IngestError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 2
    MnoEnvDataProvider(a.cache).add(snap)
    print(f"cached {snap['snapshot_id']} ({snap['data_class']}, fields {', '.join(snap['fields'])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
