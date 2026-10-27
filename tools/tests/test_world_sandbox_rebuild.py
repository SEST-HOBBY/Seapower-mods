"""A World Sandbox build over its own previous output gives the same files.

tools/build_all.py --from-scratch deletes SEST_World_Campaign before the
builder runs; a plain tools/build_all.py, or build_dynamic_campaign.py on its
own, does not. Until 27 Oct 2026 that second kind of build read the old-save
alias the first one had written (aircraft/usn_hh-60.ini, #!alias of
usn_hh-60h) as a real unit, placed the retired id and failed. These tests
compose the campaign in a separate process with the committed pack on disk,
which is exactly that situation, and write nothing into the repository.
"""
import difflib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "integration/world-sandbox"
PACK = HERE / "SEST_World_Campaign"
CAMPAIGN = PACK / "dynamic_campaigns/sest-world-sandbox/campaign.json"
REPORT = HERE / "draft/conversion.json"

# Runs in its own interpreter: the builder puts three folders on sys.path and
# imports build_pack, home_bases and submarines by bare name.
SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import build_dynamic_campaign as b
out = Path(sys.argv[2])
aliases = {}
for legacy, current in (b.LEGACY_HULL_ALIASES | b.LEGACY_AIRCRAFT_ALIASES).items():
    f = b.bp.unit_file(legacy)[1]
    aliases[legacy] = {"current": current, "file": str(f) if f else None,
                       "installed": b.bp.unit_file(current)[1] is not None,
                       "resolved": b.resolve(legacy)[0]}
campaign, report = b.compose()
(out / "campaign.json").write_text(b.campaign_text(campaign), encoding="utf-8")
(out / "conversion.json").write_text(b.report_text(report), encoding="utf-8")
(out / "aliases.json").write_text(json.dumps(aliases), encoding="utf-8")
"""


def first_difference(expected, actual, name):
    diff = difflib.unified_diff(expected.splitlines(), actual.splitlines(),
                                f"committed {name}", f"rebuilt {name}", lineterm="", n=2)
    return "\n".join(list(diff)[:40])


class WorldSandboxRebuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import global_land_mask  # noqa: F401  the committed lanes were checked with it
        except ImportError:
            raise unittest.SkipTest("global_land_mask not installed: lanes would differ")
        cls.tmp = tempfile.TemporaryDirectory()
        out = Path(cls.tmp.name)
        run = subprocess.run([sys.executable, "-c", SCRIPT, str(HERE), str(out)],
                             cwd=ROOT, capture_output=True, text=True)
        if run.returncode:
            cls.tmp.cleanup()
            raise AssertionError(f"compose() failed:\n{run.stdout}{run.stderr}")
        cls.campaign = (out / "campaign.json").read_text(encoding="utf-8")
        cls.report = (out / "conversion.json").read_text(encoding="utf-8")
        cls.aliases = json.loads((out / "aliases.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_own_old_save_alias_is_not_read_back_as_a_unit(self):
        own = {legacy: a for legacy, a in self.aliases.items()
               if a["file"] and PACK in Path(a["file"]).parents}
        if not own:
            self.skipTest("the pack holds no old-save alias, so there is nothing to read back")
        self.assertIn("usn_hh-60", own)
        for legacy, a in own.items():
            with self.subTest(legacy=legacy):
                self.assertEqual(a["resolved"], a["current"])

    def test_rebuild_over_the_committed_pack_reproduces_it(self):
        for path, rebuilt in ((CAMPAIGN, self.campaign), (REPORT, self.report)):
            with self.subTest(file=path.name):
                committed = path.read_text(encoding="utf-8")
                self.assertTrue(committed == rebuilt,
                                first_difference(committed, rebuilt, path.name))

    def test_rebuild_places_no_renamed_id(self):
        data = json.loads(self.campaign)
        placed = {u.split()[0] for f in data["forces"] for u in f["units"]}
        bought = {e["unit"] for e in data["catalogue"]}
        for legacy, a in self.aliases.items():
            if not a["installed"]:
                continue  # an older capture: the old id is still the unit
            with self.subTest(legacy=legacy):
                self.assertNotIn(legacy, placed)
                self.assertNotIn(legacy, bought)
                self.assertNotIn(legacy, data["values"])


if __name__ == "__main__":
    unittest.main()
