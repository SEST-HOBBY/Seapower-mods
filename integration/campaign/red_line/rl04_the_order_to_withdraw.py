"""RL04 - The Order to Withdraw. Banda Sea, 27 November 2028.

The first hours of the ceasefire. It took effect at 0000 on the 27th; the
group acknowledged its withdrawal order at 2304 the night before and is
carrying it out. The one ship that wants the war back is in the group's own
company: a Meridian armed coaster that has turned south for the Arafura
lane, where the coalition's first convoy sails for The First Ship Through
on the 28th. Stop her before she clears the screen, take the carrier across
the line, and touch nothing else: not the coalition's aircraft, and not the
boat that may be astern, whose nobody has said.

Southern Watch's 27 November report says not every Chinese group had
acknowledged the ceasefire; this one had. Its closing page has two groups
two hundred miles behind the convoy, one complying and one deciding, and
The First Ship Through places them in its Arafura box: a Luda and a Type 071
withdrawing (the northern element's kind of ship, which the tasking says is
not this commander's) and an unacknowledged 054A. This group is neither of
them and goes nowhere near that box; it withdraws north-west from the Banda
Sea, 370 NM from it. Fujian is not placed: Fujian's Shadow may have sunk
her, so the carrier is Liaoning, whom Southern Reach keeps afloat until
February.

The coaster is ran_ms_super_p, Role=Spy, at weapons Hold: a passive red
unit may start in company, inside the escort role's standoff. The win
requires her destroyed (an also-term of kind "destroyed"), and a denied race
ends the mission if she reaches the edge of the screen first.
"""
from campaign_data import U, F, S
from .tables import HELO

MISSION = dict(
    code="RL04", series="Red Line", seq="RED LINE  ·  MISSION 4",
    group="core", num="04", key="The Order to Withdraw", place="Banda Sea",
    intro=(
        "Ceasefire plus three hours. Take the group north-west, and stop the ship in company "
        "that wants the war back."
    ),
    sender="Fleet headquarters",
    intent=((
        "The ceasefire is the group's order now, and it binds the group, not Meridian. "
        "Withdraw as ordered. The coaster does not reach the lane, whatever it takes to stop "
        "her. The aircraft overhead is the coalition's, and nobody has said whose the boat "
        "astern is. Under a ceasefire neither is a target."
    )),
    date=(2028, 11, 27), time=(3, 10), sea=2, clouds="Clear", wind="E",
    difficulty=4, minutes=80, centre=(-4.6, 128.9),
    blue_nation="China", red_nation="Australia",
    brief=(
        (
            "BANDA SEA, 0310, 27 NOVEMBER. The ceasefire took effect at 0000. The group "
            "acknowledged the order to withdraw at 2304 last night and is carrying it out: "
            "LIAONING, the replenishment ship and HAI YANG 7, chartered, north-west for the "
            "Manipa approaches with what the twenty-third left, and your frigate on the "
            "starboard quarter. Not every group in the corridor has acknowledged. This one has, "
            "and the coalition is watching to see which is which.\\n\\nMV MERIDIAN HARMONY is "
            "not withdrawing. She is one"
            " of Meridian's armed coasters; she joined the group on the twenty-fourth asking "
            "for protection, and headquarters let her keep company. At 0240 she turned south "
            "for the Arafura lane, where the coalition's first convoy sails at first light "
            "tomorrow. She has "
            "been told to stop, twice, on the group's net and on channel 16, and has not "
            "answered. Meridian is not a party to the ceasefire. If she reaches that lane, "
            "whatever she does there she will have done from this group's company.\\n\\nA "
            "coalition Poseidon is overhead, recording the withdrawal, and a submarine may be "
            "astern. Neither is to be touched. Your frigate and its flight start at "
            "weapons Hold: engage the coaster by direct order, because a ship left free may "
            "find the Poseidon on its own. Stop her before she clears the screen, then take "
            "LIAONING and the replenishment ship across the line north-west.\\n\\nA Banda "
            "fishing boat and the Banda Neira ferry are on the water."
        )),
    forces=(
        "Your screen, with its flight. Allocated: Liaoning, the replenishment ship and MT Hai"
        " Yang 7. In company and turning away: MV Meridian Harmony, armed. Watching: a "
        "coalition P-8A, and possibly a submarine astern. Neutral: a fishing boat and a ferry."
    ),
    objectives=[
        ("Withdrawal", "Take Liaoning and the replenishment ship north-west across the line",
         "35,-35,Fail,Main"),
        ("Spoiler", "Stop Meridian Harmony before she clears the screen", "20,-40,Fail"),
        ("Restraint", "Fire on nothing but Meridian Harmony", "15,-40,Complete"),
        ("Carrier", "Bring Liaoning through intact", "10,-30,Complete"),
        ("Traffic", "Harm no fishing boat or ferry", "0,-30,Complete"),
    ],
    # Both hulls across the line, 21 NM up the withdrawal course, at a
    # replenishment ship's speed - AND the coaster gone. The win cannot come
    # while she is still running for the lane. The box is authored so that
    # the group's route ends inside it: the hulls wait there for the kill
    # instead of sailing on out of it.
    victory=dict(kind="arrive", units=["group#1", "group#2"], at=(-4.32, 128.40),
                 radius=12, min_units=2, objective="Withdrawal", transit=12,
                 also=[dict(kind="destroyed", units=["spoiler"], min_units=1)]),
    # The race, lost: the coaster at the edge of the screen, 15 NM down her
    # track, where the frigate cannot follow her and keep the withdrawal.
    denied=[dict(units=["spoiler"], at=(-4.84, 128.92), radius=4, objective="Spoiler",
                 message=(
                     "MERIDIAN HARMONY has cleared the screen and is running south for the "
                     "lane at full speed. The group cannot follow her and keep its withdrawal "
                     "order. Whatever she does tomorrow, she sailed from this group's company."
                 ))],
    fatal=[F("Restraint", ["red_air", "red_sub"]), F("Carrier")],
    neutral_objective="Traffic",
    win=(
        "LIAONING and the replenishment ship are north-west of the line, and MERIDIAN HARMONY "
        "is stopped short of the lane. The ship's flight is searching for her crew. The "
        "group's report will say what was done and why; the Poseidon has the same account."
    ),
    lose=(
        "The withdrawal has become an incident: LIAONING is lost, or the Poseidon or the boat "
        "astern is down. The ceasefire is hours old, and the group is in its first violation "
        "report."
    ),
    timeout="0430, and the group is still south of the line. The withdrawal order had a "
            "time on it, and the coalition's aircraft has recorded the group missing it.",
    stations={
        # The group on its withdrawal course, 300, for the Manipa approaches;
        # the frigate on the carrier's starboard quarter, 9 NM east-north-east
        # of her and north-east of the coaster; the coaster five miles astern of
        # the carrier, in company, with her route turned south-south-east.
        "escort": S(-4.45, 128.85, "Escort", heading=300),
        "flight": S(-4.47, 128.83, "Ship's flight", heading=300, alt=500),
        "group": S(-4.50, 128.70, "Liaoning", heading=300),
        "charter": S(-4.40, 128.60, "Hai Yang 7", heading=300),
        "spoiler": S(-4.56, 128.76, "Meridian Harmony", heading=150),
        "red_air": S(-4.00, 129.40, "Patrol aircraft", heading=240, alt=14000),
        "red_sub": S(-4.90, 128.60, "Contact GOLF", heading=330),
        "fishing": S(-4.30, 129.10, "Banda fishing boat", heading=180),
        "ferry": S(-4.75, 129.40, "Banda Neira ferry", heading=250),
    },
    units=[
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "escort", variant="Variant1",
          weapons="Hold"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        # Liaoning first: the Carrier objective and the win name group#1.
        U("blue", "liaoning-type-001", "plan_type_001", "group", name="Liaoning",
          weapons="Hold", route=[(-4.31, 128.38, 0)], telegraph=3),
        U("blue", "_vanilla", "plan_ap_qiongsha", "group", name="Replenishment ship",
          weapons="Hold", route=[(-4.34, 128.41, 0)], telegraph=3),
        U("blue", "_vanilla", "civ_ms_ritina", "charter", name="MT Hai Yang 7 (chartered)",
          weapons="Hold", route=[(-4.26, 128.33, 0)], telegraph=3),
        # A flag of convenience: Meridian's coasters are nobody's navy. Hold,
        # and her role is Spy - she will not open the fight, she will run.
        U("red", "auxilliary-merchant-pack", "ran_ms_super_p", "spoiler",
          name="MV Meridian Harmony", nation="Panama", weapons="Hold",
          route=[(-4.84, 128.92, 0), (-5.40, 129.25, 0)], telegraph=4),
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3",
          loadout="ASW", weapons="Hold",
          route=[(-4.80, 128.40, 14000), (-4.00, 129.40, 14000), (-4.80, 128.40, 14000)],
          telegraph=3),
        # The boat from the Biak approaches, astern and listening - unless
        # Routes They Can See put her on the bottom.
        U("red", "us-navy-2027", "usn_ssn_virginia_2027", "red_sub", name="Contact GOLF",
          depth="belowlayer", weapons="Hold", spawn_if=("RL02GolfSunk", "IsFalse"),
          route=[(-4.40, 128.30, "belowlayer")], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Banda fishing boat Lautaka", route=[(-4.60, 129.20, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_roro_c", "ferry",
          name="KM Banda Neira (Ambon-Banda ferry)", route=[(-3.90, 128.20, 0)],
          telegraph=3),
    ],
    resolve={"Withdrawal": "victory", "Traffic": "neutral",
             "Spoiler": ("destroy", "spoiler", 1),
             "Restraint": ("spare", "red_air", "red_sub"),
             "Carrier": ("protect", "group#1")},
    declares=[],
    # Repair only. What the twenty-third spent stays spent: there is no
    # rearm and no purchase between the ceasefire and the withdrawal.
    window=dict(buy=False, repair=True, rearm=False, flights=[HELO],
                situation=(
                    "The ceasefire allows repairs alongside the replenishment ship and "
                    "nothing else. There is no rearming and no reinforcement before the "
                    "withdrawal."
                )),
    role="escort",
)
