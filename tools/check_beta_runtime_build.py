#!/usr/bin/env python3
"""Read-only SEST gate for the Sea Power 0.8.7 Build 261026 public beta.

The existing check_game_version.py compares dotted versions, so two 0.8.7
builds can pass while their native DLLs differ. This checks the exact build
and warns about source-pinned assembly hashes. It never retargets a hash.
"""
import argparse
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = re.compile(r'^\s*\d{1,2}-[A-Za-z]{3}-\d{4}:\s+(\d+(?:\.\d+)+)\s+Build\s+#?(\w+)', re.M)
RUNTIME_HASH = re.compile(r'\bconst\s+string\s+inspected\s*=\s*"([a-fA-F0-9]{64})"')
NATIVE_HASHES = re.compile(r'NativeHashes\s*=\s*\{\s*"([a-fA-F0-9]{64})"\s*,\s*"([a-fA-F0-9]{64})"', re.S)
UI_RUNTIME_HASH = re.compile(r'\bconst\s+string\s+RuntimeHash\s*=\s*"([a-fA-F0-9]{64})"')


def parse_build(text):
    m = BUILD.search(text)
    return m.groups() if m else None


def source_pins(runtime_source, ui_source):
    native = None
    ui_native = None
    ui_noesis = None
    ui_runtime = None
    if runtime_source.exists():
        m = RUNTIME_HASH.search(runtime_source.read_text(encoding='utf-8-sig'))
        native = m.group(1).lower() if m else None
    if ui_source.exists():
        src = ui_source.read_text(encoding='utf-8-sig')
        m = NATIVE_HASHES.search(src)
        if m:
            ui_native, ui_noesis = [v.lower() for v in m.groups()]
        m = UI_RUNTIME_HASH.search(src)
        if m:
            ui_runtime = m.group(1).lower()
    return {'runtime_game': native, 'ui_game': ui_native, 'ui_noesis': ui_noesis,
            'ui_runtime': ui_runtime}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inspect(expected_version, expected_build, changelog, runtime_src, ui_src,
            scripts_dll=None, noesis_dll=None, sest_runtime_dll=None):
    problems = []
    notes = []
    if not changelog.is_file():
        problems.append(f'BLOCKED: changelog capture missing: {changelog}')
    else:
        found = parse_build(changelog.read_text(encoding='utf-8-sig', errors='replace'))
        if not found:
            problems.append('BLOCKED: cannot extract build from changelog')
        elif found != (expected_version, expected_build):
            problems.append(f'STALE: captured game is {found[0]} Build {found[1]}, expected {expected_version} Build {expected_build}')
        else:
            notes.append(f'OK: captured version {found[0]} Build {found[1]}')
    pins = source_pins(runtime_src, ui_src)
    if not pins['runtime_game']:
        problems.append('BLOCKED: runtime source hash pin unavailable; do not relax the gate')
    if not pins['ui_game'] or not pins['ui_noesis'] or not pins['ui_runtime']:
        problems.append('BLOCKED: UI hash pins unavailable; review PR #50/#51 or its integration first')
    if pins['ui_game'] and pins['runtime_game'] and pins['ui_game'] != pins['runtime_game']:
        problems.append('MISMATCH: runtime and UI source disagree on inspected game assembly')
    for name, path, expected in (
        ('Seapower-Scripts.dll', scripts_dll, pins['runtime_game']),
        ('Noesis.NoesisGUI.dll', noesis_dll, pins['ui_noesis']),
        ('SEST.RuntimeFixes.dll', sest_runtime_dll, pins['ui_runtime']),
    ):
        if path is None:
            problems.append(f'BLOCKED: {name} not supplied for hash check')
        elif not path.is_file():
            problems.append(f'BLOCKED: {name} not found at {path}')
        elif expected:
            actual = digest(path)
            if actual != expected:
                problems.append(f'MISMATCH: {name} SHA256 {actual} != inspected pin {expected}; ABI review and rebuild required')
            else:
                notes.append(f'OK: {name} matches inspected source pin {actual}')
    return problems, notes


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-version', default='0.8.7')
    p.add_argument('--expected-build', default='261026')
    p.add_argument('--changelog', type=Path, default=ROOT / 'data/install-snapshot/changelog.live.txt')
    p.add_argument('--runtime-source', type=Path, default=ROOT / 'integration/runtime-fixes/SestRuntimeFixes.cs')
    p.add_argument('--ui-source', type=Path, default=ROOT / 'integration/ui-followup/source/ContactsFix.cs')
    p.add_argument('--scripts-dll', type=Path)
    p.add_argument('--noesis-dll', type=Path)
    p.add_argument('--sest-runtime-dll', type=Path)
    args = p.parse_args(argv)
    problems, notes = inspect(args.expected_version, args.expected_build, args.changelog,
                              args.runtime_source, args.ui_source,
                              args.scripts_dll, args.noesis_dll, args.sest_runtime_dll)
    for line in notes + problems:
        print(line)
    if problems:
        print('NOT BETA-CLEARED. Do not change hashes without inspecting and rebuilding for this exact build.')
        return 1
    print('STATIC BUILD/HASH GATES MATCH; runtime playtests still required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
