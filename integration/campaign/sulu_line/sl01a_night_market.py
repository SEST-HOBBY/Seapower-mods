"""SL01A - Night Market. North of Tawi-Tawi, 15 October 2028.

The first side operation, and the first step of the Night Market thread: the
drug money is what buys Meridian's guns. A semi-submersible is running
south through the Sulu Sea for the Tawi-Tawi coast with a load worth more
than the coasters SL05 hunts, among the night's fishing boats, with a hired
civilian helicopter as the runners' eye. Two fast boats wait off the coast
to take the load off her.

A fixed force flies it: the Navy's Tawi-Tawi patrol group (an old Jacinto-
class patrol ship, two Andrada patrol boats and a Navy helicopter out of
Sanga-Sanga), not the player's task group. Nothing the player owns sails,
so nothing it fires is gone from the campaign's no-free-rearm magazines.

Taking her is what SL03A The Okean starts from (SLNarcoTaken).

Geography: the Sulu Sea south of Jolo has almost no proven positions (four
sea points round Tawi-Tawi in every loading mission put together), so this
mission is proved against the coastline instead (geo/sulu_theatre_coast.json,
tools/make_coast_extract.py --box 116 3 127 12).
"""
from campaign_data import U, S

MISSION = dict(
    code="SL01A", series="Sulu Line", seq="SULU LINE  ·  OPTIONAL",
    group="optional", num="01A", key="Night Market", place="North of Tawi-Tawi",
    geography="coast",
    intro=(
        "A semi-submersible is running for the Tawi-Tawi coast tonight with the money behind"
        " Jolo's guns. The Navy's patrol group out of Bongao has one night to find her."
    ),
    special=(
        "Naval Forces Western Mindanao has asked for the Tawi-Tawi patrol group to be "
        "tasked against a narcotics run. Its own ships fly it, not yours. The request "
        "closes when Ayungin is complete."
    ),
    sender="Naval Forces Western Mindanao; Philippine Drug Enforcement Agency liaison",
    intent=((
        "Find the semi-submersible and stop her before she reaches the coast and the boats "
        "waiting for her. She is low, slow and quiet and will be in among the fishing fleet;"
        " the helicopter overhead is a charter the runners pay to watch for us. Take the "
        "boats too if you can. Harm no fisherman: they are the people this is for."
    )),
    date=(2028, 10, 15), time=(1, 40), sea=1, clouds="Scattered_1", wind="E",
    difficulty=2, minutes=110, centre=(5.62, 120.05),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "SULU SEA, NORTH OF TAWI-TAWI, 0140, flat calm and no moon. The Drug Enforcement "
            "Agency has a source in Sandakan who says a semi-submersible left the Sabah coast "
            "at dusk with a load for Tawi-Tawi: the kind of cargo that pays for what Meridian "
            "is putting ashore on Jolo. She sits a foot out of the water and makes thirteen knots.\\n"
            "\\nThe Navy's Tawi-Tawi patrol group has the night. BRP Emilio Jacinto is north-east"
            " of the route, BRP Jose Loor Sr. and BRP Juan Magluyan are working the fishing "
            "grounds to the west and north, and the Navy's helicopter is up out of "
            "Sanga-Sanga. About six fishing boats are out tonight, and the Bongao ferry is on "
            "its usual run.\\n\\nTwo fast boats are waiting off the north coast of Tawi-Tawi "
            "to take the load. A civilian AS350 has been circling the route since midnight; "
            "it is chartered, it is unarmed and it is watching for you. Weapons are Free on "
            "the semi-submersible and the pickup boats once classified. Nothing else."
        )),
    forces=(
        "The Tawi-Tawi patrol group: BRP Emilio Jacinto, the patrol boats Jose Loor Sr. and "
        "Juan Magluyan, and the Navy helicopter Tawi 21 out of Sanga-Sanga. Opposing: one "
        "semi-submersible, two pickup boats and a chartered civilian AS350. Neutral: six "
        "fishing boats and the Bongao-Zamboanga ferry."
    ),
    objectives=[
        ("Semisub", "Stop the semi-submersible before she reaches the Tawi-Tawi coast",
         "35,-35,Fail,Main"),
        ("Identify", "Classify the semi-submersible", "15,0,None"),
        ("Pickup", "Stop the pickup boats", "10,0,None"),
        ("Eye", "Classify the runners' spotter helicopter", "5,0,None"),
        ("Traffic", "Harm no fishing boat, ferry or civilian aircraft",
         "0,-40,Complete"),
    ],
    victory=dict(kind="destroy", stations=["semisub"], min_units=1, objective="Semisub",
                 sets="SLNarcoTaken"),
    denied=[dict(units=["semisub"], at=(5.40, 120.08), radius=5, objective="Semisub",
                 message=(
                     "The semi-submersible has reached the boats off Tawi-Tawi. The load is "
                     "ashore before dawn, and the money with it."
                 ))],
    neutral_objective="Traffic",
    win=(
        "The semi-submersible is stopped short of the coast. Whatever she carried is not "
        "going to buy anything on Jolo this month, and the Agency has her navigation set."
    ),
    lose=(
        "The load is ashore on Tawi-Tawi. Somebody in Bongao is counting money tonight, and "
        "some of it is going north to the ridge above Patikul."
    ),
    timeout="{deadline_clock}, and the semi-submersible is still somewhere among the fishing "
            "boats. She will make the coast before first light.",
    stations={
        # The run comes south-east from the Sabah side through open water
        # north of the Tawi-Tawi group; the pickup boats wait inshore of it.
        "jacinto": S(5.86, 120.30, "Emilio Jacinto", heading=230),
        "west": S(5.70, 119.70, "Patrol boat west", heading=120),
        "north": S(6.05, 119.95, "Patrol boat north", heading=180),
        "helo": S(5.30, 119.85, "Tawi 21", heading=20, alt=800),
        "semisub": S(5.78, 119.86, "Semi-submersible", heading=150),
        "pickup": S(5.42, 120.15, "Pickup boats", heading=300),
        "eye": S(5.70, 119.95, "Spotter helicopter", heading=0, alt=1500),
        "fleet_w": S(5.75, 119.88, "Fishing boats", heading=90),
        "fleet_e": S(5.60, 120.10, "Fishing boats", heading=270),
        "ferry": S(5.50, 119.85, "Bongao ferry", heading=40),
        "home": dict(S(5.046, 119.753, "Sanga-Sanga"), coastal=True),
    },
    units=[
        U("blue", "philippines-luzon-line", "phl_pt_jacinto", "jacinto", variant="Variant1"),
        U("blue", "philippines-luzon-line", "phl_pb_jose_andrada", "west",
          variant="Variant19"),
        U("blue", "philippines-luzon-line", "phl_pb_jose_andrada", "north",
          variant="Variant20"),
        U("blue", "philippines-luzon-line", "phl_h-76", "helo", squadron="Squadron2",
          name="Tawi 21", alt=800, loadout="CAS"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Sanga-Sanga (Bongao)", nation="Philippines", weapons="Hold", air_group=[]),
        U("red", "red-storm-arsenal", "_narco_narcosub_adv", "semisub",
          name="Contact NOVEMBER", depth="periscope",
          route=[(5.62, 119.96, "periscope"), (5.40, 120.08, "periscope")], telegraph=4),
        # Unarmed hulls that wait for her; they run when the patrol comes.
        U("red", "red-storm-arsenal", "_narco_speedboat", "pickup", name="Pickup boat 1",
          weapons="Hold", route=[(5.40, 120.08, 0)], telegraph=2),
        U("red", "red-storm-arsenal", "_narco_speedboat", "pickup", name="Pickup boat 2",
          weapons="Hold", route=[(5.40, 120.08, 0)], telegraph=2),
        # The runners' eye: a civilian charter on the opposing side, unarmed,
        # circling the route at 1,500 ft for the whole night.
        U("red", "civilian-as350", "civ_as-350", "eye", squadron="Squadron2",
          name="AS350 charter RP-C2817", nation="Pirates", alt=1500, weapons="Hold",
          route=[(5.80, 119.85, 1500), (5.55, 120.00, 1500)], loop=True),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fleet_w",
          name="Fishing boat Nur Jannah", route=[(5.75, 120.10, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fleet_w",
          name="Fishing boat Sitti Aisah", route=[(5.80, 120.05, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fleet_w",
          name="Fishing boat Bulan Sabit", route=[(5.68, 120.02, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fleet_e",
          name="Fishing boat Dayang", route=[(5.62, 119.90, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fleet_e",
          name="Fishing boat Mutiara", route=[(5.55, 119.95, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fleet_e",
          name="Fishing boat Tanah Laut", route=[(5.66, 119.92, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_ms_roro_b", "ferry",
          name="MV Lady Mary Joy (Bongao-Zamboanga)",
          route=[(5.70, 120.25, 0), (6.20, 120.80, 0)], telegraph=3),
    ],
    resolve={"Semisub": "victory", "Traffic": "neutral",
             "Identify": ("classify", "semisub", 1),
             "Pickup": ("destroy", "pickup", 1),
             "Eye": ("classify", "eye", 1)},
    declares=["SLNarcoTaken"],
    expires_after="Ayungin",
    window=dict(),
    role="patrol",
)
