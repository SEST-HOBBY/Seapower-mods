"""SL03 - Ayungin. Second Thomas Shoal, West Philippine Sea, 26 October 2028.

The rotation-and-resupply run to BRP Sierra Madre, the grounded landing ship
the Marines hold on Ayungin Shoal. Two China Coast Guard cutters (converted
Type 056 corvettes, as the real ones are) and three militia trawlers are
between the boat and the shoal; a PLAN frigate is watching from the north.
None of them will fire. Neither will the task group: the boat gets through
by being escorted, not by shooting, and anything fired here is a provocation
and a round the supply ships have to replace.

Every Chinese hull is a `spare` with a fatal entry. The win is the boat in
the shoal's lagoon.
"""
from campaign_data import U, F, S
from .tables import HELO

MISSION = dict(
    code="SL03", series="Sulu Line", seq="SULU LINE  ·  MISSION 3",
    group="core", num="03", key="Ayungin", place="West Philippine Sea",
    intro=(
        "The resupply boat for the Marines on Ayungin Shoal, with two coast guard cutters "
        "and three militia trawlers in the way. Nobody fires."
    ),
    sender="Naval Forces West; Western Command",
    intent=((
        "The boat reaches the shoal. Escort it, put your hulls between it and the cutters, "
        "and fire on nothing: the coast guard and the militia are not shooting, and the "
        "first shot fired here would be ours. The frigate to the north is watching for it."
    )),
    date=(2028, 10, 26), time=(6, 0), sea=2, clouds="Clear", wind="NE",
    difficulty=3, minutes=100, centre=(9.75, 116.1),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "WEST PHILIPPINE SEA, 0600. M/L KALAYAAN, a chartered supply boat with the "
            "Marines' rotation, water and rations, is twenty-four miles east of Ayungin "
            "Shoal. BRP SIERRA MADRE has been aground in the lagoon since 1999 and her "
            "detachment has not been resupplied in five weeks.\\n\\nTwo China Coast Guard "
            "cutters and three militia trawlers are between the boat and the shoal, as "
            "they were the last three times. A PLAN frigate is holding north of the shoal, "
            "towards Mischief Reef, and a patrol aircraft is overhead.\\n\\nTake the boat "
            "into the lagoon. Your ships start at weapons Hold. Nobody here is going to "
            "shoot, and if the task group does it will have started something the Navy "
            "cannot finish this week. Use your hulls and your helicopter. Fishing boats are "
            "working the reef."
        )),
    forces=(
        "Your task group and its helicopter. Escorted: M/L Kalayaan. Opposing, not "
        "shooting: two China Coast Guard cutters, three militia trawlers, a PLAN Type 054A "
        "frigate and a Y-8 patrol aircraft. Neutral: fishing boats."
    ),
    special="No shot fired: every Chinese hull and the aircraft are protected by the ROE.",
    objectives=[
        ("Resupply", "Bring M/L Kalayaan into Ayungin's lagoon", "35,-35,Fail,Main"),
        ("Boat", "Keep the supply boat afloat", "15,-30,Complete"),
        ("Restraint", "Fire on nothing: not the cutters, the trawlers, the frigate or the "
                      "aircraft", "20,-40,Complete"),
        ("Traffic", "Harm no fishing boat", "0,-30,Complete"),
        ("Watchers", "Classify the PLAN frigate to the north", "10,0,None"),
    ],
    victory=dict(kind="arrive", station="boat", min_units=1, at=(9.73, 115.87),
                 radius=3, objective="Resupply"),
    fatal=[F("Boat", ["boat"]),
           F("Restraint", ["ccg", "militia", "frigate", "red_air"])],
    neutral_objective="Traffic",
    win=(
        "KALAYAAN is in the lagoon and alongside SIERRA MADRE. The Marines have their water "
        "and their relief. The cutters have gone back to station. Nothing was fired."
    ),
    lose=(
        "The run to Ayungin has failed. The detachment on SIERRA MADRE will go another week "
        "without relief, and Manila is asking what was fired."
    ),
    timeout="{deadline_clock}, and KALAYAAN is still outside the lagoon. The tide will not let her "
            "in again today.",
    stations={
        # Everything east of the shoal is on proven water out of the
        # Spratly scenarios; the shoal itself is the victory box.
        "escort": S(9.69, 116.25, "Escort", heading=270),
        "flight": S(9.70, 116.22, "Ship's flight", heading=270, alt=500),
        "boat": S(9.72, 116.10, "M/L Kalayaan", heading=265),
        "ccg": S(9.76, 116.00, "Coast guard cutters", heading=90),
        "militia": S(9.66, 115.98, "Militia trawlers", heading=60),
        "frigate": S(10.24, 115.94, "PLAN frigate", heading=180),
        "red_air": S(10.10, 115.70, "Patrol aircraft", heading=90, alt=15000),
        "fishing": S(9.78, 116.15, "Fishing boats", heading=200),
        "home": S(9.74, 118.75, "Puerto Princesa"),
    },
    units=[
        U("blue", "euromod-philippines", "pn_ffg-150", "escort", variant="Variant1",
          weapons="Hold"),
        U("blue", "philippines-luzon-line", "phl_h-76", "flight", squadron="Squadron1",
          alt=500, weapons="Hold", loadout="CAS", slot="HeloRecon"),
        U("blue", "_vanilla", "civ_fv_sterntrawler_b", "boat", name="M/L Kalayaan",
          nation="Philippines", weapons="Hold", route=[(9.73, 115.87, 0)], telegraph=3),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Puerto Princesa (Antonio Bautista Air Base)", nation="Philippines",
          weapons="Hold"),
        # The China Coast Guard's 056s are converted PLAN corvettes; the file
        # is the corvette, the name and the Hold are the coast guard's.
        U("red", "modern-plan-systems", "plan_type_056a", "ccg", variant="Variant1",
          name="CCG 6303", weapons="Hold", route=[(9.72, 116.02, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_056a", "ccg", variant="Variant2",
          name="CCG 6304", weapons="Hold", route=[(9.70, 116.05, 0)], telegraph=3),
        U("red", "_vanilla", "civ_fv_sterntrawler_a", "militia", name="Qiong Sansha Yu 00213",
          weapons="Hold", route=[(9.70, 116.06, 0)], telegraph=3),
        U("red", "_vanilla", "civ_fv_sterntrawler_c", "militia", name="Qiong Sansha Yu 00219",
          weapons="Hold", route=[(9.74, 116.04, 0)], telegraph=3),
        U("red", "_vanilla", "civ_fv_sterntrawler_d", "militia", name="Yue Tai Yu 18000",
          weapons="Hold", route=[(9.68, 116.00, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "frigate", variant="Variant2",
          weapons="Hold", radars="True"),
        U("red", "modern-plan-systems", "plan_y-8fq", "red_air", squadron="Squadron1", weapons="Hold",
          route=[(9.60, 116.40, 15000), (10.10, 115.70, 15000)], loop=True, telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_c", "fishing",
          name="Fishing boat Ngoc Lan (Vietnam)", route=[(9.85, 115.95, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Banca Joanna Marie", route=[(9.90, 116.20, 0)], telegraph=2),
    ],
    resolve={"Resupply": "victory", "Traffic": "neutral",
             "Boat": ("protect", "boat"),
             "Restraint": ("spare", "ccg", "militia", "frigate", "red_air"),
             "Watchers": ("classify", "frigate", 1)},
    declares=[],
    window=dict(buy=False, repair=True, flights=[HELO],
                situation=(
                    "No reinforcements and no rearming before Ayungin. Repairs are "
                    "available. This run is won without firing, so what the gun line spent "
                    "at Jolo does not matter today - but it will at the rendezvous."
                )),
    role="logistics",
)
