"""Shared definition of the SEST AIM-424 MALICE.

A what-if very-long-range air-to-air missile on the AGM-88G AARGM-ER
airframe, sized for F-35 internal-bay carriage. Flight/seeker behaviour
follows Murder Hornet's AIM-174B (usn_aim-174b); the 3D model rides on the
AGM-88G assets that US Naval Aviation (3737267013) ships, so that mod must
stay enabled for the proper mesh (otherwise the game falls back to the
RIM-7 asset-bundle stand-in, same as the modded AARGM-ERs themselves do).

Both F-35 patch packs write identical copies of ammunition/sest_aim-424.ini
and a partial language_en/ammunition_names.ini — identical same-path files
are a safe overlap whichever pack sits higher in the Mod Manager.
"""

AIM424_ID = "sest_aim-424"

# Seeker/guidance concept from usn_aim-174b (Murder Hornet); airframe, mass,
# kinematics and visuals from usn_agm-88g (US Naval Aviation). Deliberate
# deltas vs the AIM-174B:
#   Mass 860->467 and full ApplyKinematics, so it obeys the same drag and
#     energy model as every other AAM instead of the AIM-174B's legacy block
#   MaxLaunchRange 130->120, MaxTurnRate 30->22 with MaxTurnG=25 capping it
#   KillProbability 1.02->0.88 and CEP 5m->60m, so it can miss
#   SeekerActiveRange 65->25 nm and FOV 180->110 deg, so it can be beamed
#   SecondaryPassiveRadarGuidanceType HomeOnJam->Full (AARGM heritage:
#     passive homing on radar emitters, not just jammers)
AIM424_INI = """\
[General]
# AIM-424 MALICE (SEST what-if)
# Users: usn_f-35c (SEST F-35C JATM), raaf_f-35a (SEST RAAF F-35A JATM)
Type=Missile                           // can be Projectile, Missile, Torpedo
TargetType=AAW                         // can be AAW, ASuW, ASW
Mass=467                               // in kg. Used for aircraft
AmmoPoints=3000

DefaultCameraDistance=0.6
MinCameraDistanceForeAft=0.29
MinCameraDistanceBroadside=0.29
CameraPivotHeight=0.0

DecalClass=SAMImpacts  // referenced in effects/decals.ini

[SensorData]
VisualIdentificationRange=4  // at what range in nm this unit can be visually identified
IRSignature=Small
RCS=VerySmall
TransientRCS=Small                    // Transient visibility on the radar
TransientVisualIdentificationRange=5  // Transient can be visually detected at this distance in nmi
TransientBaseNoise=200                // In db

[WarheadData]
WarheadType=0
Power=42
ImpactSize=SemiSmall                    // Impact size, can be small, medium, large, verylarge
Penetration=Always                      // can be minor, moderate, heavy, always
FuzeProximityDistance=20.0              // for proximity fuze: distance to target in meters
KillProbability=0.88                    // vanilla AAW tops out at 0.85; 0.88 for a 2030s seeker

[Guidance]
GuidanceType=3
MidCourseCorrection=1                  // 0 = None, 1 = Radio Command, 2 = Wire Guided
DropDuration=1.0                       // bay ejection: unpropelled fall time in seconds
InitialFlightPhaseDuration=2.2         // seconds of unguided straight flight
MaxLoftAngle=25.0                      // Climb angle for initial loft
MaxLoftAlt=99000                       // Maximum altitude for lofting, in feet
MaxLoftVelocity=2400.0                 // Maximum speed in knots for lofting
TerminalApproachDist=22                // in N. miles - just under seeker range
LocalTerminalOnly=False
IgnoreHeightDifferenceForTargetDist=True
# Full kinematics, ported from the AGM-88G donor that supplies this airframe
# (same 467 kg body, same motor budget: total dv ~1284 m/s ~ Mach 3.75). The
# legacy no-drag block the AIM-174B uses would let this missile arrive at
# 120 nm still at Mach 3+, which no other AAM in the game can do.
ApplyKinematics=True
MaxVelocity=2900                       // Maximum speed in knots
VelocityBleed=0.35                     // cf. AIM-120D 0.5, AIM-260 0.12
AccelerationTime=4                     // initial booster burn, seconds
Acceleration=22                        // booster acceleration, Gs
SustainerAccelerationTime=25           // sustainer burn, seconds
SustainerAcceleration=1.8
DragCoefficient=-1                     // back-solved from MaxLaunchRange + the Typical* set
TypicalLaunchVelocity=550
TypicalFiringAlt=35000
TypicalTargetAlt=35000
TypicalTargetVelocity=500
LiftFactor=0.002                       // vanilla AIM-54A uses 0.001
MaxFlightTime=240                      // hard cutoff, seconds
MaxTurnRate=22.0                       // Maximum turnrate in degrees per second
MaxTurnG=25                            // matches AIM-54A / AIM-120D-3 / AIM-260
MinLaunchRange=2                       // Minimum launch range in nautical miles
MaxLaunchRange=120.0                   // Maximum launch range in nautical miles
MinAttackAltitude=10                   // Minimum altitude of a target, in feet
MaxAttackAltitude=100000               // Maximum altitude of target, in feet
LaunchReliability=99
CircularErrorRadius=60                 // cf. dts_aim-120d-3 at 106
CircularErrorRadiusLarge=12
SeekerGain=48.0                        // Seeker gain in dB
SeekerFOV=110.0                        // Seeker field-of-view in degrees
SecondaryPassiveRadarGuidanceType=Full // AARGM heritage: passive homing on radar and ECM emitters
PassiveRadarGuidanceFrequencies=All
SeekerPassiveRange=80                  // Seeker passive range in nautical miles
SeekerActiveRange=25.0                 // Seeker active range in nautical miles
Frequency=X-Band
PeakPower=35.0
TargetMemory=True
AntiCountermeasuresBonus=.90
AntiJammerBonus=0.85
SelfDestructDelay=5.0

[---------- Mesh definitions----------]
[Models]
AssetBundleMeshes=/AssetBundles/StandaloneWindows/aircraft
AssetBundleMaterials=/AssetBundles/StandaloneWindows/aircraft
AssetBundleMesh=usn_rim-7
AssetBundleDamagedMesh=
AssetBundleMaterial=usn_rim-7_mat
AssetBundleMeshHullCollider=usn_rim-7_coll
# Real mesh: the AGM-88G model shipped by US Naval Aviation (3737267013).
ResourcesFolder=assets/models/ammunition/agm-88/
ResourcesRoot=agm-88g.obj
ResourcesMesh=agm-88g
ResourcesMaterial=usn_agm-88g_mat.ini
NumberOfSubModels=0

[Particles]
BoosterEffect=effects/weapons/emitters/aam_effect
BoosterEffectPosition=0,0,-0.04
InFlightEffectClass=DefaultMissileInflightEffect
InFlightEffectPosition=0,0,-0.04
InFlightEffectStartTime=2.0  // in seconds

HitShipExplosionClass=MediumShipHitExplosion
HitAirExplosionClass=MediumMissileExplosions
HitWaterSplashClass=SmallWaterSplashes
HitDefaultExplosionClass=MediumMissileExplosions

[Colliders]
Collider=col_main

[col_main]
Collider=Box
Position=0,0,0
Rotation=0,0,0
Scale=0.005,0.005,0.04291637
"""

# language_en/ammunition_names.ini format: stem=DisplayName,Nickname,Category,Description
# (the description must not contain commas — they are field separators).
AIM424_NAMES_INI = """\
[AmmunitionNames]
# ---------- SEST AIM-424 MALICE ----------
sest_aim-424=AIM-424,MALICE,AAM,The AIM-424 MALICE is a what-if very-long-range air-to-air missile developed from the AGM-88G AARGM-ER airframe and sized for internal carriage on the F-35. Active-radar terminal homing with datalink midcourse guidance and a passive anti-emitter mode let it engage fighters AEW platforms and jammers at extreme range.
"""


def write_aim424(out_dir):
    """Write the ammunition ini + name entries into a pack folder (Path)."""
    ammo = out_dir / "ammunition"
    ammo.mkdir(parents=True, exist_ok=True)
    (ammo / f"{AIM424_ID}.ini").write_text(AIM424_INI, encoding="utf-8")
    lang = out_dir / "language_en"
    lang.mkdir(exist_ok=True)
    (lang / "ammunition_names.ini").write_text(AIM424_NAMES_INI, encoding="utf-8")
