"""TS05 - Under the Tasman. The cable corridor, 4 February 2029.

Blank generation: HMAS Farncomb alone, weapons free for the first time in
the campaign, against ROMEO escorting the survey ship along the corridor
with a frigate and its Z-9 over the top. Depth, speed and the layer are the
mission. The flag on ROMEO is what the Southern Convoy and Southern Cross
read.
"""
from campaign_data import U, F, S

MISSION = dict(
    code="TS05", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 5",
    group="core", num="05", key="Under the Tasman", place="The cable corridor",
    intro="Farncomb alone, weapons free, against the nuclear boat that "
          "has screened the group since Cold Route. She is escorting the "
          "survey ship along the cable. Depth and the layer are the mission.",
    special="No requisition, and nothing of your own force sails: this is "
            "Farncomb's operation. What she sinks here is not in the "
            "Southern Convoy or in the box at Southern Cross.",
    sender="Commodore Alex Mercer, for the Submarine Force",
    intent=("The rules changed at Chatham Watch. ROMEO - the Type 093B that "
            "crossed the track at Cold Route and lay under the last voyage "
            "south - is on the cable corridor escorting the survey ship "
            "that found the fault, with a frigate over the top and its "
            "helicopter dipping. Farncomb is on the corridor ahead of them "
            "at periscope depth, weapons free. Sink the boat. The survey "
            "ship is a merchant hull under a state flag and she is not a "
            "target; the frigate is, if she gets in the way, but the boat "
            "is the mission and the frigate will not go home without her."),
    date=(2029, 2, 4), time=(2, 30), sea=3, clouds="Overcast", wind="NW",
    difficulty=4, minutes=75, centre=(-36.5, 160.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE TASMAN CABLE CORRIDOR, 36 South, the small hours. HMAS "
        "FARNCOMB is at periscope depth on the corridor, three hundred "
        "miles from the nearest coast, with the cable somewhere under her "
        "and a group coming up it from the south-west at eight knots.\\n\\n"
        "RV AUSTRAL SURVEY - a survey ship, a stand-in - is following the "
        "cable with a towed array. ROMEO is under her, escorting; a Type "
        "054A is over the top of both with a Z-9 dipping ahead of them. "
        "The layer is at a hundred and twenty feet and the frigate's sonar "
        "does not see below it.\\n\\n"
        "Weapons free on the boat and the frigate. The survey ship is not "
        "a target. A Tasman bulker and a whale are in the box, and the "
        "whale sounds like a boat. Seventy-five minutes. Nothing on the "
        "surface knows Farncomb is here until she fires."),
    forces="HMAS Farncomb, alone. Neutral: a bulker, a whale. Opposing: "
           "one Type 093B under the survey ship, one Type 054A with a Z-9 "
           "dipping, the survey ship RV Austral Survey.",
    objectives=[
        ("Romeo", "Destroy ROMEO", "40,-40,Fail,Main"),
        ("Survey", "The survey ship is not a target", "15,-40,Complete"),
        ("Farncomb", "Bring Farncomb home", "20,-30,Complete"),
        ("Neutrals", "Harm no merchant or whale", "0,-25,Complete"),
    ],
    victory=dict(kind="destroy", stations=["red_sub"], min_units=1, objective="Romeo"),
    fatal=[F("Farncomb", ["farncomb"])],
    neutral_objective="Neutrals",
    win="ROMEO is on the bottom of the Tasman with the cable under her, "
        "and the survey ship has turned for home with her towed array "
        "still streaming. Farncomb goes deep. The Southern Convoy sails "
        "without a boat beneath it.",
    lose="Farncomb is lost under the Tasman. The boat that has screened "
         "the group since Cold Route is still under it.",
    timeout="Seventy-five minutes and ROMEO has passed up the corridor "
            "with the survey ship over her. She is in the Southern Convoy's "
            "water by the nineteenth.",
    stations={
        # Farncomb on the corridor; the group 19 NM south-west coming up it
        # at eight knots, the boat under the survey ship and the frigate
        # over both; the Z-9 dipping 9 NM ahead of them; the bulker on the
        # Sydney-Auckland track, the whale on the layer.
        "farncomb": S(-36.50, 160.50, "HMAS Farncomb", heading=240),
        "red_sub": S(-36.70, 160.20, "Contact ROMEO", heading=60),
        "survey": S(-36.72, 160.18, "Austral Survey", heading=60),
        "red_frig": S(-36.78, 160.08, "Type 054A", heading=60),
        "red_dip": S(-36.60, 160.35, "Z-9 dip", heading=60, alt=1500),
        "bulker": S(-36.20, 160.90, "Bulker", heading=250),
        "whale": S(-36.45, 160.70, "Biologic", heading=180),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ssg_collins", "farncomb", variant="Variant2",
          name="HMAS Farncomb", depth="periscope", telegraph=1),
        U("red", "plan-submarines", "plan_ssn_type_093b", "red_sub", name="Contact ROMEO",
          depth="belowlayer",
          route=[(-36.40, 160.80, "belowlayer"), (-36.10, 161.30, "belowlayer")],
          telegraph=2),
        U("red", "re-power-resupply", "civ_ms_slavyansk", "survey",
          name="RV Austral Survey (survey ship, stand-in)", weapons="Hold",
          route=[(-36.42, 160.78, 0), (-36.12, 161.28, 0)], telegraph=2),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_frig",
          name="Type 054A frigate",
          route=[(-36.48, 160.68, 0), (-36.18, 161.18, 0)], telegraph=2),
        U("red", "modern-plan-systems", "plan_z-9c", "red_dip", name="Z-9 dip",
          alt=1500, loadout="ASWKiller"),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Bay of Plenty (Tauranga-Newcastle)",
          route=[(-36.60, 159.50, 0)], telegraph=3),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic NOVEMBER",
          depth="shallow"),
    ],
    resolve={"Romeo": "victory", "Neutrals": "neutral",
             "Survey": ("spare", "survey"),
             "Farncomb": ("protect", "farncomb")},
    declares=["TS05RomeoSunk"],
    flags=[dict(name="TS05RomeoSunk", units=["red_sub"],
                intel="ROMEO is gone. The boat that crossed the track at Cold "
                      "Route and lay under Last Ship South is on the bottom "
                      "of the Tasman. The Southern Convoy sails without her "
                      "beneath it.")],
    reveal_if=[dict(variable="TS03TenderNamed", units=["survey"], level="Classify",
                    intel="Chatham Watch's picture: the survey ship on the "
                          "corridor carries the tender's emitters - the same "
                          "navigation set, the same signals fit - and she is on "
                          "your plot classified. Where she is, the boat is "
                          "under her.")],
    window=dict(),
    # Farncomb going home after the kill is not the force being wiped out.
    force_loss=False,
    role="patrol",
)
