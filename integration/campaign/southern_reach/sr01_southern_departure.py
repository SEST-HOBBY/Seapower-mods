"""SR01 - Southern Departure. Storm Bay, 6 December 2028.

Escort, classification and rules of engagement. The Antarctic resupply
convoy clears Storm Bay past a fishing fleet that is not all fishing, with a
frigate sixty miles south-east that has been asking merchant masters for
paperwork. No combat is required to win, and a shot at the wrong trawler
ends the operation.
"""
from campaign_data import U, F, S, HELO

MISSION = dict(
    code="SR01", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 1",
    group="core", num="01", key="Southern Departure", place="Storm Bay, Tasmania",
    intro=(
        "Escort the Antarctic resupply convoy out of Storm Bay. Identify the suspected "
        "intelligence collector among the fishing vessels while keeping the civilian traffic "
        "safe."
    ),
    sender="Commodore Alex Mercer, Maritime Border Command, Hobart detachment",
    intent=((
        "Three ships out of Storm Bay and into the open Southern Ocean, SOUTHERN ENDEAVOUR "
        "among them: she carries Casey's personnel and essential stores. Something in that "
        "fishing fleet has been logging our departures since October: classify it, and it is a "
        "name on a chart instead of a rumour. The frigate to the south-east will ask you "
        "questions on channel 16. Answer them. Your weapons are tight, and a dead trawler ends "
        "the resupply season on its first morning."
    )),
    date=(2028, 12, 6), time=(6, 20), sea=4, clouds="Broken_2", wind="W",
    difficulty=1, minutes=60, centre=(-43.4, 147.9),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "STORM BAY, 0620. The first resupply convoy of the season cleared the Derwent an "
            "hour ago: RSV SOUTHERN ENDEAVOUR with Casey's people and stores, MV CORAL PIONEER "
            "chartered for the Macquarie Island run, and the fuel coaster DERWENT SPIRIT. They "
            "make twelve knots together and they will not make more.\\n\\nA factory-trawler fleet"
            " has been working the shelf edge since October under the Southern Ocean Fisheries "
            "and Research Protection Group's flag, and one hull in it carries an electronics "
            "fit no trawler needs. It has been forty miles off the Derwent every time a ship "
            "has sailed for the ice. This morning it is closer. Sixty miles south-east, a "
            "frigate flying the same flag has been calling merchant masters to ask for their "
            "environmental compliance paperwork. It has not been told to stop.\\n\\nYou are the "
            "escort, with your Seahawk if one is embarked. BLUEFIN 31 is a Poseidon out of "
            "Edinburgh for the first half of the morning and SENTRY 21 is a Triton high to the "
            "south. Walk the convoy south out of the bay to the handover line and classify the "
            "trawler that is not one. An expedition cruise ship, two Tasmanian fishing boats "
            "and the morning airlink to Wilkins Aerodrome are in the same water and the same "
            "sky. Identify before you shoot. Your weapons are tight.\\n\\nINTELLIGENCE: Hobart is"
            " comparing satellite radar detections with AIS and port departure reports. Nan Hai"
            " 27 is the suspected collector, but distinguish the trawlers locally. Bluefin 31 "
            "and Sentry 21 support the current search. Missing AIS or an unusual antenna fit "
            "calls for investigation under the existing engagement orders."
        )),
    forces=(
        "Your escort group, one MH-60R if assigned, one P-8A on task, one MQ-4C Triton "
        "overhead. Three convoy hulls to walk out. Neutral: an expedition cruise ship, two "
        "Tasmanian fishing boats, two factory trawlers, the Wilkins airlink. One research "
        "trawler with an intelligence fit, one frigate to the south-east."
    ),
    objectives=[
        ("Convoy", "Walk the convoy south out of Storm Bay to the handover line",
         "30,-30,Fail,Main"),
        ("Neutrals", "Harm no fishing boat, merchant or aircraft", "0,-40,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
        ("Identify", "Classify the research trawler before the handover", "15,0,None"),
    ],
    # All three: the win needs every hull, so losing any of them ends the
    # mission rather than leaving the player to run out a clock they can no
    # longer win. SOUTHERN ENDEAVOUR is the one the defeat text mourns by
    # name, because she is the season.
    victory=dict(kind="arrive", station="convoy", min_units=3, objective="Convoy",
                 transit=12, also=[dict(units=["convoy#1"], min_units=1)]),
    fatal=[F("Convoy", ["convoy"])],
    neutral_objective="Neutrals",
    win=(
        "All three resupply ships have crossed the handover line. Forward any classification "
        "reports to the intelligence cell before the next patrol. Santos, on channel 16: 'Same "
        "escort as October. Good.'"
    ),
    lose="SOUTHERN ENDEAVOUR is not going south this week, and the stations "
         "start the season on what the winter left them.",
    timeout="0720 and the convoy is still in the bay. The frigate has its "
            "paperwork question answered: nothing sailed.",
    stations={
        # Storm Bay: the Derwent's mouth is 6 NM north of the escort, Bruny
        # Island 12 NM west, the Tasman Peninsula 8 NM east. The convoy sails
        # south (170) out of the bay; the handover line is solved on that
        # bearing, on water, by the builder.
        "escort": S(-43.12, 147.62, "Escort", heading=170),
        "convoy": S(-43.06, 147.56, "Resupply convoy", heading=170),
        "flight": S(-43.13, 147.60, "Ship's flight", heading=170, alt=500),
        "mpa": S(-43.55, 147.95, "Bluefin 31", heading=350, alt=15000),
        "high": S(-43.85, 147.50, "Sentry 21", heading=90, alt=50000),
        "cruise": S(-43.24, 147.52, "Expedition cruise ship", heading=160),
        "fishing": S(-43.22, 147.66, "Tasmanian fishing", heading=60),
        "airlink": S(-43.02, 147.70, "Wilkins airlink", heading=210, alt=30000),
        # The factory trawlers work the shelf edge with the intelligence hull
        # among them: 16 NM off the convoy's bow, closing, and the player has
        # to tell three Okean hulls apart by what they do.
        "trawlers": S(-43.36, 147.52, "Factory trawlers", heading=20),
        "shadow": S(-43.30, 147.75, "Research trawler", heading=340),
        # The frigate 55 NM south-east, routed onto the convoy's track: it
        # will be at the handover line about when the convoy is.
        "patrol": S(-43.90, 148.60, "Fisheries protection frigate", heading=320),
        "home": S(-34.703, 138.622, "RAAF Base Edinburgh"),
        "airport": S(-42.836, 147.510, "Hobart Airport"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant6",
          weapons="Tight"),
        # Air-tasking placeholder: the cockpit a purchased Seahawk takes. No
        # name, no objective - slot-tagged aircraft keep the player's own.
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3",
          name="Bluefin 31", alt=15000, weapons="Tight"),
        U("blue", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "high",
          name="Sentry 21", weapons="Hold"),
        # A modern freighter stands in for the research and resupply ship:
        # no icebreaker exists in the collection, and the briefing says so
        # in her name.
        U("blue", "re-power-resupply", "civ_ms_freighter_d", "convoy",
          name="RSV Southern Endeavour"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "SEST_Replenishment", "civ_ms_sealift_pacific", "convoy",
          name="MT Derwent Spirit"),
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Polar Horizon (expedition cruise)",
          route=[(-43.55, 147.45, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_b", "fishing",
          name="Tasmanian trawler", route=[(-43.20, 147.60, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_crabboat", "fishing",
          name="Storm Bay cray boat", route=[(-43.28, 147.62, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "trawlers",
          name="Factory trawler Nan Hai 21", route=[(-43.30, 147.60, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "trawlers",
          name="Factory trawler Nan Hai 24", route=[(-43.28, 147.66, 0)], telegraph=2),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airlink",
          name="Wilkins airlink 07", airway=(-66.69, 111.52)),  # Wilkins runway
        # The one that is not fishing: an Okean-class intelligence collector
        # among Okean-class trawlers, closing on the convoy's bow. Unarmed;
        # classification is the whole task.
        U("red", "_vanilla", "wp_agi_okean", "shadow", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-43.15, 147.62, 0), (-43.35, 147.70, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "patrol",
          name="Fisheries protection frigate", weapons="Tight",
          route=[(-43.45, 147.72, 0)], telegraph=3),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_edinburgh", "home",
          name="RAAF Base Edinburgh", nation="australia", weapons="Hold"),
        U("neutral", "_vanilla", "airfield_small_1", "airport",
          name="Hobart Airport", weapons="Hold"),
    ],
    resolve={"Convoy": "victory", "Neutrals": "neutral",
             "Flagship": ("protect", "escort"),
             "Identify": ("classify", "shadow", 1, "SR01ShadowNamed")},
    declares=["SR01ShadowNamed"],
    window=dict(buy=True, repair=True, rearm=True, allow=["ran_ffh_anzac", "ran_ddg_hobart", "usn_mh-60r"],
                flights=[HELO],
                situation=(
                    "Sydney and Hobart have released the first southern force allocation. "
                    "Select your escort and assign an embarked MH-60R to Ship's Flight if "
                    "required. Bluefin 31 and Sentry 21 are supporting allocations for this "
                    "operation. Further force allocation is available before Search Datum."
                )),
    role="opening",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 170, 12
