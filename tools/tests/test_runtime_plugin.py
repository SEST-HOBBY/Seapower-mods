"""A source edit must not leave a stale committed runtime DLL in the installer."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "integration/runtime-fixes"


class RuntimePluginBuild(unittest.TestCase):
    def test_compiled_binary_matches_its_reviewed_sources(self):
        manifest = json.loads((PLUGIN / "plugin-build.json").read_text())
        for name, expected in manifest["inputs"].items():
            with self.subTest(source=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected,
                                 "Rebuild integration/runtime-fixes/build_plugin.py after editing runtime sources")
        self.assertEqual(hashlib.sha256((PLUGIN / manifest["binary"]).read_bytes()).hexdigest(), manifest["sha256"])
        self.assertEqual((PLUGIN / manifest["binary"]).read_bytes(),
                         (ROOT / "integration/dist/SEST_Integration/plugins" / manifest["binary"]).read_bytes())
        self.assertEqual([p.name for p in PLUGIN.glob("*.dll")], ["SEST.RuntimeFixes.dll"])


if __name__ == "__main__":
    unittest.main()
