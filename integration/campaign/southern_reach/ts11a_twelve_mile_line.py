"""TS11A - The Twelve-Mile Line. Off Green Cape, 27 February 2029.

Optional, between Approaches and Southern Cross. A Type 056A corvette of
the protection group has asked for Australian protection and is running for
Eden; a Type 054A of her own screen is astern with orders that she is not to
reach a foreign port. The player's detachment, on passage to Sydney, has to
reach her before the frigate is in position to fire, defend a ship that
cannot defend herself, not fire first, and bring her inside twelve miles.

Built to the design panel's winning card (build notes, "The Twelve-Mile
Line"). The model is the Storozhevoy, November 1975: a split crew, a
pursuer ordered to stop her own ship short of foreign waters, force as the
last resort near the line. Three builder features carry it, each emitting
only stock keys: waypoint orders (the frigate fires at the corvette and at
nothing else - Raid on Lombok's Osa), disable= (the corvette's weapons are
off from the first second - Defense of North Borneo's Trigger4) and lift=
(Restraint stops binding once the frigate is in her firing position).

No person is named and the corvette has no name or pennant, so no real
Type 056A is claimed (Red Line bible, section 2). Nothing here states what
happened in Approaches: the carrier and the flagship are not mentioned.
"""
from campaign_data import U, F, S, HELO, RECON

# The frigate's firing position: where she is when her fire-control radar
# locks the corvette, and where her first salvo leaves. The lift circle is
# centred here.
FIRST_SALVO = (-37.42, 150.78)

MISSION = dict(
    code="TS11A", series="Tasman Shield", seq="TASMAN SHIELD  ·  OPTIONAL",
    group="optional", num="11A", key="The Twelve-Mile Line",
    place="Off Green Cape, New South Wales",
    intro="A Type 056A of the protection group has asked for Australian "
          "protection and is running for Eden with nobody on her weapons and "
          "a frigate astern. Bring her inside the twelve-mile line. Do not "
          "fire first.",
    special=(
        "A corvette of the protection group has asked for Australian protection and is "
        "running for Eden with a frigate astern. Take a detachment and bring her inside the "
        "twelve-mile line, or leave her. Nothing fired here is replaced before Southern "
        "Cross. The request closes when Southern Cross is complete."
    ),
    sender="Commodore Alex Mercer",
    intent=("At 0120 a man giving his rank as her commanding officer called "
            "Bluefin 31 on channel sixteen and asked for the protection of "
            "the Australian government for his ship's company. Canberra said "
            "yes at 0415. She is twenty-six miles east-south-east of Green "
            "Cape making for Eden, and nobody aboard will fire her weapons. "
            "A frigate of her own screen is sixteen miles astern and has been "
            "ordering her back since midnight. Get a ship to her before that "
            "frigate is in position to fire, and bring her inside twelve "
            "miles. You do not fire first; if the frigate shows hostile intent "
            "against her, defend her."),
    date=(2029, 2, 27), time=(4, 55), sea=3, clouds="Scattered_1", wind="NE",
    # 85, not 80: the defector's corvette makes the twelve-mile circle with
    # a mile to spare at the sea state 3 planning speed; at 80 it was a
    # cable short, and the circle is where the story says it is.
    difficulty=3, minutes=85, centre=(-37.28, 150.45),
    blue_nation="Australia", red_nation="China",
    brief=(
        "OFF GREEN CAPE, 0455, dark; first light about 0620. Your detachment is off "
        "Twofold Bay on passage to Sydney, where the force is to be made ready for the "
        "relief convoy. At 2155 last night one of the protection group's Type 056A "
        "corvettes, on picket a hundred and eighty miles east-south-east of Gabo Island, "
        "left her station, turned onto 295 and stopped radiating. At 0120 a voice giving his "
        "rank as her commanding officer called BLUEFIN 31, the RAAF Poseidon watching the "
        "group, on channel 16. He asked for the protection of the Australian government for "
        "his ship's company. He and her political officer hold the bridge and the engine "
        "room; those who did not join them hold the operations room, unharmed, and her "
        "weapons are made safe, guns trained fore and aft. Canberra accepted at 0415."
        "\\n\\n"
        "She is twenty-six miles east-south-east of Green Cape, steering for Eden at about "
        "twenty-one knots on engines that have not been opened up since October. A Type "
        "054A of her screen turned to follow her at 0030 and is sixteen miles astern, "
        "closing slowly, with her Z-9 over the corvette marking her. She has been ordering "
        "her back on the group's net all night.\\n\\n"
        "INTELLIGENCE: A partial decrypt of Fleet headquarters to the group at 0350 reads "
        "'...is not to reach a foreign port...'. It is an hour old and gives the frigate's "
        "orders, not her intentions now. Assess that she will use force as the corvette "
        "nears Australian waters, and not before; she will not follow her inside twelve "
        "miles.\\n\\n"
        "Offensive action against the group is paused tonight for the talks; self-defence "
        "and the defence of others stand. Your detachment is weapons tight. Do not fire on "
        "the frigate or her helicopter before they show hostile intent against the "
        "corvette. From then, defend her: the missiles first, and the frigate or her "
        "helicopter if nothing less will do. A YJ-83 fired at her goes for the first ship "
        "its seeker finds, and yours are the ships beside her. Nothing fired here is "
        "replaced before Southern Cross. A coastal bulker for Port Kembla and two Eden "
        "fishing boats are in the water."
    ),
    forces=(
        "Your detachment with its Seahawk and Poseidon if assigned; Bluefin 31, a RAAF "
        "P-8A out of East Sale. Under Australian protection: a Type 056A corvette of the "
        "protection group, her weapons made safe. Neutral: a coastal bulker and two Eden "
        "fishing boats. Opposing: one Type 054A frigate and her Z-9."
    ),
    objectives=[
        ("Protection", "Bring the corvette inside the twelve-mile line off Green Cape",
         "30,-30,Fail,Main"),
        ("Restraint", "Do not fire first on the frigate or her helicopter",
         "15,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-15,Complete"),
        ("Traffic", "Harm no fishing boat or merchant", "0,-30,Complete"),
    ],
    # The box is the Eden approach north of Green Cape, on her 295 track: on
    # the side she comes from its rim lies 11.4-12.6 NM off the coast, so she
    # enters it at about the twelve-mile line.
    victory=dict(kind="arrive", station="defector", min_units=1, objective="Protection",
                 at=(-37.18, 150.12), radius=9, sets="TS11ADefectorSafe"),
    # Losing her ends it. Restraint is scored, not fatal: whether a Generated
    # force inherits the anchor's Tight is unproven, and a Free escort
    # killing the Z-9 at T+1 must not end the mission before the player has
    # decided anything (test card 6.3).
    fatal=[F("Protection", ["defector"])],
    neutral_objective="Traffic",
    win=(
        "The corvette is inside twelve miles off Green Cape and the frigate has turned away "
        "at the line. A boarding officer from your detachment is on her bridge at her "
        "captain's invitation, and Eden's pilot is coming out. Canberra has told Beijing the "
        "ship will be returned after the talks. Her ship's company will be landed at Twofold "
        "Bay: those who ask for protection will be heard, and those who want to go home will "
        "be sent home."
    ),
    lose=(
        "The corvette is lost short of the line, or there is nothing left of the detachment "
        "to bring her in. The group has the ending it wanted: a ship that did not arrive, and "
        "a story about who stopped her."
    ),
    timeout=(
        "Eighty minutes, and the corvette is still outside the twelve-mile line, crippled "
        "or stopped, with the frigate standing off. What happens to her now is not in your "
        "report."
    ),
    stations={
        # Every point proved against the coastline extract; distances off the
        # coast in brackets.
        "escort": S(-37.12, 150.35, "Detachment", heading=140),          # 16.5
        "flight": S(-37.13, 150.37, "Ship's flight", heading=140, alt=500),
        "mpa": S(-37.02, 150.57, "Maritime patrol", heading=150, alt=12000),
        "bluefin": S(-37.26, 150.61, "Bluefin 31", heading=120, alt=15000),
        # The corvette 19 NM south-east of the detachment, steering 295 for
        # the box, and the frigate 15.7 NM astern of her on the same course.
        "defector": S(-37.36, 150.61, "The corvette", heading=295),       # 27.0
        "frigate": S(-37.47, 150.91, "Type 054A", heading=295),           # 42.4
        # The Z-9 7.3 NM from the corvette, clear of the escort role's 6 NM
        # standoff; its loop never enters the territorial sea.
        "helo": S(-37.41, 150.75, "Z-9", heading=295, alt=1000),          # 34.1
        "bulker": S(-37.00, 150.30, "Coastal bulker", heading=15),        # 17.0
        "trawler": S(-37.05, 150.14, "Eden trawler", heading=60),         # 9.1
        "fish": S(-37.08, 150.40, "Eden fishing boat", heading=90),       # 19.4
        "east_sale": S(-38.099, 147.149, "RAAF Base East Sale"),
    },
    units=[
        # The anchor: the player's detachment forms here. Tight, because the
        # detachment does not fire first.
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant7",
          weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight",
          slot="HeloRecon"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=12000,
          weapons="Tight", loadout="ASW", slot="Recon"),
        # The aircraft she called, and the one that reports the lock: a
        # picture whatever the player owns. The ASW fit carries no anti-ship
        # round.
        U("blue", "p-8-poseidon", "usn_p8", "bluefin", squadron="Squadron3",
          name="Bluefin 31", alt=15000, weapons="Tight", loadout="ASW",
          route=[(-37.31, 150.50, 15000), (-37.48, 150.86, 15000)], loop=True),
        # Blue, so the frigate can be ordered to fire at her and the player's
        # escorts never shoot her; weapons off from the first second, because
        # the plot does not hold her operations room - which also makes the
        # escort essential. Radars off: she ran dark. The player steers her,
        # standing in for the RAN directing her by radio. Not JoinTaskForce:
        # she never enters the owned roster.
        U("blue", "modern-plan-systems", "plan_type_056a", "defector",
          name="Type 056A corvette (under Australian protection)", nation="China",
          weapons="Hold", radars="False", route=[(-37.18, 150.12, 0)], telegraph=4,
          disable=("weapons",)),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_east_sale", "east_sale",
          name="RAAF Base East Sale", nation="australia", weapons="Hold"),
        # The pursuer. Tight - self-defence only - so she never opens on the
        # RAN; two scripted salvos at the corvette and at nothing else, then
        # she slows and stands off outside the line. Six of her eight YJ-83A.
        U("red", "modern-plan-systems", "plan_type_054a_p5", "frigate",
          name="Type 054A frigate", weapons="Tight", telegraph=5,
          route=[(FIRST_SALVO[0], FIRST_SALVO[1], 0,
                  [("AttackAtWaypoint", "plan_yj-83a", "defector", 2)]),
                 (-37.36, 150.63, 0,
                  [("AttackAtWaypoint", "plan_yj-83a", "defector", 4)]),
                 (-37.39, 150.50, 0, [("SetTelegraph", 2)]),
                 (-37.50, 150.62, 0)]),
        # Her eyes on a ship that is not radiating: unarmed (ASWHunter hangs
        # no weapon), but a helicopter the player must not shoot first.
        U("red", "modern-plan-systems", "plan_z-9c", "helo",
          name="Z-9 (the frigate's flight)", alt=1000, loadout="ASWHunter",
          weapons="Tight",
          route=[(-37.38, 150.67, 1000), (-37.29, 150.42, 1000)], loop=True),
        # The coastal lane and the Eden fleet, all at least 11 NM off the
        # salvo axis.
        U("neutral", "_vanilla", "civ_ms_bulk", "bulker",
          name="MV Kembla Trader (Melbourne-Port Kembla)",
          route=[(-36.55, 150.45, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "trawler",
          name="FV Twofold Venture (Eden)", route=[(-36.90, 150.45, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fish",
          name="FV Green Cape Lass (Eden)", route=[(-37.05, 150.75, 0)], telegraph=2),
    ],
    resolve={"Protection": "victory", "Traffic": "neutral",
             "Restraint": ("spare", "frigate", "helo"),
             "Flagship": ("protect", "escort")},
    # The fire-control lock: when the frigate reaches her firing position
    # (about T+10), Restraint stops binding and Bluefin says so.
    lift=[dict(objective="Restraint", units=["frigate"], at=FIRST_SALVO, radius=2.5,
               intel=(
                   "BLUEFIN 31: The frigate's fire-control radar is locked on the corvette. "
                   "Hostile intent. You are cleared to defend her: the missiles first, and "
                   "the frigate or her helicopter if that is what it takes. Weapons tight is "
                   "self-defence only - go free, or engage the missiles by hand."
               ))],
    declares=["TS11ADefectorSafe"],
    window=dict(detachment=True, flights=[HELO, RECON],
                situation=(
                    "The detachment sails as Approaches left it, on passage to Sydney. No "
                    "purchases, repair or rearm. Nothing fired here is replaced before "
                    "Southern Cross."
                )),
    expires_after="Southern Cross",
    role="escort",
    # The whole action is within 30 NM of Green Cape: East Sale, 160 NM off,
    # is named in the chart's corner rather than shrinking the fight to fit it.
    map_focus_nm=100,
)
