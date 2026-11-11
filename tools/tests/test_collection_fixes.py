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

The post-1991, Russian-built hulls register the game's Russia key through one
#!extend Nation stub each on their winning variants file (RU_REREGISTER, the
owner's Tier A rule of 11 Nov 2026); the classes the rule leaves Soviet are
in RU_LEFT_SOVIET with the reason.

The checks on built files need a build; run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_collection_fixes.py' -v
"""
import contextlib
import importlib.util
import re
import sys
import tempfile
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


class RussianRegistration(unittest.TestCase):
    """The post-1991, Russian-built hulls registered to the game's Russia key
    by one #!extend Nation stub each on the winning variants file
    (RU_REREGISTER, the owner's Tier A rule of 11 Nov 2026). The readers of
    the stubs are tested in test_russian_registration.py and
    test_build_pack.py."""

    @classmethod
    def setUpClass(cls):
        cls.b = builder()
        cls.stubs = {p.name: p for p in sorted((FIXES / "vessels_overwrite").glob(
            "*" + cls.b.RU_STUB_SUFFIX))}
        if not cls.stubs:
            raise unittest.SkipTest("SEST Collection Fixes not built")

    def rel(self, uid):
        return f"vessels/{uid}_variants.ini"

    def winner(self, uid):
        mod = self.b.top_provider(self.rel(uid))
        return mod, ROOT / "mods-source" / mod / self.rel(uid)

    def test_one_stub_per_allowed_hull(self):
        self.assertEqual(sorted(self.stubs),
                         sorted(uid + self.b.RU_STUB_SUFFIX for uid in self.b.RU_REREGISTER))
        self.assertEqual(len(self.stubs), 15)

    def test_the_two_lists_are_apart_and_the_pashin_is_in_neither(self):
        self.assertFalse(set(self.b.RU_REREGISTER) & set(self.b.RU_LEFT_SOVIET))
        for uid in self.b.RU_LEFT_SOVIET:
            self.assertNotIn(uid + self.b.RU_STUB_SUFFIX, self.stubs)
        self.assertNotIn("rfn_aor_pashin", self.b.RU_REREGISTER)
        self.assertNotIn("rfn_aor_pashin", self.b.RU_LEFT_SOVIET)

    def test_each_stub_extends_its_winner(self):
        for uid in self.b.RU_REREGISTER:
            with self.subTest(uid=uid):
                text = read(self.stubs[uid + self.b.RU_STUB_SUFFIX])
                self.assertEqual(text.splitlines()[0], f"#!extend {self.rel(uid)}")
                mod, path = self.winner(uid)
                self.assertNotEqual(mod, "_vanilla/original")
                self.assertTrue(path.is_file())
                self.assertFalse(read(path).lstrip().startswith("#!"))
                # No SEST pack ships the file the stub layers onto.
                self.assertEqual([p for p in ROOT.glob(f"integration/*/SEST_*/{self.rel(uid)}")
                                  if "dist" not in p.parts], [])

    def test_each_section_is_the_winners_soviet_one_and_says_russia(self):
        for uid in self.b.RU_REREGISTER:
            with self.subTest(uid=uid):
                stub = read(self.stubs[uid + self.b.RU_STUB_SUFFIX])
                _mod, path = self.winner(uid)
                target = read(path)
                names = [n for n in re.findall(r"^\[([^\]\n]+)\]", target, re.M) if n != "General"]
                default = self.b.section_nation(target, "Default")
                soviet = [n for n in names
                          if (self.b.section_nation(target, n) or default).lower() in ("soviet", "ussr")]
                stubbed = re.findall(r"^\[([^\]\n]+)\]", stub, re.M)
                self.assertEqual(stubbed, soviet)
                self.assertIn("Default", stubbed)
                for name in stubbed:
                    self.assertEqual(lines(section(stub, name)), ["Nation=Russia"])

    def test_no_stub_touches_a_stock_hull_or_a_stock_roster(self):
        rostered = self.b.stock_rostered()
        self.assertIn("wp_rkr_kirov", rostered)       # Pacific Strike's enemy roster is read
        vanilla = ROOT / "mods-source/_vanilla/original/vessels"
        for uid in self.b.RU_REREGISTER:
            with self.subTest(uid=uid):
                self.assertNotIn(uid.lower(), rostered)
                self.assertFalse((vanilla / f"{uid}.ini").exists())
                self.assertFalse((vanilla / f"{uid}_variants.ini").exists())

    def test_a_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(self.b, "OUT", Path(tmp)):
            self.b.build_russian_registrations()
            again = {p.name: p.read_bytes()
                     for p in (Path(tmp) / "vessels_overwrite").glob("*" + self.b.RU_STUB_SUFFIX)}
        self.assertEqual(again, {n: p.read_bytes() for n, p in self.stubs.items()})

    def test_the_consolidated_pack_has_them(self):
        for name, path in self.stubs.items():
            with self.subTest(stub=name):
                self.assertEqual((DIST / "vessels_overwrite" / name).read_bytes(), path.read_bytes())

    def test_the_mod_manager_text_says_so(self):
        self.assertIn("to the Russian Federation instead of the USSR", read(FIXES / "_info.ini"))

    def refused(self, uid, **patches):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(self.b, "OUT", Path(tmp)), \
                mock.patch.dict(self.b.RU_REREGISTER, {uid: "a test hull"}, clear=True), \
                contextlib.ExitStack() as stack:
            for name, value in patches.items():
                if name == "left":
                    stack.enter_context(mock.patch.dict(self.b.RU_LEFT_SOVIET, {uid: "x"}))
                else:
                    stack.enter_context(mock.patch.object(self.b, name, value))
            with self.assertRaises(SystemExit) as caught:
                self.b.build_russian_registrations()
        self.assertIn(uid, str(caught.exception))
        return str(caught.exception)

    def test_the_guards_stop_the_build(self):
        hull = "rfn_ffg_22350_1-4"
        self.assertIn("the game itself ships", self.refused("wp_em_sovremenny"))
        self.assertIn("common/ras.py", self.refused("rfn_aor_pashin"))
        self.assertIn("stock campaign roster",
                      self.refused(hull, stock_rostered=lambda: {hull}))
        self.assertIn("already extends", self.refused(
            hull, extended_by_mods=lambda: {self.rel(hull): ["3999999999"]}))
        self.assertIn("alias/extend itself", self.refused(
            hull, read=lambda mod, rel: "#!alias vessels/x_variants.ini\n"))
        self.assertIn("no section Soviet", self.refused(
            hull, read=lambda mod, rel: "[General]\n[Default]\nNation=Russia\n[Variant1]\nName=x\n"))
        self.assertIn("no [Default]", self.refused(
            hull, read=lambda mod, rel: "[General]\n[Variant1]\nNation=Soviet\n"))
        self.assertIn("left Soviet", self.refused(hull, left=True))
        self.assertIn("no mod ships", self.refused("sest_no_such_hull"))

    def test_a_section_registered_elsewhere_is_left_out(self):
        text = ("[General]\nNumberOfVariants=3\n[Default]\nNation=Soviet\n[Variant1]\n"
                "Nation=India\n[Variant2]\nName=x\n[Variant3]\nNation=USSR // old key\n")
        hull = "rfn_ffg_22350_1-4"
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(self.b, "OUT", Path(tmp)), \
                mock.patch.dict(self.b.RU_REREGISTER, {hull: "a test hull"}, clear=True), \
                mock.patch.object(self.b, "read", lambda mod, rel: text):
            self.b.build_russian_registrations()
            stub = read(Path(tmp) / "vessels_overwrite" / (hull + self.b.RU_STUB_SUFFIX))
        self.assertEqual(re.findall(r"^\[([^\]\n]+)\]", stub, re.M), ["Default", "Variant2", "Variant3"])
        self.assertIn("Sections registered to India are left as they are.", " ".join(
            x[2:] for x in stub.splitlines() if x.startswith("# ")))

    def test_the_left_soviet_hulls_still_register_soviet(self):
        sys.path.insert(0, str(ROOT / "integration/campaign"))
        import build_pack as bp
        for uid in self.b.RU_LEFT_SOVIET:
            with self.subTest(uid=uid):
                if bp.unit_file(uid)[1] is None:
                    continue              # a hull the export no longer carries
                self.assertEqual(bp.pick_nation(uid, "Default"), "Soviet")

if __name__ == "__main__":
    unittest.main()
