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

Sixteen enemy missiles that a mod left on another weapon's model are drawn
with a model of their own family by one #!extend each in
ammunition_overwrite/ (MISSILE_MODELS, 15 Nov 2026). The stubs ship byte for
byte as the design review checked them, every guard of build_missile_models
stops the build on a fixture, and the KD-88 pair waits for the PC
(MISSILE_MODELS_DEFERRED).

The checks on built files need a build; run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_collection_fixes.py' -v
"""
import contextlib
import copy
import hashlib
import importlib.util
import inspect
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


def headers(text):
    return re.findall(r"^\[([^\]\n]+)\]", text, re.M)


def nation_sections(text):
    """The sections a stub sets Nation=Russia on, in its order."""
    return [h for h in headers(text) if lines(section(text, h)) == ["Nation=Russia"]]


def read_file_to_ini(data, text):
    """IniHandler.ReadFileToIni on one file's text, into `data` (a dict kept
    in insertion order, as the game's Dictionary is with no removals): a
    comment line is skipped, a line is cut at its first ';', '//' or '#', a
    section is added where its header is first seen and a later header for it
    merges into it, a header repeated within one file drops the keys that
    follow, and a key already present keeps its first value (the decompiled
    IL, scratchpad design/redside/iniopen.il and the rev-ru2 dumps of
    ReadFileToIni)."""
    seen, current = [], None
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"^(//|#|;)", line):
            continue
        line = re.split(r";|//|#", line, maxsplit=1)[0].strip()
        m = re.match(r"^\[(.+)\]", line)
        if m:
            name = m.group(1)
            if re.match(r"^[ =\-*]", name) or name in seen:
                current = None
            elif name in data:
                current = data[name]
            else:
                current = data[name] = {}
                seen.append(name)
            continue
        parts = line.split("=")
        if current is None or len(parts) < 2:
            continue
        key = parts[0].strip()
        if key.lower() not in {k.lower() for k in current}:
            current[key] = "=".join(x.strip() for x in parts[1:])
    return data


def offered(data, kind):
    """The game's variant or squadron list, in its order: InitializeSimpleParameters
    keeps [Default] and every Variant<N> (Squadron<N>) with N up to the file's
    NumberOfVariants (NumberOfSquadrons), in the order of getNamesOfAllSections."""
    word, count = ("Squadron", "NumberOfSquadrons") if kind == "aircraft" else (
        "Variant", "NumberOfVariants")
    general = {k.lower(): v for k, v in data.get("General", {}).items()}
    limit = int(re.match(r"\d*", general.get(count.lower(), "")).group() or 0)
    out = []
    for name in data:
        if not (name.startswith(word) or name == "Default"):
            continue
        n = re.search(r"\d+", name)
        if name != "Default" and int(n.group() if n else 0) > limit:
            continue
        out.append(name)
    return out


def resolved_nation(data, name):
    """A section's Nation, else [Default]'s, as the game's VariantInfo reads it."""
    for s in (name, "Default"):
        value = {k.lower(): v for k, v in data.get(s, {}).items()}.get("nation")
        if value:
            return value
    return None


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


PLAN = ROOT / "mods-source/3775128499"
PAKISTAN = ROOT / "mods-source/3812140001"
VANILLA = ROOT / "mods-source/_vanilla/original"
RETIRED_Y8 = "3637954857"
# Named by stock aircraft and defined in no systems/ file: the engine's own
# (tools/check_dependencies.py, upstream_system_names).
ENGINE_SYSTEMS = {"Hardpoint", "WingHardpoint", "BombBay"}


def order_tokens():
    text = read(ROOT / "data/load-order.tokens.txt")
    return [t.strip() for t in text.splitlines() if t.strip() and not t.lstrip().startswith("#")]


def defined_systems():
    """Every systems/ section name the game reads with this load order: the
    game's own, every Workshop mod in the order and the SEST pack."""
    roots = [VANILLA] + [ROOT / "mods-source" / t for t in order_tokens() if t.isdigit()]
    roots.append(DIST if (DIST / "systems").is_dir() else FIXES)
    names = set()
    for root in roots:
        for f in sorted((root / "systems").glob("*.ini")):
            names.update(h.strip() for h in headers(read(f)))
    return names


def mounted_systems(path):
    """SystemName in each sensor, weapon and combat system section of a unit file."""
    text = read(path)
    out = []
    for name in headers(text):
        if re.fullmatch(r"(?:Sensor|Weapon|Combat)System\d+[A-Za-z]*", name.strip()):
            m = re.search(r"(?m)^SystemName\s*=\s*([^\s/#;]+)", section(text, name) or "")
            if m:
                out.append((name.strip(), m.group(1)))
    return out


class RetiredY8Y9Sensors(unittest.TestCase):
    """The Y-8/Y-9 Special Mission Aircraft Family (3637954857) left the
    Workshop and the owner's subscriptions on 12 Nov 2026. It alone defined
    [KQT-8], the MAD the PLAN Pack's own Y-8FQ and Y-9FQ mount (Red Line,
    Global Maritime Operations 2028), and [Morden_RWR], the Pakistani Pack's ZDK-03 RWR
    (Makran Line). Collection Fixes defines both, modelled on the game's own
    sections (MISSING_SENSORS); nothing of the removed mod is used."""

    MODELS = {"KQT-8": "WP_MAD", "Morden_RWR": "AircraftRWR"}

    def test_the_removed_mod_is_gone(self):
        self.assertFalse((ROOT / "mods-source" / RETIRED_Y8).exists())
        self.assertNotIn(RETIRED_Y8, order_tokens())

    def test_the_y8fq_and_y9fq_and_the_zdk03_still_mount_them(self):
        # The day an author points them elsewhere, the entry retires.
        for path, name in ((PLAN / "aircraft/plan_y-8fq.ini", "KQT-8"),
                           (PLAN / "aircraft/plan_y-9fq.ini", "KQT-8"),
                           (PAKISTAN / "aircraft/paf_zdk-03.ini", "Morden_RWR")):
            with self.subTest(unit=path.stem):
                self.assertIn(name, [n for _s, n in mounted_systems(path)])

    def test_no_mod_defines_them(self):
        # build_missing_sensors() stops the build then, rather than shadow it.
        for name in self.MODELS:
            definers = [f.relative_to(ROOT).as_posix()
                        for f in sorted((ROOT / "mods-source").rglob("systems/*.ini"))
                        if section(read(f), name) is not None]
            with self.subTest(sensor=name):
                self.assertEqual(definers, [])

    def test_each_is_the_games_own_section_and_says_why(self):
        built_text = read(FIXES / "systems" / "sensors.ini")
        for name, model in self.MODELS.items():
            with self.subTest(sensor=name):
                donor = section(read(VANILLA / "systems" / "sensors.ini"), model)
                built = section(built_text, name)
                self.assertIsNotNone(donor)
                self.assertIsNotNone(built)
                self.assertEqual(lines(built), lines(donor))
                why = re.search(rf"(?m)^# {re.escape(name)}: (.*)\n# Cloned from \[{re.escape(model)}\] "
                                r"in _vanilla/original\.\n", built_text)
                self.assertIsNotNone(why)
                self.assertIn(RETIRED_Y8, why.group(1))
                self.assertIn("removed from the Workshop", why.group(1))
                self.assertIn("only definer", why.group(1))
        kqt8 = section(built_text, "KQT-8")
        self.assertRegex(kqt8, r"(?m)^Kind=MAD\b")
        self.assertRegex(kqt8, r"(?m)^MaxDetectionRange=1\.0\b")
        self.assertRegex(built_text, r"(?m)^# KQT-8: .*plan_y-8fq and plan_y-9fq.*\[WP_MAD\]")

    def test_the_consolidated_pack_has_them(self):
        for name in self.MODELS:
            with self.subTest(sensor=name):
                built = section(read(FIXES / "systems" / "sensors.ini"), name)
                shipped = section(read(DIST / "systems" / "sensors.ini"), name)
                self.assertIsNotNone(shipped)
                self.assertEqual(lines(shipped), lines(built))

    def test_every_system_the_y8fq_and_y9fq_mount_resolves(self):
        defined = defined_systems()
        stock = {n for f in VANILLA.glob("aircraft/*.ini") for _s, n in mounted_systems(f)}
        self.assertTrue(ENGINE_SYSTEMS & stock)
        for unit in ("plan_y-8fq", "plan_y-9fq"):
            mounts = mounted_systems(PLAN / "aircraft" / f"{unit}.ini")
            self.assertIn(("SensorSystem5", "KQT-8"), mounts)
            for sec, name in mounts:
                with self.subTest(unit=unit, section=sec, system=name):
                    if name in ENGINE_SYSTEMS:
                        self.assertIn(name, stock)
                    else:
                        self.assertIn(name, defined)

    def test_every_system_the_zdk03_mounts_resolves(self):
        defined = defined_systems()
        for sec, name in mounted_systems(PAKISTAN / "aircraft/paf_zdk-03.ini"):
            with self.subTest(section=sec, system=name):
                self.assertTrue(name in ENGINE_SYSTEMS or name in defined)


class SystemsAfter090(unittest.TestCase):
    """Sea Power 0.9.0 (11 Nov 2026) changed ten of the game's combat-system
    profiles and halved the Western MAD. Two mods ship the game's whole
    combatsystems.ini and one its [AN/ASQ-81V2], each as the game had it
    before, so with the collection loaded the old values came back. Collection
    Fixes restates the game's own text over them (STALE_COMBAT_COPIES,
    STALE_VANILLA_SENSORS), as it has done for weapons.ini since 0.8.3. The
    retuned mod CIWS are a different matter: they are still on the ladder of
    0.8.3, and the build says so each time."""

    CHANGED = ("Alleya_2", "BIP_Volna", "CAAIS_64k", "Koren_1134A", "Koren_1134B", "More_U",
               "Planshet_35", "Titanit", "WDS_Mk4_Tartar", "ZKJ-3")

    @classmethod
    def setUpClass(cls):
        cls.build = builder()
        cls.game = read(VANILLA / "systems" / "combatsystems.ini")
        cls.built = read(FIXES / "systems" / "combatsystems.ini")

    def test_the_two_copies_still_hold_the_ten_profiles_at_the_old_values(self):
        # The day both copies say what the game says, the restore is empty by itself.
        for mod in self.build.STALE_COMBAT_COPIES:
            theirs = read(ROOT / "mods-source" / mod / "systems" / "combatsystems.ini")
            stale = [n for n in headers(self.game) if section(theirs, n) is not None
                     and self.build.keyed(section(theirs, n)) != self.build.keyed(section(self.game, n))]
            with self.subTest(mod=mod):
                self.assertEqual(sorted(stale), sorted(self.CHANGED))
        self.assertRegex(section(read(ROOT / "mods-source/3820759806/systems/combatsystems.ini"), "Titanit"),
                         r"(?m)^DatalinkTier=1\b")

    def test_the_built_file_restates_each_as_the_game_has_it(self):
        for name in self.CHANGED:
            with self.subTest(profile=name):
                self.assertEqual(self.build.keyed(section(self.built, name)),
                                 self.build.keyed(section(self.game, name)))
                self.assertRegex(self.built, rf"(?m)^# \[{re.escape(name)}\]: the game's own definition, "
                                             r"restored over the stale copy in 3455404959, 3820759806\.$")
        # The two this pack points hulls at by #!extend: the Ludas' ZKJ-3 and the Peykaap's Titanit.
        self.assertRegex(section(self.built, "ZKJ-3"), r"(?m)^CICSlots=15\b")
        self.assertRegex(section(self.built, "Titanit"), r"(?m)^DatalinkTier=4\b")
        # Nothing else of the game's is restated, and no SEST profile is one of the game's names.
        restated = [n for n in headers(self.built) if not n.startswith("SEST_")]
        self.assertEqual(sorted(restated), sorted(self.CHANGED))
        self.assertEqual(lines(section(read(DIST / "systems" / "combatsystems.ini"), "Titanit")),
                         lines(section(self.built, "Titanit")))

    def test_a_comment_is_not_a_difference_and_a_trailing_banner_is_not_the_sections(self):
        build = self.build
        self.assertEqual(build.keyed("# old note\nReactionTime = Slow // a remark\n\n# ==== Next ====\n"),
                         build.keyed("ReactionTime=Slow\n"))
        self.assertNotEqual(build.keyed("ReactionTime=Slow\n"), build.keyed("ReactionTime=Medium\n"))
        self.assertEqual(build.own_lines("# why\nCICSlots=4\n\n# ==== Royal Navy ====\n# next one\n"),
                         "# why\nCICSlots=4")
        # RLDN_P42 differs from the copies only in the banner that follows it in the game's file.
        self.assertIsNone(section(self.built, "RLDN_P42"))

    def test_a_copy_one_author_edits_stops_the_build(self):
        build = self.build
        defs = {"Titanit": [(37, "3820759806", "[Titanit]", "DatalinkTier=1\n"),
                            (199, "3455404959", "[Titanit]", "DatalinkTier=2\n"),
                            (10**6, "_vanilla", "[Titanit]", "DatalinkTier=4\n")]}
        with contextlib.redirect_stdout(None), self.assertRaises(SystemExit) as stop:
            build.restore_vanilla_sections(defs, build.STALE_COMBAT_COPIES, "combatsystems.ini")
        self.assertIn("no longer agree", str(stop.exception))
        defs["Titanit"][1] = (199, "3455404959", "[Titanit]", "DatalinkTier=1 // as before\n")
        restored, blocks, skipped = build.restore_vanilla_sections(defs, build.STALE_COMBAT_COPIES,
                                                                   "combatsystems.ini")
        self.assertEqual((restored, skipped), (["Titanit"], []))
        self.assertIn("[Titanit]\nDatalinkTier=4\n", blocks[0])
        # A mod that redefines it above the copies keeps it.
        defs["Titanit"].insert(0, (5, "111", "[Titanit]", "DatalinkTier=3\n"))
        self.assertEqual(build.restore_vanilla_sections(defs, build.STALE_COMBAT_COPIES, "combatsystems.ini")[2],
                         ["Titanit (111 wins)"])

    def test_the_western_mad_is_the_games_again(self):
        built = section(read(FIXES / "systems" / "sensors.ini"), "AN/ASQ-81V2")
        game = section(read(VANILLA / "systems" / "sensors.ini"), "AN/ASQ-81V2")
        self.assertEqual(self.build.keyed(built), self.build.keyed(game))
        self.assertRegex(built, r"(?m)^MaxDetectionRange=0\.5\b")
        self.assertRegex(section(read(ROOT / "mods-source/3417801942/systems/sensors.ini"), "AN/ASQ-81V2"),
                         r"(?m)^MaxDetectionRange=1\.0\b")
        self.assertEqual(lines(section(read(DIST / "systems" / "sensors.ini"), "AN/ASQ-81V2")), lines(built))

    def test_the_minimap_settings_are_the_games_again(self):
        # Apex Predators' ui/minimap.ini is the 0.8.7 file; 0.9.0 added one key to the game's.
        game = read(VANILLA / "ui" / "minimap.ini")
        stale = read(ROOT / "mods-source/3416372890/ui/minimap.ini")
        self.assertRegex(game, r"(?m)^SandMaxHeight=8\b")
        self.assertNotIn("SandMaxHeight", stale)
        self.assertEqual([p.parts[-3] for p in sorted((ROOT / "mods-source").glob("*/ui/minimap.ini"))],
                         ["3416372890"])
        built = read(FIXES / "ui" / "minimap.ini")
        self.assertTrue(built.startswith("# SEST Collection Fixes - the game's own ui/minimap.ini, verbatim"))
        self.assertEqual([x for x in built.splitlines() if not x.startswith("# ")], game.splitlines())
        self.assertEqual(read(DIST / "ui" / "minimap.ini"), built)

    def test_the_build_says_the_retuned_ciws_are_on_the_old_ladder(self):
        build = self.build
        notice = build.ciws_ladder_notice()
        self.assertEqual(len(notice), 1)
        for said in ("[MK15] MissileInterceptChance 40 -> 65", "[MK15_Blk1] MissileInterceptChance 50 -> 70",
                     "[AK630] MissileInterceptChance 20 -> 40", "[AK230] MissileInterceptChance 10 -> 20",
                     f"The {len(build.CIWS_RETUNE)} retuned mod CIWS keep the older figures"):
            self.assertIn(said, notice[0])
        # On the ladder the table was written against it says nothing.
        ladder = {name: [(10**6, "_vanilla", f"[{name}]", "".join(f"{k}={v}\n" for k, v in keys.items()))]
                  for name, keys in build.CIWS_LADDER.items()}
        with mock.patch.object(build, "system_definitions", return_value=ladder):
            self.assertEqual(build.ciws_ladder_notice(), [])
        # The shipped comments no longer call a 0.8.3 figure the game's.
        shipped = read(FIXES / "systems" / "weapons.ini")
        self.assertNotIn("0.8.3 definition", shipped)
        self.assertNotIn("vanilla's Block 1 figures (", shipped)
        self.assertIn("the figures vanilla's Block 1 had until 0.9.0", shipped)
        self.assertRegex(section(shipped, "MK15"), r"(?m)^MissileInterceptChance=65\b")
        self.assertRegex(section(shipped, "MK15B"), r"(?m)^MissileInterceptChance=50\b")


class RussianRegistration(unittest.TestCase):
    """The Russian Federation, not the USSR: one #!extend Nation stub per unit
    on its winning variants or squadrons file (the owner's rule of 11 Nov
    2026, widened the same day): the post-1991, Russian-built hulls
    (RU_REREGISTER, every Soviet section), the modern refits and the boats
    launched after 1991 (RU_BY_SECTION, the sections each names) and the
    aircraft of post-1991 Russian types (RU_AIRCRAFT). The readers of the
    stubs are tested in test_russian_registration.py and test_build_pack.py."""

    # The boat or fit each RU_BY_SECTION section names in its winner's
    # language_en/vessel_names.ini. A shift in an author's numbering (a boat
    # inserted) moves every later name and removes no section, so the
    # builder's own guard would not see it; this does.
    BOATS = {
        "ru_cv_kuznetsov": {"Variant2": "Kuznetsov(2016)"},
        "wp_rkr_admiral_nakhimov_refit": {"Default": "Admiral Nakhimov",
                                          "Variant1": "Admiral Nakhimov RKR-080"},
        "wp_rkr_slavaLU": {"Default": "Projekt 1164", "Variant1": "Marshal Ustinov"},
        "wp_rkr_slava_16": {"Default": "Slava-class (2016)", "Variant1": "Slava RKR-103",
                            "Variant2": "Marshal Ustinov", "Variant3": "Chervona Ukrayina"},
        "wp_mrk_nanuchka3_rsa": {"Default": "Nanuchka III-class", "Variant17": "Smerch"},
        "wp_ptg_tarantul_r60": {"Default": "Projekt 12411", "Variant1": "R-60"},
        "wp_bpk_udaloy2": {"Default": "Project 1155.1", "Variant1": "Admiral Chabanenko"},
        "wp_ssn_akula": {"Variant8": "K-328 Leopard", "Variant9": "K-154 Tigr",
                         "Variant11": "K-157 Vepr", "Variant12": "K-419 Kuzbass",
                         "Variant13": "K-335 Gepard", "Variant16": "K-295 Samara",
                         "Variant17": "K-152 Nerpa"},
        "wp_ssgn_oscar2": {"Variant8": "K-266 Orel", "Variant9": "K-186 Omsk",
                           "Variant10": "K-150 Tomsk", "Variant11": "K-141 Kursk"},
        "wp_mpk_grisha_mu": {"Variant24": "МПК-59", "Variant25": "МПК-14"},
        "wp_ssn_sierra2": {"Variant2": "B-336 Pskov"},
        "wp_projekt61m": {"Default": "Projekt 01090", "Variant1": "Smetlivy"},
    }

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
                         (16, 12, 32))
        self.assertEqual(len(self.stubs), 28)
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
                stubbed = nation_sections(stub)
                if wanted is self.b.ALL_SOVIET:
                    self.assertEqual(stubbed, soviet)
                    self.assertIsNone(rest)
                else:
                    self.assertEqual(stubbed, [s for s in soviet if s in wanted])
                    self.assertEqual(sorted(stubbed), sorted(wanted))
                    # Soviet sections left out are explained, and only then.
                    self.assertEqual(bool(rest), stubbed != soviet)
                # Every other header is empty, and the headers are the
                # target's own, in its order, up to the last one registered.
                listed = headers(stub)
                own = [n for n in headers(target) if n != "General"]
                self.assertEqual(listed, own[:own.index(stubbed[-1]) + 1])
                for name in listed:
                    self.assertEqual(lines(section(stub, name)),
                                     ["Nation=Russia"] if name in stubbed else [])

    def test_the_refits_register_their_modern_fit_only(self):
        # The owner named these (11 Nov 2026): only the post-1991 refit
        # registers Russia; the Soviet-era fits stay Soviet.
        kuz = self.stub("vessels", "ru_cv_kuznetsov")
        self.assertEqual(nation_sections(kuz), ["Variant2"])
        self.assertEqual(headers(kuz), ["Default", "Variant1", "Variant2"])
        self.assertIn("Kuznetsov(2016)", read(ROOT / "mods-source/3438479626/language_en/vessel_names.ini"))
        for uid in ("wp_rkr_admiral_nakhimov_refit", "wp_rkr_slavaLU", "wp_mrk_nanuchka3_rsa",
                    "wp_ptg_tarantul_r60", "wp_projekt61m"):
            with self.subTest(uid=uid):
                self.assertIn("[Default]\nNation=Russia", self.stub("vessels", uid))
        slava = nation_sections(self.stub("vessels", "wp_rkr_slava_16"))
        self.assertEqual(slava, ["Default", "Variant1", "Variant2", "Variant3"])
        # Only Smerch had the 2019 refit; her sisters stay as the author has them.
        self.assertEqual(nation_sections(self.stub("vessels", "wp_mrk_nanuchka3_rsa")),
                         ["Default", "Variant17"])
        self.assertEqual(nation_sections(self.stub("vessels", "wp_ssn_sierra2")), ["Variant2"])
        akula = nation_sections(self.stub("vessels", "wp_ssn_akula"))
        self.assertNotIn("Default", akula)
        self.assertIn("Variant13", akula)                      # K-335 Gepard
        self.assertNotIn("Variant1", akula)                    # K-284 Akula (1984)
        self.assertNotIn("Variant14", akula)                   # K-337 Kuguar, never completed
        # K-456 Tver, launched in June 1991, stays Soviet.
        self.assertEqual(nation_sections(self.stub("vessels", "wp_ssgn_oscar2")),
                         ["Variant8", "Variant9", "Variant10", "Variant11"])

    def test_each_by_section_stub_names_the_boats_it_says(self):
        self.assertEqual(sorted(self.BOATS), sorted(self.b.RU_BY_SECTION))
        for uid, (wanted, _why, _rest) in self.b.RU_BY_SECTION.items():
            with self.subTest(uid=uid):
                mod, _path = self.winner(uid)
                names = section(read(ROOT / "mods-source" / mod / "language_en/vessel_names.ini"), uid)
                self.assertIsNotNone(names)
                named = dict(re.findall(r"^(Default|Variant\d+)=(.*?)\s*$", names, re.M))
                self.assertEqual(sorted(wanted), sorted(self.BOATS[uid]))
                for s, boat in self.BOATS[uid].items():
                    self.assertIn(boat, named.get(s, ""), s)
                # No section left out names a boat registered here.
                for s, name in named.items():
                    if s not in wanted:
                        for boat in self.BOATS[uid].values():
                            self.assertNotIn(boat, name, s)

    def test_the_merged_file_keeps_the_authors_order_and_changes_only_nation(self):
        # The game reads the stub before its target into one dictionary and
        # numbers the variants or squadrons it offers by their order there
        # (the Mission Editor saves Variant<place>), so the merged list must
        # be the target's own, and only the registered sections' Nation may
        # change.
        for kind, uid, *_rest in self.b.ru_registrations():
            with self.subTest(uid=uid):
                stub = self.stub(kind, uid)
                target = read(self.winner(uid, kind)[1])
                alone = read_file_to_ini({}, target)
                merged = read_file_to_ini(read_file_to_ini({}, stub), target)
                self.assertEqual(offered(merged, kind), offered(alone, kind))
                registered = nation_sections(stub)
                self.assertTrue(registered)
                for name in offered(alone, kind):
                    expect = "Russia" if name in registered else resolved_nation(alone, name)
                    self.assertEqual(resolved_nation(merged, name), expect, name)
                for name, keys in alone.items():
                    left = {k: v for k, v in merged[name].items() if k.lower() != "nation"}
                    self.assertEqual(left, {k: v for k, v in keys.items() if k.lower() != "nation"},
                                     name)
                    if name not in registered:
                        self.assertEqual(merged[name], keys, name)

    def test_the_replayed_reader_reads_as_the_game(self):
        stub = "#!extend vessels/x_variants.ini\n# a note\n\n[Default]\n\n[Variant2]\nNation=Russia\n"
        target = ("[General]\nNumberOfVariants=2\n[Default]\nNation=Soviet // c\nName=a\n"
                  "[Variant1]\nNation=India\n[Variant2]\nNation=Soviet\nName=b=c\n[Variant3]\n")
        merged = read_file_to_ini(read_file_to_ini({}, stub), target)
        self.assertEqual(list(merged), ["Default", "Variant2", "General", "Variant1", "Variant3"])
        self.assertEqual(merged["Variant2"], {"Nation": "Russia", "Name": "b=c"})
        self.assertEqual(merged["Default"], {"Nation": "Soviet", "Name": "a"})
        # Without Variant1's header the editor's second entry would be Variant2.
        self.assertEqual(offered(merged, "vessels"), ["Default", "Variant2", "Variant1"])
        self.assertEqual(offered(read_file_to_ini({}, target), "vessels"),
                         ["Default", "Variant1", "Variant2"])
        self.assertEqual(read_file_to_ini({}, "[A]\nk=1\n[A]\nk=2\nj=3\n"), {"A": {"k": "1"}})

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
        self.assertIn("names no section", by(()))
        self.assertIn("more than once", self.refused(
            hull, table="RU_BY_SECTION", entry=(("Variant1",), "a refit", "the rest stay Soviet"),
            read=lambda mod, rel: text.replace("[Variant1]\nName=x\n",
                                               "[Variant1]\nName=x\n[Default]\nName=y\n")))
        self.assertIn("drop the reason", self.refused(
            hull, table="RU_BY_SECTION", entry=(("Default", "Variant1"), "a refit", "x"),
            read=lambda mod, rel: text.replace("[Variant3]\nNation=Soviet\n",
                                               "[Variant3]\nNation=India\n")))

    def test_a_section_registered_elsewhere_is_left_out(self):
        text = ("[General]\nNumberOfVariants=3\n[Default]\nNation=Soviet\n[Variant1]\n"
                "Nation=India\n[Variant2]\nName=x\n[Variant3]\nNation=USSR // old key\n")
        stub = self.built("rfn_ffg_22350_1-4", text)
        self.assertEqual(nation_sections(stub), ["Default", "Variant2", "Variant3"])
        # India's Variant1 is listed empty, so the order stays the author's.
        self.assertEqual(headers(stub), ["Default", "Variant1", "Variant2", "Variant3"])
        self.assertEqual(lines(section(stub, "Variant1")), [])
        self.assertIn("Sections registered to India are left as they are.", " ".join(
            x[2:] for x in stub.splitlines() if x.startswith("# ")))

    def test_a_by_section_stub_names_its_sections_in_file_order_and_says_why(self):
        text = ("[General]\nNumberOfVariants=3\n[Default]\nNation=Soviet\n[Variant1]\nName=a\n"
                "[Variant2]\nName=b\n[Variant3]\nNation=Soviet\n")
        stub = self.built("ru_cv_kuznetsov", text, table="RU_BY_SECTION",
                          entry=(("Variant3", "Variant1"), "a refit", "the 1991 fit stays Soviet"))
        self.assertEqual(nation_sections(stub), ["Variant1", "Variant3"])
        self.assertEqual(headers(stub), ["Default", "Variant1", "Variant2", "Variant3"])
        said = " ".join(x[2:] for x in stub.splitlines() if x.startswith("# "))
        self.assertIn("a refit.", said)
        self.assertIn("The 1991 fit stays Soviet.", said)
        self.assertIn("only so the game keeps the author's variant order", said)
        # A stub whose sections run from the file's first needs no empty header.
        stub = self.built("ru_cv_kuznetsov", text, table="RU_BY_SECTION",
                          entry=(("Default", "Variant1"), "a refit", "the rest stay Soviet"))
        self.assertEqual(headers(stub), ["Default", "Variant1"])
        self.assertNotIn("listed empty", stub)

    def test_an_aircraft_stub_names_its_squadrons(self):
        text = ("[General]\nNumberOfSquadrons=3\n[Default]\nNation=Soviet\n[Squadron1]\nNation=Soviet\n"
                "[Squadron2]\nNation=China\n[Squadron3]\nLiveryTexture=x\n")
        stub = self.built("wp_su-57", text, kind="aircraft")
        self.assertEqual(stub.splitlines()[0], "#!extend aircraft/wp_su-57_squadrons.ini")
        self.assertEqual(nation_sections(stub), ["Default", "Squadron1", "Squadron3"])
        self.assertEqual(headers(stub), ["Default", "Squadron1", "Squadron2", "Squadron3"])
        self.assertIn("the author's squadron order", " ".join(
            x[2:] for x in stub.splitlines() if x.startswith("# ")))
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


def consolidator():
    sys.path.insert(0, str(ROOT / "tools"))
    import consolidate_packs
    return consolidate_packs


class EnemyMissileModels(unittest.TestCase):
    """Sixteen enemy rounds a mod left on another weapon's model, drawn with a
    model of their own family by one #!extend each in ammunition_overwrite/
    (MISSILE_MODELS; docs/conflicts-and-load-order.md, 'Enemy missile models,
    15 Nov 2026'). The KD-88 pair waits for a folder check on the PC
    (MISSILE_MODELS_DEFERRED). setUpClass builds them into a temporary folder,
    so every guard in build_missile_models passes on the export as it is."""

    # sha256 of the drafts the design review checked against every donor
    # (14 Nov 2026): the stubs ship byte for byte as reviewed. A deliberate
    # change re-reviews the stub and updates its digest here.
    REVIEWED = {
        "ir_nasir": "6d9301d2dd42d23d3db1497a99538deb9e4c64b3cde626385f45b4054f530e20",
        "pla_hq-10": "f589ab77b565f4720b8633391c69b3f695229d82a1b56d09b66bda83a58c7106",
        "pla_yj-18": "71ff7d009ba34213a4bf923ba7b94c39669625d47b7b5cd1d5b83f3ec6358b5a",
        "pla_yj-83": "b7b552c9163222bb1a6cd6a18f2c1c25cede79e711cf5b21ecc95bd0dfa7e40b",
        "plaaf_aspide-1a": "f2eb97ec5c4926d51375bd8855de05a0a1946711e78f850a41c8d1ecd2d66036",
        "plaaf_yj-83": "9b249e6fcceb79a5640c0b09443413d45d25b5f155e9386983aa0cce14b05e04",
        "plan_hy-1ja": "9578ed4b75c9fc1e66b213ff7d1a18e5e9db0515f2d44195c0fbf802c20290d9",
        "plan_pl-10": "1f767e9c277887b578461dfd65a22bbbb72a895e5e2047e839ab8cdc08346e5d",
        "plan_pl-15": "6c15a4412759c9edd3105bae37c0a71cba0149b0e77eea3917ead8237d859098",
        "usn_rum-139c": "7404ab11dfaf7811538c0fe82bc7762f7c0ed2e4fade8a58bb6936e82f6ff535",
        "wp_9m317ma": "7e89d24350209c1d6204a00538fceccbba6baeb136c9bfc82e5b2da3ea2d7003",
        "wp_as-15": "a653e4043d5ae32e8f6a5e98a51cde7ac642f2b186d5b8eaf8501541df729362",
        "wp_as-15_antiship": "73edc11ed118df8c4bd1c8691978c508d14152fa257325d2646e54c546529912",
        "wp_as-15_antiship_nuclear": "6b96b86df288b1587ca57577910be5e0c43fc90512787013d4ede00095ec14f1",
        "wp_as-15_nuclear": "e0983625e61cd1890c6109fa9b132881ba89afc16ae3f41bd1824f96d72ddba0",
        "wp_ss-n-27a": "7045d996fcadaa4081c543ef4735ea40729a40c3ad8c07a64a6afefbaec41bab",
    }
    # build_aim424's three stubs share the folder.
    AIM424 = ("fury_aim424_SEST.ini", "usn_aim-424_OVWR.ini", "yf23_aim424_internal_SEST.ini")

    @classmethod
    def setUpClass(cls):
        cls.b = builder()
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(cls.b, "OUT", Path(tmp)):
            cls.done = cls.b.build_missile_models()
            cls.built = {p.name: p.read_bytes()
                         for p in sorted((Path(tmp) / "ammunition_overwrite").glob("*"))}

    def stub(self, uid):
        return self.built[f"{uid}_SEST.ini"].decode("utf-8")

    def base(self, uid):
        """The text of the round's winning copy, the file its stub lands on."""
        return read(self.b.layer_index()[f"ammunition/{uid}.ini"][0][1])

    def test_each_stub_is_the_reviewed_draft_byte_for_byte(self):
        self.assertEqual(sorted(self.built), sorted(f"{uid}_SEST.ini" for uid in self.REVIEWED))
        for uid, digest in self.REVIEWED.items():
            with self.subTest(uid=uid):
                self.assertEqual(hashlib.sha256(self.built[f"{uid}_SEST.ini"]).hexdigest(),
                                 digest, self.stub(uid))

    def test_sixteen_ship_and_the_kd88_pair_waits(self):
        self.assertEqual(sorted(self.b.MISSILE_MODELS), sorted(self.REVIEWED))
        self.assertEqual(len(self.done), 16)
        self.assertEqual(sorted(self.b.MISSILE_MODELS_DEFERRED), ["pla_kd-88", "plaaf_kd-88"])
        self.assertNotIn("pla_kd-88_SEST.ini", self.built)
        self.assertFalse((FIXES / "ammunition_overwrite" / "pla_kd-88_SEST.ini").exists())
        # SEST's own plaaf_kd-88 keeps the Exocet until the PC check clears its edit.
        built = FIXES / "ammunition" / "plaaf_kd-88.ini"
        if built.exists():
            self.assertRegex(section(read(built), "Models"), r"(?m)^ResourcesRoot=fr_am-39\s*$")
        self.assertFalse(set(self.b.MISSILE_MODELS) & set(self.b.AIM424_ROUNDS))
        for uid, spec in self.b.MISSILE_MODELS.items():
            with self.subTest(uid=uid):
                self.assertTrue(spec["why"].strip())

    def test_each_stub_reads_as_its_entry_and_nothing_else(self):
        for uid, spec in self.b.MISSILE_MODELS.items():
            with self.subTest(uid=uid):
                text = self.stub(uid)
                self.assertNotIn("\r", text)
                self.assertTrue(text.endswith("\n") and not text.endswith("\n\n"))
                head = text.split("\n[", 1)[0].split("\n")
                self.assertEqual(head[0], f"#!extend ammunition/{uid}.ini")
                self.assertTrue(all(x == "" or x.startswith("# ") for x in head[1:]), head)
                self.assertEqual(self.b.header_directives(text),
                                 [("extend", [f"ammunition/{uid}.ini"])])
                want = {"Models": spec["models"]}
                if spec["particles"]:
                    want["Particles"] = spec["particles"]
                self.assertEqual(headers(text), list(want))
                self.assertEqual(read_file_to_ini({}, text), want)
                self.assertFalse([k for keys in want.values() for k in keys if "scale" in k.lower()])

    def test_the_merged_round_changes_only_model_and_position_keys(self):
        # The game's read: the extend first, then the base; the first value wins.
        for uid, spec in self.b.MISSILE_MODELS.items():
            with self.subTest(uid=uid):
                base = self.base(uid)
                alone = read_file_to_ini({}, base)
                merged = read_file_to_ini(read_file_to_ini({}, self.stub(uid)), base)
                self.assertEqual(sorted(merged), sorted(alone))
                changed = [(s, k) for s in merged for k, v in merged[s].items()
                           if alone.get(s, {}).get(k) != v]
                for s, k in changed:
                    self.assertTrue((s == "Models" and k.startswith("Resources"))
                                    or (s == "Particles" and k.endswith("Position")), (s, k))
                for k, v in spec["models"].items():
                    self.assertEqual(merged["Models"][k], v)

    def test_the_built_pack_is_the_rebuild(self):
        on_disk = {p.name: p.read_bytes() for p in (FIXES / "ammunition_overwrite").glob("*")
                   if p.name in self.built}
        if not on_disk:
            self.skipTest("SEST Collection Fixes not built")
        self.assertEqual(on_disk, self.built)

    def test_the_consolidated_folder_will_hold_nineteen(self):
        # integration/dist is refreshed only by the full rebuild
        # (tools/build_all.py), so this reads what consolidate_packs stages from
        # the per-pack outputs, not dist: the folder's files in every source
        # pack. dist holds these 19 once the rebuild has run.
        if not any((FIXES / "ammunition_overwrite" / n).exists() for n in self.built):
            self.skipTest("SEST Collection Fixes not built")
        cp = consolidator()
        names = sorted({p.name for pack in cp.source_packs()
                        for p in (pack / "ammunition_overwrite").glob("*") if p.is_file()})
        self.assertEqual(names, sorted(self.AIM424 + tuple(self.built)))
        self.assertEqual(len(names), 19)

    def test_neither_builder_deletes_the_others_files(self):
        def names(out):
            return sorted(p.name for p in (out / "ammunition_overwrite").glob("*"))
        for order in (("build_aim424", "build_missile_models"),
                      ("build_missile_models", "build_aim424")):
            with self.subTest(order=order), tempfile.TemporaryDirectory() as tmp, \
                    mock.patch.object(self.b, "OUT", Path(tmp)):
                out = Path(tmp)
                (out / "ammunition_overwrite").mkdir()
                (out / "ammunition_overwrite" / "retired_SEST.ini").write_text("#!extend x\n")
                self.b.clean_ammunition_overwrite()
                self.assertEqual(names(out), [])
                for step in order:
                    getattr(self.b, step)()
                self.assertEqual(names(out), sorted(self.AIM424 + tuple(self.built)))
        # main() empties the folder once, ahead of both builders.
        src = inspect.getsource(self.b.main)
        clean = src.index("clean_ammunition_overwrite()")
        self.assertLess(clean, src.index("build_aim424()"))
        self.assertLess(clean, src.index("build_missile_models()"))
        self.assertEqual(src.count("clean_ammunition_overwrite()"), 1)

    def test_the_credits_name_every_donor(self):
        text = consolidator().credits_text(
            {f"ammunition_overwrite/{n}": b for n, b in self.built.items()})
        self.assertIn("The 16 files in ammunition_overwrite/", text)
        block = text.split("paint) of a round shipped by:\n", 1)[1].split("\n\n", 1)[0]
        credited, current = {}, None
        for line in block.splitlines():
            if line.startswith("      "):
                credited[current] += [x.strip() for x in line.split(",") if x.strip()]
            else:
                m = re.search(r"\(workshop (\d+)\)$", line)
                current = m.group(1) if m else "vanilla"
                self.assertTrue(m or line.strip() == "the game itself (Sea Power)", line)
                credited[current] = []
        want = {}
        for uid, spec in self.b.MISSILE_MODELS.items():
            want.setdefault(spec["donor"][0], []).append(uid)
        self.assertEqual({k: sorted(v) for k, v in credited.items()},
                         {k: sorted(v) for k, v in want.items()})

    def test_the_header_scan_reads_every_line_before_the_first_section(self):
        text = ("// the author's note\n#!Extend Ammunition\\IR_Nasir.ini, ammunition/b.ini\n"
                "#!prepend ammunition/c.ini\n[General]\n#!alias ammunition/d.ini\n")
        self.assertEqual(self.b.header_directives(text), [
            ("extend", ["ammunition/ir_nasir.ini", "ammunition/b.ini"]),
            ("prepend", ["ammunition/c.ini"])])
        self.assertEqual(self.b.model_root({"ResourcesFolder": "Weapons\\PLAN_YJ-8\\",
                                            "ResourcesRoot": "PLAN_YJ-8"}),
                         "weapons/plan_yj-8/plan_yj-8")

    def test_the_template_guard_reads_every_round_of_a_root(self):
        records = self.b.ammunition_records()
        self.assertGreater(len(records), 2000)
        roots = {self.b.model_root(spec["models"]) for spec in self.b.MISSILE_MODELS.values()}
        drawn = {rel for rel, files in records.items()
                 if self.b.model_root({k: v for _p, keys, b in files if b
                                       for k, v in keys.items()}) in roots}
        # The game's own YJ-8 and Red Storm Arsenal's YJ-82s and YJ-83s share
        # the Nasir's root; the TU-160's two Kh-55s share the AS-15s'.
        for rel in ("ammunition/plan_yj-8.ini", "ammunition/plan_yj_82.ini",
                    "ammunition/plan_yj83k.ini", "ammunition/kh-55.ini",
                    "ammunition/kh-55sm.ini", "ammunition/it_aspide_1.ini"):
            self.assertIn(rel, drawn)

    def refused(self, uid="ir_nasir", change=None, spec=None, **patches):
        """build_missile_models() with `uid` the only entry - its own entry, or
        `spec`, after change(entry) - and the builder's names in `patches`
        replaced; asserts nothing was written and returns the SystemExit's text."""
        entry = copy.deepcopy(spec or self.b.MISSILE_MODELS[uid])
        if change:
            change(entry)
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(self.b, "OUT", Path(tmp)), \
                mock.patch.dict(self.b.MISSILE_MODELS, {uid: entry}, clear=True), \
                contextlib.ExitStack() as stack:
            for name, value in patches.items():
                stack.enter_context(mock.patch.object(self.b, name, value))
            with self.assertRaises(SystemExit) as caught:
                self.b.build_missile_models()
            self.assertEqual(list(Path(tmp).rglob("*.ini")), [])
        self.assertIn(uid, str(caught.exception))
        return str(caught.exception)

    def reading(self, mod, rel, edit):
        """read(), with (mod, rel)'s text passed through edit(text)."""
        real = self.b.read

        def fake(m, r):
            text = real(m, r)
            return edit(text) if (m, r) == (mod, rel) else text
        return fake

    def in_models(self, line):
        """An edit that adds `line` to a file's [Models] block."""
        return lambda t: re.sub(r"(?m)^\[Models\][^\n]*\n", lambda m: m.group(0) + line + "\n",
                                t, count=1)

    def test_the_round_guards_stop_the_build(self):
        nasir = ("3413868677", "ammunition/ir_nasir.ini")
        self.assertIn("copy wins now", self.refused(
            change=lambda s: s.update(mod="3999999999")))
        self.assertIn("alias/extend itself", self.refused(read=self.reading(
            *nasir, lambda t: "#!alias ammunition/plan_yj83k.ini\n" + t)))
        # A directive below a comment line is still in the header.
        self.assertIn("alias/extend itself", self.refused(read=self.reading(
            *nasir, lambda t: "# the author's notes\n#!prepend ammunition/x.ini\n" + t)))
        aimed = ROOT / "mods-source/3999999999/ammunition_overwrite/ir_nasir_OVWR.ini"
        real = self.b.header_targets()
        self.assertIn("#!extends it", self.refused(header_targets=lambda: {
            **real, "ammunition/ir_nasir.ini": [("extend", "3999999999", aimed)]}))
        self.assertIn("would inherit", self.refused(read=self.reading(
            *nasir, self.in_models("ResourcesMeshPosition=0,0,0.1"))))
        self.assertIn("NumberOfStages, Stage1Mesh", self.refused(read=self.reading(
            *nasir, self.in_models("NumberOfStages=1\nStage1Mesh=usn_agm-84"))))
        self.assertIn("ResourcesMaterialFolder and the entry does not", self.refused(
            "plaaf_yj-83", change=lambda s: s["models"].pop("ResourcesMaterialFolder")))
        self.assertIn("sets no SustainerEffectPosition", self.refused(
            change=lambda s: s["particles"].update(SustainerEffectPosition="0,0,-0.029")))

    def test_an_author_change_stops_the_build(self):
        nasir = ("3413868677", "ammunition/ir_nasir.ini")
        said = self.refused(read=self.reading(*nasir, lambda t: re.sub(
            r"(?m)^ResourcesMeshSwitchTime=0\.2\b", "ResourcesMeshSwitchTime=0.3", t)))
        self.assertIn("ResourcesMeshSwitchTime=0.3, recorded 0.2", said)
        self.assertIn("'was'", said)
        self.assertIn("ResourcesMeshForDebris=usn_agm-84_d, recorded (not set)", self.refused(
            read=self.reading(*nasir, self.in_models("ResourcesMeshForDebris=usn_agm-84_d"))))
        self.assertIn("BoosterEffectPosition=0,0,0, recorded 0,0,-1", self.refused(
            change=lambda s: s["was"].update(BoosterEffectPosition="0,0,-1")))

    def test_donor_drift_and_a_shadowed_material_stop_the_build(self):
        slower = self.reading("3775128499", "ammunition/plan_yj-18.ini", lambda t: re.sub(
            r"(?m)^ResourcesMeshSwitchTime=2\.9\b", "ResourcesMeshSwitchTime=3.1", t))
        self.assertIn("donor 3775128499's ammunition/plan_yj-18.ini has 3.1",
                      self.refused("pla_yj-18", read=slower))
        moved = self.reading("_vanilla/original", "ammunition/plan_yj-8.ini", lambda t: re.sub(
            r"(?m)^SustainerEffectPosition=0,0,-0\.029\b", "SustainerEffectPosition=0,0,-0.031", t))
        self.assertIn("re-check the nozzle", self.refused(read=moved))
        material = "assets/models/ammunition/yj-18/yj-18_mat.ini"
        real = self.b.layer_index()
        with tempfile.TemporaryDirectory() as tmp:
            other = Path(tmp) / "yj-18_mat.ini"
            other.write_text("[Properties]\n_Color=1,0,0,1\n", encoding="utf-8")
            above = {**real, material: [("3999999999", other)] + real[material]}
            self.assertIn("is shadowed", self.refused("pla_yj-18", layer_index=lambda: above))
            alone = {**real, material: [("3999999999", other)]}
            self.assertIn("the donor 3775128499 ships none",
                          self.refused("pla_yj-18", layer_index=lambda: alone))

    def test_the_nasirs_launch_part_is_checked_against_its_launch_source(self):
        # RSA's plan_yj83k (the material donor) sets no launch part; the
        # Nasir's comes from the game's own plan_yj-8.ini, as vanilla draws it.
        spec = self.b.MISSILE_MODELS["ir_nasir"]
        self.assertEqual(spec["launch"], ("vanilla", "ammunition/plan_yj-8.ini"))
        self.assertEqual(spec["models"]["ResourcesMeshForLaunch"], "wplan_yj-8_dummy")
        self.assertEqual(spec["models"]["ResourcesMeshCanister"], "")
        self.assertNotIn("ResourcesMeshSwitchTime", spec["models"])
        self.assertIn("# Launch part as the game's ammunition/plan_yj-8.ini", self.stub("ir_nasir"))
        vanilla = ("_vanilla/original", "ammunition/plan_yj-8.ini")
        # The launch source moving its dummy stops the build, naming that file.
        renamed = self.reading(*vanilla, lambda t: re.sub(
            r"(?m)^ResourcesMeshForLaunch=wplan_yj-8_dummy\b", "ResourcesMeshForLaunch=other", t))
        self.assertIn("donor vanilla's ammunition/plan_yj-8.ini has other",
                      self.refused(read=renamed))
        # Without the launch source the material donor is asked, and it has none.
        self.assertIn("donor 3413868677's ammunition/plan_yj83k.ini has (not set)",
                      self.refused(change=lambda s: s.pop("launch")))
        # The round's own switch time must be the launch source's.
        slower = self.reading(*vanilla, lambda t: re.sub(
            r"(?m)^ResourcesMeshSwitchTime=0\.2\b", "ResourcesMeshSwitchTime=0.5", t))
        self.assertIn("switches at 0.5, but the round switches at 0.2",
                      self.refused(read=slower))

    def test_the_table_guards_stop_the_build(self):
        self.assertIn("AIM424_ROUNDS", self.refused(
            "usn_aim-424", spec=self.b.MISSILE_MODELS["ir_nasir"]))
        self.assertIn("MISSILE_MODELS_DEFERRED", self.refused(
            "pla_kd-88", spec=self.b.MISSILE_MODELS["ir_nasir"]))
        self.assertIn("no entry may scale its mesh", self.refused(
            change=lambda s: s["models"].update(ResourcesMeshScale="0.6,0.6,0.6")))
        self.assertIn("not a model or effect-position key", self.refused(
            change=lambda s: s["models"].update(AssetBundleMesh="usn_rim-7")))

    def test_a_transform_on_a_shared_root_stops_the_build(self):
        real = self.b.ammunition_records()
        other = ROOT / "mods-source/3999999999/ammunition/sest_test_round.ini"

        def models(text):
            return self.b.game_ini(text)["Models"]
        # Another round, on the Nasir's root spelt another way, turns its mesh.
        turned = models("[Models]\nResourcesFolder=Weapons\\PLAN_YJ-8\\\n"
                        "ResourcesRoot=PLAN_YJ-8\nResourcesMeshRotation=0,0,90\n")
        said = self.refused(ammunition_records=lambda: {
            **real, "ammunition/sest_test_round.ini": [(other, turned, True)]})
        self.assertIn("drawn from weapons/plan_yj-8/plan_yj-8", said)
        self.assertIn("sest_test_round.ini sets ResourcesMeshRotation=0,0,90", said)
        # An extend that scales the game's own YJ-8, whose root comes from its base.
        extend = ROOT / "mods-source/3999999999/ammunition_overwrite/plan_yj-8_OVWR.ini"
        said = self.refused(ammunition_records=lambda: {**real, "ammunition/plan_yj-8.ini": [
            (extend, models("[Models]\nResourcesMeshCanisterScale=1,1,1.2\n"), False)]
            + real["ammunition/plan_yj-8.ini"]})
        self.assertIn("plan_yj-8_OVWR.ini sets ResourcesMeshCanisterScale=1,1,1.2", said)


if __name__ == "__main__":
    unittest.main()
