"""SL05A - The Drone Yard. Cagayan de Tawi-Tawi (Mapun), 12 November 2028.

A strike, and the last side operation before the Aborlan Battery. The jet
drones that sank two coasters off Pearl Bank last week fly from a yard on
Mapun, the lonely island in the middle of the Sulu Sea: two Shahed 238
launchers (iran-shahed-238, the first SEST mission to field them), a
Shahed-136 rail and two guns. A Navy-chartered coaster for Balabac passes
fifty miles north-east of it at dawn, and Meridian's spotter drone goes up
at ten minutes past. Two FA-50s out of Puerto Princesa have until the drone
finds her.

Fixed force, like the other side operations: the strike pair, BRP Artemio
Ricarte and the coaster are the mission's own.

Striking the yard is what keeps the Shahed-136 rail off the Aborlan coast
in SL06 (SLYardStruck): what is not destroyed on Mapun moves to Palawan.
"""
from campaign_data import U, S

MISSION = dict(
    code="SL05A", series="Sulu Line", seq="SULU LINE  ·  OPTIONAL",
    group="optional", num="05A", key="The Drone Yard", place="Cagayan de Tawi-Tawi",
    geography="coast",
    intro=(
        "The jet drones that sank two coasters last week fly from a yard on Mapun. A Navy "
        "charter passes it at dawn. Two FA-50s have until Meridian's spotter finds her."
    ),
    special=(
        "The Air Force has offered a strike pair against a Meridian drone yard on Mapun. Its"
        " own aircraft fly it, not yours. The offer closes when The Aborlan Battery is "
        "complete."
    ),
    sender="Tactical Operations Group West, Philippine Air Force",
    intent=((
        "Destroy the drone launchers on Mapun before they fire on the charter. When their "
        "spotter goes up it will find her in minutes; after that every launcher left is a "
        "drone in the air. Take the guns if they shoot at you and the drone if you can. The "
        "village is at the north end of the island: put nothing there."
    )),
    date=(2028, 11, 12), time=(5, 30), sea=2, clouds="Scattered_2", wind="NE",
    difficulty=3, minutes=90, centre=(7.30, 118.70),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "SULU SEA, 0530. Two coasters were sunk off Pearl Bank last week by drones that "
            "flew faster than anything the network has used before: Shahed 238s, the jet "
            "version. Signals put their yard on Cagayan de Tawi-Tawi, the island the charts "
            "call Mapun, a hundred and sixty miles from anywhere. The Air Force has imagery of"
            " two launchers and a rail at the south end of the island, and two guns.\\n\\n"
            "MV Pag-asa Uno, chartered by the Navy with stores for Balabac, is fifty miles "
            "north-east of Mapun with BRP Artemio Ricarte. She cannot change her route without"
            " losing a day. Meridian's spotter drone flies from the same yard and is usually "
            "up by ten past the hour.\\n\\nTabak 11 and Tabak 12 are inbound from Puerto "
            "Princesa with precision bombs. Weapons Free on the yard. The village of Mapun is "
            "at the north end of the island and the fishing boats are off it."
        )),
    forces=(
        "Tabak 11 and 12, two FA-50PH out of Puerto Princesa; BRP Artemio Ricarte escorting "
        "the Navy charter MV Pag-asa Uno. Opposing: two Shahed 238 launchers, a Shahed-136 "
        "rail, two anti-aircraft guns and a spotter drone. Neutral: the Mapun fishing boats."
    ),
    objectives=[
        ("Yard", "Destroy the drone launchers on Mapun", "35,-35,Fail,Main"),
        ("Charter", "MV Pag-asa Uno is not lost", "15,-30,Complete"),
        ("Spotter", "Shoot down the spotter drone", "10,0,None"),
        ("Guns", "Silence the yard's guns", "5,0,None"),
        ("Traffic", "Harm no fishing boat", "0,-40,Complete"),
    ],
    victory=dict(kind="destroy", stations=["launchers"], min_units=3, objective="Yard",
                 sets="SLYardStruck"),
    neutral_objective="Traffic",
    win=(
        "The yard on Mapun is burning and the charter is on her way to Balabac. Whatever "
        "Meridian flies next will have to come from somewhere further away."
    ),
    lose=(
        "The yard is still there, or the charter is not. What is left on Mapun will be on "
        "Palawan within the week."
    ),
    timeout="{deadline_clock}, and the launchers on Mapun are still standing. The charter is out"
            " of the strike pair's reach, and the drones are not.",
    stations={
        "tabak": S(7.62, 118.62, "Tabak flight", heading=190, alt=15000),
        "charter": S(7.62, 119.02, "Charter", heading=60),
        "ricarte": S(7.66, 118.98, "Artemio Ricarte", heading=60),
        "launchers": dict(S(7.005, 118.505, "Launch site"), coastal=True),
        "guns": dict(S(7.015, 118.470, "Guns"), coastal=True),
        "drone": S(7.10, 118.55, "Spotter drone", heading=60, alt=8000),
        "bancas": S(7.10, 118.45, "Fishing boats", heading=0),
        "home": S(9.74, 118.75, "Puerto Princesa"),
    },
    units=[
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "tabak", squadron="Squadron1",
          name="Tabak 11", alt=15000, loadout="StrikePrecision"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "tabak", squadron="Squadron1",
          name="Tabak 12", alt=15000, loadout="StrikePrecision"),
        U("blue", "philippines-luzon-line", "phl_pt_jacinto", "ricarte", variant="Variant3",
          route=[(7.95, 119.45, 0)], telegraph=3),
        U("blue", "_vanilla", "civ_ms_freighter_a", "charter",
          name="MV Pag-asa Uno (Navy charter)", nation="Philippines", weapons="Hold",
          route=[(7.92, 119.42, 0)], telegraph=3),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Puerto Princesa", nation="Philippines", weapons="Hold"),
        U("red", "iran-shahed-238", "wp_shahed238_launcher", "launchers",
          name="Jet launcher ONE", nation="Panama"),
        U("red", "iran-shahed-238", "wp_shahed238_launcher", "launchers",
          name="Jet launcher TWO", nation="Panama"),
        U("red", "shahed-136-zero-two", "shahed_tel_black", "launchers",
          name="Launch rail", nation="Panama"),
        U("red", "_vanilla", "pla_aaa_type55", "guns", name="Gun north", nation="Panama"),
        U("red", "_vanilla", "pla_spaag_type63", "guns", name="Gun south", nation="Panama"),
        # The yard's eyes: up at minute 10, over the lane to the charter.
        U("red", "small-medium-uav-series", "usn_ForpostR705", "drone",
          name="Spotter drone", nation="Panama", weapons="Hold",
          route=[(7.40, 118.85, 8000), (7.60, 119.10, 8000)], loop=True, enter=10),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "bancas",
          name="Banca Mapun Pride", route=[(7.15, 118.40, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "bancas",
          name="Banca Sitti Nurhaya", route=[(7.12, 118.55, 0)], telegraph=1),
    ],
    resolve={"Yard": "victory", "Traffic": "neutral",
             "Charter": ("protect", "charter"),
             "Spotter": ("destroy", "drone", 1),
             "Guns": ("destroy", "guns", 2)},
    declares=["SLYardStruck"],
    expires_after="The Aborlan Battery",
    window=dict(),
    role="strike",
)
