"""SL05 - Celebes Gate. Basilan Strait and the Celebes Sea, 9 November 2028.

Interdiction among traffic. The Meridian network's guns for Jolo come in
from the Celebes Sea on an armed coaster that looks like every other
coaster: one of four hulls running north for the Basilan Strait with an
Indonesian ferry and the Zamboanga-Sandakan service in the same water.
Classify her, then stop her before she reaches the strait. Her escort is a
fast attack craft and a spotter drone.

Recon role: the hard part is the picture, and a ship sunk by mistake is a
neutral lost and the mission with it.
"""
from campaign_data import U, F, S
from .tables import HELO, ATTACK

MISSION = dict(
    code="SL05", series="Sulu Line", seq="SULU LINE  ·  MISSION 5",
    group="core", num="05", key="Celebes Gate", place="Celebes Sea",
    intro=(
        "One of four coasters running north for the Basilan Strait is carrying Jolo's next "
        "guns. Find the right one."
    ),
    sender="Naval Forces West; Naval Intelligence and Security Force",
    intent=((
        "Stop the gun-runner before she reaches the strait. Classify before you shoot: three"
        " of the four are what they say they are, and so is the ferry. Her escort will "
        "fight; she will run. Do it with as little as you can - the next supply ship is a "
        "week away."
    )),
    date=(2028, 11, 9), time=(5, 50), sea=3, clouds="Scattered_1", wind="NE",
    difficulty=3, minutes=100, centre=(5.75, 122.6),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "CELEBES SEA, 0550. Naval intelligence has a source in Bitung who says the "
            "weapons for Jolo left last night on a coaster under the Panama flag, armed and "
            "escorted. Four coasters are running north for the Basilan Strait this morning, "
            "with the Bitung-Zamboanga ferry and the Sandakan service in the same water.\\n"
            "\\nThe source does not know which coaster. Classify them. The one with an armed "
            "escort and a spotter drone over her is the one, but the escort will try to stay"
            " clear of her. Stop her before she reaches the strait.\\n\\nYour ships are "
            "weapons Free. A neutral sunk by mistake ends the mission and gives Meridian the "
            "story it wants. The group has had one rearm in a month; spend accordingly."
        )),
    forces=(
        "Your task group, its aircraft and any supply ships you own. Opposing: an armed "
        "coaster under the Panama flag, one Meridian fast attack craft and a spotter drone. "
        "Neutral: three coasters, the Bitung-Zamboanga ferry and the Sandakan service."
    ),
    special="Classify before you fire: the gun-runner is one of four coasters.",
    objectives=[
        ("Runner", "Stop the gun-runner before she reaches the Basilan Strait",
         "35,-35,Fail,Main"),
        ("Identify", "Classify the gun-runner", "15,0,None"),
        ("Escort", "Sink her escort", "10,0,None"),
        ("Traffic", "Harm no coaster, ferry or airliner that is what it says it is",
         "0,-40,Complete"),
    ],
    victory=dict(kind="destroy", stations=["runner"], min_units=1, objective="Runner"),
    denied=[dict(units=["runner"], at=(6.50, 121.90), radius=8, objective="Runner",
                 message=(
                     "The gun-runner has reached the Basilan Strait and the coast. Whatever she"
                     " carried is ashore on Jolo by tonight."
                 ))],
    neutral_objective="Traffic",
    win=(
        "The gun-runner is stopped short of the strait. What comes ashore on Jolo this "
        "month will be what Meridian already had."
    ),
    lose=(
        "The gun-runner is through. The ridge above Patikul will be armed again by the end "
        "of the week, and the Marines know it."
    ),
    timeout="{deadline_clock}, and the gun-runner is still a coaster among coasters. She will be in"
            " the strait after dark.",
    stations={
        # The group on the proven water south of Zamboanga, the coasters
        # spread across the lane to the south of it.
        "patrol": S(5.79, 122.87, "Patrol", heading=180),
        "flight": S(5.76, 122.85, "Ship's flight", heading=180, alt=500),
        "strike": S(7.10, 122.15, "Strike flight", heading=180, alt=3000),
        "runner": S(5.52, 122.89, "Coaster", heading=330),
        "escort": S(5.60, 122.30, "Meridian boat", heading=60),
        "drone": S(5.40, 122.60, "Drone", heading=0, alt=9000),
        "coasters": S(5.63, 122.94, "Coasters", heading=330),
        "ferry": S(5.68, 122.99, "Ferry", heading=320),
        "airliner": S(6.40, 122.30, "Sandakan service", heading=240, alt=30000),
        "home": S(6.92, 122.06, "Zamboanga"),
    },
    units=[
        U("blue", "euromod-philippines", "pn_ffg-150", "patrol", variant="Variant1"),
        U("blue", "philippines-luzon-line", "phl_h-76", "flight", squadron="Squadron1",
          alt=500, loadout="CAS", slot="HeloRecon"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "strike", squadron="Squadron1",
          alt=3000, loadout="CAS", slot="Attack"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "strike", squadron="Squadron1",
          alt=3000, loadout="CAS", slot="Attack"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Zamboanga (Edwin Andrews Air Base)", nation="Philippines", weapons="Hold"),
        # Hold, and her role is Spy: she runs, she does not open the fight.
        U("red", "auxilliary-merchant-pack", "ran_ms_super_p", "runner",
          name="MV Ocean Grace", nation="Panama", weapons="Hold",
          route=[(6.50, 121.90, 0)], telegraph=4),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "escort", name="Meridian Escort 18",
          nation="Panama", route=[(5.90, 122.50, 0)], telegraph=3),
        U("red", "small-medium-uav-series", "usn_ForpostR705", "drone",
          name="Spotter drone", nation="Panama", weapons="Hold",
          route=[(5.70, 122.70, 9000), (5.40, 122.60, 9000)], loop=True),
        U("neutral", "_vanilla", "civ_ms_freighter_a", "coasters",
          name="KM Sinar Bitung", route=[(6.60, 122.00, 0)], telegraph=3),
        U("neutral", "re-power-resupply", "civ_ms_freighter_b", "coasters",
          name="MV Zamboanga Express", route=[(6.80, 121.95, 0)], telegraph=3),
        U("neutral", "re-power-resupply", "civ_ms_freighter_d", "coasters",
          name="KM Tahuna Jaya", route=[(6.55, 121.80, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_roro_b", "ferry",
          name="KM Lambelu (Bitung-Zamboanga ferry)", route=[(6.85, 122.05, 0)],
          telegraph=3),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airliner",
          name="Zamboanga-Sandakan service", squadron="Squadron50",
          airway=(5.90, 118.06)),  # Sandakan
    ],
    resolve={"Runner": "victory", "Traffic": "neutral",
             "Identify": ("classify", "runner", 1),
             "Escort": ("destroy", "escort", 1)},
    declares=[],
    window=dict(buy=False, repair=True, flights=[HELO, ATTACK],
                situation=(
                    "No reinforcements and no rearming before Celebes Gate. Repairs are "
                    "available. What the group took from Sulu Provider is what it has, with "
                    "whatever is left in its own supply ships."
                )),
    role="recon",
)
