"""SL03A - The Okean. The Sibutu Passage, 29 October 2028.

The second step of the Night Market thread. What the drug money buys comes
back the same way: a Meridian trawler up from the Celebes Sea through the
Sibutu Passage, to hand rifles, mortars and drone parts to fast boats for
the Tawi-Tawi coast. She looks like every Okean-class trawler working the
passage, and two real ones are working it tonight. She is not like them:
she carries a hidden torpedo tube (Project 2498's civ_fv_okean_surprise),
and when she reaches the boats she will use it on whoever is closest.

Fixed force again: the Tawi-Tawi patrol group's other ships, not the
player's task group. If Night Market took the semi-submersible
(SLNarcoTaken), her navigation set gave the Agency this trawler's name and
the patrol starts with her classified.

Stopping her is what keeps the spotter drone off Celebes Gate
(SLOkeanTaken): the network loses the money and the eyes together.
"""
from campaign_data import U, S

MISSION = dict(
    code="SL03A", series="Sulu Line", seq="SULU LINE  ·  OPTIONAL",
    group="optional", num="03A", key="The Okean", place="The Sibutu Passage",
    geography="coast",
    intro=(
        "A Meridian trawler is coming up the Sibutu Passage tonight with what the drug money "
        "bought. Two real trawlers are in the same water. Find the one that is not."
    ),
    special=(
        "Naval Forces Western Mindanao has asked for the Tawi-Tawi patrol group to stop an "
        "arms delivery in the Sibutu Passage. Its own ships fly it, not yours. The request "
        "closes when Service at Sea is complete."
    ),
    sender="Naval Forces Western Mindanao",
    intent=((
        "Stop the trawler before she reaches the boats waiting for her. She is one of three "
        "Okean-class trawlers in the passage and the other two are fishing. She is armed with"
        " something we have not seen; keep your distance until you know which she is, then "
        "do not give her the chance. The helicopter shuttling to her is Meridian's. The "
        "Malaysian side of the passage is theirs: stay in our water."
    )),
    date=(2028, 10, 29), time=(3, 20), sea=2, clouds="Broken_2", wind="SW",
    difficulty=3, minutes=120, centre=(4.80, 119.35),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "SIBUTU PASSAGE, 0320. Signals and a fisherman in Sitangkai agree that a trawler "
            "under the Panama flag came out of Tarakan two days ago and is coming north up the"
            " passage tonight, low in the water. Two fast boats left Tawi-Tawi at midnight and "
            "are waiting for her west of Sibutu. What she carries was bought with the money "
            "that rides the semi-submersibles: rifles, mortars, parts for the drones on the "
            "Jolo ridge.\\n\\nTwo other Okean-class trawlers are fishing the passage tonight, "
            "both Philippine. A container ship is northbound for Sandakan's anchorage and a "
            "Malaysian tanker is going south. A helicopter has been flying from the Sabah "
            "side to a point in the passage and back since 0200 without a flight plan.\\n\\n"
            "BRP Apolinario Mabini is east of the passage, BRP Florencio Inigo in it to the "
            "south, and Tawi 22 is up out of Sanga-Sanga. Weapons are Free on the trawler, the"
            " boats and the helicopter once each is classified. Fishermen in Sitangkai say she"
            " has a tube in her stern housing. Believe them."
        )),
    forces=(
        "The Tawi-Tawi patrol group: BRP Apolinario Mabini, the patrol boat Florencio Inigo "
        "and the Navy helicopter Tawi 22 out of Sanga-Sanga. Opposing: one armed trawler under"
        " the Panama flag, two fast boats and a Bell 212 helicopter. Neutral: two fishing "
        "trawlers, a container ship and a tanker."
    ),
    objectives=[
        ("Trawler", "Stop the armed trawler before she reaches the boats",
         "35,-35,Fail,Main"),
        ("Identify", "Classify the armed trawler", "15,0,None"),
        ("Boats", "Stop the fast boats", "10,0,None"),
        ("Shuttle", "Classify the shuttle helicopter", "5,0,None"),
        ("Patrol", "Bring BRP Apolinario Mabini home", "10,-15,Complete"),
        ("Traffic", "Harm no fishing trawler or merchant ship", "0,-40,Complete"),
    ],
    victory=dict(kind="destroy", stations=["okean"], min_units=1, objective="Trawler",
                 sets="SLOkeanTaken"),
    denied=[dict(units=["okean"], at=(4.98, 119.30), radius=4, objective="Trawler",
                 message=(
                     "The trawler is alongside the boats west of Sibutu and the crates are "
                     "going over. By dawn they are on Tawi-Tawi; by the end of the week, on "
                     "Jolo."
                 ))],
    neutral_objective="Traffic",
    reveal_if=[dict(variable="SLNarcoTaken", units=["okean"], level="Classify",
                    intel=(
                        "PDEA: The semi-submersible's navigation set had one name in it twice: "
                        "the trawler Hai Xing 7. She is the one coming north. Her position is "
                        "on your plot."
                    ))],
    win=(
        "The trawler is stopped short of the boats. The Agency will spend a month on what "
        "comes up from her hold. Meridian has lost the cargo and the money that bought it."
    ),
    # Losing Mabini fails Patrol and ends nothing; the mission is lost with
    # both patrol ships, or when the trawler makes the boats (its own text).
    lose=(
        "The trawler made her rendezvous, or the patrol lost both its ships finding her. The"
        " crates are on their way north."
    ),
    timeout="{deadline_clock}, and the trawler is still a trawler among trawlers. The boats will"
            " find her before dawn.",
    stations={
        # The passage between the Dent Peninsula's islands and Sibutu: the
        # armed trawler up from the south, the two real ones working the
        # middle of it, the pickup boats waiting west of Sibutu.
        "mabini": S(4.95, 119.70, "Apolinario Mabini", heading=240),
        "inigo": S(4.65, 119.35, "Florencio Inigo", heading=330),
        "helo": S(4.98, 119.62, "Tawi 22", heading=240, alt=800),
        "okean": S(4.70, 119.15, "Trawler", heading=30),
        "boats": S(5.00, 119.38, "Fast boats", heading=180),
        "shuttle": S(4.75, 119.15, "Bell 212", heading=30, alt=500),
        "trawlers": S(4.78, 119.25, "Fishing trawlers", heading=200),
        "container": S(4.55, 119.25, "Container ship", heading=10),
        "tanker": S(5.05, 119.20, "Tanker", heading=190),
        "home": dict(S(5.046, 119.753, "Sanga-Sanga"), coastal=True),
    },
    units=[
        U("blue", "philippines-luzon-line", "phl_pt_jacinto", "mabini", variant="Variant2"),
        U("blue", "philippines-luzon-line", "phl_pb_jose_andrada", "inigo",
          variant="Variant21"),
        U("blue", "philippines-luzon-line", "phl_h-76", "helo", squadron="Squadron1",
          name="Tawi 22", alt=800, loadout="CAS"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Sanga-Sanga (Bongao)", nation="Philippines", weapons="Hold"),
        # Hold until she is at the boats; then her tube is Free, the "fights
        # back" of the brief.
        U("red", "project-2498-zyetseth", "civ_fv_okean_surprise", "okean",
          name="Hai Xing 7", nation="Panama", weapons="Hold",
          route=[(4.80, 119.24, 0), (4.98, 119.30, 0, [("SetWeaponStatus", "Free")])],
          telegraph=4),
        U("red", "red-storm-arsenal", "_narco_speedboat", "boats", name="Fast boat 1",
          weapons="Hold", route=[(4.98, 119.30, 0)], telegraph=2),
        U("red", "red-storm-arsenal", "_narco_speedboat", "boats", name="Fast boat 2",
          weapons="Hold", route=[(4.98, 119.30, 0)], telegraph=2),
        U("red", "iran-bell-212", "irinavy_bell-212", "shuttle", squadron="Squadron1",
          name="Meridian shuttle", nation="Pirates", alt=500, weapons="Hold",
          loadout="Transport",
          route=[(4.95, 119.00, 500), (4.85, 119.28, 500)], loop=True),
        U("neutral", "_vanilla", "civ_fv_okean", "trawlers",
          name="FB Santo Nino de Sitangkai", route=[(4.60, 119.30, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_fv_okean", "trawlers",
          name="FB Maria Theresa", route=[(4.70, 119.10, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_ms_act_1", "container",
          name="MV Kota Ratna (Tawau-Sandakan)", route=[(5.30, 119.40, 0)], telegraph=3),
        U("neutral", "re-power-resupply", "civ_ms_super_p", "tanker",
          name="MT Bunga Kasturi", nation="Malaysia",
          route=[(4.40, 119.30, 0)], telegraph=3),
    ],
    resolve={"Trawler": "victory", "Traffic": "neutral",
             "Identify": ("classify", "okean", 1),
             "Boats": ("destroy", "boats", 1),
             "Shuttle": ("classify", "shuttle", 1),
             "Patrol": ("protect", "mabini")},
    declares=["SLOkeanTaken"],
    expires_after="Service at Sea",
    window=dict(),
    role="patrol",
)
