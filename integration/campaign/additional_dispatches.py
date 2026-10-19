"""Three optional browser missions; no change to the campaign chronology.

Joint Fires uses the collection's previously unplaced NATO/Russian artillery.
The Far Picture pair is a controlled 2034 test for the reported engagement
range question, not a promise that a paper missile range is a firing solution.
"""
from copy import deepcopy


def missions(U, S):
    fires = dict(
        group="dispatch", num="D9", key="Joint Fires School", place="Tindal training area",
        intro="Training branch, 2030. Use a small reconnaissance UAV and a mixed artillery section to locate and silence two instrumented opposing batteries.",
        special="Standalone training branch. Fixed force; no campaign losses, rewards or units carry into the 2028 story. All live-fire targets are in the marked exercise area.",
        sender="Major Elena Ward, Joint Fires School; Sergeant Ellis, UAV section",
        intent="Use the forward UAV to classify each battery before allocating fire. Keep the K9 and PzH 2000 alive, and leave the marked safety buildings alone.",
        date=(2030, 6, 14), time=(7, 0), sea=1, clouds="Scattered_1", wind="SE",
        difficulty=3, minutes=75, centre=(-14.7, 132.55), geography="coast",
        blue_nation="Australia", red_nation="Russia", role="exercise",
        brief=("TINDAL JOINT FIRES RANGE, 2030. This is a labelled exercise branch. An allied demonstration section brings a K9 and a PzH 2000; the opposing instrumented batteries use 2S19 and 2S43 models. They can return fire. The lesson is reconnaissance, target allocation and counter-battery timing, not a free barrage.\\n\\nELLIS has MOTH 21, a small RQ-7, and a local recovery strip. Work an oblique track, classify both gun positions, then choose which battery to suppress first. Your guns start with weapons held. The range safety buildings are protected. A red spider has been painted under the school sign; Ellis will not say whether it is the original one."),
        forces="One K9, one PzH 2000, one RQ-7 airborne and two reserve UAVs. Opposing: a 2S19 and a 2S43 battery. Protected range-safety buildings.",
        objectives=[("Guns", "Silence both opposing gun batteries", "35,-30,Fail,Main"),
                    ("Section", "Preserve both allied guns", "15,-15,Complete"),
                    ("Safety", "Harm no range-safety buildings", "0,-30,Complete"),
                    ("Observe", "Classify both gun positions", "10,0,None")],
        victory=dict(kind="destroy", stations=["red_guns"], min_units=2, objective="Guns"),
        resolve={"Guns": "victory", "Section": ("protect", "guns"), "Safety": "neutral",
                 "Observe": ("classify", "red_guns", 2)},
        fatal=[], neutral_objective="Safety",
        win="The two batteries are silent. Preserve the UAV recording and compare the first salvo with the corrected fire mission. The range staff can reset the targets; the lesson is yours to keep.",
        lose="Range control ends the serial. Review the reconnaissance track, target allocation and protected buildings before resetting.",
        timeout="The firing window has closed. The unneutralised batteries remain the next crew's problem.",
        stations={"guns": S(-14.75, 132.4, "Allied gun section", 90),
                  "red_guns": S(-14.75, 132.65, "Opposing gun positions", 270),
                  "uav_strip": S(-14.521, 132.378, "UAV recovery section"),
                  "uav": S(-14.66, 132.55, "Moth observation track", 90, 5000),
                  "safety": S(-14.80, 132.70, "Protected range-safety buildings")},
        units=[U("blue", "nato-ground-artillery", "kr_k9", "guns", name="Thunder 11", nation="Australia", weapons="Hold"),
               U("blue", "nato-ground-artillery", "de_pzh2000", "guns", name="Panzer 21", nation="Germany", weapons="Hold"),
               U("blue", "SEST_Allied_Fixes", "sest_uav_forward", "uav_strip", name="Range UAV section", weapons="Hold",
                 air_group=[("usn_rq7705", "Squadron1", 2)]),
               U("blue", "small-medium-uav-series", "usn_rq7705", "uav", name="Moth 21", weapons="Hold",
                 route=[(-14.66, 132.50, 5000), (-14.66, 132.60, 5000)], loop=True),
               U("red", "russian-ground-artillery", "wp_2s19", "red_guns", name="Range battery 31"),
               U("red", "russian-ground-artillery", "wp_2s43", "red_guns", name="Range battery 32"),
               U("neutral", "buildings-targets-missions", "4tentgroup", "safety", name="Range safety camp")],
        window=dict(detachment=False), generation=None, detached=True)

    trial = dict(
        group="dispatch", num="D10", key="The Far Picture - Clear", place="Banda instrumented air range",
        intro="Speculative 2034 test. Compare MALICE, JATM and Gunslinger against the same fighter, stealth-fighter, jammer and AEW target geometry with target sensors disabled.",
        special="Controlled test branch, 2034. Fixed aircraft and identical starting geometry in Clear and Contested. Run fresh copies and use one shooter at a time. No campaign effects.",
        sender="Wing Commander Daniel Ward; Range Controller Ellis",
        intent="Record offered launch range, actual firing range, target aspect, altitude and seeker outcome for each weapon. A kill is a test result, not proof of the range printed in the encyclopedia.",
        date=(2034, 5, 20), time=(10, 0), sea=2, clouds="Clear", wind="SE",
        difficulty=2, minutes=80, centre=(-6.6, 131.0), geography="coast",
        blue_nation="USA", red_nation="China", role="exercise", detached=True,
        brief=("BANDA INSTRUMENTED RANGE, 2034. This is the openly speculative test branch. Two identical US Navy F/A-18F aircraft carry SEST MALICE and SEST AIM-260 respectively; a third carries the AIM-174B Gunslinger interceptor fit. All start at the same altitude and speed, with weapons held. The target set contains a Felon, a J-20A, a J-15D and a KJ-500 at individually separated stations.\\n\\nCLEAR disables target sensors. CONTESTED restores their normal sensor and electronic-warfare systems; nothing else in the scenario changes. Allow the engine to establish its tracks. Select one shooter, retain the others on Hold, and record the offered solution before closing the range. Repeat from a fresh start for the next weapon. The test is not deterministic: crew, detection, target manoeuvre and seeker behaviour can still vary.\\n\\nThe targets fly local loops with weapons held. The range ends when all four are destroyed. You can instead quit after recording a useful comparison. Use the same launch altitude, speed, target bearing and target state in both copies. Roosevelt is not deployed here; all blue aircraft recover to Langgur."),
        forces="Three US Navy F/A-18Fs: four-MALICE fit, eight-JATM fit and Gunslinger interceptor fit. Langgur recovery field. Four target aircraft with weapons held: Su-57, J-20A, J-15D and KJ-500.",
        objectives=[("Trial", "Complete the four target engagements or exit after recording the comparison", "30,0,None,Main"),
                    ("Aircraft", "Preserve the three test aircraft", "10,-10,Complete")],
        victory=dict(kind="destroy", stations=["felon", "dragon", "jammer", "aew"], min_units=4, objective="Trial"),
        resolve={"Trial": "victory", "Aircraft": ("protect", "shooters")},
        fatal=[], neutral_objective="Trial",
        win="The target set is complete. Compare the recorded engagement solutions, flight times and terminal outcomes before changing any missile definition.",
        lose="The test ended before completion. Preserve the observations already recorded.",
        timeout="The range window is closed. Retain the engagement records and reset for a matched comparison.",
        stations={"shooters": S(-8.2, 131.0, "Test shooters", 0, 36000),
                  "felon": S(-5.6, 130.5, "Felon target", 180, 36000),
                  "dragon": S(-5.6, 131.0, "J-20 target", 180, 36000),
                  "jammer": S(-5.6, 131.5, "J-15D target", 180, 36000),
                  "aew": S(-4.5, 131.0, "AEW target", 180, 36000),
                  "strip": S(-5.6614, 132.7314, "Langgur recovery field")},
        units=[U("blue", "SEST_Growler_NGJ_MALICE", "usn_fa-18f", "shooters", squadron="Squadron2", name="Trial MALICE", loadout="SEST_MaliceBlockIII", weapons="Hold"),
               U("blue", "SEST_Growler_NGJ_MALICE", "usn_fa-18f", "shooters", squadron="Squadron2", name="Trial JATM", loadout="SEST_Intercept260", weapons="Hold"),
               U("blue", "SEST_Growler_NGJ_MALICE", "usn_fa-18f", "shooters", squadron="Squadron2", name="Trial Gunslinger", loadout="MurderHornetInterceptor", weapons="Hold"),
               U("blue", "_vanilla", "airfield_small_1", "strip", name="Langgur range recovery", weapons="Hold", air_group=[]),
               U("red", "su-57", "wp_su-57", "felon", name="Target FELON", weapons="Hold"),
               U("red", "j-20", "plaaf_j-20a", "dragon", name="Target DRAGON", weapons="Hold"),
               U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "jammer", name="Target JAMMER", weapons="Hold"),
               U("red", "modern-plan-systems", "plaaf_kj-500", "aew", name="Target AEW", weapons="Hold")],
        window=dict(detachment=False), generation=None)
    for u in trial["units"]:
        if u["side"] == "red":
            la, lo = trial["stations"][u["station"]]["at"]
            u.update(route=[(la-.1, lo, 36000), (la+.1, lo, 36000)], loop=True,
                     disable=("sensors",))
    contested = deepcopy(trial)
    contested.update(num="D11", key="The Far Picture - Contested")
    contested["intro"] = "Speculative 2034 test. The Clear trial's target geometry with the targets' normal sensors and electronic warfare restored."
    for u in contested["units"]:
        u.pop("disable", None)
    return [fires, trial, contested]
