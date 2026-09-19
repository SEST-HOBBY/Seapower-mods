#!/usr/bin/env python3
"""Build SEST Intercept Model: restore the global intercept table, and repair
the rounds that restoring it would break.

This is the deferred half of the SM-3 investigation (see
integration/aegis-bmd/build_patch.py, "THE DEFERRED FIX"). It ships as its own
pack because restoring the table is a collection-wide behaviour change and it
MUST travel with the overrides that keep it safe. Split across two packs, a
load-order accident could install the clamp without its fixes.

WHAT IS BROKEN
  ammunition/ is a whole-file override (docs/design-notes.md). The Tu-95/AS-15
  mod (3395022688) ships an ammunition/damage.ini built on a pre-0.8.x copy of
  the file, and it is the only other damage.ini in the tree, so it wins over
  vanilla's and deletes eight global keys from the whole collection:

    InterceptOutOfAltitudePenalty=0.5       InterceptSizeBonusWeapon=0.2
    InterceptSpeedPenaltyMultiplier=1.4     InterceptSizeBonusHelicopter=0.05
    InterceptChanceOutOfAltitudeOverride    InterceptSizeBonusAircraftSmall=0
      =0.05                                 InterceptSizeBonusAircraftLarge=-0.1
                                            InterceptSizeBonusAircraftLargeSARH
                                              =-0.2
  Its intended edit is only VeryLarge and VeryLargeDecalScale (see
  CARRIED FORWARD below). The eight are collateral.

  Scope of the damage, measured rather than assumed: these keys govern the
  MISSILE intercept path only. No gun or projectile round anywhere declares an
  attack-altitude band, and the CIWS formula's own inputs - BaseRoll,
  CIWSSizeMultiplier, CIWSMultiplier, at the top of vanilla's damage.ini - are
  NOT among the eight. CIWS scoring was never affected.

WHAT RESTORING THEM ACTUALLY DOES
  Counted over the winning copy of all 1672 ammunition ids, resolved through
  the repo's own load-order resolver (winning_file in
  integration/missions/refine_civ_traffic.py), there are 497 anti-air-capable
  rounds. Against those:

    - all 497 take the five InterceptSizeBonus values. No per-round override
      form for them exists anywhere in the corpus, so nothing can opt out.
      InterceptSizeBonusWeapon=+0.2 makes every SAM better against missiles;
      InterceptSizeBonusAircraftLarge/LargeSARH make them worse against large
      aircraft.
    - 360 inherit InterceptSpeedPenaltyMultiplier=1.4 and 366 inherit
      InterceptOutOfAltitudePenalty=0.5, because they declare no value of their
      own. Both globals are at or worse than the scale the round files' own
      comments call "poor" - that is the intended penalty for not declaring.
    - InterceptChanceOutOfAltitudeOverride=0.05 is the sharpest: a hard 5%
      ceiling on any intercept where the target sits outside the round's
      MinAttackAltitude/MaxAttackAltitude band. It also has no per-round
      override form.

  This is a real rebalance, not a pure repair. It is the right one, because
  every mod in this collection was authored against a stock game where these
  values are live; the current state is an accidental global buff that an
  unrelated bomber mod has been granting for free.

  Honest about the premise: nothing in the tree establishes what the engine
  substitutes for a MISSING global. If it falls back to these same numbers,
  the restore is a no-op and only the round fixes below do anything. The
  benefit and the risk rest on the same unproven assumption.

WHAT THE CLAMP WOULD BREAK, AND IS FIXED HERE
  311 of the 497 declare a band. Two are authored in a way the clamp turns
  into a dead weapon:

  1. Red Storm Arsenal's SM-6 family (usn_rim_174a/b/c - note the UNDERSCORE,
     different ids from Euromod's hyphenated rounds) declares
     MinAttackAltitude=70000 ft on a multi-role area-defence SAM: TargetType
     =AAW, SecondaryTargetType=ASuW, LandAttackCapability=ShoreTargetsOnly,
     260 nm reach. Its file opens with a "REQUIRES STATS REVISION" banner.

     Two things settle that 70000 is an error, not a tier. First, the round's
     own file: a ship sits at 0 ft and a shore target sits at 0 ft, so a
     70,000 ft MINIMUM TARGET altitude contradicts its own secondary and land
     roles. Second, the exact comparator: Euromod's usn_rim-174c has the
     IDENTICAL 180000 ft ceiling and a floor of 5. Same variant, same ceiling,
     floor 14,000x lower. Red Storm's own ESSM (usn_rim_162a) and SM-2
     (usn_rim_66m5) use 15 on the same hulls. The floor drops to 15.

  2. 3558173926's idf_stunner.ini writes MaxAttackAltitude=51,000 with a
     thousands separator - the only such value among every altitude key in the
     tree. Sea Power is a Unity/C# game, and .NET numeric parsing accepts group
     separators by default, so under an invariant or en-US culture this reads
     51000, while under a de-DE or fr-FR culture the same string reads 51.0 and
     the band collapses to the empty 500..51. The hazard is locale-dependent,
     not universal. Rewriting it as 51000 - the author's own intended number -
     makes the file read the same on every player's machine. A no-op wherever
     it already parsed correctly.

  Neither of these is fielded by the active mission: the 21 hulls carrying the
  Red Storm SM-6 are all from that mod and none is in the order of battle, and
  idf_stunner is carried only by idf_dsws, also absent. They are fixed because
  the units are selectable, not because the current mission needs them. For
  that mission specifically, this pack is all table and no mitigation.

DELIBERATELY NOT CHANGED
  - thaad (3683253079) 20000-99000, pla_hq-19 (3733719765) 99000-495000, and
    SEST_Aegis_BMD's own SM-3 family at 100000. Dedicated ballistic-missile
    interceptors; a floor is the point.
  - usa_mim-14 (vanilla Nike Hercules) at 3600. Stock content, authored against
    a stock damage.ini that has always carried the clamp.
  - 3392434750's SA-21 rounds: wp_40n6 (floor 21000) and wp_48n6e3 (floor
    2900). State the consequence plainly, because an earlier draft of this file
    got it wrong: that mod ships FOUR SINGLE-ROUND TELs, not one mixed
    launcher. Its wp_sam_site_sa-21 land unit does carry all four tiers and is
    covered 20 ft to 99000 ft continuously, but the missions place
    wp_sa-21_40n6_tel and wp_sa-21_48n6e3_tel and no 9M96 TEL at all. So under
    the restored clamp those launchers really are held to 5% below their floors,
    with no low-tier round on the mount.

    Left alone anyway, on purpose. Those floors are internally coherent - a
    very-long-range high-tier round that is poor down low is a real design, and
    unlike the SM-6 nothing in the file contradicts it. More to the point, any
    player running that mod WITHOUT the Tu-95 mod already has exactly this
    behaviour, because the clamp is stock. Overriding it would not be repairing
    a defect, it would be SEST second-guessing another author's balance and
    handing the red side a buff. If that trade is unwanted, the fix is a
    mission edit placing a 9M96 TEL alongside, not an ammunition override.

CARRIED FORWARD, AND NOT A NUKE TWEAK
  See VERY_LARGE_IMPACT below. Both mods' descriptions and this pack's first
  draft called 3395022688's VeryLarge edit its "more realistic nuke". It is
  not: VeryLarge is a GLOBAL [ImpactSize] tier, a diameter in metres, and 59
  winning rounds use it, of which only 2 are that mod's own nuclear AS-15s.

THE ONE RESIDUAL RISK
  62 of the 311 banded rounds declare only one side - 52 a floor and no
  ceiling (the AMRAAM and Meteor families, floors of 10 to 67 ft), 10 a ceiling
  and no floor (point-defence rounds: Roland, VT-1, HQ-10, RAM, ceilings of
  4000 to 30000 ft). None of vanilla's 74 banded files does this.

  Stock content settles what an absent key means, though. Three vanilla AAW
  MISSILES declare no band at all - fr_super-530f, pla_pl-2 and pla_pl-2b - and
  they have shipped for years against a damage.ini where the clamp is live. If
  an absent altitude key defaulted to zero, those three would be permanently
  held at 5%. The engine must treat an omitted side as unbounded.

  A known blind spot in the survey behind these numbers: 80 of the 1672 winning
  files are #!alias stubs, and an alias resolves its base through the load
  order. A round can therefore inherit a band it never literally declares - the
  ESSM, RAM and SM-2 families do exactly that - and one of them composes its
  band across two mods. Every inherited band checked is sane, but the method
  would not have caught a bad one. Make the survey alias-aware before trusting
  it again.

Usage (repo root):  python3 integration/intercept-model/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
OUT = Path(__file__).resolve().parent / "SEST_Intercept_Model"

TU95 = "3395022688"        # Tu-95 With AS-15, ships the truncated damage.ini
REDSTORM = "3413868677"    # Red Storm Arsenal, ships the underscore SM-6 family
STUNNER = "3558173926"     # David's Sling, ships idf_stunner.ini

# The eight global keys the Tu-95 copy drops. Restoring them is the whole point
# of this pack, so the exact set is pinned: build_damage_ini() exits unless the
# vanilla-to-donor difference is precisely these plus the values below.
INTERCEPT_KEYS = (
    "InterceptOutOfAltitudePenalty",
    "InterceptSpeedPenaltyMultiplier",
    "InterceptChanceOutOfAltitudeOverride",
    "InterceptSizeBonusWeapon",
    "InterceptSizeBonusHelicopter",
    "InterceptSizeBonusAircraftSmall",
    "InterceptSizeBonusAircraftLarge",
    "InterceptSizeBonusAircraftLargeSARH",
)

# ---------------------------------------------------------------------------
# A DECISION, NOT A DETAIL. VeryLarge is a global [ImpactSize] tier - vanilla's
# own comment reads "Impact size diameter in meter" - and vanilla sets it to
# 120.0 with a decal scale of 3.0. 3395022688 sets 2000.0 and 1000.0.
#
# 59 winning rounds carry ImpactSize=VeryLarge and only TWO are nuclear (that
# mod's own AS-15 variants). The other 57 are conventional, among them the RBU
# rocket depth charges, the Mk46/Mk54 ASROC torpedoes, two naval mines, the
# SA-13 SAM, GBU-10/15/2, the JASSM and LRASM families, the PLA 300 mm MLRS
# rockets, and two rounds SEST itself ships (dts_agm-183a, usn_gbu-24). At
# 2000.0 every one of them gets a 2 km lethal diameter, 16.7x vanilla's.
#
# Kept at the donor's values, deliberately. That is already the live state of
# this install - 3395022688's damage.ini wins today - so keeping it changes
# nothing a player has, while reverting would silently shrink 57 conventional
# weapons AND break the one edit that mod exists to make. ImpactSize is a fixed
# enum, so the AS-15 cannot be given a tier of its own; there is no third
# option. Flip these two values to "120.0" / "3.0" to take vanilla's instead -
# that is the whole change, and the census above is the evidence for making it.
VERY_LARGE_IMPACT = {"VeryLarge": "2000.0", "VeryLargeDecalScale": "1000.0"}

# New floor for the Red Storm SM-6 trio: the value its own mod uses for ESSM
# and SM-2 on the very same hulls, and what every other SM-6 in the collection
# uses (Euromod's rim-174c, same 180000 ceiling, uses 5).
SM6_FLOOR = "15"

INFO_INI = """\
[Language_en]
Name=SEST Intercept Model
Description=Restores the eight global intercept keys that the Tu-95/AS-15 mod's \
pre-0.8.x ammunition/damage.ini deletes from the whole collection, including \
InterceptChanceOutOfAltitudeOverride, the hard 5%% ceiling on out-of-altitude \
intercepts, and the five InterceptSizeBonus values no round can opt out of. \
Every mod here was authored against a stock game where these are live, so the \
current state is an accidental global buff from an unrelated bomber mod. That \
mod's VeryLarge impact tier is carried forward unchanged so its own content \
still works. Ships with the two overrides that make restoring the table safe: \
Red Storm Arsenal's SM-6 family (usn_rim_174a/b/c) drops its 70,000 ft \
engagement floor to %(sm6)s ft, matching the ESSM and SM-2 that mod puts on the \
same hulls and the Euromod SM-6 of the same ceiling, and David's Sling \
(idf_stunner) has its MaxAttackAltitude rewritten without the thousands \
separator that reads as 51 feet under some locales. Generated by \
integration/intercept-model/build_patch.py; must load above every workshop mod.

[Compatibility]
ApproximateVersion=0.8.2
""" % {"sm6": SM6_FLOOR}


def read(mod, rel):
    src = MODS / mod / rel
    if not src.exists():
        sys.exit(f"donor missing (re-export {mod}?): {src}")
    return src.read_text(encoding="utf-8-sig", errors="replace")


def write(rel, text, header):
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    banner = "".join(f"# {line}\n" for line in header.splitlines())
    dst.write_text(banner + text, encoding="utf-8")


def edit(text, pattern, repl, expect, ctx):
    """Regex-sub with an exact match-count guard: an upstream change to the
    donor fails the build loudly instead of silently shipping a stale merge."""
    out, n = re.subn(pattern, repl, text, flags=re.M)
    if n != expect:
        sys.exit(f"{ctx}: pattern {pattern!r} matched {n} times, expected {expect} "
                 "- donor changed upstream, rebase this fix")
    return out


def sole_provider(rel, expected_mod):
    """Every file here is a whole-file override of ONE mod's copy. If a
    re-export brings a second provider, shipping ours would silently delete
    theirs - the same failure the damage.ini pin exists to prevent, one level
    up. Same shape as collection-fixes' MISSING_SENSORS guard."""
    others = sorted(
        p.parts[-3] for p in MODS.glob(f"*/{rel}")
        if p.parts[-3] not in (expected_mod, "_vanilla")
    )
    if others:
        sys.exit(f"{rel}: now also shipped by {others}, not just {expected_mod}. "
                 "Overriding it would silently delete their copy - re-verify which "
                 "donor this pack should be based on before shipping")


def kv(text):
    """Flat key -> value map. damage.ini has sections but no key is reused
    across them (73 keys in vanilla, 73 distinct), so flat is safe and lets the
    pin below compare the two files key for key."""
    d = {}
    for ln in text.splitlines():
        s = ln.split("//", 1)[0].strip()
        if not s or s[0] in "#;[":
            continue
        if "=" in s:
            k, v = s.split("=", 1)
            d[k.strip()] = v.strip()
    return d


# -------------------------------------------------------- the global table
def build_damage_ini():
    sole_provider("ammunition/damage.ini", TU95)
    vanilla = read("_vanilla/original", "ammunition/damage.ini")
    donor = read(TU95, "ammunition/damage.ini")
    v, d = kv(vanilla), kv(donor)

    # Complete pin. Anything the donor changes that this pack has not been told
    # about would be silently reverted by shipping vanilla's file, so the build
    # stops instead and asks for the merge to be rebased.
    dropped = sorted(set(v) - set(d))
    added = sorted(set(d) - set(v))
    changed = {k: (v[k], d[k]) for k in set(v) & set(d) if v[k] != d[k]}

    if dropped != sorted(INTERCEPT_KEYS):
        extra = sorted(set(dropped) - set(INTERCEPT_KEYS))
        sys.exit(
            f"damage.ini: vanilla has {len(extra)} key(s) {TU95}'s copy lacks beyond the "
            f"expected eight: {extra}. Either {TU95} changed, or a game update added keys "
            "to vanilla's table - check vanilla first, then rebase this merge"
            if extra else
            f"damage.ini: {TU95} no longer drops {sorted(set(INTERCEPT_KEYS) - set(dropped))} "
            "- if upstream fixed it, this pack may be obsolete; rebase")
    if added:
        sys.exit(f"damage.ini: {TU95} now ADDS keys vanilla lacks: {added}. Shipping "
                 "vanilla's file would delete them - rebase this merge")
    if {k: b for k, (a, b) in changed.items()} != VERY_LARGE_IMPACT:
        sys.exit(f"damage.ini: {TU95} now changes {changed}, expected only "
                 f"{VERY_LARGE_IMPACT} - rebase this merge against its new values")

    t = vanilla
    for key, value in VERY_LARGE_IMPACT.items():
        t = edit(t, rf"^{re.escape(key)}=[^\n]*$", f"{key}={value}", 1, "damage.ini")

    write("ammunition/damage.ini", t,
          "SEST Intercept Model - the vanilla global damage and intercept table,\n"
          f"with {TU95}'s VeryLarge={VERY_LARGE_IMPACT['VeryLarge']} impact tier carried\n"
          "forward unchanged. That mod ships this file built on a pre-0.8.x copy, and\n"
          "ammunition/ is a whole-file override, so winning it deleted eight global\n"
          "intercept keys from the WHOLE collection - among them\n"
          "InterceptChanceOutOfAltitudeOverride, the hard 5% ceiling on out-of-altitude\n"
          "intercepts, and the five InterceptSizeBonus values no round can opt out of.\n"
          "Restored. See this pack's builder for what VeryLarge actually affects.")
    return dropped


# ------------------------------------------- the rounds the table would break
def build_sm6():
    """Red Storm Arsenal's SM-6 trio: a 70,000 ft floor on a multi-role SAM."""
    built = []
    for variant in ("a", "b", "c"):
        name = f"usn_rim_174{variant}"
        sole_provider(f"ammunition/{name}.ini", REDSTORM)
        t = read(REDSTORM, f"ammunition/{name}.ini")

        # If this stops being a general-purpose round with surface and shore
        # roles, the contradiction that proves the floor wrong is gone.
        for key, value in (("TargetType", "AAW"), ("SecondaryTargetType", "ASuW"),
                           ("LandAttackCapability", "ShoreTargetsOnly")):
            if not re.search(rf"^{key}={value}(\s|$)", t, re.M):
                sys.exit(f"{name}: no longer {key}={value} - re-verify that the "
                         "70000 ft floor is still wrong before overriding it")
        t = edit(t, r"^MinAttackAltitude=70000(\s)", rf"MinAttackAltitude={SM6_FLOOR}\1",
                 1, name)
        write(f"ammunition/{name}.ini", t,
              f"SEST Intercept Model - base: {REDSTORM}'s {name}.ini, one delta:\n"
              f"MinAttackAltitude 70000 -> {SM6_FLOOR} ft. A 70,000 ft minimum TARGET\n"
              "altitude on a round that also lists SecondaryTargetType=ASuW and\n"
              "LandAttackCapability=ShoreTargetsOnly contradicts its own file: ships and\n"
              "shore targets sit at 0 ft. Euromod's usn_rim-174c has the identical\n"
              "180000 ft ceiling and a floor of 5; this mod's own ESSM and SM-2 use 15 on\n"
              "the same hulls. Matters because this pack restores the 5% clamp.")
        built.append(name)
    return built


def build_stunner():
    """idf_stunner: MaxAttackAltitude written with a thousands separator."""
    name = "idf_stunner"
    sole_provider(f"ammunition/{name}.ini", STUNNER)
    t = read(STUNNER, f"ammunition/{name}.ini")
    t = edit(t, r"^MaxAttackAltitude=51,000(\s)", r"MaxAttackAltitude=51000\1", 1, name)
    write(f"ammunition/{name}.ini", t,
          f"SEST Intercept Model - base: {STUNNER}'s {name}.ini, one delta:\n"
          "MaxAttackAltitude 51,000 -> 51000, the author's own intended number written\n"
          "without the thousands separator. It is the only grouped numeric altitude in\n"
          "the tree. .NET numeric parsing accepts group separators, so this reads 51000\n"
          "under an invariant or en-US culture and 51.0 under de-DE or fr-FR - where the\n"
          "band collapses to the empty 500..51 and this pack's restored clamp would hold\n"
          "David's Sling at 5% against everything. A no-op wherever it already parsed.")
    return [name]


def main():
    restored = build_damage_ini()
    rounds = build_sm6() + build_stunner()

    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)}")
    print(f"  ammunition/damage.ini: restored {len(restored)} global intercept keys "
          f"dropped by {TU95}")
    print(f"  + {len(rounds)} round override(s) the restored clamp requires - "
          f"{', '.join(rounds)}")


if __name__ == "__main__":
    main()
