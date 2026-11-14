#!/usr/bin/env python3
"""Remove from the game export the files the game no longer ships.

tools/export-mod-configs.ps1 -IncludeVanilla copies the game's text files
over mods-source/_vanilla/original and removes nothing, so a file an update
dropped stays in the repository, keeps resolving for every checker and looks
like a file the game still ships. Only the install can say which those are,
and since 13 Nov 2026 every capture writes the list:
data/install-snapshot/game-files-dropped.txt (tools/capture-context.ps1),
headed by the build the export held and the build that was installed.

    python3 tools/apply_dropped_files.py           # remove the listed files
    python3 tools/apply_dropped_files.py --check   # say what would go; exit 1 if any

It removes the files only when the export now holds the build the list was
taken against: the list's "installed" line must be the build of
mods-source/_vanilla/changelog.txt. With a beta installed the list is the
beta's, the export stays the release, and nothing is removed. After it,
tools/check_vanilla_drift.py reports each removed file with what forks or
fields it, which is what that tool's exit code is for.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIST = "data/install-snapshot/game-files-dropped.txt"
EXPORT = "mods-source/_vanilla"
BUILD = re.compile(r"\d{1,2}-[A-Za-z]{3}-\d{4}:\s+(\d+(?:\.\d+)+)\s+Build\s+#?(\w+)")


def build_of(text):
    """(version, build) of the first dated build line in a text, or None."""
    m = BUILD.search(text or "")
    return (m.group(1), m.group(2)) if m else None


def read_list(text):
    """-> (the build the list was taken against, the listed paths, why it holds none)."""
    installed = None
    paths, listing, why = [], False, None
    for line in text.splitlines():
        if line.startswith("# installed:"):
            installed = build_of(line)
        elif line.startswith("not compared:"):
            why = line.strip()
        elif re.match(r"^no longer shipped \(\d+\):", line):
            listing = True
        elif listing and line.startswith("  ") and line.strip():
            paths.append(line.strip())
    return installed, paths, why


def apply(root=ROOT, check=False, out=print):
    """Remove the listed files (or, with check, only report). -> the exit code."""
    root = Path(root)
    listed = root / LIST
    if not listed.is_file():
        out(f"{LIST} is not there: the capture that wrote this snapshot predates it (13 Nov 2026).")
        return 1
    installed, paths, why = read_list(listed.read_text(encoding="utf-8-sig", errors="replace"))
    if why:
        out(f"{LIST}: {why}")
        return 1
    changelog = root / EXPORT / "changelog.txt"
    exported = build_of(changelog.read_text(encoding="utf-8-sig", errors="replace")) if changelog.is_file() else None
    if installed is None or exported is None:
        out("The list or the export names no build, so the two cannot be matched. Nothing removed.")
        return 1
    if installed != exported:
        out(f"The list was taken with {installed[0]} Build {installed[1]} installed and the export holds "
            f"{exported[0]} Build {exported[1]}. Nothing removed: the list is for another game than the export.")
        return 1
    base = (root / EXPORT / "original").resolve()
    gone = []
    for rel in paths:
        target = (base / rel).resolve()
        if base not in target.parents:
            out(f"refused, outside the export: {rel}")
            return 1
        if target.is_file():
            gone.append((rel, target))
    out(f"{LIST}: {len(paths)} listed, {len(gone)} still in {EXPORT}/original")
    for rel, target in gone:
        out(("   would remove " if check else "   removed ") + rel)
        if not check:
            target.unlink()
    return 1 if (check and gone) else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="remove nothing; exit 1 when a listed file is still there")
    return apply(check=parser.parse_args().check)


if __name__ == "__main__":
    sys.exit(main())
