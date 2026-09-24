"""TS03 - Chatham Watch. East of New Zealand, 28 January 2029.

The rendezvous: TANGO on the surface alongside the tender, sixty miles east
of the force, and the first kill of the Tasman chapter - authorised after
Cook Strait. The tender is a merchant hull under a state flag and is not a
target. Everything stays west of 180; the Chathams are in the briefing.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="TS03", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 3",
    group="core", num="03", key="Chatham Watch", place="East of New Zealand",
    intro="The boat that lay on the cable corridor is on the surface "
          "alongside her tender, sixty miles east. Wellington has "
          "authorised the kill. The tender is not a target.",
    sender="Commodore Alex Mercer; Commander Hana Rewi for Wellington's "
           "authority",
    intent=("After Cook Strait, Wellington has said what Canberra was "
            "waiting for it to say: the boat that lay on the corridor is a "
            "hostile submarine in New Zealand's zone and she may be "
            "engaged. She is on the surface alongside AUSTRAL COMPLIANCE "
            "sixty miles east of you, taking on stores, and she will dive "
            "the moment she hears you coming. Sink her. Do not touch the "
            "tender - she is a merchant hull under a state flag and the "
            "day we sink one of those is the day this becomes something "
            "else. Classify her instead; Under the Tasman wants her "
            "emitters."),
    date=(2029, 1, 28), time=(6, 20), sea=4, clouds="Broken_3", wind="W",
    difficulty=3, minutes=70, centre=(-44.0, 178.3),
    blue_nation="Australia", red_nation="China",
    brief=(
        "EAST OF NEW ZEALAND, 44 South, first light. KIWI 05 found them at "
        "0400: TANGO on the surface, stopped, alongside MV AUSTRAL "
        "COMPLIANCE with a hose across, two hundred miles west of the "
        "Chatham Islands and sixty miles east of you. The tender has been "
        "steaming in circles out here for two days waiting for her.\\n\\n"
        "Wellington has authorised the engagement under the New Zealand "
        "zone's rules and Canberra has concurred. TANGO is the boat that "
        "lay on the Tasman cable at periscope depth; she is a target. The "
        "tender is not: she is a merchant hull under a state flag, and "
        "the rules for her are the rules for any merchant. Classify her "
        "and leave her.\\n\\n"
        "KIWI 05 is back on station out of Ohakea with your own Poseidon "
        "if bought. The Chatham Islands freighter and two longliners are "
        "in the box, and a whale that sounds like a boat on a bad day. "
        "Seventy minutes. She will dive when she hears you."),
    forces="Your task group with its Seahawk and Poseidon if bought, Kiwi 05 "
           "out of Ohakea. Neutral: the Chatham Islands freighter, two "
           "longliners, a whale. Opposing: one Type 039C on the surface, "
           "the tender MV Austral Compliance alongside her.",
    objectives=[
        ("Boat", "Destroy TANGO", "35,-35,Fail,Main"),
        ("Tender", "Classify MV Austral Compliance", "15,0,None"),
        ("Restraint", "The tender is not a target", "15,-40,Complete"),
        ("Neutrals", "Harm no freighter, longliner or whale", "0,-25,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="destroy", stations=["red_sub"], min_units=1, objective="Boat"),
    fatal=[],
    neutral_objective="Neutrals",
    win="TANGO is on the bottom two hundred miles west of the Chathams, and "
        "the tender that fed her is steaming home with her name on file. "
        "The first kill of the Tasman chapter, and the cleanest.",
    lose="The flagship is gone east of New Zealand, or the tender is, and "
         "the boat that lay on the cable is still at sea.",
    timeout="Seventy minutes and TANGO dived before you reached her. She "
            "is somewhere east of you with full stores, and the tender is "
            "already steaming for the next rendezvous.",
    stations={
        # The escort 60 NM west of the rendezvous; the boat surfaced and
        # stopped alongside the tender, everything west of 180; the
        # Poseidons between; the freighter on the Napier-Waitangi run.
        "escort": S(-44.00, 177.90, "Task group", heading=90),
        "flight": S(-44.02, 177.88, "Ship's flight", heading=90, alt=500),
        "mpa": S(-44.30, 178.20, "Maritime patrol", heading=90, alt=12000),
        "kiwi": S(-43.80, 178.40, "Kiwi 05", heading=90, alt=8000),
        "red_sub": S(-44.05, 179.30, "Contact TANGO", heading=180),
        "tender": S(-44.06, 179.32, "Austral Compliance", heading=270),
        "freighter": S(-43.70, 178.00, "Chatham freighter", heading=100),
        "longliner1": S(-44.30, 178.70, "Longliner", heading=200),
        "longliner2": S(-43.90, 178.90, "Longliner", heading=40),
        "whale": S(-44.15, 178.10, "Biologic", heading=90),
        "home": S(-40.206, 175.388, "RNZAF Base Ohakea"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight", alt=500,
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          loadout="ASW", slot="Recon"),
        U("blue", "p-8-poseidon", "usn_p8", "kiwi", squadron="Squadron6",
          name="Kiwi 05", alt=8000, loadout="ASW"),
        # Surfaced and stopped: depth 0, telegraph 1, no route. She dives
        # when she hears the force, which is the engine's own behaviour.
        U("red", "plan-submarines", "plan_ss_type_039c", "red_sub", name="Contact TANGO",
          depth=0, weapons="Tight", telegraph=1),
        # Casting off: she gets under way westward at a knot or two as the
        # force closes, which is the hose coming across and the boat diving.
        U("red", "_vanilla", "civ_ms_kommunist", "tender",
          name="MV Austral Compliance (AMS tender)", weapons="Hold",
          route=[(-44.06, 179.10, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_ms_act_1", "freighter",
          name="MV Chatham Trader (Napier-Waitangi)",
          route=[(-43.80, 179.60, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "longliner1",
          name="Longliner Moana Rua", route=[(-44.60, 178.60, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "longliner2",
          name="Longliner Rehua", route=[(-43.60, 179.20, 0)], telegraph=2),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic MIKE",
          depth="shallow"),
        U("blue", "SEST_RAAF_Bases", "airbase_rnzaf_ohakea", "home",
          name="RNZAF Base Ohakea", nation="New Zealand", weapons="Hold"),
    ],
    resolve={"Boat": "victory", "Neutrals": "neutral",
             "Tender": ("classify", "tender", 1, "TS03TenderNamed"),
             "Restraint": ("spare", "tender"),
             "Flagship": ("protect", "escort")},
    declares=["TS03TenderNamed"],
    reveal_if=[dict(variable="TS01TenderNamed", units=["tender"], level="Classify",
                    intel="Home Waters' picture: the tender at the rendezvous "
                          "is AUSTRAL COMPLIANCE, the hull you named off "
                          "Puysegur, and she is on your plot classified. She "
                          "is still not a target."),
               dict(variable="TS02SubNamed", units=["red_sub"], level="Classify",
                    intel="Cook Strait's picture: the boat on the surface is "
                          "TANGO, the Type 039C you classified on the corridor, "
                          "and she is on your plot from the first minute. She is "
                          "a target now.")],
    window=dict(flights=[HELO, RECON]),
    role="patrol",
)
