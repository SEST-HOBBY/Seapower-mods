"""Authored revisions following the d90ac062 PC playtest.

Keep the existing mission dictionaries and their objective references. This
module changes the named detachments and records damage, rather than replacing
the campaigns with new templates. Imported after Southern Watch's old tables.
"""
from copy import deepcopy


ROOSEVELT_WING = [
    ("usn_fa-18f", "Squadron2", 12),
    ("usn_fa-18e", "Squadron2", 24),
    ("usn_f-35c", "Squadron10", 14),
    ("usn_ea-18g", "Squadron1", 6),
    ("usn_e-2d", "Squadron3", 4),
    ("usn_mh-60r", "Squadron14", 6),
]


def apply_watch(missions, U, S):
    by = {m["num"]: m for m in missions}
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
