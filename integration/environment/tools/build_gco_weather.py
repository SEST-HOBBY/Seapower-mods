"""Fetch GCO's real weather pack (ERA5 recorded weather for the whole campaign) into a cache.

    python3 integration/environment/tools/build_gco_weather.py --cache out/gco-weather --years 1
    python3 integration/environment/tools/build_gco_weather.py --cache out/gco-weather --plan   # counts only

Resumable: run it once a day until it says COMPLETE. Exit codes: 0 complete, 3 stopped at the
API's daily limit (run again tomorrow; nothing is lost), 2 any other failure.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mno_env import gco_weather  # noqa: E402
from mno_env.ingest import IngestError  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--raw-dir", type=Path, help="default: <cache>/raw")
    p.add_argument("--years", type=int, default=1, help="campaign years of real weather (each maps to an earlier source year)")
    p.add_argument("--spec", type=Path, default=gco_weather.SPEC)
    p.add_argument("--plan", action="store_true", help="print the task list and quota estimate, fetch nothing")
    p.add_argument("--offline", action="store_true")
    a = p.parse_args(argv)
    spec = gco_weather.load_spec(a.spec)
    tasks = gco_weather.plan(spec, a.years)
    calls = sum(t.location_calls() for t in tasks)
    print(f"{len(tasks)} snapshots, {sum(t.requests() for t in tasks)} requests, about {calls} location-calls "
          f"(about {-(-calls // 9000)} day(s) of the free quota)")
    if a.plan:
        for t in tasks:
            print(f"  {t.task_id:34s} {t.layer:8s} {t.grid.nx}x{t.grid.ny} source {t.source_start:%Y-%m-%d} -> campaign {t.campaign_start:%Y-%m-%d}")
        return 0
    try:
        res = gco_weather.run(tasks, a.cache, a.raw_dir or (a.cache / "raw"), offline=a.offline)
    except IngestError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(res))
    if res["complete"]:
        print("COMPLETE")
        return 0
    print("STOPPED at the daily limit; run the same command again tomorrow.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
