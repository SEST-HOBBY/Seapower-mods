"""Shared definition of the SEST AIM-424 MALICE.

NO LONGER A WHAT-IF. This file was written when the AIM-424 was a rumour and
modelled it as an invented derivative of the AGM-88G AARGM-ER. The U.S. Navy
revealed the real weapon at the Tailhook symposium on 22 August 2026, already
in flight test, and published enough to retire the guesswork:

    Raytheon AIM-424 LRAAM "Malice"
    length     13.5 ft   (4.11 m)
    diameter   13.5 in   (34.3 cm)   - the SM-6 / AIM-174B diameter
    wingspan   26.2 in   (66.5 cm)
    weight     1,500 lb  (680 kg)
    range      "in excess of 250 nautical miles" (463 km)
    motor      solid-propellant rocket; press coverage of the reveal reads
               the imagery as two-stage, which the Navy has not detailed
    warhead    blast-fragmentation
    platforms  F/A-18E/F, F-35C, F/A-XX
    fit        Navy imagery shows it inside an F-35C internal weapons bay

Sources: the U.S. Navy fact file "AIM-424 LRAAM - Malice" (navy.mil,
Resources > Fact Files, article 4580867, dated 22 August 2026) for length,
diameter, span, weight, range, motor and warhead; The Aviationist
(23 August 2026) and USNI News (24 August 2026) for the reveal, the two
stages and the F-35C bay imagery. The three AIM-424 rounds other mods in
the collection ship carry the same weight: usn_aim-424 in US Naval Aviation
(3737267013) and U.S. Navy 2027 (3606774881) at Mass=680, the YF-23 mod's
yf23_aim424_internal (3796349767) at 680.4.

Everything that was disclosed is used instead of the old AARGM-ER reasoning.
Seeker, speed and guidance were NOT disclosed.

THE FLIGHT MODEL IS U.S. NAVY 2027'S. On the player's decision of 13 Oct
2026 every AIM-424 in the collection flies one set of figures: U.S. Navy
2027's usn_aim-424 [Guidance], key for key (FLIGHT below). It is the round
usn_aim-424 resolves to in game, and of the mods' figures the most plausible
against the fact file (docs/conflicts-and-load-order.md, "Four AIM-424s").
This file's own [Guidance] is FLIGHT, and SEST Collection Fixes lays FLIGHT
over the YF-23 mod's yf23_aim424_internal with an #!extend. Until then this
round was aligned to U.S. Navy 2027's AIM-174B with deltas of its own (290
nm, a 4 s boost and 20 s sustainer, a 40 nm active / 80 nm passive seeker);
those are retired with it. The warhead, mass, signature and cost are not
flight and stay as they were.

THE 3D MODEL IS STILL AN AGM-88G, by choice. AIM-424 meshes do exist in the
collection: US Naval Aviation (3737267013) ships aim-424.obj for its own
usn_aim-424 (U.S. Navy 2027's usn_aim-424 points at the same asset), and the
YF-23 mod ships yf23_aim424. This round keeps the AGM-88G model block because
that block is proven to load - the last change to it made the missile fall
back to a RIM-7 stand-in (see the ResourcesMeshScale note below). Repointing
it at aim-424.obj wants an in-game look first. US Naval Aviation must stay
enabled either way, since it ships the AGM-88G assets too. This is a
rendering substitution only - it implies nothing about the airframe.

All six SEST packs that carry MALICE fits (F-15EX Revamp, F-16CM JATM,
F-35C JATM, RAAF F-35A JATM, Growler NGJ+MALICE, Rafale F5) write identical
copies of ammunition/sest_aim-424.ini and a partial
language_en/ammunition_names.ini - identical same-path files are a safe
overlap whichever pack sits higher in the Mod Manager.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

AIM424_ID = "sest_aim-424"

# REMOVED: ResourcesMeshScale. Shrinking the mesh by 0.9 was cosmetic, and the
# missile stopped rendering as an AARGM-ER afterwards - the model block falls
# back to AssetBundleMesh=usn_rim-7, a short fat Sea Sparrow, which is exactly
# what showed up under the wing. The [Models] block below is now byte-identical
# to US Naval Aviation's own usn_agm-88g, which is proven to load. Do not add
# keys to it that the source mod does not use.

# THE FLIGHT MODEL: U.S. Navy 2027's (3606774881) ammunition/usn_aim-424.ini,
# its [Guidance] key for key and in its order - guidance, flight profile,
# kinematics, launch envelope, seeker and ECCM. Its headline figures: 2,650
# knots; one 31 s burn at 4.7 g; a 45-degree loft to 147,638 ft; datalink
# midcourse with retargeting; 4-350 nm, 500 s flight; a 15 nm active and
# passive seeker that also homes on radars and jammers. 350 nm is above the
# Navy's "in excess of 250" - optimistic, not contradicted.
# check_flight() stops the build when that file stops reading exactly so:
# copy its new values here, and every AIM-424 follows.
USN2027 = ("3606774881", "ammunition/usn_aim-424.ini")
FLIGHT = (
    ("GuidanceType", "3"),
    ("MidCourseCorrection", "3"),
    ("DropDuration", "1.0"),
    ("InitialFlightPhaseDuration", "2.2"),
    ("Retargetable", "True"),
    ("MaxLoftAngle", "45.0"),
    ("MaxLoftAlt", "147638.0"),
    ("TerminalApproachDist", "14"),
    ("LocalTerminalOnly", "False"),
    ("IgnoreHeightDifferenceForTargetDist", "True"),
    ("ApplyKinematics", "True"),
    ("MaxVelocity", "2650.0"),
    ("MaxTurnRate", "30.0"),
    ("MaxTurnG", "35"),
    ("AccelerationTime", "31.0"),
    ("Acceleration", "4.711"),
    ("SustainerAccelerationTime", "65"),
    ("SustainerAcceleration", "0"),
    ("TypicalTargetAlt", "36000"),
    ("TypicalTargetSpeed", "0"),
    ("TypicalFiringAlt", "36000"),
    ("TypicalLaunchVelocity", "260"),
    ("DragCoefficient", "2.10"),
    ("VelocityBleed", "0.3"),
    ("MaxFlightTime", "500"),
    ("TerminalLoft", "False"),
    ("TimeLimited", "True"),
    ("LiftFactor", "0.005"),
    ("MinLaunchRange", "4"),
    ("MaxLaunchRange", "350"),
    ("MinAttackAltitude", "20"),
    ("MaxAttackAltitude", "147638"),
    ("MaxAttackVelocity", "4500"),
    ("MinLaunchAltitude", "200"),
    ("MaxLaunchAltitude", "65000"),
    ("LaunchReliability", "99"),
    ("CircularErrorRadius", "6.0"),
    ("CircularErrorRadiusLarge", "12.0"),
    ("MinAltMalusFactor", "0.7"),
    ("SeekerGain", "60.0"),
    ("SeekerFOV", "135.0"),
    ("SecondaryPassiveRadarGuidanceType", "Full"),
    ("PassiveRadarGuidanceFrequencies", "All"),
    ("SeekerActiveRange", "15"),
    ("SeekerPassiveRange", "15"),
    ("Frequency", "X-Band"),
    ("PeakPower", "15"),
    ("TargetMemory", "True"),
    ("RangeGate", "2"),
    ("SizeGate", "1.1"),
    ("CounterMeasuresRejection", "98"),
    ("NoiseRejection", "98"),
    ("AntiCountermeasuresBonus", "0.98"),
    ("AntiJammerBonus", "0.98"),
    ("SelfDestructAfterTargetGone", "False"),
)


def section(text, name):
    """{key: value} for the live lines of one [section] of an .ini text."""
    m = re.search(rf"^\[{re.escape(name)}\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    out = {}
    for line in (m.group(1) if m else "").splitlines():
        body = line.split("//", 1)[0].strip()
        if "=" in body and body[0] not in "#;":
            key, value = body.split("=", 1)
            out[key.strip()] = value.strip()
    return out


def guidance_block():
    """[Guidance], FLIGHT's keys and nothing else."""
    return "[Guidance]\n" + "".join(f"{k}={v}\n" for k, v in FLIGHT)


def usn2027_drift():
    """Where U.S. Navy 2027's [Guidance] no longer reads as FLIGHT; [] if it does."""
    mod, rel = USN2027
    path = ROOT / "mods-source" / mod / rel
    if not path.is_file():
        return [f"mods-source/{mod}/{rel} is gone"]
    have = section(path.read_text(encoding="utf-8-sig", errors="replace"), "Guidance")
    want = dict(FLIGHT)
    return ([f"{k}={have.get(k, '(not set)')} there, {v} here" for k, v in FLIGHT
             if have.get(k) != v]
            + [f"{k}={v} there, not set here" for k, v in have.items() if k not in want])


def check_flight():
    drift = usn2027_drift()
    if drift:
        sys.exit("AIM-424: U.S. Navy 2027's usn_aim-424 [Guidance] no longer reads as FLIGHT "
                 "in integration/common/aim424.py - copy its values there so every AIM-424 "
                 "flies them again:\n  " + "\n  ".join(drift))


AIM424_INI = (
    """\
[General]
# Raytheon AIM-424 LRAAM "Malice" - revealed 22 Aug 2026, in flight test.
# 4.11 m long, 34.3 cm diameter (as the SM-6), 66.5 cm span, 680 kg, solid
# rocket, blast-fragmentation warhead, range "in excess of 250 nm" - all per
# the U.S. Navy fact file. Real platforms: F/A-18E/F, F-35C, F/A-XX.
# Carried here by: usn_f-35c, raaf_f-35a, usaf_f-15ex_SEII, usn_fa-18e/f,
# usn_fa-18f_blk3, usn_ea-18g(_2020), usaf_f-16cm-bl52d, fr_rafale_b/c/m_l
# (SEST packs).
Type=Missile                           // can be Projectile, Missile, Torpedo
TargetType=AAW                         // can be AAW, ASuW, ASW
SecondaryTargetType=ASuW               // parity with the AIM-174B, which declares
                                       // the same; not a disclosed capability
Mass=680                               // in kg. 1,500 lb per the U.S. Navy fact
                                       // file "AIM-424 LRAAM - Malice"
                                       // (navy.mil, 22 Aug 2026). Matches
                                       // usn_aim-424 in US Naval Aviation and
                                       // U.S. Navy 2027 (680). Was 467, an
                                       // AARGM-ER figure the published weight
                                       // has now retired.
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
Power=48                                // cf. AIM-174B 52. Same 34.3 cm diameter
                                        // on a shorter round, so less room for
                                        // warhead. ESTIMATED: the Navy gives the
                                        // type (blast-fragmentation), not the size.
ImpactSize=Medium                       // Impact size, can be small, medium, large, verylarge
Penetration=Always                      // can be minor, moderate, heavy, always
FuzeProximityDistance=18.0              // for proximity fuze: distance to target in meters
KillProbability=0.98                    // cf. AIM-174B 1.02
InterceptOutOfAltitudePenalty=0.15
InterceptSpeedPenaltyMultiplier=0.4

# Guidance, flight profile, kinematics, envelope, seeker and ECCM: U.S.
# Navy 2027's usn_aim-424, key for key (FLIGHT in integration/common/aim424.py).
"""
    + guidance_block()
    + """\

[---------- Mesh definitions----------]
[Models]
AssetBundleMeshes=/AssetBundles/StandaloneWindows/aircraft
AssetBundleMaterials=/AssetBundles/StandaloneWindows/aircraft
AssetBundleMesh=usn_rim-7
AssetBundleDamagedMesh=
AssetBundleMaterial=usn_rim-7_mat
AssetBundleMeshHullCollider=usn_rim-7_coll
# RENDERING STAND-IN, not a design claim: the AGM-88G model US Naval
# Aviation (3737267013) ships, kept because it is proven to load. That mod
# also ships an aim-424.obj (its usn_aim-424); switching to it is untested.
# The real missile is a 34.3 cm, 680 kg round, not an AARGM-ER.
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
)

# language_en/ammunition_names.ini format: stem=DisplayName,Nickname,Category,Description
# (the description must not contain commas — they are field separators).
AIM424_NAMES_INI = """\
[AmmunitionNames]
# ---------- SEST AIM-424 MALICE ----------
sest_aim-424=AIM-424,MALICE,AAM,The Raytheon AIM-424 LRAAM is a very-long-range air-to-air missile revealed by the US Navy in August 2026 and already in flight test. It is a 680 kg solid-propellant round 4.11 m long on the same 34.3 cm diameter as the SM-6 - short enough to fit the F-35C internal weapons bay - and the Navy states a range in excess of 250 nautical miles. It pushes the carrier air wing's reach out to the high-value aircraft behind an attack: airborne early-warning radars and tankers and standoff jammers. Active-radar terminal homing with two-way datalink midcourse guidance is backed by a passive anti-emitter mode that homes on radars and jammers alike so a target that shuts down its radar does not break the engagement. Like the AIM-174B it keeps a secondary anti-surface mode.
"""


def write_aim424(out_dir):
    """Write the ammunition ini + name entries into a pack folder (Path)."""
    check_flight()
    ammo = out_dir / "ammunition"
    ammo.mkdir(parents=True, exist_ok=True)
    (ammo / f"{AIM424_ID}.ini").write_text(AIM424_INI, encoding="utf-8")
    lang = out_dir / "language_en"
    lang.mkdir(exist_ok=True)
    (lang / "ammunition_names.ini").write_text(AIM424_NAMES_INI, encoding="utf-8")
