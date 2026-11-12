"""MK01 - The Fuel Road. The Karachi approaches, 24 October 2028.

The first convoy since the war-risk listing: two Pakistan-flagged tankers
from the outer roads, south-west of Karachi, to the pilot station. Two
Meridian armed trawlers - "escorts", in the company's word - are coming
in from the west to offer the masters an escort to a Meridian terminal,
and a third has been keeping company since dawn.

The opening window sells the ships and their flights only; the Air
Force's aircraft are released from Gwadar Roads. Every window rearms.
"""
from campaign_data import U, F, S
from .tables import HELO, OPENING

MISSION = dict(
    code="MK01", series="Makran Line", seq="MAKRAN LINE  ·  MISSION 1",
    group="core", num="01", key="The Fuel Road", place="Karachi approaches",
    intro=(
        "The first tanker convoy since the war-risk listing, with two Meridian trawlers "
        "coming in from the west to offer it an escort."
    ),
    sender="Commander Pakistan Fleet, Karachi",
    intent=((
        "Karachi runs on what these two ships carry. Bring both to the pilot station. "
        "Meridian's boats are armed and will order the masters to divert; if they close the "
        "convoy, stop them. Every dhow on this water is a fishing boat until you have "
        "identified it as something else."
    )),
    date=(2028, 10, 24), time=(6, 30), sea=3, clouds="Scattered_1", wind="SW",
    difficulty=2, minutes=110, centre=(24.62, 66.65),
    blue_nation="Pakistan", red_nation="Meridian",
    brief=(
        (
            "KARACHI APPROACHES, 0630. MT SINDH VOYAGER and MT ORMARA TRADER weighed at "
            "first light from the outer roads with crude for the refinery and diesel for the "
            "city. They are the first tankers to sail for Karachi since the war-risk listing, "
            "and the masters sailed on the Navy's word that they would be escorted.\\n\\n"
            "Two Meridian armed trawlers left the coast west of Sonmiani before dawn and are "
            "running east at their best speed. Meridian calls them escorts. Last week one of "
            "them ordered a Liberian tanker to divert to a Meridian terminal and put a burst "
            "of 40 mm across her bow when she would not. A third trawler, with no nets out, "
            "has kept station on the convoy since it weighed.\\n\\n"
            "Bring both tankers within six miles of the Karachi pilot station, twenty-six miles "
            "north-east. The convoy's task is complete when both are inside that circle. "
            "Your ships are weapons Free. If the Meridian boats close the convoy, stop them. "
            "The trawler keeping company is Meridian's eyes on the convoy; she has not fired."
            "\\n\\n"
            "Fishing dhows, an outbound freighter and the morning Dubai service are on the "
            "water and in the air. Identify before you fire."
        )),
    forces=(
        "Your task group, with its helicopter if one is embarked. Convoy: MT Sindh Voyager and "
        "MT Ormara Trader. Opposing: two Meridian armed trawlers, and a third keeping company. "
        "Neutral: fishing dhows, a freighter and an airliner. PAF Base Masroor is open to your "
        "helicopters."
    ),
    special=(
        "Rearm is free at every force allocation: the ships turn round at Karachi between "
        "missions. The Air Force's JF-17s and ZDK-03 are released from Gwadar Roads."
    ),
    objectives=[
        ("Convoy", "Bring both tankers within six miles of the Karachi pilot station",
         "35,-35,Fail,Main"),
        ("Ships", "Lose neither tanker", "20,-30,Complete"),
        ("Raiders", "Sink the two Meridian boats if they close the convoy", "10,0,None"),
        ("Traffic", "Harm no dhow, freighter or airliner", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", min_units=2, at=(24.70, 66.88),
                 radius=6, objective="Convoy"),
    fatal=[F("Ships")],
    neutral_objective="Traffic",
    # Information only (step 5 of the builder-grammar design): the convoy
    # halfway, and the first tanker inside the circle.
    progress=[
        dict(name="Halfway", units=["convoy#1", "convoy#2"], at=(24.60, 66.67), radius=3,
             min_units=2, intel=(
                 "CONVOY COMMODORE: Both tankers are halfway to the pilot station. Keep the "
                 "screen between them and the boats to the west.")),
        dict(name="FirstIn", units=["convoy#1", "convoy#2"], min_units=1, intel=(
            "KARACHI PORT CONTROL: The first tanker is inside the six-mile circle off the "
            "pilot station. The convoy is in when both are.")),
    ],
    win=(
        "SINDH VOYAGER and ORMARA TRADER are at the pilot station and the first pilot is "
        "climbing aboard. Two more masters at the Gulf end of the route have asked to sail "
        "under the same escort."
    ),
    lose=(
        "A tanker is lost. The war-risk listing will stay, and the next masters will take "
        "Meridian's escort rather than the Navy's."
    ),
    timeout="{deadline_clock}, and the convoy is still short of the pilot station. The masters "
            "anchor where they are and ask Karachi why.",
    stations={
        # The outer roads, 22 NM south-west of Cape Monze, with the convoy
        # two miles north of the screen and the ship's flight between them.
        "escort": S(24.47, 66.46, "Escort", heading=60),
        "flight": S(24.48, 66.48, "Ship's flight", heading=60, alt=500),
        "convoy": S(24.50, 66.46, "Convoy", heading=60),
        # The Meridian pair, 28 NM west, off the Sonmiani coast.
        "raiders": S(24.58, 65.90, "Meridian trawlers", heading=95),
        "picket": S(24.52, 66.30, "Trawler keeping company", heading=60),
        "dhows": S(24.55, 66.55, "Fishing dhows", heading=200),
        "freighter": S(24.66, 66.80, "Outbound freighter", heading=235),
        "airliner": S(24.80, 66.70, "Dubai service", heading=270, alt=24000),
        "home": S(24.894, 66.939, "PAF Base Masroor"),
    },
    units=[
        U("blue", "pakistani-pack", "pns_type_054a_p", "escort", variant="Variant1"),
        U("blue", "pakistani-pack", "plan_z-9ce", "flight", squadron="Squadron1",
          alt=500, loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Sindh Voyager",
          nation="Pakistan", weapons="Hold", route=[(24.70, 66.88, 0)], telegraph=3),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Ormara Trader",
          nation="Pakistan", weapons="Hold", route=[(24.72, 66.86, 0)], telegraph=3),
        U("blue", "_vanilla", "airfield_small_1", "home", name="PAF Base Masroor",
          nation="Pakistan", weapons="Hold", air_group=[]),
        U("red", "armed-merchantmen", "civ_fv_okean_armed", "raiders", variant="Variant4",
          name="Meridian Escort 21", nation="Meridian", route=[(24.55, 66.45, 0)],
          telegraph=4),
        U("red", "armed-merchantmen", "civ_fv_okean_armed", "raiders", variant="Variant5",
          name="Meridian Escort 22", nation="Meridian", route=[(24.52, 66.42, 0)],
          telegraph=4),
        U("red", "armed-merchantmen", "civ_fv_sidetrawler_armed", "picket",
          name="Trawler Al-Noor 7", nation="Meridian", weapons="Hold",
          route=[(24.66, 66.70, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_dhow", "dhows", name="Dhow Al-Madina",
          nation="Pakistan", route=[(24.40, 66.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_dhow", "dhows", name="Dhow Sea Pearl",
          nation="Pakistan", route=[(24.45, 66.62, 0)], telegraph=2),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "freighter",
          name="MV Gulf Courier (Karachi for Jebel Ali)", nation="Panama",
          route=[(24.30, 66.20, 0)], telegraph=3),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Karachi-Dubai service", squadron="Squadron29",
          airway=(25.25, 55.36)),  # Dubai
    ],
    resolve={"Convoy": "victory", "Traffic": "neutral",
             "Ships": ("protect", "convoy#1", "convoy#2"),
             "Raiders": ("destroy", "raiders", 2)},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True, allow=list(OPENING),
                flights=[HELO],
                situation=(
                    "Commander Pakistan Fleet has released Task Force 88. Choose its ships "
                    "and their flights: the Tughril-class frigates, PNS Alamgir, and the "
                    "Z-9CE and Sea King. The Air Force's JF-17s and ZDK-03 are not released "
                    "before Gwadar Roads. Every force allocation in this campaign rearms the "
                    "ships at Karachi."
                )),
    role="escort",
)
