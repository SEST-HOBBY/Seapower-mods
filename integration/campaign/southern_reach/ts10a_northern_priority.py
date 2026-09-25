"""TS10A - Northern Priority. The Hauraki Gulf approaches, 22 February 2029.

The optional pair: after the Southern Convoy the group splits its
remaining strength between Auckland's approaches and Adelaide's, and the
player's detachment can hold one of them. This is the northern one - a
corvette, the collector and the tender trying to establish a "compliance
station" off the Colville Channel, with the Auckland traffic in the way.
Holding it is what keeps the northern element out of Approaches.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="TS10A", series="Tasman Shield", seq="TASMAN SHIELD  ·  OPTIONAL",
    group="optional", num="10A", key="Northern Priority",
    place="The Hauraki Gulf approaches",
    intro="The group's northern element is trying to set up a compliance "
          "station off the Colville Channel with the Auckland traffic in "
          "the way. Hold the approaches with a detachment, or hold "
          "Adelaide's instead.",
    special="Optional, and one of a pair: a detachment can hold Auckland's "
            "approaches, Adelaide's, or both before Approaches. "
            "Whichever is not held reinforces the group in the western "
            "Tasman. Expires when Approaches is complete.",
    sender="Commander Tessa Brand, RNZN, HQ Joint Forces New Zealand",
    intent=("After Portland the group has split what it has left: a "
            "corvette, the collector and the tender have come round North "
            "Cape and are trying to establish a 'compliance station' off "
            "the Colville Channel, which is a way of saying they intend to "
            "stop the Auckland traffic and inspect it. HAURAKI TRADER is "
            "inbound with the port's week in her. Get her to the "
            "Rangitoto Channel approach with your detachment and Kiwi 05 "
            "out of Whenuapai, classify the tender for the record, and "
            "keep the Great Barrier ferry and the fishing boats out of "
            "it. Nothing here has fired and the corvette is weapons tight; "
            "so are you, until she is not."),
    date=(2029, 2, 22), time=(8, 30), sea=2, clouds="Scattered_1", wind="NE",
    difficulty=2, minutes=60, centre=(-36.45, 175.05),
    blue_nation="Australia", red_nation="China",
    brief=(
        "THE HAURAKI GULF, morning, flat calm. MV HAURAKI TRADER, a "
        "container ship with the port of Auckland's week in her, is in the "
        "outer Gulf inbound for the Rangitoto Channel. The Great Barrier "
        "ferry, the Tauranga container service outbound, two fishing "
        "boats and the Auckland-Sydney service are in the same water, "
        "which is narrow.\\n\\n"
        "Off the Colville Channel, fifteen miles north-east, a Type 056A, "
        "the research trawler NAN HAI 27 and MV AUSTRAL COMPLIANCE are "
        "steaming slow circles and broadcasting a 'compliance station' on "
        "the port's working channel: an intention to stop and inspect. "
        "The corvette is weapons tight.\\n\\n"
        "Your detachment is with the container ship; KIWI 05 is up out of "
        "Whenuapai, thirty miles away. Get HAURAKI TRADER to the Rangitoto "
        "approach, classify the tender, harm nothing that is New "
        "Zealand's. Hold this and the northern element stays here instead "
        "of joining the group off Sydney."),
    forces="Your detachment with its Seahawk and Poseidon if bought, Kiwi "
           "05 out of Whenuapai, the container ship Hauraki Trader. "
           "Neutral: the Tauranga container service, the Great Barrier "
           "ferry, two fishing boats, an airliner. Opposing: one Type 056A, "
           "the research trawler Nan Hai 27, MV Austral Compliance.",
    objectives=[
        ("Approaches", "MV Hauraki Trader reaches the Rangitoto Channel "
                       "approach", "30,-30,Fail,Main"),
        ("Station", "Classify MV Austral Compliance", "15,0,None"),
        ("Traffic", "Harm no ferry, merchant, fishing boat or aircraft",
         "0,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="trader", min_units=1, objective="Approaches",
                 at=(-36.72, 174.90), radius=4, sets="TS10ANorthHeld"),
    fatal=[F("Approaches", ["trader"])],
    neutral_objective="Traffic",
    win="Hauraki Trader is at the Rangitoto approach with the pilot "
        "aboard, and the compliance station is three ships steaming in "
        "circles off Colville with nobody to inspect. The northern "
        "element stays in the Gulf. Brand: 'Auckland noticed. That was "
        "the point.'",
    lose="The container ship is lost in the Gulf, or the flagship is, "
         "and the northern element goes south to join the group with "
         "Auckland's week on the bottom behind it.",
    timeout="Sixty minutes and Hauraki Trader is still in the outer Gulf "
            "with the corvette between her and the channel. The northern "
            "element leaves for the Tasman with a story to tell.",
    stations={
        # The container ship and detachment in the outer Gulf 15 NM
        # south-west of the compliance station; the station's three hulls
        # in slow circles off the Colville Channel; Kiwi 05 up out of
        # Whenuapai; the Auckland traffic on the real tracks.
        "trader": S(-36.50, 175.02, "Hauraki Trader", heading=230),
        "escort": S(-36.45, 175.05, "Detachment", heading=230),
        "flight": S(-36.47, 175.07, "Ship's flight", heading=230, alt=500),
        "mpa": S(-36.60, 175.30, "Maritime patrol", heading=20, alt=8000),
        "kiwi": S(-36.55, 174.85, "Kiwi 05", heading=40, alt=6000),
        "red_056": S(-36.35, 175.35, "Type 056A", heading=20),
        "agi": S(-36.30, 175.30, "Research trawler", heading=90),
        "tender": S(-36.38, 175.40, "Austral Compliance", heading=340),
        "container": S(-36.35, 175.25, "Tauranga service", heading=350),
        "gb_ferry": S(-36.55, 175.00, "Great Barrier ferry", heading=40),
        "fish1": S(-36.60, 175.15, "Fishing boat", heading=300),
        "fish2": S(-36.40, 175.20, "Fishing boat", heading=200),
        "airliner": S(-36.70, 174.70, "Auckland-Sydney", heading=270, alt=15000),
        "home": S(-36.788, 174.630, "RNZAF Base Auckland"),
    },
    units=[
        U("blue", "_vanilla", "civ_ms_act_1", "trader", name="MV Hauraki Trader"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=8000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("blue", "p-8-poseidon", "usn_p8", "kiwi", squadron="Squadron6",
          name="Kiwi 05", alt=6000, weapons="Tight", loadout="ASW"),
        U("red", "modern-plan-systems", "plan_type_056a", "red_056",
          name="Type 056A corvette", weapons="Tight",
          route=[(-36.40, 175.45, 0), (-36.30, 175.30, 0)], telegraph=2),
        U("red", "_vanilla", "wp_agi_okean", "agi", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-36.42, 175.50, 0), (-36.35, 175.35, 0)], telegraph=2),
        U("red", "_vanilla", "civ_ms_kommunist", "tender",
          name="MV Austral Compliance (AMS tender)", weapons="Hold",
          route=[(-36.30, 175.30, 0), (-36.40, 175.45, 0)], telegraph=2),
        U("neutral", "re-power-resupply", "civ_ms_freighter_b", "container",
          name="MV Tauranga Express (Auckland-Tauranga)",
          route=[(-36.10, 175.20, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_roro_c", "gb_ferry",
          name="Great Barrier ferry Aotea",
          route=[(-36.32, 175.32, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fish1",
          name="Fishing boat Waiheke Lass", route=[(-36.65, 174.95, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fish2",
          name="Fishing boat Coromandel Star", route=[(-36.55, 175.10, 0)], telegraph=2),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Auckland-Sydney 103", airway=(-33.95, 151.18)),  # Sydney
        U("blue", "SEST_RAAF_Bases", "airbase_rnzaf_auckland", "home",
          name="RNZAF Base Auckland (Whenuapai)", nation="NewZealand",
          weapons="Hold"),
    ],
    resolve={"Approaches": "victory", "Traffic": "neutral",
             "Station": ("classify", "tender", 1),
             "Flagship": ("protect", "escort")},
    declares=["TS10ANorthHeld"],
    expires_after="Approaches",
    window=dict(detachment=True, flights=[HELO, RECON]),
    role="patrol",
)
