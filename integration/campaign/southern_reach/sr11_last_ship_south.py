"""SR11 - Last Ship South. The deep transit, 10 January 2029.

The last voyage with a materially worn force: no field within a Poseidon's
radius (Hobart is 1,082 NM, on purpose), the Seahawk the only aviation, a
rearm only if Cold Route was held, and the tanker only if Cold Route did
not sink her. Two escorts and a boat across the track; a strike pair from a
carrier over the horizon.
"""
from campaign_data import U, F, S, HELO

MISSION = dict(
    code="SR11", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 11",
    group="core", num="11", key="Last Ship South", place="The deep transit",
    intro="The last voyage south with what is left: Southern Endeavour, the "
          "tanker if she lived, a Seahawk, and magazines that are what Cold "
          "Route left them.",
    special="No requisition before this operation. The rearm before it is "
            "paid with Cold Route: hold that route and the magazines are "
            "full here; lose it and they are what Cold Route left. No "
            "Poseidon reaches this water from any field.",
    sender="Commodore Alex Mercer; Dr Helen Marsh, RSV Southern Endeavour, for the voyage",
    intent=("SOUTHERN ENDEAVOUR is the winter. She goes south whatever else "
            "does. Two escorts of the group are coming north to meet her "
            "and a boat is across the track; the carrier is over the "
            "horizon to the east with a pair up. There is no Poseidon, no "
            "Wedgetail and no fighter for any of it, and Dr Marsh has asked "
            "me, in writing, whether the escort will be there the whole "
            "way. I told her yes."),
    date=(2029, 1, 10), time=(7, 40), sea=6, clouds="Overcast", wind="W",
    difficulty=4, minutes=80, centre=(-55.5, 128.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE DEEP TRANSIT, 55 South, morning. SOUTHERN ENDEAVOUR is on the "
        "last voyage of the season with Casey's winter aboard; DERWENT "
        "SPIRIT is in company if Cold Route left her afloat. Twelve knots, "
        "south-west, and what remains of the force around them.\\n\\n"
        "The frigate and the corvette that screened the carrier on the "
        "second are coming north-east to meet the voyage; the nuclear boat "
        "that was ahead of the January convoy is across this track too. The "
        "carrier is two hundred miles east and has a pair loaded for ships "
        "with its Ka-31 up. Hobart is eleven hundred miles behind you - "
        "nothing with wings reaches here and comes home. The Seahawk is your "
        "aviation and the magazines are what Cold Route left.\\n\\n"
        "Bring Southern Endeavour to the handover line. Bring the tanker if "
        "she is with you. The trawler and the whale are in the same water."),
    forces="What remains of your task group, with its Seahawk. RSV Southern "
           "Endeavour; MT Derwent Spirit if she survived Cold Route. "
           "Opposing: a Type 054A and a Type 056A closing, a Type 093B "
           "across the track, a J-15 pair with a Ka-31 from a carrier over "
           "the horizon. Neutral: a factory trawler, a whale.",
    objectives=[
        ("Endeavour", "Bring RSV Southern Endeavour to the handover line",
         "40,-40,Fail,Main"),
        ("Tanker", "Do not lose Derwent Spirit, if she sailed", "0,-20,None"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
        ("Neutrals", "Harm no trawler or whale", "0,-20,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", units=["convoy#1"], min_units=1,
                 objective="Endeavour", transit=12),
    fatal=[F("Endeavour", ["convoy#1"])],
    neutral_objective="Neutrals",
    win="Southern Endeavour is at the line and Casey has its winter. "
        "Whatever the escort spent getting her there is in the ledger; "
        "Marsh's message, in full: 'You were.'",
    lose="The last ship south is lost with the winter in her. The stations "
         "close early, and the season the task group sailed to keep is "
         "over.",
    timeout="Eighty minutes and the Endeavour is short of the line with a "
            "frigate closing and a boat under her. The voyage turns back "
            "for Hobart, and Casey winters on what it has.",
    stations={
        # The voyage on 250; the escorts five miles astern; the boat 25 NM
        # west across the track; the two escorts 45 NM south-west closing;
        # the strike pair 90 NM east with the AEW helicopter, routed onto
        # the voyage. No field anywhere: the Seahawk is the aviation.
        "convoy": S(-55.30, 128.40, "Last voyage", heading=250),
        "escort": S(-55.35, 128.55, "Escort", heading=250),
        "flight": S(-55.37, 128.53, "Ship's flight", heading=250, alt=500),
        "red_sag": S(-55.90, 127.30, "Escorts closing", heading=60),
        "red_sub": S(-55.55, 127.70, "Contact ROMEO", heading=80),
        "red_air": S(-56.00, 130.60, "Strike pair", heading=300, alt=25000),
        "red_helo": S(-55.90, 130.20, "Ka-31 orbit", heading=300, alt=9000),
        "fleet": S(-55.70, 128.90, "Factory trawler", heading=250),
        "whale": S(-55.45, 128.10, "Biologic", heading=270),
    },
    units=[
        U("blue", "re-power-resupply", "civ_ms_freighter_d", "convoy",
          name="RSV Southern Endeavour (resupply ship, stand-in)"),
        # Only if Cold Route did not sink her: the spawn reads the flag the
        # support-loss trigger there writes.
        U("blue", "re-power-resupply", "civ_ms_sealift_pacific", "convoy",
          name="MT Derwent Spirit", spawn_if=("SR09TankerLost", "IsFalse")),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_sag",
          name="Type 054A frigate", route=[(-55.35, 128.30, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_056a", "red_sag",
          name="Type 056A corvette", route=[(-55.35, 128.30, 0)], telegraph=3),
        U("red", "plan-submarines", "plan_ssn_type_093b", "red_sub", name="Contact ROMEO",
          depth="belowlayer", route=[(-55.35, 128.20, "belowlayer")], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 21", loadout="AntiShip",
          route=[(-55.30, 128.40, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 22", loadout="AntiShip",
          route=[(-55.30, 128.40, 20000)], telegraph=3),
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW"),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 24",
          route=[(-55.90, 128.40, 0)], telegraph=2),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic LIMA",
          depth="shallow"),
    ],
    resolve={"Endeavour": "victory", "Neutrals": "neutral",
             "Tanker": ("protect", "convoy#2"),
             "Flagship": ("protect", "escort")},
    window=dict(rearm_if=("SR09ColdRouteHeld", "IsTrue"), flights=[HELO]),
    role="escort",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 250, 12
