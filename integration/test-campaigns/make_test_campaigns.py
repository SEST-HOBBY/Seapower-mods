#!/usr/bin/env python3
"""PC test campaigns for Dynamic Campaign Mod 1.0.0: weather hand-off and polar probes.

    python3 integration/test-campaigns/make_test_campaigns.py

Writes three small campaigns into Test_Campaigns/dynamic_campaigns/ and
checks each with integration/world-sandbox/check_dynamic_campaign.py:

  sest-test-hormuz-weather  three blue groups 350-700 nm apart (northern Gulf,
                            Strait of Hormuz, Arabian Sea), each with a red
                            group about 120 nm off, to take one contact at a
                            time from the world map into a battle and compare
                            the battle's weather with the map's.
  sest-test-polar-north     the Barents Sea in March (winter ice): an ice-edge
                            group at 77N, a Bear Island group and an ice-free
                            control in the Norwegian Sea.
  sest-test-polar-south     the Antarctic Peninsula in January: Bransfield
                            Strait, the Weddell Sea ice edge and a Drake
                            Passage control.

They are tests, not campaigns to play: fog of war is off and the forces are
small. They install into the game's user layer (StreamingAssets/user/
dynamic_campaigns), which Dynamic Campaign Mod lists like any other layer
(CampaignMenuPatch: FileManager.GetDirectories("dynamic_campaigns", All)),
so the Workshop item is not touched. INSTALL-TEST-CAMPAIGNS.ps1 copies,
removes and collects.

What the tests cannot show, from the code: Dynamic Campaign Mod 1.0.0 has no
storm, fixed-weather or weather-event field (only "weather": pacific or
atlantic) and draws a new weather seed for every new campaign, so a storm
cannot be placed; and the game holds one weather state per battle. Sea ice
in the game is a fixed sonar-noise texture with no visual or movement effect,
and the campaign mod has no ice at all.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORLD = ROOT / "integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns/sest-world-regions-2028/campaign.json"
OUT = HERE / "Test_Campaigns" / "dynamic_campaigns"
CHECK = ROOT / "integration/world-sandbox/check_dynamic_campaign.py"

TEST_NOTE = ("SEST PC TEST, not a campaign to play. Fog of war is off. ")


def world():
    return json.loads(WORLD.read_text(encoding="utf-8"))


def base(w, bid, **override):
    for b in w["bases"]:
        if b["id"] == bid:
            row = dict(b)
            row.update(override)
            return row
    sys.exit(f"base {bid} is not in the world campaign")


def unit_ids(forces):
    out = set()
    for f in forces:
        for spec in f["units"]:
            out.add(spec.split()[0])
    return out


def assemble(w, *, cid, folder, name, description, start, weather, bounds, view,
             blue_nations, red_nations, bases, forces, patrols):
    used = unit_ids(forces)
    missing = sorted(u for u in used if u not in w["values"])
    if missing:
        sys.exit(f"{folder}: no value for {', '.join(missing)} in the world campaign")
    sides = []
    for s in w["sides"]:
        row = dict(s)
        row["nations"] = blue_nations if s["id"] == "blue" else red_nations
        sides.append(row)
    return {
        "id": cid,
        "name": name,
        "description": TEST_NOTE + description,
        "stars": 1,
        "start": start,
        "weather": weather,
        "bounds": bounds,
        "view": view,
        "sides": sides,
        "bases": bases,
        "forces": forces,
        "patrols": patrols,
        "fogOfWar": False,
        "enemyAirlifts": False,
        "ai": {"startTier": 7, "daysPerTier": 30, "hold": False},
        "ranks": w["ranks"],
        "values": {u: w["values"][u] for u in sorted(used)},
        "catalogue": [c for c in w["catalogue"] if c["unit"] in used
                      and c["nation"] in (blue_nations + red_nations)],
        "texts": {},
    }


def surface(name, side, base_id, at, units):
    return {"name": name, "side": side, "base": base_id, "type": "Surface", "at": at, "units": units}


def hormuz(w):
    # Spacing: Dynamic Campaign Mod joins surface groups within 200 nm (150 nm
    # coastal) into one battle, and its weather noise runs on a 5-degree
    # (about 300 nm) lattice, so the three blue groups sit 350-700 nm apart.
    # Each red group starts about 120 nm from its blue group, outside the
    # 100 nm open-sea contact range, and patrols toward it.
    forces = [
        surface("Group A - northern Gulf", "blue", "me_bahrain_nsa_bahrain", [27.9, 50.3],
                ["usn_ddg_burke_f2a_099_late named DDG-102 Sampson"]),
        surface("Group B - Strait of Hormuz", "blue", "me_bahrain_nsa_bahrain", [26.0, 56.7],
                ["usn_ddg_burke_f2a_099_late named DDG-103 Truxtun"]),
        surface("Group C - Arabian Sea", "blue", "me_bahrain_nsa_bahrain", [22.4, 61.8],
                ["usn_ddg_burke_f2a_099_late named DDG-104 Sterett"]),
        surface("Red A - Bushehr flotilla", "red", "home_irn_bushehr_naval", [27.0, 52.3],
                ["ir_ptg_combattante_II x2"]),
        surface("Red B - Bandar Abbas flotilla", "red", "home_irn_bandar_abbas", [26.4, 54.2],
                ["ir_ffg_alvand_95", "ir_ptg_peykaap_3 x2"]),
        surface("Red C - Makran flotilla", "red", "reg_irn_chabahar", [24.3, 61.0],
                ["ir_ffg_alvand", "ir_ptg_peykaap_3 x2"]),
    ]
    patrols = [
        {"force": "Red A - Bushehr flotilla", "points": [[27.0, 52.3], [27.6, 51.3]]},
        {"force": "Red B - Bandar Abbas flotilla", "points": [[26.4, 54.2], [26.1, 55.6]]},
        {"force": "Red C - Makran flotilla", "points": [[24.3, 61.0], [22.9, 61.6]]},
    ]
    bases = [base(w, b) for b in ("me_bahrain_nsa_bahrain", "home_irn_bushehr_naval",
                                   "home_irn_bandar_abbas", "home_irn_jask", "reg_irn_chabahar")]
    for b in bases:
        b.pop("supplyFrom", None)
    return assemble(
        w, cid="sest.test.hormuz_weather", folder="sest-test-hormuz-weather",
        name="SEST Test: Hormuz Weather Split",
        description=("Three US destroyers 350-700 nm apart: the northern Gulf, the Strait of Hormuz "
                     "and the Arabian Sea, each with an Iranian flotilla about 120 nm off. Watch the "
                     "weather layer, then take each contact into a battle and compare its weather "
                     "with the map at that place and time."),
        start="2028-01-15T04:00:00Z", weather="atlantic",
        bounds={"latMin": 20.0, "latMax": 31.0, "lonMin": 47.0, "lonMax": 65.0},
        view={"lat": 25.5, "lon": 56.0, "pixelsPerDegree": 45.0},
        blue_nations=["US"], red_nations=["Iran"], bases=bases, forces=forces, patrols=patrols)


def polar_north(w):
    forces = [
        surface("Group N1 - Barents ice edge", "blue", "home_nor_haakonsvern", [76.8, 36.0],
                ["knm_ffg_oslo"]),
        surface("Group N2 - Bear Island", "blue", "home_nor_haakonsvern", [74.0, 19.5],
                ["knm_ffg_oslo"]),
        surface("Group N3 - Norwegian Sea control", "blue", "home_nor_haakonsvern", [67.0, 6.0],
                ["knm_ffg_oslo"]),
        surface("Red N1 - Northern Fleet ice patrol", "red", "home_rus_severomorsk", [75.0, 41.0],
                ["rfn_ffg_22350_1-4"]),
        surface("Red N2 - Northern Fleet Bear Gap patrol", "red", "home_rus_severomorsk", [72.6, 24.5],
                ["rfn_ffg_11356"]),
    ]
    patrols = [
        {"force": "Red N1 - Northern Fleet ice patrol", "points": [[75.0, 41.0], [76.5, 37.0]]},
        {"force": "Red N2 - Northern Fleet Bear Gap patrol", "points": [[72.6, 24.5], [73.8, 20.5]]},
    ]
    bases = [base(w, "home_nor_haakonsvern"), base(w, "home_rus_severomorsk")]
    for b in bases:
        b.pop("supplyFrom", None)
    return assemble(
        w, cid="sest.test.polar_north", folder="sest-test-polar-north",
        name="SEST Test: Polar North (Barents)",
        description=("March, the winter ice maximum. Norwegian frigates at the Barents ice edge "
                     "(76.8N), off Bear Island and in the ice-free Norwegian Sea, with Russian "
                     "frigates closing on the first two. Checks the map, routing and battles this "
                     "far north."),
        start="2028-03-10T08:00:00Z", weather="atlantic",
        bounds={"latMin": 58.0, "latMax": 81.0, "lonMin": 0.0, "lonMax": 60.0},
        view={"lat": 73.0, "lon": 25.0, "pixelsPerDegree": 25.0},
        blue_nations=["Norway"], red_nations=["Russia"], bases=bases, forces=forces, patrols=patrols)


def polar_south(w):
    forces = [
        surface("Group S1 - Bransfield Strait", "blue", "home_chl_punta_arenas", [-62.9, -58.6],
                ["ch_ffg_type23_pida"]),
        surface("Group S2 - Weddell Sea ice edge", "blue", "satl_falklands_mare_harbour", [-68.0, -42.0],
                ["rn_ff_type23"]),
        surface("Group S3 - Drake Passage control", "blue", "home_chl_punta_arenas", [-57.3, -64.0],
                ["ch_ffg_karel_doorman"]),
        surface("Red S1 - Russian Antarctic patrol", "red", "red_ant_bellingshausen", [-64.0, -62.5],
                ["rfn_ffg_11356"]),
        surface("Red S2 - Russian Weddell patrol", "red", "red_ant_bellingshausen", [-66.0, -36.0],
                ["rfn_ffg_22350_1-4"]),
    ]
    patrols = [
        {"force": "Red S1 - Russian Antarctic patrol", "points": [[-64.0, -62.5], [-63.3, -60.5]]},
        {"force": "Red S2 - Russian Weddell patrol", "points": [[-66.0, -36.0], [-67.6, -40.5]]},
    ]
    # Bellingshausen Station on King George Island is Russian; the campaign
    # mod needs a red base inside the bounds. A Port, not a naval base: no
    # yard, no production. A test fixture only.
    red_port = {"id": "red_ant_bellingshausen", "name": "Bellingshausen Station (test fixture)",
                "side": "red", "nation": "Russia", "kind": "Port", "lat": -62.2, "lon": -58.96,
                "income": 1}
    bases = [base(w, "home_chl_punta_arenas"), base(w, "satl_falklands_mare_harbour"), red_port]
    for b in bases:
        b.pop("supplyFrom", None)
    return assemble(
        w, cid="sest.test.polar_south", folder="sest-test-polar-south",
        name="SEST Test: Polar South (Antarctic Peninsula)",
        description=("January, the southern summer. A Chilean frigate in the Bransfield Strait, a "
                     "British frigate at the Weddell Sea ice edge (68S) and an ice-free control in "
                     "the Drake Passage, with Russian frigates closing on the first two. Checks the "
                     "map, routing and battles this far south."),
        start="2029-01-12T12:00:00Z", weather="pacific",
        bounds={"latMin": -72.0, "latMax": -50.0, "lonMin": -80.0, "lonMax": -25.0},
        view={"lat": -62.0, "lon": -55.0, "pixelsPerDegree": 25.0},
        blue_nations=["Chile", "UK"], red_nations=["Russia"], bases=bases, forces=forces,
        patrols=patrols)


def main():
    w = world()
    built = [("sest-test-hormuz-weather", hormuz(w)),
             ("sest-test-polar-north", polar_north(w)),
             ("sest-test-polar-south", polar_south(w))]
    bad = 0
    for folder, c in built:
        path = OUT / folder / "campaign.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(c, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(CHECK), str(path)], capture_output=True, text=True)
        # The checker's submarine-roster and ground-forces lines are about the
        # world campaign (submarines.py, its ground tables), not this file; a
        # harbour anchor on land is the world campaign's own base row, as there.
        lines = (r.stdout + r.stderr).splitlines()
        real = [x.strip() for x in lines if x.startswith("    ")
                and "submarines.py:" not in x and "INFERRED risk" not in x
                and "anchor is on land (harbour anchors often are" not in x]
        engine = [x for x in lines if x.startswith(("ENGINE", "AUDIT"))]
        ok = all(x.endswith("PASS") for x in engine) and len(engine) == 2 and not real
        print(f"{folder}: {'PASS' if ok else 'FAIL'}")
        for line in engine + real:
            print("   ", line)
        bad |= not ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
