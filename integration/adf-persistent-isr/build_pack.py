#!/usr/bin/env python3
"""Build the SEST ADF Persistent ISR pack: two Australian high-altitude ISR
UAVs cloned from the MQ-9 Reaper mod's MQ-9 ER airframe (the collection's only
long-wing UAV mesh).

                    pseudo-satellite. Near-nil RCS/IR signature and a purely
                    passive sensor fit (OPAZ optics + ELINT): it emits nothing.
  raaf_mq-4c_triton MQ-4C Triton — the RAAF's maritime Global Hawk. Unarmed
                    broad-area surveillance jet with the AN/ZPY-3 MFAS 360-deg
                    radar, MTS-B optics and an ELINT/RWR fit.

Both are NEW unit ids: the MQ-9 mod is untouched and must stay installed —
meshes, materials, the gear animation file and (for the Triton) the MTS-B
sensor definition resolve from it cross-mod. Everything else resolves from
vanilla; the pack ships its own AN/ZPY-3 and OPAZ sensor definitions.

Usage (repo root):  python3 integration/adf-persistent-isr/build_pack.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
MQ9_MOD = MODS / "3503670861"                       # General Atomics MQ-9 Reaper
DONOR = MQ9_MOD / "aircraft" / "usaf_mq-9_er.ini"   # long-wing ER airframe
VANILLA_SENSORS = MODS / "_vanilla" / "original" / "systems" / "sensors.ini"
OUT = Path(__file__).resolve().parent / "SEST_ADF_Persistent_ISR"

# Every MQ-9 weapon-furniture submodel — both units fly clean
HIDE_WEAPON_FURNITURE = ("pyl_inner,rain_inner,rail_inner_low,pyl_mid,rail_mid,"
                         "rail_mid_low,lau_129,agm-114_pyl_l,agm-114_pyl_r,"
                         "pyl_outer,rail_outer,pyl_c,aim-92_l,aim-92_r")

# Vanilla sensor systems the units reference (Triton's MTS-B comes from the MQ-9 mod)
VANILLA_SYSTEMS = ["AdvancedOptics", "AircraftELINT", "AircraftRWR"]
MQ9_SYSTEMS = ["AN/AAS-52_Visual"]

TRITON_HEAD = """[---------- General Data ----------]
[General]
UnitType=Aircraft
CarrierCapable=False

DefaultCameraDistance=1
MinCameraDistanceForeAft=0.39
MinCameraDistanceBroadside=0.39
CameraPivotHeight=0.0

#Taxi values
GroundedPitchAngle=0
GroundPivot=0,-0.029,-0.015
LandingPivot=0,-0.029,-0.135
OnDeckPositionOffset=0,0,-0.023

[AI]
UnitScoreValue=4
Role=MaritimePatrol,Recon,ESM

[SensorData]
#Visual
VisualIdentificationRange=7.5
IRSignature=Small              // single high-bypass turbofan
# Radar related (RCS => radar cross section)
RCS=Small                      // blended composite airframe, smaller return than a fighter

[Animations]
NumberOfAnimationReferences=1
AnimationFile_1=animations_usaf_uav_mq-9

[---------- Flight Model ----------]
[Engine]
EngineIntakeArea=1.6

[FlightModel]
PitchGain=0.6
VelocityGain=0.06
HeadingGain=1.5
YawRateLimit=30
BankGain=0.6
MaxRollForHeading=25.0
MaxRollRate=25.0

ThrustGain=0.3
SpeedBrakeFractionGain=0.2

SpeedDeltaPerAltitudeChange=0.0885

[Performance]
#Dimensions
WingSpan=39.9                        //meters (mesh is the 20 m MQ-9 - accepted stand-in)
#Parameters
MaxG=2.5

MaxClimbRate=10.0                    //Meters per second
MaxClimbPitch=15
MaxCombatClimbPitch=20
MaxDescentPitch=-15
MaxCombatDescentPitch=-20

EmptyMass=6781.0                     // in kg
MaxFuel=7390.0                       // in kg

PerEngineMaxThrust=39700             //Newtons - RR AE 3007H turbofan
PerEngineMaxAfterburnerThrust=39700  //Newtons
EngineCount=1
EngineWarmUp=15

Ceiling=56500                        // ceiling in feet
CruiseAltitude=53000                 //in feet
AltitudeEfficiency=0.5,0.85,0.5

#Governing of max speed
MaxSpeedAtSeaLevel=331               //in knots
StallSpeed=95.0                      //in knots
MachLimit=0.6                        //for 37000ft

#SpeedAndRange   MachNumbers or knots, Specified units or multiplier (except Cruise range)
RangeUnits=Miles

SpeedAndRange_Landing=115,0.4
SpeedAndRange_Loiter=250,0.6
SpeedAndRange_Cruise=310,9430        // 8,200 nmi ferry range / 24+ hours on station
SpeedAndRange_Max=357,0.8

Altitudes=200,1000,5000,15000,30000,45000,56000  // in feet
"""

TRITON_SENSORS_WEAPONS = """[---------- Sensor Systems ----------]
############################################################
# Sensor Systems
############################################################
[SensorSystems]
NumberOfSensorSystems=4

[SensorSystem1] #MFAS 360-degree AESA maritime surveillance radar
Type=Radar
SystemName=AN/ZPY-3
Mount=Dummy
ModuleType=Sensor

[SensorSystem2] #MTS-B EO/IR turret (resolves from the MQ-9 mod)
Type=Visual
SystemName=AN/AAS-52_Visual
Mount=Dummy
ViewArcs=-180,180|-90,20
ModuleType=Sensor

#---------- ESM ----------

[SensorSystem3] #ZLQ-1 ESM/ELINT fit
Type=ESM
SystemName=AircraftELINT
Mount=Dummy
ModuleType=Sensor

[SensorSystem4] #RWR
Type=ESM
SystemName=AircraftRWR
Mount=Dummy
ModuleType=Sensor

[---------- Weapon Systems ----------]
############################################################
# Weapon Systems - none: the Triton is a pure surveillance aircraft
############################################################
[WeaponSystems]
NumberOfWeaponSystems=1

[WeaponSystem1] #Hardpoint
Type=Hardpoint
SystemName=Hardpoint
NumberOfStations=0

[---------- Weapon Loadouts ----------]
[WeaponSystem1Default]
ReadyUpTime=20               // in minutes
CoolDownTime=45              // in minutes
SubModelsToHide={hide}
"""

SYSTEMS_INI = """[AN/ZPY-3]
# Multi-Function Active Sensor: the MQ-4C's belly-mounted 360-degree AESA
# maritime surveillance radar. Pattern follows the P-8A's AN/APY-10 with a
# full-circle scan and inverse-SAR classification modes folded into gain.
Kind=Radar
Type=Search            // Classes can be "DirectedSearch", "Search", "Targeting"
HasDataLink=True       // BAMS exists to feed the surface picture to the force
Role=Surface           // Role can be "Surface", "Air", "AirAndSurface"
Mode=Illuminate
CanDetectLandTargets=True
CanDetectPeriscope=True
TargetChannels=0
WeaponChannels=0
ViewArcs=-180,180|-85,3    // belly array: everything below the horizon, all bearings
LookDownMultiplier=1.1
MinRange=0.2           // min range in km
MaxRange=430.0         // max range in km
MinAltitude=0
MaxAltitude=35000
RangeResolution=90.0
Gain=60                // gain in dB on the sensor
Frequency=X-Band
PeakPower=900.0        // output peak power in kW
IdentificationTime=25

"""

SQUADRONS = {
    "raaf_mq-4c_triton": """[General]
SerialnumberReferences=Modex,Right_Outer_Wing_Modex,Left_Rudder_Modex,Right_Rudder_Modex
EmblemReference=CarrierName
NationFlagReference=Flag1
NumberOfSquadrons=2

[Default]
ResourcesLiveryFolder=assets/textures/mq-9/
LiveryTexture=42_ATKS.png
Nation=Australia

[Squadron1]
ResourcesLiveryFolder=assets/textures/mq-9/
LiveryTexture=42_ATKS.png
Nation=Australia

[Squadron2]
ResourcesLiveryFolder=assets/textures/mq-9/
LiveryTexture=42_ATKS.png
Nation=Australia
""",
}

NAMES_INI = """[General]

[raaf_mq-4c_triton]
Type=UAV
Default=MQ-4C Triton,Triton
DefaultDescription=Northrop Grumman MQ-4C Triton, the maritime Global Hawk operated by No. 9 Squadron RAAF from Edinburgh with forward detachments at Tindal. A 40 m-span HALE surveillance jet pairing the AN/ZPY-3 MFAS 360-degree AESA radar with MTS-B optics and an ELINT/RWR fit: one orbit sweeps over two million square miles of ocean a day and feeds it to the force by datalink. Unarmed - it finds, others finish. (Flies the collection's MQ-9 ER mesh as an accepted stand-in.)
Squadron1=MQ-4C No. 9 SQN,Triton
Squadron2=MQ-4C Det Tindal,Triton
"""

INFO_INI = """[Language_en]
Name=SEST ADF Persistent ISR
Description=MQ-4C Triton, the RAAF's maritime Global Hawk, as a new unit: AN/ZPY-3 MFAS 360-degree radar, MTS-B optics, ELINT/RWR, unarmed. Flies the MQ-9 Reaper mod's ER mesh as a stand-in, so the MQ-9 mod must stay installed and enabled. Additive - place below the MQ-9 Reaper mod.

[Compatibility]
ApproximateVersion=0.6.8
"""


def extract(donor_text, start_marker, end_marker=None):
    """Verbatim donor slice from start_marker to end_marker (or EOF)."""
    start = donor_text.find(start_marker)
    if start < 0:
        sys.exit(f"donor layout changed: {start_marker!r} not found in {DONOR}")
    if end_marker is None:
        return donor_text[start:]
    end = donor_text.find(end_marker, start)
    if end < 0:
        sys.exit(f"donor layout changed: {end_marker!r} not found in {DONOR}")
    return donor_text[start:end]


def check_systems():
    problems = []
    vanilla = VANILLA_SENSORS.read_text(encoding="utf-8", errors="replace")
    for name in VANILLA_SYSTEMS:
        if f"[{name}]" not in vanilla:
            problems.append(f"vanilla sensor definition missing: [{name}]")
    mq9_sys = (MQ9_MOD / "systems" / "sensors.ini").read_text(encoding="utf-8",
                                                              errors="replace")
    for name in MQ9_SYSTEMS:
        if f"[{name}]" not in mq9_sys:
            problems.append(f"MQ-9 mod sensor definition missing: [{name}]")
    if not (MQ9_MOD / "animations" / "animations_usaf_uav_mq-9.ini").exists():
        problems.append("MQ-9 mod animation file missing: animations_usaf_uav_mq-9")
    return problems


def main():
    if not DONOR.exists():
        sys.exit(f"MQ-9 ER donor not found: {DONOR} — is mods-source exported?")
    donor = DONOR.read_text(encoding="utf-8", errors="replace")

    problems = check_systems()

    # Donor slices reused verbatim: control surfaces + the whole mesh/effects/
    # sounds/colliders tail. Identity, flight model, sensors and weapons are ours.
    controls = extract(donor, "[---------- Main Systems ----------]",
                       "[---------- Sensor Systems ----------]")
    tail = extract(donor, "[---------- Mesh definitions----------]")

    # Every submodel we hide must exist in the donor's weapon submodel list
    for sub in HIDE_WEAPON_FURNITURE.split(","):
        if not re.search(rf"^Weapon_\d+={re.escape(sub)}\s*$", donor, re.M):
            problems.append(f"donor no longer declares weapon submodel {sub!r}")
    if problems:
        sys.exit("validation failed:\n  " + "\n  ".join(problems))

    # --- Triton: a jet — drop the prop declarations (undeclared submodels are
    # never instantiated), strip the prop-idle keys and swap in vanilla jet audio
    triton_controls = re.sub(r"^Props(Idle|InFlight)=.*\n", "", controls, flags=re.M)
    triton_tail = tail.replace("General_2=Prop\n", "")
    triton_tail = triton_tail.replace("General_3=prop_disc\n", "")
    triton_tail = triton_tail.replace("EngineAudioClip=audio/aircraft/TurboPropP3-COrion",
                                      "EngineAudioClip=audio/aircraft/TF30")
    triton_tail = triton_tail.replace("ExhaustAudioClip=audio/aircraft/turboprop_far",
                                      "ExhaustAudioClip=audio/aircraft/jet_rear_1")
    triton_tail = triton_tail.replace("FarAudioClip=audio/aircraft/turboprop_far",
                                      "FarAudioClip=audio/aircraft/jet_far_1")
    if "General_2=Prop" in triton_tail or "TurboPropP3-COrion" in triton_tail:
        sys.exit("Triton prop/audio rewrite failed — donor layout changed")
    triton = (TRITON_HEAD + "\n" + triton_controls
              + TRITON_SENSORS_WEAPONS.format(hide=HIDE_WEAPON_FURNITURE)
              + "\n" + triton_tail)

    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "systems").mkdir(exist_ok=True)
    (OUT / "language_en").mkdir(exist_ok=True)

    (OUT / "aircraft" / "raaf_mq-4c_triton.ini").write_text(triton, encoding="utf-8")
    for unit, text in SQUADRONS.items():
        (OUT / "aircraft" / f"{unit}_squadrons.ini").write_text(text, encoding="utf-8")
    (OUT / "systems" / "sensors.ini").write_text(SYSTEMS_INI, encoding="utf-8")
    (OUT / "language_en" / "aircraft_names.ini").write_text(NAMES_INI, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")

    print(f"built {OUT.relative_to(ROOT)}: raaf_mq-4c_triton, "
          "donor mesh/controls verified, all sensor references validated")


if __name__ == "__main__":
    main()
