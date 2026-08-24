"""Shared definition of the SEST AIM-424 MALICE.

A what-if very-long-range air-to-air missile on the AGM-88G AARGM-ER
airframe, sized for F-35 internal-bay carriage. It is deliberately built as
a peer of the AIM-174B rather than a lesser cousin: the flight model is
aligned key-for-key with U.S. Navy 2027's usn_aim-174b so the two
encyclopedia cards compare directly. The 3D model rides on the AGM-88G
assets that US Naval Aviation (3737267013) ships, so that mod must stay
enabled for the proper mesh (otherwise the game falls back to the RIM-7
asset-bundle stand-in, same as the modded AARGM-ERs themselves do).

All four SEST packs that carry MALICE fits write identical copies of
ammunition/sest_aim-424.ini and a partial language_en/ammunition_names.ini -
identical same-path files are a safe overlap whichever pack sits higher in
the Mod Manager.
"""

AIM424_ID = "sest_aim-424"

# The MALICE borrows the AGM-88G mesh, which is a full-size AARGM-ER - longer
# than an air-to-air round sized to fit inside an F-35 bay. ResourcesMeshScale
# shrinks the model for THIS ammunition only; the real usn_agm-88g keeps its
# own dimensions because that key lives in our ini, not in the shared model.
# The collider is scaled by the same factor so the hit box tracks the visual.
# Change it with:  python3 integration/common/set_malice_scale.py --scale 0.85
MESH_SCALE = 0.9

# Aligned to usn_aim-174b as shipped by U.S. Navy 2027 Capabilities
# (3606774881) - the version that actually wins the load order in this
# collection, and the card the MALICE gets compared against in game. Same
# explicit-drag flight model, same 150,000 ft loft ceiling, same fragmentation
# warhead class, same datalink midcourse, same chart basis (36,000 ft / 260 kt),
# same modern ECCM keys.
#
# What stays different, on purpose:
#   MaxLaunchRange 290 vs 316 nm - it has to fit inside an F-35 weapons bay
#   DragCoefficient 3.6 vs 3.41 - shorter, fatter AARGM-ER airframe.
#     THIS KEY MUST STAY EXPLICIT: at -1 the engine back-solves 8.14 from the
#     airframe and the missile loses roughly a third of its reach.
#   a real dual-pulse motor, ~170 G.s against the 174B's ~144, paying for that
#   Power 48 vs 52 and CEP 10 m vs 6 - slightly less lethal endgame
#   SeekerActiveRange 40 nm vs 15, passive 80 nm vs 15, and a Full passive
#     anti-emitter mode against HomeOnJam - the 2030s seeker is what you buy
#   MaxTurnRate 28 vs 30 deg/s, MaxTurnG 25 - still not an AIM-260 (40 deg/s)
AIM424_INI = """\
[General]
# AIM-424 MALICE (SEST what-if)
# Users: usn_f-35c, raaf_f-35a, usaf_f-15ex_SEII, usn_f-18e/f/g (SEST packs)
Type=Missile                           // can be Projectile, Missile, Torpedo
TargetType=AAW                         // can be AAW, ASuW, ASW
SecondaryTargetType=ASuW               // AARGM-ER heritage: it is a strike airframe
Mass=467                               // in kg. Used for aircraft
AmmoPoints=2600
AirLaunched=True                       // encyclopedia: show the launch-altitude band

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
WarheadType=6                           // fragmentation, as the AIM-174B
Power=48                                // cf. AIM-174B 52 - smaller airframe
ImpactSize=Medium                       // Impact size, can be small, medium, large, verylarge
Penetration=Always                      // can be minor, moderate, heavy, always
FuzeProximityDistance=18.0              // for proximity fuze: distance to target in meters
KillProbability=0.98                    // cf. AIM-174B 1.02
InterceptOutOfAltitudePenalty=0.15
InterceptSpeedPenaltyMultiplier=0.4

[Guidance]
GuidanceType=3
MidCourseCorrection=3                  // 3 = Datalink, as the AIM-174B
Retargetable=True
DropDuration=1.0                       // bay ejection: unpropelled fall time in seconds
InitialFlightPhaseDuration=2.2         // seconds of unguided straight flight
MaxLoftAngle=30.0                      // Climb angle for initial loft
MaxLoftAlt=150000                      // Maximum altitude for lofting, in feet
TerminalLoft=True
TerminalApproachDist=36                // in N. miles - just under seeker range
LocalTerminalOnly=False
IgnoreHeightDifferenceForTargetDist=True
# Aligned to the U.S. Navy 2027 AIM-174B (usn_aim-174b): same explicit drag
# model, same loft ceiling, same chart basis, so the two encyclopedia cards
# are read on the same assumptions. The deliberate deltas that remain are
# the MALICE identity, not accidents:
#   MaxLaunchRange 290 vs 316 - it has to fit an F-35 weapons bay
#   DragCoefficient 3.6 vs 3.41 - shorter, fatter AARGM-ER airframe
#   a real dual-pulse motor (~170 G.s vs the 174B's ~144) offsetting that drag
#   SeekerActiveRange 40 nm vs 15, passive 80 nm vs 15, and a Full passive
#     anti-emitter mode vs HomeOnJam - the 2030s seeker is what you buy
#   MaxTurnRate 28 vs 30 and CEP 10 m vs 6 - marginally less precise endgame
ApplyKinematics=True
MaxVelocity=3000                       // Maximum speed in knots (AIM-174B 2650)
VelocityBleed=1                        // let the kinematics model decide, as the 174B
AccelerationTime=4                     // initial booster burn, seconds
Acceleration=20                        // booster acceleration, Gs
SustainerAccelerationTime=20           // sustainer burn, seconds
SustainerAcceleration=4.5
DragCoefficient=3.6                    // explicit - a -1 here back-solves to 8.14 and kills the reach
TypicalLaunchVelocity=260              // chart basis matched to usn_aim-174b
TypicalFiringAlt=36000
TypicalTargetAlt=36000
TypicalTargetSpeed=0
LiftFactor=0.001                       // matches the AIM-174B
MaxFlightTime=400                      // hard cutoff, seconds
TimeLimited=True
MaxTurnRate=28.0                       // Maximum turnrate in degrees per second
MaxTurnG=25                            // matches AIM-54A / AIM-120D-3 / AIM-260
MinLaunchRange=2                       // Minimum launch range in nautical miles
MaxLaunchRange=290.0                   // Maximum launch range in nautical miles
MinAttackAltitude=20                   // Minimum altitude of a target, in feet
MaxAttackAltitude=150000               // Maximum altitude of target, in feet
MaxAttackVelocity=7000
MinLaunchAltitude=200                  // Minimum launch altitude in feet
MaxLaunchAltitude=60000                // Maximum launch altitude in feet
LaunchReliability=99
CircularErrorRadius=10.0               // cf. AIM-174B 6.0
CircularErrorRadiusLarge=14.0
MinAltMalusFactor=0.7
SeekerGain=62.0                        // Seeker gain in dB
SeekerFOV=120.0                        // Seeker field-of-view in degrees
SecondaryPassiveRadarGuidanceType=Full // AARGM heritage: radar AND ECM emitters, not just jammers
PassiveRadarGuidanceFrequencies=All
SeekerPassiveRange=80                  // Seeker passive range in nautical miles
SeekerActiveRange=40.0                 // Seeker active range in nautical miles
Frequency=X-Band
PeakPower=40.0
TargetMemory=True
CounterMeasuresRejection=96
NoiseRejection=96
AntiCountermeasuresBonus=0.95
AntiJammerBonus=0.95
SelfDestructAfterTargetGone=False
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
# Scaled down from the full-size AARGM-ER mesh - see MESH_SCALE in aim424.py.
ResourcesMeshScale=__SCALE__,__SCALE__,__SCALE__
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
Scale=__COLX__,__COLX__,__COLZ__
"""

# language_en/ammunition_names.ini format: stem=DisplayName,Nickname,Category,Description
# (the description must not contain commas — they are field separators).
AIM424_NAMES_INI = """\
[AmmunitionNames]
# ---------- SEST AIM-424 MALICE ----------
sest_aim-424=AIM-424,MALICE,AAM,The AIM-424 MALICE is a what-if very-long-range air-to-air missile developed from the AGM-88G AARGM-ER airframe and sized for internal carriage on the F-35. It trades a little of the AIM-174B's reach for a far better seeker: active-radar terminal homing at 40 nm with datalink midcourse guidance and a full passive anti-emitter mode that homes on radars and jammers alike. A secondary anti-surface capability comes with the AARGM-ER heritage.
"""


# Collider box at MESH_SCALE=1, i.e. the raw AGM-88G hull dimensions.
_COLLIDER = (0.005, 0.04291637)


def aim424_ini(scale=None):
    """The ammunition ini with the mesh and its collider scaled together."""
    s = MESH_SCALE if scale is None else scale
    if not 0 < s <= 2:
        raise ValueError(f"implausible mesh scale {s} - expected roughly 0.1 to 1.5")
    return (AIM424_INI
            .replace("__SCALE__", f"{s:g}")
            .replace("__COLX__", f"{_COLLIDER[0] * s:.6g}")
            .replace("__COLZ__", f"{_COLLIDER[1] * s:.6g}"))


def write_aim424(out_dir, scale=None):
    """Write the ammunition ini + name entries into a pack folder (Path)."""
    ammo = out_dir / "ammunition"
    ammo.mkdir(parents=True, exist_ok=True)
    (ammo / f"{AIM424_ID}.ini").write_text(aim424_ini(scale), encoding="utf-8")
    lang = out_dir / "language_en"
    lang.mkdir(exist_ok=True)
    (lang / "ammunition_names.ini").write_text(AIM424_NAMES_INI, encoding="utf-8")
