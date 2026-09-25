"""SR09 - Cold Route. South of Australia, 2 January 2029.

The January voyage south as a convoy action: five critical hulls, the whole
owned force, a Wedgetail and a New Zealand Poseidon with no fighter within
reach, against the protection group's carrier air, its escorts and a
nuclear boat ahead of the track. The fleet action of chapter A. The tanker's
loss is what Last Ship South reads; holding the route is what its rearm is
paid with.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="SR09", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 9",
    group="core", num="09", key="Cold Route", place="South of Australia",
    intro="The January voyage to Casey: five hulls, the whole force, a Wedgetail "
          "and no fighter within a thousand miles, against Liaoning's air wing "
          "and a nuclear boat across the track.",
    sender="Commodore Alex Mercer; Wing Commander Daniel Ward for the air picture",
    intent=("Four of five through, SOUTHERN ENDEAVOUR among them - she is "
            "Casey's second lift and there is no third. The carrier's "
            "aircraft will come for the convoy and the destroyer is the air "
            "defence; Wedgetail sees them come and cannot stop them. The "
            "boat ahead of the track is the one that keeps the destroyer "
            "looking the wrong way. Keep the tanker alive if you can - the "
            "last voyage south, on the tenth, sails on what she carries - and keep the trawlers "
            "and the bulker out of your missiles' way."),
    date=(2029, 1, 2), time=(8, 30), sea=5, clouds="Broken_3", wind="W",
    difficulty=4, minutes=90, centre=(-48.5, 137.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "SOUTH OF AUSTRALIA, 48 South, morning. The January voyage is two "
        "days out of Hobart: SOUTHERN ENDEAVOUR with Casey's second lift, "
        "DERWENT SPIRIT with a new plate and the winter's fuel, CORAL "
        "PIONEER, AURORA TRADER and DAVIS PROVIDER. Twelve knots, "
        "south-west, and the whole force with them.\\n\\n"
        "The protection group's carrier, LIAONING, is a hundred and fifty miles "
        "south-east with two frigates and a corvette, and its air wing "
        "flew over the fishing fleet for the cameras on New Year's Eve. "
        "Today it flies for the convoy. ROMEO, a Type 093B nuclear boat the "
        "group calls a fisheries survey asset, is somewhere ahead of the track. WEDGETAIL "
        "05 and KIWI 05 are up out of Edinburgh; no fighter in Australia "
        "reaches this water and comes home, and the destroyer's magazine is "
        "the air defence.\\n\\n"
        "Four of five into the handover box, Southern Endeavour among them. "
        "The trawlers and the Hobart-bound bulker are not part of this and "
        "will not move out of your way."),
    forces="Your whole task group with its Seahawk and Poseidon, Wedgetail "
           "05 and Kiwi 05 out of Edinburgh. Five convoy hulls. Neutral: two "
           "factory trawlers, a bulker. Opposing: Liaoning with two Type 054A "
           "and a Type 056A, a J-15 strike flight of three, a Ka-31 and a "
           "Z-18F up, and a Type 093B ahead of the track.",
    objectives=[
        ("Convoy", "Four of five convoy hulls, Southern Endeavour among them, "
                   "into the handover box", "40,-40,Fail,Main"),
        ("Tanker", "MT Derwent Spirit must survive", "15,-20,Complete"),
        ("Wedgetail", "Keep the Wedgetail flying", "10,-15,Complete"),
        ("Neutrals", "Harm no trawler or merchant", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", min_units=4, objective="Convoy",
                 transit=12, sets="SR09ColdRouteHeld",
                 also=[dict(units=["convoy#1"], min_units=1)]),
    fatal=[F("Convoy", ["convoy#1"]), F("Convoy", ["convoy"], 2)],
    neutral_objective="Neutrals",
    win="Four hulls in the box and Southern Endeavour among them. The "
        "carrier's air wing spent its morning and the boat spent its "
        "chance. Dr Marsh, the voyage leader, from Southern Endeavour's bridge: 'We saw the missiles. "
        "We saw yours too.'",
    lose="The voyage is broken south of Australia with the stations' "
         "winter in it. Casey gets what the first lift left.",
    timeout="Ninety minutes and the convoy is still short of the box with "
            "the carrier's second strike forming. The route is theirs "
            "today.",
    stations={
        # Convoy and escorts on 240; the carrier group 150 NM south-east
        # with its strike flight routed onto the convoy and its AEW up; the
        # boat 40 NM south-west across the track; neutrals on routes
        # through the picture; the fields far to the north.
        "convoy": S(-48.30, 137.30, "January convoy", heading=240),
        "escort": S(-48.35, 137.45, "Escort group", heading=240),
        "flight": S(-48.37, 137.43, "Ship's flight", heading=240, alt=500),
        "mpa": S(-48.80, 137.00, "Maritime patrol", heading=240, alt=12000),
        "aew": S(-48.00, 137.80, "Wedgetail 05", heading=270, alt=32000),
        "kiwi": S(-48.20, 136.30, "Kiwi 05", heading=200, alt=10000),
        "red_cv": S(-50.60, 138.60, "Carrier group", heading=300),
        "red_air": S(-50.20, 138.40, "Strike flight", heading=300, alt=25000),
        "red_helo": S(-50.40, 138.50, "Ka-31 orbit", heading=300, alt=9000),
        "red_dip": S(-49.60, 138.00, "Z-18F dip", heading=300, alt=1500),
        "red_sub": S(-48.70, 136.50, "Contact ROMEO", heading=60),
        "fleet": S(-48.90, 137.60, "Factory trawlers", heading=270),
        "bulker": S(-48.00, 136.60, "Hobart-bound bulker", heading=60),
        "home": S(-34.703, 138.622, "RAAF Base Edinburgh"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          loadout="ASW", slot="Recon"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 05",
          alt=32000, weapons="Hold"),
        U("blue", "p-8-poseidon", "usn_p8", "kiwi", squadron="Squadron6",
          name="Kiwi 05", alt=10000, weapons="Tight", loadout="ASW"),
        U("blue", "re-power-resupply", "civ_ms_freighter_d", "convoy",
          name="RSV Southern Endeavour"),
        U("blue", "re-power-resupply", "civ_ms_sealift_pacific", "convoy",
          name="MT Derwent Spirit"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "anl_ms_bulk", "convoy",
          name="MV Aurora Trader", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_andizhan", "convoy",
          name="MV Davis Provider"),
        U("red", "liaoning-type-001", "plan_type_001", "red_cv", name="Liaoning",
          route=[(-49.80, 137.80, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_cv",
          name="Type 054A frigate", route=[(-49.80, 137.80, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_cv",
          name="Type 054A frigate", route=[(-49.80, 137.80, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_056a", "red_cv",
          name="Type 056A corvette", route=[(-49.80, 137.80, 0)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 11", loadout="AntiShip",
          route=[(-48.30, 137.30, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15", "red_air",
          name="Flying Shark 12", loadout="AntiShip",
          route=[(-48.30, 137.30, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_air",
          name="Flying Shark 13", loadout="AntiShip",
          route=[(-48.30, 137.30, 20000)], telegraph=3),
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW"),
        U("red", "chinese-navy-plan", "plan_z-18f", "red_dip", name="Z-18F dip",
          alt=1500, loadout="ASW"),
        U("red", "plan-submarines", "plan_ssn_type_093b", "red_sub", name="Contact ROMEO",
          depth="belowlayer", route=[(-48.40, 137.00, "belowlayer")], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 21",
          route=[(-48.70, 137.20, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 29",
          route=[(-49.00, 137.00, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker", name="MV Cape Grim (Hobart-bound)",
          route=[(-47.50, 137.40, 0)], telegraph=3),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_edinburgh", "home",
          name="RAAF Base Edinburgh", nation="australia", weapons="Hold"),
    ],
    resolve={"Convoy": "victory", "Neutrals": "neutral",
             "Tanker": ("protect", "convoy#2"),
             "Wedgetail": ("protect", "aew")},
    declares=["SR09TankerLost", "SR09ColdRouteHeld"],
    support_loss=[dict(asset="Derwent Spirit", units=["convoy#2"], objective="Tanker",
                       sets="SR09TankerLost",
                       intel="DERWENT SPIRIT is gone with the winter's fuel in "
                             "her. The last voyage south sails without a tanker, and "
                             "Casey's winter is whatever the first lift put "
                             "ashore.  - Mercer")],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "usn_mh-60r", "usn_p8",
                       "raaf_mq-4c_triton", "E7A_Wedgetail"],
                flights=[HELO, RECON],
                situation="Hobart, before the January voyage. Requisition, "
                          "repair and rearm: Cold Route sails the whole force and "
                          "there is no requisition after it until Turning North - "
                          "none before Southern Line, and Last Ship South is "
                          "rearmed only if this convoy gets through."),
    role="fleet",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 240, 15
