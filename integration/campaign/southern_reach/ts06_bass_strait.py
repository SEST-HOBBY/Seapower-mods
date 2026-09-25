"""TS06 - Bass Strait. 8 February 2029.

The densest surface picture of the chapter: ferries, a Geelong-bound tanker,
rig supply boats, three platforms, and among them a merchant radiating a
frigate's radar, a Kilo inside the strait, and a corvette coming in from
the east. The tanker to the western line; the platforms untouched. East
Sale's fighters are seventy-five miles away.
"""
from campaign_data import U, F, S, HELO, RECON, CAP

MISSION = dict(
    code="TS06", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 6",
    group="core", num="06", key="Bass Strait", place="Bass Strait",
    intro="Ferries, a tanker, three platforms and a merchant that radiates "
          "like a frigate, with a Kilo inside the strait and a corvette "
          "coming in from the east. Get the tanker to the western line and "
          "touch nothing that is not a warship.",
    sender="Commodore Alex Mercer; Wing Commander Daniel Ward for East Sale",
    intent=("Bass Strait is the shipping lane and the gas field and the "
            "ferries, and today it is also a Kilo, a corvette, and a "
            "merchant that has been radiating a frigate's search radar "
            "since dawn to see what we do about it. Get BASS PROVIDER to "
            "the western line. Do not put a missile into a merchant "
            "because it sounds like a frigate, and do not put one within a "
            "mile of a platform. The corvette is a warship and the Kilo is "
            "a warship; everything else is somebody going to work. East "
            "Sale's fighters are seventy-five miles away and they are "
            "yours."),
    date=(2029, 2, 8), time=(7, 45), sea=3, clouds="Broken_2", wind="W",
    difficulty=3, minutes=70, centre=(-39.3, 147.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "BASS STRAIT, morning. MT BASS PROVIDER, Geelong-bound with a "
        "cargo Melbourne has been waiting a fortnight for, is thirty miles "
        "east of Wilsons Promontory with your force. The strait around "
        "her is its ordinary self: two Devonport ferries on the crossing, "
        "a bulker westbound, two supply boats running out to the Gippsland "
        "platforms, three of which are on your plot some sixty miles "
        "north-east, and the Melbourne-Hobart service overhead.\\n\\n"
        "MV SOUTHERN COMPLIANCE, an Austral Meridian Services merchant, "
        "has been radiating a frigate's search radar since dawn: she is "
        "a decoy and a provocation, and she is a merchant. A Kilo is "
        "inside the strait somewhere south-west of the tanker's track. A "
        "Type 056A with a Z-9 up is coming in from the east, south of the "
        "platforms.\\n\\n"
        "The tanker to the western line. The platforms are not to be "
        "touched - a missile that finds a rig instead of a corvette ends "
        "the campaign in a courtroom. East Sale's F-35As are available "
        "for fighter cover. The Kilo has not fired. Classify her if you can; sink her "
        "if she does."),
    forces="Your task group with its Seahawk, Poseidon and East Sale "
           "fighters if requisitioned; the tanker Bass "
           "Provider. Neutral: two Devonport ferries, a bulker, two rig "
           "supply boats, three platforms, an airliner. Opposing: MV "
           "Southern Compliance radiating a frigate's radar, one Kilo, one "
           "Type 056A with a Z-9.",
    objectives=[
        ("Tanker", "MT Bass Provider reaches the western line", "35,-35,Fail,Main"),
        ("Platforms", "The Gippsland platforms are not to be touched",
         "15,-40,Complete"),
        ("Boat", "Classify the Kilo", "15,0,None"),
        ("Traffic", "Harm no ferry, merchant, supply boat or aircraft",
         "0,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="tanker", min_units=1, objective="Tanker",
                 transit=12),
    fatal=[F("Tanker", ["tanker"])],
    neutral_objective="Traffic",
    win="Bass Provider is west of the line with the ferries still "
        "crossing and every platform where it was. The corvette went home "
        "past the rigs it was hoping you would hit.",
    lose="The tanker is lost in Bass Strait, or a platform is, and "
         "Melbourne's fortnight becomes a month.",
    timeout="Seventy minutes and the tanker is still east of the line "
            "with a Kilo somewhere under her track. She anchors off "
            "Wilsons Promontory and waits for tomorrow.",
    stations={
        # The tanker and escort 30 NM east of the Promontory (16 NM off the Kent Group) on 250; the Kilo
        # 17 NM south-west across the track; the corvette 30 NM east
        # coming in past the platforms; the decoy 15 NM south-east on a
        # slow westbound beat; the ferries on the real crossing; the supply
        # boats running out to the rigs; East Sale 75 NM north.
        "tanker": S(-39.25, 147.10, "Bass Provider", heading=250),
        "escort": S(-39.30, 147.05, "Escort group", heading=250),
        "flight": S(-39.32, 147.03, "Ship's flight", heading=250, alt=500),
        "mpa": S(-39.55, 146.75, "Maritime patrol", heading=270, alt=10000),
        "cap": S(-39.10, 146.90, "Fighter cover", heading=90, alt=25000),
        "red_decoy": S(-39.55, 147.30, "Southern Compliance", heading=270),
        "red_sub": S(-39.45, 146.75, "Contact KILO", heading=90),
        "red_056": S(-39.20, 147.70, "Type 056A", heading=270),
        "red_dip": S(-39.25, 147.55, "Z-9 dip", heading=270, alt=1500),
        "ferry1": S(-39.60, 146.60, "Spirit of the Strait (Devonport-Geelong)", heading=340),
        "ferry2": S(-39.00, 146.20, "Spirit of the Strait (Geelong-Devonport)", heading=160),
        "bulker": S(-39.60, 147.55, "Bulker", heading=270),
        "supply": S(-38.90, 147.60, "Rig supply boats", heading=60),
        "rig1": S(-38.55, 148.20, "Platform"),
        "rig2": S(-38.60, 147.85, "Platform"),
        "rig3": S(-38.45, 148.05, "Platform"),
        "airliner": S(-39.00, 146.80, "Melbourne-Hobart", heading=160, alt=25000),
        "home": S(-38.099, 147.149, "RAAF Base East Sale"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=10000,
          loadout="ASW", slot="Recon"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron1",
          slot="CAP"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap", squadron="Squadron1",
          slot="CAP"),
        U("blue", "_vanilla", "civ_ms_ritina", "tanker", name="MT Bass Provider"),
        U("red", "_vanilla", "wp_ms_mercur_decoy", "red_decoy",
          name="MV Southern Compliance (AMS merchant, decoy)", weapons="Hold",
          loadout="KrivakI",
          route=[(-39.50, 146.50, 0)], telegraph=2),
        U("red", "chinese-navy-plan", "plan_ss_kilo", "red_sub", name="Contact KILO",
          depth="belowlayer", weapons="Tight",
          route=[(-39.38, 146.85, "belowlayer")], telegraph=2),
        U("red", "modern-plan-systems", "plan_type_056a", "red_056",
          name="Type 056A corvette", route=[(-39.30, 147.20, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_z-9c", "red_dip", name="Z-9 dip",
          alt=1500, loadout="ASWKiller"),
        U("neutral", "_vanilla", "civ_ms_roro_b", "ferry1",
          name="Spirit of the Strait I (Devonport-Geelong)",
          route=[(-38.60, 144.90, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_roro_b", "ferry2",
          name="Spirit of the Strait II (Geelong-Devonport)",
          route=[(-40.60, 146.20, 0), (-41.10, 146.40, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Corner Inlet (Port Kembla-Adelaide)",
          route=[(-39.40, 145.80, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "supply",
          name="Supply boat Lakes Entrance", route=[(-38.60, 147.85, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_b", "supply",
          name="Supply boat Ninety Mile", route=[(-38.55, 148.20, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_spar_rig", "rig1", name="Platform Kingfish A",
          snap="sea"),
        U("neutral", "_vanilla", "civ_spar_rig", "rig2", name="Platform Marlin",
          snap="sea"),
        U("neutral", "_vanilla", "civ_spar_rig", "rig3", name="Platform Kingfish B",
          snap="sea"),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airliner",
          name="Melbourne-Hobart 1502", airway=(-42.84, 147.51)),  # Hobart
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_east_sale", "home",
          name="RAAF Base East Sale", nation="australia", weapons="Hold"),
    ],
    resolve={"Tanker": "victory", "Traffic": "neutral",
             "Platforms": ("spare", "rig1", "rig2", "rig3"),
             "Boat": ("classify", "red_sub", 1),
             "Flagship": ("protect", "escort")},
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "ran_opv_arafura",
                       "usn_mh-60r", "usn_p8", "raaf_mq-4c_triton", "E7A_Wedgetail",
                       "raaf_f-35a", "usn_fa-18f_blk3", "usn_ea-18g"],
                flights=[HELO, RECON, CAP],
                situation="Melbourne, after Under the Tasman. Requisition, "
                          "repair and rearm before Bass Strait. The next window "
                          "is Sydney, before Southern Air Bridge, when "
                          "Williamtown's ground crews first ready aircraft for you."),
    role="escort",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 250, 10
