"""TS07 - Southern Air Bridge. The Tasman air route, 11 February 2029.

A civil charter and a Wedgetail across the air bridge into Sydney, the
destroyer's missiles the surface half of the umbrella and Williamtown's
fighters the other, with the carrier's flight routed onto the charter's
track. The first mission with airbase preparation: Williamtown is on the
plot as the player's field.
"""
from campaign_data import U, F, S, RECON, CAP

MISSION = dict(
    code="TS07", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 7",
    group="core", num="07", key="Southern Air Bridge", place="The Tasman air route",
    intro="A charter with the advance party of New Zealand's relief "
          "detachment for the Antarctic gateway, a Wedgetail beside it, and "
          "Liaoning's fighters routed onto its track. The destroyer and "
          "Williamtown are the umbrella.",
    special="For the first time Williamtown readies aircraft for you before "
            "you sail: two on the flight line and a third being turned round. "
            "What you stage there flies fighter cover.",
    sender="Wing Commander Daniel Ward, Air Component; Commodore Alex "
           "Mercer for the surface half",
    intent=((
        "RELIEF 21 is a civil Airbus charter with the advance party of New Zealand's relief "
        "detachment for the Antarctic gateway in it, and WEDGETAIL 06 is flying beside her "
        "because the carrier has put a flight onto the track twice this week to see what we do."
        " Today it is armed. Get the charter to the box off Sydney Heads with the destroyer's "
        "missiles underneath her and Williamtown's fighters above. The airliners on the same "
        "route are not to be shot at by anybody, maintain identification and keep the "
        "interception clear of civil traffic."
    )),
    date=(2029, 2, 11), time=(14, 15), sea=3, clouds="Scattered_1", wind="NE",
    difficulty=3, minutes=60, centre=(-36.0, 152.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "THE TASMAN AIR ROUTE, a hundred miles off the New South Wales coast, afternoon. "
            "RELIEF 21 - an A330, a civil charter carrying the New Zealand relief detachment's "
            "advance party - is inbound to Sydney on the air bridge with WEDGETAIL 06 beside "
            "her and SENTRY 23, a Triton, above them both. Two Sydney-Auckland services are on "
            "the same route and a cruise ship and a coastal bulker are under it.\\n\\nLIAONING is"
            " two hundred and fifty miles south-east. A J-15 pair with a J-15D behind them is "
            "routed onto the charter's track and the flight is assessed as an armed "
            "interception threat. Your force is on the track with the destroyer's missiles as "
            "the surface half of the umbrella; Williamtown is a hundred and ninety-five miles "
            "north, and its F-35As are available for fighter cover, readied on its flight line "
            "for the first time.\\n\\nRelief 21 to the box off Sydney Heads. Keep the Wedgetail "
            "flying. Nobody shoots at an airliner in this box, and the way to make sure of that"
            " is to be between the carrier's flight and both of them."
        )),
    forces=(
        "Your task group with its Poseidon and Williamtown fighters if assigned; Wedgetail 06; "
        "Sentry 23, a Triton; the charter Relief 21. Neutral: two Sydney-Auckland airliners, a "
        "cruise ship, a coastal bulker. Opposing: Liaoning to the south-east, a J-15 pair and a"
        " J-15D routed onto the track, a Ka-31 up."
    ),
    objectives=[
        ("Bridge", "Relief 21 reaches the box off Sydney Heads", "35,-35,Fail,Main"),
        ("Wedgetail", "Keep Wedgetail 06 flying", "15,-20,Complete"),
        ("Neutrals", "Harm no airliner, cruise ship or merchant", "0,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="relief", min_units=1, objective="Bridge",
                 at=(-33.85, 151.55), radius=10),
    fatal=[F("Bridge", ["relief"])],
    neutral_objective="Neutrals",
    win="Relief 21 is in the box off the Heads with the Wedgetail beside "
        "her and both airliners on schedule. Ward: 'They came to see what "
        "we do. Now they know.'",
    lose="The charter is down in the Tasman with the advance party in it, "
         "or the Wedgetail is. The air bridge closes and the relief "
         "detachment comes by sea, late.",
    timeout="Sixty minutes and Relief 21 is still short of the Heads with "
            "the carrier's flight between her and Sydney. She diverts to "
            "Williamtown, which is not what the bridge was for.",
    stations={
        # The charter and the Wedgetail 190 NM from the Heads on 320; the
        # Triton above; the force on the track; the fighters' cockpits and
        # the Poseidon's on the Williamtown side; the carrier 240 NM
        # south-east with its flight 150 NM out routed onto the track;
        # the airliners on the real route, the ships under it.
        "relief": S(-36.60, 153.30, "Relief 21", heading=320, alt=35000),
        "aew": S(-36.35, 152.95, "Wedgetail 06", heading=320, alt=32000),
        "high": S(-36.40, 153.20, "Sentry 23", heading=320, alt=50000),
        "escort": S(-36.00, 152.50, "Escort group", heading=320),
        "mpa": S(-36.20, 152.20, "Maritime patrol", heading=320, alt=12000),
        "cap": S(-35.70, 152.60, "Fighter cover", heading=140, alt=30000),
        "red_cv": S(-39.30, 155.60, "Carrier group", heading=320),
        "red_air": S(-38.00, 154.60, "Strike flight", heading=320, alt=25000),
        "red_helo": S(-39.10, 155.40, "Ka-31 orbit", heading=320, alt=9000),
        "airliner1": S(-35.20, 152.30, "Sydney-Auckland", heading=110, alt=37000),
        "airliner2": S(-36.30, 153.60, "Auckland-Sydney", heading=300, alt=36000),
        "cruise": S(-35.60, 152.00, "Cruise ship", heading=20),
        "bulker": S(-36.50, 151.60, "Coastal bulker", heading=30),
        "home": S(-32.795, 151.834, "RAAF Base Williamtown"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          loadout="ASW", slot="Recon"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron2",
          slot="CAP"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron2",
          slot="CAP"),
        U("blue", "civil-aircraft-airbus", "civ_a330", "relief",
          name="Relief 21 (NZ relief detachment charter)",
          alt=35000, weapons="Hold",
          route=[(-34.60, 152.10, 35000), (-33.85, 151.55, 20000)], telegraph=3),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 06",
          alt=32000, weapons="Hold"),
        U("blue", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "high",
          name="Sentry 23", weapons="Hold"),
        U("red", "liaoning-type-001", "plan_type_001", "red_cv", name="Liaoning",
          route=[(-38.60, 154.90, 0)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 41", loadout="AirToAir",
          route=[(-36.60, 153.30, 25000), (-34.60, 152.10, 25000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 42", loadout="AirToAir",
          route=[(-36.60, 153.30, 25000), (-34.60, 152.10, 25000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_air",
          name="Flying Shark 43", loadout="AntiShip",
          route=[(-36.00, 152.50, 20000)], telegraph=3),
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW"),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner1",
          name="Sydney-Auckland 147", airway=(-37.01, 174.79)),  # Auckland
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airliner2",
          name="Auckland-Sydney 802", airway=(-33.95, 151.18)),  # Sydney
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Pacific Aurora (Sydney-bound cruise)",
          route=[(-34.00, 151.60, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Illawarra (Melbourne-Newcastle)",
          route=[(-34.20, 151.90, 0)], telegraph=3),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_williamtown", "home",
          name="RAAF Base Williamtown", nation="australia", weapons="Hold"),
    ],
    resolve={"Bridge": "victory", "Neutrals": "neutral",
             "Wedgetail": ("protect", "aew"),
             "Flagship": ("protect", "escort")},
    window=dict(buy=True, repair=True, rearm=True, airbase_prep=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "ran_opv_arafura",
                       "usn_mh-60r", "usn_p8", "raaf_mq-4c_triton", "E7A_Wedgetail",
                       "raaf_f-35a", "usn_fa-18f_blk3", "usn_ea-18g"],
                flights=[RECON, CAP],
                situation=(
                    "Sydney, before the air bridge. Force allocation, repairs and ammunition "
                    "resupply, and for the first time Williamtown readies aircraft for you: two"
                    " on the flight line, a third being turned round. Great Australian Bight "
                    "has repair only; the next full window is Adelaide, before the Southern "
                    "Convoy."
                )),
    role="escort",
)
