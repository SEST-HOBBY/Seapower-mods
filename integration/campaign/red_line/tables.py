"""The campaign's spine: the calendar, the requisition roster, the Task Force
settings, the commander and the air-tasking rows. One place, so the schedule
reads as a schedule and a mission module that disagrees with it fails the
build.
"""

# The mission modules, in campaign order. The builder sorts the spine by
# date, so this order is also the date order.
MODULES = [
    "rl01_trailing_contact", "rl02_routes_they_can_see", "rl03_the_other_picture",
    "rl04_the_order_to_withdraw", "rl05_under_the_convergence", "rl06_the_quiet_side",
]

# code: (date, completion points, generation, anchor station)
#
# Every date sits between two things the coalition's campaigns already say
# happened, and none of them lands on a day either of those campaigns flies
# the same water (docs/campaigns/red-line/campaign-bible.md, the timeline).
# Generation "Generated" hands placement of the owned screen to the campaign
# at the anchor; None launches the file as authored - RL05 is a detached
# submarine operation, the way Southern Reach's SR02 is.
CALENDAR = {
    "RL01": ((2028, 11, 5), 100, "Generated", "screen"),
    "RL02": ((2028, 11, 12), 120, "Generated", "escort"),
    "RL03": ((2028, 11, 19), 140, "Generated", "shadow"),
    "RL04": ((2028, 11, 27), 120, "Generated", "escort"),
    "RL05": ((2028, 12, 27), 80, None, None),
    "RL06": ((2029, 1, 19), 0, "Generated", "decoy"),
}

TASKFORCE = dict(
    Enabled="True",
    TaskForceRequireFlagship="False",
    DefaultTaskForceName="Carrier Group Screen",
    TaskForceNameOptions="Carrier Group Screen|Escort Division|Protection Group Screen",
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

# The requisition roster: the carrier group's screen and what flies from it.
# Fictional prices; real variant and squadron names, checked by the builder
# against the winning files.
#
# Not for sale, on purpose: Fujian and Liaoning (the group's carriers are the
# thing the screen protects, placed and named where a mission needs one), the
# submarines (every boat operation is authored and named), the Z-18F and the
# replenishment ship (allocated where the story puts them), and the Type 052D
# (its thousand-mile hypersonic has no place in a campaign won by restraint).
ROSTER = [
    dict(unit="plan_type_054a_p5", picks=["Variant1", "Variant2", "Variant3", "Variant4"],
         points=280,
         note="the everyday escort; supports the Z-9 family on its deck"),
    dict(unit="plan_ddg_luda_typ_051dt", picks=["Variant1", "Variant2"], points=160,
         note="an older destroyer the northern screen still has"),
    dict(unit="plan_em_sovremenny", picks=["Variant1", "Variant2"], points=320,
         note="on sale in the north only; one already owned still sails"),
    dict(unit="plan_type_056a", picks=["Variant1", "Variant2", "Variant3"], points=120,
         note="the protection group's corvette; on sale in the south only"),
    dict(unit="plan_z-9c", picks=["Squadron1"], points=20,
         note="the frigate's flight; the 054A deck lists the Z-9C, D and F"),
    dict(unit="plan_y-9fq", picks=["Squadron1"], points=50,
         note="maritime patrol out of the enclave field; north only"),
    dict(unit="plaaf_kj-500", picks=["Squadron1"], points=70,
         note="land-based airborne early warning; matches the Recon row's AEW fit"),
    dict(unit="plan_j-15", picks=["Squadron1", "Squadron2"], points=40,
         note="carrier-capable; recovers on the enclave field when no deck is placed"),
    dict(unit="plan_j-15d", picks=["Squadron1"], points=45),
]

# Air-tasking rows in the fit vocabulary of the aircraft this roster sells.
# Southern Watch's rows name RAAF and US Navy fits (MurderHornetCAP,
# ASWPatrol) that no aircraft here defines, and the builder's flight check
# refuses a row that offers a fit nothing in it can fly. The Z-9C declares
# ASW and MPA as well as SAR, so it matches the Recon filter too and every
# Recon row has to carry a fit it flies.
HELO = "HeloRecon|Ship's Flight|SAR|1|ASWKiller/ASWHunter"
RECON = "Recon|Maritime Patrol|MPA/ASW/ESM/AEW|1|ASW/ASWKiller/ASWHunter/AEW"
CAP = "CAP|Combat Air Patrol|Fighter|2|AirToAir/AirToAirIntercept"

# The purchase windows, by stage. The variants come from ROSTER, never
# restated.
NORTH_HULLS = ["plan_type_054a_p5", "plan_ddg_luda_typ_051dt", "plan_em_sovremenny",
               "plan_z-9c"]
NORTH_AIR = ["plan_y-9fq"]
CARRIER_AIR = ["plan_j-15", "plan_j-15d", "plaaf_kj-500"]
SOUTH_HULLS = ["plan_type_054a_p5", "plan_type_056a", "plan_z-9c"]

# The commander. CommanderNations and the name pool are the game's own
# (language_en/ui.ini [Names_China]). The default name is invented, put
# together from that pool (last name Cao, first Ming, middle Yuan) the way
# the game builds one, and searched for before it was used - in English and
# in Chinese characters, with "navy", "PLA" and the flag ranks - with no
# naval officer of that name found. The player can change it on the
# commander screen, and the prose never uses it: he is "the group
# commander" on every page and in every briefing.
#
# The ladder is the Chinese navy's officer ranks with their NATO grades.
# The game ships rank insignia and navy emblems for the United States,
# Japan and Australia only (Pacific Strike's commander_settings.ini), so the
# image field of every rank is empty and no emblem is referenced: a path to
# a picture this repo cannot produce would be worse than none. How the
# commander screen draws an empty insignia is on the test card. Level 8 is
# Rear Admiral, the rank a two-carrier group is given.
COMMANDER = """[CommanderSettings]
CommanderNations=China
CommanderDefaultNation=China
CommanderNameDefaultChina=Cao Mingyuan
CommanderNamePoolChina=Names_China
CommanderStartingRankLevel=8
SameNationUnitDiscount=0

NavyNameChina=People's Liberation Army Navy

[OfficerRanks]
China=Ensign,ENS,OF-1,1,|Lieutenant Junior Grade,LTJG,OF-1,2,|Lieutenant,LT,OF-2,3,|Lieutenant Commander,LCDR,OF-3,4,|Commander,CDR,OF-4,5,|Captain,CAPT,OF-5,6,|Senior Captain,SCAPT,OF-6,7,|Rear Admiral,RADM,OF-7,8,|Vice Admiral,VADM,OF-8,9,|Admiral,ADM,OF-9,10,
"""
