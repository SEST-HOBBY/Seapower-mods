"""The campaign's spine: the calendar, the requisition roster, the Task Force
settings, the commander and the air-tasking rows. One place, so the schedule
reads as a schedule and a mission module that disagrees with it fails the
build.

The rule this campaign is built around: there is no free rearm. No window
from the second mission on rearms the force. What a ship fires stays fired
until a supply ship the player bought - BRP Tarlac or her sister, the Thai
oiler Chula, or a chartered MSC barge carrier - comes alongside at sea and
passes it back, or until a convoy the player escorted holds its service
window. Supply ships are sold only in three windows, so one that is sunk
stays sunk until the next of them, and costs its price again.
"""

# The mission modules, in campaign order. The builder sorts the spine by
# date, so this order is also the date order.
MODULES = [
    "sl01_the_island_road", "sl01a_night_market", "sl02_fire_mission_jolo",
    "sl03_ayungin", "sl03a_the_okean", "sl04_service_at_sea", "sl05_celebes_gate",
    "sl05a_the_drone_yard",
    "sl06_the_aborlan_battery", "sl07_balabac_strait",
]

# code: (date, completion points, generation, anchor station)
#
# Southern Watch's six weeks, October to November 2028, seen from the other
# end of the archipelago: the same Meridian network and the same Chinese
# pressure, in the Sulu Sea and the West Philippine Sea while the Australian
# task group holds the Arafura. Every mission is Generated on its anchor, so
# the bought force - supply ships included - sails in all seven.
CALENDAR = {
    "SL01": ((2028, 10, 12), 100, "Generated", "screen"),
    # The side operations (docs/campaigns/side-operations.md): optional,
    # flown by a fixed force the mission supplies, so nothing the player
    # owns sails and the no-free-rearm magazines are untouched.
    "SL01A": ((2028, 10, 15), 50, None, None),
    "SL02": ((2028, 10, 19), 120, "Generated", "gunline"),
    "SL03": ((2028, 10, 26), 120, "Generated", "escort"),
    "SL03A": ((2028, 10, 29), 60, None, None),
    "SL04": ((2028, 11, 2), 100, "Generated", "screen"),
    "SL05": ((2028, 11, 9), 140, "Generated", "patrol"),
    "SL05A": ((2028, 11, 12), 60, None, None),
    "SL06": ((2028, 11, 16), 140, "Generated", "gunline"),
    "SL07": ((2028, 11, 23), 0, "Generated", "screen"),
}

TASKFORCE = dict(
    Enabled="True",
    TaskForceRequireFlagship="False",
    DefaultTaskForceName="Sulu Sea Task Group",
    TaskForceNameOptions="Sulu Sea Task Group|Task Group Sulu|Coalition Escort Group",
    CommanderSettingsFile="commander_settings.ini",
    RosterFile="player_task_force_roster.ini",
    TaskForceDifficultyPresets="Supported|Standard|Veteran",
    DefaultTaskForceDifficultyPreset="Standard",
    StartingPoints="1000",
    PointCap="1600",
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
    ("Supported", 1250, 1600, "0.75"),
    ("Standard", 1000, 1600, "1"),
    ("Veteran", 850, 1350, "1.25"),
]

# The requisition roster. Fictional prices; real variant and squadron names,
# checked by the builder against the winning files. Philippine units take
# the same-nation discount; the Thai and Australian ships and the MSC
# charter cost their listed price, and the rules page says so.
#
# The supply ships are the campaign. Each is a working supplier (SEST
# Replenishment At Sea, tuned in integration/common/ras.py): close to half a
# mile, slow to eight knots, and what she carries crosses - guns, MICA,
# Harpoon and light torpedoes from the Tarlac and Chula, almost anything
# from the C8. Their pools are finite and whatever they hand over is gone
# from them.
ROSTER = [
    dict(unit="pn_ffg-150", picks=["Variant1", "Variant2"], points=300,
         note="BRP Jose Rizal and Antonio Luna: the fleet's two modern frigates"),
    dict(unit="pn_ffg-06", picks=["Variant1", "Variant2"], points=320,
         note="the Miguel Malvar class, the newest hulls; VLS MICA"),
    dict(unit="phl_ff_hamilton", picks=["Variant1", "Variant2", "Variant3"], points=140,
         note="the Del Pilar class: old cutters, a 76 mm gun and a deck"),
    dict(unit="phl_fs_pohang", picks=["Variant1"], points=110,
         note="BRP Conrado Yap; guns and nothing else"),
    dict(unit="phl_lpd_tarlac", picks=["Variant1", "Variant2"], points=140,
         note="SUPPLY: Tarlac and Davao del Sur; 60,000-point pool, 2000-point ceiling"),
    # Squadron2 first: the mod's AW109E LAH, its AW109 livery on the H-76
    # model (Luzon Line's language_en/aircraft_names.ini); Squadron1 is the
    # 1983 AUH-76. The missions place the AW109E too.
    dict(unit="phl_h-76", picks=["Squadron2", "Squadron1"], points=25,
         note="the Navy's flight: AW109E LAH (the mod's AW109 livery on the H-76 "
              "model) or AUH-76; CAS and transport"),
    dict(unit="rok_f-50_ph", picks=["Squadron1"], points=60,
         note="Air Force FA-50PH, out of Puerto Princesa or Zamboanga"),
    dict(unit="tha_ffg_naresuan", picks=["Variant1", "Variant2"], points=260,
         note="the Royal Thai Navy's detachment: Naresuan and Taksin"),
    dict(unit="tha_aor_chula", picks=["Variant1"], points=70,
         note="SUPPLY: HTMS Chula; small - 15,000 points"),
    dict(unit="tha_S-70B-7_Seahawk", picks=["Squadron1"], points=30,
         note="the Thai frigates' Seahawk; ASW"),
    dict(unit="ran_ffh_anzac", picks=["Variant3", "Variant8"], points=280,
         note="one RAN frigate released from the Arafura in the second week"),
    # The Anzac's own helicopter (816 or 808 Squadron), sold where she is.
    dict(unit="ran_mh-60r", picks=["Squadron1", "Squadron2"], points=35,
         note="RAN MH-60R flight, released with the Anzac from Service at Sea"),
    dict(unit="civ_ms_c8", picks=["Variant1", "Variant2"], points=150,
         note="SUPPLY: MSC prepositioning charter; 300,000 points, slow"),
]

# Air-tasking rows in the fit vocabulary of the aircraft this roster sells.
# The Philippine H-76 declares ASuW and flies CAS; the Thai Seahawk and the
# RAN MH-60R declare ASW and fly ASW (the builder's widen_flights adds the
# MH-60R's ASWLongRange, ASWHunter and SEST_REDBACK fits to the row). None
# is a Bomber, so the Attack row takes only the FA-50.
HELO = "HeloRecon|Ship's Flight|ASuW/ASW|1|CAS/ASW"
ATTACK = "Attack|Close Air Support|Bomber|2|CAS/StrikePrecision"

# The purchase windows, by stage. Supply ships are on sale only in SL01,
# SL04 and SL06 (the three resupply points the story has); everything a
# sunk supply ship carried is lost until then.
SUPPLY = ["phl_lpd_tarlac", "tha_aor_chula", "civ_ms_c8"]
OPENING = ["pn_ffg-150", "pn_ffg-06", "phl_ff_hamilton", "phl_fs_pohang", "phl_h-76",
           "phl_lpd_tarlac", "tha_aor_chula"]
# The Thai detachment and the Air Force's FA-50s are released from the
# second window; the one RAN frigate and her MH-60R from Service at Sea.
# The H-76 lands on every deck the roster sells, and the Thai Seahawk and the
# MH-60R on the Naresuan, the Anzac and BRP Tarlac: SEST Cross-Deck adds the
# fits their own lists leave out (CAMPAIGN_DECK_TYPES in
# integration/cross-deck/build_pack.py).
PARTNERS = ["tha_ffg_naresuan", "tha_S-70B-7_Seahawk", "rok_f-50_ph"]
RAN = ["ran_ffh_anzac", "ran_mh-60r"]
HULLS = ["pn_ffg-150", "pn_ffg-06", "phl_ff_hamilton", "phl_fs_pohang", "phl_h-76"]

# The commander. CommanderNations is the game's own key (nations.ini
# Philippines). The game ships no Philippine name pool, so the pool is
# [Names_Spain], whose names are the Spanish-derived ones common in the
# Philippine service. The default name is invented and the prose never uses
# it: the player is "the task group commander" on every page. The ladder is
# the Philippine Navy's officer ranks with their NATO grades; the game ships
# rank insignia for three navies only, so every image field is empty. The
# navy emblem is the Philippine flag from the SEST gallery's flag set,
# written by build_pack.py (SEST_EMBLEMS). Level 7 is Commodore, the rank a
# task group of this size is given.
COMMANDER = """[CommanderSettings]
CommanderNations=Philippines
CommanderDefaultNation=Philippines
CommanderNameDefaultPhilippines=Ramon Dominguez Navarro
CommanderNamePoolPhilippines=Names_Spain
CommanderStartingRankLevel=7
SameNationUnitDiscount=0.2

NavyNamePhilippines=Philippine Navy
NavyEmblemPhilippines=ui/campaign/navy_emblems/sest_pn_emblem.png

[OfficerRanks]
Philippines=Ensign,ENS,OF-1,1,|Lieutenant Junior Grade,LTJG,OF-1,2,|Lieutenant Senior Grade,LTSG,OF-2,3,|Lieutenant Commander,LCDR,OF-3,4,|Commander,CDR,OF-4,5,|Captain,CAPT,OF-5,6,|Commodore,COMMO,OF-6,7,|Rear Admiral,RADM,OF-7,8,|Vice Admiral,VADM,OF-8,9,|Admiral,ADM,OF-9,10,
"""
