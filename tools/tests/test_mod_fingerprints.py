"""The update-check baseline must describe the mods-source copies.

Prepare-PC runs export-mod-configs.ps1 -CheckUpdates against
data/mod-fingerprints.json. If a capture is taken in by path without
regenerating that file, every mod the capture refreshed is reported as an
author update on the PC and preparation stops (28 Nov 2026).
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location("fingerprint_mods", ROOT / "tools" / "fingerprint_mods.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModFingerprintBaseline(unittest.TestCase):
    def test_baseline_matches_mods_source(self):
        fp = _load()
        committed = json.loads(fp.OUT.read_text(encoding="utf-8"))["mods"]
        current = fp.collect()
        stale = sorted(m for m in set(current) | set(committed) if current.get(m) != committed.get(m))
        self.assertEqual(stale, [], "run python3 tools/fingerprint_mods.py after taking in a capture")


if __name__ == "__main__":
    unittest.main()
