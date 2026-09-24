"""The campaign's spine: the calendar, the requisition roster, the Task Force
settings and the commander. One place, so the schedule reads as a schedule
and a mission module that disagrees with it fails the build.
"""

# The mission modules, in campaign order. Chapter A then chapter B; the
# builder sorts the spine by date, so this order is also the date order.
MODULES = [
    "sr01_southern_departure", "sr02_silent_track", "sr03_search_datum",
    "sr04_macquarie_passage", "sr05_empty_horizon", "sr06_broken_supply_line",
    "sr07_beneath_the_south", "sr08_the_gateway", "sr09_cold_route",
    "sr10_southern_line", "sr11_last_ship_south", "sr12_turning_north",
    "ts01_home_waters", "ts02_cook_strait", "ts03_chatham_watch",
    "ts04_tasman_crossing", "ts05_under_the_tasman", "ts06_bass_strait",
    "ts07_southern_air_bridge", "ts08_great_australian_bight",
    "ts09_the_southern_convoy", "ts10a_northern_priority",
    "ts10b_southern_priority", "ts11_approaches", "ts12_southern_cross",
]

# code: (date, completion points, generation, anchor station)
#
# Generation "Generated" hands placement of the owned force to the campaign
# at the anchor; "Replaced" is the guide's pattern for a restricted
# detachment; None launches the file as authored - the detached submarine
# operations, the way Pacific Strike's 03A/07A/08A do it.
CALENDAR = {
    "SR01": ((2028, 12, 6), 100, "Generated", "escort"),
    "SR02": ((2028, 12, 9), 80, None, None),
    "SR03": ((2028, 12, 12), 100, "Generated", "escort"),
    "SR04": ((2028, 12, 15), 140, "Generated", "escort"),
    "SR05": ((2028, 12, 18), 100, None, None),
    "SR06": ((2028, 12, 21), 120, "Generated", "escort"),
    "SR07": ((2028, 12, 24), 140, "Generated", "escort"),
    "SR08": ((2028, 12, 28), 120, "Generated", "escort"),
    "SR09": ((2029, 1, 2), 160, "Generated", "escort"),
    "SR10": ((2029, 1, 6), 140, "Generated", "escort"),
    "SR11": ((2029, 1, 10), 160, "Generated", "escort"),
    "SR12": ((2029, 1, 14), 120, "Generated", "escort"),
    "TS01": ((2029, 1, 22), 100, "Generated", "escort"),
    "TS02": ((2029, 1, 25), 120, "Generated", "escort"),
    "TS03": ((2029, 1, 28), 100, "Generated", "escort"),
    "TS04": ((2029, 2, 1), 140, "Generated", "escort"),
    "TS05": ((2029, 2, 4), 100, None, None),
    "TS06": ((2029, 2, 8), 140, "Generated", "escort"),
    "TS07": ((2029, 2, 11), 140, "Generated", "escort"),
    "TS08": ((2029, 2, 15), 120, "Generated", "escort"),
    "TS09": ((2029, 2, 19), 180, "Generated", "escort"),
    "TS10A": ((2029, 2, 22), 60, "Generated", "escort"),
    "TS10B": ((2029, 2, 22), 60, "Generated", "escort"),
    "TS11": ((2029, 2, 26), 180, "Generated", "escort"),
    "TS12": ((2029, 3, 2), 0, "Generated", "escort"),
}

TASKFORCE = dict(
    Enabled="True",
    TaskForceRequireFlagship="False",
    DefaultTaskForceName="Southern Reach Task Group",
    TaskForceNameOptions="Southern Reach Task Group|TG 627.2|Antarctic Escort Group",
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

# The requisition roster. Same rules as Southern Watch's: fictional prices,
# real variant and squadron names checked against the winning files.
#
# Not for sale, on purpose: Collins (every submarine mission is a detached
# operation the way the stock campaign does them - the boat is authored and
# named), Supply and Stalwart (theatre logistics the missions protect), the
# RNZAF Poseidon (a national allocation, never the player's to own), and
# Arafura until the Tasman chapter (an offshore patrol vessel has no
# business south of the Convergence).
ROSTER = [
    dict(unit="ran_ffh_anzac",
         picks=["Variant2", "Variant3", "Variant5", "Variant6", "Variant7", "Variant8"],
         points=240,
         note="Arunta, Warramunga, Parramatta, Ballarat, Toowoomba and Perth; "
              "Variant1 (HMAS Anzac, decommissioned 2024) and Variant4 (Stuart, "
              "under repair after the north) stay out"),
    dict(unit="ran_ddg_hobart", picks=["Variant1", "Variant2", "Variant3"], points=480),
    dict(unit="ran_opv_arafura", picks=["Variant1"], points=100,
         note="on sale from the Tasman chapter only; the windows enforce it"),
    dict(unit="raaf_f-35a", picks=["Squadron1", "Squadron2"], points=45,
         note="3 and 77 Squadrons, RAAF Base Williamtown - the Tasman chapter's "
              "fighter base, checked against the SEST RAAF Bases air group"),
    dict(unit="usn_fa-18f_blk3", picks=["Squadron8"], points=35,
         note="Australian squadron in the SEST Growler pack's output"),
    dict(unit="usn_ea-18g", picks=["Squadron6"], points=55,
         note="conventional EW/SEAD fits; MALICE stays out of 2029"),
    dict(unit="usn_p8", picks=["Squadron3"], points=45,
         note="No. 11 and 12 Squadrons fly the same file; Squadron3 is the RAAF "
              "livery. Squadron6 is the RNZAF one and is never sold"),
    dict(unit="E7A_Wedgetail", picks=["Squadron1"], points=80),
    dict(unit="raaf_mq-4c_triton", picks=["Squadron1"], points=60,
         note="unarmed in this implementation"),
    dict(unit="usn_mh-60r", picks=["Squadron1"], points=20,
         note="one family chosen explicitly - usn_mh-60r_26 is a different "
              "unit and is never substituted for it"),
]

# The same RAN ladder Southern Watch uses (the base game's own, from Pacific
# Strike's commander_settings.ini). Level 6 is Captain: the commander who
# brought the task group out of the north was promoted for it, and the
# story says so.
COMMANDER = """[CommanderSettings]
CommanderNations=Australia
CommanderDefaultNation=Australia
CommanderNameDefaultAustralia=Morgan Reid
CommanderNamePoolAustralia=Names_Australia
CommanderStartingRankLevel=6
SameNationUnitDiscount=0

NavyNameAustralia=Royal Australian Navy
NavyEmblemAustralia=ui/campaign/navy_emblems/ran_emblem.png

[OfficerRanks]
Australia=Midshipman,MIDN,OF-D,0,ui/campaign/officer_ranks/australia/insignia_midn.png|Acting Sub Lieutenant,ASLT,OF-1,1,ui/campaign/officer_ranks/australia/insignia_aslt.png|Sub Lieutenant,SLT,OF-1,2,ui/campaign/officer_ranks/australia/insignia_slt.png|Lieutenant,LEUT,OF-2,3,ui/campaign/officer_ranks/australia/insignia_lt.png|Lieutenant Commander,LCDR,OF-3,4,ui/campaign/officer_ranks/australia/insignia_lcdr.png|Commander,CMDR,OF-4,5,ui/campaign/officer_ranks/australia/insignia_cdr.png|Captain,CAPT,OF-5,6,ui/campaign/officer_ranks/australia/insignia_capt.png|Commodore,CDRE,OF-6,7,ui/campaign/officer_ranks/australia/insignia_cdre.png|Rear Admiral,RADM,OF-7,8,ui/campaign/officer_ranks/australia/insignia_radm.png|Vice Admiral,VADM,OF-8,9,ui/campaign/officer_ranks/australia/insignia_vadm.png|Admiral,ADM,OF-9,10,ui/campaign/officer_ranks/australia/insignia_adm.png
"""
