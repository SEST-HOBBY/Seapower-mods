"""Price precedence and compatibility against captured CombatCosts 0.7.1 rules."""
from decimal import Decimal
from pathlib import Path
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration"))
from common.costs import (_build, build, carried_stores, cost_list, estimate_fields,  # noqa: E402
                          field_origin, fielded_units, inventory, parse_ini, price, read_ini,
                          render_catalog, resolve_field, weapon_excluded, KINDS, LAND_NOTE)

MAPPINGS = ROOT / "integration/combat-costs/mappings.json"
RESEARCH = ROOT / "integration/combat-costs/research.json"
RUNTIME_TESTS = ROOT / "integration/runtime-fixes/tests"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def tree(root, files):
    """Write {relative path: text} under root: a minimal synthetic install."""
    base = {"data/mod-catalog.json": '{"local_packs": []}',
            "data/load-order.tokens.txt": "1\n3807187341\n",
            "mods-source/3807187341/systems/weaponcosts.ini": "",
            "mods-source/3807187341/systems/vesselcosts.ini": "",
            "mods-source/3807187341/systems/aircraftcosts.ini": ""}
    for rel, text in {**base, **files}.items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return Path(root)


ESTIMATE = {
    "target": "test_frigate",
    "category": "FFG",
    "basis": "Test class: published contract price halved",
    "estimate": {"historical": "100000000", "historical_year": "1990",
                 "historical_method": "published price", "current": "250000000",
                 "current_year": "1990", "current_method": "CPI conversion",
                 "note": "100M x 334.4 / 130.7"},
    "sources": [{"title": "Test Gazette, 1 Jan 1990", "url": "https://example.org/gazette"},
                {"title": "CPI table", "url": "https://example.org/cpi"}],
}


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


def shared_table(name, columns):
    """Rows of a price-rule table the runtime plugin's mocked tests read too (build_plugin.py)."""
    lines = [line for line in (RUNTIME_TESTS / name).read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    rows = [line.split("\t") for line in lines]
    assert all(len(row) == columns for row in rows), name
    return rows[1:]


def cell(value):
    return None if value == "-" else "" if value == "(blank)" else value


class RuntimePluginParity(unittest.TestCase):
    """costs.py and the plugin's CostPolicy (CampaignCosts.cs) on the same rows, so the
    campaign totals and SEST's cost list apply one rule set."""

    def test_precedence_and_parse_match_the_plugin_table(self):
        def section(name, pairs):
            return "" if pairs == "-" else f"[{name}]\n" + "".join(p + "\n" for p in pairs.split(";"))
        rows = shared_table("cost_precedence.tsv", 8)
        self.assertGreaterEqual(len(rows), 40)
        for case, costs, entry, inline, field, inline_field, selected, expected in rows:
            with self.subTest(case=case):
                catalog = parse_ini(section("Costs", costs) + section("round", entry))
                unit = parse_ini(section("General", inline)).get("general", {})
                value = field_origin(unit, catalog, "Round", field, inline_field)[0]
                self.assertEqual(value, cell(selected))
                if expected != "-":
                    self.assertEqual(price(value), None if expected == "unknown" else Decimal(expected))

    def test_exclusion_matches_the_plugin_table(self):
        rows = shared_table("cost_exclusion.tsv", 4)
        self.assertGreaterEqual(len(rows), 30)
        for case, category, ammo_type, result in rows:
            with self.subTest(case=case):
                self.assertEqual(weapon_excluded(cell(category), ammo_type), result == "excluded")

    def test_only_ascii_digits_are_a_price(self):
        self.assertIsNone(price("٣"))    # an Arabic-Indic three: decimal.TryParse rejects it
        self.assertIsNone(price("1 000"))


class CompatibilityBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mappings = load(MAPPINGS)
        cls.research = load(RESEARCH)
        cls.built = _build(ROOT, cls.mappings)
        cls.result = cls.built[0]

    def test_existing_author_entries_are_not_replaced_even_if_blank(self):
        for kind, info in KINDS.items():
            original = read_ini(ROOT / "mods-source/3807187341/systems" / (info[1] + ".ini"))
            self.assertFalse(set(original) & set(self.result["extensions"][kind]))

    def test_generated_prices_are_exactly_source_catalog_values(self):
        for entry in self.result["entries"]:
            if entry.get("estimate"):
                continue    # SEST's own figure; checked against mappings.json below
            kind = entry["kind"]
            historical = KINDS[kind][2]
            source = read_ini(ROOT / "mods-source/3807187341/systems" / (KINDS[kind][1] + ".ini"))
            for field in (historical, "CurrentYearCost"):
                wanted = source[entry["source"].casefold()].get(field.casefold(), "") if entry["source"] else ""
                self.assertEqual(entry["fields"][field], wanted, entry["target"])

    def test_shipped_estimates_are_the_reviewed_figures_with_sources(self):
        entries = {(e["kind"], e["target"].casefold()): e for e in self.result["entries"]}
        count = 0
        for kind, items in self.mappings.items():
            for item in items:
                if "estimate" not in item:
                    continue
                count += 1
                self.assertNotIn("source", item)
                self.assertTrue(item["sources"], item["target"])
                fields = entries[(kind, item["target"].casefold())]["fields"]
                self.assertEqual(fields[KINDS[kind][2]], item["estimate"].get("historical", ""))
                self.assertEqual(fields["CurrentYearCost"], item["estimate"]["current"])
        self.assertEqual(count, 59)

    def test_refuted_and_unshipped_research_carries_no_price(self):
        for item in self.research["items"]:
            if item["kind"] == "land":
                continue    # kept for reference: the tracker prices no land platform
            fields = self.result["extensions"][item["kind"]].get(item["target"].casefold(), {})
            for key in (KINDS[item["kind"]][2], "CurrentYearCost"):
                self.assertFalse(fields.get(key), item["target"])
        # A reviewed mapping onto a blank author entry adds nothing, so none is
        # written; the spelling match still copies the author's blanks exactly.
        self.assertFalse([m for m in self.mappings["aircraft"] if m["target"] == "plaaf_j36"])
        self.assertEqual(self.result["extensions"]["aircraft"]["plaaf_j36"],
                         {"AircraftCosts": "", "CurrentYearCost": ""})

    def test_second_batch_mappings_and_estimates_24_oct(self):
        weapons = self.result["extensions"]["weapon"]
        # A reviewed mapping copies the author's pair; Category only where the source's is wrong.
        self.assertEqual(weapons["plaaf_ls-500"], {"WeaponCosts": "28000", "CurrentYearCost": "45000",
                                                   "Category": "Bomb"})
        self.assertEqual(weapons["wp_r-37"]["Category"], "AAM")
        mk54 = {e["target"]: e for e in self.result["entries"] if e.get("estimate")}["usn_mk54_air"]
        self.assertEqual((mk54["estimate"]["historical_method"], mk54["estimate"]["current_method"]),
                         ("published price", "CPI conversion"))
        self.assertEqual((weapons["usn_mk54_air"]["WeaponCosts"], weapons["usn_mk54_air"]["CurrentYearCost"]),
                         ("1000000", "1190000"))
        # A current-only estimate leaves the historical price unknown.
        self.assertEqual((weapons["usn_mk46_air"]["WeaponCosts"], weapons["usn_mk46_air"]["CurrentYearCost"]),
                         ("", "1190000"))
        # civ_a320 and civ_a330 keep their 23 Oct estimates: the new rows add no historical price.
        a320 = self.result["extensions"]["aircraft"]["civ_a320"]
        self.assertEqual((a320["AircraftCosts"], a320["CurrentYearCost"]), ("", "55000000"))
        for kind, items in self.mappings.items():
            for item in items:
                for source in item.get("sources", []):
                    self.assertNotIn("checked.json", source["title"], item["target"])
                    self.assertFalse(source["url"].startswith("file:docs/combat-costs/cost-list.md"),
                                     item["target"])

    def test_research_rerun_notes_and_land_items(self):
        kinds = {item["kind"] for item in self.research["items"]}
        self.assertEqual(kinds, {"aircraft", "vessel", "weapon", "land"})
        for item in self.research["items"]:
            if "rerun" in item:
                self.assertIn("Re-run: " + item["rerun"], item["why"], item["target"])
        keys = [(i["kind"], i["target"].casefold()) for i in self.research["items"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_custom_rounds_and_wrong_ran_names_stay_unknown(self):
        for kind, uid in (("weapon", "sest_aim-424"),
                          ("vessel", "ran_aor_supply"), ("vessel", "ran_ffh_anzac"),
                          ("vessel", "ran_ssg_collins")):
            fields = self.result["extensions"][kind][uid]
            self.assertEqual(fields[KINDS[kind][2]], "")
            self.assertEqual(fields["CurrentYearCost"], "")

    def test_redback_is_a_labelled_model_estimate(self):
        fields = self.result["extensions"]["weapon"]["sest_agr-30"]
        self.assertEqual((fields["WeaponCosts"], fields["CurrentYearCost"], fields["Category"]),
                         ("70000", "150000", "ATGM"))
        text = render_catalog("weapon", self.result)
        block = text[text.index("; SEST researched estimate, not a tracker author price: AGR-30"):]
        block = block[:block.index("[sest_agr-30]")]
        self.assertIn("model estimate, reference year 1998", block)

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
            for line in text.splitlines():
                self.assertTrue(line == "" or line.startswith((";", "[", "#!extend"))
                                or line.split("=", 1)[0] in (info[2], "CurrentYearCost", "Category"),
                                line)

    def test_normalization_does_not_choose_between_conflicting_prices(self):
        with tempfile.TemporaryDirectory() as temp:
            root = tree(temp, {"mods-source/1/ammunition/foobar.ini": "[General]\nType=Missile\n"})
            catalogs = root / "mods-source/3807187341/systems"
            (catalogs / "weaponcosts.ini").write_text("[foo-bar]\nWeaponCosts=10\n[foo_bar]\nWeaponCosts=20\n")
            result = build(root, {})
            self.assertNotIn("foobar", result["extensions"]["weapon"])
            (catalogs / "weaponcosts.ini").write_text("[foobar]\nWeaponCosts=\n[foo-bar]\nWeaponCosts=20\n")
            result = build(root, {})
            self.assertNotIn("foobar", result["extensions"]["weapon"])


class ResearchedEstimates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = tree(self.temp.name, {
            "mods-source/1/vessels/test_frigate.ini": "[General]\nLength=100\n",
            "mods-source/1/vessels/test_cutter.ini": "[General]\nLength=50\n"})

    def tearDown(self):
        self.temp.cleanup()

    def test_estimate_renders_with_its_comments(self):
        result = build(self.root, {"vessel": [ESTIMATE]})
        self.assertEqual(result["extensions"]["vessel"]["test_frigate"],
                         {"VesselCosts": "100000000", "CurrentYearCost": "250000000", "Category": "FFG"})
        text = render_catalog("vessel", result)
        block = text[text.index("; SEST researched estimate"):]
        for line in ("; SEST researched estimate, not a tracker author price: "
                     "Test class: published contract price halved",
                     "; Historical (VesselCosts): published price, reference year 1990",
                     "; Current (CurrentYearCost): CPI conversion, source year 1990",
                     "; Note: 100M x 334.4 / 130.7",
                     "; Source: Test Gazette, 1 Jan 1990 - https://example.org/gazette",
                     "; Source: CPI table - https://example.org/cpi",
                     "; Source catalog section: none",
                     "[test_frigate]", "VesselCosts=100000000", "CurrentYearCost=250000000",
                     "Category=FFG"):
            self.assertIn(line + "\n", block)
        # The comments are comments: the parsed section holds the three keys only.
        self.assertEqual(parse_ini(text)["test_frigate"],
                         {"vesselcosts": "100000000", "currentyearcost": "250000000", "category": "FFG"})

    def test_one_price_estimate_leaves_the_other_unknown(self):
        item = copy.deepcopy(ESTIMATE)
        for key in ("historical", "historical_year", "historical_method"):
            del item["estimate"][key]
        result = build(self.root, {"vessel": [item]})
        self.assertEqual(result["extensions"]["vessel"]["test_frigate"]["VesselCosts"], "")
        self.assertIn("; Historical (VesselCosts): unknown\n", render_catalog("vessel", result))
        unknown = {e["id"]: e for e in result["coverage"]["vessel"]["unknown"]}
        self.assertTrue(unknown["test_frigate"]["historical_unknown"])
        self.assertFalse(unknown["test_frigate"]["current_unknown"])

    def test_sourceless_or_unparseable_estimate_is_rejected(self):
        def broken(change):
            item = copy.deepcopy(ESTIMATE)
            change(item)
            return item
        cases = {
            "no sources": broken(lambda i: i.update(sources=[])),
            "sources missing": broken(lambda i: i.pop("sources")),
            "source without URL": broken(lambda i: i["sources"][0].pop("url")),
            "no basis": broken(lambda i: i.pop("basis")),
            "catalog source key": broken(lambda i: i.update(source="other_frigate")),
            "thousands separator": broken(lambda i: i["estimate"].update(historical="100,000,000")),
            "exponent": broken(lambda i: i["estimate"].update(current="2.5e8")),
            "negative": broken(lambda i: i["estimate"].update(current="-1")),
            "zero is not an estimate": broken(lambda i: i["estimate"].update(current="0")),
            "number not string": broken(lambda i: i["estimate"].update(current=250000000)),
            "no year": broken(lambda i: i["estimate"].pop("historical_year")),
            "unknown method": broken(lambda i: i["estimate"].update(current_method="guess")),
            "no price at all": broken(lambda i: i.update(estimate={})),
            "method without price": broken(lambda i: i["estimate"].update(historical="")),
            "line break in basis": broken(lambda i: i.update(basis="one\n[test_frigate]")),
            "line break in title": broken(lambda i: i["sources"][1].update(title="a\nWeaponCosts=1")),
            "unknown key": broken(lambda i: i["estimate"].update(historcal="1")),
            "no category": broken(lambda i: i.pop("category")),
        }
        for name, item in cases.items():
            with self.subTest(name):
                with self.assertRaises(ValueError):
                    estimate_fields("vessel", item)
                with self.assertRaises(ValueError):
                    build(self.root, {"vessel": [item]})
        self.assertEqual(estimate_fields("vessel", ESTIMATE)["VesselCosts"], "100000000")

    def test_an_author_entry_still_wins_over_an_estimate(self):
        (self.root / "mods-source/3807187341/systems/vesselcosts.ini").write_text(
            "[test_frigate]\nVesselCosts=\nCurrentYearCost=\n")
        result = build(self.root, {"vessel": [ESTIMATE]})
        self.assertNotIn("test_frigate", result["extensions"]["vessel"])


class CostList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mappings = load(MAPPINGS)
        cls.research = load(RESEARCH)
        cls.built = _build(ROOT, cls.mappings)
        cls.md, cls.csv = cost_list(ROOT, cls.mappings, cls.research, cls.built)

    def test_list_is_deterministic_across_processes(self):
        script = ("import json, sys, hashlib; sys.path.insert(0, 'integration');"
                  "from common.costs import cost_list;"
                  "md, table = cost_list('.', json.load(open(sys.argv[1], encoding='utf-8')),"
                  " json.load(open(sys.argv[2], encoding='utf-8')));"
                  "print(hashlib.sha256((md + table).encode()).hexdigest())")
        digests = set()
        for seed in ("1", "2"):
            run = subprocess.run([sys.executable, "-c", script, str(MAPPINGS), str(RESEARCH)],
                                 cwd=ROOT, capture_output=True, text=True, check=True,
                                 env=dict(os.environ, PYTHONHASHSEED=seed))
            digests.add(run.stdout.strip())
        digests.add(hashlib.sha256((self.md + self.csv).encode()).hexdigest())
        self.assertEqual(len(digests), 1)

    def test_sections_in_order_with_the_network_note_first(self):
        headings = [line for line in self.md.splitlines() if line.startswith("## ")]
        self.assertEqual(headings, [
            "## Summary", "## Weapons SEST ships", "## Vessels SEST ships",
            "## Aircraft SEST ships", "## Vessels SEST's missions field",
            "## Aircraft SEST's missions field", "## Land units SEST ships",
            "## SEST researched estimates", "## Gaps",
            "## Next batch: weapons carried by fielded units with a missing price"])
        top = self.md[:self.md.index("## Summary")]
        self.assertIn("network policy blocked", top)
        self.assertIn("Researched estimates are SEST's", top)

    def test_every_sest_unit_and_land_unit_is_listed(self):
        rows = {(r[0], r[2]) for r in (line.split(",") for line in self.csv.splitlines()[1:])}
        units = inventory(ROOT)
        for kind in KINDS:
            for unit in units[kind].values():
                if unit["owner"].startswith("SEST_"):
                    self.assertIn(("sest", unit["id"]), rows)
        land = [line for line in self.csv.splitlines() if line.startswith("land,")]
        self.assertTrue(land)
        for line in land:
            self.assertTrue(line.endswith("," + LAND_NOTE + ","), line)

    def test_gaps_keep_the_research_and_its_sources(self):
        gaps = self.md[self.md.index("### Researched, not shipped"):self.md.index("## Next batch")]
        for item in self.research["items"]:
            self.assertIn(f"- **{item['target']}** ({item['kind']}", gaps)
            for source in item["sources"]:
                self.assertIn(source["url"], gaps)
        self.assertIn("**usn_taoe_supply** (vessel, SEST_Replenishment) - refuted", gaps)

    def test_estimates_are_labelled_with_method_and_sources(self):
        section = self.md[self.md.index("## SEST researched estimates"):self.md.index("## Gaps")]
        self.assertIn("- **tha_cvl_chakri_naruebet** (vessel, CVL): historical 285,000,000 "
                      "(published price, reference year 1993); current 660,000,000 "
                      "(CPI conversion, source year 1993).", section)
        self.assertIn("| tha_cvl_chakri_naruebet | SEST_Replenishment | CVL | 285,000,000 | "
                      "660,000,000 | SEST researched estimate |", self.md)

    def test_next_batch_is_grouped_with_counts_first(self):
        batch = self.md[self.md.index("## Next batch"):]
        groups = [line[4:].rsplit(" (", 1)[0] for line in batch.splitlines() if line.startswith("### ")]
        order = ["Missiles", "Bombs and depth charges", "Torpedoes", "Guns and projectiles",
                 "Rockets", "Fuel tanks", "Containers", "Chaff", "Noisemakers and decoys",
                 "Sonobuoys", "Other"]
        self.assertEqual(groups, [g for g in order if g in groups])
        self.assertLess(batch.index("| group | missing a price |"), batch.index("### "))
        for line in self.csv.splitlines():
            if line.startswith("next-batch,"):
                self.assertNotIn(",tracker catalog,", line)

    def test_land_research_is_listed_and_duplicates_rejected_on_a_synthetic_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = tree(temp, {
                "mods-source/1/land_units/test_tel.ini": "[General]\nLength=1\n",
                "integration/campaign/SEST_Campaign/missions/Op/Op 01.ini": "[Zone1]\nType=Deployment\n",
                "integration/campaign/SEST_Campaign/campaigns/c1/c1.ini": "",
            })
            item = {"target": "test_tel", "kind": "land", "decision": "left unknown",
                    "candidate": "none", "why": "No figure.", "sources": []}
            md, _ = cost_list(root, {}, {"reviewed": "today", "items": [item]})
            self.assertIn("- **test_tel** (land, 1) - left unknown. Candidate: none. Why not shipped: "
                          "No figure. Never shipped: the tracker does not price land platforms.", md)
            with self.assertRaisesRegex(ValueError, "listed twice"):
                cost_list(root, {}, {"reviewed": "today", "items": [item, item]})
            with self.assertRaisesRegex(ValueError, "no longer exists"):
                cost_list(root, {}, {"reviewed": "today", "items": [dict(item, target="gone")]})

    def test_fielded_units_and_carried_stores_on_a_synthetic_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = tree(temp, {
                "mods-source/1/vessels/test_frigate.ini":
                    "[General]\nLength=1\n[WeaponSystem1]\nAmmunition=test_chaff\n"
                    "[WeaponMagazineA]\nAmmunition1=test_sam\nAmmunition1_Count=8\n"
                    "[WeaponSystem2]\nAssociatedMagazine=TorpedoRoom\n"
                    "[TorpedoRoom]\nNumberOfAmmunitionTypes=1\nAmmunition1=test_torp\n",
                "mods-source/1/aircraft/test_jet.ini":
                    "[General]\nLength=1\n[WeaponSystems]\nAvailableLoadouts=Strike\n"
                    "DateBased_AAM=1970,test_aam_a|1990,test_aam_b\n"
                    "[WeaponSystem1]\nStation1=-0.05,0,0\n"
                    "[WeaponSystem1Strike]\nStation1=test_bomb|Rack1\nStation2=DateBased_AAM\n"
                    "Station4=test_pod\n"
                    "# Station3=test_hidden\n"
                    "[WeaponSystem1Default]\nStation1=test_unoffered\n",
                **{f"mods-source/1/ammunition/{r}.ini": "[General]\nType=Missile\n"
                   for r in ("test_chaff", "test_sam", "test_aam_a", "test_aam_b", "test_bomb",
                             "test_hidden", "test_unoffered")},
                "mods-source/1/ammunition/test_pod.ini":
                    "[General]\nType=Container\n[Ammunition]\nAmmunition=test_rocket\n",
                "mods-source/1/ammunition/test_rocket.ini": "[General]\nType=AerialRocket\n",
                "mods-source/1/ammunition/test_torp.ini": "[General]\nType=Torpedo\n",
                "integration/campaign/SEST_Campaign/missions/Op/Op 01.ini":
                    "[Taskforce1Vessel1]\nType=test_frigate\n[Zone1]\nType=Deployment\n",
                "integration/campaign/SEST_Campaign/campaigns/c1/player_task_force_roster.ini":
                    "[AllowedAircraft]\ntest_jet=Squadron1|40\n",
            })
            units = inventory(root)
            self.assertEqual(fielded_units(root, units),
                             {"vessel": {"test_frigate": ["Op"]}, "aircraft": {"test_jet": ["c1"]}})
            self.assertEqual(carried_stores(units["vessel"]["test_frigate"], units["vessel"]),
                             ["test_chaff", "test_sam", "test_torp"])
            self.assertEqual([s for s in carried_stores(units["aircraft"]["test_jet"], units["aircraft"])
                              if s in units["weapon"]], ["test_aam_a", "test_aam_b", "test_bomb", "test_pod"])
            md, table = cost_list(root, {}, {"reviewed": "today", "items": []})
            self.assertIn("### Missiles (5)", md)
            self.assertIn("### Containers (1)", md)
            self.assertIn("### Torpedoes (1)", md)
            # The tracker charges the rounds a pod fires, so they are carried too.
            self.assertIn("| test_rocket | AerialRocket | 1 | unknown | unknown | 1: test_jet |", md)
            self.assertIn("| test_frigate | 1 | - | unknown | unknown | unknown: no tracker entry | Op |", md)


if __name__ == "__main__":
    unittest.main()
