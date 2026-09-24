"""TS01 - Home Waters. The Fiordland approaches, 22 January 2029.

The Tasman chapter opens in New Zealand's water: the task group, an
Arafura now on sale, and a New Zealand Poseidon out of Invercargill, in the
densest traffic of the campaign - Milford cruise ships, Bluff cray boats, a
fisheries patrol - with the AMS tender establishing itself off Puysegur, the
collector Turning North named somewhere behind it, and a conventional boat
to the south-west that is not routed at anyone. Classify the tender, hold
the patrol line, fire on nothing. What is named here is on the plot at the
Chatham rendezvous.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="TS01", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 1",
    group="core", num="01", key="Home Waters", place="The Fiordland approaches",
    intro="New Zealand's water, the busiest box of the campaign, and a "
          "tender off Puysegur that calls itself a compliance vessel. Put "
          "a name on it, hold the patrol line, and harm nothing.",
    sender="Commodore Alex Mercer; Commander Hana Rewi, RNZN, for the New "
           "Zealand picture",
    intent=("This is New Zealand's water and we are here at their request, "
            "which means every cray boat and cruise ship in the box is "
            "somebody's constituent. The Australian Maritime Services tender "
            "has been off Puysegur for three days telling fishing masters "
            "which grounds are closed. Put a class and a name on her, hold "
            "the patrol line south-west of her, and leave the boat to the "
            "south-west alone unless it comes to you. Nothing here fires "
            "first. Rewi's Poseidon is out of Invercargill and she knows "
            "this coast; listen to her."),
    date=(2029, 1, 22), time=(9, 0), sea=3, clouds="Scattered_2", wind="SW",
    difficulty=2, minutes=65, centre=(-46.1, 165.9),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE FIORDLAND APPROACHES, 46 South, morning. The task group is "
        "twenty-five miles off Puysegur Point in the busiest water it has "
        "seen since Sydney: two cruise ships bound for Milford Sound, the "
        "Bluff cray fleet on the grounds, a longliner, the Fisheries New "
        "Zealand patrol vessel, and the Invercargill-Queenstown service "
        "overhead.\\n\\n"
        "MV AUSTRAL COMPLIANCE, the Australian Maritime Services tender that "
        "followed the protection group north, is thirty miles south-west "
        "broadcasting closed grounds on the fishing channels. The research "
        "trawler that Turning North named is somewhere south of her. A "
        "conventional submarine was reported off the Solander Islands "
        "yesterday; it is not routed at anyone and it is not the mission.\\n\\n"
        "KIWI 05 is out of Invercargill with the New Zealand picture. Your "
        "own Seahawk and Poseidon fly if bought; the Arafura goes on sale "
        "here for the inshore work. Classify the tender - her radars, her "
        "signals, her name on the stern - then hold the patrol line to the "
        "south-west. Everything red is weapons tight and so are you. The "
        "cray boats do not move for warships."),
    forces="Your task group with its Seahawk and Poseidon if bought, an "
           "Arafura if bought, Kiwi 05 out of Invercargill. Neutral: two "
           "Milford cruise ships, three cray boats and longliners, the "
           "Fisheries New Zealand patrol vessel, an airliner. Opposing: MV "
           "Austral Compliance, the research trawler Nan Hai 27, one Type "
           "039C submarine to the south-west.",
    objectives=[
        ("Tender", "Classify MV Austral Compliance, then hold the patrol "
                   "line south-west of her", "30,-30,Fail,Main"),
        ("Boat", "Classify the submarine off the Solander Islands", "15,0,None"),
        ("Traffic", "Harm no cruise ship, fishing boat, patrol vessel or "
                    "aircraft", "0,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="escort", min_units=1, objective="Tender",
                 after=dict(kind="classify", units=["tender"], min_units=1,
                            sets="TS01TenderNamed",
                            intel="AUSTRAL COMPLIANCE has a name and a class: "
                                  "the same tender that fuelled the group off "
                                  "Macquarie in December, now with a "
                                  "navigation radar Rewi's people say is a "
                                  "frigate's. Hold the patrol line south-west "
                                  "of her. Chatham Watch will know her by her "
                                  "emitters.")),
    fatal=[],
    neutral_objective="Traffic",
    win="The tender is named, the line is held, and nobody in Fiordland "
        "lost a boat. Rewi: 'That is how you are welcome here.'",
    lose="The flagship is gone off Puysegur, or a New Zealand hull is, and "
         "the Tasman chapter opens with Wellington asking why.",
    timeout="Sixty-five minutes and the tender is still a shape on the "
            "horizon with the cray fleet between you. She keeps her "
            "anonymity for the Chathams.",
    stations={
        # The escort 25 NM off Puysegur; the tender 30 NM south-west on a
        # slow beat; the collector south of her; the boat 20 NM south-west
        # of the escort, routed along the shelf and not at anyone. The
        # traffic on real tracks: Milford-bound from the south, the cray
        # fleet on the grounds, the fisheries patrol between them.
        "escort": S(-46.10, 165.90, "Task group", heading=200),
        "flight": S(-46.12, 165.88, "Ship's flight", heading=200, alt=500),
        "mpa": S(-46.40, 165.75, "Maritime patrol", heading=200, alt=12000),
        "kiwi": S(-45.90, 166.30, "Kiwi 05", heading=240, alt=8000),
        "tender": S(-46.40, 165.30, "Austral Compliance", heading=120),
        "agi": S(-46.55, 166.10, "Research trawler", heading=90),
        "red_sub": S(-46.35, 165.55, "Contact TANGO", heading=250),
        "cruise": S(-45.70, 166.10, "Milford-bound", heading=20),
        "exped": S(-46.00, 166.20, "Expedition ship", heading=200),
        "cray1": S(-46.30, 166.10, "Cray boat", heading=90),
        "cray2": S(-46.20, 166.30, "Cray boat", heading=180),
        "cray3": S(-46.40, 166.00, "Longliner", heading=60),
        "fnz": S(-46.05, 166.15, "Fisheries patrol", heading=200),
        "airliner": S(-45.95, 166.45, "Queenstown-Invercargill", heading=230, alt=14000),
        "home": S(-46.412, 168.313, "Invercargill Airport"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("blue", "p-8-poseidon", "usn_p8", "kiwi", squadron="Squadron6",
          name="Kiwi 05", alt=8000, weapons="Tight", loadout="ASW"),
        U("red", "_vanilla", "civ_ms_kommunist", "tender",
          name="MV Austral Compliance (AMS tender)", weapons="Hold",
          route=[(-46.30, 165.70, 0), (-46.45, 165.95, 0)], telegraph=2),
        U("red", "_vanilla", "wp_agi_okean", "agi", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-46.50, 166.60, 0)], telegraph=2),
        U("red", "plan-submarines", "plan_ss_type_039c", "red_sub", name="Contact TANGO",
          depth="belowlayer", weapons="Tight",
          route=[(-46.60, 165.20, "belowlayer")], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Fiordland Sovereign (Milford cruise)",
          route=[(-44.60, 167.60, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_roro_c", "exped",
          name="MV Tutoko Explorer (expedition ship, stand-in)",
          route=[(-46.60, 167.30, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_crabboat", "cray1", name="Cray boat Kotare",
          route=[(-46.55, 167.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "cray2", name="Cray boat Ranui",
          route=[(-46.55, 167.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "cray3",
          name="Longliner Aparima", route=[(-46.55, 167.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_d", "fnz",
          name="Fisheries New Zealand patrol (stand-in)",
          route=[(-46.35, 166.45, 0)], telegraph=2),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airliner",
          name="Queenstown-Invercargill 612 (descending over Foveaux)"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Invercargill Airport (RNZAF detachment)", nation="New Zealand",
          weapons="Hold"),
    ],
    resolve={"Tender": "victory", "Traffic": "neutral",
             "Boat": ("classify", "red_sub", 1),
             "Flagship": ("protect", "escort")},
    declares=["TS01TenderNamed"],
    reveal_if=[dict(variable="SR12NetworkNamed", units=["agi"], level="Classify",
                    intel="Turning North's picture: the research trawler you "
                          "named in the Tasman approaches is south of the tender, "
                          "and she is on your plot as a classified contact. Where "
                          "she is, the tender is being told what to say.")],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "ran_opv_arafura",
                       "usn_mh-60r", "usn_p8", "raaf_mq-4c_triton", "E7A_Wedgetail",
                       "raaf_f-35a"],
                flights=[HELO, RECON],
                situation="Sydney, before the Tasman. Requisition, repair and "
                          "rearm: the Arafura goes on sale for the inshore work "
                          "in New Zealand's water. Cook Strait and Chatham Watch "
                          "have no builder; the next window is before Tasman "
                          "Crossing."),
    role="patrol",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 200, 10
