"""SL01 - The Island Road. Sulu Sea off Puerto Princesa, 12 October 2028.

The first convoy of the season down the Sulu side of Palawan: a chartered
Ro-Ro with the Balabac outpost's stores and a coastal tanker with its fuel,
from Honda Bay to the head of the Balabac lane. Two Meridian fast attack
craft are coming up from Cagayancillo to look at it, and a trawler that is
not fishing has been keeping company since dawn.

The opening window is the only one in the campaign that rearms, and it
rearms nothing: every hull bought here arrives full. It is also the first of
the three windows that sell supply ships, and the briefing says so.
"""
from campaign_data import U, F, S
from .tables import HELO, OPENING

MISSION = dict(
    code="SL01", series="Sulu Line", seq="SULU LINE  ·  MISSION 1",
    group="core", num="01", key="The Island Road", place="Sulu Sea",
    intro=(
        "The season's first convoy for the Balabac outpost, with two Meridian boats coming up"
        " from the south to look at it."
    ),
    sender="Naval Forces West, Puerto Princesa",
    intent=((
        "The outpost at Balabac lives on this road. Bring both ships into the head of the "
        "lane. The Meridian boats are armed and have fired on a Navy patrol boat before; if "
        "they close the convoy, stop them. What your ships fire today they will not get back"
        " until a supply ship gives it to them, so fire what the job needs."
    )),
    date=(2028, 10, 12), time=(6, 40), sea=3, clouds="Scattered_1", wind="NE",
    difficulty=2, minutes=110, centre=(9.1, 118.6),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "SULU SEA, 0640. MV PALAWAN PIONEER and MT PRINCESA STAR sailed from Honda Bay at "
            "first light with the Balabac outpost's stores and fuel. They are the season's "
            "first convoy down the Sulu side of Palawan, and the only one this month. The "
            "outpost has eleven days of diesel left.\\n\\nTwo Meridian fast attack craft "
            "left Cagayancillo before dawn and are running north-west at speed. Meridian "
            "calls them escorts. One of them fired on BRP Kagitingan off Tubbataha in "
            "September. A trawler with no nets out has been keeping station on the convoy "
            "since it cleared the bay.\\n\\nBring both ships into the head of the Balabac "
            "lane, thirty miles south-west. Your ships are weapons Free. Nothing is "
            "rearmed after today: what you fire comes back only from a supply ship you "
            "own, alongside, at eight knots or less.\\n\\nFishing bancas and the "
            "Puerto Princesa-Cuyo ferry are on the water. Identify before you fire."
        )),
    forces=(
        "Your task group, with its helicopter if one is embarked and any supply ship you "
        "bought. Convoy: MV Palawan Pioneer and MT Princesa Star. Opposing: two Meridian fast "
        "attack craft and a trawler keeping company. Neutral: bancas and the Cuyo ferry. "
        "Puerto Princesa's field is open to your aircraft."
    ),
    special=(
        "No free rearm in this campaign. Supply ships are on sale here, before Service at Sea"
        " and before The Aborlan Battery, and nowhere else."
    ),
    objectives=[
        ("Convoy", "Bring the convoy into the head of the Balabac lane", "35,-35,Fail,Main"),
        ("Ships", "Lose neither convoy ship", "20,-30,Complete"),
        ("Raiders", "Sink the Meridian boats if they close", "10,0,None"),
        ("Traffic", "Harm no banca, ferry or airliner", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", min_units=2, at=(8.88, 118.42),
                 radius=10, objective="Convoy"),
    fatal=[F("Ships", ["convoy#1", "convoy#2"], 2)],
    neutral_objective="Traffic",
    win=(
        "PALAWAN PIONEER and PRINCESA STAR are in the head of the lane, and the outpost will "
        "have its diesel. Naval Forces West has the convoy's track and the Meridian boats' on "
        "one plot."
    ),
    lose=(
        "The convoy is broken. Balabac will be on rationed fuel by the end of the month, and "
        "the next ships will not sail without a bigger escort than the Navy has."
    ),
    timeout="{deadline_clock}, and the convoy is still short of the lane. The outpost's next delivery "
            "is now a week late.",
    stations={
        # Honda Bay's approach, on proven water, with the convoy two miles
        # inside the screen and the ship's flight between them.
        "screen": S(9.28, 118.47, "Screen", heading=210),
        "flight": S(9.27, 118.50, "Ship's flight", heading=210, alt=500),
        "convoy": S(9.36, 118.65, "Convoy", heading=215),
        # The Meridian pair, 40 NM south-east, out of Cagayancillo.
        "raiders": S(8.72, 119.05, "Meridian boats", heading=300),
        "trawler": S(9.15, 118.62, "Trawler", heading=210),
        "bancas": S(9.02, 118.60, "Bancas", heading=90),
        "ferry": S(9.21, 118.94, "Cuyo ferry", heading=40),
        "home": S(9.74, 118.75, "Puerto Princesa"),
    },
    units=[
        U("blue", "euromod-philippines", "pn_ffg-150", "screen", variant="Variant1"),
        U("blue", "philippines-luzon-line", "phl_h-76", "flight", squadron="Squadron1",
          alt=500, loadout="CAS", slot="HeloRecon"),
        U("blue", "_vanilla", "civ_ms_roro_c", "convoy", name="MV Palawan Pioneer",
          nation="Philippines", weapons="Hold", route=[(8.86, 118.42, 0)], telegraph=3),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Princesa Star",
          nation="Philippines", weapons="Hold", route=[(8.90, 118.40, 0)], telegraph=3),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Puerto Princesa (Antonio Bautista Air Base)", nation="Philippines",
          weapons="Hold"),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raiders", name="Meridian Escort 11",
          nation="Panama", route=[(9.10, 118.55, 0)], telegraph=4),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raiders", name="Meridian Escort 12",
          nation="Panama", route=[(9.05, 118.50, 0)], telegraph=4),
        U("red", "_vanilla", "civ_fv_sterntrawler_a", "trawler", name="Trawler Yue Hai 2207",
          nation="China", weapons="Hold", route=[(8.95, 118.48, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "bancas",
          name="Banca Maria Theresa", route=[(9.00, 118.75, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "bancas",
          name="Banca Ginintuan", route=[(8.95, 118.70, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_roro_c", "ferry",
          name="MV Cuyo Star (Puerto Princesa-Cuyo ferry)", route=[(10.80, 121.0, 0)],
          telegraph=3),
    ],
    resolve={"Convoy": "victory", "Traffic": "neutral",
             "Ships": ("protect", "convoy#1", "convoy#2", 2),
             "Raiders": ("destroy", "raiders", 2)},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True, allow=list(OPENING),
                flights=[HELO],
                situation=(
                    "Naval Forces West has released the task group. Choose its ships and the "
                    "helicopter. Supply ships are on sale now: BRP Tarlac or Davao del Sur, "
                    "and the Thai oiler Chula. After this window nothing is rearmed for free, "
                    "and supply ships are sold again only before Service at Sea and before "
                    "The Aborlan Battery."
                )),
    role="escort",
)
