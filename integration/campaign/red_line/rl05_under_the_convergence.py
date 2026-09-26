"""RL05 - Under the Convergence. South of the Great Australian Bight,
27 December 2028.

A detached submarine operation, the way the stock campaign does them: an
authored boat, no builder, nothing of the owned screen sails. Liaoning is
three days astern; her submarine goes ahead of her through a RAAF Poseidon
barrier and must not be classified. It is the first mission in the pack
scored on what the ENEMY knows: the 'unseen' objective and fatal fail it
the moment the coalition's side classifies the boat.

Southern Reach first puts a Type 093B in the south on 2 January (Cold
Route, where she is ROMEO), and its intelligence summary of 5 January is the
first to list one with the protection group. So on 27 December she must pass
unclassified, and the mission's canonical outcome - its victory - is exactly
that. Fujian's Shadow already calls the Type 093B in the northern screen
ROMEO; nothing here says whether Hull 419 is that boat, because that
mission may sink her.
"""
from campaign_data import U, F, S

MISSION = dict(
    code="RL05", series="Red Line", seq="RED LINE  ·  MISSION 5",
    group="core", num="05", key="Under the Convergence",
    place="South of the Great Australian Bight",
    intro=(
        "Detached submarine operation. Take the boat through the Poseidon barrier ahead of the"
        " carrier. Do not let it classify her. Fire on nothing."
    ),
    special=(
        "No force allocation, and the screen stays with the carrier: this is a detached "
        "submarine operation. You command Hull 419 for this operation only."
    ),
    sender="Fleet headquarters, southern tasking",
    intent=((
        "The group's southern task depends on the carrier arriving before the coalition knows "
        "what is with her. Hull 419 is the carrier's screen under the water and she reaches "
        "the forward box unclassified and unused. If the aircraft finds her, she does not "
        "answer it. She leaves."
    )),
    date=(2028, 12, 27), time=(4, 30), sea=5, clouds="Overcast", wind="W",
    difficulty=3, minutes=120, centre=(-47.5, 140.5),
    blue_nation="China", red_nation="Australia",
    geography="coast",
    brief=(
        (
            "SOUTH OF THE BIGHT, 0430. LIAONING is three days astern. HULL 419 goes ahead of "
            "her, and nobody is to know the boat is in the Southern Ocean until the carrier "
            "is.\\n\\nThe RAAF has flown a Poseidon barrier across this line since Christmas "
            "Eve. Canberra and Wellington have authorised action against one submarine, the "
            "Russian boat they blame for the coaster torpedoed on the twenty-first, and their "
            "aircraft carry torpedoes. At forty-seven south, on a sonobuoy, one nuclear boat "
            "sounds much like another.\\n\\nTake HULL 419 through the barrier to the forward "
            "box. Nothing is fired. If the patrol puts a class on her, the boat is a named "
            "contact before the carrier arrives and the operation has failed.\\n\\nA longliner,"
            " an expedition cruise ship bound for the ice, a bulker for Hobart and a humpback "
            "are in the sonar picture. Use them."
        )),
    forces=(
        "Hull 419, a Type 093B, dived. Watching: a RAAF P-8A on a barrier racetrack and an "
        "MQ-4C Triton high to the north. Neutral: a toothfish longliner, an expedition cruise "
        "ship, a bulker and a whale."
    ),
    objectives=[
        ("Passage", "Take Hull 419 through the barrier to the carrier's forward box",
         "40,-40,Fail,Main"),
        ("Unseen", "Keep Hull 419 off their plot: do not let the patrol classify her",
         "25,-40,Complete"),
        ("Restraint", "Fire on nothing", "15,-40,Complete"),
        ("Boat", "Bring Hull 419 through intact", "10,-30,Complete"),
        ("Traffic", "Harm no fishing boat, merchant or whale", "0,-30,Complete"),
    ],
    # The forward box, authored rather than solved: a box solved on the
    # boat's course lands short of the racetrack, and the operation is the
    # passage under it. Its near edge is a mile past the barrier line, 9.7 NM
    # ahead of the boat. The clock is two hours because the passage is meant
    # to be made quietly: 116 minutes at five knots, 97 at six, 58 at ten.
    # At eighty minutes only ten knots arrived in time, and a boat keeping
    # herself off the plot at five ran out of clock under the barrier.
    victory=dict(kind="arrive", station="boat", at=(-47.42, 140.25), radius=10,
                 min_units=1, objective="Passage"),
    # Classified is lost: the boat on their plot ends it the same way the
    # boat on the bottom does.
    fatal=[F("Unseen", kind="unseen"), F("Restraint", ["red_air", "triton"]), F("Boat")],
    neutral_objective="Traffic",
    win=(
        "HULL 419 is in the forward box, and the coalition's plot of the Southern Ocean has no "
        "Type 093B on it. The coalition knows a carrier is coming. It does not know her "
        "submarine is already here."
    ),
    lose=(
        "HULL 419 is on the coalition's plot or on the bottom, or a patrol aircraft is down. "
        "Any of them makes the group's screen boat a named contact before the carrier arrives, "
        "and the southern task starts from that."
    ),
    timeout="0630, and HULL 419 is short of the box. She will be in it by nightfall, half "
            "a day behind the plan the carrier is sailing to.",
    stations={
        # The boat west of the barrier, heading 110 for the box beyond it.
        # The Poseidon's racetrack runs north-north-east to south-south-west
        # across her track, 9 NM ahead of her; the Triton works high to the
        # north. Every position is hundreds of miles from any coast.
        "boat": S(-47.30, 139.80, "Hull 419", heading=110),
        "red_air": S(-47.65, 139.85, "Barrier patrol", heading=20, alt=15000),
        "triton": S(-46.80, 140.50, "Triton", heading=230, alt=50000),
        "longliner": S(-47.50, 140.00, "Longliner", heading=120),
        "cruise": S(-46.90, 140.80, "Expedition cruise ship", heading=165),
        "bulker": S(-47.00, 139.50, "Bulker", heading=85),
        "whale": S(-47.35, 140.05, "Biologic", heading=150),
    },
    units=[
        # Radars off, as every submarine in the stock missions starts: a mast
        # raised at periscope depth with the radar live is an emitter the
        # Poseidon's ESM classifies.
        U("blue", "plan-submarines", "plan_ssn_type_093b", "boat", name="Hull 419",
          depth="belowlayer", weapons="Hold", radars="False"),
        # The barrier: a racetrack across the boat's track, flown until the
        # clock runs out.
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3",
          loadout="ASW", weapons="Hold",
          route=[(-47.05, 140.15, 15000), (-47.65, 139.85, 15000)], loop=True,
          telegraph=3),
        # High to the north, working back and forth over the barrier.
        U("red", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "triton", weapons="Hold",
          route=[(-47.30, 140.20, 50000), (-46.80, 140.90, 50000)], loop=True,
          telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "longliner",
          name="Longliner Tasman Harvest", route=[(-47.90, 141.00, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Southern Light (expedition cruise, Adelaide for Commonwealth Bay)",
          route=[(-49.00, 141.50, 0)], telegraph=3),
        U("neutral", "auxilliary-merchant-pack", "anl_ms_bulk", "bulker",
          name="MV Leeuwin Trader (Fremantle for Hobart)",
          route=[(-46.50, 145.00, 0)], telegraph=3),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic",
          depth="shallow"),
    ],
    resolve={"Passage": "victory", "Traffic": "neutral",
             "Unseen": ("unseen", "boat"),
             "Restraint": ("spare", "red_air", "triton"),
             "Boat": ("protect", "boat")},
    declares=[],
    window=dict(),
    role="patrol",
)
