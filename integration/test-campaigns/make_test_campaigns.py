#!/usr/bin/env python3
"""PC test campaigns for Dynamic Campaign Mod 1.0.1: weather hand-off and polar probes.

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

The Hormuz campaign also gets sest-weather.json beside its campaign.json: a
placed storm, Cyclone DARYA, written by tools/make_sest_weather.py. Dynamic
Campaign Mod 1.0.1 itself has no storm field (only "weather": pacific or
atlantic) and draws new weather for every new campaign; SEST's runtime
(WorldStorms, [Runtime] WorldStorms=1, default on) puts the sidecar's storm
into DCM's own weather model, so it shows on the weather layer and storm
list, on the contact screen and in battle [Environment]. DARYA tracks over
water from the Arabian Sea north-west up the Gulf of Oman, through the Strait
of Hormuz and west into the Gulf: about 35 nm past Group C 14 h after the
start, about 20 nm past Group B 36 h after it, and dies as a weak low short
of Group A. storm_check proves every point and segment of the track DCM
interpolates is on water (build_dynamic_campaign.is_water and segment_wet,
the land mask check_dynamic_campaign uses for forces). Everything else in the weather is still DCM's
own draw. The game holds one weather state per battle. Sea ice in the game
is a fixed sonar-noise texture with no visual or movement effect, and the
campaign mod has no ice at all.
"""
import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORLD = ROOT / "integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns/sest-world-regions-2028/campaign.json"
OUT = HERE / "Test_Campaigns" / "dynamic_campaigns"
CHECK = ROOT / "integration/world-sandbox/check_dynamic_campaign.py"
sys.path.insert(0, str(ROOT / "tools"))
import make_sest_weather as weather  # noqa: E402
sys.path.insert(0, str(ROOT / "integration/world-sandbox"))
import build_dynamic_campaign as land  # noqa: E402  (is_water, segment_wet: the forces' land mask)

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


# Cyclone DARYA, placed for the Hormuz campaign (start 2028-01-15T04:00Z).
# Rows: utc, lat, lon, max wind kn, outer radius nm. A January cyclone this
# far north is not climatology; it is a test fixture on a known track, all
# over water: the Arabian Sea north-west up the Gulf of Oman (between Ras al
# Hadd and Jask), north past Group C (22.4N 61.8E, about 35 nm, 14 h after
# the start), up the channel east of Group B (26.0N 56.7E, about 20 nm, 36 h
# after it) and west through the Strait of Hormuz south of Qeshm into the
# Gulf, where it weakens and dies as a weak low well short of Group A
# (27.9N 50.3E). Each group is in the strong ring just outside the eye
# (DCM's wind falls to calm inside the radius of maximum wind). From
# 16 Jan 00Z the waypoints sit on DCM's 6-hourly track times (Born + 6 h k),
# so the track DCM interpolates is these straight segments; storm_check
# sweeps every 6-hourly point, every segment and every half hour for land.
HORMUZ_STORM = {
    "note": "SEST PC test fixture for sest-test-hormuz-weather; tools/make_sest_weather.py",
    "storms": [{
        "id": "darya", "name": "DARYA", "kind": "Cyclone",
        "track": [
            ["2028-01-15T00:00Z", 19.6, 65.0, 65, 220],
            ["2028-01-15T12:00Z", 21.2, 63.6, 85, 230],
            ["2028-01-16T00:00Z", 24.2, 61.1, 90, 240],
            ["2028-01-16T06:00Z", 24.9, 59.4, 82, 230],
            ["2028-01-16T12:00Z", 25.45, 57.55, 74, 215],
            ["2028-01-16T18:00Z", 26.45, 56.85, 62, 200],
            ["2028-01-17T00:00Z", 26.45, 55.7, 50, 190],
            ["2028-01-17T06:00Z", 26.15, 54.6, 40, 180],
            ["2028-01-17T12:00Z", 26.15, 53.9, 32, 165],
            ["2028-01-17T18:00Z", 26.25, 53.2, 25, 150],
        ],
    }],
}
HORMUZ_GROUPS = {"C": (22.4, 61.8), "B": (26.0, 56.7), "A": (27.9, 50.3)}


def storm_check(doc, campaign):
    """The placed storm does what README-TESTS.txt tells the tester to watch."""
    s = doc["storms"][0]
    start = weather.parse_time(campaign["start"])
    lines = [f"STORM sidecar format and limits: {'PASS' if not weather.check(doc) else 'FAIL ' + '; '.join(weather.check(doc))}"]
    lines += [f"STORM {n}: FAIL" for n in weather.check_campaign(doc, campaign)]
    alive = weather.position(s, start) is not None
    lines.append(f"STORM active at the campaign start: {'PASS' if alive else 'FAIL'}")
    c, b, a = (weather.closest_approach(s, *HORMUZ_GROUPS[g]) for g in "CBA")
    hours = lambda t: (t - start).total_seconds() / 3600
    lines.append(f"STORM passes Group C: {c[0]:.0f} nm at +{hours(c[1]):.0f} h, {c[2]:.0f} kn: "
                 f"{'PASS' if 20 <= c[0] < 60 and c[2] >= 64 and 0 < hours(c[1]) <= 24 else 'FAIL'}")
    lines.append(f"STORM then Group B: {b[0]:.0f} nm at +{hours(b[1]):.0f} h, {b[2]:.0f} kn: "
                 f"{'PASS' if 20 <= b[0] < 60 and b[2] >= 50 and hours(c[1]) < hours(b[1]) <= 48 else 'FAIL'}")
    lines.append(f"STORM weak and outside its reach at Group A: {a[0]:.0f} nm, {a[2]:.0f} kn, reach {a[3]:.0f} nm: "
                 f"{'PASS' if a[0] > a[3] and a[2] < 34 else 'FAIL'}")
    lines.append(over_water(s))
    return lines


def over_water(s):
    """The storm centre never crosses land: every 6-hourly point of the track
    the runtime builds (StormSidecar.Track: Born + 6 h k, and Dies), every
    straight segment between them (DCM's WeatherSystem.At interpolates
    linearly between track points), every waypoint segment, and every half
    hour of the waypoint interpolation."""
    if land.globe is None:
        return "STORM track over water: FAIL (global_land_mask is not installed, so it cannot be checked)"
    born, dies = weather.parse_time(s["waypoints"][0]["utc"]), weather.parse_time(s["waypoints"][-1]["utc"])
    life = (dies - born).total_seconds() / 3600
    steps = [min(6 * k, life) for k in range(int(-(-life // 6)) + 1)]
    track = [weather.position(s, born + timedelta(hours=h))[:2] for h in steps]
    bad = [f"{(born + timedelta(hours=h)):%d %H:%MZ}" for h, p in zip(steps, track) if not land.is_water(*p)]
    bad += [f"6-hourly segment {k}" for k in range(len(track) - 1) if not land.segment_wet(track[k], track[k + 1], step_nm=2)]
    wps = [(p["lat"], p["lon"]) for p in s["waypoints"]]
    bad += [f"waypoint segment {k}" for k in range(len(wps) - 1) if not land.segment_wet(wps[k], wps[k + 1], step_nm=2)]
    t = born
    while t <= dies:
        if not land.is_water(*weather.position(s, t)[:2]):
            bad.append(f"{t:%d %H:%MZ}")
        t += timedelta(minutes=30)
    return (f"STORM track over water ({len(track)} six-hourly points, {len(track) - 1} segments, every half hour): "
            + ("PASS" if not bad else "FAIL on land at " + ", ".join(bad[:8])))


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
    sidecars = {"sest-test-hormuz-weather": weather.build(HORMUZ_STORM)}
    bad = 0
    for folder, c in built:
        path = OUT / folder / "campaign.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(c, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        sidecar = path.parent / weather.FILE_NAME
        storm_lines = []
        if folder in sidecars:
            weather.write(sidecars[folder], sidecar)
            storm_lines = storm_check(sidecars[folder], c)
        elif sidecar.exists():
            sidecar.unlink()
        r = subprocess.run([sys.executable, str(CHECK), str(path)], capture_output=True, text=True)
        # The checker's submarine-roster and ground-forces lines are about the
        # world campaign (submarines.py, its ground tables), not this file; a
        # harbour anchor on land is the world campaign's own base row, as there.
        lines = (r.stdout + r.stderr).splitlines()
        real = [x.strip() for x in lines if x.startswith("    ")
                and "submarines.py:" not in x and "INFERRED risk" not in x
                and "anchor is on land (harbour anchors often are" not in x]
        engine = [x for x in lines if x.startswith(("ENGINE", "AUDIT"))]
        storm_bad = [x for x in storm_lines if not x.endswith("PASS")]
        ok = all(x.endswith("PASS") for x in engine) and len(engine) == 2 and not real and not storm_bad
        print(f"{folder}: {'PASS' if ok else 'FAIL'}")
        for line in engine + real + storm_lines:
            print("   ", line)
        bad |= not ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
