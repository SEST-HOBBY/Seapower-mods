"""SR10 - Southern Line. The ice edge, 6 January 2029.

The southernmost mission, 375 NM from the nearest coastline the extract
knows. Intimidation, rules of engagement and identification with the
Seahawk as the only aviation: the group's command element is holding
station over the fishing fleet and everything red starts Tight. Fire first
and the group answers. The boat Beneath the South hunted is in the line
only if she got away; Empty Horizon's picture identifies the escorts from
the first minute.
"""
from campaign_data import U, F, S, HELO

MISSION = dict(
    code="SR10", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 10",
    group="core", num="10", key="Southern Line", place="The ice edge, 60 South",
    intro="The fisheries-protection group's command element at the ice edge, a Seahawk for "
          "aviation, and a rule of engagement that is the whole mission: "
          "identify the carrier, fire on nothing that has not fired.",
    special="No requisition before this operation, and the weather has "
            "grounded the Poseidons and the Triton: the Seahawk is your "
            "aviation. Everything in the group's line starts weapons tight. Fire "
            "first and it answers.",
    sender="Commodore Alex Mercer",
    intent=("The carrier is at the ice edge with a frigate, a corvette and "
            "the collector, holding station over the fishing fleet where "
            "the last voyages have to pass. Put a class and a name on the "
            "carrier and the collector, and pull back north to the withdrawal line. Do "
            "not fire on anything that has not fired. AKADEMIK FERSMAN is "
            "a research vessel today; the trawlers are trawlers. If VICTOR, "
            "the Akula we hunted on Christmas Eve, got away, she is in that line "
            "and she is the one thing here that has already fired at us."),
    date=(2029, 1, 6), time=(11, 0), sea=6, clouds="Overcast", wind="SW",
    difficulty=3, minutes=60, centre=(-60.0, 118.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE ICE EDGE, 60 South, midday. The protection group's command "
        "element has come south to the fishing fleet: the carrier, a "
        "frigate, a corvette, the research trawler NAN HAI 27, a Ka-31 "
        "over it all. It is holding station where every voyage to Casey "
        "must pass, to be seen there, and to be fired on first.\\n\\n"
        "The weather at Hobart has grounded the Poseidons and the Triton, "
        "and no field in the world reaches here for anything else. Your "
        "aviation is the Seahawk. AKADEMIK FERSMAN, VICTOR's tender at "
        "Christmas, is at the ice with the trawlers, a research vessel again; and if VICTOR "
        "survived Christmas Eve she is somewhere in this line.\\n\\n"
        "Identify the carrier and the collector by class and name, and "
        "pull back north to the withdrawal line. Everything red starts weapons tight. "
        "Fire on nothing that has not fired; a shot at the collector is the "
        "incident they came here to have."),
    forces="Your escort group with its Seahawk. Opposing, at the ice edge: "
           "Liaoning, a Type 054A, a Type 056A, the research trawler Nan Hai "
           "27, a Ka-31 up - and VICTOR, if she got away. Neutral: three "
           "factory trawlers, a research vessel, a whale.",
    objectives=[
        ("Identify", "Classify the carrier and the collector, then pull back "
                     "north to the withdrawal line", "35,-35,Fail,Main"),
        ("Restraint", "Do not fire on the collector", "10,-25,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-20,Complete"),
        ("Neutrals", "Harm no trawler, research vessel or whale", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="escort", min_units=1, objective="Identify",
                 after=dict(kind="classify", units=["group#1", "group#4"], min_units=2,
                            intel="The carrier is LIAONING, and the collector is "
                                  "the same Nan Hai 27 that shadowed the Storm Bay "
                                  "convoy on 6 December. The group has a name, a flagship "
                                  "and a face. Pull back north to the withdrawal line - and "
                                  "do not give them the shot they came for.")),
    fatal=[],
    neutral_objective="Neutrals",
    win="The escort is north of the withdrawal line with the carrier and the collector "
        "named, and nothing in the south fired first. The photographs are "
        "ours this time.",
    lose="The escort is gone at the ice edge, or the incident happened. "
         "Either way the group has what it came south for.",
    timeout="Sixty minutes and the escort is still at the ice edge with the "
            "carrier a contact and no name. The group will be there "
            "tomorrow; the last voyage will not.",
    stations={
        # The escort 40 NM north of the line; the command element holding
        # over the fleet on slow routes; the boat, if she lives, 30 NM west
        # closing; the trawlers, the research vessel and a whale inside the
        # picture. No field: nothing here can reach one.
        "escort": S(-59.70, 118.20, "Escort", heading=180),
        "flight": S(-59.72, 118.18, "Ship's flight", heading=180, alt=500),
        "group": S(-60.40, 118.30, "Command element", heading=90),
        "red_helo": S(-60.30, 118.50, "Ka-31 orbit", heading=90, alt=9000),
        "red_sub": S(-60.10, 117.60, "Contact VICTOR", heading=30),
        "fleet": S(-60.50, 118.80, "Factory trawlers", heading=270),
        "research": S(-60.60, 117.60, "Research vessel", heading=90),
        "whale": S(-59.95, 118.35, "Biologic", heading=180),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort", weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("red", "liaoning-type-001", "plan_type_001", "group", name="Liaoning",
          weapons="Tight", route=[(-60.40, 118.90, 0)], telegraph=2),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "group",
          name="Type 054A frigate", weapons="Tight",
          route=[(-60.40, 118.90, 0)], telegraph=2),
        U("red", "modern-plan-systems", "plan_type_056a", "group",
          name="Type 056A corvette", weapons="Tight",
          route=[(-60.40, 118.90, 0)], telegraph=2),
        U("red", "_vanilla", "wp_agi_okean", "group", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-60.40, 118.90, 0)], telegraph=2),
        # An AEW orbit that carries her out over the line: she is the
        # group's eye, and she looks at the escort.
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW",
          route=[(-60.00, 118.30, 9000), (-60.20, 118.80, 9000)], telegraph=2),
        # In the line only if Beneath the South did not put her on the bottom.
        U("red", "russian-submarines", "wp_ssn_akula", "red_sub", name="Contact VICTOR",
          depth="belowlayer", weapons="Tight", spawn_if=("SR07AkulaSunk", "IsFalse"),
          route=[(-59.85, 118.00, "belowlayer")], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 21",
          route=[(-60.40, 118.20, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 24",
          route=[(-60.60, 118.40, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 29",
          route=[(-60.30, 119.00, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_kommunist", "research",
          name="RV Akademik Fersman (research vessel)",
          route=[(-60.50, 118.20, 0)], telegraph=1),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic KILO",
          depth="shallow"),
    ],
    resolve={"Identify": "victory", "Neutrals": "neutral",
             "Restraint": ("spare", "group#4"),
             "Flagship": ("protect", "escort")},
    reveal_if=[dict(variable="SR05GroupClassified", units=["group#2", "group#3"],
                    level="Identify",
                    intel="Sentry 22's picture from Empty Horizon: the frigate "
                          "and the corvette in that line are the two she "
                          "classified on the eighteenth, and they are identified "
                          "on your plot from the start. The carrier and the "
                          "collector are not - that you still have to do.")],
    window=dict(flights=[HELO]),
    role="recon",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 0, 15
