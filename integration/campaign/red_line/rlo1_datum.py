"""RLO1 - Datum. North of Biak, 11 November 2028.

The first side operation (campaign-upgrade-plan.md section 4.2, step RL-1,
20 Oct 2026). The night before, a torpedo hit the Russian detachment's
auxiliary in the northern approaches to Biak - Routes They Can See's "two
nights ago", Return Passage's "eleven days ago" on the 21st - and nobody
has claimed the boat that fired. Fleet headquarters designates her GOLF and
wants a class on her before the enclave's fuel run goes in by the northern
roads the next night. The enclave detachment's Y-9 has the buoys; the order
is the group's own, and it fires nothing.

A fixed force flies it: Sea Ear 31 and the enclave field, not the screen,
so nothing the player owns sails. Classifying GOLF writes RLO1GolfDatum, and
Routes They Can See reads it as a datum on her for fifteen minutes - the
shape of Southern Watch's O2 -> SW04: a position from a record, not a
classified track, because classifying her again is that mission's own task.

GOLF cannot be lost here. She is in both later northern missions (Routes
They Can See sinks her or leaves her for The Order to Withdraw), so she is
in the Restraint fatal with the Poseidon: a torpedo on her ends the
operation, which is the order anyway. She is usn_ssn_virginia_2027
Variant10, in all three, from 20 Oct 2026: Variant1 is the hull Southern
Watch's Fujian's Shadow and Southern Reach's Approaches place as "US
submarine support" (mission_depth.SUB_SUPPORT), which Fujian's Shadow can
lose four days before GOLF's last appearance. The text never says whose she
is; neither the briefing's photographs nor the Situation window shows her.

Geography: proved against the coastline (geo/banda_theatre_coast.json), as
Southern Watch's side operations round Biak are; the four northern core
missions use the pool.
"""
from campaign_data import U, F, S

MISSION = dict(
    code="RLO1", series="Red Line", seq="RED LINE  ·  OPTIONAL",
    group="optional", num="O1", key="Datum", place="North of Biak",
    geography="coast",
    intro=(
        "Optional. A boat nobody has claimed torpedoed the Russian auxiliary last night. Put a "
        "class on her from the enclave's Y-9. Fire nothing."
    ),
    special=(
        "No force allocation: the enclave detachment's Y-9 flies this operation, and the "
        "screen stays on its station. What the buoys hear goes into the fuel run's picture "
        "tomorrow night. The request closes when Routes They Can See is complete."
    ),
    sender="Fleet headquarters",
    intent=((
        "The boat that fired last night is not ours and not the Russians', and the enclave's "
        "fuel goes in through her water tomorrow night. Know what she is. A class is a buoy "
        "pattern and patience; it is not a torpedo, and nothing the group launches today has "
        "a warhead on it. The Australian aircraft over the same water is recording. Give it "
        "nothing to record but an aircraft laying buoys."
    )),
    date=(2028, 11, 11), time=(6, 40), sea=3, clouds="Scattered_2", wind="SE",
    difficulty=2, minutes=45, centre=(-0.4, 136.4),
    blue_nation="China", red_nation="Australia",
    brief=(
        (
            "NORTH OF BIAK, 0640. At 2340 last night a torpedo hit the Russian detachment's "
            "auxiliary in the northern approaches. She is afloat and making six knots, and she "
            "is the Russian detachment's business, not this headquarters'. The boat that fired "
            "is not.\\n\\nNobody has claimed her. Fleet headquarters has designated her GOLF and "
            "wants a class on her before HAI YANG 7 goes into the northern roads tomorrow "
            "night. SEA EAR 31, the enclave detachment's Y-9, is airborne with a full load of "
            "buoys. GOLF has had seven hours, and she is assessed to be within thirty miles of "
            "where the auxiliary was hit, north-east of the aircraft.\\n\\nA RAAF Poseidon is "
            "over the same water, recording. Leave it alone.\\n\\nPut a class on GOLF, then "
            "bring the aircraft back over the enclave field. Fire nothing: SEA EAR 31 starts at "
            "weapons Hold, and a torpedo from it would be the group firing first on a boat it "
            "cannot name. Biak's fishing boats and a coaster bound for Jayapura are on the "
            "water."
        )),
    forces=(
        "Sea Ear 31, a Y-9 out of the enclave field, with sonobuoys. Opposing: one submarine, "
        "GOLF, unclaimed. Watching: a RAAF P-8A. Neutral: two Biak fishing boats and a "
        "coaster."
    ),
    objectives=[
        ("Datum", "Classify the submarine, then bring Sea Ear 31 back over the enclave field",
         "35,-35,Fail,Main"),
        ("Restraint", "Fire on nothing: not the boat, not the patrol aircraft",
         "15,-40,Complete"),
        ("Aircraft", "Bring Sea Ear 31 home", "10,-30,Complete"),
        ("Watchers", "Classify the patrol aircraft over the buoy field", "10,0,None"),
        ("Traffic", "Harm no fishing boat or coaster", "0,-30,Complete"),
    ],
    # Nothing counts until GOLF has a class - that is the operation - and
    # the class is what Routes They Can See reads (RLO1GolfDatum, set by the
    # stage). Then the Y-9 back over the water off the field, where it
    # lands: a box on the coast proves on water, a box on the airfield
    # would not.
    victory=dict(kind="arrive", station="mpa", at=(-0.80, 136.20), radius=8,
                 min_units=1, objective="Datum",
                 after=dict(kind="classify", units="red_sub", min_units=1,
                            sets="RLO1GolfDatum",
                            intel=(
                                "SONAR REPORT / SEA EAR 31: Contact GOLF classified: a "
                                "nuclear submarine, dived, slow, working west. The class is "
                                "logged and her signature goes to the group for tomorrow "
                                "night. It does not say whose she is, and it does not "
                                "authorise an attack. Bring the aircraft home."
                            ))),
    # The order is the mission: a weapon on the boat or the Poseidon ends
    # it. GOLF is in both later northern missions, so she cannot be lost
    # here and still be there. The Y-9 lost ends it too: the classification
    # is hers to carry home.
    fatal=[F("Restraint", ["red_sub", "red_air"]), F("Aircraft")],
    neutral_objective="Traffic",
    win=(
        "SEA EAR 31 is over the enclave field with GOLF's class on tape. The fuel run "
        "tomorrow night starts with her signature, and the Poseidon's recording shows an "
        "aircraft laying buoys."
    ),
    lose=(
        "The boat or the Poseidon is lost, or the Y-9 is. The group has fired first, or "
        "lost the aircraft that was to keep it from having to; either way the fuel run "
        "goes in blind."
    ),
    timeout="{deadline_clock}, and GOLF still has no class. The fuel run goes in tomorrow "
            "night with a boat on its route that nobody can name.",
    stations={
        # The water north of Biak and Supiori: the auxiliary was hit about
        # forty miles out, and GOLF is slow and west of there seven hours
        # later, 26 NM north-north-east of the Y-9 and 54 NM off the coast.
        # The Poseidon's racetrack runs north-west to south-east over both;
        # the field is on Biak, where RL02 and RL03 put it.
        "mpa": S(-0.45, 136.30, "Sea Ear 31", heading=20, alt=8000),
        "field": S(-1.10, 136.20, "Enclave field"),
        "red_sub": S(-0.10, 136.55, "Contact GOLF", heading=250),
        "red_air": S(0.05, 136.35, "Patrol aircraft", heading=130, alt=15000),
        "fishing": S(-0.55, 136.55, "Biak fishing boats", heading=20),
        "coaster": S(-0.35, 135.95, "Coaster", heading=80),
    },
    units=[
        # The enclave detachment's own Y-9, not a purchase: no slot, so the
        # win and the Aircraft objective can name her.
        U("blue", "modern-plan-systems", "plan_y-9fq", "mpa", name="Sea Ear 31",
          squadron="Squadron1", loadout="ASW", alt=8000, weapons="Hold"),
        U("blue", "modern-chinese-airbase", "pla_airbase_modern", "field",
          name="Enclave field (PLAAF detachment)", weapons="Hold"),
        # Dived, slow, working west towards the route the fuel run takes,
        # weapons Hold: she has nothing to shoot at that flies. Still
        # nobody's: no photograph, no Situation entry.
        U("red", "us-navy-2027", "usn_ssn_virginia_2027", "red_sub", variant="Variant10",
          name="Contact GOLF", depth="belowlayer", weapons="Hold", radars="False",
          route=[(-0.25, 136.05, "belowlayer")], telegraph=2,
          recognise=False, orbat=False),
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3",
          loadout="ASW", weapons="Hold",
          route=[(0.20, 136.15, 15000), (-0.40, 136.85, 15000)], loop=True,
          telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Biak fishing boat Wundi", route=[(-0.40, 136.75, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fishing",
          name="Biak fishing boat Korido", route=[(-0.30, 136.40, 0)], telegraph=2),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "coaster",
          name="KM Supiori Jaya (Manokwari-Jayapura)", route=[(-0.45, 137.40, 0)],
          telegraph=3),
    ],
    resolve={"Datum": "victory", "Traffic": "neutral",
             "Restraint": ("spare", "red_sub", "red_air"),
             "Aircraft": ("protect", "mpa"),
             "Watchers": ("classify", "red_air", 1)},
    declares=["RLO1GolfDatum"],
    expires_after="Routes They Can See",
    window=dict(),
    role="patrol",
)
