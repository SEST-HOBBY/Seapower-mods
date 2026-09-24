"""TS10B - Southern Priority. The Gulf St Vincent approaches, 22 February 2029.

The southern half of the optional pair: a frigate and a Kilo in the
approaches to Adelaide, a tanker for Outer Harbor, the Kangaroo Island
ferry on its crossing, and a Poseidon out of Edinburgh sixty miles away.
Holding it is what keeps the southern element out of Approaches.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="TS10B", series="Tasman Shield", seq="TASMAN SHIELD  ·  OPTIONAL",
    group="optional", num="10B", key="Southern Priority",
    place="The Gulf St Vincent approaches",
    intro="The group's southern element - a frigate and a Kilo - is in "
          "Adelaide's approaches with a tanker for Outer Harbor coming "
          "through them. Hold the approaches with a detachment, or hold "
          "Auckland's instead.",
    special="Optional, and one of a pair: a detachment can hold Adelaide's "
            "approaches or Auckland's before Approaches, not both. "
            "Whichever is not held reinforces the group in the western "
            "Tasman. Expires when Approaches is complete.",
    sender="Commodore Alex Mercer",
    intent=("A Type 054A and a Kilo came through Backstairs Passage last "
            "night and are sitting in the Gulf's approaches, which is "
            "Adelaide's front door. OSBORNE SPIRIT is coming up Investigator "
            "Strait for Outer Harbor with the refinery's fortnight in her. "
            "Take a detachment and Edinburgh's Poseidon and get her to the "
            "approach past both of them. The frigate is weapons tight and "
            "the Kilo has not fired; the Kangaroo Island ferry is on her "
            "crossing and the tuna boats are on the grounds. Classify the "
            "boat if you can. Hold this and the southern element stays "
            "here instead of joining the group off Sydney."),
    date=(2029, 2, 22), time=(15, 0), sea=2, clouds="Clear", wind="S",
    difficulty=2, minutes=60, centre=(-35.15, 137.9),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE GULF ST VINCENT APPROACHES, afternoon, a light southerly. MT "
        "OSBORNE SPIRIT is at the mouth of the Gulf with your detachment, "
        "inbound for Outer Harbor with a fortnight's crude for the "
        "refinery. The Kangaroo Island ferry is on the Cape Jervis-"
        "Penneshaw crossing, two tuna boats are bound out for Port "
        "Lincoln, a grain bulker is coming down from Port Giles for "
        "Backstairs Passage, and the Adelaide-Melbourne service is "
        "overhead.\\n\\n"
        "A Type 054A came through Backstairs Passage at 0300 and is "
        "forty miles south-west of the tanker, weapons tight, "
        "closing at twelve knots to 'escort' her. A Kilo came through "
        "with her and is somewhere between the frigate and the tanker's "
        "track with a Z-9 dipping over her.\\n\\n"
        "Edinburgh's Poseidon is on the Recon row, sixty miles away. "
        "Get the tanker to the Outer Harbor approach. Classify the Kilo. "
        "Harm nothing that is South Australia's. Hold this and the "
        "southern element stays in the Gulf instead of going east."),
    forces="Your detachment with its Seahawk and Poseidon if bought, out "
           "of Edinburgh; the tanker Osborne Spirit. Neutral: the Kangaroo "
           "Island ferry, two tuna boats, a grain bulker, an airliner. "
           "Opposing: one Type 054A, one Kilo, a Z-9.",
    objectives=[
        ("Approaches", "MT Osborne Spirit reaches the Outer Harbor approach",
         "30,-30,Fail,Main"),
        ("Boat", "Classify the Kilo", "15,0,None"),
        ("Traffic", "Harm no ferry, fishing boat, merchant or aircraft",
         "0,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="tanker", min_units=1, objective="Approaches",
                 at=(-34.75, 138.35), radius=5, sets="TS10BSouthHeld"),
    fatal=[F("Approaches", ["tanker"])],
    neutral_objective="Traffic",
    win="Osborne Spirit is at the Outer Harbor approach with the pilot "
        "aboard and the frigate twenty miles astern of her with nothing "
        "to escort. The southern element stays in the Gulf.",
    lose="The tanker is lost in Adelaide's front door, or the flagship "
         "is, and the southern element goes east to join the group.",
    timeout="Sixty minutes and Osborne Spirit is still in the Gulf's mouth "
            "with the frigate alongside her offering an escort. The "
            "southern element leaves for the Tasman tonight.",
    stations={
        # The tanker and detachment inside the Gulf's mouth on 020, 14 NM
        # from the approach box (the clock buys 13.5 NM at the solver's
        # 18 kn); the frigate 40 NM south-west closing slowly; the Kilo between the
        # frigate and the track with the Z-9 over her; the ferry on the
        # real crossing, the grain bulker for Backstairs Passage, the tuna
        # boats round Cape Spencer for Port Lincoln.
        "tanker": S(-34.92, 138.15, "Osborne Spirit", heading=20),
        "escort": S(-35.02, 138.10, "Detachment", heading=20),
        "flight": S(-35.04, 138.08, "Ship's flight", heading=20, alt=500),
        "mpa": S(-34.85, 138.28, "Maritime patrol", heading=200, alt=8000),
        "red_frig": S(-35.55, 137.60, "Type 054A", heading=30),
        "red_sub": S(-35.25, 137.85, "Contact KILO", heading=30),
        "red_dip": S(-35.45, 137.70, "Z-9 dip", heading=30, alt=1500),
        "ferry": S(-35.62, 138.02, "Kangaroo Island ferry", heading=250),
        "tuna": S(-35.30, 137.50, "Tuna boats", heading=270),
        "grain": S(-35.20, 137.75, "Grain bulker", heading=130),
        "airliner": S(-35.30, 138.30, "Adelaide-Melbourne", heading=110, alt=20000),
        "home": S(-34.703, 138.622, "RAAF Base Edinburgh"),
    },
    units=[
        U("blue", "_vanilla", "civ_ms_ritina", "tanker", name="MT Osborne Spirit"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=8000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_frig",
          name="Type 054A frigate", weapons="Tight",
          route=[(-35.30, 137.90, 0), (-34.95, 138.20, 0)], telegraph=2),
        U("red", "chinese-navy-plan", "plan_ss_kilo", "red_sub", name="Contact KILO",
          depth="belowlayer", weapons="Tight",
          route=[(-35.05, 138.15, "belowlayer")], telegraph=2),
        U("red", "modern-plan-systems", "plan_z-9c", "red_dip", name="Z-9 dip",
          alt=1500, loadout="ASWKiller", weapons="Tight"),
        U("neutral", "_vanilla", "civ_ms_roro_c", "ferry",
          name="Kangaroo Island ferry Sealink (stand-in)",
          route=[(-35.70, 137.98, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "tuna",
          name="Tuna boat Lincoln Cove",
          route=[(-35.45, 136.60, 0), (-35.10, 135.85, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "tuna",
          name="Tuna boat Spencer Gulf",
          route=[(-35.45, 136.60, 0), (-35.10, 135.85, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_bulk", "grain",
          name="MV Yorke Harvest (Port Giles-Melbourne)",
          route=[(-35.66, 138.08, 0), (-35.85, 138.45, 0)], telegraph=3),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airliner",
          name="Adelaide-Melbourne 684"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_edinburgh", "home",
          name="RAAF Base Edinburgh", nation="australia", weapons="Hold"),
    ],
    resolve={"Approaches": "victory", "Traffic": "neutral",
             "Boat": ("classify", "red_sub", 1),
             "Flagship": ("protect", "escort")},
    declares=["TS10BSouthHeld"],
    expires_after="Approaches",
    window=dict(detachment=True, flights=[HELO, RECON]),
    role="patrol",
)
