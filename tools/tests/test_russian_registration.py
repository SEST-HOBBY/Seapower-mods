#!/usr/bin/env python3
"""The Russian Federation, not the USSR: the readers of SEST's Nation stubs.

SEST Collection Fixes re-registers the post-1991, Russian-built hulls to the
game's Russia key with #!extend Nation stubs on their variants files
(integration/collection-fixes/build_patch.py, RU_REREGISTER; the stubs
themselves are tested in test_collection_fixes.py). Three readers outside the
campaign builder have to read the stub before the winning file, as the game
does, through the one shared helper (integration/common/nation_stubs.py):

  integration/mission-seeds/set_enemy_flags.py   registered()
  integration/world-sandbox/build_dynamic_campaign.py   operators()
  integration/world-sandbox/submarines.py   MAPPINGS' flag column, by hand

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
LEFT = "wp_ssn_akula"

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

    def test_a_seed_unit_still_gets_its_russian_flag(self):
        # R0: with the identity entry the pass writes Nation=Russia on a
        # stubbed hull exactly as it did when the file said Soviet.
        for uid in (STUBBED, LEFT):
            text = f"[Taskforce2Vessel1]\nType={uid}\nVariantReference=Variant1\nName=x\n"
            new, changes = self.sef.rewrite(text, self.idx)
            self.assertEqual(changes, [("Taskforce2Vessel1", uid, "Russia")], uid)
            self.assertIn(f"Type={uid}\nNation=Russia\n", new)

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
                                                       ("aircraft", "wp_mig-29k_941"))},
       "key": {n: b.NATION_KEY.get(n.lower()) for n in ("Russia", "Soviet")},
       "mappings": [[n, u, m[2], b.bp.pick_nation(u, "Default")] for (n, u), m in MAPPINGS.items()]}
print(json.dumps(out))
"""


@unittest.skipUnless(built(), "SEST Collection Fixes not built")
class WorldSandbox(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        run = subprocess.run([sys.executable, "-c", WORLD, str(ROOT / "integration/world-sandbox"),
                              STUBBED, LEFT], cwd=ROOT, capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.out = json.loads(run.stdout.strip().splitlines()[-1])

    def test_operators_read_the_stub_first(self):
        ops = self.out["operators"]
        self.assertTrue(ops[STUBBED])
        self.assertEqual(set(ops[STUBBED]), {"Russia"})
        self.assertEqual(set(ops[LEFT]), {"Soviet"})
        # A squadron registered elsewhere keeps its own nation (no aircraft is stubbed).
        self.assertEqual(ops["wp_mig-29k_941"], ["Soviet", "Soviet", "India"])

    def test_both_keys_still_fold_into_one_buy_list_nation(self):
        self.assertEqual(self.out["key"], {"Russia": "Russia", "Soviet": "Russia"})

    def test_the_submarine_flags_are_what_the_hulls_register(self):
        rows = [r for r in self.out["mappings"] if r[2] in ("Russia", "Soviet")]
        self.assertTrue(rows)
        for nation, uid, flag, registered in rows:
            self.assertEqual(flag, registered, (nation, uid))
        self.assertIn(["Russia", "wp_ssgn_yasen", "Russia", "Russia"], rows)
        self.assertIn(["Russia", "wp_ssn_akula", "Soviet", "Soviet"], rows)


if __name__ == "__main__":
    unittest.main()
