#!/usr/bin/env python3
"""Build the SEST RAN Fleet: Royal Australian Navy vessels cloned from their
real European design donors in the Euromod packs.

The RAN sails European designs, so the clones are honest: Hobart-class = the
Spanish F-100 (ae_ffg_alvaro_bazan), Canberra-class LHD = Juan Carlos I,
Collins stand-in = S-80, plus Galicia (Choules), Teide (Supply) and Meteoro
(Arafura) stand-ins. Each clone gets Australian
nation/flag, real HMAS hull names, transparent hull numbers (no Spanish
pennants), and MH-60R / S-70B-2 air groups.

Clones are NEW unit ids — nothing overrides the donors, so both fleets coexist.

The Anzac is the exception, and the reason there are two modes here. It was a
Type 23 MLU clone only because the collection had no Anzac; since 2026-09-20 it
has the real ASMD hull (Workshop 3440622312), so that entry is a PATCH of the
mod's own ran_ffh_anzac rather than a clone of somebody else's frigate. Patch
mode keeps the mod's identity - its hull-number and emblem textures, its eight
HMAS names - and changes only what is wrong or missing: see the entry in FLEET.

Usage (repo root):  python3 integration/ran-fleet/build_fleet.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
OUT = Path(__file__).resolve().parent / "SEST_RAN_Fleet"

SPA_MODERN = "3731208477"   # Spanish Navy Mod (Modern)
RSA = "3413868677"          # Red Storm Arsenal - sole source of usn_rgm_184a (NSM)
EUROMOD = "3629144864"      # Euromod pack - usn_rgm-109e5a (Tomahawk Block Va)
SPA_COLDWAR = "3630495619"  # Spanish Navy Mod (Cold War)
# Modern British Navy (3599752717) is no longer a donor here - the Anzac was
# its only customer and now patches the real hull instead. The mod stays
# subscribed: SEST_Allied_Fixes patches HMS Ocean out of it.
ANZAC = "3440622312"        # Anzac Class Frigate - the REAL hull, subscribed 2026-09-20

HELOS = "usn_mh-60r,S-70B-2_Seahawk"

# --- 2027 armament refresh ---------------------------------------------------
# The clones inherited their donors' placeholder fits. Two real RAN programs
# supersede them, both with every round already in the collection:
#
#   NSM   - replaced Harpoon on Anzac and Hobart from 2024. The round is
#           Euromod's knm_nsm_1a; see the block above NSM_KNM for why it beat
#           RSA's usn_rgm_184a and the Type 23's rn_nsm. The MK141 racks stay -
#           SystemName refers to a systems/ launcher definition, and the NSM
#           deck launchers replace Harpoon's 1:1 anyway.
#
#   TLAM  - Hobart's 48 Mk41 cells: module 1 = 32 ESSM (quad), modules 2-6 =
#           40 SM-2. Module 6 converts to 8x usn_rgm-109e5a, the exact
#           magazine pattern Modern US Navy's 2025 Burkes and Ticos use for
#           the same round. 32 ESSM + 32 SM-2 stay - she is an air warfare
#           destroyer first.
#
# Each entry: (regex, replacement, exact expected substitutions) - a count
# mismatch fails the build rather than shipping a half-applied refresh.
# The NSM round: Euromod's knm_nsm_1a, on both mounts, on both classes.
#
# This started as a hunt for why Warramunga would not fire usn_rgm_184a (Red
# Storm Arsenal's RGM-184A), and briefly ran as an experiment with one round on
# each mount. The encyclopedia settled the part the files could not: the round
# DOES fire there, which exercises the definition, the mount, the launch mesh
# and the launch path. So the round was never structurally broken, the split
# test had nothing left to separate, and the choice reverts to what it always
# should have been - which missile is the better one to ship.
#
# That is knm_nsm_1a, for three reasons that outrank the headline stats the
# original choice was made on:
#
#   REALISM   - it is the Kongsberg NSM, which is the missile the RAN actually
#               bought. usn_rgm_184a is the US ship-launched designation.
#   COHERENCE - MidCourseCorrection=1 (radio command) rather than 3 (datalink,
#               which needs a guidance channel the donor mounts never had), and
#               a 12 nm terminal approach INSIDE its own 20 nm seeker rather
#               than 25 nm outside it. RSA's own header admits the round
#               "REQUIRES STATS REVISION" and has no RC flight stage.
#   PRECEDENT - ten hulls fire it and four are fielded in NFIII (Zeven
#               Provincien, Iver Huitfeldt, F127 batch 2, Type 45). RSA's round
#               is fired by nothing else we field.
#
# Performance is not the trade it looks like: the two are the same missile by
# the numbers - Mass 1450, Power 34, 620 kt, 165.6 nm, 20 nm seeker.
#
# To go back to the RSA round: set both entries below to NSM_RSA.
NSM_KNM = "knm_nsm_1a"           # Euromod, mission-proven on four fielded hulls
NSM_RSA = "usn_rgm_184a"         # Red Storm Arsenal, the one that would not fire
NSM_IDS = (NSM_KNM, NSM_RSA)

def nsm_swap(rounds, replaces="usn_rgm-84d"):
    """Replace the donor's anti-ship round positionally, one per launcher.

    `replaces` is the id the donor ships on those mounts: the cloned hulls
    inherit vanilla's Harpoon, while the real Anzac already carries its own
    mod's RGM-184A. Either way the mounts are unchanged - only the round is."""
    def apply(text, ship_id):
        out, n = text, 0
        note = ("NSM - replaced Harpoon from 2024" if replaces == "usn_rgm-84d"
                else "NSM - the fleet-standard Kongsberg round")
        for rnd in rounds:
            out, k = re.subn(rf"^Ammunition={re.escape(replaces)}[^\n]*$",
                             f"Ammunition={rnd}               // {note}",
                             out, count=1, flags=re.M)
            n += k
        if n != len(rounds):
            sys.exit(f"{ship_id}: NSM swap replaced {n} line(s), expected {len(rounds)} - "
                     "donor layout changed, re-check")
        return out
    return apply

NSM_LOADS = {
    # (rounds, the id the donor already carries on those mounts)
    "ran_ffh_anzac": ((NSM_KNM, NSM_KNM), "RGM-184A"),
    "ran_ddg_hobart": ((NSM_KNM, NSM_KNM), "usn_rgm-84d"),
}
# The Anzac mod ships its OWN RGM-184A and the hull already fires it, so this
# swap is a deliberate standardisation rather than a fix. Both rounds are the
# same missile structurally - GuidanceType=1, MidCourseCorrection=1, 620 kt -
# and the Kongsberg one wins on the three grounds this pack already settled
# the question on: it is the missile the RAN actually bought, Hobart fires it,
# and four other fielded hulls fire it, so the encyclopedia shows one NSM
# rather than two with different numbers. On the detail the two disagree
# about most, it is also the more defensible: knm_nsm_1a acquires at 20 nm and
# runs a 12 nm terminal leg inside that, where RGM-184A claims an 80 nm
# passive seeker on an imaging-infrared round. To ship the mod author's round
# instead, set the Anzac entry's rounds to ("RGM-184A", "RGM-184A").

ARMAMENT_REFRESH = {
    "ran_ddg_hobart": [
        (r"(\[WeaponMagazineVLS_6\][^\[]*?)Ammunition1=usn_rim-66m-5",
         r"\1Ammunition1=usn_rgm-109e5a", 1),
        # SM-6 in module 5 - the RAN's approved Aegis refresh, and the same
        # SM-2/SM-6/ESSM/TLAM/NSM pattern Red Storm Arsenal's own 2026
        # Hobart (ran_ddg_hobart_alt_late) carries. U.S. Navy 2027's
        # usn_rim-174a wins the id. Final cells: 32 ESSM, 24 SM-2, 8 SM-6,
        # 8 Tomahawk.
        (r"(\[WeaponMagazineVLS_5\][^\[]*?)Ammunition1=usn_rim-66m-5",
         r"\1Ammunition1=usn_rim-174a", 1),
    ],
    "ran_ffh_anzac": [],
}
REFRESH_ROUNDS = {RSA: "usn_rgm_184a", EUROMOD: "usn_rgm-109e5a"}

# --- the NSM's midcourse datalink needs a provider ---------------------------
# Swapping the Ammunition line was not the whole job. usn_rgm_184a is
# MidCourseCorrection=3 (datalink midcourse); the launcher must draw a guidance
# channel from an associated Type=Targeting / Mode=RadioCommand sensor or fire
# control never forms a solution, and the mount simply never fires - no error,
# no log line, the ship just holds its missiles. That is what HMAS Warramunga
# did in game.
#
# The rule was measured, not guessed: across vanilla and all 132 mods, 373 of
# 373 launcher blocks firing an MCC=3 round associate a sensor. The only four
# that did not were these two hulls' MK141 pairs. Red Storm Arsenal, the round's
# own author, wires every hull that fires it (Constellation, Richard Morris,
# both Hobart alts) to a Type=Targeting / Mode=RadioCommand sensor and nothing
# else. The donor blocks looked fine because the Type 23 fires vanilla's
# usn_rgm-84d, which is MidCourseCorrection=0 and needs no channel at all.
#
# Hobart already carries eu_GPS_Receiver (SensorSystem12, Type=Targeting,
# Mode=RadioCommand, 5000 weapon channels) - she only needed the association.
# The Anzac donor carries no RadioCommand sensor at all (Type996 and the nav
# radars are Search with WeaponChannels=0; the Type911s are 40 km Sea Wolf
# illuminators), so she gets the same Euromod receiver appended as a new
# system. Appending keeps every existing SensorSystem index valid, so no
# AssociatedSensors= line anywhere else has to be renumbered.
GPS_SENSOR = """\
[SensorSystem{index}]  # GPS Receiver - NSM midcourse datalink
Type=Radar
SystemName=eu_GPS_Receiver
Mount=Dummy
MountPosition={position}

"""
# ship id -> (sensor index to associate, position for a sensor to be added, add?)
#
# ran_ffh_anzac is NOT here any more, and that is the point of the rebase.
# The Type 23 clone had to be given a sensor because none of its twelve could
# guide a missile: Type996 and the nav radars are Search with
# WeaponChannels=0, and the Type911s are Sea Wolf illuminators. The real Anzac
# is the ASMD hull - both MK141 mounts already associate SensorSystem2
# (CEAFAR), which its own systems/sensors.ini defines with WeaponChannels=10.
# That is the condition tools/check_weapon_employment.py measures for an
# MCC 1 or 3 round, so the remedy that saved Warramunga is simply not needed
# on this hull. verify_nsm_channel() below asserts it rather than assuming it.
NSM_DATALINK = {
    # already mounted as SensorSystem12; associate only
    "ran_ddg_hobart": {"sensor": 12, "add": False, "position": None},
}


def verify_nsm_channel(ship_id, text):
    """Every NSM mount must associate SOME sensor - the Warramunga rule.

    Checked here as well as in tools/check_weapon_employment.py because this
    builder is what chooses the round: if a future donor drops the
    association, the failure is silent in game (the ship just holds its
    missiles) and this is the last place that can see it coming."""
    ids = "|".join(re.escape(i) for i in NSM_IDS)
    mounts = re.findall(rf"(?ms)^\[WeaponSystem\d+\][^\n]*\n(?:(?!^\[).)*?"
                        rf"^Ammunition=(?:{ids})[^\n]*\n(?:(?!^\[).)*", text)
    if not mounts:
        sys.exit(f"{ship_id}: no NSM mount found after the swap")
    bare = [i for i, b in enumerate(mounts, 1) if "AssociatedSensors" not in b]
    if bare:
        sys.exit(f"{ship_id}: NSM mount(s) {bare} associate no sensor - an MCC=1 "
                 "round with no guidance channel never fires (see the Warramunga "
                 "note above)")
    return len(mounts)


def wire_nsm_datalink(ship_id, text):
    """Give the NSM launchers the guidance channel MCC=3 requires."""
    spec = NSM_DATALINK.get(ship_id)
    if not spec:
        return text
    sensor = spec["sensor"]

    if spec["add"]:
        count = re.search(r"^NumberOfSensorSystems=(\d+)$", text, re.M)
        if not count:
            sys.exit(f"{ship_id}: NumberOfSensorSystems not found")
        have = int(count.group(1))
        if have != sensor - 1:
            sys.exit(f"{ship_id}: donor now has {have} sensor systems, expected "
                     f"{sensor - 1} - the NSM datalink sensor index is stale")
        if "eu_GPS_Receiver" in text:
            sys.exit(f"{ship_id}: donor now carries eu_GPS_Receiver itself - "
                     "associate that one instead of appending another")
        text = text[:count.start()] + f"NumberOfSensorSystems={sensor}" + text[count.end():]
        # insert after the last sensor block, i.e. before the section that
        # follows it - the weapon-systems banner
        anchor = re.search(rf"^\[SensorSystem{sensor - 1}\].*?\n(?=^\[(?!SensorSystem))",
                           text, re.S | re.M)
        if not anchor:
            sys.exit(f"{ship_id}: could not locate the end of the sensor list")
        block = GPS_SENSOR.format(index=sensor, position=spec["position"])
        text = text[:anchor.end()] + block + text[anchor.end():]

    # associate the sensor with every MK141 block that now fires the NSM
    def add_assoc(m):
        body = m.group(0)
        if "AssociatedSensors" in body:
            sys.exit(f"{ship_id}: an NSM block already associates a sensor - re-check")
        return re.sub(r"^(SystemName=MK141[^\n]*\n)",
                      rf"\1AssociatedSensors=SensorSystem{sensor}"
                      "               // MCC=3 datalink provider\n",
                      body, count=1, flags=re.M)

    ids = "|".join(re.escape(i) for i in NSM_IDS)
    text, n = re.subn(r"(?ms)^\[WeaponSystem\d+\][^\n]*\n(?:(?!^\[).)*?"
                      rf"^Ammunition=(?:{ids})[^\n]*\n(?:(?!^\[).)*",
                      add_assoc, text)
    if n != 2:
        sys.exit(f"{ship_id}: wired {n} NSM launcher(s), expected 2 - "
                 "block layout changed, re-check")
    return text


ESSM_SRC = "RIM-162 ESSM"          # the Anzac mod's id - note the SPACE
# The round the ASMD Anzac's Mk41 fires: Euromod's RIM-162H, a complete
# active ESSM Block II that nothing above Euromod overrides.
#
# The first builds re-shipped the Anzac mod's own "RIM-162 ESSM" under a
# space-free id. That file is a RIM-7F template its author left flagged
# "REQUIRES STATS REVISION": it declares no kinematic model (no
# ApplyKinematics, no MaxLoftAlt/MaxLoftAngle, no TypicalTargetAlt), and
# MinAttackAltitude=26 puts every sea-skimming anti-ship missile outside the
# band where the engine "greatly increases missile deviation" - the one
# target ESSM exists to kill. In game it was reported flying at a metre
# above the sea like an anti-ship round. Both collection Block IIs are
# complete: U.S. Navy 2027's usn_rim-162e and Euromod's usn_rim-162h. The
# Euromod file is the one taken because it is the same family the rest of
# SEST's interceptor work already rebuilds on (Collection Fixes' SM-3, SM-6
# and PAC-3 MSE), accepts targets down to 5 ft, lofts (60,000 ft, 40 deg,
# TerminalLoft) and carries a kill probability on the usual 0-1 scale; the
# U.S. Navy 2027 file writes KillProbability=3.8 and TypicalTargetAlt=0.
#
# It is datalink midcourse (MidCourseCorrection=3). That needs a guidance
# channel, and this hull has one: both Mk41 blocks associate CEAFAR
# (SensorSystem2, WeaponChannels=10), which is the condition
# tools/check_weapon_employment.py checks for an MCC 1 or 3 round.
ESSM_ID = "usn_rim-162h"
ESSM_DONOR = EUROMOD


def check_essm():
    """The Block II round must still be where it was taken from."""
    f = MODS / ESSM_DONOR / "ammunition" / f"{ESSM_ID}.ini"
    if not f.exists():
        sys.exit(f"{ESSM_ID} no longer ships in {ESSM_DONOR} - re-choose the Anzac's ESSM")
    body = f.read_text(encoding="utf-8-sig", errors="replace")
    for key, want in (("GuidanceType", "3"), ("TargetType", "AAW")):
        m = re.search(rf"^{key}=(\S+)", body, re.M)
        if not m or m.group(1) != want:
            sys.exit(f"{ESSM_ID}: {key} is no longer {want} - re-check the Anzac's ESSM")


def fix_vls_magazine(ship_id, text):
    """Repair the Anzac mod's Mk41 magazine, which silently holds half its ESSM.

    As shipped:

        NumberOfAmmunitionTypes=1
        Ammunition1=RIM-162 ESSM
        Ammunition1_Count=32
        Ammunition2=usn_rim-66h
        Ammunition1_Count=16      <- second entry's count, mis-keyed

    Two defects in four lines. The count key for the second round says
    Ammunition1 again, so it overwrites the ESSM's 32 with 16 and the SM-1
    gets no count at all; and NumberOfAmmunitionTypes=1 means the second
    round was never enabled anyway. The ship therefore sails with 16 ESSM
    where the author wrote 32, and an SM-1 that does not exist.

    The fix keeps the author's stated intent - one ammunition type, 32 rounds
    - and drops the orphan. 32 is also the right number: the ASMD Anzac's
    8-cell Mk41 quad-packs ESSM, and the RAN's Anzacs never carried SM-1."""
    m = re.search(r"^\[WeaponMagazineMK141\]\n(.*?)(?=^\[)", text, re.M | re.S)
    if not m:
        sys.exit(f"{ship_id}: [WeaponMagazineMK141] not found - donor changed")
    body = m.group(1)
    if body.count("Ammunition1_Count=") != 2:
        sys.exit(f"{ship_id}: expected the doubled Ammunition1_Count in the Mk41 "
                 "magazine - upstream may have fixed it, re-check this patch")
    fixed = re.sub(r"^Ammunition2=[^\n]*\n", "", body, count=1, flags=re.M)
    fixed = re.sub(r"^Ammunition1_Count=16[^\n]*\n", "", fixed, count=1, flags=re.M)
    fixed = re.sub(r"^(Ammunition1_Count=)\d+", r"\g<1>32", fixed, count=1, flags=re.M)
    fixed, n = re.subn(rf"^Ammunition1={re.escape(ESSM_SRC)}\s*$",
                       f"Ammunition1={ESSM_ID}", fixed, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"{ship_id}: the Mk41 magazine no longer loads '{ESSM_SRC}' - "
                 "re-check the ESSM swap")
    if fixed.count("Ammunition1_Count=") != 1 or "Ammunition2=" in fixed:
        sys.exit(f"{ship_id}: Mk41 magazine repair did not land cleanly")
    return text[:m.start(1)] + fixed + text[m.end(1):]


def refresh_armament(ship_id, text):
    if ship_id in NSM_LOADS:
        rounds, replaces = NSM_LOADS[ship_id]
        text = nsm_swap(rounds, replaces)(text, ship_id)
    for pat, repl, want in ARMAMENT_REFRESH.get(ship_id, []):
        text, n = re.subn(pat, repl, text, flags=re.M)
        if n != want:
            sys.exit(f"{ship_id}: armament refresh made {n} substitution(s), "
                     f"expected {want} - donor layout changed, re-check")
    return wire_nsm_datalink(ship_id, text)

FLEET = {
    "ran_ddg_hobart": {
        "donor": (SPA_MODERN, "ae_ffg_alvaro_bazan"),
        "class_name": "Hobart-class DDG",
        "type_line": "DDG,Destroyer",
        "short": "Hobart",
        "desc": ("Royal Australian Navy air warfare destroyer, built to the Spanish F-100 "
                 "Alvaro de Bazan design with Aegis and SPY-1D(V).\\n\\nEmbarks an MH-60R. "
                 "Home port Fleet Base East, Sydney."),
        "service": "2017|2055",
        "hulls": [("DDG 39 HMAS Hobart", "Hobart"),
                  ("DDG 41 HMAS Brisbane", "Brisbane"),
                  ("DDG 42 HMAS Sydney", "Sydney")],
        "airgroup": ["usn_mh-60r=Squadron20,1"],
    },
    # REBASED 2026-09-20 from a clone to a PATCH. The Type 23 MLU stood in for
    # the MEKO 200 only because the collection had no Anzac; it now has the
    # real ASMD hull - CEAFAR/CEAMOUNT phased arrays, Ceros 200 directors,
    # Spherion sonar, its own hull-number and emblem textures for all eight
    # ships. Cloning a British frigate to stand in for a ship that is now
    # modelled would be worse in every respect, so this entry stops cloning
    # and starts patching the real file instead.
    #
    # What that changes about this entry: patch mode keeps the mod's own
    # identity wholesale. Its variants file carries real FFH-150..157 hull
    # numbers and per-ship emblems where the clone could only blank them out,
    # and its vessel_names already names all eight HMAS hulls - so this pack
    # now ships NEITHER for the Anzac and lets the mod's win. The hulls list
    # below is kept for the build summary and as the record of what the class
    # is; nothing is generated from it any more.
    "ran_ffh_anzac": {
        "donor": (ANZAC, "ran_ffh_anzac"),
        "patch": True,
        "class_name": "Anzac-class FFH",
        "type_line": "FFH,Frigate",
        "short": "Anzac",
        "desc": ("Royal Australian Navy long-range ASW/patrol frigate, ASMD-upgraded: "
                 "CEAFAR/CEAMOUNT phased arrays, 32 ESSM in the Mk41, NSM on the deck "
                 "launchers."),
        "service": "1996|2045",
        "hulls": [("FFH 150 HMAS Anzac", "Anzac"),
                  ("FFH 151 HMAS Arunta", "Arunta"),
                  ("FFH 152 HMAS Warramunga", "Warramunga"),
                  ("FFH 153 HMAS Stuart", "Stuart"),
                  ("FFH 154 HMAS Parramatta", "Parramatta"),
                  ("FFH 155 HMAS Ballarat", "Ballarat"),
                  ("FFH 156 HMAS Toowoomba", "Toowoomba"),
                  ("FFH 157 HMAS Perth", "Perth")],
        "airgroup": ["usn_mh-60r=Squadron20,1"],
    },
    "ran_lhd_canberra": {
        "donor": (SPA_MODERN, "ae_lhd_juan_carlos"),
        "class_name": "Canberra-class LHD",
        "type_line": "LHD,Amphibious",
        "short": "Canberra",
        "desc": ("Royal Australian Navy landing helicopter dock, built to the Spanish Juan "
                 "Carlos I design. The RAN operates no fixed-wing aviation from them — the "
                 "air group is MH-60R and S-70B-2 Seahawks.\\n\\nHome port Fleet Base East."),
        "service": "2014|2060",
        "hulls": [("L02 HMAS Canberra", "Canberra"),
                  ("L01 HMAS Adelaide", "Adelaide")],
        "airgroup": ["usn_mh-60r=Squadron20,4", "S-70B-2_Seahawk=Squadron1,4"],
        # The LHD deck is rated for the CH-53E the campaign lifts with (the
        # Juan Carlos design was sized for it); the campaign builder refuses
        # to home an aircraft on a deck whose list leaves it out.
        # USMC lift she carries in the campaign: the Super Stallion and, since
        # MRF-D Ospreys have operated from the class in Talisman Sabre, the MV-22B.
        "deck": ["usmc_ch53_standalone", "mv22b_osprey"],
    },
    "ran_lsd_choules": {
        "donor": (SPA_MODERN, "ae_lpd_galicia"),
        "class_name": "HMAS Choules LSD (stand-in)",
        "type_line": "LSD,Amphibious",
        "short": "Choules",
        "desc": ("Royal Australian Navy dock landing ship. Stand-in hull: the Galicia-class "
                 "LPD stands in for the Bay-class."),
        "service": "2011|2050",
        "hulls": [("L100 HMAS Choules", "Choules")],
        "airgroup": ["usn_mh-60r=Squadron20,2"],
    },
    "ran_aor_supply": {
        "donor": (SPA_COLDWAR, "ae_ao_teide"),
        "class_name": "Supply-class AOR (stand-in)",
        "type_line": "AOR,Replenishment",
        "short": "Supply",
        "desc": ("Royal Australian Navy fleet replenishment ship. Stand-in hull: the Teide-"
                 "class oiler stands in for the Cantabria-derived Supply-class (no Cantabria "
                 "in the collection)."),
        "service": "2021|2060",
        "hulls": [("A195 HMAS Supply", "Supply"),
                  ("A304 HMAS Stalwart", "Stalwart")],
        "airgroup": None,
    },
    "ran_ssg_collins": {
        "donor": (SPA_MODERN, "ae_ssk_s80"),
        "class_name": "Collins-class SSG (stand-in)",
        "type_line": "SSG,Submarine",
        "short": "Collins",
        "desc": ("Royal Australian Navy long-range diesel-electric attack submarine. "
                 "Stand-in hull: the S-80 Plus family stands in for the Collins — a large, "
                 "modern conventional boat of comparable role."),
        "service": "1996|2040",
        "hulls": [("SSG 73 HMAS Collins", "Collins"),
                  ("SSG 74 HMAS Farncomb", "Farncomb"),
                  ("SSG 75 HMAS Waller", "Waller"),
                  ("SSG 76 HMAS Dechaineux", "Dechaineux"),
                  ("SSG 77 HMAS Sheean", "Sheean"),
                  ("SSG 78 HMAS Rankin", "Rankin")],
        "airgroup": None,
    },
    "ran_opv_arafura": {
        "donor": (SPA_MODERN, "ae_opv_meteoro"),
        "class_name": "Arafura-class OPV (stand-in)",
        "type_line": "OPV,Patrol",
        "short": "Arafura",
        "desc": ("Royal Australian Navy offshore patrol vessel. Stand-in hull: the "
                 "Meteoro-class BAM stands in for the Arafura (Luerssen OPV 80)."),
        "service": "2022|2060",
        "hulls": [("OPV 203 HMAS Arafura", "Arafura"),
                  ("OPV 204 HMAS Eyre", "Eyre"),
                  ("OPV 205 HMAS Pilbara", "Pilbara"),
                  ("OPV 206 HMAS Gippsland", "Gippsland")],
        "airgroup": None,
        # No hangar, so no embarked air group - but the flight deck is rated
        # for a Seahawk to land and refuel, which is what the campaign's
        # patrol missions ask of it.
        "deck": HELOS.split(","),
    },
}

INFO_INI = """[Language_en]
Name=SEST RAN Fleet
Description=Royal Australian Navy fleet cloned from its real European design donors: Hobart-class DDG (F-100), Canberra-class LHD (Juan Carlos I), Collins stand-in (S-80), HMAS Choules (Galicia), Supply-class (Teide), Arafura OPV (Meteoro) - new unit ids, donors untouched. The Anzac is different: it patches the real Anzac Class Frigate mod rather than cloning anything, giving it the fleet-standard NSM, repairing a Mk41 magazine that silently held 16 ESSM instead of 32, re-shipping that ESSM under an id without a space in it so it resolves, and letting the deck operate the MH-60R. Requires Euromod Main, the Modern + Cold War Spanish Navy packs, the Anzac Class Frigate mod, and an MH-60R / S-70B-2 source. Place ABOVE the Anzac mod and below the Euromod packs.

[Compatibility]
ApproximateVersion=0.8.2
"""

DEFAULT_VARIANT = """ResourcesHullnumberFolder=textures/Misc/
HullnumberTexture=transparent
ResourcesFlagFolder=ships/materials/textures/
FlagTexture=flag_australia
Nation=Australia
"""


def main():
    problems = []
    for ship_id, ship in FLEET.items():
        mod, donor = ship["donor"]
        # A patched ship keeps the mod's own variants file, so only the unit
        # file has to be there.
        needed = (".ini",) if ship.get("patch") else (".ini", "_variants.ini")
        for suffix in needed:
            if not (MODS / mod / "vessels" / f"{donor}{suffix}").exists():
                problems.append(f"{ship_id}: donor file missing: {mod}/vessels/{donor}{suffix}")
        if ship.get("patch") and donor != ship_id:
            problems.append(f"{ship_id}: patch mode must write the donor's own id, "
                            f"got {donor}")
    for helo in HELOS.split(","):
        if not list(MODS.glob(f"*/aircraft/{helo}.ini")):
            problems.append(f"helo not found in any mod: {helo}")
    for mod, round_ in REFRESH_ROUNDS.items():
        if not (MODS / mod / "ammunition" / f"{round_}.ini").exists():
            problems.append(f"armament refresh round missing: {mod}/ammunition/{round_}.ini")
    if problems:
        sys.exit("validation failed:\n  " + "\n  ".join(problems))

    (OUT / "vessels").mkdir(parents=True, exist_ok=True)
    (OUT / "language_en").mkdir(exist_ok=True)
    # Section headers stay ASCII, as every vanilla language_en file's are.
    # This one carried an em dash when the editor listed the SEST ships as
    # "Missing Type / Missing Class" (16 Sep 2026). Not confirmed as the
    # cause: vanilla's language_es/fr/vn files and one workshop language_en
    # file (3681873198) put non-ASCII text inside [...] lines too.
    names = ["[****************************** Australia - SEST RAN Fleet ******************************]", ""]

    for ship_id, ship in FLEET.items():
        mod, donor = ship["donor"]
        text = (MODS / mod / "vessels" / f"{donor}.ini").read_text(encoding="utf-8-sig", errors="replace")

        text, n = re.subn(r"^DisplayClassName=.*$", f"DisplayClassName={ship['class_name']}",
                          text, count=1, flags=re.M)
        if n == 0:
            print(f"note: {donor} has no DisplayClassName line; relying on language names")

        if ship.get("patch"):
            check_essm()
            text = fix_vls_magazine(ship_id, text)
        text = refresh_armament(ship_id, text)
        if ship_id in NSM_LOADS:
            n_mounts = verify_nsm_channel(ship_id, text)
            print(f"  {ship_id}: {n_mounts} NSM mount(s), each with a guidance channel")

        if ship["airgroup"]:
            new_ag = "[AirGroup]\n" + "\n".join(ship["airgroup"]) + "\n\n"
            text, n = re.subn(r"\[AirGroup\].*?(?=\n\[)", new_ag.rstrip("\n") + "\n", text,
                              count=1, flags=re.S)
            if n == 0:
                sys.exit(f"{ship_id}: donor {donor} has no [AirGroup] block to replace")
            text, n = re.subn(r"^(AircraftSupported=.*)$", rf"\1,{HELOS}", text,
                              count=1, flags=re.M)
            if n == 0:
                # The Anzac mod declares a flight deck and an air group but no
                # AircraftSupported list at all, so the deck would accept only
                # what the air group already names. Add it where every other
                # helo-capable hull in the collection keeps it: in
                # [FlightDeck], under the taxi-path count.
                anchor = re.search(r"^(\[FlightDeck\](?:(?!^\[).)*?"
                                   r"^NumberOfTaxiPaths=\d+\n)", text, re.M | re.S)
                if not anchor:
                    sys.exit(f"{ship_id}: donor {donor} has neither an "
                             "AircraftSupported line nor a [FlightDeck] to add one to")
                text = (text[:anchor.end(1)]
                        + f"AircraftSupported={HELOS}"
                        + "   // SEST: the deck operates both RAN Seahawks\n"
                        + text[anchor.end(1):])
                print(f"  {ship_id}: added AircraftSupported ({HELOS}) - donor had none")

        if ship.get("deck"):
            # Types the deck operates beyond the donor's own list and the
            # embarked air group. Appended before any trailing comment.
            add = ",".join(ship["deck"])
            text, n = re.subn(r"^(AircraftSupported=[^\n/]*)", rf"\1,{add}", text,
                              count=1, flags=re.M)
            if n == 0:
                anchor = re.search(r"^(\[FlightDeck\](?:(?!^\[).)*?"
                                   r"^NumberOfTaxiPaths=\d+\n)", text, re.M | re.S)
                if not anchor:
                    sys.exit(f"{ship_id}: donor {donor} has neither an "
                             "AircraftSupported line nor a [FlightDeck] to add one to")
                text = (text[:anchor.end(1)] + f"AircraftSupported={add}"
                        + "   // SEST: the deck operates these types\n"
                        + text[anchor.end(1):])
            print(f"  {ship_id}: deck also operates {add}")

        (OUT / "vessels" / f"{ship_id}.ini").write_text(text, encoding="utf-8")

        if ship.get("patch"):
            # The mod owns its identity: real hull-number and emblem textures
            # in its variants file, all eight HMAS names in its vessel_names.
            # Shipping ours would override the first and duplicate the second,
            # so this pack ships neither. Clear the clone-era copy if it is
            # still sitting in the pack folder from a previous build.
            stale = OUT / "vessels" / f"{ship_id}_variants.ini"
            if stale.exists():
                stale.unlink()
                print(f"  {ship_id}: removed the clone's variants file - the mod's "
                      "own carries real hull numbers and emblems")
            continue

        # Variants: keep the donor's [General] block (texture/reference wiring must
        # match the donor mesh), then emit Australian variants with clean hull numbers.
        vtext = (MODS / mod / "vessels" / f"{donor}_variants.ini").read_text(encoding="utf-8",
                                                                             errors="replace")
        g = re.search(r"\[General\].*?(?=\[Default\])", vtext, re.S)
        if not g:
            sys.exit(f"{ship_id}: [General] block not found in donor variants")
        general = re.sub(r"^NumberOfVariants=.*$", f"NumberOfVariants={len(ship['hulls'])}",
                         g.group(0).rstrip() + "\n", flags=re.M)
        parts = [general, "", "[Default]", DEFAULT_VARIANT.rstrip()]
        for i in range(1, len(ship["hulls"]) + 1):
            parts += ["", f"[Variant{i}]", DEFAULT_VARIANT.rstrip(),
                      f"ServiceDate={ship['service']}"]
        (OUT / "vessels" / f"{ship_id}_variants.ini").write_text("\n".join(parts) + "\n",
                                                                 encoding="utf-8")

        names += [f"[{ship_id}]", f"Type={ship['type_line']}",
                  f"Default={ship['class_name']},{ship['short']}",
                  f"DefaultDescription={ship['desc']}"]
        names += [f"Variant{i}={full},{shrt}"
                  for i, (full, shrt) in enumerate(ship["hulls"], start=1)]
        names.append("")

    (OUT / "language_en" / "vessel_names.ini").write_text("\n".join(names), encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")

    n_hulls = sum(len(s["hulls"]) for s in FLEET.values())
    print(f"built {OUT.relative_to(ROOT)}: {len(FLEET)} classes, {n_hulls} named hulls, "
          "all donors and helos validated")


if __name__ == "__main__":
    main()
