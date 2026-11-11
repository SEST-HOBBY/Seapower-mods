"""Native campaign ribbons, commander nations and real-award representations.

The unit tests drive integration/campaign/service_awards.py directly. The
BuiltCampaigns tests read the four campaigns build_pack.py wrote under
integration/campaign/SEST_Campaign the way the game reads them: awards from
[MissionN] TaskForceModeRibbonAwards ('|' between awards, ',' before nation
selectors), definitions from commander_settings.ini Ribbon_<id> sections,
nations from [CommanderSettings] and ranks from [OfficerRanks].
"""
from datetime import date
import hashlib
import importlib.util
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "integration/campaign/service_awards.py"
spec = importlib.util.spec_from_file_location("service_awards", SOURCE)
awards = importlib.util.module_from_spec(spec)
spec.loader.exec_module(awards)
PACK = ROOT / "integration/campaign/SEST_Campaign"
STOCK_MEDIA = ROOT / "data/install-snapshot/streaming-media.txt"
UI = ROOT / "mods-source/_vanilla/original/language_en/ui.ini"
NATION_KEYS = ROOT / "mods-source/_vanilla/original/language_en/nations.ini"
STOCK_EMBLEMS = {"ui/campaign/navy_emblems/ran_emblem.png", "ui/campaign/navy_emblems/usn_emblem.png",
                 "ui/campaign/navy_emblems/jmsdf_emblem.png"}
# Every award id the ribbon expansion (4d342e31) shipped, by campaign. An id
# a save may hold must keep its definition.
SHIPPED = {
    "sest-southern-watch": {"sest_southern_watch_service", "sest_northern_lifeline", "sest_archipelago_operations",
                            "navy_achievement_medal", "navy_commendation_medal",
                            "australian_distinguished_service_cross", "navy_unit_commendation"},
    "sest-southern-reach": {"sest_southern_reach_service", "sest_antarctic_lifeline", "sest_southern_convoy",
                            "navy_achievement_medal", "sest_aosm_indo_pacific", "navy_commendation_medal",
                            "australian_distinguished_service_cross", "navy_unit_commendation",
                            "meritorious_unit_commendation"},
    "sest-red-line": {"sest_red_line_service", "sest_contact_intelligence", "sest_undersea_operations"},
    "sest-sulu-line": {"sest_sulu_line_service", "sest_fleet_sustainment", "sest_littoral_operations"},
    # Makran Line's, added 11 Nov 2026: fictional only.
    "sest-makran-line": {"sest_makran_line_service", "sest_arabian_sea_security",
                         "sest_trailing_operations"},
}
# The four original completion strips (4727e4e0), the CC0 AOSM-IP strip and
# Makran Line's completion strip.
ART = {
    "sest-red-line/art/ribbons/sest_red_line_service.png": "a057977e528b620ab6bd17df47c75b2bca50b3748e5a301f676248e84f618cd4",
    "sest-southern-reach/art/ribbons/sest_southern_reach_service.png": "e7ff281a75e2cf01bc7c042d1999f3384f9159a71601db72e364a6763b03b1d0",
    "sest-southern-watch/art/ribbons/sest_southern_watch_service.png": "7714b93ac05e69756483c77b7a33141d2af794cf1d4c90fbf1811990acab90d4",
    "sest-sulu-line/art/ribbons/sest_sulu_line_service.png": "1259be4279650a72d650ae677c4b0fae78bc750c9607d676d957edece356ce69",
    "sest-southern-reach/art/ribbons/sest_aosm_indo_pacific.png": "89be086bb2b1b169f53ed29269d01505c950c60cda1fbdf0a86ed92e2423d5de",
    # Makran Line's completion strip, pinned when it was first drawn (11 Nov 2026).
    "sest-makran-line/art/ribbons/sest_makran_line_service.png": "ceca933ba1e81c8be901770366d5037776c4844a7e75a8267c42da5bd9ca9802",
}
DEVELOPER_WORDS = ("required native result", "Scenario qualification", "as a Australia", "as a US commander",
                   "SEST fictional-operation representation", "1985", "John Lehman", "no unrecorded")


def section(text, name):
    m = re.search(r"(?ms)^\[" + re.escape(name) + r"\][^\n]*\n(.*?)(?=^\[|\Z)", text)
    return dict((k.strip(), v) for k, v in re.findall(r"^([^=\n;#]+)=(.*)$", m[1], re.M)) if m else {}


def of_grade(grade):
    """NATO OF number from a ladder's grade: OF-4, or a US O-5 (OF-4)."""
    m = re.fullmatch(r"OF-(\d+)", grade)
    if m:
        return int(m[1])
    m = re.fullmatch(r"O-(\d+)", grade)
    if m:
        return max(1, int(m[1]) - 1)
    return 0                                        # OF-D, a midshipman


def stock_pictures():
    found, folder = set(), None
    for raw in STOCK_MEDIA.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\[(.+)\]\s+\d+ file", raw)
        if m:
            folder = m[1].replace("\\", "/")
        elif folder and raw.startswith("  ") and raw.strip():
            found.add(folder + "/" + raw.split()[0])
    return found


class CampaignServiceAwards(unittest.TestCase):
    def test_existing_ribbon_ids_and_definitions_are_preserved(self):
        before = "[TaskForceRibbons]\nRibbonIds=baltic_approaches\n\n[Ribbon_baltic_approaches]\nType=CampaignAward\nName_en=Existing\n"
        text = awards.commander_settings(before, "sest-southern-watch")
        self.assertIn("RibbonIds=baltic_approaches|sest_southern_watch_service", text)
        self.assertIn("[Ribbon_baltic_approaches]\nType=CampaignAward\nName_en=Existing", text)
        self.assertEqual(text, awards.commander_settings(text, "sest-southern-watch"))

    def test_unknown_campaign_remains_unchanged(self):
        self.assertIsNone(awards.award_id("third-party-campaign"))
        self.assertEqual(awards.commander_settings("existing\n", "third-party-campaign"), "existing\n")
        self.assertEqual(awards.mission_awards("third-party-campaign", {"code": "X1"}, True), [])

    def test_catalogue_preserves_pipe_and_comma_lists_without_duplicate_ids(self):
        for separators in ["|", ","]:
            text = awards.commander_settings("[TaskForceRibbons]\nRibbonIds=legacy_a" + separators + "legacy_b\n", "sest-southern-watch")
            ids = re.search(r"^RibbonIds=(.*)$", text, re.M)[1].split("|")
            self.assertEqual(ids[:2], ["legacy_a", "legacy_b"])
            self.assertEqual(len(ids), len(set(ids)))

    def test_new_national_options_keep_defaults_and_set_every_native_key(self):
        source = ("[CommanderSettings]\nCommanderNations=Australia\nCommanderDefaultNation=Australia\n"
                  "CommanderStartingRankLevel=5\nCommanderNameDefaultUS=Kept Name\n\n[OfficerRanks]\nAustralia=unchanged\n")
        text = awards.commander_settings(source, "sest-southern-watch")
        values = section(text, "CommanderSettings")
        self.assertEqual(values["CommanderNations"], "Australia|US|UK|Japan|NewZealand|France|Canada|"
                                                     "South_Korea|Spain|Italy|Germany|Netherlands|"
                                                     "Norway|Denmark")
        self.assertEqual(values["CommanderDefaultNation"], "Australia")
        self.assertEqual(values["CommanderStartingRankLevel"], "5")
        self.assertEqual(values["CommanderNameDefaultUS"], "Kept Name")     # never overwritten
        ranks = section(text, "OfficerRanks")
        self.assertEqual(ranks["Australia"], "unchanged")
        native = section(awards.NATIVE.read_text(encoding="utf-8-sig"), "OfficerRanks")
        self.assertEqual(ranks["US"], native["US"])
        self.assertEqual(ranks["Japan"], native["Japan"])
        self.assertEqual(ranks["UK"], awards.UK_RANKS)
        self.assertEqual(ranks["NewZealand"], awards.NEWZEALAND_RANKS)
        self.assertEqual(ranks["South_Korea"], awards.SOUTH_KOREA_RANKS)
        for nation in awards.NATIONS["sest-southern-watch"][1:]:
            for key in ("CommanderNameDefault", "CommanderNamePool", "NavyName", "NavyEmblem"):
                self.assertTrue(values.get(key + nation), key + nation)
        self.assertEqual(text, awards.commander_settings(text, "sest-southern-watch"))
        red = awards.commander_settings("[CommanderSettings]\nCommanderNations=China\n", "sest-red-line")
        self.assertIn("CommanderNations=China\n", red)
        # Sulu Line offers a Thai or Australian officer beside its Philippine
        # default; the Australian is the stock one, ladder and emblem.
        sulu = awards.commander_settings("[CommanderSettings]\nCommanderNations=Philippines\n", "sest-sulu-line")
        self.assertIn("CommanderNations=Philippines|Thailand|Australia\n", sulu)
        self.assertEqual(section(sulu, "OfficerRanks")["Australia"], native["Australia"])
        self.assertEqual(section(sulu, "CommanderSettings")["NavyEmblemAustralia"],
                         "ui/campaign/navy_emblems/ran_emblem.png")
        self.assertEqual(section(sulu, "OfficerRanks")["Thailand"], awards.THAILAND_RANKS)
        # Makran Line is a Pakistan Navy group with no partner navy: the
        # commander file offers Pakistan alone and adds no nation's rows.
        makran = awards.commander_settings("[CommanderSettings]\nCommanderNations=Pakistan\n",
                                           "sest-makran-line")
        self.assertIn("CommanderNations=Pakistan\n", makran)
        self.assertNotIn("[OfficerRanks]", makran)
        self.assertEqual(awards.describe("Pakistan"), "a Pakistani commander")
        self.assertEqual(awards.NATIONS["sest-makran-line"], ("Pakistan",))
        self.assertNotIn("sest-makran-line", awards.GRANTS)        # no real award until sourced

    def test_national_grants_use_native_id_nation_grammar(self):
        specs = awards.mission_awards("sest-southern-watch",
                                      {"num": "12", "key": "The First Ship Through", "date": (2028, 11, 28)}, True)
        self.assertEqual(specs[0], "sest_southern_watch_service")
        for expected in ("australian_distinguished_service_cross,Australia", "bronze_star_medal,US",
                         "uk_distinguished_service_order,UK", "jmsdf_first_class_commendation,Japan",
                         "australian_meritorious_unit_citation"):
            self.assertIn(expected, specs)
        joined = "|".join(specs)
        for gone in ("navy_unit_commendation", "navy_achievement_medal", "meritorious_unit_commendation,US"):
            self.assertNotIn(gone, joined)
        self.assertEqual(awards.mission_awards("sest-southern-watch", {"num": "05"}), ["sest_northern_lifeline"])

    def test_a_moved_or_renamed_mission_stops_the_build(self):
        with self.assertRaisesRegex(ValueError, "update MISSIONS"):
            awards.mission_awards("sest-southern-watch", {"num": "08", "key": "The Open Door", "date": (2028, 11, 14)})
        with self.assertRaisesRegex(ValueError, "update MISSIONS"):
            awards.mission_awards("sest-red-line", {"code": "RL05", "key": "The Quiet Side", "date": (2028, 12, 27)})
        with self.assertRaisesRegex(ValueError, "final mission"):
            awards.mission_awards("sest-sulu-line", {"code": "SL06"}, True)

    def test_service_medals_require_thirty_calendar_days(self):
        mission = {"code": "SR10", "key": "Southern Line", "date": (2029, 1, 6)}
        specs = awards.mission_awards("sest-southern-reach", mission)
        self.assertIn("sest_aosm_indo_pacific,Australia", specs)
        self.assertIn("armed_forces_expeditionary_medal,US", specs)
        start = date(*awards.MISSIONS["sest-southern-reach"][awards.FIRST["sest-southern-reach"]][1])
        self.assertGreaterEqual((date(2029, 1, 6) - start).days, 30)
        with self.assertRaisesRegex(ValueError, "30 campaign days"):
            awards.mission_awards("sest-southern-reach", {"code": "SR10", "date": (2028, 12, 20)})

    def test_preserved_final_mission_keeps_nation_qualified_specs(self):
        text = "[Mission1]\nTaskForceModeFinalMission=True\nTaskForceModeRibbonAwards=legacy_real,US|legacy_other,Australia\n"
        out = awards.final_mission_awards(text, "sest-southern-watch")
        self.assertIn("legacy_real,US|legacy_other,Australia|sest_southern_watch_service", out)
        self.assertEqual(out, awards.final_mission_awards(out, "sest-southern-watch"))

    def test_citations_are_two_plain_sentences(self):
        for slug in awards.CAMPAIGNS:
            for rid, row in awards.catalogue(slug).items():
                with self.subTest(campaign=slug, award=rid):
                    text = row["citation"]
                    note = awards.FICTIONAL if row["reference"] == "Fictional" else awards.REAL_NOTE
                    self.assertTrue(text.endswith(" " + note), text)
                    first = text[:-len(note) - 1]
                    self.assertTrue(first.startswith("For ") and first.endswith("."), first)
                    self.assertEqual(first.count(". "), 0, first)
                    for word in DEVELOPER_WORDS:
                        self.assertNotIn(word, text)
                    if row["type"] == "UnitAward":
                        self.assertEqual(row["recipient"], "unit")
                        self.assertIn("by {TaskForceName}", first)
        text = awards.commander_settings("[CommanderSettings]\nCommanderNations=Australia\n", "sest-southern-reach")
        self.assertIn("CitationRecipient_en={TaskForceName}", text)
        self.assertIn("CitationIssuance_en=records the award of the", text)
        self.assertEqual(awards.describe("Australia"), "an Australian commander")
        self.assertEqual(awards.describe("US"), "an American commander")

    def test_rl05_names_under_the_convergence(self):
        row = awards.catalogue("sest-red-line")["sest_undersea_operations"]
        self.assertIn("Under the Convergence", row["citation"])
        self.assertNotIn("Quiet Side", row["citation"])

    def test_milestones_have_distinct_names_and_centres(self):
        names, centres = set(), set()
        for slug, rows in awards.MILESTONES.items():
            service = awards.CAMPAIGNS[slug]
            for code, (rid, name, why, stripes) in rows.items():
                self.assertNotIn(name, names)
                self.assertNotIn("Lifeline", name)          # the SW subtitle and SW09's title
                names.add(name)
                centre = stripes[len(stripes) // 2][0]
                self.assertNotEqual(centre, service[3][len(service[3]) // 2], rid)
                self.assertNotIn(centre, centres, rid)
                centres.add(centre)
                self.assertIn(awards.MISSIONS[slug][code][0], why, rid)

    def test_each_grant_is_one_mission_and_an_offered_nation(self):
        for slug in awards.CAMPAIGNS:
            catalogue = awards.catalogue(slug)
            for rid, code in awards.grants(slug).items():
                self.assertIn(rid, catalogue)
                self.assertIn(code, awards.MISSIONS[slug])
                nation = awards.REAL.get(rid, {}).get("nation")
                if nation:
                    self.assertIn(nation, awards.NATIONS[slug], rid)
            self.assertFalse(set(awards.grants(slug)) & set(awards.RETIRED), slug)

    def test_canada_and_new_zealand_awards_follow_the_other_nations(self):
        # 10 Nov 2026: a lesser decoration at SW08 and SR12, the senior one at
        # SW12 and TS09, the operational service medal at SR10.
        expected = {
            "sest-southern-watch": {"ca_meritorious_service_medal_military": "SW08",
                                    "nz_distinguished_service_decoration": "SW08",
                                    "ca_meritorious_service_cross_military": "SW12",
                                    "nz_member_order_of_merit": "SW12"},
            "sest-southern-reach": {"ca_general_campaign_star_expedition": "SR10",
                                    "nz_operational_service_medal": "SR10",
                                    "ca_meritorious_service_medal_military": "SR12",
                                    "nz_distinguished_service_decoration": "SR12",
                                    "ca_meritorious_service_cross_military": "TS09",
                                    "nz_member_order_of_merit": "TS09"},
        }
        for slug, rows in expected.items():
            granted = awards.grants(slug)
            for rid, code in rows.items():
                self.assertEqual(granted[rid], code, (slug, rid))
        specs = awards.mission_awards("sest-southern-reach", {"code": "SR10", "key": "Southern Line",
                                                              "date": (2029, 1, 6)})
        self.assertIn("ca_general_campaign_star_expedition,Canada", specs)
        self.assertIn("nz_operational_service_medal,NewZealand", specs)
        self.assertEqual(awards.REAL["ca_general_campaign_star_expedition"]["service_days"], 14)
        self.assertEqual(awards.REAL["nz_operational_service_medal"]["service_days"], 7)
        # Official GCS-EXPEDITION widths: red 8, white 2, light grey 12, from
        # the DND medal page, which is its source (the owner's researcher
        # read it on 10 Nov 2026), with the 14-day rule.
        gcs_row = awards.REAL["ca_general_campaign_star_expedition"]
        self.assertEqual([w for _c, w in gcs_row["art"]], [8, 2, 12, 2, 8])
        self.assertEqual(gcs_row["source"], "https://www.canada.ca/en/department-national-defence/services/"
                                            "medals/medals-chart-index/general-campaign-star-expedition-gcs-exp.html")
        self.assertIn("widths as specified by Canada (DND medal page); colours sampled from a Commons image",
                      " ".join(awards.sources_text("sest-southern-reach").split()))
        for slug in ("sest-southern-watch", "sest-southern-reach"):
            catalogue = awards.catalogue(slug)
            text = awards.sources_text(slug)
            for rid in expected[slug]:
                row = catalogue[rid]
                with self.subTest(campaign=slug, award=rid):
                    self.assertEqual(row["reference"], awards.REAL[rid]["nation"])
                    self.assertTrue(row["source"].startswith("https://"))
                    self.assertAlmostEqual(sum(w for _c, w in row["stripes"]),
                                           1 if len(row["stripes"]) == 1 else 32, places=1)
                    self.assertIn(rid, awards.ART_NOTES)
                    self.assertIn(f"{rid}.png - {row['name']}", text)
            if slug == "sest-southern-reach":
                gcs = catalogue["ca_general_campaign_star_expedition"]["citation"]
                self.assertTrue(gcs.startswith("For 14 days of service in the presence of an armed "
                                               "enemy with {TaskForceName}"), gcs)
                # No real designated or specified theatre is claimed.
                self.assertNotRegex(gcs, r"(?i)designated|specified|theatre|operation [A-Z]")
        self.assertIn("proportions measured from an image", awards.sources_text("sest-southern-watch"))
        self.assertIn("approved\n12 January 2025", awards.sources_text("sest-southern-reach"))
        for slug in awards.CAMPAIGNS:
            self.assertFalse({"nz_antarctic_medal", "nz_officer_order_of_merit"} & set(awards.grants(slug)))

    def test_french_korean_spanish_german_and_danish_awards(self):
        # 10 Nov 2026, second pass: the same pattern, from verified sources.
        # Italy, the Netherlands and Norway stay on the fictional ribbons.
        lesser = {"France": "fr_chevalier_ordre_national_du_merite",
                  "South_Korea": "kr_national_security_medal",
                  "Spain": "es_cruz_merito_naval_distintivo_blanco",
                  "Germany": "de_ehrenkreuz_der_bundeswehr_gold",
                  "Denmark": "dk_defence_medal_meritorious_service"}
        senior = {"France": "fr_chevalier_legion_d_honneur",
                  "South_Korea": "kr_order_of_national_security_merit_samil",
                  "Spain": "es_cruz_merito_naval_distintivo_rojo",
                  "Germany": "de_verdienstkreuz_am_bande",
                  "Denmark": "dk_defence_medal_excellent_service"}
        service = {"Spain": "es_medalla_de_campana", "Germany": "de_einsatzmedaille_bundeswehr_bronze"}
        watch, reach = awards.grants("sest-southern-watch"), awards.grants("sest-southern-reach")
        for nation in lesser:
            with self.subTest(nation=nation):
                self.assertEqual((watch[lesser[nation]], watch[senior[nation]]), ("SW08", "SW12"))
                self.assertEqual((reach[lesser[nation]], reach[senior[nation]]), ("SR12", "TS09"))
                for rid in (lesser[nation], senior[nation], service.get(nation)):
                    if rid:
                        self.assertEqual(awards.REAL[rid]["nation"], nation)
                        self.assertIn(rid, awards.ART_NOTES)
        for nation, rid in service.items():
            self.assertEqual(reach[rid], "SR10")
            self.assertNotIn(rid, watch)
            self.assertEqual(awards.REAL[rid]["service_days"], 30)
            # No real named operation or designated theatre is claimed.
            self.assertNotRegex(awards.REAL[rid]["merit"], r"(?i:designated|specified|theatre)|[Oo]peration [A-Z]")
        for slug in ("sest-southern-watch", "sest-southern-reach"):
            nations, _unit = awards.award_nations(slug)
            self.assertEqual(set(awards.NATIONS[slug]) - set(nations), {"Italy", "Netherlands", "Norway"})
        # Widths as the sources give them: Spain's 30 mm and Korea's 38 mm
        # ribbons in millimetres, the drawing-measured ones scaled to 32.
        width = lambda rid: round(sum(w for _c, w in awards.REAL[rid]["art"]), 3)
        for rid in ("es_cruz_merito_naval_distintivo_blanco", "es_cruz_merito_naval_distintivo_rojo",
                    "es_medalla_de_campana"):
            self.assertEqual(width(rid), 30, rid)
        for rid in ("kr_national_security_medal", "kr_order_of_national_security_merit_samil"):
            self.assertEqual(width(rid), 38, rid)
            self.assertEqual(awards.REAL[rid]["device"], "taegeuk")
            self.assertIn(("#FFFFFF", 3 if "medal" in rid else 1.5), awards.REAL[rid]["art"])
        for rid in ("de_ehrenkreuz_der_bundeswehr_gold", "de_verdienstkreuz_am_bande",
                    "de_einsatzmedaille_bundeswehr_bronze", "dk_defence_medal_meritorious_service",
                    "dk_defence_medal_excellent_service"):
            self.assertAlmostEqual(width(rid), 32, places=1, msg=rid)
        self.assertEqual([c for c, _w in awards.REAL["es_cruz_merito_naval_distintivo_rojo"]["art"]],
                         ["#AF0B19", "#FCBD00", "#AF0B19"])
        self.assertEqual(awards.REAL["es_cruz_merito_naval_distintivo_rojo"]["art"][1][1], 3.75)
        self.assertEqual(awards.REAL["fr_chevalier_legion_d_honneur"]["art"], (("#AD1710", 1),))
        # Denmark's meritorious ribbon has red edges, not white.
        self.assertEqual(awards.REAL["dk_defence_medal_meritorious_service"]["art"][0][0], "#C02020")
        self.assertEqual(awards.REAL["de_ehrenkreuz_der_bundeswehr_gold"]["device"], "gold_cross")
        text = " ".join(awards.sources_text("sest-southern-reach").split())
        self.assertIn("drawn without the operation's silver rectangle, as the operation is fictional", text)
        self.assertIn("drawn without the clasp, as the deployment is fictional", text)
        self.assertIn("measured from a public-domain drawing (Wikimedia Commons)", text)

    def test_every_offered_nation_is_a_game_key_with_settings_and_a_ladder(self):
        # The discount and the award selectors compare the key with the
        # units' Nation=, so it must be the game's own (nations.ini), and a
        # nation the campaign's own text does not define needs a row.
        keys = {line.partition("=")[0].strip() for line in NATION_KEYS.read_text(
            encoding="utf-8-sig").splitlines() if "=" in line}
        for slug, nations in awards.NATIONS.items():
            for nation in nations:
                with self.subTest(campaign=slug, nation=nation):
                    self.assertIn(nation, keys)
                    self.assertIn(nation, awards.ADJECTIVE)
                    self.assertFalse(awards.describe(nation).startswith(("a A", "a E", "a I", "a O", "an B")))
        for nation, row in awards.NATION_SETTINGS.items():
            with self.subTest(nation=nation):
                if row["ranks"] is None:
                    continue
                ranks = [r.split(",") for r in row["ranks"].split("|")]
                self.assertEqual(len(ranks), 10)
                self.assertTrue(all(len(r) == 5 and r[4] == "" for r in ranks))
                levels = {int(r[3]): r[2] for r in ranks}
                self.assertEqual(sorted(levels), list(range(1, 11)))
                self.assertEqual((levels[5], levels[6], levels[7]), ("OF-4", "OF-5", "OF-6"))
                # Latin-1 accents only: the game font has no Hangul or Thai.
                for text in (row["ranks"], row["navy"], row["name"]):
                    self.assertTrue(all(ord(c) < 256 for c in text), text)

    def test_sest_emblems_are_registered_and_credited(self):
        sys.path.insert(0, str(ROOT / "integration/campaign"))
        import build_pack as bp
        credits = (ROOT / "integration/gallery/source/VISUAL_CREDITS.txt").read_text(encoding="utf-8")
        rows = [(nation, row["emblem"].rsplit("/", 1)[1], row)
                for nation, row in awards.NATION_SETTINGS.items()]
        # The campaigns' own emblems (Sulu Line's Philippine Navy, Red Line's
        # PLA Navy) are credited the same way.
        rows += [(name, name, row) for name, row in awards.CAMPAIGN_EMBLEMS.items()]
        for nation, name, row in rows:
            if not name.startswith("sest_"):
                self.assertIn(row["emblem"], STOCK_EMBLEMS, nation)
                continue
            with self.subTest(nation=nation):
                self.assertIn(name, bp.SEST_EMBLEMS)
                flag = bp.SEST_EMBLEMS[name]
                self.assertTrue((ROOT / "integration/gallery/source/visuals/flags/png" / flag).is_file())
                entry = re.search(r"^visuals/flags/source/" + re.escape(flag.rsplit(".", 1)[0])
                                  + r"\.(?:svg|png)\n(File:[^\n]+)\n(?:.*\n){2}Licence: Public domain",
                                  credits, re.M)
                self.assertTrue(entry, flag)
                self.assertEqual(entry[1], row["commons"])
        for slug in ("sest-southern-watch", "sest-southern-reach", "sest-sulu-line"):
            text = awards.sources_text(slug)
            for nation in awards.NATIONS[slug]:
                row = awards.NATION_SETTINGS.get(nation, {})
                if row.get("commons"):
                    self.assertIn(row["emblem"].rsplit("/", 1)[1], text)
                    self.assertIn("Source: " + row["commons"], text)
        # Where the file is a national flag and the navy's ensign is not, the
        # SOURCES text says so.
        for nation in ("Germany", "Norway", "Denmark", "Thailand"):
            self.assertIn("gallery set has no file for it", awards.NATION_SETTINGS[nation]["about"])

    def test_sest_name_pools_add_to_the_stock_pools_and_replace_none(self):
        stock = set(re.findall(r"^\[(Names_\w+)\]", UI.read_text(encoding="utf-8-sig"), re.M))
        text = awards.name_pools_text()
        sections = re.findall(r"^\[(\w+)\]$", text, re.M)
        self.assertEqual(sections, list(awards.NAME_POOLS))
        self.assertFalse(set(sections) & stock)
        for pool, lists in awards.NAME_POOLS.items():
            with self.subTest(pool=pool):
                for key, value in zip(("FirstNames", "MiddleNames", "LastNames"), lists):
                    self.assertIn(f"{key}={value}\n", text)
                    names = value.split(",")
                    if value != "_":
                        self.assertEqual(len(names), 50, key)
                    self.assertEqual(len(names), len(set(names)), key)
                    self.assertTrue(value.isascii() and " " not in value, key)
        for nation, row in awards.NATION_SETTINGS.items():
            self.assertTrue(row["pool"] in stock or row["pool"] in awards.NAME_POOLS, nation)
            # A SEST pool's default name reads as the pool builds one: given
            # name first, surname last ('Seongjin Han', as stock's 'Hiroshi
            # Watanabe'), so randomising does not flip the order.
            if row["pool"] in awards.NAME_POOLS:
                first, _middle, last = (v.split(",") for v in awards.NAME_POOLS[row["pool"]])
                words = row["name"].split()
                with self.subTest(nation=nation, name=row["name"]):
                    self.assertIn(words[0], first)
                    self.assertIn(words[-1], last)
        self.assertEqual(awards.NATION_SETTINGS["South_Korea"]["name"], "Seongjin Han")
        self.assertEqual(awards.unknown_pools("CommanderNamePoolX=Names_Nowhere\nCommanderNamePoolY=Names_UK\n"
                                              "CommanderNamePoolZ=Names_Thailand\n"), ["Names_Nowhere"])
        saved = dict(awards.NAME_POOLS)
        try:
            awards.NAME_POOLS["Names_Australia"] = ("A", "_", "B")
            with self.assertRaisesRegex(ValueError, "stock pool"):
                awards.name_pools_text()
        finally:
            awards.NAME_POOLS.clear()
            awards.NAME_POOLS.update(saved)


class BuiltCampaigns(unittest.TestCase):
    """What the builder wrote, read the way the game reads it."""

    @classmethod
    def setUpClass(cls):
        cls.campaigns = {}
        for slug in awards.CAMPAIGNS:
            folder = PACK / "campaigns" / slug
            text = (folder / "campaign.ini").read_text(encoding="utf-8")
            missions = {}
            for m in re.finditer(r"(?ms)^\[(Mission\d+)\][ \t]*#(\S+) ([^\n]*)\n(.*?)(?=^\[|\Z)", text):
                code = m[2] if not m[2][0].isdigit() else "SW" + m[2]
                missions[m[1]] = dict(code=code, title=m[3].strip(), body=m[4])
            cls.campaigns[slug] = dict(folder=folder, missions=missions,
                                       commander=(folder / "commander_settings.ini").read_text(encoding="utf-8"))

    def granted(self, slug):
        """[(mission, award id, selectors)] as the native parser splits them."""
        out = []
        for mission in self.campaigns[slug]["missions"].values():
            m = re.search(r"^TaskForceModeRibbonAwards=(.*)$", mission["body"], re.M)
            for spec in (m[1].split("|") if m else []):
                fields = [f.strip() for f in spec.split(",") if f.strip()]
                out.append((mission, fields[0].split(":")[0], fields[1:]))
        return out

    def mission_date(self, slug, mission):
        path = re.search(r"^MissionFile=(.*)$", mission["body"], re.M)[1].strip()
        y, mo, d = (int(x) for x in re.search(r"^Date=(\d+),(\d+),(\d+)", (PACK / path).read_text(
            encoding="utf-8", errors="replace"), re.M).groups())
        return date(y, mo, d)

    def test_every_awarded_id_has_a_section_and_a_picture(self):
        stock = stock_pictures()
        for slug in awards.CAMPAIGNS:
            commander = self.campaigns[slug]["commander"]
            listed = section(commander, "TaskForceRibbons")["RibbonIds"].split("|")
            for mission, rid, _nations in self.granted(slug):
                with self.subTest(campaign=slug, award=rid):
                    row = section(commander, "Ribbon_" + rid)
                    self.assertTrue(row, "no Ribbon_ section")
                    self.assertIn(rid, listed)
                    for key in ("ImagePath", "MedalImagePath"):
                        path = row.get(key)
                        if not path:
                            continue
                        if path.startswith("campaigns/pacific-strike-task-force/"):
                            self.assertIn(path, stock, "not an installed Sea Power picture")
                        else:
                            self.assertTrue((PACK / path).is_file(), path)
            ids = [r for _m, r, _n in self.granted(slug)]
            self.assertEqual(len(ids), len(set(ids)), f"{slug}: an award is granted twice")

    def test_every_selector_is_an_offered_nation_with_native_settings(self):
        # A pool is the game's (ui.ini) or one the pack adds (sest_name_pools.ini).
        ui = UI.read_text(encoding="utf-8-sig") + (PACK / awards.NAME_POOL_FILE).read_text(encoding="utf-8")
        for slug in awards.CAMPAIGNS:
            commander = self.campaigns[slug]["commander"]
            values = section(commander, "CommanderSettings")
            offered = values["CommanderNations"].split("|")
            self.assertEqual(tuple(offered), awards.NATIONS[slug])
            self.assertEqual(values["CommanderDefaultNation"], offered[0])
            level = int(values["CommanderStartingRankLevel"])
            for nation in offered:
                with self.subTest(campaign=slug, nation=nation):
                    self.assertTrue(values.get("CommanderNameDefault" + nation))
                    self.assertIn("[" + values["CommanderNamePool" + nation] + "]", ui)
                    self.assertTrue(values.get("NavyName" + nation))
                    emblem = values["NavyEmblem" + nation]
                    self.assertTrue(emblem in STOCK_EMBLEMS or (PACK / emblem).is_file(), emblem)
                    ladder = section(commander, "OfficerRanks")[nation].split("|")
                    ranks = [r.split(",") for r in ladder]
                    self.assertTrue(all(len(r) == 5 for r in ranks), nation)
                    self.assertIn(str(level), [r[3] for r in ranks])
            for _mission, rid, nations in self.granted(slug):
                for nation in nations:
                    self.assertIn(nation, offered, f"{slug}: {rid},{nation}")

    def test_the_pack_ships_the_sest_name_pools_for_the_dist(self):
        built = (PACK / awards.NAME_POOL_FILE).read_text(encoding="utf-8")
        self.assertEqual(built, awards.name_pools_text())
        # The consolidator stages every file of every integration/*/SEST_*
        # pack; a path only one pack ships is carried into the dist as it
        # is. No other pack ships it, or any [Names_X] section a language
        # merge could set against it.
        spec = importlib.util.spec_from_file_location("consolidate_packs", ROOT / "tools/consolidate_packs.py")
        consolidate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(consolidate)
        packs = consolidate.source_packs()
        self.assertIn(PACK, packs)
        owners = [p for p in packs if (p / awards.NAME_POOL_FILE).is_file()]
        self.assertEqual(owners, [PACK])
        for pack in packs:
            for f in pack.glob("language_*/*.ini"):
                if f != PACK / awards.NAME_POOL_FILE:
                    self.assertNotRegex(f.read_text(encoding="utf-8", errors="replace"), r"(?m)^\[Names_",
                                        f)
        staged = {"ui/campaign/navy_emblems/sest_rn_emblem.png": b"", awards.NAME_POOL_FILE: b""}
        credits = consolidate.credits_text(staged)
        self.assertIn("sest_rn_emblem.png", credits)
        self.assertIn(awards.NAME_POOL_FILE, credits)

    def test_each_citation_names_its_mission_and_date(self):
        for slug in awards.CAMPAIGNS:
            commander = self.campaigns[slug]["commander"]
            for mission, rid, _nations in self.granted(slug):
                with self.subTest(campaign=slug, award=rid):
                    row = section(commander, "Ribbon_" + rid)
                    self.assertIn(mission["title"], row["CitationText_en"])
                    when = self.mission_date(slug, mission)
                    self.assertEqual(row["CitationDate_en"], f"{when.day} {when.strftime('%B')} {when.year}")
                    for word in DEVELOPER_WORDS:
                        self.assertNotIn(word, row["CitationText_en"])
            # Definitions kept for earlier records carry a date too.
            for rid in re.findall(r"^\[Ribbon_(\w+)\]", commander, re.M):
                self.assertTrue(section(commander, "Ribbon_" + rid).get("CitationDate_en"), rid)

    def test_personal_awards_respect_the_rank_limits(self):
        for slug in awards.CAMPAIGNS:
            commander = self.campaigns[slug]["commander"]
            level = section(commander, "CommanderSettings")["CommanderStartingRankLevel"]
            ladders = section(commander, "OfficerRanks")
            for _mission, rid, nations in self.granted(slug):
                row = awards.REAL.get(rid)
                if not row or row["type"] == "UnitAward":
                    continue
                self.assertEqual(nations, [row["nation"]], rid)
                rank = next(r.split(",") for r in ladders[row["nation"]].split("|") if r.split(",")[3] == level)
                low, high = row["ranks"]
                with self.subTest(campaign=slug, award=rid, rank=rank[0]):
                    self.assertTrue(low <= of_grade(rank[2]) <= high, f"{rank[0]} {rank[2]} outside OF-{low}..OF-{high}")
            granted = {r for _m, r, _n in self.granted(slug)}
            self.assertNotIn("navy_achievement_medal", granted)      # O-4 and below only

    def test_rules_pages_state_the_discount_for_every_nation(self):
        sys.path.insert(0, str(ROOT / "integration/campaign"))
        import build_pack as bp
        for slug in awards.CAMPAIGNS:
            folder = self.campaigns[slug]["folder"]
            page = (folder / "campaign_rules_en.xml").read_text(encoding="utf-8")
            roster = []
            for raw in (folder / "player_task_force_roster.ini").read_text(encoding="utf-8").splitlines():
                # Unit ids may carry an apostrophe (fr_fdi_amiral_ronarc'h).
                m = re.match(r"^([^;\[\s=]+)=([^|]+)\|\d+", raw)
                if m:
                    roster.append(dict(unit=m[1], picks=m[2].split(",")))
            counts = {}
            for nation in bp.roster_nations(roster).values():
                counts[nation.lower()] = counts.get(nation.lower(), 0) + 1
            offered = awards.NATIONS[slug]
            with self.subTest(campaign=slug):
                self.assertIn("Unrestricted mode", page)
                if len(offered) == 1:
                    self.assertIn("The commander's nation is fixed.", page)
                    continue
                self.assertNotIn("The commander's nation is fixed.", page)
                self.assertNotIn("without the same-nation discount", page)
                self.assertIn("The discount follows the commander's nation", page)
                for nation in offered:
                    name = bp.nation_name(nation)
                    name = ("the " if name in ("USA", "United Kingdom", "Netherlands", "Philippines")
                            else "") + name
                    adjective, article = awards.ADJECTIVE[nation]
                    count = counts.get(nation.lower(), 0)
                    # One class reads singular, in a word (Norway's Skjold,
                    # Denmark's Iver Huitfeldt, New Zealand's P-8A); none says
                    # so.
                    words = "one" if count == 1 else str(count)
                    self.assertIn(f"the {words} class{'es' if count != 1 else ''} registered to {name} "
                                  f"for {article} {adjective} commander" if count else
                                  f"no class for {article} {adjective} commander (none is registered "
                                  f"to {name})", page)
                self.assertNotRegex(page, r"\bthe 1 class\b")
                # Every offered nation is named once in the awards sentence:
                # with its own nation's awards, or with the fictional ribbons
                # and the host's unit award only.
                awarded, unit = awards.award_nations(slug)
                m = re.search(r"commander can receive\. (.*?)(?: commanders? receives? their own "
                              r"nation's awards| awards go to an? [\w ]+ commander only); (.*?) "
                              r"commanders? receives? the fictional ribbons and the group's (.*?) only\.",
                              page)
                self.assertTrue(m, slug)
                rest = [n for n in offered if n not in awarded]
                self.assertEqual(re.split(r", | and ", m[1]), [awards.ADJECTIVE[n][0] for n in awarded])
                self.assertEqual(re.split(r", | and ", m[2]), [awards.ADJECTIVE[n][0] for n in rest])
                self.assertEqual(m[3], " and ".join(unit))

    def test_sources_credit_every_sest_emblem_the_commander_file_names(self):
        # Review of 10 Nov 2026: SOURCES.txt listed only the NATION_SETTINGS
        # emblems, so Sulu Line's default sest_pn_emblem.png (philippines.png)
        # and Red Line's sest_plan_emblem.png (china_naval.png) were missing.
        sys.path.insert(0, str(ROOT / "integration/campaign"))
        import build_pack as bp
        credits = (ROOT / "integration/gallery/source/VISUAL_CREDITS.txt").read_text(encoding="utf-8")
        for slug in awards.CAMPAIGNS:
            commander = self.campaigns[slug]["commander"]
            sources = (self.campaigns[slug]["folder"] / "art/ribbons/SOURCES.txt").read_text(encoding="utf-8")
            values = section(commander, "CommanderSettings")
            named = [(k[len("NavyEmblem"):], v.rsplit("/", 1)[1]) for k, v in values.items()
                     if k.startswith("NavyEmblem") and v.rsplit("/", 1)[1].startswith("sest_")]
            self.assertTrue(named, slug)
            with self.subTest(campaign=slug):
                self.assertEqual(sources, awards.sources_text(slug, commander))
                for nation, name in named:
                    flag = bp.SEST_EMBLEMS[name].rsplit(".", 1)[0]
                    commons = re.search(r"^visuals/flags/source/" + re.escape(flag) + r"\.(?:svg|png)\n(File:[^\n]+)\n",
                                        credits, re.M)[1]
                    entry = re.search(r"^  " + re.escape(name) + r" - ([^:]+):(?:.*\n)*?    Source: (File:[^\n]+)$",
                                      sources, re.M)
                    self.assertTrue(entry, name)
                    self.assertEqual(entry[1], values["NavyName" + nation])
                    self.assertEqual(entry[2], commons, name)
        self.assertIn("sest_pn_emblem.png - Philippine Navy:",
                      (self.campaigns["sest-sulu-line"]["folder"] / "art/ribbons/SOURCES.txt").read_text(encoding="utf-8"))
        self.assertIn("sest_plan_emblem.png - People's Liberation Army Navy:",
                      (self.campaigns["sest-red-line"]["folder"] / "art/ribbons/SOURCES.txt").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "credits"):
            awards.emblem_credits("sest-red-line", "[CommanderSettings]\nCommanderNations=China\n"
                                                   "NavyEmblemChina=ui/campaign/navy_emblems/sest_nowhere.png\n")

    def test_the_builder_reproduces_the_commander_files(self):
        sys.path.insert(0, str(ROOT / "integration/campaign"))
        import build_pack as bp
        for spec in bp.campaign_specs():
            slug = spec["SLUG"]
            once = awards.commander_settings(spec["COMMANDER"], slug)
            with self.subTest(campaign=slug):
                self.assertEqual(once, self.campaigns[slug]["commander"])
                self.assertEqual(once, awards.commander_settings(once, slug))

    def test_shipped_ids_flags_and_art_are_preserved(self):
        for slug, ids in SHIPPED.items():
            commander = self.campaigns[slug]["commander"]
            for rid in ids:
                self.assertIn(f"[Ribbon_{rid}]", commander, f"{slug}: {rid}")
            final = [(m, r) for m, r, _n in self.granted(slug) if r == awards.award_id(slug)]
            self.assertEqual(len(final), 1, slug)
            self.assertIn("TaskForceModeFinalMission=True", final[0][0]["body"])
            self.assertIn("ReferenceSource=Fictional", commander)
        for rel, digest in ART.items():
            data = (PACK / "campaigns" / rel).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest, rel)

    def test_code_drawn_strips_are_native_size(self):
        from PIL import Image
        for slug in awards.CAMPAIGNS:
            for rid, row in awards.catalogue(slug).items():
                if not row.get("stripes"):
                    continue
                with Image.open(PACK / "campaigns" / slug / "art/ribbons" / (rid + ".png")) as image:
                    self.assertEqual(image.size, (140, 36), rid)
                    self.assertEqual(image.getpixel((20, 18))[3], 255, rid)
            sources = (PACK / "campaigns" / slug / "art/ribbons/SOURCES.txt").read_text(encoding="utf-8")
            self.assertEqual("Nford24" in sources, slug == "sest-southern-reach", slug)


if __name__ == "__main__":
    unittest.main()
