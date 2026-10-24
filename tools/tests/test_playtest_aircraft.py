"""The geometry and phase couplings behind the October PC regressions."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "integration/dist/SEST_Integration"


def section(text, name):
    m = re.search(r"^\[" + re.escape(name) + r"\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not m:
        raise AssertionError(name + " missing")
    return m[1]


def value(text, key):
    return re.search(r"^" + re.escape(key) + r"=([^\s/]+)", text, re.M)[1]


class PlaytestAircraft(unittest.TestCase):
    def test_pure_aam_hornet_fits_cannot_show_sdb_racks(self):
        racks = {"bru-61a_left", "bru-61a_right", "bru-61a_left_inner", "bru-61a_right_inner"}
        for uid in ("usn_fa-18f", "usn_fa-18f_blk3", "usn_fa-18e"):
            text = (DIST / "aircraft" / (uid + ".ini")).read_text()
            for fit in ("SEST_MaliceBlockIII", "SEST_Intercept260", "SEST_Intercept260ER", "SEST_Escort260"):
                with self.subTest(uid=uid, fit=fit):
                    body = section(text, "WeaponSystem1" + fit)
                    hidden = set(value(body, "SubModelsToHide").split(","))
                    self.assertTrue(racks <= hidden)
                    self.assertNotRegex(body, r"(?m)^Station\d+=.*(?:gbu|sdb)")
                    if fit.endswith("ER") or fit == "SEST_Escort260":
                        self.assertNotRegex(body, r"(?m)^Station(?:32|33)=")

    def test_arrw_turns_early_and_separates_when_the_motor_ends(self):
        models = []
        for uid in ("dts_agm-183a", "dts_agm-183a(w62)", "usn_arrw"):
            text = (DIST / "ammunition" / (uid + ".ini")).read_text()
            with self.subTest(uid=uid):
                self.assertLessEqual(float(value(text, "InitialFlightPhaseDuration")), 1)
                burn = float(value(text, "SustainerAccelerationTime"))
                self.assertEqual(float(value(text, "ResourcesMeshSwitchTime")), burn)
                self.assertEqual(value(text, "ResourcesMesh"), "Glider")
                self.assertEqual(value(text, "ResourcesMeshForLaunch"), "agm-183")
                self.assertNotRegex(text, r"(?m)^InFlightEffect(?:Class)?=")
                self.assertEqual(len(re.findall(r"(?m)^SustainerEffect=", text)), 1)
                self.assertNotIn("SeaSkimming=True", text)
                models.append(section(text, "Models"))
        self.assertEqual(models[0], models[1])
        self.assertEqual(models[1], models[2])


if __name__ == "__main__":
    unittest.main()
