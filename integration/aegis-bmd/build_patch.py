#!/usr/bin/env python3
"""Build SEST Aegis BMD: repairs the Euromod SM-3 family (RIM-161B/C/D).

Two defects, found while diagnosing a RIM-161D SM-3 Block IIA fired from an
Arleigh Burke Flight III that flew oddly, showed a very long range ring and
almost never hit anything.

1. THE SM-3 ALTITUDE FLOOR IS AN OUTLIER THAT PENALISES EVERY SHOT.  All three
   variants declare MinAttackAltitude=220000 ft (67 km).  The floor does not
   veto the shot, it degrades it (docs/design-notes.md), so the ship fires and
   then eats the penalty: with the round's own InterceptOutOfAltitudePenalty at
   0.50, the grade its own comment calls "poor", nearly every engagement is
   scored out-of-altitude however good the KillProbability (0.85 on the IA and
   IB, 0.90 on the IIA).  220,000 ft is 2.2x the highest floor any other round
   in the collection uses.  It drops to 100000 ft; see MIN_ATTACK_ALT.

   The same condition gates vanilla's InterceptChanceOutOfAltitudeOverride=0.05,
   a HARD 5% ceiling on any out-of-altitude intercept.  When this pack was first
   written that key was suppressed collection-wide; SEST_Intercept_Model now
   restores it (see THE DEFERRED FIX below), so the clamp is live and this floor
   is what keeps the SM-3 out from under it.

2. THE FLIGHT MODEL LIVES IN A CHAINLOADER-ONLY FILE.  The base files ship with
   MaxLoftAngle, LaunchTurnRate and TimeLimited commented out and a stub seeker
   (8 nm terminal handover, 10 nm / 30 deg IR seeker).  The real values live in
   mods-source/3784474738/ammunition_overwrite/usn_rim-161*_OVWR.ini, which
   only applies if the Anchor Chain preloader is installed - and this repo
   records that install as never verified (data/mod-catalog.json's
   known_missing_dependencies, docs/setup-runbook.md Phase 1).  Every value
   restored here is copied from that overwrite, so the round flies identically
   whether or not the chainloader is present.  Nothing is invented.

Deliberately NOT changed, and why:
  - MaxAttackAltitude (1,640,000 ft on B/C, 3,000,000 ft on D).  It is far
    above anything the round can climb to, but a ceiling that never triggers is
    harmless; lowering it would create a NEW out-of-altitude clamp for high
    targets.  Unrealistic but inert.
  - MaxLoftAlt=300000.0.  Changing how high the round climbs is a flight-model
    rewrite, not a defect repair, and it is the author's value across all three.
  - MaxVelocity=8747 (D).  The declared motor delivers about 7660 kt, so the
    round never reaches it.  That shortfall is the author's house style across
    the whole Euromod ammunition set, not a D-specific bug.
  - The Anchor Chain overwrite's own extension keys (NumberOfStages,
    OptimalTargetDist, AutoAttackBelowMinAltitude/AboveMaxAltitude).  They have
    no reader without the chainloader and the overwrite still supplies them
    with it, so duplicating them here would buy nothing.

THE DEFERRED FIX - the global intercept table, NOT shipped here.
  ammunition/ is a whole-file override (docs/design-notes.md), and the
  Tu-95/AS-15 mod (3395022688) ships an ammunition/damage.ini built on a
  pre-0.8.x copy.  It is the only other damage.ini in the tree, so it wins over
  vanilla's and silently deletes eight global keys from the WHOLE collection:
  InterceptOutOfAltitudePenalty, InterceptSpeedPenaltyMultiplier,
  InterceptChanceOutOfAltitudeOverride and the five InterceptSizeBonus* values.
  Its only intended edit is VeryLarge 120 -> 2000 / VeryLargeDecalScale 3 ->
  1000 - a global [ImpactSize] tier, not the "more realistic nuke" its
  description claims.  Restoring vanilla's table with those two values carried
  forward is a two-line merge and was written, tested and then deliberately
  pulled back out of THIS pack, because restoring the table ARMS the 5% clamp
  collection-wide and that needed surveying first:

    - Red Storm Arsenal's SM-6 family (3413868677's usn_rim_174a/b/c, note the
      UNDERSCORE - different ids from Euromod's hyphenated rounds, uncontested,
      loaded by 21 vessel files) declares MinAttackAltitude=70000.  Arming the
      clamp caps all three at 5% against every aircraft and anti-ship missile
      below 70,000 ft, and none of them sets AutoAttackOutsideAltitudes, so
      Aegis would keep firing into the clamp.
    - 3558173926's idf_stunner.ini writes MaxAttackAltitude=51,000 with a
      thousands separator.  How the parser reads that decides whether its band
      is 500-51000 or the empty 500-51.
    - 61 rounds across the collection declare only one side of the band
      (fr_mica-em/ir.ini Min-only, and others; the count is alias-aware, so
      usn_rim-174b is NOT one of them - it inherits its floor from
      usn_rim-174a).  No vanilla file does this, so what the engine defaults
      the missing side to is unknown and cannot be settled from the files.

  Landing it safely needs those three answered first, and the survey belongs in
  its own pack with its own overrides - not smuggled in behind an SM-3 fix.
  That survey was done and the table now ships in SEST_Intercept_Model
  (integration/intercept-model/), together with the SM-6 and Stunner overrides
  it needs.  Read that builder for what arming the clamp actually changes.

Usage (repo root):  python3 integration/aegis-bmd/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
OUT = Path(__file__).resolve().parent / "SEST_Aegis_BMD"

EUROMOD = "3629144864"        # Euromod - Main Pack, ships the SM-3 family
OVERWRITE = "3784474738"      # Euromod - Anchorchain Expansion, ships the _OVWR files

# The new engagement floor, in feet, for all three SM-3 variants.
#
# 100,000 ft is where the collection's own data draws the line, not a round
# number picked for comfort.  A sweep of all 2108 ammunition files found that
# every offensive round topping out between 100,000 and 220,000 ft is ballistic
# or boost-glide (Iskander, JL-3, R-39, R-29RMU, air-launched YJ-21, PrSM), and
# that NO air-breathing cruise missile or anti-ship missile anywhere in the
# collection exceeds 98,000 ft - the Zircon (3597650470's rfn_3m22.ini) tops
# that list.  So a 100,000 ft floor excludes every non-ballistic threat in the
# game by physics alone, on top of the CanNotAttackTypes=Aircraft,Helicopter
# exclusion the files already carry.  The round cannot become a general SAM.
#
# It also lands on two independent in-collection precedents:
#   - THAAD (3683253079/ammunition/thaad.ini) runs 20,000-99,000, so 100,000
#     hands off cleanly one thousand feet above where THAAD stops.
#   - HQ-19 (3733719765/ammunition/pla_hq-19.ini), the red-side midcourse
#     exo-atmospheric interceptor and the closest analogue SM-3 has here, runs
#     99,000-495,000.  Its author put the floor in exactly the same place.
# Against those, 220,000 is 2.2x the highest floor anyone else in the collection
# uses and 61x the largest value stock vanilla contains anywhere (3,600 ft, on
# usa_mim-14.ini).  It is an outlier, not a convention.
#
# What it buys, concretely: the usable band becomes 100,000 up to the round's
# own 300,000 ft loft ceiling instead of a 80,000 ft sliver.  The Iskander
# (apex 165,000, and the closest ballistic threat to the task force in the
# active mission), the DF-21 terminal leg (200,000), DF-15B (120,000), the
# air-launched YJ-21 (apex 180,000) and the upper part of the YJ-17/YJ-20
# terminal dives all come inside it.  The DF-26B terminal leg (270,000) and both
# PLAN glide-vehicle cruise legs already worked and still do.
#
# The trade-off, stated plainly: SM-3 costs AmmoPoints=9000 against 8000 for
# SM-6 Block IB and 4500 for PAC-3 MSE, and this puts it in-band alongside both
# across roughly 100,000-180,000 ft.  An Aegis ship carrying all three may spend
# the expensive round where a cheaper one would have done.  That is the price of
# the fix, and it is worth paying: the alternative is the status quo, where a
# nominally 0.90-Pk interceptor is scored out-of-altitude against most of the
# ballistic threats it was loaded to stop - and would be hard-clamped to 0.05
# against them the moment the global intercept table is repaired.
MIN_ATTACK_ALT = 100000

# InterceptOutOfAltitudePenalty.  The base files' own comment grades the scale
# "0.20 is excellent ... 0.50 is poor".  B and D ship 0.50, C ships 1.10 which
# is off the documented scale entirely.  Euromod's own BMD round (usn_pac3_mse)
# uses 0.10, so all three are brought onto that.
OUT_OF_ALT_PENALTY = "0.10"

# LiftFactor is absent from all three SM-3 files, so they fly to 91 km on the
# engine default.  The key's own comment in usn_pac3_mse.ini reads "default is
# 0.005 ... lower values improve lift characteristics and are less impacted by
# altitude".  Ten other Euromod surface-to-air rounds set it; the PAC-3 MSE, the
# closest analogue by role and author, uses 0.0025.
LIFT_FACTOR = ("LiftFactor=0.0025				// default is 0.005, defines the extra drag "
               "at high altitudes/low speeds due to the increase AOA from lift loss, "
               "lower values improve lift characteristics and are less impacted by altitude")

INFO_INI = """\
[Language_en]
Name=SEST Aegis BMD
Description=Repairs the Euromod SM-3 family. Drops the RIM-161B/C/D engagement \
floor from 220,000 to %(floor)s ft, an outlier 2.2x higher than any other \
interceptor in the collection that had nearly every SM-3 shot scored \
out-of-altitude; folds the Anchor Chain overwrite's flight model (loft angle, \
launch turn rate, time limit, 5 s initial phase, 50 nm terminal handover, \
100 nm / 90 deg seeker) into the base files so the missiles fly correctly \
without the unverified preloader; corrects the Block IIA's 1500 nm declared \
range to the 729 nm its own speed and flight time allow, which also un-breaks \
the drag model derived from it; returns its TypicalTargetAlt and speed penalty \
to the family values; and gives all three a LiftFactor. Generated by \
integration/aegis-bmd/build_patch.py; must load above every workshop mod.

[Compatibility]
ApproximateVersion=0.8.2
""" % {"floor": f"{MIN_ATTACK_ALT:,}"}


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


def commented_out(text, key):
    """Is `key` present but commented? Euromod uses BOTH ';' and '#' for this -
    usn_rim-161c.ini comments LaunchTurnRate with '#' while its siblings use
    ';' - so anything that looks for only one marker silently misses the other."""
    return re.search(rf"^[;#]{re.escape(key)}=[^\n]*$", text, re.M)


def uncomment(text, key, value, ctx):
    """Activate a key the donor ships commented out. Fails if the key is already
    live (the donor fixed it upstream - drop the edit) or absent."""
    if re.search(rf"^{re.escape(key)}=", text, re.M):
        sys.exit(f"{ctx}: {key} is now live in the donor - drop this edit")
    m = commented_out(text, key)
    if not m:
        sys.exit(f"{ctx}: no commented {key}= line in donor - rebase this fix")
    tail = m.group(0).split("//", 1)
    comment = ("              //" + tail[1]) if len(tail) > 1 else ""
    return text[:m.start()] + f"{key}={value}{comment}" + text[m.end():]


def insert_after(text, anchor, line, ctx):
    """Add a key the donor does not define at all, anchored to a known line."""
    key = line.split("=", 1)[0]
    if re.search(rf"^{re.escape(key)}=", text, re.M):
        sys.exit(f"{ctx}: donor now defines {key} - drop this edit")
    if commented_out(text, key):
        sys.exit(f"{ctx}: donor now ships {key} commented out - uncomment it instead "
                 "of inserting, or the output carries two declarations")
    return edit(text, rf"^({re.escape(anchor)}[^\n]*)$", r"\1" + "\n" + line, 1, ctx)


# --------------------------------------------------------------------- SM-3
# Values taken verbatim from the matching _OVWR file in 3784474738 so the round
# behaves the same whether or not the Anchor Chain preloader is installed.
OVWR_VALUES = {
    "MaxLoftAngle": "90.0",
    "LaunchTurnRate": "5",
    "InitialFlightPhaseDuration": "5",
    "TerminalApproachDist": "50.0",
    "SeekerFOV": "90",
    "SeekerPassiveRange": "100",
}


def check_overwrite_still_agrees(variant):
    """The whole point of the flight-model half of this pack is that our values
    match the chainloader overwrite exactly. If that mod re-tunes, we must too."""
    ovwr = read(OVERWRITE, f"ammunition_overwrite/usn_rim-161{variant}_OVWR.ini")
    for key, value in OVWR_VALUES.items():
        # (?![\d.]) and not (\D|$): '.' is a non-digit, so the loose form would
        # accept an upstream retune of LaunchTurnRate=5 to 5.5 as a match.
        if not re.search(rf"^{re.escape(key)}={re.escape(value)}(?![\d.])", ovwr, re.M):
            sys.exit(f"usn_rim-161{variant}: the Anchorchain overwrite no longer sets "
                     f"{key}={value} - rebase this pack against its new value, or the "
                     "round will behave differently with and without the chainloader")
    if not re.search(r"^TimeLimited=True$", ovwr, re.M):
        sys.exit(f"usn_rim-161{variant}: overwrite no longer sets TimeLimited=True - rebase")


def build_sm3(variant, extra):
    """Shared repairs for all three RIM-161 variants, plus per-variant deltas."""
    name = f"usn_rim-161{variant}"
    check_overwrite_still_agrees(variant)
    t = read(EUROMOD, f"ammunition/{name}.ini")

    # --- 1. the 5% clamp: drop the engagement floor
    t = edit(t, r"^MinAttackAltitude=220000(\s)", rf"MinAttackAltitude={MIN_ATTACK_ALT}\1",
             1, name)
    # --- out-of-altitude penalty onto the author's own BMD value
    t = edit(t, r"^InterceptOutOfAltitudePenalty=[\d.]+(\s)",
             rf"InterceptOutOfAltitudePenalty={OUT_OF_ALT_PENALTY}\1", 1, name)

    # --- 2. fold the chainloader overwrite's flight model into the base file
    t = uncomment(t, "MaxLoftAngle", OVWR_VALUES["MaxLoftAngle"], name)
    if commented_out(t, "LaunchTurnRate"):
        t = uncomment(t, "LaunchTurnRate", OVWR_VALUES["LaunchTurnRate"], name)
    else:
        t = insert_after(t, "MaxTurnG=",
                         f"LaunchTurnRate={OVWR_VALUES['LaunchTurnRate']}"
                         "                      // Missiles like S-300 rapidly orient "
                         "themselves after launch. in degrees per second", name)
    if commented_out(t, "TimeLimited"):
        t = uncomment(t, "TimeLimited", "True", name)
    else:
        t = insert_after(t, "VelocityBleed=", "TimeLimited=True", name)
    t = edit(t, r"^InitialFlightPhaseDuration=\d+(\s)",
             rf"InitialFlightPhaseDuration={OVWR_VALUES['InitialFlightPhaseDuration']}\1",
             1, name)
    t = edit(t, r"^TerminalApproachDist=[\d.]+(\s)",
             rf"TerminalApproachDist={OVWR_VALUES['TerminalApproachDist']}\1", 1, name)
    t = edit(t, r"^SeekerFOV=\d+(\s)", rf"SeekerFOV={OVWR_VALUES['SeekerFOV']}\1", 1, name)
    t = edit(t, r"^SeekerPassiveRange=\d+(\s)",
             rf"SeekerPassiveRange={OVWR_VALUES['SeekerPassiveRange']}\1", 1, name)

    # --- 3. high-altitude lift, absent from all three
    t = insert_after(t, "VelocityBleed=", LIFT_FACTOR, name)

    t, notes = extra(t, name)
    write(f"ammunition/{name}.ini", t, notes)
    return name


def sm3_bc(t, name):
    """RIM-161B (Block IA) and RIM-161C (Block IB): their range and
    target-altitude keys are already self-consistent - 486.0 nm is exactly
    MaxVelocity x MaxFlightTime - so only the shared repairs apply. Neither is
    fielded in the active mission; both ride older Burkes and Ticonderogas."""
    return t, (
        f"SEST Aegis BMD - base: Euromod's {name}.ini, unchanged except:\n"
        f"MinAttackAltitude 220000 -> {MIN_ATTACK_ALT} ft (the old floor put every\n"
        "realistic engagement outside the band, where the round eats its own\n"
        "out-of-altitude penalty - and, on a stock install, vanilla damage.ini's\n"
        f"hard 5% clamp); InterceptOutOfAltitudePenalty -> {OUT_OF_ALT_PENALTY}, the\n"
        "value Euromod's own PAC-3 MSE uses; and the flight model the Anchor Chain\n"
        "overwrite supplies (MaxLoftAngle 90, LaunchTurnRate 5, TimeLimited, 5 s\n"
        "initial phase, 50 nm terminal handover, 100 nm / 90 deg seeker) folded in\n"
        "so the round flies correctly without the preloader. LiftFactor added.")


def sm3_d(t, name):
    """RIM-161D Block IIA: the only variant with range and calibration errors."""
    # MaxLaunchRange. The author's rule across this family is that declared range
    # equals MaxVelocity x MaxFlightTime: the B and C both declare 486.0, which is
    # exactly 5832 kt x 300 s. The D declares 1500.0 against a 728.9 nm ceiling -
    # 2.06x, the worst overshoot in all 31 Euromod ammunition files. It also drives
    # the flight model: DragCoefficient=-1 back-solves drag FROM this number, so an
    # unreachable range also makes the missile fly nearly frictionless.
    for key, value in (("MaxVelocity", "8747.0"), ("MaxFlightTime", "300"),
                       ("DragCoefficient", "-1")):
        if not re.search(rf"^{key}={re.escape(value)}(\D|$)", t, re.M):
            sys.exit(f"{name}: {key} is no longer {value} - recompute MaxLaunchRange "
                     "(MaxVelocity x MaxFlightTime / 3600) before shipping this fix")
    t = edit(t, r"^MaxLaunchRange=1500\.0(\s)", r"MaxLaunchRange=729.0\1", 1, name)

    # TypicalTargetAlt is the altitude the range solution is calibrated at. The D
    # shipped 200000, which is BELOW its own MinAttackAltitude of 220000 - the
    # calibration point sat outside the round's own engagement band. B and C both
    # use 800000.
    t = edit(t, r"^TypicalTargetAlt=200000(\s)", r"TypicalTargetAlt=800000\1", 1, name)

    # InterceptSpeedPenaltyMultiplier 0.3 vs 0.01 on both siblings - 30x the
    # penalty, applied to exactly the fast targets the Block IIA exists to kill.
    t = edit(t, r"^InterceptSpeedPenaltyMultiplier=0\.3(\s)",
             r"InterceptSpeedPenaltyMultiplier=0.01\1", 1, name)

    return t, (
        "SEST Aegis BMD - base: Euromod's usn_rim-161d.ini (SM-3 Block IIA).\n"
        f"MinAttackAltitude 220000 -> {MIN_ATTACK_ALT} ft, so realistic engagements\n"
        "stop being scored out-of-altitude; MaxLaunchRange\n"
        "1500 -> 729 nm, the figure its own MaxVelocity x MaxFlightTime allows and\n"
        "the rule its siblings follow exactly (this also un-breaks DragCoefficient=-1,\n"
        "which derives drag from it); TypicalTargetAlt 200000 -> 800000, off a\n"
        "calibration point that sat below the round's own altitude floor;\n"
        "InterceptSpeedPenaltyMultiplier 0.3 -> 0.01 to match both siblings;\n"
        f"InterceptOutOfAltitudePenalty -> {OUT_OF_ALT_PENALTY}; LiftFactor added;\n"
        "and the Anchor Chain overwrite's flight model folded in so the round flies\n"
        "the same with or without the preloader.")


def main():
    built = [build_sm3("b", sm3_bc), build_sm3("c", sm3_bc), build_sm3("d", sm3_d)]
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)}: {len(built)} SM-3 overrides - {', '.join(built)}")
    print("  (the global ammunition/damage.ini repair is deliberately NOT shipped - "
          "see THE DEFERRED FIX in this file's docstring)")


if __name__ == "__main__":
    main()
