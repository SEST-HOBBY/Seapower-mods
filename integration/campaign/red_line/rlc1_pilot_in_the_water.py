"""RLC1 — the same rescue race, starting closer to its decision.

24 Oct 2026: the lead ship starts roughly seven miles from the raft and
the patrol vessel just under nine. Best speed still matters; the four-minute
pickup and protected patrol vessel/aircraft are retained. Thirty-five-minute
window replaces the earlier sixty-minute approach.
"""
from campaign_data import U, F, S
from .tables import HELO

MISSION = dict(
    code="RLC1", series="Red Line", seq="RED LINE  ·  CONTINGENCY",
    group="contingency", num="C1", key="Pilot in the Water", place="Banda Sea",
    geography="coast",
    intro=(
        "Contingency. A J-15 pilot is in his raft, and an Australian patrol vessel is racing "
        "the screen to him. Be alongside first. Fire on nothing."
    ),
    special=(
        "Recover the pilot of a J-15 down in the Banda Sea. Select a detachment from the "
        "screen; there is no rearming and no reinforcement before it sails. The task closes "
        "when The Order to Withdraw is complete."
    ),
    sender="Fleet headquarters",
    intent=((
        "A pilot of the group's is alive in the water, and the coalition can hear his beacon "
        "as well as we can. He comes home in a Chinese ship. Get there first and get him "
        "aboard, and fire on nothing to do it: whatever yesterday was, this morning is a man "
        "in the water. The patrol vessel is doing what any ship does for one. Do not stop "
        "her from doing it, and do not let her be the one who does."
    )),
    date=(2028, 11, 24), time=(6, 10), sea=2, clouds="Scattered_1", wind="SE",
    difficulty=2, minutes=35, centre=(-5.05, 129.0),
    blue_nation="China", red_nation="Australia",
    brief=(
        (
            "BANDA SEA, 0610. At 0447 FLYING SHARK 85, a J-15 on LIAONING's dawn patrol, "
            "reported a fire warning sixty miles south-east of the group and went into the "
            "sea at 0452. The pilot ejected. His beacon has been transmitting since 0455, and "
            "he is on your plot, alive in his raft.\\n\\nThe Australians heard it too. A patrol "
            "vessel of theirs in the southern approaches turned for the beacon at 0540 and is "
            "closing at about twenty knots, a little under nine miles off him. Nobody aboard her has fired "
            "at anybody. Anything that happens to her, or to the Poseidon overhead, is the "
            "group firing on a ship that is recovering a man.\\n\\nYour detachment is "
            "about seven miles north-west of him: closer than she is, and faster. Short of "
            "your best speed she is there first. Get the lead ship close alongside, inside "
            "three cables, stopped, put the boat in the water and hold there until he is "
            "aboard: about four minutes. If the patrol vessel is alongside "
            "him first, he goes home on the Australians' timetable, and the coalition has a "
            "photograph of a Chinese pilot on an Australian deck.\\n\\nYour ships and the "
            "ship's flight start at weapons Hold. Two Banda fishing boats are on the water."
        )),
    forces=(
        "Your detachment, with the ship's flight if one is embarked. In the water: the pilot "
        "of Flying Shark 85, in his raft. Racing you: an Australian patrol vessel. Watching: "
        "a RAAF P-8A. Neutral: two fishing boats."
    ),
    objectives=[
        ("Pilot", "Get the lead ship alongside the pilot and hold there until he is aboard, "
                  "before the patrol vessel reaches him", "35,-35,Fail,Main"),
        ("Restraint", "Fire on nothing: not the patrol vessel, not the aircraft",
         "15,-40,Complete"),
        ("Watchers", "Classify the patrol vessel and the aircraft over her", "10,0,None"),
        ("Traffic", "Harm no fishing boat", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="frigate", at=(-5.05, 129.05), radius=2,
                 min_units=1, objective="Pilot",
                 after=dict(kind="area", units="frigate", at_unit="pilot", radius=0.3,
                            min_units=1, hold_minutes=4,
                            intel=(
                                "SEA BOAT: The ship is alongside the raft and the boat is in "
                                "the water. Hold her here, stopped, until the pilot is "
                                "aboard."
                            ),
                            held=("Pilot aboard.",
                                  "SEA BOAT: The pilot of Flying Shark 85 is aboard, cold and "
                                  "talking. The boat is coming back to the davit."))),
    denied=[dict(units=["opv"], at=(-5.05, 129.05), radius=1, objective="Pilot",
                 message=(
                     "The Australian patrol vessel is alongside the raft and her boat has the "
                     "pilot. He goes home when Canberra says so, and the coalition has the "
                     "photograph."
                 ))],
    fatal=[F("Restraint", ["opv", "red_air"])],
    neutral_objective="Traffic",
    win=(
        "The pilot of FLYING SHARK 85 is aboard and the detachment is turning for the group. "
        "The patrol vessel has stopped short of the raft and is recovering her own boat. The "
        "Poseidon's recording shows two ships racing for one man, and the right one winning."
    ),
    lose=(
        "The patrol vessel or the Poseidon has been fired on. The group has done the one thing "
        "its orders say it will not do, over a man in the water, and the coalition has it "
        "recorded."
    ),
    timeout="{deadline_clock}, and nobody has the pilot. Whichever ship reaches him now, he "
            "has been in the water too long.",
    stations={
        "frigate": S(-4.965,128.965, "Detachment", heading=135),
        "flight": S(-4.975,128.955, "Ship's flight", heading=135, alt=500),
        "pilot": S(-5.05, 129.05, "Pilot in the water"),
        "opv": S(-5.18,129.11, "Australian patrol vessel", heading=335),
        "red_air": S(-5.40, 129.40, "Patrol aircraft", heading=310, alt=12000),
        "fishing_e": S(-4.90, 129.30, "Fishing boat", heading=200),
        "fishing_w": S(-5.15, 128.80, "Fishing boat", heading=60),
    },
    units=[
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "frigate", variant="Variant2",
          weapons="Hold"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "_vanilla", "all_life_raft_single", "pilot",
          name="Flying Shark 85 (pilot's raft)", weapons="Hold"),
        U("red", "SEST_RAN_Fleet", "ran_opv_arafura", "opv", variant="Variant4",
          name="Australian patrol vessel", weapons="Hold",
          route=[(-5.05, 129.05, 0)], telegraph=4),
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3",
          loadout="ASW", weapons="Hold",
          route=[(-5.50, 129.30, 12000), (-4.85, 128.95, 12000)], loop=True,
          telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing_e",
          name="Banda fishing boat Bintang Timur", route=[(-5.10, 129.20, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fishing_w",
          name="Banda fishing boat Sinar Pagi", route=[(-5.00, 128.95, 0)], telegraph=1),
    ],
    resolve={"Pilot": "victory", "Traffic": "neutral",
             "Restraint": ("spare", "opv", "red_air"),
             "Watchers": ("classify", ["opv", "red_air"], 2)},
    declares=[],
    expires_after="The Order to Withdraw",
    window=dict(flights=[HELO], detachment=True),
    role="patrol",
)
