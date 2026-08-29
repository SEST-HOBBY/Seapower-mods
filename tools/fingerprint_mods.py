#!/usr/bin/env python3
"""Fingerprint every exported mod so upstream updates become visible.

The export copies each mod's text config into mods-source/<id>/ but records
nothing about WHICH version it captured, so a Workshop update lands silently:
the author changes a file, the export is now stale, and the only symptom is a
patch that quietly stops matching its donor. design-notes calls this out
("Upstream moves under you") and until now the only way to notice was to
re-export everything and read the git diff.

This writes data/mod-fingerprints.json - one content hash per mod - which
tools\\export-mod-configs.ps1 -CheckUpdates recomputes against the LIVE
workshop folders. Anything whose hash moved has been updated by its author
since the export; anything new is a fresh subscription.

The hash is defined identically in both places, so they must stay in step:

    for each file under the mod, with a tracked extension and <= 2 MB:
        key  = its path relative to the mod root, lowercased, forward slashes
        val  = SHA-256 of the file's bytes
    join "key:val" for all files sorted by key, with newlines
    fingerprint = SHA-256 of that string, UTF-8

    python3 tools/fingerprint_mods.py            # write the baseline
    python3 tools/fingerprint_mods.py --check    # verify it still matches
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS = ROOT / "mods-source"
OUT = ROOT / "data" / "mod-fingerprints.json"

# Must match $TextExtensions and $MaxFileBytes in tools/export-mod-configs.ps1.
EXTS = {".ini", ".txt", ".json", ".cfg", ".xml", ".md", ".yaml", ".yml", ".csv"}
MAX_BYTES = 2 * 1024 * 1024


def fingerprint(mod_dir):
    parts = []
    for f in sorted(mod_dir.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in EXTS:
            continue
        if f.stat().st_size > MAX_BYTES:
            continue
        rel = f.relative_to(mod_dir).as_posix().lower()
        parts.append(f"{rel}:{hashlib.sha256(f.read_bytes()).hexdigest()}")
    if not parts:
        return None, 0
    joined = "\n".join(sorted(parts))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest(), len(parts)


def collect():
    out = {}
    for d in sorted(p for p in MODS.iterdir() if p.is_dir() and p.name[0].isdigit()):
        fp, n = fingerprint(d)
        if fp:
            out[d.name] = {"fingerprint": fp, "files": n}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="compare against the committed baseline instead of writing it")
    args = ap.parse_args()

    current = collect()
    if args.check:
        if not OUT.exists():
            sys.exit(f"no baseline yet - run: python3 {Path(__file__).name}")
        old = json.loads(OUT.read_text(encoding="utf-8"))["mods"]
        changed = [m for m in current if m in old
                   and current[m]["fingerprint"] != old[m]["fingerprint"]]
        added = [m for m in current if m not in old]
        gone = [m for m in old if m not in current]
        for label, rows in (("changed since baseline", changed),
                            ("new since baseline", added),
                            ("no longer exported", gone)):
            if rows:
                print(f"{label}: {', '.join(rows)}")
        if changed or added or gone:
            return 1
        print(f"all {len(current)} mod fingerprints match the baseline")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "_comment": "Content hash per exported mod. Regenerate with "
                    "tools/fingerprint_mods.py after every export; compare "
                    "against the live install with export-mod-configs.ps1 "
                    "-CheckUpdates to see which mods the authors have updated.",
        "algorithm": "sha256 over sorted '<relpath lowercased>:<sha256 of bytes>' lines",
        "extensions": sorted(EXTS),
        "max_file_bytes": MAX_BYTES,
        "mods": current,
    }, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(current)} mods fingerprinted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
