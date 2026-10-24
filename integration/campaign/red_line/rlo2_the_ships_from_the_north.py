"""RLO2 — reconnaissance escorted through a timed fighter interception.

24 Oct 2026: a weapons-free F-2 pair joins at minute eight and has native
scripted AAM orders against the Y-9. The two protected Japanese ships still
need classifying. The old RLO2EscortsNamed reveal remains held; no new
cross-mission classification assumption is introduced.
"""
from campaign_data import U, F, S

MISSION = dict(
    code="RLO2", series="Red Line", seq="RED LINE  ·  OPTIONAL",
    group="optional", num="O2", key="The Ships from the North", place="Ceram Sea",
    geography="coast",
    intro=(
        "Optional. Two Japanese escorts are crossing the Ceram Sea to join tomorrow's convoy. "
        "Name them from the Y-9, with a J-15 pair alongside. Fire on nothing afloat."
    ),
    special=(
        "No force allocation: the enclave detachment's Y-9 and two J-15s released to the field "
        "fly this operation, and the screen stays on its station. The names go to "
        "headquarters. The request closes when The Other Picture is complete."
    ),
    sender="Fleet headquarters",
    intent=((
        "The convoy forming at Kai sails the day after tomorrow with whatever escort reaches "
        "it, and two Japanese ships are on their way. Headquarters wants them named before "
        "they get there: which ships, and what they hunt with. Japan is at sea under its own "
        "rules, and yesterday those rules sent the Langgur fighters against northern ships "
        "south of Seram. They were not this group's ships, and the group is not at war with "
        "Japan. The same fighters will come up to see the Y-9 off. Let them. Ours are there "
        "so that seeing it off is all they do."
    )),
    date=(2028, 11, 18), time=(9, 20), sea=3, clouds="Scattered_1", wind="E",
    difficulty=3, minutes=45, centre=(-2.4, 130.4),
    blue_nation="China", red_nation="Japan",
    brief=(
        (
            "CERAM SEA, 0920. Two Japanese escorts came south past the Talaud Islands two days "
            "ago and are crossing the Ceram Sea this morning for the Kai Islands, where the "
            "coalition's next convoy is forming. Fleet headquarters wants their names before "
            "they join it: which ships they are, and which of them hunts submarines.\\n\\nSEA "
            "EAR 31, the enclave detachment's Y-9, has the look from the east. FLYING SHARK 81 "
            "and 82, J-15s the carrier air wing has released to the enclave field, keep it "
            "company. The two ships are eighty-five miles west of the aircraft, steaming "
            "south-east for the passage east of Seram.\\n\\nExpect a JASDF F-2A pair up from "
            "Langgur, the detachment that flew against the northern element's ships yesterday, "
            "to see the Y-9 off. They enter at minute eight with weapons Free and can fire on the Y-9. Your escorts remain at Tight. If "
            "the intercept develops, keep the Y-9 covered and engage the fighters, not the ships - by "
            "direct order: fighters left free will go for the ships, and that ends the "
            "operation. Nothing afloat is a target.\\n\\nClassify both escorts, then take SEA "
            "EAR 31 back east towards the field. A Misool fishing boat and a coaster bound "
            "for Sorong are in the same water."
        )),
    forces=(
        "Sea Ear 31, a Y-9, and two J-15s, Flying Shark 81 and 82, out of the enclave field. "
        "Opposing: two Japanese escorts at weapons Hold, and a JASDF F-2A pair from Langgur "
        "entering at minute eight with weapons Free. Neutral: a fishing boat and a coaster."
    ),
    objectives=[
        ("Names", "Classify both Japanese escorts, then take Sea Ear 31 back east",
         "35,-35,Fail,Main"),
        ("Restraint", "Fire on nothing afloat", "15,-40,Complete"),
        ("Eye", "Bring Sea Ear 31 home", "10,-30,Complete"),
        ("Fighters", "Classify the Japanese fighters", "10,0,None"),
        ("Traffic", "Harm no fishing boat or coaster", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="mpa", at=(-1.85, 131.75), radius=10,
                 min_units=1, objective="Names",
                 also=[dict(kind="time",after_minutes=14),dict(kind="no_incoming")],
                 after=dict(kind="classify", units=["jmsdf#1", "jmsdf#2"], min_units=2,
                            intel=(
                                "PICTURE REPORT / SEA EAR 31: Both escorts classified: JS "
                                "Mogami, a frigate with a towed array, and JS Maya, a "
                                "destroyer with her own air defence. The recording goes to "
                                "headquarters. Take the aircraft home."
                            ))),
    fatal=[F("Restraint", ["jmsdf"]), F("Eye")],
    neutral_objective="Traffic",
    win=(
        "SEA EAR 31 is on her way home with both escorts classified, JS Mogami and JS Maya, "
        "and the recording and the two names go to headquarters. The F-2As have a recording "
        "of their own: a Y-9 that did nothing but look."
    ),
    lose=(
        "A Japanese ship is hit, or the Y-9 is down. Either way the group has an incident "
        "with a navy it is not at war with, two days before the convoy sails."
    ),
    timeout="{deadline_clock}, and the escorts are through the Ceram Sea with no names this "
            "group confirmed. They join the convoy tonight as two contacts.",
    stations={
        "jmsdf": S(-2.40, 129.60, "Japanese escorts", heading=115),
        "mpa": S(-2.00, 131.00, "Sea Ear 31", heading=250, alt=24000),
        "cap": S(-1.95, 131.05, "Flying Shark 81", heading=250, alt=28000),
        "red_air": S(-3.50, 131.20, "Japanese fighters", heading=320, alt=25000),
        "field": S(-1.10, 136.20, "Enclave field"),
        "fishing": S(-2.10, 129.80, "Misool fishing boat", heading=200),
        "coaster": S(-2.62, 130.25, "Coaster", heading=60),
    },
    units=[
        U("blue", "modern-plan-systems", "plan_y-9fq", "mpa", name="Sea Ear 31",
          squadron="Squadron1", loadout="ASW", alt=24000, weapons="Hold"),
        U("blue", "type-003-004-maneuverwarfare", "plan_j-15", "cap", name="Flying Shark 81",
          loadout="AirToAir", alt=28000, weapons="Tight"),
        U("blue", "type-003-004-maneuverwarfare", "plan_j-15", "cap", name="Flying Shark 82",
          loadout="AirToAir", alt=28000, weapons="Tight"),
        U("blue", "modern-chinese-airbase", "pla_airbase_modern", "field",
          name="Enclave field (PLAAF detachment)", weapons="Hold"),
        U("red", "SEST_JMSDF_Mogami", "js_ffg_mogami", "jmsdf", name="JS Mogami",
          weapons="Hold", route=[(-2.85, 130.90, 0), (-3.60, 131.40, 0)], telegraph=3),
        U("red", "euromod-jmsdf", "jmsdf_ddg_maya", "jmsdf", name="JS Maya",
          weapons="Hold", route=[(-2.85, 130.90, 0), (-3.60, 131.40, 0)], telegraph=3),
        U("red", "f-2a-viper-zero", "jp_f-2a_late", "red_air", loadout="AirToAir",
          alt=25000, weapons="Free", enter=8,
          contact="Announced minute-eight intercept after escort preparation.",
          attacks=[(12,"jp_aam-4","mpa",1)],
          route=[(-2.45, 130.80, 25000), (-3.00, 130.55, 25000)], loop=True,
          telegraph=3),
        U("red", "f-2a-viper-zero", "jp_f-2a_late", "red_air", loadout="AirToAir",
          alt=25000, weapons="Free", enter=8,
          contact="Announced minute-eight intercept after escort preparation.",
          attacks=[(12,"jp_aam-4","mpa",1)],
          route=[(-2.45, 130.80, 25000), (-3.00, 130.55, 25000)], loop=True,
          telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Misool fishing boat Harapan Baru", route=[(-2.35, 129.75, 0)], telegraph=2),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "coaster",
          name="KM Seram Jaya (Ambon-Sorong)", route=[(-2.30, 131.40, 0)], telegraph=3),
    ],
    resolve={"Names": "victory", "Traffic": "neutral",
             "Restraint": ("spare", "jmsdf"),
             "Eye": ("protect", "mpa"),
             "Fighters": ("classify", "red_air", 1)},
    declares=[],
    expires_after="The Other Picture",
    window=dict(),
    role="recon",
)
