#!/usr/bin/env python3
"""Build SEST's own runtime plugin and run its mocked native-API regressions.

Needs mono-mcs. For an extracted local toolchain, set SEST_MONO_PREFIX to
the prefix containing usr/bin/mono and usr/lib/mono/4.5/mcs.exe. The temporary
Anchor Chain API stand-in is never shipped. No game/Unity/Harmony DLL is
required to compile. The committed output is rebuilt only on source changes.
"""
import os
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
STUB = HERE.parent / "menu-background/stubs/AnchorChain.cs"
SOURCES = sorted(HERE.glob("*.cs"))
TEST_SOURCES = sorted((HERE / "tests").glob("*.cs"))
FIXTURE = HERE / "tests/cost_precedence.tsv"


def toolchain():
    prefix = os.environ.get("SEST_MONO_PREFIX")
    env = os.environ.copy()
    if prefix:
        p = Path(prefix).resolve()
        mono = p / "usr/bin/mono"
        mcs = [str(mono), str(p / "usr/lib/mono/4.5/mcs.exe")]
        env["MONO_CFG_DIR"] = str(p / "etc")
        env["MONO_PATH"] = str(p / "usr/lib/mono/4.5")
        env["LD_LIBRARY_PATH"] = str(p / "usr/lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")
        return mcs, str(mono), env
    if not shutil.which("mcs") or not shutil.which("mono"):
        raise SystemExit("Install mono-mcs, or set SEST_MONO_PREFIX to an extracted Mono prefix")
    return ["mcs"], "mono", env


def main():
    mcs, mono, env = toolchain()

    def compile_cs(args):
        subprocess.run(mcs + ["-nologo", "-langversion:7", "-optimize+", "-warnaserror+"] + args,
                       check=True, env=env)

    with tempfile.TemporaryDirectory(prefix="sest-runtime-") as tmp:
        tmp = Path(tmp)
        stub = tmp / "AnchorChain.dll"
        compile_cs(["-target:library", f"-out:{stub}", str(STUB)])
        candidate = tmp / "SEST.RuntimeFixes.dll"
        compile_cs(["-target:library", f"-out:{candidate}", f"-r:{stub}"] + [str(s) for s in SOURCES])
        tests = tmp / "RuntimeTests.exe"
        compile_cs(["-target:exe", f"-out:{tests}", str(STUB)] + [str(s) for s in SOURCES + TEST_SOURCES])
        run = subprocess.run([mono, str(tests), str(FIXTURE)], env=env, capture_output=True, text=True)
        print(run.stdout, end="")
        if run.returncode:
            print(run.stderr, end="", file=__import__("sys").stderr)
            run.check_returncode()
        match = re.search(r"Runtime regressions passed: (\d+) assertions", run.stdout)
        if not match:
            raise SystemExit("Runtime test receipt missing")
        assertions = int(match[1])
        # Preserve the previous committed DLL if compilation or tests fail.
        (HERE / candidate.name).write_bytes(candidate.read_bytes())
    root = HERE.parents[1]
    inputs = SOURCES + [STUB, Path(__file__).resolve()] + TEST_SOURCES + [FIXTURE]
    manifest = {
        "format": 1,
        "binary": "SEST.RuntimeFixes.dll",
        "sha256": hashlib.sha256((HERE / "SEST.RuntimeFixes.dll").read_bytes()).hexdigest(),
        "inputs": {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        "validation": f"{assertions} assertions passed using mocked native APIs; no Unity gameplay claim",
    }
    (HERE / "plugin-build.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Built integration/runtime-fixes/SEST.RuntimeFixes.dll")


if __name__ == "__main__":
    main()
