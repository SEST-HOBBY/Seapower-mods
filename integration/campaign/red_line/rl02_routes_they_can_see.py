"""RL02 — compact final approach, an active torpedo threat and a missile flank.

24 Oct 2026: GOLF uses explicit ten/eighteen-minute torpedo orders instead
of relying on a passive/free AI search. Her identity, Variant10, the loss
flag read by RL04 and Datum's fifteen-minute position record are retained.
The observer is neutral, not a fire-control aircraft for the attackers.
"""
from campaign_data import U, F, S
from .tables import HELO, RECON, NORTH_HULLS, NORTH_AIR

MISSION = dict(
    code="RL02", series="Red Line", seq="RED LINE  ·  MISSION 2",
    group="core", num="02", key="Routes They Can See", place="Biak approaches",
    intro="A shorter final escort into Biak: hunt the torpedo shooter and stop the missile craft while the tanker keeps moving.",
    sender="Fleet headquarters",
    intent="Deliver the fuel. GOLF and the declared hostile missile craft may be engaged; the Australian observer and civil traffic may not. Dipper 23 is allocated so the screen always has an airborne ASW search.",
    date=(2028, 11, 12), time=(23, 10), sea=2, clouds="Broken_2", wind="NW",
    difficulty=3, minutes=55, centre=(-0.5, 135.8),
    blue_nation="China", red_nation="Australia",
    brief=("BIAK APPROACHES, 2310. HAI YANG 7 is already on the final leg into the northern roads, "
           "about eleven miles from the holding point. She makes twelve knots: keep her moving "
           "while the escort clears the approaches. There is no need to sail the earlier open-water leg.\n\n"
           "Contact GOLF is east of the route and closing across it. Expect her first torpedo "
           "attack at about minute ten if she is not stopped, with a second attack window at "
           "eighteen. The allocated Z-18F, DIPPER 23, is already ahead of the tanker; use it for "
           "the search rather than waiting for an optional purchased aircraft. A ship's flight "
           "and a Y-9 can add coverage if allocated.\n\n"
           "A Meridian missile craft has also been identified north of the lane. Its launcher "
           "can reach the tanker and an attack is expected around minute fourteen. It is a "
           "declared hostile, separate from the submarine: screen both bearings. You may engage "
           "either shooter before it fires. GOLF's loss is remembered in the withdrawal mission.\n\n"
           "If Sea Ear 31 completed Datum, its fifteen-minute position record remains available. "
           "It is a datum, not a fresh sonar contact. Classification earns a bonus; protecting "
           "the tanker and delivering her are the task.\n\n"
           "The RAAF Poseidon records the run and is a protected non-belligerent with a neutral "
           "symbol. It is not providing the hostile craft's orders. Numfor's fishing boats and "
           "the coaster are protected too."),
    forces="Your screen, Dipper 23, Hai Yang 7 and the enclave field; a ship's flight and Y-9 if allocated. Hostile: GOLF and one missile craft. Protected: the Australian Poseidon and civil traffic.",
    objectives=[
        ("Fuel", "Bring Hai Yang 7 into Biak's northern roads", "40,-40,Fail,Main"),
        ("Tanker", "Keep Hai Yang 7 afloat", "0,-40,Complete"),
        ("Restraint", "Do not fire on the patrol aircraft", "10,-40,Complete"),
        ("Boat", "Classify the submarine on the route", "15,0,None"),
        ("Raider", "Stop the missile craft on the northern flank", "15,0,None"),
        ("Traffic", "Harm no fishing boat or coaster", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="tanker", at=(-0.62, 136.00), radius=2,
                 transit=12, min_units=1, objective="Fuel",
                 also=[dict(kind="time",after_minutes=20),dict(kind="no_incoming")]),
    fatal=[F("Tanker"), F("Restraint", ["red_air"])],
    neutral_objective="Traffic",
    flags=[dict(name="RL02GolfSunk", units=["red_sub"],
                intel=(
                    "SONAR REPORT: Contact GOLF destroyed. Log the time, the weapon and what she "
                    "was doing when it was used; the group will be asked."
                ))],
    reveal_if=[dict(
        variable="RLO1GolfDatum", units=["red_sub"], level="", time=900,
        intel=(
            "AIR OPERATIONS: Sea Ear 31's buoy recordings of the eleventh, correlated with "
            "tonight's picture, put GOLF here. That position is on your display as a datum "
            "and will age off in fifteen minutes. It is a record, not a contact: find her "
            "with your own sensors."
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
    timeout="{deadline_clock}, and HAI YANG 7 is still outside the roads with no time left to "
            "discharge before the relief window opens. She turns back; the detachment "
            "flies on what it has.",
    stations={
        "escort": S(-0.48,135.915, "Escort", heading=110),
        "flight": S(-0.46,135.90, "Ship's flight", heading=110, alt=500),
        "tanker": S(-0.50,135.86, "Hai Yang 7", heading=110),
        "mpa": S(-0.20, 135.60, "Maritime patrol", heading=110, alt=8000),
        "field": S(-1.10, 136.20, "Enclave field"),
        "raider": S(-0.22, 135.97, "Hostile missile craft", heading=195),
        "asw_support": S(-0.43, 136.03, "Dipper 23", heading=70, alt=500),
        "red_sub": S(-0.38, 136.22, "Contact GOLF", heading=250),
        "red_air": S(0.00, 136.20, "Patrol aircraft", heading=240, alt=12000),
        "fishing": S(-0.30, 135.45, "Numfor fishing boats", heading=90),
        "coaster": S(-0.30, 136.40, "Coaster", heading=80),
    },
    units=[
        U("red","_vanilla","wp_ptg_komar","raider",name="Meridian missile craft 43",nation="Panama",weapons="Hold",
          route=[(-0.48,135.93,0)],telegraph=2,attacks=[(14,"wp_ss-n-2","tanker",2)]),
        U("blue","chinese-navy-plan","plan_z-18f","asw_support",name="Dipper 23",loadout="ASW",weapons="Tight"),
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "escort", variant="Variant2",
          weapons="Tight"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Tight",
          loadout="ASWKiller", slot="HeloRecon"),
        U("blue", "_vanilla", "civ_ms_ritina", "tanker", name="MT Hai Yang 7 (chartered)",
          weapons="Hold", route=[(-0.62, 136.00, 0)], telegraph=3),
        U("blue", "modern-plan-systems", "plan_y-9fq", "mpa", alt=8000, weapons="Tight",
          loadout="ASW", slot="Recon"),
        U("blue", "modern-chinese-airbase", "pla_airbase_modern", "field",
          name="Enclave field (PLAAF detachment)", weapons="Hold"),
        U("red", "us-navy-2027", "usn_ssn_virginia_2027", "red_sub", variant="Variant10",
          name="Contact GOLF", depth="belowlayer", weapons="Hold", radars="False",
          attacks=[(10,"usn_mk48_7","tanker",1),(18,"usn_mk48_7","tanker",1)],
          route=[(-0.55, 135.85, "belowlayer")], telegraph=2,
          recognise=False, orbat=False),
        U("neutral", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3", nation="Australia",
          loadout="ASW", weapons="Hold",
          route=[(-0.45, 135.40, 12000), (0.00, 136.20, 12000)], loop=True,
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
             "Boat": ("classify", "red_sub", 1), "Raider": ("destroy", "raider", 1)},
    declares=["RL02GolfSunk"],
    window=dict(buy=True, repair=True, rearm=True, allow=NORTH_HULLS + NORTH_AIR,
                flights=[HELO, RECON],
                situation=(
                    "The screen has a week in the approaches behind it. A Y-9 maritime patrol"
                    " aircraft can be allocated from the enclave field's detachment for the "
                    "night's escort. Hai Yang 7 is chartered and allocated to this operation."
                )),
    reports=[dict(minute=2,intel="ASW CONTROL: Dipper 23 is already ahead of the tanker. GOLF is east of the route; start the search before her ten-minute attack window. The missile craft north of the lane is a separate threat. The grey Poseidon is protected, not its spotter.")],
    role="escort",
)
