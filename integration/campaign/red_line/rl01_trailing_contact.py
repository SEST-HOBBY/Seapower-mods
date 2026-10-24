"""RL01 — carrier defence and an optional trailing-contact investigation.

24 Oct 2026 pacing revision. Coalition observers are non-belligerents on the
neutral task force, so normal defensive weapons settings cannot turn an
intercept into an accidental attack on a protected Poseidon. Two declared
hostile chartered missile craft make timed strikes on Fujian. ALPHA's class
is useful intelligence, rather than a mandatory sonar search that blocks exit.
"""
from campaign_data import U, F, S
from .tables import HELO, NORTH_HULLS

MISSION = dict(
    code="RL01", series="Red Line", seq="RED LINE  ·  MISSION 1",
    group="core", num="01", key="Trailing Contact", place="Molucca Sea",
    intro="Defend Fujian against two missile craft. Investigate the trailing submarine if the screen has time.",
    sender="Fleet headquarters",
    intent=("Protect the carrier and clear the two declared hostile missile craft. The coalition's "
            "submarine and surveillance aircraft are not part of that attack. Protect them as "
            "non-belligerents; do not give the coalition an incident it did not start."),
    date=(2028, 11, 5), time=(7, 10), sea=3, clouds="Scattered_1", wind="SE",
    difficulty=3, minutes=40, centre=(1.3, 126.7),
    blue_nation="China", red_nation="Australia",
    brief=("MOLUCCA SEA, 0710. Two missile craft hired through a Meridian charter have attacked "
           "a coastal patrol outside the group's area and are now closing FUJIAN from the east "
           "and north-east. Their launchers are trained towards the group. Headquarters has "
           "declared those two craft hostile: engage them. Expect the first missile salvo at "
           "about minute eight if they are left alone, and another bearing shortly afterwards.\n\n"
           "Your screen is already ahead of the carrier. Bring FUJIAN to the nearby morning "
           "station and destroy both missile craft. Use the preparation phase to ready her "
           "flight deck, set the screen's sensors and weapons, and decide whether to intercept "
           "the shooters or meet their missiles. You do not have to wait for them to fire.\n\n"
           "DIPPER 21 also has a diesel-submarine report twelve miles astern of FUJIAN: ALPHA. "
           "A class on her earns intelligence credit but does not hold up completion. She has "
           "not attacked. The Australian Poseidon, Triton and Wedgetail are also observing. "
           "These non-belligerents use neutral tactical symbols and are protected; normal "
           "defensive settings can engage the hostile craft without authorising fire on them.\n\n"
           "A ferry, two tuna boats, a coaster and the Manado-Ambon service cross the picture. "
           "Identify the two missile craft; the rest of the traffic is not a target."),
    forces=("Your purchased screen and ship's flight. Allocated: Fujian and Dipper 21, a Z-18F. "
            "Hostile: two missile craft on separate bearings. Protected observers: ALPHA and "
            "three Australian surveillance aircraft. Civil traffic remains protected."),
    objectives=[
        ("Contact", "Destroy both missile craft and bring Fujian to the morning station", "35,-35,Fail,Main"),
        ("Raiders", "Stop both hostile missile craft", "20,0,None"),
        ("Restraint", "Do not attack the trailing submarine or surveillance aircraft", "15,-40,Complete"),
        ("Carrier", "Keep Fujian afloat", "10,-30,Complete"),
        ("Trail", "Classify ALPHA if the screen can spare the search", "15,0,None"),
        ("Traffic", "Harm no protected observer or civil contact", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="carrier", at=(1.45,126.77), radius=3,
                 min_units=1, objective="Contact",
                 also=[dict(kind="destroyed",units=["raider_e","raider_ne"],min_units=2),dict(kind="no_incoming")]),
    fatal=[F("Restraint",["red_sub","red_air","triton","wedgetail"]),F("Carrier")],
    neutral_objective="Traffic",
    reports=[dict(minute=2,intel="GROUP STAFF: The eastern and north-eastern missile craft are declared hostile. Intercept them before their scheduled launch windows if possible. ALPHA is an optional ASW task; keep the carrier on her short southbound leg.")],
    win="Both launch platforms are stopped and FUJIAN is on station. The group has defended itself without attacking the coalition's observers.",
    lose="FUJIAN is lost, or the group has attacked a protected observer. The defence has become an incident.",
    timeout="{deadline_clock}, and the group has not cleared both missile craft and brought the carrier to her station.",
    stations={
        "screen":S(1.45,126.75,"Screen",heading=190),
        "flight":S(1.43,126.73,"Ship's flight",heading=190,alt=500),
        "carrier":S(1.60,126.80,"Fujian",heading=190),
        "dipper":S(1.62,126.84,"Dipper 21",heading=190,alt=500),
        "raider_e":S(1.45,127.18,"Eastern missile craft",heading=270),
        "raider_ne":S(1.82,127.10,"North-eastern missile craft",heading=225),
        "red_sub":S(1.80,126.85,"Contact ALPHA",heading=190),
        "red_air":S(0.90,127.05,"Protected patrol aircraft",heading=330,alt=15000),
        "triton":S(0.60,126.40,"Protected Triton",heading=20,alt=50000),
        "wedgetail":S(-0.30,126.90,"Protected Wedgetail",heading=60,alt=30000),
        "airliner":S(0.92,125.31,"Manado-Ambon service",heading=150,alt=33000),
        "ferry":S(1.10,126.90,"Ternate-Bitung ferry",heading=280),
        "fishing":S(1.25,126.55,"Tuna boats",heading=60),
        "coaster":S(1.20,126.75,"Coaster",heading=0),
    },
    units=[
        U("blue","modern-plan-systems","plan_type_054a_p5","screen",variant="Variant1",weapons="Tight"),
        U("blue","modern-plan-systems","plan_z-9c","flight",alt=500,weapons="Hold",loadout="ASWHunter",slot="HeloRecon"),
        U("blue","modern-plan-systems","plan_cv_type_003","carrier",name="Fujian",weapons="Tight",route=[(1.45,126.77,0)],telegraph=3),
        U("blue","chinese-navy-plan","plan_z-18f","dipper",name="Dipper 21",loadout="ASW",weapons="Hold"),
        U("red","_vanilla","plan_ptg_type_021","raider_e",name="Meridian missile craft 41",nation="Panama",weapons="Hold",loadout="Late",
          route=[(1.49,126.92,0)],telegraph=2,attacks=[(8,"plan_sy-1a","carrier",2)]),
        U("red","_vanilla","plan_ptg_type_021","raider_ne",name="Meridian missile craft 42",nation="Panama",weapons="Hold",loadout="Late",
          route=[(1.53,126.94,0)],telegraph=2,attacks=[(12,"plan_sy-1a","carrier",2)]),
        U("neutral","SEST_RAN_Fleet","ran_ssg_collins","red_sub",variant="Variant3",name="Contact ALPHA",nation="Australia",depth="belowlayer",weapons="Hold",radars="False",
          route=[(1.20,126.75,"belowlayer")],telegraph=2,recognise=False),
        U("neutral","p-8-poseidon","usn_p8","red_air",squadron="Squadron3",nation="Australia",loadout="ASW",weapons="Hold",
          route=[(1.90,126.60,15000),(0.90,127.05,15000)],loop=True,telegraph=3),
        U("neutral","SEST_ADF_Persistent_ISR","raaf_mq-4c_triton","triton",nation="Australia",weapons="Hold"),
        U("neutral","e-7a-wedgetail","E7A_Wedgetail","wedgetail",squadron="Squadron1",nation="Australia",weapons="Hold",
          route=[(-0.45,126.55,30000),(-0.10,127.25,30000)],loop=True,telegraph=3),
        U("neutral","_vanilla","civ_ms_roro_b","ferry",name="KM Tidore Express (Ternate-Bitung ferry)",nation="Indonesia",route=[(1.30,125.60,0)],telegraph=3),
        U("neutral","_vanilla","civ_fv_fishingboat_a","fishing",name="Tuna boat Mina Sejahtera",route=[(1.40,126.90,0)],telegraph=2),
        U("neutral","_vanilla","civ_fv_sterntrawler_a","fishing",name="Tuna boat Bintang Laut",nation="Indonesia",route=[(1.05,126.45,0)],telegraph=2),
        U("neutral","re-power-resupply","civ_ms_freighter_a","coaster",name="KM Sangihe Jaya",route=[(2.40,126.70,0)],telegraph=3),
        U("neutral","civil-aircraft-airbus","civ_a330","airliner",name="Manado-Ambon service",squadron="Squadron50",airway=(-3.71,128.09)),
    ],
    resolve={"Contact":"victory","Raiders":("destroy",["raider_e","raider_ne"],2),
             "Traffic":"neutral","Restraint":("spare","red_sub","red_air","triton","wedgetail"),
             "Carrier":("protect","carrier"),"Trail":("classify","red_sub",1)},
    declares=[],
    window=dict(buy=True,repair=True,rearm=True,allow=list(NORTH_HULLS),flights=[HELO],
                situation="Select the carrier screen and its ship's flight. Fujian and Dipper 21 are allocated. Prepare anti-missile defence and a surface strike: the missile craft are hostile, the coalition's observers are protected non-belligerents."),
    role="patrol",
)
