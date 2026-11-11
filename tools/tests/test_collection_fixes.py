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

The post-1991, Russian-built hulls, the modern refits of Soviet-built ships
and the aircraft of post-1991 Russian types register the game's Russia key
through one #!extend Nation stub each on their winning variants or squadrons
file (RU_REREGISTER, RU_BY_SECTION and RU_AIRCRAFT, the owner's rule of 11
Nov 2026); what the rule leaves Soviet is in RU_LEFT_SOVIET and
RU_AIRCRAFT_LEFT_SOVIET with the reason.

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
    """The Russian Federation, not the USSR: one #!extend Nation stub per unit
    on its winning variants or squadrons file (the owner's rule of 11 Nov
    2026, widened the same day): the post-1991, Russian-built hulls
    (RU_REREGISTER, every Soviet section), the modern refits and the boats
    completed after 1991 (RU_BY_SECTION, the sections each names) and the
    aircraft of post-1991 Russian types (RU_AIRCRAFT). The readers of the
    stubs are tested in test_russian_registration.py and test_build_pack.py."""

    @classmethod
    def setUpClass(cls):
        cls.b = builder()
        cls.stubs = {p.name: p for p in sorted((FIXES / "vessels_overwrite").glob(
            "*" + cls.b.RU_STUB_SUFFIX))}
        cls.air = {p.name: p for p in sorted((FIXES / "aircraft_overwrite").glob(
            "*" + cls.b.RU_AIR_STUB_SUFFIX))}
        if not cls.stubs:
            raise unittest.SkipTest("SEST Collection Fixes not built")

    @staticmethod
    def rel(uid, kind="vessels"):
        return f"{kind}/{uid}_{'squadrons' if kind == 'aircraft' else 'variants'}.ini"

    def winner(self, uid, kind="vessels"):
        mod = self.b.top_provider(self.rel(uid, kind))
        return mod, ROOT / "mods-source" / mod / self.rel(uid, kind)

    def stub(self, kind, uid):
        if kind == "aircraft":
            return read(self.air[uid + self.b.RU_AIR_STUB_SUFFIX])
        return read(self.stubs[uid + self.b.RU_STUB_SUFFIX])

    def soviet(self, text):
        names = [n for n in re.findall(r"^\[([^\]\n]+)\]", text, re.M) if n != "General"]
        default = self.b.section_nation(text, "Default")
        return [n for n in names
                if ((self.b.section_nation(text, n) or default) or "").lower() in ("soviet", "ussr")]

    def test_one_stub_per_registered_unit(self):
        self.assertEqual(sorted(self.stubs), sorted(
            uid + self.b.RU_STUB_SUFFIX for uid in list(self.b.RU_REREGISTER) + list(self.b.RU_BY_SECTION)))
        self.assertEqual(sorted(self.air),
                         sorted(uid + self.b.RU_AIR_STUB_SUFFIX for uid in self.b.RU_AIRCRAFT))
        self.assertEqual((len(self.b.RU_REREGISTER), len(self.b.RU_BY_SECTION), len(self.b.RU_AIRCRAFT)),
                         (16, 10, 32))
        self.assertEqual(len(self.stubs), 26)
        self.assertEqual(len(self.air), 32)

    def test_the_lists_are_apart_and_the_pashin_is_in_none(self):
        hulls = [self.b.RU_REREGISTER, self.b.RU_BY_SECTION, self.b.RU_LEFT_SOVIET]
        for i, a in enumerate(hulls):
            for b in hulls[i + 1:]:
                self.assertFalse(set(a) & set(b))
        self.assertFalse(set(self.b.RU_AIRCRAFT) & set(self.b.RU_AIRCRAFT_LEFT_SOVIET))
        for uid in self.b.RU_LEFT_SOVIET:
            self.assertNotIn(uid + self.b.RU_STUB_SUFFIX, self.stubs)
        for uid in self.b.RU_AIRCRAFT_LEFT_SOVIET:
            self.assertNotIn(uid + self.b.RU_AIR_STUB_SUFFIX, self.air)
        for table in hulls:
            self.assertNotIn("rfn_aor_pashin", table)

    def test_every_listed_uid_names_a_mods_file_as_spelt_on_disk(self):
        # Every list is keyed by the winning file's uid, spelt as the file
        # is: a key in the wrong case names no file on a case-sensitive
        # checkout, so the left-Soviet record would silently cover nothing
        # (wp_rkr_slavaLU, once keyed wp_rkr_slavalu).
        rows = [(u, "vessels") for u in list(self.b.RU_REREGISTER) + list(self.b.RU_BY_SECTION)
                + list(self.b.RU_LEFT_SOVIET)]
        rows += [(u, "aircraft") for u in list(self.b.RU_AIRCRAFT) + list(self.b.RU_AIRCRAFT_LEFT_SOVIET)]
        for uid, kind in rows:
            with self.subTest(uid=uid):
                mod, path = self.winner(uid, kind)
                self.assertNotEqual(mod, "_vanilla/original")
                self.assertIn(path.name, [p.name for p in path.parent.iterdir()])

    def test_each_stub_extends_its_winner(self):
        for kind, uid, *_rest in self.b.ru_registrations():
            with self.subTest(uid=uid):
                text = self.stub(kind, uid)
                self.assertEqual(text.splitlines()[0], f"#!extend {self.rel(uid, kind)}")
                mod, path = self.winner(uid, kind)
                self.assertNotEqual(mod, "_vanilla/original")
                self.assertTrue(path.is_file())
                self.assertFalse(read(path).lstrip().startswith("#!"))
                # No SEST pack ships the file the stub layers onto.
                self.assertEqual([p for p in ROOT.glob(f"integration/*/SEST_*/{self.rel(uid, kind)}")
                                  if "dist" not in p.parts], [])

    def test_each_section_is_a_soviet_one_of_the_winner_and_says_russia(self):
        for kind, uid, wanted, _why, rest in self.b.ru_registrations():
            with self.subTest(uid=uid):
                stub = self.stub(kind, uid)
                target = read(self.winner(uid, kind)[1])
                soviet = self.soviet(target)
                stubbed = re.findall(r"^\[([^\]\n]+)\]", stub, re.M)
                if wanted is self.b.ALL_SOVIET:
                    self.assertEqual(stubbed, soviet)
                    self.assertIsNone(rest)
                else:
                    self.assertEqual(stubbed, [s for s in soviet if s in wanted])
                    self.assertEqual(sorted(stubbed), sorted(wanted))
                    # Soviet sections left out are explained, and only then.
                    self.assertEqual(bool(rest), stubbed != soviet)
                for name in stubbed:
                    self.assertEqual(lines(section(stub, name)), ["Nation=Russia"])

    def test_the_refits_register_their_modern_fit_only(self):
        # The owner named these (11 Nov 2026): only the post-1991 refit
        # registers Russia; the Soviet-era fits stay Soviet.
        kuz = self.stub("vessels", "ru_cv_kuznetsov")
        self.assertEqual(re.findall(r"^\[([^\]\n]+)\]", kuz, re.M), ["Variant2"])
        self.assertIn("Kuznetsov(2016)", read(ROOT / "mods-source/3438479626/language_en/vessel_names.ini"))
        for uid in ("wp_rkr_admiral_nakhimov_refit", "wp_rkr_slavaLU", "wp_mrk_nanuchka3_rsa",
                    "wp_ptg_tarantul_r60"):
            with self.subTest(uid=uid):
                self.assertIn("[Default]\nNation=Russia", self.stub("vessels", uid))
        slava = re.findall(r"^\[([^\]\n]+)\]", self.stub("vessels", "wp_rkr_slava_16"), re.M)
        self.assertEqual(slava, ["Default", "Variant1", "Variant2", "Variant3"])
        akula = re.findall(r"^\[([^\]\n]+)\]", self.stub("vessels", "wp_ssn_akula"), re.M)
        self.assertNotIn("Default", akula)
        self.assertIn("Variant13", akula)                      # K-335 Gepard
        self.assertNotIn("Variant1", akula)                    # K-284 Akula (1984)
        self.assertNotIn("Variant14", akula)                   # K-337 Kuguar, never completed

    def test_the_aircraft_rule_post_1991_types_register_and_cold_war_types_do_not(self):
        for uid in ("wp_su-57", "wp_su-35s", "wp_su-30sm", "wp_su-33", "wp_mig-31bm",
                    "wp_mig-29k_941", "wp_mig-35", "wp_a-50u", "wp_su-24m2", "wp_su-25sm3", "wp_su_47"):
            self.assertIn(uid, self.b.RU_AIRCRAFT)
        for uid in ("wp_su-27", "wp_mig-31", "wp_mig-29a", "wp_mig-29k", "wp_tu-160", "wp_tu-95ms",
                    "wp_il-76md", "wp_il-78", "wp_ka_27PL", "wp_mi-8t", "wp_mi-24p", "wp_su-24sm3",
                    "wp_mig_23am_98"):
            self.assertIn(uid, self.b.RU_AIRCRAFT_LEFT_SOVIET)
        # A squadron registered to another nation keeps it.
        su35 = self.stub("aircraft", "wp_su-35s")
        self.assertNotIn("[Squadron4]", su35)
        self.assertIn("Squadrons registered to China are left as they are.",
                      " ".join(x[2:] for x in su35.splitlines() if x.startswith("# ")))

    def test_every_soviet_registered_aircraft_is_decided(self):
        # Every non-stock aircraft whose winning squadrons file registers a
        # squadron Soviet is either registered or left Soviet with a reason;
        # a new one in a later export fails here until it is decided.
        vanilla = ROOT / "mods-source/_vanilla/original/aircraft"
        rank = self.b.load_rank()
        decided = set(self.b.RU_AIRCRAFT) | set(self.b.RU_AIRCRAFT_LEFT_SOVIET)
        seen, open_ = set(), []
        for mod in sorted(rank, key=rank.get):
            for f in sorted((ROOT / "mods-source" / mod / "aircraft").glob("*_squadrons.ini")):
                uid = f.name[:-len("_squadrons.ini")]
                if uid.lower() in seen:
                    continue
                seen.add(uid.lower())
                if (vanilla / f"{uid}.ini").is_file() or (vanilla / f.name).is_file():
                    continue
                if self.soviet(read(f).replace("\r\n", "\n")) and uid not in decided:
                    open_.append(f"{mod}/{f.name}")
        self.assertEqual(open_, [])

    def test_no_stub_touches_a_stock_unit_or_a_stock_roster(self):
        rostered = self.b.stock_rostered()
        self.assertIn("wp_rkr_kirov", rostered)       # Pacific Strike's enemy roster is read
        for kind, uid, *_rest in self.b.ru_registrations():
            vanilla = ROOT / "mods-source/_vanilla/original" / kind
            table = "squadrons" if kind == "aircraft" else "variants"
            with self.subTest(uid=uid):
                self.assertNotIn(uid.lower(), rostered)
                self.assertFalse((vanilla / f"{uid}.ini").exists())
                self.assertFalse((vanilla / f"{uid}_{table}.ini").exists())

    def test_a_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(self.b, "OUT", Path(tmp)):
            self.b.build_russian_registrations()
            again = {p.name: p.read_bytes()
                     for p in (Path(tmp) / "vessels_overwrite").glob("*" + self.b.RU_STUB_SUFFIX)}
            again_air = {p.name: p.read_bytes()
                         for p in (Path(tmp) / "aircraft_overwrite").glob("*" + self.b.RU_AIR_STUB_SUFFIX)}
        self.assertEqual(again, {n: p.read_bytes() for n, p in self.stubs.items()})
        self.assertEqual(again_air, {n: p.read_bytes() for n, p in self.air.items()})

    def test_the_consolidated_pack_has_them(self):
        for folder, stubs in (("vessels_overwrite", self.stubs), ("aircraft_overwrite", self.air)):
            for name, path in stubs.items():
                with self.subTest(stub=name):
                    self.assertEqual((DIST / folder / name).read_bytes(), path.read_bytes())

    def test_the_mod_manager_text_says_so(self):
        info = read(FIXES / "_info.ini")
        self.assertIn("to the Russian Federation instead of the USSR", info)
        self.assertIn("Cold War aircraft stay Soviet", info)

    def refused(self, uid, kind="vessels", table=None, entry=None, **patches):
        """build_russian_registrations() with one unit in one table, patched;
        the SystemExit's text."""
        table = table or ("RU_AIRCRAFT" if kind == "aircraft" else "RU_REREGISTER")
        if entry is None:
            entry = "a test unit" if table == "RU_REREGISTER" else (self.b.ALL_SOVIET, "a test unit", None)
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(self.b, "OUT", Path(tmp)), \
                mock.patch.dict(self.b.RU_REREGISTER, {}, clear=True), \
                mock.patch.dict(self.b.RU_BY_SECTION, {}, clear=True), \
                mock.patch.dict(self.b.RU_AIRCRAFT, {}, clear=True), \
                contextlib.ExitStack() as stack:
            getattr(self.b, table)[uid] = entry
            for name, value in patches.items():
                if name == "left":
                    left = "RU_AIRCRAFT_LEFT_SOVIET" if kind == "aircraft" else "RU_LEFT_SOVIET"
                    stack.enter_context(mock.patch.dict(getattr(self.b, left), {uid: "x"}))
                else:
                    stack.enter_context(mock.patch.object(self.b, name, value))
            with self.assertRaises(SystemExit) as caught:
                self.b.build_russian_registrations()
        self.assertIn(uid, str(caught.exception))
        return str(caught.exception)

    def built(self, uid, text, kind="vessels", table=None, entry=None):
        """The stub build_russian_registrations() writes for `uid` with its
        winning file read as `text`."""
        table = table or ("RU_AIRCRAFT" if kind == "aircraft" else "RU_REREGISTER")
        if entry is None:
            entry = "a test unit" if table == "RU_REREGISTER" else (self.b.ALL_SOVIET, "a test unit", None)
        folder, suffix = self.b.RU_KINDS[kind][1:]
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(self.b, "OUT", Path(tmp)), \
                mock.patch.dict(self.b.RU_REREGISTER, {}, clear=True), \
                mock.patch.dict(self.b.RU_BY_SECTION, {}, clear=True), \
                mock.patch.dict(self.b.RU_AIRCRAFT, {}, clear=True), \
                mock.patch.object(self.b, "read", lambda mod, rel: text):
            getattr(self.b, table)[uid] = entry
            self.b.build_russian_registrations()
            return read(Path(tmp) / folder / (uid + suffix))

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
        self.assertIn("writes vessels/", self.refused(
            hull, sest_writers=lambda rel: ["SEST_Some_Pack"]))
        # The REDFOR mod's 2017 Nanuchka III ships a variants file and no hull.
        with mock.patch.dict(self.b.RU_LEFT_SOVIET):
            del self.b.RU_LEFT_SOVIET["wp_mrk_nanuchka_3"]
            self.assertIn("never reads", self.refused("wp_mrk_nanuchka_3"))

    def test_the_aircraft_guards_stop_the_build(self):
        su57 = "wp_su-57"
        self.assertIn("the game itself ships", self.refused("wp_su-24m", "aircraft"))
        self.assertIn("left Soviet", self.refused(su57, "aircraft", left=True))
        self.assertIn("stock campaign roster",
                      self.refused(su57, "aircraft", stock_rostered=lambda: {su57}))
        self.assertIn("already extends", self.refused(
            su57, "aircraft", extended_by_mods=lambda: {self.rel(su57, "aircraft"): ["3999999999"]}))
        self.assertIn("writes aircraft/wp_su-57_squadrons.ini itself", self.refused(
            su57, "aircraft", sest_writers=lambda rel: ["SEST_Some_Pack"]))
        self.assertIn("no mod ships", self.refused("sest_no_such_jet", "aircraft"))
        self.assertIn("no section Soviet", self.refused(
            su57, "aircraft", read=lambda mod, rel: "[General]\n[Default]\nNation=China\n[Squadron1]\n"))

    def test_the_by_section_guards_stop_the_build(self):
        text = ("[General]\nNumberOfVariants=2\n[Default]\nNation=Soviet\n[Variant1]\nName=x\n"
                "[Variant2]\nNation=India\n[Variant3]\nNation=Soviet\n")
        hull = "ru_cv_kuznetsov"

        def by(secs, rest="the rest stay Soviet"):
            return self.refused(hull, table="RU_BY_SECTION", entry=(secs, "a refit", rest),
                                read=lambda mod, rel: text)
        self.assertIn("has no [Variant9]", by(("Variant9",)))
        self.assertIn("no longer registers [Variant2] Soviet", by(("Variant2",)))
        self.assertIn("lie past", by(("Variant3",)))
        self.assertIn("neither names them nor says why", by(("Variant1",), None))
        self.assertIn("names a section twice", by(("Variant1", "Variant1")))
        self.assertIn("drop the reason", self.refused(
            hull, table="RU_BY_SECTION", entry=(("Default", "Variant1"), "a refit", "x"),
            read=lambda mod, rel: text.replace("[Variant3]\nNation=Soviet\n",
                                               "[Variant3]\nNation=India\n")))

    def test_a_section_registered_elsewhere_is_left_out(self):
        text = ("[General]\nNumberOfVariants=3\n[Default]\nNation=Soviet\n[Variant1]\n"
                "Nation=India\n[Variant2]\nName=x\n[Variant3]\nNation=USSR // old key\n")
        stub = self.built("rfn_ffg_22350_1-4", text)
        self.assertEqual(re.findall(r"^\[([^\]\n]+)\]", stub, re.M), ["Default", "Variant2", "Variant3"])
        self.assertIn("Sections registered to India are left as they are.", " ".join(
            x[2:] for x in stub.splitlines() if x.startswith("# ")))

    def test_a_by_section_stub_names_its_sections_in_file_order_and_says_why(self):
        text = ("[General]\nNumberOfVariants=3\n[Default]\nNation=Soviet\n[Variant1]\nName=a\n"
                "[Variant2]\nName=b\n[Variant3]\nNation=Soviet\n")
        stub = self.built("ru_cv_kuznetsov", text, table="RU_BY_SECTION",
                          entry=(("Variant3", "Variant1"), "a refit", "the 1991 fit stays Soviet"))
        self.assertEqual(re.findall(r"^\[([^\]\n]+)\]", stub, re.M), ["Variant1", "Variant3"])
        said = " ".join(x[2:] for x in stub.splitlines() if x.startswith("# "))
        self.assertIn("a refit.", said)
        self.assertIn("The 1991 fit stays Soviet.", said)

    def test_an_aircraft_stub_names_its_squadrons(self):
        text = ("[General]\nNumberOfSquadrons=3\n[Default]\nNation=Soviet\n[Squadron1]\nNation=Soviet\n"
                "[Squadron2]\nNation=China\n[Squadron3]\nLiveryTexture=x\n")
        stub = self.built("wp_su-57", text, kind="aircraft")
        self.assertEqual(stub.splitlines()[0], "#!extend aircraft/wp_su-57_squadrons.ini")
        self.assertEqual(re.findall(r"^\[([^\]\n]+)\]", stub, re.M), ["Default", "Squadron1", "Squadron3"])
        self.assertIn("Squadrons registered to China are left as they are.", " ".join(
            x[2:] for x in stub.splitlines() if x.startswith("# ")))

    def test_the_left_soviet_units_still_register_soviet(self):
        # Every section the winner registers Soviet still reads Soviet
        # through the builders' reader (idn_tu-16ks1's [Default] is
        # Indonesia's; its Soviet squadron is Squadron3).
        sys.path.insert(0, str(ROOT / "integration/campaign"))
        import build_pack as bp
        rows = [(u, "vessels") for u in self.b.RU_LEFT_SOVIET]
        rows += [(u, "aircraft") for u in self.b.RU_AIRCRAFT_LEFT_SOVIET]
        for uid, kind in rows:
            with self.subTest(uid=uid):
                if bp.unit_file(uid)[1] is None:
                    continue              # a unit the export no longer carries
                soviet = self.soviet(read(self.winner(uid, kind)[1]).replace("\r\n", "\n"))
                self.assertTrue(soviet)
                self.assertEqual({s: bp.pick_nation(uid, s) for s in soviet},
                                 {s: "Soviet" for s in soviet})

    def test_a_partly_registered_file_keeps_its_other_sections_soviet(self):
        sys.path.insert(0, str(ROOT / "integration/campaign"))
        import build_pack as bp
        for kind, uid, wanted, _why, rest in self.b.ru_registrations():
            if not rest:
                continue
            with self.subTest(uid=uid):
                soviet = self.soviet(read(self.winner(uid, kind)[1]).replace("\r\n", "\n"))
                for s in soviet:
                    self.assertEqual(bp.pick_nation(uid, s), "Russia" if s in wanted else "Soviet", s)


if __name__ == "__main__":
    unittest.main()
