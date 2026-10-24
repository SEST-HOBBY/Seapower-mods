"""RL03 — an escorted reconnaissance aircraft under an active fighter intercept.

24 Oct 2026: the two allocated J-15s guarantee an escort even if no CAP is
purchased. The F-35 pair joins at minute eight with weapons free. Protected
convoy ships and observers are non-belligerents on the neutral task force.
Ship classification is a bonus; breaking the intercept and recovering the
KJ-500 is the main task, so another long recognition search cannot stall it.
"""
from campaign_data import U, F, S
from .tables import HELO, RECON, CAP, NORTH_HULLS, NORTH_AIR, CARRIER_AIR

MISSION = dict(
    code="RL03", series="Red Line", seq="RED LINE  ·  MISSION 3",
    group="core", num="03", key="The Other Picture", place="Eastern Banda Sea",
    intro="Escort Dragon Eye through a fighter intercept, then bring it back with the picture it collected.",
    sender="Fleet headquarters",
    intent="Protect Dragon Eye and defeat the intercepting fighters. The merchants, Japanese ships, Growler and Rivet Joint are protected non-belligerents; none is a strike target. Record their classes if the tactical picture permits.",
    date=(2028, 11, 19), time=(10, 30), sea=3, clouds="Scattered_2", wind="SE",
    difficulty=4, minutes=45, centre=(-5.6, 131.5),
    blue_nation="China", red_nation="Australia",
    brief=("EASTERN BANDA SEA, 1030. DRAGON EYE 05 is collecting the convoy picture west of Kai. "
           "The coalition has ordered a two-aircraft intercept. Expect the F-35s at about minute "
           "eight, closing from the south-east; they are cleared to engage our aircraft. You "
           "may defend the KJ-500 and engage those fighters.\n\n"
           "Two J-15s, FLYING SHARK 83 and 84, are allocated to escort DRAGON EYE regardless of "
           "your purchases. Your own CAP pair and patrol aircraft can reinforce them if "
           "allocated. Use the first minutes to establish the escort and ready the screen's "
           "air defence. Stay between the interceptors and the KJ-500; do not send every fighter "
           "after a retreating contact and leave the radar aircraft bare.\n\n"
           "Break the intercept by destroying at least one fighter, then bring DRAGON EYE into "
           "the return box north-west, with no incoming weapons still threatening the force. "
           "Classifying CORAL PIONEER, MOGAMI and MAYA earns a separate intelligence bonus and "
           "does not block the exit. The three merchants, both Japanese escorts, the Growler "
           "and Rivet Joint use neutral tactical symbols: their protection is real and "
           "defensive weapons settings do not authorise an attack on them.\n\n"
           "The Kai fishing boats, ferry and Sydney-Hong Kong service remain protected. "
           "Nothing here decides tomorrow's Common Sea engagement."),
    forces="Your screen and any allocated aircraft, plus Dragon Eye 05 and an allocated J-15 pair. Hostile: two F-35As entering at minute eight. Protected non-belligerents: the convoy, Japanese escorts, Growler and Rivet Joint; civil traffic remains protected.",
    objectives=[
        ("Picture","Break the fighter intercept and bring Dragon Eye to the return box","35,-35,Fail,Main"),
        ("Restraint","Do not attack the convoy or protected surveillance aircraft","15,-40,Complete"),
        ("Eye","Keep Dragon Eye 05 alive","10,-30,Complete"),
        ("Fighters","Destroy at least one intercepting fighter","20,0,None"),
        ("Names","Classify Coral Pioneer and both Japanese escorts if practicable","20,0,None"),
        ("Traffic","Harm no protected non-belligerent or civil contact","0,-30,Complete"),
    ],
    victory=dict(kind="arrive",station="eye",at=(-4.15,130.60),radius=8,min_units=1,objective="Picture",
                 also=[dict(kind="destroyed",units=["red_air"],min_units=1),
                       dict(kind="time",after_minutes=9),dict(kind="no_incoming")]),
    fatal=[F("Restraint",["convoy","jmsdf","growler","rivet"]),F("Eye")],
    neutral_objective="Traffic",
    win="Dragon Eye is back in the return box, the intercept is broken and its recordings are going to headquarters. The convoy and its protected escorts remain intact for tomorrow.",
    lose="Dragon Eye is lost, or a protected ship or observer has been destroyed. The reconnaissance has failed.",
    timeout="{deadline_clock}. Dragon Eye is not safely back with the intercept broken.",
    stations={
        "shadow": S(-5.40, 131.05, "Shadow", heading=120),
        "flight": S(-5.42, 131.03, "Ship's flight", heading=120, alt=500),
        "eye": S(-4.40, 131.00, "Dragon Eye 05", heading=150, alt=30000),
        "mpa": S(-4.60, 131.60, "Patrol aircraft", heading=150, alt=24000),
        "cap": S(-4.80, 131.20, "Fighter escort", heading=150, alt=28000),
        "field": S(-1.10, 136.20, "Enclave field"),
        "growler": S(-6.50, 131.95, "Growler", heading=300, alt=24000),
        "rivet": S(-7.10, 131.30, "Rivet Joint", heading=90, alt=31000),
        "airliner": S(-7.66, 132.40, "Sydney-Hong Kong service", heading=328,
                      alt=37000),
        "convoy": S(-6.10, 132.00, "Convoy", heading=120),
        "jmsdf": S(-6.00, 131.95, "Japanese escort", heading=120),
        "red_air": S(-5.45, 131.55, "Covering fighters", heading=300, alt=25000),
        "fishing": S(-5.80, 131.80, "Kai fishing boats", heading=200),
        "ferry": S(-5.45, 131.70, "Tual-Ambon ferry", heading=290),
    },
    units=[
        U("blue","type-003-004-maneuverwarfare","plan_j-15","cap",name="Flying Shark 83",alt=28000,loadout="AirToAir",weapons="Tight"),
        U("blue","type-003-004-maneuverwarfare","plan_j-15","cap",name="Flying Shark 84",alt=28000,loadout="AirToAir",weapons="Tight"),
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "shadow", variant="Variant3",
          weapons="Hold"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "modern-plan-systems", "plaaf_kj-500", "eye", name="Dragon Eye 05",
          loadout="AEW", weapons="Hold",
          route=[(-5.30, 131.50, 30000), (-4.40, 131.00, 30000)], loop=True,
          telegraph=3),
        U("blue", "modern-plan-systems", "plan_y-9fq", "mpa", alt=24000, weapons="Hold",
          loadout="ASW", slot="Recon"),
        U("blue", "type-003-004-maneuverwarfare", "plan_j-15", "cap", alt=28000,
          loadout="AirToAir", weapons="Tight", slot="CAP"),
        U("blue", "type-003-004-maneuverwarfare", "plan_j-15", "cap", alt=28000,
          loadout="AirToAir", weapons="Tight", slot="CAP"),
        U("blue", "modern-chinese-airbase", "pla_airbase_modern", "field",
          name="Enclave field (PLAAF detachment)", weapons="Hold"),
        U("neutral", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer", route=[(-6.35, 132.45, 0)], telegraph=1),
        U("neutral", "auxilliary-merchant-pack", "ran_ms_antares", "convoy",
          name="MV Antares", weapons="Hold", route=[(-6.35, 132.45, 0)], telegraph=1),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "convoy",
          name="MV Kai Trader", route=[(-6.35, 132.45, 0)], telegraph=1),
        U("neutral", "SEST_JMSDF_Mogami", "js_ffg_mogami", "jmsdf", name="JS Mogami",
          weapons="Hold", route=[(-6.25, 132.40, 0)], telegraph=2),
        U("neutral", "euromod-jmsdf", "jmsdf_ddg_maya", "jmsdf", name="JS Maya",
          weapons="Hold", route=[(-6.25, 132.40, 0)], telegraph=2),
        U("red", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "red_air", squadron="Squadron3",
          loadout="AirToAir", weapons="Free", enter=8,
          contact="Announced minute-eight interception after player preparation; the convoy is not a target.",
          attacks=[(10,"usaf_aim-120c7","eye",1),(16,"usaf_aim-120c7","eye",1)],
          route=[(-5.40, 131.30, 25000), (-6.40, 131.80, 25000)], loop=True,
          telegraph=3),
        U("red", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "red_air", squadron="Squadron3",
          loadout="AirToAir", weapons="Free", enter=8,
          contact="Announced minute-eight interception after player preparation; the convoy is not a target.",
          attacks=[(10,"usaf_aim-120c7","eye",1),(16,"usaf_aim-120c7","eye",1)],
          route=[(-5.40, 131.30, 25000), (-6.40, 131.80, 25000)], loop=True,
          telegraph=3),
        U("neutral", "SEST_Growler_NGJ_MALICE", "usn_ea-18g", "growler", squadron="Squadron6",
          loadout="SEST_SEAD120D", weapons="Hold", radars="False",
          route=[(-5.50, 131.40, 24000), (-6.50, 131.95, 24000)], loop=True,
          telegraph=3),
        U("neutral", "rc-135-rivet-joint", "boeing_rc135", "rivet", squadron="Squadron2",
          loadout="SIGINT", weapons="Hold",
          route=[(-7.10, 130.90, 31000), (-7.10, 131.70, 31000)], loop=True,
          telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Kai fishing boat Harapan", route=[(-6.00, 131.60, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_b", "fishing",
          name="Trawler Sinar Tual", route=[(-5.95, 131.70, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_roro_a", "ferry",
          name="KM Nuhu Evav (Tual-Ambon ferry)", route=[(-4.90, 130.40, 0)], telegraph=3),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Sydney-Hong Kong service", squadron="Squadron61",
          airway=(22.31, 113.91)),  # Hong Kong
    ],
    resolve={"Picture": "victory", "Traffic": "neutral",
             "Restraint": ("spare", "convoy", "jmsdf", "growler", "rivet"),
             "Eye": ("protect", "eye"),
             "Fighters": ("destroy", "red_air", 1),
             "Names": ("classify", ["convoy#1","jmsdf#1","jmsdf#2"], 3)},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True,
                allow=NORTH_HULLS + NORTH_AIR + CARRIER_AIR,
                flights=[HELO, RECON, CAP],
                situation=(
                    "The carrier air wing has released aircraft to the enclave field for "
                    "escort work ashore. A J-15 pair can be allocated to cover Dragon Eye 05,"
                    " and a Y-9 or a second KJ-500 to share the look; Dragon Eye 05 itself is "
                    "allocated to this operation. Flying Shark 83 and 84 provide its guaranteed fighter escort."
                )),
    reports=[dict(minute=3,intel="AIR OPERATIONS: Keep the allocated J-15s with Dragon Eye. The intercept enters at minute eight; the grey convoy and surveillance aircraft are protected. The north-west return box is the exit, not another ship-classification gate.")],
    role="recon",
)
