"""The 2028 World Sandbox must not stage or sell the P-3-bodied imitation P-8.

build_dynamic_campaign.WORLD_UNIT_SUBSTITUTIONS swaps Red Storm Arsenal's
usn_p_8a (named a P-8A, draws the P-3C) for US Navy 2027's usn_p8_2027 in the
World Sandbox only. These checks are relations, not counts, so a Workshop
refresh that adds or removes units does not break them. That the committed
campaign is the builder's output is tools/tests/test_world_sandbox_rebuild.py,
and that the regional variant is built from it is test_regional_expansion.py.
"""
import json
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "integration/world-sandbox"
WORLD = HERE / "SEST_World_Campaign/dynamic_campaigns"
DIST = ROOT / "integration/dist/SEST_Integration/dynamic_campaigns"
REPORT = HERE / "draft/conversion.json"
OLD = "usn_p_8a"
CURRENT = "usn_p8_2027"
WORLD_VARIANTS = ("sest-world-sandbox", "sest-world-regions-2028")

# Facts only the builder can answer (its resolver, value rule and quantity
# parser), from a separate interpreter: it imports build_pack, home_bases and
# submarines by bare name.
SCRIPT = r"""
import json, re, sys
sys.path.insert(0, sys.argv[1])
import build_dynamic_campaign as b


def shipped_by(rel):
    # The first provider in load order that ships rel, matched without case
    # as the game does. bp.index() leaves out files two folders deep under
    # aircraft/, which is where model folders sit, so walk the providers.
    for token, base in b.bp.providers():
        cur = base
        for part in filter(None, rel.split("/")):
            cur = next((c for c in cur.iterdir() if c.name.lower() == part.lower()),
                       None) if cur.is_dir() else None
            if cur is None:
                break
        if cur is not None and cur.is_file():
            return token
    return None


units = {}
for uid in sys.argv[2:]:
    f = b.bp.unit_file(uid)[1]
    squadrons = b.bp.winning(f"aircraft/{uid}_squadrons.ini")
    text = b.text_of(uid)
    key = lambda k: (re.search(rf"^\s*{k}\s*=\s*(\S+)", text, re.M) or [None, None])[1]
    folder, material = key("ResourcesFolder"), key("ResourcesMaterial")
    units[uid] = {"file": str(f) if f else None, "text": text,
                  "squadrons": b.bp.read(squadrons) if squadrons else "",
                  "value": b.value_of(uid)[0] if f else None,
                  "model_folder": folder, "material": material,
                  "material_from": shipped_by(f"{folder}/{material}")   # folder may end in /
                                   if folder and material else None}
register = json.loads(b.REGISTER.read_text(encoding="utf-8"))
quantity = {f"{p['world_id']} {r['asset_id']}": b.quantity(r)
            for p in register["packages"] for r in p["forces"]}
json.dump({"substitutions": b.WORLD_UNIT_SUBSTITUTIONS, "units": units, "quantity": quantity},
          sys.stdout)
"""


def unit_counts(force):
    """{unit id: aircraft} of a force's 'uid xN' specs."""
    out = Counter()
    for spec in force["units"]:
        m = re.match(r"(\S+)(?:\s+x(\d+))?", spec)
        out[m.group(1)] += int(m.group(2) or 1)
    return out


class WorldPoseidonModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run = subprocess.run([sys.executable, "-c", SCRIPT, str(HERE), OLD, CURRENT],
                             cwd=ROOT, capture_output=True, text=True)
        if run.returncode:
            raise AssertionError(f"builder facts failed:\n{run.stdout}{run.stderr}")
        cls.facts = json.loads(run.stdout)
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.campaigns = {}
        for variant in WORLD_VARIANTS:
            source = json.loads((WORLD / variant / "campaign.json").read_text(encoding="utf-8"))
            shipped = json.loads((DIST / variant / "campaign.json").read_text(encoding="utf-8"))
            cls.campaigns[variant] = (source, shipped)

    def test_the_builder_swaps_this_unit_for_this_one(self):
        self.assertEqual(self.facts["substitutions"].get(OLD), CURRENT)

    def test_replacement_is_a_poseidon_with_a_us_navy_squadron(self):
        unit = self.facts["units"][CURRENT]
        self.assertIsNotNone(unit["file"], f"no installed mod defines {CURRENT}")
        self.assertRegex(unit["text"], r"(?m)^ResourcesRoot=P8_Poseidon\.obj\s*$")
        self.assertRegex(unit["squadrons"], r"(?m)^Nation=US\s*$")
        # The model folder comes from another mod (Boeing P-8 Poseidon,
        # 3602046770, today), so check that the load order still ships it:
        # the exported mods are text only, so its material file stands in
        # for the mesh.
        self.assertIsNotNone(
            unit["material_from"],
            f"no mod in the load order ships {unit['model_folder']}{unit['material']}")

    def test_the_swap_keeps_the_price(self):
        # value_of(): an aircraft is valued by its first Role (both are MPA).
        old, new = self.facts["units"][OLD], self.facts["units"][CURRENT]
        if old["file"] is None:
            self.skipTest(f"{OLD} is no longer installed")
        self.assertEqual(new["value"], old["value"])
        for variant, (source, _) in self.campaigns.items():
            with self.subTest(campaign=variant):
                self.assertEqual(source["values"][CURRENT], new["value"])

    def test_both_worlds_sell_the_replacement_once_and_never_the_old_model(self):
        for variant, (source, shipped) in self.campaigns.items():
            with self.subTest(campaign=variant):
                self.assertEqual(source, shipped)
                bought = [e["unit"] for e in source["catalogue"]]
                placed = {u for f in source["forces"] for u in unit_counts(f)}
                # Every unit for sale has a value and every value is for sale:
                # the catalogue and the value table are the same set of ids.
                self.assertEqual(len(bought), len(set(bought)))
                self.assertEqual(set(bought), set(source["values"]))
                self.assertEqual(bought.count(CURRENT), 1)
                entry = next(e for e in source["catalogue"] if e["unit"] == CURRENT)
                self.assertEqual((entry["side"], entry.get("aircraft")), ("blue", True))
                self.assertNotIn(OLD, bought)
                self.assertNotIn(OLD, source["values"])
                self.assertNotIn(OLD, placed)
                self.assertIn(CURRENT, placed)

    def test_every_register_row_for_the_old_model_now_flies_the_replacement(self):
        rows = [r for r in self.report["rows"] if OLD in r["units"]]
        self.assertTrue(rows, f"the register no longer names {OLD}: retire the substitution")
        self.assertFalse([r for r in self.report["rows"] if r.get("unit") == OLD])
        # The builder takes a row's first id that resolves; OLD always does,
        # through the substitution, so a converted row naming it first flies CURRENT.
        taken = [r for r in rows if r["outcome"] == "converted" and r["units"][0] == OLD]
        self.assertTrue(taken)
        for r in taken:
            with self.subTest(row=r["asset_id"]):
                self.assertEqual(r["unit"], CURRENT)
                self.assertIn(f"corrected from {OLD}", r["resolved"])

    def test_same_bases_and_strength_as_the_register(self):
        # Per air base: the replacement's aircraft in the opening forces are
        # exactly the register quantities of the converted rows that fly it.
        expected = Counter()
        for r in self.report["rows"]:
            if r["outcome"] == "converted" and r.get("unit") == CURRENT:
                expected[r["base"]] += self.facts["quantity"][f"{r['node']} {r['asset_id']}"]
        self.assertTrue(expected)
        for variant, (source, _) in self.campaigns.items():
            with self.subTest(campaign=variant):
                fielded = Counter()
                for f in source["forces"]:
                    n = unit_counts(f)[CURRENT]
                    if n:
                        self.assertEqual(f["type"], "Air", f["name"])
                        fielded[f["base"]] += n
                self.assertEqual(fielded, expected)


if __name__ == "__main__":
    unittest.main()
