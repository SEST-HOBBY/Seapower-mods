#!/usr/bin/env python3
"""Check the local export by ID and content; this cannot read Steam subscriptions."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLED_STATUSES = {"active", "deprecated", "wip"}


def audit(root):
    source = root / "mods-source"
    with (source / "_export-manifest.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    catalog = json.loads((root / "data/mod-catalog.json").read_text(encoding="utf-8-sig"))
    tokens = [s.strip() for s in (root / "data/load-order.tokens.txt").read_text(encoding="utf-8-sig").splitlines()
              if s.strip() and not s.lstrip().startswith("#")]
    groups = {
        "manifest": [r["WorkshopId"] for r in rows],
        "folders": [p.name for p in source.iterdir() if p.is_dir() and p.name.isascii() and p.name.isdigit()],
        "catalog": [m["workshop_id"] for m in catalog["mods"] if m.get("status") in INSTALLED_STATUSES],
        "order": [s for s in tokens if s != "SEST_Integration"],
    }
    problems = []
    if not rows:
        problems.append("Export manifest is empty")
    if not tokens or tokens[0] != "SEST_Integration" or tokens.count("SEST_Integration") != 1:
        problems.append("Load order must contain exactly one SEST_Integration, at position 1")
    all_catalog_ids = [m["workshop_id"] for m in catalog["mods"]]
    for name, ids in {**groups, "all catalog entries": all_catalog_ids}.items():
        duplicates = sorted(k for k, n in Counter(ids).items() if n > 1)
        if duplicates:
            problems.append(f"{name}: duplicate IDs {', '.join(duplicates)}")
        invalid = sorted(set(i for i in ids if not i.isascii() or not i.isdigit()))
        if invalid:
            problems.append(f"{name}: invalid Workshop IDs {invalid}")
    expected = set(groups["manifest"])
    for name in ("folders", "catalog", "order"):
        actual = set(groups[name])
        if actual != expected:
            problems.append(f"{name}: missing={sorted(expected - actual)}; extra={sorted(actual - expected)}")

    files = {}
    for row in rows:
        wid = row["WorkshopId"]
        if not wid.isascii() or not wid.isdigit():
            continue
        entries = [p for p in (source / wid).rglob("*") if p.is_file()]
        size = sum(p.stat().st_size for p in entries)
        if len(entries) != int(row["FilesCopied"]) or size != int(row["Bytes"]):
            problems.append(f"{wid}: manifest {row['FilesCopied']} files / {row['Bytes']} bytes; "
                            f"disk {len(entries)} files / {size} bytes")
        for p in entries:
            rel = p.relative_to(source).as_posix()
            key = rel.casefold()
            if key in files:
                problems.append(f"Windows path collision: {files[key].relative_to(source)} / {rel}")
            files[key] = p

    # New exports carry per-file hashes. Older manifests prove only totals,
    # never which particular paths are stale or whether equal-size bytes changed.
    file_manifest = source / "_export-files.csv"
    if file_manifest.exists():
        seen = set()
        with file_manifest.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                rel = row["RelativePath"].replace("\\", "/")
                wid = row["WorkshopId"]
                if not wid.isascii() or not wid.isdigit() or not rel or rel.startswith("/") or any(p in {"", ".", ".."} for p in rel.split("/")) or ":" in rel:
                    problems.append(f"Unsafe file-manifest path: {wid}/{rel}")
                    continue
                key = f"{wid}/{rel}".casefold()
                if key in seen:
                    problems.append(f"Duplicate file-manifest path: {key}")
                seen.add(key)
                path = files.get(key)
                if path is None:
                    problems.append(f"File-manifest path missing on disk: {key}")
                elif path.stat().st_size != int(row["Bytes"]) or hashlib.sha256(path.read_bytes()).hexdigest() != row["SHA256"].lower():
                    problems.append(f"File-manifest content mismatch: {key}")
        if seen != set(files):
            problems.append(f"Per-file manifest coverage differs: {len(set(files) - seen)} unlisted files")
    counts = {name: len(ids) for name, ids in groups.items()}
    return counts, problems, file_manifest.exists()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        counts, problems, hashes = audit(args.root)
    except (OSError, ValueError, KeyError) as exc:
        raise SystemExit(f"Inventory audit could not read its inputs: {exc}")
    print("Workshop IDs: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"Mod Manager entries: {counts['order']} Workshop + 1 SEST = {counts['order'] + 1}")
    print("Steam account subscription total: not measured by this export")
    if not hashes:
        print("Legacy manifest: file counts/bytes checked; per-file hashes unavailable")
    for problem in problems:
        print(f"FAIL: {problem}")
    print(f"Inventory audit: {'FAILED' if problems else 'PASS'}")
    return bool(problems)


if __name__ == "__main__":
    raise SystemExit(main())
