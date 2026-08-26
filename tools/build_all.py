#!/usr/bin/env python3
"""Rebuild every SEST pack from mods-source/, in dependency order.

Why order matters: SEST_RAAF_Bases validates its air groups against sibling
packs' output (integration/raaf-bases/build_pack.py resolves squadrons through
integration/*/SEST_*/aircraft/), so on a clean tree it must build after the
packs it reads. That edge is declared in data/mod-catalog.json's local_packs
registry as "build_after" — this script topologically sorts on it, so the
ordering can never again be satisfied only by accident of alphabetical
iteration.

    python3 tools/build_all.py               # rebuild all 15 in order
    python3 tools/build_all.py --from-scratch  # delete pack output first, then
                                               # rebuild; with committed output,
                                               # `git status` after a clean run
                                               # must come back empty

--from-scratch plus a clean `git status` is the repo's regression gate: it
proves the committed pack output is byte-identical to what the builders
produce from the current mods-source export.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ordered_packs():
    packs = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))["local_packs"]
    by_folder = {p["folder"]: p for p in packs}
    done, out = set(), []

    def visit(pack, chain=()):
        if pack["folder"] in done:
            return
        if pack["folder"] in chain:
            sys.exit(f"build_after cycle: {' -> '.join(chain + (pack['folder'],))}")
        for dep in pack.get("build_after", []):
            if dep not in by_folder:
                sys.exit(f"{pack['folder']}: build_after names unknown pack {dep!r}")
            visit(by_folder[dep], chain + (pack["folder"],))
        done.add(pack["folder"])
        out.append(pack)

    for pack in packs:
        visit(pack)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-scratch", action="store_true",
                        help="delete every pack's output folder before rebuilding")
    args = parser.parse_args()

    packs = ordered_packs()
    if args.from_scratch:
        for pack in packs:
            target = ROOT / pack["source"] / pack["folder"]
            if target.exists():
                shutil.rmtree(target)
        dist = ROOT / "integration" / "dist" / "SEST_Integration"
        if dist.exists():
            shutil.rmtree(dist)
        print(f"deleted {len(packs)} pack folders + dist")

    failed = []
    for pack in packs:
        builder = ROOT / pack["source"] / pack["builder"]
        run = subprocess.run([sys.executable, str(builder)], cwd=ROOT,
                             capture_output=True, text=True)
        status = "ok" if run.returncode == 0 else "FAILED"
        print(f"  {status:<7} {pack['folder']}")
        if run.returncode != 0:
            failed.append(pack["folder"])
            print("    " + (run.stdout + run.stderr).strip().replace("\n", "\n    "))

    if failed:
        sys.exit(f"{len(failed)} builder(s) failed: {', '.join(failed)}")

    # Final stage: merge the per-pack outputs into the one deployable pack.
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "consolidate_packs.py")],
                         cwd=ROOT, capture_output=True, text=True)
    print(("  ok      " if run.returncode == 0 else "  FAILED  ") + "SEST_Integration (dist)")
    if run.returncode != 0:
        sys.exit("    " + (run.stdout + run.stderr).strip().replace("\n", "\n    "))

    print(f"\nall {len(packs)} packs built and consolidated. If output is committed, "
          "`git status` should now be clean — a diff means mods-source or a builder changed.")


if __name__ == "__main__":
    main()
