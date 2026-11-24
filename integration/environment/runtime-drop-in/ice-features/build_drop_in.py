#!/usr/bin/env python3
"""Compile and run the ice-features drop-in tests with Mono (mcs + mono). No game files needed.

    python3 integration/environment/runtime-drop-in/ice-features/build_drop_in.py [--out DIR] [--check-data]

Steps:
1. (--check-data) tools/make_ice_features_data.py --check: the generated C# matches the bundled data.
2. The pure logic alone (IceFeaturesData.g.cs, IceShelfRules.cs, IcebergField.cs) as a library with
   no Unity or game reference: proves it needs neither.
3. IceFeaturesTests.exe: the pure logic, IceFeaturesBattle.cs, the golden values and the stub game
   types (tests/stubs: UnityEngine, SeaPower, and r16's Api/Policy as a shim).
4. mono IceFeaturesTests.exe; the exit code is the result.

Output goes to a temporary folder unless --out is given. Nothing is installed anywhere.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV = HERE.parents[1]
PURE = [HERE / "IceFeaturesData.g.cs", HERE / "IceShelfRules.cs", HERE / "IcebergField.cs"]
BATTLE = [HERE / "IceFeaturesBattle.cs"]
TESTS = sorted((HERE / "tests").glob("*.cs")) + sorted((HERE / "tests" / "stubs").glob("*.cs"))


def run(args, **kw):
    print("+ " + " ".join(str(a) for a in args), flush=True)
    return subprocess.run([str(a) for a in args], **kw)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--out", type=Path, help="build folder (default: a temporary folder)")
    p.add_argument("--check-data", action="store_true", help="also check the generated files are up to date")
    a = p.parse_args()
    mcs, mono = shutil.which("mcs"), shutil.which("mono")
    if not mcs or not mono:
        print("mcs and mono are needed (apt install mono-mcs mono-runtime)", file=sys.stderr)
        return 2
    if a.check_data:
        r = run([sys.executable, ENV / "tools" / "make_ice_features_data.py", "--check"])
        if r.returncode:
            return r.returncode
    tmp = None
    out = a.out
    if out is None:
        tmp = tempfile.TemporaryDirectory(prefix="ice-features-")
        out = Path(tmp.name)
    out.mkdir(parents=True, exist_ok=True)
    try:
        common = [mcs, "-nologo", "-optimize+", "-warnaserror+", "-nowarn:414", "-r:System.Core.dll"]
        r = run(common + ["-target:library", "-out:" + str(out / "IceFeaturesPure.dll")] + PURE)
        if r.returncode:
            return r.returncode
        exe = out / "IceFeaturesTests.exe"
        r = run(common + ["-target:exe", "-out:" + str(exe)] + PURE + BATTLE + TESTS)
        if r.returncode:
            return r.returncode
        r = run([mono, exe])
        return r.returncode
    finally:
        if tmp is not None:
            tmp.cleanup()


if __name__ == "__main__":
    sys.exit(main())
