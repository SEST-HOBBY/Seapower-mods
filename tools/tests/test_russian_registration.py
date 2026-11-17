#!/usr/bin/env python3
"""The Russian Federation, not the USSR: the readers of SEST's Nation stubs.

SEST Collection Fixes re-registers the post-1991, Russian-built hulls, the
modern refits of Soviet-built ships and the aircraft of post-1991 Russian
types to the game's Russia key with #!extend Nation stubs on their variants
and squadrons files (integration/collection-fixes/build_patch.py:
RU_REREGISTER, RU_BY_SECTION, RU_AIRCRAFT; the stubs themselves are tested in
test_collection_fixes.py). The readers outside the campaign builder have to
read the stub before the winning file, as the game does, through the one
shared helper (integration/common/nation_stubs.py):

  integration/mission-seeds/set_enemy_flags.py   registered()
  integration/world-sandbox/build_dynamic_campaign.py   operators()
  integration/world-sandbox/submarines.py   MAPPINGS' flag column, by hand
  integration/cross-deck/build_pack.py   nation()
  tools/check_campaign_coverage.py   nations(), the flag check

The checks on built files need a build; run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_russian_registration.py' -v
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXES = ROOT / "integration/collection-fixes/SEST_Collection_Fixes"
STUBBED = "rfn_ffg_22350_1-4"
LEFT = "wp_ssbn_delta4"           # every section left Soviet
SPLIT = "wp_ssn_akula"            # the boats launched after 1991 only
JET = "wp_su-35s"                 # an aircraft: Squadron4 is China's
OLD_JET = "wp_su-27"              # a Cold War Flanker, left Soviet

sys.path.insert(0, str(ROOT / "integration"))
from common import nation_stubs  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def built():
    return bool(list((FIXES / "vessels_overwrite").glob("*_variants_RU_SEST.ini")))


class SharedReader(unittest.TestCase):
    """nation_stubs reads what the game's IniHandler.ScanForModifierFiles reads."""

    def test_targets_are_read_before_the_first_section_only(self):
        lines = ["﻿# a comment", "#!extend vessels/a_variants.ini, vessels\\b_variants.ini",
                 "", "[Default]", "#!extend vessels/c_variants.ini"]
        self.assertEqual(nation_stubs.targets(lines),
                         ["vessels/a_variants.ini", "vessels/b_variants.ini"])
        self.assertEqual(nation_stubs.targets(["[General]", "#!extend x.ini"]), [])

    def test_a_section_nation_reads_as_pick_nation_reads_it(self):
        text = ("[Default]\nNation=Russia  // stub\n[Variant1]\nNation=\nName=x\n"
                "[Variant2] ; a comment\nNation=Russia\nNation=Soviet\n")
        self.assertEqual(nation_stubs.section_nations(text),
                         {"Default": "Russia", "Variant2": "Russia"})

    def test_an_aircraft_stub_is_indexed_by_its_squadrons_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "integration/some-pack/SEST_Some_Pack/aircraft_overwrite"
            pack.mkdir(parents=True)
            (pack / "j_squadrons_RU_SEST.ini").write_text(
                "#!extend aircraft/J_squadrons.ini\n\n[Squadron2]\nNation=Russia\n", encoding="utf-8")
            root = Path(tmp)
            self.assertEqual(nation_stubs.nation("aircraft/j_squadrons.ini", "Squadron2", root), "Russia")
            self.assertIsNone(nation_stubs.nation("aircraft/j_squadrons.ini", "Default", root))
            self.assertFalse(nation_stubs.TARGET.match("aircraft/j.ini"))

    def test_an_index_over_a_scratch_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "integration/some-pack/SEST_Some_Pack/vessels_overwrite"
            pack.mkdir(parents=True)
            (pack / "u_variants_RU_SEST.ini").write_text(
                "#!extend vessels/U_variants.ini\n# why\n\n[Default]\nNation=Russia\n\n"
                "[Variant1]\nNation=Russia\n", encoding="utf-8")
            (pack / "u_CombatSystems_SEST.ini").write_text(
                "#!extend vessels/u.ini\n[CombatSystems]\nNumberOfCombatSystems=1\n",
                encoding="utf-8")
            dist = Path(tmp) / "integration/dist/SEST_Integration/vessels_overwrite"
            dist.mkdir(parents=True)
            (dist / "v_variants_RU_SEST.ini").write_text(
                "#!extend vessels/v_variants.ini\n[Default]\nNation=Russia\n", encoding="utf-8")
            root = Path(tmp)
            self.assertEqual(nation_stubs.index(root),
                             {"vessels/u_variants.ini": {"Default": "Russia", "Variant1": "Russia"}})
            self.assertEqual(nation_stubs.nation("vessels/u_variants.ini", "Variant1", root), "Russia")
            self.assertIsNone(nation_stubs.nation("vessels/u_variants.ini", "Variant2", root))
            self.assertEqual(nation_stubs.sections("vessels/v_variants.ini", root), {})


@unittest.skipUnless(built(), "SEST Collection Fixes not built")
class MissionSeeds(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sef = load("set_enemy_flags_under_test", ROOT / "integration/mission-seeds/set_enemy_flags.py")
        cls.idx = cls.sef.index()

    def test_registered_reads_the_stub_first(self):
        winner = self.idx[f"vessels/{STUBBED}_variants.ini"]
        self.assertIn("Nation=Soviet", winner.read_text(encoding="utf-8-sig"))
        self.assertEqual(self.sef.registered(self.idx, STUBBED, "Variant1"), "Russia")
        self.assertEqual(self.sef.registered(self.idx, STUBBED, "Default"), "Russia")
        self.assertEqual(self.sef.registered(self.idx, LEFT, "Variant1"), "Soviet")
        self.assertEqual(self.sef.registered(self.idx, SPLIT, "Variant1"), "Soviet")
        self.assertEqual(self.sef.registered(self.idx, SPLIT, "Variant13"), "Russia")

    def test_registered_reads_an_aircraft_stub_first(self):
        winner = self.idx[f"aircraft/{JET}_squadrons.ini"]
        self.assertIn("Nation=Soviet", winner.read_text(encoding="utf-8-sig"))
        self.assertEqual(self.sef.registered(self.idx, JET, "Squadron1"), "Russia")
        self.assertEqual(self.sef.registered(self.idx, JET, "Squadron4"), "China")
        self.assertEqual(self.sef.registered(self.idx, OLD_JET, "Squadron1"), "Soviet")

    def test_a_seed_unit_still_gets_its_russian_flag(self):
        # R0: with the identity entry the pass writes Nation=Russia on a
        # stubbed hull exactly as it did when the file said Soviet.
        for uid in (STUBBED, LEFT, SPLIT):
            text = f"[Taskforce2Vessel1]\nType={uid}\nVariantReference=Variant1\nName=x\n"
            new, changes = self.sef.rewrite(text, self.idx)
            self.assertEqual(changes, [("Taskforce2Vessel1", uid, "Russia")], uid)
            self.assertIn(f"Type={uid}\nNation=Russia\n", new)
        for uid in (JET, OLD_JET):
            text = f"[Taskforce2Aircraft1]\nType={uid}\nSquadronReference=Squadron1\nName=x\n"
            new, changes = self.sef.rewrite(text, self.idx)
            self.assertEqual(changes, [("Taskforce2Aircraft1", uid, "Russia")], uid)
        # The squadron the mission names decides: the Su-35S's Squadron4 is
        # China's, so the pass leaves it alone ([Default] says Russia).
        text = f"[Taskforce2Aircraft1]\nType={JET}\nSquadronReference=Squadron4\nName=x\n"
        self.assertEqual(self.sef.rewrite(text, self.idx), (text, []))

    def test_the_seed_report_is_unchanged_by_the_stubs(self):
        # Every unit the pass reports would be rewritten to the same flag with
        # the stub layer switched off: the stubs move no seed's Nation=.
        saved = self.sef.nation_stubs.nation
        try:
            on = self.report()
            self.sef.nation_stubs.nation = lambda rel, section, root=None: None
            off = self.report()
        finally:
            self.sef.nation_stubs.nation = saved
        self.assertEqual(on, off)

    def report(self):
        out = []
        for f in sorted(self.sef.HERE.glob("*.ini")):
            if " backup-" in f.name or f.name.lower().startswith(self.sef.OUT_OF_THEATRE):
                continue
            _new, changes = self.sef.rewrite(f.read_text(encoding="utf-8-sig", errors="replace"),
                                             self.idx)
            out.append((f.name, changes))
        return out


# Runs in its own interpreter, as test_world_sandbox_rebuild does: the world
# builder puts three folders on sys.path and imports by bare name.
WORLD = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
import build_dynamic_campaign as b
from submarines import MAPPINGS
out = {"operators": {u: b.operators(k, u) for k, u in (("vessels", sys.argv[2]), ("vessels", sys.argv[3]),
                                                       ("vessels", sys.argv[4]),
                                                       ("aircraft", "wp_mig-29k_941"),
                                                       ("aircraft", "wp_su_33"),
                                                       ("aircraft", "wp_su-27"))},
       "key": {n: b.NATION_KEY.get(n.lower()) for n in ("Russia", "Soviet")},
       "mappings": [[n, u, m[2], b.bp.pick_nation(u, "Default")] for (n, u), m in MAPPINGS.items()]}
print(json.dumps(out))
"""


@unittest.skipUnless(built(), "SEST Collection Fixes not built")
class WorldSandbox(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        run = subprocess.run([sys.executable, "-c", WORLD, str(ROOT / "integration/world-sandbox"),
                              STUBBED, LEFT, SPLIT], cwd=ROOT, capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.out = json.loads(run.stdout.strip().splitlines()[-1])

    def test_operators_read_the_stub_first(self):
        ops = self.out["operators"]
        self.assertTrue(ops[STUBBED])
        self.assertEqual(set(ops[STUBBED]), {"Russia"})
        self.assertEqual(set(ops[LEFT]), {"Soviet"})
        # Seven Akulas register Russia; [Default] and the other eleven, Soviet.
        self.assertEqual(ops[SPLIT].count("Russia"), 7)
        self.assertEqual(ops[SPLIT].count("Soviet"), 12)
        # A squadron registered elsewhere keeps its own nation.
        self.assertEqual(ops["wp_mig-29k_941"], ["Russia", "Russia", "India"])
        # Red Storm Arsenal's Su-33, a post-1991 type: every squadron, the
        # 279th's and those of its fictional carriers alike.
        self.assertEqual(ops["wp_su_33"], ["Russia"] * 11)
        self.assertEqual(set(ops["wp_su-27"]), {"Soviet"})

    def test_both_keys_still_fold_into_one_buy_list_nation(self):
        self.assertEqual(self.out["key"], {"Russia": "Russia", "Soviet": "Russia"})

    def test_the_submarine_flags_are_what_the_hulls_register(self):
        rows = [r for r in self.out["mappings"] if r[2] in ("Russia", "Soviet")]
        self.assertTrue(rows)
        for nation, uid, flag, registered in rows:
            self.assertEqual(flag, registered, (nation, uid))
        self.assertIn(["Russia", "wp_ssgn_yasen", "Russia", "Russia"], rows)
        self.assertIn(["Russia", "wp_ssn_akula", "Soviet", "Soviet"], rows)


@unittest.skipUnless(built(), "SEST Collection Fixes not built")
class CrossDeckAndCoverage(unittest.TestCase):
    """The Cross-Deck builder's nation() and check_campaign_coverage's flag
    check read the stub first, section by section."""

    @classmethod
    def setUpClass(cls):
        cls.xd = load("cross_deck_under_test", ROOT / "integration/cross-deck/build_pack.py")
        cls.cov = load("coverage_under_test", ROOT / "tools/check_campaign_coverage.py")

    def test_cross_deck_reads_the_stub_first(self):
        self.assertEqual(self.xd.nation("vessels", STUBBED), "russia")
        self.assertEqual(self.xd.nation("vessels", LEFT), "soviet")
        self.assertEqual(self.xd.nation("aircraft", JET), "russia")
        self.assertEqual(self.xd.nation("aircraft", OLD_JET), "soviet")
        self.assertEqual(self.xd.nation("vessels", "ru_cv_kuznetsov"), "soviet")   # Variant1, 1991

    def test_cross_deck_adds_nothing_to_a_russian_deck_either_way(self):
        # Neither key is an ally's, so the plan is the same with the stubs on
        # or off.
        self.assertNotIn("russia", {a.lower() for a in self.xd.ALLIES})
        self.assertNotIn("soviet", {a.lower() for a in self.xd.ALLIES})

    def test_the_flag_check_reads_the_stub(self):
        parsed = {"Taskforce2Aircraft1": {"Type": JET, "SquadronReference": "Squadron1"},
                  "Taskforce2Vessel1": {"Type": STUBBED, "VariantReference": "Variant1"}}
        self.assertEqual(self.cov.nations("x.ini", parsed), [])
        saved = self.cov.bp.nation_stubs.nation
        try:
            self.cov.bp.nation_stubs.nation = lambda rel, section, root=None: "Nowhere"
            out = self.cov.nations("x.ini", parsed)
        finally:
            self.cov.bp.nation_stubs.nation = saved
        self.assertEqual(len(out), 2)
        self.assertTrue(all("SEST's Nation stub" in line for line in out), out)


if __name__ == "__main__":
    unittest.main()
