"""Shared definition of the SEST AIM-424 MALICE.

NO LONGER A WHAT-IF. This file was written when the AIM-424 was a rumour and
modelled it as an invention on the AGM-88G AARGM-ER airframe. The U.S. Navy
revealed the real weapon at the Tailhook symposium on 22 August 2026, already
in flight test, and published enough to retire the guesswork:

    Raytheon AIM-424 LRAAM "Malice"
    length     13.5 ft   (4.11 m)
    diameter   13.5 in   (34.3 cm)   - the same body as the SM-6 / AIM-174B
    wingspan   26.2 in   (66.5 cm)
    range      "in excess of 250 nautical miles" (463 km), per the Navy fact file
    design     two-stage, solid-propellant rocket motor
    warhead    blast-fragmentation
    platforms  F/A-18E/F, F-35C, F/A-XX, and reportedly the USAF F-47
    fit        confirmed to fit the F-35 internal weapons bay

Mass, seeker and guidance were NOT disclosed and remain this file's estimates;
each one is justified at its key below. Everything that was disclosed is now
used instead of the old AARGM-ER reasoning.

The flight model stays aligned key-for-key with U.S. Navy 2027's usn_aim-174b,
which is now a stronger choice than it was: the two missiles share a diameter,
a mission and a Navy, so the encyclopedia cards genuinely do compare.

THE 3D MODEL IS STILL AN AGM-88G. No AIM-424 mesh exists in the collection, so
the missile renders on the AARGM-ER assets US Naval Aviation (3737267013)
ships. That mod must stay enabled or the game falls back to a RIM-7 stand-in.
This is a rendering substitution only - it no longer implies anything about
the airframe.

All four SEST packs that carry MALICE fits write identical copies of
ammunition/sest_aim-424.ini and a partial language_en/ammunition_names.ini -
identical same-path files are a safe overlap whichever pack sits higher in
the Mod Manager.
"""

AIM424_ID = "sest_aim-424"

# REMOVED: ResourcesMeshScale. Shrinking the mesh by 0.9 was cosmetic, and the
# missile stopped rendering as an AARGM-ER afterwards - the model block falls
# back to AssetBundleMesh=usn_rim-7, a short fat Sea Sparrow, which is exactly
# what showed up under the wing. The [Models] block below is now byte-identical
# to US Naval Aviation's own usn_agm-88g, which is proven to load. Do not add
# keys to it that the source mod does not use.

# Aligned to usn_aim-174b as shipped by U.S. Navy 2027 Capabilities
# (3606774881) - the version that actually wins the load order in this
# collection, and the card the MALICE gets compared against in game. Same
# explicit-drag flight model, same 150,000 ft loft ceiling, same fragmentation
# warhead class, same datalink midcourse, same chart basis (36,000 ft / 260 kt),
# same modern ECCM keys.
#
# What stays different, on purpose:
#   MaxLaunchRange 290 vs 316 nm - the Navy states "in excess of 250"; 290
#     clears that floor and sits just under the 174B, which is the peer
#     relationship the reveal describes rather than a penalty for bay fit.
#     The old note here read "it has to fit inside an F-35 weapons bay" as if
#     that cost it reach. It does fit the bay, and it makes 250+ anyway.
#   DragCoefficient 3.6 vs 3.41 - same 34.3 cm body, 5% shorter, so slightly
#     blunter for its length.
#     THIS KEY MUST STAY EXPLICIT: at -1 the engine back-solves 8.14 from the
#     airframe and the missile loses roughly a third of its reach.
#   a two-stage motor, ~170 G.s against the 174B's ~144, paying for that drag.
#     Two-stage is now confirmed rather than assumed.
#   Power 48 vs 52 and CEP 10 m vs 6 - slightly less lethal endgame
#   SeekerActiveRange 40 nm vs 15, passive 80 nm vs 15, and a Full passive
#     anti-emitter mode against HomeOnJam - ESTIMATED, not disclosed. Justified
#     by the mission the Navy describes: a 250 nm shot at high-value emitters
#     (AEW, tankers, jammers) needs terminal reach and a passive mode, or the
#     target simply turns away inside the 174B's 15 nm seeker window.
#   MaxTurnRate 28 vs 30 deg/s, MaxTurnG 25 - still not an AIM-260 (40 deg/s)
AIM424_INI = """\
[General]
# Raytheon AIM-424 LRAAM "Malice" - revealed 22 Aug 2026, in flight test.
# 4.11 m long, 34.3 cm diameter (SM-6 body), 66.5 cm span, two-stage solid,
# blast-fragmentation warhead, range "in excess of 250 nm" per the Navy.
# Real platforms: F/A-18E/F, F-35C, F/A-XX, USAF F-47.
# Carried here by: usn_f-35c, raaf_f-35a, usaf_f-15ex_SEII, usn_f-18e/f/g,
# usaf_f-16cm, fr_rafale_m (SEST packs).
Type=Missile                           // can be Projectile, Missile, Torpedo
TargetType=AAW                         // can be AAW, ASuW, ASW
SecondaryTargetType=ASuW               // parity with the AIM-174B, which declares
                                       // the same - an SM-6-bodied round keeps the
                                       // family's secondary anti-surface mode
Mass=650                               // in kg. NOT disclosed - scaled from the
                                       // AIM-174B: same 34.3 cm body, 5% shorter
                                       // (4.11 m vs 4.33), so 705 x 4.11/4.33 =
                                       // 669, rounded down because this is a
                                       // purpose-built AAM and carries none of
                                       // the SM-6's shipboard marinisation.
                                       // Was 467, an AARGM-ER figure that the
                                       // real dimensions have now retired.
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
Power=48                                // cf. AIM-174B 52. Same 34.3 cm body but
                                        // shorter and two-stage so less of it is
                                        // warhead. Blast-fragmentation either way.
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
SecondaryPassiveRadarGuidanceType=Full // ESTIMATED. Homes on radars AND jammers,
                                       // not jammers alone - the counter-AEW and
                                       // counter-tanker mission the reveal describes
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
# RENDERING STAND-IN, not a design claim: no AIM-424 mesh exists in the
# collection, so this borrows the AGM-88G model US Naval Aviation (3737267013)
# ships. The real missile is a 34.3 cm two-stage round, not an AARGM-ER.
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
# This Scale is the HIT COLLIDER box, not the visual - every ammunition ini
# in the collection carries it under [col_main] and none has a model-size
# key. The visual renders at the shared usn_rim-7 mesh's native size, same
# as usn_agm-88g, and cannot be resized from the ini (ResourcesMeshScale,
# the one candidate key, breaks the model - see the note above [Models]).
# Keep the collider matched to usn_agm-88g's, whose visual this shares.
Scale=0.005,0.005,0.04291637
"""

# language_en/ammunition_names.ini format: stem=DisplayName,Nickname,Category,Description
# (the description must not contain commas — they are field separators).
AIM424_NAMES_INI = """\
[AmmunitionNames]
# ---------- SEST AIM-424 MALICE ----------
sest_aim-424=AIM-424,MALICE,AAM,The Raytheon AIM-424 LRAAM is a very-long-range air-to-air missile revealed by the US Navy in August 2026 and already in flight test. It is a two-stage solid-propellant round on the same 34.3 cm body as the SM-6 but shorter at 4.11 m - short enough to fit the F-35 internal weapons bay - and the Navy states a range in excess of 250 nautical miles. It is built to kill the high-value aircraft that make a carrier group's life difficult: AEW radars tankers and standoff jammers. Active-radar terminal homing with two-way datalink midcourse guidance is backed by a passive anti-emitter mode that homes on radars and jammers alike so a target that shuts down its radar does not break the engagement. A secondary anti-surface capability comes with the SM-6 lineage.
"""


def write_aim424(out_dir):
    """Write the ammunition ini + name entries into a pack folder (Path)."""
    ammo = out_dir / "ammunition"
    ammo.mkdir(parents=True, exist_ok=True)
    (ammo / f"{AIM424_ID}.ini").write_text(AIM424_INI, encoding="utf-8")
    lang = out_dir / "language_en"
    lang.mkdir(exist_ok=True)
    (lang / "ammunition_names.ini").write_text(AIM424_NAMES_INI, encoding="utf-8")
