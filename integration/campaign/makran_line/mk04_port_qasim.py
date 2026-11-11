"""MK04 - Port Qasim. The Karachi approaches, 14 November 2028. Final.

The last convoy: three tankers from the Karachi outer anchorage to Port
Qasim, with Meridian's three armed trawlers and an armed ro-ro coming for
them, and the mothership, MV Meridian Sentinel, off the Indus mouths
running for the open sea. Stopping her ends Meridian's campaign on the
road: she is the trawlers' fuel and ammunition.

Step 3 and 4 of the builder-grammar design, as Red Line's The Order to
Withdraw uses them: the victory has two paths, Sunk and HoveTo. Closed to
three miles by the screen's lead ship (the ship's flight does not count),
she heaves to: a turn_back moves her to the neutral task force, sends her
to the Karachi roads and slows her to telegraph 2, and sinking her after
that ends the mission as a protected neutral's loss does. Progress
reports tell the player where the convoy and the mothership are on the
way to the release terms. If Hangor classified her (MK03MotherNamed), her
position is on the plot for the first fifteen minutes.
"""
from campaign_data import U, F, S
from .tables import HELO, ATTACK, CAP, AEW, WHOLE

MISSION = dict(
    code="MK04", series="Makran Line", seq="MAKRAN LINE  ·  MISSION 4",
    group="core", num="04", key="Port Qasim", place="Karachi approaches",
    intro=(
        "The last convoy into Port Qasim, with Meridian's boats coming for it and their "
        "mothership running for the open sea."
    ),
    sender="Commander Pakistan Fleet, Karachi",
    intent=((
        "Bring the convoy in, and stop the mothership. SENTINEL is the trawlers' fuel and "
        "ammunition; if she stops, Meridian's boats have nowhere to go. A warship close aboard "
        "is enough to make her heave to, and a ship that has hove to is not fired on."
    )),
    date=(2028, 11, 14), time=(5, 0), sea=3, clouds="Scattered_1", wind="NE",
    difficulty=4, minutes=120, centre=(24.40, 66.95),
    blue_nation="Pakistan", red_nation="Meridian",
    brief=(
        (
            "KARACHI APPROACHES, 0500. MT LANDHI, MT KORANGI CREEK and MT THATTA SPIRIT "
            "weighed from the Karachi outer anchorage at 0300 with the month's fuel for Port "
            "Qasim and are on the deep-water route, twenty-four miles south-west of the Port "
            "Qasim anchorage. Three "
            "Meridian armed trawlers are coming in from the south-west, and an armed ro-ro, MV "
            "SEA FALCON, from the south.\\n\\n"
            "MV MERIDIAN SENTINEL, their mothership, was off the Indus mouths at midnight. She "
            "is now running south for the open sea. If she reaches the marked circle south of "
            "the delta, she is clear to sea and Meridian keeps the ship that fuels its "
            "boats.\\n\\n"
            "Bring at least two of the three tankers within four miles of the Port Qasim "
            "anchorage. Stop SENTINEL before she reaches that circle: sink her, or close her with "
            "the screen's lead ship to within about three miles, and she will heave to and "
            "follow your orders into the Karachi roads. From then she is a protected neutral; "
            "her loss ends the operation. Set the lead ship's weapons to Hold before closing "
            "her, or it may engage her on the way in. The convoy is in when two tankers are "
            "inside the anchorage circle, SENTINEL is sunk or has hove to, and no incoming "
            "weapon is still tracked against the task group.\\n\\n"
            "Fishing dhows, a bulk carrier at the Port Qasim anchorage and the Dubai service "
            "are on the water and in the air. Identify before you fire."
        )),
    forces=(
        "Your task group, its flights and any Air Force aircraft allocated, out of Masroor. "
        "Convoy: MT Landhi, MT Korangi Creek and MT Thatta Spirit. Opposing: three Meridian "
        "armed trawlers and the armed ro-ro MV Sea Falcon; running: MV Meridian Sentinel, "
        "armed. Neutral: dhows, a bulk carrier and an airliner."
    ),
    special=(
        "The final mission. Rearm is free at this force allocation, as at every one; the whole "
        "roster is on offer."
    ),
    objectives=[
        ("Convoy", "Bring two of the three tankers within four miles of the Port Qasim "
                   "anchorage", "35,-35,Fail,Main"),
        ("Mothership", "Also required: stop Meridian Sentinel before she reaches the marked "
                       "circle south of the delta, by sinking her or closing her until she "
                       "heaves to", "20,-40,Fail,Main"),
        ("Ships", "Lose none of the three tankers", "15,-30,Complete"),
        ("Raiders", "Sink three of the four Meridian boats coming for the convoy",
         "10,0,None"),
        ("Traffic", "Harm no dhow, merchant or airliner, nor Meridian Sentinel once she has "
                    "hove to", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", at=(24.60, 67.08), radius=4,
                 min_units=2, objective="Convoy",
                 also=[dict(kind="no_incoming")],
                 any_of=[
                     dict(name="Sunk", also=[dict(kind="destroyed", units=["mother"],
                                                  min_units=1)]),
                     dict(name="HoveTo",
                          also=[dict(kind="event", event="HeaveTo"),
                                dict(kind="afloat", units=["mother"])],
                          win=(
                              "The convoy is at the Port Qasim anchorage, and MERIDIAN "
                              "SENTINEL has hove to and is under escort into the Karachi roads"
                              " with her crew. Meridian's boats have lost the ship that fuels "
                              "them."
                          )),
                 ]),
    # The heave-to: the screen's lead ship (escort, the anchor) inside three
    # miles of her on her own track, the helicopter not counted.
    turn_back=[dict(
        name="HeaveTo", units=["mother"], by=["escort"], radius=3,
        to=(24.62, 66.80), telegraph=2, transfer="Neutral", objective="Mothership",
        intel=(
            "BRIDGE: MERIDIAN SENTINEL has stopped engines and answered. She has hove to and is "
            "turning for the Karachi roads under our orders. She is no longer hostile; do not "
            "fire on her."
        ),
        protected=dict(objective="Traffic", message=(
            "MERIDIAN SENTINEL had hove to and was under escort when she was sunk. Her crew "
            "had surrendered their ship, and the Navy will answer for it."
        )))],
    denied=[dict(units=["mother"], at=(24.00, 67.00), radius=4, objective="Mothership",
                 message=(
                     "MERIDIAN SENTINEL has cleared the delta and is running south-west for "
                     "the open sea. The task group cannot follow her and keep the convoy. "
                     "Meridian keeps its mothership."
                 ))],
    fatal=[F("Ships", ["convoy#1", "convoy#2", "convoy#3"], 2)],
    neutral_objective="Traffic",
    reveal_if=[dict(
        variable="MK03MotherNamed", units=["mother"], level="", time=900,
        intel=(
            "FLEET OPERATIONS: HANGOR's recording of the sixth, correlated with tonight's "
            "picture, puts MERIDIAN SENTINEL here. The position is on your display as a datum "
            "and will age off in fifteen minutes. It is a record, not a contact: find her with "
            "your own sensors."
        ))],
    # Information only (step 5): the convoy halfway and the first tanker in,
    # and the mothership halfway to clearing the delta on her own route
    # (the heave-to switches that one off).
    progress=[
        dict(name="Halfway", units=["convoy#1", "convoy#2", "convoy#3"], at=(24.47, 66.91),
             radius=3, min_units=2, intel=(
                 "CONVOY COMMODORE: Two tankers are halfway to the Port Qasim anchorage. Keep "
                 "the screen between them and the boats to the south-west.")),
        dict(name="FirstIn", units=["convoy#1", "convoy#2", "convoy#3"], min_units=1, intel=(
            "PORT QASIM CONTROL: The first tanker is inside the four-mile circle off the "
            "anchorage. The convoy is in when two are, MERIDIAN SENTINEL is sunk or has hove "
            "to, and nothing is inbound.")),
        dict(name="Running", units=["mother"], at=(24.20, 67.10), radius=2, intel=(
            "FLEET OPERATIONS: MERIDIAN SENTINEL is halfway to clearing the delta. Sink her or "
            "close her now.")),
    ],
    win=(
        "The convoy is at the Port Qasim anchorage, and MERIDIAN SENTINEL is sunk off the "
        "delta. Meridian's boats have lost the ship that fuelled them, and the masters at the "
        "Gulf end of the road are asking for the next sailing date."
    ),
    lose=(
        "The convoy is broken: two of the three tankers are lost. Port Qasim will be short of "
        "fuel by the end of the month, and Meridian's escorts will be the only ones the "
        "masters can get."
    ),
    timeout=("{deadline_clock}, and the convoy is not in: two tankers are not inside the "
             "anchorage circle, or MERIDIAN SENTINEL is neither sunk nor hove to. The tankers "
             "anchor short of Port Qasim and wait for daylight."),
    stations={
        "escort": S(24.33, 66.78, "Escort", heading=45),
        "flight": S(24.34, 66.80, "Ship's flight", heading=45, alt=500),
        "convoy": S(24.35, 66.75, "Convoy", heading=50),
        "mother": S(24.40, 67.20, "Meridian Sentinel", heading=200),
        "raiders": S(24.05, 66.35, "Meridian trawlers", heading=45),
        "roro": S(23.95, 67.10, "Armed ro-ro", heading=340),
        "dhows": S(24.45, 66.95, "Fishing dhows", heading=250),
        "bulker": S(24.55, 67.04, "Bulk carrier at anchor", heading=200),
        "airliner": S(24.80, 66.70, "Dubai service", heading=270, alt=24000),
        "home": S(24.894, 66.939, "PAF Base Masroor"),
        "strike": S(24.80, 66.95, "Strike flight", heading=200, alt=3000),
        "cap": S(24.82, 66.98, "Air defence flight", heading=200, alt=20000),
        "aew": S(24.90, 67.10, "ZDK-03", heading=200, alt=25000),
    },
    units=[
        # air_group=[]: the pack's file embarks the PLAN's Z-9F (China), which
        # would fill her one deck slot when the mission is launched as authored.
        U("blue", "pakistani-pack", "pns_type_054a_p", "escort", variant="Variant3",
          air_group=[]),
        U("blue", "pakistani-pack", "plan_z-9ce", "flight", squadron="Squadron1",
          alt=500, loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "pakistani-pack", "paf_jf-17_blk_iii", "strike", squadron="Squadron2",
          alt=3000, loadout="AntiShip", slot="Attack"),
        U("blue", "pakistani-pack", "paf_jf-17_blk_iii", "strike", squadron="Squadron2",
          alt=3000, loadout="AntiShip", slot="Attack"),
        U("blue", "pakistani-pack", "paf_jf-17_blk_ii", "cap", squadron="Squadron2",
          alt=20000, loadout="AirToAir", slot="CAP"),
        U("blue", "pakistani-pack", "paf_jf-17_blk_ii", "cap", squadron="Squadron2",
          alt=20000, loadout="AirToAir", slot="CAP"),
        U("blue", "pakistani-pack", "paf_zdk-03", "aew", squadron="Squadron1",
          alt=25000, loadout="AEW", slot="Recon"),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Landhi",
          nation="Pakistan", weapons="Hold", route=[(24.60, 67.08, 0)], telegraph=3),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Korangi Creek",
          nation="Pakistan", weapons="Hold", route=[(24.62, 67.06, 0)], telegraph=3),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Thatta Spirit",
          nation="Pakistan", weapons="Hold", route=[(24.58, 67.10, 0)], telegraph=3),
        U("blue", "_vanilla", "airfield_small_1", "home", name="PAF Base Masroor",
          nation="Pakistan", weapons="Hold", air_group=[]),
        U("red", "armed-merchantmen", "civ_ms_act_1_armed", "mother",
          name="MV Meridian Sentinel", nation="Meridian", weapons="Hold",
          route=[(24.10, 67.05, 0), (23.80, 66.95, 0)], telegraph=3),
        U("red", "armed-merchantmen", "civ_fv_okean_armed", "raiders", variant="Variant4",
          loadout="Bofors", name="Meridian Escort 51", nation="Meridian", route=[(24.42, 66.86, 0)],
          telegraph=4),
        U("red", "armed-merchantmen", "civ_fv_okean_armed", "raiders", variant="Variant5",
          loadout="Bofors", name="Meridian Escort 52", nation="Meridian", route=[(24.45, 66.90, 0)],
          telegraph=4),
        U("red", "armed-merchantmen", "civ_fv_sidetrawler_armed", "raiders",
          name="Meridian Escort 53", nation="Meridian", route=[(24.40, 66.82, 0)],
          telegraph=4),
        U("red", "armed-merchantmen", "civ_ms_roro_b_armed", "roro", name="MV Sea Falcon",
          nation="Meridian", route=[(24.48, 66.98, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_dhow", "dhows", name="Dhow Ibrahim Haidery",
          nation="Pakistan", route=[(24.38, 66.70, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_dhow", "dhows", name="Dhow Keti Bandar",
          nation="Pakistan", route=[(24.30, 66.90, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker", name="MV Qasim Venture",
          nation="Panama"),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Karachi-Dubai service", squadron="Squadron29",
          airway=(25.25, 55.36)),  # Dubai
    ],
    resolve={"Convoy": "victory", "Traffic": "neutral",
             "Mothership": ("destroy", "mother", 1),
             "Ships": ("protect", "convoy#1", "convoy#2", "convoy#3"),
             "Raiders": ("destroy", ["raiders", "roro"], 3)},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True, allow=list(WHOLE),
                flights=[HELO, ATTACK, CAP, AEW],
                situation=(
                    "The last force allocation of the campaign. The whole roster is on offer, "
                    "and the ships have rearmed at Karachi."
                )),
    role="escort",
)
