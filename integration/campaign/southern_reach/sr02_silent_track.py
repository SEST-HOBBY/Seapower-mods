"""SR02 - Silent Track. Macquarie Ridge, 9 December 2028.

A detached submarine operation, the way the stock campaign does them: an
authored boat, no builder, nothing of the owned force sails. HMAS Collins
and a New Zealand Poseidon put a name on the nuclear boat working the ridge
where the resupply route crosses it, without either side doing anything the
ceasefire would have to notice. Destruction is a failure, not a bonus.
"""
from campaign_data import U, F, S

MISSION = dict(
    code="SR02", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 2",
    group="core", num="02", key="Silent Track", place="Macquarie Ridge, south of New Zealand",
    intro="HMAS Collins and a New Zealand Poseidon put a name on the nuclear "
          "boat working the Macquarie Ridge. The ceasefire holds until somebody says it does not, and "
          "that is not going to be a torpedo.",
    special="No requisition, and nothing of your own force sails: this is a "
            "detached submarine operation. You command HMAS Collins for this "
            "operation only, with a New Zealand Poseidon overhead on a "
            "national allocation.",
    sender="Commodore Alex Mercer; Squadron Leader Tane Rewi, No. 5 Squadron RNZAF, for the aircraft",
    intent=("A nuclear boat is working the ridge because the ridge is where "
            "the Antarctic resupply route crosses. Put a name on her - class, and if you can, "
            "hull - and get off her track. Nobody fires. The ceasefire is twelve "
            "days old and it is not Collins's to end. Rewi's crew flies its "
            "own plan and goes home to Ohakea; the aircraft is not yours to "
            "spend. A research vessel with a New Zealand flag is on the ridge "
            "with a science party. She is ours."),
    date=(2028, 12, 9), time=(4, 30), sea=5, clouds="Overcast", wind="W",
    difficulty=2, minutes=70, centre=(-50.3, 162.8),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "MACQUARIE RIDGE, before dawn. A longliner south of Campbell Island "
        "reported a submarine contact on the sixth, twelve hundred miles from "
        "any tender, where no diesel boat works in December. Contact VICTOR "
        "is nuclear, it is "
        "working the ridge, and the ridge is where every ship for the ice "
        "crosses.\\n\\n"
        "COLLINS is at periscope depth on the ridge's western flank with "
        "thirty-one days of patrol left in her. KIWI 05, a New Zealand "
        "Poseidon out of Ohakea with Squadron Leader Rewi's crew, has one "
        "sortie and a field of buoys. NAN HAI 27, the research trawler that "
        "shadowed the Storm Bay convoy, is thirty miles north, and the boat "
        "will not be far from her.\\n\\n"
        "Classify the contact, then take Collins east off the ridge to the "
        "exit point. Do not attack it. RV SOUTHERN SURVEYOR is on the ridge "
        "with a science party, a Bluff longliner is working the shelf, and "
        "there is a whale that three sonar operators will call a submarine. "
        "The ceasefire holds down here until somebody says it does not."),
    forces="HMAS Collins at periscope depth. One RNZAF P-8A on a single "
           "national sortie. In the water: one nuclear boat, one research "
           "trawler with an intelligence fit, a New Zealand research vessel, "
           "a Bluff longliner, one whale.",
    objectives=[
        ("Track", "Classify the contact, then take Collins to the exit point",
         "30,-30,Fail,Main"),
        ("Restraint", "Do not attack the contact: the ceasefire holds",
         "15,-35,Complete"),
        ("Collins", "HMAS Collins must survive", "10,-25,Complete"),
        ("Kiwi", "Do not lose Kiwi 05", "10,-15,Complete"),
        ("Traffic", "Harm no research vessel, fishing boat or whale", "0,-25,Complete"),
    ],
    # Nothing counts until the boat is classified: the mission is called
    # Silent Track because finding out what she is IS the task. Then Collins
    # to the exit point east of the ridge, solved at a submarine's speed.
    victory=dict(kind="arrive", station="collins", min_units=1, objective="Track",
                 after=dict(kind="classify", units="red_sub", min_units=1,
                            intel="VICTOR classified: an Akula-class nuclear "
                                  "boat, running north-east along the ridge at "
                                  "eight knots. Rewi's crew has the datum logged "
                                  "for Wellington and Canberra both. Take Collins "
                                  "east, off her track, and do not give her a "
                                  "reason.")),
    fatal=[F("Collins", ["collins"])],
    neutral_objective="Traffic",
    win="Collins is off the ridge with a name on the boat, and the boat never "
        "knew how long she was held. Rewi, on the way home: 'One Akula. One "
        "whale. No torpedoes. Good morning.'",
    lose="Collins is lost on a ridge nobody was fighting over, and the "
         "ceasefire in the south is now a question.",
    timeout="Seventy minutes and the contact is still a contact. She is off "
            "the ridge and so is the picture, and the next convoy crosses "
            "it blind.",
    stations={
        # Collins on the western flank at periscope depth; VICTOR 25 NM
        # north-east running up the ridge; the collector 30 NM north as the
        # tell. The research vessel, the longliner and the whale are inside
        # the picture - the whale 8 NM from Collins, where a sonar operator
        # will call it first.
        "collins": S(-50.35, 162.70, "HMAS Collins", heading=60),
        "kiwi": S(-50.90, 163.40, "Kiwi 05", heading=330, alt=12000),
        "red_sub": S(-50.05, 163.15, "Contact VICTOR", heading=40),
        "shadow": S(-49.85, 162.90, "Research trawler", heading=40),
        "longliner": S(-50.55, 163.30, "Bluff longliner", heading=120),
        "survey": S(-50.20, 162.30, "RV Southern Surveyor", heading=200),
        "whale": S(-50.45, 162.95, "Biologic ECHO", heading=150),
        "home": S(-40.206, 175.388, "RNZAF Base Ohakea"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ssg_collins", "collins", variant="Variant1",
          name="HMAS Collins", weapons="Tight", depth="periscope"),
        # No. 5 Squadron's own aircraft: Squadron6 of the winning P-8
        # squadrons file is New Zealand. A loan, not a grant - no JoinTaskForce.
        U("blue", "p-8-poseidon", "usn_p8", "kiwi", squadron="Squadron6",
          name="Kiwi 05", alt=12000, weapons="Tight", loadout="ASW"),
        U("red", "russian-submarines", "wp_ssn_akula", "red_sub", name="Contact VICTOR",
          depth="belowlayer", weapons="Tight",
          route=[(-49.70, 163.60, "belowlayer"), (-49.40, 164.00, "belowlayer")],
          telegraph=2),
        U("red", "_vanilla", "wp_agi_okean", "shadow", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-49.50, 163.30, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "longliner",
          name="Longliner Toroa (Bluff)", route=[(-50.80, 163.90, 0)], telegraph=2),
        U("neutral", "re-power-resupply", "civ_ms_irkutsk", "survey",
          name="RV Southern Surveyor (NZ research vessel)",
          route=[(-50.60, 162.00, 0)], telegraph=2),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic ECHO",
          depth="shallow"),
        U("blue", "SEST_RAAF_Bases", "airbase_rnzaf_ohakea", "home",
          name="RNZAF Base Ohakea", nation="NewZealand", weapons="Hold"),
    ],
    resolve={"Track": "victory", "Traffic": "neutral",
             "Restraint": ("spare", "red_sub"),
             "Collins": ("protect", "collins"),
             "Kiwi": ("protect", "kiwi")},
    # The classify stage does not write a variable itself; the Track
    # objective's completion is what Beneath the South reads, so it is
    # written by a classify resolver of its own on the same contact.
    declares=["SR02BoatNamed"],
    window=dict(),
    # The player's force here is a submarine and a loaned aircraft; the
    # aircraft going home is not the force being wiped out. The fatal on
    # Collins says what losing means.
    force_loss=False,
    role="patrol",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 120, 10
# The classify that writes the campaign variable is the stage's twin: same
# contact, same condition, and the objective it completes is hidden-free -
# it is the main objective's first half, scored once by the stage and
# recorded once by this resolver.
MISSION["objectives"].insert(1, ("Named", "Put a name on VICTOR for the record",
                                 "5,0,None"))
MISSION["resolve"]["Named"] = ("classify", "red_sub", 1, "SR02BoatNamed")
