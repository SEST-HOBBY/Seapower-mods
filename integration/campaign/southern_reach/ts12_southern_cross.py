"""TS12 - Southern Cross. Mid-Tasman, 2 March 2029.

The last mission: the relief convoy to New Zealand through a box with two
groups in it - the withdrawing group, neutral, complying with the
ceasefire, and the spoiler that is not. ROMEO is under the convoy if
Farncomb missed her, the strike flies if the carrier is afloat, and the
collector is revealed as the spoiler's spotter if Search Datum's crew came
home. Points zero; the epilogue reads the ledger.
"""
from campaign_data import U, F, S, HELO, RECON, CAP

MISSION = dict(
    code="TS12", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 12",
    group="core", num="12", key="Southern Cross", place="Mid-Tasman",
    intro="The relief convoy to New Zealand, two ships withdrawing under a "
          "nine-hour-old ceasefire, and a frigate that has not read it. Three of "
          "four hulls across, Coral Pioneer among them. The ledger closes "
          "here.",
    special=(
        "Final relief passage. Repairs and replacement allocations are available, but there is "
        "no ammunition resupply. The withdrawing formation is protected by the ceasefire and "
        "must not be attacked."
    ),
    sender="Commodore Alex Mercer",
    intent=("There is a ceasefire as of midnight and most of the group is "
            "keeping it: a frigate and the replenishment ship are steaming "
            "north out of the Tasman under it and they are neutral, "
            "whatever they were on Thursday. One frigate is not keeping "
            "it, and neither is whatever is under her or over her. The "
            "relief convoy - four hulls, Coral Pioneer among them - goes "
            "to New Zealand today and three of four get there. Fire on "
            "that frigate - the spoiler - when she fires. Do not fire on the "
            "withdrawing group, whatever it does, because the ceasefire is "
            "what three months at sea were for. This is the last one. Bring the escorts "
            "home."),
    date=(2029, 3, 2), time=(9, 15), sea=4, clouds="Scattered_2", wind="SW",
    difficulty=4, minutes=75, centre=(-40.5, 155.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "MID-TASMAN, 40 South, morning, under a ceasefire that is nine hours old. The "
            "relief convoy for New Zealand: CORAL PIONEER, the freighter AOTEAROA RELIEF, the "
            "bulker WAIRAU TRADER and the tanker TASMAN SPIRIT, eleven knots, east for "
            "Auckland, with your escorts - what the Tasman left of them - and KIWI 05 and "
            "WEDGETAIL 05 up. East Sale's and Williamtown's F-35As can give you fighter cover "
            "at the end of their reach.\\n\\nTwo groups are in the box. The WITHDRAWING GROUP - a"
            " Type 054A and the Qiongsha-class supply ship - is forty miles east steaming north"
            " under the ceasefire, complying, and is neutral. The SPOILER is a second Type 054A"
            " south-west of the convoy on a course to intercept it, with the research trawler "
            "NAN HAI 27 ahead of her, ROMEO under her if Farncomb missed her on 4 February, and"
            " a J-15 pair coming if LIAONING is afloat to send it.\\n\\nThree of four into the "
            "box east, Coral Pioneer among them. The spoiler is a target when she fires; the "
            "withdrawing group is not a target at all. A Tasman bulker and the "
            "Sydney-Wellington service are in the box. Seventy-five minutes and it is "
            "over.\\n\\nINTELLIGENCE: Joint reporting distinguishes the declared withdrawing "
            "formation from the suspected spoiler. Check those assessments against current "
            "movement, emissions and hostile acts. Shared ship classes or an old position "
            "report are insufficient to place both groups under the same engagement authority."
        )),
    forces=(
        "Your task group with its Seahawk, Poseidon and fighters if assigned, Kiwi 05, "
        "Wedgetail 05. Four convoy hulls. Neutral: the withdrawing Type 054A and the Qiongsha "
        "under the ceasefire, a bulker, an airliner. Opposing: the spoiler Type 054A, the "
        "research trawler Nan Hai 27, ROMEO if she is alive, a J-15 pair if Liaoning is."
    ),
    objectives=[
        ("Convoy", "Three of four convoy hulls into the box east, Coral "
                   "Pioneer among them", "40,-40,Fail,Main"),
        ("Ceasefire", "The withdrawing group is not a target", "20,-40,Complete"),
        ("Escorts", "Bring your flagship home", "15,-25,Complete"),
        ("Wedgetail", "Keep the Wedgetail flying", "10,-15,Complete"),
        ("Neutrals", "Harm no merchant or aircraft", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", min_units=3, objective="Convoy",
                 transit=11, also=[dict(units=["convoy#1"], min_units=1)]),
    fatal=[F("Convoy", ["convoy#1"]), F("Convoy", ["convoy"], 2)],
    neutral_objective="Neutrals",
    win=(
        "At least three merchants, including Coral Pioneer, have reached the Auckland handover "
        "and the withdrawing group remains protected. Account for the ships still at sea and "
        "maintain the ceasefire. Santos, from the bridge: 'Auckland on the bow. Southern Cross "
        "overhead. We are through.'"
    ),
    lose="The relief convoy is broken in the middle of the Tasman on the "
         "first morning of the ceasefire, or the ceasefire is broken by "
         "us. Either way the ledger closes in the red.",
    timeout=(
        "The convoy has not met the handover requirement within seventy-five minutes. Suspend "
        "the passage and report the ships' positions. Their eventual arrival and the spoiler's "
        "next move remain unconfirmed."
    ),
    stations={
        # The convoy and escorts on 080 for Auckland; the withdrawing
        # group 40 NM east on 000, neutral; the spoiler 30 NM south-west
        # routed onto the convoy with the collector ahead of her, ROMEO
        # under her if alive, the strike pair from the south-east if the
        # carrier is; the cockpits on the East Sale side.
        "convoy": S(-40.55, 155.30, "Relief convoy", heading=80),
        "escort": S(-40.60, 155.45, "Escort group", heading=80),
        "flight": S(-40.62, 155.43, "Ship's flight", heading=80, alt=500),
        "mpa": S(-40.80, 155.20, "Maritime patrol", heading=200, alt=12000),
        "cap": S(-40.30, 155.20, "Fighter cover", heading=200, alt=30000),
        "kiwi": S(-40.40, 155.90, "Kiwi 05", heading=80, alt=8000),
        "aew": S(-40.20, 155.00, "Wedgetail 05", heading=90, alt=32000),
        "withdrawing": S(-40.90, 156.20, "Withdrawing group", heading=0),
        "spoiler": S(-41.00, 155.00, "The spoiler", heading=40),
        "agi": S(-40.35, 155.75, "Research trawler", heading=80),
        "red_sub": S(-40.80, 154.90, "Contact ROMEO", heading=50),
        "red_air": S(-41.60, 156.60, "Strike pair", heading=320, alt=25000),
        "bulker": S(-40.20, 156.00, "Tasman bulker", heading=250),
        "airliner": S(-40.70, 154.80, "Sydney-Wellington", heading=90, alt=37000),
        "east_sale": S(-38.099, 147.149, "RAAF Base East Sale"),
        "williamtown": S(-32.795, 151.834, "RAAF Base Williamtown"),
        "ohakea": S(-40.206, 175.388, "RNZAF Base Ohakea"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          loadout="ASW", slot="Recon"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron1",
          slot="CAP"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron1",
          slot="CAP"),
        U("blue", "p-8-poseidon", "usn_p8", "kiwi", squadron="Squadron6",
          name="Kiwi 05", alt=8000, loadout="ASW"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 05",
          alt=32000, weapons="Hold"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "re-power-resupply", "civ_ms_freighter_d", "convoy",
          name="MV Aotearoa Relief"),
        U("blue", "auxilliary-merchant-pack", "anl_ms_bulk", "convoy",
          name="MV Wairau Trader", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_sealift_pacific", "convoy",
          name="MT Tasman Spirit"),
        # Under the ceasefire: neutral, complying, steaming north. The
        # neutral-loss rule ends the mission if the player fires on them.
        U("neutral", "modern-plan-systems", "plan_type_054a_p5", "withdrawing",
          name="Type 054A frigate (withdrawing under the ceasefire)",
          weapons="Hold", route=[(-39.50, 156.40, 0)], telegraph=3),
        U("neutral", "_vanilla", "plan_ap_qiongsha", "withdrawing",
          name="Qiongsha-class supply ship (withdrawing)",
          weapons="Hold", route=[(-39.50, 156.40, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "spoiler",
          name="Type 054A frigate (the spoiler)",
          route=[(-40.55, 155.60, 0)], telegraph=3),
        U("red", "_vanilla", "wp_agi_okean", "agi", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-40.45, 156.30, 0)], telegraph=2),
        U("red", "plan-submarines", "plan_ssn_type_093b", "red_sub", name="Contact ROMEO",
          depth="belowlayer", spawn_if=("TS05RomeoSunk", "IsFalse"),
          route=[(-40.55, 155.40, "belowlayer")], telegraph=3),
        # No field on the map for the pair: if the carrier is afloat she is
        # over the south-eastern horizon, and the engine's rule for a
        # base-less aircraft is unlimited fuel.
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 71", loadout="AntiShip",
          spawn_if=("TS11CarrierSunk", "IsFalse"),
          route=[(-40.55, 155.30, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 72", loadout="AntiShip",
          spawn_if=("TS11CarrierSunk", "IsFalse"),
          route=[(-40.55, 155.30, 20000)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Kaikoura (Wellington-Newcastle)",
          route=[(-40.60, 154.20, 0)], telegraph=3),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Sydney-Wellington 251", airway=(-41.33, 174.81)),  # Wellington
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_east_sale", "east_sale",
          name="RAAF Base East Sale", nation="australia", weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_williamtown", "williamtown",
          name="RAAF Base Williamtown", nation="australia", weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_rnzaf_ohakea", "ohakea",
          name="RNZAF Base Ohakea", nation="NewZealand", weapons="Hold"),
    ],
    resolve={"Convoy": "victory", "Neutrals": "neutral",
             "Ceasefire": ("spare", "withdrawing"),
             "Escorts": ("protect", "escort"),
             "Wedgetail": ("protect", "aew")},
    reveal_if=[dict(variable="SR03CrewRecovered", units=["agi"], level="Identify",
                    intel=(
                        "FUSION CELL: The Wilkins airlink search record of 12 December "
                        "identifies the collector ahead of the spoiler as NAN HAI 27. The "
                        "contact is identified on the plot and held there for the operation. "
                        "Intelligence assesses a possible "
                        "spotting role; the contents of its current transmissions remain "
                        "unknown."
                    ))],
    window=dict(buy=True, repair=True,
                allow=["ran_ffh_anzac", "ran_opv_arafura", "usn_mh-60r", "usn_p8",
                       "raaf_mq-4c_triton", "E7A_Wedgetail", "raaf_f-35a",
                       "usn_fa-18f_blk3", "usn_ea-18g"],
                flights=[HELO, RECON, CAP],
                situation=(
                    "Sydney can provide repairs and replacement allocations before the final "
                    "relief passage. No ammunition resupply is available; plan around what "
                    "remains after Approaches."
                )),
    role="escort",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 80, 15
