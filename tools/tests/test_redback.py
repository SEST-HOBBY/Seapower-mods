#!/usr/bin/env python3
"""Regression checks for the shared Redback fit recipe and generated flight profile.

Run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_redback.py' -v
"""
import sys
import re
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration"))
sys.path.insert(0, str(ROOT / "tools"))
from common import redback  # noqa: E402
import check_weapon_employment as employment  # noqa: E402

ALLIED = ROOT / "integration/allied-fixes/SEST_Allied_Fixes"


def built(uid):
    return (ALLIED / "aircraft" / f"{uid}.ini").read_text(encoding="utf-8")


def stations(body, store):
    """Station numbers hanging exactly `store` (any seat) in a fit body."""
    return sorted(int(n) for n in re.findall(
        rf"^Station(\d+)={re.escape(store)}(?:\|[^\s]*)?\s*$", body, re.M))


def hidden(body):
    """A fit's SubModelsToHide names, in order."""
    m = re.search(r"^SubModelsToHide=([^\n]*)", body, re.M)
    return [x for x in m.group(1).strip().split(",") if x] if m else []

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


class SeahawkMounts(unittest.TestCase):
    """Each pod hangs from structure the model draws, and not inside a rack.

    23 Oct 2026, the owner, in game: the RAN MH-60R's pod sat "at the bottom
    of a quad Hellfire rack" - the 19 Oct fit hung it on the M299 launcher's
    lower rail point (Stations 12/13) with the launcher (H60_Pylon114) drawn.
    Only H60_Pylon114 or H60_Pylon119 reaches those outboard points; the
    inboard pylon (H60_PylonA) is always drawn and carries the tanks and
    torpedoes in every SH-60 file in the collection."""

    OUTBOARD = (10, 11, 12, 13, 15)     # the M299's rail points and the Penguin's

    def test_mh60_pods_hang_on_the_inboard_pylon_in_the_tanks_place(self):
        for uid in ("ran_mh-60r", "usn_mh-60r"):
            with self.subTest(uid=uid):
                text = built(uid)
                body = fit(text)
                self.assertEqual(stations(body, redback.POD19), [1, 2])
                self.assertEqual(stations(body, redback.POD), [])
                self.assertNotIn("usn_sh60_tank", body)
                # Raised from the tank's point toward the torpedo's on the
                # same rack: the tank is far fatter than the pod, and a bare
                # pod there would hang about 0.1 m clear of the rack (the
                # 19 Oct "pods float" report). Straight up, and not as high
                # as the torpedo's point, since the LAU-3 is the fatter.
                self.assertRegex(body, rf"(?m)^Station1={redback.POD19}\|RedbackH60$")
                self.assertRegex(body, rf"(?m)^Station2={redback.POD19}\|RedbackH60$")
                seat = [float(v) for v in re.search(
                    r"(?m)^RedbackH60Positions=(\S+)", text).group(1).split(",")]
                point = {n: float(re.search(rf"(?m)^Station{n}=[-0-9.]+,([-0-9.]+),", text).group(1))
                         for n in (1, 3)}
                self.assertEqual((seat[0], seat[2]), (0.0, 0.0))
                self.assertGreater(seat[1], 0.0005)
                self.assertLess(seat[1], point[3] - point[1])
                for n in self.OUTBOARD:
                    self.assertNotRegex(body, rf"(?m)^Station{n}=sest_agr-30")
                # The point is the author's: a fit of this airframe already
                # hangs its tanks on Stations 1/2 with these sub-models hidden.
                self.assertNotIn("H60_PylonA", hidden(body))
                donors = [b for name, b in employment.weapon_blocks(text)
                          if name != "1SEST_REDBACK"
                          and stations(b, "usn_sh60_tank") == [1, 2]
                          and hidden(b) == hidden(body)]
                self.assertTrue(donors, "no author fit proves this station and hide pair")

    def test_mh60_hellfires_stay_on_the_drawn_launcher(self):
        for uid in ("ran_mh-60r", "usn_mh-60r"):
            with self.subTest(uid=uid):
                body = fit(built(uid))
                self.assertNotIn("H60_Pylon114", hidden(body))
                self.assertIn("H60_Pylon119", hidden(body))
                self.assertEqual(stations(body, "usa_agm-114l_mm"), [10, 11])
                self.assertEqual(stations(body, "usa_agm-114k_hh"), [12, 13])

    def test_s70_pod_is_the_penguin_sized_7_tube_on_its_station(self):
        # The Penguin hangs between the four Hellfire rails, 0.345 m apart.
        # The 19-tube pod's outer tubes alone sit 0.48 m apart; the 7-tube
        # pod's 0.22 m, inside the Penguin's own envelope. Whether the drawn
        # launcher (AGM-114_Rails) should stay, the loadout preview decides
        # (provisional, 23 Oct 2026): this does not pin it either way.
        for uid in ("ran_S-70B-2_Seahawk", "S-70B-2_Seahawk"):
            with self.subTest(uid=uid):
                text = built(uid)
                body = fit(text)
                self.assertEqual(stations(body, redback.POD), [9])
                self.assertNotIn(redback.POD19, body)
                self.assertNotIn("|MK46", body)

    def test_mq9_pods_hang_under_the_pylon_not_on_the_hellfire_launcher(self):
        for uid in ("usaf_mq-9a", "usaf_mq-9_er"):
            with self.subTest(uid=uid):
                text = built(uid)
                body = fit(text)
                self.assertIn("agm-114_pyl_l", hidden(body))
                self.assertIn("agm-114_pyl_r", hidden(body))
                self.assertNotIn("|AGM-114", body)
                self.assertEqual(stations(body, redback.POD), [1, 2, 3, 4])
                self.assertIn("Station1=" + redback.POD + "|RedbackMQ9\n", body)
                # one pod a side, centred, at the author's Hellfire height
                mount = re.search(r"^RedbackMQ9Positions=([^\n]*)", text, re.M).group(1)
                pair = re.search(r"^AGM-114Positions=([^\n]*)", text, re.M).group(1)
                left, right = ([float(v) for v in p.split(",")] for p in pair.split("|"))
                centre = [round((a + b) / 2, 6) for a, b in zip(left, right)]
                self.assertEqual([float(v) for v in mount.split(",")], centre)


class RedbackCarriers(unittest.TestCase):
    """No SEST_REDBACK carrier needs a guidance channel it lacks.

    Only the channel condition: it says nothing else about launching. A
    radio-command (1) or datalink (3) round needs a guidance channel from a
    sensor the hardpoint links in AssociatedSensors= - the Warramunga NSM's
    lesson in tools/check_weapon_employment.py, which checks ship, submarine
    and land mounts only. On 19 Oct the AGR-30 became radio command, and the
    Seahawks and A-10s link no such sensor: the owner's RAN MH-60R listed it
    against a boat and never fired (23 Oct 2026). A laser designator is not
    a command link, so it does not count here."""

    SEAHAWKS = {"ran_mh-60r", "usn_mh-60r", "S-70B-2_Seahawk", "ran_S-70B-2_Seahawk"}

    @staticmethod
    def round_of(pod):
        text = (ALLIED / "ammunition" / f"{pod}.ini").read_text(encoding="utf-8")
        return re.search(r"^Ammunition=(\S+)", text, re.M).group(1)

    @staticmethod
    def midcourse(round_):
        text = (ALLIED / "ammunition" / f"{round_}.ini").read_text(encoding="utf-8")
        return int(re.search(r"^MidCourseCorrection=(\d+)", text, re.M).group(1))

    def test_every_carrier_can_launch_its_redbacks(self):
        carriers = set()
        for f in sorted(ROOT.glob("integration/*/SEST_*/aircraft/*.ini")):
            if f.parts[-4] == "dist":           # checked through its source packs
                continue
            text = f.read_text(encoding="utf-8")
            if "[WeaponSystem1SEST_REDBACK]" not in text:
                continue
            carriers.add(f.stem)
            body = fit(text)
            base = dict(employment.weapon_blocks(text))["1"]
            kinds = {int(m.group(1)): m.group(2) for m in re.finditer(
                r"^\[SensorSystem(\d+)\][^\n]*\n(?:[^\[][^\n]*\n)*?Type=(\S+)", text, re.M)}
            names = employment.unit_sensors(text)
            links = [i for m in re.finditer(r"^(?:AssociatedSensors|AssociatedSensor\d+)=(.+)$",
                                            base, re.M)
                     for i in map(int, re.findall(r"SensorSystem(\d+)", m.group(1)))]
            channel = [names[i] for i in links if i in names and kinds.get(i) != "LaserDesignator"
                       and employment.channels(names[i]) > 0]
            pods = set(re.findall(r"^Station\d+=(sest_agr-30_pod(?:19)?)(?=[|\s])", body, re.M))
            self.assertTrue(pods, f"{f.stem}: no Redback pod in its fit")
            for pod in sorted(pods):
                round_ = self.round_of(pod)
                with self.subTest(carrier=f.stem, pod=pod):
                    if self.midcourse(round_) in (1, 3):
                        self.assertTrue(channel, f"{f.stem}: {round_} needs a guidance "
                                        "channel and the hardpoint links none")
        self.assertLessEqual(self.SEAHAWKS, carriers)
        self.assertGreaterEqual(len(carriers), 21)


class RedbackProfile(unittest.TestCase):
    """Requirement invariants for the generated game profile, not flight proof."""

    def setUp(self):
        self.paths = [ROOT / p / 'ammunition/sest_agr-30.ini' for p in (
            'integration/allied-fixes/SEST_Allied_Fixes',
            'integration/dist/SEST_Integration')]
        self.text = self.paths[0].read_text()

    def number(self, name):
        return float(re.search(rf'^{name}=([0-9.]+)', self.text, re.M).group(1))

    def test_burn_and_phase_targets_match_the_requested_shape(self):
        self.assertAlmostEqual(self.number('SustainerAccelerationTime'), 10)
        self.assertGreater(self.number('SustainerAcceleration'), 0)
        self.assertLessEqual(140, self.number('MaxVelocity'))
        self.assertLessEqual(self.number('MaxVelocity'), 160)
        self.assertLess(self.number('MaxVelocity'), self.number('TerminalVelocity'))
        self.assertLess(self.number('TerminalVelocity'), self.number('MaxLoftVelocity'))
        self.assertGreater(self.number('Deceleration'), 0)
        self.assertLess(self.number('Deceleration'), 3)  # native legacy default

    def test_dive_geometry_uses_horizontal_distance_and_is_near_45_degrees(self):
        drop_nm = self.number('MaxLoftAlt') / 6076.11549
        slope = math.degrees(math.atan2(drop_nm, self.number('TerminalDiveDistance')))
        self.assertGreater(slope, 40)
        self.assertLess(slope, 50)
        self.assertIn('IgnoreHeightDifferenceForTargetDist=True', self.text)
        self.assertGreater(self.number('TerminalApproachDist'),
                           self.number('TerminalDiveDistance'))
        self.assertNotRegex(self.text, r'(?m)^TerminalDiveAngle=', 'unverified game key')

    def test_profile_retains_guidance_target_classes_and_one_timed_flame(self):
        for required in ('TargetType=ASuW', 'SecondaryTargetType=AAW',
                         'LandAttackCapability=All',
                         'TargetMemory=True', 'GuidanceType=3',
                         'TerminalAlt=Maintain',
                         'ApplyKinematics=False', 'MinAttackAltitude=0',
                         'Frequency=Ka-Band', 'PeakPower=11.0'):
            self.assertIn(required, self.text)
        self.assertEqual(len(re.findall(r'^SustainerEffect=', self.text, re.M)), 1)
        self.assertNotRegex(self.text, r'(?m)^InFlightEffect(?:Class)?=')

    def test_fire_and_forget_needs_no_guidance_channel(self):
        # 23 Oct 2026: radio command (MidCourseCorrection=1) was listed but
        # never launched from a Seahawk, whose hardpoint links no channel.
        self.assertEqual(self.number('MidCourseCorrection'), 0)
        # Kept, as six of the collection's MidCourseCorrection=0 rounds have it.
        self.assertIn('Retargetable=True', self.text)
        # With nothing updating it in flight, the seeker must switch on early
        # enough to find a target that moved, inside its own reach, and
        # before the dive.
        self.assertGreaterEqual(self.number('TerminalApproachDist'), 5)
        self.assertLess(self.number('TerminalApproachDist'), self.number('SeekerActiveRange'))

    def test_installed_profile_is_the_generated_source_profile(self):
        self.assertEqual(self.paths[0].read_bytes(), self.paths[1].read_bytes())


if __name__ == "__main__":
    unittest.main()
