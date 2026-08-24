#!/usr/bin/env python3
"""Resize the AIM-424 MALICE model and rebuild every pack that carries it.

The MALICE borrows the AGM-88G mesh, which is a full-size AARGM-ER. This sets
ResourcesMeshScale on the SEST ammunition only - the real usn_agm-88g is
untouched, because the key lives in our ini rather than in the shared model -
and scales the collider by the same factor so the hit box matches what you see.

Usage (repo root):
    python3 integration/common/set_malice_scale.py                # show current
    python3 integration/common/set_malice_scale.py --scale 0.9    # 10% smaller
    python3 integration/common/set_malice_scale.py --scale 0.8
"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMON = Path(__file__).resolve().parent / "aim424.py"

# Every pack whose builder calls write_aim424().
BUILDERS = [
    "integration/f-15ex-revamp/build_patch.py",
    "integration/f-35c-jatm/build_patch.py",
    "integration/raaf-f-35a-jatm/build_patch.py",
    "integration/growler-ngj-malice/build_patch.py",
]


def current():
    m = re.search(r"^MESH_SCALE = ([\d.]+)$", COMMON.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit("MESH_SCALE not found in aim424.py")
    return float(m.group(1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scale", type=float,
                    help="uniform mesh scale; 1.0 is the raw AGM-88G model")
    args = ap.parse_args()

    if args.scale is None:
        print(f"AIM-424 mesh scale is currently {current():g} "
              f"({(1 - current()) * 100:.0f}% smaller than the AGM-88G mesh)")
        return
    if not 0 < args.scale <= 2:
        sys.exit(f"implausible scale {args.scale} - expected roughly 0.1 to 1.5")

    text = COMMON.read_text(encoding="utf-8")
    COMMON.write_text(re.sub(r"^MESH_SCALE = [\d.]+$", f"MESH_SCALE = {args.scale:g}",
                             text, count=1, flags=re.M), encoding="utf-8")
    print(f"MESH_SCALE {current():g} -> rebuilding {len(BUILDERS)} packs")

    for b in BUILDERS:
        r = subprocess.run([sys.executable, str(ROOT / b)], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{b} failed:\n{r.stdout}{r.stderr}")
        print(f"  {Path(b).parent.name}")

    # All four copies must stay byte-identical, or whichever pack wins the load
    # order silently decides how big the missile is.
    digests = {hashlib.md5(p.read_bytes()).hexdigest()
               for p in ROOT.glob("integration/*/SEST_*/ammunition/sest_aim-424.ini")}
    if len(digests) != 1:
        sys.exit(f"copies diverged: {len(digests)} distinct versions")
    print(f"all {len(BUILDERS)} copies identical at scale {args.scale:g}")


if __name__ == "__main__":
    main()
