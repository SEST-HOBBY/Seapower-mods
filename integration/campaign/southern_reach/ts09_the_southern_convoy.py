"""TS09 - The Southern Convoy. South of Portland, 19 February 2029.

The fleet action of chapter B: five critical hulls for Adelaide and
Melbourne, the whole force with every Air Tasking row, against the group
with its flagship destroyer in the line for the first time, its air wing,
and whichever boats the chapter left alive - ROMEO if Under the Tasman
missed her, SIERRA-TWO if the Bight did.
"""
from campaign_data import U, F, S, HELO, RECON, CAP, STRIKE

MISSION = dict(
    code="TS09", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 9",
    group="core", num="09", key="The Southern Convoy", place="South of Portland",
    intro="Five hulls for Adelaide and Melbourne, the whole force and "
          "every aircraft it can task, against Liaoning, her air wing, the "
          "group's Type 052D flagship and whatever is still under the water.",
    sender="Commodore Alex Mercer; Wing Commander Daniel Ward for the "
           "strike and the fighter cover",
    intent=((
        "This is the one. Five hulls with a month of Adelaide's and Melbourne's cargo in them, "
        "the whole force, Edinburgh's fighters, Poseidon and Wedgetail, and for the first time "
        "Super Hornets tasked to strike. The group is eighty miles south-west with its flagship"
        " destroyer in the line, and it means to break the convoy here because it cannot break "
        "it off Sydney. Four of five into the split point off Portland. ROMEO and SIERRA-TWO "
        "remain possible threats unless the earlier action reports confirm their loss. Use "
        "everything."
    )),
    date=(2029, 2, 19), time=(10, 0), sea=5, clouds="Broken_3", wind="SW",
    difficulty=4, minutes=90, centre=(-38.6, 140.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "SOUTH OF PORTLAND, 38 South, mid-morning, a south-westerly. The "
        "Southern Convoy: the tanker PORTLAND SPIRIT, the bulker LIMESTONE "
        "COAST, the freighter GLENELG, the car carrier BASS HIGHWAY and "
        "CORAL PIONEER, thirteen knots, bound for the split point off "
        "Portland where the Adelaide hulls turn west and the Melbourne "
        "hulls go on.\\n\\n"
        "The protection group is eighty miles south-west and it has "
        "stopped pretending: LIAONING, the Type 052D that has commanded "
        "the group since October, two frigates and a corvette, three J-15s "
        "with anti-ship missiles and a J-15D with them, a Ka-31 and a Z-18F "
        "up. If Farncomb missed ROMEO on the fourth, she is under the "
        "convoy; if the Bight search missed SIERRA-TWO, so is she.\\n\\n"
        "You have the whole force: the Seahawk, Edinburgh's Poseidon and "
        "WEDGETAIL 05, Edinburgh's F-35As for fighter cover, and for the "
        "first time Super Hornets and Growlers tasked to strike, "
        "recovering at Edinburgh. A coastal ro-ro, a bulker and the "
        "Melbourne-Perth service are in the box. Four of five to the "
        "split point."),
    forces=(
        "Your whole task group with its Seahawk, Poseidon, Wedgetail, fighters and strike "
        "aircraft if assigned; Wedgetail 05. Five convoy hulls. Neutral: a coastal ro-ro, a "
        "bulker, an airliner. Opposing: Liaoning, a Type 052D, two Type 054A, a Type 056A, "
        "three J-15 with anti-ship missiles, a J-15D, a Ka-31, a Z-18F, and ROMEO and "
        "SIERRA-TWO if Farncomb and the Bight search left them alive."
    ),
    objectives=[
        ("Convoy", "Four of five convoy hulls into the split point off "
                   "Portland", "45,-45,Fail,Main"),
        ("Wedgetail", "Keep the Wedgetail flying", "10,-15,Complete"),
        ("Neutrals", "Harm no merchant or aircraft", "0,-25,Complete"),
        ("Flagship", "Bring your flagship out intact", "15,-20,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", min_units=4, objective="Convoy",
                 transit=12),
    fatal=[F("Convoy", ["convoy"], 2)],
    neutral_objective="Neutrals",
    win=(
        "At least four ships have reached the Portland split point. Adelaide-bound cargo can "
        "turn west while the Melbourne ships continue east. Command is accounting for losses "
        "and remaining ammunition before the next passage."
    ),
    lose="Two hulls lost south of Portland with a month of two cities' "
         "cargo in them. The group broke the convoy where it said it "
         "would.",
    timeout="Ninety minutes and the convoy is still short of the split "
            "point with the carrier's second strike forming. Portland's "
            "pilot boat waits for a convoy that turned back.",
    stations={
        # The convoy and escorts on 060 for the split point; every cockpit
        # on the Edinburgh side (the nearer field, so the fighters recover
        # there too); the group 85 NM south-west
        # routed onto the convoy with its strike flight ahead of it; the
        # boats across the track, each only if the chapter left it alive.
        "convoy": S(-38.70, 140.30, "Southern Convoy", heading=60),
        "escort": S(-38.65, 140.45, "Escort group", heading=60),
        "flight": S(-38.67, 140.43, "Ship's flight", heading=60, alt=500),
        "mpa": S(-38.90, 140.70, "Maritime patrol", heading=240, alt=12000),
        "cap": S(-38.40, 140.90, "Fighter cover", heading=240, alt=30000),
        "attack": S(-38.30, 140.20, "Strike", heading=240, alt=25000),
        "aew": S(-38.20, 140.60, "Wedgetail 05", heading=270, alt=32000),
        "red_cv": S(-40.00, 139.50, "Protection group", heading=40),
        "red_air": S(-39.60, 139.80, "Strike flight", heading=40, alt=25000),
        "red_helo": S(-39.90, 139.60, "Ka-31 orbit", heading=40, alt=9000),
        "red_dip": S(-39.40, 140.00, "Z-18F dip", heading=40, alt=1500),
        "red_romeo": S(-38.95, 139.90, "Contact ROMEO", heading=60),
        "red_sierra": S(-38.30, 139.80, "Contact SIERRA-TWO", heading=120),
        "roro": S(-39.10, 141.30, "Coastal ro-ro", heading=90),
        "bulker": S(-38.20, 140.00, "Bulker", heading=300),
        "airliner": S(-38.30, 141.50, "Melbourne-Perth", heading=280, alt=38000),
        "edinburgh": S(-34.703, 138.622, "RAAF Base Edinburgh"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          loadout="ASW", slot="Recon"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron1",
          slot="CAP"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron1",
          slot="CAP"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_fa-18f_blk3", "attack",
          squadron="Squadron8", slot="Attack"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_fa-18f_blk3", "attack",
          squadron="Squadron8", slot="Attack"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 05",
          alt=32000, weapons="Hold"),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Portland Spirit"),
        U("blue", "auxilliary-merchant-pack", "anl_ms_bulk", "convoy",
          name="MV Limestone Coast", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_freighter_b", "convoy",
          name="MV Glenelg"),
        U("blue", "_vanilla", "civ_ms_car_carrier_a", "convoy",
          name="MV Bass Highway"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("red", "liaoning-type-001", "plan_type_001", "red_cv", name="Liaoning",
          route=[(-39.20, 140.10, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_052d_p3", "red_cv",
          name="Type 052D (the flagship)", route=[(-39.20, 140.10, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_cv",
          name="Type 054A frigate", route=[(-39.20, 140.10, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_cv",
          name="Type 054A frigate", route=[(-39.20, 140.10, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_056a", "red_cv",
          name="Type 056A corvette", route=[(-39.20, 140.10, 0)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 51", loadout="AntiShip",
          route=[(-38.70, 140.30, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 52", loadout="AntiShip",
          route=[(-38.70, 140.30, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 53", loadout="AntiShip",
          route=[(-38.70, 140.30, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_air",
          name="Flying Shark 54", loadout="AntiShip",
          route=[(-38.70, 140.30, 20000)], telegraph=3),
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW",
          route=[(-39.40, 139.90, 9000)], telegraph=2),
        U("red", "chinese-navy-plan", "plan_z-18f", "red_dip", name="Z-18F dip",
          alt=1500, loadout="ASW"),
        # Only if the chapter left them alive: the spawns read the flags
        # Under the Tasman and Great Australian Bight write.
        U("red", "plan-submarines", "plan_ssn_type_093b", "red_romeo",
          name="Contact ROMEO", depth="belowlayer",
          spawn_if=("TS05RomeoSunk", "IsFalse"),
          route=[(-38.60, 140.40, "belowlayer")], telegraph=3),
        U("red", "russian-submarines", "wp_ssgn_yasen", "red_sierra",
          name="Contact SIERRA-TWO", depth="belowlayer",
          spawn_if=("TS08YasenSunk", "IsFalse"),
          route=[(-38.45, 140.45, "belowlayer")], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_roro_a", "roro",
          name="MV Coorong (Adelaide-Melbourne ro-ro)",
          route=[(-39.30, 143.60, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Kingston (Portland-Whyalla)",
          route=[(-37.60, 139.20, 0)], telegraph=3),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Melbourne-Perth 471", airway=(-31.94, 115.97)),  # Perth
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_edinburgh", "edinburgh",
          name="RAAF Base Edinburgh", nation="australia", weapons="Hold"),
    ],
    resolve={"Convoy": "victory", "Neutrals": "neutral",
             "Wedgetail": ("protect", "aew"),
             "Flagship": ("protect", "escort")},
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "ran_opv_arafura",
                       "usn_mh-60r", "usn_p8", "raaf_mq-4c_triton", "E7A_Wedgetail",
                       "raaf_f-35a", "usn_fa-18f_blk3", "usn_ea-18g"],
                flights=[HELO, RECON, CAP, STRIKE],
                situation=(
                    (
                        "Adelaide, before the Southern Convoy. Force allocation, repairs and "
                        "ammunition resupply: the convoy sails the whole force with every "
                        "aircraft it can task, and there is no further force allocation before "
                        "the optional priorities after it. The next window is Sydney, before "
                        "Approaches."
                    )
                )),
    role="fleet",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 60, 15
