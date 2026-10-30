#!/usr/bin/env python3
"""Build SEST's own runtime plugin and run its mocked native-API regressions.

Needs mono-mcs. For an extracted local toolchain, set SEST_MONO_PREFIX to
the prefix containing usr/bin/mono and usr/lib/mono/4.5/mcs.exe. The temporary
Anchor Chain API stand-in is never shipped. No game/Unity/Harmony DLL is
required to compile the fork base. The committed output is rebuilt only on
source changes.

While plugin-build.json's status is "captured-binary-source-not-recovered"
the committed DLL is a capture whose source is not in this folder (the .cs
files are its fork base), so this refuses to run unless given
--replace-captured-binary. It refuses too, failing closed, when a committed
DLL is there but plugin-build.json cannot be read or does not record that
DLL's hash: then nothing says what the DLL is.

A scratch build leaves the committed DLL and plugin-build.json alone:
--output PATH writes the DLL elsewhere, --source DIR compiles another
folder's .cs files (such as source-1.5.0/, with DIR/tests/ as its mocked
regressions when that folder exists) and --reference DLL adds an assembly to
compile against that is not committed, such as the game's Seapower-Scripts.dll
or BepInEx's 0Harmony.dll. Each DIR/stubs/<Assembly>.cs is a committed
compile-time stand-in for the game assembly of that name: it is compiled to
<Assembly>.dll in the temporary folder, referenced, and never shipped, like
the Anchor Chain stand-in. Replacing nothing, a scratch build needs no
--replace-captured-binary; --source without --output is refused, so
another folder's sources never become the committed DLL by accident.
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
MANIFEST = HERE / "plugin-build.json"
CAPTURED = "captured-binary-source-not-recovered"
REPLACE_FLAG = "--replace-captured-binary"


def refuse_captured_binary():
    """Stop before the toolchain is touched if the committed DLL may be a capture.

    Fails closed: a committed DLL that plugin-build.json does not account for
    (unreadable, not a JSON object, or another sha256) is treated as one, and
    a captured status refuses even when the DLL itself has gone missing.
    """
    dll = HERE / "SEST.RuntimeFixes.dll"
    where = f"integration/runtime-fixes/{dll.name}"
    actual = hashlib.sha256(dll.read_bytes()).hexdigest() if dll.is_file() else None
    try:
        manifest = json.loads(MANIFEST.read_text())
        if not isinstance(manifest, dict):
            raise ValueError("not a JSON object")
    except (OSError, ValueError) as error:
        if actual is None:
            return
        sys.exit(
            f"build_plugin.py: refusing to overwrite {where} (sha256 {actual}).\n"
            f"  integration/runtime-fixes/plugin-build.json cannot be read ({error}), so nothing says\n"
            f"  whether that DLL is the captured SEST Runtime 1.5.0, whose source is not here. Restore\n"
            f"  plugin-build.json from git first (integration/runtime-fixes/README.md).\n"
            f"  To replace the DLL anyway, run again with {REPLACE_FLAG}.")
    if manifest.get("status") != CAPTURED:
        if actual is None or manifest.get("sha256") == actual:
            return
        sys.exit(
            f"build_plugin.py: refusing to overwrite {where} (sha256 {actual}).\n"
            f"  plugin-build.json records sha256 {manifest.get('sha256')} for it, so it is not the DLL\n"
            f"  this builder last wrote: it may be the captured SEST Runtime 1.5.0, whose source is not\n"
            f"  here. Put back the matching plugin-build.json, or the DLL, from git first\n"
            f"  (integration/runtime-fixes/README.md).\n"
            f"  To replace the DLL anyway, run again with {REPLACE_FLAG}.")
    plugin = manifest.get("plugin", {})
    version = plugin.get("version", "?")
    base = manifest.get("fork_base", {}).get("version", "?")
    missing = "" if actual else f"  ({dll.name} itself is missing: restore it from git.)\n"
    sys.exit(
        f"build_plugin.py: refusing to overwrite {where}.\n"
        f"  It is the captured SEST Runtime {version} (sha256 {manifest.get('sha256')}), and its source has\n"
        f"  not been recovered. The .cs files in this folder are its {base} fork base, not its source:\n"
        f"  building them would ship a {base} DLL in place of {version}, without {version}'s native F11\n"
        f"  windows, 3-row debrief, Contacts/Group Manager pop-out bridges, preparation map and\n"
        f"  towed-sonar guard, and SEST.ContactsFix.dll (which accepts only this exact hash) would go\n"
        f"  inactive. Recover the {version} source first (integration/runtime-fixes/README.md).\n"
        f"{missing}"
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
    parser.add_argument("--source", metavar="DIR",
                        help="compile DIR's *.cs files instead of this folder's; DIR/tests/*.cs and "
                             "DIR/tests/cost_precedence.tsv are its mocked regressions when DIR/tests "
                             "exists, otherwise none run. Needs --output")
    parser.add_argument("--output", metavar="PATH",
                        help="write the DLL to PATH instead of over the committed one and leave "
                             "plugin-build.json alone (a scratch build); PATH must not be the committed DLL")
    parser.add_argument("--reference", metavar="DLL", action="append", default=[],
                        help="an assembly to compile against that is not committed (repeatable), "
                             "such as the game's Seapower-Scripts.dll; never shipped")
    args = parser.parse_args(argv)
    shipped = HERE / "SEST.RuntimeFixes.dll"
    output = Path(args.output).resolve() if args.output else None
    if output is not None and output == shipped.resolve():
        parser.error("--output names the committed DLL; drop --output to build in place")
    if args.source and output is None:
        parser.error("--source needs --output: another folder's sources never replace the committed DLL")
    scratch = output is not None
    if scratch:
        pass  # nothing committed is written, so there is nothing to refuse
    elif not args.replace_captured_binary:
        refuse_captured_binary()
    else:
        print(f"build_plugin.py: {REPLACE_FLAG}: a successful build replaces the committed DLL "
              "and plugin-build.json, whatever they held", file=sys.stderr)
    source = Path(args.source).resolve() if args.source else HERE
    sources = sorted(source.glob("*.cs"))
    if not sources:
        raise SystemExit(f"build_plugin.py: no .cs files in {source}")
    test_sources = sorted((source / "tests").glob("*.cs"))
    fixture = source / "tests/cost_precedence.tsv"
    stub_sources = sorted((source / "stubs").glob("*.cs"))
    references = [Path(r).resolve() for r in args.reference]
    for reference in references:
        if not reference.is_file():
            raise SystemExit(f"build_plugin.py: --reference {reference}: no such file")
    mcs, mono, env = toolchain()

    def compile_cs(args):
        subprocess.run(mcs + ["-nologo", "-langversion:7.2", "-optimize+", "-warnaserror+"] + args,
                       check=True, env=env)

    with tempfile.TemporaryDirectory(prefix="sest-runtime-") as tmp:
        tmp = Path(tmp)
        stub = tmp / "AnchorChain.dll"
        compile_cs(["-target:library", f"-out:{stub}", str(STUB)])
        stand_ins = []
        for stub_source in stub_sources:  # DIR/stubs/<Assembly>.cs -> tmp/<Assembly>.dll
            stand_in = tmp / (stub_source.stem + ".dll")
            compile_cs(["-target:library", f"-out:{stand_in}", str(stub_source)])
            stand_ins.append(stand_in)
        extra = [f"-r:{r}" for r in stand_ins + references]
        candidate = tmp / "SEST.RuntimeFixes.dll"
        compile_cs(["-target:library", f"-out:{candidate}", f"-r:{stub}"] + extra + [str(s) for s in sources])
        assertions = None
        if test_sources:
            for reference in references:  # so the test runner can load a stand-in it touches
                shutil.copy2(reference, tmp / reference.name)
            tests = tmp / "RuntimeTests.exe"
            compile_cs(["-target:exe", f"-out:{tests}", str(STUB)] + extra
                       + [str(s) for s in sources + test_sources])
            run = subprocess.run([mono, str(tests), str(fixture)], env=env, capture_output=True, text=True)
            print(run.stdout, end="")
            if run.returncode:
                print(run.stderr, end="", file=sys.stderr)
                run.check_returncode()
            match = re.search(r"Runtime regressions passed: (\d+) assertions", run.stdout)
            if not match:
                raise SystemExit("Runtime test receipt missing")
            assertions = int(match[1])
        elif not scratch:
            raise SystemExit("build_plugin.py: tests/*.cs missing: the committed DLL is written only "
                             "after the mocked regressions pass")
        else:
            print(f"build_plugin.py: no tests/ under {source}: mocked regressions not run", file=sys.stderr)
        built = candidate.read_bytes()
        # Preserve the previous committed DLL if compilation or tests fail.
        target = output if scratch else shipped
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(built)
    digest = hashlib.sha256(built).hexdigest()
    if scratch:
        print(f"Built {target} (sha256 {digest}, {len(built)} bytes) from {len(sources)} .cs files in "
              f"{source} with {len(stand_ins)} stand-in(s) from stubs/ and {len(references)} --reference "
              f"assembl{'y' if len(references) == 1 else 'ies'}; the committed DLL and plugin-build.json are untouched")
        return
    root = HERE.parents[1]
    inputs = sources + [STUB, Path(__file__).resolve()] + test_sources + [fixture]
    manifest = {
        "format": 1,
        "binary": "SEST.RuntimeFixes.dll",
        "sha256": digest,
        "inputs": {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        "validation": f"{assertions} assertions passed using mocked native APIs; no Unity gameplay claim",
    }
    (HERE / "plugin-build.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Built integration/runtime-fixes/SEST.RuntimeFixes.dll")


if __name__ == "__main__":
    main()
