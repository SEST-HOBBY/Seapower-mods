#!/usr/bin/env python3
"""Tests for the builder rules no shipped mission exercises.

The pack build and tools/check_campaign_coverage.py prove Southern Watch and
Southern Reach as built. They cannot prove a rule neither campaign uses, and
every case here is one of those: a spec key a third campaign must set, a
victory term that used to compile silently into a different condition, a
predicate or a gate a mission played from the other side needs. Each test
builds the smallest mission that shows the rule and reads the lines the
builder emits. Nothing is written into the tree.

    python3 integration/campaign/test_build_pack.py
"""
import contextlib
import importlib.abc
import io
import re
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import build_pack as bp  # noqa: E402
import check_campaign_coverage as coverage_check  # noqa: E402
from campaign_data import F, S, U  # noqa: E402
try:
    import make_art  # noqa: E402
except ImportError:          # Pillow missing: the art tests are skipped
    make_art = None

_ABSENT = object()


# --- a small mission, rendered ----------------------------------------------
# The ceasefire-morning shape from the Red Line design: a frigate, a carrier
# withdrawing, an armed coaster in company that has turned for the convoy
# lane, a Poseidon overhead. Positions are in the mission's NM frame and are
# written straight into `placed`, so render() runs without the proven-point
# pool or the coastline.

def _keys(uid, x, z, **extra):
    return dict(Type=uid, RelativePositionInNM=f"{x},0,{z}", **extra)


def small_mission(**over):
    m = dict(
        key="Test Withdrawal", code="T01", num="01", group="core",
        brief="Brief.", win="Won.", lose="Lost.", timeout="Out of time.",
        date=(2028, 11, 28), time=(5, 10), sea=2, clouds="Clear", wind="E",
        centre=(-4.6, 128.9), blue_nation="China", red_nation="Australia",
        minutes=80, role="escort",
        stations={"escort": S(-4.45, 128.85, "Escort"),
                  "group": S(-4.50, 128.70, "Carrier group"),
                  "spoiler": S(-4.62, 128.90, "Armed coaster"),
                  "red_air": S(-4.00, 129.40, "Poseidon", alt=14000)},
        objectives=[("Withdrawal", "Withdraw north-west", "35,-35,Fail,Main"),
                    ("Spoiler", "Stop the coaster", "20,-40,Fail")],
        victory=dict(kind="arrive", station="group", at=(-4.30, 128.60),
                     radius=12, objective="Withdrawal"),
        resolve={"Withdrawal": "victory", "Spoiler": ("destroy", "spoiler", 1)},
        units=[])
    m.update(over)
    return m


def small_placement():
    placed = {
        "Taskforce1Vessel": [
            ("Taskforce1Vessel1", _keys("plan_type_054a_p5", 0, 9), None, False),
            ("Taskforce1Vessel2", _keys("plan_type_001", -12, 6), "Liaoning", False)],
        "Taskforce2Vessel": [
            ("Taskforce2Vessel1", _keys("ran_ms_super_p", 0, -1), "MV Meridian Harmony", False)],
        "Taskforce2Aircraft": [
            ("Taskforce2Aircraft1", _keys("usn_p8", 30, 36), None, False)],
    }
    members = {"escort": ["Taskforce1Vessel1"], "group": ["Taskforce1Vessel2"],
               "spoiler": ["Taskforce2Vessel1"], "red_air": ["Taskforce2Aircraft1"]}
    return placed, members


def rendered(mission, placed=None, members=None):
    """render() -> {trigger name: [lines]}, after the pack checker's own
    trigger-integrity pass has read the whole file."""
    if placed is None:
        placed, members = small_placement()
    _name, text = bp.render(mission, placed, members)
    parsed = coverage_check.blocks(text)
    problems = coverage_check.trigger_integrity(HERE / "test.ini", text, parsed)
    if problems:
        raise AssertionError("\n".join(problems))
    triggers = {}
    for line in text.split("\n\n"):
        rows = line.strip().splitlines()
        if rows and rows[0].startswith("[Trigger"):
            triggers[rows[1].partition("=")[2]] = rows[2:]
    return triggers


class _BrokenRedLine(importlib.abc.MetaPathFinder):
    """A red_line package whose own import fails on a missing dependency."""

    def find_spec(self, name, path, target=None):
        if name == "red_line":
            raise ModuleNotFoundError("No module named 'red_line_dependency'",
                                      name="red_line_dependency")
        return None


class CampaignRegistry(unittest.TestCase):
    """A third campaign is registered by its package being in the tree."""

    def setUp(self):
        self.saved = sys.modules.get("red_line", _ABSENT)

    def tearDown(self):
        if self.saved is _ABSENT:
            sys.modules.pop("red_line", None)
        else:
            sys.modules["red_line"] = self.saved

    @staticmethod
    def fake_red_line(**spec):
        mod = types.ModuleType("red_line")
        mod.__file__ = str(HERE / "red_line" / "__init__.py")
        mod.CAMPAIGN = dict(dict(
            SLUG="sest-red-line", TITLE="Red Line",
            DOCS_DIR=bp.ROOT / "docs" / "campaigns" / "red-line",
            COVERAGE_DOC=bp.ROOT / "docs" / "campaigns" / "red-line" / "coverage.md",
            INFO_DESC="", EXCUSES={}), **spec)
        return mod

    def test_absent_package_builds_the_two_campaigns(self):
        sys.modules["red_line"] = None          # import raises, named red_line
        self.assertEqual([s["SLUG"] for s in bp.campaign_specs()],
                         ["sest-southern-watch", "sest-southern-reach"])

    def test_present_package_is_appended_last(self):
        sys.modules["red_line"] = self.fake_red_line()
        self.assertEqual([s["SLUG"] for s in bp.campaign_specs()],
                         ["sest-southern-watch", "sest-southern-reach", "sest-red-line"])

    def test_a_folder_holding_only_pycache_counts_as_absent(self):
        sys.modules["red_line"] = types.ModuleType("red_line")   # no __file__
        self.assertEqual(len(bp.campaign_specs()), 2)

    def test_a_package_that_fails_to_import_stops_the_build(self):
        sys.modules.pop("red_line", None)
        finder = _BrokenRedLine()
        sys.meta_path.insert(0, finder)
        try:
            with self.assertRaises(ModuleNotFoundError) as caught:
                bp.campaign_specs()
            self.assertEqual(caught.exception.name, "red_line_dependency")
        finally:
            sys.meta_path.remove(finder)

    def test_every_campaigns_excuses_count_for_the_pack(self):
        sys.modules["red_line"] = self.fake_red_line(
            EXCUSES={"red-line-only-mod": ("library", "a reason")})
        merged = bp.pack_excuses(bp.campaign_specs())
        self.assertIn("red-line-only-mod", merged)
        self.assertIn("anchor-chain", merged)     # Southern Watch's own

    def test_two_campaigns_may_not_share_a_report(self):
        reach = bp.ROOT / "docs" / "campaigns" / "southern-reach" / "coverage.md"
        sys.modules["red_line"] = self.fake_red_line(COVERAGE_DOC=reach)
        with self.assertRaisesRegex(SystemExit, "Southern Reach and Red Line both set COVERAGE_DOC"):
            bp.campaign_specs()


class CampaignFiles(unittest.TestCase):
    """Only Southern Watch may leave out the paths main() writes into docs/."""

    def tearDown(self):
        bp.set_campaign(bp.campaign_specs()[0])

    def test_southern_watch_may_rely_on_its_defaults(self):
        bp.set_campaign(dict(SLUG="sest-southern-watch", INFO_DESC=""))
        self.assertEqual(bp.COVERAGE_DOC, bp.ROOT / "docs" / "campaign-coverage.md")

    def test_the_shipped_specs_pass(self):
        for spec in bp.campaign_specs():
            bp.set_campaign(spec)
            self.assertEqual(bp.COVERAGE_DOC, spec["COVERAGE_DOC"])

    def test_a_new_campaign_must_name_its_own(self):
        for key in ("DOCS_DIR", "COVERAGE_DOC"):
            spec = dict(CampaignRegistry.fake_red_line().CAMPAIGN)
            del spec[key]
            with self.assertRaisesRegex(SystemExit, f"Red Line: the spec sets no {key}"):
                bp.set_campaign(spec)

    def test_a_new_campaign_may_not_borrow_southern_watchs(self):
        spec = dict(CampaignRegistry.fake_red_line().CAMPAIGN,
                    COVERAGE_DOC=bp.ROOT / "docs" / "campaign-coverage.md")
        with self.assertRaisesRegex(SystemExit, "COVERAGE_DOC is Southern Watch's"):
            bp.set_campaign(spec)


class VictoryAlsoTerms(unittest.TestCase):
    """An `also` term compiles to the condition its kind names, or stops the
    build. kind='destroyed' used to come out as an area test on the same
    units - the spoiler inside the arrival box - and the mission it was
    written for could not be won."""

    def win(self, also, **victory):
        v = dict(small_mission()["victory"], also=also, **victory)
        return rendered(small_mission(victory=v))

    def test_destroyed_term_is_a_kill(self):
        lines = self.win([dict(kind="destroyed", units=["spoiler"])])["Objective met"]
        self.assertIn("Condition_Condition2_Type=UnitDestroyed", lines)
        self.assertIn("Condition_Condition2_Units=Taskforce2Vessel1", lines)
        self.assertIn("Condition_Condition2_MinimumUnits=1", lines)
        self.assertIn("ConditionsCompleted=<Condition1> AND <Condition2>", lines)
        self.assertNotIn("Condition_Condition2_Type=UnitsInTheArea", lines)

    def test_area_and_time_terms_read_as_before(self):
        lines = self.win([dict(units=["escort"], min_units=1),
                          dict(after_minutes=70)])["Objective met"]
        self.assertIn("Condition_Condition2_Type=UnitsInTheArea", lines)
        self.assertIn("Condition_Condition2_AreaRadiusNM=12", lines)
        self.assertIn("Condition_Condition3_Type=Time", lines)
        self.assertIn("Condition_Condition3_Time=4200", lines)
        self.assertIn("ConditionsCompleted=<Condition1> AND <Condition2> AND <Condition3>",
                      lines)

    def test_unknown_kind_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "kind 'sunk'"):
            self.win([dict(kind="sunk", units=["spoiler"])])

    def test_unknown_key_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "'minimum'"):
            self.win([dict(units=["spoiler"], minimum=1)])

    def test_a_key_the_kind_does_not_read_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "'radius'"):
            self.win([dict(kind="destroyed", units=["spoiler"], radius=5)])

    def test_a_term_no_win_can_meet_stops_the_build(self):
        for term, why in ((dict(kind="destroyed", units=[]), r"\[\]"),
                          (dict(units=[]), r"\[\]"),
                          (dict(kind="destroyed", units=["spoiler"], min_units=5), "5 of"),
                          (dict(units=["escort"], min_units=0), "0 of"),
                          (dict(after_minutes=80), "minute 80"),
                          (dict(after_minutes=0), "minute 0"),
                          (dict(kind="time", after_minutes=70.5), "minute 70.5"),
                          (("destroyed", "spoiler"), "is a dict")):
            with self.assertRaisesRegex(SystemExit, why, msg=repr(term)):
                self.win([term])

    def test_a_destroyed_term_on_the_players_own_units_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "player's own Taskforce1Vessel1"):
            self.win([dict(kind="destroyed", units=["escort"])])

    def test_the_per_unit_chain_reads_the_same_terms(self):
        stage = dict(kind="area", units="escort", at=(-4.45, 128.85), radius=3,
                     per_unit=True)
        triggers = self.win([dict(kind="destroyed", units=["spoiler"])], after=stage)
        lines = triggers["Objective met by Taskforce1Vessel1"]
        self.assertIn("Condition_Condition2_Type=UnitDestroyed", lines)
        with self.assertRaisesRegex(SystemExit, "kind 'sunk'"):
            self.win([dict(kind="sunk", units=["spoiler"])], after=stage)


STOCK = bp.ROOT / "mods-source" / "_vanilla" / "original" / "missions"


class UnseenObjective(unittest.TestCase):
    """('unseen', station): fails when the ENEMY classifies those player
    units, in stock's own shape; F(..., kind="unseen") ends the mission on it."""

    def mission(self, fatal=(), how=("unseen", "escort"), spec="25,-40,Complete"):
        m = small_mission()
        m["objectives"] = m["objectives"] + [("Unseen", "Stay unclassified", spec)]
        m["resolve"] = dict(m["resolve"], Unseen=how)
        m["fatal"] = list(fatal)
        return m

    def test_the_condition_is_stocks_own(self):
        stock = coverage_check.blocks(
            (STOCK / "Warsaw Pact" / "Operation Polar Fury 1985.ini").read_text(
                encoding="utf-8-sig", errors="replace"))["Trigger5"]
        want = [k for k in stock if k.startswith("Condition")]
        lines = rendered(self.mission())["Unseen classified by the enemy"]
        got = [l.partition("=")[0] for l in lines if l.startswith("Condition")]
        self.assertEqual(got, want)
        self.assertEqual(stock["Condition_Condition1_Taskforce"], "Taskforce2")

    def test_the_resolver_fails_the_objective(self):
        lines = rendered(self.mission())["Unseen classified by the enemy"]
        self.assertEqual(lines, [
            "Condition_Condition1_Type=UnitClassified",
            "Condition_Condition1_Taskforce=Taskforce2",
            "Condition_Condition1_Units=Taskforce1Vessel1",
            "Condition_Condition1_MinimumUnits=1",
            "ConditionsCompleted=<Condition1>",
            "Action_ObjectivesFailed=Unseen"])

    def test_the_fatal_ends_the_mission(self):
        triggers = rendered(self.mission(fatal=[F("Unseen", kind="unseen")]))
        lines = triggers["Unseen classified by the enemy - mission over"]
        for want in ("Condition_Condition1_Type=UnitClassified",
                     "Condition_Condition1_Taskforce=Taskforce2",
                     "Condition_Condition1_Units=Taskforce1Vessel1",
                     "Action_Victory=Taskforce2", "Action_ObjectivesFailed=Unseen",
                     "Action_EnableTriggers=Trigger1"):
            self.assertIn(want, lines)
        self.assertEqual(triggers["Mission exit"][-2:],
                         ["Action_EndMission=True", "Action_EndMissionDelay=0"])

    def test_a_fatal_may_name_a_subset_and_nothing_else(self):
        rendered(self.mission(fatal=[F("Unseen", ["escort"], kind="unseen")]))
        with self.assertRaisesRegex(SystemExit, "reporting the wrong ship"):
            rendered(self.mission(fatal=[F("Unseen", ["group"], kind="unseen")]))

    def test_only_the_players_units_can_be_unseen(self):
        with self.assertRaisesRegex(SystemExit, "Taskforce2Vessel1"):
            rendered(self.mission(how=("unseen", "spoiler")))
        with self.assertRaisesRegex(SystemExit, "Taskforce2Vessel1"):
            rendered(self.mission(fatal=[F("Unseen", ["spoiler"], kind="unseen")],
                                  how=("spare", "spoiler")))

    def test_it_only_fails_so_it_cannot_end_fail(self):
        with self.assertRaisesRegex(SystemExit, "ends Fail"):
            rendered(self.mission(spec="25,-40,Fail"))

    def test_the_resolver_names_stations_only(self):
        # protect reads a trailing count; unseen has none, and used to drop it
        for how in (("unseen", "escort", 2), ("unseen", ["escort", "group"])):
            with self.assertRaisesRegex(SystemExit, "names stations", msg=repr(how)):
                rendered(self.mission(how=how))

    def test_a_fatal_minimum_runs_from_one_to_the_count(self):
        two = ("unseen", "escort", "group")
        lines = rendered(self.mission(how=two, fatal=[F("Unseen", kind="unseen", minimum=2)]))[
            "Unseen classified by the enemy - mission over"]
        self.assertIn("Condition_Condition1_Units=Taskforce1Vessel1,Taskforce1Vessel2", lines)
        self.assertIn("Condition_Condition1_MinimumUnits=2", lines)
        for least in (0, 3):     # 0 ends the mission on its first tick; 3 never
            with self.assertRaisesRegex(SystemExit, "minimum= runs from 1"):
                rendered(self.mission(how=two, fatal=[F("Unseen", kind="unseen",
                                                        minimum=least)]))

    def test_an_unknown_fatal_kind_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "'sighted'"):
            rendered(self.mission(fatal=[F("Unseen", ["escort"], kind="sighted")]))

    def test_unseen_units_are_not_escorted_hulls(self):
        placed, members = small_placement()
        m = self.mission(fatal=[F("Unseen", kind="unseen")])
        self.assertNotIn("Taskforce1Vessel1", bp.protected_tags(m, members))


class StandoffAndClosure(unittest.TestCase):
    """The standoff gate ignores a red unit that will not shoot and is not
    built to; the closure gate counts an armed boat as an escort and leaves
    a hull marked independent=True alone. Real units, placed by the builder
    on the coastline extract, well south of the Bight."""

    STATIONS = {"tender": S(-47.50, 140.50, "Tender"),
                "boat": S(-47.50, 140.70, "Boat"),          # 12 NM east
                "far_boat": S(-47.50, 141.20, "Far boat"),  # 42 NM east
                "decoy": S(-47.50, 142.00, "Decoy"),        # 90 NM east
                "spoiler": S(-47.53, 140.50, "In company")}  # 1.8 NM south

    TENDER = dict(side="blue", mod="_vanilla", type="civ_ms_kommunist",
                  station="tender", weapons="Hold")
    DECOY = dict(side="blue", mod="modern-plan-systems", type="plan_type_054a_p5",
                 station="decoy", weapons="Hold")
    BOAT = dict(side="blue", mod="plan-submarines", type="plan_ss_type_039c",
                station="boat", depth="belowlayer", weapons="Hold")

    def setUp(self):
        for lst in (bp.PLACEMENT_PROBLEMS, bp.COAST_CHECKED, bp.CLOSURE_PROBLEMS,
                    bp.CLOSURE_NOTES, bp.REACH_PROBLEMS):
            del lst[:]

    def placed(self, units):
        m = dict(key="Test Quiet Side", num="06", group="core", centre=(-47.5, 140.5),
                 minutes=80, role="escort", stations=self.STATIONS,
                 units=[dict(u) for u in units],
                 victory=dict(kind="arrive", station="tender", at=(-47.30, 140.20),
                              radius=6, objective="Rendezvous"),
                 objectives=[("Rendezvous", "Meet", "35,-35,Fail,Main")],
                 resolve={"Rendezvous": "victory"}, fatal=[])
        placed, members, _credits, _far = bp.place(m, bp.CoastPlacer(bp.coast_data(), m))
        self.assertEqual(bp.PLACEMENT_PROBLEMS, [])
        return m, placed, members

    def standoff(self, red):
        m, placed, members = self.placed([self.TENDER, self.DECOY, red])
        bp.check_reach(m, placed, members)
        return [p for p in bp.REACH_PROBLEMS if "opens with red" in p]

    def closure(self, units):
        m, placed, members = self.placed(units)
        bp.check_closure(m, placed, members)
        return bp.CLOSURE_PROBLEMS

    def test_a_passive_spoiler_may_start_in_company(self):
        self.assertEqual(self.standoff(dict(
            side="red", mod="auxilliary-merchant-pack", type="ran_ms_super_p",
            station="spoiler", weapons="Hold")), [])

    def test_the_same_hull_weapons_free_may_not(self):
        self.assertEqual(len(self.standoff(dict(
            side="red", mod="auxilliary-merchant-pack", type="ran_ms_super_p",
            station="spoiler", weapons="Free"))), 1)

    def test_a_warship_at_hold_may_not(self):
        self.assertEqual(len(self.standoff(dict(
            side="red", mod="SEST_RAN_Fleet", type="ran_ffh_anzac",
            station="spoiler", weapons="Hold"))), 1)

    def test_a_role_the_builder_does_not_name_is_not_passive(self):
        # Role=SSGN is in neither list, so is_combat() says no; a 1,000 NM
        # Tomahawk boat at Hold must still not start inside the standoff.
        self.assertFalse(bp.is_combat("usn_ssgn_ohio"))
        self.assertFalse(bp.is_passive("usn_ssgn_ohio"))
        self.assertTrue(bp.is_passive("ran_ms_super_p"))
        self.assertEqual(len(self.standoff(dict(
            side="red", mod="us-submarines", type="usn_ssgn_ohio",
            station="spoiler", depth="periscope", weapons="Hold"))), 1)

    def test_the_decoy_alone_is_too_far_to_escort(self):
        problems = self.closure([self.TENDER, self.DECOY])
        self.assertEqual(len(problems), 1)
        self.assertIn("Taskforce1Vessel1 (civ_ms_kommunist) is protected", problems[0])
        self.assertIn("at 24 kn", problems[0])

    def test_an_armed_boat_escorts_her_tender(self):
        self.assertEqual(self.closure([self.TENDER, self.DECOY, self.BOAT]), [])

    def test_a_boat_is_held_to_a_boats_speed(self):
        problems = self.closure([self.TENDER, dict(self.BOAT, station="far_boat")])
        self.assertEqual(len(problems), 1)
        self.assertIn("at 10 kn", problems[0])

    def test_an_independent_hull_is_not_measured(self):
        self.assertEqual(self.closure([dict(self.TENDER, independent=True),
                                       self.DECOY]), [])

    def test_only_the_players_hulls_can_be_independent(self):
        with self.assertRaises(SystemExit):
            self.placed([self.TENDER, dict(
                side="red", mod="auxilliary-merchant-pack", type="ran_ms_super_p",
                station="spoiler", weapons="Hold", independent=True)])


class OpeningRanges(StandoffAndClosure):
    """check_opening: a red unit weapons free at the start must not already
    be inside the fight - a boat or a ship inside 25 NM of the player's
    nearest hull, a ship in anti-ship reach with a drone over her target.
    Tight, a contact= reason and range each clear it."""

    STATIONS = dict(StandoffAndClosure.STATIONS,
                    eye=S(-47.52, 140.52, "Drone", alt=10000))
    SUB = dict(side="red", mod="plan-submarines", type="plan_ss_type_039c",
               station="boat", depth="belowlayer")
    PEYKAAP = dict(side="red", mod="red-storm-arsenal", type="ir_ptg_peykaap_3",
                   station="far_boat")
    DRONE = dict(side="red", mod="small-medium-uav-series", type="usn_ForpostR705",
                 station="eye", alt=10000)

    def setUp(self):
        super().setUp()
        del bp.OPENING_PROBLEMS[:]

    def opening(self, units):
        m, placed, _members = self.placed([self.TENDER] + units)
        bp.check_opening(m, placed)
        return bp.OPENING_PROBLEMS

    def test_a_free_boat_inside_25_nm_is_refused(self):
        problems = self.opening([self.SUB])
        self.assertEqual(len(problems), 1)
        self.assertIn("inside 25 NM", problems[0])

    def test_the_same_boat_tight_is_not(self):
        self.assertEqual(self.opening([dict(self.SUB, weapons="Tight")]), [])

    def test_a_stated_contact_is_not(self):
        self.assertEqual(self.opening([dict(
            self.SUB, contact="the briefing puts her in the box")]), [])

    def test_the_same_boat_42_nm_out_is_not(self):
        self.assertEqual(self.opening([dict(self.SUB, station="far_boat")]), [])

    def test_a_ship_in_reach_with_a_drone_over_her_target_is_refused(self):
        self.assertEqual(self.opening([self.PEYKAAP]), [])
        problems = self.opening([self.PEYKAAP, self.DRONE])
        self.assertEqual(len(problems), 1)
        self.assertIn("giving the track", problems[0])

    def test_only_red_units_take_a_contact_reason(self):
        with self.assertRaises(SystemExit):
            self.placed([dict(self.TENDER, contact="why")])

    def test_ship_reach_reads_the_torpedo_room(self):
        # The Virginia's tubes name no round; her Mk 48s are listed only in
        # the [TorpedoRoom] the tubes feed from. Read as unarmed, RL02's boat
        # passed the gate 21 NM from the escort.
        self.assertGreaterEqual(bp.ship_reach("usn_ssn_virginia_2027", None), 20)

    def test_ship_reach_ignores_sonobuoys(self):
        # The Ka-28's sonobuoys read 100 NM in reach(); its torpedo is what
        # can hit a ship.
        kind_dir, path = bp.unit_file("plan_ka-28")
        fit, _why = bp.pick_loadout("plan_ka-28", path, None)
        self.assertGreaterEqual(bp.reach("plan_ka-28", kind_dir, path, fit), 100)
        self.assertGreater(bp.ship_reach("plan_ka-28", fit), 0)
        self.assertLess(bp.ship_reach("plan_ka-28", fit), 10)


class RacetrackLoop(unittest.TestCase):
    """loop=True flies a patrol aircraft's route until the clock runs out,
    in stock's own form; nothing else may loop."""

    STATIONS = {"red_air": S(-47.60, 140.60, "Barrier patrol", alt=15000),
                "ship": S(-47.50, 140.50, "Ship"),
                "airliner": S(-47.40, 140.40, "Airliner", alt=35000)}
    TRACK = [(-47.05, 140.15, 15000), (-47.65, 139.85, 15000)]
    P8 = dict(side="red", mod="p-8-poseidon", type="usn_p8", station="red_air",
              squadron="Squadron3", loadout="ASW", weapons="Hold", route=TRACK)

    def setUp(self):
        del bp.PLACEMENT_PROBLEMS[:]

    def waypoints(self, unit):
        m = dict(key="Test Barrier", num="05", group="core", centre=(-47.5, 140.5),
                 minutes=120, stations=self.STATIONS, units=[unit])
        placed, _members, _credits, _far = bp.place(m, bp.CoastPlacer(bp.coast_data(), m))
        return next(keys for entries in placed.values()
                    for _tag, keys, _n, _x in entries).get("Waypoints")

    def test_a_looped_patrol_ends_on_stocks_token(self):
        self.assertEqual(self.waypoints(dict(self.P8, loop=True)),
                         "-21.00,15000,27.00|-39.00,15000,-9.00|Loop")

    def test_without_loop_the_route_is_as_before(self):
        self.assertEqual(self.waypoints(self.P8),
                         "-21.00,15000,27.00|-39.00,15000,-9.00")

    def test_a_ship_an_unrouted_aircraft_and_an_airliner_may_not(self):
        for unit in (dict(side="blue", mod="modern-plan-systems",
                          type="plan_type_054a_p5", station="ship",
                          route=[(-47.40, 140.80, 0)], loop=True),
                     dict({k: v for k, v in self.P8.items() if k != "route"},
                          loop=True),
                     dict(side="neutral", mod="civil-aircraft-airbus", type="civ_a330",
                          station="airliner", route=[(-40.0, 150.0, 35000)],
                          loop=True)):
            with self.assertRaises(SystemExit) as caught:
                self.waypoints(unit)
            self.assertIn("loop", str(caught.exception.code))


SIGNAL = dict(file="99_test_signal", form="signal",
              header=[("FROM", "FLEET HQ"), ("TO", "COMMANDER CARRIER TASK GROUP")],
              body=["1. THE GROUP IS NOT AT WAR WITH ANY STATE."],
              note="Para 3 is the order.")
LOG = dict(file="99_test_log", form="log", ship="Test Ship", master="A. Test",
           date="28 November 2028", entries=[("0510", "Group turned north-west.")],
           note="Acknowledged.  - A.T.")
INTSUM = dict(file="99_test_intsum", form="intsum", org="Fleet HQ", ref="INTSUM 01",
              date="22 December 2028", subject="Test", body=["The picture."])


@unittest.skipIf(make_art is None, "Pillow is not installed")
class StoryArt(unittest.TestCase):
    """The page labels a campaign played from the other side needs, and only
    the map tiles something stands on."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sest-art-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def png(self, draw, *args, **kw):
        out = self.tmp / "page.png"
        with contextlib.redirect_stdout(io.StringIO()):
            draw(out, *args, **kw)
        return out.read_bytes()

    def render_all(self, events, **kw):
        with contextlib.redirect_stdout(io.StringIO()):
            make_art.render_all(self.tmp / "camp", [], events, "sest-test",
                                "Test", "Subtitle", **kw)
        return self.tmp / "camp" / "art"

    def signal(self, **kw):
        return self.png(make_art.signal, SIGNAL["header"], SIGNAL["body"],
                        note=SIGNAL["note"], **kw)

    def log(self, **kw):
        return self.png(make_art.log, LOG["ship"], LOG["master"], LOG["date"],
                        LOG["entries"], note=LOG["note"], **kw)

    def test_the_defaults_draw_what_they_drew(self):
        self.assertEqual(self.signal(), self.signal(note_label="ANALYST NOTE"))
        self.assertEqual(self.log(), self.log(heading="DECK LOG EXTRACT",
                                              master_label="MASTER",
                                              note_label="MASTER'S NOTE"))

    def test_each_label_changes_the_page(self):
        self.assertNotEqual(self.signal(), self.signal(note_label="SENDER'S NOTE"))
        for key, value in (("heading", "LOG EXTRACT"), ("master_label", "CAPTAIN"),
                           ("note_label", "CAPTAIN'S NOTE")):
            self.assertNotEqual(self.log(), self.log(**{key: value}), key)

    def test_render_all_passes_the_event_keys_through(self):
        art = self.render_all([
            dict(SIGNAL, note_label="SENDER'S NOTE"),
            dict(LOG, log_heading="LOG EXTRACT", master_label="CAPTAIN",
                 note_label="CAPTAIN'S NOTE"),
            dict(INTSUM, marking="SECRET  //  FLEET HQ ONLY")])
        self.assertEqual((art / "99_test_signal_image.png").read_bytes(),
                         self.signal(note_label="SENDER'S NOTE"))
        self.assertEqual((art / "99_test_log_image.png").read_bytes(),
                         self.log(heading="LOG EXTRACT", master_label="CAPTAIN",
                                  note_label="CAPTAIN'S NOTE"))
        self.assertEqual((art / "99_test_intsum_image.png").read_bytes(),
                         self.png(make_art.intsum, INTSUM["org"], INTSUM["ref"],
                                  INTSUM["date"], INTSUM["subject"], INTSUM["body"],
                                  marking="SECRET  //  FLEET HQ ONLY"))

    def test_only_the_tiles_the_events_stand_on_are_written(self):
        events = [SIGNAL, LOG]
        art = self.render_all(events, tiles={bp.event_tile(e) for e in events})
        self.assertEqual(sorted(f.name for f in art.glob("bkg_tile_*.png")),
                         ["bkg_tile_message.png"])

    def test_a_tile_that_is_not_one_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "no map tile called press"):
            self.render_all([SIGNAL], tiles={"press", "message"})
        self.assertFalse((self.tmp / "camp").exists())

    def test_the_tile_rule(self):
        self.assertEqual(bp.event_tile(dict(file="x")), "newspaper")
        self.assertEqual({bp.event_tile(e) for e in (SIGNAL, LOG, INTSUM)}, {"message"})


@unittest.skipIf(make_art is None, "Pillow is not installed")
class CardFrame(unittest.TestCase):
    """The mission card's chart holds the whole objective ring, not only its
    centre, and the card's title stays off the chart."""

    # The ceasefire-morning card: the group ahead, the box 21 NM up its
    # course, 12 NM across - wider than the margin the marks leave.
    MARKS = [(0.0, 9.0, "ship"), (-12.0, 6.0, "ship"), (-18.0, 12.0, "ship"),
             (-1.2, 7.8, "air")]

    @staticmethod
    def square(afloat, goal):
        x0, z1, span = make_art.plot_extent(afloat, goal)
        return x0, x0 + span, z1 - span, z1

    def assertInside(self, goal, square):
        w, e, s, n = square
        gx, gz, r = goal
        self.assertTrue(w <= gx - r and gx + r <= e and s <= gz - r and gz + r <= n,
                        f"ring {goal} leaves the chart {square}")

    def test_a_wide_ring_is_framed_whole(self):
        goal = (-30.12, 16.74, 12.0)
        self.assertInside(goal, self.square(self.MARKS, goal))

    def test_a_ring_that_fits_is_framed_as_before(self):
        # The old rule: the marks and the ring's centre, with 42% to spare.
        goal = (-6.0, 8.0, 3.0)
        xs = [x for x, _z, _k in self.MARKS] + [goal[0]]
        zs = [z for _x, z, _k in self.MARKS] + [goal[1]]
        span = max(max(xs) - min(xs), max(zs) - min(zs), 20.0) * 1.42
        x0 = (min(xs) + max(xs)) / 2 - span / 2
        z1 = (min(zs) + max(zs)) / 2 + span / 2
        self.assertEqual(make_art.plot_extent(self.MARKS, goal), (x0, z1, span))
        self.assertInside(goal, self.square(self.MARKS, goal))

    def test_no_objective_frames_the_marks(self):
        x0, z1, span = make_art.plot_extent(self.MARKS, None)
        self.assertAlmostEqual(span, 20.0 * 1.42)

    @staticmethod
    def measure(line, px):
        from PIL import Image, ImageDraw
        d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
        return d.textlength(line, font=make_art.font(px, True))

    # The card's own geometry: the chart's frame starts at 1188 px on the
    # 2x canvas and the title at 86, 40 px clear of it.
    ROOM = make_art.SHEET_W * 2 - 1100 - 80 - 40 - 86 if make_art else 0

    def test_a_wide_title_is_set_smaller_to_clear_the_chart(self):
        for title in (["UNDER THE", "CONVERGENCE"], ["BROKEN WAKE"]):
            self.assertGreater(max(self.measure(l, 132) for l in title), self.ROOM)
            size = make_art.title_size(title, self.ROOM, self.measure)
            self.assertLess(size, 132)
            self.assertLessEqual(max(self.measure(l, size) for l in title), self.ROOM)

    def test_a_title_that_fits_keeps_its_size(self):
        self.assertEqual(make_art.title_size(["THE QUIET", "PASSENGER"], self.ROOM,
                                             self.measure), 132)


@unittest.skipIf(make_art is None, "Pillow is not installed")
class BackdropFrame(unittest.TestCase):
    """The campaign backdrop keeps its campaign marks off the chart's top edge
    and clear of the title at the bottom, however tall the theatre."""

    @staticmethod
    def old_rule(marks):
        # 2.2 degrees round the marks, then padded out to the frame's aspect.
        W, H = make_art.W, make_art.H
        lats, lons = [m[1] for m in marks], [m[2] for m in marks]
        la0, la1 = min(lats) - 2.2, max(lats) + 2.2
        lo0, lo1 = min(lons) - 2.2, max(lons) + 2.2
        if (lo1 - lo0) / (la1 - la0) < W / H:
            need, mid = (la1 - la0) * W / H, (lo0 + lo1) / 2
            return la0, la1, mid - need / 2, mid + need / 2
        need, mid = (lo1 - lo0) * H / W, (la0 + la1) / 2
        return mid - need / 2, mid + need / 2, lo0, lo1

    def test_a_tall_theatre_keeps_its_marks_off_the_edges(self):
        # The equator to 47 South: 2.2 degrees left the first and last marks
        # on the frame's edge.
        marks = [("RL01", 1.3, 126.7, True), ("RL02", -0.5, 135.8, True),
                 ("RL03", -5.6, 131.5, True), ("RL04", -4.6, 128.9, True),
                 ("RL05", -47.5, 140.5, True), ("RL06", -46.3, 166.0, True)]
        H, W = make_art.H, make_art.W
        s, n, w, e = self.old_rule(marks)
        self.assertLess((n - 1.3) / (n - s) * H, 100)
        s, n, w, e = make_art.backdrop_frame(marks)
        self.assertGreaterEqual((n - 1.3) / (n - s) * H, 100 - 1e-6)
        self.assertGreaterEqual((-47.5 - s) / (n - s) * H, 150 - 1e-6)
        self.assertTrue(all(w < m[2] < e for m in marks))
        self.assertAlmostEqual((e - w) / (n - s), W / H)

    def test_a_compact_theatre_is_framed_as_before(self):
        # An optional beat near the bottom does not move the frame; only the
        # campaign marks are held to the margins.
        marks = [("01", -10.5, 131.2, True), ("02", -10.0, 145.0, True),
                 ("08", -2.0, 135.0, True), ("03", -11.0, 126.0, True),
                 ("D1", -15.9, 148.8, False)]
        self.assertEqual(make_art.backdrop_frame(marks), self.old_rule(marks))


class RosterAndSeahawk(unittest.TestCase):
    """Generated text that assumed Southern Watch: the roster file's header
    and footer, and a Seahawk's squadron chosen by side instead of flag."""

    GEN = "; Generated by integration/campaign/build_pack.py - edit "

    def tearDown(self):
        bp.set_campaign(bp.campaign_specs()[0])

    def roster(self, spec):
        bp.set_campaign(spec)
        return bp.roster_ini(spec["ROSTER"])[0].splitlines()

    def red(self, *units):
        return dict(CampaignRegistry.fake_red_line().CAMPAIGN,
                    ROSTER=[dict(unit=u, picks=["Variant1"], points=100) for u in units])

    def test_each_roster_names_the_file_to_edit(self):
        watch, reach = bp.campaign_specs()[:2]
        self.assertEqual(self.roster(watch)[1], self.GEN + "campaign_data.py.")
        self.assertEqual(self.roster(reach)[1], self.GEN + "southern_reach/tables.py.")
        red = self.roster(self.red("plan_type_054a_p5"))
        self.assertEqual(red[0], "; SEST Red Line requisition roster.")
        self.assertEqual(red[1], self.GEN + "the Red Line campaign's roster.")
        red = self.roster(dict(self.red("plan_type_054a_p5"),
                               ROSTER_SOURCE="red_line/tables.py"))
        self.assertEqual(red[1], self.GEN + "red_line/tables.py.")

    def test_the_footer_says_what_the_hulls_on_sale_declare(self):
        self.assertEqual(self.roster(self.red("plan_type_054a_p5"))[-1],
                         "; and tested - no hull on this roster declares one.")
        self.assertEqual(self.roster(self.red("plan_type_054a_p5", "plan_type_056a"))[-2:],
                         ["; and tested.",
                          "; plan_type_056a declares Default, AntiShip, ASW; "
                          "none is priced here."])
        self.assertIn("; ran_opv_arafura declares Containers, AntiShip, AntiAir; "
                      "none is priced here.", self.roster(bp.campaign_specs()[0]))

    def squadron(self, side, blue_nation, red_nation, **kw):
        m = dict(key="Test Seahawk", num="01", group="core", centre=(-47.5, 140.5),
                 minutes=60, blue_nation=blue_nation, red_nation=red_nation,
                 stations={"deck": S(-47.50, 140.50, "Deck"),
                           "flight": S(-47.48, 140.50, "Flight", alt=500)},
                 units=[U(side, "SEST_RAN_Fleet", "ran_ffh_anzac", "deck", weapons="Hold"),
                        U(side, "us-navy-2027", "usn_mh-60r", "flight", **kw)])
        placed, _members, _credits, _far = bp.place(m, bp.CoastPlacer(bp.coast_data(), m))
        family = "Taskforce1Helicopter" if side == "blue" else "Taskforce2Helicopter"
        return placed[family][0][1]["SquadronReference"]

    def test_an_australian_seahawk_is_816_squadron_on_either_side(self):
        self.assertEqual(self.squadron("blue", "Australia", "China"), "Squadron20")
        self.assertEqual(self.squadron("red", "China", "Australia"), "Squadron20")

    def test_anybody_elses_keeps_the_files_default(self):
        self.assertEqual(self.squadron("red", "Australia", "USA"), "Squadron1")
        self.assertEqual(self.squadron("blue", "China", "Australia"), "Squadron1")

    def test_the_units_own_flag_and_an_explicit_squadron_win(self):
        self.assertEqual(self.squadron("red", "China", "USA", nation="australia"),
                         "Squadron20")
        self.assertEqual(self.squadron("red", "China", "Australia", squadron="Squadron2"),
                         "Squadron2")


class RosterOnSale(unittest.TestCase):
    """A roster entry no purchase window sells is a price nobody can pay -
    Southern Watch's KC-46 was one until the builder refused it."""

    ROSTER = [dict(unit="ran_ffh_anzac", picks=["Variant3"], points=240),
              dict(unit="usn_p8", picks=["Squadron3"], points=55)]

    @staticmethod
    def missions(*windows):
        return [dict(key=f"M{n}", window=w) for n, w in enumerate(windows, 1)]

    def check(self, roster, missions):
        bp.check_roster_on_sale(roster, missions, "Test")

    def test_an_entry_no_window_sells_stops_the_build(self):
        with self.assertRaises(SystemExit) as caught:
            self.check(self.ROSTER, self.missions(dict(buy=True, allow=["ran_ffh_anzac"])))
        self.assertIn("usn_p8", str(caught.exception))
        self.assertNotIn("ran_ffh_anzac", str(caught.exception))

    def test_an_entry_on_sale_in_any_window_passes(self):
        self.check(self.ROSTER, self.missions(dict(buy=True, allow=["ran_ffh_anzac"]),
                                              dict(), dict(buy=True, allow=["usn_p8"])))

    def test_an_allowlist_on_a_closed_builder_sells_nothing(self):
        with self.assertRaises(SystemExit):
            self.check(self.ROSTER, self.missions(dict(buy=True, allow=["ran_ffh_anzac"]),
                                                  dict(buy=False, allow=["usn_p8"])))

    def test_an_open_builder_without_an_allowlist_sells_the_roster(self):
        self.check(self.ROSTER, self.missions(dict(buy=True, allow=["ran_ffh_anzac"]),
                                              dict(buy=True)))

    def test_the_shipped_campaigns_pass_and_the_kc46_would_not(self):
        for spec in bp.campaign_specs():
            self.check(spec["ROSTER"], spec["MISSIONS"])
        watch = bp.campaign_specs()[0]
        kc46 = dict(unit="usaf_kc-46a_boom", picks=["Squadron1"], points=75)
        with self.assertRaises(SystemExit) as caught:
            self.check(watch["ROSTER"] + [kc46], watch["MISSIONS"])
        self.assertIn("usaf_kc-46a_boom", str(caught.exception))


class HomeBases(unittest.TestCase):
    """Where the player's force is generated in, a player-side aircraft
    names no Taskforce1 ship as its HomeBase - stock never does, and Rig
    Seventeen died in ResolvePlacedCampaignAircraft twice when it did."""

    @staticmethod
    def placed():
        return {
            "Taskforce1Vessel": [
                ("Taskforce1Vessel1", _keys("plan_type_054a_p5", 0, 9), None, False),
                ("Taskforce1Vessel2", _keys("plan_cv_type_003", 6, 18), None, False)],
            "Taskforce1Helicopter": [
                ("Taskforce1Helicopter1", _keys("plan_z-18f", 8.4, 19.2), None, False)],
            "Taskforce2Vessel": [
                ("Taskforce2Vessel1", _keys("plan_cv_type_003", 40, 40), None, False)],
            "Taskforce2Helicopter": [
                ("Taskforce2Helicopter1", _keys("plan_z-18f", 41, 41), None, False)],
        }

    def test_a_generated_mission_writes_no_player_ship_home(self):
        placed = self.placed()
        self.assertEqual(bp.assign_home_bases(placed, generated=True), [])
        helo = placed["Taskforce1Helicopter"][0][1]
        self.assertNotIn("HomeBase", helo)
        self.assertEqual(helo["UnlimitedFuel"], "False")      # still charged fuel
        # The other side's deck is not the player's force: it keeps its home.
        self.assertEqual(placed["Taskforce2Helicopter"][0][1]["HomeBase"],
                         "Taskforce2Vessel1")

    def test_a_mission_launched_as_authored_keeps_the_deck(self):
        placed = self.placed()
        self.assertEqual(bp.assign_home_bases(placed, generated=False), [])
        self.assertEqual(placed["Taskforce1Helicopter"][0][1]["HomeBase"],
                         "Taskforce1Vessel2")

    def test_no_shipped_generated_mission_names_a_player_ship_home(self):
        for spec in bp.campaign_specs():
            camp = bp.ROOT / "integration" / "campaign" / "SEST_Campaign" / "campaigns" / spec["SLUG"]
            ini = (camp / "campaign.ini").read_text(encoding="utf-8")
            for block in re.split(r"\n(?=\[)", ini):
                gen = re.search(r"^TaskForceModeMissionGenerationType=(\S+)", block, re.M)
                path = re.search(r"^MissionFile=campaigns/[^/]+/(.+)$", block, re.M)
                if not (gen and path):
                    continue
                text = (camp / path.group(1).strip()).read_text(encoding="utf-8")
                self.assertNotRegex(text, r"(?m)^HomeBase=Taskforce1Vessel",
                                    path.group(1))


class OpenAllocation(unittest.TestCase):
    """The Open Allocation twin sells the whole roster at every open window
    and is otherwise its base campaign's spine, line for line."""

    ROSTER = [dict(unit="ran_ffh_anzac", picks=["Variant3", "Variant8"], points=240),
              dict(unit="usn_p8", picks=["Squadron3"], points=55)]
    FULL = "ran_ffh_anzac,Variant3,Variant8|usn_p8,Squadron3"
    SPINE = "\n".join([
        "[File]", "Base=campaigns/sest-test/campaign.ini", "",
        "[TaskForceModeDifficulty_Standard]", "Name=Standard", "",
        "[Language_en]", "Name=Test Watch (Royal Australian Navy)", "Description=Blurb.", "",
        "[Missions]", "NumberOfMissions=3", "",
        "[Mission1]  #01 First", "MissionFile=campaigns/sest-test/missions/One.ini",
        "TaskForceModeEnableTaskForceBuilder=True",
        "TaskForceModeAllowedRosterUnits=ran_ffh_anzac,Variant3,Variant8",
        "TaskForceModeBuilderSituation_en=Frigates only.", "",
        "[Mission2]  #Stop", "TaskForceModeEnableTaskForceBuilder=False",
        "TaskForceModeBuilderSituation_en=Repairs only.", "",
        "[Mission3]  #02 Second", "MissionFile=campaigns/sest-test/missions/Two.ini",
        "TaskForceModeEnableTaskForceBuilder=True", ""])

    def test_the_twin_sells_everything_and_keeps_the_rest(self):
        twin = bp.open_allocation_ini(self.SPINE, "sest-test", self.ROSTER).split("\n")
        base = self.SPINE.split("\n")
        self.assertEqual(len(twin), len(base))
        changed = {b: w for b, w in zip(base, twin) if b != w}
        self.assertEqual(changed, {
            "Base=campaigns/sest-test/campaign.ini":
                "Base=campaigns/sest-test-open/campaign.ini",
            "Name=Test Watch (Royal Australian Navy)":
                "Name=Test Watch - Open Allocation (Royal Australian Navy)",
            "Description=Blurb.": "Description=" + bp.OPEN_BLURB + "Blurb.",
            "TaskForceModeAllowedRosterUnits=ran_ffh_anzac,Variant3,Variant8":
                "TaskForceModeAllowedRosterUnits=" + self.FULL,
            "TaskForceModeBuilderSituation_en=Frigates only.":
                "TaskForceModeBuilderSituation_en=" + bp.OPEN_NOTE + " Frigates only.",
        })
        # The missions are still the base campaign's; the repair-only stop
        # and the preset keep their text.
        self.assertIn("MissionFile=campaigns/sest-test/missions/One.ini", twin)
        self.assertIn("TaskForceModeBuilderSituation_en=Repairs only.", twin)
        self.assertIn("Name=Standard", twin)

    def test_a_spine_it_cannot_read_stops_the_build(self):
        with self.assertRaises(SystemExit):
            bp.open_allocation_ini(self.SPINE.replace("sest-test/campaign.ini", "x.ini"),
                                   "sest-test", self.ROSTER)

    def test_the_twins_rules_page_says_so(self):
        spec = bp.campaign_specs()[0]
        page = bp.campaign_rules(spec, open_allocation=True)
        import xml.dom.minidom
        xml.dom.minidom.parseString(page.encode("utf-8"))
        self.assertIn(f'{bp._xml_text(spec["TITLE"])} - Open Allocation - Task Force Mode',
                      page)
        self.assertIn("every force allocation offers the whole campaign roster", page)
        self.assertNotIn("not available for purchase at the start", page)
        self.assertNotIn("Open Allocation", bp.campaign_rules(spec))


class SameNationDiscount(unittest.TestCase):
    """The discount is the game's own rule; the page says what it covers,
    read from the squadron and hull-variant files the game takes nations from."""

    def test_the_enemy_roster_sorts_units_the_way_the_stock_file_does(self):
        # A 22,000 t LPD is a flagship, a frigate with a variant is persistent,
        # a boat with none is reusable, a submarine is persistent, two fighters
        # of one squadron are a flight of two, a helicopter is a helicopter.
        missions = [dict(key="m", group="core", red_nation="China")]
        placed = {
            "Taskforce2Vessel": [
                ("Taskforce2Vessel1", {"Type": "plan_lpd_type_071", "VariantReference": "Variant1"}, None, False),
                ("Taskforce2Vessel2", {"Type": "plan_type_054a_p5", "VariantReference": "Variant1"}, None, False),
                ("Taskforce2Vessel3", {"Type": "ir_ptg_peykaap_3", "Nation": "Iran"}, None, False)],
            "Taskforce2Submarine": [
                ("Taskforce2Submarine1", {"Type": "plan_ss_type_039c", "VariantReference": "Variant1"}, None, False)],
            "Taskforce2Aircraft": [
                ("Taskforce2Aircraft1", {"Type": "plan_j-15d", "SquadronReference": "Squadron1"}, None, False),
                ("Taskforce2Aircraft2", {"Type": "plan_j-15d", "SquadronReference": "Squadron1"}, None, False)],
            "Taskforce2Helicopter": [
                ("Taskforce2Helicopter1", {"Type": "plan_z-9d", "SquadronReference": "Squadron1"}, None, False)],
            "Taskforce1Vessel": [
                ("Taskforce1Vessel1", {"Type": "ran_ffh_anzac", "VariantReference": "Variant1"}, None, False)],
        }
        placed["Taskforce2Vessel"].append(
            ("Taskforce2Vessel4", {"Type": "civ_ms_encounter", "VariantReference": "Variant1"}, None, False))
        text = bp.enemy_roster_ini(missions, {"m": placed})
        self.assertNotIn("civ_ms_encounter", text, "an unarmed merchant is traffic, not ORBAT")
        self.assertIn("[NationalForces_PLAN]\nShowOnlyClassName=True", text)
        self.assertIn("[SurfaceMajorFlagships_PLAN]\nplan_lpd_type_071=Variant1", text)
        self.assertIn("[SurfacePersistent_PLAN]\nplan_type_054a_p5=Variant1", text)
        self.assertIn("[SurfaceReusable_Iran]\nir_ptg_peykaap_3=Default", text)
        self.assertIn("[SubmarinesPersistent_PLAN]\nplan_ss_type_039c=Variant1", text)
        self.assertIn("[AircraftReusable_PLAN]\nplan_j-15d=Squadron1,2", text)
        self.assertIn("[HelicoptersReusable_PLAN]\nplan_z-9d=Squadron1,1", text)
        self.assertNotIn("ran_ffh_anzac", text, "the player's own ships are not enemy ORBAT")

    def test_the_enemy_roster_is_what_the_missions_place(self):
        # The built pack: every Taskforce2 unit a campaign's missions place is
        # in its roster, the twin carries the same file, and the spine names it.
        root = Path(bp.__file__).resolve().parent / "SEST_Campaign" / "campaigns"
        checked = 0
        for camp in sorted(root.iterdir()):
            missions = camp / "missions"
            roster = camp / "enemy_theater_roster.ini"
            self.assertTrue(roster.exists(), camp.name)
            spine = (camp / "campaign.ini").read_text(encoding="utf-8")
            self.assertIn("[DynamicUnitGeneration]\nTaskforce2RosterFile=enemy_theater_roster.ini", spine, camp.name)
            if not missions.exists():
                twin_of = root / camp.name.replace("-open", "")
                self.assertEqual(roster.read_bytes(), (twin_of / "enemy_theater_roster.ini").read_bytes(),
                                 f"{camp.name} must carry its campaign's roster")
                continue
            listed = set(re.findall(r"^([A-Za-z0-9_.()'-]+)=", roster.read_text(encoding="utf-8"), re.M))
            for ini in missions.glob("*.ini"):
                text = ini.read_text(encoding="utf-8")
                for m in re.finditer(r"^\[Taskforce2(Vessel|Submarine|Aircraft|Helicopter)\d+\][^\n]*\n(.*?)(?=^\[)",
                                     text, re.M | re.S):
                    uid = re.search(r"^Type=(\S+)", m.group(2), re.M).group(1)
                    if m.group(1) == "Vessel" and not bp.armed(uid):
                        continue
                    self.assertIn(uid, listed, f"{ini.name}: {uid} is placed but not in the roster")
                    checked += 1
        self.assertGreater(checked, 100)

    def test_the_beacon_reward_is_a_datum_that_ages_off(self):
        ini = (Path(bp.__file__).resolve().parent / "SEST_Campaign" / "campaigns" /
               "sest-southern-watch" / "missions" / "Southern Watch 02 - Steel Highway.ini")
        text = ini.read_text(encoding="utf-8")
        self.assertIn("Action_UnitRevealToTaskforce=Taskforce1\nAction_UnitRevealTime=900\n", text)
        self.assertNotIn("Taskforce1|Classify", text)

    def test_every_shipped_roster_is_the_commanders_own(self):
        for spec in bp.campaign_specs():
            nation = re.search(r"^CommanderNations=(.+)$", spec["COMMANDER"], re.M).group(1)
            self.assertEqual(bp.same_nation_discount(spec["COMMANDER"]), 0.2, spec["SLUG"])
            self.assertEqual(set(bp.roster_nations(spec["ROSTER"]).values()), {nation},
                             spec["SLUG"])

    def test_the_us_built_airframes_fly_australian_squadrons(self):
        for uid, pick in (("usn_fa-18f_blk3", "Squadron8"), ("usn_ea-18g", "Squadron6"),
                          ("usn_p8", "Squadron3"), ("usn_mh-60r", "Squadron20")):
            self.assertEqual(bp.pick_nation(uid, pick), "Australia", uid)

    def test_the_page_carries_the_games_binding_and_the_cover(self):
        page = bp.campaign_rules(bp.campaign_specs()[0])
        self.assertIn("{Binding SameNationDiscountPercentText}", page)
        self.assertIn("registered to Australia by its squadron or hull variant, so the "
                      "discount applies to all of it", page)
        self.assertNotIn("No national purchase discount", page)

    def test_no_discount_says_so(self):
        spec = dict(bp.campaign_specs()[0])
        spec["COMMANDER"] = spec["COMMANDER"].replace("SameNationUnitDiscount=0.2",
                                                      "SameNationUnitDiscount=0")
        page = bp.campaign_rules(spec)
        self.assertIn("No national purchase discount applies", page)
        self.assertNotIn("SameNationDiscountPercentText", page)

    def test_a_foreign_unit_is_named_at_its_listed_price(self):
        spec = dict(bp.campaign_specs()[0])
        spec["ROSTER"] = spec["ROSTER"] + [
            dict(unit="plan_j-15", picks=["Squadron1"], points=40)]
        page = bp.campaign_rules(spec)
        self.assertIn("The discount covers the 10 classes registered to Australia. The 1 "
                      "class registered to other nations - from China (1) - costs its "
                      "listed price.", page)

    def _squadrons(self, text):
        """pick_nation() over a squadrons file with this text."""
        tmp = Path(tempfile.mkdtemp()) / "u_squadrons.ini"
        tmp.write_text(text, encoding="utf-8")
        saved = bp.unit_file, bp.winning
        bp.unit_file = lambda uid: ("aircraft", tmp)
        bp.winning = lambda rel: tmp
        try:
            return bp.pick_nation("u", "Squadron1")
        finally:
            bp.unit_file, bp.winning = saved
            shutil.rmtree(tmp.parent, ignore_errors=True)

    def test_an_empty_or_commented_nation_falls_through_to_default(self):
        for body in ("Nation=\nName=No. 1 Sqn\n", "Nation=//todo\nName=x\n",
                     "Name=No. 1 Sqn\n", "Nation= \r\nName=x\r\n"):
            self.assertEqual(self._squadrons(f"[Squadron1]\n{body}[Default]\nNation=US\n"),
                             "US", repr(body))
        self.assertEqual(self._squadrons("[Squadron1]  ; RAAF\nNation=Australia  // 77 Sqn\n"
                                         "[Default]\nNation=US\n"), "Australia")
        self.assertIsNone(self._squadrons("[Squadron1]\nNation=\n[Default]\nName=x\n"))

    def test_picks_that_disagree_stop_the_build(self):
        saved = bp.pick_nation
        bp.pick_nation = lambda uid, pick: "Australia" if pick == "Squadron3" else "US"
        try:
            with self.assertRaises(SystemExit) as caught:
                bp.roster_nations([dict(unit="usn_p8", picks=["Squadron3", "Squadron1"],
                                        points=55)])
            self.assertIn("usn_p8", str(caught.exception))
        finally:
            bp.pick_nation = saved

    def test_a_unit_file_nation_that_disagrees_stops_the_build(self):
        saved = bp.unit_value
        bp.unit_value = lambda uid, key, depth=0: "US" if key == "Nation" else saved(uid, key)
        try:
            with self.assertRaises(SystemExit) as caught:
                bp.roster_nations([dict(unit="usn_p8", picks=["Squadron3"], points=55)])
            self.assertIn("Nation=US", str(caught.exception))
        finally:
            bp.unit_value = saved

    def test_a_discount_that_is_not_a_fraction_stops_the_build(self):
        self.assertEqual(bp.same_nation_discount("[CommanderSettings]\n"), 0.0)
        self.assertEqual(bp.same_nation_discount("SameNationUnitDiscount= 0.20\n"), 0.2)
        for bad in ("20", ".", "", "-0.1", "1"):
            with self.assertRaises(SystemExit):
                bp.same_nation_discount(f"SameNationUnitDiscount={bad}\n")

    def test_a_pick_with_no_declared_nation_stops_the_build(self):
        saved = bp.pick_nation
        bp.pick_nation = lambda uid, pick: None if uid == "usn_p8" else "Australia"
        try:
            with self.assertRaises(SystemExit) as caught:
                bp.roster_nations(bp.campaign_specs()[0]["ROSTER"])
            self.assertIn("usn_p8", str(caught.exception))
        finally:
            bp.pick_nation = saved


class AlliedFleet(unittest.TestCase):
    """The Open Allocation twin sells the allied fleet beside the campaign's
    roster: ships always, aircraft only where a row launches and recovers them."""

    @staticmethod
    def _missions():
        spec = bp.campaign_specs()[0]
        bp.set_campaign(spec)
        return spec, spec["MISSIONS"]

    def test_ships_are_kept_and_an_aircraft_no_row_takes_is_dropped(self):
        spec, missions = self._missions()
        saved = bp.airframe_rows
        bp.airframe_rows = lambda uid, m, placed: []
        try:
            kept, dropped = bp.usable_allied(
                [dict(unit="ran_ddg_hobart", picks=["Variant1"], points=480),
                 dict(unit="usn_p8", picks=["Squadron3"], points=55)],
                missions, {m["key"]: {} for m in missions})
        finally:
            bp.airframe_rows = saved
        self.assertEqual([e["unit"] for e in kept], ["ran_ddg_hobart"])
        self.assertEqual(dropped[0][0]["unit"], "usn_p8")
        self.assertIn("no air-tasking row", dropped[0][1])

    def test_an_aircraft_is_kept_only_where_every_row_recovers_it(self):
        spec, missions = self._missions()
        saved = bp.airframe_rows
        entry = [dict(unit="usn_p8", picks=["Squadron3"], points=55)]
        places = {m["key"]: {} for m in missions}
        try:
            bp.airframe_rows = lambda uid, m, placed: [("Patrol", 400.0, True, 1)]
            kept, _dropped = bp.usable_allied(entry, missions, places)
            self.assertEqual(len(kept), 1)
            bp.airframe_rows = lambda uid, m, placed: [("Patrol", 400.0, m is not missions[0], 1)]
            kept, dropped = bp.usable_allied(entry, missions, places)
            self.assertEqual(kept, [])
            self.assertIn("no field or deck in reach", dropped[0][1])
            # A row with no cockpit is never written, so it takes nothing.
            bp.airframe_rows = lambda uid, m, placed: [("Patrol", 400.0, True, 0)]
            kept, dropped = bp.usable_allied(entry, missions, places)
            self.assertEqual(kept, [])
        finally:
            bp.airframe_rows = saved

    def test_every_allied_entry_resolves_and_is_one_nation(self):
        import allied_fleet
        for nation, fleet in allied_fleet.FOR_NATION.items():
            units = [e["unit"] for e in fleet]
            self.assertEqual(len(units), len(set(units)), nation)
            bp.roster_nations(fleet)                    # one declared nation each
            self.assertTrue(all(isinstance(e["points"], int) and e["points"] > 0
                                for e in fleet))

    def test_the_twin_rules_page_names_the_submarine_missions(self):
        spec = dict(bp.campaign_specs()[0])
        spec["ROSTER"] = spec["ROSTER"] + [
            dict(unit="plan_type_054a_p5", picks=["Variant1"], points=280)]
        saved = bp.unit_type
        bp.unit_type = lambda uid, depth=0: ("Submarine" if uid == "plan_type_054a_p5"
                                             else saved(uid, depth))
        try:
            page = bp.campaign_rules(spec, open_allocation=True,
                                     submarine_missions=["Southern Lifeline"], allied=1)
            self.assertIn("A submarine sails only in a mission that includes one - "
                          "Southern Lifeline - and waits in reserve", page)
            self.assertIn("the allied fleet included", page)
            with self.assertRaises(SystemExit):
                bp.campaign_rules(spec, open_allocation=True, submarine_missions=[])
        finally:
            bp.unit_type = saved


class AlliedFleetReview(unittest.TestCase):
    """The review of 2e845dc9: the flight rule on allied aircraft, the allied
    sentence's grammar, and the gate on a twin that drifted."""

    def test_an_aircraft_whose_role_a_row_takes_without_its_fits_is_dropped(self):
        spec = bp.campaign_specs()[0]
        bp.set_campaign(spec)
        rows = [r for m in spec["MISSIONS"] for r in m.get("window", {}).get("flights", [])]
        authored = {u["type"] for m in spec["MISSIONS"] for u in m["units"] if u.get("slot")}
        saved = bp.airframe_rows
        bp.airframe_rows = lambda uid, m, placed: [("Attack", 400.0, True, 1)]
        try:
            kept, dropped = bp.usable_allied(
                [dict(unit="usaf_f-16cm-bl52d", picks=["Squadron1"], points=32)],
                spec["MISSIONS"], {m["key"]: {} for m in spec["MISSIONS"]},
                rows, spec["ROSTER"], authored)
        finally:
            bp.airframe_rows = saved
        self.assertEqual(kept, [])
        self.assertIn("offers none of its fits", dropped[0][1])

    def test_the_allied_sentence_reads_for_one_nation_and_for_several(self):
        commander = "CommanderNations=Australia\n"
        one = bp.allied_line([dict(unit="plan_j-15", picks=["Squadron1"])], commander)
        self.assertEqual(one, "The allied fleet is on sale beside it at full price: "
                              "1 class from China. ")
        two = bp.allied_line([dict(unit="plan_j-15", picks=["Squadron1"]),
                              dict(unit="usn_fa-18f_blk3", picks=["Squadron8"]),
                              dict(unit="usn_p8_2027", picks=["Squadron1"])], commander)
        self.assertIn("2 classes from China and USA.", two)
        self.assertEqual(bp.allied_line([dict(unit="usn_p8", picks=["Squadron3"])],
                                        commander), "")

    def test_the_gate_refuses_a_twin_that_drifted(self):
        pack = bp.ROOT / "integration" / "campaign" / "SEST_Campaign"
        slug = "sest-red-line"
        if not (pack / "campaigns" / bp.open_slug(slug)).is_dir():
            self.skipTest("pack not built")
        tmp = Path(tempfile.mkdtemp())
        try:
            for s in (slug, bp.open_slug(slug)):
                shutil.copytree(pack / "campaigns" / s, tmp / "campaigns" / s)
            self.assertEqual(coverage_check.open_twin(tmp, slug)[:1], [])
            ini = tmp / "campaigns" / bp.open_slug(slug) / "campaign.ini"
            good = ini.read_text(encoding="utf-8")
            for bad in (good.replace("Description=OPEN ALLOCATION - ",
                                     "Description=OPEN ALLOCATION - junk ", 1),
                        good.replace("|plan_z-9c,Squadron1", "", 1)):
                self.assertNotEqual(bad, good)
                ini.write_text(bad, encoding="utf-8")
                self.assertTrue(coverage_check.open_twin(tmp, slug))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class RulesPage(unittest.TestCase):
    """The Campaign Rules button opens campaign_rules_en.xml; each campaign's
    page is the stock one with its own passages and thresholds in place."""

    def test_each_page_parses_and_carries_only_its_own_campaign(self):
        import xml.dom.minidom
        for spec in bp.campaign_specs():
            page = bp.campaign_rules(spec)
            xml.dom.minidom.parseString(page.encode("utf-8"))
            self.assertIn(f'Text="{bp._xml_text(spec["TITLE"])} - Task Force Mode"', page)
            for stock in ("Pacific Strike", "Japan", "optional side missions",
                          "include their airwing for free"):
                self.assertNotIn(stock, page, f"{spec['SLUG']}: {stock}")

    def test_the_survived_missions_column_is_the_campaigns_thresholds(self):
        spec = dict(bp.campaign_specs()[0])
        spec["TASKFORCE"] = dict(spec["TASKFORCE"], CrewSkillThresholds=
                                 "Trained:3|Seasoned:6|Veterans:11|Ultra:23")
        page = bp.campaign_rules(spec)
        table = page[page.index('Text="Survived Missions"'):]
        cells = re.findall(r'Grid\.Row="\d" Grid\.Column="1"[^>]*><TextBlock Text="([^"]*)"',
                           table)
        # Since 0.8.3 the game fills the column from CrewSkillThresholds
        # itself: the page carries its bindings, not our numbers.
        self.assertEqual(cells, [f"{{Binding {lvl}CrewSkillSurvivalRequirement}}" for lvl in
                                 ("Green", "Trained", "Seasoned", "Veterans", "Ultra")])


class DefectorEscortFeatures(unittest.TestCase):
    """TS11A's three builder features: waypoint orders (a salvo at one named
    ship), disable= (weapons off from the first second) and lift= (a
    restraint that stops binding at hostile intent). Each emits only stock
    keys; a mission without them renders byte-for-byte as before."""

    CENTRE = (-37.28, 150.45)
    STATIONS = {"escort": S(-37.12, 150.35, "Detachment", heading=140),
                "defector": S(-37.36, 150.61, "The corvette", heading=295),
                "frigate": S(-37.47, 150.91, "Type 054A", heading=295),
                "helo": S(-37.41, 150.75, "Z-9", heading=295, alt=1000)}
    ANZAC = dict(side="blue", mod="SEST_RAN_Fleet", type="ran_ffh_anzac",
                 station="escort", variant="Variant7", weapons="Tight")
    CORVETTE = dict(side="blue", mod="modern-plan-systems", type="plan_type_056a",
                    station="defector", name="The corvette", weapons="Hold",
                    route=[(-37.18, 150.12, 0)], telegraph=4, disable=("weapons",))
    Z9 = dict(side="red", mod="modern-plan-systems", type="plan_z-9c", station="helo",
              loadout="ASWHunter", weapons="Tight", alt=1000,
              route=[(-37.38, 150.67, 1000), (-37.29, 150.42, 1000)], loop=True)

    def setUp(self):
        del bp.PLACEMENT_PROBLEMS[:]

    def frigate(self, orders=None, **over):
        orders = orders if orders is not None else [
            ("AttackAtWaypoint", "plan_yj-83a", "defector", 2)]
        return dict(dict(side="red", mod="modern-plan-systems", type="plan_type_054a_p5",
                         station="frigate", weapons="Tight", telegraph=5,
                         route=[(-37.42, 150.78, 0, orders), (-37.50, 150.62, 0)]),
                    **over)

    def mission(self, units, **over):
        m = dict(key="Test Line", code="T11A", num="11A", group="optional",
                 brief="Brief.", win="Won.", lose="Lost.", timeout="Out of time.",
                 date=(2029, 2, 27), time=(4, 55), sea=3, clouds="Clear", wind="NE",
                 centre=self.CENTRE, blue_nation="Australia", red_nation="China",
                 minutes=80, role="escort", generation="Generated", anchor="escort",
                 stations=self.STATIONS, units=units,
                 objectives=[("Protection", "Bring her in", "30,-30,Fail,Main"),
                             ("Restraint", "Do not fire first", "15,-30,Complete")],
                 victory=dict(kind="arrive", station="defector", at=(-37.18, 150.12),
                              radius=9, objective="Protection"),
                 fatal=[F("Protection", ["defector"])],
                 resolve={"Protection": "victory",
                          "Restraint": ("spare", "frigate", "helo")})
        m.update(over)
        return m

    def place(self, m):
        return bp.place(m, bp.CoastPlacer(bp.coast_data(), m))

    def sections(self, placed):
        return {tag: keys for entries in placed.values() for tag, keys, _n, _x in entries}

    def test_attack_names_the_corvettes_section_and_overrides_status(self):
        m = self.mission([self.ANZAC, self.CORVETTE, self.frigate()])
        placed, members, _c, _f = self.place(m)
        frigate = self.sections(placed)["Taskforce2Vessel1"]
        self.assertEqual(frigate["Waypoints"],
                         "19.80,0,-8.40/AttackAtWaypoint,plan_yj-83a,Taskforce1Vessel2,2"
                         "|10.20,0,-13.20")
        self.assertEqual(frigate["OverrideWeaponStatus"], "Tight")

    def test_telegraph_and_status_orders(self):
        m = self.mission([self.ANZAC, self.CORVETTE, self.frigate(
            [("SetTelegraph", 2), ("SetWeaponStatus", "Hold")])])
        placed, _m, _c, _f = self.place(m)
        frigate = self.sections(placed)["Taskforce2Vessel1"]
        self.assertTrue(frigate["Waypoints"].startswith(
            "19.80,0,-8.40/SetTelegraph,2/SetWeaponStatus,Hold|"))
        self.assertNotIn("OverrideWeaponStatus", frigate)

    def test_a_route_without_orders_is_unchanged(self):
        plain = dict(self.frigate(), route=[(-37.42, 150.78, 0), (-37.50, 150.62, 0)])
        m = self.mission([self.ANZAC, self.CORVETTE, plain])
        placed, _m, _c, _f = self.place(m)
        self.assertEqual(self.sections(placed)["Taskforce2Vessel1"]["Waypoints"],
                         "19.80,0,-8.40|10.20,0,-13.20")

    def test_orders_are_refused_when_they_cannot_be_carried_out(self):
        bad = [
            [("Ram", "defector")],                                    # unknown
            [("SetTelegraph", 7)],                                    # out of range
            [("SetWeaponStatus", "Weapons free")],                   # not a status
            [("AttackAtWaypoint", "usn_rgm-84d", "defector", 2)],     # not carried
            [("AttackAtWaypoint", "plan_yj-83a", "defector", 0)],     # no rounds
            [("AttackAtWaypoint", "plan_yj-83a", "helo", 2)],         # own side
        ]
        for orders in bad:
            del bp.PLACEMENT_PROBLEMS[:]
            m = self.mission([self.ANZAC, self.CORVETTE, self.Z9, self.frigate(orders)])
            with self.assertRaises(SystemExit, msg=repr(orders)):
                self.place(m)

    def test_disable_emits_north_borneos_trigger(self):
        m = self.mission([self.ANZAC, self.CORVETTE, self.Z9, self.frigate()])
        placed, members, _c, _f = self.place(m)
        self.assertEqual(m["_disabled"], [("Taskforce1Vessel2", ("weapons",))])
        triggers = rendered(m, placed, members)
        self.assertEqual(triggers["Systems disabled at start"], [
            "Condition_Condition1_Type=OnMissionStart",
            "ConditionsCompleted=<Condition1>",
            "Action_Units=Taskforce1Vessel2",
            "Action_EnableDisableWeaponSystems=Disable"])

    def test_a_disarmed_hull_is_not_her_own_escort(self):
        # The detachment 150 NM away cannot reach her in 80 minutes. Counted
        # as armed, the corvette would be her own escort at 0 NM and pass.
        stations = dict(self.STATIONS, escort=S(-35.00, 152.50, "Far detachment"))
        m = self.mission([self.ANZAC, self.CORVETTE, self.Z9, self.frigate()],
                         stations=stations)
        placed, members, _c, _f = self.place(m)
        del bp.CLOSURE_PROBLEMS[:]
        bp.check_closure(m, placed, members)
        problems = list(bp.CLOSURE_PROBLEMS)
        del bp.CLOSURE_PROBLEMS[:]
        self.assertTrue(any("Taskforce1Vessel2" in p and "Taskforce1Vessel1" in p
                            for p in problems), problems)

    def test_disable_is_refused_on_the_anchor_and_unknown_systems(self):
        for anchor in (dict(self.ANZAC, disable=("weapons",)),):
            m = self.mission([anchor, self.CORVETTE, self.frigate()])
            with self.assertRaises(SystemExit):
                self.place(m)
        m = self.mission([self.ANZAC, dict(self.CORVETTE, disable=("guns",)),
                          self.frigate()])
        with self.assertRaises(SystemExit):
            self.place(m)

    def test_lift_switches_off_exactly_the_restraint_trigger(self):
        lift = [dict(objective="Restraint", units=["frigate"], at=(-37.42, 150.78),
                     radius=2.5, intel="BLUEFIN 31: Hostile intent.")]
        m = self.mission([self.ANZAC, self.CORVETTE, self.Z9, self.frigate()], lift=lift)
        placed, members, _c, _f = self.place(m)
        _name, text = bp.render(m, placed, members)
        numbers = {}
        for chunk in text.split("\n\n"):
            rows = chunk.strip().splitlines()
            if rows and rows[0].startswith("[Trigger"):
                numbers[rows[1].partition("=")[2]] = (rows[0].split("]")[0][1:], rows[2:])
        broken, _ = numbers["Restraint broken"]
        _tag, lifted = numbers["Restraint lifted"]
        self.assertIn(f"Action_DisableTriggers={broken}", lifted)
        self.assertIn("Condition_Condition1_AreaDisplaySide=None", lifted)
        self.assertIn("Action_Taskforce1_Intel=RestraintLiftIntel", lifted)
        self.assertIn("RestraintLiftIntel=BLUEFIN 31: Hostile intent.", text)
        rendered(m, placed, members)            # the pack checker's integrity pass

    def test_lift_is_refused_when_it_could_never_fire_or_is_not_a_restraint(self):
        units = [self.ANZAC, self.CORVETTE, self.Z9, self.frigate()]
        cases = [
            dict(objective="Protection", units=["frigate"], at=(-37.42, 150.78), radius=2.5),
            dict(objective="Restraint", units=["defector"], at=(-37.42, 150.78), radius=2.5),
            dict(objective="Restraint", units=["frigate"], at=(-37.00, 151.40), radius=2.5),
        ]
        for lift in cases:
            del bp.PLACEMENT_PROBLEMS[:]
            m = self.mission(units, lift=[dict(lift, intel="x")])
            placed, members, _c, _f = self.place(m)
            with self.assertRaises(SystemExit, msg=repr(lift)):
                bp.render(m, placed, members)


class BriefingChartSupport(unittest.TestCase):
    """An unarmed aircraft far from the ships is named, not charted.

    The wider forces put tankers 130-280 NM behind the fighters and a Midas
    behind the Bear; charted, they tripled the span of TS09, TS11 and SR07.
    A Hold aircraft near the ships (SR05's Triton at 102 NM), an armed one
    far out, and every surface unit stay on the chart."""

    def setUp(self):
        sys.path.insert(0, str(HERE.parent / "missions"))
        import briefing_maps
        self.bm = briefing_maps

    @staticmethod
    def _u(kind, lat, lon, hold=False, side="friend"):
        return dict(kind=kind, lat=lat, lon=lon, hold=hold, side=side, key=f"{kind}{lat}")

    def test_far_tanker_is_named_near_triton_is_drawn(self):
        ships = [self._u("Vessel", -40.0, 140.0), self._u("Vessel", -40.1, 140.1)]
        tanker = self._u("Aircraft", -36.2, 140.0, hold=True)    # ~230 NM
        triton = self._u("Aircraft", -38.4, 140.0, hold=True)    # ~100 NM
        fighter = self._u("Aircraft", -36.0, 140.0)              # far, armed
        kept, named, far = self.bm.off_chart(ships + [tanker, triton, fighter], 350)
        self.assertEqual(named, [tanker])
        self.assertIn(triton, kept)
        self.assertIn(fighter, kept)
        self.assertEqual(len(far.centre), 2)

    def test_far_field_rule_unchanged(self):
        ships = [self._u("Vessel", -43.0, 147.5)]
        field = self._u("LandUnit", -34.7, 138.6)                # Edinburgh, ~640 NM
        kept, named, _far = self.bm.off_chart(ships + [field], 350)
        self.assertEqual(named, [field])
        self.assertEqual(kept, ships)

    def test_no_ships_no_support_rule(self):
        planes = [self._u("Aircraft", -40.0, 140.0), self._u("Aircraft", -30.0, 140.0, hold=True)]
        kept, named, _far = self.bm.off_chart(planes, 350)
        self.assertEqual(named, [])
        self.assertEqual(kept, planes)


class CoverageGeography(unittest.TestCase):
    """The coverage report says how positions were placed, per campaign.

    It said every campaign snapped to points from a loading mission, "0.0 NM"
    included, while Southern Reach places every position as authored against
    the coastline extract and Red Line does so in two of its six."""

    MISSIONS = [dict(units=[]), dict(units=[]), dict(units=[])]

    def _sentence(self, pooled):
        text = bp.report([], self.MISSIONS, 6.7, pooled=pooled)
        return next(l for l in text.splitlines() if l.startswith("Sea and land"))

    def test_all_pooled_keeps_the_snap_sentence(self):
        line = self._sentence(3)
        self.assertIn("snapped to points already used by a loading mission", line)
        self.assertIn("6.7 NM", line)
        self.assertEqual(line, self._sentence(None))    # the old default

    def test_all_coast_says_nothing_was_snapped(self):
        line = self._sentence(0)
        self.assertIn("used as authored and checked against the coastline", line)
        self.assertNotIn("NM", line)

    def test_mixed_names_both_halves(self):
        line = self._sentence(2)
        self.assertIn("in 2 of the 3 missions are snapped", line)
        self.assertIn("6.7 NM", line)
        self.assertIn("the other 1 use them as authored", line)



class ClockAndSea(unittest.TestCase):
    """The planned window, the deadline behind it, and the sea's price."""

    def test_window_closes_with_a_message_and_the_mission_is_lost_later(self):
        t = rendered(small_mission())          # small_mission plans 80 minutes
        self.assertIn("Condition_Time=4800", t["Window closed"])
        self.assertIn("Action_Taskforce1_Message=BehindScheduleMessage", t["Window closed"])
        self.assertIn("Condition_Time=7200", t["Deadline"])       # 80 x 1.5
        self.assertIn("Action_Victory=Taskforce2", t["Deadline"])
        self.assertNotIn("Action_Victory=Taskforce2", t["Window closed"])

    def test_deadline_is_half_as_long_again(self):
        self.assertEqual(bp.deadline_minutes({"minutes": 60}), 90)
        self.assertEqual(bp.deadline_minutes({"minutes": 45}), 68)

    def test_only_ships_pay_for_the_sea(self):
        calm, rough = {"sea": 2}, {"sea": 5}
        self.assertEqual(bp.ship_speed("Vessel", calm), 18.0)
        self.assertAlmostEqual(bp.ship_speed("Vessel", rough), 18.0 * 0.45)
        self.assertAlmostEqual(bp.ship_speed("Vessel", rough, calm=9.0), 9.0 * 0.45)
        self.assertEqual(bp.ship_speed("Submarine", rough), 10.0)
        self.assertEqual(bp.ship_speed("Aircraft", rough), 300.0)
        self.assertEqual(bp.sea_factor({"sea": 9}), 0.25)       # off the table: the worst row
        self.assertEqual(bp.sea_factor({}), 1.0)

    def test_a_held_stage_comes_off_the_window(self):
        held = {"after": dict(kind="area", units=["a"], at_unit="a", radius=5,
                              after_minutes=30)}
        self.assertEqual(bp.hold_minutes(held), 30)
        self.assertEqual(bp.hold_minutes({"after": dict(kind="classify", units="x")}), 0)
        self.assertEqual(bp.hold_minutes({}), 0)

    def test_timeout_figures_are_the_builders(self):
        m = dict(small_mission(), time=(7, 10), minutes=75)
        self.assertEqual(bp.clock_text(m, "{Deadline} minutes; {deadline}; {deadline_clock}."),
                         "One hundred and twelve minutes; one hundred and twelve; 0902.")
        self.assertEqual(bp.number_words(68), "sixty-eight")
        self.assertEqual(bp.number_words(100), "one hundred")
        self.assertEqual(bp.number_words(135), "one hundred and thirty-five")
        for bad in ("Seventy-five minutes and the ships are still south.",
                    "0820, and FUJIAN is short of her station.",
                    "has not met the requirement within ninety minutes.",
                    "No more than 90 minutes."):
            with self.assertRaisesRegex(SystemExit, "names a time", msg=bad):
                bp.check_message_texts(dict(small_mission(), timeout=bad))
        bp.check_message_texts(dict(small_mission(),
                                    timeout="{Deadline} minutes and HULL 419 is short of the box."))


if __name__ == "__main__":
    unittest.main(verbosity=2)
