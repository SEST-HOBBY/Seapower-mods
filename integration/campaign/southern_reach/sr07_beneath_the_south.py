"""SR07 - Beneath the South. The deep Southern Ocean, 24 December 2028.

The first authorised kill of the campaign: the boat that fired on the
coaster. Difficulty is depth, route, search area and what the player brought
to the hunt; the tender she lives off is a merchant hull under a state flag
and sinking it is the incident Canberra will not own. What Collins put a
name to on the ninth is on the plot from the first minute.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="SR07", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 7",
    group="core", num="07", key="Beneath the South", place="The deep Southern Ocean",
    intro="Christmas Eve at 57 South. The boat that fired on the coaster is "
          "the task group's to sink, and the research vessel it lives off "
          "is not.",
    sender="Commodore Alex Mercer",
    intent=("Canberra and Wellington said the same thing on the same "
            "afternoon: find the boat that fired and sink her. That is the "
            "whole authorisation. The tender is a research vessel with a "
            "flag and a science party, and the day you sink her is the day "
            "this stops being a torpedo attack on a coaster and becomes "
            "something with a name. The Poseidon is out of Hobart with fuel "
            "for one field of buoys; the Seahawk is what you have after "
            "that. Use the water. She has to come to the tender, and the "
            "tender is where you can see it."),
    date=(2028, 12, 24), time=(13, 30), sea=6, clouds="Overcast", wind="W",
    difficulty=3, minutes=80, centre=(-57.5, 152.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "THE DEEP SOUTHERN OCEAN, 57 South, Christmas Eve. VICTOR fired on "
        "DERWENT SPIRIT on the twenty-first and has been running south ever "
        "since, toward the research vessel that keeps her at sea. The "
        "vessel is here, sixty miles south-west, holding station where the "
        "boat will come to her.\\n\\n"
        "You have what you rearmed at Bluff, the Seahawk, and a Poseidon out "
        "of Hobart with fuel for one field of buoys before she has to turn "
        "for home - the Wedgetail cannot fly in this and the Triton is on "
        "the ground. A Bear-F is coming to look at what you are doing.\\n\\n"
        "Sink VICTOR. Leave RV AKADEMIK FERSMAN alone whatever she does - "
        "she is a merchant hull under a state flag with forty scientists "
        "aboard, and she is not the boat. A factory trawler and a whale are "
        "in the same water."),
    forces="Your escort group with its Seahawk and Poseidon, out of Hobart. "
           "Opposing: one Akula, her tender, a Bear-F with tanker support. "
           "Neutral: a factory trawler, a whale.",
    objectives=[
        ("Boat", "Sink VICTOR", "40,-35,Fail,Main"),
        ("Tender", "Leave the research vessel alone", "10,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
        ("Neutrals", "Harm no trawler or whale", "0,-20,Complete"),
    ],
    victory=dict(kind="destroy", stations=["red_sub"], min_units=1, objective="Boat"),
    fatal=[],
    neutral_objective="Neutrals",
    win="VICTOR is on the bottom at 57 South. The research vessel is still "
        "afloat, still flagged and still researching, which is the sentence "
        "Canberra wanted to be able to say on Boxing Day.",
    lose="The escort is gone and the boat is not. The route south is hers "
         "for the rest of the season.",
    timeout="Eighty minutes and VICTOR is still a contact. She has her "
            "tender and the ice edge to hide in, and the January voyage "
            "sails through her.",
    stations={
        # The hunt: VICTOR 30 NM south-east at belowlayer, routed across the
        # escorts' bow toward her tender; the tender 60 NM south-west, holding
        # station; the Poseidon's cockpit on the threat axis; the Bear's pass
        # over the group; a trawler and a whale in the water.
        "escort": S(-57.40, 151.80, "Escort", heading=150),
        "flight": S(-57.42, 151.78, "Ship's flight", heading=150, alt=500),
        "mpa": S(-57.80, 152.60, "Maritime patrol", heading=300, alt=8000),
        "red_sub": S(-57.85, 152.30, "Contact VICTOR", heading=320),
        "tender": S(-58.10, 151.20, "Research vessel", heading=60),
        "bear": S(-58.60, 150.80, "Bear-F", heading=40, alt=6000),
        "fleet": S(-57.20, 152.50, "Factory trawler", heading=250),
        "whale": S(-57.55, 152.15, "Biologic", heading=180),
        "home": S(-42.836, 147.510, "Hobart Airport"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=8000,
          loadout="ASW", slot="Recon"),
        U("red", "russian-submarines", "wp_ssn_akula", "red_sub", name="Contact VICTOR",
          depth="belowlayer",
          route=[(-57.55, 151.95, "belowlayer"), (-57.30, 151.60, "belowlayer"),
                 (-57.90, 151.30, "belowlayer")],
          telegraph=2),
        U("red", "_vanilla", "civ_ms_kommunist", "tender",
          name="RV Akademik Fersman (research vessel, tender)", weapons="Hold",
          route=[(-57.90, 151.80, 0)], telegraph=1),
        U("red", "_vanilla", "wp_tu-142m", "bear", name="Bear-F 24", alt=6000,
          weapons="Hold", loadout="ASW",
          route=[(-57.60, 152.00, 6000), (-56.90, 152.80, 6000)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 29",
          route=[(-57.50, 151.90, 0)], telegraph=2),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic JULIET",
          depth="shallow"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Hobart Airport (RAAF detachment)", nation="australia", weapons="Hold"),
    ],
    resolve={"Boat": "victory", "Neutrals": "neutral",
             "Tender": ("spare", "tender"),
             "Flagship": ("protect", "escort")},
    declares=["SR07AkulaSunk"],
    flags=[dict(name="SR07AkulaSunk", units=["red_sub"],
                intel="VICTOR is on the bottom. The boat that fired the first "
                      "shot in the south will not be in the line at the ice "
                      "edge, and the research vessel has nothing left to "
                      "tend.")],
    reveal_if=[dict(variable="SR02BoatNamed", units=["red_sub"], level="Classify",
                    intel="Collins's datum from the ninth: VICTOR is on your "
                          "plot as a classified contact from the first minute, "
                          "with the signature Rewi's crew logged on the ridge. "
                          "You know what she sounds like. Now find where.")],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "usn_mh-60r", "usn_p8",
                       "raaf_mq-4c_triton", "E7A_Wedgetail"],
                flights=[HELO, RECON],
                situation="Christmas at Bluff. Requisition, repair and a full "
                          "rearm before Beneath the South - Bluff's slipway and "
                          "Invercargill's field are New Zealand's contribution "
                          "and they are open. The next window is at Lyttelton, "
                          "before Cold Route."),
    role="escort",
)
