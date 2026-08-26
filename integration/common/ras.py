"""Shared definitions for SEST Replenishment At Sea.

Sea Power ships a complete ship-to-ship replenishment mechanic and leaves it
switched off. The ONLY `[SupplySystem1]` block on any hull in vanilla or in
the 131 exported Workshop mods is commented out, on the Sacramento:

    mods-source/_vanilla/original/vessels/usn_aoe_sacramento.ini:298-316
        #[SupplySystem1]
        #SystemName=VesselSupplySystem
        ...
        #AccountableAmmunitionCategory_1=Harpoon,100

The three suppliers that DO work in vanilla are land units - `wp_car_ural`,
`usa_car_m923`, `tgt_ammo_depot_small` - using `SystemName=TruckSupplySystem`.
RE-power (3605013271, now exported under mods-source/) settles which name a
VESSEL must use: every one of its 23 field-tested ship suppliers runs
`SystemName=TruckSupplySystem` with `TargetTypes=Vessel` or `=Submarine`, and
its bundled "reference for resupply mechanics .txt" documents the TargetTypes
vocabulary as "LandUnit", "Vessel" or "Submarine". `VesselSupplySystem` - the
name in vanilla's commented Sacramento block - appears in no working file
anywhere and has no localisation, so this pack uses the proven name. It also
means vanilla's `TruckSupplySystem=Ammunition supply` label applies to the
panel for free. This module is the single source of
truth for both halves of the contract, so that
integration/replenishment/build_patch.py, integration/ran-fleet/build_fleet.py
and integration/jmsdf-mogami/build_patch.py emit identical syntax and can
never drift.

Imported the same way as common/aim424.py:

    sys.path.insert(0, str(ROOT / "integration"))
    from common.ras import SUPPLIERS, insert_supply_block, make_reloadable

----------------------------------------------------------------------------
THE FIVE GATES

A round reaches a receiver only if all of these pass. Every one is evaluated
on the SUPPLIER except the last, which is a property of the receiver's
launcher:

  1. TargetTypes vs the receiver's [General] UnitType, plus ReplenishOnly.
  2. SupplyRange (nmi), MaxOwnVelocity, MaxTargetVelocity, a free MaxTargets
     slot.
  3. The round's own AmmoPoints must not exceed MaxAmmoPoints. If the key is
     ABSENT there is no per-round cap at all - `tgt_ammo_depot_small` omits it
     deliberately, which is why the depot can reload an SA-5 (21000 points)
     that a truck capped at 200 cannot touch. This is the size gate.
  4. If the ammunition declares `SupplyCategory=X`, the supplier must list
     `AccountableAmmunitionCategory_N=X,<count>` with count > 0. A supplier
     with no category lines can never hand over a tagged round, whatever its
     pool. This is the headcount gate.
  5. The receiving LAUNCHER must be refillable: either it is fed by an
     `AssociatedMagazine=`, or it carries `ReloadableWithoutMagazine=True`.
     See make_reloadable() below - this is the gate that decides whether any
     of the other four matter.

Gates 3 and 4 are what keep this from being a cheat. Of 643 ship-referenced
ammunition files only 32 carry any SupplyCategory, and every modern VLS round
in the collection - SM-2/3/6, ESSM, RAM, Tomahawk, LRASM, NSM, Kalibr, Onyx,
Zircon, YJ-18 - carries none. Turning the Sacramento block on and stopping
there hands out 184 Tomahawks from one pool with nothing rationing them.
SEST_CATEGORIES below closes that.

----------------------------------------------------------------------------
UNITS AND TUNING

SupplyRange is NAUTICAL MILES, not statute. The ini comment says "In miles"
but the UI string settles it:

    language_en/ui.ini:2685  SupplyRange=Supply range: ${SupplyRangeInMiles} nmi.

MaxOwnVelocity is 13 kn for blue-water hulls rather than the commented
template's 6. Real underway replenishment runs at a base course and speed of
12-16 kn; 6 kn is not RAS, it is an alongside transfer. 13 is chosen because
it sits BELOW the top speed of every blue-water supplier here (Sacramento 26,
Kilauea 20, Boris Chilikin 16, Sealift Pacific 16, T2 14, Kazbek 14, Don 18),
so replenishing costs the task force its speed of advance and is a real
tactical decision rather than a free action. MaxTargetVelocity is set 3 kn
higher, preserving the supplier<receiver relationship the vanilla template
already has at 6/10, so an escort closing to station does not abort the
transfer on a momentary overspeed.

Where a hull's own top speed is below 13 the ceiling is clamped to it and the
entry says so - a gate above hull speed is a gate that never fires.

Every supplier targets "Vessel,Submarine": a boat rearms from whatever it can
reach, with the same per-hull ceilings deciding what moves - an oiler passes a
boat its point-defence and torpedo-class rounds while Kalibr-class weapons
need an ammunition ship, exactly as for surface receivers.

Both halves are now TESTED IN GAME. The comma list parses (nothing else in the
corpus uses one - RE-power picks one value per hull - so this was the riskiest
line here; had it not parsed, all 19 suppliers would have failed at once). And
a SUBMERGED boat replenishes: the engine applies no surfaced-state check, and
none can be added from the ini layer. No supply key mentions depth, and
`EnabledSurfaced` - the one candidate, 90 occurrences - is cosmetic, appearing
only in [Sail_Submerged]/[Sail_Surfaced] mesh sections to swap the
conning-tower model. Underwater resupply is therefore left ENABLED as a
deliberate house rule ("surface your boats") rather than lose surfaced rearm
along with it. To close it, drop "Submarine" from the target_types below: the
only other submarine-capable supplier in the collection is RE-power's
nv_pt_boats_docks_small, a dock, which is where a boat should rearm anyway.
"""

import re

# The divider the game's own files use above a supply system.
DIVIDER = "[---------- Supply Systems ----------]"

# Insertion anchor. Spacing differs between hulls - Sacramento writes
# "[--------------------------- Mesh definitions ---------------------------]"
# and Kilauea "[---------- Mesh definitions----------]" - so match loosely.
MESH_ANCHOR = re.compile(r"^\[-+\s*Mesh definitions", re.M)

# Last-resort anchor, for a hull that carries neither an existing supply block
# nor a mesh-definitions divider. Exactly one supplier is in that position: the
# Algol's vanilla file runs [---------- AI related ----------],
# [---------- Cargoholds ----------] and no other divider at all, and the mesh
# sections open on a bare [Models] under a ### banner. RE-power's copy of the
# hull has a divider because RE-power PUT one there, so this only became load-
# bearing when the pack switched to forking vanilla.
#
# The optional leading run is what makes the result readable rather than merely
# correct: it walks the match START back over the "### Main Model with collider
# ###" banner, so the supply block lands after the compartment data and the
# banner stays where it belongs - heading [Models], not the block just
# inserted. Vanilla's own Sacramento orders it the same way: Cargoholds, then
# Supply Systems, then the mesh.
#
# The run must OPEN on a comment line, never on a blank one, or leftmost-match
# starts it on the blank line above the banner and swallows the separator - the
# divider then butts straight up against the last compartment key. Opening it on
# the `#` leaves that blank line in place as the separator, and the block's own
# trailing blank separates it from the banner. The whole run is optional so a
# hull whose [Models] carries no banner still anchors.
MODELS_ANCHOR = re.compile(
    r"^(?:#[^\n]*\n(?:#[^\n]*\n|[ \t]*\n)*)?\[Models\]", re.M)

# An existing supply block, active or commented, including its divider.
# Stripping first means all suppliers take one code path and the emitted block
# is identical everywhere - whatever the fork source happened to carry.
#
# Only one hull still exercises it: the vanilla Sacramento's fully COMMENTED
# block (divider + # lines). The ACTIVE shape (divider + a real
# [SupplySystemN] section) is RE-power's, and it stopped reaching this regex
# when supplier_source() switched to forking vanilla. It is kept matched, and
# the multiplicity below with it, because the cost of doing so is one
# alternation and the cost of not doing so is a hull carrying two
# [SupplySystem1] sections - the exact duplicate-section defect the Zumwalt
# pack exists to fix - the day a supplier's fork source is a mod again (the
# Teide's already is).
EXISTING_BLOCK = re.compile(
    r"^\[-+ Supply Systems -+\][^\n]*\n"
    r"(?:#[^\n]*\n|\n|\[SupplySystem\d+\][^\n]*\n(?:(?!^\[).*\n)*)*",
    re.M)

# Key order is fixed and matches the vanilla template's order exactly, so a
# diff of the Sacramento against its original reads as a value change rather
# than a rewrite.
KEY_ORDER = ("SystemName", "AmmoLoadSpeed", "AmmoCapacity", "MaxAmmoPoints",
             "SupplyRange", "MaxTargets", "MaxOwnVelocity", "MaxTargetVelocity",
             "TargetTypes", "UpdateDelay")

# Two new categories, SEST_-prefixed per the repo's global-namespace rule.
# They exist because every modern heavy round carries no SupplyCategory and
# would otherwise be unrationed. They are deliberately NOT named LRASM /
# JASSM / NatoAdvancedASM etc: thirteen such names sit commented out in mod
# ammunition files and would become live orphans the moment anyone uncommented
# one.
LAND_ATTACK = "SEST_LandAttack"
LONG_RANGE_SAM = "SEST_LongRangeSAM"

# WHICH ROUNDS GET METERED IS DERIVED, NOT LISTED.
#
# A hand-written id list looked reviewable and was wrong: it caught the
# dash-named vanilla and Euromod rounds and missed Red Storm Arsenal's entire
# underscore-named parallel family - usn_rgm_109c3 alone sits in 90 launchers,
# usn_rgm_109e in 68, usn_rim_174b in 28 - so the exact failure the pack exists
# to prevent survived on the mod the pack names as the reason it is needed.
# So the rule is computed from mods-source on every build, the way
# tools/check_load_order.py computes its ordering rules: nothing to keep in
# sync, nothing to forget when a mod is added.
#
# A round is metered when ALL of these hold:
#   - some vessel references it (a round no ship carries is not our business)
#   - Type=Missile. Torpedoes and ASROC are commodity ordnance here; the ones
#     that should be counted already carry vanilla's AirTorpedo or ALWT.
#   - TargetType is ASuW or AAW. TargetType=ASW is a stand-off ASW round
#     (SS-N-14/16 and friends) and stays free, with the torpedoes.
#   - AmmoPoints >= METER_THRESHOLD
#   - it declares no SupplyCategory already - vanilla's six categories win
#   - NO aircraft hangs it on a station. Tagging a round a carrier arms from
#     its FlightDeck_ magazine would break deck rearming for it.
#   - NO land unit carries it. The three land suppliers stock no categories at
#     all, so tagging a round they service takes away the one working supply
#     path the game ships. Red Storm Arsenal's usa_tomahawk_launcher fires
#     usn_rgm-109b, which is why that round is not metered.
#
# A round is metered when its cost is STRICTLY ABOVE this. 2000 sits above
# everything meant to top up anywhere - VL-ASROC 1217, SM-2MR 1400-1768,
# Harpoon 1725, Exocet and YJ-83 1675, ESSM 500-700, RAM 126-150, every gun
# and CIWS round - and below the cheapest strike/area rounds (Otomat-family
# 2422, SM-2ER 4080, Tomahawk 4350).
METER_THRESHOLD = 2000

# TargetType -> the category it is metered under.
METER_CATEGORIES = {"ASuW": LAND_ATTACK, "AAW": LONG_RANGE_SAM}

# Rounds the rule would catch but that are deliberately left free, with the
# reason. Empty today; every exclusion the rule makes on its own is one of the
# conditions above, and the builder prints what it excluded and why.
METER_EXEMPT = {}

# Four rounds whose vanilla AmmoPoints and SupplyCategory are stripped by a
# lower-priority mod's stats stub. Restoring the vanilla bytes at tier 0 is a
# straight bug fix and is worth shipping on its own merits: the whole Euromod
# Harpoon Block II tree aliases usn_rgm-84d, so today that family costs zero
# points and carries no category at all.
RESTORE_ROUNDS = {
    "usn_rgm-84d": "3456859157",    # Mogami-class stats stub drops 1725 / Harpoon
    "usn_agm-84d": "3430135740",    # drops 1350 / Harpoon
    "wp_ss-n-12": "3395022688",     # drops 7740 / SovietAdvancedASM
    "wp_ss-n-19": "3395022688",     # drops 21000 / SovietAdvancedASM
}


def supply_spec(load, pool, rng, targets, own, target_vel, cats,
                cap=None, target_types="Vessel,Submarine", note=""):
    """Map the readable tuning names onto the game's ini keys.

    Every supply block in this repo - the ten upstream hulls, the eight clones
    and the RAN Supply-class that integration/ran-fleet owns - is built
    through this one function, so a hull can never end up with a block that
    silently omits half its keys.
    """
    return {"AmmoLoadSpeed": load, "AmmoCapacity": pool, "MaxAmmoPoints": cap,
            "SupplyRange": rng, "MaxTargets": targets, "MaxOwnVelocity": own,
            "MaxTargetVelocity": target_vel, "TargetTypes": target_types,
            "categories": cats, "note": note}


def _supplier(source, unit, nation, role, **tuning):
    spec = supply_spec(**tuning)
    spec.update(source=source, unit=unit, nation=nation, role=role)
    return spec


# MaxAmmoPoints is the size gate. Reference costs it is threaded against:
#   gun/CIWS 0.27-75, RAM 126-150, Mk46/Mk54/MU90/Stingray 460-728,
#   ESSM 500-700, VL-ASROC 1217, SM-2MR 1400-1768, Harpoon 1725,
#   C-802 1675, Tomahawk 4350, SM-2ER 4525, Mk48 ADCAP 4695,
#   SS-N-12 7740, NSM 8000, SM-6 Blk IB 8000, SM-3 9000, Onyx 5000,
#   Zircon 10000, SS-N-22 Moskit 12300, SS-N-19 Granit 21000.
SUPPLIERS = {
    # ---- vanilla hulls, engine-tagged Role=RAS ------------------------------
    "usn_aoe_sacramento": _supplier(
        "vanilla", "Sacramento-class fast combat support ship (AOE-1)", "US", "AOE",
        load=120, pool=600000, rng=1.0, targets=2, own=13, target_vel=16,
        cap=None,   # no size gate - fuel, ammunition and stores in one hull
        cats=[("Harpoon", 40), ("AirTorpedo", 60), ("ALWT", 24), (LAND_ATTACK, 24), (LONG_RANGE_SAM, 32)],
        note="two rigs plus UH-46 VERTREP; hull tops out at 26 kn"),

    "usn_ae_kilauea": _supplier(
        "vanilla", "Kilauea-class ammunition ship (AE-26)", "US", "AE",
        load=100, pool=500000, rng=1.0, targets=2, own=13, target_vel=16,
        cap=None,   # an ammunition ship is the naval tgt_ammo_depot_small
        cats=[("Harpoon", 60), ("AirTorpedo", 90), ("ALWT", 40), ("Nuclear_ASW", 4),
              (LAND_ATTACK, 40),
              (LONG_RANGE_SAM, 60)],
        note="UH-46 VERTREP; sole source of Nuclear_ASW, an orphan category today"),

    "usn_ao_t2": _supplier(
        "vanilla", "T2-class (modified) fleet oiler", "US", "AO",
        load=50, pool=60000, rng=0.5, targets=1, own=13, target_vel=16, cap=2000,
        cats=[("Harpoon", 8), ("AirTorpedo", 16)],
        note="hull tops out at 14 kn"),

    "wp_vt_boris_chilikin": _supplier(
        "vanilla", "Boris Chilikin-class (Project 1559V) replenishment oiler",
        "Soviet", "AOR",
        load=80, pool=200000, rng=0.5, targets=2, own=13, target_vel=16, cap=13000,
        cats=[("SovietAdvancedASM", 24), ("AirTorpedo", 40), (LAND_ATTACK, 16)],
        note="ceiling threaded between SS-N-22 Moskit (12300) and "
             "SS-N-19 Granit (21000): Granit's angled below-deck silos are "
             "genuinely not reloadable at sea"),

    "wp_vt_kazbek": _supplier(
        "vanilla", "Kazbek-class fleet tanker", "Soviet", "AO",
        load=50, pool=60000, rng=0.5, targets=1, own=13, target_vel=16, cap=2000,
        cats=[("AirTorpedo", 16)],
        note="no SovietAdvancedASM line on purpose - every round in that "
             "category costs 7740 or more and the 2000 ceiling blocks it anyway"),

    "wp_pb_don": _supplier(
        "vanilla", "Don-class (Project 310) submarine tender", "Soviet", "AS",
        load=60, pool=150000, rng=0.3, targets=2, own=5, target_vel=8, cap=8000,
        cats=[("SovietAdvancedASM", 12), ("AirTorpedo", 30), (LAND_ATTACK, 12)],
        note="alongside/at-anchor tender work, not underway RAS. RE-power's "
             "own Don runs TargetTypes=Submarine, the field-tested precedent "
             "for boats receiving at all"),

    "ir_aor_delvar": _supplier(
        "vanilla", "Delvar-class fleet auxiliary", "Iran", "AOR",
        load=25, pool=15000, rng=0.3, targets=1, own=8, target_vel=12, cap=2000,
        cats=[("AirTorpedo", 4), ("Harpoon", 2)],
        note="64 m coastal auxiliary, hull tops out at 11 kn; pool is about "
             "nine C-802 reloads"),

    "civ_ms_sealift_pacific": _supplier(
        "vanilla", "Sealift Pacific-class medium tanker (T-AOT, MSC)", "US", "AOT",
        load=40, pool=40000, rng=0.5, targets=1, own=13, target_vel=16, cap=2000,
        cats=[("AirTorpedo", 8)],
        note="MSC charter tanker - fuel first, ordnance incidental"),

    "usn_takr_algol": _supplier(
        "vanilla", "Algol-class fast sealift ship (T-AKR)", "US", "T-AKR",
        load=45, pool=500000, rng=0.5, targets=2, own=8, target_vel=12,
        cap=None,   # top tier: no per-round size gate
        cats=[("Harpoon", 40), ("AirTorpedo", 48), ("ALWT", 24),
              (LAND_ATTACK, 32), (LONG_RANGE_SAM, 32)],
        note="the one supplier here that is NOT Role=RAS - it is Role=Transport, "
             "an MSC fast sealift Ro-Ro. Top tier all the same, and on its own "
             "merits: at 288 m it is the LONGEST hull in this table, longer than "
             "the Sacramento, with 31 cargo slots of military materiel. "
             "Strategic sealift is precisely the thing that moves the heaviest "
             "items - so no size ceiling, and it will pass a Granit at 21000 "
             "like the ammunition ships. What it does not have is a "
             "replenishment rig, and that is where the cost sits instead of in "
             "a ceiling: 45 points/sec against an AOE's 120, and 8 kn on a hull "
             "that makes 33. It carries anything, slowly, very nearly stopped"),

    # ---- Workshop mod hull ---------------------------------------------------
    "ae_ao_teide": _supplier(
        "3630495619", "Teide-class fleet oiler (BP-11)", "Spain", "AO",
        load=80, pool=120000, rng=0.5, targets=2, own=12, target_vel=16, cap=2000,
        cats=[("Harpoon", 16), ("AirTorpedo", 24), ("ALWT", 8)],
        note="hull tops out at 12.0 kn, so the speed gate is the hull itself"),

    # ---- owned by integration/ran-fleet, patched by that builder -------------
    "ran_aor_supply": _supplier(
        "SEST_RAN_Fleet", "Supply-class AOR (A195 Supply, A304 Stalwart)",
        "Australia", "AOR",
        load=90, pool=160000, rng=0.5, targets=2, own=12, target_vel=16, cap=8000,
        cats=[("Harpoon", 16), ("AirTorpedo", 24), (LAND_ATTACK, 8),
              (LONG_RANGE_SAM, 16)],
        note="ceiling admits Tomahawk (4350), Mk48 ADCAP (4695), SM-6 Blk IB "
             "and the NSM (8000 each) and blocks SM-3 (9000): the RAN's own "
             "oiler has to be able to service the RAN's own anti-ship missile, "
             "which is what the Hobart and the Anzac actually carry. Counts are "
             "sized against the Hobart's fit of 8 Tomahawk and 8 SM-6. Teide "
             "donor hull tops out at 12.0 kn"),
}

# ---------------------------------------------------------------------------
# New modern replenishment hulls.
#
# The collection has twelve replenishment-capable hulls and all but two are
# Cold War. A modern task force therefore had nothing to replenish from, which
# made the rest of this pack close to decorative. These are NEW unit ids
# cloned from vanilla donors the way integration/ran-fleet/build_fleet.py
# clones its European donors - the donors themselves are untouched and both
# ships coexist.
#
# Donors are chosen on hull length, because the mesh is what the player sees:
#   Supply-class T-AOE-6  229 m  <- Sacramento 242 m
#   Lewis and Clark T-AKE 210 m  <- Kilauea    172 m
#   Henry J. Kaiser T-AO  206 m  <- Teide      118 m  (the weakest match, and
#                                   the only proper oiler silhouette available)
#   Mashuu-class AOE      221 m  <- Sacramento 242 m
#   Tide-class AOR        201 m  <- Sacramento 242 m
#   Type 901 Fuyu AOE     241 m  <- Sacramento 242 m  (near exact)
# ---------------------------------------------------------------------------
# The refit.
#
# A clone is its donor plus a supply block, and for five of the eight that
# donor is a 1960s Sacramento. Left alone, a 2017 Chinese replenishment ship
# sails with an SPS-40, a NATO Sea Sparrow launcher and an AN/SLQ-32 - a US
# Navy fit twenty years older than the ship, on the wrong navy. The refit
# retunes the systems to something the ship's own era and flag would carry.
#
# THE RULE IS RETUNE, NEVER RESTRUCTURE. Only three keys are ever rewritten:
# SystemName inside a [SensorSystemN] or [WeaponSystemN] section, and
# Ammunition1 inside a [WeaponMagazine*] section. Mount, Collider, Container,
# Gun, FiringArcs, MountPosition and every mesh section are the donor's and
# stay the donor's, because those name geometry that exists in the donor model
# and nowhere else. A refit therefore changes what a system DOES, never what
# it looks like - the Type 901 still shows Phalanx barrels while shooting like
# a Type 730. That is the same trade the donor choice already makes.
#
# ONE EXCEPTION, and it is the sharp edge here: a MISSILE LAUNCHER's SystemName
# is not purely behavioural. [MK29] declares eight AttachmentPositions and
# [HQ-10_24] twenty-four, and those are mesh-relative coordinates saying where
# each missile is drawn on the mount. Swap one for the other and the rounds
# render at another launcher's geometry on a mount that has eight rails. So
# launchers keep their SystemName and are refitted through the MAGAZINE
# instead - the Type 901 fires HQ-10 from a Mk29, the Tide fires Sea Ceptor
# from one. Guns and sensors carry no such geometry ([MK15] and [Type_730] are
# rates, arcs and effects) and swap freely.
#
# The mesh sections are left alone even where they carry a SystemName of their
# own - vanilla's [SPS_40] block says SystemName=SPS-40 next to its Mesh= line,
# and after a refit that no longer names any system the ship has. Measured
# before deciding: across every vanilla vessel, of the mesh sections a sensor
# actually mounts, 757 carry NO SystemName at all, 129 carry a matching one,
# and 11 carry one that disagrees - the Ticonderoga's SPS-55 mounts a mesh
# whose SystemName is "usn_cg_ticonderoga_sps_55", a mesh name, and the Ivan
# Rogov's three Palm Fronds mount meshes labelled Nav_Radar. The link the
# engine uses is Mount=, pointing at the section; the key is decorative and
# vanilla is not consistent about it. So it stays as the donor wrote it.
#
# Each slot is a PREFERENCE LIST, not a name, and the builder picks the first
# entry defined by vanilla or an exported mod (see resolve_system in
# build_patch.py). Two reasons. The good radars live in Red Storm Arsenal,
# Euromod and the PLAN packs, and hard-coding one would silently break the
# ship for anyone who does not run that mod - the pack's dependency story is
# "patches whatever it finds", and this keeps it true. And every list ends in
# a name vanilla itself defines, so the floor is always reachable.
#
# A key is either a bare SystemName, which matches every section carrying it,
# or "SensorSystem2:Nav_Radar", which matches only that section. The scoped
# form exists for the Boris Chilikin, which carries three identical Nav_Radar
# entries where the real Type 903A has one search set and two navigation sets.
BLUE = "BLUE"
RED = "RED"

# Fallback tails, spelled once. Every one of these names is defined by vanilla.
_US_ESM = ["AN/SLQ-32A_ESM", "AN/SLQ-32_ESM"]
_US_ECM = ["AN/SLQ-32(V)6", "AN/SLQ-32"]
_US_CIWS = ["MK15B", "eu_MK15B", "MK15"]
_ESSM = ["usn_rim-162", "usn_rim-162a", "usn_rim-7m"]

CLONES = {
    "usn_taoe_supply": {
        "donor": ("vanilla", "usn_aoe_sacramento"),
        "class_name": "Supply-class T-AOE (stand-in)",
        "hull_code": "T-AOE", "bloc": BLUE,
        "short": "Supply",
        "nation": "US", "flag": "flag_us",
        "service": "1994|2060",
        "refit": {
            # AOE-6 really did carry SPS-49 and SLQ-32, so this is the ship's
            # own fit rather than a modernisation: the Sacramento donor is
            # simply a generation behind it. ESSM in the Mk29 is the one
            # liberty - the launcher is real, the round is the current one.
            "SPS-40": ["AN/SPS-49(V)5", "SPS-49V5"],
            "SPS-67": ["AN/SPQ-9B", "SPQ-9"],
            "AN/SLQ-32_ESM": _US_ESM,
            "AN/SLQ-32": _US_ECM,
            "MK15": _US_CIWS,
            "@usn_rim-7m": _ESSM,
        },
        "desc": ("Military Sealift Command fast combat support ship - fuel, ammunition, "
                 "provisions and spares in one hull, built to keep pace with a carrier "
                 "strike group.\\n\\nStand-in hull: the Sacramento-class stands in for the "
                 "Supply-class (no T-AOE-6 mesh in the collection) - comparable length, "
                 "same role, same two-rig plus VERTREP delivery."),
        "hulls": [("T-AOE 6 USNS Supply", "Supply"),
                  ("T-AOE 7 USNS Rainier", "Rainier"),
                  ("T-AOE 8 USNS Arctic", "Arctic"),
                  ("T-AOE 10 USNS Bridge", "Bridge")],
        "supply": supply_spec(load=130, pool=700000, rng=1.0, targets=2, own=13,
                       target_vel=16, cap=None,
                       cats=[("Harpoon", 40), ("AirTorpedo", 60), ("ALWT", 32),
                             (LAND_ATTACK, 40), (LONG_RANGE_SAM, 48)],
                       note="no size gate - the modern counterpart of the Sacramento"),
    },
    "usn_take_lewis_clark": {
        "donor": ("vanilla", "usn_ae_kilauea"),
        "class_name": "Lewis and Clark-class T-AKE (stand-in)",
        "hull_code": "T-AKE", "bloc": BLUE,
        "short": "Lewis and Clark",
        "nation": "US", "flag": "flag_us",
        "service": "2006|2060",
        "refit": {
            # The Kilauea donor's two Mk33 3"/50 are a 1950s weapon; a T-AKE
            # that carries a gun at all would carry the Mk110 the LCS and the
            # Constellations carry. Same mounts, same arcs, modern round.
            "SPS-67": ["AN/SPQ-9B", "SPQ-9"],
            "AN/SLQ-32_RWR": ["AN/SLQ-32A_ESM", "AN/SLQ-32_RWR"],
            "MK33": ["eu_Bofors_57mm_L/70_Mk3", "MK33"],
            "MK15": _US_CIWS,
            "@usn_cal_3in50": ["bofors_cal_57mm_3P", "usn_cal_3in50"],
        },
        "desc": ("Military Sealift Command dry cargo and ammunition ship, the replacement "
                 "for the Kilauea-class AE and the Mars-class AFS.\\n\\nStand-in hull: the "
                 "Kilauea-class stands in for the T-AKE. Deepest ordnance magazine in the "
                 "pack and no per-round size limit."),
        "hulls": [("T-AKE 1 USNS Lewis and Clark", "Lewis and Clark"),
                  ("T-AKE 2 USNS Sacagawea", "Sacagawea"),
                  ("T-AKE 6 USNS Amelia Earhart", "Amelia Earhart"),
                  ("T-AKE 11 USNS Washington Chambers", "Washington Chambers")],
        "supply": supply_spec(load=110, pool=550000, rng=1.0, targets=2, own=13,
                       target_vel=16, cap=None,
                       cats=[("Harpoon", 48), ("AirTorpedo", 72), ("ALWT", 40),
                             (LAND_ATTACK, 48), (LONG_RANGE_SAM, 56)],
                       note="no size gate; carries no Nuclear_ASW - a T-AKE does not"),
    },
    "usn_tao_kaiser": {
        "donor": ("3630495619", "ae_ao_teide"),
        "class_name": "Henry J. Kaiser-class T-AO (stand-in)",
        "hull_code": "T-AO", "bloc": BLUE,
        "short": "Kaiser",
        "nation": "US", "flag": "flag_us",
        "service": "1986|2055",
        "refit": {
            # The smallest refit in the pack, because the Teide donor is the
            # smallest fit: optics, one radar and a single 40 mm mount. The
            # Bofors goes L/60 to L/70 - same calibre, so the donor's 40 mm
            # magazine still feeds it and no round swap is needed.
            "Optics": ["AdvancedOptics", "Optics"],
            "Nav_Radar": ["AN/SPQ-9B", "SPQ-9", "Nav_Radar"],
            "Bofors_L/60_MkIX": ["eu_Bofors_40mm_L70", "Bofors_L/60_MkIX"],
        },
        "desc": ("Military Sealift Command fleet replenishment oiler - the workhorse that "
                 "keeps a battle group fuelled, with limited ordnance transfer."
                 "\\n\\nStand-in hull: the Spanish Teide-class oiler stands in for the "
                 "Kaiser. Fuel first: the 2000-point ceiling passes guns, CIWS, ESSM, RAM, "
                 "SM-2MR, Harpoon and ship torpedoes and stops at every strike round."),
        "hulls": [("T-AO 187 USNS Henry J. Kaiser", "Henry J. Kaiser"),
                  ("T-AO 189 USNS John Lenthall", "John Lenthall"),
                  ("T-AO 193 USNS Walter S. Diehl", "Walter S. Diehl"),
                  ("T-AO 204 USNS Rappahannock", "Rappahannock")],
        "supply": supply_spec(load=60, pool=80000, rng=0.5, targets=2, own=12,
                       target_vel=16, cap=2000,
                       cats=[("Harpoon", 8), ("AirTorpedo", 16)],
                       note="Teide donor hull tops out at 12.0 kn"),
    },
    "jmsdf_aoe_mashuu": {
        "donor": ("vanilla", "usn_aoe_sacramento"),
        "class_name": "Mashuu-class AOE (stand-in)",
        "hull_code": "AOE", "bloc": BLUE,
        "short": "Mashuu",
        "nation": "Japan", "flag": "flag_civ_japan",
        "service": "2004|2060",
        "refit": {
            # Japanese kit throughout: OPS air and surface search, NOLQ-2 for
            # the EW suite. Phalanx and ESSM stay American because the JMSDF
            # buys them American.
            "SPS-40": ["eu_OPS-48", "OPS-50", "SPS-49V5"],
            "SPS-67": ["eu_OPS-20", "OPS-17", "SPS-67"],
            "AN/SLQ-32_ESM": ["eu_NOLQ-2_ESM", "AN/SLQ-32_ESM"],
            "AN/SLQ-32": ["eu_NOLQ-2_ECM", "AN/SLQ-32"],
            "MK15": _US_CIWS,
            "@usn_rim-7m": _ESSM,
        },
        "desc": ("Japan Maritime Self-Defense Force fast combat support ship, the largest "
                 "auxiliary the JMSDF operates.\\n\\nStand-in hull: the Sacramento-class "
                 "stands in for the Mashuu (221 m against 242 m, same AOE role)."),
        "hulls": [("AOE-425 JS Mashuu", "Mashuu"),
                  ("AOE-426 JS Omi", "Omi")],
        "supply": supply_spec(load=100, pool=250000, rng=0.8, targets=2, own=13,
                       target_vel=16, cap=5000,
                       cats=[("Harpoon", 24), ("AirTorpedo", 40), ("ALWT", 16),
                             (LAND_ATTACK, 12), (LONG_RANGE_SAM, 24)],
                       note="ceiling admits Tomahawk and Type 12; blocks SM-3 and SM-6 IB"),
    },
    "rn_aor_tide": {
        "donor": ("vanilla", "usn_aoe_sacramento"),
        "class_name": "Tide-class AOR (stand-in)",
        "hull_code": "AOR", "bloc": BLUE,
        "short": "Tide",
        "nation": "UK", "flag": "flag_rn",
        "service": "2017|2060",
        "refit": {
            # Artisan on the air-search mount, SharpEye on the surface set and
            # UAT for the EW suite - the RFA's own equipment. Sea Ceptor in the
            # Mk29 is the deliberate liberty: a real Tide carries Phalanx and
            # nothing else, and an unarmed hull is a free kill in a scenario.
            "SPS-40": ["eu_Type_997", "eu_SMART-S_Mk2", "SPS-49V5"],
            "SPS-67": ["eu_SharpEye_X", "Type1007", "SPS-67"],
            "AN/SLQ-32_ESM": ["eu_Thales_UAT", "AN/SLQ-32_ESM"],
            "AN/SLQ-32": ["eu_type_1048", "AN/SLQ-32"],
            "MK15": ["eu_MK15B", "MK15B", "MK15"],
            "@usn_rim-7m": ["mbda_camm", "rn_seaceptor"] + _ESSM,
        },
        "desc": ("Royal Fleet Auxiliary fast fleet tanker supporting the Queen Elizabeth "
                 "carrier strike group.\\n\\nStand-in hull: the Sacramento-class stands in "
                 "for the Tide-class (201 m against 242 m)."),
        "hulls": [("A136 RFA Tidespring", "Tidespring"),
                  ("A137 RFA Tiderace", "Tiderace"),
                  ("A138 RFA Tidesurge", "Tidesurge"),
                  ("A139 RFA Tideforce", "Tideforce")],
        "supply": supply_spec(load=90, pool=180000, rng=0.6, targets=2, own=13,
                       target_vel=16, cap=5000,
                       cats=[("Harpoon", 16), ("AirTorpedo", 32),
                             (LAND_ATTACK, 8), (LONG_RANGE_SAM, 16)],
                       note="a tanker first, so a smaller pool than the AOEs"),
    },
    "plan_aor_type901": {
        "donor": ("vanilla", "usn_aoe_sacramento"),
        "class_name": "Type 901 Fuyu-class AOE (stand-in)",
        "hull_code": "AOE", "bloc": RED,
        "short": "Fuyu",
        "nation": "China", "flag": "flag_plan",
        "service": "2017|2060",
        "refit": {
            # The whole US fit goes: Type 382 and Type 364 for search, Type
            # 347G on the illuminator mounts, RJZ-726 for EW, and Type 730 on
            # both CIWS mounts. The 20 mm magazine has to go to 30 mm with
            # them or the Type 730s have nothing to fire - exactly the kind of
            # half-swap this table exists to make impossible to forget.
            #
            # The Mk29 KEEPS its SystemName and takes HQ-10 rounds instead.
            # Swapping it to HQ-10_24 was the obvious move and is the one
            # thing a launcher SystemName must not do: [MK29] declares eight
            # AttachmentPositions and [HQ-10_24] twenty-four, and those are
            # mesh-relative coordinates for where the missiles are DRAWN. On a
            # Mk29 box that is twenty-four missiles floating at another
            # launcher's coordinates. Guns are safe to swap - [MK15] and
            # [Type_730] are rates, arcs and effects with no geometry at all -
            # and launchers are not.
            "SPS-40": ["Type_382", "Type_364", "SPS-49V5"],
            "SPS-67": ["Type_364", "Nav_Radar"],
            "MK-95": ["Type_347G", "Type_344", "MK-95"],
            "AN/SLQ-32_ESM": ["H/RJZ-726_ESM", "AN/SLQ-32_ESM"],
            "AN/SLQ-32": ["RJZ-726_ECM", "AN/SLQ-32"],
            "MK15": ["Type_730", "Type_730_H", "MK15"],
            "@usn_rim-7m": ["pla_hq-10", "plan_hq-10", "usn_rim-7m"],
            "@usn_cal_20mm": ["plan_cal_30mm", "usn_cal_20mm"],
        },
        "desc": ("People's Liberation Army Navy fast combat support ship, built to keep "
                 "station with the Type 003 carriers and the Type 055 cruisers."
                 "\\n\\nStand-in hull: the Sacramento-class stands in for the Type 901 - at "
                 "241 m against 242 m the closest length match in the collection."),
        "hulls": [("965 CNS Hulunhu", "Hulunhu"),
                  ("967 CNS Chaganhu", "Chaganhu")],
        "supply": supply_spec(load=110, pool=400000, rng=0.8, targets=2, own=13,
                       target_vel=16, cap=9000,
                       cats=[("AirTorpedo", 40), ("SovietAdvancedASM", 12),
                             (LAND_ATTACK, 32), (LONG_RANGE_SAM, 32)],
                       note="ceiling admits YJ-18 (4800), YJ-12A (8000) and "
                            "YJ-19 (8800) and blocks Zircon (10000) and YJ-20 "
                            "(11050) - 13000 would have passed the Zircon the "
                            "note claimed it stopped"),
    },
    # --- RED -----------------------------------------------------------------
    # The two below exist because the bloc split was one-sided without them.
    # Before they were added the modern half of this table read six BLUE hulls
    # and a single Chinese one, and RED's only other options were the Boris
    # Chilikin, the Kazbek and the Don - all Cold War. A RED task force in 2025
    # had a supply ship; it did not have a modern one.
    #
    # Both are unarmed, and that is not an omission. Their donors carry no
    # weapon mounts at all, the refit rule forbids adding geometry that is not
    # in the donor mesh, and in both cases the real ship is unarmed too - the
    # Pashin has provision for two AK-630 that are not fitted, and a Type 903A
    # keeps its guns for a wartime fit. So they are what they look like:
    # replenishment hulls that need an escort.
    "plan_aor_type903a": {
        "donor": ("vanilla", "wp_vt_boris_chilikin"),
        "class_name": "Type 903A Fuchi-class AOR (stand-in)",
        "hull_code": "AOR", "bloc": RED,
        "short": "Fuchi",
        "nation": "China", "flag": "flag_plan",
        "service": "2004|2060",
        "refit": {
            # Only SensorSystem2 becomes a Type 364. The donor carries three
            # identical Nav_Radar entries and the real Type 903A carries one
            # search set and two navigation sets, so a bare "Nav_Radar" key -
            # which matches every section - would have given it three search
            # radars. This is the scoped form's whole reason for existing.
            "Optics": ["AdvancedOptics", "Optics"],
            "SensorSystem2:Nav_Radar": ["Type_364", "Nav_Radar"],
        },
        "desc": ("People's Liberation Army Navy fleet replenishment oiler - the class "
                 "that made PLAN deployments beyond the first island chain routine, and "
                 "the most numerous modern auxiliary in this table."
                 "\\n\\nStand-in hull: the Boris Chilikin-class stands in for the Type "
                 "903A (162 m against 178 m). Unarmed, like the ship it stands in for - "
                 "give it an escort."),
        "hulls": [("889 CNS Taihu", "Taihu"),
                  ("890 CNS Chaohu", "Chaohu"),
                  ("963 CNS Honghu", "Honghu"),
                  ("964 CNS Luomahu", "Luomahu")],
        "supply": supply_spec(load=80, pool=220000, rng=0.6, targets=2, own=13,
                       target_vel=16, cap=5000,
                       cats=[("AirTorpedo", 32), ("SovietAdvancedASM", 8),
                             (LAND_ATTACK, 16), (LONG_RANGE_SAM, 24)],
                       note="a tanker first, so a smaller pool and a lower ceiling "
                            "than the Type 901: it passes YJ-18 and HHQ-16 and "
                            "stops at YJ-12A"),
    },
    "rfn_aor_pashin": {
        "donor": ("vanilla", "wp_vt_kazbek"),
        "class_name": "Project 23130 Akademik Pashin (stand-in)",
        "hull_code": "VT", "bloc": RED,
        "short": "Pashin",
        "nation": "Soviet", "flag": ["RFN_Flag.png", "flag_soviet"],
        "service": "2021|2060",
        "refit": {
            # The thinnest refit here, because the Kazbek donor is optics and
            # one radar. MR-760 is a real Russian search set and a genuine
            # upgrade on a bare navigation radar; there is nothing else on the
            # hull to retune.
            "Optics": ["AdvancedOptics", "Optics"],
            "Nav_Radar": ["rfn_mr760", "Nav_Radar"],
        },
        "desc": ("Russian Navy medium sea tanker, the first purpose-built replenishment "
                 "ship Russia has commissioned since the Soviet era and the only modern "
                 "one it has.\\n\\nStand-in hull: the Kazbek-class stands in for Project "
                 "23130 (145 m against 130 m). Unarmed, like the ship it stands in for - "
                 "give it an escort."),
        "hulls": [("Akademik Pashin", "Pashin")],
        "supply": supply_spec(load=55, pool=90000, rng=0.5, targets=1, own=12,
                       target_vel=14, cap=2000,
                       cats=[("AirTorpedo", 16), ("SovietAdvancedASM", 4)],
                       note="a fuel-first tanker with one rig: the 2000 ceiling stops "
                            "every Soviet heavy ASM, which is what the Boris Chilikin "
                            "is for"),
    },
}


# A system entry: [SensorSystem2], [WeaponSystem1], [WeaponSystem1Gun]. The
# trailing [A-Za-z]* is the same loadout-suffix lesson _WEAPON_BLOCK learned -
# the Teide's only gun lives in [WeaponSystem1Gun], and a header-only match
# would have refitted nothing on the Kaiser while reporting success.
_SYSTEM_SECTION = re.compile(
    r"^\[((?:Sensor|Weapon)System\d+[A-Za-z]*)\][^\n]*\n(?:(?!^\[).*(?:\n|$))*", re.M)
_MAGAZINE_SECTION = re.compile(
    r"^\[(WeaponMagazine[^\]\n]*)\][^\n]*\n(?:(?!^\[).*(?:\n|$))*", re.M)
# Captures the whole remainder of the line, comment and all, because a system
# name can CONTAIN a slash - AN/SLQ-32_ESM, Bofors_L/60_MkIX, H/RJZ-726_ESM.
# The first version excluded "/" from the value to keep "//" comments out and
# so matched none of those three, which is how the Sacramento reported its ESM
# slot as missing from a file that plainly had it. The comment is split off in
# code instead, where "//" can be told apart from a name.
_VALUE = r"^{}[ \t]*=[ \t]*([^\n]*)$"


def apply_refit(text, refit, resolve, unit_id):
    """Retune a clone's systems and magazine rounds. Returns (text, chosen).

    Only SystemName inside a system section and Ammunition1 inside a magazine
    section are ever rewritten - see the REFIT commentary above CLONES for why
    the geometry keys are untouchable.

    `refit` maps a slot to a preference list. A key is one of:

        "SPS-40"                   every system section whose SystemName is that
        "SensorSystem2:Nav_Radar"  only that section
        "@usn_rim-7m"              every magazine whose Ammunition1 is that round

    `resolve` takes a preference list and returns the first name the exported
    collection actually defines; the builder supplies it, because ras.py is a
    tuning table and does not read the filesystem.

    Every key MUST match something. A donor that quietly stopped carrying an
    SPS-40 would otherwise leave the clone on its old fit while the build log
    still said "refitted" - the same silent-success failure the launcher regex
    had, and the reason that one went unnoticed across 245 launchers.
    """
    chosen, hit = {}, set()

    def pass_over(src, section_re, key, scoped):
        def one(m):
            section, body = m.group(1), m.group(0)
            cur = re.search(_VALUE.format(key), body, re.M)
            if not cur:
                return body
            raw = cur.group(1)
            value = raw.split("//", 1)[0]
            old = value.strip()
            # the section-scoped key wins over the bare one, so a hull can
            # refit one of three identical radars and leave the others alone
            slot = next((s for s in (f"{section}:{old}", f"{scoped}{old}") if s in refit),
                        None)
            if slot is None:
                return body
            hit.add(slot)
            new = resolve(refit[slot], unit_id, slot)
            chosen.setdefault(slot, []).append((section, old, new))
            if new == old:
                return body
            # keep whatever followed the value - the padding and the comment
            replacement = new + raw[len(value.rstrip()):]
            return body[:cur.start(1)] + replacement + body[cur.end(1):]
        return section_re.sub(one, src)

    text = pass_over(text, _SYSTEM_SECTION, "SystemName", "")
    text = pass_over(text, _MAGAZINE_SECTION, "Ammunition1", "@")

    missing = sorted(set(refit) - hit)
    if missing:
        raise SystemExit(f"{unit_id}: refit slot(s) {missing} matched nothing in the "
                         "donor - the donor's systems changed, so re-check the fit "
                         "before shipping a ship that was not actually refitted")
    return text, chosen


def render_supply_block(spec):
    """The [SupplySystem1] block for one supplier, as text.

    Emits the vanilla key order, then the accountable-category list. Keys with
    a None value are omitted - that is how MaxAmmoPoints is left off the
    ammunition ships, which is the difference between "can pass a 21000-point
    round" and "cannot".
    """
    comments = {
        "AmmoLoadSpeed": "// Ammo points per second, per target",
        "AmmoCapacity": "// Ammo points",
        "MaxAmmoPoints": "// Rounds costing more than this are refused outright",
        "SupplyRange": "// In nautical miles",
        "MaxTargets": "// Simultaneous receivers, each at the full load speed",
        "MaxOwnVelocity": "// In knots. Above this replenishment is impossible",
        "MaxTargetVelocity": "// In knots. Above this replenishment is impossible",
        "TargetTypes": "// What unit types can be replenished by this system",
        "UpdateDelay": "// Delay between replenishment calculations",
    }
    values = dict(spec)
    values["SystemName"] = "TruckSupplySystem"
    values["UpdateDelay"] = 1

    lines = [DIVIDER, "[SupplySystem1]"]
    for key in KEY_ORDER:
        value = values.get(key)
        if value is None:
            continue
        pad = f"{key}={value}".ljust(30)
        lines.append(f"{pad}{comments[key]}" if key in comments else f"{key}={value}")
    if values.get("MaxAmmoPoints") is None:
        lines.append("# MaxAmmoPoints is deliberately absent: no per-round size cap, "
                     "as tgt_ammo_depot_small")
    cats = values["categories"]
    lines.append("")
    lines.append(f"NumberOfAccountableAmmunitionCategories={len(cats)}")
    for i, (name, count) in enumerate(cats, start=1):
        lines.append(f"AccountableAmmunitionCategory_{i}={name},{count}")
    if values.get("note"):
        lines.append("")
        for chunk in _wrap(values["note"], 74):
            lines.append(f"# {chunk}")
    return "\n".join(lines) + "\n\n"


def _wrap(text, width):
    out, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


def insert_supply_block(text, spec, unit_id):
    """Return `text` with this hull's supply system in place.

    Any existing block is removed first - vanilla's commented Sacramento one,
    RE-power's active ones, or both on the same hull - so every supplier goes
    through one code path and the emitted syntax is identical everywhere.

    The block then goes back where the hull already kept one; failing that
    before the mesh-definitions divider; failing that before the [Models]
    section. Order matters, and all three rungs are load-bearing:

      - Reusing the stripped block's own offset is the most faithful thing to
        do - upstream chose that spot. Only the Sacramento qualifies now
        (vanilla's commented block).
      - Eight of the ten suppliers have no block but do have a mesh divider.
      - The Algol has neither. Its vanilla file carries just two dividers, AI
        related and Cargoholds, and opens the mesh sections on a bare [Models].
        RE-power's copy has a Supply Systems divider only because RE-power put
        one there, so this rung only became load-bearing when the pack switched
        to forking vanilla instead of RE-power.
    """
    # ALL existing blocks go, not just the first. No hull forked today carries
    # two, but RE-power's Sacramento does - it keeps vanilla's commented
    # VesselSupplySystem block AND adds its own active one - so the shape is
    # real upstream and one fork-source change away from mattering. Removing
    # back-to-front keeps the earlier offsets valid; the replacement goes back
    # at the first block's position.
    blocks = list(EXISTING_BLOCK.finditer(text))
    if blocks:
        at = blocks[0].start()
        for m in reversed(blocks):
            text = text[:m.start()] + text[m.end():]
        return text[:at] + render_supply_block(spec) + text[at:], len(blocks)
    anchor = MESH_ANCHOR.search(text) or MODELS_ANCHOR.search(text)
    if not anchor:
        raise SystemExit(f"{unit_id}: no existing supply block, no mesh-definitions "
                         "divider and no [Models] section to anchor one to - donor "
                         "layout changed, re-check")
    at = anchor.start()
    return text[:at] + render_supply_block(spec) + text[at:], 0


# ---------------------------------------------------------------------------
# Gate 5: the receiving launcher.

# The trailing `[A-Za-z]\w*` catches LOADOUT-SCOPED launchers -
# [WeaponSystem6AntiShip], [WeaponSystem4Strike], [WeaponSystem12Late] and so
# on. Ships carry loadouts exactly as aircraft do, and 245 bare launchers on
# 24 modern hulls live only in those sections: the Meteoro/Arafura's NSM quad
# launcher, the FREMM and PPA anti-ship fits, the Type 052D strike fit. A
# header-only match silently skips every one. `\d+` stays required so the
# [WeaponSystems] count header can never match. The body alternation accepts a
# final line with no newline, so a weapon block that ends the file is not
# truncated - 493 vessel files in the export have no trailing newline.
_WEAPON_BLOCK = re.compile(
    r"^\[WeaponSystem(\d+)([A-Za-z]\w*)?\][^\n]*\n(?:(?!^\[).*(?:\n|$))*", re.M)
_HAS_AMMO = re.compile(r"^Ammunition\d*\s*=\s*\S", re.M)
_HAS_MAGAZINE = re.compile(r"^AssociatedMagazine\s*=", re.M)
_HAS_FLAG = re.compile(r"^ReloadableWithoutMagazine\s*=", re.M)
_LOADING_ANCHOR = re.compile(r"^Ammunition\d*\s*=[^\n]*\n", re.M)

RELOAD_LINE = ("ReloadableWithoutMagazine=True  // SEST RAS: without this a "
               "launcher with no magazine can never be reloaded\n")


def make_reloadable(text):
    """Flag every launcher that has ammunition but no magazine, and return
    (text, count).

    This is the gate that decides whether the other four matter, and it is the
    reason the RE-power author reports that "most Anti-ship missiles and
    torpedoes cannot" be replenished. Vanilla spells the rule out on the Long
    Beach's Mk141 Harpoon canisters:

        usn_cgn_long_beach_83.ini:431
            ReloadableWithoutMagazine=False  // If true - can replenished even
                                             // without magazine. For launchers only

    A launcher fed by `AssociatedMagazine=` refills when its magazine refills.
    A launcher holding a bare `Ammunition=` - a sealed canister, a deck rail, a
    fixed tube - needs this flag or it is one-shot forever. The flag appears on
    exactly 11 units in vanilla plus the mods, ALL of them land SAM TELs, i.e.
    precisely the units the supply trucks exist to service. No vessel anywhere
    sets it True.

    That matters far beyond deck canisters: Red Storm Arsenal models every
    Mk41 cell as its own launcher with a bare `Ammunition=` line, so without
    this transform not one VLS round on any of its 115 hulls could ever be
    replenished, however many oilers were alongside.

    Adding the key explicitly is safe whichever way the engine's default falls:
    if the default is already True the line is a no-op, and if it is False -
    which the comment's phrasing and the TEL-only usage both point to - it is
    the fix.
    """
    count = 0

    def patch(match):
        nonlocal count
        block = match.group(0)
        if not _HAS_AMMO.search(block) or _HAS_MAGAZINE.search(block) \
                or _HAS_FLAG.search(block):
            return block
        last = None
        for last in _LOADING_ANCHOR.finditer(block):
            pass
        if last is None:                      # unreachable given _HAS_AMMO
            return block
        count += 1
        return block[:last.end()] + RELOAD_LINE + block[last.end():]

    return _WEAPON_BLOCK.sub(patch, text), count
