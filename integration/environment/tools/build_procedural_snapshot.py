"""Write a seeded procedural snapshot into a cache folder (offline demo / fallback data).

    python3 integration/environment/tools/build_procedural_snapshot.py --seed gco-save-1 \
        --start 2028-09-14T06:00:00Z --hours 72 --res 4 --cache out/env-cache
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mno_env import procedural  # noqa: E402
from mno_env.cache import MnoEnvDataProvider  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--hours", type=int, default=72)
    p.add_argument("--res", type=float, default=4.0)
    p.add_argument("--cache", type=Path, required=True)
    a = p.parse_args(argv)
    start = dt.datetime.fromisoformat(a.start.replace("Z", "+00:00"))
    snap = procedural.generate(a.seed, start, hours=a.hours, res_deg=a.res)
    m = MnoEnvDataProvider(a.cache).add(snap)
    e = next(x for x in m["snapshots"] if x["snapshot_id"] == snap["snapshot_id"])
    print(f"{snap['snapshot_id']}: {e['bytes']} bytes, sha256 {e['sha256']}")


if __name__ == "__main__":
    main()
