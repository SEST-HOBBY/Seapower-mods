#!/usr/bin/env python3
"""Build the SEST Growler NGJ + MALICE compatibility patch.

The three Growler identifiers in the installed collection come from three
different Workshop mods.  This builder deliberately rebases each identifier
on the file that currently wins the user's canonical load order, then adds
SEST loadouts without changing the original choices.

Targets:
  * usn_ea-18g       - U.S. Navy 2027 Capabilities (upgraded from ALQ-99)
  * usn_ea-18g_2020s - F/A-18E/F (already carries the NGJ meshes)
  * usn_ea-18g_2020  - US Naval Aviation (already carries the NGJ meshes)
  * usn_fa-18f_blk3  - U.S. Navy 2027 Capabilities Block III Super Hornet
  * usn_fa-18f       - U.S. Navy 2027 two-seat Super Hornet (AN/APG-79)
  * usn_fa-18e       - U.S. Navy 2027 single-seat Super Hornet (AN/APG-79(V))

Usage (repo root):  python3 integration/growler-ngj-malice/build_patch.py
"""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NAVY_2027 = ROOT / "mods-source" / "3606774881"
SUPER_HORNET = ROOT / "mods-source" / "3426791311"
US_NAVAL_AVIATION = ROOT / "mods-source" / "3737267013"
MURDER_HORNET = ROOT / "mods-source" / "3430135740"
OUT = Path(__file__).resolve().parent / "SEST_Growler_NGJ_MALICE"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402


# TANK MESH HISTORY - the coupling theory below was superseded, keep both.
#
# usn_tank_1200_f-18 is Murder Hornet's, and its mesh really is the vanilla
# F-15C tank (ResourcesMesh=usaf_f-15c_tank_610 out of aircraft/usaf_f-15c/)
# with Fuel raised from 1800 to 4500. usn_tank_610_f-18 was the genuine Hornet
# article - f-18_fuletank out of the F/A-18E/F mod.
#
# Round 1 (earlier session): swapping fits TO f-18_fuletank made the tanks
# hang visibly low and detached, and was reverted under the theory that each
# airframe's stations were "tuned around" its own tank mesh - no id swapping,
# detect_wing_tank() asks the airframe what it flies.
#
# Round 2 (in-game reports on the 2020/2020s Growlers and the E tanker):
# f-18_fuletank hung low ON ITS OWN airframes too, and seat offsets of
# 0.0015 then 0.003 produced no visible change. Stations 27/28 carry
# IDENTICAL coordinates on all four airframes, so the coupling theory cannot
# hold - the truth is simpler: f-18_fuletank is a submesh pulled out of
# fa-18e.obj, a whole-aircraft root, so its origin rides low at ANY station,
# while the F-15C tank mesh sits flush at these coordinates everywhere
# (proven by usn_tank_1200_f-18 and usaf_tank_610_f-15 in game).
#
# Resolution: ids still never swap (detect_wing_tank stays), but the
# usn_tank_610_f-18 AMMUNITION file is overridden to render the F-15C tank
# mesh - see build_tank_610_override(). Fuel stays 1800 everywhere: the
# usn_tank_1200_f-18 override below keeps its 4500 -> 1800 correction.
DEFAULT_WING_TANK = "usn_tank_1200_f-18"

# Same file as Murder Hornet's, one number changed.
TANK_OVERRIDE = """\
[General]
# usn_tank_1200_f-18 - SEST override of Murder Hornet's tank.
# Geometry is untouched: the mesh below is what stations 27/28 and 29 are
# positioned around, and substituting the real f-18_fuletank makes the tanks
# hang low and detached. Only Fuel changes, 4500 -> 1800, which is what both
# the genuine Hornet tank (usn_tank_610_f-18) and the vanilla F-15 610 gal
# tank carry. 4500 was giving the fits that used it 2.5x the external fuel of
# the ones that did not, which is why NGJ MALICE showed ~1433 nm against the
# SEAD fits' ~860.
Type=Fueltank
Fuel=1800

[---------- Mesh definitions----------]
[Models]
AssetBundleMeshes=/AssetBundles/StandaloneWindows/aircraft
AssetBundleMaterials=/AssetBundles/StandaloneWindows/aircraft
AssetBundleMesh=usn_rim-7
AssetBundleDamagedMesh=
AssetBundleMaterial=usn_rim-7_mat
AssetBundleMeshHullCollider=usn_rim-7_coll
ResourcesFolder=aircraft/usaf_f-15c/
ResourcesRoot=usaf_f-15c
ResourcesMesh=usaf_f-15c_tank_610
ResourcesMaterialFolder=aircraft/usaf_f-15c/
ResourcesMaterial=usaf_f-15c_tank_mat
"""

# Bar for flagging stores that sit close to a fuel tank: same separation or
# closer than the AGM-88G case, AND at least as heavy. Both halves matter -
# distance alone flags 20 per airframe, because Murder Hornet routinely parks
# SDBs (93 kg) beside the tanks and those are fine.
CLASH_SEPARATION = 0.0181
CLASH_MASS = 468              # usn_agm-88g

GROWLER_KEYS = ["SEST_MaliceNGJ"]
LONG_RANGE_KEY = "SEST_NGJLongRange"
BLOCK_III_KEYS = ["SEST_MaliceBlockIII", "SEST_Intercept260",
                  "SEST_Intercept260ER", "SEST_Escort260"]

GROWLER_LOADOUTS = """\
[--------------------------- SEST NGJ + MALICE ---------------------------]
# Added by SEST_Growler_NGJ_MALICE.  The AN/ALQ-249 and NGL-LB pod meshes
# remain fitted; MALICE uses the AGM-88G airframe from US Naval Aviation.

[WeaponSystem1SEST_MaliceNGJ]
ReadyUpTime=25               // minutes to refuel and rearm before takeoff
CoolDownTime=60              // minutes of maintenance after landing
# fule_tank_point is the WING tank attachment. Every upstream fit that puts
# tanks on stations 27/28 (the "EF" external-fuel ones) leaves it VISIBLE and
# only centreline-tank fits hide it - hiding it here left the tanks floating.
# The tank id is filled in from whatever this airframe already flies -
# see detect_wing_tank() for why substituting a different mesh breaks it.
Station3=sest_aim-424
Station4=sest_aim-424
Station11=dts_aim-260
Station12=dts_aim-260
Station27=__WING_TANK__
Station28=__WING_TANK__

"""

# The centreline is the EW station, not a wet one - in game the third tank
# sat inside the Growler's centre jamming equipment (user screenshot). And
# "either side of the NGJ" cannot be four tanks: the model carries exactly ONE
# pair of wing tank pylons (fule_tank_point, stations 27/28), the airframes
# end at NumberOfStations=28, and 13/14 carry sead/aam racks a tank would
# float beside. So maximum persistence is TWO wing tanks - which also means
# every Growler gets this fit now, not just the ones with a Station29.
LONG_RANGE_LOADOUT = """\
[--------------------------- SEST NGJ Long Range ---------------------------]
# Maximum-persistence jamming fit: no anti-radiation missiles, both wing
# tanks, a pair of AMRAAM for self-defence, centreline left to the EW fit.
# fule_tank_point must stay VISIBLE for the wing tanks - no hide line here.

[WeaponSystem1SEST_NGJLongRange]
ReadyUpTime=25               // minutes to refuel and rearm before takeoff
CoolDownTime=60              // minutes of maintenance after landing
Station11=dts_aim-260
Station12=dts_aim-260
Station27=__WING_TANK__
Station28=__WING_TANK__
"""

BLOCK_III_LOADOUT = """\
[--------------------------- SEST Block III MALICE ---------------------------]
# Counter-air / anti-emitter fit based on the proven Murder Hornet
# Interceptor station geometry.  MALICE replaces the four AIM-174Bs.

[WeaponSystem1SEST_MaliceBlockIII]
ReadyUpTime=30               // minutes to refuel and rearm before takeoff
CoolDownTime=60              // minutes of maintenance after landing
SubModelsToHide=aam_point2,aam_pointCRIR,aam_pointCRIL,agm_inner_point,agm_point,gbu_point,Targeting_Pod,fule_tank_point,BRU_55_Left,BRU_55_Right,BRU_55_Left_Inner,BRU_55_Right_Inner,gbu_outer,gbu_inner
Station1=usn_aim-9x
Station2=usn_aim-9x
Station3=usn_aim-120d3
Station4=usn_aim-120d3
Station11=dts_aim-260
Station12=dts_aim-260
Station29=__WING_TANK__
Station30=sest_aim-424
Station31=sest_aim-424
Station32=sest_aim-424
Station33=sest_aim-424

"""

NGJ_SENSOR = """\
[AN/ALQ-249]
# Next Generation Jammer Mid-Band.  Stats match the established F/A-18E/F
# implementation so this patch changes availability rather than balance.
Kind=ECM
Frequencies=All
Type=Offensive
PeakPower=75.0
MaxRange=400.0
Gain=7.5
JamConeViewArcs=45.0
JamChance=0.3
"""

LOADOUT_NAMES = {
    "en": {
        "SEST_MaliceNGJ": "SEST NGJ MALICE (2x AIM-424)",
        "SEST_NGJLongRange": "SEST NGJ Long Range (2 tanks)",
        "SEST_MaliceBlockIII": "SEST Block III MALICE (4x AIM-424)",
        "SEST_Intercept260": "SEST Intercept (8x AIM-260)",
        "SEST_Intercept260ER": "SEST Intercept260 LongRange (3 tanks)",
        "SEST_Escort260": "SEST Escort260 (4x AIM-260, 3 tanks)",
        "SEST_SEAD260": "SEST SEAD260 (AGM-88G + AIM-260)",
    },
    "cn": {
        "SEST_MaliceNGJ": "SEST NGJ MALICE (2x AIM-424)",
        "SEST_NGJLongRange": "SEST NGJ Long Range (2 tanks)",
        "SEST_MaliceBlockIII": "SEST Block III MALICE (4x AIM-424)",
        "SEST_Intercept260": "SEST Intercept (8x AIM-260)",
        "SEST_Intercept260ER": "SEST Intercept260 LongRange (3 tanks)",
        "SEST_Escort260": "SEST Escort260 (4x AIM-260, 3 tanks)",
        "SEST_SEAD260": "SEST SEAD260 (AGM-88G + AIM-260)",
    },
}

INFO_INI = """[Language_en]
Name=SEST Growler NGJ + MALICE
Description=Adds functional AN/ALQ-249 Next Generation Jammer equipment and an AIM-424 MALICE fit to the modern EA-18G Growlers, plus a four-MALICE counter-air fit for every AN/APG-79 Super Hornet (F/A-18F Block III, F/A-18F and F/A-18E), whose anti-ship fits now carry LRASM in place of the AGM-84N Harpoon. Requires U.S. Navy 2027 Capabilities, F/A-18E/F, and US Naval Aviation. US Naval Aviation supplies the AGM-88G model used by MALICE. Place this patch ABOVE all three required mods.

[Compatibility]
ApproximateVersion=0.8.2
"""


def normalize_generated_text(text: str) -> str:
    """Remove trailing horizontal whitespace and keep one final newline."""
    body = "\n".join(line.rstrip(" \t") for line in text.splitlines())
    return body.rstrip("\n") + "\n"

def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        sys.exit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def extend_loadouts(text: str, keys: list[str], source_name: str) -> str:
    match = re.search(r"^(AvailableLoadouts=)([^\r\n]+)$", text, re.M)
    if not match:
        sys.exit(f"{source_name}: AvailableLoadouts line not found")
    existing = [key.strip() for key in match.group(2).split(",")]
    clashes = [key for key in keys if key in existing]
    if clashes:
        sys.exit(f"{source_name}: loadout keys already exist: {clashes}")
    replacement = match.group(1) + match.group(2).rstrip() + "," + ",".join(keys)
    return text[: match.start()] + replacement + text[match.end() :]


def inject_loadouts(text: str, sections: str, source_name: str) -> str:
    marker = "[---------- WeaponMagazines ----------]"
    if text.count(marker) != 1:
        sys.exit(f"{source_name}: expected one WeaponMagazines marker")
    return text.replace(marker, sections + marker, 1)


def upgrade_legacy_growler(text: str) -> str:
    """Replace the two ALQ-99 systems/meshes with the modern NGJ set."""
    text = replace_once(
        text,
        "NumberOfSensorSystems=7",
        "NumberOfSensorSystems=6",
        "legacy Growler sensor count",
    )

    sensor = """[SensorSystem5] #AN/ALQ-249 Next Generation Jammer
Type=ECM
SystemName=AN/ALQ-249
Mount=ALQ-249
ModuleType=Sensor

"""
    text, count = re.subn(
        r"(?ms)^\[SensorSystem5\][^\n]*\n.*?(?=^\[SensorSystem7\])",
        sensor,
        text,
        count=1,
    )
    if count != 1:
        sys.exit("legacy Growler: could not replace ALQ-99 sensor blocks")
    text = replace_once(text, "[SensorSystem7] #GPS", "[SensorSystem6] #GPS", "legacy Growler GPS index")

    text = replace_once(
        text,
        "ALQ-99=ALQ-99\nALQ-99_C=ALQ-99_C",
        "NGL-LB=NGL-LB\nALQ-249=ALQ-249",
        "legacy Growler NGJ submodels",
    )
    text = text.replace("SubModelsToHide=fule_tank_point,ALQ-99", "SubModelsToHide=fule_tank_point")

    mesh_pattern = re.compile(
        r"(?ms)^\[ALQ-99\]\n.*?^\[ALQ-99_C\]\n.*?(?=^#{10,}\n# Decals)"
    )
    ngj_meshes = """[NGL-LB]
Mesh=ngllb
ResourcesFolder=assets/models/vechicle/aircraft/ea-18g/
Material=ngllb_mat.ini

[ALQ-249]
Mesh=alq249_open
ResourcesFolder=assets/models/vechicle/aircraft/ea-18g/
Material=alq249_mat.ini

"""
    text, count = mesh_pattern.subn(ngj_meshes, text, count=1)
    if count != 1:
        sys.exit("legacy Growler: could not replace ALQ-99 mesh definitions")

    checks = {
        "AN/ALQ-249 sensor": "SystemName=AN/ALQ-249",
        "NGJ low-band model": "NGL-LB=NGL-LB",
        "NGJ mid-band model": "ALQ-249=ALQ-249",
    }
    for label, token in checks.items():
        if text.count(token) != 1:
            sys.exit(f"legacy Growler: invalid {label}")
    if "SystemName=AN/ALQ-99" in text:
        sys.exit("legacy Growler: an active ALQ-99 sensor remains")
    return text


def verify_station_geometry(text: str, sections: str, source_name: str) -> None:
    hardpoint = re.search(r"(?ms)^\[WeaponSystem1\].*?(?=^\[WeaponSystem\d+\])", text)
    if not hardpoint:
        sys.exit(f"{source_name}: WeaponSystem1 hardpoint block not found")
    defined = {int(value) for value in re.findall(r"^Station(\d+)=", hardpoint.group(0), re.M)}
    used = {int(value) for value in re.findall(r"^Station(\d+)=", sections, re.M)}
    missing = sorted(used - defined)
    if missing:
        sys.exit(f"{source_name}: loadout uses undefined stations {missing}")


# Stations 27/28 are the WING tank pylons; their attachment mesh is
# fule_tank_point. Station 29 is the centreline, which does not use it.
WING_TANK_STATIONS = {27, 28}
WING_TANK_POINT = "fule_tank_point"


def verify_tank_points(text: str, source_name: str) -> None:
    """A loadout may not hide the wing tank point while using a wing tank.

    Doing so renders the tanks detached in mid-air. Only SEST sections are
    checked - upstream's own loadouts are not ours to police.
    """
    for m in re.finditer(r"^\[WeaponSystem1(SEST_[A-Za-z0-9_]+)\]\n(.*?)(?=^\[)",
                         text, re.M | re.S):
        name, body = m.group(1), m.group(2)
        hidden = re.search(r"^SubModelsToHide=(.*)$", body, re.M)
        if not (hidden and WING_TANK_POINT in hidden.group(1)):
            continue
        used = {int(s) for s, ammo in re.findall(r"^Station(\d+)=(\S+)", body, re.M)
                if "tank" in ammo}
        clash = sorted(used & WING_TANK_STATIONS)
        if clash:
            sys.exit(f"{source_name}: {name} hides {WING_TANK_POINT} but mounts a "
                     f"tank on wing station(s) {clash} - the tanks would float")


def fix_floating_tanks(text: str, source_name: str) -> str:
    """Stop wing tanks rendering detached in upstream's own loadouts.

    Several upstream fits hide fule_tank_point - the WING tank attachment -
    while mounting tanks on stations 27/28, so the tanks float unattached.
    Upstream's own external-fuel ("EF") loadouts show the correct pattern:
    tanks on 27/28 with the point left visible. This drops fule_tank_point
    from the hide list of any loadout that mounts a wing tank, and touches
    nothing else.
    """
    fixed = []

    def repair(match):
        header, body = match.group(1), match.group(2)
        hidden = re.search(r"^SubModelsToHide=(.*)$", body, re.M)
        if not (hidden and WING_TANK_POINT in hidden.group(1)):
            return match.group(0)
        used = {int(st) for st, ammo in re.findall(r"^Station(\d+)=(\S+)", body, re.M)
                if "tank" in ammo}
        if not (used & WING_TANK_STATIONS):
            return match.group(0)
        kept = [p for p in hidden.group(1).split(",")
                if p.strip() and p.strip() != WING_TANK_POINT]
        new_line = ("SubModelsToHide=" + ",".join(kept)) if kept else ""
        new_body = re.sub(r"^SubModelsToHide=.*$", lambda _: new_line, body,
                          count=1, flags=re.M)
        if not kept:
            new_body = new_body.replace("\n\n", "\n", 1)
        fixed.append(re.match(r"\[WeaponSystem1([A-Za-z0-9_\-]+)\]", header).group(1))
        return header + new_body

    text = re.sub(r"(^\[WeaponSystem1[A-Za-z0-9_\-]+\]\n)(.*?)(?=^\[)",
                  repair, text, flags=re.M | re.S)
    if fixed:
        print(f"    {source_name}: wing tanks re-attached in {len(fixed)} loadout(s): "
              f"{', '.join(fixed)}")
    return text


# ---------------------------------------------------------------------------
# Growler pylon convention
# ---------------------------------------------------------------------------
# One rule for where things hang, matching the real EA-18G and the model:
#
#   fuselage       (|x| < 0.025)  AIM-120D3
#   INBOARD wing   (~0.033)       fuel
#   MID wing       (~0.048-0.055) NGJ pods - KEEP CLEAR OF STORES
#   OUTBOARD wing  (0.0629)       AGM-88G / AIM-424 / AIM-260 / fuel
#   centreline     (0)            fuel
#
# The mid-wing rule is the important one. The ALQ-249 and NGL-LB pod meshes are
# baked into the airframe at that pylon and cannot be moved from the ini - they
# are submodels with no Position key. So anything hung there intersects them,
# which is what the AGM-88G pair on stations 13/14 was doing. It was never the
# fuel tanks: those are on the inboard pylon, a whole pylon further in.
#
# CONSEQUENCE: the outboard pylon is a SINGLE PAIR, stations 3 and 4. Under this
# convention a Growler carries TWO heavy weapons, not four or six. The four- and
# six-AGM fits cannot exist as such, and are re-cut below to differ by fuel
# instead of by weapon count.
PYLON_BANDS = [
    (0.025, "fuselage"),
    (0.042, "inboard"),
    (0.058, "mid"),          # NGJ pods
    (0.075, "outboard"),
    (9.999, "wingtip"),
]
MID_WING = "mid"

# Station numbers by role on the Growler airframes.
FUSELAGE_AAM = (11, 12)
INBOARD_TANK = (27, 28)
OUTBOARD_WEAPON = (3, 4)
CENTRELINE_TANK = 29

# The Growler fits, re-cut to the convention. Each is (loadout, description of
# what changed) plus the station lines that replace whatever was there.
GROWLER_FIT_PLAN = {
    "MurderHornetSEADHeavy": (
        "clean SEAD: 2x AGM-88G outboard, no fuel",
        [(3, "usn_agm-88g"), (4, "usn_agm-88g"),
         (11, "dts_aim-260"), (12, "dts_aim-260")]),
    "MurderHornetSEADHeavyTanks": (
        "SEAD with fuel: 2x AGM-88G outboard, 2 wing tanks inboard",
        [(3, "usn_agm-88g"), (4, "usn_agm-88g"),
         (11, "dts_aim-260"), (12, "dts_aim-260"),
         (27, "__WING_TANK__"), (28, "__WING_TANK__")]),
    "MurderHornetLightsOut": (
        "max-endurance SEAD: 2x AGM-88G outboard, 2 wing tanks - the centre "
        "is the EW station, not a wet one (was the last 3-tank Growler fit)",
        [(3, "usn_agm-88g"), (4, "usn_agm-88g"),
         (11, "dts_aim-260"), (12, "dts_aim-260"),
         (27, "__WING_TANK__"), (28, "__WING_TANK__")]),
}


def pylon_of(x: float) -> str:
    for limit, name in PYLON_BANDS:
        if abs(x) < limit:
            return name
    return "wingtip"


def station_positions(text: str) -> dict:
    return {int(a): float(b) for a, b, _c, _d in
            re.findall(r"^Station(\d+)=([-\d.]+),([-\d.]+),([-\d.]+)", text, re.M)}


def apply_pylon_convention(text: str, source_name: str, wing_tank: str) -> str:
    """Re-cut the Growler fits so every store hangs on the right pylon."""
    pos = station_positions(text)
    for loadout, (why, plan) in GROWLER_FIT_PLAN.items():
        m = re.search(rf"^(\[WeaponSystem1{re.escape(loadout)}\]\n)(.*?)(?=^\[)",
                      text, re.M | re.S)
        if not m:
            continue                      # not on this airframe
        body = m.group(2)
        wanted = [(s, a) for s, a in plan if s in pos]
        dropped = [s for s in plan if s[0] not in pos]
        if dropped:
            print(f"    {source_name}: {loadout} - skipping station(s) "
                  f"{[s for s, _ in dropped]}, not on this airframe")
        before = re.findall(r"^Station\d+=\S+", body, re.M)
        kept = [l for l in body.splitlines() if not re.match(r"^Station\d+=", l)]
        lines = [f"Station{s}={a.replace('__WING_TANK__', wing_tank)}" for s, a in wanted]
        # keep the non-station keys, then the new station block
        while kept and not kept[-1].strip():
            kept.pop()
        new_body = "\n".join(kept + lines) + "\n\n"
        if len(before) != len(lines):
            print(f"    {source_name}: {loadout} - {len(before)} -> {len(lines)} stores: {why}")
        text = text[:m.start(2)] + new_body + text[m.end(2):]
    return text


def verify_pylon_convention(text: str, source_name: str) -> None:
    """Nothing may hang on the mid-wing pylon - the NGJ pods are there."""
    pos = station_positions(text)
    problems = []
    for m in re.finditer(r"^\[WeaponSystem1([A-Za-z0-9_\-]+)\]\n(.*?)(?=^\[)",
                         text, re.M | re.S):
        for s, ammo in re.findall(r"^Station(\d+)=([A-Za-z]\S*)", m.group(2), re.M):
            s = int(s)
            if s in pos and pylon_of(pos[s]) == MID_WING:
                problems.append(f"{m.group(1)} S{s}={ammo.split('|')[0]} "
                                f"(|x|={abs(pos[s]):.5f}) is on the NGJ pylon")
    if problems:
        sys.exit(f"{source_name}: stores on the mid-wing pylon:\n  "
                 + "\n  ".join(sorted(set(problems))))


def detect_wing_tank(text: str, source_name: str) -> str:
    """The tank THIS airframe's own loadouts hang on the wing stations.

    The tank mesh and the station positions are one unit - substituting a mesh
    from a different aircraft's model leaves the tanks visibly low and
    detached, because the mesh origin is wherever the tank sits on that other
    model. So the SEST fits copy whatever the airframe already flies.
    """
    used = re.findall(r"^Station2[78]=(\S*tank\S*)\s*$", text, re.M)
    if not used:
        print(f"    {source_name}: no existing wing tank to copy - "
              f"defaulting to {DEFAULT_WING_TANK}")
        return DEFAULT_WING_TANK
    tank = max(set(used), key=used.count).split("|")[0]
    print(f"    {source_name}: wing tank is {tank} (copied from this airframe's own fits)")
    return tank


def ammunition_mass(ammo_id: str, _cache: dict = {}) -> int:
    """Mass of a store in kg, or 0 if it cannot be resolved."""
    if ammo_id not in _cache:
        _cache[ammo_id] = 0
        for path in (ROOT / "mods-source").rglob(f"{ammo_id}.ini"):
            if path.parent.name != "ammunition":
                continue
            m = re.search(r"^Mass=(\d+)", path.read_text(encoding="utf-8", errors="replace"), re.M)
            if m:
                _cache[ammo_id] = int(m.group(1))
                break
    return _cache[ammo_id]


def report_tank_clearance(text: str, source_name: str) -> None:
    """List other stores sitting as close to a tank as the confirmed clash.

    Informational only, never a build failure. Murder Hornet's external-fuel
    loadouts routinely place stores near the tanks and most are fine - a
    Sidewinder beside a tank is normal. This flags only those at or inside the
    separation of the one clash confirmed in game, so they can be eyeballed
    rather than guessed at.
    """
    pos = {int(a): (float(b), float(c), float(d)) for a, b, c, d in
           re.findall(r"^Station(\d+)=([-\d.]+),([-\d.]+),([-\d.]+)", text, re.M)}
    suspects = []
    for m in re.finditer(r"^\[WeaponSystem1([A-Za-z0-9_\-]+)\]\n(.*?)(?=^\[)",
                         text, re.M | re.S):
        st = {int(a): b.split("|")[0] for a, b in
              re.findall(r"^Station(\d+)=([A-Za-z]\S*)", m.group(2), re.M)}
        tanks = [s for s, v in st.items() if "tank" in v]
        for s, store in sorted(st.items()):
            if s in tanks or s not in pos:
                continue
            for k in tanks:
                if k not in pos:
                    continue
                d = sum((pos[s][i] - pos[k][i]) ** 2 for i in range(3)) ** 0.5
                if d <= CLASH_SEPARATION and ammunition_mass(store) >= CLASH_MASS:
                    suspects.append((m.group(1), s, store, d, ammunition_mass(store)))
    if suspects:
        print(f"    {source_name}: {len(suspects)} large store(s) as close to a tank as "
              f"the confirmed clash - worth a look in game:")
        for name, s, store, d, mass in sorted(suspects, key=lambda x: x[3]):
            print(f"       {name} S{s} {store} ({mass} kg) at {d:.5f}")


def verify_ammunition() -> None:
    expected = {
        AIM424_ID,
        "usn_aim-120d3",
        "usn_aim-9x",
        "usn_tank_610_f-18",
        "usn_tank_1200_f-18",
    }
    found = {path.stem for path in (ROOT / "mods-source").rglob("*.ini") if path.parent.name == "ammunition"}
    found.add(AIM424_ID)  # this pack writes it below
    missing = sorted(expected - found)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")


def build_growler(source: Path, destination_name: str, *, upgrade_ngj: bool) -> None:
    text = source.read_text(encoding="utf-8-sig")
    if upgrade_ngj:
        text = upgrade_legacy_growler(text)
    else:
        required = ("SystemName=AN/ALQ-249", "NGL-LB=NGL-LB", "ALQ-249=ALQ-249")
        missing = [token for token in required if token not in text]
        if missing:
            sys.exit(f"{source.name}: upstream NGJ layout changed; missing {missing}")

    text = fix_floating_tanks(text, source.name)
    wing_tank = detect_wing_tank(text, source.name)
    text = apply_pylon_convention(text, source.name, wing_tank)
    verify_station_geometry(text, GROWLER_LOADOUTS, source.name)
    verify_tank_points(GROWLER_LOADOUTS, source.name)
    keys = list(GROWLER_KEYS) + [LONG_RANGE_KEY]
    sections = (GROWLER_LOADOUTS + LONG_RANGE_LOADOUT).replace('__WING_TANK__', wing_tank)
    verify_station_geometry(text, LONG_RANGE_LOADOUT, source.name)
    text = extend_loadouts(text, keys, source.name)
    text = inject_loadouts(text, sections, source.name)
    verify_pylon_convention(text, source.name)
    report_tank_clearance(text, source.name)
    for key in keys:
        if text.count(f"[WeaponSystem1{key}]") != 1:
            sys.exit(f"{source.name}: invalid generated {key} section count")

    text = derive_sead260(text, source.name)
    aircraft = OUT / "aircraft"
    aircraft.mkdir(parents=True, exist_ok=True)
    (aircraft / destination_name).write_text(normalize_generated_text(text), encoding="utf-8")


def replace_harpoons(text: str, source_name: str) -> str:
    """Swap the AGM-84N Harpoons out of the anti-ship fits for LRASM.

    MurderHornetAntiShip and MH_AntiShipEF are the only fits on these
    airframes still carrying Harpoon. b-2_lrasm already flies from this
    airframe in MH_LRASM, so the substitution needs no geometry change - the
    stations involved (30-33) are the same ones that carry the AIM-174B.
    """
    text, n = re.subn(r"^(Station\d+=)usn_agm-84n\b", r"\1b-2_lrasm", text, flags=re.M)
    if n == 0:
        sys.exit(f"{source_name}: no AGM-84N found - upstream anti-ship fits changed")
    print(f"    {source_name}: {n} Harpoon rounds replaced with LRASM")
    return text


def derive_sead260(text: str, source_name: str) -> str:
    """Best-of SEAD for the 2020-family Growlers: AGM-88G AARGM-ER plus
    AIM-260, cloned from the airframe's own [SEAD] fit (the legacy Growler's
    reshaped MurderHornetSEADHeavyTanks already IS this fit, so it is skipped
    rather than duplicated under a second name)."""
    m = re.search(r"^\[WeaponSystem1SEAD\][^\n]*\n(.*?)(?=^\[)", text, re.M | re.S)
    if not m:
        return text
    body = m.group(1)
    # Adaptive: each airframe's SEAD carries its own era of rounds. Upgrade
    # whatever ARM and AMRAAM variants are present; require that at least one
    # swap actually landed so a silently-empty derivation cannot ship.
    swapped = 0
    for old, new in (("usn_agm-88e", "usn_agm-88g"), ("usn_agm-88c", "usn_agm-88g"),
                     ("usaf_aim-120c", "dts_aim-260"), ("usn_aim-120d-3", "dts_aim-260"),
                     ("usn_aim-120d3", "dts_aim-260"), ("usn_aim-120b", "dts_aim-260")):
        if old in body:
            body = body.replace(old, new)
            swapped += 1
    if swapped == 0 and "usn_agm-88g" not in body:
        sys.exit(f"{source_name}: SEAD donor carries nothing recognisable - re-check SEAD260")
    # extend_loadouts edits the AvailableLoadouts line ABOVE the loadout
    # blocks, so every offset held from before it - including m.end() - is
    # stale afterwards. Re-find the SEAD block on the mutated text before
    # splicing, or the clone lands mid-line 13 characters short.
    text = extend_loadouts(text, ["SEST_SEAD260"], source_name)
    m = re.search(r"^\[WeaponSystem1SEAD\][^\n]*\n(?:.*?)(?=^\[)", text, re.M | re.S)
    if not m:
        sys.exit(f"{source_name}: SEAD block vanished after AvailableLoadouts edit")
    return text[:m.end()] + "[WeaponSystem1SEST_SEAD260]\n" + body + text[m.end():]


def build_tank_610_override() -> None:
    """Re-mesh usn_tank_610_f-18: the fix for the low-riding wing tanks.

    The upstream ammunition file renders f-18_fuletank, a submesh carved out
    of the fa-18e aircraft model, so its origin is the aircraft's - the tank
    rides a fixed height below every pylon and neither seat offsets (0.0015
    and 0.003 both showed no visible change in game) nor station edits fix a
    mesh-origin error cleanly. usn_tank_1200_f-18 proved the VANILLA F-15C
    610 gal tank mesh sits flush on these exact stations (27/28, identical
    coordinates on all four airframes), so this override renders that mesh
    instead. Whole-file ammunition override: our pack outranks all three
    workshop mods that ship this file (F/A-18E/F, US Naval Aviation, RSA)."""
    src = SUPER_HORNET / "ammunition" / "usn_tank_610_f-18.ini"
    text = src.read_text(encoding="utf-8-sig")
    old = ("ResourcesFolder=assets/models/vechicle/aircraft/f-18e/\n"
           "ResourcesRoot=fa-18e.obj\n"
           "ResourcesMesh=f-18_fuletank\n"
           "ResourcesMaterial=f-18e_mat.ini")
    if old not in text:
        sys.exit("usn_tank_610_f-18: upstream Models block changed - re-check the re-mesh")
    new = ("# SEST re-mesh: f-18_fuletank is a submesh of the fa-18e aircraft model\n"
           "# and carries its origin, riding low under every pylon. The vanilla\n"
           "# F-15C 610 gal tank mesh (what usn_tank_1200_f-18 renders) sits flush\n"
           "# on the same stations, so it is used here. Fuel data untouched.\n"
           "ResourcesFolder=aircraft/usaf_f-15c/\n"
           "ResourcesRoot=usaf_f-15c\n"
           "ResourcesMesh=usaf_f-15c_tank_610\n"
           "ResourcesMaterialFolder=aircraft/usaf_f-15c/\n"
           "ResourcesMaterial=usaf_f-15c_tank_mat")
    ammo = OUT / "ammunition"
    ammo.mkdir(parents=True, exist_ok=True)
    (ammo / "usn_tank_610_f-18.ini").write_text(text.replace(old, new, 1), encoding="utf-8")
    print("    usn_tank_610_f-18.ini: re-meshed to the vanilla F-15C 610 tank")


def port_tanker_fit(text: str, source_name: str) -> str:
    """Port US Naval Aviation's new buddy-tanker fit onto our F/A-18E.

    USNA's 2026-08-25 update added a Tanker loadout to usn_fa-18e - a D-704
    buddy refuelling store on the centreline (probe-and-drogue, transferable
    external fuel) with two wing tanks. This pack shadows that file wholesale,
    so without porting it the update would silently vanish. The blocks are
    lifted verbatim from USNA's copy; usn_d-704 resolves via the Custom
    Loadout Editor. E-model only, matching the author.
    """
    src = US_NAVAL_AVIATION / "aircraft" / "usn_fa-18e.ini"
    donor = src.read_text(encoding="utf-8-sig", errors="replace")
    m = re.search(r"^\[WeaponSystem1Tanker\]\n.*?(?=^\[)", donor, re.M | re.S)
    keys = re.search(r"^FT_CenterPositions=[^\n]*\nFT_CenterRotations=[^\n]*\n",
                     donor, re.M)
    aar = re.search(r"^\[AerialRefuelingTanker\]\n(?:[^\n\[][^\n]*\n)*", donor, re.M)
    if not (m and keys and aar):
        sys.exit(f"{source_name}: USNA tanker blocks not found - upstream changed again")
    if "Tanker" in re.search(r"^AvailableLoadouts=(.+)$", text, re.M).group(1):
        sys.exit(f"{source_name}: Tanker already declared - drop this port")
    text = extend_loadouts(text, ["Tanker"], source_name)
    # position keys go into the WS1 table, next to the other centre keys
    anchor = re.search(r"^Station29=[^\n]*\n", text, re.M)
    if not anchor:
        sys.exit(f"{source_name}: no Station29 to anchor FT_Center keys")
    text = text[:anchor.end()] + keys.group(0) + text[anchor.end():]
    block = m.group(0).replace("Station2=usn_aim-9x\n",
                               "Station2=usn_aim-9x\n"
                               "Station11=dts_aim-260\n"
                               "Station12=dts_aim-260\n", 1)
    if block.count("dts_aim-260") != 2:
        sys.exit(f"{source_name}: tanker AIM-260 injection failed")
    marker = "[---------- WeaponMagazines ----------]"
    text = text.replace(marker, block + "\n" + marker, 1)
    return text + ("" if text.endswith("\n") else "\n") + "\n" + aar.group(0)


def derive_intercept260(text: str, source_name: str) -> str:
    """A pure AIM-260 CAP fit, cloned from the in-game-verified MALICE block.

    Same stations, same tank, same SubModelsToHide - only the rounds change:
    the four AIM-424 and four AIM-120D-3 all become dts_aim-260, giving eight
    JATMs plus the wingtip Sidewinders. Selectable under any squadron, which
    on the F/A-18F includes 1 SQN RAAF - that is the RAAF kitout.
    """
    m = re.search(r"^\[WeaponSystem1SEST_MaliceBlockIII\][^\n]*\n(.*?)(?=^\[)",
                  text, re.M | re.S)
    if not m:
        sys.exit(f"{source_name}: MALICE donor block missing for Intercept260")
    body = m.group(1)
    for old in ("sest_aim-424", "usn_aim-120d3"):
        n = len(re.findall(rf"^Station\d+={re.escape(old)}\s*$", body, re.M))
        if n == 0:
            sys.exit(f"{source_name}: donor no longer carries {old}")
        body = re.sub(rf"^(Station\d+={re.escape(old)})(\s*)$",
                      lambda mm: mm.group(1).replace(old, "dts_aim-260") + mm.group(2),
                      body, flags=re.M)
    return text[:m.end()] + "[WeaponSystem1SEST_Intercept260]\n" + body + text[m.end():]


def derive_hornet_escorts(text: str, wing_tank: str, source_name: str) -> str:
    """Two fuel-heavy AIM-260 fits, cloned from the Intercept260 block.

    Three external tanks is this airframe's ceiling, not a choice - one pair
    of wing tank pylons (fule_tank_point, stations 27/28) plus the
    centreline. The requested five-tank fit has nowhere to hang the other
    two, so both fits carry the maximum three.

      SEST_Intercept260ER  six JATM plus all three tanks - Intercept260
                           with the wing pylons wet (S32/33 removed: those
                           stations ARE the fuel pylons, seen overlapped).
      SEST_Escort260       the long-legged CAP: AIM-260 on the fuselage
                           (S11/12) and outer wing (S30/31) only, Sidewinders
                           on the tips, three tanks.

    fule_tank_point must be VISIBLE for wing tanks, so it leaves the hide
    list in both.
    """
    m = re.search(r"^\[WeaponSystem1SEST_Intercept260\][^\n]*\n(.*?)(?=^\[)",
                  text, re.M | re.S)
    if not m:
        sys.exit(f"{source_name}: Intercept260 donor missing for escort fits")
    body = m.group(1)
    er = body.replace(",fule_tank_point", "")
    er = re.sub(r"^(Station29=[^\n]*\n)",
                rf"Station27={wing_tank}\nStation28={wing_tank}\n\g<1>", er, flags=re.M)
    if er.count(wing_tank) < 3:
        sys.exit(f"{source_name}: escort fit failed to gain its wing tanks")
    # S32/33 (x +/-0.0328) sit 0.0003 from the wing tank stations 27/28
    # (x +/-0.0331) - in game those AIM-260 rode ON the fuel pylon, inside
    # the tank. With the wing pylons wet they must go: the ER fit is
    # 6x AIM-260 + 2x AIM-9X + 3 tanks.
    er = re.sub(r"^Station(32|33)=[^\n]*\n", "", er, flags=re.M)
    esc = re.sub(r"^Station(3|4)=[^\n]*\n", "", er, flags=re.M)
    return (text[:m.end()]
            + "[WeaponSystem1SEST_Intercept260ER]\n" + er
            + "[WeaponSystem1SEST_Escort260]\n" + esc
            + text[m.end():])


def build_super_hornet(file_name: str) -> None:
    """Add the MALICE fit to an APG-79 Super Hornet.

    Every Navy 2027 Super Hornet that already flies MurderHornetInterceptor
    carries the AIM-174B on stations 30-33, so the same fit transplants
    without geometry changes: usn_fa-18f_blk3 (Block III), plus usn_fa-18f
    and usn_fa-18e, which have the same radar class and station layout.
    """
    source = NAVY_2027 / "aircraft" / file_name
    text = source.read_text(encoding="utf-8-sig")
    text = replace_harpoons(text, source.name)
    text = fix_floating_tanks(text, source.name)
    wing_tank = detect_wing_tank(text, source.name)
    text = apply_pylon_convention(text, source.name, wing_tank)
    verify_station_geometry(text, BLOCK_III_LOADOUT, source.name)
    verify_tank_points(BLOCK_III_LOADOUT, source.name)
    text = extend_loadouts(text, BLOCK_III_KEYS, source.name)
    text = inject_loadouts(text, BLOCK_III_LOADOUT.replace("__WING_TANK__", wing_tank),
                           source.name)
    text = derive_intercept260(text, source.name)
    text = derive_hornet_escorts(text, wing_tank, source.name)
    if file_name == "usn_fa-18e.ini":
        text = port_tanker_fit(text, source.name)
    report_tank_clearance(text, source.name)
    if text.count("[WeaponSystem1SEST_MaliceBlockIII]") != 1:
        sys.exit(f"{source.name}: invalid generated MALICE section count")
    if text.count("[WeaponSystem1SEST_Intercept260]") != 1:
        sys.exit(f"{source.name}: invalid generated Intercept260 section count")

    aircraft = OUT / "aircraft"
    aircraft.mkdir(parents=True, exist_ok=True)
    (aircraft / file_name).write_text(normalize_generated_text(text), encoding="utf-8")


def write_language_files() -> None:
    for language, names in LOADOUT_NAMES.items():
        folder = OUT / f"language_{language}"
        folder.mkdir(parents=True, exist_ok=True)
        body = "[LoadoutNames]\n\n# ---------- SEST Growler NGJ + MALICE ----------\n"
        body += "".join(f"{key}={value}\n" for key, value in names.items())
        (folder / "loadout_names.ini").write_text(body, encoding="utf-8")


def build_raaf_squadrons() -> None:
    """RAAF strike wing (fwd Townsville) - claim the liveries Murder Hornet painted.

    Murder Hornet ships raaf_f18f.png and raaf_f18g.png, but the identity
    wiring is broken three ways:

      1. The EA-18G file declares NumberOfSquadrons=5 and defines Squadron6 -
         the RAAF one sits past the declared count and is unselectable, the
         same defect the F-22 mod had (declares 7, defines 1).
      2. That squadron flies Nation=US - an Australian-liveried Growler under
         a US flag.
      3. The language file pins "(Australia)" and callsign CRIKEY on
         Squadron2, which is VAQ-138's US Yellowjackets livery. The label and
         the paint are five squadrons apart.

    Two whole-file overrides fix the wiring (this pack already outranks
    Murder Hornet), and the merge-semantics language file renames the real
    squadrons: 1 SQN RAAF flies the F/A-18F, 6 SQN the Growler - forward-based Townsville by user call.
    Nation becomes "Australia" - the string the RAAF F-35A mod and the RAN
    fleet already use.
    """
    aircraft = OUT / "aircraft"
    aircraft.mkdir(parents=True, exist_ok=True)

    src = MURDER_HORNET / "aircraft" / "usn_ea-18g_squadrons.ini"
    text = src.read_text(encoding="utf-8", errors="replace")
    text = replace_once(text, "NumberOfSquadrons=5", "NumberOfSquadrons=6",
                        "usn_ea-18g_squadrons: declare Squadron6")
    text = replace_once(
        text,
        "LiveryTexture=raaf_f18g.png\nNation=US",
        "LiveryTexture=raaf_f18g.png\nNation=Australia   # 6 SQN RAAF, fwd Townsville",
        "usn_ea-18g_squadrons: RAAF nation")
    (aircraft / "usn_ea-18g_squadrons.ini").write_text(text, encoding="utf-8")

    # 1 SQN RAAF flies the BLOCK III, not the plain F (user call: if the RAAF
    # operates US Super Hornets, they operate the improved jet). The plain
    # F's RAAF squadron - Murder Hornet's Squadron10, its last - is deleted
    # outright so the un-upgraded F stops appearing under Australia, and the
    # Block III squadrons file gains Squadron8 with the same livery.
    src = MURDER_HORNET / "aircraft" / "usn_fa-18f_squadrons.ini"
    text = src.read_text(encoding="utf-8", errors="replace")
    text = replace_once(text, "NumberOfSquadrons=10", "NumberOfSquadrons=9",
                        "usn_fa-18f_squadrons: retire Squadron10")
    m = re.search(r"\n\[Squadron10\][^\n]*\n(?:.*?)(?=\n\[|\Z)", text, re.S)
    if not m or "raaf_f18f.png" not in m.group(0):
        sys.exit("usn_fa-18f_squadrons: Squadron10 is not the RAAF entry any more - re-check")
    text = text[:m.start()] + text[m.end():]
    (aircraft / "usn_fa-18f_squadrons.ini").write_text(text, encoding="utf-8")

    src = MURDER_HORNET / "aircraft" / "usn_fa-18f_blk3_squadrons.ini"
    text = src.read_text(encoding="utf-8", errors="replace")
    text = replace_once(text, "NumberOfSquadrons=7", "NumberOfSquadrons=8",
                        "usn_fa-18f_blk3_squadrons: declare Squadron8")
    if "raaf" in text.lower():
        sys.exit("usn_fa-18f_blk3_squadrons: upstream added its own RAAF squadron - re-check")
    # raaf_f18f.png lives in the plain F's texture folder; the Block III is
    # the same airframe so the skin should map - verify in game, the
    # fallback on a mismatch is default paint under the Australian flag.
    text = text.rstrip("\n") + (
        "\n\n[Squadron8]\n"
        "ResourcesLiveryFolder=assets/textures/fa-18f/\n"
        "LiveryTexture=raaf_f18f.png\n"
        "Nation=Australia   # 1 SQN RAAF, fwd Townsville\n")
    (aircraft / "usn_fa-18f_blk3_squadrons.ini").write_text(text, encoding="utf-8")

    folder = OUT / "language_en"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "aircraft_names.ini").write_text(
        "# SEST Growler NGJ + MALICE - RAAF strike wing identities (fwd Townsville).\n"
        "# language files merge key-by-key, so only these keys change.\n"
        "[usn_fa-18f_blk3]\n"
        "Squadron8=F/A-18F Block III (1 SQN RAAF),F/A-18F\n"
        "[usn_ea-18g]\n"
        "Squadron2=E/A-18G (VAQ-138),E/A-18G\n"
        "Squadron6=E/A-18G (6 SQN RAAF),E/A-18G\n"
        "Callsigns=Squadron1,ZAPPER|Squadron2,YELLOWJACKET|Squadron6,CRIKEY\n",
        encoding="utf-8")


def main() -> None:
    verify_ammunition()
    build_growler(NAVY_2027 / "aircraft" / "usn_ea-18g.ini", "usn_ea-18g.ini", upgrade_ngj=True)
    build_growler(
        SUPER_HORNET / "aircraft" / "usn_ea-18g_2020s.ini",
        "usn_ea-18g_2020s.ini",
        upgrade_ngj=False,
    )
    build_growler(
        US_NAVAL_AVIATION / "aircraft" / "usn_ea-18g_2020.ini",
        "usn_ea-18g_2020.ini",
        upgrade_ngj=False,
    )
    for hornet in ("usn_fa-18f_blk3.ini", "usn_fa-18f.ini", "usn_fa-18e.ini"):
        build_super_hornet(hornet)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    systems = OUT / "systems"
    systems.mkdir(exist_ok=True)
    (systems / "sensors.ini").write_text(NGJ_SENSOR, encoding="utf-8")
    write_aim424(OUT)
    build_tank_610_override()
    (OUT / "ammunition" / "usn_tank_1200_f-18.ini").write_text(
        TANK_OVERRIDE, encoding="utf-8")
    write_language_files()
    build_raaf_squadrons()

    outputs = sorted(path for path in OUT.rglob("*") if path.is_file())
    print(
        f"built {OUT.relative_to(ROOT)}: 3 NGJ Growlers, 3 APG-79 Super Hornets, "
        f"{len(GROWLER_KEYS) + len(BLOCK_III_KEYS) + 1} new loadouts "
        f"(NGJ Long Range on every Growler, two wing tanks), "
        f"{len(outputs)} files"
    )


if __name__ == "__main__":
    main()
