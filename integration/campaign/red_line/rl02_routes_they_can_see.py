"""RL02 - Routes They Can See. Biak approaches, 12 November 2028.

An escort in the dark. The enclave field's jet fuel goes into Biak's
northern roads the night before the coalition's relief window opens (The
Open Door, 0450 on the 13th), with a submarine nobody has claimed on the
route and a Poseidon over it that must not be touched.

The coalition's intelligence summary of 12 November says the Russian
detachment's supply routes into the enclave show up in imagery, patrol
reports and intercepted logistics traffic. The Chinese detachment on the
same field is supplied the same way, and this is its fuel run, seen from
the tanker's escort. The boat is
the one that torpedoed the Russian detachment's auxiliary two nights before
(Return Passage: "a torpedo forward eleven days ago" on the 21st). Nobody
in either campaign says whose she is, and no text here does either: she is
GOLF, and a classification shows her class, which is as far as the group
gets. The player may classify her, and may sink her, which sets
RL02GolfSunk and keeps her out of The Order to Withdraw.
"""
from campaign_data import U, F, S
from .tables import HELO, RECON, NORTH_HULLS, NORTH_AIR

MISSION = dict(
    code="RL02", series="Red Line", seq="RED LINE  ·  MISSION 2",
    group="core", num="02", key="Routes They Can See", place="Biak approaches",
    intro=(
        "Take the enclave field's jet fuel into Biak's northern roads tonight, ahead of the "
        "coalition's relief window. A submarine is on the route; a patrol aircraft is over it."
    ),
    sender="Fleet headquarters",
    intent=((
        "The detachment on the enclave field flies on fuel that comes by sea, and it is down to"
        " two days. Hai Yang 7 goes in tonight by the northern roads, away from the southern "
        "approach the coalition's relief aircraft will be over. Defend her against anything that "
        "attacks her. The patrol aircraft attacks nothing: it records. Shooting it down is "
        "the incident Beijing does not want this week."
    )),
    date=(2028, 11, 12), time=(23, 10), sea=2, clouds="Broken_2", wind="NW",
    difficulty=3, minutes=95, centre=(-0.5, 135.8),
    blue_nation="China", red_nation="Australia",
    brief=(
        (
            "BIAK APPROACHES, 2310. The detachment on the enclave field flies on fuel that "
            "comes by sea, and it is down to two days. MT HAI YANG 7, chartered, is in company "
            "with a full load of aviation fuel. Before dawn the coalition's relief window opens "
            "over the enclave and its aircraft will be over the southern approach. A tanker "
            "there at first light is a target and an incident, so she goes into the northern "
            "roads tonight.\\n\\nTwo nights ago a submarine put a torpedo into the Russian "
            "detachment's auxiliary in the approaches. Nobody has said whose boat it was, or "
            "whether she tells a Russian hull from a chartered one. Assume she does not. She is"
            " designated GOLF.\\n\\nA RAAF Poseidon has been over the route since dusk. It is "
            "recording, not attacking. Leave it alone.\\n\\nYour frigate and its flight, a Y-9 "
            "out of the enclave field if one is allocated, and HAI YANG 7 at twelve knots. "
            "Numfor's fishing boats and a coaster bound east for Jayapura are on the same "
            "water."
        )),
    forces=(
        "Your screen, a Z-9C if embarked and a Y-9 if allocated. Allocated: MT Hai Yang 7, "
        "chartered, and the enclave field. Opposing: one submarine, GOLF. Watching: a RAAF "
        "P-8A. Neutral: two Numfor fishing boats and a coaster."
    ),
    objectives=[
        ("Fuel", "Bring Hai Yang 7 into Biak's northern roads", "40,-40,Fail,Main"),
        ("Tanker", "Keep Hai Yang 7 afloat", "0,-40,Complete"),
        ("Restraint", "Do not fire on the patrol aircraft", "10,-40,Complete"),
        ("Boat", "Classify the submarine on the route", "15,0,None"),
        ("Traffic", "Harm no fishing boat or coaster", "0,-30,Complete"),
    ],
    # The northern roads, authored: Biak's south harbour approach has no
    # proven water within 42 NM, which is also the story's reason for the
    # north. Twelve knots, laden.
    victory=dict(kind="arrive", station="tanker", at=(-0.62, 136.00), radius=6,
                 transit=12, min_units=1, objective="Fuel"),
    fatal=[F("Tanker"), F("Restraint", ["red_air"])],
    neutral_objective="Traffic",
    # GOLF sunk is allowed - she is an unclaimed boat no coalition mission
    # tracks - and remembered: The Order to Withdraw reads it.
    flags=[dict(name="RL02GolfSunk", units=["red_sub"],
                intel=(
                    "SONAR REPORT: Contact GOLF destroyed. Log the time, the weapon and what she "
                    "was doing when it was used; the group will be asked."
                ))],
    win=(
        "HAI YANG 7 is in the northern roads and discharging, and the detachment flies "
        "tomorrow. The Poseidon has a night's recording of a frigate escorting a tanker, which "
        "is what it was."
    ),
    lose=(
        "HAI YANG 7 is lost, or the patrol aircraft is down. Either way the enclave's week has "
        "started badly, and the group's name is on it."
    ),
    timeout="0045, and HAI YANG 7 is still outside the roads with no time left to "
            "discharge before the relief window opens. She turns back; the detachment "
            "flies on what it has.",
    stations={
        # Out of the west, north of Supiori and Numfor, for the roads off
        # Biak's north coast: the frigate 13 NM astern of the tanker, GOLF closing
        # from the east across the track, the Poseidon north of it all.
        "escort": S(-0.40, 135.50, "Escort", heading=110),
        "flight": S(-0.42, 135.48, "Ship's flight", heading=110, alt=500),
        "tanker": S(-0.50, 135.70, "Hai Yang 7", heading=110),
        "mpa": S(-0.20, 135.60, "Maritime patrol", heading=110, alt=8000),
        # The enclave field, on the airfield The Open Door strikes the next
        # morning; it snaps to proven land.
        "field": S(-1.10, 136.20, "Enclave field"),
        "red_sub": S(-0.40, 136.10, "Contact GOLF", heading=250),
        "red_air": S(0.00, 136.20, "Patrol aircraft", heading=240, alt=12000),
        "fishing": S(-0.30, 135.45, "Numfor fishing boats", heading=90),
        "coaster": S(-0.30, 136.40, "Coaster", heading=80),
    },
    units=[
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "escort", variant="Variant2",
          weapons="Tight"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Tight",
          loadout="ASWKiller", slot="HeloRecon"),
        U("blue", "_vanilla", "civ_ms_ritina", "tanker", name="MT Hai Yang 7 (chartered)",
          weapons="Hold", route=[(-0.62, 136.00, 0)], telegraph=3),
        # Air-tasking placeholder for a purchased Y-9: no name, no objective.
        U("blue", "modern-plan-systems", "plan_y-9fq", "mpa", alt=8000, weapons="Tight",
          loadout="ASW", slot="Recon"),
        U("blue", "modern-chinese-airbase", "pla_airbase_modern", "field",
          name="Enclave field (PLAAF detachment)", weapons="Hold"),
        # Weapons free and routed across the tanker's track: the threat the
        # escort exists for.
        U("red", "us-navy-2027", "usn_ssn_virginia_2027", "red_sub", name="Contact GOLF",
          depth="belowlayer", weapons="Free",
          route=[(-0.55, 135.85, "belowlayer")], telegraph=2),
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3",
          loadout="ASW", weapons="Hold",
          route=[(-0.45, 135.40, 12000), (0.00, 136.20, 12000), (-0.45, 135.40, 12000)],
          telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Numfor fishing boat Karang", route=[(-0.35, 135.75, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fishing",
          name="Numfor fishing boat Mansinam", route=[(-0.20, 135.30, 0)], telegraph=2),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "coaster",
          name="KM Teluk Jaya (Biak-Jayapura)", route=[(-0.20, 137.30, 0)], telegraph=3),
    ],
    resolve={"Fuel": "victory", "Traffic": "neutral",
             "Tanker": ("protect", "tanker"),
             "Restraint": ("spare", "red_air"),
             "Boat": ("classify", "red_sub", 1)},
    declares=["RL02GolfSunk"],
    window=dict(buy=True, repair=True, rearm=True, allow=NORTH_HULLS + NORTH_AIR,
                flights=[HELO, RECON],
                situation=(
                    "The screen has a week in the approaches behind it. A Y-9 maritime patrol"
                    " aircraft can be allocated from the enclave field's detachment for the "
                    "night's escort. Hai Yang 7 is chartered and allocated to this operation."
                )),
    role="escort",
)
