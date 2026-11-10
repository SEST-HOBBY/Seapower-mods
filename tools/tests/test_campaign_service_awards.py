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
}
# The four original completion strips (4727e4e0) and the CC0 AOSM-IP strip.
ART = {
    "sest-red-line/art/ribbons/sest_red_line_service.png": "a057977e528b620ab6bd17df47c75b2bca50b3748e5a301f676248e84f618cd4",
    "sest-southern-reach/art/ribbons/sest_southern_reach_service.png": "e7ff281a75e2cf01bc7c042d1999f3384f9159a71601db72e364a6763b03b1d0",
    "sest-southern-watch/art/ribbons/sest_southern_watch_service.png": "7714b93ac05e69756483c77b7a33141d2af794cf1d4c90fbf1811990acab90d4",
    "sest-sulu-line/art/ribbons/sest_sulu_line_service.png": "1259be4279650a72d650ae677c4b0fae78bc750c9607d676d957edece356ce69",
    "sest-southern-reach/art/ribbons/sest_aosm_indo_pacific.png": "89be086bb2b1b169f53ed29269d01505c950c60cda1fbdf0a86ed92e2423d5de",
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
        self.assertEqual(values["CommanderNations"], "Australia|US|UK|Japan")
        self.assertEqual(values["CommanderDefaultNation"], "Australia")
        self.assertEqual(values["CommanderStartingRankLevel"], "5")
        self.assertEqual(values["CommanderNameDefaultUS"], "Kept Name")     # never overwritten
        ranks = section(text, "OfficerRanks")
        self.assertEqual(ranks["Australia"], "unchanged")
        native = section(awards.NATIVE.read_text(encoding="utf-8-sig"), "OfficerRanks")
        self.assertEqual(ranks["US"], native["US"])
        self.assertEqual(ranks["Japan"], native["Japan"])
        self.assertEqual(ranks["UK"], awards.UK_RANKS)
        for nation in ("US", "UK", "Japan"):
            for key in ("CommanderNameDefault", "CommanderNamePool", "NavyName", "NavyEmblem"):
                self.assertTrue(values.get(key + nation), key + nation)
        self.assertEqual(text, awards.commander_settings(text, "sest-southern-watch"))
        red = awards.commander_settings("[CommanderSettings]\nCommanderNations=China\n", "sest-red-line")
        self.assertIn("CommanderNations=China\n", red)
        sulu = awards.commander_settings("[CommanderSettings]\nCommanderNations=Philippines\n", "sest-sulu-line")
        self.assertIn("CommanderNations=Philippines\n", sulu)

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
        ui = UI.read_text(encoding="utf-8-sig")
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
                m = re.match(r"^([A-Za-z0-9_\-]+)=([^|]+)\|\d+", raw)
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
                    name = ("the " if name in ("USA", "United Kingdom", "Netherlands") else "") + name
                    adjective, article = awards.ADJECTIVE[nation]
                    self.assertIn(f"the {counts[nation.lower()]} classes registered to {name} "
                                  f"for {article} {adjective} commander", page)

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
