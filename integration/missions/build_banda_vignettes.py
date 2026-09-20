#!/usr/bin/env python3
"""Build small, scored scenarios out of the SEST Banda Front sandbox.

"SEST Banda Front Lean v2" is 5,846 lines: 87 warships and submarines, 396
land units, 37 airliners, four convoys and a whole archipelago. It is a
world, not a mission - it has no objectives, no triggers and no end. Sitting
down to it means choosing your own problem out of a map the size of
Indonesia, which is a fine way to spend an evening and a poor way to spend
forty minutes.

These are the forty-minute versions. Each one lifts a single situation out of
that world - the same ships, the same bases, the same coordinates - and gives
it what the sandbox deliberately lacks: a force small enough to hold in your
head, one problem, a way to win and a way to lose.

WHY THE POSITIONS AND UNITS ARE COPIED RATHER THAN INVENTED

Every unit type and nearly every coordinate here is lifted from the parent
mission. That is not laziness, it is the cheapest available guarantee: the
parent loads, so its types resolve against this exact mod set and its
positions are real water. A scenario written from imagination would need all
of that established from scratch, and would break the first time a mod moved.
validate() re-checks every type against mods-source and the built packs
anyway, so a retired unit fails the build here rather than in the game.

WHAT MAKES THEM DIFFERENT FROM EACH OTHER

Six problems, deliberately not six versions of one problem:

  Sanctioned Cargo      surface interdiction under identification pressure
  Warramunga's Shot     one frigate, one salvo, a target beyond the horizon
  Fujian's Shadow       carrier air defence against a stream raid
  The Biak Regiment     SEAD against a live S-400
  Narco Transit         ASW against something small and quiet in shallow water
  Tigers over Papua     deep strike on relocatable launchers

Usage (repo root):
    python3 integration/missions/build_banda_vignettes.py           # report
    python3 integration/missions/build_banda_vignettes.py --write   # emit
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = ROOT / "integration" / "missions"
MODS = ROOT / "mods-source"
PARENT = (MODS / "_vanilla" / "user" / "missions" / "user_missions"
          / "SEST Banda Front Lean v2.ini")

PREFIX = "SEST Banda"          # every file this script owns starts with this
MAP = ("-6", "130")            # the parent's map centre: lat, lon


def known_types():
    """Every unit id the collection can place - mods plus the built packs."""
    out = set()
    for root in (MODS, ROOT / "integration"):
        for f in root.rglob("*.ini"):
            if f.parent.name in ("aircraft", "vessels", "submarines",
                                 "land_units", "biologic"):
                out.add(f.stem)
    return out


# --- the vignettes -----------------------------------------------------------
# A unit is (type, "x,alt,z", heading, {extra keys}).
# Positions are the parent's own, so the water and the coastlines are real.

V = []

V.append(dict(
    key="Sanctioned Cargo",
    time=(5, 40),
    sea=3, clouds="Scattered_1",
    blue_nation="Australia", red_nation="China",
    brief=(
        "BANDA SEA, first light. Three hulls broke out of the Bayu-Undan "
        "anchorage overnight under a sanctioned flag and are running east for "
        "the Seram passage. Two are lifts. One is an armed escort, and the "
        "fourth contact in the group has been squawking as a merchant since "
        "it sailed - the last four vessels that did that in this corridor "
        "turned out to be the same decoy hull.\\n\\n"
        "You have ANZAC and ARUNTA, detached from the Darwin surface group "
        "and 40 nautical miles south of the lane. The Banda corridor carries "
        "real traffic: a vehicle carrier and two fishing boats are inside "
        "your weapons envelope right now and none of them are yours to sink. "
        "Identify before you shoot. The lifts must not reach the passage."),
    objectives=[
        ("Lifts", "Stop both sanctioned lifts", "20,-20,Fail,Main"),
        ("Neutrals", "Harm no neutral shipping", "0,-25,Complete"),
        ("Ships", "Bring both frigates home", "5,-10,Complete"),
    ],
    blue=[
        ("ran_ffh_anzac", "6,0,-46", 70, {"VariantReference": "Variant1"}),
        ("ran_ffh_anzac", "4.5,0,-49", 70, {"VariantReference": "Variant2"}),
    ],
    blue_names=["HMAS Anzac", "HMAS Arunta"],
    red=[
        ("civ_ms_ritina", "1.5,0,-49.5", 85, {}),
        ("civ_ms_irkutsk", "3,0,-51", 85, {}),
        ("wp_ms_roro_b", "6,0,-52.5", 85, {}),
        ("wp_ms_mercur_decoy", "7.5,0,-54", 85, {}),
    ],
    red_names=["MV Banda Lift 1 [SANCTIONED]", "MV Banda Lift 2 [SANCTIONED]",
               "MV Banda Escort 3 [SANCTIONED]", "MV Banda Escort 4 [SANCTIONED]"],
    neutral=[
        ("civ_ms_car_carrier_a", "-4,0,-44", 85, {}),
        ("civ_fv_sterntrawler_a", "9,0,-44", 200, {}),
        ("civ_fv_sterntrawler_c", "-1,0,-57", 20, {}),
    ],
    neutral_names=["Banda Vehicle North", "Banda Fishing North", "Banda Fishing South"],
    win_units="Taskforce2Vessel1,Taskforce2Vessel2",
    win_min=2,
    win_text=("Both lifts are on the bottom and the passage is closed. The "
              "escort can run home and explain it."),
    lose_text="Both frigates lost. The lane is open and Darwin knows it.",
))

V.append(dict(
    key="Warramunga's Shot",
    time=(14, 10),
    sea=4, clouds="Overcast",
    blue_nation="Australia", red_nation="China",
    brief=(
        "TIMOR SEA. A red surface action group is working south-west out of "
        "the Sunrise field, screening the second sanctioned convoy. You are "
        "WARRAMUNGA, alone, 60 nautical miles on their disengaged bow with "
        "the weather in your favour and a full deck-launcher load of Naval "
        "Strike Missile.\\n\\n"
        "This is a shooting problem, not a fair fight. The NSM outranges "
        "anything they can answer with, but only while they do not know where "
        "you are: your own radar is the thing most likely to tell them. The "
        "Seahawk is the other way to find them. Get a solution, take the "
        "shot, and be somewhere else when the counter-battery arrives."),
    objectives=[
        ("Escort", "Sink the armed escort", "20,-15,Fail,Main"),
        ("Lifts", "Stop the sanctioned lifts", "10,0,None"),
        ("Warramunga", "Survive", "10,-20,Complete"),
    ],
    blue=[
        ("ran_ffh_anzac", "-150,0,-250", 300, {"VariantReference": "Variant3"}),
    ],
    blue_names=["HMAS Warramunga"],
    red=[
        ("wp_ms_andizhan_armed", "-100.5,0,-234", 240, {}),
        ("civ_ms_ritina", "-106.5,0,-229.5", 240, {}),
        ("civ_ms_bulk", "-105,0,-231", 240, {}),
        ("civ_ms_metallurg_anosov", "-102,0,-232.5", 240, {}),
    ],
    red_names=["MV Sunrise Escort 4 [SANCTIONED]", "MV Sunrise Lift 1 [SANCTIONED]",
               "MV Sunrise Lift 2 [SANCTIONED]", "MV Sunrise Lift 3 [SANCTIONED]"],
    neutral=[
        ("civ_fv_sterntrawler_b", "-130,0,-245", 90, {}),
    ],
    neutral_names=["Timor Fishing North"],
    win_units="Taskforce2Vessel1",
    win_min=1,
    win_text=("The escort is gone and the convoy is naked. NSM works when "
              "nobody sees you coming."),
    lose_text="WARRAMUNGA lost. They found you first.",
))

V.append(dict(
    key="Fujian's Shadow",
    time=(9, 20),
    sea=2, clouds="Scattered_1",
    blue_nation="USA", red_nation="China",
    brief=(
        "NORTH OF THE BANDA SEA. FORD is 200 nautical miles south of the "
        "Fujian group and both sides know it. The red carrier has been "
        "cycling deck launches for an hour and the pattern has stopped "
        "looking like training: two sweeps forward, then a stream behind "
        "them.\\n\\n"
        "You have the carrier, two Burkes and the Hobart. The F-35Cs and the "
        "JATM are the reason this is survivable - the missile outranges "
        "theirs and the aircraft sees first - but there are more of them than "
        "you have missiles for, and the Growlers can only blind one axis at a "
        "time. Keep FORD alive. Everything else is negotiable."),
    objectives=[
        ("Ford", "Keep FORD afloat and fighting", "25,-30,Complete,Main"),
        ("Raid", "Break up the strike", "15,-10,Fail"),
        ("Screen", "Keep the screen intact", "5,-5,Complete"),
    ],
    blue=[
        ("usn_cvn_ford", "120,0,-276", 90, {
            "CustomAirGroup": "True",
            "_air": ["usn_f-35c=Squadron1,16", "usn_ea-18g=Squadron1,6",
                     "usn_fa-18f_blk3=Squadron1,12", "usn_e-2d=Squadron4,4",
                     "usn_mh-60r_26=Squadron17,6"]}),
        ("usn_ddg_burke_f3_125", "123,0,-274.5", 90, {}),
        ("usn_ddg_burke_f2a_113", "117,0,-277.5", 90, {}),
        ("ran_ddg_hobart", "117,0,-273", 90, {"VariantReference": "Variant1"}),
    ],
    blue_names=["USS Gerald R. Ford", "Aegis Screen East", "Aegis Screen West",
                "HMAS Hobart"],
    red=[
        ("plan_cv_type_003", "-1.38,0,77.68", 180, {
            "CustomAirGroup": "True",
            "_air": ["plan_j-35=Squadron1,16", "plan_j-15t=Squadron1,16",
                     "plan_j-15dt=Squadron1,4", "plan_kj-600=Squadron1,4"]}),
        ("plan_type_055_2026", "1.62,0,79.18", 180, {}),
        ("plan_type_055_2026", "-4.38,0,76.18", 180, {}),
        ("plan_type_052d_p3", "-4.38,0,80.68", 180, {}),
    ],
    red_names=["Fujian", "Type 055 Screen One", "Type 055 Screen Two",
               "Type 052D Screen One"],
    neutral=[],
    neutral_names=[],
    win_units="Taskforce2Vessel1",
    win_min=1,
    win_text="Fujian is burning. The Banda front just became a one-carrier war.",
    lose_text="FORD is gone. There is no second carrier this side of Guam.",
))

V.append(dict(
    key="The Biak Regiment",
    time=(4, 30),
    sea=2, clouds="Clear",
    blue_nation="USA", red_nation="Russia",
    brief=(
        "BIAK, 0430. A Russian S-400 regiment sits on the airfield with its "
        "big radar up, and while it is up nothing allied flies the northern "
        "route. The airfield has a modern fighter regiment on it as well.\\n\\n"
        "You have Growlers and Eagles out of the forward field. The Growler's "
        "jamming buys you the approach, not the kill: the HARM shot has to "
        "come from inside the engagement envelope, which is the whole problem "
        "with a 40N6. Pull the radar off the air, put the launchers down, and "
        "get the package home. Losses here are measured in aircraft you do "
        "not get back for the rest of the campaign."),
    objectives=[
        ("SAM", "Destroy the S-400 site", "25,-20,Fail,Main"),
        ("Field", "Crater the airfield", "10,0,None"),
        ("Package", "Bring the package home", "10,-15,Complete"),
    ],
    blue=[
        ("usn_ddg_burke_f3_125", "300,0,250", 45, {}),
    ],
    blue_names=["Tomahawk Shooter"],
    blue_air=[
        ("usn_ea-18g_2020", "330,28000,255", 40, {"LoadoutVariant": "SEAD"}),
        ("usn_ea-18g_2020", "332,28000,253", 40, {"LoadoutVariant": "SEAD"}),
        ("usaf_f-15ex_SEII", "328,30000,250", 40, {"LoadoutVariant": "AAMT260"}),
        ("usaf_f-15ex_SEII", "326,30000,248", 40, {"LoadoutVariant": "AAMT260"}),
    ],
    blue_air_names=["Growler 11", "Growler 12", "Eagle 21", "Eagle 22"],
    red=[],
    red_names=[],
    red_land=[
        ("wp_sam_site_sa-21", "365.01,low,289.6", 0, {}),
        ("wp_airbase_modern", "366.07,low,290.66", 0, {}),
    ],
    red_land_names=["Biak S-400 Regiment", "Biak Airfield"],
    neutral=[],
    neutral_names=[],
    win_units="Taskforce2LandUnit1",
    win_min=1,
    win_text="The radar is off the air for good. The northern route is open.",
    lose_text="The package is gone and the regiment is still shooting.",
))

V.append(dict(
    key="Narco Transit",
    time=(2, 15),
    sea=1, clouds="Clear",
    blue_nation="Australia", red_nation="China",
    brief=(
        "TIMOR CORRIDOR, middle watch. Border Force has a pattern: something "
        "small and very quiet runs this line twice a week, snorting at "
        "periscope depth between the fishing fleets, and nothing with a hull "
        "number has ever caught it. Tonight you have the Anzac's Seahawk and "
        "a sea state of one.\\n\\n"
        "A narco boat is a poor sonar target and a worse visual one, and the "
        "trawlers out here work at night with their gear down. You are "
        "looking for something the size of a bus that does not want to be "
        "found, in water busy enough that every contact has to be resolved "
        "before it is attacked."),
    objectives=[
        ("Boat", "Find and stop the transit", "25,-15,Fail,Main"),
        ("Fishing", "Leave the fishing fleet alone", "0,-25,Complete"),
    ],
    blue=[
        ("ran_ffh_anzac", "-60,0,-345", 20, {"VariantReference": "Variant5"}),
    ],
    blue_names=["HMAS Parramatta"],
    red_sub=[
        ("_narco_narcosub_adv", "-72,periscope,-360", 30, {}),
    ],
    red_sub_names=["Narco Transit Timor Northbound"],
    red=[],
    red_names=[],
    neutral=[
        ("civ_fv_fishingboat_b", "-68,0,-352", 140, {}),
        ("civ_fv_fishingboat_c", "-77,0,-366", 300, {}),
        ("civ_fv_sampan", "-64,0,-341", 95, {}),
    ],
    neutral_names=["Timor Fishing North", "Timor Fishing South", "Timor Sampan"],
    win_units="Taskforce2Submarine1",
    win_min=1,
    win_text="Transit stopped. Border Force will want the recording.",
    lose_text="It got through. Again.",
))

V.append(dict(
    key="Tigers over Papua",
    time=(3, 50),
    sea=2, clouds="Scattered_1",
    blue_nation="USA", red_nation="China",
    brief=(
        "PAPUA, before dawn. A DF-21D and a DF-26B are sitting on an airlift "
        "field 600 miles inside the red lodgement, and while they are there "
        "no allied carrier operates east of the Banda Sea. They move at "
        "first light.\\n\\n"
        "You have a single B-1B staging out of the south with the ARRW "
        "testbed fit - six rounds, hypersonic, launched from outside "
        "everything the lodgement owns. That is the whole plan and the whole "
        "margin: the launchers are soft, the window is short, and there is no "
        "second pass. Put the TELs down before the sun comes up."),
    objectives=[
        ("TELs", "Destroy both launchers", "30,-25,Fail,Main"),
        ("Field", "Hit the airlift field", "5,0,None"),
        ("Lancer", "Bring the bomber home", "15,-20,Complete"),
    ],
    blue=[],
    blue_names=[],
    blue_air=[
        ("usaf_b-1b_dts", "560,32000,-260", 20, {"LoadoutVariant": "ARRWTestbed"}),
    ],
    blue_air_names=["Bone 01"],
    red=[],
    red_names=[],
    red_land=[
        ("pla_df-21d_tel", "624.95,low,-150.24", 0, {}),
        ("pla_df-26b_tel", "625.81,low,-151.47", 0, {}),
        ("plaaf_airlift_airbase", "625.08,low,-151.2", 0, {}),
    ],
    red_land_names=["DF-21D Launcher", "DF-26B Launcher", "Papua Airlift Field"],
    neutral=[],
    neutral_names=[],
    win_units="Taskforce2LandUnit1,Taskforce2LandUnit2",
    win_min=2,
    win_text="Both launchers are wreckage. The eastern Banda is open again.",
    lose_text="The launchers moved. Everything east of here is now in range.",
))


def block(tag, unit, extra_order=("VariantReference",)):
    ty, pos, hdg, extra = unit
    out = [f"[{tag}]", f"Type={ty}"]
    for k in extra_order:
        if k in extra:
            out.append(f"{k}={extra[k]}")
    out += ["UnlimitedFuel=False", "WeaponStatus=Free", "RadarsActive=True",
            "CrewSkill=Trained", "Morale=3",
            f"RelativePositionInNM={pos}", f"Heading={hdg}"]
    for k, v in extra.items():
        if k in extra_order or k.startswith("_"):
            continue
        out.append(f"{k}={v}")
    for line in extra.get("_air", []):
        out.append(line)
    return "\n".join(out) + "\n"


def render(v):
    L, blue_air, red_land = [], v.get("blue_air", []), v.get("red_land", [])
    red_sub = v.get("red_sub", [])
    name = f"{PREFIX} - {v['key']}"

    L.append("[Language_en]")
    L.append(f"Name={name}")
    L.append(f"Description={v['brief']}")
    for oid, text, _ in v["objectives"]:
        L.append(f"Objective_{oid}={text}")
    L.append(f"Taskforce1StartMessage=<color=yellow>{v['key']}</color>|{v['brief']}")
    L.append(f"Taskforce1VictoryMessage=<color=lime>Mission complete.</color>|{v['win_text']}")
    L.append(f"Taskforce1DefeatMessage=<color=red>Mission failed.</color>|{v['lose_text']}")
    L.append(f"Taskforce2VictoryMessage=<color=lime>Red victory.</color>|{v['lose_text']}")
    L.append(f"Taskforce2DefeatMessage=<color=red>Red defeat.</color>|{v['win_text']}")
    if v["neutral"]:
        L.append("NeutralLossMessage=<color=orange>Neutral vessel hit.</color>|"
                 "A neutral crew is in the water. That will be on the record.")
    # per-unit names
    for fam, key in (("Taskforce1Vessel", "blue_names"), ("Taskforce2Vessel", "red_names"),
                     ("NeutralVessel", "neutral_names"), ("Taskforce1Aircraft", "blue_air_names"),
                     ("Taskforce2LandUnit", "red_land_names"),
                     ("Taskforce2Submarine", "red_sub_names")):
        for i, n in enumerate(v.get(key, []), start=1):
            L.append(f"{fam}{i}NameOverride={n}")
    L.append("")

    L.append("[Environment]")
    L += [f"Date=2026,9,17", f"Time={v['time'][0]},{v['time'][1]}",
          "ConvertTimeToLocal=True", f"SeaState={v['sea']}", f"Clouds={v['clouds']}",
          "WindDirection=SE", f"MapCenterLatitude={MAP[0]}",
          f"MapCenterLongitude={MAP[1]}", "LoadBackgroundData=False", ""]

    L.append("[Mission]")
    L += ["Difficulty=1", "PlayerTaskforce=Taskforce1", "EnemyTaskforce=Taskforce2",
          f"Taskforce1_Nation={v['blue_nation']}", f"Taskforce2_Nation={v['red_nation']}",
          f"NumberOfTaskforce1Vessels={len(v['blue'])}",
          f"NumberOfTaskforce2Vessels={len(v['red'])}",
          f"NumberOfNeutralVessels={len(v['neutral'])}",
          f"NumberOfTaskforce1Aircraft={len(blue_air)}",
          f"NumberOfTaskforce2Submarines={len(red_sub)}",
          f"NumberOfTaskforce2LandUnits={len(red_land)}"]
    n_trig = 3 + (1 if v["blue"] or blue_air else 0) + (1 if v["neutral"] else 0)
    L.append(f"NumberOfTriggers={n_trig}")
    L.append("")

    for i, u in enumerate(v["blue"], 1):
        L.append(block(f"Taskforce1Vessel{i}", u))
    for i, u in enumerate(blue_air, 1):
        # An airborne aircraft carries a SquadronReference in every example
        # the parent and the stock missions give; Squadron1 exists on all
        # three types used here (checked: 2, 8 and 19 squadrons declared).
        ty, pos, hdg, extra = u
        extra = dict(extra, SquadronReference="Squadron1")
        L.append(block(f"Taskforce1Aircraft{i}",
                       (ty, pos, hdg, extra), ("SquadronReference",)))
    for i, u in enumerate(v["red"], 1):
        L.append(block(f"Taskforce2Vessel{i}", u))
    for i, u in enumerate(red_sub, 1):
        L.append(block(f"Taskforce2Submarine{i}", u))
    for i, u in enumerate(red_land, 1):
        L.append(block(f"Taskforce2LandUnit{i}", u))
    for i, u in enumerate(v["neutral"], 1):
        L.append(block(f"NeutralVessel{i}", u))

    L.append("[Taskforce1_Objectives]")
    L.append("#ID=CompletedScore,FailedScore,StatusAtMissionEnd")
    for oid, _, spec in v["objectives"]:
        L.append(f"{oid}={spec}")
    L.append("")

    n = 0
    n += 1
    L += [f"[Trigger{n}]  #Mission exit", "Name=Mission exit",
          "Disabled=True", "Condition_Type=Time", "Condition_Time=90",
          "Action_EndMission=True", "Action_EndMissionDelay=0", ""]
    n += 1
    L += [f"[Trigger{n}]  #Start message", "Name=Start message",
          "Condition_Type=Time", "Condition_Time=0.5",
          "Action_Taskforce1_Message=Taskforce1StartMessage", ""]
    n += 1
    L += [f"[Trigger{n}]  #Objective met", "Name=Objective met",
          "Condition_Type=UnitDestroyed", f"Condition_Units={v['win_units']}",
          f"Condition_MinimumUnits={v['win_min']}",
          "Action_Taskforce1_Message=Taskforce1VictoryMessage",
          "Action_Taskforce2_Message=Taskforce2DefeatMessage",
          "Action_Victory=Taskforce1",
          f"Action_ObjectivesCompleted={v['objectives'][0][0]}", ""]
    if v["blue"] or blue_air:
        n += 1
        L += [f"[Trigger{n}]  #Player force gone", "Name=Player force gone",
              "Condition_Type=HasNoUnitsOfType", "Condition_Taskforce=Taskforce1",
              f"Condition_UnitType={'Vessel' if v['blue'] else 'Aircraft'}",
              "Action_Taskforce1_Message=Taskforce1DefeatMessage",
              "Action_Victory=Taskforce2", "Action_EnableTriggers=Trigger1",
              "Action_ReactivateTriggers=Trigger1", ""]
    if v["neutral"]:
        n += 1
        units = ",".join(f"NeutralVessel{i}" for i in range(1, len(v["neutral"]) + 1))
        L += [f"[Trigger{n}]  #Neutral harmed", "Name=Neutral harmed",
              "Condition_Type=UnitDestroyed", f"Condition_Units={units}",
              "Condition_MinimumUnits=1",
              "Action_Taskforce1_Message=NeutralLossMessage",
              "Action_ObjectivesFailed=Neutrals" if any(
                  o[0] == "Neutrals" for o in v["objectives"]) else
              "Action_ObjectivesFailed=Fishing", ""]
    assert n == n_trig, f"{v['key']}: wrote {n} triggers, declared {n_trig}"
    return name, "\n".join(L) + "\n"


def validate(known):
    problems = []
    for v in V:
        for group in ("blue", "red", "neutral", "blue_air", "red_land", "red_sub"):
            for ty, _pos, _hdg, extra in v.get(group, []):
                if ty not in known:
                    problems.append(f"{v['key']}: {group} type {ty!r} is not defined "
                                    "by any mod or pack")
                # An air group is a list of "<unit id>=SquadronN,count" lines and
                # an unresolvable id there is just as fatal as an unresolvable
                # hull - it is simply harder to see, so check it here too.
                for line in extra.get("_air", []):
                    aid = line.split("=")[0].strip()
                    if aid not in known:
                        problems.append(f"{v['key']}: {ty} air group names {aid!r}, "
                                        "which is not defined by any mod or pack")
        for key in ("blue", "red", "neutral", "blue_air", "red_land", "red_sub"):
            names = v.get(key.split("_")[0] + "_names" if "_" not in key
                          else key + "_names", [])
            if names and len(names) != len(v.get(key, [])):
                problems.append(f"{v['key']}: {key} has {len(v.get(key, []))} unit(s) "
                                f"but {len(names)} name(s)")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not PARENT.exists():
        sys.exit(f"parent mission missing: {PARENT} - re-export mods-source")
    known = known_types()
    problems = validate(known)
    if problems:
        sys.exit("validation failed:\n  " + "\n  ".join(problems))

    for v in V:
        name, text = render(v)
        dst = MISSIONS / f"{name}.ini"
        if args.write:
            dst.write_text(text, encoding="utf-8")
        units = sum(len(v.get(g, [])) for g in
                    ("blue", "red", "neutral", "blue_air", "red_land", "red_sub"))
        print(f"  {'wrote' if args.write else 'would write'} {name}.ini  "
              f"({units} units, {len(v['objectives'])} objectives)")
    print(f"\n{len(V)} vignettes from {PARENT.name}"
          + ("" if args.write else " - re-run with --write to emit"))


if __name__ == "__main__":
    main()
