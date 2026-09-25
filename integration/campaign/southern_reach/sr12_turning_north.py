"""SR12 - Turning North. The Tasman approaches, 14 January 2029.

The group transits north-east into the Tasman and the task group shadows it
out of the south, naming every hull in the network without starting the
Tasman war. The first fighter cover of the campaign, out of East Sale; the
classification is what Home Waters and Tasman Crossing read.
"""
from campaign_data import U, F, S, HELO, RECON, CAP

MISSION = dict(
    code="SR12", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 12",
    group="core", num="12", key="Turning North", place="The Tasman approaches",
    intro="The fisheries-protection group turns north into the Tasman with "
          "its carrier, its replenishment ship and its collector in company. Shadow it, name every hull, "
          "and do not start the war it is going north to have.",
    sender="Commodore Alex Mercer",
    intent=("The group is going north into the Tasman and it is not going "
            "home. Shadow it out of the south and put a class and a name on "
            "every hull in the network - the carrier, the replenishment "
            "ship, the collector - so that Sydney and Wellington know what "
            "is coming before it arrives. Fire on nothing. East Sale's "
            "fighters reach this water for the first time since the group arrived in October; "
            "they are cover, not a strike. Hold the shadowing line and come "
            "home to Hobart."),
    date=(2029, 1, 14), time=(9, 20), sea=4, clouds="Scattered_2", wind="SW",
    difficulty=3, minutes=70, centre=(-40.5, 151.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE TASMAN APPROACHES, morning. The protection group is fifty miles "
        "north-east of you, transiting at fourteen knots: LIAONING, a "
        "frigate, a corvette, a replenishment ship, the research trawler "
        "NAN HAI 27 and the Russian research vessel AKADEMIK FERSMAN, all in company, all "
        "going the same way. The fishing fleet it came to protect has been "
        "left to fish.\\n\\n"
        "You have what came out of the south, WEDGETAIL 05 out of East Sale, "
        "and for the first time since the group arrived in October a fighter that can reach the "
        "water you are in. Coastal traffic and the Melbourne-Auckland "
        "service are in the same box.\\n\\n"
        "Shadow the group. Classify the carrier, the replenishment ship and "
        "the collector. Hold the shadowing line behind them. Everything red "
        "is weapons tight and so are you: nobody in this box fires first, "
        "and the day that changes it will be in the Tasman, not here."),
    forces="Your task group with its Seahawk; your Poseidon and F-35As, if "
           "requisitioned, and Wedgetail 05, all out of East Sale. Neutral: a coastal "
           "bulker, a trawler, an airliner. Opposing, transiting north-east: "
           "Liaoning, a Type 054A, a Type 056A, a replenishment ship, the "
           "research trawler Nan Hai 27, the Russian research vessel, a "
           "Ka-31 up.",
    objectives=[
        ("Network", "Classify the carrier, the replenishment ship and the "
                    "collector", "25,-25,Fail"),
        ("Shadow", "Then hold the shadowing line behind the group",
         "15,-20,Fail,Main"),
        ("Restraint", "Fire on nothing: shadow, do not start the Tasman war",
         "15,-35,Complete"),
        ("Wedgetail", "Keep the Wedgetail flying", "10,-15,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
        ("Neutrals", "Harm no merchant, trawler or aircraft", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="escort", min_units=1, objective="Shadow",
                 after=dict(kind="classify", units=["network#1", "network#4", "network#5"],
                            min_units=3,
                            intel="The network has names: LIAONING, a "
                                  "Qiongsha-class replenishment ship, and NAN "
                                  "HAI 27 - the collector that shadowed the Storm Bay "
                                  "convoy on 6 December. Sydney and Wellington have the "
                                  "picture. Hold the shadowing line behind them.")),
    fatal=[],
    neutral_objective="Neutrals",
    win="The group is in the Tasman with every hull in its network named, "
        "and nobody fired. The ledger closes the south and opens the north.",
    lose="The escort is gone in the Tasman approaches, or the war started "
         "here. Either way the fight for the Tasman opens on the group's terms.",
    timeout="Seventy minutes and the group is over the horizon with half "
            "its network unnamed. Sydney meets it without a picture.",
    stations={
        # The escort 50 NM south-west of the network; the network on 040 at
        # fourteen knots; the fighters' cockpits and the Wedgetail on the
        # East Sale side; neutrals on routes across the box.
        "escort": S(-40.60, 151.20, "Escort group", heading=60),
        "flight": S(-40.62, 151.18, "Ship's flight", heading=60, alt=500),
        "mpa": S(-40.20, 151.90, "Maritime patrol", heading=60, alt=12000),
        "cap": S(-40.40, 150.80, "Fighter cover", heading=60, alt=30000),
        "aew": S(-40.90, 150.60, "Wedgetail 05", heading=90, alt=32000),
        "network": S(-40.20, 152.20, "The network", heading=40),
        "red_helo": S(-40.10, 152.40, "Ka-31 orbit", heading=40, alt=9000),
        "bulker": S(-40.80, 151.80, "Coastal bulker", heading=200),
        "trawler": S(-40.35, 151.55, "Trawler", heading=120),
        "airliner": S(-40.30, 151.00, "Melbourne-Auckland service", heading=90, alt=35000),
        "home": S(-38.099, 147.149, "RAAF Base East Sale"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort", weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron1",
          weapons="Tight", slot="CAP"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron1",
          weapons="Tight", slot="CAP"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 05",
          alt=32000, weapons="Hold"),
        U("red", "liaoning-type-001", "plan_type_001", "network", name="Liaoning",
          weapons="Tight", route=[(-39.60, 152.90, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "network",
          name="Type 054A frigate", weapons="Tight",
          route=[(-39.60, 152.90, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_056a", "network",
          name="Type 056A corvette", weapons="Tight",
          route=[(-39.60, 152.90, 0)], telegraph=3),
        U("red", "_vanilla", "plan_ap_qiongsha", "network",
          name="Qiongsha-class supply ship", weapons="Hold",
          route=[(-39.60, 152.90, 0)], telegraph=3),
        U("red", "_vanilla", "wp_agi_okean", "network", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-39.60, 152.90, 0)], telegraph=3),
        U("red", "_vanilla", "civ_ms_kommunist", "network",
          name="RV Akademik Fersman (research vessel)", weapons="Hold",
          route=[(-39.60, 152.90, 0)], telegraph=3),
        # An AEW orbit between the network and the shadowing line.
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW",
          route=[(-40.40, 151.70, 9000), (-39.90, 152.60, 9000)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Gippsland Trader (Newcastle-Melbourne)",
          route=[(-41.50, 151.20, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_b", "trawler",
          name="Trawler Eden Star", route=[(-40.50, 152.00, 0)], telegraph=2),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Melbourne-Auckland 402", airway=(-37.01, 174.79)),  # Auckland
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_east_sale", "home",
          name="RAAF Base East Sale", nation="australia", weapons="Hold"),
    ],
    resolve={"Shadow": "victory", "Neutrals": "neutral",
             "Network": ("classify", ["network#1", "network#4", "network#5"], 3,
                         "SR12NetworkNamed"),
             "Restraint": ("spare", "network", "red_helo"),
             "Wedgetail": ("protect", "aew"),
             "Flagship": ("protect", "escort")},
    declares=["SR12NetworkNamed"],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "usn_mh-60r", "usn_p8",
                       "raaf_mq-4c_triton", "E7A_Wedgetail", "raaf_f-35a"],
                flights=[HELO, RECON, CAP],
                situation="Hobart, after the last voyage. Requisition, repair "
                          "and rearm before Turning North - and the F-35A is "
                          "released to the task group, because East Sale's fighters reach the Tasman "
                          "approaches. The next window is Sydney, before Home "
                          "Waters."),
    role="recon",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 40, 15
