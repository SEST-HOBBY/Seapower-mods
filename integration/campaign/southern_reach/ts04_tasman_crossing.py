"""TS04 - Tasman Crossing. Mid-Tasman, 1 February 2029.

Two merchant groups thirty miles apart, Auckland-bound, and the force
between them with the first Tasman fighter cover; the carrier two hundred
miles south-east sends its strike flight onto the trailing group. The
escort problem of the chapter: which group gets the destroyer.
"""
from campaign_data import U, F, S, HELO, RECON, CAP

MISSION = dict(
    code="TS04", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 4",
    group="core", num="04", key="Tasman Crossing", place="Mid-Tasman",
    intro="Two merchant groups thirty miles apart on the Auckland run, the "
          "force between them, and a carrier's strike flight coming for "
          "the one you are not with.",
    sender="Commodore Alex Mercer; Wing Commander Daniel Ward for the "
           "fighter picture",
    intent=("Four hulls in two groups, thirty miles apart because the "
            "charterers would not wait for each other, and you cannot be "
            "with both. The carrier is two hundred miles south-east and "
            "its strike flight will come for whichever group it thinks "
            "you are not covering. Wedgetail already has them, a hundred and twenty miles out; "
            "Williamtown's fighters are on the CAP row for the first time "
            "in the Tasman and the Super Hornets go on sale here. Three of "
            "four into the box. Coral Pioneer is in group A and Santos "
            "has not lost a hull yet."),
    date=(2029, 2, 1), time=(13, 0), sea=4, clouds="Scattered_2", wind="W",
    difficulty=3, minutes=80, centre=(-38.5, 158.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "MID-TASMAN, early afternoon. Two merchant groups on the Auckland "
        "run: GROUP A is CORAL PIONEER and the bulker WAIRAU TRADER, thirty "
        "miles south-east of GROUP B, the freighter TASMAN VENTURE and the "
        "car carrier HAURAKI HIGHWAY, both groups making for the same "
        "turning point north-east. Neither group would wait for the "
        "other and both want the same escort.\\n\\n"
        "LIAONING is two hundred miles south-east with a frigate, and the "
        "J-15s that flew over the fishing fleet for the cameras in "
        "December are already up with anti-ship missiles, a hundred and thirty miles from group B and closing. WEDGETAIL 05 is up "
        "out of Williamtown and, for the first time in the Tasman, so is "
        "a fighter that can reach you: the F-35As are on the CAP row and "
        "the Super Hornets and Growlers go on sale here.\\n\\n"
        "Three of four hulls into the box, north-east. The Sydney-Auckland "
        "service, a cruise ship and a bulker are crossing the same water. "
        "The carrier's aircraft have not fired at a merchant yet; today "
        "they will."),
    forces="Your task group with its Seahawk, Poseidon and fighters if "
           "bought, Wedgetail 05 out of Williamtown. Four merchant hulls in "
           "two groups. Neutral: an airliner, a cruise ship, a bulker. "
           "Opposing: Liaoning with a Type 054A, a J-15 anti-ship pair and a "
           "J-15D routed onto group B, a Ka-31 up.",
    objectives=[
        ("Crossing", "Three of four merchant hulls into the box north-east",
         "40,-40,Fail,Main"),
        ("Wedgetail", "Keep the Wedgetail flying", "10,-15,Complete"),
        ("Neutrals", "Harm no airliner, cruise ship or merchant", "0,-25,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    # Two groups abeam of the track, fifteen miles either side of it, and
    # one box twenty miles ahead of the escort: each group is twenty-five
    # miles from it, which twelve knots covers. Groups in line ahead could
    # never share a box - the trailing one cannot reach it in the clock.
    victory=dict(kind="arrive", station="group_a", units=["group_a", "group_b"],
                 min_units=3, objective="Crossing", transit=12,
                 at=(-38.33, 158.87), radius=15),
    fatal=[F("Crossing", ["group_a", "group_b"], 2)],
    neutral_objective="Neutrals",
    win="Three hulls in the box and the strike flight spent. Santos, from "
        "Coral Pioneer: 'Group B says thank you. Group A says nothing, "
        "which is what we always say.'",
    lose="Two hulls lost in the middle of the Tasman with Auckland's "
         "cargo in them. The charterers were right not to wait.",
    timeout="Eighty minutes and the groups are still short of the box "
            "with the carrier's second flight forming. The crossing is "
            "made tomorrow, or not.",
    stations={
        # The two groups 30 NM apart, abeam of the 060 track, the escort
        # between them; the fighters' cockpits on the Williamtown side; the
        # carrier 190 NM south-east with its strike flight routed low onto
        # group B, the north-western group.
        "group_a": S(-38.72, 158.66, "Group A", heading=60),
        "group_b": S(-38.28, 158.34, "Group B", heading=60),
        "escort": S(-38.50, 158.50, "Escort group", heading=60),
        "flight": S(-38.52, 158.48, "Ship's flight", heading=60, alt=500),
        "mpa": S(-38.60, 158.90, "Maritime patrol", heading=120, alt=12000),
        "cap": S(-38.30, 158.10, "Fighter cover", heading=120, alt=30000),
        "aew": S(-38.70, 157.90, "Wedgetail 05", heading=90, alt=32000),
        "red_cv": S(-41.00, 161.20, "Carrier group", heading=320),
        "red_air": S(-40.00, 160.20, "Strike flight", heading=310, alt=25000),
        "red_helo": S(-40.80, 161.00, "Ka-31 orbit", heading=320, alt=9000),
        "airliner": S(-38.00, 158.00, "Sydney-Auckland", heading=80, alt=37000),
        "cruise": S(-38.90, 159.20, "Cruise ship", heading=240),
        "bulker": S(-38.10, 157.60, "Bulker", heading=240),
        "home": S(-32.795, 151.834, "RAAF Base Williamtown"),
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
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 05",
          alt=32000, weapons="Hold"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "group_a",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "anl_ms_bulk", "group_a",
          name="MV Wairau Trader", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_freighter_a", "group_b",
          name="MV Tasman Venture"),
        U("blue", "_vanilla", "civ_ms_car_carrier_a", "group_b",
          name="MV Hauraki Highway"),
        U("red", "liaoning-type-001", "plan_type_001", "red_cv", name="Liaoning",
          route=[(-40.20, 160.40, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_cv",
          name="Type 054A frigate", route=[(-40.20, 160.40, 0)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 31", loadout="AntiShip",
          route=[(-38.28, 158.34, 500)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 32", loadout="AntiShip",
          route=[(-38.28, 158.34, 500)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_air",
          name="Flying Shark 33", loadout="AntiShip",
          route=[(-38.28, 158.34, 500)], telegraph=3),
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW"),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Sydney-Auckland 145"),
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Coral Princess Royal (Auckland-Sydney cruise)",
          route=[(-39.50, 157.50, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Tauranga Bay (Tauranga-Newcastle)",
          route=[(-38.90, 156.20, 0)], telegraph=3),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_williamtown", "home",
          name="RAAF Base Williamtown", nation="australia", weapons="Hold"),
    ],
    resolve={"Crossing": "victory", "Neutrals": "neutral",
             "Wedgetail": ("protect", "aew"),
             "Flagship": ("protect", "escort")},
    reveal_if=[dict(variable="SR12NetworkNamed", units=["red_cv#2"], level="Classify",
                    intel="Turning North's picture: the frigate with the carrier "
                          "is the Type 054A you named in the Tasman approaches, "
                          "and she is on your plot classified. Where she is, the "
                          "carrier is: a mile off her beam.")],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "ran_opv_arafura",
                       "usn_mh-60r", "usn_p8", "raaf_mq-4c_triton", "E7A_Wedgetail",
                       "raaf_f-35a", "usn_fa-18f_blk3", "usn_ea-18g"],
                flights=[HELO, RECON, CAP],
                situation="Sydney, before the crossing. Requisition, repair "
                          "and rearm: the Super Hornet and the Growler go on "
                          "sale, because Williamtown's aircraft reach the "
                          "mid-Tasman and the carrier is in it. Under the Tasman "
                          "has no builder; the next window is Melbourne, before "
                          "Bass Strait."),
    role="escort",
)
