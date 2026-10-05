"""SL04 - Service at Sea. Sulu Sea, east of Cagayancillo, 2 November 2028.

The campaign's one scheduled rearm, and it is not free: an MSC-chartered
barge carrier with the task group's ammunition has come down from Subic, and
the group has to go and get it. Her supply system is real (SEST Replenishment
At Sea: half a mile, eight knots, a 300,000-point pool), so a ship that
comes alongside and slows down takes back what it fired at Jolo. The window
is scored as Southern Reach's Macquarie Passage scores its own: the lead ship
inside three miles of her when thirty minutes have run, then the charter
north to the withdrawal box. Meridian knows she is coming.

If she is sunk she is gone for the rest of the campaign: SL04SupplierLost
keeps her out of The Aborlan Battery, where she would otherwise be waiting
at the anchorage with whatever is left in her.
"""
from campaign_data import U, F, S
from .tables import HELO, ATTACK, HULLS, PARTNERS, RAN, SUPPLY

MISSION = dict(
    code="SL04", series="Sulu Line", seq="SULU LINE  ·  MISSION 4",
    group="core", num="04", key="Service at Sea", place="Sulu Sea",
    intro=(
        "An ammunition charter from Subic at the rendezvous east of Cagayancillo. Go "
        "alongside, take back what Jolo cost, and get her out before Meridian arrives."
    ),
    sender="Naval Forces West",
    intent=((
        "This is the group's rearm, and it is not free. Bring the lead ship within three "
        "miles of the charter and hold her there for thirty minutes, while every ship that "
        "needs it goes alongside at eight knots or less. Then take the charter north to the "
        "withdrawal box. She carries the group's next month. Lose her and she is not "
        "replaced."
    )),
    date=(2028, 11, 2), time=(7, 0), sea=2, clouds="Scattered_1", wind="NE",
    difficulty=3, minutes=120, centre=(8.8, 119.1),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "SULU SEA, 0700. MV SULU PROVIDER, a C8 barge carrier on charter to Military "
            "Sealift Command, is at the rendezvous east of Cagayancillo. She has the task "
            "group's ammunition: 76 mm, MICA, Harpoon and torpedoes, from the stocks the "
            "Seventh Fleet left at Subic.\\n\\nShe is the group's rearm. Her supply system "
            "is live: a ship that comes within half a mile of her at eight knots or less "
            "takes stores across, one ship at a time. Keep your lead ship within three miles "
            "of her for thirty minutes while the others go alongside, then bring her north "
            "to the withdrawal box, twenty miles up.\\n\\nMeridian has her movement. Three "
            "fast attack craft sailed from Cagayancillo at 0500 and a drone has been "
            "overhead since first light. A ship alongside and slowed down is the easiest "
            "target in the Sulu Sea; keep a screen out while the others replenish."
        )),
    forces=(
        "Your task group, its aircraft and any supply ships you own. The charter: MV Sulu "
        "Provider, a working supply ship. Opposing: three Meridian fast attack craft and a "
        "spotter drone. Neutral: an inter-island freighter."
    ),
    special=(
        "The service window: the lead ship within three miles of Sulu Provider at the "
        "thirty-minute check. Supply ships, the Thai detachment and one RAN frigate are on "
        "sale before this mission."
    ),
    objectives=[
        ("Service", (
            "Hold the lead ship by SULU PROVIDER for thirty minutes, then bring her to the "
            "withdrawal box"
        ), "35,-35,Fail,Main"),
        ("Charter", "Keep MV Sulu Provider afloat", "20,-30,Complete"),
        ("Raiders", "Sink the Meridian boats", "15,0,None"),
        ("Traffic", "Harm no freighter or banca", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="charter", min_units=1, at=(9.02, 119.12),
                 radius=6, objective="Service",
                 after=dict(kind="area", units=["screen#1"], at_unit="charter#1",
                            radius=3, min_units=1, after_minutes=30,
                            sets="SL04ServiceHeld",
                            intel=(
                                "SULU PROVIDER: Thirty minutes. The rendezvous is complete. "
                                "Ships still needing stores may continue alongside; the "
                                "charter is to proceed north to the withdrawal box."
                            ))),
    fatal=[F("Charter", ["charter#1"])],
    support_loss=[dict(asset="Sulu Provider", units=["charter#1"], objective="Charter",
                       sets="SL04SupplierLost",
                       intel=(
                           "LOGISTICS REPORT: SULU PROVIDER is lost with her cargo. There is "
                           "no second charter. The group's ammunition from now on is what is "
                           "in its magazines and in its own supply ships."
                       ))],
    neutral_objective="Traffic",
    win=(
        "SULU PROVIDER is north of the box with what is left in her barges. The ships that "
        "went alongside have their magazines back. Naval Forces West will hold her at Puerto"
        " Princesa for the next time the group needs her."
    ),
    lose=(
        "The rendezvous is broken. SULU PROVIDER is gone, or the group never held its "
        "window, and the ammunition is still in her barges or at the bottom."
    ),
    timeout="{deadline_clock}, and SULU PROVIDER is still south of the box. Meridian has her "
            "position for another night.",
    stations={
        # The rendezvous on the proven water east of Cagayancillo; the
        # charter in the middle of it, the group's anchor two miles off.
        "screen": S(8.72, 119.09, "Screen", heading=0),
        "flight": S(8.70, 119.07, "Ship's flight", heading=0, alt=500),
        "strike": S(9.70, 118.80, "Strike flight", heading=180, alt=3000),
        "charter": S(8.71, 119.19, "Sulu Provider", heading=0),
        # The Meridian boats 40 NM south-east, out of Cagayancillo.
        "raiders": S(8.25, 119.75, "Meridian boats", heading=320),
        "drone": S(8.90, 119.60, "Spotter drone", heading=270, alt=9000),
        "freighter": S(9.02, 118.60, "Freighter", heading=90),
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
        U("blue", "_vanilla", "civ_ms_c8", "charter", variant="Variant1",
          name="MV Sulu Provider (MSC charter)", weapons="Hold",
          route=[(9.04, 119.12, 0)], telegraph=1),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Puerto Princesa (Antonio Bautista Air Base)", nation="Philippines",
          weapons="Hold"),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raiders", name="Meridian Escort 15",
          nation="Panama", route=[(8.75, 119.25, 0)], telegraph=4),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raiders", name="Meridian Escort 16",
          nation="Panama", route=[(8.70, 119.30, 0)], telegraph=4),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raiders", name="Meridian Escort 17",
          nation="Panama", route=[(8.65, 119.25, 0)], telegraph=4),
        U("red", "small-medium-uav-series", "usn_ForpostR705", "drone",
          name="Spotter drone", nation="Panama", weapons="Hold",
          route=[(8.80, 119.20, 9000), (8.90, 119.60, 9000)], loop=True),
        U("neutral", "_vanilla", "civ_ms_roro_c", "freighter",
          name="MV Lorenzo Hope (Iloilo-Cotabato)", route=[(8.40, 120.60, 0)], telegraph=3),
    ],
    resolve={"Service": "victory", "Traffic": "neutral",
             "Charter": ("protect", "charter#1"),
             "Raiders": ("destroy", "raiders", 3)},
    declares=["SL04ServiceHeld", "SL04SupplierLost"],
    window=dict(buy=True, repair=True, allow=SUPPLY + HULLS + PARTNERS + RAN,
                flights=[HELO, ATTACK],
                situation=(
                    "The second of the three supply-ship sales: Tarlac, Davao del Sur, Chula "
                    "and an MSC barge carrier are on offer, with the Thai detachment and one "
                    "RAN frigate released from the Arafura. Nothing is rearmed here: the "
                    "rearm is the charter at the rendezvous."
                )),
    role="logistics",
)
