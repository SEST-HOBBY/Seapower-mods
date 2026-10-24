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

    23 Oct 2026, the owner, in game: the RAN MH-60R's 19-tube pod sat "at the
    bottom of a quad Hellfire rack" (27153767, the M299 launcher's lower rail
    point with the launcher, H60_Pylon114, drawn); hidden, the launcher left
    the pods floating (d9755f4e). Then, on 57375598, which fired the round
    from 19-tube pods on the auxiliary tanks' Stations 1/2: "swap agm for agr,
    no quad rack clipping issue" - tanks back, and the rockets in the
    Hellfires' place on the launcher. The launcher's rail points (upper
    10/11, lower 12/13, two missiles each on TERAGM114) are 0.49 m apart side
    to side and 0.39 m top to bottom: room for a LAU-68 at each, not a LAU-3.
    So the fit is the donor's with a 7-tube pod for each Hellfire, on the
    Hellfire's seat lowered 0.04 m (RedbackM299) for the pod's fatter body."""

    DONORS = {"ran_mh-60r": "AntiShip", "usn_mh-60r": "AntiShipLateLongRange"}
    RAILS = [10, 11, 12, 13]            # the M299's rail points
    SEAT = "0.002461,-0.0004,0|-0.002405,-0.0004,0"

    @staticmethod
    def seat(text, name):
        """A seat's positions, each [x, y, z]."""
        value = re.search(rf"(?m)^{re.escape(name)}Positions=(\S+)", text).group(1)
        return [[float(v) for v in p.split(",")] for p in value.split("|")]

    def test_mh60_fit_is_its_donor_with_a_pod_for_each_hellfire(self):
        pod = (ALLIED / "ammunition" / f"{redback.POD}.ini").read_text(encoding="utf-8")
        tubes = int(re.search(r"(?m)^NumberOfAttachments=(\d+)", pod).group(1))
        for uid, donor in self.DONORS.items():
            with self.subTest(uid=uid):
                text = built(uid)
                blocks = dict(employment.weapon_blocks(text))
                body = blocks["1" + redback.LOADOUT]
                # The donor's body, line for line, with only its four
                # Hellfire lines changed: tanks on 1/2, its hide list and
                # everything else as the author wrote them.
                expected, n = re.subn(
                    r"(?m)^(Station(?:10|11|12|13))=usa_agm-114\w+\|TERAGM114$",
                    rf"\1={redback.POD}|RedbackM299", blocks["1" + donor])
                self.assertEqual(n, len(self.RAILS))
                self.assertEqual(body, expected)
                self.assertEqual(stations(body, "usn_sh60_tank"), [1, 2])
                self.assertEqual(stations(body, redback.POD), self.RAILS)
                # The launcher drawn, the Penguin arm hidden.
                self.assertNotIn("H60_Pylon114", hidden(body))
                self.assertIn("H60_Pylon119", hidden(body))
                # The seat: the Hellfire's, at the same points side to side
                # and fore and aft, 0.04 m lower.
                value = re.search(r"(?m)^RedbackM299Positions=(\S+)$", text).group(1)
                self.assertEqual(value, self.SEAT)
                seat, hellfire = self.seat(text, "RedbackM299"), self.seat(text, "TERAGM114")
                self.assertEqual(len(seat), len(hellfire))
                for mine, its in zip(seat, hellfire):
                    self.assertEqual((mine[0], mine[2]), (its[0], its[2]))
                    self.assertAlmostEqual(its[1] - mine[1], 0.0004)
                # Eight pods, 56 rounds: each station line hangs a pod at
                # each of the seat's positions, seven rounds a pod.
                pods = len(stations(body, redback.POD)) * len(seat)
                self.assertEqual(pods, 8)
                self.assertEqual(pods * tubes, 56)

    def test_no_redbackh60_seat_is_left(self):
        # 57375598's raised tank-point seat for the 19-tube pod, gone on the
        # owner's second report of 23 Oct 2026.
        paths = [ROOT / "integration/allied-fixes/build_patch.py",
                 ROOT / "integration/common/redback.py",
                 *sorted(ROOT.glob("integration/*/SEST_*/aircraft/*.ini"))]
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8", errors="replace")
                self.assertEqual([x for x in text.splitlines() if "RedbackH60" in x], [])

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
    """Invariants of the generated game profile, not flight proof.

    The game rules they rest on are summarised in the comment above the
    round's swaps in integration/allied-fixes/build_patch.py (Sea Power 0.8.7,
    ApplyKinematics=False): the flame is a timer, SustainerAccelerationTime
    from launch; each stage has a speed target - MaxVelocity while the round
    launches and turns onto its bearing, MaxLoftVelocity through the climb
    and the whole cruise, TerminalVelocity from TerminalApproachDist in;
    above its target the speed falls in a straight line at Deceleration x
    19.05 kt/s; and fired from an aircraft the motor works only with
    AccelerationTime=6, the game's default. Nothing about this flight has
    been seen in the game yet (23 Oct 2026)."""

    KT_PER_S = 19.05                    # one unit of Deceleration, kt/s

    def setUp(self):
        self.paths = [ROOT / p / 'ammunition/sest_agr-30.ini' for p in (
            'integration/allied-fixes/SEST_Allied_Fixes',
            'integration/dist/SEST_Integration')]
        self.text = self.paths[0].read_text()

    def number(self, name):
        return float(re.search(rf'^{name}=([0-9.]+)', self.text, re.M).group(1))

    def test_fire_and_forget_needs_no_guidance_channel(self):
        # 23 Oct 2026: radio command (MidCourseCorrection=1) was listed but
        # never launched from a Seahawk, whose hardpoint links no channel;
        # at 0 the RAN MH-60R fired it the same day (57375598).
        self.assertEqual(self.number('MidCourseCorrection'), 0)
        # Kept, as six of the collection's MidCourseCorrection=0 rounds have it.
        self.assertIn('Retargetable=True', self.text)

    def test_the_motor_works_when_an_aircraft_fires_it(self):
        # The simpler speed model, and the game's own AccelerationTime: the
        # 19 Oct 0.01 gave an aircraft-launched round no thrust at all.
        self.assertRegex(self.text, r'(?m)^ApplyKinematics=False\b')
        self.assertEqual(self.number('AccelerationTime'), 6)

    def test_run_up_then_a_steady_slow_down_to_the_cruise(self):
        """23 Oct 2026, the owner: "would like realistic slow down to cruise
        speed". A run-up target above the 150 kt climb-and-cruise target,
        and a straight-line bleed from one to the other that lasts between
        half a minute and two minutes (about a minute as built)."""
        self.assertEqual(self.number('MaxLoftVelocity'), 150)
        self.assertGreater(self.number('MaxVelocity'), self.number('MaxLoftVelocity'))
        bleed = ((self.number('MaxVelocity') - self.number('MaxLoftVelocity'))
                 / (self.number('Deceleration') * self.KT_PER_S))
        self.assertGreaterEqual(bleed, 30)
        self.assertLessEqual(bleed, 120)
        # The pick-up for the terminal approach.
        self.assertGreater(self.number('TerminalVelocity'), self.number('MaxLoftVelocity'))

    def test_the_flame_is_ten_seconds(self):
        self.assertEqual(self.number('SustainerAccelerationTime'), 10)
        self.assertGreater(self.number('SustainerAcceleration'), 0)

    def test_terminal_approach_waits_for_the_climb(self):
        # 23 Oct 2026, the owner, on 57375598: "agr doesnt boost as long
        # anymore". Its TerminalApproachDist=8 put every shot inside 8 NM
        # into terminal approach from launch, which holds the height: no
        # climb. 2 NM, the 19 Oct follow-up's value, leaves the 2 km climb to
        # shots from about 4 NM, and the approach still starts before the
        # dive and inside the seeker's reach.
        self.assertEqual(self.number('TerminalApproachDist'), 2.0)
        self.assertGreater(self.number('TerminalApproachDist'),
                           self.number('TerminalDiveDistance'))
        self.assertLess(self.number('TerminalApproachDist'), self.number('SeekerActiveRange'))
        climb = (self.number('MaxLoftAlt') / 6076.11549
                 / math.tan(math.radians(self.number('MaxLoftAngle'))))
        self.assertLessEqual(self.number('TerminalApproachDist') + climb, 4.0)

    def test_dive_geometry_uses_horizontal_distance_and_is_near_45_degrees(self):
        drop_nm = self.number('MaxLoftAlt') / 6076.11549
        slope = math.degrees(math.atan2(drop_nm, self.number('TerminalDiveDistance')))
        self.assertGreater(slope, 40)
        self.assertLess(slope, 50)
        self.assertIn('IgnoreHeightDifferenceForTargetDist=True', self.text)
        self.assertNotRegex(self.text, r'(?m)^TerminalDiveAngle=', 'unverified game key')

    def test_profile_retains_guidance_target_classes_and_one_timed_flame(self):
        for required in ('TargetType=ASuW', 'SecondaryTargetType=AAW',
                         'LandAttackCapability=All',
                         'TargetMemory=True', 'GuidanceType=3',
                         'TerminalAlt=Maintain',
                         'MinAttackAltitude=0',
                         'Frequency=Ka-Band', 'PeakPower=11.0'):
            self.assertIn(required, self.text)
        self.assertEqual(len(re.findall(r'^SustainerEffect=', self.text, re.M)), 1)
        self.assertNotRegex(self.text, r'(?m)^InFlightEffect(?:Class)?=')

    def test_installed_profile_is_the_generated_source_profile(self):
        self.assertEqual(self.paths[0].read_bytes(), self.paths[1].read_bytes())


if __name__ == "__main__":
    unittest.main()
