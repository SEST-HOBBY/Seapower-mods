#!/usr/bin/env python3
"""Build SEST's own runtime plugin and run its mocked native-API regressions.

Needs mono-mcs. For an extracted local toolchain, set SEST_MONO_PREFIX to
the prefix containing usr/bin/mono and usr/lib/mono/4.5/mcs.exe. The temporary
Anchor Chain API stand-in is never shipped. No game/Unity/Harmony DLL is
required to compile. The committed output is rebuilt only on source changes.

While plugin-build.json's status is "captured-binary-source-not-recovered"
the committed DLL is a capture whose source is not in this folder (the .cs
files are its fork base), so this refuses to run unless given
--replace-captured-binary.
"""
import argparse
import os
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
STUB = HERE.parent / "menu-background/stubs/AnchorChain.cs"
SOURCES = sorted(HERE.glob("*.cs"))
TEST_SOURCES = sorted((HERE / "tests").glob("*.cs"))
FIXTURE = HERE / "tests/cost_precedence.tsv"
MANIFEST = HERE / "plugin-build.json"
CAPTURED = "captured-binary-source-not-recovered"
REPLACE_FLAG = "--replace-captured-binary"


def refuse_captured_binary():
    """Stop before the toolchain is touched if the committed DLL is a capture."""
    try:
        manifest = json.loads(MANIFEST.read_text())
    except (OSError, ValueError):
        return
    if manifest.get("status") != CAPTURED:
        return
    plugin = manifest.get("plugin", {})
    version = plugin.get("version", "?")
    base = manifest.get("fork_base", {}).get("version", "?")
    sys.exit(
        f"build_plugin.py: refusing to overwrite integration/runtime-fixes/{manifest['binary']}.\n"
        f"  It is the captured SEST Runtime {version} (sha256 {manifest['sha256']}), and its source has\n"
        f"  not been recovered. The .cs files in this folder are its {base} fork base, not its source:\n"
        f"  building them would ship a {base} DLL in place of {version}, without {version}'s native F11\n"
        f"  windows, 3-row debrief, Contacts/Group Manager pop-out bridges, preparation map and\n"
        f"  towed-sonar guard, and SEST.ContactsFix.dll (which accepts only this exact hash) would go\n"
        f"  inactive. Recover the {version} source first (integration/runtime-fixes/README.md).\n"
        f"  To replace the captured DLL anyway, run again with {REPLACE_FLAG}.")


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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(REPLACE_FLAG, action="store_true",
                        help="build even though plugin-build.json marks the committed DLL as a "
                             "captured binary whose source is not here, and replace it")
    args = parser.parse_args(argv)
    if not args.replace_captured_binary:
        refuse_captured_binary()
    else:
        print(f"build_plugin.py: {REPLACE_FLAG}: a successful build replaces the committed DLL "
              "and plugin-build.json, whatever they held", file=sys.stderr)
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
            print(run.stderr, end="", file=sys.stderr)
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
