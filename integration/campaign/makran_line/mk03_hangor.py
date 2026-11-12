"""MK03 - Hangor. South of Gwadar, 6 November 2028.

A detached submarine operation, the way Red Line's Under the Convergence
is: an authored boat, no force allocation, nothing the player owns sails.
PNS Hangor, the first of the Navy's Hangor-class boats (the Pakistani
Pack's S-26P), trails the Meridian merchant that fuels and arms the
trawlers to her next rendezvous. She classifies the mothership on passive
sonar and takes station on the rendezvous, unseen and firing nothing.

Classifying her writes MK03MotherNamed, and Port Qasim reads it as a datum
on her for fifteen minutes: the shape of Red Line's Datum -> Routes They
Can See. The roster sells no submarine; this boat is placed here only.
"""
from campaign_data import U, F, S

MISSION = dict(
    code="MK03", series="Makran Line", seq="MAKRAN LINE  ·  MISSION 3",
    group="core", num="03", key="Hangor", place="South of Gwadar",
    intro=(
        "Detached submarine operation. Trail Meridian's mothership to her rendezvous and "
        "classify her. Do not be seen. Fire on nothing."
    ),
    special=(
        "No force allocation: this is a detached submarine operation, and the task group's "
        "ships stay at Karachi. You command PNS Hangor for this operation only."
    ),
    sender="Commander Pakistan Fleet, Karachi; submarine operating authority",
    intent=((
        "The trawlers that came for Gwadar were fuelled and armed at sea. Find the ship that "
        "does it and know her: her signature is what the next convoy's escort will hunt by. "
        "Hangor is a trail, not an attack. She is not seen, and she fires nothing."
    )),
    date=(2028, 11, 6), time=(1, 30), sea=3, clouds="Overcast", wind="NE",
    difficulty=3, minutes=75, centre=(24.28, 62.20),
    blue_nation="Pakistan", red_nation="Meridian",
    geography="coast",
    brief=(
        (
            "SOUTH OF GWADAR, 0130. MV MERIDIAN SENTINEL, the merchant fleet intelligence "
            "believes fuels and arms Meridian's trawlers, is steaming east fifty miles south "
            "of the coast without lights. Two of the trawlers are waiting for her somewhere "
            "ahead.\\n\\n"
            "PNS HANGOR is dived across her track. Classify SENTINEL on passive sonar, then "
            "take the boat within three miles of the trail datum marked east of you, on her "
            "rendezvous. The trail is complete when SENTINEL has been classified and HANGOR "
            "is inside that circle afterwards. If any Meridian ship classifies HANGOR, the "
            "trail is blown and the operation has failed. Nothing is fired: the boat starts "
            "at weapons Hold, and a torpedo on any ship here ends the operation.\\n\\n"
            "Dhows and a tanker bound for the Gulf are in the sonar picture. Use them."
        )),
    forces=(
        "PNS Hangor (S-131), an S-26P, dived. Opposing: MV Meridian Sentinel, an armed "
        "merchant, and two armed trawlers at her rendezvous. Neutral: fishing dhows and a "
        "tanker."
    ),
    objectives=[
        ("Trail", "Classify Meridian Sentinel, then take Hangor within three miles of the "
                  "trail datum", "40,-40,Fail,Main"),
        ("Unseen", "Keep Hangor off Meridian's plot: no Meridian ship may classify her",
         "25,-40,Complete"),
        ("Restraint", "Fire on nothing", "15,-40,Complete"),
        ("Boat", "Bring Hangor through intact", "10,-30,Complete"),
        ("Traffic", "Harm no dhow or tanker", "0,-30,Complete"),
    ],
    # Nothing counts until the mothership has a class - that is the
    # operation - and the class is what Port Qasim reads (MK03MotherNamed,
    # set by the stage). Then the boat on the rendezvous.
    victory=dict(kind="arrive", station="boat", at=(24.30, 62.36), radius=3,
                 min_units=1, objective="Trail",
                 after=dict(kind="classify", units="mother", min_units=1,
                            sets="MK03MotherNamed",
                            intel=(
                                "SONAR / HANGOR: Contact classified: MV MERIDIAN SENTINEL, "
                                "single screw, heavy, a generator forward that a merchant "
                                "does not need. Her signature is logged for the Port Qasim "
                                "escort. Take the boat on to the trail datum."
                            ))),
    fatal=[F("Unseen", kind="unseen"), F("Restraint", ["mother", "raiders"]), F("Boat")],
    neutral_objective="Traffic",
    win=(
        "HANGOR is on SENTINEL's rendezvous with her signature on tape, and nobody on the "
        "Meridian ships knows a submarine was there. The Port Qasim escort will know her when "
        "it hears her."
    ),
    lose=(
        "HANGOR has been seen, or has fired, or is lost. Meridian knows the Navy has a boat on "
        "its mothership, and SENTINEL will not come this way again."
    ),
    timeout="{deadline_clock}, and the trail is not complete. SENTINEL is past the rendezvous "
            "and HANGOR has lost her in the morning traffic.",
    stations={
        # Fifty miles south of the coast: the boat south of the merchant's
        # track, the trawlers on the rendezvous six miles east of the datum.
        "boat": S(24.24, 62.22, "Hangor", heading=80),
        "mother": S(24.30, 62.05, "Meridian Sentinel", heading=85),
        "raiders": S(24.33, 62.46, "Trawlers at the rendezvous", heading=260),
        "dhows": S(24.20, 62.40, "Fishing dhows", heading=300),
        "tanker": S(24.15, 62.00, "Tanker for the Gulf", heading=280),
    },
    units=[
        U("blue", "pakistani-pack", "pns_ss_s-26p", "boat", variant="Variant1",
          name="PNS Hangor (S-131)", depth="belowlayer", weapons="Hold", radars="False"),
        U("red", "armed-merchantmen", "civ_ms_act_1_armed", "mother",
          name="MV Meridian Sentinel", nation="Meridian", weapons="Hold",
          route=[(24.31, 62.20, 0), (24.33, 62.44, 0)], telegraph=2),
        U("red", "armed-merchantmen", "civ_fv_okean_armed", "raiders", variant="Variant4",
          name="Meridian Escort 41", nation="Meridian", weapons="Hold"),
        U("red", "armed-merchantmen", "civ_fv_sidetrawler_armed", "raiders",
          name="Meridian Escort 42", nation="Meridian", weapons="Hold"),
        U("neutral", "_vanilla", "civ_fv_dhow", "dhows", name="Dhow Gwadar Moon",
          nation="Pakistan", route=[(24.30, 62.10, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_dhow", "dhows", name="Dhow Al-Habib",
          nation="Pakistan", route=[(24.10, 62.30, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_ritina", "tanker",
          name="MT Gulf Horizon (Karachi for Fujairah)", nation="Liberia",
          route=[(24.40, 60.50, 0)], telegraph=3),
    ],
    resolve={"Trail": "victory", "Traffic": "neutral",
             "Unseen": ("unseen", "boat"),
             "Restraint": ("spare", "mother", "raiders"),
             "Boat": ("protect", "boat")},
    declares=["MK03MotherNamed"],
    window=dict(),
    role="patrol",
)
