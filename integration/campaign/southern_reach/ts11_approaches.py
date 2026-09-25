"""TS11 - Approaches. The western Tasman, 26 February 2029.

The second fleet action: contain what is left of the group off Sydney
while the last movement passes north-east. The flagship destroyer is the
objective that pays; the carrier is the one that changes Southern Cross.
Whichever optional priority was not held, that element is here.
"""
from campaign_data import U, F, S, HELO, RECON, CAP, STRIKE

MISSION = dict(
    code="TS11", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 11",
    group="core", num="11", key="Approaches", place="The western Tasman",
    intro=(
        "Hold the opposing group off while the relief transports pass north-east through the "
        "western Tasman. Secure the passage, engage the Type 052D command ship, and attack "
        "Liaoning if the opportunity permits."
    ),
    sender="Commodore Alex Mercer; Wing Commander Daniel Ward for the "
           "fighter cover and the strike",
    intent=((
        "Bring at least two of the three relief transports to the north-eastern handover. "
        "Engage the Type 052D command ship while protecting that movement; attack Liaoning if "
        "an opportunity permits. The carrier's confirmed loss removes its contribution to the "
        "relief-convoy interception on 2 March. The opposing force also depends on whether the "
        "Auckland and Adelaide detachments were contained. Coordinate the allocated aircraft "
        "without delaying a necessary defensive engagement."
    )),
    date=(2029, 2, 26), time=(11, 40), sea=4, clouds="Broken_2", wind="S",
    difficulty=5, minutes=90, centre=(-39.5, 151.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE WESTERN TASMAN, 39 South, late morning. The last movement - "
        "three transports with the vehicles and stores of New Zealand's "
        "relief detachment - is on 045 for New Zealand with the whole force, "
        "WEDGETAIL 05, and every aircraft it can task: the Seahawk, the "
        "Poseidon, East Sale's F-35As two hundred miles away, "
        "Williamtown's four hundred, and the Super Hornets and Growlers "
        "tasked to strike.\\n\\n"
        "The group is eighty miles south-east: LIAONING, the Type 052D "
        "that has commanded it since October, a frigate, three J-15s "
        "with anti-ship missiles and a J-15D, a Ka-31 and a Z-18F up. If "
        "Auckland's approaches were not held, the Type 056A and NAN HAI "
        "27 from the Hauraki Gulf have joined it; if Adelaide's were not, "
        "the Type 054A from Gulf St Vincent has too.\\n\\n"
        "Two of three transports into the box north-east. Sink the "
        "destroyer. Sink the carrier if you can. A coastal bulker, a "
        "trawler and the Sydney-Hobart service are in the box. Ninety "
        "minutes, and the strike goes when it is ready, not when the "
        "clock says."),
    forces=(
        "Your whole task group with its Seahawk, Poseidon, fighters and strike aircraft if "
        "assigned; Wedgetail 05. Three transports. Neutral: a bulker, a trawler, an airliner. "
        "Opposing: Liaoning, a Type 052D, a Type 054A, three J-15 with anti-ship missiles, a "
        "J-15D, a Ka-31, a Z-18F - and a Type 056A with Nan Hai 27, or a second Type 054A, or "
        "both, if Auckland's or Adelaide's approaches were not held."
    ),
    objectives=[
        ("Movement", "Two of three transports into the box north-east",
         "40,-40,Fail,Main"),
        ("Flagship", "Destroy the Type 052D", "20,-10,Fail"),
        ("Carrier", "Destroy Liaoning", "25,0,None"),
        ("Wedgetail", "Keep the Wedgetail flying", "10,-15,Complete"),
        ("Neutrals", "Harm no merchant, trawler or aircraft", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="lift", min_units=2, objective="Movement",
                 transit=14),
    fatal=[F("Movement", ["lift"], 2)],
    neutral_objective="Neutrals",
    win="Two transports in the box, and the ledger says whether the "
        "destroyer that commanded the group since October is on the "
        "bottom. What is left of "
        "the group turns for home, or waits for the relief convoy; the "
        "second of March will show which.",
    lose="Two transports lost in the western Tasman with the relief in "
         "them. The group holds the water and the relief convoy "
         "sails into it anyway.",
    timeout="Ninety minutes and the transports are still short of the box "
            "with the group between them and New Zealand. The movement "
            "turns back for Sydney and the relief waits.",
    stations={
        # The transports and escorts on 045; the cockpits and the Wedgetail
        # on the East Sale side; the group 80 NM south-east routed onto the
        # transports with its strike flight ahead; the reinforcing elements
        # closing from north and south, each only if its priority fell.
        "lift": S(-39.70, 150.70, "The last movement", heading=45),
        "escort": S(-39.60, 150.85, "Escort group", heading=45),
        "flight": S(-39.62, 150.83, "Ship's flight", heading=45, alt=500),
        "mpa": S(-39.90, 150.60, "Maritime patrol", heading=135, alt=12000),
        "cap": S(-39.30, 150.70, "Fighter cover", heading=135, alt=30000),
        "attack": S(-39.40, 150.30, "Strike", heading=135, alt=25000),
        "aew": S(-39.20, 150.40, "Wedgetail 05", heading=90, alt=32000),
        "red_cv": S(-40.40, 152.30, "Protection group", heading=300),
        "red_air": S(-40.10, 152.00, "Strike flight", heading=300, alt=25000),
        "red_helo": S(-40.30, 152.20, "Ka-31 orbit", heading=300, alt=9000),
        "red_dip": S(-40.00, 151.60, "Z-18F dip", heading=300, alt=1500),
        "red_north": S(-40.10, 152.60, "Northern element", heading=300),
        "red_south": S(-40.60, 151.80, "Southern element", heading=20),
        "bulker": S(-39.30, 151.60, "Coastal bulker", heading=200),
        "trawler": S(-39.85, 151.20, "Trawler", heading=100),
        "airliner": S(-39.00, 150.50, "Sydney-Hobart", heading=200, alt=35000),
        "williamtown": S(-32.795, 151.834, "RAAF Base Williamtown"),
        "east_sale": S(-38.099, 147.149, "RAAF Base East Sale"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          loadout="ASW", slot="Recon"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron2",
          slot="CAP"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron2",
          slot="CAP"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_fa-18f_blk3", "attack",
          squadron="Squadron8", slot="Attack"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_ea-18g", "attack",
          squadron="Squadron6", slot="Attack"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 05",
          alt=32000, weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_roro_a", "lift",
          name="MV Tasman Relief I (transport)", weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_jeparit", "lift",
          name="MV Tasman Relief II (transport)", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_freighter_a", "lift",
          name="MV Tasman Relief III (transport)"),
        U("red", "liaoning-type-001", "plan_type_001", "red_cv", name="Liaoning",
          route=[(-39.90, 151.30, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_052d_p3", "red_cv",
          name="Type 052D (the flagship)", route=[(-39.90, 151.30, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_cv",
          name="Type 054A frigate", route=[(-39.90, 151.30, 0)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 61", loadout="AntiShip",
          route=[(-39.70, 150.70, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 62", loadout="AntiShip",
          route=[(-39.70, 150.70, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 63", loadout="AntiShip",
          route=[(-39.70, 150.70, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_air",
          name="Flying Shark 64", loadout="AntiShip",
          route=[(-39.70, 150.70, 20000)], telegraph=3),
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW",
          route=[(-40.00, 151.70, 9000)], telegraph=2),
        U("red", "chinese-navy-plan", "plan_z-18f", "red_dip", name="Z-18F dip",
          alt=1500, loadout="ASW"),
        # The priorities: each element is here only if its approach was
        # not held. The spawns read the victory flags of TS10A and TS10B.
        U("red", "modern-plan-systems", "plan_type_056a", "red_north",
          name="Type 056A corvette (northern element)",
          spawn_if=("TS10ANorthHeld", "IsFalse"),
          route=[(-39.75, 151.30, 0)], telegraph=3),
        U("red", "_vanilla", "wp_agi_okean", "red_north",
          name="Research trawler Nan Hai 27", weapons="Hold",
          spawn_if=("TS10ANorthHeld", "IsFalse"),
          route=[(-39.75, 151.30, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_south",
          name="Type 054A frigate (southern element)",
          spawn_if=("TS10BSouthHeld", "IsFalse"),
          route=[(-39.80, 150.90, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Shoalhaven (Newcastle-Melbourne)",
          route=[(-40.50, 151.00, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_b", "trawler",
          name="Trawler Ulladulla Pride", route=[(-39.80, 151.70, 0)], telegraph=2),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airliner",
          name="Sydney-Hobart 1531", airway=(-42.84, 147.51)),  # Hobart
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_williamtown", "williamtown",
          name="RAAF Base Williamtown", nation="australia", weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_east_sale", "east_sale",
          name="RAAF Base East Sale", nation="australia", weapons="Hold"),
    ],
    resolve={"Movement": "victory", "Neutrals": "neutral",
             "Flagship": ("destroy", "red_cv#2", 1),
             "Carrier": ("destroy", "red_cv#1", 1),
             "Wedgetail": ("protect", "aew")},
    declares=["TS11CarrierSunk"],
    flags=[dict(name="TS11CarrierSunk", units=["red_cv#1"],
                intel=(
                    "DAMAGE REPORT | LIAONING confirmed lost. Its contribution to the next "
                    "convoy interception is removed from the air threat assessment. Surface "
                    "ships and submarines remain threats; maintain the escort screen."
                ))],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "ran_opv_arafura",
                       "usn_mh-60r", "usn_p8", "raaf_mq-4c_triton", "E7A_Wedgetail",
                       "raaf_f-35a", "usn_fa-18f_blk3", "usn_ea-18g"],
                flights=[HELO, RECON, CAP, STRIKE],
                situation=(
                    "Sydney can repair, rearm and reinforce the force before Approaches. This "
                    "is the final ammunition resupply before Southern Cross; repairs and "
                    "replacement allocations remain available for that last passage."
                )),
    role="fleet",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 45, 15
