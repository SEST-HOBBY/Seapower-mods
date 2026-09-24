"""SR04 - Macquarie Passage. Macquarie Island, 15 December 2028.

The island's resupply is a service window, not a mechanic: HMAS Supply and
Coral Pioneer have to be inside five miles of the Buckles Bay anchorage when
thirty minutes have run, and then come north together to the withdrawal
line. A Russian boat is closing from the south-west, its tender is keeping
station to the west, and a Bear-F comes to look. Holding the window is what
Broken Supply Line's rearm is paid with.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="SR04", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 4",
    group="core", num="04", key="Macquarie Passage", place="Macquarie Island",
    intro="Supply and Coral Pioneer in Buckles Bay for the service window the "
          "island's weather allows one day in three, with a Russian boat "
          "closing and a Bear coming to look.",
    special="Hold the service window and Broken Supply Line begins with a full "
            "rearm; miss it and Broken Supply Line sails on what you have "
            "left. The rule is the box at the moment the window closes.",
    sender="Commodore Alex Mercer",
    intent=("Thirty minutes in the anchorage for Supply and Coral Pioneer, "
            "and then both of them north together to the line. The island "
            "gets its year in those thirty minutes. A boat is coming up from "
            "the south-west to look at the anchorage and a Bear is coming to "
            "look at you; the tender west of the island is a research vessel "
            "with a science party and a flag. Nothing here has fired and you "
            "do not fire first. The window is the win."),
    date=(2028, 12, 15), time=(7, 10), sea=5, clouds="Overcast", wind="W",
    difficulty=3, minutes=75, centre=(-54.3, 158.3),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "MACQUARIE ISLAND, first light. SUPPLY and CORAL PIONEER are in "
        "Buckles Bay under the station, with the island's year going ashore "
        "by boat and by helicopter while the weather allows it, which is "
        "about one day in three. This is the day.\\n\\n"
        "The service window is thirty minutes and it runs on the clock, not "
        "on what crosses the beach. Both ships have to be inside the service "
        "box - five miles around the anchorage - when the window closes; "
        "what you do with them in between is your judgement. Hold it and "
        "Broken Supply Line starts with full magazines; miss it and it sails "
        "on what you have. When the thirty minutes are up, both ships come "
        "north together to the withdrawal line.\\n\\n"
        "The boat Collins named on the ridge, or one very like it, is "
        "forty-five miles south-west and closing at twenty knots. The "
        "Russian research vessel that keeps station west of the island is "
        "her tender, and a Bear-F is coming down the outside of the box "
        "with a Midas somewhere behind it. The Bear is a reconnaissance "
        "flight until it is not; the tender is a research vessel with a "
        "flag. Your weapons are tight. Hold the window and get everybody "
        "out of it."),
    forces="HMAS Supply and MV Coral Pioneer at the anchorage, your escort "
           "group with its Seahawk and Poseidon if bought. The station "
           "ashore. Opposing: one Akula closing from the south-west, its "
           "tender to the west, one Bear-F with tanker support. A longliner "
           "and a whale east of the island.",
    objectives=[
        ("Service", "Hold the service box for the 30-minute window, then "
                    "bring SUPPLY and CORAL PIONEER north together to the "
                    "withdrawal line", "35,-35,Fail,Main"),
        ("Supply", "HMAS Supply must survive", "20,-30,Complete"),
        ("Cargo", "MV Coral Pioneer must survive", "15,-25,Complete"),
        ("Restraint", "Fire on nothing that has not fired: the Bear and the "
                      "tender are not targets", "10,-20,Complete"),
        ("Neutrals", "Harm no fishing boat or whale", "0,-25,Complete"),
    ],
    # Supply AND Coral Pioneer, still inside five miles of Supply's start
    # when the clock reaches thirty minutes (the 03 Lifeline Trigger8 shape),
    # then both to the line twenty miles north. The line is authored: the
    # solver does not know the first thirty minutes are spent at anchor.
    victory=dict(kind="arrive", units=["support#1", "support#2"], min_units=2,
                 station="support", objective="Service",
                 at=(-54.17, 159.05), radius=12,
                 after=dict(kind="area", units=["support#1", "support#2"],
                            at_unit="support#1", radius=5, min_units=2,
                            after_minutes=30, sets="SR04ServiceHeld",
                            intel="The window has run. The station has its "
                                  "year and the last boat is hoisted. Bring "
                                  "SUPPLY and CORAL PIONEER north together to "
                                  "the withdrawal line before the boat from the "
                                  "south-west is inside the bay.")),
    fatal=[F("Supply", ["support#1"]), F("Cargo", ["support#2"])],
    neutral_objective="Neutrals",
    win="The window held and both ships are north of the line. Macquarie "
        "Island has its year, Broken Supply Line has its magazines, and the "
        "Bear went home with photographs of a resupply.",
    lose="The anchorage is broken. The island gets what was ashore before "
         "the window closed and nothing more until next summer.",
    timeout="Seventy-five minutes and the ships are still south of the "
            "line with a boat somewhere in the bay. Whatever crossed the "
            "beach, the group is not out of the anchorage, and the Bear has "
            "the photographs.",
    stations={
        # Buckles Bay, east of the isthmus, 1 NM off the beach: a coastal
        # station, each hull on its own sea check. The escorts five miles
        # east in open water; the Poseidon's cockpit north; the boat 55 NM
        # south-west routed round the north tip of the island into the bay,
        # in the bay about when the window closes.
        "support": dict(S(-54.50, 158.99, "Service group", heading=20), coastal=True),
        "escort": S(-54.45, 159.12, "Escort", heading=0),
        "flight": S(-54.46, 159.10, "Ship's flight", heading=0, alt=500),
        "mpa": S(-54.10, 158.60, "Maritime patrol", heading=200, alt=12000),
        "station": S(-54.499, 158.937, "Macquarie Island station"),
        "red_sub": S(-54.95, 157.60, "Contact VICTOR", heading=40),
        "tender": S(-54.55, 157.70, "Research vessel", heading=90),
        "bear": S(-55.40, 157.20, "Bear-F", heading=40, alt=8000),
        "longliner": S(-54.70, 159.40, "Longliner", heading=30),
        "whale": S(-54.20, 158.90, "Biologic", heading=180),
        "home": S(-42.836, 147.510, "Hobart Airport"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_aor_supply", "support", variant="Variant1",
          name="HMAS Supply", weapons="Tight"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "support",
          name="MV Coral Pioneer"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("neutral", "_vanilla", "civ_radiostation", "station",
          name="Macquarie Island station"),
        U("red", "russian-submarines", "wp_ssn_akula", "red_sub", name="Contact VICTOR",
          depth="belowlayer", weapons="Tight",
          route=[(-54.60, 158.60, "belowlayer"), (-54.42, 158.80, "belowlayer"),
                 (-54.45, 159.00, "belowlayer")],
          telegraph=4),
        U("red", "_vanilla", "civ_ms_kommunist", "tender",
          name="RV Akademik Fersman (research vessel, tender)", weapons="Hold",
          route=[(-54.50, 158.00, 0)], telegraph=1),
        # A reconnaissance pass over the anchorage. No field on the map for a
        # Bear: the engine's own rule for a base-less aircraft is unlimited
        # fuel, and the briefing says a Midas is behind it.
        U("red", "_vanilla", "wp_tu-142m", "bear", name="Bear-F 22", alt=8000,
          weapons="Hold", loadout="ASW",
          route=[(-54.50, 159.00, 8000), (-53.80, 159.60, 8000)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_d", "longliner",
          name="Longliner Austral Leader", route=[(-54.30, 159.80, 0)], telegraph=2),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic GOLF",
          depth="shallow"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Hobart Airport (RAAF detachment)", nation="australia", weapons="Hold"),
    ],
    resolve={"Service": "victory", "Neutrals": "neutral",
             "Supply": ("protect", "support#1"),
             "Cargo": ("protect", "support#2"),
             "Restraint": ("spare", "bear", "tender")},
    declares=["SR04ServiceHeld"],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "usn_mh-60r", "usn_p8",
                       "raaf_mq-4c_triton", "E7A_Wedgetail"],
                flights=[HELO, RECON],
                situation="Requisition before Macquarie Passage. The Wedgetail "
                          "goes on sale here and recovers at Hobart. Broken Supply "
                          "Line gets no builder and its rearm depends on the "
                          "service window; the next window is Christmas at Bluff, "
                          "before Beneath the South."),
    role="logistics",
)
