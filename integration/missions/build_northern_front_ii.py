#!/usr/bin/env python3
"""Build NORTHERN FRONT II from the user's original Northern Front editor save.

One authoritative generator (replaces the earlier incremental edits):
- swaps the two airbase_us stand-ins for the real SEST RAAF bases (custom
  mission air groups preserved), date to 2026-08-24
- blue: RAN inshore screen (Hobart + two Anzacs), E-7A racetrack over Darwin
- red: Pyotr Velikiy in the Varyag group, S-400 site in BADDIES 2,
  Iskander/SCUD TBMs in BADDIES 1, and three SEIZED armed gas rigs as red
  emplacements on the Timor shelf
- neutrals (the fix for "everything is blue"): all merchants, fishing boats
  and airliners are Neutral* units — unknown contacts until identified — with
  vanilla-format vessel waypoints (y=220.4727 + /SetTelegraph) so they MOVE,
  and whales are native NeutralBiologics with RandomSpawnRange so the pods
  land somewhere new every load.

Usage (repo root):  python3 "integration/missions/build_northern_front_ii.py"
"""
import glob
import re
from pathlib import Path

SRC = Path("mods-source/_vanilla/user/missions/NORTHERN FRONT.ini")
OUT = Path("integration/missions/NORTHERN FRONT II.ini")
Y = "220.4727"  # vanilla vessel-waypoint sea-level constant

t = SRC.read_text(encoding="utf-8", errors="replace")

# ---------- identity ----------------------------------------------------------
t = t.replace("Name=_TempMission", "Name=NORTHERN FRONT II")
t, n = re.subn(r"^Date=1985,6,26$", "Date=2026,8,24", t, count=1, flags=re.M)
assert n == 1

# rig name overrides for flavor (appended into [Language_en])
m = re.search(r"^\[Language_en\]\n", t, flags=re.M)
t = t[:m.end()] + (
    "Taskforce2LandUnit41NameOverride=Seized Rig Bayu-Undan\n"
    "Taskforce2LandUnit42NameOverride=Seized Rig Ichthys Explorer\n"
    "Taskforce2LandUnit43NameOverride=Seized Rig Montara\n") + t[m.end():]

# ---------- base swap ---------------------------------------------------------
for section, new in (("Taskforce1LandUnit1", "airbase_raaf_darwin"),
                     ("Taskforce1LandUnit5", "airbase_raaf_scherger")):
    t, n = re.subn(rf"(\[{section}\]\nType=)airbase_us\b", rf"\g<1>{new}", t, count=1)
    assert n == 1, section
assert "airbase_us" not in t

# ---------- counts ------------------------------------------------------------
def bump(text, old, new):
    text, n = re.subn(rf"^{re.escape(old)}$", new, text, count=1, flags=re.M)
    assert n == 1, old
    return text

t = bump(t, "NumberOfTaskforce1Vessels=17", "NumberOfTaskforce1Vessels=20")
t = bump(t, "NumberOfTaskforce2Vessels=15", "NumberOfTaskforce2Vessels=16")
t = bump(t, "NumberOfTaskforce1Aircraft=21", "NumberOfTaskforce1Aircraft=22")
t = bump(t, "NumberOfTaskforce2LandUnits=32", "NumberOfTaskforce2LandUnits=43")
t = bump(t, "Taskforce1_NumberOfFormations=12", "Taskforce1_NumberOfFormations=13")

m = re.search(r"^NumberOfTaskforce2LandUnits=43$", t, flags=re.M)
t = t[:m.end()] + ("\nNumberOfNeutralVessels=24"
                   "\nNumberOfNeutralBiologics=9"
                   "\nNumberOfNeutralAircraft=8") + t[m.end():]

m = re.search(r"^Taskforce1_Formation12=.*$", t, flags=re.M)
t = t[:m.end()] + ("\nTaskforce1_Formation13=Taskforce1Vessel18,Taskforce1Vessel19,"
                   "Taskforce1Vessel20|RAN Inshore Screen|Loose|1.5") + t[m.end():]
t, n = re.subn(r"^(Taskforce2_Formation1=Taskforce2Vessel1,Taskforce2Vessel2,Taskforce2Vessel3,Taskforce2Vessel4)\|",
               r"\1,Taskforce2Vessel16|", t, count=1, flags=re.M)
assert n == 1
t, n = re.subn(r"^(Taskforce2_Formation5=[^|]+)\|",
               r"\1,Taskforce2LandUnit33,Taskforce2LandUnit34,Taskforce2LandUnit35,Taskforce2LandUnit36|",
               t, count=1, flags=re.M)
assert n == 1
t, n = re.subn(r"^(Taskforce2_Formation4=[^|]+)\|",
               r"\1,Taskforce2LandUnit37,Taskforce2LandUnit38,Taskforce2LandUnit39,Taskforce2LandUnit40|",
               t, count=1, flags=re.M)
assert n == 1

# ---------- section builders --------------------------------------------------
def warship(sec, vtype, variant, role, x, z, hdg, extra=""):
    return (f"\n[{sec}]\nType={vtype}\nVariantReference={variant}\nStationRole={role}\n"
            f"RadarsActive=True\nCrewSkill=Veterans\nRelativePositionInNM={x},0,{z}\n"
            f"Telegraph=2\nHeading={hdg}\n{extra}")

def land(sec, vtype, x, z, hdg=0, extra=""):
    return (f"\n[{sec}]\nType={vtype}\nVariantReference=Default\nCrewSkill=Trained\nMorale=3\n"
            f"RelativePositionInNM={x},low,{z}\nHeading={hdg}\n{extra}")

def nvessel(i, vtype, x, z, hdg, tel, wpts, radar=True):
    return (f"\n[NeutralVessel{i}]\nType={vtype}\nVariantReference=Default\n"
            f"RadarsActive={'True' if radar else 'False'}\nCrewSkill=Trained\n"
            f"RelativePositionInNM={x},0,{z}\nTelegraph={tel}\nHeading={hdg}\n"
            f"Waypoints={wpts}\n")

def nbio(i, btype, x, z, rng):
    return (f"\n[NeutralBiologic{i}]\nType={btype}\nVariantReference=Default\n"
            f"UnlimitedFuel=False\nWeaponStatus=Free\nCrewSkill=Trained\n"
            f"RelativePositionInNM={x},shallow,{z}\nRandomSpawnCenter={x},shallow,{z}\n"
            f"RandomSpawnRange={rng}\nTelegraph=3\n")

def nair(i, vtype, x, alt, z, hdg, wpts):
    return (f"\n[NeutralAircraft{i}]\nType={vtype}\nSquadronReference=Default\n"
            f"RadarsActive=True\nRelativePositionInNM={x},{alt},{z}\n"
            f"Telegraph=3\nHeading={hdg}\nWaypoints={wpts}\n")

b = []
# --- blue military additions ---
b.append(warship("Taskforce1Vessel18", "ran_ddg_hobart", "Variant1", "AAW", 9455.0, -3862.0, 45))
b.append(warship("Taskforce1Vessel19", "ran_ffh_anzac", "Variant2", "ASW", 9448.0, -3868.0, 45,
                 "TowedArrayDeployed=True\n"))
b.append(warship("Taskforce1Vessel20", "ran_ffh_anzac", "Variant3", "ASW", 9462.0, -3856.0, 45,
                 "TowedArrayDeployed=True\n"))
b.append(f"\n[Taskforce1Aircraft22]\nType=E7A_Wedgetail\nSquadronReference=Default\n"
         f"UnlimitedFuel=False\nCrewSkill=Trained\nMorale=3\n"
         f"RelativePositionInNM=9440,30000,-3990\nTelegraph=3\nHeading=90\n"
         f"Waypoints=9520,30000,-3950|9440,30000,-3990|9520,30000,-3950\n")

# --- red additions ---
b.append(warship("Taskforce2Vessel16", "wp_rkr_kirov_improved", "Variant1", "AAW",
                 9314.0, -3394.0, 120))
b.append(land("Taskforce2LandUnit33", "wp_sa-21_flaplid", 9472.8, -3684.2))
b.append(land("Taskforce2LandUnit34", "wp_sa-21_40n6_tel", 9471.6, -3685.9, 300))
b.append(land("Taskforce2LandUnit35", "wp_sa-21_40n6_tel", 9473.9, -3686.4, 200))
b.append(land("Taskforce2LandUnit36", "wp_sa-21_48n6e3_tel", 9472.3, -3687.1, 250))
b.append(land("Taskforce2LandUnit37", "wp_ss-26_tel", 9628.1, -3667.0, 230))
b.append(land("Taskforce2LandUnit38", "wp_ss-26_tel", 9630.2, -3667.6, 230))
b.append(land("Taskforce2LandUnit39", "wp_scud_9k72", 9628.6, -3669.4, 230))
b.append(land("Taskforce2LandUnit40", "wp_scud_9k72", 9630.0, -3669.9, 230))
# seized gas rigs — red emplacements on the shelf, spread ~100nm apart
b.append(land("Taskforce2LandUnit41", "civ_spar_rig_helo", 9528.0, -3838.0))
b.append(land("Taskforce2LandUnit42", "civ_spar_rig_helo", 9612.0, -3762.0))
b.append(land("Taskforce2LandUnit43", "civ_spar_rig_helo", 9498.0, -3742.0))

# --- neutral shipping: two long lanes + coastal + two fishing grounds ---
lane1 = [  # Darwin <-> NE shelf, ~380nm, alternating directions
    (1, "civ_ms_bulk",          9455.0, -3975.0, 40, 2, f"9610,{Y},-3830|9760,{Y},-3640/SetTelegraph,3"),
    (2, "civ_ms_act_1",         9530.0, -3905.0, 40, 3, f"9680,{Y},-3720|9790,{Y},-3610/SetTelegraph,3"),
    (3, "civ_ms_mairangi_bay",  9615.0, -3825.0, 40, 2, f"9740,{Y},-3665|9800,{Y},-3595/SetTelegraph,3"),
    (4, "civ_ms_amra",          9690.0, -3710.0, 220, 2, f"9540,{Y},-3895|9450,{Y},-3985/SetTelegraph,1"),
    (5, "civ_ms_andizhan",      9755.0, -3645.0, 220, 2, f"9600,{Y},-3845|9455,{Y},-3980/SetTelegraph,1"),
    (6, "civ_ms_super_p",       9575.0, -3860.0, 220, 2, f"9470,{Y},-3960|9445,{Y},-3992/SetTelegraph,1"),
]
lane2 = [  # east-west between the fleets, ~500nm
    (7, "civ_ms_car_carrier_a", 9830.0, -3440.0, 250, 3, f"9560,{Y},-3540|9340,{Y},-3610/SetTelegraph,3"),
    (8, "civ_ms_freighter_a",   9720.0, -3480.0, 250, 2, f"9500,{Y},-3560|9330,{Y},-3615/SetTelegraph,3"),
    (9, "civ_ms_c8",            9600.0, -3525.0, 250, 2, f"9420,{Y},-3585|9330,{Y},-3618/SetTelegraph,3"),
    (10, "civ_ms_roro_b",       9370.0, -3600.0, 70, 3, f"9620,{Y},-3515|9840,{Y},-3438/SetTelegraph,3"),
    (11, "civ_ms_encounter",    9480.0, -3565.0, 70, 2, f"9700,{Y},-3492|9845,{Y},-3440/SetTelegraph,3"),
    (12, "civ_ms_freighter_d",  9660.0, -3505.0, 70, 2, f"9780,{Y},-3465|9850,{Y},-3435/SetTelegraph,3"),
]
coastal = [
    (13, "ran_ms_austral",      9444.0, -3968.0, 40, 2, f"9520,{Y},-3945|9600,{Y},-3850/SetTelegraph,3"),
    (14, "ran_ms_antares",      9436.0, -3982.0, 40, 2, f"9505,{Y},-3958|9585,{Y},-3862/SetTelegraph,3"),
    (15, "ran_ms_jeparit",      9452.0, -3958.0, 220, 1, f"9440,{Y},-3990|9438,{Y},-3998/SetTelegraph,1"),
]
fishA = [  # Timor shelf, spread ~40nm
    (16, "civ_fv_fishingboat_a", 9540.0, -3852.0, 300, 1, f"9528,{Y},-3846|9545,{Y},-3860/SetTelegraph,1"),
    (17, "civ_fv_sidetrawler",   9565.0, -3838.0, 120, 2, f"9578,{Y},-3848|9560,{Y},-3830/SetTelegraph,1"),
    (18, "civ_fv_crabboat",      9552.0, -3872.0, 210, 1, f"9542,{Y},-3880|9556,{Y},-3866/SetTelegraph,1"),
    (19, "civ_fv_sterntrawler_b",9585.0, -3812.0, 30, 2, f"9595,{Y},-3800|9575,{Y},-3820/SetTelegraph,1"),
]
fishB = [  # northern contested water, spread ~50nm
    (20, "civ_fv_dhow",          9668.0, -3520.0, 300, 1, f"9660,{Y},-3512|9672,{Y},-3528/SetTelegraph,1"),
    (21, "civ_fv_dhow",          9705.0, -3495.0, 120, 1, f"9714,{Y},-3504|9698,{Y},-3488/SetTelegraph,1"),
    (22, "civ_fv_sampan",        9685.0, -3470.0, 200, 1, f"9678,{Y},-3478|9690,{Y},-3464/SetTelegraph,1"),
    (23, "civ_fv_fishingboat_c", 9730.0, -3515.0, 30, 1, f"9738,{Y},-3505|9722,{Y},-3522/SetTelegraph,1"),
    (24, "civ_fv_fishingboat_d", 9648.0, -3488.0, 160, 1, f"9642,{Y},-3496|9654,{Y},-3480/SetTelegraph,1"),
]
for i, ty, x, z, h, tel, w in lane1 + lane2 + coastal + fishA + fishB:
    small = ty.startswith("civ_fv") and ty not in ("civ_fv_sterntrawler_b", "civ_fv_sidetrawler")
    b.append(nvessel(i, ty, x, z, h, tel, w, radar=not small))

# --- neutral biologics: native whales, random spawn each load ---
bios = [
    (1, "bio_humpback_whale", 9460.0, -3870.0, 25),   # inside the RAN screen's water
    (2, "bio_humpback_whale", 9560.0, -3800.0, 30),
    (3, "bio_humpback_whale", 9650.0, -3690.0, 30),
    (4, "bio_humpback_whale", 9380.0, -3800.0, 30),
    (5, "bio_humpback_whale", 9700.0, -3450.0, 30),
    (6, "bio_blue_whale",     9750.0, -3550.0, 40),
    (7, "bio_blue_whale",     9350.0, -3650.0, 40),
    (8, "bio_fin_whale",      9520.0, -3700.0, 40),
    (9, "bio_fin_whale",      9600.0, -3900.0, 25),
]
for i, ty, x, z, r in bios:
    b.append(nbio(i, ty, x, z, r))

# --- neutral air traffic: eight liners on crossing airways ---
airs = [
    (1, "civ_a330", 9750.0, 35000, -3550.0, 225, f"9350,35000,-3980|9250,35000,-4090"),
    (2, "civ_a320", 9380.0, 33000, -3700.0, 60, f"9800,33000,-3450|9900,33000,-3360"),
    (3, "civ_a380", 9300.0, 43000, -4050.0, 40, f"9700,43000,-3500|9850,43000,-3350"),
    (4, "civ_a330", 9600.0, 37000, -3400.0, 190, f"9500,37000,-3800|9450,37000,-3990"),
    (5, "civ_a320", 9550.0, 29000, -3990.0, 20, f"9620,29000,-3760|9680,29000,-3560"),
    (6, "civ_a330", 9850.0, 39000, -3700.0, 265, f"9500,39000,-3750|9330,39000,-3780"),
    (7, "civ_dc-10", 9330.0, 36000, -3500.0, 110, f"9650,36000,-3620|9880,36000,-3700"),
    (8, "civ_a320", 9480.0, 31000, -3880.0, 350, f"9460,31000,-3600|9440,31000,-3420"),
]
for i, ty, x, alt, z, h, w in airs:
    b.append(nair(i, ty, x, alt, z, h, w))

t = t.rstrip("\n") + "\n" + "".join(b)

# ---------- validate every unit type ------------------------------------------
refs = set(re.findall(r"^Type=([^\s/]+)$", "".join(b), re.M))
missing = []
for r in refs:
    hits = (glob.glob(f"mods-source/*/**/{r}.ini", recursive=True)
            + glob.glob(f"mods-source/_vanilla/original/**/{r}.ini", recursive=True)
            + glob.glob(f"integration/*/SEST_*/**/{r}.ini", recursive=True))
    if not hits:
        missing.append(r)
assert not missing, f"unresolved unit types: {missing}"

OUT.write_text(t, encoding="utf-8")
print(f"built {OUT.name}: {len(t.splitlines())} lines — "
      f"24 neutral vessels, 9 random-spawn biologics, 8 neutral aircraft, "
      f"3 seized red rigs, all {len(refs)} unit types validated")
