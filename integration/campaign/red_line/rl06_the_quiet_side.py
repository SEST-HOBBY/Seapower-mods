"""RL06 — defend the tender against a contractor Q-ship, then rendezvous.

24 Oct 2026: the decoy check is at minute eight rather than thirty. A
Meridian Q-ship attacks the tender; the submarine can counter it. Being
classified costs the stealth bonus but no longer instantly discards the
operation. Kiwi 05 remains protected. No outcome of another campaign is set.
"""
from campaign_data import U, F, S
from .tables import HELO, SOUTH_HULLS

MISSION = dict(
    code="RL06", series="Red Line", seq="RED LINE  ·  MISSION 6",
    group="core", num="06", key="The Quiet Side", place="Fiordland approaches",
    intro="The screen draws the patrol; the submarine must protect the tender from a hostile Q-ship.",
    sender="Fleet headquarters, southern tasking",
    intent="Complete the rendezvous and protect the tender. The contractor Q-ship is a declared hostile. Kiwi 05 and civil traffic are protected. Concealment earns credit, but losing it does not erase a successful defence.",
    date=(2029, 1, 19), time=(5, 20), sea=5, clouds="Broken_3", wind="SW",
    difficulty=4, minutes=45, centre=(-46.3, 166.0),
    blue_nation="China", red_nation="NewZealand",
    geography="coast",
    brief=("FIORDLAND APPROACHES, 0520. AUSTRAL COMPLIANCE is on the final approach to meet "
           "HULL 334. One of Meridian's contractor vessels, FV AUSTRAL WARDEN, has rejected the "
           "handover and is closing the tender. It is a Q-ship with a wake-homing torpedo, "
           "not another fishing boat. Expect its attack around minute twelve if it is left "
           "alone. The Q-ship is declared hostile and may be engaged before it fires.\n\n"
           "Your screen still provides the loud decoy on the eastern station, but it needs to "
           "be there at minute eight while the tender completes the final leg. The screen is "
           "some thirty miles from the rendezvous; HULL 334 is the "
           "nearby combat unit and can counter the Q-ship while the screen holds the patrol's "
           "attention. Keep enough time for a torpedo to reach the Q-ship before its own shot "
           "reaches the slow tender.\n\n"
           "Destroy the Q-ship and bring the tender and boat together in the holding box. "
           "KIWI 05 remains a protected patrol aircraft. Leave it alone. Keep HULL 334 quiet "
           "where possible: classification loses the concealment bonus but does not end the "
           "mission. Report the compromise and continue the defence and rendezvous.\n\n"
           "The Milford cruise ship and local fishing boats are protected. They are not cover "
           "for an indiscriminate attack."),
    forces="Your screen and its flight; allocated tender Austral Compliance and Type 039C Hull 334. Hostile: one contractor Q-ship. Protected: Kiwi 05, the cruise ship and fishing traffic.",
    objectives=[
        ("Rendezvous", "Cover the decoy station at minute eight, stop the Q-ship, then bring the tender and "
                       "Hull 334 to the holding position", "35,-35,Fail,Main"),
        ("Unseen", "Avoid classification if possible; detection does not end the mission",
         "25,-15,Complete"),
        ("Restraint", "Do not attack Kiwi 05 or civil traffic", "15,-40,Complete"),
        ("Frigate", "Bring the screen off the decoy station intact", "10,-20,Complete"),
        ("Tender", "Keep Austral Compliance afloat", "10,-30,Complete"),
        ("Boat", "Keep Hull 334 afloat", "10,-30,Complete"),
        ("Qship", "Destroy the hostile Q-ship threatening the tender", "20,0,None"),
        ("Traffic", "Harm no cruise ship or fishing boat", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="tender", at=(-46.38, 165.45), radius=4,
                 min_units=1, objective="Rendezvous",
                 also=[dict(units=["boat"], min_units=1),dict(kind="destroyed",units=["qship"],min_units=1),dict(kind="no_incoming")],
                 after=dict(kind="area", units="decoy", at=(-46.32, 166.15), radius=8,
                            min_units=1, after_minutes=8,
                            intel=(
                                "DECOY REPORT: The screen is on the decoy station at minute eight. The "
                                "rendezvous is cleared to proceed."
                            ))),
    fatal=[F("Restraint", ["red_air"]),F("Tender"),F("Boat")],
    neutral_objective="Traffic",
    win="The Q-ship is stopped and Austral Compliance has met Hull 334. The tender and boat survived; concealment is scored separately from the completed rendezvous.",
    lose="The tender or Hull 334 is lost, or the protected patrol aircraft has been destroyed. The rendezvous cannot proceed.",
    timeout="{deadline_clock}, and the tender and boat have not completed their defended rendezvous.",
    stations={
        "decoy": S(-46.32, 166.15, "Decoy station", heading=200),
        "flight": S(-46.30, 166.13, "Ship's flight", heading=200, alt=500),
        "qship": S(-46.38,165.22,"Hostile Q-ship",heading=60),
        "tender": S(-46.30,165.34, "Austral Compliance", heading=170),
        "boat": S(-46.28,165.42,"Hull 334", heading=190),
        "red_air": S(-46.00, 166.20, "Kiwi 05", heading=220, alt=12000),
        "cruise": S(-45.90, 166.00, "Milford-bound", heading=20),
        "cray": S(-46.25, 166.40, "Cray boat", heading=120),
        "longliner": S(-46.50, 165.80, "Longliner", heading=250),
    },
    units=[
        U("red","project-2498-zyetseth","civ_fv_okean_surprise","qship",name="FV Austral Warden",nation="Panama",weapons="Hold",
          route=[(-46.32,165.37,0)],telegraph=3,attacks=[(12,"wp_53-65K","tender",1)]),
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "decoy", variant="Variant4",
          weapons="Hold"),
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "_vanilla", "civ_ms_kommunist", "tender",
          name="MV Austral Compliance (AMS tender)", nation="Panama", weapons="Hold",
          radars="False", route=[(-46.38, 165.45, 0)], telegraph=3),
        U("blue", "plan-submarines", "plan_ss_type_039c", "boat", name="Hull 334",
          depth="belowlayer", weapons="Hold", radars="False",
          route=[(-46.38, 165.47, "belowlayer")], telegraph=3),
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron6", name="Kiwi 05",
          loadout="ASW", weapons="Hold",
          route=[(-46.50, 165.60, 12000), (-46.00, 166.20, 12000)], loop=True,
          telegraph=3),
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Southern Explorer (Milford cruise)", nation="Panama",
          route=[(-45.30, 166.30, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "cray",
          name="Cray boat Tawaki (Bluff)", route=[(-46.40, 166.70, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "longliner",
          name="Longliner Otago Venture", route=[(-46.70, 165.00, 0)], telegraph=2),
    ],
    resolve={"Rendezvous": "victory", "Traffic": "neutral",
             "Unseen": ("unseen", "boat"),
             "Restraint": ("spare", "red_air"),
             "Frigate": ("protect", "decoy"),"Tender": ("protect","tender"),
             "Boat": ("protect","boat"),"Qship": ("destroy","qship",1)},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True, allow=list(SOUTH_HULLS),
                flights=[HELO],
                situation=(
                    "The protection group's screen is at sea in the Tasman. A frigate or a "
                    "corvette can be allocated for the decoy station; the tender and Hull 334"
                    " are allocated to this operation. The ship's flight is the only air "
                    "tasking, and no operation follows this one: a fixed-wing aircraft "
                    "allocated here will not fly."
                )),
    reports=[dict(minute=2,intel="TENDER CONTROL: Austral Warden is the hostile Q-ship, west of the tender. Hull 334 can engage it; the frigate should not abandon the decoy station before minute eight. Losing concealment costs points, not the whole operation.")],
    role="escort",
)
