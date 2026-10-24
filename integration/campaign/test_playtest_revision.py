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

    def test_uav_team_uses_field_squad_geometry_and_only_recon_inventory(self):
        text = b.read(b.winning("land_units/sest_uav_forward.ini"))
        self.assertIn("ResourcesRoot=dronesquad.obj", text)
        self.assertNotIn("#!alias land_units/airfield_small", text)
        self.assertRegex(text, r"(?m)^AircraftCapacity=3$")
        self.assertRegex(text, r"(?m)^AircraftSupported=usn_rq7705$")
        self.assertRegex(text, r"(?m)^NumberOfWeaponSystems=0$")
        self.assertNotIn("[WeaponSystem1]", text)
        self.assertNotIn("Mugin5FPV", text)
        self.assertNotIn("[SensorSystem2]", text)
        self.assertNotIn("HitZone3", text)
        self.assertNotIn("TargetPointPosition3=", text)
        self.assertRegex(text, r"(?m)^NumberOfLaunchPoints=1$")
        self.assertRegex(text, r"(?m)^NumberOfRecoveryPoints=1$")

    def test_o10_team_is_on_yapen_and_has_a_finite_recovery_margin(self):
        m, p, members = self.placed("SWO10")
        team = next(k for _tag, k, _n, _x in p["Taskforce1LandUnit"]
                    if k["Type"] == "sest_uav_forward")
        # Station intent is Yapen, south across water from the enclave.
        self.assertLess(m["stations"]["uav_strip"]["at"][0], -1.6)
        self.assertGreater(m["stations"]["pads"]["at"][0], -1.3)
        distance = b.nm_between(m["stations"]["uav_strip"]["at"], m["stations"]["uav_scout"]["at"])
        self.assertLess(distance * 2 + 10, 100)
        self.assertGreater(distance, 10)
        drone = next(k for _t, k, n, _x in p["Taskforce1Aircraft"] if n == "Moth 11")
        self.assertEqual(drone["HomeBase"], members["uav_strip"][0])
        self.assertIn("friendly Yapen", m["brief"])

    def test_o10_support_targets_are_separate_and_not_main_launcher_kills(self):
        m, p, members = self.placed("SWO10")
        self.assertEqual(m["victory"]["stations"], ["pads"])
        self.assertEqual(m["victory"]["min_units"], 3)
        self.assertEqual(len(members["pads"]), 5)
        _name, text = b.render(m, p, members)
        for oid, station in (("MissileStores", "missile_ammo"),
                             ("MilitaryFuel", "missile_fuel"),
                             ("LaunchControl", "missile_command")):
            self.assertEqual(m["resolve"][oid], ("destroy", station, 1))
            self.assertTrue(all(tag.startswith("Taskforce2LandUnit") for tag in members[station]))
            self.assertFalse(set(members[station]) & set(members["pads"]))
            self.assertIn("Action_ObjectivesCompleted=" + oid, text)
            self.assertGreater(b.nm_between(m["stations"][station]["at"], m["stations"]["pads"]["at"]), 5)

    def test_authored_operations_offer_preparation_without_changing_force_generation(self):
        for code in ("SWO10", "SW08", "SWD9"):
            m, p, members = self.placed(code)
            before = [(k.get("WeaponStatus"), k.get("RadarsActive"))
                      for entries in p.values() for _t, k, _n, _x in entries]
            _name, text = b.render(m, p, members)
            self.assertIn("Action_PrepareFlightDeck=True", text)
            self.assertIn("Action_Taskforce1_Message=FlightDeckPrepMessage", text)
            message = next(line for line in text.splitlines() if line.startswith("FlightDeckPrepMessage="))
            self.assertEqual(message.count("|"), 2)
            self.assertIn("Keep the simulation paused", message)
            self.assertEqual(before, [(k.get("WeaponStatus"), k.get("RadarsActive"))
                                    for entries in p.values() for _t, k, _n, _x in entries])
        self.assertIsNone(self.missions["SWO10"].get("generation"))

    def test_ford_has_usable_us_f35cs_without_overfilling_the_carrier(self):
        from common.carrier_wings import FORD_WING
        carrier = next(u for u in self.missions["SW11"]["units"] if u["type"] == "usn_cvn_ford")
        self.assertEqual(carrier["air_group"], FORD_WING)
        self.assertEqual(sum(n for uid, _sq, n in FORD_WING if uid == "usn_f-35c"), 16)
        self.assertEqual(sum(n for _uid, _sq, n in FORD_WING), 70)
        self.assertLess(sum(n for _uid, _sq, n in FORD_WING), b.deck_size(carrier["type"]))
        for uid, sq, _n in FORD_WING:
            self.assertIn(sq, b.squadrons(uid))
            self.assertEqual(b.pick_nation(uid, sq), "US", (uid, sq))

    def test_ford_variant_wings_cannot_hide_the_f35s(self):
        from common.carrier_wings import FORD_TYPES, FORD_WING, ford_lines
        for uid in FORD_TYPES:
            text = b.read(b.winning(f"vessels/{uid}_variants.ini"))
            sections = re.findall(r"^\[(Default|Variant\d+)\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
            self.assertTrue(sections, uid)
            for variant, body in sections:
                with self.subTest(uid=uid, variant=variant):
                    self.assertIn("CustomAirGroup=True", body)
                    self.assertIn(ford_lines().strip(), body)
                    rows = re.findall(r"^(usn_[^=]+)=([^\n]+)", body, re.M)
                    count = sum(int(p.split(",")[1]) for _unit, values in rows for p in values.split("|"))
                    self.assertEqual(count, 70)
            self.assertLess(sum(n for _u, _s, n in FORD_WING), b.deck_size(uid))
        jsf = next(u for u in self.missions["SWD6"]["units"] if u["type"] == "usn_cvn_ford_jsf")
        self.assertEqual(jsf.get("name"), "USS Enterprise")

    def test_broken_wake_relay_cancels_only_the_uncommitted_surface_attack(self):
        m, p, members = self.placed("SWC2")
        b.solve_arrival(m, p, members)
        _name, text = b.render(m, p, members)
        blocks = re.findall(r"^\[Trigger(\d+)\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
        joins = [(number, body) for number, body in blocks if "Name=Joins at minute 25\n" in body]
        self.assertEqual(len(joins), 1)
        number, body = joins[0]
        self.assertIn("Action_Units=" + ",".join(members["followup"]), body)
        cancel = next(body for _n, body in blocks if "Name=Reinforcements cancelled before minute 25" in body)
        self.assertIn("Condition_Condition1_Units=" + ",".join(members["relay"]), cancel)
        self.assertIn("Condition_Condition2_Time=1500", cancel)
        self.assertIn("ConditionsCompleted=<Condition1> AND NOT <Condition2>", cancel)
        self.assertIn(f"Action_DisableTriggers=Trigger{number}", cancel)
        first_raid = next(body for _n, body in blocks if "Name=Joins at minute 5\n" in body)
        self.assertNotIn("Action_DisableTriggers", first_raid)
        self.assertEqual(m["victory"]["station"], "straggler")
        self.assertEqual(m["victory"]["transit"], 6)
        self.assertEqual(m["neutral_objective"], "Traffic")
        self.assertEqual(m["resolve"]["RelayID"], ("classify", "relay", 1))
        self.assertEqual(m["resolve"]["ClearDatum"], ("destroy", "red_sub", 1))
        self.assertNotIn("Action_UnitReveal", text)
        b.mark_supplied(m, p)
        submarine = next(k for tag, k, name, _ in p["Taskforce1Submarine"] if name == "HMAS Sheean")
        self.assertEqual(submarine["WeaponStatus"], "Hold")
        self.assertEqual(submarine["TaskForceModeIgnoreUnit"], "True")
        self.assertEqual(m["geography"], "coast")
        x, _depth, z = submarine["RelativePositionInNM"].split(",")
        actual = (m["centre"][0] + float(z) / 60, m["centre"][1] + float(x) / 60)
        self.assertAlmostEqual(actual[0], -6.30, places=3)
        self.assertAlmostEqual(actual[1], 130.52, places=3)
        self.assertGreater(b.coast_data(m).nm_to_coast(*actual), 20)

    def test_relay_cannot_cancel_unrelated_units_sharing_its_deadline(self):
        m, p, members = self.placed("SWC2")
        b.solve_arrival(m, p, members)
        for tag, minute in list(m["_enter"].items()):
            if minute == 5:
                m["_enter"][tag] = 25
        with self.assertRaisesRegex(SystemExit, "entire opposing join"):
            b.render(m, p, members)

    def test_j20_close_range_choice_leaves_radar_and_weapons_intact(self):
        # Compare only the intentional pair of keys, not a synthetic radar buff.
        donor = b.read(b.ROOT / "mods-source/3591563716/aircraft/plaaf_j-20a.ini")
        built = b.read(b.winning("aircraft/plaaf_j-20a.ini"))
        def values(text):
            return {match[1]: match[2].split("//")[0].strip()
                    for match in re.finditer(r"^([^#\[\s][^=\n]*)=([^\n]*)", text, re.M)}
        a, c = values(donor), values(built)
        self.assertEqual({key for key in a if a[key] != c.get(key)}, {"VisualIdentificationRange", "IRSignature"})
        self.assertEqual(c["RCS"], "0.0014")
        self.assertEqual(c["VisualIdentificationRange"], "6")
        self.assertEqual(c["IRSignature"], "Meager")

    def test_all_missions_have_reports_and_pair_is_controlled(self):
        # Every mission of every campaign, each under its own code: the count
        # comes from the specs, so a campaign that gains missions does not
        # have to edit it, and two missions sharing a code still fail it.
        self.assertEqual(len(self.missions), sum(len(s["MISSIONS"]) for s in self.specs))
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
