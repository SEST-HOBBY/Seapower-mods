"""TS08 - Great Australian Bight. 15 February 2029.

A long-range search with limited service: the escorts and Collins working
two sectors against SIERRA-TWO, the Yasen nobody has held, with the Udaloy and its oiler at a rendezvous to the
south-west. Eighty minutes is the point. The flag on the Yasen is what the
Southern Convoy reads.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="TS08", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 8",
    group="core", num="08", key="Great Australian Bight", place="The Bight",
    intro="SIERRA-TWO, the Russian detachment's Yasen and the one boat "
          "nobody has held contact on, is in the Bight ahead of the Southern Convoy's track. Collins has the "
          "western sector; you have the eastern. Eighty minutes.",
    special=(
        "Repair only before this operation: Adelaide's dockyard has the plate and not the "
        "magazines. Rearm comes before the Southern Convoy."
    ),
    sender="Commodore Alex Mercer, for the Submarine Force",
    intent=((
        "SIERRA-TWO is the Yasen, the second nuclear boat the 5 January intelligence summary "
        "credited to the Russian detachment, and nobody has held contact on her; the last thing"
        " anybody wants under the Southern Convoy on the nineteenth is a Yasen. The "
        "Udaloy-class destroyer MARSHAL SHAPOSHNIKOV and her oiler are at a rendezvous seventy "
        "miles south-west; intelligence assesses a possible rendezvous there, but the boat's "
        "present course and depth are unconfirmed. Collins has the western sector at periscope "
        "depth, weapons tight; you have the eastern with the Seahawk and Edinburgh's Poseidon. "
        "Find her and sink her. The Udaloy is a warship that has not fired and the oiler is an "
        "oiler; classify the oiler, leave the Udaloy unless she makes it necessary. Eighty "
        "minutes."
    )),
    date=(2029, 2, 15), time=(5, 50), sea=4, clouds="Broken_3", wind="SW",
    difficulty=4, minutes=80, centre=(-35.5, 132.5),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        (
            "THE GREAT AUSTRALIAN BIGHT, a hundred and forty miles offshore, before dawn. Two "
            "sectors: HMAS COLLINS in the western at periscope depth, your escorts in the "
            "eastern with the Seahawk and a Poseidon out of Edinburgh, three hundred miles "
            "behind you. The US Navy Virginia-class boat on the Western Australia rotation is "
            "somewhere west of Collins and is not on your plot.\\n\\nSIERRA-TWO, the Yasen, is in"
            " the Bight because MARSHAL SHAPOSHNIKOV, an Udaloy-class destroyer, and the oiler "
            "BORIS CHILIKIN are seventy miles south-west of you, stopped, with a Ka-27 up - a "
            "suspected support rendezvous and a useful search cue. It does not establish the "
            "submarine's position or depth.\\n\\nFind the boat and sink her before she reaches "
            "them. Two Port Lincoln tuna boats, a Bight bulker and a whale are in the sectors. "
            "The Udaloy has not fired; classify the oiler and leave the Udaloy unless she gives"
            " you no choice. The search window is eighty minutes. The submarine's arrival at "
            "the suspected rendezvous is unconfirmed.\\n\\nASW PICTURE: Satellite imagery and "
            "surface reports can locate the support ships. Collins, the escorts and maritime "
            "patrol aircraft must find SIERRA-TWO acoustically. Correlate acoustic reports "
            "independently of the surface rendezvous assessment."
        )),
    forces=(
        "Your task group with its Seahawk and Poseidon if assigned, out of Edinburgh; HMAS "
        "Collins in the western sector. Neutral: two tuna boats, a bulker, a whale. Opposing: "
        "one Yasen, the destroyer Marshal Shaposhnikov with a Ka-27 up, the oiler Boris "
        "Chilikin."
    ),
    objectives=[
        ("Boat", "Destroy SIERRA-TWO", "40,-40,Fail,Main"),
        ("Oiler", "Classify the oiler at the rendezvous", "15,0,None"),
        ("Collins", "HMAS Collins must survive", "15,-25,Complete"),
        ("Neutrals", "Harm no tuna boat, merchant or whale", "0,-25,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="destroy", stations=["red_sub"], min_units=1, objective="Boat"),
    fatal=[F("Collins", ["collins"])],
    neutral_objective="Neutrals",
    win=(
        "SIERRA-TWO is confirmed lost in the Bight. The Udaloy and oiler require a separate "
        "contact report; their withdrawal has not been confirmed. This submarine will no longer"
        " threaten the southern convoy."
    ),
    lose="Collins is lost in the Bight, or the flagship is, and the Yasen "
         "reaches her rendezvous with full stores.",
    timeout=(
        "No confirmed loss of SIERRA-TWO has been reported within the search window. Retain the"
        " Yasen on the outstanding threat list for the Southern Convoy; its arrival at the "
        "suspected rendezvous is unconfirmed."
    ),
    stations={
        # The escorts in the eastern sector on 240; Collins 25 NM west at
        # periscope depth (an escort has to be able to steam to what it
        # protects in the clock); the boat 16 NM south of Collins, routed
        # for the rendezvous 75 NM south-west; the
        # Udaloy and the oiler stopped there with the Ka-27 up; the tuna
        # boats bound for Port Lincoln, the bulker westbound.
        "escort": S(-35.50, 132.50, "Escort group", heading=240),
        "flight": S(-35.52, 132.48, "Ship's flight", heading=240, alt=500),
        "mpa": S(-35.30, 132.10, "Maritime patrol", heading=240, alt=10000),
        "collins": S(-35.65, 132.00, "HMAS Collins", heading=240),
        "red_sub": S(-35.90, 131.90, "Contact SIERRA-TWO", heading=230),
        "red_rv": S(-36.30, 131.30, "Rendezvous", heading=0),
        "red_helo": S(-36.15, 131.45, "Ka-27 search", heading=60, alt=1500),
        "tuna": S(-35.30, 133.00, "Tuna boats", heading=80),
        "bulker": S(-35.80, 133.20, "Bight bulker", heading=270),
        "whale": S(-35.40, 132.20, "Biologic", heading=180),
        "home": S(-34.703, 138.622, "RAAF Base Edinburgh"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=10000,
          loadout="ASW", slot="Recon"),
        U("blue", "SEST_RAN_Fleet", "ran_ssg_collins", "collins", variant="Variant1",
          name="HMAS Collins", depth="periscope", weapons="Tight", telegraph=1),
        U("red", "russian-submarines", "wp_ssgn_yasen", "red_sub", name="Contact SIERRA-TWO",
          depth="belowlayer",
          route=[(-36.15, 131.55, "belowlayer"), (-36.28, 131.34, "shallow")],
          telegraph=2),
        U("red", "_vanilla", "wp_bpk_udaloy", "red_rv", name="Marshal Shaposhnikov",
          weapons="Tight", telegraph=1),
        U("red", "SEST_Replenishment", "wp_vt_boris_chilikin", "red_rv",
          name="Oiler Boris Chilikin", weapons="Hold", telegraph=1),
        U("red", "_vanilla", "wp_ka-27", "red_helo", name="Ka-27 search",
          alt=1500, loadout="ASW", weapons="Tight"),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "tuna",
          name="Tuna boat Boston Bay", route=[(-35.10, 135.85, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "tuna",
          name="Tuna boat Thistle Island", route=[(-35.10, 135.85, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Nullarbor (Whyalla-Fremantle)",
          route=[(-35.70, 130.00, 0)], telegraph=3),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic OSCAR",
          depth="shallow"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_edinburgh", "home",
          name="RAAF Base Edinburgh", nation="australia", weapons="Hold"),
    ],
    resolve={"Boat": "victory", "Neutrals": "neutral",
             "Oiler": ("classify", "red_rv#2", 1),
             "Collins": ("protect", "collins"),
             "Flagship": ("protect", "escort")},
    declares=["TS08YasenSunk"],
    flags=[dict(name="TS08YasenSunk", units=["red_sub"],
                intel="SIERRA-TWO is gone, short of her rendezvous. The Russian "
                      "detachment's second boat is on the bottom of the "
                      "Bight, and the Southern Convoy sails "
                      "without her.")],
    window=dict(repair=True, flights=[HELO, RECON],
                situation=(
                    "Adelaide can repair the force before the Bight search, but no ammunition "
                    "resupply or replacement allocation is available at this stop. Full support"
                    " resumes before the Southern Convoy."
                )),
    role="patrol",
)
