"""File-layer probe tool: metadata reader, overrides scan, probe install and uninstall."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
import probe_file_layers as P  # noqa: E402

REPO = HERE.parents[2]
VANILLA = REPO / "mods-source" / "_vanilla"
DLL = REPO / "integration" / "runtime-fixes" / "SEST.RuntimeFixes.dll"
HORMUZ = VANILLA / "user" / "missions" / "NEW MISSIONS CLEAN" / "NATO" / "Hormuz.ini"


@unittest.skipUnless(DLL.exists(), "compiled plugin not present")
class TestMetadata(unittest.TestCase):
    def test_reads_types_methods_and_user_strings(self):
        m = P.ClrMetadata(DLL.read_bytes())
        types = m.types()
        self.assertEqual(types[0]["name"], "<Module>")
        names = {t["name"] for t in types}
        self.assertIn("CampaignCosts", names)
        cc = next(t for t in types if t["name"] == "CampaignCosts")
        self.assertIn("Bind", cc["methods"])
        self.assertTrue(any("IniHandler" in u for u in m.user_strings()))
        rep = P.scan_dll(DLL)
        self.assertEqual(len(rep["sha256"]), 64)

    def test_refuses_non_assembly(self):
        with self.assertRaises(ValueError):
            P.ClrMetadata(b"not a dll at all")


@unittest.skipUnless(VANILLA.exists() and HORMUZ.exists(), "vanilla export not present")
class TestProbes(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        sa = self.tmp / "StreamingAssets"
        (sa / "original" / "language_en").mkdir(parents=True)
        shutil.copy(VANILLA / "original" / "environment.ini", sa / "original")
        for f in ("aircraft_names.ini", "vessel_names.ini"):
            shutil.copy(VANILLA / "original" / "language_en" / f, sa / "original" / "language_en")
        um = sa / "user" / "missions" / "user_missions"
        um.mkdir(parents=True)
        self.mission = um / "MNO Weather Lab - Hormuz.ini"
        shutil.copy(HORMUZ, self.mission)
        self.sa = sa
        self.state = mock.patch.object(P, "STATE_DIR", self.tmp / "state")
        self.state.start()

    def tearDown(self):
        self.state.stop()
        shutil.rmtree(self.tmp)

    def tree(self):
        return sorted(p.relative_to(self.tmp).as_posix() for p in self.tmp.rglob("*") if "state" not in p.parts)

    def test_every_probe_installs_and_uninstalls_cleanly(self):
        before = self.tree()
        P.install("A-mod", self.sa, None, None)
        P.install("A-user1", self.sa, None, None)
        P.install("A2", self.sa, None, None)
        P.install("B1", self.sa, self.mission, None)
        P.install("C", self.sa, self.mission, "{dir}/{stem}_overrides")
        P.install("D", self.sa, self.mission, "{dir}/{stem}/x")
        text = (self.sa / "MNO_LayerProbe" / "overrides" / "language_en" / "aircraft_names.ini").read_text()
        self.assertIn("[usn_f-14a]", text)
        self.assertIn("Default=F-14A MNO-PROBE-A,F-14A", text)
        b1 = (self.mission.parent / self.mission.stem / "overrides" / "language_en" / "vessel_names.ini").read_text()
        self.assertIn("[usn_cg_belknap]", b1)
        self.assertIn("MNO-PROBE-B1", b1)
        c = (self.mission.parent / (self.mission.stem + "_overrides") / "environment.ini").read_text()
        self.assertIn("[Sonar]\nBaseAmbientOceanNoise=90", c)
        self.assertNotIn("[Night]", c)  # partial: only the [Sonar] sentinel
        d = (self.mission.parent / self.mission.stem / "x" / "environment.ini").read_text()
        self.assertIn("[Night]", d)
        self.assertEqual(sum(1 for ln in d.splitlines() if ln.startswith("BaseAmbientOceanNoise=90")), 1)  # one key line, comments aside
        P.uninstall("all", self.sa)
        self.assertEqual(self.tree(), before)  # nothing left behind, no empty folders

    def test_refusals(self):
        P.install("A-mod", self.sa, None, None)
        with self.assertRaises(SystemExit):
            P.install("A-mod", self.sa, None, None)  # files already exist
        target = self.sa / "MNO_LayerProbe" / "_info.ini"
        target.write_text(target.read_text() + "edited\n")
        rep = P.uninstall("A-mod", self.sa)
        self.assertTrue(any("REFUSED" in r for r in rep))
        self.assertTrue(target.exists())  # an edited file is never deleted
        with self.assertRaises(ValueError):
            P.probe_files("C", self.sa, self.mission, None)  # C needs a proven location


@unittest.skipUnless((REPO / "mods-source" / "3438479626" / "overrides").exists() and VANILLA.exists(), "Kuznetsov export not present")
class TestScanMods(unittest.TestCase):
    def test_kuznetsov_overrides_are_partial_additions(self):
        rows = P.scan_mods(REPO / "mods-source" / "3438479626", VANILLA / "original")
        f14 = next(r for r in rows if r["file"] == "aircraft/usn_f-14a_squadrons.ini")
        self.assertTrue(f14["partial"])
        self.assertGreater(f14["keys_added"], 0)
        self.assertGreater(f14["original_sections_left_out"], 10)


if __name__ == "__main__":
    unittest.main()
