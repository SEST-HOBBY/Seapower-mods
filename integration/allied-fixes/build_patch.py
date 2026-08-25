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

MISSING = "usn_agm-84g"      # defined by nothing, anywhere
REPLACE = "usn_agm-84n"      # U.S. Navy 2027's own Harpoon Block II+ ER

# (workshop id, aircraft file)
TARGETS = [
    ("3606774881", "usn_p8_2027.ini"),   # U.S. Navy 2027 - fielded in NFIII FINAL
    ("3602046770", "usn_p8.ini"),        # same typo, same fix
]

INFO_INI = """\
[Language_en]
Name=SEST Allied Fixes
Description=Small allied corrections: the P-8's anti-ship fit pointed at a \
Harpoon no mod defines (loaded empty), and HMS Ocean could not operate the \
Apache AH1 her sister hulls already support.
"""


def main():
    if not (ROOT / "mods-source" / "3606774881" / "ammunition" / f"{REPLACE}.ini").exists():
        sys.exit(f"{REPLACE} not found - U.S. Navy 2027 must be exported first")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print("SEST_Allied_Fixes")

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
        text = src.read_text(encoding="utf-8")
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
        text = src.read_text(encoding="utf-8")
        if "uk_ah_mk_1" in text:
            sys.exit("rn_lph_ocean.ini: upstream now supports the Apache - drop this fix")
        text, n = re.subn(r"^AircraftSupported=raac_lynx_ah7\s*$",
                          "AircraftSupported=raac_lynx_ah7,uk_ah_mk_1",
                          text, flags=re.M)
        if n != 1:
            sys.exit(f"rn_lph_ocean.ini: AircraftSupported line changed upstream ({n} matches)")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        print("  vessels/rn_lph_ocean.ini  (+uk_ah_mk_1 Apache AH1 supported)")

    # APKWS II-ER: the medium-range strike guided rocket (user ask). The
    # Apache mod's M282 APKWS with its launch envelope extended 3.5 -> 8 nm -
    # in this engine range is the MaxLaunchRange key, there is no separate
    # flight-time knob. No new art: rocket, pod, meshes and effects are the
    # Apache mod's own, byte-identical but for the range line and the pod's
    # payload reference. Carried by the Ocean-capable Apache AH1 as a new
    # fit cloned from its all-rockets Strike loadout.
    apache = ROOT / "mods-source" / "3425450153"
    rocket_src = apache / "ammunition" / "usa_apkws_2_m282.ini"
    pod_src = apache / "ammunition" / "usn_agr-20b_apache.ini"
    heli_src = apache / "aircraft" / "uk_ah_mk_1.ini"
    if not (rocket_src.exists() and pod_src.exists() and heli_src.exists()):
        print("  APKWS-ER  SKIPPED - Apache mod 3425450153 not exported")
    else:
        rocket = rocket_src.read_text(encoding="utf-8", errors="replace")
        rocket, n = re.subn(r"^MaxLaunchRange=3\.5\b", "MaxLaunchRange=8", rocket, flags=re.M)
        if n != 1:
            sys.exit(f"usa_apkws_2_m282: MaxLaunchRange line changed upstream ({n} matches)")
        (OUT / "ammunition").mkdir(parents=True, exist_ok=True)
        (OUT / "ammunition" / "sest_apkws_er.ini").write_text(
            "# SEST APKWS II-ER - the Apache mod's M282 APKWS with the launch\n"
            "# envelope extended 3.5 -> 8 nm. Everything else is upstream's.\n"
            + rocket, encoding="utf-8")

        pod = pod_src.read_text(encoding="utf-8", errors="replace")
        pod, n = re.subn(r"^Ammunition=usa_apkws_2_m282\s*$",
                         "Ammunition=sest_apkws_er", pod, flags=re.M)
        if n != 1:
            sys.exit(f"usn_agr-20b_apache: Ammunition line changed upstream ({n} matches)")
        (OUT / "ammunition" / "sest_agr-20er.ini").write_text(
            "# SEST LAU-68 pod loaded with the extended-range APKWS II-ER.\n" + pod,
            encoding="utf-8")

        heli = heli_src.read_text(encoding="utf-8", errors="replace")
        if "SEST_APKWS_ER" in heli:
            sys.exit("uk_ah_mk_1: upstream already defines SEST_APKWS_ER - re-check")
        heli, n = re.subn(r"^(AvailableLoadouts=[^\n]*)$", r"\1,SEST_APKWS_ER",
                          heli, count=1, flags=re.M)
        if n != 1:
            sys.exit("uk_ah_mk_1: AvailableLoadouts line not found")
        # search AFTER the AvailableLoadouts edit - held offsets go stale
        # (the SEAD260 lesson).
        m = re.search(r"^\[WeaponSystem1Strike\][^\n]*\n(.*?)(?=^\[)", heli, re.M | re.S)
        if not m:
            sys.exit("uk_ah_mk_1: Strike donor block not found")
        body = m.group(1)
        body2 = body.replace("usn_agr-20b_apache|LAU-68", "sest_agr-20er|LAU-68")
        if body2.count("sest_agr-20er") != 4:
            sys.exit("uk_ah_mk_1: expected 4 rocket pods in the Strike donor")
        heli = (heli[:m.end()] + "[WeaponSystem1SEST_APKWS_ER]\n" + body2 + heli[m.end():])
        (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
        (OUT / "aircraft" / "uk_ah_mk_1.ini").write_text(heli, encoding="utf-8")

        lang = OUT / "language_en"
        lang.mkdir(parents=True, exist_ok=True)
        (lang / "ammunition_names.ini").write_text(
            "[AmmunitionNames]\n"
            "sest_apkws_er=M282ER,APKWS II-ER,GFFAR,"
            "Extended-range development of the AGR-20 APKWS II laser-guided "
            "70mm rocket. An uprated motor stretches the launch envelope from "
            "3.5 to 8 nautical miles - a medium-range precision strike round "
            "at rocket cost. Same guidance kit and warhead as the M282.\n"
            "sest_agr-30=AGR-30,Redback,GFFAR,"
            "What-if evolution of the 70mm guided rocket family: the AGR-30 "
            "Redback replaces the APKWS II laser kit with an imaging-infrared "
            "seeker - true fire and forget out to 15 nautical miles with a "
            "lofted profile and terminal dive. Same airframe and warhead as "
            "the APKWS II; missile performance at rocket cost.\n",
            encoding="utf-8")
        (lang / "loadout_names.ini").write_text(
            "[LoadoutNames]\n"
            "SEST_APKWS_ER=SEST APKWS-ER Strike (28x guided rockets)\n"
            "SEST_REDBACK=SEST Redback Strike (28x AGR-30 F&F)\n",
            encoding="utf-8")
        print("  APKWS-ER: ammunition x2, uk_ah_mk_1 fit SEST_APKWS_ER (4 pods + Starstreak)")

        # AGR-30 Redback: rebased onto dts_apkws-ii after two freezes. The
        # M282-based build differed from every working pod round in dozens
        # of keys; dts_apkws-ii is a PROVEN in-pod rocket WITH loft keys from
        # the collection's own weapon pack, so the Redback is now that file
        # with the minimum deltas: IR seeker instead of laser (GuidanceType
        # 1, MidCourseCorrection stays 0 - pure fire and forget, five
        # in-container precedents), range 6 -> 15 nm, loft raised 5/1500 ->
        # 12/4000 for the higher profile. Motor, fuze, effects, terminal
        # logic all stay the working weapon's.
        rb_src = ROOT / "mods-source" / "3760871384" / "ammunition" / "dts_apkws-ii.ini"
        if not rb_src.exists():
            sys.exit("dts_apkws-ii.ini missing - Dingtools Weapon Pack must be exported")
        rb = rb_src.read_text(encoding="utf-8", errors="replace")
        swaps = [
            (r"^GuidanceType=5\b", "GuidanceType=1"),
            (r"^SeekerPassiveRange=6\.0\b", "SeekerPassiveRange=8"),
            (r"^MaxLaunchRange=6\b", "MaxLaunchRange=15"),
            (r"^MaxLoftAngle=5\.0\b", "MaxLoftAngle=12.0"),
            (r"^MaxLoftAlt=1500\b", "MaxLoftAlt=4000"),
        ]
        for pat, rep in swaps:
            rb, k = re.subn(pat, rep, rb, flags=re.M)
            if k != 1:
                sys.exit(f"dts_apkws-ii: {pat} matched {k} times - upstream changed")
        (OUT / "ammunition" / "sest_agr-30.ini").write_text(
            "# SEST AGR-30 Redback - dts_apkws-ii (proven in-pod, lofting) with an\n"
            "# IR seeker, 15 nm reach and a raised loft. Minimum-delta rebase after\n"
            "# the M282-based build froze the game twice.\n"
            + rb, encoding="utf-8")

        rbpod, k = re.subn(r"^Ammunition=usa_apkws_2_m282\s*$",
                           "Ammunition=sest_agr-30",
                           pod_src.read_text(encoding="utf-8", errors="replace"), flags=re.M)
        if k != 1:
            sys.exit("usn_agr-20b_apache: Ammunition line changed upstream (Redback pod)")
        (OUT / "ammunition" / "sest_agr-30_pod.ini").write_text(
            "# SEST LAU-68 pod loaded with the AGR-30 Redback.\n" + rbpod, encoding="utf-8")

        heli = (OUT / "aircraft" / "uk_ah_mk_1.ini").read_text(encoding="utf-8")
        if "SEST_REDBACK" in heli:
            sys.exit("uk_ah_mk_1: SEST_REDBACK already present - re-check")
        heli, k = re.subn(r"^(AvailableLoadouts=[^\n]*)$", r"\1,SEST_REDBACK",
                          heli, count=1, flags=re.M)
        if k != 1:
            sys.exit("uk_ah_mk_1: AvailableLoadouts not found (Redback)")
        m = re.search(r"^\[WeaponSystem1SEST_APKWS_ER\][^\n]*\n(.*?)(?=^\[)", heli, re.M | re.S)
        if not m:
            sys.exit("uk_ah_mk_1: SEST_APKWS_ER donor block not found")
        body = m.group(1).replace("sest_agr-20er|LAU-68", "sest_agr-30_pod|LAU-68")
        if body.count("sest_agr-30_pod") != 4:
            sys.exit("uk_ah_mk_1: expected 4 pods in the Redback donor")
        heli = heli[:m.end()] + "[WeaponSystem1SEST_REDBACK]\n" + body + heli[m.end():]
        (OUT / "aircraft" / "uk_ah_mk_1.ini").write_text(heli, encoding="utf-8")
        print("  Redback: ammunition x2, uk_ah_mk_1 fit SEST_REDBACK (28x AGR-30 active)")

        # Redback rollout (user ask): the other Apaches, the A-10C, and the
        # MQ-9s. Only the Redback travels - the laser APKWS-ER stays on the
        # Ocean Apache. Each carrier clones its own densest rocket (or
        # strike) fit with the pods swapped in, seats preserved.
        ROLLOUT = [
            ("3425450153", "usa_ah-64a.ini", "Strike",
             [(r"^(Station\d+=)usn_agr-20b_apache\|", r"\1sest_agr-30_pod|", 4)]),
            ("3425450153", "usa_ah-64d.ini", "Strike",
             [(r"^(Station\d+=)usn_agr-20b_apache\|", r"\1sest_agr-30_pod|", 4)]),
            ("3425450153", "usa_ah-64e.ini", "Strike",
             [(r"^(Station\d+=)usn_agr-20b_apache\|", r"\1sest_agr-30_pod|", 4)]),
            ("3425450153", "usn_ah-64na.ini", None,
             [(r"^(Station\d+=)usn_agr-20b\|", r"\1sest_agr-30_pod|", 3)]),
            ("3459682829", "usa_a-10c.ini", "CAS1",
             [(r"^(Station\d+=)usn_agr-20b\|", r"\1sest_agr-30_pod|", 5)]),
            ("3503670861", "usaf_mq-9a.ini", "Strike",
             [(r"^(Station\d+=)uav_agm-114k\|AGM-114$", r"\1sest_agr-30_pod|AGM-114", 2),
              (r"^(Station\d+=)uav_gbu-49$", r"\1sest_agr-30_pod", 2)]),
            ("3503670861", "usaf_mq-9_er.ini", "Strike",
             [(r"^(Station\d+=)uav_agm-114k\|AGM-114$", r"\1sest_agr-30_pod|AGM-114", 2),
              (r"^(Station\d+=)uav_gbu-49$", r"\1sest_agr-30_pod", 2)]),
        ]
        for mod, fname, donor, swaps in ROLLOUT:
            csrc = ROOT / "mods-source" / mod / "aircraft" / fname
            cdst = OUT / "aircraft" / fname
            if not csrc.exists():
                if cdst.exists():
                    cdst.unlink()
                print(f"  {fname}  SKIPPED - {mod} not exported")
                continue
            ct = csrc.read_text(encoding="utf-8", errors="replace")
            if "SEST_REDBACK" in ct:
                sys.exit(f"{fname}: upstream already defines SEST_REDBACK - re-check")
            ct, k = re.subn(r"^(AvailableLoadouts=[^\n]*)$", r"\1,SEST_REDBACK",
                            ct, count=1, flags=re.M)
            if k != 1:
                sys.exit(f"{fname}: AvailableLoadouts not found")
            if donor is None:
                # densest fit by the first swap pattern
                best = None
                for bm in re.finditer(r"^\[WeaponSystem1(\w+)\][^\n]*\n(.*?)(?=^\[)",
                                      ct, re.M | re.S):
                    c = len(re.findall(swaps[0][0], bm.group(2), re.M))
                    if c and (best is None or c > best[1]):
                        best = (bm.group(1), c)
                if not best:
                    sys.exit(f"{fname}: no donor fit carries the base rockets")
                donor = best[0]
            bm = re.search(r"^\[WeaponSystem1" + donor + r"\][^\n]*\n(.*?)(?=^\[)",
                           ct, re.M | re.S)
            if not bm:
                sys.exit(f"{fname}: donor fit {donor} not found")
            body = bm.group(1)
            for pat, rep, need in swaps:
                body, k = re.subn(pat, rep, body, flags=re.M)
                if k < need:
                    sys.exit(f"{fname}: {donor} swapped {k} lines for {pat}, expected {need}")
            ct = ct[:bm.end()] + "[WeaponSystem1SEST_REDBACK]\n" + body + ct[bm.end():]
            cdst.parent.mkdir(parents=True, exist_ok=True)
            cdst.write_text(ct, encoding="utf-8")
            pods = body.count("sest_agr-30_pod")
            print(f"  aircraft/{fname}  SEST_REDBACK ({pods} pods, donor {donor})")



        built += 1

    if not built:
        sys.exit("nothing built - no target mod is exported")


if __name__ == "__main__":
    main()
