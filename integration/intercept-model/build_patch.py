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
  integration/missions/refine_civ_traffic.py) AND through #!alias inheritance -
  80 of those files are alias stubs whose base is itself resolved by load
  order, so a round can carry a band it never literally declares - there are
  514 anti-air-capable rounds. Against those:

    - six of the eight keys have NO per-round override form anywhere in the
      corpus, so nothing can opt out of them: the five InterceptSizeBonus
      values and the clamp. All 514 take them.
      InterceptSizeBonusWeapon=+0.2 makes every SAM better against missiles;
      InterceptSizeBonusAircraftLarge/LargeSARH make them worse against large
      aircraft.
    - the other two DO have a per-round form, and most rounds decline it. 360
      inherit InterceptSpeedPenaltyMultiplier=1.4 and 366 inherit
      InterceptOutOfAltitudePenalty=0.5. Both globals are at or worse than the
      scale the round files' own comments call "poor" - that is the intended
      penalty for not declaring.
    - InterceptChanceOutOfAltitudeOverride=0.05 is the sharpest: a hard 5%
      ceiling on any intercept where the target sits outside the round's
      MinAttackAltitude/MaxAttackAltitude band.

  This is a real rebalance, not a pure repair - IF the keys are doing anything
  by their absence. Nothing in the tree establishes what the engine substitutes
  for a MISSING global. Two readings, and the files cannot separate them:

    - it falls back to these same numbers, in which case the table's deletion
      never changed anything, this restore is a no-op, and only the two round
      fixes below do any work;
    - it falls back to something else, most likely zero or no modifier, in
      which case the deletion has been handing every round in the collection a
      quiet buff and restoring the table takes it away.

  The case for shipping does not depend on which: either the pack is inert on
  this axis, or it returns the collection to the stock values every one of its
  mods was authored against. The claim NOT being made is that the second
  reading is established. It is not.

WHAT THE CLAMP WOULD BREAK, AND IS FIXED HERE
  328 of the 514 declare a band, 18 of them by alias inheritance. Scanned for
  floors above 1000 ft, ceilings below 5000 ft, inverted or empty bands and
  malformed values, two are authored in a way the clamp turns into a dead
  weapon. The alias-resolved pass found no case the flat pass had missed:

  1. Red Storm Arsenal's SM-6 family (usn_rim_174a/b/c - note the UNDERSCORE,
     different ids from Euromod's hyphenated rounds) declares
     MinAttackAltitude=70000 ft on a multi-role area-defence SAM: TargetType
     =AAW, SecondaryTargetType=ASuW, LandAttackCapability=ShoreTargetsOnly,
     260 nm reach. Its file opens with a "REQUIRES STATS REVISION" banner.

     The argument that settles it is the comparator, not the role. Euromod's
     usn_rim-174c has the IDENTICAL 180000 ft ceiling and a floor of 5 - same
     variant, same ceiling, floor 14,000x lower. Red Storm's own ESSM
     (usn_rim_162a) and SM-2 (usn_rim_66m5) use 15 on the same hulls. Across
     the corpus, 132 anti-air rounds carry a surface or land role and declare a
     floor; the highest any stock one uses is 328 ft. 70000 is 210x that.

     Do NOT lean on the surface-role contradiction on its own, tempting as it
     is: 23 of the 24 distinct floor values among those 132 rounds are above
     zero, including vanilla's own ASuW-capable SAMs at 85, 100, 164 and 328
     ft. A non-zero floor on a round that can shoot at ships is normal, so the
     mere fact of one proves nothing - and the replacement 15 does not resolve
     that contradiction either, since 15 is still above a ship's 0 ft. 15 is
     chosen because it is what this mod and every other SM-6 in the collection
     use, not because it fixes the surface case. Whether the clamp applies to
     surface engagements at all is untested.

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
  See SHIPPED_IMPACT below. Both mods' descriptions and this pack's first draft
  called 3395022688's VeryLarge edit its "more realistic nuke". It is not:
  VeryLarge is a GLOBAL [ImpactSize] tier, and 59 winning rounds use it, of
  which only 2 are that mod's own nuclear AS-15s. Preserving the install's
  current behaviour is the reason it is kept; that is not the same as arguing
  2000.0 is correct for the 57 conventional rounds that share the tier, and
  this pack does not argue that.

WHAT THIS PACK HAS NOT DEMONSTRATED, AND HOW TO SETTLE IT
  Everything above is read out of the files. None of it is verified in game,
  and the four repo checkers do not test behaviour - they test that references
  resolve and that load order is sane. Green checkers say the configuration is
  coherent; they say nothing about whether the SM-3 now hits.

  Three questions are inference, not measurement. Each needs a PAIRED
  comparison - the same engagement run twice, changing one thing - because a
  single engagement cannot distinguish "clamped to 5%" from "rolled badly", and
  a single hit cannot rule a 5% clamp out. Read the displayed intercept
  percentage rather than the outcome wherever the UI shows one, and repeat
  enough shots that the difference is not noise. Keep SHIPPED_IMPACT unchanged
  across every run below, or the impact tier becomes a second variable.

  1. Do missing globals already fall back to vanilla's values?
     Run one engagement with this pack installed and the same engagement with
     it disabled, so the only difference is which ammunition/damage.ini wins.
     Use a round that declares NEITHER InterceptOutOfAltitudePenalty nor
     InterceptSpeedPenaltyMultiplier, so it has to inherit both - 360 of the
     514 qualify. Identical percentages mean the engine was already supplying
     these values and this half of the pack is inert. Different percentages
     mean the deletion was live and the restore is real.

  2. How is a missing SIDE of an altitude band handled?
     Pick an AMRAAM (floor, no ceiling) and a RAM (ceiling, no floor). Run each
     as shipped, then again against a local copy that supplies the missing
     bound explicitly - an unbounded value for the open side, so the band
     covers the same space either way. Same percentage means the engine already
     treats an omitted side as open and the 61 one-sided rounds are safe.
     A jump to 5% on the as-shipped run means it does not, and those rounds
     need the missing bound written in, here, the way this pack fixes the SM-6.

  3. Does the clamp reach surface and land engagements?
     This one cannot be answered by any air engagement, so it needs its own
     shot: fire a Red Storm SM-6 at a SHIP. That round carries
     SecondaryTargetType=ASuW and a floor this pack sets to 15 ft, above a
     ship's 0 ft, so if the clamp applies outside the air path the engagement
     is capped at 5% even after the fix. If it is, the floor has to go to 0 for
     rounds with a surface role, and the same question reopens for every other
     round in the collection that has one.

  Do (1) first with an SM-3 against a ballistic target above 100,000 ft, since
  that is the engagement this whole line of work started from: it answers the
  original complaint and question 1 in the same pair of runs.

THE ONE RESIDUAL RISK
  61 of the 328 banded rounds declare only one side - a floor and no ceiling
  (the AMRAAM and Meteor families, floors of 10 to 67 ft), or a ceiling and no
  floor (point-defence rounds: Roland, VT-1, HQ-10, RAM, ceilings of 4000 to
  30000 ft). None of vanilla's 74 banded files does this, so what the engine
  substitutes for the missing side is not settled by stock content.

  There is a partial argument, and it is worth being precise about how far it
  reaches. Three vanilla AAW MISSILES declare no band AT ALL - fr_super-530f,
  pla_pl-2 and pla_pl-2b - and they have shipped for years against a damage.ini
  where the clamp is live. If a missing altitude bound defaulted to zero they
  would be permanently held at 5%. That rules out a zero default for the
  BOTH-ABSENT case. It does NOT prove the one-absent case: an engine may well
  skip the band check entirely when neither bound is present while still
  running it, against a defaulted other side, when one is. The 61 one-sided
  rounds rest on the weaker inference that 23 mods ship them and play against a
  stock table without the breakage being noticed.

  If after installing this pack an AMRAAM or a RAM starts reading 5%, that
  inference is wrong: the fix is to add the missing side to those rounds here,
  and the diagnosis is recorded above. Question 2 under WHAT THIS PACK HAS NOT
  DEMONSTRATED is the paired test that settles it.

  The counts in this docstring come from tools/survey_attack_altitudes.py, which
  is committed so the next mods-source export can re-derive them rather than
  trust these numbers. Re-run it after any export or reorder: a new mod can move
  a band into the danger set without a single file this repo owns changing.

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
# 2000.0 the tier reads 2000 m where vanilla reads 120, 16.7x. What the engine
# does with that number beyond the comment's "diameter in meter" - lethal
# radius, damage-application extent, something else - is not established here.
#
# Kept at the donor's values, deliberately. That is already the live state of
# this install - 3395022688's damage.ini wins today - so keeping it changes
# nothing a player has, while reverting would silently change 57 conventional
# weapons AND undo the one edit that mod exists to make. ImpactSize is a fixed
# enum, so the AS-15 cannot be given a tier of its own; there is no third
# option.
#
# Two separate things, deliberately two constants. DONOR_IMPACT is what the
# merge pin EXPECTS to find in 3395022688's file; SHIPPED_IMPACT is what this
# pack WRITES. They are equal today, which is what "carried forward unchanged"
# means. To take vanilla's values instead, edit SHIPPED_IMPACT alone and leave
# DONOR_IMPACT describing the donor - an earlier version of this file used one
# constant for both jobs, so the revert it advertised aborted its own build.
DONOR_IMPACT = {"VeryLarge": "2000.0", "VeryLargeDecalScale": "1000.0"}
SHIPPED_IMPACT = {"VeryLarge": "2000.0", "VeryLargeDecalScale": "1000.0"}
VANILLA_IMPACT = {"VeryLarge": "120.0", "VeryLargeDecalScale": "3.0"}

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
Every mod here was authored against a stock game where these are live, so \
restoring them returns the collection to the values its mods were written for. \
What the engine substitutes for a deleted global is not established, so this \
half may prove inert. That mod's VeryLarge impact tier is carried forward \
unchanged so its own content still works. Ships with the two overrides that \
make restoring the table safe: \
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
    if {k: b for k, (a, b) in changed.items()} != DONOR_IMPACT:
        sys.exit(f"damage.ini: {TU95} now changes {changed}, expected only "
                 f"{DONOR_IMPACT} - rebase this merge against its new values")
    # Vanilla is the base we write onto, so its values must still be what
    # SHIPPED_IMPACT is choosing between.
    for key, want in VANILLA_IMPACT.items():
        if v.get(key) != want:
            sys.exit(f"damage.ini: vanilla {key} is now {v.get(key)!r}, not {want!r} - "
                     "a game update moved the impact tier; re-decide SHIPPED_IMPACT")

    t = vanilla
    for key, value in SHIPPED_IMPACT.items():
        t = edit(t, rf"^{re.escape(key)}=[^\n]*$", f"{key}={value}", 1, "damage.ini")

    origin = "vanilla" if SHIPPED_IMPACT == VANILLA_IMPACT else f"{TU95}'s value"
    write("ammunition/damage.ini", t,
          "SEST Intercept Model - the vanilla global damage and intercept table,\n"
          f"with the VeryLarge impact tier set to {SHIPPED_IMPACT['VeryLarge']} ({origin}).\n"
          "That mod ships this file built on a pre-0.8.x copy, and ammunition/ is a\n"
          "whole-file override, so winning it deleted eight global intercept keys from\n"
          "the WHOLE collection - among them InterceptChanceOutOfAltitudeOverride, the\n"
          "hard 5% ceiling on out-of-altitude intercepts, and the five\n"
          "InterceptSizeBonus values no round can opt out of. Restored. See this pack's\n"
          "builder for what the VeryLarge tier actually affects.")
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
              f"MinAttackAltitude 70000 -> {SM6_FLOOR} ft, on the comparators alone:\n"
              "Euromod's usn_rim-174c has the identical 180000 ft ceiling with a floor\n"
              "of 5, this mod's own ESSM and SM-2 use 15 on the same hulls, and 70000 is\n"
              "210x the highest floor any stock round with a surface role uses. NOT on\n"
              "the round's anti-ship and shore roles: 23 of the 24 distinct floors among\n"
              "the 132 such rounds are above zero, so a non-zero floor there is normal,\n"
              "and 15 is above a ship's 0 ft too. Matters because this pack restores the\n"
              "5% clamp; whether that clamp reaches surface engagements is untested.")
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
