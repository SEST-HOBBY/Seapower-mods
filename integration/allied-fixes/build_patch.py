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
Redback - an infrared fire-and-forget 70mm guided rocket, 30 nm, a boost \
then a cruise, air targets first and the surface second - as a SEST_REDBACK \
fit on the Apaches, the A-10s, the MQ-9s, \
the Seahawks and the RAAF Hornets.

[Compatibility]
ApproximateVersion=0.8.6
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
    #   - an infrared seeker, fire and forget (GuidanceType 1, MidCourse 0;
    #     five in-container precedents), reaching as far as it may be shot;
    #   - the boost is the APKWS's own; a sustainer then holds it on while
    #     VelocityBleed brings it down to about 600 kt for the cruise (stock's
    #     own pair: Seacat's SustainerAcceleration/Time, VelocityBleed on 85
    #     rounds).
    # Everything else is the APKWS's own: air first, ships and land second
    # (TargetType=AAW, SecondaryTargetType=ASuW), and its shallow climb (5
    # degrees to 1,500 ft) and terminal dive - the profile already proven to
    # fire from a pod without a freeze. The first cut of 19 Oct flew the
    # NSM's sea skimming under an anti-surface primary instead; no stock
    # round pairs that low flight with an air target, so against a drone it
    # would most likely have stayed low and passed underneath.
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
        (r"^GuidanceType=5\b", "GuidanceType=1"),
        (r"^SeekerPassiveRange=6\.0\b", "SeekerPassiveRange=30"),
        (r"^MaxLaunchRange=6\b", "MaxLaunchRange=30"),
        (r"^(MaxVelocity=)2000\b", r"\g<1>1500"),
        (r"^(Acceleration=200\b[^\n]*\n)",
         r"\g<1>SustainerAccelerationTime=170\nSustainerAcceleration=0.5\nVelocityBleed=0.4\n"),
        (r"^(InFlightEffectClass=[^\n]*\n)",
         r"\g<1>SustainerEffect=effects/weapons/emitters/missile_sustainer_small_effect\n"
         r"SustainerEffectPosition=0,0,-0.02\nSustainerEffectStartTime=1\n"),
    ]
    for pat, rep in swaps:
        rb, k = re.subn(pat, rep, rb, count=1, flags=re.M)
        if k != 1:
            sys.exit(f"dts_apkws-ii: {pat} matched {k} times - upstream changed")
    # The targeting and the climb and dive are kept as upstream wrote them;
    # the description promises them, so stop if they move.
    for key in (r"TargetType=AAW", r"SecondaryTargetType=ASuW", r"MaxLoftAngle=5\.0",
                r"MaxLoftAlt=1500", r"TerminalApproachDist=100", r"TerminalAlt=Maintain",
                r"TerminalDiveDistance=2"):
        if not re.search(rf"^{key}\b", rb, re.M):
            sys.exit(f"dts_apkws-ii: {key} changed upstream - re-check the Redback profile")
    (OUT / "ammunition").mkdir(parents=True, exist_ok=True)
    (OUT / "ammunition" / "sest_agr-30.ini").write_text(
        "# SEST AGR-30 Redback - dts_apkws-ii (proven in-pod, lofting) with an IR\n"
        "# seeker, 30 nm and a sustainer cruise after the boost.\n"
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
        "Redback replaces the APKWS II laser kit with an imaging-infrared "
        "seeker for fire and forget out to 30 nautical miles. A rocket boost, "
        "then a sustained cruise at about 600 knots in a shallow climb and a "
        "dive onto the target. Built from the counter-drone APKWS, it takes "
        "aircraft and drones first, ships and land targets second. Same "
        "airframe and warhead as the APKWS II.\n",
        encoding="utf-8")
    (lang / "loadout_names.ini").write_text(
        "[LoadoutNames]\nSEST_REDBACK=SEST Redback Strike (AGR-30 guided rockets)\n",
        encoding="utf-8")
    print("  Redback: sest_agr-30 (30 nm, boost + cruise, loft and dive, air first), "
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
        # Seahawks: one 19-tube pod a side, as the Navy's MH-60S carries its
        # APKWS. On the MH-60R it takes the Hellfire launcher's place (the
        # launcher is hidden; the pod was a pair on its rails), the inner
        # pair's missiles dropped, the torpedoes or tanks kept. The S-70B-2s
        # hang it on the torpedo pylons, where four 7-tube pods once stood
        # two by two on one Hellfire launcher's rails.
        ("3606774881", "usn_mh-60r.ini", "AntiShipLate",
         [("usa_agm-114l_mm", "pod19", 2, ""), ("usa_agm-114k_hh", None, 2)],
         dict(hide=("H60_Pylon114",))),
        ("3820759806", "ran_mh-60r.ini", "AntiShip",
         [("usa_agm-114l_mm", "pod19", 2, ""), ("usa_agm-114k_hh", None, 2)],
         dict(hide=("H60_Pylon114",))),
        ("3403661005", "S-70B-2_Seahawk.ini", "ASW", [("usn_mk46_air", "pod19", 2)]),
        ("3820759806", "ran_S-70B-2_Seahawk.ini", "ASW", [("usn_mk46_mod5_air", "pod19", 2)]),
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


if __name__ == "__main__":
    main()
