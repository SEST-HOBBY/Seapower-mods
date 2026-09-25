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
    intro="Fiordland's approaches, thick with cruise ships and cray boats, "
          "and an Austral Meridian tender off Puysegur that calls itself a "
          "compliance vessel. Put a name on it, hold the patrol line, and "
          "harm nothing.",
    sender="Commodore Alex Mercer; Squadron Leader Tane Rewi, No. 5 Squadron "
           "RNZAF, for the New Zealand picture",
    intent=("This is New Zealand's water and we are here at their request, "
            "which means every cray boat and cruise ship in the box is "
            "somebody's constituent. The Austral Meridian Services tender "
            "has been off Puysegur for three days telling fishing masters "
            "which grounds are closed. Put a class and a name on her, hold "
            "the patrol line to the south-west, and leave the submarine out "
            "there alone unless it comes to you. Nothing here fires "
            "first. Rewi's Poseidon, KIWI 05, is out of Invercargill and his "
            "crew knows this coast; listen to him."),
    date=(2029, 1, 22), time=(9, 0), sea=3, clouds="Scattered_2", wind="SW",
    difficulty=2, minutes=65, centre=(-46.1, 165.9),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "THE FIORDLAND APPROACHES, 46 South, morning. The task group is twenty-five miles "
            "off Puysegur Point in the busiest water it has seen since Sydney: two cruise ships"
            " bound for Milford Sound, the Bluff cray fleet on the grounds, a longliner, the "
            "Fisheries New Zealand patrol vessel, and the Invercargill-Queenstown service "
            "overhead.\\n\\nMV AUSTRAL COMPLIANCE, the Austral Meridian Services tender that "
            "followed the protection group north, is thirty miles south-west broadcasting "
            "closed grounds on the fishing channels. NAN HAI 27, the group's intelligence "
            "collector since October, is somewhere east of her, between her and the Solanders. "
            "A conventional submarine, contact TANGO, is reported twenty miles south-west of "
            "you, heading away from the traffic; monitor the report without abandoning the "
            "surface patrol.\\n\\nKIWI 05 is out of Invercargill with the New Zealand picture. "
            "Your own Seahawk and Poseidon fly, and an Arafura sails for the inshore work, if "
            "they were assigned at Sydney. Classify the tender - her radars, her signals, her "
            "name on the stern - then hold the patrol line to the south-west. The opposing "
            "formation is reported under restrictive engagement orders; your own orders also "
            "remain restrictive. The cray boats do not move for warships."
        )),
    forces=(
        "Your task group with its Seahawk, Poseidon and Arafura if assigned; Kiwi 05 out of "
        "Invercargill. Neutral: two Milford cruise ships, three cray boats and longliners, the "
        "Fisheries New Zealand patrol vessel, an airliner. Opposing: MV Austral Compliance, the"
        " research trawler Nan Hai 27, one Type 039C submarine to the south-west."
    ),
    objectives=[
        ("Tender", "Classify MV Austral Compliance, then hold the patrol "
                   "line to the south-west", "30,-30,Fail,Main"),
        ("Boat", "Classify the submarine reported to the south-west", "15,0,None"),
        ("Traffic", "Harm no cruise ship, fishing boat, patrol vessel or "
                    "aircraft", "0,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="escort", min_units=1, objective="Tender",
                 after=dict(kind="classify", units=["tender"], min_units=1,
                            sets="TS01TenderNamed",
                            intel=(
                                "IDENTIFICATION REPORT: AUSTRAL COMPLIANCE classified as the "
                                "Austral Meridian Services coaster reported with the protection"
                                " group. Its emissions and registration have been recorded for "
                                "comparison with later contacts. Hold the patrol line "
                                "south-west of the traffic. Classification alone does not "
                                "authorise an attack."
                            ))),
    fatal=[],
    neutral_objective="Traffic",
    win="The tender is named, the line is held, and nobody in Fiordland "
        "lost a boat. Rewi: 'That is how you are welcome here.'",
    lose=(
        "The Fiordland patrol has failed. Report the losses and last confirmed contacts to "
        "Wellington before another patrol is assigned."
    ),
    timeout="Sixty-five minutes and the tender is still a shape on the "
            "horizon with the cray fleet between you. She keeps her "
            "anonymity for whatever she is here to meet.",
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
        "exped": S(-46.00, 166.20, "Expedition ship", heading=20),
        "cray1": S(-46.30, 166.10, "Cray boat", heading=90),
        "cray2": S(-46.20, 166.30, "Cray boat", heading=180),
        "cray3": S(-46.40, 166.00, "Longliner", heading=60),
        "fnz": S(-46.05, 166.15, "Fisheries patrol", heading=200),
        "airliner": S(-45.95, 166.45, "Invercargill-Queenstown", heading=40, alt=14000),
        "home": S(-46.412, 168.313, "Invercargill Airport"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight",
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
          name="MV Tutoko Explorer (expedition ship)",
          route=[(-44.60, 167.60, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_crabboat", "cray1", name="Cray boat Kotare",
          route=[(-46.55, 167.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "cray2", name="Cray boat Ranui",
          route=[(-46.55, 167.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "cray3",
          name="Longliner Aparima", route=[(-46.55, 167.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_d", "fnz",
          name="Fisheries New Zealand patrol vessel",
          route=[(-46.35, 166.45, 0)], telegraph=2),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airliner",
          name="Invercargill-Queenstown 612 (Fiordland scenic routing)", airway=(-45.02, 168.74)),  # Queenstown
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Invercargill Airport (RNZAF detachment)", nation="NewZealand",
          weapons="Hold"),
    ],
    resolve={"Tender": "victory", "Traffic": "neutral",
             "Boat": ("classify", "red_sub", 1),
             "Flagship": ("protect", "escort")},
    declares=["TS01TenderNamed"],
    reveal_if=[dict(variable="SR12NetworkNamed", units=["agi"], level="Classify",
                    intel=(
                        "FUSION CELL: The 14 January identification of NAN HAI 27 matches the "
                        "collector reported east of AUSTRAL COMPLIANCE. The contact is "
                        "classified on the plot and held there for the operation. Its "
                        "association with Austral Meridian Services"
                        " is assessed; the contents of its current transmissions are "
                        "unconfirmed."
                    ))],
    window=dict(buy=True, repair=True, rearm=True,
                allow=["ran_ffh_anzac", "ran_ddg_hobart", "ran_opv_arafura",
                       "usn_mh-60r", "usn_p8", "raaf_mq-4c_triton", "E7A_Wedgetail",
                       "raaf_f-35a"],
                flights=[HELO, RECON],
                situation=(
                    "Sydney, before the Tasman. Force allocation, repairs and ammunition "
                    "resupply: the Arafura-class patrol vessel is released to the task group "
                    "for the inshore work in New Zealand's water. Cook Strait and Chatham Watch"
                    " sail on what you have; the next window is Sydney, before Tasman Crossing."
                )),
    role="patrol",
)
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 200, 10
