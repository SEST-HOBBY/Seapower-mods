"""RLO2 - The Ships from the North. Ceram Sea, 18 November 2028.

The second side operation (campaign-upgrade-plan.md section 4.2, step RL-1,
20 Oct 2026). The Japanese escort detachment Common Sea sails with on the
20th is crossing the Ceram Sea for the Kai Islands, and The Other Picture's
convoy is forming there for it the next day. Fleet headquarters wants the
two escorts' names before they join it: the enclave detachment's Y-9 has
the look, and a J-15 pair the carrier air wing has released to the field -
The Other Picture's own words the next day - keeps it company.

A fixed force flies it, as Datum is: nothing the player owns sails. It
writes nothing for now, as Pilot in the Water writes nothing: the names go
to headquarters, and the operation pays its own completion points
(tables.py), which The Other Picture's window can spend. Until 21 Oct 2026
naming both escorts wrote RLO2EscortsNamed, and The Other Picture started
with the two ships on its plot classified. The owner pulled that before
upload (21 Oct 2026): nothing has shown that a reveal at Classify counts
for The Other Picture's UnitClassified stage, and if it does not, a player
who won this could not win that mission. It comes back, restorable from
commit 9035f291, once the Red Line test card's 7.4 is answered: Southern
Reach's TS01 -> TS03 and Sulu Line's SL01A -> SL03A have the same shape on
optional objectives, and flying either settles it (Southern Reach card
3.10, Sulu Line card 7.1).

The ships are the ones The Other Picture and Common Sea place, JS Mogami
and JS Maya on the same variants, so this adds no hull to the reserve's
pack-wide filter; no standard coalition campaign owns either before the
20th, after both their Red Line appearances. They are weapons Hold and
spared with a fatal entry, as in The Other Picture. The Japanese fighters
are not: they are a JASDF F-2A pair out of Langgur - the detachment Viper
Zero and Common Sea fly from, here unnamed - at weapons Tight, and if one
fires the brief's rule is The Other Picture's, reply against the aircraft
that fired. The J-15s are Tight too, and no objective scores which pair
opens first: if Tight lets a fighter fire on an identified F-2A, test card
8B.3a starts them at Hold.

The day before is Viper Zero's: the same Langgur detachment's F-2As went
for a PLAN 054A and 056A south of Seram. That is said as its premise - the
northern element's ships, not this group's - and never how it ended,
because Southern Watch flies it as an optional.

Geography: proved against the coastline (geo/banda_theatre_coast.json).
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
    difficulty=3, minutes=80, centre=(-2.4, 130.4),
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
            "to see the Y-9 off. They will be at weapons Tight, and so are yours. If "
            "they fire, you may reply against the aircraft that fired and nothing else - by "
            "direct order: fighters left free will go for the ships, and that ends the "
            "operation. Nothing afloat is a target.\\n\\nClassify both escorts, then take SEA "
            "EAR 31 back east towards the field. A Misool fishing boat and a coaster bound "
            "for Sorong are in the same water."
        )),
    forces=(
        "Sea Ear 31, a Y-9, and two J-15s, Flying Shark 81 and 82, out of the enclave field. "
        "Opposing: two Japanese escorts at weapons Hold, and a JASDF F-2A pair from Langgur "
        "at weapons Tight. Neutral: a fishing boat and a coaster."
    ),
    objectives=[
        ("Names", "Classify both Japanese escorts, then take Sea Ear 31 back east",
         "35,-35,Fail,Main"),
        ("Restraint", "Fire on nothing afloat", "15,-40,Complete"),
        ("Eye", "Bring Sea Ear 31 home", "10,-30,Complete"),
        ("Fighters", "Classify the Japanese fighters", "10,0,None"),
        ("Traffic", "Harm no fishing boat or coaster", "0,-30,Complete"),
    ],
    # Both escorts by name, then the Y-9 back in the box on the way home,
    # 46 NM east of where she starts, so the win cannot be met at spawn.
    # The stage set RLO2EscortsNamed for The Other Picture until 21 Oct
    # 2026; it sets nothing while that reveal is held (see above).
    victory=dict(kind="arrive", station="mpa", at=(-1.85, 131.75), radius=10,
                 min_units=1, objective="Names",
                 after=dict(kind="classify", units=["jmsdf#1", "jmsdf#2"], min_units=2,
                            intel=(
                                "PICTURE REPORT / SEA EAR 31: Both escorts classified: JS "
                                "Mogami, a frigate with a towed array, and JS Maya, a "
                                "destroyer with her own air defence. The recording goes to "
                                "headquarters. Take the aircraft home."
                            ))),
    # The ships are the next two days' convoy escort in Southern Watch:
    # lose one and the coalition's own campaign has a hole in it. The
    # fighters are not spared - The Other Picture's rule, a reply to the
    # aircraft that fired - and the Y-9 lost ends it, the names being hers.
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
        # The Japanese pair in the middle of the Ceram Sea, 23 NM off Obi
        # and Seram, on the route south-east for the passage east of Seram
        # and the Kai Islands; the Y-9 and the J-15s 88 NM east of them,
        # inbound from the enclave; the F-2As coming north out of the Banda
        # Sea, 91 NM from the Y-9; the field on Biak, 315 NM east.
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
        # Mogami first: the stage names jmsdf#1 and #2. The Other Picture's
        # and Common Sea's hulls, on their default variants.
        U("red", "SEST_JMSDF_Mogami", "js_ffg_mogami", "jmsdf", name="JS Mogami",
          weapons="Hold", route=[(-2.85, 130.90, 0), (-3.60, 131.40, 0)], telegraph=3),
        U("red", "euromod-jmsdf", "jmsdf_ddg_maya", "jmsdf", name="JS Maya",
          weapons="Hold", route=[(-2.85, 130.90, 0), (-3.60, 131.40, 0)], telegraph=3),
        # Up from Langgur to see the Y-9 off, and round the ships' track
        # until the clock runs out. Tight: they defend; they do not open.
        U("red", "f-2a-viper-zero", "jp_f-2a_late", "red_air", loadout="AirToAir",
          alt=25000, weapons="Tight",
          route=[(-2.45, 130.80, 25000), (-3.00, 130.55, 25000)], loop=True,
          telegraph=3),
        U("red", "f-2a-viper-zero", "jp_f-2a_late", "red_air", loadout="AirToAir",
          alt=25000, weapons="Tight",
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
