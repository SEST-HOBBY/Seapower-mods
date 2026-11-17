"""MK02 - Gwadar Roads. Off Gwadar, 31 October 2028.

Two Pakistani tankers with Gwadar's fuel have been at anchor in the roads
for three days, among merchants waiting for a berth. One of the ships at
anchor is not a merchant: a Meridian freighter with eight SS-N-2
containers under her hatch covers (the armed Poltava's StyxCarrier fit),
anchored there last night. At dawn three
Meridian armed trawlers come out of the west for the anchorage.

The second window releases the Air Force: JF-17 Block II and III strike and
air defence flights and a ZDK-03 out of Gwadar's field. Every window
rearms.
"""
from campaign_data import U, F, S
from .tables import HELO, ATTACK, CAP, AEW, WHOLE

MISSION = dict(
    code="MK02", series="Makran Line", seq="MAKRAN LINE  ·  MISSION 2",
    group="core", num="02", key="Gwadar Roads", place="Gwadar",
    intro=(
        "Three armed trawlers are coming for the Gwadar anchorage, and one of the ships at "
        "anchor is Meridian's."
    ),
    sender="Commander Pakistan Fleet, Karachi; Task Force 88 staff, Gwadar",
    intent=((
        "Gwadar's fuel is at anchor and Meridian means to burn it where it lies. Sink the three "
        "trawlers, and find the armed merchant among the anchored ships and sink her before "
        "she fires again. Every other ship in the roads is a merchant with a crew; a missile "
        "into the wrong hull does Meridian's work for it."
    )),
    date=(2028, 10, 31), time=(5, 50), sea=2, clouds="Scattered_2", wind="NE",
    difficulty=3, minutes=100, centre=(25.0, 62.35),
    blue_nation="Pakistan", red_nation="Meridian",
    brief=(
        (
            "GWADAR ROADS, 0550. MT INDUS PRIDE and MT HAB RIVER have been at anchor seven "
            "miles south of the port for three days, with Gwadar's fuel. Two merchants are at "
            "anchor west of them, waiting for a berth, and a third freighter anchored among "
            "them last night without answering the port.\\n\\n"
            "Fleet intelligence assesses that she is MERIDIAN's: a freighter with SS-N-2 "
            "launchers under her hatch covers, sent to put a missile into the tankers at "
            "anchor. Three armed trawlers left the fishing grounds off Jiwani before dawn and are "
            "running north-east for the roads. The Air Force has released JF-17s and a ZDK-03 to "
            "the task group from Gwadar's field.\\n\\n"
            "Sink the three trawlers and the armed freighter. The operation is complete when "
            "all four are sunk. Classify the anchored ships before you fire into the roads: "
            "two of them are merchants, and their crews are aboard. Your ships are weapons "
            "Free; the shore battery and the air-defence site at Gwadar start at Hold and are "
            "yours to release.\\n\\n"
            "Fishing dhows are working the bay. Keep a missile defence over the two tankers."
        )),
    forces=(
        "Your task group and its flight, with the Air Force's JF-17s and ZDK-03 if allocated; "
        "Gwadar's field, an HQ-16AE air-defence site and a C-602 coastal battery ashore. At "
        "anchor: MT Indus Pride and MT Hab River, two merchants and an armed Meridian "
        "freighter. Opposing: three Meridian armed trawlers. Neutral: fishing dhows."
    ),
    special=(
        "The Air Force's JF-17 Block II and III and its ZDK-03 are released to the task group "
        "from this force allocation. Rearm is free at every force allocation."
    ),
    objectives=[
        ("Raiders", "Sink the three Meridian armed trawlers", "30,-30,Fail,Main"),
        ("Launcher", "Also required: find the armed freighter among the anchored ships and "
                     "sink her", "20,-30,Fail,Main"),
        ("Anchorage", "Lose neither tanker at anchor", "20,-30,Complete"),
        ("Named", "Classify the armed freighter among the anchored ships", "10,0,None"),
        ("Traffic", "Harm no merchant or dhow that is what it says it is", "0,-30,Complete"),
    ],
    victory=dict(kind="destroy", stations=["raiders"], min_units=3, objective="Raiders",
                 also=[dict(kind="destroyed", units=["launcher"], min_units=1)]),
    fatal=[F("Anchorage")],
    neutral_objective="Traffic",
    win=(
        "The three trawlers and the armed freighter are sunk, and the tankers are still at "
        "anchor with Gwadar's fuel. The port has sent out its first pilot in four days."
    ),
    lose=(
        "A tanker at anchor is burning. Gwadar's fuel is in the sea, and the roads will be "
        "empty of shipping by tonight."
    ),
    timeout="{deadline_clock}, and Meridian still has ships in the roads. The port keeps its "
            "pilots ashore and the tankers sail for Karachi with their fuel.",
    stations={
        # The task group came in from Karachi overnight and is eleven miles
        # east of the anchorage; the roads are seven miles off the port.
        "screen": S(24.95, 62.50, "Screen", heading=270),
        "flight": S(24.96, 62.47, "Ship's flight", heading=270, alt=500),
        "anchorage": S(25.00, 62.30, "Tankers at anchor", heading=200),
        "merchants": S(24.96, 62.22, "Merchants at anchor", heading=200),
        "launcher": S(24.95, 62.20, "Armed freighter", heading=200),
        # The Meridian trawlers, 33 miles south-west of the screen.
        "raiders": S(24.62, 62.02, "Meridian trawlers", heading=40),
        "dhows": S(24.90, 62.40, "Fishing dhows", heading=120),
        # Ashore at Gwadar: the field, the air-defence site and the battery.
        # The old airport. It closed to civil traffic in January 2025, when New
        # Gwadar International opened 26 km north-east; that the Air Force flies
        # from it in 2028 is a campaign assumption (bible, section 1).
        "home": S(25.233, 62.329, "Gwadar airfield (old airport)"),
        "sam": dict(S(25.21, 62.36, "HQ-16AE site"), coastal=True),
        "battery": dict(S(25.24, 62.28, "Coastal battery"), coastal=True),
        "strike": S(25.30, 62.60, "Strike flight", heading=225, alt=3000),
        "cap": S(25.32, 62.65, "Air defence flight", heading=225, alt=20000),
        "aew": S(25.40, 62.80, "ZDK-03", heading=225, alt=25000),
    },
    units=[
        # air_group=[]: the pack's file embarks the PLAN's Z-9F (China), which
        # would fill her one deck slot when the mission is launched as authored.
        U("blue", "pakistani-pack", "pns_type_054a_p", "screen", variant="Variant2",
          air_group=[]),
        U("blue", "pakistani-pack", "plan_z-9ce", "flight", squadron="Squadron1",
          alt=500, loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "pakistani-pack", "paf_jf-17_blk_iii", "strike", squadron="Squadron1",
          alt=3000, loadout="AntiShip", slot="Attack"),
        U("blue", "pakistani-pack", "paf_jf-17_blk_iii", "strike", squadron="Squadron1",
          alt=3000, loadout="AntiShip", slot="Attack"),
        U("blue", "pakistani-pack", "paf_jf-17_blk_ii", "cap", squadron="Squadron1",
          alt=20000, loadout="AirToAir", slot="CAP"),
        U("blue", "pakistani-pack", "paf_jf-17_blk_ii", "cap", squadron="Squadron1",
          alt=20000, loadout="AirToAir", slot="CAP"),
        U("blue", "pakistani-pack", "paf_zdk-03", "aew", squadron="Squadron1",
          alt=25000, loadout="AEW", slot="Recon"),
        U("blue", "_vanilla", "civ_ms_ritina", "anchorage", name="MT Indus Pride",
          nation="Pakistan", weapons="Hold"),
        U("blue", "_vanilla", "civ_ms_ritina", "anchorage", name="MT Hab River",
          nation="Pakistan", weapons="Hold"),
        U("blue", "_vanilla", "airfield_small_1", "home", name="Gwadar airfield (old airport)",
          nation="Pakistan", weapons="Hold", air_group=[]),
        U("blue", "pakistani-pack", "pla_sam_site_hq-16ae", "sam",
          name="HQ-16AE site, Gwadar", nation="Pakistan", weapons="Hold"),
        U("blue", "pakistani-pack", "pla_c-602_tel", "battery",
          name="Coastal battery, Gwadar", nation="Pakistan", weapons="Hold"),
        # Anchored among the merchants, weapons held until her two scripted
        # salvoes: a Styx at each tanker. StyxCarrier is the fit that carries
        # the SS-N-2 (WeaponSystem3StyxCarrier); Default is machine guns only.
        U("red", "armed-merchantmen", "wp_ms_poltava_armed", "launcher",
          name="MV Sea Venture", nation="Meridian", weapons="Hold", loadout="StyxCarrier",
          attacks=[(14, "wp_ss-n-2c", "anchorage#1", 1), (32, "wp_ss-n-2c", "anchorage#2", 1)]),
        U("red", "armed-merchantmen", "civ_fv_okean_armed", "raiders", variant="Variant4",
          loadout="Bofors", name="Meridian Escort 31", nation="Meridian", route=[(24.98, 62.28, 0)],
          telegraph=4),
        U("red", "armed-merchantmen", "civ_fv_okean_armed", "raiders", variant="Variant5",
          loadout="Bofors", name="Meridian Escort 32", nation="Meridian", route=[(24.97, 62.31, 0)],
          telegraph=4),
        U("red", "armed-merchantmen", "civ_fv_sidetrawler_armed", "raiders",
          name="Meridian Escort 33", nation="Meridian", route=[(24.99, 62.33, 0)],
          telegraph=4),
        U("neutral", "_vanilla", "civ_ms_bulk", "merchants", name="MV Arabian Grace",
          nation="Liberia"),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "merchants",
          name="MV Coral Bay", nation="Panama"),
        U("neutral", "_vanilla", "civ_fv_dhow", "dhows", name="Dhow Pasni Star",
          nation="Pakistan", route=[(24.80, 62.60, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_dhow", "dhows", name="Dhow Al-Rehman",
          nation="Pakistan", route=[(25.05, 62.55, 0)], telegraph=2),
    ],
    resolve={"Raiders": "victory", "Traffic": "neutral",
             "Launcher": ("destroy", "launcher", 1),
             "Anchorage": ("protect", "anchorage#1", "anchorage#2"),
             "Named": ("classify", "launcher", 1)},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True, allow=list(WHOLE),
                flights=[HELO, ATTACK, CAP, AEW],
                situation=(
                    "The Air Force has released JF-17 Block II and III flights and a ZDK-03 to "
                    "the task group, out of Gwadar's field. The whole roster is on offer, and "
                    "the ships have rearmed and taken on fuel at Karachi."
                )),
    role="strike",
)
