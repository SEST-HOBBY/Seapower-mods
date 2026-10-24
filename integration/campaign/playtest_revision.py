"""Authored revisions following the d90ac062 PC playtest.

Keep the existing mission dictionaries and their objective references. This
module changes the named detachments and records damage, rather than replacing
the campaigns with new templates. Imported after Southern Watch's old tables.
"""
from copy import deepcopy
from pathlib import Path
import sys

# Campaign packages also import campaign_data directly, before build_pack has
# installed its paths (including unittest discovery through those packages).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.carrier_wings import FORD_WING


ROOSEVELT_WING = [
    ("usn_fa-18f", "Squadron2", 12),
    ("usn_fa-18e", "Squadron2", 24),
    ("usn_f-35c", "Squadron10", 14),
    ("usn_ea-18g", "Squadron1", 6),
    ("usn_e-2d", "Squadron3", 4),
    ("usn_mh-60r", "Squadron14", 6),
]


def deepen_broken_wake(m, U, S):
    """A choice between screening, ASW and breaking a time-limited relay."""
    m["difficulty"] = 4
    # Use the coastline extract for this operation. The older harvested pool
    # would move the eastern submarine almost 28 nm away from its patrol box.
    m["geography"] = "coast"
    m["intro"] = ("Contingency. Escort the six-knot Stuart through a submarine datum and a civilian lane. "
                  "An armed relay trawler is preparing a second attack; stopping it early can prevent that attack.")
    m["special"] = ("Detached recovery: Stuart, thirty-one wounded, six knots. Preserve the civilian traffic. "
                    "Sheean supports the underwater screen with weapons held. The first air raid is committed; "
                    "destroying the armed relay before minute 25 cancels the later missile-boat attack.")
    m["stations"]["relay"] = S(-5.82, 130.39, "Eastern relay search sector", 205)
    m["stations"]["followup"] = S(-5.62, 130.62, "Eastern fast-craft approach", 225)
    m["stations"]["sub_support"] = dict(S(-6.30, 130.52, "Sheean eastern barrier", 250), coastal=True)
    m["units"] += [
        U("red", "armed-merchantmen", "civ_fv_okean_armed", "relay", name="Banda Surveyor",
          route=[(-6.00, 130.28, 0)], telegraph=2),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "followup", name="Meridian 23",
          enter=25, route=[(-6.00, 130.35, 0), (-6.20, 130.20, 0)], telegraph=4),
        U("blue", "SEST_RAN_Fleet", "ran_ssg_collins", "sub_support", name="HMAS Sheean", variant="Variant5",
          weapons="Hold", depth="belowlayer", telegraph=2, independent=True,
          route=[(-6.30, 130.37, "belowlayer")]),
    ]
    m["objectives"] += [
        ("RelayID", "Classify the armed relay trawler", "5,0,None"),
        ("Relay", "Silence the armed relay trawler", "5,0,None"),
        ("ClearDatum", "Neutralize the Kilo on the recovery approach", "10,0,None"),
        ("Sheean", "Preserve SHEEAN", "5,-5,Complete"),
    ]
    m["resolve"].update(RelayID=("classify", "relay", 1), Relay=("destroy", "relay", 1),
                          ClearDatum=("destroy", "red_sub", 1), Sheean=("protect", "sub_support"))
    m["reinforcement_cutoffs"] = [dict(source=["relay"], reinforcements=["followup"], minute=25,
        intel="ELLIS: The armed relay was silenced before its scheduled transmission. The follow-on fast-craft attack has been cancelled. The Kilo and the already committed J-15Ds are unaffected.")]
    m.setdefault("reports", []).extend([
        dict(minute=18, intel="ELLIS: Seven minutes to the relay deadline. If Banda Surveyor is still afloat, classify the eastern contact and decide whether you can stop it without stripping Stuart's screen. This report gives no target reveal."),
        dict(minute=35, intel="STUART / CHIEF MASON: Shaft vibration is steady at six knots. Keep the screen ahead of our bow and the merchants clear of the recovery lane. Nobody in my engine room has authorized a dash."),
    ])
    m["brief"] = ("BANDA SEA, before dawn. STUART has one shaft, thirty-one wounded and a six-knot engineering limit. "
        "Bring her south-south-east to Darwin's tug handover line. The recovery remains the main task; sinking "
        "the opposing ships is not a substitute for a live frigate at the line.\\n\\n"
        "SCREEN AND SEARCH: A Kilo is working the south-western approach. Flying Shark 31 and 32 are already "
        "committed and join from the north at minute five. Keep the helicopter or an escort ahead of Stuart "
        "while the air-defence ship covers the straggler. HMAS SHEEAN is allocated on the eastern barrier, "
        "submerged with weapons held. You command her; deconflict her patrol from the flight's torpedo attacks. "
        "She is a theatre attachment for this operation, not a new permanent roster purchase.\\n\\n"
        "BREAK THE RELAY: An armed Okean trawler, operating as BANDA SURVEYOR, is east of the recovery lane. "
        "She is due to release a fast missile craft at minute twenty-five. Identify the contact among the "
        "civilian traffic. If you destroy this hostile relay before that deadline, the follow-on craft never "
        "joins. Once released, sinking the relay will not recall it. The first air raid and Kilo are independent. "
        "Continue searching for the other threats with your own sensors.\\n\\n"
        "CHOICES AND CONSEQUENCES: Split the screen to hunt the relay and risk the southern submarine approach, "
        "or keep the escorts close and prepare for the later surface attack. Classifying the relay, silencing it, "
        "neutralizing the Kilo and preserving Sheean earn separate credit. They are optional; the main recovery "
        "ends the mission, so do them before Stuart reaches the line if you choose. MT BANDA SPIRIT and "
        "MV TANIMBAR TRADER remain neutral throughout. Harming either fails the operation.\\n\\n"
        "CHIEF MASON has taped a red spider over the broken shaft repeater. Mercer says the spider is the "
        "only member of this detachment authorized to move faster than six knots.")
    m["forces"] = ("Your recovery detachment and Stuart; Sheean on an independent eastern submarine barrier, "
        "weapons held. Two protected neutral merchants. Opposing: one Kilo, a J-15D strike pair at minute five, "
        "one armed relay trawler and one fast missile craft at minute twenty-five if the relay survives its deadline.")
    m["intent"] = ("Bring Stuart to the line at six knots. Assign separate ASW and air-defence sectors. "
        "Use Sheean without confusing her with TANGO. Break the eastern relay before minute 25 if the screen "
        "can spare the effort; otherwise meet the fast craft without abandoning the wounded or firing on a merchant.")


def apply_watch(missions, U, S):
    by = {m["num"]: m for m in missions}
    deepen_broken_wake(by["C2"], U, S)
    door, ring, service = (by[n] for n in ("08", "O7", "09"))
    by["O4"]["intent"] = by["O4"]["intent"].replace(
        "Langgur is where The Open Door's F-35 pair will recover", "Langgur supports the forward aircraft for The Open Door and Second Ring")
    door["stations"]["bombers"] = S(-5.8, 135.9, "ARRW launch line", 10, 32000)
    door["stations"]["tindal"] = S(-14.521, 132.378, "RAAF Base Tindal")
    door["units"] = [u for u in door["units"]
                     if not (u["side"] == "blue" and u["type"] == "raaf_f-35a")]
    door["units"] += [U("blue", "SEST_B52_ARRW", "dts_b-52h", "bombers",
                         name=f"Doom {n}", loadout="Strike183", alt=32000)
                      for n in (41, 42)]
    door["units"].append(U("blue", "SEST_RAAF_Bases", "airbase_raaf_tindal", "tindal",
                           name="RAAF Base Tindal", nation="australia", weapons="Hold"))
    for u in door["units"]:
        if u["type"] == "usn_cvn_nimitz_2025":
            u["air_group"] = deepcopy(ROOSEVELT_WING)
            u["ready"] = [("usn_ea-18g", "Squadron1", "SEST_SEAD120D", 2, 0)]
        if u["type"] == "usn_ea-18g" and u["station"] == "strike":
            u["squadron"] = "Squadron1"
            u["name"] = "Grizzly 31"
    # Specific sections, not the whole 'field' station containing civilians.
    flags = (("SW08MainFieldLost", "field#3", "Enclave runway complex"),
             ("SW08DispersalLost", "field#4", "Russian dispersal"),
             ("SW08HindLost", "detach#1", "Hind detachment"),
             ("SW08HipEWLost", "detach#3", "Hip electronic-warfare detachment"))
    for name, ref, label in flags:
        door.setdefault("declares", []).append(name)
        door.setdefault("flags", []).append(dict(name=name, units=[ref],
            intel=f"DAMAGE ASSESSMENT: {label} destroyed. Second Ring will reflect this loss."))
    door["objectives"].append(("Airfield", "Disable the military runway complex", "10,0,None"))
    door["resolve"]["Airfield"] = ("destroy", "field#3", 1)
    door["objectives"].append(("Dispersal", "Disable the military dispersal complex", "5,0,None"))
    door["resolve"]["Dispersal"] = ("destroy", "field#4", 1)
    door["brief"] = door["brief"].replace(
        "The F-35 pair carries the follow-up strike, out of Langgur on the Kai group - Captain Prasetyo has lent the strip for this one operation and not an hour longer, and the pair recovers there, not on the carrier.",
        "DOOM 41 and 42, B-52H with conventional ARRW, have the opening airfield strike. Fire early from the southern launch line; target the military runway and dispersal complexes. They recover to Tindal. Civilian shelters and the power station remain protected. Captain Prasetyo keeps Langgur open for local aircraft.")
    door["brief"] += ("\\n\\nROOSEVELT AIR OPERATIONS: The carrier has a specified US Navy wing, including six Growlers and US-flagged Super Hornets. Two Growlers are ready for launch. The airborne Growler is also American. Military buildings and detached helicopters destroyed here remain absent in Second Ring; mobile replacement SAMs arrive independently. Destroying the airfield is useful, but the relief movement remains the main task.")
    door["forces"] = ("Two B-52H with conventional ARRW and a US Navy Growler; Roosevelt's 66-aircraft US wing, including six Growlers; two relief transports; Texaco 52 and the Langgur detachment. Texaco 53 joins after Weather Alternate. Opposing: S-400, military airfield/dispersal, ballistic launcher and Russian tactical aviation. Civilian buildings are protected.")

    ring["stations"]["bombers"]["label"] = "Four-ship JSM package"
    ring["intro"] = "Optional. The day after The Open Door, a mobile replacement missile belt covers the surviving enclave infrastructure. Take its engagement radars down before the next launch south."
    ring["units"] = [u for u in ring["units"] if u["type"] != "dts_b-52h"]
    ring["units"][0:0] = [U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "bombers",
                            squadron="Squadron3", name=f"Lightning {n}",
                            loadout="StrikeLongRangeStealth", alt=30000)
                            for n in range(41, 45)]
    ring["objectives"] = [(oid, "Bring all four JSM F-35As home" if oid == "Bombers" else text, score)
                           for oid, text, score in ring["objectives"]]
    ring["brief"] = ("BIAK, THE NEXT NIGHT. The Open Door's B-52s have gone back to the southern launch pool. LIGHTNING 41 to 44 are four RAAF F-35As carrying internal JSM from Langgur, supported by Grizzly's conventional SEAD pair, two Eagle IIs and Wedgetail 04. Suppress the new S-350 and S-300 engagement radars before committing the JSM package.\\n\\nThe mobile missile belt was delivered separately. The runway, Russian dispersal, Hind and Hip EW assets are present only if they survived The Open Door. Losing a complex removes its local fighter support, not the replacement SAMs. A standalone Second Ring starts with the surviving-defence case because it has no earlier damage record.\\n\\nDestroy both engagement radars. The Buk, Nebo and Iskander are secondary targets; the relief ship and town remain protected. Prasetyo's ground crew have chalked a small red spider under the squadron board. Ward says it is not a kill marking.")
    ring["special"] = "Optional operation: four RAAF F-35As with internal JSM, two Growlers, two F-15EX and Wedgetail. Your standing task group remains elsewhere. Earlier airfield and helicopter losses carry forward; the replacement SAM belt is independent."
    ring["intent"] = "Use the four JSM Lightnings and the conventional SEAD pair to remove the two engagement radars. Check the current airfield damage report before planning the approach. Bring the package home to Langgur."
    ring["sender"] = "Wing Commander Daniel Ward; Captain Ratna Prasetyo at Langgur"
    ring["forces"] = "Four RAAF F-35As with JSM, two RAAF Growlers, two F-15EX and Wedgetail. New S-350/S-300PMU2, Buk, Nebo and Iskander; surviving enclave airfield, dispersal, fighters and helicopters. Protected relief shipping."
    ring["win"] = "Both engagement radars are down. The four-ship JSM package can disengage; Ballistic Shield will meet launchers without this radar cover."
    ring["lose"] = "The replacement belt still covers the enclave. Account for every Lightning before planning the next sortie."
    ring["stations"]["old_field"] = deepcopy(door["stations"]["field"])
    ring["stations"]["old_helos"] = S(-1.2, 136.4, "Surviving detachment", 180, 4000)
    for uid, variable, label, mod in (
        ("pla_airbase_modern", "SW08MainFieldLost", "Surviving runway complex", "modern-chinese-airbase"),
        ("wp_airbase_modern", "SW08DispersalLost", "Surviving dispersal", "modern-russian-airbase")):
        ring["units"].append(U("red", mod, uid, "old_field", name=label,
                               air_group=[], spawn_if=(variable, "IsFalse")))
    for uid, var, mod, name in (("wp_mi-24p", "SW08HindLost", "mi-24", "Hind 21"),
                                ("wp_mi-8ew", "SW08HipEWLost", "mi-8ew", "Hip EW 43")):
        ring["units"].append(U("red", mod, uid, "old_helos", name=name,
                               spawn_if=(var, "IsFalse"), weapons="Hold"))
    for u in ring["units"]:
        if u["type"] == "plaaf_j16":
            u["spawn_if"] = ("SW08MainFieldLost", "IsFalse")
    # Conditional units must not share a formation with a differently gated unit.
    for u in ring["units"]:
        if u["station"] in ("old_field", "old_helos"):
            key = "survivor_" + u["type"]
            ring["stations"][key] = deepcopy(ring["stations"][u["station"]])
            u["station"] = key

    service["stations"]["support"].update(spawn_spacing=.25, formation_spacing=.25)
    for u in service["units"]:
        if u["type"] in ("ran_ssg_collins", "ran_aor_supply"):
            u["telegraph"] = 2
            u["route"] = [(-13.78, 148.35, 0)]
            if u["type"] == "ran_ssg_collins":
                u["depth"] = 0
    service["stations"]["red_surface"] = S(-13.05, 149.0, "Corvette approach", 215)
    service["units"].append(U("red", "russian-navy-21", "rfn_cvt_20380_7-12", "red_surface",
                               name="Corvette STEREGUSHCHIY", enter=12,
                               route=[(-13.36, 148.78, 0)], telegraph=3))
    service["brief"] += ("\\n\\nSERVICE DETAIL: Collins uses the collection's actual Collins hull and begins on the surface at the rendezvous. Collins and Stalwart both have the four-knot service telegraph selected. They creep south inside the box during the check; after the 35-minute signal, order withdrawal speed and depth yourself. The clock does not verify depth.\\n\\nKILA: A light Russian corvette is approaching from the north-east, expected about twelve minutes into the window. Her missiles make her a real surface threat. The trawler remains a separate identification problem. Keep a surface screen while the flight and Poseidon work VICTOR.")
    service["forces"] += " A light Russian Steregushchiy-class corvette approaches after twelve minutes."

    # O10's fixed strike force keeps its main three-of-five launcher task.
    # These are separate military support sites, not a larger launcher tally.
    shield = by["O10"]
    for station, at, label, uid, name in (
        ("missile_ammo", (-1.03, 135.88), "Western missile stores", "tgt_ammo_depot_small", "Military missile stores"),
        ("missile_fuel", (-1.18, 136.13), "Eastern military fuel site", "tgt_fueltanks_medium", "Military fuel reserve"),
        ("missile_command", (-0.95, 135.92), "Northern command hide", "wp_car_ural_command", "Enclave command truck"),
    ):
        shield["stations"][station] = dict(S(*at, label), coastal=True)
        shield["units"].append(U("red", "_vanilla", uid, station, name=name, weapons="Hold"))
    shield["objectives"] += [
        ("MissileStores", "Destroy the western military ammunition site", "5,0,None"),
        ("MilitaryFuel", "Destroy the eastern military fuel reserve", "5,0,None"),
        ("LaunchControl", "Destroy the enclave command truck", "5,0,None"),
    ]
    shield.setdefault("resolve", {}).update(
        MissileStores=("destroy", "missile_ammo", 1),
        MilitaryFuel=("destroy", "missile_fuel", 1),
        LaunchControl=("destroy", "missile_command", 1))
    shield["brief"] += ("\\n\\nDISPERSED SUPPORT TARGETS: Military missile stores west of the pads, the eastern fuel reserve and a command truck in the northern hide are separate optional aimpoints. Reconnoitre them and allocate remaining weapons before completing the third launcher kill, which ends the operation. The launchers already hold their first rounds; destroying a support site does not magically disarm them. Civilian infrastructure is not a target.")
    shield["forces"] += " Separate military ammunition, fuel and command targets on Biak."

    # Also put the requested wing explicitly into SW11, so authored mission
    # inventory takes precedence over any later upstream variant change.
    for u in by["11"]["units"]:
        if u["type"] == "usn_cvn_ford":
            u["air_group"] = deepcopy(FORD_WING)
    by["11"]["brief"] += ("\\n\\nFORD AIR WING: Sixteen F-35Cs are embarked alongside twenty-four F/A-18Es, twelve F/A-18Fs, six Growlers, four Hawkeyes and eight Seahawks. This is a 70-aircraft SEST 2028 wing; the F-35Cs are available in the carrier's Flight Deck window as well as the airborne cover. Set their loadouts during preparation before starting the operation.")
