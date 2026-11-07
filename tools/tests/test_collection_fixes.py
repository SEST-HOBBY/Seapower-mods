#!/usr/bin/env python3
"""SEST Collection Fixes and the 28 Oct 2026 export.

The SM-3 IIA and IIB overwrites in the Euromod Anchorchain Expansion gained
an [ExtendedGuidance] section, five keys only the AC Pack's ExtendedGuidance
plugin reads. SEST keeps that plugin off, so the keys are declined
(SM3_OVWR_DECLINED, the owner's decision of 30 Oct 2026): the rounds keep the
game's own guidance, and the guard still stops the build if the author moves
a value or gives the IB the section.

Charles De Gaulle & Modern French Navy renamed its [EOMS-NG] sensor
[EOMS_NG] and left both carriers mounting EOMS-NG, which then nothing
defined; this pack supplies [EOMS-NG], cloned from the author's renamed
section (MISSING_SENSORS).

The checks on built files need a build; run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_collection_fixes.py' -v
"""
import importlib.util
import re
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXES = ROOT / "integration/collection-fixes/SEST_Collection_Fixes"
DIST = ROOT / "integration/dist/SEST_Integration"
FRENCH = ROOT / "mods-source/3567256221"
SM3 = ("usn_rim-161b", "usn_rim-161c", "usn_rim-161d")
EG_KEYS = ("SeekerProfile", "SeekerTrackRate", "IRBackgroundRejection",
           "IRBrightnessRejection", "IRShapeRejection")


def builder():
    spec = importlib.util.spec_from_file_location(
        "collection_fixes_build_patch", ROOT / "integration/collection-fixes/build_patch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return Path(path).read_text(encoding="utf-8-sig", errors="replace")


def section(text, name):
    """A section's body, its header's trailing comment allowed; None if absent."""
    m = re.search(rf"^\[{re.escape(name)}\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def lines(body):
    """A body's lines, comments and blank lines aside."""
    return [x.rstrip() for x in body.splitlines() if x.strip() and not x.lstrip().startswith("#")]


class SM3ExtendedGuidance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bp = builder()

    def base(self, name):
        return self.bp.read("3629144864", f"ammunition/{name}.ini")

    def overwrite(self, name):
        return self.bp.read(self.bp.SM3_OVERWRITE, f"ammunition_overwrite/{name}_OVWR.ini")

    def check(self, name, text):
        """sm3_check_overwrite() with the round's overwrite read as `text`."""
        real = self.bp.read

        def fake(mod, rel):
            if (mod, rel) == (self.bp.SM3_OVERWRITE, f"ammunition_overwrite/{name}_OVWR.ini"):
                return text
            return real(mod, rel)

        with mock.patch.object(self.bp, "read", fake):
            self.bp.sm3_check_overwrite(self.base(name), name)

    def test_the_export_reads_as_recorded(self):
        for name in SM3:
            with self.subTest(name=name):
                self.bp.sm3_check_overwrite(self.base(name), name)

    def test_the_iia_and_iib_set_them_and_the_ib_does_not(self):
        for name in SM3:
            with self.subTest(name=name):
                has = "[ExtendedGuidance]" in self.overwrite(name)
                self.assertEqual(has, name != "usn_rim-161b")
                for key in EG_KEYS:
                    self.assertEqual(name in self.bp.SM3_OVWR_DECLINED[key], has, key)

    def test_the_ib_gaining_the_section_stops_the_build(self):
        name = "usn_rim-161b"
        with self.assertRaises(SystemExit) as caught:
            self.check(name, self.overwrite(name)
                       + "\n[ExtendedGuidance]\nSeekerProfile=IIR_Imaging\n")
        self.assertIn("SeekerProfile", str(caught.exception))

    def test_a_moved_value_stops_the_build(self):
        name = "usn_rim-161d"
        text = self.overwrite(name)
        self.assertIn("SeekerTrackRate=50\n", text)
        with self.assertRaises(SystemExit) as caught:
            self.check(name, text.replace("SeekerTrackRate=50\n", "SeekerTrackRate=60\n"))
        self.assertIn("SeekerTrackRate=60", str(caught.exception))

    def test_a_key_not_recorded_stops_the_build(self):
        # The two Patriot overwrites carry SeekerBeamWidth; the SM-3s do not.
        name = "usn_rim-161c"
        with self.assertRaises(SystemExit) as caught:
            self.check(name, self.overwrite(name) + "SeekerBeamWidth=4\n")
        self.assertIn("SeekerBeamWidth", str(caught.exception))

    def test_the_built_rounds_carry_none_of_them(self):
        for name in SM3:
            with self.subTest(name=name):
                text = read(FIXES / "ammunition" / f"{name}.ini")
                self.assertNotIn("[ExtendedGuidance]", text)
                for key in EG_KEYS:
                    self.assertNotRegex(text, rf"(?m)^\s*{key}\s*=")


class CharlesDeGaulleEomsNg(unittest.TestCase):
    CARRIERS = {"fr_cvn_charles-de-gaulle": "SensorSystem6",
                "fr_cvn_charles-de-gaulle_late": "SensorSystem5"}

    def test_both_carriers_still_mount_it(self):
        # The day the author points them at [EOMS_NG], the entry retires.
        for hull, mount in self.CARRIERS.items():
            with self.subTest(hull=hull):
                body = section(read(FRENCH / "vessels" / f"{hull}.ini"), mount)
                self.assertRegex(body, r"(?m)^SystemName=EOMS-NG\s*$")

    def test_no_mod_defines_it(self):
        # build_missing_sensors() stops the build then, rather than shadow it.
        definers = [f.relative_to(ROOT).as_posix()
                    for f in sorted((ROOT / "mods-source").rglob("systems/sensors.ini"))
                    if section(read(f), "EOMS-NG") is not None]
        self.assertEqual(definers, [])

    def test_the_clone_is_the_authors_renamed_section(self):
        donor = section(read(FRENCH / "systems" / "sensors.ini"), "EOMS_NG")
        self.assertIsNotNone(donor)
        built = section(read(FIXES / "systems" / "sensors.ini"), "EOMS-NG")
        self.assertIsNotNone(built)
        self.assertEqual(lines(built), lines(donor))
        self.assertRegex(built, r"(?m)^Kind=Visual\b")
        self.assertRegex(built, r"(?m)^MaxRange=40\.0\b")
        self.assertRegex(built, r"(?m)^HasDataLink=True\b")

    def test_the_consolidated_pack_has_it(self):
        built = section(read(FIXES / "systems" / "sensors.ini"), "EOMS-NG")
        shipped = section(read(DIST / "systems" / "sensors.ini"), "EOMS-NG")
        self.assertIsNotNone(shipped)
        self.assertEqual(lines(shipped), lines(built))


if __name__ == "__main__":
    unittest.main()
