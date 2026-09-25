"""SR03 - Search Datum. The southern route, 12 December 2028.

A large-area search with benign contacts and one story-critical datum. The
Wilkins airlink went out of contact on the Hobart-Casey track; an EPIRB was
heard by a longliner; the crew are aboard a foreign trawler that "recovered"
them and is holding position for the collector. Find which of six contacts
she is, classify her, and put the escort alongside. Sinking her is a fatal:
the people are aboard.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="SR03", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 3",
    group="core", num="03", key="Search Datum", place="The southern route",
    intro="The Wilkins airlink is missing on the southern route. Six contacts "
          "in the search box, and one of them has the crew aboard and no "
          "intention of bringing them home.",
    sender="Commodore Alex Mercer; Wing Commander Daniel Ward for the search plan",
    intent=("WILKINS 03 put down on the water at 0410 and her crew are alive: "
            "the EPIRB says so and so does the longliner that heard it. "
            "Something recovered them before we could, and it is not steaming "
            "for Hobart. Find it among the traffic, classify it, and put a "
            "ship alongside. Do not fire at anything on the water today - the "
            "people we want are on one of those decks."),
    date=(2028, 12, 12), time=(9, 15), sea=5, clouds="Overcast", wind="W",
    difficulty=2, minutes=70, centre=(-52.0, 140.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE SOUTHERN ROUTE, mid-morning. WILKINS 03, the airlink to the ice, "
        "lost contact on the Hobart-Casey track at 0352 and put down on the "
        "water eighteen minutes later. Her EPIRB ran for forty minutes and "
        "then stopped, which is what happens when somebody switches it "
        "off.\\n\\n"
        "A longliner heard it and reported it. A factory trawler from the "
        "fleet that shadowed the Storm Bay convoy was closer, and the "
        "trawler is now holding position sixty miles west of the datum, "
        "answering nobody, with the research trawler NAN HAI 27 steaming to "
        "meet her.\\n\\n"
        "You have your escort group with the Seahawk and the Poseidon you "
        "brought, and SENTRY 21 high to the south. Six contacts are in the "
        "search box: longliners, a factory trawler that is only fishing, the "
        "expedition cruise ship POLAR HORIZON southbound, a whale, and the "
        "one that matters. Classify her and put your flagship within three "
        "miles of her. Your weapons are tight, and a shot at the wrong hull is a "
        "shot at the crew."),
    forces="Your escort group with one MH-60R and one P-8A if bought, one "
           "MQ-4C Triton overhead. Neutral: two longliners, a factory "
           "trawler, an expedition cruise ship, a whale. Opposing: the "
           "trawler holding the crew, unarmed; the research trawler Nan Hai "
           "27 closing to meet her.",
    objectives=[
        ("Datum", "Classify the trawler holding the crew, then put your "
                  "flagship within three miles of her", "35,-35,Fail,Main"),
        ("Neutrals", "Harm no fishing boat, cruise ship or whale", "0,-40,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
        ("Collector", "Classify Nan Hai 27 as well", "10,0,None"),
    ],
    # The trawler is hove to, waiting for the collector, so the box is drawn
    # on her: nothing counts until she is classified, and then the flagship
    # has to reach her. A slot-tagged Seahawk cannot be named by a trigger,
    # so it is the ship that goes alongside.
    victory=dict(kind="arrive", station="escort", min_units=1, objective="Datum",
                 at=(-52.25, 139.65), radius=3, sets="SR03CrewRecovered",
                 after=dict(kind="classify", units="datum", min_units=1,
                            intel="NAN HAI 24 classified: the Okean hull with "
                                  "her nets stowed and eleven people on deck who "
                                  "are not fishermen. She is holding for the "
                                  "collector. Get the flagship alongside before "
                                  "it arrives.")),
    fatal=[F("Datum", ["datum"])],
    neutral_objective="Neutrals",
    win="A boarding party is on Nan Hai 24's deck and the airlink's crew are "
        "in the flagship's wardroom. The trawler's master says he was taking "
        "them to the nearest medical facility. He was steaming away from it.",
    lose="The trawler is gone west with the crew aboard, or gone under with "
         "them. Either way Wilkins 03's people do not come home this week.",
    timeout="The search box is worked and the collector has the trawler in "
            "company, and both are steaming west with the crew aboard. The "
            "search is over; the negotiation starts.",
    stations={
        # The escort group and its slots north-east of the datum; the datum
        # 18 NM south-west, hove to; the collector 45 NM off closing on her;
        # the six contacts spread across the box with routes through it.
        "escort": S(-52.00, 139.90, "Escort group", heading=220),
        "flight": S(-52.02, 139.88, "Ship's flight", heading=220, alt=500),
        "mpa": S(-52.30, 140.40, "Maritime patrol", heading=250, alt=15000),
        "high": S(-52.60, 139.50, "Sentry 21", heading=270, alt=50000),
        "datum": S(-52.25, 139.65, "Trawler holding the crew", heading=300),
        "shadow": S(-52.50, 139.00, "Research trawler", heading=40),
        "longliner": S(-52.20, 140.50, "Longliner", heading=60),
        "okean": S(-52.50, 140.20, "Factory trawler", heading=200),
        "side": S(-51.70, 139.50, "Longliner", heading=320),
        "cruise": S(-51.60, 140.60, "Polar Horizon", heading=190),
        "whale": S(-52.30, 139.70, "Biologic", heading=90),
        "home": S(-42.836, 147.510, "Hobart Airport"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        # Air-tasking placeholders: the cockpits a purchased Seahawk and
        # Poseidon take. Unnamed, and named by no trigger.
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=15000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("blue", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "high",
          name="Sentry 21", weapons="Hold"),
        # The one that matters: an Okean hull, red so the story can hang on
        # her, unarmed, hove to. Sinking her is the fatal.
        U("red", "_vanilla", "civ_fv_okean", "datum", name="Factory trawler Nan Hai 24",
          weapons="Hold"),
        U("red", "_vanilla", "wp_agi_okean", "shadow", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-52.25, 139.65, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "longliner",
          name="Longliner Austral Leader", route=[(-52.00, 141.00, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "okean", name="Factory trawler Nan Hai 21",
          route=[(-52.90, 140.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sidetrawler", "side",
          name="Longliner Kerguelen Star", route=[(-51.40, 139.00, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Polar Horizon (expedition cruise)",
          route=[(-52.40, 140.90, 0)], telegraph=3),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic FOXTROT",
          depth="shallow"),
        # The RAAF detachment's field for the season: a civil airport stood
        # in by the game's small airfield. Edinburgh is outside a Poseidon's
        # radius from here.
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Hobart Airport (RAAF detachment)", nation="australia", weapons="Hold"),
    ],
    resolve={"Datum": "victory", "Neutrals": "neutral",
             "Flagship": ("protect", "escort"),
             "Collector": ("classify", "shadow", 1)},
    declares=["SR03CrewRecovered"],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "usn_mh-60r", "usn_p8",
                       "raaf_mq-4c_triton"],
                flights=[HELO, RECON],
                situation="Requisition before Search Datum. The Poseidon and the "
                          "Triton go on sale here: a Poseidon on the Maritime "
                          "Patrol row is the search, and it recovers at Hobart. "
                          "The next window is before Macquarie Passage."),
    role="patrol",
)
