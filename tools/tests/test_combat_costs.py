"""Price precedence and compatibility against captured CombatCosts 0.7.1 rules."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration"))
from common.costs import (build, parse_ini, price, read_ini, render_catalog,
                          resolve_field, KINDS)  # noqa: E402


class PricePrecedence(unittest.TestCase):
    def test_inline_default_and_independent_current_price(self):
        catalog = parse_ini("[round]\nWeaponCosts=2500000\nCurrentYearCost=3000000\n")
        own = {"weaponcosts": "10"}
        self.assertEqual(resolve_field(own, catalog, "ROUND", "WeaponCosts"), "10")
        self.assertEqual(resolve_field(own, catalog, "round", "CurrentYearCost"), "3000000")

    def test_field_then_entry_then_global_switch(self):
        catalog = parse_ini("[Costs]\nOverrideInline=True\n[round]\n"
                            "OverrideInline=False\nOverrideCurrentYearCost=True\n"
                            "WeaponCosts=20\nCurrentYearCost=30\n")
        own = {"weaponcosts": "1", "currentyearcost": "2"}
        self.assertEqual(resolve_field(own, catalog, "round", "WeaponCosts"), "1")
        self.assertEqual(resolve_field(own, catalog, "round", "CurrentYearCost"), "30")

    def test_explicit_blank_and_invalid_are_unknown_not_fallback(self):
        catalog = parse_ini("[round]\nWeaponCosts=500\nCurrentYearCost=600\n")
        for value in ("", "unknown", "-2"):
            with self.subTest(value=value):
                selected = resolve_field({"weaponcosts": value}, catalog, "round", "WeaponCosts")
                self.assertIsNone(price(selected))
        catalog["round"].update(overrideinline="True", weaponcosts="")
        self.assertIsNone(price(resolve_field({"weaponcosts": "500"}, catalog, "round", "WeaponCosts")))

    def test_zero_is_free_and_current_never_falls_back_to_historical(self):
        self.assertEqual(price("0"), 0)
        self.assertIsNone(resolve_field({"weaponcosts": "500"}, {}, "round", "CurrentYearCost"))
        for value in ("1,000", "1e6", "NaN", "Infinity", "-1", "1000000000000001"):
            self.assertIsNone(price(value), value)

    def test_native_points_are_not_dollars(self):
        self.assertIsNone(resolve_field({"cost": "900", "perround": "12.5"}, {}, "round", "WeaponCosts"))

    def test_category_uses_its_own_field_switch(self):
        catalog = parse_ini("[round]\nCategory=AAM\nOverrideCategory=True\nWeaponCosts=200\n")
        own = {"weaponcostcategory": "Other", "weaponcosts": "100"}
        self.assertEqual(resolve_field(own, catalog, "round", "Category", "WeaponCostCategory"), "AAM")
        self.assertEqual(resolve_field(own, catalog, "round", "WeaponCosts"), "100")


class CompatibilityBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mappings = json.loads((ROOT / "integration/combat-costs/mappings.json").read_text())
        cls.result = build(ROOT, cls.mappings)

    def test_existing_author_entries_are_not_replaced_even_if_blank(self):
        for kind, info in KINDS.items():
            original = read_ini(ROOT / "mods-source/3807187341/systems" / (info[1] + ".ini"))
            self.assertFalse(set(original) & set(self.result["extensions"][kind]))

    def test_generated_prices_are_exactly_source_catalog_values(self):
        for entry in self.result["entries"]:
            kind = entry["kind"]
            historical = KINDS[kind][2]
            source = read_ini(ROOT / "mods-source/3807187341/systems" / (KINDS[kind][1] + ".ini"))
            for field in (historical, "CurrentYearCost"):
                wanted = source[entry["source"].casefold()].get(field.casefold(), "") if entry["source"] else ""
                self.assertEqual(entry["fields"][field], wanted, entry["target"])

    def test_custom_rounds_and_wrong_ran_names_stay_unknown(self):
        for kind, uid in (("weapon", "sest_aim-424"), ("weapon", "sest_agr-30"),
                          ("vessel", "ran_aor_supply"), ("vessel", "ran_ffh_anzac"),
                          ("vessel", "ran_ssg_collins")):
            fields = self.result["extensions"][kind][uid]
            self.assertEqual(fields[KINDS[kind][2]], "")
            self.assertEqual(fields["CurrentYearCost"], "")

    def test_actual_ran_airframe_and_arrw_values(self):
        ran = self.result["extensions"]["aircraft"]["ran_mh-60r"]
        self.assertEqual((ran["AircraftCosts"], ran["CurrentYearCost"]), ("33800000", "56200000"))
        arrw = self.result["extensions"]["weapon"]["usn_arrw"]
        self.assertEqual((arrw["WeaponCosts"], arrw["CurrentYearCost"]), ("6720000", "8700000"))
        self.assertEqual(arrw["Category"], "Land Attack")

    def test_extensions_preserve_global_settings_and_only_contain_cost_keys(self):
        for kind, info in KINDS.items():
            text = render_catalog(kind, self.result)
            self.assertTrue(text.startswith("#!extend systems/" + info[1] + ".ini\n"))
            sections = parse_ini(text)
            self.assertNotIn("costs", sections)
            self.assertNotIn("overlay", sections)
            for fields in sections.values():
                self.assertLessEqual(set(fields), {info[2].casefold(), "currentyearcost", "category"})

    def test_normalization_does_not_choose_between_conflicting_prices(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "data").mkdir()
            (root / "data/mod-catalog.json").write_text('{"local_packs": []}')
            (root / "data/load-order.tokens.txt").write_text("1\n3807187341\n")
            (root / "mods-source/1/ammunition").mkdir(parents=True)
            (root / "mods-source/1/ammunition/foobar.ini").write_text("[General]\nType=Missile\n")
            catalogs = root / "mods-source/3807187341/systems"
            catalogs.mkdir(parents=True)
            (catalogs / "weaponcosts.ini").write_text("[foo-bar]\nWeaponCosts=10\n[foo_bar]\nWeaponCosts=20\n")
            for name in ("vesselcosts", "aircraftcosts"):
                (catalogs / (name + ".ini")).write_text("")
            result = build(root, {})
            self.assertNotIn("foobar", result["extensions"]["weapon"])
            (catalogs / "weaponcosts.ini").write_text("[foobar]\nWeaponCosts=\n[foo-bar]\nWeaponCosts=20\n")
            result = build(root, {})
            self.assertNotIn("foobar", result["extensions"]["weapon"])


if __name__ == "__main__":
    unittest.main()
