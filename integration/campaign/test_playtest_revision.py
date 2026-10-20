"""Regressions from the PC report, checked against the built collection."""
import copy
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pack as b
from mission_depth import UAV_SITES, code_of


class PlaytestRevision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = b.campaign_specs()
        cls.missions = {code_of(m): m for s in cls.specs for m in s["MISSIONS"]}

    def placed(self, code):
        m = copy.deepcopy(self.missions[code])
        p, members, _credits, _far = b.place(m, b.CoastPlacer(b.coast_data(m), m))
        return m, p, members

    def test_roosevelt_uses_available_us_squadrons_and_growlers(self):
        carrier = next(u for u in self.missions["SW08"]["units"] if u["type"] == "usn_cvn_nimitz_2025")
        for uid, sq, n in carrier["air_group"]:
            self.assertIn(sq, b.squadrons(uid))
            self.assertEqual(b.pick_nation(uid, sq), "US", (uid, sq))
        self.assertEqual(next(n for uid, sq, n in carrier["air_group"] if uid == "usn_ea-18g"), 6)
        self.assertEqual(carrier["ready"][0][3], 2)
        self.assertLessEqual(sum(n for uid, sq, n in carrier["air_group"]), b.deck_size(carrier["type"]))

    def test_strike_swap_and_damage_dependencies(self):
        door, ring = self.missions["SW08"], self.missions["SWO7"]
        bombers = [u for u in door["units"] if u["type"] == "dts_b-52h"]
        self.assertEqual(len(bombers), 2)
        self.assertTrue(all(u["loadout"] == "Strike183" for u in bombers))
        jets = [u for u in ring["units"] if u["type"] == "raaf_f-35a"]
        self.assertEqual(len(jets), 4)
        self.assertTrue(all(u["loadout"] == "StrikeLongRangeStealth" for u in jets))
        self.assertFalse(any(u["type"] == "dts_b-52h" for u in ring["units"]))
        declared = set(door["declares"])
        for u in ring["units"]:
            if u.get("spawn_if", ("",))[0].startswith("SW08"):
                self.assertIn(u["spawn_if"][0], declared)
        self.assertLess(door["date"], ring["date"])
        for code in ("SW08", "SWO7"):
            m, p, members = self.placed(code)
            _name, text = b.render(m, p, members)
            if code == "SW08":
                self.assertIn("Action_VariableSet=SW08MainFieldLost,True", text)
            else:
                self.assertIn("SpawnByVariableAND=SW08MainFieldLost,IsFalse", text)

    def test_collins_is_surfaced_retained_and_service_speed_is_real(self):
        m, p, members = self.placed("SW09")
        b.mark_supplied(m, p)
        _tag, k, _name, _x = p["Taskforce1Submarine"][0]
        self.assertEqual(k["Type"], "ran_ssg_collins")
        self.assertEqual(k["RelativePositionInNM"].split(",")[1], "0")
        self.assertEqual(k["Telegraph"], 2)
        self.assertEqual(k["TaskForceModeIgnoreUnit"], "True")
        tender = next(v for t, v, n, x in p["Taskforce1Vessel"] if v["Type"] == "ran_aor_supply")
        a, c = b.unit_spot(k), b.unit_spot(tender)
        self.assertLess(((a[0]-c[0])**2 + (a[1]-c[1])**2)**.5, .5)
        for uid in ("ran_ssg_collins", "ran_aor_supply"):
            values = b.unit_value(uid, "TelegraphVelocities").split(",")
            self.assertEqual(float(values[3]), 4)

    def test_uav_sections_have_finite_fuel_and_local_recovery(self):
        for code in UAV_SITES:
            with self.subTest(code=code):
                m, p, members = self.placed(code)
                drone = next(k for entries in p.values() for t, k, n, x in entries if n == "Moth 11")
                self.assertEqual(drone["UnlimitedFuel"], "False")
                self.assertTrue(drone["HomeBase"].startswith("Taskforce1LandUnit"))
                self.assertEqual(drone["Disabled"], "True")
                self.assertIn(10, m["_enter"].values())
                self.assertEqual(m["resolve"]["ForwardRecon"][0], "classify")

    def test_uav_strip_has_a_registered_and_localized_mission_variant(self):
        uid = "sest_uav_forward"
        registered = b.variants(uid, "land_units")
        self.assertTrue(registered, "an alias needs its own companion variants file")
        variants = b.read(b.winning(f"land_units/{uid}_variants.ini"))
        self.assertNotRegex(variants, r"(?m)^CustomAirGroup=True")
        language = b.read(b.winning("language_en/land_units_names.ini"))
        names = re.search(rf"^\[{uid}\]\n(.*?)(?=^\[|\Z)", language, re.M | re.S)[1]
        targets = [code for code, mission in self.missions.items()
                   if any(u["type"] == uid for u in mission["units"])]
        for code in targets:
            with self.subTest(code=code):
                _m, p, _members = self.placed(code)
                strip = next(k for entries in p.values() for _t, k, _n, _x in entries
                             if k["Type"] == uid)
                pick = strip.get("VariantReference")
                self.assertIn(pick, registered)
                self.assertRegex(names, rf"(?m)^{re.escape(pick)}=[^,\n]+,[^,\n]+$")
                self.assertEqual(strip["CustomAirGroup"], "True")
                self.assertEqual(strip["usn_rq7705"], "Squadron1,2")

    def test_all_missions_have_reports_and_pair_is_controlled(self):
        self.assertEqual(len(self.missions), 77)
        for code, m in self.missions.items():
            self.assertTrue(m.get("reports"), code)
            b.check_message_texts(m)
        a, c = self.missions["SWD10"], self.missions["SWD11"]
        self.assertEqual(a["stations"], c["stations"])
        self.assertEqual(a["date"], c["date"])
        for u, v in zip(a["units"], c["units"]):
            self.assertEqual({k: val for k, val in u.items() if k != "disable"}, v)
            if u["side"] == "red":
                self.assertEqual(u["disable"], ("sensors",))

    def test_ran_rosters_and_resident_wings_use_the_ran_model(self):
        for spec in self.specs[:2]:
            units = {e["unit"]: e for e in spec["ROSTER"]}
            self.assertNotIn("usn_mh-60r", units)
            self.assertEqual(units["ran_mh-60r"]["picks"], ["Squadron1"])
            self.assertTrue({"rn_ff_type23", "js_ffg_mogami", "ko_ffg-818"} <= units.keys())
        sq = b.winning("aircraft/ran_mh-60r_squadrons.ini").read_text(encoding="utf-8-sig")
        self.assertIn("LiveryTexture=ran_mh-60r_816.png", sq)
        self.assertIn("Nation=Australia", sq)

    def test_rankin_cannot_reappear_after_loss(self):
        a, c = self.missions["SR06"], self.missions["SR09"]
        self.assertIn("SR06RankinLost", a["declares"])
        boat = next(u for u in c["units"] if u.get("name") == "HMAS Rankin")
        self.assertEqual(boat["spawn_if"], ("SR06RankinLost", "IsFalse"))

    def test_four_aircraft_rows_have_four_real_placeholder_sections(self):
        for m in self.missions.values():
            if m.get("role") != "fleet":
                continue
            for row in m.get("window", {}).get("flights", []):
                role = row.split("|", 1)[0]
                if role in ("CAP", "Attack"):
                    slots = [u for u in m["units"] if u["side"] == "blue" and u.get("slot") == role]
                    if slots:
                        self.assertEqual(len(slots), 4, (m["key"], role))

    def test_submerged_boat_cannot_receive_an_airborne_radar_ship_track(self):
        m, p, members = self.placed("SR09")
        old = b.OPENING_PROBLEMS[:]
        try:
            b.OPENING_PROBLEMS.clear()
            b.check_opening(m, p)
            self.assertEqual(b.OPENING_PROBLEMS, [])
            # Surfacing the same boat makes it a radar-visible ship target;
            # the gate must still reject that unprotected opening.
            k = p["Taskforce1Submarine"][0][1]
            bits = k["RelativePositionInNM"].split(",")
            bits[1] = "0"
            k["RelativePositionInNM"] = ",".join(bits)
            b.check_opening(m, p)
            self.assertTrue(any("radar" in text for text in b.OPENING_PROBLEMS))
        finally:
            b.OPENING_PROBLEMS[:] = old


if __name__ == "__main__":
    unittest.main()
