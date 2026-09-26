"""RL06 - The Quiet Side. Fiordland approaches, 19 January 2029.

Deception as discipline. The diesel boat off Fiordland needs her tender,
and the AMS coaster is to meet her among the Milford cruise traffic west of
Puysegur under Kiwi 05's morning racetrack. The frigate is the loud one: it
holds a decoy station to the east with everything radiating and must still
be on it at the half hour, and only then does the rendezvous count. The
boat must not be classified; the tender, a surfaced merchant, is not asked
to be invisible.

Southern Reach's Home Waters (22 January) finds the tender among the
Milford cruise ships near the holding position used here, with TANGO
reported south-west of the task group, and its 27 January signal is still
reasoning about a rendezvous - so on the 19th the boat passes unclassified.
Kiwi 05 is Squadron Leader Rewi's aircraft through Southern Reach; the
player cannot touch it and keep the result.

The tender's nearest escort is the boat, which the closure gate counts as
an armed escort at a dived speed, so the frigate's decoy station is where
the story puts it: 37 miles east-south-east of the tender, towards the cray
grounds under the north-east end of the racetrack, not the 32 frame-miles
the gate allowed when only a surface ship counted.
"""
from campaign_data import U, F, S
from .tables import HELO, SOUTH_HULLS

MISSION = dict(
    code="RL06", series="Red Line", seq="RED LINE  ·  MISSION 6",
    group="core", num="06", key="The Quiet Side", place="Fiordland approaches",
    intro=(
        "Your screen is the loud one. The tender and the boat are the quiet ones."
    ),
    sender="Fleet headquarters, southern tasking",
    intent=((
        "The boat off Fiordland has a week of patrol left in her and none of it is worth "
        "anything without her tender. The screen draws the patrol's eye and keeps it; the "
        "tender and the boat meet where the aircraft is not looking. Answer nothing on the "
        "radio. Illuminate nothing. Kiwi 05 is New Zealand's, and nothing the group does "
        "this morning gives Wellington a reason to say otherwise."
    )),
    date=(2029, 1, 19), time=(5, 20), sea=5, clouds="Broken_3", wind="SW",
    difficulty=4, minutes=80, centre=(-46.3, 166.0),
    blue_nation="China", red_nation="NewZealand",
    geography="coast",
    brief=(
        (
            "FIORDLAND APPROACHES, 0520. The group is in the Tasman. HULL 334, the diesel boat"
            " working the New Zealand side, needs her tender, and MV AUSTRAL COMPLIANCE, the "
            "AMS coaster, is to meet her this morning in the Milford cruise traffic west of "
            "Puysegur.\\n\\nKIWI 05, a New Zealand Poseidon out of Invercargill, flies a "
            "racetrack over this approach every morning. Your screen is the loud one: take the"
            " decoy station on the cray grounds to the east, radiate every search set it has, "
            "and still be on station at the half hour. Only then does the tender's arrival "
            "count.\\n\\nThe tender and the boat go to the holding position quietly, some thirty "
            "miles west of the decoy station. If the aircraft puts a class on HULL 334, the "
            "rendezvous"
            " is known and the operation has failed. Answer nothing on the radio. Illuminate "
            "nothing: no fire-control radar goes near the aircraft.\\n\\nA cruise ship bound for"
            " Milford, a Bluff cray boat and an Otago longliner are in the approach."
        )),
    forces=(
        "Your screen with its flight, holding the decoy station. Allocated: MV Austral "
        "Compliance, the AMS tender, and Hull 334, a Type 039C, dived. Watching: Kiwi 05, an "
        "RNZAF P-8A out of Invercargill. Neutral: a cruise ship, a cray boat and a longliner."
    ),
    objectives=[
        ("Rendezvous", "Hold the decoy station at the half hour, then bring the tender and "
                       "Hull 334 to the holding position", "35,-35,Fail,Main"),
        ("Unseen", "Keep Hull 334 off their plot: do not let the patrol classify her",
         "25,-40,Complete"),
        ("Restraint", "Answer nothing: fire on nothing", "15,-40,Complete"),
        ("Frigate", "Bring the screen off the decoy station intact", "10,-20,Complete"),
        ("Traffic", "Harm no cruise ship or fishing boat", "0,-30,Complete"),
    ],
    # The tender AND the boat at the holding position, and only once the
    # frigate has been on the decoy station at minute 30 - the service-window
    # shape (Southern Watch's SW09) on a unit that starts inside the area.
    victory=dict(kind="arrive", station="tender", at=(-46.38, 165.45), radius=6,
                 min_units=1, objective="Rendezvous",
                 also=[dict(units=["boat"], min_units=1)],
                 after=dict(kind="area", units="decoy", at=(-46.32, 166.15), radius=8,
                            min_units=1, after_minutes=30,
                            intel=(
                                "DECOY REPORT: The screen has held the decoy station for "
                                "thirty minutes with the patrol on its racetrack. The "
                                "rendezvous is cleared to proceed."
                            ))),
    fatal=[F("Unseen", kind="unseen"), F("Restraint", ["red_air"])],
    neutral_objective="Traffic",
    win=(
        "The tender and HULL 334 are at the holding position, and the patrol has a warship on "
        "its plot and nothing under it. The boat will have what she needs by nightfall."
    ),
    lose=(
        "HULL 334 is on the New Zealanders' plot, or their aircraft is down. The rendezvous "
        "is known either way, and the boat goes without."
    ),
    timeout="0640, and the tender is short of the holding position. The patrol will be "
            "back over the approach at first light tomorrow, and so will the decoy.",
    stations={
        # West of Puysegur: the decoy station 22 NM off the coast towards the
        # cray grounds, under the north-east end of Kiwi 05's racetrack; the
        # tender and the boat 37 NM further west among the Milford traffic,
        # the holding position south of them. The racetrack runs across both.
        "decoy": S(-46.32, 166.15, "Decoy station", heading=200),
        "flight": S(-46.30, 166.13, "Ship's flight", heading=200, alt=500),
        "tender": S(-46.15, 165.30, "Austral Compliance", heading=170),
        "boat": S(-46.22, 165.48, "Hull 334", heading=190),
        "red_air": S(-46.00, 166.20, "Kiwi 05", heading=220, alt=12000),
        "cruise": S(-45.90, 166.00, "Milford-bound", heading=20),
        "cray": S(-46.25, 166.40, "Cray boat", heading=120),
        "longliner": S(-46.50, 165.80, "Longliner", heading=250),
    },
    units=[
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "decoy", variant="Variant4",
          weapons="Hold"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        # AMS charters under a flag of convenience; the hull's own file flies
        # a Soviet flag. She and the boat start with their radars off: the
        # screen is the one that radiates.
        U("blue", "_vanilla", "civ_ms_kommunist", "tender",
          name="MV Austral Compliance (AMS tender)", nation="Panama", weapons="Hold",
          radars="False", route=[(-46.38, 165.45, 0)], telegraph=3),
        # The holding position is ten miles south. The route is flown at
        # cruise; slower is quieter, and the choice is the player's.
        U("blue", "plan-submarines", "plan_ss_type_039c", "boat", name="Hull 334",
          depth="belowlayer", weapons="Hold", radars="False",
          route=[(-46.38, 165.47, "belowlayer")], telegraph=3),
        # Rewi's Poseidon, out of Invercargill, on her racetrack until the
        # clock runs out; without the loop she flew it for twenty-odd minutes
        # and circled its north-east end, 39 NM from the rendezvous, before
        # the rendezvous could count. The field is not placed: a red
        # aircraft with no field flies on the engine's unlimited fuel, and an
        # enemy airfield on the chart reads as a target the orders forbid.
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron6", name="Kiwi 05",
          loadout="ASW", weapons="Hold",
          route=[(-46.50, 165.60, 12000), (-46.00, 166.20, 12000)], loop=True,
          telegraph=3),
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Southern Explorer (Milford cruise)", route=[(-45.30, 166.30, 0)],
          telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "cray",
          name="Cray boat Tawaki (Bluff)", route=[(-46.40, 166.70, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "longliner",
          name="Longliner Otago Venture", route=[(-46.70, 165.00, 0)], telegraph=2),
    ],
    resolve={"Rendezvous": "victory", "Traffic": "neutral",
             "Unseen": ("unseen", "boat"),
             "Restraint": ("spare", "red_air"),
             "Frigate": ("protect", "decoy")},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True, allow=list(SOUTH_HULLS),
                flights=[HELO],
                situation=(
                    "The protection group's screen is at sea in the Tasman. A frigate or a "
                    "corvette can be allocated for the decoy station; the tender and Hull 334"
                    " are allocated to this operation."
                )),
    role="patrol",
)
