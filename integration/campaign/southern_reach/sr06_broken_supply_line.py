"""SR06 - Broken Supply Line. South of the Auckland Islands, 21 December 2028.

The fuel coaster with one engine and a hull patch, six knots by the Chief's
word (telegraph 1 on her route: the engine has no damage to author), and
the boat that did it ahead of her track. The persistent force escorts her
the last miles toward Bluff on what it has left - the rearm before this
mission is Macquarie Passage's window, held or not.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="SR06", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 6",
    group="core", num="06", key="Broken Supply Line", place="South of the Auckland Islands",
    intro="The fuel coaster Derwent Spirit took a torpedo and is making six "
          "knots for Bluff. The Akula that fired is ahead of her, and this is what you have "
          "left to stop it with.",
    special="No requisition before this operation: you sail what you own, "
            "rearmed only if Supply and Coral Pioneer held the Macquarie "
            "service window. The coaster makes six knots because her Chief "
            "says so, and the handover line with Bluff's tug is set for six knots.",
    sender="Commodore Alex Mercer; Commander Tessa Brand, RNZN, for Bluff",
    intent=("DERWENT SPIRIT was hit at 0210 south of the Auckland Islands, "
            "in New Zealand's search and rescue region and in nobody's war. "
            "She is making six knots for Bluff on one engine with CORAL "
            "PIONEER in company. The boat that hit her is somewhere ahead of "
            "her track, and a frigate that calls itself fisheries protection "
            "is shadowing from the east with a helicopter up. Bring the "
            "coaster north-east to the handover line, where Bluff's tug will "
            "meet her. Do not drive her faster than the Chief says she will "
            "go. If the boat fires again you answer her. The hunt for "
            "her is Wellington's question and Canberra's, and neither has "
            "answered it yet."),
    date=(2028, 12, 21), time=(5, 50), sea=5, clouds="Overcast", wind="SW",
    difficulty=3, minutes=75, centre=(-51.5, 165.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "SOUTH OF THE AUCKLAND ISLANDS, early morning. DERWENT SPIRIT took a "
        "torpedo forward at 0210 - the first shot fired in the south - and "
        "she is still afloat because the Chief got a collision mat over the "
        "hole and the tanks aft are full. One engine, six knots, Bluff. "
        "CORAL PIONEER is in company because her master, Leila Santos, would not be "
        "elsewhere.\\n\\n"
        "The boat that fired is VICTOR, the Akula HMAS Collins named on the "
        "Macquarie Ridge on the ninth, and "
        "she is ahead of the coaster's track, somewhere between here and "
        "the islands. A Type 054A flying the fisheries-protection flag is fifty miles "
        "east with its helicopter up and has been keeping station on the "
        "coaster since first light, which is not something a fisheries "
        "patrol does. A Bear is overhead.\\n\\n"
        "You have what you own and what Macquarie left in the magazines. "
        "Bring the coaster to the handover line. The expedition ship out of the "
        "islands, the longliner and the whale are in the same water; nobody "
        "in New Zealand's region will forgive a dead tourist. Weapons tight "
        "on anything that has not fired; on the boat, answer her if she "
        "fires again - the hunt waits on Wellington and Canberra."),
    forces="Your escort group with its Seahawk; your Poseidon out of "
           "Invercargill. MT Derwent Spirit at six knots and MV Coral "
           "Pioneer in company. Neutral: an expedition ship out of the "
           "islands, a Bluff longliner, a whale. Opposing: one Akula ahead of "
           "the track, a Type 054A shadowing with a Z-9 up, a Bear-D overhead.",
    objectives=[
        ("Coaster", "Bring DERWENT SPIRIT to the handover line", "35,-35,Fail,Main"),
        ("Cargo", "MV Coral Pioneer must survive", "15,-25,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
        ("Neutrals", "Harm no expedition ship, fishing boat or whale", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="coaster", units=["coaster#1"], min_units=1,
                 objective="Coaster", transit=6),
    fatal=[F("Coaster", ["coaster#1"])],
    neutral_objective="Neutrals",
    win="Derwent Spirit is at the line with a tug coming down from Bluff, "
        "and Coral Pioneer is beside her. The Chief's mat held. Brand: 'She "
        "is in our hands now. Nobody touches her.'",
    lose="The coaster is gone with the winter's fuel in her, three hundred "
         "miles from a slipway. Casey's January is a different problem now.",
    timeout="Seventy-five minutes and the coaster is still short of the line "
            "with a boat somewhere ahead of her. The tug from Bluff has "
            "nothing to meet yet.",
    stations={
        # The coaster and Coral Pioneer on the track north-east; the escorts
        # five miles astern; VICTOR 30 NM ahead across the track, routed
        # onto it; the frigate 50 NM east closing slowly with its Z-9; the
        # neutrals inside the picture with routes.
        "coaster": S(-51.55, 164.90, "Derwent Spirit", heading=40),
        "escort": S(-51.60, 164.80, "Escort", heading=40),
        "flight": S(-51.62, 164.78, "Ship's flight", heading=40, alt=500),
        "mpa": S(-51.20, 165.60, "Maritime patrol", heading=200, alt=10000),
        "red_sub": S(-51.05, 165.55, "Contact VICTOR", heading=220),
        "red_sag": S(-51.30, 166.20, "Shadowing frigate", heading=280),
        "red_helo": S(-51.28, 166.00, "Z-9", heading=280, alt=1500),
        "bear": S(-52.30, 164.00, "Bear-D", heading=30, alt=20000),
        "expedition": S(-51.00, 165.90, "Expedition ship", heading=350),
        "longliner": S(-51.80, 165.40, "Longliner", heading=120),
        "whale": S(-51.40, 165.20, "Biologic", heading=60),
        "home": S(-46.412, 168.313, "Invercargill Airport"),
    },
    units=[
        # Telegraph 1 on her route is the six knots; the rest is the Chief.
        U("blue", "SEST_Replenishment", "civ_ms_sealift_pacific", "coaster",
          name="MT Derwent Spirit (one engine)",
          route=[(-51.20, 165.40, 0), (-50.90, 165.90, 0)], telegraph=1),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "coaster",
          name="MV Coral Pioneer",
          route=[(-51.20, 165.45, 0), (-50.90, 165.95, 0)], telegraph=1),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=10000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("red", "russian-submarines", "wp_ssn_akula", "red_sub", name="Contact VICTOR",
          depth="belowlayer",
          route=[(-51.35, 165.15, "belowlayer"), (-51.50, 164.95, "belowlayer")],
          telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_sag",
          name="Fisheries protection frigate", weapons="Tight",
          route=[(-51.25, 165.60, 0)], telegraph=2),
        U("red", "modern-plan-systems", "plan_z-9c", "red_helo", name="Z-9 shadow",
          alt=1500, weapons="Tight", loadout="ASWKiller"),
        U("red", "_vanilla", "wp_tu-95rt", "bear", name="Bear-D 31", alt=20000,
          weapons="Hold", route=[(-51.30, 165.40, 20000), (-50.50, 166.00, 20000)],
          telegraph=3),
        U("neutral", "_vanilla", "civ_ms_encounter", "expedition",
          name="MV Enderby Expedition (Auckland Islands charter)",
          route=[(-50.50, 165.60, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "longliner",
          name="Longliner Toroa (Bluff)", route=[(-52.10, 165.90, 0)], telegraph=2),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic INDIA",
          depth="shallow"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Invercargill Airport (RNZAF/RAAF detachment)", nation="NewZealand",
          weapons="Hold"),
    ],
    resolve={"Coaster": "victory", "Neutrals": "neutral",
             "Cargo": ("protect", "coaster#2"),
             "Flagship": ("protect", "escort")},
    window=dict(rearm_if=("SR04ServiceHeld", "IsTrue"), flights=[HELO, RECON]),
    role="escort",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 40, 10
