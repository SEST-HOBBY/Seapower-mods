#!/usr/bin/env python3
"""SEST Allied Fixes: the P-8 Harpoon's guidance channel (28 Oct 2026).

usn_agm-84n is radio command (MidCourseCorrection=1). Sea Power 0.8.7 will
not launch such a round from a hardpoint that links no sensor, and guides it
in flight only through a linked radar with a weapon channel (the game code
is summarised above P8_GUIDANCE in integration/allied-fixes/build_patch.py).
usn_p8 linked nothing, usn_p8_2027 only a FLIR; both now link a
GPS_Receiver to their wing pylons.
These check the built files, so run them after a build, from the
repository root:
    python3 -m unittest discover -s tools/tests -p 'test_allied_fixes.py' -v
"""
import importlib.util
import re
import sys
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


if __name__ == "__main__":
    unittest.main()
