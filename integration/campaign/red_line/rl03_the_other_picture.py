"""RL03 - The Other Picture. Eastern Banda Sea, 19 November 2028.

Reconnaissance against fighters, with the rules of engagement pointing one
way. The day before Common Sea, the convoy is forming west of the Kai
Islands with its Japanese escort, and Fleet headquarters wants names. The
KJ-500 does the long look, a J-15 pair keeps it company, and a frigate
closes only as far as a classification needs. Two Australian F-35s are
weapons Tight; nothing afloat is a target.

The mirror of Southern Watch's Blind Horizon. The convoy is Common Sea's
own - Coral Pioneer, Antares and Kai Trader - with Mogami and Maya, and a
fatal entry on every hull keeps it whole for the next day. The attackers
Common Sea meets (a Type 039C, a 054A from the east, the enclave's
fighters) are not this commander's, and the brief says the picture goes
to people he does not command.
"""
from campaign_data import U, F, S
from .tables import HELO, RECON, CAP, NORTH_HULLS, NORTH_AIR, CARRIER_AIR

MISSION = dict(
    code="RL03", series="Red Line", seq="RED LINE  ·  MISSION 3",
    group="core", num="03", key="The Other Picture", place="Eastern Banda Sea",
    intro=(
        "Name the convoy and its Japanese escort from outside their reach. Fire on nothing "
        "afloat."
    ),
    sender="Fleet headquarters",
    intent=((
        "Headquarters needs to know which merchant matters and which escorts hunt, by class "
        "and by name, before the convoy sails. Get the names and bring the aircraft home. The"
        " convoy and its escort are not targets today, and the group does not start a fight "
        "with their fighters. If they fire, reply against the aircraft that fired."
    )),
    date=(2028, 11, 19), time=(10, 30), sea=3, clouds="Scattered_2", wind="SE",
    difficulty=3, minutes=75, centre=(-5.6, 131.5),
    blue_nation="China", red_nation="Australia",
    brief=(
        (
            "EASTERN BANDA SEA, 1030. The coalition's next convoy is forming west of the Kai "
            "Islands with a Japanese escort detachment, and it sails tomorrow. Headquarters "
            "wants names: which merchant matters, and which escorts hunt submarines.\\n\\nDRAGON"
            " EYE 05, a KJ-500, has the long look from the north-west, and a J-15 pair keeps "
            "it company; a patrol aircraft from the enclave field can share the look if one is "
            "allocated. Your frigate shadows from outside the escorts' reach and closes only "
            "as far as a classification needs. Two Australian F-35s are covering the convoy at"
            " weapons Tight. If they fire, you may reply against the aircraft that fired and "
            "nothing else. Nothing in that convoy or its escort is a target.\\n\\nThe picture "
            "you build goes to headquarters. What is done with it tomorrow will be done by "
            "people this group does not command.\\n\\nA Kai fishing boat, a stern trawler and "
            "the Tual-Ambon ferry are in the box."
        )),
    forces=(
        "Your screen with its flight, and a J-15 pair and a patrol aircraft if allocated. "
        "Allocated: Dragon Eye 05, "
        "a KJ-500. Opposing: three merchants, JS Mogami and JS Maya, and two RAAF F-35As at "
        "weapons Tight. Neutral: two Kai fishing hulls and a ferry. The enclave field, 400 "
        "miles north-east, is where the aircraft recover."
    ),
    objectives=[
        ("Picture", "Classify MV Coral Pioneer and both Japanese escorts, then take the "
                    "frigate back north-west", "35,-35,Fail,Main"),
        ("Restraint", "Fire on nothing in the convoy or its escort", "15,-40,Complete"),
        ("Eye", "Bring Dragon Eye 05 home", "10,-20,Complete"),
        ("Fighters", "Classify the covering fighters", "10,0,None"),
        ("Traffic", "Harm no fishing boat or ferry", "0,-30,Complete"),
    ],
    # The three hulls headquarters asked about, by name, out of a formation of
    # five: Coral Pioneer (convoy#1) and both Japanese escorts. Then the
    # frigate back to the group's line.
    victory=dict(kind="arrive", station="shadow", min_units=1, objective="Picture",
                 after=dict(kind="classify", units=["convoy#1", "jmsdf#1", "jmsdf#2"],
                            min_units=3,
                            intel=(
                                "PICTURE REPORT: MV Coral Pioneer, JS Mogami and JS Maya "
                                "classified and passed to headquarters. The frigate may "
                                "withdraw to the group's line."
                            ))),
    # Every hull Common Sea sails the next day. The F-35s are unnamed and
    # nothing tomorrow depends on them.
    fatal=[F("Restraint", ["convoy", "jmsdf"])],
    neutral_objective="Traffic",
    win=(
        "Coral Pioneer, Mogami and Maya are classified and the frigate is back on the group's "
        "line. The picture has gone to headquarters. The convoy sails tomorrow, and this group"
        " will not be the one that meets it."
    ),
    lose=(
        "The group has sunk a ship of the convoy or its escort, the day before a passage the "
        "coalition has announced to the world. The picture no longer matters; the incident "
        "does."
    ),
    timeout="1145. The convoy has the names the coalition gave it and none this group "
            "confirmed. Headquarters will send what it has, which is a guess.",
    stations={
        # The frigate 70 NM north-west of the convoy, outside the escorts' reach; the
        # KJ-500's racetrack runs from the north-west towards the convoy; the
        # fighter cockpits between it and the F-35s. The convoy forms 30 NM
        # west of Kai, making slowly towards the next day's start.
        "shadow": S(-5.40, 131.05, "Shadow", heading=120),
        "flight": S(-5.42, 131.03, "Ship's flight", heading=120, alt=500),
        "eye": S(-4.40, 131.00, "Dragon Eye 05", heading=150, alt=30000),
        # The cockpit a purchased Y-9 or KJ-500 takes, east of the fighter
        # escort and clear of Dragon Eye's own mark on the briefing map.
        "mpa": S(-4.60, 131.60, "Patrol aircraft", heading=150, alt=24000),
        "cap": S(-4.80, 131.20, "Fighter escort", heading=150, alt=28000),
        # The enclave field on Biak, 400 NM north-east: where the J-15s and
        # the KJ-500 recover. Off the briefing chart.
        "field": S(-1.10, 136.20, "Enclave field"),
        "convoy": S(-6.10, 132.00, "Convoy", heading=120),
        "jmsdf": S(-6.00, 131.95, "Japanese escort", heading=120),
        "red_air": S(-6.40, 131.80, "Covering fighters", heading=300, alt=25000),
        "fishing": S(-5.80, 131.80, "Kai fishing boats", heading=200),
        "ferry": S(-5.45, 131.70, "Tual-Ambon ferry", heading=290),
    },
    units=[
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "shadow", variant="Variant3",
          weapons="Hold"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "modern-plan-systems", "plaaf_kj-500", "eye", name="Dragon Eye 05",
          loadout="AEW", weapons="Hold",
          route=[(-5.30, 131.50, 30000), (-4.40, 131.00, 30000)], loop=True,
          telegraph=3),
        # Air-tasking placeholder for a purchased Y-9 or KJ-500: no name, no
        # objective. Without this row the two were on sale here and could fly
        # in no mission after it.
        U("blue", "modern-plan-systems", "plan_y-9fq", "mpa", alt=24000, weapons="Hold",
          loadout="ASW", slot="Recon"),
        # Two cockpits for a purchased J-15 pair. No names, no objective.
        U("blue", "type-003-004-maneuverwarfare", "plan_j-15", "cap", alt=28000,
          loadout="AirToAir", weapons="Tight", slot="CAP"),
        U("blue", "type-003-004-maneuverwarfare", "plan_j-15", "cap", alt=28000,
          loadout="AirToAir", weapons="Tight", slot="CAP"),
        U("blue", "modern-chinese-airbase", "pla_airbase_modern", "field",
          name="Enclave field (PLAAF detachment)", weapons="Hold"),
        # Coral Pioneer first: the Picture stage names convoy#1.
        U("red", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer", route=[(-6.35, 132.45, 0)], telegraph=1),
        U("red", "auxilliary-merchant-pack", "ran_ms_antares", "convoy",
          name="MV Antares", weapons="Hold", route=[(-6.35, 132.45, 0)], telegraph=1),
        U("red", "re-power-resupply", "civ_ms_freighter_a", "convoy",
          name="MV Kai Trader", route=[(-6.35, 132.45, 0)], telegraph=1),
        U("red", "SEST_JMSDF_Mogami", "js_ffg_mogami", "jmsdf", name="JS Mogami",
          weapons="Hold", route=[(-6.25, 132.40, 0)], telegraph=2),
        U("red", "euromod-jmsdf", "jmsdf_ddg_maya", "jmsdf", name="JS Maya",
          weapons="Hold", route=[(-6.25, 132.40, 0)], telegraph=2),
        # Weapons Tight, coming out towards the KJ-500's track and back over
        # the convoy until the clock runs out: the reason the long look has
        # to stay long.
        U("red", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "red_air", squadron="Squadron3",
          loadout="AirToAir", weapons="Tight",
          route=[(-5.40, 131.30, 25000), (-6.40, 131.80, 25000)], loop=True,
          telegraph=3),
        U("red", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "red_air", squadron="Squadron3",
          loadout="AirToAir", weapons="Tight",
          route=[(-5.40, 131.30, 25000), (-6.40, 131.80, 25000)], loop=True,
          telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Kai fishing boat Harapan", route=[(-6.00, 131.60, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_b", "fishing",
          name="Trawler Sinar Tual", route=[(-5.95, 131.70, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_roro_a", "ferry",
          name="KM Nuhu Evav (Tual-Ambon ferry)", route=[(-4.90, 130.40, 0)], telegraph=3),
    ],
    resolve={"Picture": "victory", "Traffic": "neutral",
             "Restraint": ("spare", "convoy", "jmsdf"),
             "Eye": ("protect", "eye"),
             "Fighters": ("classify", "red_air", 1)},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True,
                allow=NORTH_HULLS + NORTH_AIR + CARRIER_AIR,
                flights=[HELO, RECON, CAP],
                situation=(
                    "The carrier air wing has released aircraft to the enclave field for "
                    "escort work ashore. A J-15 pair can be allocated to cover Dragon Eye 05,"
                    " and a Y-9 or a second KJ-500 to share the look; Dragon Eye 05 itself is "
                    "allocated to this operation."
                )),
    role="recon",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 315, 12
