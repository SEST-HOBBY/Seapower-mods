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
import collections
import contextlib
import copy
import importlib.abc
import io
import json
import re
import shutil
import subprocess
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
PACK = Path(bp.__file__).resolve().parent / "SEST_Campaign"
_STORY = {}


def story_windows():
    """{slug: {mission code: dict(buy, allow, situation)}} - every
    campaign's windows as its story writes them, before the reserve
    (mission_depth.apply_reserve) touches one. Read in a fresh interpreter
    with apply_reserve switched off, because the first campaign_specs() in
    this one has already opened the windows the campaign modules share."""
    if not _STORY:
        code = "\n".join([
            "import json, sys",
            f"sys.path.insert(0, {str(HERE)!r})",
            "import mission_depth",
            "mission_depth.apply_reserve = lambda specs: None",
            "import build_pack",
            "out = {s['SLUG']: {mission_depth.code_of(m): dict(",
            "    buy=bool(m.get('window', {}).get('buy')),",
            "    allow=m.get('window', {}).get('allow'),",
            "    situation=m.get('window', {}).get('situation', ''))",
            "    for m in s['MISSIONS']} for s in build_pack.campaign_specs()}",
            "print('STORY ' + json.dumps(out))"])
        run = subprocess.run([sys.executable, "-B", "-c", code], cwd=HERE,
                             capture_output=True, text=True)
        if run.returncode:
            raise AssertionError(run.stderr)
        _STORY.update(json.loads(next(x for x in run.stdout.splitlines()
                                      if x.startswith("STORY "))[6:]))
    return _STORY


def built_twin(slug, tmp):
    """`slug`'s Open Allocation twin, built into tmp/campaigns/<slug>-open
    from the built base campaign (copied beside it) the way main() builds
    one for a spec with OPEN_ALLOCATION. No campaign in the pack opts in
    since 21 Oct 2026, so this is what keeps open_allocation_twin(),
    write_open_twin(), OPEN_HOLD and the gate's open_twin() checked against
    the shipped campaigns. None when the pack is not built.

    No placements are passed: usable_allied keeps an allied aircraft only
    where a placed mission's row takes it, and the two campaigns built here
    leave their twins no fleet at all - Red Line's PLAN support ships are on
    its roster through the reserve since 21 Oct 2026, and Sulu Line's
    commander calls on none - so the spine, rules page, rosters and
    commander settings are the ones main() would write. REQUIRED-MODS.txt is not: no
    play credits or coverage rows are passed, so it lists only the mods the
    twin's roster reaches, and no test reads it.
    """
    base = PACK / "campaigns" / slug
    if not (base / "campaign.ini").is_file():
        return None
    spec = next(s for s in bp.campaign_specs() if s["SLUG"] == slug)
    bp.set_campaign(spec)
    shutil.copytree(base, tmp / "campaigns" / slug)
    missions = spec["MISSIONS"]
    rows = [r for m in missions for r in m.get("window", {}).get("flights", [])]
    authored = {u["type"] for m in missions for u in m["units"] if u.get("slot")}
    twin = bp.open_allocation_twin(spec, (base / "campaign.ini").read_text(encoding="utf-8"),
                                   missions, {}, rows, authored)
    bp.write_open_twin(tmp, spec, twin)
    return twin


class SailedLegs(unittest.TestCase):
    """Wet endpoints must not let a ship cross an island between them."""

    def setUp(self):
        self.before = bp.PLACEMENT_PROBLEMS[:]
        bp.PLACEMENT_PROBLEMS.clear()
        self.placer = bp.CoastPlacer(bp.coast_data({"centre": (-5.8, 132.7)}), {})

    def tearDown(self):
        bp.PLACEMENT_PROBLEMS[:] = self.before

    def test_the_reported_kai_crossing_is_rejected_with_wet_endpoints(self):
        start, end = (-5.7, 133.1), (-6.05, 132.65)
        self.assertFalse(self.placer.coast.on_land(*start))
        self.assertFalse(self.placer.coast.on_land(*end))
        self.placer.route(start, [end], "Weather Alternate raider")
        self.assertTrue(bp.PLACEMENT_PROBLEMS)
        self.assertIn("leg 1 crosses", bp.PLACEMENT_PROBLEMS[0])

    def test_a_bend_through_the_passage_is_accepted(self):
        self.placer.route((-5.90, 132.82),
                          [(-5.80, 132.84), (-5.72, 132.86), (-5.66, 132.84)],
                          "Weather Alternate fuel coaster")
        self.assertEqual(bp.PLACEMENT_PROBLEMS, [])

    def test_the_spawn_to_first_waypoint_is_checked(self):
        self.placer.route((-5.8, 132.7), [(-5.8, 132.84)], "Beached start")
        self.assertIn("leg 1 crosses land", bp.PLACEMENT_PROBLEMS[0])

    def test_a_route_outside_the_extract_is_not_silently_approved(self):
        self.placer.route((-5.8, 144), [(-5.8, 145)], "Outside chart")
        self.assertIn("outside the coastline extract", bp.PLACEMENT_PROBLEMS[0])

    def test_wider_clearance_rejects_the_in_game_reported_eastern_passage(self):
        self.placer.route((-5.90, 132.82),
                          [(-5.80, 132.84), (-5.72, 132.86), (-5.66, 132.84)],
                          "Weather Alternate old passage", least=4)
        self.assertTrue(bp.PLACEMENT_PROBLEMS)
        self.assertIn("4 NM shore margin", bp.PLACEMENT_PROBLEMS[0])

    def test_route_clearance_cannot_disable_validation(self):
        for least in (0, -1, float("nan"), float("inf")):
            with self.assertRaisesRegex(SystemExit, "finite and positive"):
                self.placer.route((-5.96, 132.48), [(-5.72, 132.50)],
                                  "Weather Alternate", least=least)


class SouthernWatchFollowup(unittest.TestCase):
    """Exercise the real mission placements behind the reported regressions."""

    @classmethod
    def setUpClass(cls):
        from campaign_data import MISSIONS
        cls.missions = {}
        cls.placements = {}
        for num in ("08", "O4"):
            mission = copy.deepcopy(next(m for m in MISSIONS if m["num"] == num))
            placed, members, _credits, _worst = bp.place(
                mission, bp.CoastPlacer(bp.coast_data(mission), mission))
            cls.missions[num] = mission
            cls.placements[num] = placed

    def test_carrier_is_south_of_papua_with_open_water_clearance(self):
        mission = self.missions["08"]
        keys = self.placements["08"]["Taskforce1Vessel"][0][1]
        x, _y, z = map(float, keys["RelativePositionInNM"].split(","))
        at = (mission["centre"][0] + z / 60, mission["centre"][1] + x / 60)
        self.assertLess(at[0], -6)
        self.assertFalse(bp.coast_data(mission).on_land(*at))
        self.assertGreater(bp.coast_data(mission).nm_to_coast(*at), 20)

    def test_langgur_has_a_modern_wing_with_room_for_recoveries(self):
        keys = self.placements["08"]["Taskforce1LandUnit"][0][1]
        self.assertEqual(keys["CustomAirGroup"], "True")
        self.assertIn("usaf_f-16cm-bl52d", keys)
        self.assertIn("dts_saab_ge", keys)
        self.assertNotIn("usaf_f-4e", keys)
        self.assertNotIn("usn_ea-6b", keys)
        from campaign_data import LANGGUR_AIR_GROUP
        self.assertLess(sum(n for _t, _s, n in LANGGUR_AIR_GROUP) + 7,
                        bp.deck_size(keys["Type"]))

    def test_texaco_is_available_without_a_campaign_flag_and_bonus_remains_gated(self):
        rows = {name: keys for _tag, keys, name, _x
                in self.placements["08"]["Taskforce1Aircraft"]}
        self.assertNotIn("SpawnByVariableAND", rows["Texaco 52"])
        self.assertIn("HomeBase", rows["Texaco 52"])
        self.assertTrue(rows["Texaco 52"]["Waypoints"].endswith("|Loop"))
        self.assertEqual(rows["Texaco 53"]["SpawnByVariableAND"],
                         "O4LanggurStocked,IsTrue")

    def test_emitted_coaster_tracks_stay_well_offshore_and_stop_in_the_goal(self):
        mission = self.missions["O4"]
        coast = bp.coast_data(mission)
        centre = mission["centre"]
        for _tag, keys, name, _x in self.placements["O4"]["Taskforce1Vessel"]:
            if name not in ("MV Langgur Provider", "MV Kei Star"):
                continue
            def geo(point):
                x, _y, z = map(float, point.split("/")[0].split(","))
                return (centre[0] + z / 60, centre[1] + x / 60)
            route = [geo(keys["RelativePositionInNM"])]
            route.extend(geo(w) for w in keys["Waypoints"].split("|"))
            for a, b in zip(route, route[1:]):
                for i in range(101):
                    at = (a[0] + (b[0] - a[0]) * i / 100,
                          a[1] + (b[1] - a[1]) * i / 100)
                    self.assertFalse(coast.on_land(*at), name)
                    self.assertGreater(coast.nm_to_coast(*at), 8, name)
            self.assertIn("/SetTelegraph,0", keys["Waypoints"].split("|")[-1])
            self.assertLess(bp.nm_between(route[-1], mission["victory"]["at"]),
                            mission["victory"]["radius"])
            self.assertLess(sum(bp.nm_between(a, b) for a, b in zip(route, route[1:])),
                            13 * mission["minutes"] / 60)



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
        # Sulu Line registers the same way, after Red Line. These tests are
        # about the red_line slot, so the fourth package is held absent
        # unless a test puts it back.
        self.saved_sl = sys.modules.get("sulu_line", _ABSENT)
        sys.modules["sulu_line"] = None

    def tearDown(self):
        for name, saved in (("red_line", self.saved), ("sulu_line", self.saved_sl)):
            if saved is _ABSENT:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = saved

    def test_sulu_line_is_appended_after_red_line(self):
        if self.saved_sl is _ABSENT:
            sys.modules.pop("sulu_line", None)
        else:
            sys.modules["sulu_line"] = self.saved_sl
        sys.modules["red_line"] = self.fake_red_line()
        self.assertEqual([s["SLUG"] for s in bp.campaign_specs()],
                         ["sest-southern-watch", "sest-southern-reach", "sest-red-line",
                          "sest-sulu-line"])

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

    def test_a_ship_with_dated_fits_sails_the_fit_in_service_by_the_mission_year(self):
        # Euromod's Anzac dates its fits (Default 2011, AMCAP 2019, AMCAP Late
        # 2025). Writing Default sent a 2028 campaign out without NSM.
        kind_dir, path = bp.unit_file("ran_ffh_anzac")
        self.assertEqual(bp.pick_loadout("ran_ffh_anzac", path, None, 2028)[0], "AMCAP Late")
        self.assertEqual(bp.pick_loadout("ran_ffh_anzac", path, None, 2020)[0], "AMCAP")
        self.assertEqual(bp.pick_loadout("ran_ffh_anzac", path, None, 2015)[0], "Default")
        # a declared fit still wins, and no year keeps the old rule
        self.assertEqual(bp.pick_loadout("ran_ffh_anzac", path, "AMCAP", 2028)[0], "AMCAP")
        self.assertEqual(bp.pick_loadout("ran_ffh_anzac", path, None)[0], "Default")
        # ties go to the first offered: the Hobart's five 2025 fits -> Late
        _k, hob = bp.unit_file("ran_ddg_hobart")
        self.assertEqual(bp.pick_loadout("ran_ddg_hobart", hob, None, 2028)[0], "Late")


class QuietOpening(OpeningRanges):
    """The stricter gate of 13 October (Fujian's Shadow): nothing red can fire
    in the first OPENING_QUIET_MIN minutes. A standoff bomber may not start
    inside its own launch range however long it is; a radar aircraft's
    picture is a track for every ship and boat; air-to-air reach counts; a
    unit that joins later (enter=) is held to the raid rule where it joins."""

    STATIONS = dict(OpeningRanges.STATIONS,
                    bomber=S(-47.50, 143.80, "Bomber", alt=30000),   # 198 NM east
                    aew=S(-47.50, 142.20, "AEW", alt=26000),         # 102 NM east
                    cap=S(-47.50, 142.10, "CAP", alt=30000),         # 96 NM east
                    patrol=S(-47.50, 140.40, "Patrol", alt=20000))   # over the tender
    BOMBER = dict(side="red", mod="plaaf-aircraft-pack", type="plaaf_h-6k_late",
                  station="bomber", loadout="AntiShip")
    AEW = dict(side="red", mod="type-003-004-maneuverwarfare", type="pla_kj-600",
               station="aew", weapons="Hold")
    RED_BOAT = dict(side="red", mod="plan-submarines", type="plan_ssn_type_093b",
                station="far_boat", depth="belowlayer")
    J16 = dict(side="red", mod="j-16-multirole", type="plaaf_j16", station="cap")
    # A player aircraft in the air, with the blue 054A (DECOY) as its deck.
    HELO = dict(side="blue", mod="modern-plan-systems", type="plan_z-9c",
                station="patrol", weapons="Hold")

    def opening(self, units):
        del bp.OPENING_PROBLEMS[:]
        return super().opening(units)

    def test_a_standoff_bomber_in_its_own_reach_is_refused(self):
        problems = self.opening([self.BOMBER])
        self.assertEqual(len(problems), 1)
        self.assertIn("so the raid is seen coming", problems[0])

    def test_the_same_bomber_joining_after_the_quiet_minutes_is_a_raid(self):
        self.assertEqual(self.opening([dict(self.BOMBER, enter=10)]), [])

    def test_joining_inside_the_quiet_minutes_is_the_start(self):
        self.assertEqual(len(self.opening([dict(self.BOMBER, enter=3)])), 1)

    def test_a_radar_aircraft_gives_a_boat_her_track(self):
        self.assertEqual(self.opening([self.RED_BOAT]), [])
        problems = self.opening([self.RED_BOAT, self.AEW])
        self.assertEqual(len(problems), 1)
        self.assertIn("radar on her", problems[0])
        self.assertEqual(self.opening([self.RED_BOAT, dict(self.AEW, enter=8)]), [])

    def test_a_fighter_in_air_to_air_reach_of_a_player_aircraft_is_refused(self):
        problems = self.opening([self.DECOY, self.HELO, self.J16])
        self.assertEqual(len(problems), 1)
        self.assertIn("air-to-air reach", problems[0])
        self.assertEqual(self.opening([self.DECOY, self.HELO, dict(self.J16, enter=5)]), [])

    def test_enter_switches_the_unit_off_until_its_minute(self):
        m, placed, _members = self.placed([self.TENDER, dict(self.BOMBER, enter=7.5)])
        (tag, keys, _n, _x), = placed["Taskforce2Aircraft"]
        self.assertEqual(keys["Disabled"], "True")
        self.assertEqual(m["_enter"], {tag: 7.5})

    def test_enter_is_a_red_minute_inside_the_plan(self):
        for bad in (dict(self.TENDER, enter=5), dict(self.BOMBER, enter=0),
                    dict(self.BOMBER, enter=80), dict(self.BOMBER, enter=True)):
            with self.assertRaises(SystemExit, msg=repr(bad)):
                self.placed([self.TENDER, bad] if bad["side"] == "red" else [bad])


class JoiningTrigger(unittest.TestCase):
    """enter= on the page: Disabled=True on the unit and stock's own timed
    Action_SetEnabledStatus trigger (01A Senkaku Run Trigger4), checked by
    the pack checker; and one formation joins together."""

    def test_the_trigger_is_stocks_and_the_checker_reads_it(self):
        placed, members = small_placement()
        placed["Taskforce2Aircraft"][0][1]["Disabled"] = "True"
        m = small_mission(_enter={"Taskforce2Aircraft1": 7})
        triggers = rendered(m, placed, members)
        self.assertEqual(triggers["Joins at minute 7"],
                         ["Condition_Condition1_Type=Time",
                          "Condition_Condition1_Time=420",
                          "ConditionsCompleted=<Condition1>",
                          "Action_SetEnabledStatus=True",
                          "Action_Units=Taskforce2Aircraft1"])
        _name, text = bp.render(small_mission(), placed, members)
        problems = coverage_check.trigger_integrity(HERE / "t.ini", text,
                                                    coverage_check.blocks(text))
        self.assertTrue(any("Disabled=True and no trigger switches it on" in p
                            for p in problems), problems)

    def test_one_formation_joins_at_one_minute(self):
        placed, members = small_placement()
        placed["Taskforce2Aircraft"].append(
            ("Taskforce2Aircraft2", _keys("usn_p8", 30.5, 36), None, False))
        members["red_air"].append("Taskforce2Aircraft2")
        with self.assertRaisesRegex(SystemExit, "join at different minutes"):
            bp.render(small_mission(_enter={"Taskforce2Aircraft1": 7}), placed, members)


class DeckLists(unittest.TestCase):
    """deck_fit reads the deck the way the game does: the `Helicopters`
    wildcard takes every helicopter (29 vanilla hulls, the Burkes among
    them - refused here until 13 Oct), and SEST Cross-Deck's extended list
    replaces the winning file's where a stub is built."""

    def test_the_helicopters_wildcard_takes_a_helicopter_and_not_a_jet(self):
        self.assertEqual(bp.unit_value("usn_ddg_burke_f3_125", "AircraftSupported"),
                         "Helicopters")
        self.assertEqual(bp.deck_fit("usn_mh-60r", "Helicopter", "usn_ddg_burke_f3_125", True), 0)
        self.assertIsNone(bp.deck_fit("usn_f-35c", "Aircraft", "usn_ddg_burke_f3_125", True))

    def test_a_cross_deck_stub_extends_the_deck(self):
        tmp = Path(tempfile.mkdtemp())
        saved = bp.CROSS_DECK
        bp.CROSS_DECK = tmp
        try:
            self.assertIsNone(bp.deck_fit("usn_mh-60r", "Helicopter", "rn_ddg_type45_26", True))
            (tmp / "rn_ddg_type45_26_CrossDeck_SEST.ini").write_text(
                "#!extend vessels/rn_ddg_type45_26.ini\n\n[FlightDeck]\n"
                "AircraftSupported=rn_sea_lynx_mk8,rn_merlin_hm2,rn_aw159,usn_mh-60r\n",
                encoding="utf-8")
            self.assertEqual(bp.deck_fit("usn_mh-60r", "Helicopter", "rn_ddg_type45_26", True), 0)
            self.assertIsNone(bp.deck_fit("fr_nh90", "Helicopter", "rn_ddg_type45_26", True))
        finally:
            bp.CROSS_DECK = saved
            shutil.rmtree(tmp, ignore_errors=True)

    def test_the_built_pack_keeps_every_type_the_hull_listed(self):
        stubs = sorted(bp.CROSS_DECK.glob("*_CrossDeck_SEST.ini"))
        if not stubs:
            self.skipTest("SEST Cross-Deck not built")
        for stub in stubs:
            uid = stub.name[:-len("_CrossDeck_SEST.ini")]
            text = stub.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"#!extend vessels/{uid}.ini\n"), stub.name)
            own = bp.unit_value(uid, "AircraftSupported")
            self.assertTrue(own and "Helicopters" not in own, uid)
            new = bp.deck_types(uid).split(",")
            self.assertEqual(new[:len(own.split(","))], own.split(","), uid)
            self.assertEqual(len(new), len(set(new)), uid)


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
                        U(side, "SEST_Allied_Fixes", "usn_mh-60r", "flight", **kw)])
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


class CoastExtracts(unittest.TestCase):
    """A "coast" mission is proved on the extract its centre is in. One
    campaign-wide extract leaked between campaigns: after Southern Watch's
    spec, Southern Reach's Southern Ocean positions were "outside the box"."""

    def test_each_theatre_gets_its_own_coast(self):
        def name(mission):
            c = bp.coast_data(mission)
            return [k for k, v in __import__("coast")._COAST.items() if v is c][0]
        self.assertEqual(name(dict(centre=(-47.5, 140.5))), "southern_theatre_coast.json")
        self.assertEqual(name(dict(centre=(5.62, 120.05))), "sulu_theatre_coast.json")
        self.assertEqual(name(dict(centre=(-6.5, 131.5))), "banda_theatre_coast.json")
        # Nothing holds the North Atlantic: the southern default, whose box
        # check then names the positions.
        self.assertEqual(name(dict(centre=(50.0, -20.0))), "southern_theatre_coast.json")
        self.assertEqual(name(None), "southern_theatre_coast.json")

    def test_land_units_on_one_station_stand_apart(self):
        del bp.PLACEMENT_PROBLEMS[:]
        m = dict(key="Test Yard", centre=(7.30, 118.70),
                 stations={"yard": dict(S(7.005, 118.505, "Yard"), coastal=True)})
        placer = bp.CoastPlacer(bp.coast_data(m), m)
        spots = [placer.take("land", (7.005, 118.505), where="Test Yard yard")[0]
                 for _ in range(3)]
        self.assertEqual(len(set(spots)), 3)
        self.assertEqual(bp.PLACEMENT_PROBLEMS, [])      # all three still on Mapun

    def test_the_sulu_coast_puts_jolo_ashore(self):
        c = bp.coast_data(dict(centre=(6.0, 121.0)))
        self.assertTrue(c.on_land(6.03, 121.05))      # Jolo island
        self.assertFalse(c.on_land(5.70, 120.35))     # the Sulu Sea north of Tawi-Tawi


def _trigger_numbers(text):
    """{trigger name: its number} in a rendered mission."""
    return {m.group(2): int(m.group(1)) for m in
            re.finditer(r"^\[Trigger(\d+)\][^\n]*\nName=([^\n]+)", text, re.M)}


class PlayTest18Oct(unittest.TestCase):
    """The rules the play test of 18 Oct 2026 asked for: a stage held for
    minutes before the win arms (SW03's lifters), a second win by sinking
    (SW04's craft), deck prep before the start, a deck's own air group
    (Canberra's Apaches) and air-tasking rows that offer every fit an
    aircraft can fly for the job."""

    def test_a_held_stage_arms_the_win_after_its_minutes(self):
        v = dict(small_mission()["victory"],
                 after=dict(kind="area", units="group", at=(-4.40, 128.70), radius=3,
                            min_units=1, hold_minutes=3, intel="Over the rig.",
                            held=("Loaded.", "All aboard.")))
        m = small_mission(victory=v)
        triggers = rendered(m)
        _name, text = bp.render(m, *small_placement())
        n = _trigger_numbers(text)
        self.assertIn(f"Action_EnableTriggers=Trigger{n['Stage held']}", triggers["Stage"])
        held = triggers["Stage held"]
        self.assertIn("Disabled=True", held)
        self.assertIn("Condition_Condition2_Time=180", held)
        self.assertIn("ConditionsCompleted=<Condition1> AND <Condition2>", held)
        self.assertIn("Action_Taskforce1_Message=StageHeldMessage", held)
        self.assertIn(f"Action_EnableTriggers=Trigger{n['Objective met']}", held)
        self.assertIn("Disabled=True", triggers["Objective met"])
        self.assertIn("StageHeldMessage=<color=yellow>Loaded.</color>|All aboard.", text)

    def test_a_held_stage_needs_its_message(self):
        v = dict(small_mission()["victory"],
                 after=dict(kind="area", units="group", at=(-4.40, 128.70),
                            hold_minutes=3))
        with self.assertRaisesRegex(SystemExit, "held"):
            rendered(small_mission(victory=v))

    def test_sinking_after_the_stage_is_a_win_without_the_bonus(self):
        objectives = small_mission()["objectives"] + [("Taken", "Take her", "15,0,None")]
        v = dict(kind="arrive", station="spoiler", at=(-4.30, 128.60), radius=12,
                 objective="Withdrawal", bonus=["Taken"], or_destroyed="She is sunk.",
                 after=dict(kind="classify", units="spoiler", min_units=1))
        m = small_mission(victory=v, objectives=objectives,
                          resolve={"Withdrawal": "victory", "Taken": "victory",
                                   "Spoiler": ("destroy", "spoiler", 1)})
        triggers = rendered(m)
        _name, text = bp.render(m, *small_placement())
        n = _trigger_numbers(text)
        self.assertIn(f"Action_EnableTriggers=Trigger{n['Objective met']},"
                      f"Trigger{n['Objective met by sinking']}", triggers["Stage"])
        self.assertIn("Action_ObjectivesCompleted=Withdrawal,Taken", triggers["Objective met"])
        sunk = triggers["Objective met by sinking"]
        self.assertIn("Disabled=True", sunk)
        self.assertIn("Condition_Condition1_Type=UnitDestroyed", sunk)
        self.assertIn("Action_ObjectivesCompleted=Withdrawal", sunk)
        self.assertIn("Action_Victory=Taskforce1", sunk)
        self.assertIn("Action_Taskforce1_Message=SunkVictoryMessage", sunk)

    def test_deck_prep_pause_requires_an_explicit_mission_choice(self):
        # A carrier or generated force must not imply the unusable modal.
        for generation in (None, "Generated"):
            self.assertNotIn("Allow initial flight deck prep",
                             rendered(small_mission(generation=generation)))
        self.assertIn("Action_PrepareFlightDeck=True",
                      rendered(small_mission(initial_deck_prep=True))[
                          "Allow initial flight deck prep"])

    def _deck(self, **unit):
        m = dict(key="Test Deck", centre=(-11.6, 126.6), date=(2028, 10, 24),
                 blue_nation="Australia", red_nation="China",
                 stations={"amphib": S(-11.6, 126.6, "Amphibious group", heading=10)},
                 units=[U("blue", "SEST_RAN_Fleet", "ran_lhd_canberra", "amphib", **unit)])
        placed, _m, credits, _f = bp.place(m, bp.CoastPlacer(bp.coast_data(m), m))
        return placed["Taskforce1Vessel"][0][1], credits

    def test_a_deck_carries_its_own_air_group(self):
        keys, credits = self._deck(
            air_group=[("adf_ah-64e", "Squadron1", 2)],
            ready=[("adf_ah-64e", "Squadron1", "AntiShip", 2, 0)])
        self.assertEqual(keys["CustomAirGroup"], "True")
        self.assertEqual(keys["adf_ah-64e"], "Squadron1,2")
        self.assertEqual(keys["FlightDeck_ReadyUpTasks"], "1")
        self.assertEqual(keys["FlightDeck_ReadyUpTask1"], "adf_ah-64e,Squadron1,AntiShip,2,0")
        self.assertIn(bp.owner("aircraft/adf_ah-64e.ini"), credits)

    def test_an_air_group_the_deck_cannot_take_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "does not take"):
            self._deck(air_group=[("usn_p8", "Squadron3", 1)])
        with self.assertRaisesRegex(SystemExit, "offers"):
            self._deck(air_group=[("adf_ah-64e", "Squadron1", 2)],
                       ready=[("adf_ah-64e", "Squadron1", "NoSuchFit", 2, 0)])

    def test_tasking_rows_offer_every_fit_for_the_job(self):
        missions = [dict(window=dict(flights=[
            "CAP|Combat Air Patrol|Fighter|2|MurderHornetCAP",
            "Attack|Maritime Strike|Bomber/SEAD|2|MurderHornetAntiShip"]))]
        bp.widen_flights(missions, [dict(unit="usn_fa-18f_blk3")])
        cap, attack = (set(r.split("|")[4].split("/")) for r in missions[0]["window"]["flights"])
        self.assertIn("MurderHornetPenetrator", cap)       # AIM-120D and AIM-174B
        self.assertNotIn("MH_CAP_424", cap)                # AIM-424: barred
        self.assertNotIn("SEST_Intercept260", cap)         # AIM-260: barred
        self.assertNotIn("MurderHornetSEAD", cap)          # carries AGM-88G
        self.assertNotIn("Empty", cap)
        self.assertIn("MH_LRASM", attack)                  # LRASM-ER, an alias of the LRASM
        self.assertIn("MurderHornetSEAD", attack)
        self.assertNotIn("MurderHornetCAP", attack)
        self.assertIn("SEST_REDBACK", attack)              # AGR-30: air first, ASuW second
        self.assertNotIn("SEST_REDBACK", cap)
        self.assertNotIn("MurderHornetPenetrator", attack) # AIM-174B's ASuW secondary is not counted
        self.assertEqual(missions[0]["window"]["flights"][0].split("|")[4].split("/")[0],
                         "MurderHornetCAP")                 # the authored fit stays first


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
    and is otherwise its base campaign's spine, line for line. Dormant since
    21 Oct 2026 - no campaign in the pack opts in (spec OPEN_ALLOCATION) -
    and kept for a world-wide campaign, so these call it directly."""

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

    def test_a_held_unit_is_sold_only_where_the_story_sells_it(self):
        # OPEN_HOLD: the P-8 is not in the first window's story allowlist, so
        # the twin's first window leaves it out and says so. The second open
        # window has no allowlist - the story sells everything there - and
        # the twin sells it too.
        twin = bp.open_allocation_ini(self.SPINE, "sest-test", self.ROSTER,
                                      hold=["usn_p8"]).split("\n")
        self.assertIn("TaskForceModeAllowedRosterUnits=ran_ffh_anzac,Variant3,Variant8", twin)
        self.assertIn("TaskForceModeBuilderSituation_en=" + bp.OPEN_NOTE_HELD
                      + " Frigates only.", twin)
        self.assertIn("Description=" + bp.OPEN_BLURB_HELD + "Blurb.", twin)
        held_too = self.SPINE.replace("Variant3,Variant8\n", "Variant3,Variant8|usn_p8,Squadron3\n")
        twin = bp.open_allocation_ini(held_too, "sest-test", self.ROSTER, hold=["usn_p8"])
        self.assertIn("TaskForceModeAllowedRosterUnits=" + self.FULL, twin)
        self.assertIn(bp.OPEN_NOTE + " Frigates only.", twin)
        with self.assertRaisesRegex(SystemExit, "OPEN_HOLD names civ_ms_c8"):
            bp.open_allocation_ini(self.SPINE, "sest-test", self.ROSTER, hold=["civ_ms_c8"])

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
        # the Peykaap registers Iran; the story flies it under the Meridian flag
        self.assertIn("[SurfaceReusable_Meridian Maritime Group]\nir_ptg_peykaap_3=Default", text)
        self.assertIn("[SubmarinesPersistent_PLAN]\nplan_ss_type_039c=Variant1", text)
        self.assertIn("[AircraftReusable_PLAN]\nplan_j-15d=Squadron1,2", text)
        self.assertIn("[HelicoptersReusable_PLAN]\nplan_z-9d=Squadron1,1", text)
        self.assertNotIn("ran_ffh_anzac", text, "the player's own ships are not enemy ORBAT")

    def test_a_hull_the_campaign_places_more_than_once_is_reusable(self):
        # Three Peykaaps under one variant are a class, not one named boat:
        # tracked as persistent, the first sunk read "Destroyed" while the next
        # missions still sailed them (16 Oct 2026 test). A hull and variant
        # placed once stays a tracked, named ship.
        missions = [dict(key="m1", group="core", red_nation="China"),
                    dict(key="m2", group="core", red_nation="China")]
        boat = lambda n: ("Taskforce2Vessel%d" % n, {"Type": "plan_type_056a", "VariantReference": "Variant1"}, None, False)
        once = ("Taskforce2Vessel9", {"Type": "plan_type_054a_p5", "VariantReference": "Variant1"}, None, False)
        text = bp.enemy_roster_ini(missions, {"m1": {"Taskforce2Vessel": [boat(1), boat(2), once]},
                                              "m2": {"Taskforce2Vessel": [boat(1)]}})
        self.assertIn("[SurfaceReusable_PLAN]\nplan_type_056a=Default", text)
        self.assertIn("[SurfacePersistent_PLAN]\nplan_type_054a_p5=Variant1", text)
        self.assertNotIn("plan_type_056a=Variant1", text)

    def test_the_narco_submarine_files_under_a_capitalised_pirates_tab(self):
        # The narco-sub mod registers Nation=pirates; the Situation window shows
        # the roster label raw, and the 16 Oct 2026 test read a "pirates" tab.
        missions = [dict(key="m", group="core", red_nation="China")]
        placed = {"Taskforce2Submarine": [
            ("Taskforce2Submarine1", {"Type": "_narco_narcosub_adv", "VariantReference": "Variant1"}, None, False)]}
        text = bp.enemy_roster_ini(missions, {"m": placed})
        self.assertIn("[SubmarinesPersistent_Pirates]\n_narco_narcosub_adv=Variant1", text)
        self.assertNotIn("_pirates]", text)

    def test_a_rostered_squadron_the_unit_does_not_define_stops_the_build(self):
        # The JH-7A filed as Squadron1 when its table defined none, and its row
        # showed the unknown flag. A squadron no winning file defines is refused.
        missions = [dict(key="m", group="core", red_nation="China")]
        placed = {"Taskforce2Aircraft": [
            ("Taskforce2Aircraft1", {"Type": "plan_j-15d", "SquadronReference": "Squadron99"}, None, False)]}
        with self.assertRaisesRegex(SystemExit, "plan_j-15d is rostered as Squadron99"):
            bp.enemy_roster_ini(missions, {"m": placed})

    def test_the_enemy_roster_is_what_the_missions_place(self):
        # The built pack: every Taskforce2 unit a campaign's missions place is
        # in its roster, and the spine names it. Every folder under
        # campaigns/ is a campaign the pack builds - since 21 Oct 2026 no
        # Open Allocation twin, unless a spec opts in to one.
        root = PACK / "campaigns"
        if not root.is_dir():
            self.skipTest("pack not built")
        # orbat=False leaves a unit out on purpose (Red Line's ALPHA, GOLF and
        # HOTEL), by mission file.
        unlisted, known = {}, set()
        for spec in bp.campaign_specs():
            bp.set_campaign(spec)
            known.add(spec["SLUG"])
            if spec.get("OPEN_ALLOCATION"):
                known.add(bp.open_slug(spec["SLUG"]))
            for m in spec["MISSIONS"]:
                unlisted[bp.mission_name(m) + ".ini"] = {
                    u["type"] for u in m["units"] if u.get("orbat") is False}
        self.assertEqual(sorted(p.name for p in root.iterdir() if p.name not in known), [])
        checked = 0
        for camp in sorted(root.iterdir()):
            missions = camp / "missions"
            roster = camp / "enemy_theater_roster.ini"
            self.assertTrue(roster.exists(), camp.name)
            spine = (camp / "campaign.ini").read_text(encoding="utf-8")
            self.assertIn("[DynamicUnitGeneration]\nTaskforce2RosterFile=enemy_theater_roster.ini", spine, camp.name)
            if not missions.exists():
                # An opted-in twin: its campaign's roster, byte for byte.
                twin_of = root / camp.name.removesuffix(bp.OPEN_SUFFIX)
                self.assertEqual(roster.read_bytes(), (twin_of / "enemy_theater_roster.ini").read_bytes(),
                                 f"{camp.name} must carry its campaign's roster")
                continue
            listed = set(re.findall(r"^([A-Za-z0-9_.()'-]+)=", roster.read_text(encoding="utf-8"), re.M))
            for ini in missions.glob("*.ini"):
                text = ini.read_text(encoding="utf-8")
                for m in re.finditer(r"^\[Taskforce2(Vessel|Submarine|Aircraft|Helicopter)\d+\][^\n]*\n(.*?)(?=^\[)",
                                     text, re.M | re.S):
                    uid = re.search(r"^Type=(\S+)", m.group(2), re.M).group(1)
                    if (m.group(1) == "Vessel" and not bp.armed(uid)) \
                            or uid in unlisted.get(ini.name, ()):
                        continue
                    self.assertIn(uid, listed, f"{ini.name}: {uid} is placed but not in the roster")
                    checked += 1
        self.assertGreater(checked, 100)

    def test_the_beacon_reward_is_a_datum_that_ages_off(self):
        ini = (Path(bp.__file__).resolve().parent / "SEST_Campaign" / "campaigns" /
               "sest-southern-watch" / "missions" / "Southern Watch 02 - Steel Highway.ini")
        text = ini.read_text(encoding="utf-8")
        # One minute, stock Sub Duel's initial contact: fifteen left the boat
        # on the plot with nothing seeming to hold it (play test, 18 Oct 2026).
        self.assertIn("Action_UnitRevealToTaskforce=Taskforce1\nAction_UnitRevealTime=60\n", text)
        self.assertNotIn("Taskforce1|Classify", text)

    # Sulu Line is the one campaign whose roster is a coalition on purpose:
    # the Thai detachment, one RAN frigate and the MSC charter are sold at
    # their listed price, and the rules page says so. The two RAN campaigns
    # sell an allied reserve beside their own navy (mission_depth.
    # apply_reserve): eleven classes of five navies in Southern Watch and
    # three in Southern Reach on 20 Oct 2026, the whole allied fleet of
    # eleven navies in both since 21 Oct. Red Line's reserve is its own
    # navy's.
    ALLIED_NAVIES = {"us", "uk", "france", "germany", "italy", "spain", "netherlands",
                     "norway", "denmark", "japan", "south_korea"}
    PARTNER_NATIONS = {"sest-sulu-line": {"thailand", "australia", "us"},
                       "sest-southern-watch": ALLIED_NAVIES,
                       "sest-southern-reach": ALLIED_NAVIES}

    def test_every_shipped_roster_is_the_commanders_own(self):
        for spec in bp.campaign_specs():
            nation = re.search(r"^CommanderNations=(.+)$", spec["COMMANDER"], re.M).group(1)
            self.assertEqual(bp.same_nation_discount(spec["COMMANDER"]), 0.2, spec["SLUG"])
            found = {n.lower() for n in bp.roster_nations(spec["ROSTER"]).values()}
            self.assertIn(nation.lower(), found, spec["SLUG"])
            self.assertEqual(found - {nation.lower()},
                             self.PARTNER_NATIONS.get(spec["SLUG"], set()), spec["SLUG"])

    def test_sulu_line_never_rearms_for_free(self):
        spec = next(s for s in bp.campaign_specs() if s["SLUG"] == "sest-sulu-line")
        for m in spec["MISSIONS"][1:]:
            self.assertFalse(m["window"].get("rearm"), m["code"])
        page = bp.campaign_rules(spec)
        self.assertNotIn("for free", page)
        self.assertIn("There is no free rearm in this campaign", page)

    def test_the_us_built_airframes_fly_australian_squadrons(self):
        for uid, pick in (("usn_fa-18f_blk3", "Squadron8"), ("usn_ea-18g", "Squadron6"),
                          ("usn_p8", "Squadron3"), ("usn_mh-60r", "Squadron20")):
            self.assertEqual(bp.pick_nation(uid, pick), "Australia", uid)

    def test_the_page_carries_the_games_binding_and_the_cover(self):
        spec = dict(bp.campaign_specs()[0])
        nations = bp.roster_nations(spec["ROSTER"])
        spec["ROSTER"] = [e for e in spec["ROSTER"] if nations[e["unit"]] == "Australia"]
        page = bp.campaign_rules(spec)
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
        nations = bp.roster_nations(spec["ROSTER"])
        # The campaign's own ten: the reserve's Canberra-class LHD is
        # Australian too (21 Oct 2026).
        spec["ROSTER"] = [e for e in spec["ROSTER"] if nations[e["unit"]] == "Australia"
                          and e["unit"] not in spec["RESERVE_OPENS"]] + [
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
    """The allied fleet beside the campaign's roster: ships always, aircraft
    only where a row launches and recovers them (usable_allied). The Open
    Allocation twins sold it so until 21 Oct 2026; since, the allied reserve
    sells it in the standard campaigns from a window each names, and no
    campaign in the pack opts in to a twin."""

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

    def test_the_reserve_is_sold_from_the_roster_not_the_allied_fleet(self):
        # mission_depth.apply_reserve moves each reserve class from the
        # allied fleet to the roster - a ship at once, an aircraft once the
        # build has judged it (RESERVE_AIR) - so a twin, for a campaign that
        # opts in to one, sells it once; a second campaign_specs() call adds
        # nothing twice.
        for _ in range(2):
            for spec in bp.campaign_specs():
                units = [e["unit"] for e in spec["ROSTER"]]
                self.assertEqual(len(units), len(set(units)), spec["SLUG"])
                held = {e["unit"] for e in spec.get("RESERVE_AIR", [])}
                left = {e["unit"] for e, _why in spec.get("RESERVE_LEFT_OUT", [])}
                for uid in spec.get("RESERVE_OPENS", {}):
                    self.assertEqual([uid in units, uid in held, uid in left].count(True), 1,
                                     (spec["SLUG"], uid))
                    self.assertNotIn(uid, {e["unit"] for e in spec["ALLIED_FLEET"]})
                    # A ship is never held; an aircraft is on no roster until
                    # main() has judged it on the built missions.
                    if bp.unit_type(uid) == "Vessel":
                        self.assertNotIn(uid, held, uid)
                    else:
                        self.assertIn(bp.unit_type(uid), ("Aircraft", "Helicopter", "VTOL"), uid)
                        self.assertNotIn(uid, units, uid)

    def test_every_allied_entry_resolves_and_is_one_nation(self):
        import allied_fleet
        for nation, fleet in allied_fleet.FOR_NATION.items():
            units = [e["unit"] for e in fleet]
            self.assertEqual(len(units), len(set(units)), nation)
            bp.roster_nations(fleet)                    # one declared nation each
            self.assertTrue(all(isinstance(e["points"], int) and e["points"] > 0
                                for e in fleet))

    def test_every_allied_pick_is_still_offered(self):
        # Only roster_ini() checks a pick against the winning variants or
        # squadrons file, and until 21 Oct 2026 only the twins' build ran it
        # on the allied entries the reserve does not sell. Dormant since,
        # the lists are kept for a world-wide campaign, so a mod update that
        # drops a variant fails here rather than on the day one opts in.
        import allied_fleet
        bp.set_campaign(bp.campaign_specs()[0])
        for nation, fleet in allied_fleet.FOR_NATION.items():
            text, _credits = bp.roster_ini(list(fleet))
            for e in fleet:
                self.assertIn(f"\n{e['unit']}=", text, nation)

    def test_no_roster_sells_a_submarine(self):
        # In-game check, 13 Oct: a bought boat never showed in the formation
        # editor and a dismissed one still sailed. The roster and the rules
        # page both refuse one, and the allied fleet carries none.
        import allied_fleet
        for fleet in allied_fleet.FOR_NATION.values():
            self.assertEqual([e["unit"] for e in fleet
                              if bp.unit_type(e["unit"]) == "Submarine"], [])
        boat = dict(unit="plan_ss_type_039c", picks=["Variant1"], points=200)
        bp.set_campaign(bp.campaign_specs()[0])
        with self.assertRaisesRegex(SystemExit, "plan_ss_type_039c is a submarine"):
            bp.roster_ini([boat])
        spec = dict(bp.campaign_specs()[0])
        spec["ROSTER"] = spec["ROSTER"] + [boat]
        with self.assertRaisesRegex(SystemExit, "sells submarines"):
            bp.campaign_rules(spec, open_allocation=True, allied=1)
        page = bp.campaign_rules(bp.campaign_specs()[0], open_allocation=True, allied=1)
        self.assertIn("Submarines cannot be bought in this campaign", page)
        self.assertIn("the allied fleet included", page)


class DeploymentZones(unittest.TestCase):
    """deployment_zones: the blue boxes the player may place units in before
    a mission (user report, 13 Oct: "i cant move my task force around at
    all"; decision of 14 Oct: every playable unit gets one). The first holds
    the hulls, opens away from the enemy and the mission's goals, never
    toward them; every other unit of the player's - a boat on her own, an
    aircraft on station, a battery ashore - is in a box of its own cluster's
    types, and a base gets none. Open Southern Ocean, so no edge meets land
    unless a test says otherwise."""

    CENTRE = (-50.0, 150.0)

    def placement(self, blue, red=()):
        """blue entries are (uid, x, z) hulls - a boat where the uid has
        "_ss" - or (uid, x, z, family) for any Taskforce1 family."""
        placed = collections.defaultdict(list)
        for entry in blue:
            uid, x, z = entry[:3]
            family = (entry[3] if len(entry) > 3
                      else "Submarine" if "_ss" in uid else "Vessel")
            family = "Taskforce1" + family
            n = len(placed[family]) + 1
            placed[family].append((f"{family}{n}", _keys(uid, x, z), None, False))
        for i, (uid, x, z) in enumerate(red, 1):
            placed["Taskforce2Vessel"].append((f"Taskforce2Vessel{i}", _keys(uid, x, z), None, False))
        return dict(placed)

    def mission(self, **over):
        m = dict(key="Test Zones", centre=self.CENTRE, victory=dict(kind="survive"),
                 resolve={}, _anchor_section="Taskforce1Vessel1")
        m.update(over)
        return m

    def zones(self, blue, red=(), **mission):
        return bp.deployment_zones(self.mission(**mission), self.placement(blue, red),
                                   {"goal": ["Taskforce2Vessel1"]})

    def box(self, z):
        """(west, east, south, north) edges in the mission's NM frame."""
        cx = (z["at"][1] - self.CENTRE[1]) * 60
        cz = (z["at"][0] - self.CENTRE[0]) * 60
        return (round(cx - z["width"] / 2, 1), round(cx + z["width"] / 2, 1),
                round(cz - z["height"] / 2, 1), round(cz + z["height"] / 2, 1))

    def holds(self, z, x, zz):
        west, east, south, north = self.box(z)
        return west <= x <= east and south <= zz <= north

    def test_the_box_opens_away_from_the_enemy_and_not_toward_it(self):
        (z,) = self.zones([("plan_type_054a_p5", 0, 0)],
                          red=[("plan_type_054a_p5", 0, 60)])
        self.assertEqual(z["types"], bp.DEPLOY_ALL)
        west, east, south, north = self.box(z)
        self.assertEqual(north, bp.DEPLOY_PAD_NM)            # the pad, no more
        self.assertEqual(south, -bp.DEPLOY_PAD_NM - bp.DEPLOY_OPEN_NM)
        self.assertEqual((west, east), (-28.0, 28.0))         # abeam is free

    def test_a_goal_holds_the_box_back_too(self):
        (z,) = self.zones([("plan_type_054a_p5", 0, 0)],
                          red=[("plan_type_054a_p5", 0, 60)],
                          lift=[dict(at=(self.CENTRE[0] - 40 / 60.0, self.CENTRE[1]))])
        _w, _e, south, north = self.box(z)
        self.assertEqual((south, north), (-3.0, 3.0))

    def test_every_hull_in_the_group_is_inside(self):
        (z,) = self.zones([("plan_type_054a_p5", 0, 0), ("plan_type_054a_p5", 10, -12)])
        west, east, south, north = self.box(z)
        self.assertTrue(west <= -3 and east >= 13 and south <= -15 and north >= 3)

    def test_a_boat_on_her_own_gets_a_submarine_box(self):
        main, boat = self.zones([("plan_type_054a_p5", 0, 0), ("plan_ss_type_039c", 80, 0)])
        self.assertEqual(main["types"], bp.DEPLOY_ALL)
        self.assertEqual((boat["types"], boat["label"]), ("Submarine", "Submarine Patrol Box"))
        self.assertEqual(boat["tags"], ["Taskforce1Submarine1"])

    def test_no_unit_no_zone(self):
        self.assertEqual(self.zones([]), [])

    def test_the_mission_file_carries_the_zone_and_its_label(self):
        # the Liaoning, which the arrival circle counts, starts 1.4 NM off
        # it: her box ends at her, apart from the frigate's (14 October)
        _name, text = bp.render(small_mission(), *small_placement())
        self.assertIn("Zone1Label_en=Deployment Zone\nZone2Label_en=Detachment Zone", text)
        self.assertIn("[Zones]\nNumberOfZones=2\nZone1=Zone1\nZone2=Zone2\n[Zone1]\nType=Deployment", text)
        self.assertIn("Side=Blue", text)

    # --- every playable unit (14 October) ---------------------------------

    def test_an_airborne_aircraft_away_from_the_force_gets_an_air_station(self):
        main, air = self.zones([("plan_type_054a_p5", 0, 0), ("plan_y-9fq", 0, 60, "Aircraft")],
                               red=[("plan_type_054a_p5", 0, 120)])
        self.assertEqual(main["label"], "Deployment Zone")
        self.assertEqual((air["types"], air["label"], air["tags"]),
                         ("Aircraft", "Air Station", ["Taskforce1Aircraft1"]))
        self.assertTrue(self.holds(air, 0, 60))
        west, east, south, north = self.box(air)
        # the same rules as the first box: the pad towards the enemy, open behind
        self.assertEqual(north, 60 + bp.DEPLOY_PAD_NM)
        self.assertEqual(south, 60 - bp.DEPLOY_PAD_NM - bp.DEPLOY_OPEN_NM)

    def test_an_aircraft_the_first_box_already_holds_gets_no_second(self):
        zones = self.zones([("plan_type_054a_p5", 0, 0), ("plan_z-9c", 1, -1, "Helicopter")])
        self.assertEqual([z["label"] for z in zones], ["Deployment Zone"])
        self.assertTrue(self.holds(zones[0], 1, -1))

    def test_a_flight_and_its_helicopter_share_one_air_station(self):
        zones = self.zones([("plan_type_054a_p5", 0, 0), ("plan_j-15", 60, 0, "Aircraft"),
                            ("plan_j-15", 63, 0, "Aircraft"), ("plan_z-9c", 70, 10, "Helicopter")])
        self.assertEqual(len(zones), 2)
        self.assertEqual((zones[1]["types"], zones[1]["label"]), ("Helicopter,Aircraft", "Air Station"))
        self.assertEqual(zones[1]["tags"],
                         ["Taskforce1Aircraft1", "Taskforce1Aircraft2", "Taskforce1Helicopter1"])

    def test_a_mission_of_aircraft_alone_has_air_stations_and_no_deployment_zone(self):
        zones = self.zones([("raaf_mq-4c_triton", 18, 36, "Aircraft"), ("usn_p8", -24, 24, "Aircraft")],
                           _anchor_section=None)
        self.assertEqual([z["label"] for z in zones], ["Air Station 1", "Air Station 2"])
        self.assertEqual([z["types"] for z in zones], ["Aircraft", "Aircraft"])

    def test_a_mobile_land_unit_is_boxed_and_a_base_is_not(self):
        # pla_hy-2_launcher is LandUnitSubType=MissileSite; airfield_small_1 an Airbase
        zones = self.zones([("plan_type_054a_p5", 0, 0), ("pla_hy-2_launcher", 0, 60, "LandUnit"),
                            ("airfield_small_1", 0, -60, "LandUnit")])
        self.assertEqual([(z["types"], z["label"]) for z in zones],
                         [(bp.DEPLOY_ALL, "Deployment Zone"), ("Land", "Detachment Zone")])
        self.assertEqual(zones[1]["tags"], ["Taskforce1LandUnit1"])
        self.assertFalse(any("Taskforce1LandUnit2" in z["tags"] for z in zones))
        self.assertIsNone(bp.deploy_type("Taskforce1LandUnit2", {"Type": "airfield_small_1"}))
        self.assertIsNone(bp.deploy_type("Taskforce1LandUnit3", {"Type": "FOB"}))
        self.assertEqual(bp.deploy_type("Taskforce1LandUnit4", {"Type": "china_hq15_launcher"}), "Land")

    def test_a_sest_base_resolves_without_the_consolidated_pack(self):
        # airbase_raaf_darwin ships only in SEST_RAAF_Bases, and the consolidated
        # pack is written after this builder: read through it, a --from-scratch
        # build found no file, took Darwin for a movable land unit and boxed it.
        f = bp.fix_land_positions.winning_file("land_units/airbase_raaf_darwin.ini")
        self.assertEqual(f.parts[-3], "SEST_RAAF_Bases")
        self.assertIsNone(bp.deploy_type("Taskforce1LandUnit1", {"Type": "airbase_raaf_darwin"}))

    def test_a_far_boat_and_her_tender_share_a_detachment_box(self):
        # Red Line 06's shape: the escort here, the tender and the boat 80 NM off
        main, far = self.zones([("plan_type_054a_p5", 0, 0), ("civ_ms_kommunist", -80, 0),
                                ("plan_ss_type_039c", -75, 4)])
        self.assertEqual((far["types"], far["label"]), ("Vessel,Submarine", "Detachment Zone"))
        self.assertEqual(far["tags"], ["Taskforce1Submarine1", "Taskforce1Vessel2"])
        self.assertTrue(self.holds(far, -80, 0) and self.holds(far, -75, 4))

    def test_duplicate_labels_are_numbered_as_stock_numbers_its_patrol_boxes(self):
        zones = self.zones([("plan_type_054a_p5", 0, 0), ("plan_ss_type_039c", 80, 0),
                            ("plan_ss_type_039c", -80, 0)])
        self.assertEqual([z["label"] for z in zones],
                         ["Deployment Zone", "Submarine Patrol Box 1", "Submarine Patrol Box 2"])

    # --- no box into an objective (14 October) ----------------------------

    HULL = {"hull": ["Taskforce1Vessel1"]}        # the circle counts the player's own hull

    def arrive(self, x, z, radius):
        return dict(kind="arrive", units=["hull"], min_units=1, radius=radius,
                    at=(self.CENTRE[0] + z / 60.0, self.CENTRE[1] + x / 60.0))

    def hull_zones(self, blue, **mission):
        return bp.deployment_zones(self.mission(**mission), self.placement(blue), self.HULL)

    def test_a_box_never_opens_towards_the_arrival_circle(self):
        # the circle's edge 18 NM north of the hull: the pad alone that way
        # (a goal is never approached), the other sides open as before
        (main,) = self.hull_zones([("plan_type_054a_p5", 0, 0)], victory=self.arrive(0, 30, 12))
        west, east, south, north = self.box(main)
        self.assertEqual(north, bp.DEPLOY_PAD_NM)
        self.assertEqual(south, -bp.DEPLOY_PAD_NM - bp.DEPLOY_OPEN_NM)
        self.assertEqual(east, bp.DEPLOY_PAD_NM + bp.DEPLOY_OPEN_NM)

    def test_a_box_that_would_reach_within_the_clearance_loses_its_pad_that_way(self):
        # the edge 5.5 NM north of the hull: 3 NM of pad would leave 2.5
        (main,) = self.hull_zones([("plan_type_054a_p5", 0, 0)], victory=self.arrive(0, 17.5, 12))
        west, east, south, north = self.box(main)
        self.assertEqual(north, bp.DEPLOY_NEAR_PAD_NM)
        self.assertEqual(south, -bp.DEPLOY_PAD_NM - bp.DEPLOY_OPEN_NM)

    def test_a_force_starting_near_the_circle_keeps_its_start_and_no_pad_towards_it(self):
        # the edge 2 NM off the hull: no pad north, the other sides open as before
        (main,) = self.hull_zones([("plan_type_054a_p5", 0, 0)], victory=self.arrive(0, 14, 12))
        west, east, south, north = self.box(main)
        self.assertEqual(north, bp.DEPLOY_NEAR_PAD_NM)
        self.assertEqual((west, east), (-bp.DEPLOY_PAD_NM - bp.DEPLOY_OPEN_NM,
                                        bp.DEPLOY_PAD_NM + bp.DEPLOY_OPEN_NM))

    def test_a_force_starting_inside_a_service_circle_is_left_alone(self):
        stage = dict(kind="area", units="hull", radius=5, after_minutes=30, at=self.CENTRE)
        (main,) = self.hull_zones([("plan_type_054a_p5", 0, 0)],
                                  victory=dict(kind="survive", after=stage))
        west, east, south, north = self.box(main)
        self.assertEqual(north, bp.DEPLOY_PAD_NM + bp.DEPLOY_OPEN_NM)

    def test_an_escort_waiting_inside_the_convoys_circle_has_no_box(self):
        # the freighter must reach the circle 26 NM east; the frigate waits
        # inside it. A box round the frigate would let the freighter in.
        mission = self.mission(victory=dict(kind="arrive", units=["convoy"], min_units=1, radius=12,
                                            at=(self.CENTRE[0], self.CENTRE[1] + 26 / 60.0)))
        placed = self.placement([("civ_ms_freighter_a", 0, 0), ("plan_type_054a_p5", 20, 0)])
        zones = bp.deployment_zones(mission, placed, {"convoy": ["Taskforce1Vessel1"]})
        self.assertEqual([z["tags"] for z in zones], [["Taskforce1Vessel1"]])
        self.assertEqual(list(mission["_parked"]), ["Taskforce1Vessel2"])
        self.assertIn("6.0 NM inside the 12 NM circle", mission["_parked"]["Taskforce1Vessel2"])
        self.assertEqual(self.box(zones[0])[1], bp.DEPLOY_PAD_NM)          # east: no nearer
        bp.check_deployment_cover(mission, placed, zones)                   # the parked one is excused

    def test_a_circle_for_helicopters_is_kept_out_of_the_ships_box(self):
        # the helicopter must reach a circle 10 NM north of the ships, whose
        # box reaches to 7 NM of it: the box no longer admits helicopters
        mission = self.mission(victory=dict(kind="arrive", units=["heli"], min_units=1, radius=5,
                                            at=(self.CENTRE[0] + 10 / 60.0, self.CENTRE[1])))
        placed = self.placement([("plan_type_054a_p5", 0, 0), ("plan_z-9c", 60, 0, "Helicopter")])
        main, air = bp.deployment_zones(mission, placed, {"heli": ["Taskforce1Helicopter1"]})
        self.assertEqual(main["types"], "Vessel,Submarine,Aircraft,Land")
        self.assertEqual((air["types"], air["tags"]), ("Helicopter", ["Taskforce1Helicopter1"]))
        self.assertEqual(mission["_parked"], {})

    def test_a_helicopter_nearer_the_circle_than_its_ships_gets_its_own_box(self):
        # Borrowed Shield's shape: the circle counts the two ships; their
        # helicopter rides 8 NM east, inside the clearance. The ships' box
        # is pulled to the ships, and the helicopter is boxed on its own.
        # The force's own ship (the anchor) is 60 NM east, so the Korean
        # group is a detachment: ships and helicopter chained into one box.
        mission = self.mission(victory=dict(kind="arrive", units=["ships"], min_units=2, radius=12,
                                            at=(self.CENTRE[0], self.CENTRE[1] + 24 / 60.0)))
        placed = self.placement([("ran_ffh_anzac", 60, 0), ("plan_type_054a_p5", 0, 0),
                                 ("plan_type_054a_p5", 0, -1), ("plan_z-9c", 8, 2, "Helicopter")])
        zones = bp.deployment_zones(mission, placed, {"ships": ["Taskforce1Vessel2", "Taskforce1Vessel3"]})
        self.assertEqual([z["label"] for z in zones], ["Deployment Zone", "Detachment Zone", "Air Station"])
        self.assertEqual(zones[1]["tags"], ["Taskforce1Vessel2", "Taskforce1Vessel3"])
        self.assertEqual(self.box(zones[1])[1], bp.DEPLOY_NEAR_PAD_NM)        # east: the ships, no nearer
        self.assertEqual(zones[2]["tags"], ["Taskforce1Helicopter1"])
        self.assertTrue(self.holds(zones[2], 8, 2))
        bp.check_deployment_cover(mission, placed, zones)

    def test_escorts_waiting_near_the_convoys_circle_have_no_box(self):
        # Western Passage's shape: two escorts 1 and 2 NM outside the circle
        # the convoy must reach, the convoy 18 NM beyond it. The game lets a
        # ship be placed in any box that admits ships, so a box round the
        # escorts would let the convoy start 1 NM off its objective: the
        # escorts keep their starts and no box, the convoy's keeps 5 NM.
        mission = self.mission(victory=dict(kind="arrive", units=["convoy"], min_units=2, radius=12,
                                            at=self.CENTRE))
        placed = self.placement([("ran_ffh_anzac", 0, 13), ("ran_ffh_anzac", 0, 14),
                                 ("civ_ms_freighter_a", 0, 30), ("civ_ms_freighter_a", 1, 31)])
        members = {"convoy": ["Taskforce1Vessel3", "Taskforce1Vessel4"]}
        zones = bp.deployment_zones(mission, placed, members)
        self.assertEqual(list(mission["_parked"]), ["Taskforce1Vessel1", "Taskforce1Vessel2"])
        self.assertIn("1.0 NM off the edge of the 12 NM circle", mission["_parked"]["Taskforce1Vessel1"])
        self.assertIn("let them be placed there", mission["_parked"]["Taskforce1Vessel2"])
        self.assertEqual([(z["label"], z["tags"]) for z in zones],
                         [("Deployment Zone", ["Taskforce1Vessel3", "Taskforce1Vessel4"])])
        self.assertGreaterEqual(self.box(zones[0])[2], 12 + bp.DEPLOY_CLEAR_NM)  # the convoy's south edge
        text = ("[Trigger1]\nName=Objective met\nCondition_Condition1_Type=UnitsInTheArea\n"
                "Condition_Condition1_PositionNM=0.00,0,0.00\nCondition_Condition1_AreaRadiusNM=12\n"
                "Condition_Condition1_Units=Taskforce1Vessel3,Taskforce1Vessel4\n")
        bp.check_zone_areas(mission, placed, zones, text)
        bp.check_deployment_cover(mission, placed, zones)

    def test_a_counted_unit_near_the_circle_sets_how_near_boxes_of_its_kind_may_come(self):
        # the designer's start, no nearer: the freighter the circle counts
        # starts 2 NM off it, so her box ends at her less the near pad, and
        # the gate allows every ship box her distance less 1 NM (the pad and
        # a corner) - the other freighter's, 20 NM back, no nearer either
        mission = self.mission(victory=dict(kind="arrive", units=["convoy"], min_units=2, radius=12,
                                            at=self.CENTRE), _anchor_section="Taskforce1Vessel1")
        placed = self.placement([("civ_ms_freighter_a", 0, 14), ("civ_ms_freighter_a", 30, 34)])
        members = {"convoy": ["Taskforce1Vessel1", "Taskforce1Vessel2"]}
        zones = bp.deployment_zones(mission, placed, members)
        self.assertEqual(mission["_parked"], {})
        self.assertEqual([z["tags"] for z in zones], [["Taskforce1Vessel1"], ["Taskforce1Vessel2"]])
        self.assertEqual(self.box(zones[0])[2], 14 - bp.DEPLOY_NEAR_PAD_NM)
        text = ("[Trigger1]\nName=Objective met\nCondition_Condition1_Type=UnitsInTheArea\n"
                "Condition_Condition1_PositionNM=0.00,0,0.00\nCondition_Condition1_AreaRadiusNM=12\n"
                "Condition_Condition1_Units=Taskforce1Vessel1,Taskforce1Vessel2\n")
        bp.check_zone_areas(mission, placed, zones, text)
        zones[1]["at"] = (self.CENTRE[0] + 14.0 / 60.0, self.CENTRE[1])   # the far box moved to 2 NM off too
        zones[1]["width"] = zones[1]["height"] = 1.0
        bp.check_zone_areas(mission, placed, zones, text)                 # the counted start: allowed
        zones[1]["at"] = (self.CENTRE[0] + 12.5 / 60.0, self.CENTRE[1])   # to the circle's edge: not
        with self.assertRaisesRegex(SystemExit, "must keep 1.0"):
            bp.check_zone_areas(mission, placed, zones, text)

    def test_an_escort_at_the_circles_edge_is_parked_and_the_straggler_boxed_on_her_own(self):
        # Broken Wake's shape: the straggler, which the circle counts, 4 NM
        # off it; her escort, uncounted, 0.2 NM off its edge. The escort can
        # have no box that stays out of the circle; the straggler's box ends
        # at her.
        mission = self.mission(victory=dict(kind="arrive", units=["straggler"], min_units=1, radius=10,
                                            at=self.CENTRE))
        placed = self.placement([("ran_ffh_anzac", 0, 10.2), ("ran_ffh_anzac", -6, 14)])
        zones = bp.deployment_zones(mission, placed, {"straggler": ["Taskforce1Vessel2"]})
        self.assertEqual(list(mission["_parked"]), ["Taskforce1Vessel1"])
        self.assertIn("0.2 NM off the edge of the 10 NM circle", mission["_parked"]["Taskforce1Vessel1"])
        self.assertEqual([z["tags"] for z in zones], [["Taskforce1Vessel2"]])
        self.assertGreaterEqual(self.box(zones[0])[2], 14 - bp.DEPLOY_NEAR_PAD_NM)
        bp.check_deployment_cover(mission, placed, zones)

    def test_the_gate_refuses_a_box_that_reaches_into_an_arrival_circle(self):
        mission = self.mission(victory=self.arrive(0, 30, 12))
        placed = self.placement([("plan_type_054a_p5", 0, 0)])
        zones = bp.deployment_zones(mission, placed, self.HULL)
        text = ("[Trigger1]\nName=Objective met\nCondition_Condition1_Type=UnitsInTheArea\n"
                "Condition_Condition1_PositionNM=0.00,0,30.00\nCondition_Condition1_AreaRadiusNM=12\n"
                "Condition_Condition1_Units=Taskforce1Vessel1\n")
        bp.check_zone_areas(mission, placed, zones, text)          # north edge at 13: clear
        zones[0]["height"] += 20                                   # north edge to 33: 15 NM inside
        zones[0]["at"] = (zones[0]["at"][0] + 10 / 60.0, zones[0]["at"][1])
        with self.assertRaises(SystemExit) as cm:
            bp.check_zone_areas(mission, placed, zones, text)
        self.assertIn("placed into an objective", str(cm.exception))
        self.assertIn("Zone1 (Deployment Zone)", str(cm.exception))

    # --- generated missions: the stock pattern (15 October) ---------------

    def generated(self):
        """The anchor, an escort 0.6 NM off her, a freighter of the convoy
        4 NM off, a slot-tagged P-8 and a supplied Triton 40 NM away."""
        placed = self.placement([("ran_ffh_anzac", 0, 0), ("ran_ffh_anzac", 0.6, 0),
                                 ("civ_ms_freighter_a", 0, 4)])
        placed["Taskforce1Aircraft"] = [
            ("Taskforce1Aircraft1", _keys("usn_p8", 40, 0, TaskForceModeAirTaskingSlot="1"), None, False),
            ("Taskforce1Aircraft2", _keys("raaf_mq-4c_triton", 40, 6), None, False)]
        return self.mission(generation="Generated"), placed

    def test_a_generated_mission_boxes_the_anchor_and_the_slots_only(self):
        mission, placed = self.generated()
        zones = bp.deployment_zones(mission, placed, {})
        self.assertEqual([(z["label"], z["tags"]) for z in zones],
                         [("Deployment Zone", ["Taskforce1Vessel1"]),
                          ("Air Station", ["Taskforce1Aircraft1"])])
        for x, z in ((0.6, 0), (0, 4), (40, 6)):          # escort, freighter, Triton
            self.assertFalse(any(self.holds(zone, x, z) for zone in zones), (x, z))
        west, east, south, north = self.box(zones[0])
        self.assertLessEqual(east, 0.6 - bp.DEPLOY_KEEP_OUT_NM + 0.05)   # the escort cut out
        bp.check_deployment_cover(mission, placed, zones)

    def test_the_gate_refuses_a_generated_box_holding_a_supplied_unit(self):
        mission, placed = self.generated()
        zones = bp.deployment_zones(mission, placed, {})
        zones[0]["width"] += 20                              # now reaches the escort
        with self.assertRaisesRegex(SystemExit, "Taskforce1Vessel2 in Zone1"):
            bp.check_deployment_cover(mission, placed, zones)

    def test_a_panel_mission_flags_every_unit_it_supplies_as_stock_09_does(self):
        mission, placed = self.generated()
        placed["Taskforce1Vessel"][0][1]["TaskForceModeAnchor"] = "True"
        placed["Taskforce1Helicopter"] = [
            ("Taskforce1Helicopter1", _keys("usn_mh-60r", 0, 1), None, False)]
        placed["Taskforce1Submarine"] = [
            ("Taskforce1Submarine1", _keys("ran_ss_collins", 0, 8), None, False)]
        self.assertTrue(bp.deployment_panel(mission, placed))
        self.assertEqual(bp.mark_supplied(mission, placed),
                         ["Taskforce1Vessel2", "Taskforce1Vessel3",
                          "Taskforce1Submarine1",
                          "Taskforce1Aircraft2", "Taskforce1Helicopter1"])
        flagged = {tag for entries in placed.values() for tag, keys, _n, _x in entries
                   if keys.get("TaskForceModeIgnoreUnit") == "True"}
        self.assertNotIn("Taskforce1Vessel1", flagged)        # the anchor
        self.assertNotIn("Taskforce1Aircraft1", flagged)      # the slot
        self.assertIn("Taskforce1Submarine1", flagged)        # retain the supplied boat
        text = bp.block("Taskforce1Vessel3", placed["Taskforce1Vessel"][2][1])
        self.assertIn("TaskForceModeIgnoreUnit=True", text)

    def test_no_panel_no_flag(self):
        mission, placed = self.generated()
        mission.pop("generation")                             # blank: launches as authored
        self.assertFalse(bp.deployment_panel(mission, placed))
        self.assertEqual(bp.mark_supplied(mission, placed), [])
        mission, placed = self.generated()
        mission["detached"] = True                            # the force does not sail
        self.assertEqual(bp.mark_supplied(mission, placed), [])

    def test_a_granted_unit_joins_and_is_never_ignored(self):
        mission, placed = self.generated()
        placed["Taskforce1Aircraft"][1][1]["JoinTaskForce"] = "True"
        self.assertNotIn("Taskforce1Aircraft2", bp.mark_supplied(mission, placed))

    def test_only_a_box_a_hull_can_be_moved_in_is_held_off_land(self):
        saved = bp.fix_land_positions.water
        bp.fix_land_positions.water = lambda *a, **k: False       # land everywhere
        try:
            main, air = self.zones([("plan_type_054a_p5", 0, 0), ("usn_p8", 0, 60, "Aircraft")])
        finally:
            bp.fix_land_positions.water = saved
        self.assertEqual((main["width"], main["height"]), (6.0, 6.0))   # the pad alone
        self.assertEqual((air["width"], air["height"]), (56.0, 56.0))   # fully open

    def test_the_build_stops_when_a_unit_is_outside_every_box_of_its_type(self):
        m = self.mission()
        placed = self.placement([("plan_type_054a_p5", 0, 0), ("usn_p8", 0, 60, "Aircraft")])
        zones = bp.deployment_zones(m, placed, {})
        bp.check_deployment_cover(m, placed, zones)                 # as built: fine
        with self.assertRaises(SystemExit) as stop:
            bp.check_deployment_cover(m, placed, zones[:1])         # the aircraft's box dropped
        self.assertIn("usn_p8 at Taskforce1Aircraft1 (Aircraft", str(stop.exception))
        # a box of the wrong type over the unit does not count
        wrong = [dict(zones[1], types="Submarine")]
        with self.assertRaises(SystemExit):
            bp.check_deployment_cover(m, placed, zones[:1] + wrong)
        # a base outside every box is not a reason to stop
        bases = self.placement([("plan_type_054a_p5", 0, 0), ("airfield_small_1", 300, 300, "LandUnit")])
        bp.check_deployment_cover(m, bases, bp.deployment_zones(m, bases, {}))

    def test_the_mission_file_carries_every_box_in_order(self):
        placed, members = small_placement()
        placed["Taskforce1Aircraft"] = [("Taskforce1Aircraft1", _keys("usn_p8", 0, 70), None, False)]
        _name, text = bp.render(small_mission(), placed, members)
        self.assertIn("Zone1Label_en=Deployment Zone\nZone2Label_en=Detachment Zone\n"
                      "Zone3Label_en=Air Station", text)
        self.assertIn("NumberOfZones=3\nZone1=Zone1\nZone2=Zone2\nZone3=Zone3\n", text)
        self.assertIn("[Zone3]\nType=Deployment", text)
        self.assertIn("AllowedUnitTypes=Aircraft\n", text)


class AlliedFleetReview(unittest.TestCase):
    """The review of 2e845dc9: the flight rule on allied aircraft, the allied
    sentence's grammar, and the gate on a twin that drifted. The twins are
    built into a temporary folder (built_twin): none ships since 21 Oct 2026."""

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

    def test_the_allied_sentence_counts_the_allied_fleet_not_the_roster(self):
        # Sulu Line's own roster sells Thai, Australian and MSC units, and
        # the sentence built from the twin's whole roster called them "the
        # allied fleet ... 5 classes from Thailand, Australia and USA" (until
        # 20 Oct 2026). The builder passes the allied entries alone; Sulu's
        # commander calls on none.
        spec = next(s for s in bp.campaign_specs() if s["SLUG"] == "sest-sulu-line")
        self.assertTrue(bp.allied_line(spec["ROSTER"], spec["COMMANDER"]))
        self.assertEqual(spec["ALLIED_FLEET"], [])
        self.assertEqual(bp.allied_line(spec["ALLIED_FLEET"], spec["COMMANDER"]), "")
        tmp = Path(tempfile.mkdtemp())
        try:
            if built_twin(spec["SLUG"], tmp) is None:
                self.skipTest("pack not built")
            twin = tmp / "campaigns" / bp.open_slug(spec["SLUG"]) / "campaign.ini"
            description = re.search(r"^Description=(.*)$", twin.read_text(encoding="utf-8"),
                                    re.M).group(1)
            self.assertNotIn("allied fleet", description)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_the_gate_refuses_a_twin_that_drifted(self):
        slug = "sest-red-line"
        tmp = Path(tempfile.mkdtemp())
        try:
            twin = built_twin(slug, tmp)
            if twin is None:
                self.skipTest("pack not built")
            # Red Line's twin added its commander's PLAN support ships until
            # 21 Oct 2026; the standard campaign's reserve sells them now, so
            # they are on the roster the twin starts from and it adds none.
            self.assertEqual([e["unit"] for e in twin["allied"]], [])
            self.assertEqual([e["unit"] for e in twin["roster"]][-2:],
                             ["plan_aor_type901", "plan_aor_type903a"])
            self.assertEqual(coverage_check.open_twin(tmp, slug), [])
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

    def test_the_gate_refuses_a_twin_that_sells_a_held_unit(self):
        # Sulu Line's twin sells its supply ships only where the story does
        # (OPEN_HOLD). The C8 back at The Island Road is the shipped defect.
        slug = "sest-sulu-line"
        hold = next(s for s in bp.campaign_specs() if s["SLUG"] == slug)["OPEN_HOLD"]
        tmp = Path(tempfile.mkdtemp())
        try:
            if built_twin(slug, tmp) is None:
                self.skipTest("pack not built")
            self.assertEqual(coverage_check.open_twin(tmp, slug, hold), [])
            # Without the hold, the gate expects every window to sell all.
            self.assertTrue(coverage_check.open_twin(tmp, slug))
            ini = tmp / "campaigns" / bp.open_slug(slug) / "campaign.ini"
            good = ini.read_text(encoding="utf-8")
            first = good.index("TaskForceModeAllowedRosterUnits=")
            end = good.index("\n", first)
            bad = good[:end] + "|civ_ms_c8,Variant1,Variant2" + good[end:]
            ini.write_text(bad, encoding="utf-8")
            self.assertTrue(coverage_check.open_twin(tmp, slug, hold))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class AlliedReserve(unittest.TestCase):
    """The allied reserve (mission_depth.apply_reserve): what a standard
    campaign sells beside its own navy from a window its story names, never
    a hull a mission places. The owner's decisions of 20 Oct 2026 sold
    escorts only - eleven classes in Southern Watch from Weapons Free (Q2),
    three in Southern Reach from Tasman Crossing (Q3). On 21 Oct, retiring
    the Open Allocation twins, the owner put what they sold in the standard
    campaigns from those same windows: the whole allied fleet, aircraft
    where a row launches and recovers them, and in Red Line the PLAN's own
    Type 901 and 903A from Trailing Contact. Sulu Line's commander calls on
    none, and its twin sold nothing beyond its roster. Later that day (step
    2) each window from the same opening was opened to the whole roster as
    well: OpenAllocationStandard."""

    PACK = bp.ROOT / "integration" / "campaign" / "SEST_Campaign" / "campaigns"
    OPENS = {"sest-southern-watch": "SW05", "sest-southern-reach": "TS04",
             "sest-red-line": "RL01"}
    # The opening window's own entry in the built spine.
    HEADS = {"sest-southern-watch": "#05 ", "sest-southern-reach": "#TS04 ",
             "sest-red-line": "#RL01 "}
    COVERAGE = {"sest-southern-watch": bp.ROOT / "docs" / "campaign-coverage.md",
                "sest-southern-reach": bp.ROOT / "docs" / "campaigns" / "southern-reach"
                / "coverage.md",
                "sest-red-line": bp.ROOT / "docs" / "campaigns" / "red-line" / "coverage.md"}
    # usable_allied's three reasons for leaving an aircraft out, and the
    # named-hull filter's one for a ship.
    AIR_REASONS = ("no air-tasking row in this campaign takes it",
                   "a row takes its role but offers none of its fits: ",
                   "no field or deck in reach in ")
    PLACED = "every hull it prices is placed by a mission"

    @classmethod
    def setUpClass(cls):
        import allied_fleet
        import mission_depth
        cls.md = mission_depth
        cls.af = allied_fleet
        cls.specs = {s["SLUG"]: s for s in bp.campaign_specs()}

    def fleet(self, slug):
        nation = re.search(r"^CommanderNations=(.+)$", self.specs[slug]["COMMANDER"],
                           re.M).group(1).strip()
        return self.af.FOR_NATION.get(nation, [])

    def windows(self, slug):
        """[(code, allowlist)] - every buy window of the campaign, in date order."""
        buying = [m for m in self.specs[slug]["MISSIONS"] if m.get("window", {}).get("buy")]
        return [(self.md.code_of(m), m["window"].get("allow", []))
                for m in sorted(buying, key=self.md._when)]

    def built(self, slug, name):
        path = self.PACK / slug / name
        if not path.is_file():
            self.skipTest("pack not built")
        return path.read_text(encoding="utf-8")

    def built_roster(self, slug):
        """{uid: [picks]} - the built player_task_force_roster.ini."""
        text = self.built(slug, "player_task_force_roster.ini")
        return {uid: picks.split(",") for uid, picks in
                re.findall(r"^([^;\[\s=]+)=([^|\n]+)\|", text, re.M)}

    def not_sold(self, slug):
        """{uid: why} - the coverage report's record of the reserve's left-out
        classes (build_pack.reserve_report)."""
        if not self.COVERAGE[slug].is_file():
            self.skipTest("pack not built")
        text = self.COVERAGE[slug].read_text(encoding="utf-8")
        self.assertIn("## The reserve", text, slug)
        part = text.split("## The reserve", 1)[1].split("\n## ", 1)[0]
        return dict(re.findall(r"^\| `([^`]+)` \| (.*) \|$", part, re.M))

    def test_each_campaign_names_its_whole_fleet_from_its_window(self):
        for slug, opens in self.OPENS.items():
            spec, fleet = self.specs[slug], self.fleet(slug)
            self.assertTrue(fleet, slug)
            self.assertEqual(spec["RESERVE_FLEET"], dict(opens=opens), slug)
            self.assertFalse(spec.get("RESERVE"), slug)
            self.assertEqual(spec["RESERVE_OPENS"], {e["unit"]: opens for e in fleet}, slug)
            # Each class of the fleet is in exactly one place: on the roster
            # (a ship), held for the build to judge (an aircraft), or left out
            # with the reason. None stays in the fleet a twin would sell.
            on_roster = {e["unit"] for e in spec["ROSTER"]}
            held = {e["unit"] for e in spec["RESERVE_AIR"]}
            left = {e["unit"]: why for e, why in spec["RESERVE_LEFT_OUT"]}
            for e in fleet:
                self.assertEqual([e["unit"] in on_roster, e["unit"] in held,
                                  e["unit"] in left].count(True), 1, (slug, e["unit"]))
                self.assertEqual(e["unit"] in held, self.md.is_aircraft(e), (slug, e["unit"]))
            self.assertEqual(spec["ALLIED_FLEET"], [], slug)
            self.assertEqual(set(left.values()) - {self.PLACED}, set(), slug)
            # The roster grows by the fleet's ships less those left out.
            ships = [e for e in fleet if not self.md.is_aircraft(e)]
            sold = [e for e in spec["ROSTER"] if e["unit"] in spec["RESERVE_OPENS"]]
            self.assertEqual(len(sold), len(ships) - len(left), slug)
        # Every hull of HMAS Choules and of the Supply-class AOR sails in a
        # Southern Watch or Southern Reach mission; the twins sold them.
        for slug in ("sest-southern-watch", "sest-southern-reach"):
            self.assertEqual(sorted(e["unit"] for e, _w in self.specs[slug]["RESERVE_LEFT_OUT"]),
                             ["ran_aor_supply", "ran_lsd_choules"], slug)
        self.assertFalse(self.specs["sest-sulu-line"].get("RESERVE_OPENS"))
        self.assertEqual(self.specs["sest-sulu-line"]["ALLIED_FLEET"], [])

    def test_windows_before_the_opening_keep_the_storys_own_lists(self):
        import campaign_data as sw
        for slug, opens in self.OPENS.items():
            reserve = set(self.specs[slug]["RESERVE_OPENS"])
            ships = reserve & {e["unit"] for e in self.specs[slug]["ROSTER"]}
            opened = False
            for code, allow in self.windows(slug):
                opened = opened or code == opens
                self.assertEqual(set(allow) & reserve, ships if opened else set(), (slug, code))
                self.assertEqual(len(allow), len(set(allow)), (slug, code))
            self.assertTrue(opened, slug)
        story = {code: allow for code, allow in self.windows("sest-southern-watch")}
        self.assertEqual([story["SW01"], story["SW02"], story["SW03"]],
                         [sw.BUY_01, sw.BUY_02, sw.BUY_03])
        # From the opening each window offers the whole roster, in roster
        # order, every story unit among it (step 2, 21 Oct 2026; until then
        # the story's own list came first and the reserve after it). The
        # lists campaign_data shares between windows were replaced, never
        # extended in place (BUY_03 is BUY_02, BUY_09 is BUY_07).
        roster = [e["unit"] for e in self.specs["sest-southern-watch"]["ROSTER"]]
        for code, own in (("SW05", sw.BUY_05), ("SW09", sw.BUY_09), ("SW11", sw.BUY_11),
                          ("SW12", sw.BUY_12)):
            self.assertEqual(story[code], roster, code)
            self.assertEqual(set(own) - set(story[code]), set(), code)
        for name in ("BUY_01", "BUY_02", "BUY_03", "BUY_05", "BUY_07", "BUY_09", "BUY_11",
                     "BUY_12"):
            self.assertFalse(set(getattr(sw, name)) & set(self.specs["sest-southern-watch"]
                                                          ["RESERVE_OPENS"]), name)

    def test_a_second_call_changes_nothing(self):
        before = {slug: ([e["unit"] for e in s["ROSTER"]], self.windows(slug),
                         [e["unit"] for e in s.get("RESERVE_AIR", [])])
                  for slug, s in self.specs.items()}
        again = {s["SLUG"]: s for s in bp.campaign_specs()}
        for slug, s in again.items():
            self.assertEqual(([e["unit"] for e in s["ROSTER"]], self.windows(slug),
                              [e["unit"] for e in s.get("RESERVE_AIR", [])]), before[slug], slug)

    def test_admitted_aircraft_are_sold_from_the_opening_and_said_once(self):
        # On a copy: main() admits what usable_allied keeps after placement,
        # then each window from the opening says what the reserve sells.
        spec = copy.deepcopy(self.specs["sest-southern-reach"])
        held = spec["RESERVE_AIR"]
        kept, dropped = held[:2], [(e, self.AIR_REASONS[0]) for e in held[2:]]
        self.md.admit_aircraft(spec, kept, dropped)
        self.md.admit_aircraft(spec, kept, dropped)
        self.md.say_reserve(spec)
        self.md.say_reserve(spec)
        units = [e["unit"] for e in spec["ROSTER"]]
        self.assertEqual(len(units), len(set(units)))
        self.assertEqual(len(spec["RESERVE_LEFT_OUT"]), 2 + len(held) - 2)
        allied = [e for e in spec["ROSTER"] if e["unit"] in spec["RESERVE_OPENS"]
                  and self.md._navy(e) != "Australia"]
        ships = sum(1 for e in allied if not self.md.is_aircraft(e))
        by_code = {self.md.code_of(m): m for m in spec["MISSIONS"]}
        ts04 = by_code["TS04"]["window"]
        for e in kept:
            self.assertIn(e["unit"], ts04["allow"])
            self.assertNotIn(e["unit"], by_code["TS01"]["window"]["allow"])
        # The window offers the whole roster with the kept aircraft, in
        # roster order, the admitted ones last.
        self.assertEqual(ts04["allow"], units)
        lead = " This force allocation offers the campaign's whole roster"
        self.assertEqual(ts04["situation"].count(lead), 1)
        said = ts04["situation"].split(lead, 1)[1]
        self.assertTrue(said.startswith(" and, at their own navies' prices, the allied fleet - "
                                        f"{ships} ship classes and 2 aircraft types from the "
                                        "USA, "), said)
        self.assertTrue(said.endswith(" - and the Royal Australian Navy's Canberra-class LHD."),
                        said)
        self.assertNotIn("Also on sale", ts04["situation"])
        self.assertNotIn(lead, by_code["TS01"]["window"]["situation"])
        # Red Line's are its own navy's ships, and never called allied.
        rl = copy.deepcopy(self.specs["sest-red-line"])
        self.md.admit_aircraft(rl, [], [])
        self.md.say_reserve(rl)
        rl01 = next(m for m in rl["MISSIONS"] if self.md.code_of(m) == "RL01")
        self.assertTrue(rl01["window"]["situation"].endswith(
            lead + " and the People's Liberation Army Navy's Type 901 Fuyu fast combat "
            "support ship and Type 903A Fuchi replenishment oiler."))

    def test_a_class_with_no_hull_left_is_set_aside_not_fatal(self):
        def spec(windows, fleet, placed=(), named=(), whole="M2"):
            missions = [dict(code=code, num=code, key=f"Mission {code}", group="core",
                             date=(2028, 10, n + 1), units=[], window=w)
                        for n, (code, w) in enumerate(windows)]
            missions[0]["units"] = [dict(type=t, variant=v) for t, v in placed]
            out = dict(TITLE="Test", COMMANDER="CommanderNations=Australia\n",
                       MISSIONS=missions, ALLIED_FLEET=fleet,
                       ROSTER=[dict(unit="ran_ffh_anzac", picks=["Variant3"], points=240)],
                       RESERVE=list(named))
            if whole:
                out["RESERVE_FLEET"] = dict(opens=whole)
            return out
        fleet = [dict(unit="rn_ff_type23", picks=["Variant3"], points=260,
                      note="United Kingdom - Type 23 class (LIFEX)"),
                 dict(unit="js_ffg_mogami", picks=["Variant1", "Variant2"], points=300,
                      note="Japan - Mogami-class"),
                 dict(unit="usn_p8_2027", picks=["Squadron1"], points=55,
                      note="USA - P-8A Poseidon (2027)")]
        windows = [("M1", dict(buy=True, allow=["ran_ffh_anzac"])),
                   ("M2", dict(buy=True, allow=["ran_ffh_anzac"]))]
        s = spec(windows, copy.deepcopy(fleet),
                 placed=[("rn_ff_type23", "Variant3"), ("js_ffg_mogami", "Variant1")])
        self.md.apply_reserve([s])
        self.assertEqual([(e["unit"], why) for e, why in s["RESERVE_LEFT_OUT"]],
                         [("rn_ff_type23", self.PLACED)])
        self.assertEqual(next(e for e in s["ROSTER"] if e["unit"] == "js_ffg_mogami")["picks"],
                         ["Variant2"])
        self.assertEqual([e["unit"] for e in s["RESERVE_AIR"]], ["usn_p8_2027"])
        self.assertEqual([w["allow"] for _c, w in windows],
                         [["ran_ffh_anzac"], ["ran_ffh_anzac", "js_ffg_mogami"]])
        # With no class of the commander's own navy among them, the words
        # are the allied fleet's alone.
        self.assertEqual(self.md.reserve_phrase(s, ["js_ffg_mogami"]),
                         "the allied fleet, 1 ship class from Japan")
        # A named class may open earlier than the rest of the fleet.
        windows = [("M1", dict(buy=True, allow=["ran_ffh_anzac"])),
                   ("M2", dict(buy=True, allow=["ran_ffh_anzac"]))]
        s = spec(windows, copy.deepcopy(fleet), named=[dict(unit="js_ffg_mogami", opens="M1")])
        self.md.apply_reserve([s])
        self.assertEqual(s["RESERVE_OPENS"], {"js_ffg_mogami": "M1", "rn_ff_type23": "M2",
                                              "usn_p8_2027": "M2"})
        self.assertEqual([w["allow"] for _c, w in windows],
                         [["ran_ffh_anzac", "js_ffg_mogami"],
                          ["ran_ffh_anzac", "js_ffg_mogami", "rn_ff_type23"]])
        # A window with no allowlist before the opening would sell it early;
        # an opening that is not a mission here is a typo.
        with self.assertRaisesRegex(SystemExit, "M1's window has no allowlist"):
            self.md.apply_reserve([spec([("M1", dict(buy=True)), ("M2", dict(buy=True))],
                                        copy.deepcopy(fleet))])
        with self.assertRaisesRegex(SystemExit, "which is not one of its missions"):
            self.md.apply_reserve([spec(windows, copy.deepcopy(fleet), whole="M9")])

    def test_no_reserve_hull_is_one_a_mission_places(self):
        # Southern Reach sold JS Mogami (Variant1; Common Sea, The Other
        # Picture) and Daegu (Variant1; O3) until 20 Oct 2026: the filter
        # looked at its own campaign's blue units only. The twins sold JS
        # Maya Variant1, which Red Line places, until 21 Oct.
        placed = {(u["type"], u.get("variant", "Variant1"))
                  for spec in self.specs.values() for m in spec["MISSIONS"]
                  if m["group"] != "dispatch" for u in m["units"]}
        for slug in self.OPENS:
            spec = self.specs[slug]
            for e in spec["ROSTER"]:
                if e["unit"] in spec["RESERVE_OPENS"]:
                    self.assertTrue(e["picks"], (slug, e["unit"]))
                    for pick in e["picks"]:
                        self.assertNotIn((e["unit"], pick), placed, slug)
        for slug in ("sest-southern-watch", "sest-southern-reach"):
            sold = {e["unit"]: e["picks"] for e in self.specs[slug]["ROSTER"]}
            self.assertEqual(sold["jmsdf_ddg_maya"], ["Variant2"], slug)
            self.assertNotIn("Variant1", sold["js_ffg_mogami"], slug)
            self.assertNotIn("Variant1", sold["ko_ffg-818"], slug)
        rl = {e["unit"]: e["picks"] for e in self.specs["sest-red-line"]["ROSTER"]}
        self.assertEqual(rl["plan_aor_type901"], ["Variant2"])
        self.assertEqual(rl["plan_aor_type903a"], ["Variant2", "Variant3", "Variant4"])

    def test_no_reserve_hull_on_sale_is_placed_in_a_built_mission(self):
        # The same rule on the built bytes, where a variant left to the
        # file's default is spelled out: every reserve pick on a standard
        # roster against every VariantReference of every campaign mission.
        placed = set()
        for ini in self.PACK.glob("*/missions/*.ini"):
            for block in re.split(r"\n(?=\[)", ini.read_text(encoding="utf-8")):
                kind = re.search(r"^Type=(\S+)", block, re.M)
                variant = re.search(r"^VariantReference=(\S+)", block, re.M)
                if kind and variant:
                    placed.add((kind.group(1), variant.group(1)))
        for slug in self.OPENS:
            reserve = set(self.specs[slug]["RESERVE_OPENS"])
            for uid, picks in self.built_roster(slug).items():
                if uid in reserve:
                    for pick in picks:
                        self.assertNotIn((uid, pick), placed, slug)
        self.assertGreater(len(placed), 100)

    def test_no_submarine_is_on_sale(self):
        for slug in self.OPENS:
            self.assertNotIn("[AllowedSubmarines]", self.built(slug, "player_task_force_roster.ini"))
            for uid in self.built_roster(slug):
                self.assertNotEqual(bp.unit_type(uid), "Submarine", (slug, uid))

    def test_the_built_rosters_sell_what_the_twins_sold(self):
        # The Open Allocation twins sold the whole fleet beside the roster
        # until 21 Oct 2026, aircraft where usable_allied kept them. Every
        # class of it is on the built standard roster now or in the
        # coverage report's record of what is not sold, with the reason.
        counts = {}
        for slug in self.OPENS:
            sold, left = self.built_roster(slug), self.not_sold(slug)
            fleet = self.fleet(slug)
            for e in fleet:
                self.assertEqual([e["unit"] in sold, e["unit"] in left].count(True), 1,
                                 (slug, e["unit"]))
                if e["unit"] in left and not self.md.is_aircraft(e):
                    self.assertEqual(left[e["unit"]], self.PLACED, (slug, e["unit"]))
                elif e["unit"] in left:
                    self.assertTrue(left[e["unit"]].startswith(self.AIR_REASONS),
                                    (slug, e["unit"], left[e["unit"]]))
            # The campaign's own roster is still sold whole.
            own = [e["unit"] for e in self.specs[slug]["ROSTER"]
                   if e["unit"] not in self.specs[slug]["RESERVE_OPENS"]]
            self.assertEqual(sorted(u for u in sold
                                    if u not in self.specs[slug]["RESERVE_OPENS"]),
                             sorted(own), slug)
            air = sum(1 for e in fleet if self.md.is_aircraft(e) and e["unit"] in sold)
            counts[slug] = (len(sold) - len(own) - air, air)
        # Ships: the fleet's less Choules and the Supply-class AOR. Aircraft:
        # the 19 and 10 the twins sold (their "63 and 62 allied units on sale"
        # less the 44 and 52 ships beyond the reserve they had).
        ships = sum(1 for e in self.af.ALLIED if not self.md.is_aircraft(e)) - 2
        self.assertEqual(counts, {"sest-southern-watch": (ships, 19),
                                  "sest-southern-reach": (ships, 10),
                                  "sest-red-line": (2, 0)})

    def test_the_aircraft_judgement_is_usable_allieds(self):
        # Re-judged here on the built missions, read back into the placement
        # shape airframe_rows reads (each Taskforce section's keys), against
        # the rows widened by the campaign's own roster as main() widens
        # them. What usable_allied keeps is what the built roster sells and
        # what it drops is the record, word for word.
        for slug in ("sest-southern-watch", "sest-southern-reach"):
            spec = self.specs[slug]
            sold, left = self.built_roster(slug), self.not_sold(slug)
            bp.set_campaign(spec)
            missions = copy.deepcopy(spec["MISSIONS"])
            bp.widen_flights(missions, spec["ROSTER"])
            rows = [r for m in missions for r in m.get("window", {}).get("flights", [])]
            authored = {u["type"] for m in missions for u in m["units"] if u.get("slot")}
            placements = {}
            for m in missions:
                if m["group"] == "dispatch":
                    path = PACK / "missions" / bp.browse_folder(m) / f"{bp.mission_name(m)}.ini"
                else:
                    path = self.PACK / slug / "missions" / f"{bp.mission_name(m)}.ini"
                self.assertTrue(path.is_file(), path)
                placed = collections.defaultdict(list)
                for tag, keys in coverage_check.blocks(path.read_text(encoding="utf-8")).items():
                    family = re.match(r"(Taskforce\d+\D+?)\d+$", tag)
                    if family and keys.get("Type"):
                        placed[family.group(1)].append((tag, keys, None, None))
                placements[m["key"]] = placed
            held = {e["unit"] for e in spec["RESERVE_AIR"]}
            kept, dropped = bp.usable_allied(spec["RESERVE_AIR"], missions, placements, rows,
                                             spec["ROSTER"], authored)
            self.assertEqual(sorted(e["unit"] for e in kept),
                             sorted(u for u in sold if u in held), slug)
            self.assertEqual({e["unit"]: why for e, why in dropped},
                             {u: why for u, why in left.items() if u in held}, slug)

    def test_the_built_windows_follow_the_reserve(self):
        for slug in self.OPENS:
            sold = self.built_roster(slug)
            reserve = {u for u in sold if u in self.specs[slug]["RESERVE_OPENS"]}
            self.assertTrue(reserve, slug)
            opened, windows = False, 0
            for sec in re.split(r"\n(?=\[)", self.built(slug, "campaign.ini")):
                head = sec.split("\n", 1)[0]
                opened = opened or self.HEADS[slug] in head
                allow = re.search(r"^TaskForceModeAllowedRosterUnits=(.*)$", sec, re.M)
                if allow:
                    windows += 1
                    on_sale = {e.split(",")[0] for e in allow.group(1).split("|")}
                    self.assertEqual(on_sale & reserve, reserve if opened else set(), head)
                    situation = re.search(r"^TaskForceModeBuilderSituation_en=(.*)$", sec,
                                          re.M).group(1)
                    self.assertEqual(situation.count("This force allocation offers the "
                                                     "campaign's whole roster"),
                                     int(opened), head)
                    self.assertNotIn("Also on sale here", situation, head)
            self.assertTrue(opened and windows, slug)


class OpenAllocationStandard(unittest.TestCase):
    """Open Allocation built into the standard campaigns (the owner's
    decision of 21 Oct 2026, step 2): from the window where the allied
    reserve opens - Weapons Free, Tasman Crossing, Red Line's first force
    allocation - every force allocation offers the campaign's whole roster,
    every priced variant, with the fleet the reserve admits, as the Open
    Allocation versions did from the first (mission_depth.open_from,
    open_offer). Step 1 had added the fleet after each story list, so the
    window before Fujian's Shadow still sold no Seahawk, Wedgetail or Triton
    and Red Line's aircraft waited for the windows its story released them
    at. The windows before the opening, and every window without a builder,
    are the story's own. Sulu Line has no opening and is unchanged."""

    PACK = AlliedReserve.PACK
    OPENS = AlliedReserve.OPENS
    COVERAGE = AlliedReserve.COVERAGE
    LEAD = " This force allocation offers the campaign's whole roster"

    @classmethod
    def setUpClass(cls):
        import allied_fleet
        import mission_depth
        cls.md = mission_depth
        cls.af = allied_fleet
        cls.specs = {s["SLUG"]: s for s in bp.campaign_specs()}
        cls.story = story_windows()

    def built(self, slug):
        """{mission code: its [MissionN] section} of the built spine."""
        path = self.PACK / slug / "campaign.ini"
        if not path.is_file():
            self.skipTest("pack not built")
        bp.set_campaign(self.specs[slug])
        by_file = {bp.mission_name(m): self.md.code_of(m) for m in self.specs[slug]["MISSIONS"]}
        out = {}
        for sec in re.split(r"\n(?=\[)", path.read_text(encoding="utf-8")):
            f = re.search(r"^MissionFile=campaigns/[^/]+/missions/(.+)\.ini$", sec, re.M)
            if f:
                out[by_file[f.group(1)]] = sec
        return out

    @staticmethod
    def key(sec, name):
        m = re.search(rf"^{name}=(.*)$", sec, re.M)
        return m.group(1) if m else None

    def built_roster(self, slug):
        """{uid: [picks]} - the built player_task_force_roster.ini."""
        text = (self.PACK / slug / "player_task_force_roster.ini").read_text(encoding="utf-8")
        return {uid: picks.split(",") for uid, picks in
                re.findall(r"^([^;\[\s=]+)=([^|\n]+)\|", text, re.M)}

    def whole(self, slug):
        """The roster as the build settled it: the spec's, then the reserve
        aircraft the build admitted, in the order admit_aircraft() appends
        them (RESERVE_AIR's, those the built roster sells)."""
        spec, sold = self.specs[slug], self.built_roster(slug)
        return spec["ROSTER"] + [e for e in spec.get("RESERVE_AIR", []) if e["unit"] in sold]

    def is_open(self, slug, m):
        start = self.md.open_from(self.specs[slug])
        return (start is not None and m.get("window", {}).get("buy")
                and self.md._when(m) >= self.md._when(start))

    @staticmethod
    def offer(line):
        return {(e.split(",")[0], p) for e in line.split("|") for p in e.split(",")[1:]}

    def test_every_window_from_the_opening_offers_the_whole_roster(self):
        for slug, opens in self.OPENS.items():
            spec, built = self.specs[slug], self.built(slug)
            self.assertEqual(self.md.code_of(self.md.open_from(spec)), opens, slug)
            whole = self.whole(slug)
            # Every priced variant: the built roster file is the whole roster.
            self.assertEqual({e["unit"]: e["picks"] for e in whole}, self.built_roster(slug),
                             slug)
            line = bp.allowed_roster_units([e["unit"] for e in whole], whole, slug)
            windows = 0
            for m in spec["MISSIONS"]:
                if not self.is_open(slug, m):
                    continue
                windows += 1
                code, sec = self.md.code_of(m), built[self.md.code_of(m)]
                self.assertEqual(self.key(sec, "TaskForceModeAllowedRosterUnits"), line,
                                 (slug, code))
                # The story's own list is all on offer: nothing it sold is lost.
                story = self.story[slug][code]["allow"] or []
                self.assertEqual(set(story) - {e["unit"] for e in whole}, set(), (slug, code))
                situation = self.key(sec, "TaskForceModeBuilderSituation_en")
                self.assertTrue(situation.startswith(
                    bp.ini_text(self.story[slug][code]["situation"]) + self.LEAD + " and"),
                    (slug, code, situation))
                self.assertEqual(situation.count(self.LEAD), 1, (slug, code))
                self.assertNotIn("Also on sale here", situation, (slug, code))
            self.assertGreater(windows, 0, slug)
        # What the story held back from a window it now offers: the cases
        # the owner's request named.
        def sold(slug, code):
            return {u for u, _p in self.offer(self.key(self.built(slug)[code],
                                                       "TaskForceModeAllowedRosterUnits"))}
        self.assertLessEqual({"ran_mh-60r", "E7A_Wedgetail", "raaf_mq-4c_triton"},
                             sold("sest-southern-watch", "SW11"))
        self.assertLessEqual({"ran_ddg_hobart", "usn_ea-18g"}, sold("sest-southern-watch", "SW12"))
        self.assertIn("raaf_mq-4c_triton", sold("sest-southern-watch", "SW05"))
        self.assertIn("ran_ddg_hobart", sold("sest-southern-reach", "TS12"))
        rl = {e["unit"] for e in self.specs["sest-red-line"]["ROSTER"]}
        for code in ("RL01", "RL02", "RL03", "RL06"):
            self.assertEqual(sold("sest-red-line", code), rl, code)
        # Red Line's window words stay the PLAN's own.
        for sec in self.built("sest-red-line").values():
            self.assertNotIn("llied", self.key(sec, "TaskForceModeBuilderSituation_en") or "")

    def test_windows_before_the_opening_and_without_a_builder_are_the_storys(self):
        # Every window but an open one, in every campaign, Sulu Line's all:
        # the spec's list and words are the story's, and the built line is
        # allowed_roster_units() of the story's list.
        checked = collections.Counter()
        for slug, spec in self.specs.items():
            built = self.built(slug)
            whole = self.whole(slug)
            for m in spec["MISSIONS"]:
                if self.is_open(slug, m):
                    continue
                code, w, story = self.md.code_of(m), m.get("window", {}), self.story[slug]
                self.assertEqual((bool(w.get("buy")), w.get("allow"), w.get("situation", "")),
                                 (story[code]["buy"], story[code]["allow"],
                                  story[code]["situation"]), (slug, code))
                if code not in built:
                    continue            # a Dispatch: the campaign never loads it
                sec = built[code]
                allow = story[code]["allow"]
                self.assertEqual(self.key(sec, "TaskForceModeAllowedRosterUnits"),
                                 bp.allowed_roster_units(allow, whole, code)
                                 if story[code]["buy"] and allow else None, (slug, code))
                self.assertEqual(self.key(sec, "TaskForceModeBuilderSituation_en"),
                                 bp.ini_text(story[code]["situation"])
                                 if story[code]["situation"] else None, (slug, code))
                checked["buy" if story[code]["buy"] else "no builder"] += 1
        # Southern Watch's three, Southern Reach's eight and Sulu Line's four
        # buy windows; Red Line opens at its first.
        self.assertEqual(checked["buy"], 3 + 8 + 4)
        self.assertTrue(checked["no builder"])
        self.assertIsNone(self.md.open_from(self.specs["sest-sulu-line"]))

    def test_the_story_lists_are_replaced_not_extended(self):
        # campaign_data's windows share their lists (BUY_03 is BUY_02, BUY_09
        # is BUY_07): an open window is given a new list, and the module's
        # stay as the story wrote them.
        import campaign_data as sw
        story = self.story["sest-southern-watch"]
        for code, name in (("SW01", "BUY_01"), ("SW02", "BUY_02"), ("SW03", "BUY_03"),
                           ("SW05", "BUY_05"), ("SW09", "BUY_09"), ("SW11", "BUY_11"),
                           ("SW12", "BUY_12")):
            self.assertEqual(getattr(sw, name), story[code]["allow"], name)
        for m in self.specs["sest-southern-watch"]["MISSIONS"]:
            if self.is_open("sest-southern-watch", m):
                for name in ("BUY_05", "BUY_07", "BUY_09", "BUY_11", "BUY_12"):
                    self.assertIsNot(m["window"]["allow"], getattr(sw, name))

    def test_opening_twice_changes_nothing(self):
        # Admission, the windows and the words, each run twice on a copy:
        # main() runs them once, campaign_specs() may run many times.
        spec = copy.deepcopy(self.specs["sest-southern-watch"])
        held = spec["RESERVE_AIR"]
        self.md.admit_aircraft(spec, held[:3], [(e, "x") for e in held[3:]])
        once = {self.md.code_of(m): list(m["window"]["allow"])
                for m in spec["MISSIONS"] if m.get("window", {}).get("buy")}
        self.md.admit_aircraft(spec, held[:3], [(e, "x") for e in held[3:]])
        self.md._open_windows(spec, [e["unit"] for e in spec["ROSTER"]
                                     if e["unit"] in spec["RESERVE_OPENS"]])
        self.md.say_reserve(spec)
        self.md.say_reserve(spec)
        roster = [e["unit"] for e in spec["ROSTER"]]
        self.assertEqual(len(roster), len(set(roster)))
        for m in spec["MISSIONS"]:
            w = m.get("window", {})
            if not w.get("buy"):
                continue
            code = self.md.code_of(m)
            self.assertEqual(w["allow"], once[code], code)
            if self.is_open("sest-southern-watch", m):
                self.assertEqual(w["allow"], roster, code)
                self.assertEqual(self.md.open_offer(spec, m), roster, code)
                self.assertEqual(w["situation"].count(self.LEAD), 1, code)
            else:
                self.assertIsNone(self.md.open_offer(spec, m), code)
                self.assertNotIn(self.LEAD, w["situation"], code)

    def test_a_named_class_opening_later_waits_for_its_own_window(self):
        # A class RESERVE names may open after the fleet's window: the open
        # windows before it offer the whole roster less that class, and a
        # window without a builder gets no list.
        def spec(opens="M2"):
            fleet = [dict(unit="rn_ff_type23", picks=["Variant3"], points=260,
                          note="United Kingdom - Type 23 class (LIFEX)"),
                     dict(unit="js_ffg_mogami", picks=["Variant2"], points=300,
                          note="Japan - Mogami-class")]
            windows = [dict(buy=True, allow=["ran_ffh_anzac"]),
                       dict(buy=True, allow=["ran_ffh_anzac"]),
                       dict(repair=True),
                       dict(buy=True, allow=["ran_ffh_anzac"])]
            missions = [dict(code=f"M{n + 1}", num=f"M{n + 1}", key=f"Mission {n + 1}",
                             group="core", date=(2028, 10, n + 1), units=[], window=w)
                        for n, w in enumerate(windows)]
            return dict(TITLE="Test", COMMANDER="CommanderNations=Australia\n",
                        MISSIONS=missions, ALLIED_FLEET=fleet,
                        RESERVE=[dict(unit="js_ffg_mogami", opens="M4")],
                        RESERVE_FLEET=dict(opens=opens),
                        ROSTER=[dict(unit="ran_ffh_anzac", picks=["Variant3"], points=240),
                                dict(unit="ran_ddg_hobart", picks=["Variant1"], points=480)])
        s = spec()
        self.md.apply_reserve([s])
        self.assertEqual([m["window"].get("allow") for m in s["MISSIONS"]],
                         [["ran_ffh_anzac"],
                          ["ran_ffh_anzac", "ran_ddg_hobart", "rn_ff_type23"],
                          None,
                          ["ran_ffh_anzac", "ran_ddg_hobart", "js_ffg_mogami", "rn_ff_type23"]])
        with self.assertRaisesRegex(SystemExit, "RESERVE_FLEET opens at M9"):
            self.md.apply_reserve([spec("M9")])
        # A twin built from the opened campaign would quote the open
        # windows' sentence as the story's (review of 21 Oct 2026): a spec
        # takes OPEN_ALLOCATION or RESERVE_FLEET, not both.
        with self.assertRaisesRegex(SystemExit, "OPEN_ALLOCATION and RESERVE_FLEET are both set"):
            self.md.apply_reserve([dict(spec(), OPEN_ALLOCATION=True)])

    def test_the_coverage_report_names_windows_before_only_where_there_are_some(self):
        # Red Line opens at its first force allocation, so its report says
        # nothing of windows before it, as its rules page does not (review
        # of 21 Oct 2026); the RAN campaigns' do.
        for slug, opens in self.OPENS.items():
            spec = self.specs[slug]
            bp.set_campaign(spec)
            text = "\n".join(bp.reserve_report(spec))
            buying = sorted((m for m in spec["MISSIONS"] if m.get("window", {}).get("buy")),
                            key=self.md._when)
            first = self.md.code_of(buying[0]) == opens
            self.assertEqual("the ones before it offer what the story releases" in text,
                             not first, slug)
            self.assertEqual(text.count("| yes |"),
                             sum(1 for m in buying if self.is_open(slug, m)), slug)
        self.assertEqual(self.OPENS["sest-red-line"], "RL01")

    def test_red_lines_last_window_says_its_aircraft_will_not_fly(self):
        # The whole roster at The Quiet Side sells the Y-9, KJ-500, J-15 and
        # J-15D, and nothing after it tasks an aircraft but the ship's flight
        # there: the owner accepted the version's offer, and the window says
        # what it means. Every other open window in the pack has a row for
        # each aircraft it sells, there or later (checked on the built rows,
        # 21 Oct 2026).
        spec = self.specs["sest-red-line"]
        rl06 = next(m for m in spec["MISSIONS"] if self.md.code_of(m) == "RL06")
        self.assertEqual([self.md.code_of(m) for m in spec["MISSIONS"]
                          if self.md._when(m) > self.md._when(rl06)], [])
        self.assertEqual({r.split("|")[1] for r in rl06["window"]["flights"]}, {"Ship's Flight"})
        fixed = [e["unit"] for e in spec["ROSTER"] if bp.unit_type(e["unit"]) == "Aircraft"]
        self.assertEqual(sorted(fixed), ["plaaf_kj-500", "plan_j-15", "plan_j-15d", "plan_y-9fq"])
        self.assertLessEqual(set(fixed), set(rl06["window"]["allow"]))
        situation = self.built("sest-red-line")["RL06"]
        self.assertIn("no operation follows this one: a fixed-wing aircraft allocated here "
                      "will not fly.", self.key(situation, "TaskForceModeBuilderSituation_en"))

    def test_the_twins_offer_is_sold_from_the_opening(self):
        # The twins sold, at every window, the campaign's own roster and the
        # fleet its commander calls on, every priced variant. Derived here
        # from those two lists, that offer holds every unit and variant the
        # twins' built rosters sold at 9035f291 (304 Southern Watch, 261
        # Southern Reach and 23 Red Line pairs, checked 21 Oct 2026) and
        # more - the aircraft usable_allied dropped, the escort hulls the 20
        # Oct reserve had taken off. Each pair is on sale at every window
        # from the opening, or its class is in the coverage report's record
        # of what is not sold, with the reason, or the hull is one a mission
        # places.
        placed = {(u["type"], u.get("variant", "Variant1"))
                  for spec in self.specs.values() for m in spec["MISSIONS"]
                  if m["group"] != "dispatch" for u in m["units"]}
        for slug in self.OPENS:
            spec, built = self.specs[slug], self.built(slug)
            nation = re.search(r"^CommanderNations=(.+)$", spec["COMMANDER"],
                               re.M).group(1).strip()
            own = [e for e in spec["ROSTER"] if e["unit"] not in spec["RESERVE_OPENS"]]
            fleet = self.af.FOR_NATION[nation]
            left = AlliedReserve.not_sold(self, slug)
            offers = [self.offer(self.key(built[self.md.code_of(m)],
                                          "TaskForceModeAllowedRosterUnits"))
                      for m in spec["MISSIONS"] if self.is_open(slug, m)]
            self.assertTrue(offers, slug)
            self.assertEqual(len({frozenset(o) for o in offers}), 1, slug)
            counts = collections.Counter()
            for e in own + fleet:
                for pick in e["picks"]:
                    if (e["unit"], pick) in offers[0]:
                        counts["sold"] += 1
                    elif e["unit"] in left:
                        self.assertTrue(left[e["unit"]].startswith(
                            (AlliedReserve.PLACED,) + AlliedReserve.AIR_REASONS),
                            (slug, e["unit"]))
                        counts["class left out"] += 1
                    else:
                        self.assertIn((e["unit"], pick), placed, (slug, e["unit"], pick))
                        counts["hull placed"] += 1
            self.assertGreater(counts["sold"], 0, slug)
            # The campaign's own roster is sold whole, every variant.
            self.assertLessEqual({(e["unit"], p) for e in own for p in e["picks"]}, offers[0],
                                 slug)

    def test_sulu_line_sells_every_unit_at_some_window(self):
        # No reserve and no opening: its twin's only difference was its own
        # roster from the first window, and the story sells all of it, every
        # variant, at Service at Sea and The Aborlan Battery.
        spec, built = self.specs["sest-sulu-line"], self.built("sest-sulu-line")
        on_sale = set()
        for sec in built.values():
            line = self.key(sec, "TaskForceModeAllowedRosterUnits")
            if line:
                on_sale |= self.offer(line)
            self.assertNotIn(self.LEAD, self.key(sec, "TaskForceModeBuilderSituation_en") or "")
        self.assertEqual({(e["unit"], p) for e in spec["ROSTER"] for p in e["picks"]}, on_sale)
        self.assertNotIn("RESERVE_OPENS", spec)


class SuluOpenAllocation(unittest.TestCase):
    """Sulu Line's Open Allocation twin, built: its supply ships only where
    the story sells them, and no allied-fleet sentence (20 Oct 2026). Built
    into a temporary folder from the shipped campaign (built_twin), as no
    twin ships since 21 Oct 2026."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.built = built_twin("sest-sulu-line", cls.tmp) is not None

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        if not self.built:
            self.skipTest("pack not built")

    def sections(self, slug):
        text = (self.tmp / "campaigns" / slug / "campaign.ini").read_text(encoding="utf-8")
        return {s.split("\n", 1)[0].split("]")[0] + "]": s for s in re.split(r"\n(?=\[)", text)}

    @staticmethod
    def sold(sec):
        allow = re.search(r"^TaskForceModeAllowedRosterUnits=(.*)$", sec, re.M)
        return {e.split(",")[0] for e in allow.group(1).split("|")} if allow else None

    def test_supply_ships_are_sold_only_where_the_story_sells_them(self):
        spec = next(s for s in bp.campaign_specs() if s["SLUG"] == "sest-sulu-line")
        hold = set(spec["OPEN_HOLD"])
        self.assertEqual(hold, {"phl_lpd_tarlac", "tha_aor_chula", "civ_ms_c8"})
        base, twin = self.sections("sest-sulu-line"), self.sections("sest-sulu-line-open")
        windows = 0
        for head, sec in base.items():
            if self.sold(sec) is None:
                continue
            windows += 1
            self.assertEqual(self.sold(twin[head]) & hold, self.sold(sec) & hold, head)
        self.assertEqual(windows, 4)
        # The two shipped leaks: the C8 at The Island Road, every supply ship
        # at Fire Mission Jolo.
        self.assertNotIn("civ_ms_c8", self.sold(twin["[Mission2]"]))
        self.assertEqual(self.sold(twin["[Mission5]"]) & hold, set())
        self.assertIn(bp.OPEN_NOTE_HELD, twin["[Mission5]"])

    def test_the_description_names_no_allied_fleet(self):
        description = re.search(r"^Description=(.*)$", self.sections("sest-sulu-line-open")
                                ["[Language_en]"], re.M).group(1)
        self.assertTrue(description.startswith(bp.OPEN_BLURB_HELD))
        self.assertNotIn("allied fleet", description)


class ServiceAtSea(unittest.TestCase):
    """Sulu Line's charter (owner's decision Q8, 20 Oct 2026): her loss is a
    failed objective, not the end of the mission, so a won Service at Sea
    can leave The Aborlan Battery without her; the rearm is the transfer
    alongside, and no variable is set for one."""

    def setUp(self):
        sl = next(s for s in bp.campaign_specs() if s["SLUG"] == "sest-sulu-line")
        self.missions = {m["code"]: m for m in sl["MISSIONS"]}

    def test_the_charter_is_scored_not_fatal(self):
        m = self.missions["SL04"]
        self.assertFalse([f for f in m.get("fatal", []) if f["objective"] == "Charter"])
        self.assertEqual(m["resolve"]["Charter"], ("protect", "charter#1"))
        self.assertEqual(m["victory"]["station"], "screen#1")
        self.assertNotIn("sets", m["victory"]["after"])
        self.assertEqual(m["declares"], ["SL04SupplierLost"])
        reader = self.missions["SL06"]
        self.assertIn(("SL04SupplierLost", "IsFalse"),
                      [u.get("spawn_if") for u in reader["units"]])

    def test_the_okean_says_what_loses_it(self):
        m = self.missions["SL03A"]
        self.assertFalse(m.get("fatal"))
        self.assertIn("lost both its ships", m["lose"])


class SouthernWatchReveals(unittest.TestCase):
    """The Quiet Passenger reads both of its side operations: Paper Trail's
    datum on the passenger and Southern Cross's on the submarine. From 18 to
    20 Oct 2026 the second was assigned over the first."""

    def test_both_reveals_are_in_the_mission(self):
        sw = bp.campaign_specs()[0]
        m = next(m for m in sw["MISSIONS"] if m["num"] == "04" and m["group"] == "core")
        self.assertEqual([r["variable"] for r in m["reveal_if"]],
                         ["O5ReceiverNamed", "O2KiwiPicture"])

    def test_both_reveals_are_built(self):
        ini = (bp.ROOT / "integration" / "campaign" / "SEST_Campaign" / "campaigns" /
               "sest-southern-watch" / "missions" / "Southern Watch 04 - The Quiet Passenger.ini")
        if not ini.is_file():
            self.skipTest("pack not built")
        text = ini.read_text(encoding="utf-8")
        for var in ("O5ReceiverNamed", "O2KiwiPicture"):
            self.assertIn(f"#Reveal from {var}\n", text)
            self.assertIn(f"Condition_Condition1_Variable={var}\n", text)


class CampaignVariables(unittest.TestCase):
    """Pack-wide: every campaign variable a mission reads is declared by one
    that writes it, and every one declared is read. Sulu Line declared
    SL04ServiceHeld and nothing read it; Southern Watch wrote O5ReceiverNamed
    for The Quiet Passenger, which had stopped reading it."""

    @staticmethod
    def audit(spec):
        """(declared, written, read) - the variable names in the spec."""
        declared, written, read = set(), set(), set()
        for m in spec["MISSIONS"]:
            declared |= set(m.get("declares", []))
            victory = m.get("victory", {})
            for stage in (victory, victory.get("after") or {}):
                if stage.get("sets"):
                    written.add(stage["sets"])
            written |= {loss["sets"] for loss in m.get("support_loss", []) if loss.get("sets")}
            written |= {flag["name"] for flag in m.get("flags", [])}
            written |= {how[3] for how in m.get("resolve", {}).values()
                        if isinstance(how, tuple) and how[0] == "classify"
                        and len(how) > 3 and how[3]}
            read |= {r["variable"] for r in m.get("reveal_if", [])}
            read |= {u["spawn_if"][0] for u in m["units"] if u.get("spawn_if")}
            if m.get("window", {}).get("rearm_if"):
                read.add(m["window"]["rearm_if"][0])
        return declared, written, read

    def test_every_variable_read_is_declared_and_every_declared_variable_is_read(self):
        for spec in bp.campaign_specs():
            declared, written, read = self.audit(spec)
            self.assertEqual(sorted(read - declared), [], f"{spec['SLUG']}: read, never declared")
            self.assertEqual(sorted(declared - read), [], f"{spec['SLUG']}: declared, never read")
            self.assertEqual(written, declared, spec["SLUG"])

    def test_the_built_campaigns_agree(self):
        # The same rule on the built bytes, every key that reads or writes
        # one: SpawnByVariableAND, a VariableCheck condition and the window's
        # TaskForceModeRearmByVariableAND read; [CampaignVariables] declares;
        # Action_VariableSet writes.
        pack = bp.ROOT / "integration" / "campaign" / "SEST_Campaign" / "campaigns"
        if not pack.is_dir():
            self.skipTest("pack not built")
        checked = 0
        for spec in bp.campaign_specs():
            camp = pack / spec["SLUG"]
            declared, written, read = set(), set(), set()
            spine = (camp / "campaign.ini").read_text(encoding="utf-8")
            read |= set(re.findall(r"^TaskForceModeRearmByVariableAND=([^,\n]+),", spine, re.M))
            for ini in camp.glob("missions/*.ini"):
                text = ini.read_text(encoding="utf-8")
                block = re.search(r"^\[CampaignVariables\]\n(.*?)(?:\n\n|\Z)", text, re.M | re.S)
                if block:
                    declared |= set(re.findall(r"^([^=\n]+)=False$", block.group(1), re.M))
                written |= set(re.findall(r"^Action_VariableSet=([^,\n]+),True$", text, re.M))
                read |= set(re.findall(r"^SpawnByVariableAND=([^,\n]+),", text, re.M))
                read |= set(re.findall(r"^Condition_Condition\d+_Variable=(\S+)$", text, re.M))
            self.assertEqual(sorted(read - declared), [], spec["SLUG"])
            self.assertEqual(sorted(declared - read), [], spec["SLUG"])
            self.assertEqual(written, declared, spec["SLUG"])
            checked += len(declared)
        self.assertGreater(checked, 30)


class RedSidePresentation(unittest.TestCase):
    """What a briefing and the Situation window give away (20 Oct 2026).
    recognise=False keeps a unit's photograph out of the briefing and
    orbat=False keeps it out of the Situation window; a red class every
    hull of which a `spare` resolver names is labelled as protected."""

    PACK = bp.ROOT / "integration" / "campaign" / "SEST_Campaign" / "campaigns"

    def test_recognise_false_leaves_the_photo_out(self):
        cat = bp.gallery_catalogue()
        if not cat:
            self.skipTest("no gallery source in this checkout")
        a, b = sorted(cat)[:2]
        picked = bp.recognition({"units": [
            {"side": "red", "type": a, "recognise": False},
            {"side": "red", "type": b}]})
        self.assertEqual([p[1]["unit_id"].lower() for p in picked], [b])

    def test_a_class_is_protected_only_when_every_hull_of_it_is_spared(self):
        mission = {"units": [
            U("red", "m", "usn_p8", "patrol"),
            U("red", "m", "plan_type_054a_p5", "group"),
            U("red", "m", "plan_type_054a_p5", "group"),
            U("red", "m", "plan_type_056a", "group"),
            U("neutral", "m", "civ_ms_roro_b", "ferry")],
            "resolve": {"Restraint": ("spare", "patrol", "group#2", "ferry"),
                        "Corvette": ("spare", "group#3")}}
        self.assertEqual(bp.protected_classes(mission),
                         {"usn_p8": "Protected - do not engage",
                          "plan_type_056a": "Protected - do not engage"})
        entry = {"unit_id": "usn_p8", "label": "P-8A Poseidon", "mapping_status": "exact"}
        asset = {"label": "P-8A", "asset_id": "p8a"}
        saved = bp.photo_credit
        bp.photo_credit = lambda asset: "Photo: test"
        try:
            xml = bp.recognition_xml([("s", entry, asset, "red")],
                                     {"usn_p8": "Protected - do not engage"})
            self.assertIn("Protected - do not engage. Photo: test", xml)
            self.assertNotIn("Expected opposition", xml)
            self.assertIn("Expected opposition", bp.recognition_xml([("s", entry, asset, "red")]))
        finally:
            bp.photo_credit = saved

    def test_a_lifted_restraint_is_do_not_fire_first(self):
        # TS11A's shape: Restraint lifts on the frigate's fire-control lock,
        # after which the mission clears the player to engage her and her
        # helicopter, so "do not engage" under their photos was false. A hull
        # an unlifted restraint also names stays protected, and a class
        # whose hulls are under different rules keeps the plain label.
        mission = {"units": [
            U("red", "m", "plan_type_054a_p5", "frigate"),
            U("red", "m", "plan_z-9c", "helo"),
            U("red", "m", "usn_p8", "patrol"),
            U("red", "m", "plan_type_056a", "group"),
            U("red", "m", "plan_type_056a", "group")],
            "resolve": {"Restraint": ("spare", "frigate", "helo", "patrol", "group#1"),
                        "Umpire": ("spare", "patrol", "group#2")},
            "lift": [dict(objective="Restraint", units=["frigate"])]}
        self.assertEqual(bp.protected_classes(mission),
                         {"plan_type_054a_p5": "Opposition - do not fire first",
                          "plan_z-9c": "Opposition - do not fire first",
                          "usn_p8": "Protected - do not engage"})

    def test_twelve_mile_line_says_do_not_fire_first(self):
        brief = (self.PACK / "sest-southern-reach" / "missions" /
                 "Tasman Shield 11A - The Twelve-Mile Line_briefing" / "BriefingText_en.xml")
        if not brief.is_file():
            self.skipTest("pack not built")
        text = brief.read_text(encoding="utf-8")
        # the 054A and the Z-9C; the corvette is under the player's protection, blue
        self.assertEqual(text.count("Protected - do not engage"), 0)
        self.assertEqual(text.count("Opposition - do not fire first. "), 2)

    def test_an_unlisted_unit_is_not_in_the_order_of_battle(self):
        missions = [dict(key="m", group="core", red_nation="Australia",
                         _unlisted={"Taskforce2Submarine1"})]
        placed = {"Taskforce2Submarine": [
            ("Taskforce2Submarine1", {"Type": "ran_ssg_collins", "VariantReference": "Variant3"},
             None, False)],
            "Taskforce2Aircraft": [
            ("Taskforce2Aircraft1", {"Type": "usn_p8", "SquadronReference": "Squadron3"},
             None, False)]}
        text = bp.enemy_roster_ini(missions, {"m": placed})
        self.assertNotIn("ran_ssg_collins", text)
        self.assertIn("usn_p8=Squadron3,1", text)

    def test_red_lines_boats_are_puzzles_in_the_built_campaign(self):
        rl = self.PACK / "sest-red-line"
        if not (rl / "enemy_theater_roster.ini").is_file():
            self.skipTest("pack not built")
        roster = (rl / "enemy_theater_roster.ini").read_text(encoding="utf-8")
        self.assertNotIn("SubmarinesPersistent_USN", roster)
        self.assertNotIn("ran_ssg_collins", roster)
        brief = (rl / "missions" / "Red Line 02 - Routes They Can See_briefing" /
                 "BriefingText_en.xml").read_text(encoding="utf-8")
        self.assertNotIn("Virginia", brief)
        self.assertIn("Protected - do not engage", brief)
        brief = (rl / "missions" / "Red Line 01 - Trailing Contact_briefing" /
                 "BriefingText_en.xml").read_text(encoding="utf-8")
        self.assertNotIn("Collins", brief)
        # ALPHA is the one Collins hull no other mission places.
        rl01 = (rl / "missions" / "Red Line 01 - Trailing Contact.ini").read_text(encoding="utf-8")
        self.assertIn("Type=ran_ssg_collins\nVariantReference=Variant3\n", rl01)

    def test_red_lines_civilians_fly_no_russian_flag(self):
        rl = self.PACK / "sest-red-line" / "missions"
        if not rl.is_dir():
            self.skipTest("pack not built")
        for ini in sorted(rl.glob("*.ini")):
            for block in re.split(r"\n(?=\[)", ini.read_text(encoding="utf-8")):
                if block.startswith("[Neutral"):
                    self.assertNotIn("\nNation=Russia", block, ini.name)

    def test_red_lines_reports_name_no_one(self):
        import mission_depth
        # Every Red Line report, the side operations' with the rest.
        codes = sorted(c for c in mission_depth.REPORTS if c.startswith("RL"))
        self.assertEqual(len(codes), 9)
        for code in codes:
            speaker = mission_depth.REPORTS[code].split(":", 1)[0]
            for name in ("LI", "CHEN"):
                self.assertNotIn(name, speaker.split(), code)
        self.assertNotIn("ceasefire", mission_depth.REPORTS["RL02"])
        self.assertNotIn("snorkel", mission_depth.REPORTS["RL05"])
        for code in ("SL01", "SL05", "SL07"):
            self.assertTrue(mission_depth.REPORTS[code].startswith("MANALO:"), code)


class RedLineSideOperations(unittest.TestCase):
    """Red Line's step RL-1 (campaign-upgrade-plan.md section 4.2, 20 Oct
    2026): two optionals flown by the enclave field's own aircraft and a
    contingency for the screen's detachment - Datum read by the next core
    mission, The Ships from the North's read held (21 Oct 2026), the
    contingency a race of its own - on days neither coalition campaign
    flies, with no hull a coalition mission can own or lose first."""

    PACK = bp.ROOT / "integration" / "campaign" / "SEST_Campaign" / "campaigns"

    def setUp(self):
        self.specs = bp.campaign_specs()
        self.rl = next(s for s in self.specs if s["SLUG"] == "sest-red-line")
        self.missions = {m["code"]: m for m in self.rl["MISSIONS"]}

    def test_the_shape(self):
        groups = collections.Counter(m["group"] for m in self.rl["MISSIONS"])
        self.assertEqual(groups, {"core": 6, "optional": 2, "contingency": 1})
        self.assertEqual(len(self.rl["EVENTS"]), 8)
        for code, closer in (("RLO1", "Routes They Can See"),
                             ("RLO2", "The Other Picture"),
                             ("RLC1", "The Order to Withdraw")):
            self.assertEqual(self.missions[code]["expires_after"], closer, code)
        # The optionals are somebody else's aircraft: nothing the player
        # owns sails and no window opens. The contingency is a detachment.
        for code in ("RLO1", "RLO2"):
            self.assertIsNone(self.missions[code]["generation"], code)
            self.assertEqual(self.missions[code]["window"], {}, code)
        self.assertEqual(self.missions["RLC1"]["generation"], "Generated")
        self.assertTrue(self.missions["RLC1"]["window"]["detachment"])
        self.assertFalse(self.missions["RLC1"]["window"].get("rearm"))

    def test_datum_is_read_and_the_ships_from_the_north_is_held(self):
        datum, names = self.missions["RLO1"], self.missions["RLO2"]
        self.assertEqual(datum["victory"]["after"]["sets"], "RLO1GolfDatum")
        # A datum on GOLF for fifteen minutes, as Southern Watch's O2 gives
        # SW04: classifying her is still RL02's own objective.
        golf = self.missions["RL02"]["reveal_if"]
        self.assertEqual([(r["variable"], r["units"], r["level"], r["time"]) for r in golf],
                         [("RLO1GolfDatum", ["red_sub"], "", 900)])
        self.assertIn(("classify", "red_sub", 1), self.missions["RL02"]["resolve"].values())
        # Held (owner, 21 Oct 2026): O2 names both escorts and writes
        # nothing, and RL03 reads nothing, until the Red Line test card's
        # 7.4 shows a reveal at Classify satisfying a UnitClassified stage.
        # RL03 started with both escorts classified (RLO2EscortsNamed) until
        # then; the reveal is restorable from commit 9035f291.
        self.assertEqual(names["victory"]["after"]["units"], ["jmsdf#1", "jmsdf#2"])
        self.assertNotIn("sets", names["victory"]["after"])
        self.assertNotIn("sets", names["victory"])
        self.assertEqual(names["declares"], [])
        self.assertNotIn("reveal_if", self.missions["RL03"])

    def test_red_line_flies_no_day_the_coalition_campaigns_fly(self):
        # Correction X3: no day Southern Watch or Southern Reach flies,
        # optionals and dispatches included. Sulu Line may share a day.
        flown = {m["date"]: f"{s['TITLE']} {m['key']}" for s in self.specs
                 if s["SLUG"] in ("sest-southern-watch", "sest-southern-reach")
                 for m in s["MISSIONS"]}
        for m in self.rl["MISSIONS"]:
            self.assertNotIn(m["date"], flown, f"{m['code']} shares {m['date']} with "
                             f"{flown.get(m['date'])}")

    def test_no_hull_a_coalition_mission_can_own_or_lose_first(self):
        # The bible's rule as corrected on 20 Oct 2026: a coalition warship
        # Red Line places is no hull another standard campaign sells (its
        # roster, the allied reserve included) or places on the player's
        # side before her last Red Line appearance. GOLF was Variant1 until
        # then, the hull Fujian's Shadow can lose on the 23rd.
        last = {}
        for m in self.rl["MISSIONS"]:
            for u in m["units"]:
                if u["side"] == "red" and bp.unit_type(u["type"]) in ("Vessel", "Submarine") \
                        and bp.is_combat(u["type"]):
                    key = (u["type"], u.get("variant", "Variant1"))
                    last[key] = max(last.get(key, m["date"]), m["date"])
        self.assertIn(("ran_opv_arafura", "Variant4"), last)
        self.assertEqual(last[("usn_ssn_virginia_2027", "Variant10")], (2028, 11, 27))
        for spec in self.specs:
            if spec is self.rl:
                continue
            for e in spec["ROSTER"]:
                for pick in e.get("picks", []):
                    self.assertNotIn((e["unit"], pick), last, f"{spec['TITLE']} sells it")
            for m in spec["MISSIONS"]:
                if m["group"] == "dispatch":
                    continue
                for u in m["units"]:
                    key = (u["type"], u.get("variant", "Variant1"))
                    if u["side"] == "blue" and key in last:
                        self.assertGreater(m["date"], last[key],
                                           f"{spec['TITLE']} {m['key']} places {key}")
        # The Open Allocation twins sold the whole allied fleet unfiltered,
        # JS Maya Variant1 - Red Line's - among it, until 21 Oct 2026. The
        # standard campaigns sell that fleet now through the reserve, whose
        # named-hull filter is pack-wide, so the rosters above are the whole
        # check; what a twin would still add is pinned empty.
        self.assertIn(("jmsdf_ddg_maya", "Variant1"), last)
        on_twins = sorted({(e["unit"], pick) for spec in self.specs
                           if spec is not self.rl
                           for e in spec.get("ALLIED_FLEET", []) for pick in e["picks"]
                           if (e["unit"], pick) in last})
        self.assertEqual(on_twins, [])

    def test_golf_is_one_boat(self):
        golf = {(code, u.get("variant")) for code, m in self.missions.items()
                for u in m["units"] if u.get("name") == "Contact GOLF"}
        self.assertEqual(sorted(golf), [("RL02", "Variant10"), ("RL04", "Variant10"),
                                        ("RLO1", "Variant10")])
        # Spared in Datum: sunk there, she could not be in RL02 or RL04.
        self.assertIn("red_sub", self.missions["RLO1"]["fatal"][0]["units"])

    def test_the_pilot_race(self):
        m = self.missions["RLC1"]
        v, stage = m["victory"], m["victory"]["after"]
        pilot = m["stations"]["pilot"]["at"]
        # The held stage needs its pop-up (the builder refuses one without);
        # the win's box is round the raft and wider than the stage's, so the
        # pilot aboard is the win and the patrol vessel arriving after it
        # changes nothing.
        self.assertEqual((stage["kind"], stage["at_unit"]), ("area", "pilot"))
        self.assertTrue(stage["hold_minutes"] and stage["held"])
        self.assertEqual(v["at"], pilot)
        self.assertGreater(v["radius"], stage["radius"])
        self.assertEqual([(d["units"], d["at"]) for d in m["denied"]], [(["opv"], pilot)])
        # The hold needs the ship stopped: crossing the stage's circle
        # through its centre takes the four minutes only at ten knots or
        # less. The first build's mile let an 054A at 30 knots win without
        # slowing (review of 20 Oct 2026).
        self.assertLessEqual(2 * stage["radius"] / (stage["hold_minutes"] / 60.0), 10)
        # And it is a race: the patrol vessel (20 knots at telegraph 4) is
        # at the mile after an 054A at 27 knots has the pilot aboard from
        # the authored start, and before a ship at the builder's 18 has.
        start = bp.nm_between(m["stations"]["frigate"]["at"], pilot) - stage["radius"]
        hers = (bp.nm_between(m["stations"]["opv"]["at"], pilot) - m["denied"][0]["radius"]) / 20
        self.assertLess(start / 27 + stage["hold_minutes"] / 60.0, hers)
        self.assertGreater(start / 18 + stage["hold_minutes"] / 60.0, hers)
        opv = next(u for u in m["units"] if u["station"] == "opv")
        self.assertEqual((opv["type"], opv["variant"], opv["weapons"]),
                         ("ran_opv_arafura", "Variant4", "Hold"))
        self.assertEqual(m["fatal"][0]["units"], ["opv", "red_air"])

    def test_the_pages_are_from_this_side(self):
        for e in self.rl["EVENTS"]:
            form = e.get("form", "press")
            self.assertIn(form, ("signal", "log", "intsum"), e["file"])
            if form in ("signal", "log") and e.get("note"):
                # Never the coalition analyst's or a merchant master's box.
                self.assertIn(e.get("note_label"), ("COMMANDER'S NOTE", "FILE NOTE"),
                              e["file"])
            if form == "log":
                self.assertNotEqual(e.get("master_label", "MASTER"), "MASTER", e["file"])
            if form == "intsum":
                self.assertNotIn("COALITION", e["marking"], e["file"])
        befores = [e.get("before") for e in self.rl["EVENTS"][1:-1]]
        for key in ("Datum", "The Ships from the North", "Pilot in the Water"):
            self.assertIn(key, befores)

    def test_the_built_spine(self):
        ini = self.PACK / "sest-red-line" / "campaign.ini"
        if not ini.is_file():
            self.skipTest("pack not built")
        text = ini.read_text(encoding="utf-8")
        self.assertIn("NumberOfMissions=17\n", text)
        self.assertIn("Length=6\n", text)
        index = {name: int(n) for n, name in
                 re.findall(r"^\[Mission(\d+)\]  #RL\w+ (.+)$", text, re.M)}
        for side, closer in (("Datum", "Routes They Can See"),
                             ("The Ships from the North", "The Other Picture"),
                             ("Pilot in the Water", "The Order to Withdraw")):
            section = re.search(rf"^\[Mission{index[side]}\].*?(?=^\[Mission|\Z)", text,
                                re.M | re.S).group(0)
            self.assertIn(f"ExpiresAfterMissionComplete={index[closer]}\n", section, side)


class RevealBeforeClassify(unittest.TestCase):
    """A campaign variable's reveal at Classify or Identify must not land on
    a unit a classify stage of the reading mission names (21 Oct 2026).
    Nothing has shown that the reveal counts for that stage's
    UnitClassified, and if it does not, the unit is classified already and
    can never be classified again: the mission cannot be won by a player who
    won the one before. RL03's reveal on RLO2EscortsNamed had that shape and
    is held (Red Line test card 7.4)."""

    # The in-pack proof of the shape, on optional objectives only, so
    # neither mission becomes unwinnable if the answer is no: TS03's Tender
    # after TS01 (Southern Reach test card 3.10) and SL03A's Identify after
    # Night Market (Sulu Line test card 7.1). Their answer decides whether
    # RL03's reveal comes back. Any other overlap is a decision, made here.
    PROOF = {("TS03", "tender"): "Southern Reach test card 3.10",
             ("SL03A", "okean"): "Sulu Line test card 7.1"}

    @staticmethod
    def refs(units):
        """A unit reference or a list of them, as (station, index) pairs:
        index "" is every unit at the station, as build_pack.refs() reads it."""
        return {tuple(u.partition("#")[::2])
                for u in ([units] if isinstance(units, str) else units)}

    @staticmethod
    def same_unit(a, b):
        return a[0] == b[0] and (not a[1] or not b[1] or a[1] == b[1])

    def test_no_classify_level_reveal_lands_on_a_classify_target(self):
        seen = set()
        for spec in bp.campaign_specs():
            for m in spec["MISSIONS"]:
                code = bp.mission_code(m)
                victory = m.get("victory", {})
                staged = set()
                for stage in (victory, victory.get("after") or {}):
                    if stage.get("kind") == "classify":
                        staged |= self.refs(stage["units"])
                optional = set()
                for how in m.get("resolve", {}).values():
                    if isinstance(how, tuple) and how[0] == "classify":
                        optional |= self.refs(how[1])
                for r in m.get("reveal_if", []):
                    # The builder's default level is Identify; "" is the bare
                    # datum, which reveals a contact and no class.
                    if r.get("level", "Identify") not in ("Classify", "Identify"):
                        continue
                    for ref in self.refs(r["units"]):
                        where = (f"{spec['TITLE']} {code}: {r['variable']} reveals "
                                 f"{'#'.join(filter(None, ref))}")
                        self.assertFalse([s for s in staged if self.same_unit(ref, s)],
                                         where + ", which a classify stage names")
                        if [o for o in optional if self.same_unit(ref, o)]:
                            self.assertIn((code, ref[0]), self.PROOF,
                                          where + ", which a classify objective names")
                            seen.add((code, ref[0]))
        self.assertEqual(seen, set(self.PROOF))


class OpenAllocationRetired(unittest.TestCase):
    """The owner retired the Open Allocation twins from the pack on 21 Oct
    2026, once the allied reserve put allied escorts in the standard
    campaigns, and the same day put what they sold there too: the allied
    fleet (AlliedReserve) and the whole roster from the same windows
    (OpenAllocationStandard). No campaign opts in (spec OPEN_ALLOCATION),
    no twin folder ships, and the pack's Mod Manager entry no longer offers
    one. The machinery stays for a world-wide campaign: OpenAllocation,
    AlliedFleetReview and SuluOpenAllocation build it."""

    DIST = bp.ROOT / "integration" / "dist" / "SEST_Integration"

    def test_no_campaign_opts_in(self):
        self.assertEqual([s["SLUG"] for s in bp.campaign_specs()
                          if s.get("OPEN_ALLOCATION")], [])

    def test_no_twin_folder_ships(self):
        roots = [r for r in (PACK, self.DIST) if (r / "campaigns").is_dir()]
        if not roots:
            self.skipTest("pack not built")
        for root in roots:
            self.assertEqual(sorted(f.name for f in (root / "campaigns").iterdir()
                                    if f.name.endswith(bp.OPEN_SUFFIX)), [], root.name)

    def test_the_mod_manager_entry_offers_no_twin(self):
        infos = [r / "_info.ini" for r in (PACK, self.DIST) if (r / "_info.ini").is_file()]
        if not infos:
            self.skipTest("pack not built")
        for info in infos:
            self.assertNotIn("Open Allocation", info.read_text(encoding="utf-8"),
                             info.parent.name)

    def test_the_gate_refuses_a_twin_nothing_builds(self):
        # A pack synced over an old one keeps its -open folders, and the
        # game lists each as a campaign; check_campaign_coverage refuses
        # one unless its campaign opts in.
        specs = bp.campaign_specs()
        with tempfile.TemporaryDirectory() as d:
            pack = Path(d)
            for spec in specs:
                (pack / "campaigns" / spec["SLUG"]).mkdir(parents=True)
            self.assertEqual(coverage_check.stray_campaigns(pack, specs), [])
            twin = bp.open_slug(specs[0]["SLUG"])
            (pack / "campaigns" / twin).mkdir()
            (pack / "campaigns" / "sest-elsewhere").mkdir()
            found = coverage_check.stray_campaigns(pack, specs)
            self.assertEqual(len(found), 2, found)
            self.assertIn(f"campaigns/{twin}: no campaign builds it - an Open Allocation "
                          "twin, and its campaign does not opt in to one", " ".join(found))
            opted = [dict(s, OPEN_ALLOCATION=True) if s is specs[0] else s for s in specs]
            self.assertEqual(coverage_check.stray_campaigns(pack, opted),
                             ["campaigns/sest-elsewhere: no campaign builds it"])


class RulesPage(unittest.TestCase):
    """The Campaign Rules button opens campaign_rules_en.xml; each campaign's
    page is the stock one with its own passages and thresholds in place."""

    def test_each_page_parses_and_carries_only_its_own_campaign(self):
        import xml.dom.minidom
        for spec in bp.campaign_specs():
            page = bp.campaign_rules(spec)
            xml.dom.minidom.parseString(page.encode("utf-8"))
            self.assertIn(f'Text="{bp._xml_text(spec["TITLE"])} - Task Force Mode"', page)
            for stock in ("Pacific Strike", "Japanese units, for example", "optional side missions",
                          "include their airwing for free"):
                self.assertNotIn(stock, page, f"{spec['SLUG']}: {stock}")

    def test_the_story_page_says_when_the_reserve_is_on_sale(self):
        # Story mode only: the availability line says what is on sale when,
        # and the line after it the catalogue, the prices and the named
        # hulls. Until 21 Oct 2026 the line named the escorts and said no
        # allied aircraft, carrier, amphibious ship or tanker was sold; step
        # 1 of that day said every force allocation from the opening "also
        # sells" the fleet, and step 2 says the opening offers the whole
        # roster with it, the windows before it what the story releases.
        leads = {"sest-southern-watch": "- Force allocations before Weapons Free offer what "
                                        "the story releases. From the force allocation before "
                                        "Weapons Free, every force allocation offers the whole "
                                        "roster and the allied fleet - ",
                 "sest-southern-reach": "- Force allocations before Tasman Crossing offer what "
                                        "the story releases. From the force allocation before "
                                        "Tasman Crossing, every force allocation offers the "
                                        "whole roster and the allied fleet - ",
                 "sest-red-line": "- Every force allocation offers the whole roster and the "
                                  "People's Liberation Army Navy's Type 901 Fuyu fast combat "
                                  "support ship and Type 903A Fuchi replenishment oiler. Some "
                                  "operations still limit what sails."}
        story = ("- Unit availability changes between missions: Task Force Builder offers only "
                 "what the current force-allocation window allows.")
        for spec in bp.campaign_specs():
            page = bp.campaign_rules(spec)
            twin = bp.campaign_rules(spec, open_allocation=True)
            for text in (page, twin):
                self.assertNotIn("No allied aircraft, carrier", text, spec["SLUG"])
                self.assertNotIn(" also sells ", text, spec["SLUG"])
            if spec["SLUG"] not in leads:
                self.assertIn(story, page, spec["SLUG"])
                self.assertNotIn("whole roster", page, spec["SLUG"])
                continue
            self.assertNotIn(story, page, spec["SLUG"])
            self.assertEqual(page.count(leads[spec["SLUG"]]), 1, spec["SLUG"])
            line = page[page.index(leads[spec["SLUG"]]):].split('"', 1)[0]
            after = page[page.index(line) + len(line):].split('Text="', 1)[1].split('"', 1)[0]
            self.assertTrue(line.endswith(" Some operations still limit what sails."), line)
            if spec["SLUG"] == "sest-red-line":
                # The PLAN's own supply ships: never called allied, and the
                # first window is where everything opens.
                self.assertEqual(after, "- No hull a mission names is sold.")
                for text in (line, after):
                    self.assertNotIn("llied", text)
                    self.assertNotIn("story releases", text)
                continue
            for said in ("Carriers and amphibious ships come without aircraft, as every ship "
                         "bought here does.",
                         "An allied aircraft is sold only where some mission here can launch "
                         "and recover it.",
                         "- and the Royal Australian Navy's Canberra-class LHD."):
                self.assertIn(said, line, spec["SLUG"])
            self.assertEqual(after, "- The Unit Catalog lists all of it from the start. Allied "
                                    "classes cost their own navies' listed prices, without the "
                                    "same-nation discount. No hull a mission names is sold.")
            # The airwing line is every campaign's: no bought ship brings one.
            self.assertIn("Ships purchased in Task Force Builder come without aircraft", page)

    def test_the_fixed_wing_line_follows_the_first_window(self):
        # Red Line's first window offers the whole roster since 21 Oct 2026,
        # its J-15s and Y-9 among it, so the stock "not available at the
        # start" line would be false there; the other three sell no
        # fixed-wing aircraft before their second window.
        stock = "Fixed-wing aircraft are not available for purchase at the start"
        on_sale = "Fixed-wing aircraft are on sale from the first force allocation."
        import mission_depth
        for spec in bp.campaign_specs():
            first = min((m for m in spec["MISSIONS"] if m.get("window", {}).get("buy")),
                        key=mission_depth._when)
            sold = first["window"].get("allow") or [e["unit"] for e in spec["ROSTER"]]
            fixed = [u for u in sold if bp.unit_type(u) in ("Aircraft", "VTOL")]
            page = bp.campaign_rules(spec)
            self.assertEqual((stock in page, on_sale in page), (not fixed, bool(fixed)),
                             spec["SLUG"])
            self.assertEqual(bool(fixed), spec["SLUG"] == "sest-red-line", spec["SLUG"])

    def test_the_built_pages_count_what_the_built_rosters_sell(self):
        # The aircraft are judged in the build, so the counts are the built
        # page's: ships and aircraft as the built roster sells them.
        import mission_depth
        for spec in bp.campaign_specs():
            folder = PACK / "campaigns" / spec["SLUG"]
            if not (folder / "campaign_rules_en.xml").is_file():
                self.skipTest("pack not built")
            page = (folder / "campaign_rules_en.xml").read_text(encoding="utf-8")
            roster = (folder / "player_task_force_roster.ini").read_text(encoding="utf-8")
            sold = re.findall(r"^([^;\[\s=]+)=", roster, re.M)
            reserve = [u for u in sold if u in spec.get("RESERVE_OPENS", {})]
            allied = [u for u in reserve if not u.startswith("ran_")]
            if spec["SLUG"] not in ("sest-southern-watch", "sest-southern-reach"):
                self.assertNotIn("the allied fleet", page, spec["SLUG"])
                continue
            air = sum(1 for u in allied
                      if bp.unit_type(u) in ("Aircraft", "Helicopter", "VTOL"))
            self.assertIn(f"the allied fleet - {len(allied) - air} ship classes and {air} "
                          "aircraft types from the USA, ", page, spec["SLUG"])
            self.assertEqual([mission_depth.code_of(m) for m, _u in
                              mission_depth.reserve_offer(spec)],
                             [{"sest-southern-watch": "SW05",
                               "sest-southern-reach": "TS04"}[spec["SLUG"]]])

    def test_a_held_aircraft_must_be_one(self):
        # The reserve holds an entry priced by squadron for the aircraft
        # judgement; the unit file has the last word.
        spec = copy.deepcopy(next(s for s in bp.campaign_specs()
                                  if s["SLUG"] == "sest-southern-reach"))
        bp.set_campaign(spec)
        spec["RESERVE_AIR"] = spec["RESERVE_AIR"] + [
            dict(unit="rn_ff_type23", picks=["Squadron1"], points=260,
                 note="United Kingdom - Type 23 class (LIFEX)")]
        with self.assertRaisesRegex(SystemExit, r"holds rn_ff_type23 \(Vessel\) as aircraft"):
            bp.admit_reserve_aircraft(spec, spec["MISSIONS"], {})

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


class RecognitionPhotos(unittest.TestCase):
    """The briefing's RECOGNITION photos: own side first, conditional units
    left out, one photo per class, every bound stem written as a PNG."""

    def setUp(self):
        cat = bp.gallery_catalogue()
        if not cat:
            self.skipTest("no gallery source in this checkout")
        self.ids = sorted(cat)[:12]

    def mission(self, units):
        return {"units": units}

    def test_own_side_first_and_spawn_if_left_out(self):
        a, b, c = self.ids[:3]
        picked = bp.recognition(self.mission([
            {"side": "red", "type": a},
            {"side": "blue", "type": b},
            {"side": "red", "type": c, "spawn_if": "x"},
            {"side": "neutral", "type": self.ids[3]}]))
        sides = [p[3] for p in picked]
        self.assertEqual(sides, sorted(sides))           # blue before red
        self.assertNotIn(c, [p[1]["unit_id"].lower() for p in picked])
        self.assertNotIn("neutral", sides)

    def test_capped_and_bound_in_the_page(self):
        units = [{"side": "blue", "type": t} for t in self.ids]
        picked = bp.recognition(self.mission(units))
        self.assertLessEqual(len(picked), bp.REC_MAX)
        self.assertEqual(len({p[2]["asset_id"] for p in picked}), len(picked))
        xml = bp.recognition_xml(picked)
        for stem, *_ in picked:
            self.assertIn(f"Assets[{stem}]", xml)
        self.assertTrue(bp.recognition_png(picked[0][2]["file"]).startswith(b"\x89PNG"))


class MenuBackground(unittest.TestCase):
    """The plugins/ folder: the plugin, its film and the files a player reads,
    and never a second AnchorChain.dll - Anchor Chain loads every DLL it
    finds in a mod folder, and the compile-time stub would be one."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sest-menu-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_folder_holds_the_plugin_film_settings_and_credits(self):
        with contextlib.redirect_stdout(io.StringIO()):
            bp.write_menu_background(self.tmp)
        folder = self.tmp / "plugins"
        self.assertEqual(sorted(f.name for f in folder.iterdir()),
                         ["MENU_CREDITS.txt", "README.txt", "SEST.MenuBackground.dll",
                          "sest_menu.ini", "sest_menu.mp4"])
        self.assertEqual([f.name for f in self.tmp.rglob("*.dll")], ["SEST.MenuBackground.dll"])
        ini = (folder / "sest_menu.ini").read_text(encoding="utf-8")
        self.assertIn("\nEnabled=1\n", ini)
        self.assertIn("\nFilm=sest_menu.mp4\n", ini)
        self.assertEqual((folder / "sest_menu.mp4").read_bytes()[4:8], b"ftyp")

    def test_no_plugin_no_folder(self):
        saved = bp.MENU_BACKGROUND
        bp.MENU_BACKGROUND = self.tmp / "nothing-here"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                bp.write_menu_background(self.tmp)
        finally:
            bp.MENU_BACKGROUND = saved
        self.assertFalse((self.tmp / "plugins").exists())


class LoadingScreens(unittest.TestCase):
    """Every one of the game's 80 loading-screen slots gets a SEST photograph,
    in turn, under the game's own file name."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sest-loading-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_all_slots_filled_in_turn(self):
        with contextlib.redirect_stdout(io.StringIO()):
            bp.write_loading_screens(self.tmp)
        slots = sorted((self.tmp / "ui" / "backgrounds").iterdir(), key=lambda f: int(f.stem.split("_")[-1]))
        self.assertEqual([f.name for f in slots], [f"loading_screen_{n}.png" for n in range(1, 81)])
        photos = sorted(bp.LOADING.glob("sest_loading_*.jpg"))
        self.assertGreater(len(photos), 1)
        self.assertEqual(slots[0].read_bytes(), photos[0].read_bytes())
        self.assertEqual(slots[len(photos)].read_bytes(), photos[0].read_bytes())
        self.assertEqual(slots[0].read_bytes()[:2], b"\xff\xd8")    # JPEG data
        self.assertTrue((self.tmp / "LOADING-SCREEN-CREDITS.txt").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
