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

DESTRUCTIVE, AND A ONE-SHOT. This regenerates NORTHERN FRONT II from the
ORIGINAL editor save, discarding everything applied since - every civilian
refinement, depth pass, formation name, land fix and hand edit made in the
mission editor. It is kept for provenance, not for routine use.

Unlike every other tool in this folder it is straight-line code with no
argparse, so ANY invocation used to rebuild the mission - including
`--help`, which is how it once silently reverted a mission mid-session.
It now refuses to run without --force.

Usage (repo root):
    python3 "integration/missions/build_northern_front_ii.py" --force
"""
import glob
import re
import sys
from pathlib import Path

if "--force" not in sys.argv:
    sys.exit(
        "build_northern_front_ii.py rebuilds NORTHERN FRONT II from the original\n"
        "editor save and DISCARDS every refinement applied since. It does not run\n"
        "by accident. Pass --force if that is genuinely what you want.")

SRC = Path("mods-source/_vanilla/user/missions/NORTHERN FRONT.ini")
OUT = Path("integration/missions/NORTHERN FRONT II.ini")
Y = "220.4727"  # vanilla vessel-waypoint sea-level constant
MLAT, MLON = 54.27, -26.28  # mission map datum: x = (lon-MLON)*60, z = (lat-MLAT)*60

def ll(lat, lon):
    """Real-world coordinates -> mission x,z (verified against Darwin/Scherger)."""
    return round((lon - MLON) * 60.0, 1), round((lat - MLAT) * 60.0, 1)

t = SRC.read_text(encoding="utf-8-sig", errors="replace")

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
# seized gas rigs — red emplacements on real Arafura/Timor-shelf field positions
for i, (lat, lon) in enumerate([(-9.6, 131.7), (-8.9, 133.2), (-10.15, 130.4)], start=41):
    x, z = ll(lat, lon)
    b.append(land(f"Taskforce2LandUnit{i}", "civ_spar_rig_helo", x, z))

# --- neutral shipping on REAL sea lanes (all waypoints verified water) ---
def route(points):
    """lat/lon chain -> spawn at first point, waypoints through the rest."""
    xz = [ll(la, lo) for la, lo in points]
    wpts = "|".join(f"{x},{Y},{z}" for x, z in xz[1:]) + "/SetTelegraph,3"
    return xz[0], wpts

# Darwin <-> Torres Strait coastal lane (south of the Arafura, around Cape Wessel)
L1 = [(-12.05, 130.75), (-11.30, 132.00), (-10.90, 133.80), (-10.80, 136.00),
      (-10.60, 138.50), (-10.50, 140.50)]
# Banda Sea <-> Torres Strait international lane (south of Tanimbar, across the Arafura)
L2 = [(-5.80, 128.30), (-8.30, 131.30), (-9.00, 133.50), (-9.60, 136.00),
      (-10.00, 138.60), (-10.45, 141.00)]

lanes = [
    (1, "civ_ms_bulk",          L1[0:3], 55, 2),   # eastbound along L1
    (2, "civ_ms_act_1",         L1[1:4], 70, 3),
    (3, "civ_ms_mairangi_bay",  L1[2:5], 80, 2),
    (4, "civ_ms_amra",          L1[3:0:-1], 250, 2),  # westbound
    (5, "civ_ms_andizhan",      L1[4:1:-1], 255, 2),
    (6, "civ_ms_super_p",       L1[5:2:-1], 260, 2),
    (7, "civ_ms_car_carrier_a", L2[0:3], 130, 3),   # southeast-bound along L2
    (8, "civ_ms_freighter_a",   L2[1:4], 110, 2),
    (9, "civ_ms_c8",            L2[2:5], 105, 2),
    (10, "civ_ms_roro_b",       L2[3:0:-1], 300, 3),  # northwest-bound
    (11, "civ_ms_encounter",    L2[4:1:-1], 295, 2),
    (12, "civ_ms_freighter_d",  L2[5:2:-1], 290, 2),
]
for i, ty, pts, hdg, tel in lanes:
    (x, z), wpts = route(pts)
    b.append(nvessel(i, ty, x, z, hdg, tel, wpts))

# Darwin coastal traders
coastal = [
    (13, "ran_ms_austral", [(-12.15, 130.65), (-11.60, 131.60), (-11.00, 133.00)], 50, 2),
    (14, "ran_ms_antares", [(-11.80, 131.40), (-12.10, 130.80), (-12.25, 130.60)], 230, 2),
    (15, "ran_ms_jeparit", [(-12.20, 130.70), (-12.28, 130.58)], 230, 1),
]
for i, ty, pts, hdg, tel in coastal:
    (x, z), wpts = route(pts)
    b.append(nvessel(i, ty, x, z, hdg, tel, wpts))

# Timor-shelf fishing ground (west of Darwin, open water)
fishA = [(16, "civ_fv_fishingboat_a", -10.20, 130.90), (17, "civ_fv_sidetrawler", -10.45, 131.30),
         (18, "civ_fv_crabboat", -10.05, 131.55), (19, "civ_fv_sterntrawler_b", -10.60, 130.60)]
# Indonesian fishing ground (Arafura Sea, south of the Aru Islands)
fishB = [(20, "civ_fv_dhow", -8.60, 133.60), (21, "civ_fv_dhow", -8.85, 134.10),
         (22, "civ_fv_sampan", -8.40, 134.40), (23, "civ_fv_fishingboat_c", -9.05, 133.30),
         (24, "civ_fv_fishingboat_d", -8.25, 133.90)]
for i, ty, lat, lon in fishA + fishB:
    x, z = ll(lat, lon)
    small = ty in ("civ_fv_dhow", "civ_fv_sampan", "civ_fv_crabboat",
                   "civ_fv_fishingboat_a", "civ_fv_fishingboat_c", "civ_fv_fishingboat_d")
    wx, wz = ll(lat + 0.12, lon - 0.10)
    b.append(nvessel(i, ty, x, z, 200, 1, f"{wx},{Y},{wz}/SetTelegraph,1", radar=not small))

# --- neutral biologics: real whale water, random spawn each load ---
bios = [
    (1, "bio_humpback_whale", -9.90, 131.40, 20),   # the RAN screen's water
    (2, "bio_humpback_whale", -10.40, 133.00, 30),
    (3, "bio_humpback_whale", -9.00, 134.80, 30),
    (4, "bio_humpback_whale", -11.20, 135.50, 30),
    (5, "bio_humpback_whale", -8.00, 132.30, 30),
    (6, "bio_blue_whale",     -6.50, 130.00, 40),   # Banda Sea deep water
    (7, "bio_blue_whale",     -5.20, 127.60, 40),
    (8, "bio_fin_whale",      -7.60, 133.00, 40),
    (9, "bio_fin_whale",      -10.90, 138.80, 30),  # Gulf of Carpentaria
]
for i, ty, lat, lon, r in bios:
    x, z = ll(lat, lon)
    b.append(nbio(i, ty, x, z, r))

# --- neutral air traffic: city-pair airways (overland is fine for aircraft) ---
def airway(points, alt):
    xz = [ll(la, lo) for la, lo in points]
    return xz[0], "|".join(f"{x},{alt},{z}" for x, z in xz[1:])

airs = [
    (1, "civ_a330", 35000, [(-12.20, 130.95), (-8.00, 130.50), (-4.00, 130.00)], 355),  # Darwin-Manila
    (2, "civ_a320", 31000, [(-12.30, 131.10), (-10.50, 134.00), (-9.00, 137.00)], 65),  # Darwin-Cairns
    (3, "civ_a380", 41000, [(-7.50, 128.20), (-10.50, 133.00), (-12.80, 137.00)], 130), # Singapore-Sydney
    (4, "civ_a330", 39000, [(-12.50, 139.00), (-10.00, 134.00), (-8.80, 129.20)], 290), # Brisbane-Denpasar
    (5, "civ_a320", 29000, [(-12.10, 130.80), (-10.00, 131.50), (-7.80, 132.20)], 15),  # Darwin-Ambon
    (6, "civ_a330", 37000, [(-4.50, 137.00), (-8.00, 134.00), (-11.50, 131.20)], 220),  # Manila-Perth
    (7, "civ_dc-10", 36000, [(-6.00, 128.80), (-8.50, 133.50), (-10.20, 137.50)], 120), # freighter, Banda-Torres
    (8, "civ_a320", 33000, [(-10.30, 141.00), (-11.20, 136.50), (-12.15, 131.20)], 255),# Cairns-Darwin
]
for i, ty, alt, pts, hdg in airs:
    (x, z), wpts = airway(pts, alt)
    b.append(nair(i, ty, x, alt, z, hdg, wpts))

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
