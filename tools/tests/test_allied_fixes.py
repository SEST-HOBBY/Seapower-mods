#!/usr/bin/env python3
"""SEST Allied Fixes: the P-8 Harpoon's guidance channel (28 Oct 2026).

usn_agm-84n is radio command (MidCourseCorrection=1). Sea Power 0.8.7 will
not launch such a round from a hardpoint that links no sensor, and guides it
in flight only through a linked radar with a weapon channel (the game code
is summarised above P8_GUIDANCE in integration/allied-fixes/build_patch.py).
usn_p8 linked nothing, usn_p8_2027 only a FLIR; both now link a
GPS_Receiver to their wing pylons.
Also the RAN S-70B-2's airframe (30 Oct 2026): the author's current file,
on the SH-60 model, with only the Redback fit added (RanSeahawkAirframe).
These check the built files, so run them after a build, from the
repository root:
    python3 -m unittest discover -s tools/tests -p 'test_allied_fixes.py' -v
"""
import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_weapon_employment as employment  # noqa: E402

ALLIED = ROOT / "integration/allied-fixes/SEST_Allied_Fixes"
DIST = ROOT / "integration/dist/SEST_Integration"
UPSTREAM = {"usn_p8": ROOT / "mods-source/3602046770/aircraft/usn_p8.ini",
            "usn_p8_2027": ROOT / "mods-source/3606774881/aircraft/usn_p8_2027.ini"}
GPS = "GPS_Receiver"


def builder():
    spec = importlib.util.spec_from_file_location(
        "allied_fixes_build_patch", ROOT / "integration/allied-fixes/build_patch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def built(uid):
    return (ALLIED / "aircraft" / f"{uid}.ini").read_text(encoding="utf-8")


def upstream(uid):
    # Universal newlines, as the builder reads it: upstream writes CRLF.
    return UPSTREAM[uid].read_text(encoding="utf-8-sig")


def changed_lines(before, after):
    """(lines removed, lines added), as multisets."""
    old, new = Counter(before.splitlines()), Counter(after.splitlines())
    return old - new, new - old


def pylons(text):
    return dict(employment.weapon_blocks(text))["2"]


class P8HarpoonChannel(unittest.TestCase):

    def test_every_radio_command_round_on_the_wing_pylons_has_a_guiding_radar(self):
        # The guiding radar must be a radar (only radars carry Mode=) with a
        # weapon channel: a FLIR's default channel lets the round launch, but
        # the game takes only a radar as its guide.
        defs = employment.sensor_defs()
        for uid in UPSTREAM:
            with self.subTest(uid=uid):
                text = built(uid)
                linked = employment.assoc_names(pylons(text), employment.unit_sensors(text))
                channel = [n for n in linked if (defs.get(n) or {}).get("mode")
                           and employment.channels(n) > 0]
                rounds = set()
                for name, body in employment.weapon_blocks(text):
                    if re.fullmatch(r"2[A-Za-z]\w*", name):
                        rounds |= set(re.findall(r"^Station\d+=([^|\s]+)", body, re.M))
                needy = sorted(r for r in rounds
                               if ((employment.ammo(r) or {}).get("mcc") in (1, 3)))
                # Not vacuous: the AntiShip Harpoons are radio command.
                self.assertIn("usn_agm-84n", needy)
                self.assertEqual(channel, [GPS], f"{uid}: {needy} need a guidance channel")

    def test_the_gps_receiver_is_a_command_channel_that_stays_on(self):
        # The merged sensors.ini, highest mod first, as the game reads it.
        winner = employment.sensor_defs()[GPS]
        self.assertEqual(winner["mode"], "RadioCommand")
        self.assertGreater(employment.channels(GPS), 0)
        # Every copy, whichever mod wins a key: Targeting, so EMCON and the
        # search-radar switches leave it on (see P8_GUIDANCE).
        builder().check_gps_receiver()

    def test_linked_sensors_name_real_sections(self):
        # The game splits AssociatedSensors= on commas without trimming and
        # looks each name up as a section of the unit file.
        for uid in UPSTREAM:
            with self.subTest(uid=uid):
                text = built(uid)
                value = re.search(r"^AssociatedSensors=([^\n]*)$", pylons(text), re.M).group(1)
                for name in value.split(","):
                    self.assertRegex(name, r"^SensorSystem\d+$")
                    self.assertRegex(text, rf"(?m)^\[{name}\]")
                sensors = re.findall(r"^\[SensorSystem(\d+)\]", text, re.M)
                count = int(re.search(r"^NumberOfSensorSystems=(\d+)", text, re.M).group(1))
                self.assertEqual(max(map(int, sensors)), count)

    def test_usn_p8_is_upstream_but_the_typo_and_the_gps(self):
        removed, added = changed_lines(upstream("usn_p8"), built("usn_p8"))
        self.assertEqual(removed, Counter(
            [f"Station{i}=usn_agm-84g" for i in range(1, 5)] + ["NumberOfSensorSystems=5"]))
        self.assertEqual(added, Counter(
            [f"Station{i}=usn_agm-84n" for i in range(1, 5)]
            + ["NumberOfSensorSystems=6", "[SensorSystem6] # Harpoon midcourse provider",
               "Type=Radar", f"SystemName={GPS}", "Mount=Dummy", "MountPosition=0,0,0",
               "ModuleType=Sensor", "", "NumberOfAssociatedSensors=1",
               "AssociatedSensors=SensorSystem6"]))

    def test_usn_p8_2027_is_upstream_but_the_link(self):
        # Shipped again for this alone; its stations have said usn_agm-84n
        # since the 2026-09-20 export.
        removed, added = changed_lines(upstream("usn_p8_2027"), built("usn_p8_2027"))
        self.assertEqual(removed, Counter(["AssociatedSensors=SensorSystem5"]))
        self.assertEqual(added, Counter(["NumberOfAssociatedSensors=2",
                                         "AssociatedSensors=SensorSystem5,SensorSystem6"]))

    def test_the_consolidated_pack_ships_them(self):
        for uid in UPSTREAM:
            with self.subTest(uid=uid):
                self.assertEqual((DIST / "aircraft" / f"{uid}.ini").read_bytes(),
                                 (ALLIED / "aircraft" / f"{uid}.ini").read_bytes())

    def test_usn_p8_2027_is_not_retired(self):
        bp = builder()
        self.assertNotIn("usn_p8_2027.ini", [name for _mod, name, _why in bp.RETIRED])
        self.assertEqual(sorted(bp.P8_GUIDANCE), ["usn_p8.ini", "usn_p8_2027.ini"])


class P8HarpoonChannelGuards(unittest.TestCase):
    """The link is rebuilt from upstream on every build and stops the build,
    rather than guessing, when upstream changes the shape it expects."""

    @classmethod
    def setUpClass(cls):
        cls.bp = builder()
        cls.p8 = upstream("usn_p8").replace("usn_agm-84g", "usn_agm-84n")   # after TARGETS
        cls.p8_2027 = upstream("usn_p8_2027")

    def stops(self, text, name):
        with self.assertRaises(SystemExit) as caught:
            self.bp.link_gps(text, name)
        self.assertIn(name, str(caught.exception))

    def test_it_reproduces_the_built_files(self):
        self.assertEqual(self.bp.link_gps(self.p8, "usn_p8.ini"), built("usn_p8"))
        self.assertEqual(self.bp.link_gps(self.p8_2027, "usn_p8_2027.ini"), built("usn_p8_2027"))

    def test_upstream_adds_a_sensor(self):
        self.stops(self.p8.replace("NumberOfSensorSystems=5", "NumberOfSensorSystems=6"),
                   "usn_p8.ini")

    def test_upstream_adds_its_own_gps(self):
        self.stops(self.p8.replace("SystemName=AN/AAS-44", f"SystemName={GPS}"), "usn_p8.ini")

    def test_upstream_links_the_pylons_itself(self):
        self.stops(self.p8.replace("SystemName=WingHardpoint\n",
                                   "SystemName=WingHardpoint\nAssociatedSensors=SensorSystem5\n"),
                   "usn_p8.ini")
        self.stops(self.p8_2027.replace("AssociatedSensors=SensorSystem5\n",
                                        "AssociatedSensors=SensorSystem5,SensorSystem6\n"),
                   "usn_p8_2027.ini")

    def test_the_sixth_sensor_is_no_longer_the_gps(self):
        self.stops(self.p8_2027.replace(f"SystemName={GPS}", "SystemName=AN/ASQ-999"),
                   "usn_p8_2027.ini")

    def test_the_harpoons_move(self):
        self.stops(self.p8.replace("[WeaponSystem2AntiShip]", "[WeaponSystem1AntiShipX]"),
                   "usn_p8.ini")
        self.stops(self.p8_2027.replace("Station4=usn_agm-84n", "Station4=usn_agm-158c"),
                   "usn_p8_2027.ini")


class GpsReceiverGuards(unittest.TestCase):
    """check_gps_receiver() against a scratch tree: every [GPS_Receiver] copy
    must stay a radio-command Targeting radar with a weapon channel, and no
    copy of the Harpoon (or #!extend stub of it) may write a non-empty
    CompatibleGuidanceSystems= that leaves GPS_Receiver out - the game's
    SensorSystem.CanGuideAmmo returns false then."""

    GPS_COPY = ("[GPS_Receiver] #GPS receiver\n"
                "Kind=Radar\n"
                "Type=Targeting                         // Search or Targeting\n"
                "Mode=RadioCommand\n"
                "WeaponChannels=5000                    // weapons it can guide\n"
                "ModuleType=SmallSensor\n\n"
                "[NextSensor]\nKind=Radar\n")
    HARPOON = ("[General]\nType=Missile\n[Guidance]\nGuidanceType=3\n"
               "MidCourseCorrection=1                  // 1 = Radio Command\n")

    @classmethod
    def setUpClass(cls):
        cls.bp = builder()

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.write("mods-source/3606774881/systems/sensors.ini", self.GPS_COPY)
        self.write("mods-source/3606774881/ammunition/usn_agm-84n.ini", self.HARPOON)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def passes(self):
        self.bp.check_gps_receiver(self.root)

    def stops(self, says):
        with self.assertRaises(SystemExit) as caught:
            self.bp.check_gps_receiver(self.root)
        self.assertIn(says, str(caught.exception))

    def harpoon(self, value, rel="mods-source/3606774881/ammunition/usn_agm-84n.ini",
                head=""):
        self.write(rel, head + self.HARPOON + f"CompatibleGuidanceSystems={value}\n")

    def test_the_scratch_tree_passes(self):
        self.passes()

    # The receiver -----------------------------------------------------------

    def test_a_copy_that_is_a_search_radar_stops(self):
        self.write("mods-source/3606774881/systems/sensors.ini",
                   self.GPS_COPY.replace("Type=Targeting", "Type=Search", 1))
        self.stops("no longer a radio-command channel")

    def test_a_copy_that_illuminates_stops(self):
        self.write("mods-source/3606774881/systems/sensors.ini",
                   self.GPS_COPY.replace("Mode=RadioCommand", "Mode=Illuminate", 1))
        self.stops("no longer a radio-command channel")

    def test_a_copy_with_no_weapon_channel_stops(self):
        self.write("mods-source/3606774881/systems/sensors.ini",
                   self.GPS_COPY.replace("WeaponChannels=5000", "WeaponChannels=0", 1))
        self.stops("no longer a radio-command channel")

    def test_a_copy_that_guides_only_datalink_rounds_stops(self):
        self.write("mods-source/3606774881/systems/sensors.ini",
                   self.GPS_COPY.replace("ModuleType", "DatalinkGuidance=True\nModuleType", 1))
        self.stops("no longer a radio-command channel")

    def test_another_mods_bad_copy_stops(self):
        # The game merges sensors.ini key by key: any mod's copy counts.
        self.write("mods-source/3737267013/systems/sensors.ini",
                   self.GPS_COPY.replace("Kind=Radar", "Kind=Visual", 1))
        self.stops("3737267013")

    def test_a_sest_packs_bad_copy_stops(self):
        self.write("integration/x/SEST_X/systems/sensors.ini",
                   self.GPS_COPY.replace("Type=Targeting", "Type=Search", 1))
        self.stops("SEST_X")

    def test_us_navy_2027_dropping_it_stops(self):
        self.write("mods-source/3606774881/systems/sensors.ini", "[NextSensor]\nKind=Radar\n")
        self.write("mods-source/3737267013/systems/sensors.ini", self.GPS_COPY)
        self.stops("U.S. Navy 2027 no longer defines")

    # The Harpoon ------------------------------------------------------------

    def test_a_list_that_leaves_the_receiver_out_stops(self):
        self.harpoon("GuidancePod,GuidancePodNoAlignment")
        self.stops("does not name GPS_Receiver")

    def test_a_list_that_names_it_passes(self):
        self.harpoon("GuidancePod,GPS_Receiver   // pod or GPS")
        self.passes()

    def test_an_empty_value_passes(self):
        # One empty entry is cleared, and an empty list lets any sensor guide.
        self.harpoon("    // none")
        self.passes()

    def test_a_space_after_the_comma_stops(self):
        # The game splits on commas and does not trim the names.
        self.harpoon("GuidancePod, GPS_Receiver")
        self.stops("does not name GPS_Receiver")

    def test_a_sest_packs_copy_stops(self):
        self.harpoon("GuidancePod", rel="integration/x/SEST_X/ammunition/usn_agm-84n.ini",
                     head="#!extend ammunition/usn_agm-84n.ini\n")
        self.stops("SEST_X")

    def test_an_extend_stub_under_another_name_stops(self):
        self.harpoon("GuidancePod", rel="mods-source/123/ammunition/harpoon_fix.ini",
                     head="#!extend ammunition/usn_agm-84n.ini\n")
        self.stops("harpoon_fix.ini")

    def test_an_extend_line_with_a_trailing_comment_stops(self):
        # The game keeps the comment as part of the path and extends nothing;
        # the guard cuts it, so taking the comment out cannot arm the list.
        for comment in ("; Harpoon fix", "// Harpoon fix", "# Harpoon fix"):
            with self.subTest(comment=comment):
                self.harpoon("GuidancePod", rel="mods-source/123/ammunition/harpoon_fix.ini",
                             head=f"#!extend ammunition/usn_agm-84n.ini   {comment}\n")
                self.stops("harpoon_fix.ini")

    def test_an_extend_line_naming_several_files_stops(self):
        # ScanForModifierFiles splits the line on commas; 15 ammunition stubs in
        # the export name several rounds that way.
        self.harpoon("GuidancePod", rel="mods-source/123/ammunition/harpoon_fix.ini",
                     head="#!extend ammunition/usn_agm-84d.ini, ammunition\\usn_agm-84n.ini\n")
        self.stops("harpoon_fix.ini")

    def test_an_extend_stub_outside_the_ammunition_folder_stops(self):
        # Any .ini in the mod's folder tree: U.S. Navy 2027 keeps its own
        # stubs in ammunition_overwrite/.
        self.harpoon("GuidancePod",
                     rel="mods-source/3606774881/ammunition_overwrite/usn_agm-84n_OVWR.ini",
                     head="#!extend ammunition/usn_agm-84n.ini\n")
        self.stops("usn_agm-84n_OVWR.ini")

    def test_a_copy_whose_alias_base_leaves_the_receiver_out_stops(self):
        # ReadFileToIni reads an #!alias base's keys after the copy's own, so a
        # copy that writes no list takes its base's.
        self.write("mods-source/3606774881/ammunition/usn_agm-84n.ini",
                   "#!alias ammunition/usn_agm-84d.ini\n" + self.HARPOON)
        self.write("mods-source/999/ammunition/usn_agm-84d.ini",
                   "[Guidance]\nCompatibleGuidanceSystems=GuidancePod   // pods only\n")
        self.stops("#!alias base of mods-source/3606774881/ammunition/usn_agm-84n.ini")

    def test_an_alias_base_in_the_stock_game_stops(self):
        self.write("mods-source/3606774881/ammunition/usn_agm-84n.ini",
                   "#!alias ammunition/usn_agm-84d.ini\n" + self.HARPOON)
        self.write("mods-source/_vanilla/original/ammunition/usn_agm-84d.ini",
                   "[Guidance]\nCompatibleGuidanceSystems=GuidancePod\n")
        self.stops("_vanilla")

    def test_an_alias_chain_is_followed(self):
        self.write("mods-source/3606774881/ammunition/usn_agm-84n.ini",
                   "#!alias ammunition/harpoon_mid.ini\n" + self.HARPOON)
        self.write("mods-source/999/ammunition/harpoon_mid.ini",
                   "#!alias ammunition/harpoon_base.ini\n[General]\nType=Missile\n")
        self.write("mods-source/999/ammunition/harpoon_base.ini",
                   "[Guidance]\nCompatibleGuidanceSystems=GuidancePod\n")
        self.stops("harpoon_base.ini")

    def test_an_extend_stubs_alias_base_is_followed(self):
        self.write("mods-source/123/ammunition/harpoon_fix.ini",
                   "#!extend ammunition/usn_agm-84n.ini\n#!alias ammunition/pods.ini\n"
                   "[General]\nType=Missile\n")
        self.write("mods-source/123/ammunition/pods.ini",
                   "[Guidance]\nCompatibleGuidanceSystems=GuidancePod\n")
        self.stops("pods.ini")

    def test_a_copy_source_that_leaves_the_receiver_out_stops(self):
        # IniHandler.open reads a file's #!copy sources after its own keys, and
        # a key already read is kept: a copy with no list takes its source's.
        self.write("mods-source/3606774881/ammunition/usn_agm-84n.ini",
                   "#!copy ammunition/usn_agm-84d.ini\n" + self.HARPOON)
        self.write("mods-source/999/ammunition/usn_agm-84d.ini",
                   "[Guidance]\nCompatibleGuidanceSystems=GuidancePod\n")
        self.stops("#!copy source of mods-source/3606774881/ammunition/usn_agm-84n.ini")

    def test_a_copy_sources_own_copy_is_followed(self):
        # CollectCopyFiles adds each source's own #!copy lines, read without case.
        self.write("mods-source/3606774881/ammunition/usn_agm-84n.ini",
                   "#!COPY ammunition/harpoon_mid.ini\n" + self.HARPOON)
        self.write("mods-source/999/ammunition/harpoon_mid.ini",
                   "#!copy ammunition\\harpoon_base.ini   ; pods\n[General]\nType=Missile\n")
        self.write("mods-source/999/ammunition/harpoon_base.ini",
                   "[Guidance]\nCompatibleGuidanceSystems=GuidancePod\n")
        self.stops("harpoon_base.ini")

    def test_a_prepend_stub_stops(self):
        # ScanForModifierFiles reads #!prepend as it reads #!extend, and open()
        # reads the stub's keys before the Harpoon's #!alias base.
        self.harpoon("GuidancePod", rel="mods-source/123/ammunition/harpoon_pre.ini",
                     head="#!prepend ammunition/usn_agm-84n.ini\n")
        self.stops("harpoon_pre.ini")

    def test_a_copy_that_writes_its_own_list_is_not_held_to_its_base(self):
        # Its own [Guidance] value wins over the base's.
        self.write("mods-source/3606774881/ammunition/usn_agm-84n.ini",
                   "#!alias ammunition/usn_agm-84d.ini\n" + self.HARPOON
                   + "CompatibleGuidanceSystems=GPS_Receiver\n")
        self.write("mods-source/999/ammunition/usn_agm-84d.ini",
                   "[Guidance]\nCompatibleGuidanceSystems=GuidancePod\n")
        self.passes()

    def test_another_rounds_list_is_not_its_business(self):
        self.write("mods-source/123/ammunition/usn_gbu-12.ini",
                   "[Guidance]\nCompatibleGuidanceSystems=GuidancePod\n")
        self.passes()

    def test_no_harpoon_at_all_stops(self):
        (self.root / "mods-source/3606774881/ammunition/usn_agm-84n.ini").unlink()
        self.stops("nothing defines ammunition/usn_agm-84n.ini")


class RanSeahawkAirframe(unittest.TestCase):
    """SEST's RAN S-70B-2 is Euromod RAN's current airframe (28 Oct 2026).

    The author rebuilt ran_S-70B-2_Seahawk on US Naval Aviation's SH-60 model
    and pointed its squadron table, which SEST does not ship, at the RAN
    MH-60R's liveries for that model. SEST ships the airframe for its
    SEST_REDBACK fit alone, so a copy of the old airframe beside the new
    table would wear liveries painted for another model. The pack's file is
    the author's, line for line, with the fit added and, since 4 Nov 2026,
    the AN/AAQ-16's night vision level written out (RedbackCarriersAtNight):
    no key of the old model survives."""

    UID = "ran_S-70B-2_Seahawk"
    UPSTREAM = ROOT / "mods-source/3820759806/aircraft/ran_S-70B-2_Seahawk.ini"

    def test_it_is_the_authors_file_with_the_redback_fit(self):
        upstream = self.UPSTREAM.read_text(encoding="utf-8-sig")
        text = built(self.UID)
        removed, added = changed_lines(upstream, text)
        loadouts = re.search(r"^AvailableLoadouts=[^\n]*", upstream, re.M).group(0)
        self.assertEqual(removed, Counter([loadouts]))
        fit = dict(employment.weapon_blocks(text))["1SEST_REDBACK"]
        night = [line for line in text.splitlines() if line.startswith("NightVisionLevel=")]
        self.assertEqual(len(night), 1, night)
        self.assertEqual(added, Counter([loadouts + ",SEST_REDBACK", "[WeaponSystem1SEST_REDBACK]"]
                                        + fit.splitlines() + night))

    def test_none_of_the_old_airframe_is_left(self):
        # The old file's own mesh and tandem-rotor animation, its Penguin on
        # Station9, its Hellfire rails and the fit the author dropped.
        text = built(self.UID)
        for stale in ("S-70B-2_Seahawk.obj", "aircraft/ran_S-70B-2_Seahawk/",
                      "animations_S-70B-2_Seahawk", "knm_penguin_mk2", "AGM-114_Rails",
                      "ASWHunterLight"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)
        self.assertRegex(text, r"(?m)^ResourcesFolder=assets/models/aircraft/sh60/$")
        self.assertRegex(text, r"(?m)^AnimationFile_1=animations_usn_sh60$")
        self.assertRegex(text, r"(?m)^RotorConfiguration=SingleMain\b")

    def test_the_consolidated_pack_ships_it(self):
        self.assertEqual((DIST / "aircraft" / f"{self.UID}.ini").read_bytes(),
                         (ALLIED / "aircraft" / f"{self.UID}.ini").read_bytes())


if __name__ == "__main__":
    unittest.main()


class RedbackCarriersAtNight(unittest.TestCase):
    """The AGR-30 keeps AAW as its secondary target type (counter-drone), so
    the game's weapon panel treats it as an air-to-air round and warns "No
    radar or night vision: this aircraft cannot find air targets at night"
    unless the carrier passes SensorUtils.HasNightCapableSensors(unit, true):
    an Infrared sensor, a Visual sensor whose NightVisionLevel is above 0, or a
    radar whose Role covers air targets. A Visual sensor's level is the merged
    sensors.ini value unless the unit's own section carries the key (both
    builds). The builder writes it into the Redback carriers' unit files
    (build_patch.NIGHT_VISION), each the value of the top-most mod that defines
    it in the canonical load order, so the stable game sees no change."""
    LOAD_ORDER = DIST / "LOAD-ORDER.txt"
    AIR_ROLES = {"Air", "AirAndSurface"}

    @classmethod
    def setUpClass(cls):
        cls.build = builder()
        cls.position = {}
        for line in cls.LOAD_ORDER.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*(\d+)\.\s+(\d{8,})\b", line)
            if m:
                cls.position[m[2]] = int(m[1])
        cls.carriers = sorted(p for p in (ALLIED / "aircraft").glob("*.ini")
                              if "sest_agr-30" in p.read_text(encoding="utf-8"))

    @staticmethod
    def sensors(text):
        """[(section, type, system name, explicit night vision level or None)]."""
        out = []
        for m in re.finditer(r"^\[(SensorSystem\d+)\][^\n]*\n", text, re.M):
            nxt = re.compile(r"^\[", re.M).search(text, m.end())
            body = text[m.end():nxt.start() if nxt else len(text)]
            values = lambda key: (lambda v: v[-1] if v else None)(
                re.findall(rf"^{key}=([^\n]*)", body, re.M))
            cut = lambda v: None if v is None else re.split(r";|//|#", v)[0].strip()
            out.append((m[1], cut(values("Type")), cut(values("SystemName")),
                        cut(values("NightVisionLevel"))))
        return out

    def definitions(self, system, key):
        """[(position, mod, value)] over every exported mod's systems/sensors.ini
        that defines [system] with `key`; vanilla sits below every mod."""
        found = []
        for ini in sorted((ROOT / "mods-source").glob("*/systems/sensors.ini")):
            mod = ini.parts[-3]
            text = ini.read_text(encoding="utf-8-sig", errors="replace")
            m = re.search(rf"^\[{re.escape(system)}\][^\n]*\n", text, re.M)
            if not m:
                continue
            nxt = re.compile(r"^\[", re.M).search(text, m.end())
            body = text[m.end():nxt.start() if nxt else len(text)]
            values = re.findall(rf"^{key}=([^\n]*)", body, re.M)
            if not values:
                continue
            value = re.split(r";|//|#", values[-1])[0].strip()
            pos = 10 ** 6 if mod == "_vanilla" else self.position.get(mod)
            if pos is None:
                continue  # exported but not in the canonical order: never merged
            found.append((pos, mod, value))
        return sorted(found)

    def test_every_redback_carrier_passes_the_night_check_without_the_merge(self):
        self.assertTrue(self.carriers)
        for path in self.carriers:
            capable = []
            for section, kind, name, level in self.sensors(path.read_text(encoding="utf-8")):
                if kind == "Infrared":
                    capable.append(f"{section} {name} is Infrared")
                elif kind == "Visual" and level and float(level) > 0:
                    capable.append(f"{section} {name} NightVisionLevel={level}")
                elif kind == "Radar":
                    roles = self.definitions(name, "Role")
                    if roles and roles[0][2] in self.AIR_ROLES:
                        capable.append(f"{section} {name} Role={roles[0][2]} ({roles[0][1]})")
            self.assertTrue(capable, f"{path.name}: no night-capable sensor of its own; "
                                     f"sensors: {self.sensors(path.read_text(encoding='utf-8'))}")

    def test_the_explicit_levels_are_the_top_most_definitions(self):
        for fname, entries in self.build.NIGHT_VISION.items():
            text = (ALLIED / "aircraft" / fname).read_text(encoding="utf-8")
            explicit = {name: level for _, kind, name, level in self.sensors(text) if level}
            for system, level, mod in entries:
                defined = self.definitions(system, "NightVisionLevel")
                self.assertTrue(defined, f"{fname}: nothing defines [{system}] NightVisionLevel")
                self.assertEqual(defined[0][1], mod,
                                 f"{fname}: [{system}] is set highest by {defined[0]}, not {mod}: {defined}")
                self.assertEqual(float(defined[0][2]), float(level), f"{fname}: [{system}] {defined[0]}")
                self.assertEqual(explicit.get(system), level, f"{fname}: {explicit}")

    def test_the_consolidated_pack_ships_the_levels(self):
        for fname in self.build.NIGHT_VISION:
            self.assertEqual((DIST / "aircraft" / fname).read_text(encoding="utf-8"),
                             (ALLIED / "aircraft" / fname).read_text(encoding="utf-8"), fname)

    SYNTHETIC = ("[SensorSystem1] #FLIR\nType=Visual\nSystemName=3rd_Gen_FLIR\nMount=Dummy\n\n"
                 "[SensorSystem2]\nType=Radar\nSystemName=APS-147\n\n[WeaponSystems]\n")

    def test_the_builder_writes_the_level_after_the_system_name(self):
        out = self.build.set_night_vision(self.SYNTHETIC, "x.ini", [("3rd_Gen_FLIR", "0.85", "3775128499")])
        self.assertIn("SystemName=3rd_Gen_FLIR\nNightVisionLevel=0.85   // SEST: 3775128499's value", out)
        self.assertEqual(out.replace("NightVisionLevel=0.85   // SEST: 3775128499's value, explicit so "
                                     "the AGR-30's night check holds whatever sensors.ini wins\n", ""),
                         self.SYNTHETIC)

    def stops(self, text, entries):
        with self.assertRaises(SystemExit) as cm:
            self.build.set_night_vision(text, "x.ini", entries)
        return str(cm.exception)

    def test_a_section_that_already_sets_the_level_stops(self):
        why = self.stops(self.SYNTHETIC.replace("Mount=Dummy", "NightVisionLevel=1"),
                         [("3rd_Gen_FLIR", "0.85", "3775128499")])
        self.assertIn("already sets NightVisionLevel", why)

    def test_a_missing_sensor_stops(self):
        self.assertIn("no [SensorSystemN] names", self.stops(self.SYNTHETIC, [("AN/AAQ-16", "0.7", "3820759806")]))

    def test_a_radar_stops(self):
        self.assertIn("not Type=Visual", self.stops(self.SYNTHETIC, [("APS-147", "0.85", "3775128499")]))

    def test_a_moved_definition_stops(self):
        self.assertIn("sensors.ini changed", self.stops(self.SYNTHETIC, [("3rd_Gen_FLIR", "0.5", "3775128499")]))
