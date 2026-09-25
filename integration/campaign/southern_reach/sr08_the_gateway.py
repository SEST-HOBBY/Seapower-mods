"""SR08 - The Gateway. Christchurch approaches, 28 December 2028.

New Zealand's Antarctic gateway: a US Antarctic Program cargo ship and a
tanker into Lyttelton south-west across Pegasus Bay, with a corvette closing to
"inspect" the tanker and a New Zealand Poseidon overhead. No RNZN hull is
placed - Commander Brand's signal says where they are - and the New Zealand
contribution is the aircraft, the field and the port.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="SR08", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 8",
    group="core", num="08", key="The Gateway", place="Christchurch approaches",
    intro="Two gateway ships into Lyttelton south-west across Pegasus Bay, a corvette "
          "that wants to inspect the tanker, and a New Zealand Poseidon "
          "overhead saying no in two languages.",
    sender="Commodore Alex Mercer; Commander Tessa Brand, RNZN, for Lyttelton",
    intent=("POLAR GIANT and CANTERBURY SPIRIT into the Lyttelton approach, "
            "both of them. The corvette to the south-east has been asking "
            "tankers for their compliance paperwork since Christmas; today it "
            "will try to put a boat on one, and it may not. Put a class and a "
            "name on it for the record. Your weapons are tight and so are "
            "its: nobody has fired at a ship in New Zealand's waters yet, and "
            "the day that starts, it will not be an Australian frigate that "
            "started it. Lyttelton's traffic is Lyttelton's; the Chatham "
            "freighter and the pilot launch are not yours to move."),
    date=(2028, 12, 28), time=(15, 40), sea=3, clouds="Scattered_2", wind="NE",
    difficulty=2, minutes=65, centre=(-43.7, 173.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "CHRISTCHURCH APPROACHES, afternoon. The gateway traffic for the "
        "American programme's summer is coming into Lyttelton: POLAR GIANT "
        "with McMurdo's cargo and CANTERBURY SPIRIT with its fuel, both "
        "in Pegasus Bay and both making twelve knots south-west across Pegasus Bay "
        "to the pilot station.\\n\\n"
        "A corvette flying the protection flag has been working the "
        "Canterbury coast for four days and has asked three tankers for "
        "their environmental compliance certificates. It is south-east of "
        "the peninsula with its helicopter up, and the research trawler "
        "NAN HAI 27 is off Akaroa. KIWI 05 is overhead out of Christchurch "
        "and stays overhead; the Chatham freighter, the pilot launch, two "
        "trawlers and the afternoon Sydney flight are in the same water and "
        "sky.\\n\\n"
        "Walk both ships into the Lyttelton approach. Classify the corvette. "
        "Weapons tight: nobody fires first in this bay, and if the corvette "
        "does, you answer it and Wellington answers everything else."),
    forces="Your escort group with its Seahawk and Poseidon, out of "
           "Christchurch. One RNZAF P-8A on a national allocation. Two "
           "gateway ships. Neutral: the Chatham freighter, the pilot launch, "
           "two trawlers, an airliner. Opposing: a Type 056A corvette with "
           "a Z-9, the research trawler Nan Hai 27.",
    objectives=[
        ("Gateway", "Bring POLAR GIANT and CANTERBURY SPIRIT into the "
                    "Lyttelton approach", "35,-35,Fail,Main"),
        ("Corvette", "Classify the inspecting corvette", "15,0,None"),
        ("Traffic", "Harm no freighter, launch, trawler or aircraft", "0,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    # Both hulls into the approach: the box is authored on water off the
    # Heads, two miles from the coast, and solved for nothing.
    victory=dict(kind="arrive", station="gateway", min_units=2, objective="Gateway",
                 at=(-43.55, 172.90), radius=6, transit=12),
    fatal=[F("Gateway", ["gateway"], 1)],
    neutral_objective="Traffic",
    win="Both ships are at the pilot station with Lyttelton's tugs coming "
        "out, and the corvette has a class, a name and a recording of itself "
        "asking a tanker for a certificate. Brand: 'That is the gateway. It "
        "stays open.'",
    lose="A gateway ship is lost in New Zealand's front yard and the "
         "American programme's summer goes to Hobart. Wellington will say "
         "what it says.",
    timeout="Sixty-five minutes and the ships are still short of the Heads "
            "with the corvette between them and the pilot. The gateway is "
            "a question again.",
    stations={
        # Pegasus Bay to the Heads: the gateway ships 14 NM north-east of
        # the approach, the escort six miles off them; the corvette 30 NM
        # south-east routed onto the tanker; the collector off Akaroa; the
        # traffic on routes through the picture.
        "gateway": S(-43.40, 173.18, "Gateway ships", heading=210),
        "escort": S(-43.45, 173.30, "Escort", heading=210),
        "flight": S(-43.47, 173.28, "Ship's flight", heading=210, alt=500),
        "mpa": S(-43.90, 173.90, "Maritime patrol", heading=300, alt=10000),
        "kiwi": S(-43.55, 173.70, "Kiwi 05", heading=250, alt=8000),
        "corvette": S(-43.75, 173.70, "Inspecting corvette", heading=300),
        "red_helo": S(-43.72, 173.62, "Z-9", heading=300, alt=1500),
        "shadow": S(-43.95, 173.30, "Research trawler", heading=20),
        "freighter": S(-43.55, 173.45, "Chatham freighter", heading=90),
        "launch": S(-43.52, 173.12, "Pilot launch", heading=30),
        "trawlers": S(-43.50, 173.65, "Trawlers", heading=150),
        "airliner": S(-43.50, 173.00, "Sydney flight", heading=300, alt=20000),
        "field": S(-43.489, 172.532, "Christchurch International"),
        "home": S(-40.206, 175.388, "RNZAF Base Ohakea"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=10000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("blue", "p-8-poseidon", "usn_p8", "kiwi", squadron="Squadron6",
          name="Kiwi 05", alt=8000, weapons="Tight", loadout="ASW"),
        U("blue", "re-power-resupply", "civ_ms_amra", "gateway",
          name="MV Polar Giant (US Antarctic Program cargo)"),
        U("blue", "_vanilla", "civ_ms_ritina", "gateway", name="MT Canterbury Spirit"),
        U("red", "modern-plan-systems", "plan_type_056a", "corvette",
          name="Fisheries protection corvette", weapons="Tight",
          route=[(-43.45, 173.25, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_z-9c", "red_helo", name="Z-9 inspect",
          alt=1500, weapons="Tight", loadout="ASWKiller"),
        U("red", "_vanilla", "wp_agi_okean", "shadow", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-43.70, 173.40, 0)], telegraph=2),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "freighter",
          name="MV Chatham Trader (Lyttelton-Waitangi)",
          route=[(-43.60, 174.20, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "launch",
          name="Lyttelton pilot launch", route=[(-43.58, 173.05, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "trawlers",
          name="Trawler Pegasus (Lyttelton)", route=[(-43.30, 173.80, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_b", "trawlers",
          name="Trawler Waimakariri", route=[(-43.65, 174.00, 0)], telegraph=2),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airliner",
          name="Christchurch-Sydney 731"),
        U("blue", "_vanilla", "airfield_small_1", "field",
          name="Christchurch International (Antarctic gateway, RNZAF/RAAF detachment)",
          nation="New Zealand", weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_rnzaf_ohakea", "home",
          name="RNZAF Base Ohakea", nation="New Zealand", weapons="Hold"),
    ],
    resolve={"Gateway": "victory", "Traffic": "neutral",
             "Corvette": ("classify", "corvette", 1, "SR08CorvetteNamed"),
             "Flagship": ("protect", "escort")},
    declares=["SR08CorvetteNamed"],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "usn_mh-60r", "usn_p8",
                       "raaf_mq-4c_triton", "E7A_Wedgetail"],
                flights=[HELO, RECON],
                situation="Lyttelton. Requisition, repair and rearm before The "
                          "Gateway; the Poseidon recovers at Christchurch. The "
                          "next window is at Hobart, before Cold Route - and "
                          "Cold Route sails the whole force."),
    role="escort",
)
