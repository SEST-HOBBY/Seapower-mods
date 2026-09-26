"""RL01 - Trailing Contact. Molucca Sea, 5 November 2028.

Identification with the safety off. The carrier group comes down from the
Philippine Sea into the approaches with a diesel boat twelve miles astern of
Fujian and a Poseidon filming it. The group is under orders not to fire
first: put a class on the boat, keep the ship's flight from putting a
torpedo on her, and take the carrier to her station on time.

The mirror of Southern Reach's Silent Track, from the other side: here the
Chinese side names a Collins-class boat. Variant6 (Rankin) is a hull
neither coalition campaign places; the text calls her Contact ALPHA and
the class, never the name.
"""
from campaign_data import U, F, S
from .tables import HELO, NORTH_HULLS

MISSION = dict(
    code="RL01", series="Red Line", seq="RED LINE  ·  MISSION 1",
    group="core", num="01", key="Trailing Contact", place="Molucca Sea",
    intro=(
        "A submarine has been trailing the carrier since the Talaud Islands. Classify her. Do"
        " not fire on her."
    ),
    sender="Fleet headquarters",
    intent=((
        "The group is in the approaches to protect Chinese nationals and, if asked, to bring "
        "them out. It is not at war with any state and it will not fire first. A submarine "
        "following a carrier is doing her job: know which one she is and get on with ours. "
        "Fujian arrives on station intact and on time, and nothing the Australian aircraft "
        "records today shows a Chinese weapon in the water."
    )),
    date=(2028, 11, 5), time=(7, 10), sea=3, clouds="Scattered_1", wind="SE",
    difficulty=2, minutes=70, centre=(1.3, 126.7),
    blue_nation="China", red_nation="Australia",
    brief=(
        (
            "MOLUCCA SEA, 0710. The group came down from the Philippine Sea at first light, "
            "bound for its station in the Banda approaches. Last night DIPPER 21's sonar heard "
            "a diesel boat twelve miles astern of FUJIAN. She has been there since the Talaud "
            "Islands, matching the carrier's speed and keeping her distance. She is designated "
            "ALPHA.\\n\\nA RAAF Poseidon and a Triton are over the group. They are recording "
            "everything it does, and anything it does to that boat.\\n\\nPut a class on ALPHA, "
            "so the group knows what has been following it, then take FUJIAN to her morning "
            "station, twenty-two miles down the track. Your ships and helicopters start at "
            "weapons Hold. Set them free and"
            " the ship's flight may put a torpedo on the boat without being told, and that "
            "ends the operation.\\n\\nThe Ternate-Bitung ferry, two tuna boats and a coaster "
            "bound north for the Sangihe islands are in the same water. Identify before you "
            "act."
        )),
    forces=(
        "Your screen, with the ship's flight if one is embarked. Allocated: FUJIAN and her "
        "dipping Z-18F, Dipper 21. Watching: a RAAF P-8A and an MQ-4C Triton. Astern: one "
        "diesel submarine, ALPHA. Neutral: a ferry, two tuna boats and a coaster."
    ),
    objectives=[
        ("Contact", "Classify ALPHA, then take Fujian south to her morning station",
         "35,-35,Fail,Main"),
        ("Restraint", "Fire on nothing: not the boat, not the aircraft", "15,-40,Complete"),
        ("Carrier", "Bring Fujian through intact", "10,-30,Complete"),
        ("Traffic", "Harm no ferry, fishing boat or coaster", "0,-30,Complete"),
        ("Watchers", "Classify the patrol aircraft over the group", "10,0,None"),
    ],
    # Nothing counts until ALPHA has a class: the operation is called
    # Trailing Contact because knowing what she is IS the task. Then the
    # carrier on her morning station, 22 NM down the group's course (the Banda
    # station itself is days south; this is the first leg). The box is
    # authored so that Fujian's own route ends inside it: a solved box she
    # sailed through before the stage fired would leave her beyond it.
    victory=dict(kind="arrive", station="carrier", at=(1.24, 126.74), radius=10,
                 min_units=1, objective="Contact",
                 after=dict(kind="classify", units="red_sub", min_units=1,
                            intel=(
                                "SONAR REPORT: Contact ALPHA classified as a Collins-class "
                                "diesel submarine, Australian. She is holding twelve miles "
                                "astern and has not changed speed. The classification is "
                                "logged. It does not authorise an attack."
                            ))),
    # The ROE is the mission's hard rule: sink the boat or down either
    # aircraft and it is over, whoever gave the order. Fujian lost ends it
    # too; her loss is the carrier objective's own.
    fatal=[F("Restraint", ["red_sub", "red_air", "triton"]), F("Carrier")],
    neutral_objective="Traffic",
    win=(
        "FUJIAN is on her station and the boat astern has a class: Collins-class, "
        "Australian. She is still there. The Poseidon's recording shows a carrier group going "
        "about its business."
    ),
    lose=(
        "The group's first morning in the approaches has ended in an incident: something the "
        "orders protected is lost. Fleet headquarters has asked for the log, and the "
        "coalition already has the recording."
    ),
    timeout="0820, and FUJIAN is short of her station with a boat astern that still has "
            "no class. The group arrives late, and followed.",
    stations={
        # The group on its southbound track through the Molucca Sea: the
        # screen ahead, the carrier astern of it with her dipper, ALPHA
        # twelve miles behind the carrier. The station box is solved on
        # the group's course, 190.
        "screen": S(1.45, 126.75, "Screen", heading=190),
        "flight": S(1.43, 126.73, "Ship's flight", heading=190, alt=500),
        "carrier": S(1.60, 126.80, "Fujian", heading=190),
        "dipper": S(1.62, 126.84, "Dipper 21", heading=190, alt=500),
        "red_sub": S(1.80, 126.85, "Contact ALPHA", heading=190),
        # The Poseidon's racetrack runs the length of the group; the Triton
        # stays high to the south-west.
        "red_air": S(0.90, 127.05, "Patrol aircraft", heading=330, alt=15000),
        "triton": S(0.60, 126.40, "Triton", heading=20, alt=50000),
        "ferry": S(1.10, 126.90, "Ternate-Bitung ferry", heading=280),
        "fishing": S(1.25, 126.55, "Tuna boats", heading=60),
        "coaster": S(1.20, 126.75, "Coaster", heading=0),
    },
    units=[
        U("blue", "modern-plan-systems", "plan_type_054a_p5", "screen", variant="Variant1",
          weapons="Hold"),
        # Air-tasking placeholder: the cockpit a purchased Z-9C takes. No
        # name, no objective - slot-tagged aircraft keep the player's own.
        U("blue", "modern-plan-systems", "plan_z-9c", "flight", alt=500, weapons="Hold",
          loadout="ASWHunter", slot="HeloRecon"),
        U("blue", "fujian-cv-18", "plan_cv_type_003", "carrier", name="Fujian",
          weapons="Hold", route=[(1.24, 126.74, 0)], telegraph=3),
        U("blue", "chinese-navy-plan", "plan_z-18f", "dipper", name="Dipper 21",
          loadout="ASW", weapons="Hold"),
        # The boat that has been following since the Talaud Islands, still
        # following: a route down the group's track at a trailing speed.
        U("red", "SEST_RAN_Fleet", "ran_ssg_collins", "red_sub", variant="Variant6",
          name="Contact ALPHA", depth="belowlayer", weapons="Hold",
          route=[(1.20, 126.75, "belowlayer")], telegraph=2),
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3",
          loadout="ASW", weapons="Hold",
          route=[(1.90, 126.60, 15000), (0.90, 127.05, 15000), (1.90, 126.60, 15000)],
          telegraph=3),
        U("red", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "triton", weapons="Hold"),
        U("neutral", "_vanilla", "civ_ms_roro_b", "ferry",
          name="KM Tidore Express (Ternate-Bitung ferry)",
          route=[(1.30, 125.60, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Tuna boat Mina Sejahtera", route=[(1.40, 126.90, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "fishing",
          name="Tuna boat Bintang Laut", route=[(1.05, 126.45, 0)], telegraph=2),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "coaster",
          name="KM Sangihe Jaya", route=[(2.40, 126.70, 0)], telegraph=3),
    ],
    resolve={"Contact": "victory", "Traffic": "neutral",
             "Restraint": ("spare", "red_sub", "red_air", "triton"),
             "Carrier": ("protect", "carrier"),
             "Watchers": ("classify", "red_air", 1)},
    declares=[],
    window=dict(buy=True, repair=True, rearm=True, allow=list(NORTH_HULLS),
                flights=[HELO],
                situation=(
                    "Fleet headquarters has released the screen for the Banda "
                    "deployment. Select the escorts that will sail with the carrier group "
                    "and embark a Z-9C for the ship's flight if required. Fujian and her "
                    "dipping helicopter are allocated to this operation."
                )),
    role="patrol",
)
