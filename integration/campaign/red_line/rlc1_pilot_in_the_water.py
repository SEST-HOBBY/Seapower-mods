"""RLC1 - Pilot in the Water. Banda Sea, 24 November 2028.

The campaign's first contingency (campaign-upgrade-plan.md section 4.2,
step RL-1, 20 Oct 2026): a race, with the safety still on. A J-15 off
Liaoning's dawn patrol went into the sea sixty miles south-east of the
group, and the pilot's beacon has an Australian patrol vessel turning for
it too. Get alongside him first, hold there while the sea boat brings him
in, and touch nothing of the coalition's: the patrol vessel is doing what
any ship does for a man in the water.

The screen's own detachment flies it - stock's 03B shape, Southern Watch's
After the Wake - so the ship that races is one the player still owns, not a
placed hull The Other Picture may already have cost them. It is the morning
after the coalition's fleet action, and nothing here says what happened on
the 23rd: the aircraft is Liaoning's, whom Southern Reach keeps until
February, and it came down with a fire warning, not to a missile. The brief
says nothing of Fujian, and nothing that would mean the group had never
fired: the reply of the 22nd was to enforce the closure on the 23rd, so the
restraint asked for is this morning's, over one man (review of 20 Oct 2026).

The recovery is the builder's held stage (hold_minutes, with its `held`
message): the lead ship within three cables of the raft for four minutes,
the pop-up, and the win, whose box is already met when the hold arms it.
The circle is that small so that the hold needs the ship stopped: the
first build's mile was crossed in four minutes at 30 knots, so an 054A
could win without slowing (review of 20 Oct 2026); three cables' circle
is 0.6 NM across, nine knots for four minutes at most. A denied race is
lost to the patrol vessel alongside him first, and stays armed to the
end; a win cannot come later than the hold, so the race is only ever lost
while he is still in the water.

The patrol vessel is ran_opv_arafura Variant4 (OPV 206 Gippsland), the
one Arafura hull no mission places and no roster sells: Variant1 is on
both coalition rosters, Variant2 (Eyre) and Variant3 (Pilbara) sail in
Southern Watch and can be lost there. The text calls her "an Australian
patrol vessel" and never the name a full identification shows. She and the
Poseidon are spared with a fatal entry, as every coalition unit here is.

Geography: proved against the coastline (geo/banda_theatre_coast.json);
the nearest land is thirty-five miles from anything placed.
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
    difficulty=2, minutes=60, centre=(-5.05, 129.0),
    blue_nation="China", red_nation="Australia",
    brief=(
        (
            "BANDA SEA, 0610. At 0447 FLYING SHARK 85, a J-15 on LIAONING's dawn patrol, "
            "reported a fire warning sixty miles south-east of the group and went into the "
            "sea at 0452. The pilot ejected. His beacon has been transmitting since 0455, and "
            "he is on your plot, alive in his raft.\\n\\nThe Australians heard it too. A patrol "
            "vessel of theirs in the southern approaches turned for the beacon at 0540 and is "
            "closing at about twenty knots, fourteen miles off him. Nobody aboard her has fired "
            "at anybody. Anything that happens to her, or to the Poseidon overhead, is the "
            "group firing on a ship that is recovering a man.\\n\\nYour detachment is "
            "thirteen miles north-west of him: about as far as she is, and faster. Short of "
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
    # The lead ship (the generated anchor) within three cables of the raft
    # for four minutes: the held trigger's clock starts on her first arrival,
    # it shows the pop-up and arms the win, whose two-mile box the ship is
    # already in - so the pilot aboard IS the win, and the patrol vessel
    # arriving after it changes nothing. Nothing restarts that clock (the
    # arrival enables the held trigger once). Leave the circle before the
    # four minutes and come back after them, and the pop-up comes the moment
    # she is back inside if a Time condition stays met once its minute has
    # passed, or never if it is met only at that minute: test card 8B.7
    # records which, and the brief says to stop there.
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
    # The race, lost: the patrol vessel within a mile of him while he is
    # still in the water.
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
        # The raft 60 NM south-east of the group, in the middle of the Banda
        # Sea; the detachment 13.5 NM north-west of him, the patrol vessel
        # 13.9 NM south-south-east, both turned towards the beacon. She is
        # at the mile at minute 39 at telegraph 4's 20 knots; an 054A at 27
        # is stopped in the three cables at about 30 and done at 34, and at
        # the builder's conservative 18 knots is there at 44: below about 23
        # knots the race is lost. It was 20.1 NM until the review of 20 Oct
        # 2026, which left her an hour and the race no race. The deployment
        # box's nearest corner is 9.3 NM from the raft (the builder's 3 NM
        # pad on the diagonal), a shorter run the player may take. The
        # Poseidon's racetrack runs over the raft; the fishing boats are
        # either side of the race.
        "frigate": S(-4.89, 128.89, "Detachment", heading=135),
        "flight": S(-4.90, 128.87, "Ship's flight", heading=135, alt=500),
        "pilot": S(-5.05, 129.05, "Pilot in the water"),
        "opv": S(-5.26, 129.15, "Australian patrol vessel", heading=335),
        "red_air": S(-5.40, 129.40, "Patrol aircraft", heading=310, alt=12000),
        "fishing_e": S(-4.90, 129.30, "Fishing boat", heading=200),
        "fishing_w": S(-5.15, 128.80, "Fishing boat", heading=60),
    },
    units=[
        # The anchor: replaced by the player's first ship. Unnamed - the
        # builder refuses a name on a generated anchor.
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "frigate", variant="Variant2",
          weapons="Hold"),
        # Air-tasking placeholder: the cockpit a purchased Z-9C takes. No
        # name, no objective - slot-tagged aircraft keep the player's own.
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        # One man in a one-man raft, the kind carried in an ejection seat.
        # On the player's side, so his beacon is on the plot from the first
        # second and no deployment box can be drawn round him.
        U("blue", "_vanilla", "all_life_raft_single", "pilot",
          name="Flying Shark 85 (pilot's raft)", weapons="Hold"),
        # Turned for the beacon, at weapons Hold: she is recovering a man
        # in the water, not fighting for him.
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
    # A detachment of what The Other Picture left, with a Ship's Flight
    # row. No builder, no repair, no rearm: the tasking's paragraph 4, and a
    # man in the water does not wait for the replenishment ship.
    window=dict(flights=[HELO], detachment=True),
    role="patrol",
)
