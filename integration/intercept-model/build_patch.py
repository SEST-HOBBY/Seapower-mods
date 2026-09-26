#!/usr/bin/env python3
"""Build SEST Intercept Model: restore the global intercept table, and repair
the rounds that restoring it would break.

This is the half of the SM-3 investigation that the SM-3 repair itself left
alone. That repair lives in SEST_Collection_Fixes
(integration/collection-fixes/build_patch.py, usn_rim-161b/c/d: the 150,000 ft
floor, explicit penalties, the author's seeker folded in; the story is in
docs/campaigns/southern-watch/build-notes.md) and never touched the global
table. This pack does. It ships as its own pack because restoring the table is
a collection-wide behaviour change and it MUST travel with the overrides that
keep it safe. Split across two packs, a load-order accident could install the
clamp without its fixes.

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
  Counted by tools/survey_attack_altitudes.py over the winning copy of all
  1774 ammunition ids - workshop mods AND the SEST packs, which introduce five
  rounds of their own - resolved through the repo's own load-order resolver
  (winning_file in integration/missions/refine_civ_traffic.py) AND through
  #!alias and #!extend inheritance, since 115 of those files are directive stubs
  whose base is itself resolved by load order, so a round can carry a band it
  never literally declares. That gives 557 anti-air-capable rounds. Against
  those:

    - six of the eight keys have NO per-round override form anywhere in the
      corpus, so nothing can opt out of them: the five InterceptSizeBonus
      values and the clamp. All 557 take them.
      InterceptSizeBonusWeapon=+0.2 makes every SAM better against missiles;
      InterceptSizeBonusAircraftLarge/LargeSARH make them worse against large
      aircraft.
    - the other two DO have a per-round form, and most rounds decline it. 389
      inherit InterceptSpeedPenaltyMultiplier=1.4 and 401 inherit
      InterceptOutOfAltitudePenalty=0.5; 374 inherit both, and 116 of those also
      carry a closed band, which makes them the valid probes for test 1 below.
      Both globals are at or worse than the scale the round files' own comments
      call "poor" - that is the intended penalty for not declaring.
    - InterceptChanceOutOfAltitudeOverride=0.05 is the sharpest: a hard 5%
      ceiling on any intercept where the target sits outside the round's
      MinAttackAltitude/MaxAttackAltitude band.

  This is a real rebalance, not a pure repair - IF the keys are doing anything
  by their absence. Nothing in the tree establishes what the engine substitutes
  for a MISSING global. Two readings, and the files cannot separate them:

    - it falls back to these same numbers, in which case the table's deletion
      never changed anything, this restore is a no-op, and only the round
      fixes below do any work;
    - it falls back to something else, most likely zero or no modifier, in
      which case the deletion has been handing every round in the collection a
      quiet buff and restoring the table takes it away.

  One reading from the game leans toward the second, and it is a hint, not a
  measurement. The report behind the SM-3 repair (57403d63) put the SM-3 at
  "~5% intercept against everything - 7% against supersonic-high" while its
  floor stood at 220,000 ft and the truncated table was live. Almost nothing
  flies that high, so those shots were out of band, and 7% is above a 5%
  ceiling. If the figure the UI shows is the one the ceiling caps, the ceiling
  was not being applied, and arming it here changes every out-of-band shot in
  the collection. Test 1 below is what settles it.

  The case for shipping does not depend on which: either the pack is inert on
  this axis, or it returns the collection to the stock values every one of its
  mods was authored against. The claim NOT being made is that the second
  reading is established. It is not.

WHAT THE CLAMP WOULD BREAK, AND IS FIXED HERE
  360 of the 557 declare a band, 22 of them by directive inheritance. Scanned
  for floors above 1000 ft, ceilings below 5000 ft, inverted or empty bands and
  malformed values, three are authored in a way the clamp turns into a dead
  weapon. The alias-resolved pass found no case the flat pass had missed:

  1. Red Storm Arsenal's SM-6 family (usn_rim_174a/b/c - note the UNDERSCORE,
     different ids from Euromod's hyphenated rounds) declares
     MinAttackAltitude=70000 ft on a multi-role area-defence SAM: TargetType
     =AAW, SecondaryTargetType=ASuW, LandAttackCapability=ShoreTargetsOnly,
     260 nm reach (360 on the C). Its file opens with a "REQUIRES STATS
     REVISION" banner.

     The argument that settles it is the comparator, not the role. Euromod's
     usn_rim-174c has the IDENTICAL 180000 ft ceiling to the Red Storm C and a
     floor of 10 - same variant, same ceiling, floor 7,000x lower - and every
     other surface-launched SM-6 in the collection floors at 10 or 15. Red
     Storm's own ESSM (usn_rim_162a) and SM-2 (usn_rim_66m5) use 15 on the same
     hulls. Across the corpus, as the donors ship them, 138 anti-air rounds
     carry a surface or land role and declare a floor; the highest any stock
     one uses is 328 ft. 70000 is 210x that.

     Do NOT lean on the surface-role contradiction on its own, tempting as it
     is: 24 of the 25 distinct floor values among those 138 rounds are above
     zero, including vanilla's own ASuW-capable SAMs at 85, 100, 164 and 328
     ft. A non-zero floor on a round that can shoot at ships is normal, so the
     mere fact of one proves nothing - and the replacement 15 does not resolve
     that contradiction either, since 15 is still above a ship's 0 ft. 15 is
     chosen because it is what this mod uses on the same hulls and sits with
     every other SM-6 in the collection, not because it fixes the surface case.
     Whether the clamp applies to surface engagements at all is untested.

  2. 3789208859's rok_k-sam-II, which its author names "SAM-II, south korea
     SM-2 ver.", is Red Storm's usn_rim_174a under another name: the same
     70000 ft floor, 130000 ft ceiling, ASuW and shore roles and 260 nm reach,
     and most of the file line for line. It arrived with the Korean mod after
     this pack was first written, and the survey flags it the same way. Every
     argument in 1 carries over, and one more: the K-SAAM on the same frigate
     (rok_saam-400k) floors at 15. It is ko_ffg-828's only area SAM, so under
     the clamp that ship would be left with its 27 nm K-SAAM against anything
     below 70,000 ft. Same fix, same value. The builder also checks that the
     ceiling and the reach still match the SM-6, since that match is the case
     for the override.

  3. 3558173926's idf_stunner.ini writes MaxAttackAltitude=51,000 with a
     thousands separator - the only such value among every altitude key in the
     tree. Sea Power is a Unity/C# game, and .NET numeric parsing accepts group
     separators by default, so under an invariant or en-US culture this reads
     51000, while under a de-DE or fr-FR culture the same string reads 51.0 and
     the band collapses to the empty 500..51. The hazard is locale-dependent,
     not universal. Rewriting it as 51000 - the author's own intended number -
     makes the file read the same on every player's machine. A no-op wherever
     it already parsed correctly.

  Where they are fielded. The active mission, NORTHERN FRONT III FINAL NEWEST,
  places none of them: for that mission this pack is all table and no
  mitigation. idf_stunner is carried only by idf_dsws, which the Southern
  Watch dispatch Range Week places, so that fix is live in the campaign. The
  21 hulls carrying the Red Storm SM-6 are all from that mod; seven of them -
  both alternative Hobarts, the Ticonderoga VLS, Kansas, two Burke Flight IIIs
  and Trump - appear in loose missions under integration/missions/ (AUS DEF,
  AUS INDO-PAC ESCA among them), none in either campaign. No mission places
  ko_ffg-828. The rest are fixed because the units are selectable.

  Range Week is also where the campaign would feel a live ceiling. Its
  Shahed-136 pad (3497601759's Shahed_136_white) is authored to fly no higher
  than 300 ft - MaxLoftAlt and FinalFlightPhaseAlt both 300 - which is under
  the Stunner's own 500 ft floor, left as its author set it, and under THAAD's
  20,000 ft. If test 1 shows the ceiling live, neither battery does better
  than 5% against the drones, and that mission ends the moment one of its
  launchers or radars is lost.

DELIBERATELY NOT CHANGED
  - thaad (3683253079) 20000-99000, pla_hq-19 (3789188689's #!extend over
    3733719765) 99000-495000, and the Euromod SM-3 family (usn_rim-161b/c/d),
    which SEST_Collection_Fixes floors at 150000. Dedicated ballistic-missile
    interceptors; a floor is the point. What the clamp costs the SM-3, on the
    record: automatic launch below its floor is already off
    (AutoAttackOutsideAltitudes=False), and a manual shot at anything under
    150,000 ft - the 99,000 ft tier its builder names, plan_yj21, plaaf_cm401,
    usn_cps and usn_arrw, included - is held to 5%. The 150,000 ft floor was
    the user's choice; it stays, and the build notes ask for it to be decided
    again once test 1 shows whether the ceiling is live.
  - usa_mim-14 (vanilla Nike Hercules) at 3600. Stock content, authored against
    a stock damage.ini that has always carried the clamp.
  - 3392434750's SA-21 rounds: wp_40n6 (floor 21000) and wp_48n6e3 (floor
    2900). State the consequence plainly, because an earlier draft of this file
    got it wrong: that mod ships FOUR SINGLE-ROUND TELs, not one mixed
    launcher. Its wp_sam_site_sa-21 land unit does carry all four tiers and is
    covered 20 ft to 99000 ft continuously. The Banda Front missions, the
    Indo-Pacific Land Assets showcase and Southern Watch's The Open Door put
    that site or 9M96 TELs beside their 40N6 and 48N6E3 TELs; the NORTHERN
    FRONT II and III missions and SEST NF3 - SEAD over the Shelf place
    wp_sa-21_40n6_tel and wp_sa-21_48n6e3_tel with neither. So under the
    restored clamp those launchers really are held to 5% below their floors,
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
  VeryLarge is a GLOBAL [ImpactSize] tier, and 64 winning rounds use it, of
  which only 2 are that mod's own nuclear AS-15s. Preserving the install's
  current behaviour is the reason it is kept; that is not the same as arguing
  2000.0 is correct for the 62 other rounds that share the tier, and this pack
  does not argue that.

WHAT THIS PACK HAS NOT DEMONSTRATED, AND HOW TO SETTLE IT
  Everything above is read out of the files. None of it is verified in game,
  and the repo checkers do not test behaviour - they test that references
  resolve and that load order is sane. Green checkers say the configuration is
  coherent; they say nothing about whether the SM-3 now hits.

  None of the three tests below has been run. The paired builds for test 1
  were written and never deployed, so the pack ships the 5% out-of-band
  ceiling untested.

  Three questions are inference, not measurement. Each needs a PAIRED
  comparison - the same engagement run twice, changing one thing - because a
  single engagement cannot distinguish "clamped to 5%" from "rolled badly", and
  a single hit cannot rule a 5% clamp out. Read the displayed intercept
  percentage rather than the outcome wherever the UI shows one, and repeat
  enough shots that the difference is not noise. Keep SHIPPED_IMPACT unchanged
  across every run below, or the impact tier becomes a second variable.

  1. Do missing globals already fall back to vanilla's values?
     Run tools/make_intercept_ab_builds.py. It writes two deployables that are
     byte-identical except for ammunition/damage.ini - A carries the restored
     table, B carries the Tu-95 mod's truncated one - and refuses to emit them
     unless exactly one file differs. Toggling a mod cannot do this: the
     deployable is the single consolidated SEST_Integration entry, so disabling
     it would change every SEST override at once and leaving it enabled keeps
     the restored table.

     Fire the SAME engagement under each. Use a round that inherits BOTH
     penalties and has a closed band, so the out-of-altitude clamp is not also
     in play; tools/survey_attack_altitudes.py lists 116 of them. Do NOT use the
     SM-3: it declares both InterceptSpeedPenaltyMultiplier and
     InterceptOutOfAltitudePenalty itself (SEST_Collection_Fixes sets them to
     0.01 and 0.10), so it inherits neither and cannot probe this at all.

     A difference means the deleted globals were doing something. NO difference
     is the weaker result: it means no effect under the conditions tested, not
     that the engine supplies vanilla's values. The penalty may be inactive for
     that geometry, or masked by another cap. Vary speed, aspect and target size
     before concluding anything from a null.

  2. How is a missing SIDE of an altitude band handled?
     Pick an AMRAAM (floor, no ceiling) and a Roland or Crotale VT-1 (ceiling,
     no floor). Run each as shipped, then again against a local copy that
     supplies the missing bound explicitly - a value beyond anything reachable,
     so the band covers the same space either way. Same percentage means the
     engine already treats an omitted side as open and the 69 one-sided rounds
     are safe. A jump to 5% on the as-shipped run means it does not, and those
     rounds need the missing bound written in, here, the way this pack fixes the
     SM-6.

  3. Does the clamp reach surface and land engagements?
     No air engagement can answer this, so it needs its own shot: fire a Red
     Storm SM-6 at a SHIP. That round carries SecondaryTargetType=ASuW and a
     floor this pack sets to 15 ft, above a ship's 0 ft, so if the clamp applies
     outside the air path the engagement is capped at 5% even after the fix. If
     it is, the floor has to go to 0 for rounds with a surface role, and the
     question reopens for every other round in the collection that has one.

  Separately from all three, the engagement this work started from: an SM-3
  against a ballistic target above its 150,000 ft floor, before and after the
  SEST_Collection_Fixes SM-3 changes. That is the original complaint and it is
  its own test - it does not answer question 1, because of what the SM-3
  declares.

THE ONE RESIDUAL RISK
  69 of the 360 banded rounds declare only one side - a floor and no ceiling
  (the AMRAAM, Meteor, MICA, PL-12/PL-15, R-27 and R-77 families among them,
  floors of 15 to 67 ft), or a ceiling and no floor (point-defence rounds:
  Roland, Crotale VT-1, HQ-10, ADATS, 9M340E and three PLA land-unit rounds,
  ceilings of 4000 to 30000 ft). None of vanilla's 74 banded files does this,
  so what the engine substitutes for the missing side is not settled by stock
  content.

  There is a partial argument, and it is worth being precise about how far it
  reaches. Three vanilla AAW MISSILES declare no band AT ALL - fr_super-530f,
  pla_pl-2 and pla_pl-2b - and they have shipped for years against a damage.ini
  where the clamp is live. If a missing altitude bound defaulted to zero they
  would be permanently held at 5%. That rules out a zero default for the
  BOTH-ABSENT case. It does NOT prove the one-absent case: an engine may well
  skip the band check entirely when neither bound is present while still
  running it, against a defaulted other side, when one is. The 69 one-sided
  rounds rest on the weaker inference that 27 mods ship them and play against a
  stock table without the breakage being noticed.

  If after installing this pack an AMRAAM or a Roland starts reading 5%, that
  inference is wrong: the fix is to add the missing side to those rounds here,
  and the diagnosis is recorded above. Question 2 under WHAT THIS PACK HAS NOT
  DEMONSTRATED is the paired test that settles it.

  The counts in this docstring come from tools/survey_attack_altitudes.py, which
  is committed so the next mods-source export can re-derive them rather than
  trust these numbers. Re-run it after any export or reorder: a new mod can move
  a band into the danger set without a single file this repo owns changing -
  which is how rok_k-sam-II joined the list.

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
ROKN = "3789208859"        # Euromod-South Korea Navy, ships rok_k-sam-II.ini

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
# 64 winning rounds carry ImpactSize=VeryLarge and only TWO are that mod's own
# (its nuclear AS-15 variants). Of the other 62 all but the Trident II
# (usn_ugm-133a, Power=100000) are conventional, among them the RBU
# rocket depth charges, the Mk46/Mk54 ASROC torpedoes, two naval mines, the
# SA-13 SAM, GBU-10/15/2, the JASSM and LRASM families, the PLA 300 mm MLRS
# rockets, and two rounds SEST itself ships (dts_agm-183a, usn_gbu-24). At
# 2000.0 the tier reads 2000 m where vanilla reads 120, 16.7x. What the engine
# does with that number beyond the comment's "diameter in meter" - lethal
# radius, damage-application extent, something else - is not established here.
#
# Kept at the donor's values, deliberately. That is already the live state of
# this install - 3395022688's damage.ini wins today - so keeping it changes
# nothing a player has, while reverting would silently change 62 other
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
# and SM-2 on the very same hulls, and in line with every other surface-launched
# SM-6 in the collection (Euromod's rim-174a/c use 10, the rim-174c with the
# same 180000 ceiling as Red Storm's C; U.S. Navy 2027's rim-174a uses 15). The
# Korean K-SAM II is a copy of the same file and takes the same value, which is
# also what the K-SAAM on its frigate uses.
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
NOT TESTED IN GAME: the paired A/B builds that would show what the engine does \
without these keys have never been run. If it already falls back to the same \
numbers, this half is inert; if not, it arms the 5%% ceiling, and SAMs with a \
high floor - the SA-21 40N6 and 48N6E3, HQ-19, THAAD and the SM-3 - are held \
to 5%% against anything below it. That mod's VeryLarge impact tier is carried \
forward unchanged so its own content still works. Ships with the overrides \
that make restoring the table safe: \
Red Storm Arsenal's SM-6 family (usn_rim_174a/b/c) and the Korean K-SAM II \
(rok_k-sam-II), a copy of the same file, drop their 70,000 ft engagement floor \
to %(sm6)s ft, matching the ESSM and SM-2 that mod puts on the same hulls and \
in line with every other SM-6 in the collection, and David's Sling \
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
def lower_floor(donor, name, header):
    """One area SAM's 70,000 ft floor down to SM6_FLOOR, and nothing else."""
    sole_provider(f"ammunition/{name}.ini", donor)
    t = read(donor, f"ammunition/{name}.ini")

    # If this stops being a general-purpose round with surface and shore
    # roles, the contradiction that proves the floor wrong is gone.
    for key, value in (("TargetType", "AAW"), ("SecondaryTargetType", "ASuW"),
                       ("LandAttackCapability", "ShoreTargetsOnly")):
        if not re.search(rf"^{key}={value}(\s|$)", t, re.M):
            sys.exit(f"{name}: no longer {key}={value} - re-verify that the "
                     "70000 ft floor is still wrong before overriding it")
    t = edit(t, r"^MinAttackAltitude=70000(\s)", rf"MinAttackAltitude={SM6_FLOOR}\1",
             1, name)
    write(f"ammunition/{name}.ini", t, header)
    return name


def build_sm6():
    """Red Storm Arsenal's SM-6 trio: a 70,000 ft floor on a multi-role SAM."""
    built = []
    for variant in ("a", "b", "c"):
        name = f"usn_rim_174{variant}"
        built.append(lower_floor(
            REDSTORM, name,
            f"SEST Intercept Model - base: {REDSTORM}'s {name}.ini, one delta:\n"
            f"MinAttackAltitude 70000 -> {SM6_FLOOR} ft, on the comparators alone:\n"
            "every other surface-launched SM-6 in the collection floors at 10 or 15 ft\n"
            "(Euromod's usn_rim-174c, with the Red Storm C's 180000 ft ceiling, at 10),\n"
            "this mod's own ESSM and SM-2 use 15 on the same hulls, and 70000 is\n"
            "210x the highest floor any stock round with a surface role uses. NOT on\n"
            "the round's anti-ship and shore roles: 24 of the 25 distinct floors among\n"
            "the 138 such rounds are above zero, so a non-zero floor there is normal,\n"
            "and 15 is above a ship's 0 ft too. Matters because this pack restores the\n"
            "5% clamp; whether that clamp reaches surface engagements is untested."))
    return built


def build_ksam2():
    """Euromod-South Korea Navy's K-SAM II: the same file, the same floor."""
    name = "rok_k-sam-II"
    t = read(ROKN, f"ammunition/{name}.ini")
    # The case for this override is that the file is the Red Storm SM-6 under
    # another name. If it stops matching that round's band and reach, the
    # comparators above no longer carry over and the floor needs its own case.
    for key, value in (("MaxAttackAltitude", "130000"), ("MaxLaunchRange", "260.0")):
        if not re.search(rf"^{key}={re.escape(value)}(\s|$)", t, re.M):
            sys.exit(f"{name}: no longer {key}={value} like {REDSTORM}'s usn_rim_174a - "
                     "re-verify that it is still the SM-6 copy before overriding it")
    return [lower_floor(
        ROKN, name,
        f"SEST Intercept Model - base: {ROKN}'s {name}.ini, one delta:\n"
        f"MinAttackAltitude 70000 -> {SM6_FLOOR} ft. The file is Red Storm Arsenal's\n"
        "usn_rim_174a under another name - the same 70000 ft floor, 130000 ft ceiling,\n"
        "anti-ship and shore roles and 260 nm reach - and its author calls it the\n"
        "'SM-2 ver.': an area SAM, not a high-altitude interceptor. It takes the SM-6\n"
        f"fix, {SM6_FLOOR} ft, which is also what the K-SAAM on the same frigate uses. It\n"
        "is ko_ffg-828's only area SAM; with this pack's restored 5% clamp and the old\n"
        "floor it would be capped at 5% against everything below 70,000 ft.")]


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
    rounds = build_sm6() + build_ksam2() + build_stunner()

    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)}")
    print(f"  ammunition/damage.ini: restored {len(restored)} global intercept keys "
          f"dropped by {TU95}")
    print(f"  + {len(rounds)} round override(s) the restored clamp requires - "
          f"{', '.join(rounds)}")


if __name__ == "__main__":
    main()
