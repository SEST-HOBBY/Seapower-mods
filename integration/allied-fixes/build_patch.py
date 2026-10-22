#!/usr/bin/env python3
"""Build the SEST Allied Fixes patch: the P-8 Poseidon's anti-ship loadout.

usn_p8_2027 declares AvailableLoadouts=ASW,AntiShip - two options - and the
AntiShip one hangs four rounds of usn_agm-84g on WeaponSystem2. Nothing in the
collection defines usn_agm-84g. Not U.S. Navy 2027, which ships the aircraft;
not any of the other 128 mods; not vanilla. There is no real AGM-84G either.
So the Poseidon's only anti-ship fit puts nothing on the wings, and half of
what a maritime patrol aircraft is for quietly does not work.

It is a typo, and the mod answers it itself: U.S. Navy 2027 writes usn_agm-84n
nineteen times and usn_agm-84g four times, and all four are these station
lines. usn_agm-84n is its own Harpoon Block II+ ER - 522 kg, 150 nm - already
carried by its ships and its Super Hornets.

usn_p8 from mod 3602046770 has the identical four-line typo and the identical
ASW,AntiShip pair, so it gets the same substitution.

UPDATE, 2026-09-20 export: U.S. Navy 2027 fixed its own copy - usn_p8_2027
now writes Station1..4=usn_agm-84n, which is precisely what this patch was
substituting. That target is retired (see RETIRED); 3602046770's usn_p8 still
carries the typo four times and is still patched.

Not included, having checked each one:
  - usn_e-2d, fr_e2c, fr_e2d, usn_ch-46d, usaf_ac-130a_83, jmsdf_kv_107*
    all declare a loadout with no matching block, but every one of them is an
    unarmed aircraft whose blocks carry zero stores. The picker entry is
    cosmetic and an override would add a dependency for no gameplay change.
  - usn_p-3d is missing only its Recon block; ASW, AntiShip and Empty all
    work, and nothing fields it.
  - rn_merlin_hm1 and the two Lynxes look like they reference undefined
    DateBased_* stores. They do not - DateBased_ is a vanilla mechanic, used
    by stock submarines like usn_ssn_permit.

Usage (repo root):  python3 integration/allied-fixes/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "SEST_Allied_Fixes"

sys.path.insert(0, str(ROOT / "integration"))
from common.a10c import fix_squadron_count, register_ir_head  # noqa: E402
from common.ras import make_reloadable  # noqa: E402
from common.redback import add_fit as add_redback  # noqa: E402

MISSING = "usn_agm-84g"      # defined by nothing, anywhere
REPLACE = "usn_agm-84n"      # U.S. Navy 2027's own Harpoon Block II+ ER

# (workshop id, aircraft file)
TARGETS = [
    ("3602046770", "usn_p8.ini"),        # still carries the typo, 4x
]

# Targets retired because upstream adopted the fix. Checked in the 2026-09-20
# export: U.S. Navy 2027's usn_p8_2027 AntiShip block now reads
# Station1..4=usn_agm-84n - the exact substitution this patch was making - so
# shipping a copy of that file would add an override that changes nothing and
# a dependency for no reason. The file is unlinked below so a pack folder
# built before the retirement does not keep serving a stale copy.
RETIRED = [("3606774881", "usn_p8_2027.ini", "upstream now writes usn_agm-84n itself")]

INFO_INI = """\
[Language_en]
Name=SEST Allied Fixes
Description=Small allied corrections: the P-8's anti-ship fit pointed at a \
Harpoon no mod defines (loaded empty), HMS Ocean could not operate the \
Apache AH1 her sister hulls already support, the RNZAF and ROKN P-8 \
squadrons named nations the game has no flag for, and the A-10C's infrared \
head was never registered as a sensor module while its squadron file \
declared seven squadrons against two defined liveries. Also SEST's AGR-30 \
Redback - a fictional active-homing 70mm guided rocket, 30 nm, a ten-second \
boost, slow cruise and diving approach, with radio retargeting - as a SEST_REDBACK \
fit on the Apaches, the A-10s, the MQ-9s, \
the Seahawks and the RAAF Hornets.

[Compatibility]
ApproximateVersion=0.8.7
"""


def main():
    if not (ROOT / "mods-source" / "3606774881" / "ammunition" / f"{REPLACE}.ini").exists():
        sys.exit(f"{REPLACE} not found - U.S. Navy 2027 must be exported first")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print("SEST_Allied_Fixes")

    for _mod, name, why in RETIRED:
        stale = OUT / "aircraft" / name
        if stale.exists():
            stale.unlink()
            print(f"    removed aircraft/{name} - {why}")

    built = 0
    for mod, name in TARGETS:
        src = ROOT / "mods-source" / mod / "aircraft" / name
        dst = OUT / "aircraft" / name
        if not src.exists():
            if dst.exists():
                dst.unlink()
                print(f"    removed stale aircraft/{name} (upstream no longer exported)")
            print(f"  {name}  SKIPPED - {mod} not exported")
            continue
        text = src.read_text(encoding="utf-8-sig")
        n = len(re.findall(rf"^Station\d+={re.escape(MISSING)}\s*$", text, re.M))
        if not n:
            sys.exit(f"{name}: no {MISSING} station lines left - upstream fixed it, "
                     f"drop this target")
        out = re.sub(rf"^(Station\d+=){re.escape(MISSING)}(\s*)$", rf"\g<1>{REPLACE}\g<2>",
                     text, flags=re.M)
        if MISSING in out:
            sys.exit(f"{name}: {MISSING} still present after substitution")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out, encoding="utf-8")
        print(f"  aircraft/{name}  ({n}x {MISSING} -> {REPLACE})")
        built += 1

    # The P-8's squadron flags. 3602046770 writes Nation=New Zealand for its
    # No. 5 Squadron RNZAF livery and Nation=South Korea for its ROKN one,
    # but the game's nation keys have no spaces (language_en/nations.ini:
    # NewZealand, South_Korea; Settings_UI_General.ini maps those keys to the
    # flag art). An unknown key shows no flag, which is what the RNZAF
    # Poseidons of the Southern Reach campaign did. Only the Nation= values
    # change; every livery, serial and emblem line is upstream's.
    sq_src = ROOT / "mods-source" / "3602046770" / "aircraft" / "usn_p8_squadrons.ini"
    sq_dst = OUT / "aircraft" / "usn_p8_squadrons.ini"
    nations_ini = ROOT / "mods-source" / "_vanilla" / "original" / "language_en" / "nations.ini"
    if not sq_src.exists():
        if sq_dst.exists():
            sq_dst.unlink()
            print("    removed stale aircraft/usn_p8_squadrons.ini (upstream gone)")
        print("  usn_p8_squadrons.ini  SKIPPED - P-8 mod not exported")
    else:
        game_keys = {l.split("=", 1)[0].strip().lower()
                     for l in nations_ini.read_text(encoding="utf-8-sig").splitlines()
                     if "=" in l}
        spelled = {"new zealand": "NewZealand", "south korea": "South_Korea"}
        text = sq_src.read_text(encoding="utf-8-sig")
        fixed = []

        def respell(m):
            value = m.group(2).strip()
            key = spelled.get(value.lower())
            if key:
                fixed.append(f"{value} -> {key}")
                return f"{m.group(1)}{key}{m.group(3)}"
            return m.group(0)

        text = re.sub(r"^(Nation=)([^\r\n/#;]*?)(\s*(?://.*|#.*|;.*)?)$", respell, text, flags=re.M)
        left = [v for v in re.findall(r"^Nation=([^\r\n/#;]*)", text, re.M)
                if v.strip().lower() not in game_keys]
        if left:
            sys.exit(f"usn_p8_squadrons.ini: nation(s) the game has no key for: {left}")
        if not fixed:
            sys.exit("usn_p8_squadrons.ini: every Nation= is already a game key - "
                     "upstream fixed it, drop this patch")
        sq_dst.parent.mkdir(parents=True, exist_ok=True)
        sq_dst.write_text(text, encoding="utf-8")
        print(f"  aircraft/usn_p8_squadrons.ini  ({'; '.join(fixed)})")

    # HMS Ocean vs the Apache: her own sister hulls in the same mod
    # (rn_lph_ocean_asw_00 and _asw_13) already list uk_ah_mk_1 - the British
    # Army Apache AH1 that really flew from Ocean off Libya in 2011 - but the
    # base rn_lph_ocean only ever got the Lynx. One appended id fixes it.
    src = ROOT / "mods-source" / "3599752717" / "vessels" / "rn_lph_ocean.ini"
    dst = OUT / "vessels" / "rn_lph_ocean.ini"
    if not src.exists():
        if dst.exists():
            dst.unlink()
            print("    removed stale vessels/rn_lph_ocean.ini (upstream gone)")
        print("  rn_lph_ocean.ini  SKIPPED - Modern British Navy not exported")
    else:
        text = src.read_text(encoding="utf-8-sig")
        if "uk_ah_mk_1" in text:
            sys.exit("rn_lph_ocean.ini: upstream now supports the Apache - drop this fix")
        # APPEND to whatever the line holds rather than matching an expected
        # value: the 2026-09-20 export added rn_sea_king_hc4 to it, which an
        # exact match read as "upstream changed, stop". The fix is still
        # needed (no uk_ah_mk_1 anywhere in the file), so the patch now adds
        # the Apache to the list as it finds it and prints what it appended to.
        lines = re.findall(r"^AircraftSupported=([^\n]*?)\s*$", text, re.M)
        if len(lines) != 1:
            sys.exit(f"rn_lph_ocean.ini: expected 1 AircraftSupported line, found {len(lines)}")
        had = lines[0]
        text, n = re.subn(r"^AircraftSupported=[^\n]*?\s*$",
                          f"AircraftSupported={had},uk_ah_mk_1", text, flags=re.M)
        if n != 1:
            sys.exit(f"rn_lph_ocean.ini: AircraftSupported substitution hit {n} lines")
        # SEST Replenishment At Sea owns the launcher fix for every modern hull,
        # but it cannot touch this one - THIS pack ships rn_lph_ocean.ini, and
        # two packs shipping different bytes at one path is an unconditional
        # consolidation failure. So the transform is imported and applied here.
        text, reloadable = make_reloadable(text)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        print(f"  vessels/rn_lph_ocean.ini  (+uk_ah_mk_1 Apache AH1 supported, "
              f"{reloadable} launcher(s) made reloadable for RAS)")

    # AGR-30 Redback: SEST's one upgraded 70mm guided rocket. The decision of
    # 19 Oct 2026 retired the 8 nm laser APKWS II-ER (its rocket, its pod and
    # the Ocean Apache's SEST_APKWS_ER fit) and asked for this one round,
    # everywhere: 30 nm and a rocket's boost then a slower cruise. It stays
    # dts_apkws-ii - the proven in-pod rocket it was rebased onto after two
    # freezes, the weapon pack's counter-drone APKWS - with the minimum deltas:
    # The second 19 Oct request extends the visible motor to ten seconds and
    # asks for gentler slowdown, an approximately 45-degree final descent and
    # some terminal speed pickup. Legacy phase caps keep the fictional slow
    # cruise without modelling an unpowered 70mm rocket's real-world stall.
    # AS-4 demonstrates TerminalVelocity and Deceleration; the latter's
    # 0.8 factor is gentler than the documented legacy default of 3.0.
    # A 6562-ft loft over 1.1 horizontal NM gives about 44.5 degrees to a
    # sea-level target. IgnoreHeightDifferenceForTargetDist is essential to
    # that geometry. This is not a verified fixed-pitch control: terrain,
    # target height, short shots and target motion change the approach.
    # AIM-54A's timed SustainerEffect supplies the ten-second visible motor,
    # without an everlasting InFlightEffect or a new flame in terminal.
    # The active seeker and command link use stock missile keys; Walleye II
    # demonstrates Retargetable with MidCourseCorrection=1. These settings
    # require a new in-game test; they do not prove hits or terrain clearance.
    for stale in ("sest_apkws_er.ini", "sest_agr-20er.ini"):
        if (OUT / "ammunition" / stale).exists():
            (OUT / "ammunition" / stale).unlink()
            print(f"    removed ammunition/{stale} - the APKWS II-ER is retired")
    rb_src = ROOT / "mods-source" / "3760871384" / "ammunition" / "dts_apkws-ii.ini"
    pod_src = ROOT / "mods-source" / "3425450153" / "ammunition" / "usn_agr-20b_apache.ini"
    for need in (rb_src, pod_src):
        if not need.exists():
            sys.exit(f"{need.relative_to(ROOT)} missing - export it first")
    rb = rb_src.read_text(encoding="utf-8-sig", errors="replace")
    swaps = [
        # Surface attack is the primary AI job; retain counter-drone eligibility.
        # The laser donor had no active-radar transmitter or target-height band.
        (r"^TargetType=AAW[^\n]*", "TargetType=ASuW"),
        (r"^SecondaryTargetType=ASuW[^\n]*", "SecondaryTargetType=AAW"),
        (r"^GuidanceType=5\b", "GuidanceType=3"),
        (r"^MidCourseCorrection=0[^\n]*", "MidCourseCorrection=1  // radio command; autonomous seeker in terminal"),
        (r"^SeekerPassiveRange=6\.0[^\n]*", "SeekerPassiveRange=0\nSeekerActiveRange=35\nSeekerGain=50\nFrequency=Ka-Band\nPeakPower=11.0\nMinAttackAltitude=0\nMaxAttackAltitude=20000\nSeekerReliability=0.99\nTargetMemory=True\nRetargetable=True\nSelfDestructAfterTargetGone=False"),
        (r"^MaxLaunchRange=6\b", "MaxLaunchRange=30"),
        (r"^MaxLoftAngle=5\.0[^\n]*", "MaxLoftAngle=35.0"),
        (r"^MaxLoftAlt=1500[^\n]*", "MaxLoftAlt=6562  // feet: approximately 2 km\nMaxLoftVelocity=450"),
        (r"^TerminalApproachDist=100[^\n]*", "TerminalApproachDist=2.0"),
        (r"^TerminalDiveDistance=2[^\n]*", "TerminalDiveDistance=1.1\nTerminalVelocity=220  // legacy terminal phase target, knots\nIgnoreHeightDifferenceForTargetDist=True"),
        (r"^MaxVelocity=2000[^\n]*", "MaxVelocity=150  // legacy cruise phase cap, knots\nApplyKinematics=False\nMaxFlightTime=1500\nTimeLimited=True"),
        (r"^AccelerationTime=1[^\n]*", "AccelerationTime=0.01"),
        (r"^Acceleration=200[^\n]*", "Acceleration=2.0\nDeceleration=0.8\nSustainerAccelerationTime=10\nSustainerAcceleration=8"),
        (r"^MaxTurnRate=50\.0[^\n]*", "MaxTurnRate=20.0  // soften the nose-over while retaining target correction"),
        (r"^KillProbability=0\.6\b", "KillProbability=0.95"),
        (r"^SeekerFOV=15\b", "SeekerFOV=60"),
        (r"^SeekerGimbalFOV=90\b", "SeekerGimbalFOV=120"),
        (r"^BoosterEffect=[^\n]*\nBoosterEffectPosition=[^\n]*\n", ""),
        (r"^InFlightEffectClass=[^\n]*\nInFlightEffectPosition=[^\n]*\nInFlightEffectStartTime=[^\n]*",
         "SustainerEffect=effects/weapons/emitters/missile_sustainer_small_effect\n"
         "SustainerEffectPosition=0,0,-0.02\nSustainerEffectStartTime=0"),
    ]
    for pat, rep in swaps:
        rb, k = re.subn(pat, rep, rb, count=1, flags=re.M)
        if k != 1:
            sys.exit(f"dts_apkws-ii: {pat} matched {k} times - upstream changed")
    # Preserve the donor's target classes, including mobile land targets.
    for key in (r"TargetType=ASuW", r"SecondaryTargetType=AAW",
                r"LandAttackCapability=All", r"TerminalAlt=Maintain"):
        if not re.search(rf"^{key}\b", rb, re.M):
            sys.exit(f"dts_apkws-ii: {key} changed upstream - re-check the Redback profile")
    (OUT / "ammunition").mkdir(parents=True, exist_ok=True)
    (OUT / "ammunition" / "sest_agr-30.ini").write_text(
        "# SEST AGR-30 Redback - fictional 30 nm guided rocket.\n"
        "# Ten-second motor / 450 kt loft cap / 150 kt cruise / 220 kt terminal target.\n"
        "# 2 km loft and 1.1 horizontal NM dive start approximate a 45-degree surface attack.\n"
        "# Active terminal seeker, radio midcourse and retargeting. Playtest required.\n"
        + rb, encoding="utf-8")
    rbpod, k = re.subn(r"^Ammunition=usa_apkws_2_m282\s*$", "Ammunition=sest_agr-30",
                       pod_src.read_text(encoding="utf-8-sig", errors="replace"), flags=re.M)
    if k != 1:
        sys.exit("usn_agr-20b_apache: Ammunition line changed upstream (Redback pod)")
    (OUT / "ammunition" / "sest_agr-30_pod.ini").write_text(
        "# SEST LAU-68 pod loaded with the AGR-30 Redback.\n" + rbpod, encoding="utf-8")
    # The 19-tube pod, for a single pylon: the game's own LAU-3/A (its model
    # ships with the game, so the pod needs no mod) with the Redback in place
    # of the Hydra, and a salvo of two like the 7-tube pod's - eight was for
    # unguided rockets spread over an area. The Euromod RAN mod's
    # usn_lau-3a_APKWS already flies 19 guided rockets from this pod.
    lau3 = (ROOT / "mods-source" / "_vanilla" / "original" / "ammunition"
            / "usn_lau-3a.ini").read_text(encoding="utf-8-sig", errors="replace")
    for pat, rep in ((r"^Ammunition=usn_hydra\b", "Ammunition=sest_agr-30"),
                     (r"^SalvoFireAmount=8\b", "SalvoFireAmount=2")):
        lau3, k = re.subn(pat, rep, lau3, count=1, flags=re.M)
        if k != 1:
            sys.exit(f"usn_lau-3a: {pat} matched {k} times - the game changed the pod")
    (OUT / "ammunition" / "sest_agr-30_pod19.ini").write_text(
        "# SEST LAU-3/A pod loaded with 19 AGR-30 Redbacks, a salvo of two.\n" + lau3,
        encoding="utf-8")

    lang = OUT / "language_en"
    lang.mkdir(parents=True, exist_ok=True)
    (lang / "ammunition_names.ini").write_text(
        "[AmmunitionNames]\n"
        "sest_agr-30=AGR-30,Redback,GFFAR,"
        "What-if evolution of the 70mm guided rocket family: the AGR-30 "
        "Redback adds active terminal homing and radio midcourse retargeting "
        "out to 30 nautical miles. A ten-second motor and loft to approximately "
        "2 km precede a gradual slowdown toward 150 knots. The final descent "
        "is tuned for roughly 45 degrees against surface targets, with a "
        "220-knot terminal speed target. This is an experimental game profile. "
        "Eligible against aircraft, drones, ships and land targets. Its slow "
        "cruise is intended for surface targets and slow aircraft. Same "
        "airframe and warhead as the APKWS II.\n",
        encoding="utf-8")
    (lang / "loadout_names.ini").write_text(
        "[LoadoutNames]\nSEST_REDBACK=SEST Redback Strike (AGR-30 guided rockets)\n",
        encoding="utf-8")
    print("  Redback: sest_agr-30 (30 nm, boost + cruise, loft and dive, surface first), "
          "its LAU-68 and LAU-3 pods")

    # The fit, on every carrier whose file this pack ships. Each clones a fit
    # it already flies and puts Redback pods on the pylons named (common/
    # redback.py). The A-10C+, F-16CM and US Super Hornets are other SEST
    # packs' files and get the same fit from their own builders. The 19-tube
    # pod goes on a single pylon, on the airframe's own mount for a store its
    # size; the 7-tube stays where a rack hangs several (the A-10's TERs, the
    # Hornets' twin mounts) and on the MQ-9's light pylons.
    ROLLOUT = [
        # Apaches: four 19-tube pods on the mod's own LAU-3 mount, as its
        # Default fit hangs them.
        ("3425450153", "uk_ah_mk_1.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3425450153", "usa_ah-64a.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3425450153", "usa_ah-64d.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3425450153", "usa_ah-64e.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3425450153", "usn_ah-64na.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3820759806", "adf_ah-64e.ini", "StrikePrecision",
         [("usn_agr-20b_apache", "pod19", 2, "LAU-3"), ("usn_lau-3a_APKWS", "pod19", 2)]),
        # A-10s: a 19-tube pod on each single outer pylon, on the 2,000 lb
        # bomb's mount (the files write MK-82's twice, the second about 20 m
        # below the wing); the TERs keep three or two 7-tube pods on their
        # own points.
        ("3459682829", "usa_a-10c.ini", "CAS1",
         [("usn_agr-20b", "pod19", 1, "MK-84", (3,)), ("usn_agr-20b", "pod", 4)]),
        ("3414146266", "usa_a-10a.ini", "CAS",
         [("usn_lau-68", "pod19", 2, "MK-84", (3, 4)), ("usn_lau-68", "pod", 2)]),
        ("3503670861", "usaf_mq-9a.ini", "Strike",
         [("uav_agm-114k", "pod", 2), ("uav_gbu-49", "pod", 2)]),
        ("3503670861", "usaf_mq-9_er.ini", "Strike",
         [("uav_agm-114k", "pod", 2), ("uav_gbu-49", "pod", 2)]),
        # Keep the Seahawk's actual supporting geometry visible. The MH-60R
        # pods use the lower Hellfire seats and retain H60_Pylon114; hiding
        # that submodel removed their support. The S-70B-2 has one modelled
        # missile arm: use its Penguin seat, not a floating pod each side on
        # the torpedo-specific MK46 offsets. Its AntiShip fit keeps the arm.
        ("3606774881", "usn_mh-60r.ini", "AntiShipLate",
         [("usa_agm-114l_mm", None, 2), ("usa_agm-114k_hh", "pod19", 2, "")]),
        ("3820759806", "ran_mh-60r.ini", "AntiShip",
         [("usa_agm-114l_mm", None, 2), ("usa_agm-114k_hh", "pod19", 2, "")]),
        ("3403661005", "S-70B-2_Seahawk.ini", "AntiShip", [("knm_penguin_mk2", "pod19", 1)]),
        ("3820759806", "ran_S-70B-2_Seahawk.ini", "AntiShip", [("knm_penguin_mk2", "pod19", 1)]),
        # RAAF Hornets. The F/A-18A's CAS fit already flies the layout: wing
        # tanks, and two 7-tube pods on the pylon outboard of them (the twin
        # Zuni mount). The F/A-18F takes it from its long-range anti-ship
        # fit, whose wing and centreline tanks stay: two 7-tube pods on the
        # mid pylon (a twin mount at the A's spacing, which SEST adds), and a
        # 19-tube pod on the outboard pylon, on the bombs' outer mount.
        ("3820759806", "raaf_fa-18f.ini", "AntishipLongRange",
         [("usn_aim-9x", "pod19", 2, "GBU24A", (3, 4)), ("DateBased_AShM", "pod", 2, "RedbackTwin")],
         dict(positions={"RedbackTwin": "-0.004146,-0.001,0|0.004146,-0.001,0"})),
        ("3820759806", "raaf_fa-18a_2011.ini", "CAS", [("usn_lau-10a", "pod", 2)]),
    ]
    for mod, fname, donor, pylons, *opts in ROLLOUT:
        csrc = ROOT / "mods-source" / mod / "aircraft" / fname
        cdst = OUT / "aircraft" / fname
        if not csrc.exists():
            if cdst.exists():
                cdst.unlink()
            if fname == "usa_a-10c.ini":
                stale_sq = cdst.parent / "usa_a-10c_squadrons.ini"
                if stale_sq.exists():
                    stale_sq.unlink()
            print(f"  {fname}  SKIPPED - {mod} not exported")
            continue
        ct = csrc.read_text(encoding="utf-8-sig", errors="replace")
        extra = ""
        if fname == "uk_ah_mk_1.ini":
            # Upstream's Default fit names Station3 and Station4 twice - a
            # LAU-3 rocket pod AND a Brimstone on each inner pylon - so the
            # encyclopedia and the default loadout draw the pod and the
            # missiles on top of each other. Every other fit puts the rocket
            # pods on the outer pylons (Stations 1/2), and this one already
            # hides the outer missile rails for them, so the pods move there.
            ct, k = re.subn(r"(\[WeaponSystem1Default\][^\[]*?)"
                            r"^Station3=usa_lau-3a_apache\|LAU-3\n^Station4=usa_lau-3a_apache\|LAU-3\n",
                            r"\1Station1=usa_lau-3a_apache|LAU-3\nStation2=usa_lau-3a_apache|LAU-3\n",
                            ct, count=1, flags=re.M | re.S)
            if k != 1:
                sys.exit("uk_ah_mk_1: Default fit's doubled inner-pylon rocket pods not found - "
                         "upstream changed, re-check the overlap fix")
            extra = ", Default fit's doubled pods moved outboard"
        ct = add_redback(ct, fname, donor, pylons, **(opts[0] if opts else {}))
        if fname == "usa_a-10c.ini":
            # Two defects in the standard aircraft, repaired here because
            # this pack already ships the file. They are bugs, not the
            # upgrade: SEST A-10C+ carries the added sensors and AIM-9X on
            # a separate unit id, and applies these same two repairs from
            # integration/common/a10c.py so the pair cannot drift.
            ct = register_ir_head(ct, fname)
            sqsrc = ROOT / "mods-source" / mod / "aircraft" / "usa_a-10c_squadrons.ini"
            sq, was, defined = fix_squadron_count(
                sqsrc.read_text(encoding="utf-8-sig", errors="replace"), sqsrc.name)
            (cdst.parent / sqsrc.name).parent.mkdir(parents=True, exist_ok=True)
            (cdst.parent / sqsrc.name).write_text(sq, encoding="utf-8")
            extra = f", IR head registered, squadrons {was}->{defined}"
        cdst.parent.mkdir(parents=True, exist_ok=True)
        cdst.write_text(ct, encoding="utf-8")
        print(f"  aircraft/{fname}  SEST_REDBACK (donor {donor}){extra}")
        built += 1

    if not built:
        sys.exit("nothing built - no target mod is exported")
    # Use the collection's actual field-drone squad geometry and its tested
    # catapult/recovery positions, not a runway and hangars on hostile ground.
    # Keep only one fixed-wing lane and RQ-7 inventory. The donor also carries
    # unrelated one-way attack drones, a GPS sensor 3.5 km above its model and
    # an orphan third hit zone; none belongs in this reconnaissance section.
    drone_source = ROOT / "mods-source/3601891050/land_units/dronesquad705_1.ini"
    team = drone_source.read_text(encoding="utf-8-sig")
    edits = {
        "General": {"DisplayClassName": "RQ-7 field detachment", "DefaultCameraDistance": "0.15",
                    "MinCameraDistanceForeAft": "0.08", "MinCameraDistanceBroadside": "0.08"},
        "AirGroup": {"usn_rq7705": "Squadron1,2"},
        "FlightDeck": {"AircraftCapacity": "3", "NumberOfElevators": "1",
                       "NumberOfLaunchPoints": "1", "NumberOfRecoveryPoints": "1",
                       "NumberOfTaxiPaths": "2", "AircraftSupported": "usn_rq7705"},
        "SensorSystems": {"NumberOfSensorSystems": "1"},
        "SensorSystem1": {"MountPosition": "0,0.02,0"},
        "WeaponSystems": {"NumberOfWeaponSystems": "0"},
        "TargetingData": {"NumberOfTargetPoints": "2",
                          "TargetPointPosition1": "0,0.017,-0.0023",
                          "TargetPointPosition2": "0,0.003,-0.0023"},
    }
    drop = {"SensorSystem2", "WeaponSystem1", "WeaponMagazineMissile",
            "Elevator2", "LaunchPoint2", "RecoveryPoint2", "TaxiPath3", "TaxiPath4"}
    chunks = []
    for chunk in re.split(r"(?=^\[)", team, flags=re.M):
        match = re.match(r"^\[([^]\n]+)\]", chunk)
        section = match[1] if match else ""
        if section in drop:
            continue
        if section == "AirGroup":
            chunk = "[AirGroup]\n"
        if section == "Submodels":
            chunk = "[Submodels]\nSubModel1=net\n\n"
        for key, value in edits.get(section, {}).items():
            pattern = rf"^{re.escape(key)}=[^\n]*$"
            if re.search(pattern, chunk, re.M):
                chunk = re.sub(pattern, f"{key}={value}", chunk, flags=re.M)
            else:
                chunk = chunk.rstrip() + f"\n{key}={value}\n"
        if section == "TargetingData":
            chunk = re.sub(r"^TargetPoint(?:Position|AssociatedSystems|Priority)3=[^\n]*\n?", "", chunk, flags=re.M)
        chunks.append(chunk)
    (OUT / "land_units").mkdir(parents=True, exist_ok=True)
    team = ("# SEST RQ-7 field team. Model and launch/recovery layout from\n"
            "# FallschimJager705, Small and Medium-Sized UAV Series (3601891050).\n"
            "# Uses the subscribed mod's dronesquad assets; no mesh is redistributed.\n"
            + "".join(chunks))
    (OUT / "land_units/sest_uav_forward.ini").write_text(team, encoding="utf-8")
    # The new unit id needs its own companion variants file for the native
    # class/variant lookup. Do not inherit the donor's national air groups.
    # Missions supply their nation and two-aircraft custom air group.
    (OUT / "land_units/sest_uav_forward_variants.ini").write_text(
        "[General]\nAllVariantsAreOfSameNation=True\nNumberOfVariants=1\n\n"
        "[Default]\nNation=Australia\n\n[Variant1]\nNation=Australia\n",
        encoding="utf-8")
    (OUT / "language_en/land_units_names.ini").write_text(
        "[sest_uav_forward]\nType=RQ-7 field detachment\n"
        "Default=Forward UAV team,UAV team\n"
        "Variant1=Forward UAV team,UAV team\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
