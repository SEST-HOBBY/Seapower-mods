"""The ice-features runtime drop-in (runtime-drop-in/ice-features): generated data up to date,
the pure C# free of game types and network use, and its Mono test exe passing (skipped without mcs)."""
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ENV = Path(__file__).resolve().parents[1]
DROP = ENV / "runtime-drop-in" / "ice-features"


class TestIceFeaturesDropIn(unittest.TestCase):
    def test_generated_files_up_to_date(self):
        r = subprocess.run([sys.executable, str(ENV / "tools" / "make_ice_features_data.py"), "--check"],
                           capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_sources_follow_the_runtime_rules(self):
        for name in ("IceFeaturesData.g.cs", "IceShelfRules.cs", "IcebergField.cs", "IceFeaturesBattle.cs"):
            text = (DROP / name).read_text(encoding="utf-8")
            self.assertIn("namespace Sest.RuntimeFixes\n{", text, name)  # block namespace: mcs and Roslyn C# 12
            self.assertNotRegex(text, r"System\.Net|WebClient|HttpClient|UnityWebRequest", name)  # no network in game code
        for name in ("IceFeaturesData.g.cs", "IceShelfRules.cs", "IcebergField.cs"):
            text = (DROP / name).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"using (UnityEngine|SeaPower)", name)  # pure logic
        battle = (DROP / "IceFeaturesBattle.cs").read_text(encoding="utf-8")
        for switch in ("IceShelves", "Icebergs", "IceFeaturesDiagnostics"):
            self.assertRegex(battle, r'TextOption\(lines, "%s", "0"\)' % switch)  # OFF unless set to 1
        self.assertIsNone(re.search(r"using SeaPower", battle))  # game access by reflection only

    @unittest.skipUnless(shutil.which("mcs") and shutil.which("mono"), "mcs/mono not installed")
    def test_mono_build_and_tests(self):
        r = subprocess.run([sys.executable, str(DROP / "build_drop_in.py")], capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-4000:] + r.stderr[-4000:])
        self.assertRegex(r.stdout, r"ice features: \d+ checks passed")


if __name__ == "__main__":
    unittest.main()
