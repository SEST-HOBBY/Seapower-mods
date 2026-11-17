import datetime as dt
import os
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV_ROOT = HERE.parent
REPO = ENV_ROOT.parents[1]
VANILLA = REPO / "mods-source" / "_vanilla" / "original"
HORMUZ = VANILLA / "missions" / "NATO" / "Hormuz.ini"
BREAKTHROUGH = VANILLA / "missions" / "Warsaw Pact" / "Breakthrough.ini"
UTC = dt.timezone.utc
START = dt.datetime(2028, 9, 14, 6, tzinfo=UTC)

sys.path.insert(0, str(ENV_ROOT))
os.environ["MNO_ENV_LAND_MASK"] = "naturalearth"  # tests use the bundled mask, whatever is installed


@lru_cache(maxsize=4)
def procedural_snapshot(seed="test-seed", hours=72, res=4.0):
    from mno_env import procedural
    return procedural.generate(seed, START, hours=hours, res_deg=res)


def state(seed="test-seed", hours=72, res=4.0):
    from mno_env.clock import MnoEnvState
    return MnoEnvState(procedural_snapshot(seed, hours, res))


def t0():
    from mno_env.clock import to_seconds
    return to_seconds(START)
