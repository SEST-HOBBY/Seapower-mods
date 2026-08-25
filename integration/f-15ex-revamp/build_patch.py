#!/usr/bin/env python3
"""Build the SEST F-15EX Revamp patch mod from the exported upstream files.

Reads the original F-15EX (F-15SE) mod out of mods-source/, injects four new
loadouts, and writes a ready-to-install mod folder. Re-run after re-exporting
mods-source/ to rebase the patch onto an upstream update.

Usage (repo root):  python3 integration/f-15ex-revamp/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "mods-source" / "3636386513"          # F-15SE (F-15EX) by dingtools
WEAPON_PACK = ROOT / "mods-source" / "3760871384"       # Dingtools Weapon Pack
MURDER_HORNET = ROOT / "mods-source" / "3430135740"     # Murder Hornet (AIM-174B)
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
OUT = Path(__file__).resolve().parent / "SEST_F-15EX_Revamp"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402

NEW_KEYS = ["AntiShipHeavy", "Quicksink", "BigStick174", "BigStick174ER",
            "Truck174", "Malice6", "MaliceER", "MaliceTruck",
            "AAMT120Tanks", "AAMT260Tanks"]

NEW_SECTIONS = """\
[--------------------------- SEST Revamp loadouts ---------------------------]
# Added by the SEST F-15EX Revamp patch. Requires the Dingtools Weapon Pack
# (dts_ weapons); the BigStick174 loadout additionally requires Murder Hornet
# (usn_aim-174b). The 610 gal tank is vanilla.

[WeaponSystem1AntiShipHeavy]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station15=usaf_tank_610_f-15|WT
Station26=dts_anaaq-33
Station27=dts_anaaq-13
[WeaponSystem2AntiShipHeavy]
Station1=dts_agm-158c-3|JDAM32
Station2=dts_agm-158c-3|JDAM32
Station3=dts_agm-158c-3|JDAM32
Station4=dts_agm-158c-3|JDAM32
Station13=dts_agm-158c-3|WW
Station14=dts_agm-158c-3|WW

[WeaponSystem1Quicksink]
ReadyUpTime=25               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=dts_gbu-31|JDAM31
Station12=dts_gbu-31|JDAM31
Station13=dts_gbu-31|JDAM31
Station14=dts_gbu-31|JDAM31
Station15=usaf_tank_610_f-15|WT
Station26=dts_anaaq-33
Station27=dts_anaaq-13

[WeaponSystem1BigStick174]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# AIM-260 on the inner wing pylon rails, which this fit used to leave empty.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=usn_aim-174b|SEST174
Station12=usn_aim-174b|SEST174
Station13=usn_aim-174b|SEST174
Station14=usn_aim-174b|SEST174
Station15=usaf_tank_610_f-15|WT
Station16=usn_aim-174b|WW
Station17=usn_aim-174b|WW

[WeaponSystem1BigStick174ER]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# The outer wing pylons are baked into the airframe model and render whether
# or not they carry anything, so use them: AMRAAM on the pylon2 inner
# stations, AIM-9X outboard of them on the outermost pair.
# AIM-260 on the inner wing pylon rails alongside the tanks.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=usn_aim-174b|SEST174
Station12=usn_aim-174b|SEST174
Station13=usn_aim-174b|SEST174
Station14=usn_aim-174b|SEST174
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|WT
Station17=usaf_tank_610_f-15|WT

[WeaponSystem1Truck174]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# 8-round AIM-174B missile truck: 4 under the fuselage (Bottom1 wells) and
# 4 on the inner wing pylons' shoulder rails, with the outer wing pylons
# carrying self-escort AAMs and centreline fuel only.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=usn_aim-174b|SEST174
Station12=usn_aim-174b|SEST174
Station13=usn_aim-174b|SEST174
Station14=usn_aim-174b|SEST174
Station16=usn_aim-174b|WW
Station17=usn_aim-174b|WW
Station15=usaf_tank_610_f-15|WT

[WeaponSystem1Malice6]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# MALICE mirror of BigStick174: 6x AIM-424 plus AIM-260 on the inner rails.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=sest_aim-424|M424
Station12=sest_aim-424|M424
Station13=sest_aim-424|M424
Station14=sest_aim-424|M424
Station15=usaf_tank_610_f-15|WT
Station16=sest_aim-424|M424W
Station17=sest_aim-424|M424W

[WeaponSystem1MaliceER]
ReadyUpTime=30               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# MALICE mirror of BigStick174ER: 4x AIM-424 under, 3 tanks, AIM-260 on the
# inner side rails (RAIL_EXEMPT keeps them; the outer pair is stripped).
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=sest_aim-424|M424
Station12=sest_aim-424|M424
Station13=sest_aim-424|M424
Station14=sest_aim-424|M424
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|WT
Station17=usaf_tank_610_f-15|WT

[WeaponSystem1AAMT120Tanks]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R
# Upstream's AAMT120 missile truck with three tanks and the fuselage dual
# racks FILLED. The AAMT rack mesh stays visible (its hide list matches the
# upstream truck's) and all eight belly rounds sit in real rack slots via
# the SESTR seats - see the seat-key comment for the geometry. Sixteen
# missiles, three tanks. Known trade, user-approved layout: the AAMT is one
# combined wing+belly mesh, so its (empty) wing twin racks render at the
# wing stations where the tanks hang - if the overlap reads badly in game,
# the alternative is hiding AAMT and losing the fuselage racks with it.
Station1=dts_aim-120d-3_w|120
Station2=dts_aim-120d-3_w|120
Station5=dts_aim-120d-3_w|120
Station6=dts_aim-120d-3_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-120d-3_w|120
Station10=dts_aim-120d-3_w|120
Station11=dts_aim-120d-3|SESTR-OR
Station12=dts_aim-120d-3|SESTR-OL
Station13=dts_aim-120d-3|SESTR-OR
Station14=dts_aim-120d-3|SESTR-OL
Station18=dts_aim-120d-3|SESTR-FL
Station19=dts_aim-120d-3|SESTR-FR
Station22=dts_aim-120d-3|SESTR-AR
Station23=dts_aim-120d-3|SESTR-AL
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|SESTWTF
Station17=usaf_tank_610_f-15|SESTWTF

[WeaponSystem1AAMT260Tanks]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R
# The AIM-260 twin of the dual-rack three-tank truck above.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-260_w|120
Station8=dts_aim-260_w|120
Station9=dts_aim-260_w|120
Station10=dts_aim-260_w|120
Station11=dts_aim-260|SESTR-OR
Station12=dts_aim-260|SESTR-OL
Station13=dts_aim-260|SESTR-OR
Station14=dts_aim-260|SESTR-OL
Station18=dts_aim-260|SESTR-FL
Station19=dts_aim-260|SESTR-FR
Station22=dts_aim-260|SESTR-AR
Station23=dts_aim-260|SESTR-AL
Station15=usaf_tank_610_f-15|WT
Station16=usaf_tank_610_f-15|SESTWTF
Station17=usaf_tank_610_f-15|SESTWTF

[WeaponSystem1MaliceTruck]
ReadyUpTime=35               // in minutes. Time that plane will spend refueling and rearming before takeoff.
CoolDownTime=60              // in minutes. Time that plane will spend in maintenance after landing.
SubModelsToHide=TER_Rack_Left,TER_Rack_Right,LAU-88_L,LAU-88_R,AAMT,Py13,Py33,33Glass
# MALICE mirror of Truck174: 8x AIM-424 plus self-escort AAMs on the outer
# wing pylons, centreline fuel only.
Station1=dts_aim-260_w|120
Station2=dts_aim-260_w|120
Station5=dts_aim-260_w|120
Station6=dts_aim-260_w|120
Station7=dts_aim-120d-3_w|120
Station8=dts_aim-120d-3_w|120
Station9=dts_aim-9x
Station10=dts_aim-9x
Station11=sest_aim-424|M424
Station12=sest_aim-424|M424
Station13=sest_aim-424|M424
Station14=sest_aim-424|M424
Station16=sest_aim-424|M424W
Station17=sest_aim-424|M424W
Station15=usaf_tank_610_f-15|WT

"""

LOADOUT_NAMES = {
    "en": {
        "AntiShipHeavy": "SEST AntiShipLRASM6",
        "Quicksink": "SEST StrikeQuicksink",
        "BigStick174": "SEST Intercept174",
        "BigStick174ER": "SEST Intercept174 LongRange",
        "Truck174": "SEST Intercept174 Truck (8x)",
        "Malice6": "SEST InterceptMALICE (6x AIM-424)",
        "MaliceER": "SEST InterceptMALICE LongRange",
        "MaliceTruck": "SEST InterceptMALICE Truck (8x)",
        "AAMT120Tanks": "SEST AAMT120 DualRack (16x, 3 tanks)",
        "AAMT260Tanks": "SEST AAMT260 DualRack (16x, 3 tanks)",
    },
    "cn": {
        "AntiShipHeavy": "SEST 重型反舰LRASM×6",
        "Quicksink": "SEST 快沉反舰JDAM",
        "BigStick174": "SEST 超远程截击174",
        "BigStick174ER": "SEST 超远程截击174 (远程)",
        "Truck174": "SEST 超远程截击174 (8联卡车)",
        "Malice6": "SEST 马利斯截击 (6x AIM-424)",
        "MaliceER": "SEST 马利斯截击 (远程)",
        "MaliceTruck": "SEST 马利斯截击 (8联卡车)",
        "AAMT120Tanks": "SEST AMRAAM双联卡车 (16弹 3副油箱)",
        "AAMT260Tanks": "SEST AIM-260双联卡车 (16弹 3副油箱)",
    },
}

# ---------------------------------------------------------------------------
# Squadrons
# ---------------------------------------------------------------------------
# Upstream defines two squadrons - the 44th and 67th FS at Kadena, each with
# its own livery texture. A mission that wants more than two distinct F-15EX
# units has nothing to reference, so this adds the type's other announced
# operators. The mod ships only those two skins, so the added squadrons reuse
# them in rotation and differ by identity and callsign rather than by paint.
#
# The first two entries MUST stay byte-identical to upstream's (checked at
# build time) so nothing that already references Squadron1/2 changes.
#
# (display name, basing note, livery texture, callsigns)
F15EX_SQUADRONS = [
    ("44th FS 'Vampires'", "18th Wing, Kadena AB, Japan",
     "44_fs.jpg", ["Dusk", "Lazarus"]),
    ("67th FS 'Fighting Cocks'", "18th Wing, Kadena AB, Japan",
     "67_fs.jpg", ["Gobbler", "Rooster"]),
    ("85th TES", "53rd Wing, Eglin AFB - first F-15EX operator",
     "44_fs.jpg", ["Bench"]),
    ("40th FLTS", "96th Test Wing, Eglin AFB",
     "67_fs.jpg", ["Probe"]),
    ("123rd FS 'Redhawks'", "142nd Wing OR ANG, Portland - first ANG F-15EX unit",
     "44_fs.jpg", ["Redhawk"]),
    ("194th FS 'Griffins'", "144th FW CA ANG, Fresno",
     "67_fs.jpg", ["Griffin"]),
    ("131st FS", "104th FW MA ANG, Barnes",
     "44_fs.jpg", ["Minuteman"]),
    ("114th FS 'Eagles'", "173rd FW OR ANG, Kingsley Field",
     "67_fs.jpg", ["Talon"]),
]

# ---------------------------------------------------------------------------
# Side-rail height
# ---------------------------------------------------------------------------
# CORRECTED. The first attempt dropped these 0.005 on the reasoning that they
# sat above the wing station (-0.0063) where the tank pylon attaches. That was
# an inference about the model, not a measurement, and it was too aggressive:
# the report was that ONE missile sat higher than the OTHERS, a relative
# difference, not that all of them were too high in absolute terms.
#
# What is actually measurable: all four side rails (1/2/5/6) are IDENTICAL in
# every loadout - same y, same |120 key, net -0.00050. They cannot differ from
# each other. The only real height difference among wing-mounted AAMs is
# between the two groups:
#
#     side rails  1/2/5/6   net y -0.00050
#     pylon2      7/8/9/10  net y -0.00120     0.0007 lower
#
# So the side rails sit 0.0007 above the outer-pylon missiles they fly beside.
# This levels them, and nothing more. Dropping further is guesswork until
# somebody who can see the model says the whole group is too high.
SIDE_RAIL_DROP = 0.0007
SIDE_RAIL_STATIONS = (1, 2, 5, 6)

LIVERY_FOLDER = "assets/textures/F-15EX/"

SQUADRONS_HEADER = """\
# SEST F-15EX Revamp - squadron definitions for the F-15EX.
# Upstream ships the two Kadena squadrons and their liveries; these add the
# type's other announced operators so a mission can field more than two
# distinct F-15EX units. The mod carries only those two skins, so the added
# squadrons reuse them in rotation and differ by identity and callsign.
[General]
SerialnumberReferences=AF_Serial
EmblemReference=Emblem
NationFlagReference=Flag1
NumberOfSquadrons={count}

[Default]
Nation=US

"""


def lower_side_rails(text):
    """Drop the inner-pylon side rails onto the pylon instead of into the wing."""
    moved = {}

    def drop(m):
        s, x, y, z, comment = int(m.group(1)), *[float(m.group(i)) for i in (2, 3, 4)], m.group(5) or ""
        if s not in SIDE_RAIL_STATIONS:
            return m.group(0)
        new_y = round(y - SIDE_RAIL_DROP, 6)
        moved[s] = (y, new_y, x)
        return f"Station{s}={m.group(2)},{new_y:g},{m.group(4)}{comment}"

    # ONLY the [WeaponSystem1] hardpoint block. WeaponSystem2 has its own
    # station table where 1/2/5/6 are fuselage wells, and rewriting those would
    # move the wrong stores - the same conflation that produced a page of false
    # positives in the symmetry audit.
    m = re.search(r"^\[WeaponSystem1\][^\n]*\n(.*?)(?=^\[WeaponSystem)", text, re.S | re.M)
    if not m:
        sys.exit("[WeaponSystem1] hardpoint block not found — upstream layout changed")
    text = text[:m.start(1)] + re.sub(
        r"^Station(\d+)=([-\d.]+),([-\d.]+),([-\d.]+)(\s*//.*)?$",
        drop, m.group(1), flags=re.M) + text[m.end(1):]
    missing = [s for s in SIDE_RAIL_STATIONS if s not in moved]
    if missing:
        sys.exit(f"side rail station(s) {missing} not found — upstream layout changed")

    # Both wings must move together, and nothing may end up at or below the tank.
    ys = {new for _old, new, _x in moved.values()}
    if len(ys) != 1:
        sys.exit(f"side rails ended at different heights: {sorted(ys)}")
    hp = re.search(r"^\[WeaponSystem1\][^\n]*\n(.*?)(?=^\[WeaponSystem)", text, re.S | re.M).group(1)
    tank_y = float(re.search(r"^Station17=[-\d.]+,([-\d.]+),", hp, re.M).group(1))
    new_y = ys.pop()
    if new_y <= tank_y:
        sys.exit(f"side rails dropped to {new_y} which is at or below the wing "
                 f"station at {tank_y} — reduce SIDE_RAIL_DROP")
    pairs = [(1, 2), (5, 6)]
    for a, b in pairs:
        if abs(moved[a][2] + moved[b][2]) > 1e-9:
            sys.exit(f"side rails S{a}/S{b} are no longer mirrored")
    old = next(iter(moved.values()))[0]
    print(f"  side rails S{list(SIDE_RAIL_STATIONS)} lowered {old:g} -> {new_y:g} "
          f"(net {new_y + 0.0005:g} with the 120 offset; pylon attaches at {tank_y:g})")
    return text


# --- The wing station owns its pylon ----------------------------------------
# Station16/17 ("Wing Station", |x| 0.04308) sits 0.0129 from BOTH wing pylon
# rails - Station5/6 inner (0.03743) and Station1/2 outer (0.0486). They are
# one physical pylon, so what hangs on the station decides what the rails can
# take. Upstream is consistent about it across every loadout it ships:
#
#   S16/17 = tank            -> rails EMPTY (Ferry, Strike183N) or AIM-9X
#                               (AirToAirLongRange). Nothing larger, ever.
#   S16/17 = |WW big store   -> rails EMPTY (StrikePrecision GBU-10,
#                               StrikeNuke B-61). No exceptions.
#   S16/17 = |MTW rack       -> rails loaded (AAMT120, AAMT260). The multi-rail
#                               rack is built to share the pylon; a tank and a
#                               2000 lb bomb are not.
#
# Five loadouts here broke it, on a comment reading "AIM-260 on the inner wing
# pylon rails alongside the tanks". There is no alongside - the missile renders
# through whatever is on the station. Reported in game on AAMT260Tanks (16x
# AIM-260, three tanks) and on the MALICE fits, both as a missile sitting on a
# rail that already had fuel on it.
WING_STATIONS = (16, 17)
WING_PYLON_RAILS = (1, 2, 5, 6)

# The rule, third revision, each step forced by in-game evidence. S1/S2 and
# S5/S6 are the OUTBOARD and INBOARD side rails of the same inner wing pylon
# (left wing: rails at -0.0486 and -0.03743, tank centred between them at
# -0.04308). The first revision stripped every rail whenever the wing station
# carried anything but an MTW rack. Then MaliceER flew all four rails armed
# with AIM-260 beside three tanks and the user confirmed it looks right - the
# rails hold stores at the pylon's flanks, above the tank's shoulder - so a
# TANK no longer restricts the rails at all. What still does is a wide |WW
# store (GBU-10, B-61, AIM-174B, AIM-424) hung ON the wing station itself:
# that occupies the space between the faces, and upstream never arms the
# rails around one.
# The trucks fly their side rails armed ABOVE the underslung round - user
# call, same in-game-verified coexistence as MaliceER's rails-beside-tank.
RAIL_EXEMPT = {(t, r) for t in ("MaliceTruck", "Truck174") for r in (1, 2, 5, 6)}


def _rail_allowance(station_store):
    """What the rails may carry given what is on the wing station."""
    if station_store is None:
        return "any"
    if "|MTW" in station_store or "tank" in station_store:
        return "any"                   # racks share the pylon; tanks proven in game
    return "none"                      # |WW and anything else big


def _walk_loadouts(text, fn):
    return re.sub(r"^\[WeaponSystem1([A-Za-z0-9_\-]+)\]\n(.*?)(?=^\[|\Z)",
                  fn, text, flags=re.M | re.S)


def clear_rails_under_wing_station(text):
    """Strip rail stores the wing station has no room for."""
    dropped = []

    def fix(m):
        name, body = m.group(1), m.group(2)
        st = dict(re.findall(r"^Station(\d+)=([A-Za-z]\S*)$", body, re.M))
        allow = _rail_allowance(next((st[str(k)] for k in WING_STATIONS
                                      if str(k) in st), None))
        if allow == "any":
            return m.group(0)
        out = body
        for k in WING_PYLON_RAILS:
            v = st.get(str(k))
            if not v or (name, k) in RAIL_EXEMPT:
                continue
            if allow == "aim-9" and "aim-9" in v.lower():
                continue
            out = re.sub(rf"^Station{k}={re.escape(v)}\n", "", out, flags=re.M)
            dropped.append((name, k, v))
        return f"[WeaponSystem1{name}]\n" + out

    text = _walk_loadouts(text, fix)
    for name in sorted({d[0] for d in dropped}):
        ks = [f"S{k}" for n, k, v in dropped if n == name]
        store = next(v for n, k, v in dropped if n == name)
        print(f"    {name}: cleared {len(ks)} rail(s) - {', '.join(ks)} = {store}")
    return text


def verify_rails_under_wing_station(text):
    """Refuse to ship a rail store sharing a pylon that cannot take it."""
    for m in re.finditer(r"^\[WeaponSystem1([A-Za-z0-9_\-]+)\]\n(.*?)(?=^\[|\Z)",
                         text, re.M | re.S):
        st = dict(re.findall(r"^Station(\d+)=([A-Za-z]\S*)$", m.group(2), re.M))
        allow = _rail_allowance(next((st[str(k)] for k in WING_STATIONS
                                      if str(k) in st), None))
        if allow == "any":
            continue
        for k in WING_PYLON_RAILS:
            v = st.get(str(k))
            if (m.group(1), k) in RAIL_EXEMPT:
                continue
            if v and not (allow == "aim-9" and "aim-9" in v.lower()):
                sys.exit(f"{m.group(1)}: Station{k}={v} shares the wing pylon "
                         f"with Station16/17 (allowance: {allow})")


def build_squadrons():
    """Complete replacement usaf_f-15ex_SEII_squadrons.ini (whole-file override)."""
    src = UPSTREAM / "aircraft" / "usaf_f-15ex_SEII_squadrons.ini"
    upstream = src.read_text(encoding="utf-8", errors="replace")

    # Guard: upstream's own two squadrons must still be what we think they are,
    # or we would silently change which jet wears which paint.
    for i, (_, _, livery, _) in enumerate(F15EX_SQUADRONS[:2], start=1):
        m = re.search(rf"^\[Squadron{i}\].*?^LiveryTexture=(\S+)", upstream, re.S | re.M)
        if not m or m.group(1) != livery:
            sys.exit(f"upstream Squadron{i} livery changed "
                     f"({m.group(1) if m else 'missing'} != {livery}) — rebase this patch")
    if len(re.findall(r"^\[Squadron\d+\]", upstream, re.M)) != 2:
        sys.exit("upstream no longer defines exactly 2 squadrons — rebase this patch")

    blocks = "".join(
        f"[Squadron{i}]  #{name} - {basing}\n"
        f"ResourcesLiveryFolder={LIVERY_FOLDER}\n"
        f"LiveryTexture={livery}\n"
        f"Nation=US\n\n"
        for i, (name, basing, livery, _) in enumerate(F15EX_SQUADRONS, start=1))
    body = SQUADRONS_HEADER.format(count=len(F15EX_SQUADRONS)) + blocks
    return body.rstrip("\n") + "\n"


def build_aircraft_names(lang):
    """Upstream's aircraft_names.ini with the new squadrons appended.

    Upstream's existing Squadron1/2 lines and its Callsigns value are kept
    verbatim - including the Chinese ones - so nothing already translated is
    replaced by English text; only the new units are added.
    """
    src = UPSTREAM / f"language_{lang}" / "aircraft_names.ini"
    text = src.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

    m = re.search(r"^Default=([^,\n]+),([^,\n]*)$", text, re.M)
    if not m:
        sys.exit(f"language_{lang}/aircraft_names.ini has no parsable Default= line")
    short = m.group(2).strip()

    kept = [l for l in text.rstrip("\n").splitlines()
            if not re.match(r"^(Squadron\d+|Callsigns)=", l)]
    existing_sq = re.findall(r"^Squadron\d+=.*$", text, re.M)
    if len(existing_sq) != 2:
        sys.exit(f"language_{lang}: expected 2 upstream squadron names, "
                 f"found {len(existing_sq)} — rebase this patch")
    calls = re.search(r"^Callsigns=(.*)$", text, re.M)
    if not calls:
        sys.exit(f"language_{lang}: no Callsigns line — rebase this patch")

    new_sq = [f"Squadron{i}=F-15EX {name},{short}"
              for i, (name, _, _, _) in enumerate(F15EX_SQUADRONS[2:], start=3)]
    new_calls = "|".join(f"Squadron{i}," + ",".join(c)
                         for i, (_, _, _, c) in enumerate(F15EX_SQUADRONS[2:], start=3))
    lines = kept + existing_sq + new_sq + [f"{calls.group(1)}|{new_calls}"
                                           if calls.group(1).startswith("Callsigns=")
                                           else f"Callsigns={calls.group(1)}|{new_calls}"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Symmetry repairs
# ---------------------------------------------------------------------------
# An aircraft hangs stores in mirrored pairs. Two upstream defects break that:
#
#  1. AirToAirIntercept puts dts_aim-260_w on Station9 (right outer wing pylon)
#     and dts_aim-9x on Station10 (left outer wing pylon) - visibly different
#     missiles on the same pair of pylons. Every other fit in the mod pairs
#     those two stations correctly (Default and AirToAir 9x/9x, LongRange and
#     AAMT120 120d-3/120d-3, AAMT260 260/260), and this is the only fit that
#     carries an ODD number of Sidewinders: exactly one, on the left wing.
#
#     Station10 is the stale half, not Station9: it reads plain `dts_aim-9x`
#     with no position key, which is the Default/AirToAir pattern, while every
#     other wing-rail missile in this loadout carries the `|120` rail offset.
#     So the fix matches Station10 to Station9 rather than the other way, which
#     also makes the fit a clean 12x AIM-260.
#
#  2. Stations 2, 3 and 4 sit at the IDENTICAL point x=+0.0486 - "Right Wing
#     pylon outer" plus TWO "Right Wing pylon bottom". There is no left-hand
#     pylon-bottom station at all, so anything mounted on 3 and 4 stacks on the
#     right wing with nothing opposite. Nothing in WeaponSystem1 uses them
#     today, so this is a latent trap rather than a live bug; Station4 is
#     mirrored to the left so the pair is usable and cannot spring it later.
# (section to edit, line to replace, replacement). Both edits are scoped to a
# named section: `Station10=dts_aim-9x` is CORRECT in 18 other loadouts, so a
# blind file-wide replace would have rewritten every one of them.
SYMMETRY_FIXES = [
    ("WeaponSystem1AirToAirIntercept",
     "Station10=dts_aim-9x",
     "Station10=dts_aim-260_w|120",
     "AirToAirIntercept left outer pylon: AIM-9X -> AIM-260 to match Station9"),
    ("WeaponSystem1",
     "Station4=0.0486,-0.001,-0.0079      //Right Wing pylon bottom",
     "Station4=-0.0486,-0.001,-0.0079     //Left Wing pylon bottom",
     "Station4 mirrored to the left wing (was a duplicate of the right)"),
]

# Pairs that are asymmetric on purpose and must NOT trip the guard below.
SYMMETRY_EXEMPT = {
    # Two different pods (AAQ-33 targeting, AAQ-13 navigation) on mounts at
    # slightly different heights - not a mirrored pair to begin with.
    (26, 27),
    # A single B61 on one wing station. Upstream's choice, and a real single
    # weapon carry is a thing; flagging it every build would be noise.
    (16, 17),
}


def fix_symmetry(text):
    """Repair the mirror-symmetry defects, failing loudly if upstream moved."""
    fixed = []
    for section, old, new, what in SYMMETRY_FIXES:
        m = re.search(rf"^\[{re.escape(section)}\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.S | re.M)
        if not m:
            sys.exit(f"section [{section}] not found — rebase this patch")
        body = m.group(1)
        if old not in body:
            sys.exit(f"[{section}] no longer contains {old!r} — it may already be fixed "
                     "upstream; rebase this patch")
        if body.count(old) != 1:
            sys.exit(f"{old!r} appears {body.count(old)} times in [{section}], expected 1 — rebase")
        text = text[:m.start(1)] + body.replace(old, new, 1) + text[m.end(1):]
        fixed.append(what)
    return text, fixed


def check_symmetry(text):
    """Fail the build if any loadout hangs mismatched stores on a mirror pair.

    Each [WeaponSystemN] #Hardpoint block owns its own station table, and a
    loadout named [WeaponSystemN<Name>] indexes into THAT table - conflating
    them produces a page of false positives, so the check is done per system.
    """
    problems = []
    for m in re.finditer(r"^\[WeaponSystem(\d+)\]([^\n]*)\n(.*?)(?=^\[WeaponSystem|\Z)",
                         text, re.S | re.M):
        if "Hardpoint" not in m.group(2):
            continue
        ws = m.group(1)
        pos, lab = {}, {}
        for sm in re.finditer(
                r"^Station(\d+)=([-\d.]+),([-\d.]+),([-\d.]+)\s*(?://\s*(.*))?$",
                m.group(3), re.M):
            pos[int(sm.group(1))] = tuple(round(float(sm.group(i)), 6) for i in (2, 3, 4))
            lab[int(sm.group(1))] = (sm.group(5) or "").strip()

        # Mirror partner: exactly negated x, same y and z, nearest index.
        mirror = {}
        for a, (x, y, z) in pos.items():
            if abs(x) < 1e-9:
                continue
            cands = [b for b, (x2, y2, z2) in pos.items()
                     if b != a and abs(x2 + x) < 1e-9 and abs(y2 - y) < 1e-9 and abs(z2 - z) < 1e-9]
            if cands:
                mirror[a] = min(cands, key=lambda b: abs(b - a))

        for lm in re.finditer(rf"^\[WeaponSystem{ws}([A-Za-z0-9_]+)\]\n(.*?)(?=^\[|\Z)",
                              text, re.S | re.M):
            st = {int(a): b for a, b in re.findall(r"^Station(\d+)=(\S+)", lm.group(2), re.M)}
            for s, store in sorted(st.items()):
                p = mirror.get(s)
                if p is None or s > p or tuple(sorted((s, p))) in SYMMETRY_EXEMPT:
                    continue
                other = st.get(p)
                if other is None:
                    problems.append(f"[{lm.group(1)}] S{s} ({lab[s]}) loaded, mirror S{p} empty")
                elif other.split("|")[0] != store.split("|")[0]:
                    problems.append(f"[{lm.group(1)}] S{s}={store} but mirror S{p}={other}")
    if problems:
        sys.exit("asymmetric loadouts:\n  " + "\n  ".join(sorted(set(problems))))


INFO_INI = """[Language_en]
Name=SEST F-15EX Revamp
Description=Ten extra F-15EX loadouts: 6x LRASM anti-ship surge, 4x GBU-31 Quicksink, and a what-if very-long-range family - 6x/4x+fuel/8x-truck AIM-174B fits plus matching 6x/4x+fuel/8x-truck AIM-424 MALICE fits, plus long-range versions of the AMRAAM and AIM-260 missile trucks that trade the wing twin-racks for fuel. Requires the F-15SE (F-15EX) mod and Dingtools Weapon Pack; AIM-174B fits also need Murder Hornet, and the MALICE model comes from US Naval Aviation. Place ABOVE the F-15EX mod in the Mod Manager.

[Compatibility]
ApproximateVersion=0.8.2
"""


def main():
    src = UPSTREAM / "aircraft" / "usaf_f-15ex_SEII.ini"
    text = src.read_text(encoding="utf-8")

    # 1. Extend AvailableLoadouts
    m = re.search(r"^(AvailableLoadouts=)(.+)$", text, re.M)
    if not m:
        sys.exit("AvailableLoadouts line not found — upstream layout changed")
    existing = [k.strip() for k in m.group(2).split(",")]
    clash = [k for k in NEW_KEYS if k in existing]
    if clash:
        sys.exit(f"loadout keys already exist upstream: {clash}")
    text = text[: m.start(2)] + m.group(2).rstrip() + "," + ",".join(NEW_KEYS) + text[m.end(2):]

    # 1b. A dedicated belly seat for the AIM-424. It shares stations 11-14
    #     with the AIM-174B, whose AGM key (0,-0.002,0) seats IT flush - but
    #     the 424 renders with the AGM-88G mesh, whose origin rides lower, and
    #     in game it hung visibly below the CFT pylon. Raising the shared key
    #     would unseat the 174, so the 424 gets its own, 0.0015 higher.
    agm = re.search(r"^AGMPositions=[^\n]*\n", text, re.M)
    if not agm:
        sys.exit("AGMPositions not found - upstream layout changed")
    if "M424Positions" in text:
        sys.exit("M424Positions already defined upstream - re-check")
    # 1c. Dual-rack slot seats for the 3-tank trucks. The AAMT rack mesh
    #     stays VISIBLE (user call: the fuselage racks are the look) and each
    #     of the four belly racks is FILLED with two real rounds. |MTH's two
    #     pipe segments (x +/-0.0022, y -0.0025, z -0.01) are the rack's two
    #     slots; segment assignment per station is engine-internal, so every
    #     round gets an explicit single-segment seat instead: SESTR-OR/OL put
    #     the S11-14 rounds in the outboard slots, and the four free fuselage
    #     stations 18/19/22/23 are offset into the inboard slots (offset =
    #     slot position minus station origin, the B-52O pylon technique).
    #     Rotations: S13/14 carry the station's +3 pitch natively; their
    #     partners S22/23 sit on +5 stations, so -2 nets +3 (assuming seat
    #     rotations ADD to the station's; if in game they lean the other way
    #     the engine replaces, and AR/AL want 3,0,0 instead).
    #     SEST174 seats the belly AIM-174B: |AGM raised 0.001 to sit flush
    #     with the fuselage (in-game call).
    text = (text[:agm.end()]
            + "M424Positions=0,-0.0005,0\n"
            + "M424WPositions=0,-0.0005,0\n"   # WW raised 0.001 - the 424 hung low underslung
            + "SEST174Positions=0,-0.001,0\n"
            + "SESTR-ORPositions=0.0022,-0.0025,-0.01\n"
            + "SESTR-OLPositions=-0.0022,-0.0025,-0.01\n"
            + "SESTR-FRPositions=-0.0082,-0.0055,0.0335\n"   # S19 z is -0.0335 like S18 (S20 owns 0.003 - the first cut used the wrong row and pushed this round aft)
            + "SESTR-FLPositions=0.0082,-0.0055,0.0335\n"
            + "SESTR-ARPositions=-0.0082,-0.005,0\n"
            + "SESTR-ALPositions=0.0082,-0.005,0\n"
            + "SESTR-ARRotations=-2,0,0\n"
            + "SESTR-ALRotations=-2,0,0\n"
            + "SESTWTFPositions=0,-0.002,0\n"   # DualRack wing tanks slung under the visible AAMT wing rack
            + text[agm.end():])

    # 2. Inject new sections just before the WeaponMagazines banner
    marker = "[---------- WeaponMagazines ----------]"
    if marker not in text:
        sys.exit("WeaponMagazines marker not found — upstream layout changed")
    text = text.replace(marker, NEW_SECTIONS + marker, 1)

    # 3. Validate: every referenced ammo id must exist in the ecosystem
    search_dirs = [UPSTREAM, WEAPON_PACK, MURDER_HORNET, VANILLA]
    known = {AIM424_ID}  # provided by this pack itself (written below)
    for d in search_dirs:
        known |= {p.stem for p in d.rglob("*.ini") if p.parent.name == "ammunition"}
    refs = set(re.findall(r"^Station\d+=([^|\s/]+)", NEW_SECTIONS, re.M))
    missing = sorted(r for r in refs if r not in known)
    if missing:
        sys.exit(f"unresolved ammunition ids: {missing}")

    # 4. Validate: every position key used exists in the hardpoint sections
    # scanned from the PATCHED text, so the M424 key injected above counts
    pos_keys = set(re.findall(r"^([\w\-]+)Positions=", text, re.M))
    used = set(re.findall(r"\|([\w\-]+)$", NEW_SECTIONS, re.M))
    bad = sorted(k for k in used if k not in pos_keys)
    if bad:
        sys.exit(f"unknown position keys: {bad}")

    # 5. Repair mirror symmetry, then refuse to ship anything still lopsided
    text, sym_fixed = fix_symmetry(text)
    text = lower_side_rails(text)
    check_symmetry(text)

    # 5b. The wing station owns its pylon - clear any rail store it has no
    #     room for, then refuse to ship if one survives.
    text = clear_rails_under_wing_station(text)
    verify_rails_under_wing_station(text)

    # 6. Write the mod folder
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "usaf_f-15ex_SEII.ini").write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    write_aim424(OUT)
    (OUT / "aircraft" / "usaf_f-15ex_SEII_squadrons.ini").write_text(
        build_squadrons(), encoding="utf-8")
    for lang in ("en", "cn"):
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "aircraft_names.ini").write_text(build_aircraft_names(lang),
                                              encoding="utf-8")
    for lang, names in LOADOUT_NAMES.items():
        src_names = UPSTREAM / f"language_{lang}" / "loadout_names.ini"
        body = src_names.read_text(encoding="utf-8").rstrip("\n")
        body += "\n# ---------- SEST Revamp ----------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")

    n_loadouts = len(existing) + len(NEW_KEYS)
    print(f"built {OUT.relative_to(ROOT)}: {n_loadouts} loadouts ({len(NEW_KEYS)} new), "
          f"{len(F15EX_SQUADRONS)} squadrons ({len(F15EX_SQUADRONS) - 2} new), "
          f"{len(refs)} ammo refs validated, {len(used)} position keys validated, "
          f"symmetry repaired ({len(sym_fixed)}) and verified")


if __name__ == "__main__":
    main()
