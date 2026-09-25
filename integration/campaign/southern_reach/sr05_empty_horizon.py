"""SR05 - Empty Horizon. The open Southern Ocean, 18 December 2028.

An allocated air operation, blank generation: a Triton and a Poseidon,
nothing of the owned force. Classify the protection group's command element
among a fishing fleet, a Russian oiler and a cruise ship, and bring the
Triton home. Nothing scores "undetected"; the frigate's missiles are the
reason the Triton cannot simply overfly, and the briefing says so.
"""
from campaign_data import U, F, S

MISSION = dict(
    code="SR05", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 5",
    group="core", num="05", key="Empty Horizon", place="The open Southern Ocean",
    intro="Two aircraft, an empty ocean, and a group somewhere in it that "
          "calls itself fisheries protection. Put a class and a name on its "
          "command element and bring the Triton home.",
    special=(
        "This detached reconnaissance uses the allocated Triton and Poseidon. Your standing "
        "task group remains on its other duties. Contact classifications from this sortie will "
        "support the January patrol at the ice edge."
    ),
    sender="Wing Commander Daniel Ward, Air Component, RAAF Edinburgh",
    intent=((
        "The protection group has a command element somewhere south of the fishing fleet and "
        "nobody has put a class on it. Sentry 22 and Bluefin 32 are assigned to establish the "
        "local picture from the earlier search cues. Classify the frigate and the corvette, and"
        " the Triton comes home; losing the Triton leaves a major gap in local surveillance. "
        "The frigate has a surface-to-air missile with a forty-mile reach and no reason yet to "
        "use it. Do not give it one, and do not give me a reason to explain a Poseidon."
    )),
    date=(2028, 12, 18), time=(10, 40), sea=6, clouds="Broken_3", wind="W",
    difficulty=2, minutes=65, centre=(-56.0, 148.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "THE SOUTHERN OCEAN, 56 South, mid-morning. The protection group's command element "
            "- a frigate, a corvette, the research trawler NAN HAI 27 and whatever is keeping "
            "them fuelled - has been south of the fishing fleet for a week. Satellite radar "
            "detections and merchant reports give a broad search area, but identities and "
            "present positions remain uncertain.\\n\\nSENTRY 22 is high and BLUEFIN 32 is under "
            "the cloud, both out of Hobart, both with the fuel for one look. The fleet is three"
            " factory trawlers, a Russian oiler that visits it, and the expedition ship POLAR "
            "HORIZON coming home to the west of them.\\n\\nClassify the frigate and the corvette,"
            " then recover the Triton to the point north. The frigate's missiles reach forty "
            "miles and nobody has fired at an aircraft yet; you are not going to be the first. "
            "Nothing here is a target. Bring back the identification report."
        )),
    forces="One MQ-4C Triton, one P-8A, both allocated, both out of Hobart. "
           "Neutral: three factory trawlers, an expedition cruise ship, a "
           "whale. Opposing: a Type 054A frigate and a Type 056A corvette "
           "with a Ka-31 and a Z-9 up, the research trawler Nan Hai 27, and "
           "a Russian oiler.",
    objectives=[
        ("Picture", "Classify the frigate and the corvette", "25,-25,Fail"),
        ("Recover", "Then bring Sentry 22 to the recovery point north",
         "15,-20,Fail,Main"),
        ("Sentry", "Do not lose the Triton", "20,-25,Complete"),
        ("Bluefin", "Do not lose the Poseidon", "10,-15,Complete"),
        ("Neutrals", "Harm no trawler, cruise ship or whale", "0,-25,Complete"),
    ],
    # The classify pays twice on purpose: the Picture objective completes
    # (and writes the variable Southern Line reads) and the stage opens the
    # recovery box. Same contacts, same condition.
    victory=dict(kind="arrive", station="high", min_units=1, objective="Recover",
                 at=(-54.0, 148.3), radius=15,
                 after=dict(kind="classify", units=["group#1", "group#2"],
                            min_units=2,
                            intel=(
                                "SENTRY 22 REPORT: Type 054A frigate and Type 056A corvette "
                                "classified. The intelligence cell can now correlate these "
                                "contacts with earlier satellite detections. Withdraw the "
                                "Triton north; maintain separation from the frigate's "
                                "air-defence envelope."
                            ))),
    fatal=[F("Sentry", ["high"])],
    neutral_objective="Neutrals",
    win="The Triton is at the recovery point with the group's command "
        "element classified and on file. Ward: 'That is the whole south "
        "on one plot. Now bring the aeroplane home.'",
    lose=(
        "The reconnaissance operation has failed. Existing imagery and reports remain "
        "available, but they cannot replace a current patrol picture. Command must reassess "
        "coverage before the next convoy."
    ),
    timeout="Fuel. Both aircraft turn for Hobart with the frigate still a "
            "contact and the corvette still a rumour.",
    stations={
        # The aircraft 90-100 NM north of the group; the group holding
        # station south of the fleet with its helicopters up; the fleet and
        # the cruise ship between them, which is the identification problem.
        "high": S(-55.40, 148.30, "Sentry 22", heading=180, alt=50000),
        "mpa": S(-55.60, 147.60, "Bluefin 32", heading=180, alt=15000),
        "group": S(-57.30, 148.40, "Command element", heading=90),
        "agi": S(-57.28, 148.45, "Research trawler", heading=90),
        "red_helo": S(-57.15, 148.60, "Ka-31 orbit", heading=90, alt=9000),
        "red_dip": S(-57.35, 148.10, "Z-9 dip", heading=270, alt=1500),
        "oiler": S(-57.60, 147.50, "Russian oiler", heading=60),
        "fleet": S(-57.00, 149.20, "Factory trawlers", heading=270),
        "cruise": S(-56.60, 147.00, "Polar Horizon", heading=20),
        "whale": S(-56.80, 148.20, "Biologic", heading=90),
        "home": S(-42.836, 147.510, "Hobart Airport"),
    },
    units=[
        U("blue", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "high",
          name="Sentry 22", weapons="Hold"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3",
          name="Bluefin 32", alt=15000, weapons="Tight", loadout="ASW"),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "group",
          name="Fisheries protection frigate", weapons="Tight",
          route=[(-57.30, 149.00, 0)], telegraph=2),
        U("red", "modern-plan-systems", "plan_type_056a", "group",
          name="Fisheries protection corvette", weapons="Tight",
          route=[(-57.30, 149.00, 0)], telegraph=2),
        # Her own station, so the Picture objective and the variable it
        # writes are the two warships and not any two of three.
        U("red", "_vanilla", "wp_agi_okean", "agi", name="Research trawler Nan Hai 27",
          weapons="Hold", route=[(-57.30, 149.00, 0)], telegraph=2),
        U("red", "modern-plan-systems", "plan_ka-31", "red_helo", name="Ka-31 eye",
          alt=9000, weapons="Hold", loadout="AEW"),
        U("red", "modern-plan-systems", "plan_z-9c", "red_dip", name="Z-9 dip",
          alt=1500, loadout="ASWKiller"),
        U("red", "re-power-resupply", "wp_vt_boris_chilikin", "oiler",
          name="Oiler Boris Chilikin", weapons="Hold",
          route=[(-57.40, 148.20, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 21",
          route=[(-56.80, 148.60, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 24",
          route=[(-57.10, 148.50, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_okean", "fleet", name="Factory trawler Nan Hai 29",
          route=[(-56.90, 148.80, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_ivan_franko", "cruise",
          name="MV Polar Horizon (expedition cruise)",
          route=[(-55.80, 147.40, 0)], telegraph=3),
        U("neutral", "humpback-whale", "civ_humpback", "whale", name="Biologic HOTEL",
          depth="shallow"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Hobart Airport (RAAF detachment)", nation="australia", weapons="Hold"),
    ],
    resolve={"Recover": "victory", "Neutrals": "neutral",
             "Picture": ("classify", "group", 2, "SR05GroupClassified"),
             "Sentry": ("protect", "high"),
             "Bluefin": ("protect", "mpa")},
    declares=["SR05GroupClassified"],
    reveal_if=[dict(variable="SR01ShadowNamed", units=["agi"], level="Classify",
                    intel=(
                        "FUSION CELL: Earlier Storm Bay reporting identifies NAN HAI 27. That "
                        "identification has been correlated with the collector in the current "
                        "search area; the collector is on the plot and held there for the "
                        "operation. The frigate and corvette still require classification."
                    ))],
    window=dict(),
    role="recon",
)
