"""The campaign's spine: the calendar, the requisition roster, the Task Force
settings, the commander and the air-tasking rows. One place, so the schedule
reads as a schedule and a mission module that disagrees with it fails the
build.

What the collection can field for a Pakistan Navy task group in 2028, and
what it cannot (docs/campaigns/makran-line/campaign-bible.md, section 3):
the Pakistani Pack (Workshop 3812140001) gives the Type 054A/P (the Tughril
class), the Oliver Hazard Perry long hull PNS Alamgir, the Z-9CE and the
SH-3H, the JF-17 Block II and III and the ZDK-03. It has no Babur
(MILGEM), no Zulfiquar (F-22P), no Yarmook offshore patrol vessel, no PNS
Moawin or Nasr, no Agosta 90B and no P-3C, ATR or Sea Sultan patrol
aircraft. With no Pakistani supply ship in the collection there is nothing
to rearm the ships at sea, so every force allocation rearms them: the turn
round is at Karachi, between missions.
"""

# The mission modules, in campaign order. The builder sorts the spine by
# date, so this order is also the date order.
MODULES = [
    "mk01_the_fuel_road", "mk02_gwadar_roads", "mk03_hangor", "mk04_port_qasim",
]

# code: (date, completion points, generation, anchor station)
#
# Inside Southern Watch's six weeks (18 October to 28 November 2028), at the
# other end of the Indian Ocean: the same withdrawal of American combat
# power to the east (Southern Watch's "north" is seen from Australia) and
# the same Meridian network, here on the tanker road from the Gulf to
# Karachi. MK03 is a detached submarine operation, flown
# by an authored boat (generation None), the way Red Line's Under the
# Convergence is: the roster sells no submarine.
CALENDAR = {
    "MK01": ((2028, 10, 24), 100, "Generated", "escort"),
    "MK02": ((2028, 10, 31), 120, "Generated", "screen"),
    "MK03": ((2028, 11, 6), 80, None, None),
    "MK04": ((2028, 11, 14), 0, "Generated", "escort"),
}

TASKFORCE = dict(
    Enabled="True",
    TaskForceRequireFlagship="False",
    DefaultTaskForceName="Task Force 88",
    TaskForceNameOptions="Task Force 88|Arabian Sea Task Group|Makran Escort Group",
    CommanderSettingsFile="commander_settings.ini",
    RosterFile="player_task_force_roster.ini",
    TaskForceDifficultyPresets="Supported|Standard|Veteran",
    DefaultTaskForceDifficultyPreset="Standard",
    StartingPoints="1000",
    PointCap="1500",
    ShipIncludesAirwing="False",
    PurchaseLoadouts="True",
    CSARPointModifier="10",
    CrewSkillInitial="Trained",
    CrewSkillThresholds="Trained:1|Seasoned:4|Veterans:9|Ultra:16",
    UnitDecommissionPointReturnModifier="0.25",
    UnitDismissPointReturnModifier="0.5",
    DamageToAllowRepair="Light,Moderate",
    DamageToDisallowRepair="Heavy",
    RepairPointsCost="Light,0.1|Moderate,0.25",
)

DIFFICULTIES = [
    ("Supported", 1250, 1500, "0.75"),
    ("Standard", 1000, 1500, "1"),
    ("Veteran", 850, 1250, "1.25"),
]

# The requisition roster. Fictional prices; real variant and squadron names,
# checked by the builder against the winning files. Every unit registers
# Pakistan, so the same-nation discount covers the whole roster.
#
# Not for sale, on purpose:
#   - submarines. The builder sells none (build_pack's roster refuses them);
#     PNS Hangor is placed, named, in Hangor only.
#   - SEST Replenishment's plan_ffg_type_054a(_late)_rsa Variants 37-40,
#     which also register Pakistan: they are a second copy of the Tughril
#     class, and one class is sold once.
#   - the J-10CE (paf_j-10ce), held off the roster by the owner's decision
#     of 11 Nov 2026: the Air Force flies it from the north, not over the
#     Makran coast.
#   - PNS Alamgir is sold for 2028 as a stated scenario assumption. She was
#     commissioned in 2011 and her retirement date is not public; the
#     campaign assumes she is still in service in November 2028.
ROSTER = [
    dict(unit="pns_type_054a_p", picks=["Variant1", "Variant2", "Variant3", "Variant4"],
         points=280,
         note="the Tughril class, F-261 to F-264: the fleet's newest frigates; the Z-9CE "
              "lands on her deck through SEST Cross-Deck"),
    dict(unit="pns_ffg_oliver_hazard_perry_longhull", picks=["Variant1"], points=160,
         note="PNS Alamgir (F-260), the Perry long hull; kept in service for 2028 as a "
              "scenario assumption; her deck takes the Z-9CE (SEST Cross-Deck) and the "
              "pack's Sea King, which her deck list takes"),
    dict(unit="plan_z-9ce", picks=["Squadron1"], points=20,
         note="the frigates' Z-9CE flight; ASW and search"),
    dict(unit="pns_sh-3h", picks=["Squadron1"], points=25,
         note="the pack's Sea King, which the Alamgir's deck list takes; ASW"),
    dict(unit="paf_jf-17_blk_ii", picks=["Squadron1", "Squadron2"], points=40,
         note="Air Force JF-17 Block II out of Masroor or Gwadar; anti-ship and air "
              "defence fits"),
    dict(unit="paf_jf-17_blk_iii", picks=["Squadron1", "Squadron2"], points=50,
         note="Air Force JF-17 Block III; anti-ship and air defence fits"),
    dict(unit="paf_zdk-03", picks=["Squadron1"], points=70,
         note="Air Force ZDK-03 airborne early warning"),
]

# Air-tasking rows in the fit vocabulary of the aircraft this roster sells.
# The Z-9CE and the SH-3H both carry ASWHunter and ASWKiller; the Z-9CE
# declares MPA, ASW and SAR and the SH-3H ASW and SAR, so the ASW/SAR filter
# takes both. The JF-17s declare Bomber and Fighter and carry AntiShip,
# AntiShipHeavy, AirToAir and AirToAirLongRange; the ZDK-03 declares AEW.
HELO = "HeloRecon|Ship's Flight|ASW/SAR|1|ASWHunter/ASWKiller"
ATTACK = "Attack|Maritime Strike|Bomber|2|AntiShip/AntiShipHeavy"
CAP = "CAP|Combat Air Patrol|Fighter|2|AirToAir/AirToAirLongRange"
AEW = "Recon|Airborne Early Warning|AEW|1|AEW"

# The purchase windows, by stage. The opening sells the ships and their
# flights only: the Air Force's JF-17s and ZDK-03 are released to the task
# group from Gwadar Roads, so no fixed-wing aircraft is on sale before the
# second window.
OPENING = ["pns_type_054a_p", "pns_ffg_oliver_hazard_perry_longhull", "plan_z-9ce",
           "pns_sh-3h"]
AIR = ["paf_jf-17_blk_ii", "paf_jf-17_blk_iii", "paf_zdk-03"]
WHOLE = OPENING + AIR

# The commander. CommanderNations is the game's own key (nations.ini
# Pakistan=Pakistan), and the name pool is the game's own [Names_Pakistan]
# (language_en/ui.ini). The default name is invented, put together from that
# pool (first Kamran, middle Aziz, last Durrani) the way the game builds one.
# It was searched for on 11 Nov 2026 before it was used - the full name, and
# "Kamran Durrani" with "Commodore" and "Pakistan Navy" - and checked against
# the English Wikipedia's list of serving admirals of the Pakistan Navy: no
# naval officer of that name was found (the one Kamran on that list is Rear
# Admiral Kamran Ahmed). Checked again later that day: a web search for the
# full name, and for "Kamran Durrani" with Commodore, Admiral or Captain and
# "Pakistan Navy", found no naval officer; and the same Wikipedia list, as
# last edited on 5 Nov 2026, has no Durrani and no Aziz, and the same one
# Kamran. The nearest namesake found is not a naval officer: Kamran Shah
# Durrani, the nineteenth-century ruler of Herat. The player can change it
# on the commander screen, and the prose never uses it: the commander is
# "the task group commander" on every page.
#
# The ladder is the Pakistan Navy's ten commissioned ranks in their English
# Commonwealth form, Midshipman to Admiral, as the English Wikipedia's
# "Pakistan Navy ranks and insignia" lists them (citing the Navy's own
# 2013 ranks page). The abbreviations are NOT verified: the Navy's official
# site could not be read from the build environment, and the Wikipedia page
# gives none. They follow the Royal Navy's pattern - the ladder matches
# SEST's Royal Navy one, service_awards.UK_RANKS, letter for letter - and
# are marked unverified in RIBBONS.txt and the campaign's docs. The game ships rank insignia for
# three navies only, so every image field is empty. The navy emblem is the
# flag of Pakistan from the SEST gallery's flag set (public domain), which
# build_pack.py writes (SEST_EMBLEMS). Level 7 is Commodore, the rank a task
# group of this size is given: Task Force 88's first commander, at its
# inauguration at Gwadar on 13 Dec 2016, was a Commodore (the bible's
# section 1 has the reports).
COMMANDER = """[CommanderSettings]
CommanderNations=Pakistan
CommanderDefaultNation=Pakistan
CommanderNameDefaultPakistan=Kamran Aziz Durrani
CommanderNamePoolPakistan=Names_Pakistan
CommanderStartingRankLevel=7
SameNationUnitDiscount=0.2

NavyNamePakistan=Pakistan Navy
NavyEmblemPakistan=ui/campaign/navy_emblems/sest_pakn_emblem.png

[OfficerRanks]
Pakistan=Midshipman,MID,OF-D,1,|Sub-Lieutenant,SLT,OF-1,2,|Lieutenant,LT,OF-2,3,|Lieutenant Commander,LT CDR,OF-3,4,|Commander,CDR,OF-4,5,|Captain,CAPT,OF-5,6,|Commodore,CDRE,OF-6,7,|Rear Admiral,RADM,OF-7,8,|Vice Admiral,VADM,OF-8,9,|Admiral,ADM,OF-9,10,
"""
