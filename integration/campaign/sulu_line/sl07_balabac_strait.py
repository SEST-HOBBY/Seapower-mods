"""SL07 - Balabac Strait. Balabac Strait, 23 November 2028.

The day the closure was enforced. Red Line's group commander was told on the
22nd to enforce it in the Banda approaches; the same order reached the
southern surface group in the South China Sea, which comes east for the
Balabac Strait to close the island road's western door. The coalition's
convoy is at the Balabac anchorage. The task group meets the surface group
in the strait with whatever is left in its magazines and its supply ships -
the campaign's one fleet action, and the reason the six missions before it
were about not firing what was not needed.

Fleet role. The PLAN group comes in from the west with a strike regiment
behind it; three of its five ships sunk, or the strait held, wins it.
"""
from campaign_data import U, F, S
from .tables import HELO, ATTACK

MISSION = dict(
    code="SL07", series="Sulu Line", seq="SULU LINE  ·  MISSION 7",
    group="core", num="07", key="Balabac Strait", place="Balabac Strait",
    intro=(
        "The Chinese southern surface group is coming east to close the Balabac Strait. "
        "Hold it with what is left in the magazines."
    ),
    sender="Naval Forces West",
    intent=((
        "The strait stays open and the convoy at the anchorage stays afloat. The surface "
        "group has been ordered to close the strait and will fire to do it; you are weapons"
        " Free. Sink three of its five ships and it turns back. Keep your supply ships out "
        "of the fight and close enough to reach - this is what they were for."
    )),
    date=(2028, 11, 23), time=(5, 30), sea=3, clouds="Overcast", wind="NE",
    difficulty=5, minutes=130, centre=(7.9, 116.8),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "BALABAC STRAIT, 0530, 23 NOVEMBER. At 0300 Beijing announced the closure of "
            "the southern passages to coalition shipping 'for the period of the "
            "negotiations'. The southern surface group - a Type 052D, two Type 054A and two"
            " Type 056A - is in the South China Sea seventy miles west of the strait, coming"
            " east. A JH-7A strike regiment is airborne from Mischief Reef.\\n\\nThe "
            "convoy for Balabac and the Sulu is at the anchorage east of the strait. If the"
            " surface group gets through, it closes the island road from the west, and "
            "everything the group has fought for since October goes with it.\\n\\nHold the "
            "strait. Three of the five ships sunk will turn the group back. Your ships are "
            "weapons Free. There is no rearm after this: what is in the magazines and the "
            "supply ships is the whole war. A submarine was reported in the strait two "
            "days ago and has not been seen since."
        )),
    forces=(
        "Your task group, its aircraft and its supply ships. At the anchorage: the Balabac "
        "convoy. Opposing: a Type 052D, two Type 054A and two Type 056A, a JH-7A strike "
        "regiment and possibly a Type 039C submarine. Neutral: fishing boats."
    ),
    special="The fleet action: the surface group turns back when three of its five ships "
            "are sunk.",
    objectives=[
        ("Strait", "Sink three of the five ships of the surface group", "40,-40,Fail,Main"),
        ("Convoy", "Keep the convoy at the anchorage afloat", "20,-30,Complete"),
        ("Flagship", "Sink the Type 052D", "15,0,None"),
        ("Traffic", "Harm no fishing boat", "0,-30,Complete"),
    ],
    victory=dict(kind="destroy", stations=["sag"], min_units=3, objective="Strait"),
    fatal=[F("Convoy", ["convoy#1", "convoy#2"], 2)],
    neutral_objective="Traffic",
    win=(
        "The surface group has turned west with three ships left behind it. The strait is "
        "open. The convoy sails for Balabac at noon, and the ceasefire talks have a new map."
    ),
    lose=(
        "The strait is closed. The convoy is lost or turned back, and the island road is "
        "shut from the west for the rest of the war."
    ),
    timeout="{deadline_clock}, and the surface group is still in the strait. The convoy will not "
            "sail.",
    stations={
        # The strait's eastern mouth and the anchorage beyond it, on the
        # proven water of the Palawan Passage scenarios; the surface group
        # 70 NM west in the South China Sea.
        "screen": S(7.99, 117.16, "Screen", heading=270),
        "flight": S(8.00, 117.13, "Ship's flight", heading=270, alt=500),
        "strike": S(9.70, 118.80, "Strike flight", heading=230, alt=3000),
        "convoy": S(8.03, 117.56, "Anchorage", heading=270),
        "sag": S(7.71, 115.80, "Surface group", heading=90),
        "red_sub": S(7.57, 116.40, "Submarine", heading=60),
        "red_air": S(9.90, 115.30, "Strike regiment", heading=150, alt=6000),
        "fishing": S(7.83, 116.63, "Fishing boats", heading=180),
        "home": S(9.74, 118.75, "Puerto Princesa"),
    },
    units=[
        U("blue", "euromod-philippines", "pn_ffg-150", "screen", variant="Variant1"),
        U("blue", "philippines-luzon-line", "phl_h-76", "flight", squadron="Squadron1",
          alt=500, loadout="CAS", slot="HeloRecon"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "strike", squadron="Squadron1",
          alt=3000, loadout="CAS", slot="Attack"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "strike", squadron="Squadron1",
          alt=3000, loadout="CAS", slot="Attack"),
        U("blue", "_vanilla", "civ_ms_roro_c", "convoy", name="MV Palawan Pioneer",
          nation="Philippines", weapons="Hold"),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Princesa Star",
          nation="Philippines", weapons="Hold"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Puerto Princesa (Antonio Bautista Air Base)", nation="Philippines",
          weapons="Hold"),
        U("red", "modern-plan-systems", "plan_type_052d_p3", "sag",
          name="Type 052D (the flagship)", route=[(7.95, 117.00, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "sag", variant="Variant1",
          route=[(7.90, 117.00, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "sag", variant="Variant3",
          route=[(8.00, 117.00, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_056a", "sag", variant="Variant1",
          route=[(7.85, 116.95, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_056a", "sag", variant="Variant3",
          route=[(8.05, 116.95, 0)], telegraph=3),
        U("red", "plan-submarines", "plan_ss_type_039c", "red_sub", depth="belowlayer",
          route=[(7.90, 116.90, "belowlayer")], telegraph=2),
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike 31", loadout="AntiShip",
          route=[(8.30, 116.40, 6000), (8.00, 117.30, 3000)], telegraph=3),
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike 32", loadout="AntiShip",
          route=[(8.30, 116.40, 6000), (8.00, 117.30, 3000)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Banca Balabac Star", route=[(7.70, 116.80, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "fishing",
          name="Fishing boat Hoang Sa 27 (Vietnam)", route=[(7.95, 116.30, 0)], telegraph=2),
    ],
    resolve={"Strait": "victory", "Traffic": "neutral",
             "Convoy": ("protect", "convoy#1", "convoy#2", 2),
             "Flagship": ("destroy", "sag#1", 1)},
    declares=[],
    window=dict(buy=False, repair=True, flights=[HELO, ATTACK],
                situation=(
                    "No reinforcements and no rearming before the strait. Repairs are "
                    "available. The force sails with what its magazines and its supply ships"
                    " hold."
                )),
    role="fleet",
)
