#!/usr/bin/env python3
"""Regression checks for the patrol-loop thinner and the Lean v2 handover.

Run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_thin_waypoints.py' -v
"""
import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = ROOT / "integration" / "missions"
sys.path.insert(0, str(MISSIONS))
import thin_waypoints as thin  # noqa: E402
from build_land_defence import Mission  # noqa: E402


class PeriodTests(unittest.TestCase):
    def test_repeated_loop_is_found(self):
        self.assertEqual(4, thin.period(["a", "b", "a", "c"] * 12))
        self.assertEqual(3, thin.period(["a", "b", "c"] * 4))

    def test_trailing_partial_lap_is_allowed(self):
        self.assertEqual(4, thin.period(["a", "b", "a", "c"] * 3 + ["a", "b"]))

    def test_a_route_that_does_not_repeat_is_none(self):
        self.assertIsNone(thin.period(["a", "b", "c", "d"]))
        self.assertIsNone(thin.period(["a", "b", "a", "b", "c"]))
        self.assertIsNone(thin.period(["a"]))

    def test_annotations_stay_on_the_point(self):
        self.assertEqual((-60.0, -270.0), thin.xz("-60.000,Periscope,-270.000"))
        self.assertEqual((1.5, -2.25), thin.xz("1.5,220.4727,-2.25/SetTelegraph,3"))


class LeanV2HandoverTests(unittest.TestCase):
    def test_source_preservation_and_repeatable_output(self):
        source = MISSIONS / "SEST Banda Front Living Seas.ini"
        expected = (MISSIONS / "SEST Banda Front Lean v2.ini").read_bytes()
        before = source.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            shutil.copyfile(source, temp / source.name)
            with patch.object(thin, "MISSIONS", temp), patch.object(sys, "argv", ["thin_waypoints.py"]):
                with contextlib.redirect_stdout(io.StringIO()):
                    thin.main()
                    first = (temp / "SEST Banda Front Lean v2.ini").read_bytes()
                    thin.main()
                self.assertEqual(first, (temp / "SEST Banda Front Lean v2.ini").read_bytes())
            self.assertEqual(expected, first)
            self.assertEqual(before, (temp / source.name).read_bytes())
            living = Mission(source)
            lean = Mission(temp / "SEST Banda Front Lean v2.ini")
            self.assertEqual([], lean.verify())
            # only the selected routes differ; every other block is verbatim
            touched = 0
            for side in thin.SIDES:
                for cls in thin.MOVING + ("LandUnit",):
                    old = {n: b for n, _, _, _, b in living.units(side, cls)}
                    new = {n: b for n, _, _, _, b in lean.units(side, cls)}
                    self.assertEqual(list(old), list(new))
                    for n in old:
                        if old[n] != new[n]:
                            touched += 1
                            ty = next(t for m, t, *_ in living.units(side, cls) if m == n)
                            self.assertTrue("narco" in ty or "civ_fv" in ty, n)
                            self.assertEqual(old[n].count("\n"), new[n].count("\n"))
            self.assertEqual(12, touched)
            self.assertEqual(living.formation_specs("Neutral"), lean.formation_specs("Neutral"))
        self.assertEqual(before, source.read_bytes())


if __name__ == "__main__":
    unittest.main()
