#!/usr/bin/env python3
"""Regression checks for the shared Redback fit recipe (integration/common/redback.py).

Run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_redback.py' -v
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration"))
from common import redback  # noqa: E402

AIRFRAME = """\
[WeaponSystem1]
AvailableLoadouts=Default,CAS
Station3=0.05,-0.003,0
TwinPositions=-0.004,-0.003,0|0.004,-0.003,0
MK-84Positions=0,-0.003,0
[WeaponSystem1Default]
Station1=usn_aim-9x
[WeaponSystem1CAS]
SubModelsToHide=rail_a
Station1=usn_aim-9x
Station2=usn_aim-9x
Station3=usn_gbu-12|Twin
Station4=usn_gbu-12|Twin
Station5=usn_hellfire
[Engine]
"""


def fit(text):
    return text.split("[WeaponSystem1SEST_REDBACK]\n", 1)[1].split("[", 1)[0]


class RedbackFit(unittest.TestCase):
    def test_a_pod_keeps_the_seat_by_default(self):
        body = fit(redback.add_fit(AIRFRAME, "t", "CAS", [("usn_gbu-12", "pod", 2)]))
        self.assertIn("Station3=sest_agr-30_pod|Twin\n", body)
        self.assertIn("AvailableLoadouts=Default,CAS,SEST_REDBACK",
                      redback.add_fit(AIRFRAME, "t", "CAS", [("usn_gbu-12", "pod", 2)]))

    def test_a_seat_is_set_or_dropped(self):
        body = fit(redback.add_fit(AIRFRAME, "t", "CAS", [
            ("usn_gbu-12", "pod19", 1, "MK-84", (3,)), ("usn_gbu-12", "pod", 1, ""),
            ("usn_hellfire", None, 1)]))
        self.assertIn("Station3=sest_agr-30_pod19|MK-84\n", body)
        self.assertIn("Station4=sest_agr-30_pod\n", body)
        self.assertNotIn("usn_hellfire", body)

    def test_stations_limit_a_swap(self):
        body = fit(redback.add_fit(AIRFRAME, "t", "CAS", [
            ("usn_aim-9x", "pod19", 1, "", (2,)), ("usn_gbu-12", "pod", 2)]))
        self.assertIn("Station1=usn_aim-9x\n", body)
        self.assertIn("Station2=sest_agr-30_pod19\n", body)

    def test_a_rack_is_hidden_once(self):
        body = fit(redback.add_fit(AIRFRAME, "t", "CAS", [("usn_gbu-12", "pod", 2)],
                                   hide=("rack_b", "rail_a")))
        self.assertIn("SubModelsToHide=rail_a,rack_b\n", body)

    def test_a_mount_is_added_ahead_of_the_fits(self):
        out = redback.add_fit(AIRFRAME, "t", "CAS", [("usn_gbu-12", "pod", 2, "New")],
                              positions={"New": "0,-0.001,0"})
        self.assertLess(out.index("NewPositions=0,-0.001,0"), out.index("[WeaponSystem1Default]"))
        self.assertGreater(out.index("NewPositions="), out.index("MK-84Positions="))
        self.assertIn("Station3=sest_agr-30_pod|New\n", fit(out))

    def test_upstream_changes_stop_the_build(self):
        for swaps, opts in (([("usn_gbu-12", "pod", 3)], {}),                 # count moved
                            ([("usn_gbu-12", "pod", 2, "Nowhere")], {}),       # seat has no offsets
                            ([("usn_gbu-12", "pod", 2)], {"positions": {"Twin": "0,0,0"}})):
            with self.assertRaises(SystemExit):
                redback.add_fit(AIRFRAME, "t", "CAS", swaps, **opts)
        with self.assertRaises(SystemExit):
            redback.add_fit(AIRFRAME, "t", "Missing", [("usn_gbu-12", "pod", 2)])


if __name__ == "__main__":
    unittest.main()
