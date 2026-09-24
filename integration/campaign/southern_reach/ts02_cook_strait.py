"""TS02 - Cook Strait. 25 January 2029.

The cable corridor is a declared box, not a mechanic: the cable repair ship
has to be inside it when twenty-five minutes have run, with the ferries
crossing and a conventional boat at periscope depth on the corridor, and
then reach Wellington's approach. The Gateway's corvette comes up from the
south to "inspect" her. A detachment, no builder, in the narrowest water of
the campaign.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="TS02", series="Tasman Shield", seq="TASMAN SHIELD  ·  MISSION 2",
    group="core", num="02", key="Cook Strait", place="Cook Strait",
    intro="The cable ship has to hold the declared corridor while the "
          "ferries cross, with a boat at periscope depth on the corridor "
          "and a corvette coming up from the south to inspect her.",
    special="Choose a detachment: the strait is twelve miles wide and the "
            "whole force will not fit in it usefully. No builder before "
            "this mission or the next.",
    sender="Commander Hana Rewi, RNZN, Maritime Component Commander (NZ)",
    intent=("The Tasman cable comes ashore at Oteranga Bay and TASMAN "
            "RELIANCE is repairing the fault the survey ship found in it. "
            "She needs twenty-five minutes inside the declared corridor and "
            "then a clear run to Wellington's approach. A submarine has been "
            "on the corridor at periscope depth since dawn and the corvette "
            "from Lyttelton is coming up from Cape Campbell to 'inspect' "
            "her under some regulation nobody has read. Keep the cable ship "
            "in the box, keep the ferries crossing, and keep it from "
            "becoming the first shot of the Tasman war. Nothing red has "
            "fired. Neither have we."),
    date=(2029, 1, 25), time=(11, 30), sea=4, clouds="Broken_2", wind="NW",
    difficulty=3, minutes=60, centre=(-41.55, 174.45),
    blue_nation="Australia", red_nation="China",
    brief=(
        "COOK STRAIT, late morning, a northerly building. CS TASMAN RELIANCE "
        "- a cable repair ship, a stand-in - is on the declared corridor "
        "twelve miles south-west of Oteranga Bay with the Tasman cable's "
        "fault under her. The corridor is a box on a chart, five miles "
        "around her: she has to be inside it when twenty-five minutes have "
        "run, and then make Wellington's approach.\\n\\n"
        "Two Interislander ferries are crossing - Wellington to Picton and "
        "back - with a Marlborough fishing boat, a coastal tanker and the "
        "Wellington-Christchurch service in the same box. TANGO, the boat "
        "from Fiordland, is at periscope depth on the corridor. The Type "
        "056A that inspected the freighters off Lyttelton is coming up "
        "from Cape Campbell, weapons tight, to do it again.\\n\\n"
        "Your detachment is eight miles east of the corridor. KIWI 05 is "
        "out of Ohakea. Hold the corridor, get the cable ship to the "
        "approach, classify the boat if you can. Fire on nothing that has "
        "not fired; a ferry in this strait is a thousand people."),
    forces="Your detachment with its Seahawk and Poseidon if bought, Kiwi "
           "05 out of Ohakea, the cable ship Tasman Reliance. Neutral: two "
           "Interislander ferries, a fishing boat, a coastal tanker, an "
           "airliner. Opposing: one Type 039C at periscope depth, one Type "
           "056A corvette from the south.",
    objectives=[
        ("Corridor", "Tasman Reliance holds the corridor box for 25 minutes, "
                     "then reaches Wellington's approach", "35,-35,Fail,Main"),
        ("Contact", "Classify the submarine on the corridor", "15,0,None"),
        ("Ferries", "The Interislander ferries are not targets", "10,-30,Complete"),
        ("Traffic", "Harm no fishing boat, tanker or aircraft", "0,-25,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
    ],
    # The corridor is the 03 Lifeline Trigger8 shape: inside five miles of
    # her own start when the clock reaches twenty-five minutes, then the
    # approach box, authored, off Wellington Heads. The solver does not
    # know the first twenty-five minutes are spent holding station.
    victory=dict(kind="arrive", station="cable", min_units=1, objective="Corridor",
                 at=(-41.42, 174.75), radius=5, transit=14,
                 after=dict(kind="area", units=["cable"], at_unit="cable#1",
                            radius=5, min_units=1, after_minutes=25,
                            intel="The splice is made and the corridor has "
                                  "held. TASMAN RELIANCE is recovering her "
                                  "gear: bring her to Wellington's approach "
                                  "before the corvette is alongside her.")),
    fatal=[F("Corridor", ["cable"])],
    neutral_objective="Traffic",
    win="The cable is repaired, the ferries crossed, and the corvette "
        "inspected nothing. Rewi: 'Wellington heard it on the news, which "
        "is how it should be.'",
    lose="The cable ship is lost in the strait, or a ferry is, and the "
         "Tasman war has its first hull.",
    timeout="Sixty minutes and the cable ship is still short of the "
            "approach with the corvette closing. Wellington's cable is "
            "spliced and the strait belongs to whoever is left in it.",
    stations={
        # The corridor 12 NM south-west of Oteranga; the detachment 8 NM
        # east; the boat on the corridor 10 NM west of the cable ship; the
        # corvette 25 NM south off Cape Campbell routed onto the corridor;
        # the ferries on the real crossing, the tanker Wellington-bound.
        "cable": S(-41.47, 174.58, "Cable corridor", heading=0),
        "escort": S(-41.55, 174.62, "Detachment", heading=330),
        "flight": S(-41.57, 174.64, "Ship's flight", heading=330, alt=500),
        "mpa": S(-41.68, 174.70, "Maritime patrol", heading=270, alt=10000),
        "kiwi": S(-41.70, 174.20, "Kiwi 05", heading=90, alt=6000),
        "red_sub": S(-41.50, 174.35, "Contact TANGO", heading=90),
        "red_056": S(-41.85, 174.55, "Type 056A", heading=350),
        "ferry_a": S(-41.38, 174.70, "Interislander (Wellington-Picton)", heading=280),
        "ferry_b": S(-41.32, 174.48, "Interislander (Picton-Wellington)", heading=100),
        "fish": S(-41.50, 174.25, "Marlborough fishing boat", heading=90),
        "tanker": S(-41.75, 174.60, "Coastal tanker", heading=20),
        "airliner": S(-41.65, 174.20, "Wellington-Christchurch", heading=210, alt=22000),
        "home": S(-40.206, 175.388, "RNZAF Base Ohakea"),
    },
    units=[
        U("blue", "_vanilla", "civ_ms_encounter", "cable",
          name="CS Tasman Reliance (cable repair ship, stand-in)"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=10000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        U("blue", "p-8-poseidon", "usn_p8", "kiwi", squadron="Squadron6",
          name="Kiwi 05", alt=6000, weapons="Tight", loadout="ASW"),
        U("red", "plan-submarines", "plan_ss_type_039c", "red_sub", name="Contact TANGO",
          depth="periscope", weapons="Tight",
          route=[(-41.52, 174.45, "periscope"), (-41.48, 174.52, "periscope")],
          telegraph=1),
        U("red", "modern-plan-systems", "plan_type_056a", "red_056",
          name="Type 056A corvette", weapons="Tight",
          route=[(-41.55, 174.55, 0), (-41.49, 174.60, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_roro_a", "ferry_a",
          name="Interislander Aratere (stand-in)",
          route=[(-41.36, 174.50, 0), (-41.28, 174.42, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_roro_b", "ferry_b",
          name="Interislander Kaitaki (stand-in)",
          route=[(-41.38, 174.70, 0), (-41.40, 174.80, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fish",
          name="Fishing boat Te Awaiti", route=[(-41.55, 174.45, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_ritina", "tanker",
          name="MT Kapiti Coast (Lyttelton-Wellington)",
          route=[(-41.45, 174.78, 0)], telegraph=3),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "airliner",
          name="Wellington-Christchurch 428"),
        U("blue", "SEST_RAAF_Bases", "airbase_rnzaf_ohakea", "home",
          name="RNZAF Base Ohakea", nation="New Zealand", weapons="Hold"),
    ],
    resolve={"Corridor": "victory", "Traffic": "neutral",
             "Contact": ("classify", "red_sub", 1, "TS02SubNamed"),
             "Ferries": ("spare", "ferry_a", "ferry_b"),
             "Flagship": ("protect", "escort")},
    declares=["TS02SubNamed"],
    reveal_if=[dict(variable="SR08CorvetteNamed", units=["red_056"], level="Classify",
                    intel="The Gateway's picture: the corvette coming up from "
                          "Cape Campbell is the one that inspected the freighters "
                          "off Lyttelton, and she is on your plot classified. Her "
                          "captain has done this before.")],
    window=dict(detachment=True, flights=[HELO, RECON]),
    role="patrol",
)
