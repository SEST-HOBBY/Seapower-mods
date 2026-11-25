#!/usr/bin/env python3
"""PC test campaigns for Dynamic Campaign Mod 1.0.1: weather hand-off and polar probes.

    python3 integration/test-campaigns/make_test_campaigns.py

Writes three small campaigns into Test_Campaigns/dynamic_campaigns/ and
checks each with integration/world-sandbox/check_dynamic_campaign.py:

  sest-test-hormuz-weather  three blue groups 350-700 nm apart (northern Gulf,
                            Strait of Hormuz, Arabian Sea), each with a red
                            group about 120 nm off, to take one contact at a
                            time from the world map into a battle and compare
                            the battle's weather with the map's; and a pair of
                            blue groups (D, E) that one red group (Red D)
                            pulls into ONE battle with D inside Cyclone DARYA
                            and E beyond its gale ring (local battle weather).
  sest-test-polar-north     the Barents Sea in March (winter ice): a frigate in
                            the marginal ice (about 50 %), a submarine under
                            the pack (about 75 %), a Bear Island group, an
                            ice-free control in the Norwegian Sea, and a
                            frigate off the eastern Murman coast (4 %) that
                            must cross the ice edge to reach a Russian picket
                            deep in the eastern Barents pack (88 %).
  sest-test-polar-south     the Antarctic Peninsula in January: Bransfield
                            Strait, a frigate in the western Weddell pack
                            (about 58 % on 12 January, 49 % on the 14th), a
                            submarine under it (about 75 %, 67 % on the 14th),
                            a Drake Passage control, and a frigate south-east
                            of Elephant Island (2 %) that must cross the ice
                            edge to reach a Russian picket in the south-
                            western Weddell pack (79 %).

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
of Group A. Groups D and E are the local-weather test (README-TESTS.txt
section 1h): at 15 Jan 08:00Z (+4 h) D is about 40 nm from DARYA's centre and
E about 180 nm, 144 nm apart, both within Dynamic Campaign Mod's 200 nm
open-sea join of the contact Red D makes, so one battle holds both and the
camera's weather changes between them (LocalWeatherView). storm_check proves every point and segment of the track DCM
interpolates is on water (build_dynamic_campaign.is_water and segment_wet,
the land mask check_dynamic_campaign uses for forces). Everything else in the weather is still DCM's
own draw. The game holds one weather state per battle; SEST's local battle
weather (LocalWeatherView) moves it with the camera in this campaign's
battles. Sea ice in the game itself is a fixed sonar-noise texture with no
visual or movement effect, and the campaign mod has no ice at all; SEST's
runtime (SeaIce=1, default on) adds seasonal ice inside battles, and
(CampaignIce=1, default on) draws the same ice on the campaign globe and
slows surface groups in it. ice_check prints the ice each polar group will
find, from tools/sea_ice_model.py (the runtime's own table and formula), and
checks the ice probes sit in 40-80 % ice (ships), 60-80 % (submarines) and
under 1 % (controls), all over water; that the campaign map opens with the
10 % ice edge in view (IceEdge.Default, the runtime's edge); and, for the transit group of each polar campaign,
the ice along the straight line to its target (DCM's Movement.Advance
interpolates latitude and longitude linearly between route points) and the
campaign speed it gets there (ice class "none": 1.0 under 10 %, 0.7 to 30 %,
0.4 to 60 %, beset at 0.1 from 60 %; CampaignIceSpeed); that the line gets
into 30 % ice while the target is still more than Dynamic Campaign Mod's
100 nm contact range away (and no other opposing group is that close), so
the 0.4 leg is run before the contact stops the transit; and that the
transit pair starts more than 100 nm from every opposing group and more than
200 nm (the surface join radius) from where the other tests' patrols make
contact, so it neither starts a contact nor joins those battles.
"""
import json
import math
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
import sea_ice_model as ice  # noqa: E402  (the runtime's sea-ice table and formula)

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
        # Local battle weather (LOCAL_WEATHER below): one contact, two weathers.
        surface("Group D - inside DARYA", "blue", "me_bahrain_nsa_bahrain", list(LOCAL_WEATHER["D"]),
                ["usn_ddg_burke_f2a_099_late named DDG-105 Dewey"]),
        surface("Group E - outside DARYA", "blue", "me_bahrain_nsa_bahrain", list(LOCAL_WEATHER["E"]),
                ["usn_ddg_burke_f2a_099_late named DDG-106 Stockdale"]),
        surface("Red D - Makran raiders", "red", "reg_irn_chabahar", list(LOCAL_WEATHER["red"][0]),
                ["ir_ffg_alvand", "ir_ffg_alvand_95"]),
    ]
    patrols = [
        {"force": "Red A - Bushehr flotilla", "points": [[27.0, 52.3], [27.6, 51.3]]},
        {"force": "Red B - Bandar Abbas flotilla", "points": [[26.4, 54.2], [26.1, 55.6]]},
        {"force": "Red C - Makran flotilla", "points": [[24.3, 61.0], [22.9, 61.6]]},
        {"force": "Red D - Makran raiders", "points": [list(p) for p in LOCAL_WEATHER["red"]]},
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
                     "with the map at that place and time. Groups D and E (south-east, in the open "
                     "Arabian Sea) meet Red D in one battle around 15 Jan 08:00Z: D inside Cyclone "
                     "DARYA, E beyond its gale ring; jump the camera between them."),
        start="2028-01-15T04:00:00Z", weather="atlantic",
        # lonMax 68 (65 before 21 Nov) takes in Group E, 180 nm east of DARYA.
        bounds={"latMin": 20.0, "latMax": 31.0, "lonMin": 47.0, "lonMax": 68.0},
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

# Local battle weather: ONE contact with ships inside DARYA and well outside
# it. At T (15 Jan 08:00Z, 4 h after the start) DARYA is at 20.67N 64.07E,
# 78 kn, moving north-west about 10 kn. Group D sits 40 nm ESE of the centre
# (the strong ring just outside the calm eye); Group E 180 nm ENE, beyond the
# gale ring; D-E 144 nm. Red D comes south from off the Makran coast towards
# E and makes contact (Dynamic Campaign Mod 1.0.1: ContactRanges.OpenSea
# ContactNm 100) a few hours in; the Engagement point is the midpoint of the
# two movers (Battles.Open: GeoPoint.Midpoint), and every surface group within
# SurfaceJoinNm of it joins (Battles.InReach: 200 nm open sea, 150 nm coastal,
# blended 30-90 nm from the coast by Battles.RangesAt). Out here the coast is
# 120+ nm away, so 200 nm. Group C (and its Red C contact) stay more than
# 200 nm from that point, and D/E more than 200 nm from Group C's.
# expected: what LocalWeatherTests reads from DCM 1.0.1's own model with DARYA
# placed (seed 4242), and how often over 60 campaign seeds; approximate for
# any one campaign (DCM draws new background weather for each).
LOCAL_WEATHER = {
    "T": "2028-01-15T08:00Z",
    "window": ("2028-01-15T07:00Z", "2028-01-15T10:00Z"),
    "D": (20.55, 64.77),
    "E": (21.3, 67.2),
    "red": ((23.6, 66.6), (21.9, 66.6)),
    "expected": {
        "D": "sea state 8-9, rain and thunder, overcast, wind about 60 kn (SS >= 7 in 57 of 60 seeds)",
        "E": "sea state 2-5, no storm rain, broken cloud, wind about 15-25 kn (SS <= 5 in 45 of 60 seeds)",
    },
}


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
    lines += local_check(s)
    return lines


def _smooth(x):
    """DCM 1.0.1 ClimateRegion.Smooth: smoothstep on 0..1."""
    return 0.0 if x <= 0 else 1.0 if x >= 1 else x * x * (3 - 2 * x)


def dcm_sea_state(knots):
    """DCM 1.0.1 Weather.SeaState(knots)."""
    for limit, ss in ((4, 1), (11, 2), (17, 3), (22, 4), (28, 5), (34, 6), (41, 7), (48, 8)):
        if knots < limit:
            return ss
    return 9


def tropical_term(point, d, rmw=None):
    """A placed tropical storm's own part of DCM 1.0.1's weather at d nm from
    its centre, from the runtime's track point (StormSidecar.cs: Vmax = wind,
    Outer = radius, R = rmw or clamp(radius / 10, 8, 45), Env 1): the wind
    term of WeatherModel.Compose for a tropical system (Vmax * (d < R ? d / R
    : sqrt(R / d)) * (1 - Smooth((d - 0.6 Outer) / (0.4 Outer)))) and
    WeatherModel.GaleRadiusNm (min(0.8 Outer, R (Vmax / 34)^2), 0 under
    34 kn). LocalWeatherTests checks the gale radius rule against DCM's own;
    DCM adds its background wind to the storm's, so these are the storm's
    share, not the whole sample (LocalWeatherTests samples the whole model)."""
    _, _, vmax, outer = point
    r = rmw if rmw else max(8.0, min(45.0, outer / 10))
    shape = d / r if d < r else math.sqrt(r / d)
    wind = vmax * shape * (1 - _smooth((d - 0.6 * outer) / (0.4 * outer)))
    gale = min(0.8 * outer, r * (vmax / 34) ** 2) if vmax >= 34 else 0.0
    return wind, gale


def local_check(s):
    """Groups D and E: one battle, two weathers (README-TESTS.txt 1h)."""
    lw = LOCAL_WEATHER
    t = weather.parse_time(lw["T"].replace("Z", ":00Z"))
    here = weather.position(s, t)
    lat, lon, wind, radius = here
    (dl, do), (el, eo) = lw["D"], lw["E"]
    dist = weather.distance_nm
    dd, de, sep = dist(lat, lon, dl, do), dist(lat, lon, el, eo), dist(dl, do, el, eo)
    lines = []
    ok = 30 <= dd <= 50 and 150 <= de <= 200 and sep <= 160
    lines.append(f"LOCAL at {t:%d %H:%MZ} DARYA {lat:.2f}N {lon:.2f}E {wind:.0f} kn, outer {radius:.0f} nm: "
                 f"Group D {dd:.0f} nm from the centre, Group E {de:.0f} nm, {sep:.0f} nm apart: {'PASS' if ok else 'FAIL'}")
    # The expected split, from DARYA's own wind term (DCM's tropical profile):
    # D inside the gale ring with storm sea (SS 8-9 from the storm alone), E
    # beyond it with the storm adding less than a gale (E's weather is DCM's
    # background, sea state 2-5 in most campaigns).
    wd, gale = tropical_term(here, dd)
    we, _ = tropical_term(here, de)
    checks = {"D": (dd < gale and dcm_sea_state(wd) >= 8, wd),
              "E": (de > gale and we < 34, we)}
    for g, d in (("D", dd), ("E", de)):
        ok, w = checks[g]
        lines.append(f"LOCAL expected at Group {g} ({lw[g][0]}N {lw[g][1]}E, {d:.0f} nm from DARYA) at {t:%H:%MZ}: "
                     f"{lw['expected'][g]}; DARYA's own wind there {w:.0f} kn (sea state {dcm_sea_state(w)} from it alone), "
                     f"gale ring {gale:.0f} nm: {'PASS' if ok else 'FAIL'}")
    # The window the README gives: D stays in the strong ring, E outside it.
    w0, w1 = (weather.parse_time(x.replace("Z", ":00Z")) for x in lw["window"])
    worst = []
    u = w0
    while u <= w1:
        p = weather.position(s, u)
        a, b = dist(p[0], p[1], dl, do), dist(p[0], p[1], el, eo)
        wa, g_r = tropical_term(p, a)
        wb, _ = tropical_term(p, b)
        worst.append((a, b, a < g_r and dcm_sea_state(wa) >= 8 and b > g_r and wb < 34))
        u += timedelta(minutes=30)
    ok = all(25 <= a <= 60 and b >= 140 and split for a, b, split in worst)
    lines.append(f"LOCAL {w0:%H:%M}-{w1:%H:%MZ}: Group D {min(x[0] for x in worst):.0f}-{max(x[0] for x in worst):.0f} nm from the centre "
                 f"(inside the gale ring, storm sea), Group E {min(x[1] for x in worst):.0f}+ nm (beyond it): {'PASS' if ok else 'FAIL'}")
    # One battle: Red D down its patrol line to the first contact (100 nm open sea).
    (r0, r1) = lw["red"]
    contact = None
    for i in range(201):
        f = i / 200
        r = (r0[0] + (r1[0] - r0[0]) * f, r0[1] + (r1[1] - r0[1]) * f)
        near = min((dist(*r, *lw[g]), g) for g in "DE")
        if near[0] <= 100:
            contact = (r, near[1], dist(*r0, *r))
            break
    if contact is None:
        lines.append("LOCAL Red D reaches contact range of Group D or E on its patrol line: FAIL")
        return lines
    r, g, run = contact
    mid = ((r[0] + lw[g][0]) / 2, (r[1] + lw[g][1]) / 2)
    jd, je = dist(*mid, dl, do), dist(*mid, el, eo)
    c = HORMUZ_GROUPS["C"]
    red_c = ((24.3, 61.0), (22.9, 61.6))
    jc = dist(*mid, *c)
    c_points = [((c[0] + p[0]) / 2, (c[1] + p[1]) / 2) for p in red_c]
    away = min(dist(*q, *x) for q in c_points for x in (lw["D"], lw["E"]))
    ok = jd <= 200 and je <= 200 and jc > 200 and away > 200
    lines.append(f"LOCAL Red D meets Group {g} after {run:.0f} nm; Engagement point {mid[0]:.2f}N {mid[1]:.2f}E: "
                 f"Group D {jd:.0f} nm, Group E {je:.0f} nm (both join, 200 nm), Group C {jc:.0f} nm (stays out); "
                 f"Group C's contacts at least {away:.0f} nm from D and E: {'PASS' if ok else 'FAIL'}")
    if land.globe is None:
        lines.append("LOCAL groups and Red D's line over water: FAIL (global_land_mask is not installed)")
        return lines
    wet = all(land.is_water(*p) for p in (lw["D"], lw["E"], r0, r1)) and land.segment_wet(r0, r1, step_nm=2) \
        and land.segment_wet(lw["D"], lw["E"], step_nm=2)
    lines.append(f"LOCAL Groups D and E, Red D's start, patrol line and the D-E line over water: {'PASS' if wet else 'FAIL'}")
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


# Sea-ice placement (SEST runtime SeaIce=1): each group's expected battle ice,
# from tools/sea_ice_model.py (the same table and formula as the runtime's
# SeaIceModel.cs, from the weather branch's seaice.py). role "ship": a surface
# group in 40-80 % ice (slowed: 30-60 % restricted 0.4, 60 % and up blocked
# for class "none"); "sub": a submarine under heavy ice (60 % and up, held
# below 30 m), at most 80 % so leads exist; "open": an ice-free control.
POLAR_ICE = {
    "sest-test-polar-north": [
        ("Group N1 - Barents marginal ice", "ship"),
        ("Group N4 - Kobben under the pack", "sub"),
        ("Group N3 - Norwegian Sea control", "open"),
    ],
    "sest-test-polar-south": [
        ("Group S2 - Weddell Sea pack", "ship"),
        ("Group S4 - Astute under the Weddell pack", "sub"),
        ("Group S3 - Drake Passage control", "open"),
    ],
}


# The campaign transit test (CampaignIce=1): a blue surface group in open water
# whose target, a red group, sits in the pack, so reaching it means crossing
# the ice edge (ICE_EDGE). (blue group, red group).
POLAR_TRANSIT = {
    "sest-test-polar-north": ("Group N5 - Murman coast transit", "Red N3 - Northern Fleet pack picket"),
    "sest-test-polar-south": ("Group S5 - Elephant Island transit", "Red S3 - Russian Weddell pack picket"),
}

# The runtime's ice edge (SeaIceRules IceEdge.Default, SeaIceEdgePercent unset):
# the campaign globe's cyan line and "pack ice" label, and the battle sheet edge.
ICE_EDGE = 10.0


def campaign_factor(c):
    """CampaignIceSpeed.Factor for ice class none (SeaIceRules thresholds 10/30/60)."""
    return 1.0 if c < 10 else 0.7 if c < 30 else 0.4 if c < 60 else 0.1


def view_edge_check(campaign, start):
    """The map opens on campaign["view"]; at its zoom a 1600 x 900 window spans
    +-800/ppd degrees of longitude and +-450/ppd of latitude. PASS when the ICE_EDGE (10 %)
    ice edge crosses the view's own meridian (or one 5 degrees either side),
    over water, inside both the view and the theatre bounds."""
    v, b = campaign["view"], campaign["bounds"]
    half_lat, half_lon = 450 / v["pixelsPerDegree"], 800 / v["pixelsPerDegree"]
    lat0, lat1 = max(b["latMin"], v["lat"] - half_lat), min(b["latMax"], v["lat"] + half_lat)
    found = []
    for lon in (v["lon"] - 5, v["lon"], v["lon"] + 5):
        if not (b["lonMin"] <= lon <= b["lonMax"]):
            continue
        steps = int(round((lat1 - lat0) / 0.1))
        prev = None
        for k in range(steps + 1):
            # from the pole side towards the equator: the polar pack's edge
            # first, not a lake or the Baltic
            lat = lat1 - k * 0.1 if v["lat"] > 0 else lat0 + k * 0.1
            c = ice.concentration(lat, lon, start)
            if prev is not None and (prev < ICE_EDGE) != (c < ICE_EDGE) and (land.globe is None or land.is_water(lat, lon)):
                found.append((lat, lon))
                break
            prev = c
    where = ", ".join(f"{abs(a):.1f}{'S' if a < 0 else 'N'} on {abs(o):.0f}{'W' if o < 0 else 'E'}" for a, o in found)
    return (f"ICE edge in view at the start ({v['lat']:.0f}, {v['lon']:.0f}, {v['pixelsPerDegree']:.0f} px/deg): "
            + (f"{ICE_EDGE:.0f} % line at {where}: PASS" if found else f"no {ICE_EDGE:.0f} % line in view: FAIL"))



# Dynamic Campaign Mod 1.0.1's contact rules (ContactRanges..cctor): two
# opposing movers within ContactNm open an Engagement at their midpoint
# (Battles.Detect, Battles.Open: GeoPoint.Midpoint), and every surface group
# within SurfaceJoinNm of that point joins it (Battles.InReach, JoinsTheFight
# for a group without an AI air mission). Open sea 100 / 200 nm, coastal
# 55 / 150 nm (Battles.RangesAt blends them 30-90 nm from the coast); the
# open-sea values are the larger, so the checks use them.
CONTACT_NM = 100.0
SURFACE_JOIN_NM = 200.0


def line_points(a, b, step_nm):
    """DCM's Movement.Advance moves linearly in latitude and longitude between
    route points: the points every ~step_nm of that line, with the distance
    run to each."""
    nm = weather.distance_nm(*a, *b)
    n = max(2, int(math.ceil(nm / step_nm)))
    pts = [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]
    run = [0.0]
    for k in range(1, n + 1):
        run.append(run[-1] + weather.distance_nm(*pts[k - 1], *pts[k]))
    return pts, run


def nearest_on(p, line, step_nm=2):
    """Distance from p to a patrol (or route) polyline, sampled every ~2 nm."""
    best = min(weather.distance_nm(*p, *q) for q in line)
    for a, b in zip(line, line[1:]):
        pts, _ = line_points(tuple(a), tuple(b), step_nm)
        best = min(best, min(weather.distance_nm(*p, *q) for q in pts))
    return best


def hostiles_of(campaign, side, skip=()):
    """(name, track) of every force of the other side: its patrol line, or its
    start point for a group without a patrol."""
    patrols = {pr["force"]: pr["points"] for pr in campaign["patrols"]}
    return [(f["name"], patrols.get(f["name"], [f["at"]])) for f in campaign["forces"]
            if "at" in f and f["side"] != side and f["name"] not in skip]


def contact_points(campaign, skip=()):
    """Where the patrols of the campaign's other tests (sections 2-4) first come
    within ContactNm of an opposing group: the midpoint DCM puts the
    Engagement at. The transit pair (skip) is left out: it must stay clear."""
    forces = {f["name"]: f for f in campaign["forces"] if "at" in f and f["name"] not in skip}
    out = []
    for pr in campaign["patrols"]:
        me = forces.get(pr["force"])
        if me is None:
            continue
        foes = [f["at"] for f in forces.values() if f["side"] != me["side"]]
        hit = None
        for a, b in zip(pr["points"], pr["points"][1:]):
            pts, _ = line_points(tuple(a), tuple(b), 1)
            for r in pts:
                d, g = min((weather.distance_nm(*r, *x), tuple(x)) for x in foes)
                if d <= CONTACT_NM:
                    hit = ((r[0] + g[0]) / 2, (r[1] + g[1]) / 2)
                    break
            if hit:
                break
        if hit:
            out.append((pr["force"], hit))
    return out


def _ll(p):
    return f"{abs(p[0]):.2f}{'S' if p[0] < 0 else 'N'} {abs(p[1]):.2f}{'W' if p[1] < 0 else 'E'}"


def separation_check(folder, campaign):
    """The transit pair must not start a contact or join another test's battle:
    each more than ContactNm from every opposing group at the start (and from
    every opposing patrol line), and more than SurfaceJoinNm from the contact
    points of the other tests' patrols."""
    blue, red = POLAR_TRANSIT[folder]
    by = {f["name"]: f for f in campaign["forces"]}
    lines, ok = [], True
    for name in (blue, red):
        me = by[name]
        foes = hostiles_of(campaign, me["side"])
        near = min((nearest_on(tuple(me["at"]), track), foe) for foe, track in foes)
        good = near[0] > CONTACT_NM
        ok &= good
        lines.append(f"ICE separation {name} at the start: nearest opposing group {near[1]} {near[0]:.0f} nm"
                     f" (contact {CONTACT_NM:.0f} nm): {'PASS' if good else 'FAIL'}")
    points = contact_points(campaign, skip=(blue, red))
    if not points:
        lines.append("ICE separation: no contact point found for the other tests' patrols: FAIL")
        return lines
    for force, pt in points:
        d = min(weather.distance_nm(*pt, *by[n]["at"]) for n in (blue, red))
        good = d > SURFACE_JOIN_NM
        ok &= good
        lines.append(f"ICE separation {force}'s contact at {_ll(pt)}: transit pair {d:.0f} nm away"
                     f" (join {SURFACE_JOIN_NM:.0f} nm): {'PASS' if good else 'FAIL'}")
    return lines


def transit_check(folder, campaign, start):
    """The ice along the transit group's straight line to its target, every
    ~20 nm, with the campaign speed factor there; PASS when it starts open
    (under 10 %), crosses the ICE_EDGE (10 %) edge, ends in 30 % or more and stays over
    water. Then the reach: the line must get into 30 % ice (0.4, restricted)
    while the target is still more than ContactNm away and before any other
    opposing group (or patrol line) is within ContactNm, so the tester sees
    1.0, 0.7 and 0.4 before DCM's contact stops the transit."""
    if folder not in POLAR_TRANSIT:
        return []
    blue, red = POLAR_TRANSIT[folder]
    at = {f["name"]: tuple(f["at"]) for f in campaign["forces"] if "at" in f}
    a, b = at[blue], at[red]
    pts, run = line_points(a, b, 20)
    nm, n = run[-1], len(pts) - 1
    cs = [ice.concentration(lat, lon, start) for lat, lon in pts]
    wet = land.globe is None or (all(land.is_water(*p) for p in pts) and land.segment_wet(a, b, step_nm=2))
    first_edge = next((k for k, c in enumerate(cs) if c >= ICE_EDGE), None)
    first60 = next((k for k, c in enumerate(cs) if c >= 60), None)
    ok = cs[0] < 10 and first_edge is not None and cs[-1] >= 30 and wet
    def nm_at(k):
        return "never" if k is None else f"{run[k]:.0f} nm"
    path = ", ".join(f"{c:.0f}" for c in cs)
    factors = ", ".join(f"{campaign_factor(c):.1f}" for c in cs)
    verdict = "PASS" if ok else "FAIL"
    lines = [f"ICE transit {blue} -> {red}: {nm:.0f} nm straight, ice every {nm / n:.0f} nm: {path} %"
             f" (starts open, crosses {ICE_EDGE:.0f} %, ends at 30 % or more): {verdict}",
             f"ICE transit speed factor (class none) along it: {factors}; {ICE_EDGE:.0f} % edge after {nm_at(first_edge)},"
             f" 60 % after {nm_at(first60)}; {'over water' if wet else 'CROSSES LAND'}: {verdict}"]
    # The reach, every ~2 nm.
    fine, frun = line_points(a, b, 2)
    fc = [ice.concentration(lat, lon, start) for lat, lon in fine]
    k10 = next((k for k, c in enumerate(fc) if c >= 10), None)
    k30 = next((k for k, c in enumerate(fc) if c >= 30), None)
    kc = next((k for k, p in enumerate(fine) if weather.distance_nm(*p, *b) <= CONTACT_NM), len(fine) - 1)
    others = [(foe, track) for foe, track in hostiles_of(campaign, by_side(campaign, blue), skip=(red,))]
    upto = k30 if k30 is not None else len(fine) - 1
    other = min(((nearest_on(fine[k], track), foe) for k in range(0, upto + 1, 5) for foe, track in others),
                default=(float("inf"), "none"))
    if k30 is None or k10 is None:
        lines.append("ICE transit reach: the line never gets to 30 % ice: FAIL")
        return lines
    left = weather.distance_nm(*fine[k30], *b)
    good = left > CONTACT_NM and k30 < kc and other[0] > CONTACT_NM
    p30 = fine[k30]
    lines.append(f"ICE transit reach: 0.7 (10 %) after {frun[k10]:.0f} nm, 0.4 (30 %) after {frun[k30]:.0f} nm at {_ll(p30)},"
                 f" {left:.0f} nm from {red}; contact ({CONTACT_NM:.0f} nm) only after {frun[kc]:.0f} nm,"
                 f" {frun[kc] - frun[k30]:.0f} nm of 0.4 before it; nearest other opposing group on the way"
                 f" {other[1]} {other[0]:.0f} nm: {'PASS' if good else 'FAIL'}")
    return lines


def by_side(campaign, name):
    return next(f["side"] for f in campaign["forces"] if f["name"] == name)


def ice_check(folder, campaign):
    """Expected sea ice at every group on the campaign's start date and two days
    later (battles happen in between), and the ice roles the README asks for."""
    from datetime import date, datetime
    start = datetime.fromisoformat(campaign["start"].replace("Z", "+00:00")).date()
    later = start + timedelta(days=2)
    roles = dict(POLAR_ICE.get(folder, []))
    lines = []
    for f in campaign["forces"]:
        if "at" not in f:
            continue
        lat, lon = f["at"]
        c0, c2 = ice.concentration(lat, lon, start), ice.concentration(lat, lon, later)
        role = roles.get(f["name"])
        ok = {"ship": lambda c: 40 <= c <= 80, "sub": lambda c: 60 <= c <= 80, "open": lambda c: c < 1}.get(role, lambda c: True)
        wet = land.globe is None or land.is_water(lat, lon)
        verdict = "PASS" if ok(c0) and ok(c2) and wet else "FAIL"
        lines.append(f"ICE {f['name']} at {lat:.2f}, {lon:.2f}: {c0:.1f} % on {start:%d %b}, {c2:.1f} % on {later:%d %b}"
                     f" ({role or 'not an ice probe'}{'' if wet else ', ON LAND'}): {verdict}")
    for pr in campaign["patrols"]:
        pts = pr["points"]
        dry = [k for k in range(len(pts) - 1) if land.globe is not None and not land.segment_wet(pts[k], pts[k + 1], step_nm=2)]
        tail = ", ".join(f"{ice.concentration(a, b, start):.0f} %" for a, b in pts)
        lines.append(f"ICE patrol {pr['force']}: ice along it {tail}; over water: {'PASS' if not dry else 'FAIL segment ' + str(dry)}")
    lines.append(view_edge_check(campaign, start))
    lines += transit_check(folder, campaign, start)
    if folder in POLAR_TRANSIT:
        lines += separation_check(folder, campaign)
    return lines


def polar_north(w):
    # 10 March, the winter maximum: the 10 % ice edge crosses 36E at about
    # 71.3N (the review's seaice.py run: 72N 18.7 %, 74N 62.3 %). N1 sits in
    # the marginal ice at 73.5N (about 50 %), the Kobben 66 nm further in at
    # 74.6N (about 75 %), and Red N1 closes from open water south-west of them,
    # so the contact is fought in the ice.
    forces = [
        surface("Group N1 - Barents marginal ice", "blue", "home_nor_haakonsvern", [73.5, 36.0],
                ["knm_ffg_oslo"]),
        surface("Group N4 - Kobben under the pack", "blue", "home_nor_haakonsvern", [74.6, 36.0],
                ["knm_ss_kobben"]),
        surface("Group N2 - Bear Island", "blue", "home_nor_haakonsvern", [74.0, 19.5],
                ["knm_ffg_oslo"]),
        surface("Group N3 - Norwegian Sea control", "blue", "home_nor_haakonsvern", [67.0, 6.0],
                ["knm_ffg_oslo"]),
        surface("Red N1 - Northern Fleet ice patrol", "red", "home_rus_severomorsk", [72.0, 30.0],
                ["rfn_ffg_22350_1-4"]),
        surface("Red N2 - Northern Fleet Bear Gap patrol", "red", "home_rus_severomorsk", [72.6, 24.5],
                ["rfn_ffg_11356"]),
        # The campaign transit test, away from the N1/N4 and N2 fights: N5 in
        # open water off the eastern Murman coast (69.5N 40E, 4 %) must cross
        # the ice edge to reach Red N3, a picket deep in the eastern Barents
        # pack (72.5N 49E, 88 %). The line gets into 30 % ice (0.4) about
        # 135 nm short of Red N3, so the 0.4 leg is run before DCM's 100 nm
        # contact; both start more than 100 nm from every opposing group and
        # more than 200 nm from where Red N1 and Red N2 make contact
        # (separation_check, transit_check).
        surface("Group N5 - Murman coast transit", "blue", "home_nor_haakonsvern", [69.5, 40.0],
                ["knm_ffg_oslo"]),
        surface("Red N3 - Northern Fleet pack picket", "red", "home_rus_severomorsk", [72.5, 49.0],
                ["rfn_ffg_11356"]),
    ]
    patrols = [
        {"force": "Red N1 - Northern Fleet ice patrol", "points": [[72.0, 30.0], [73.4, 35.5]]},
        {"force": "Red N2 - Northern Fleet Bear Gap patrol", "points": [[72.6, 24.5], [73.8, 20.5]]},
    ]
    bases = [base(w, "home_nor_haakonsvern"), base(w, "home_rus_severomorsk")]
    for b in bases:
        b.pop("supplyFrom", None)
    return assemble(
        w, cid="sest.test.polar_north", folder="sest-test-polar-north",
        name="SEST Test: Polar North (Barents)",
        description=("March, the winter ice maximum. A Norwegian frigate in the Barents marginal "
                     "ice (73.5N 36E, about 50 % ice), the submarine Kobben under the pack 66 nm "
                     "north (74.6N, about 75 %), a frigate off Bear Island and one in the ice-free "
                     "Norwegian Sea, with Russian frigates closing from open water. Group N5 off the "
                     "Murman coast must cross the ice edge to reach a Russian picket in the pack "
                     "(72.5N 49E). With SEST's sea ice on, the campaign map shows the ice edge and "
                     "slows N5 in the ice, and the battle at the ice edge has visible pack ice, "
                     "slowed ships, a submarine held under the ice and louder ice noise."),
        start="2028-03-10T08:00:00Z", weather="atlantic",
        bounds={"latMin": 58.0, "latMax": 81.0, "lonMin": 0.0, "lonMax": 60.0},
        view={"lat": 73.0, "lon": 25.0, "pixelsPerDegree": 25.0},
        blue_nations=["Norway"], red_nations=["Russia"], bases=bases, forces=forces, patrols=patrols)


def polar_south(w):
    # 12 January, southern summer: the surviving pack is in the western Weddell
    # Sea (seaice.py's summer shape peaks at 55W) and is retreating fast (a few
    # points a day). S2 sits at 67.2S 49W (about 58 % on the 12th, 49 % two
    # days later), the Astute 48 nm south at 68S 49W, and Red S2 closes from
    # the open water to the north-east. 68S 42W, the old S2, is 37 %
    # (restricted, not pack).
    forces = [
        surface("Group S1 - Bransfield Strait", "blue", "home_chl_punta_arenas", [-62.9, -58.6],
                ["ch_ffg_type23_pida"]),
        surface("Group S2 - Weddell Sea pack", "blue", "satl_falklands_mare_harbour", [-67.2, -49.0],
                ["rn_ff_type23"]),
        surface("Group S4 - Astute under the Weddell pack", "blue", "satl_falklands_mare_harbour", [-68.0, -49.0],
                ["rn_ssn_astute"]),
        surface("Group S3 - Drake Passage control", "blue", "home_chl_punta_arenas", [-57.3, -64.0],
                ["ch_ffg_karel_doorman"]),
        surface("Red S1 - Russian Antarctic patrol", "red", "red_ant_bellingshausen", [-64.0, -62.5],
                ["rfn_ffg_11356"]),
        surface("Red S2 - Russian Weddell patrol", "red", "red_ant_bellingshausen", [-66.0, -43.5],
                ["rfn_ffg_22350_1-4"]),
        # The campaign transit test, away from the S1 and S2/S4 fights: S5 in
        # open water south-east of Elephant Island (62.5S 52W, 2 %) must cross
        # the ice edge to reach Red S3, a picket in the south-western Weddell
        # pack (67.75S 58W, 79 %). The line gets into 30 % ice (0.4) about
        # 155 nm short of Red S3, so the 0.4 leg is run before DCM's 100 nm
        # contact; both start more than 100 nm from every opposing group and
        # more than 200 nm from where Red S1 and Red S2 make contact
        # (separation_check, transit_check).
        surface("Group S5 - Elephant Island transit", "blue", "satl_falklands_mare_harbour", [-62.5, -52.0],
                ["rn_ff_type23"]),
        surface("Red S3 - Russian Weddell pack picket", "red", "red_ant_bellingshausen", [-67.75, -58.0],
                ["rfn_ffg_11356"]),
    ]
    patrols = [
        {"force": "Red S1 - Russian Antarctic patrol", "points": [[-64.0, -62.5], [-63.5, -61.5]]},
        {"force": "Red S2 - Russian Weddell patrol", "points": [[-66.0, -43.5], [-67.1, -48.2]]},
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
                     "British frigate in the western Weddell pack (67.2S 49W, about 58 % ice), HMS "
                     "Astute under it 48 nm south (68S 49W, about 75 %) and an ice-free control in the "
                     "Drake Passage, with Russian frigates closing on the first two from open water. "
                     "Group S5 off Elephant Island must cross the ice edge to reach a Russian picket "
                     "in the pack (67.75S 58W); with SEST's sea ice on, the campaign map shows the "
                     "ice edge and slows S5 in the ice."),
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
        storm_lines = ice_check(folder, c) if folder in POLAR_ICE else []
        if folder in sidecars:
            weather.write(sidecars[folder], sidecar)
            storm_lines += storm_check(sidecars[folder], c)
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
