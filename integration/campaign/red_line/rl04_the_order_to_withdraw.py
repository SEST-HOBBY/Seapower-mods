"""RL04 — stop a ceasefire spoiler while defending the withdrawing supplier.

24 Oct 2026: a separate Meridian Q-ship attacks Hulunhu during the chase.
The Poseidon and any surviving GOLF are non-belligerents; the ceasefire
still protects them. GOLF remains conditional and is never a fatal target.

10 Nov 2026 (step 4 of the builder-grammar design): the coaster need not be
sunk. Closed to about three miles by the screen's lead ship (the ship's
flight does not count) she heaves to: a turn_back moves her to the neutral
task force, sends her after the group and slows her to telegraph 2, and
sinking her after that ends the mission as any protected neutral's loss
does. The victory has two paths, Sunk and HoveTo. A third, her engines
stopped, waits for campaign_data.DAMAGE_STATE (PC check P1) and is off.
"""
from campaign_data import U, F, S, DAMAGE_STATE
from .tables import HELO

# The engines-stopped outcome needs the UnitDamageState condition, whose INI
# keys no stock mission shows; it is offered only once DAMAGE_STATE is set.
_ENGINES = bool(DAMAGE_STATE)

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
    difficulty=4, minutes=50, centre=(-4.6, 128.9),
    blue_nation="China", red_nation="Australia",
    brief=(
        (
            "TACTICAL UPDATE: A second Meridian vessel, the Q-ship FV MERIDIAN WARDEN, "
            "has turned on HULUNHU. Expect a torpedo attack around minute nine. Your screen "
            "must split its attention between the escaping coaster and the supplier; both "
            "Meridian vessels are declared hostile. The grey Poseidon and any surviving GOLF "
            "are protected non-belligerents. Do not attack them.\n\n"
            "BANDA SEA, 0310, 27 NOVEMBER. The ceasefire took effect at 0000. The group "
            "acknowledged the order to withdraw at 2304 last night and is carrying it out: "
            "LIAONING, the replenishment ship HULUNHU and HAI YANG 7, chartered, north-west "
            "for the Manipa approaches with what the twenty-third left, and your frigate on the "
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
            "defensive settings: engage only the two Meridian vessels. The protected observers "
            "are non-belligerents. Stop the coaster before she reaches the marked circle "
            "south-east, where she clears the screen. "
            + ("Sink her, stop her engines, or close her" if _ENGINES else "Sink her, or close her")
            + " with the screen's lead ship to within about three miles: she will heave to "
            "and follow the group, and from then she is a protected neutral whose loss ends "
            "the operation. Set the lead ship's weapons to Hold before closing, or she may open "
            "fire first. "
            "Then bring LIAONING and HULUNHU both within five miles of the withdrawal point "
            "north-west. The order is complete when both are inside that circle, MERIDIAN "
            "HARMONY is sunk" + (", stopped" if _ENGINES else "") + " or has hove to, and no "
            "incoming weapon is still tracked against the group.\\n\\nA Banda "
            "fishing boat and the Banda Neira ferry are on the water."
        )),
    forces=(
        "Your screen, with its flight. A hostile Q-ship is closing Hulunhu. Allocated: Liaoning, the replenishment ship and MT Hai"
        " Yang 7. In company and turning away: MV Meridian Harmony, armed. Watching: a "
        "coalition P-8A, and possibly a submarine astern. Neutral: a fishing boat and a ferry."
    ),
    objectives=[
        ("Withdrawal", "Bring Liaoning and Hulunhu inside the withdrawal circle north-west",
         "35,-35,Fail,Main"),
        ("Spoiler", "Also required: stop Meridian Harmony before she clears the screen, by "
                    "sinking her or closing her until she heaves to", "20,-40,Fail,Main"),
        ("Restraint", "Engage only the two declared hostile Meridian vessels, and not Meridian "
                      "Harmony once she has hove to", "15,-40,Complete"),
        ("Boat", "Leave the boat astern alone, if she is there", "0,-40,None"),
        ("Carrier", "Bring Liaoning through intact", "10,-30,Complete"),
        ("Supply", "Keep Hulunhu afloat during the withdrawal", "10,-30,Complete"),
        ("Qship", "Stop the Q-ship attacking the replenishment ship", "15,0,None"),
        ("Traffic", "Harm no protected contact or civil traffic", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", units=["group#1", "group#2"], at=(-4.40, 128.50),
                 radius=5, min_units=2, objective="Withdrawal", transit=12,
                 also=[dict(kind="no_incoming")],
                 any_of=[
                     dict(name="Sunk", also=[dict(kind="destroyed", units=["spoiler"], min_units=1)]),
                     dict(name="HoveTo",
                          also=[dict(kind="event", event="HeaveTo"),
                                dict(kind="afloat", units=["spoiler"])],
                          win=(
                              "LIAONING and HULUNHU are inside the withdrawal circle, and MERIDIAN "
                              "HARMONY has hove to and is following the group north-west. The "
                              "group's report will say what was done and why; the Poseidon has "
                              "the same account."
                          )),
                 ] + ([dict(name="Crippled",
                            also=[dict(kind="event", event="HeaveToDisabled"),
                                  dict(kind="afloat", units=["spoiler"])],
                            win=(
                                "LIAONING and HULUNHU are inside the withdrawal circle, and MERIDIAN "
                                "HARMONY is dead in the water short of the lane, her engines "
                                "stopped. The group's report will say what was done and why; the "
                                "Poseidon has the same account."
                            ))] if _ENGINES else [])),
    # The heave-to: the screen's lead ship (escort, the anchor) inside three
    # miles of her on her own track, the helicopter not counted.
    turn_back=[dict(
        name="HeaveTo", units=["spoiler"], by=["escort"], radius=3,
        to=(-4.45, 128.60), telegraph=2, transfer="Neutral", objective="Spoiler",
        intel=(
            "BRIDGE: MERIDIAN HARMONY has answered at last. She has hove to and is turning to "
            "follow the group north-west. She is no longer a declared hostile; do not fire on her."
        ),
        protected=dict(objective="Restraint", message=(
            "MERIDIAN HARMONY had hove to and was following the group when she was sunk. Under "
            "the ceasefire that is the group's violation, and the Poseidon has it recorded."
        )),
        **(dict(or_damaged=dict(mode="propulsion_all")) if _ENGINES else {}))],
    denied=[dict(units=["spoiler"], at=(-4.84, 128.92), radius=4, objective="Spoiler",
                 message=(
                     "MERIDIAN HARMONY has cleared the screen and is running south for the "
                     "lane at full speed. The group cannot follow her and keep its withdrawal "
                     "order. Whatever she does tomorrow, she sailed from this group's company."
                 ))],
    fatal=[F("Restraint", ["red_air"]), F("Carrier"), F("Supply")],
    neutral_objective="Traffic",
    win=(
        "LIAONING and HULUNHU are inside the withdrawal circle, and MERIDIAN HARMONY is sunk "
        "short of the lane. The ship's flight is searching for her crew. The group's report "
        "will say what was done and why; the Poseidon has the same account."
    ),
    lose=(
        "The withdrawal has failed: LIAONING or HULUNHU is lost, or the Poseidon is down. "
        "The ceasefire is hours old, and the group is in its first violation report."
    ),
    timeout="{deadline_clock}, and the group is still short of the withdrawal circle. The withdrawal "
            "order had a time on it, and the coalition's aircraft has recorded the group missing it.",
    stations={
        "escort": S(-4.45, 128.85, "Escort", heading=300),
        "flight": S(-4.47, 128.83, "Ship's flight", heading=300, alt=500),
        "group": S(-4.50, 128.70, "Liaoning", heading=300),
        "charter": S(-4.40, 128.60, "Hai Yang 7", heading=300),
        "spoiler": S(-4.56, 128.76, "Meridian Harmony", heading=150),
        "qship": S(-4.63,128.62,"Hostile Q-ship",heading=330),
        "red_air": S(-4.00, 129.40, "Patrol aircraft", heading=240, alt=14000),
        "red_sub": S(-4.90, 128.60, "Contact GOLF", heading=330),
        "fishing": S(-4.30, 129.10, "Banda fishing boat", heading=180),
        "ferry": S(-4.75, 129.40, "Banda Neira ferry", heading=250),
    },
    units=[
        U("red","project-2498-zyetseth","civ_fv_okean_surprise","qship",name="FV Meridian Warden",nation="Panama",weapons="Hold",
          route=[(-4.43,128.51,0)],telegraph=3,attacks=[(9,"wp_53-65K","group#2",1)]),
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "escort", variant="Variant1",
          weapons="Tight"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "liaoning-type-001", "plan_type_001", "group", name="Liaoning",
          weapons="Hold", route=[(-4.40, 128.50, 0)], telegraph=3),
        U("blue", "SEST_Replenishment", "plan_aor_type901", "group", variant="Variant1",
          name="Replenishment ship Hulunhu", weapons="Hold",
          route=[(-4.42, 128.52, 0)], telegraph=3),
        U("blue", "_vanilla", "civ_ms_ritina", "charter", name="MT Hai Yang 7 (chartered)",
          weapons="Hold", route=[(-4.39, 128.48, 0)], telegraph=3),
        U("red", "auxilliary-merchant-pack", "ran_ms_super_p", "spoiler",
          name="MV Meridian Harmony", nation="Panama", weapons="Hold",
          route=[(-4.84, 128.92, 0), (-5.40, 129.25, 0)], telegraph=4),
        U("neutral", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3", nation="Australia",
          loadout="ASW", weapons="Hold",
          route=[(-4.80, 128.40, 14000), (-4.00, 129.40, 14000)], loop=True,
          telegraph=3),
        U("neutral", "us-navy-2027", "usn_ssn_virginia_2027", "red_sub", variant="Variant10",
          name="Contact GOLF", depth="belowlayer", weapons="Hold", radars="False",
          spawn_if=("RL02GolfSunk", "IsFalse"),
          route=[(-4.40, 128.30, "belowlayer")], telegraph=2,
          recognise=False),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Banda fishing boat Lautaka", route=[(-4.60, 129.20, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_roro_c", "ferry",
          name="KM Banda Neira (Ambon-Banda ferry)", route=[(-3.90, 128.20, 0)],
          telegraph=3),
    ],
    resolve={"Withdrawal": "victory", "Traffic": "neutral",
             "Spoiler": ("destroy", "spoiler", 1),
             "Restraint": ("spare", "red_air"),
             "Boat": ("spare", "red_sub"),
             "Carrier": ("protect", "group#1"), "Supply": ("protect", "group#2"),
             "Qship": ("destroy", "qship", 1)},
    declares=[],
    window=dict(buy=False, repair=True, rearm=False, flights=[HELO],
                situation=(
                    "The ceasefire allows repairs alongside the replenishment ship and "
                    "nothing else. There is no rearming and no reinforcement before the "
                    "withdrawal."
                )),
    reports=[dict(minute=2,intel="GROUP STAFF: The coaster is the escape problem; the Q-ship is the immediate threat to Hulunhu. Use separate assignments, and do not send the whole screen away from the replenishment ship.")],
    role="escort",
)
