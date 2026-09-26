#!/usr/bin/env python3
"""Build the SEST B-52 ARRW patch: put the AGM-183A on every in-service B-52,
and make it actually loft.

TWO DEFECTS, both found by comparing against the collection rather than by
taste.

1. The AGM-183A flies flat. Dingtools' dts_agm-183a and dts_agm-183a(w62),
   which win the load order over the ARRW mod's own usn_arrw, model the
   weapon with SeaSkimming=True and SeaSkimmingAlt=90000: the sea-skimming
   flight model with the skim altitude moved to 90,000 ft, so the round
   climbs once and then holds that one altitude all the way in - a boost-
   glide weapon reduced to a high-altitude cruise missile. The files also
   declare no loft keys, no AccelerationTime and no VelocityBleed, so the
   boost has no defined duration and nothing holds speed through a glide.
   This pack used to add only MaxLoftAngle/MaxLoftAlt, which are inert while
   sea-skimming owns the trajectory.

   The profile now comes from the ARRW mod's usn_arrw, the reference
   implementation of this exact weapon: sea-skimming off, a 75 deg loft to
   99,000 ft, Acceleration 16 and VelocityBleed 0.6, with the boost cut to
   35 s so it lines up with the booster-separation mesh swap Dingtools'
   file already carries. usn_cps, the Navy boost-glide round, corroborates
   the shape. The hardware stays Dingtools': usn_arrw gets that wrong -
   850 kg against the real ~2270 kg, Power 45 against 300, and a MaxVelocity
   written "10,648" with a thousands separator that no other value in the
   collection uses - so Dingtools keeps its mass, motor and warhead and only
   the flight profile changes. Every key it overrides is checked as
   (expected, new), so an upstream value change fails the build.

2. The B-52H cannot carry the W62. dts_agm-183a(w62) ships in the B-52H mod's
   own folder, and the F-15EX and B-1B both have loadouts for it - but the
   B-52H, the only aircraft that ever actually flew ARRW, has none. Adding
   Strike183Nuke mirrors the existing Strike183 exactly: the same four pylon
   stations, the same position keys, the same SubModelsToHide.

3. The three B-52s each flew fits the others could not, for no reason but
   which mod defined them. The B-52H's AntiShip is 20 rounds of AGM-158C-3
   (8 in the rotary launcher, 3 on each of four pylon seats) while this pack
   had given the B-52O a 16-round fit of its own invention; the 419th FLTS
   testbed had exactly one loadout. They are the same airframe where it
   matters - identical bay table, identical pylon coordinates, the H just
   declares more rows - so the H's 20-round fit now flies on all three and
   the testbed's usn_arrw fit flies on both B-52s and on the B-1B, each on
   the carriage its own file already proved. assert_shared_geometry() fails
   the build the day that stops being true.

Usage (repo root):  python3 integration/b52-arrw/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "SEST_B52_ARRW"

B52_MOD = ROOT / "mods-source" / "3741944366"      # B-52H, ships dts_b-52h
RSA = ROOT / "mods-source" / "3413868677"          # Red Storm Arsenal, ships usaf_b-52o
ARRW_MOD = ROOT / "mods-source" / "3502273861"     # ARRW, ships the 419th FLTS bird
DINGTOOLS = ROOT / "mods-source" / "3760871384"    # Dingtools, WINS both AGM-183A files

B1B_MOD = ROOT / "mods-source" / "3652097318"      # B-1B, ships usaf_b-1b_dts

# --- The three B-52s are one airframe as far as carriage goes ---------------
# Checked across the exported files, and the reason a fit can be ported
# between them at all:
#
#   WS1 (bomb bay)   identical table on all three; Station6 is the CSRL
#   WS2 (pylons)     identical coordinates - the forward pair is
#                    -/+0.077,-0.0071,0.0693 in every one of the three
#
# The H differs only by DECLARING more pylon rows (8 against 2); the rows it
# adds sit at coordinates the others simply do not list. So porting the H's
# 20-round fit is not a guess about three models, it is the same numbers on
# the same points - which is the argument build_b52o() already makes for the
# ARRW pylon. assert_shared_geometry() fails the build if that stops holding.
PYLON_FWD = ("-0.077,-0.0071,0.0693", "0.077,-0.0071,0.0693")
PYLON_AFT = ("-0.077,-0.0071,-0.02", "0.077,-0.0071,-0.02")   # the H's Station7/8
CSRL_BAY = "0,-0.0135,0.0026"                                  # WS1 Station6

# The H's own 20-round LRASM fit: 8 in the rotary launcher plus 3 on each of
# four pylon seats. AGM86_Pylon is a 3-position triangle, which is where the
# 12 come from - the other B-52s' 6-position pylon keys are a different rack
# and would give a different count and a different silhouette.
LRASM = "dts_agm-158c-3"
AGM86_PYLON = "0,-0.005,0.048|-0.0084,0.0000,0.048|0.0084,0.0000,0.048"
# And the cant that makes those three points a triangle instead of a row.
# Leaving this line off was a real bug in the first port: the B-52O and the
# testbed got the positions and not the rotations, so their outer two rounds
# stood upright out to the side of the rack instead of rolled 45 deg in
# against it - reported in game as the LRASM fits "not angled on the wing
# pylons". The H had it right all along; the port simply dropped half the
# seat. A position key and its rotation key are one seat, never one without
# the other. assert_pylon_seat() now fails the build if either drifts.
AGM86_PYLON_ROT = "1,0,0|1,0,-45|1,0,45"


def _stations(text, block_name):
    """The Station<n>=x,y,z rows of one WeaponSystem block, as {n: 'x,y,z'}."""
    m = re.search(rf"^\[{re.escape(block_name)}\][^\n]*\n(.*?)(?=^\[WeaponSystem)",
                  text, re.M | re.S)
    if not m:
        sys.exit(f"[{block_name}] not found - upstream layout changed")
    return {int(n): v.strip() for n, v in
            re.findall(r"^Station(\d+)=([-\d.,]+)\s*(?://.*)?$", m.group(1), re.M)}


def assert_pylon_seat(text):
    """The H owns the AGM86_Pylon seat; the ports copy it verbatim.

    Both halves are checked, because the rotations half is the one that got
    left behind once already."""
    for key, want in (("AGM86_PylonPositions", AGM86_PYLON),
                      ("AGM86_PylonRotations", AGM86_PYLON_ROT)):
        m = re.search(rf"^{key}=([^\n]+)$", text, re.M)
        got = m and re.split(r"\s*(?:#|//)", m.group(1))[0].strip()
        if got != want:
            sys.exit(f"dts_b-52h.ini: {key} is {got!r}, expected {want!r} - the "
                     "donor seat moved, re-copy it into this script by hand")


def assert_shared_geometry(files):
    """Refuse to port a fit if the airframes stop agreeing on where things are."""
    for name, text in files.items():
        ws1, ws2 = _stations(text, "WeaponSystem1"), _stations(text, "WeaponSystem2")
        if ws1.get(6) != CSRL_BAY:
            sys.exit(f"{name}: WS1 Station6 is {ws1.get(6)!r}, expected the CSRL at "
                     f"{CSRL_BAY!r} - the bay table moved, re-check by hand")
        if (ws2.get(1), ws2.get(2)) != PYLON_FWD:
            sys.exit(f"{name}: WS2 pylon pair is {(ws2.get(1), ws2.get(2))!r}, expected "
                     f"{PYLON_FWD!r} - the airframes no longer share pylon geometry")


# THE ROUND FLEW FLAT, and adding loft keys alone could never fix it.
#
# Dingtools' dts_agm-183a - which wins the load order over the ARRW mod's own
# usn_arrw - models the weapon with SeaSkimming=True and SeaSkimmingAlt=90000.
# That is the sea-skimming flight model with the skim altitude moved to 90,000
# feet: climb, then hold ONE ALTITUDE all the way in. A boost-glide weapon
# reduced to a high-altitude cruise missile. Worse, the loft keys this pack
# used to add were inert underneath it - the profile that owns the trajectory
# was never loft, so MaxLoftAngle changed nothing anyone could see.
#
# The ARRW mod's own usn_arrw is the reference implementation of this exact
# weapon and it does it properly: no sea-skimming, a steep 75 deg loft to
# 99,000 ft, a long powered boost (AccelerationTime=75.7) and VelocityBleed to
# hold hypersonic speed through the glide. Those are the author's figures for
# this airframe, so they are taken rather than invented - except the boost
# duration, which is cut to match booster separation (see SET below).
#
# usn_cps, the Navy boost-glide round, corroborates the shape: loft to 90,000
# ft, no sea-skimming, IgnoreHeightDifferenceForTargetDist=True, a long
# terminal dive.
ADD = {
    # Dingtools' copy declares NO loft keys at all - it had no loft phase to
    # tune, which is the other half of why the round flew flat.
    # 75 deg and 99,000 ft are the ARRW mod author's own figures for this
    # airframe; they only take effect now that SeaSkimming is off.
    "MaxLoftAngle": "75.0",
    "MaxLoftAlt": "99000.0",
    # No AccelerationTime at all upstream, so the boost had no defined
    # duration. 35 s of powered climb, then the vehicle is on its own.
    "AccelerationTime": "35.0",
    # 0.6 = keep most of the speed through the glide instead of bleeding to
    # subsonic. The ARRW mod's value; nothing in Dingtools' copy retained speed.
    "VelocityBleed": "0.6",
    "IgnoreHeightDifferenceForTargetDist": "True",
    "TerminalVelocity": "3800",
}

# Keys that EXIST upstream and carry the wrong value. Each is (old, new) so a
# silent upstream change to the value cannot be overwritten unnoticed.
SET = {
    # The whole defect. False hands the trajectory back to the loft keys.
    "SeaSkimming": ("True", "False"),
    # 6.0 leaves it wallowing off the wing; both CPS and the ARRW mod use 16.
    "Acceleration": ("6.0", "16.0"),
}

# The mesh swap is ALREADY in Dingtools' file: ResourcesMeshForLaunch=launch
# becomes ResourcesMesh=AGM at ResourcesMeshSwitchTime. It fired at 15 s, which
# matched no physical event because no boost duration existed. Aligned to
# AccelerationTime it becomes what it looks like - booster burnout, the boosted
# stack dropping away and the glide vehicle flying on.
MESH_SWITCH = ("15", "35.0")

AGM183 = ["dts_agm-183a", "dts_agm-183a(w62)"]

# One key per fit, shared across airframes: loadout names are a GLOBAL
# key->name table, so the same fit on four aircraft wants the same key and
# gets one name. Neither key is used by any mission file (checked).
LRASM20_KEY = "AntiShipLRASM20"
TESTBED_KEY = "ARRWTestbed"
TESTBED_ROUND = "usn_arrw"


def extend_pylon_table(text, name):
    """Give a 2-station pylon table the H's aft pair, and the AGM86 seat.

    The recipients declare only the forward pylon pair. The H's 20-round fit
    hangs three rounds on each of two pairs, so the aft rows have to exist
    before the fit can be ported. They are the H's own Station7/8 verbatim -
    same coordinates, and like the H's, no per-station Rotation line (it
    defines those only for stations 1-6).

    The SEAT is a different thing from the station, and both halves of it
    come across: AGM86_PylonPositions and AGM86_PylonRotations. The first
    port copied only the positions, which is why the ported fits' outer
    rounds sat upright instead of rolled in against the rack."""
    m = re.search(r"^\[WeaponSystem2\][^\n]*\n(.*?)(?=^\[WeaponSystem)", text, re.M | re.S)
    if not m:
        sys.exit(f"{name}: [WeaponSystem2] not found - upstream layout changed")
    body = m.group(1)
    n = re.search(r"^NumberOfStations=(\d+)$", body, re.M)
    if not n or n.group(1) != "2":
        sys.exit(f"{name}: WS2 declares {n and n.group(1)} stations, expected 2 - "
                 "upstream added pylon rows, re-check the port by hand")
    if "AGM86_Pylon" in body:
        sys.exit(f"{name}: AGM86_Pylon already defined upstream - re-check")

    new = body.replace(f"NumberOfStations=2", "NumberOfStations=4", 1)
    st2 = re.search(r"^Station2=[^\n]*\n", new, re.M)
    new = (new[:st2.end()]
           + f"Station3={PYLON_AFT[0]}       //Left Pylon aft (ported from the B-52H)\n"
           + f"Station4={PYLON_AFT[1]}        //Right Pylon aft (ported from the B-52H)\n"
           + new[st2.end():])
    mt = re.search(r"^ModuleType=Weapon\n", new, re.M)
    if not mt:
        sys.exit(f"{name}: no ModuleType=Weapon in WS2 to anchor the seat key to")
    new = (new[:mt.end()]
           + "\n#AGM-86 pylon triangle, ported from the B-52H with its 20x LRASM fit\n"
           + f"AGM86_PylonPositions={AGM86_PYLON}\n"
           + f"AGM86_PylonRotations={AGM86_PYLON_ROT}\n"
           + new[mt.end():])
    return text[:m.start(1)] + new + text[m.end(1):]


def lrasm20(bay_template, name):
    """The H's 20-round LRASM fit: 8 in the CSRL, 3 on each of four pylons."""
    bay = re.sub(r"^Station\d+=.*$", f"Station6={LRASM}|CSRL", bay_template.rstrip("\n"),
                 count=1, flags=re.M)
    if f"Station6={LRASM}|CSRL" not in bay:
        sys.exit(f"{name}: could not seat the CSRL round in the bay template")
    return (f"[WeaponSystem1{LRASM20_KEY}]\n" + bay + "\n"
            + f"[WeaponSystem2{LRASM20_KEY}]\n"
            + "".join(f"Station{s}={LRASM}|AGM86_Pylon\n" for s in (1, 2, 3, 4)))


def declare(text, name, *keys):
    """Append loadout keys to AvailableLoadouts, refusing to double-declare."""
    m = re.search(r"^AvailableLoadouts=([^\n]+)$", text, re.M)
    if not m:
        sys.exit(f"{name}: no AvailableLoadouts line - upstream layout changed")
    have = [k.strip() for k in m.group(1).split(",")]
    clash = [k for k in keys if k in have]
    if clash:
        sys.exit(f"{name}: loadout key(s) already declared upstream: {clash}")
    return text[:m.start(1)] + m.group(1).rstrip() + "," + ",".join(keys) + text[m.end(1):]


def add_loft(text: str, name: str) -> str:
    """Turn the high-altitude cruise back into a boost-glide profile."""
    for key in ADD:
        if re.search(rf"^{re.escape(key)}=", text, re.M):
            sys.exit(f"{name}: {key} already present - upstream changed, re-check by hand")

    for key, (want, new) in SET.items():
        m = re.search(rf"^{re.escape(key)}=([^\s/]*)([^\n]*)$", text, re.M)
        if not m:
            sys.exit(f"{name}: {key} not found upstream - re-check this override by hand")
        if want and m.group(1) != want:
            sys.exit(f"{name}: {key} is {m.group(1)!r} upstream, expected {want!r} - "
                     "the author changed it, re-check whether this override is still right")
        text = text[:m.start()] + f"{key}={new}{m.group(2)}" + text[m.end():]

    m = re.search(r"^ResourcesMeshSwitchTime=([^\s/]*)([^\n]*)$", text, re.M)
    if not m:
        sys.exit(f"{name}: no ResourcesMeshSwitchTime - the launch-mesh swap is gone")
    want, new = MESH_SWITCH
    if m.group(1) != want:
        sys.exit(f"{name}: ResourcesMeshSwitchTime is {m.group(1)!r}, expected {want!r} - "
                 "re-check it still marks booster separation")
    text = text[:m.start()] + f"ResourcesMeshSwitchTime={new}{m.group(2)}" + text[m.end():]

    m = re.search(r"^SeaSkimmingAlt=[^\n]*\n", text, re.M)
    if not m:
        sys.exit(f"{name}: no SeaSkimmingAlt to anchor the added keys to")
    block = "".join(f"{k}={v}\n" for k, v in ADD.items())
    return text[:m.end()] + block + text[m.end():]


def build_ammunition():
    for a in AGM183:
        src = DINGTOOLS / "ammunition" / f"{a}.ini"
        if not src.exists():
            sys.exit(f"missing upstream: {src}")
        out = add_loft(src.read_text(encoding="utf-8-sig"), a)
        dst = OUT / "ammunition" / f"{a}.ini"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out, encoding="utf-8")
        print(f"  ammunition/{a}.ini  (+{len(ADD)} added, {len(SET)} corrected, mesh swap -> {MESH_SWITCH[1]}s)")


def build_aircraft(testbed):
    src = B52_MOD / "aircraft" / "dts_b-52h.ini"
    text = src.read_text(encoding="utf-8-sig")

    # Mirror Strike183 exactly, swapping only the round. Copying the real block
    # rather than writing one keeps the station numbers and position keys
    # correct even if the mod author moves them later.
    m = re.search(r"^\[WeaponSystem1Strike183\]\n(.*?)(?=^\[WeaponSystem2Strike183\])"
                  r"(\[WeaponSystem2Strike183\]\n)(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not m:
        sys.exit("Strike183 not found in dts_b-52h.ini - upstream changed")
    ws1_body, ws2_body = m.group(1), m.group(3)
    if "dts_agm-183a" not in ws2_body:
        sys.exit("Strike183 no longer carries dts_agm-183a - re-check by hand")

    # The rounds hung visibly below the pylon adapter in game (user
    # screenshot, confirmed as the H specifically). Upstream seats both
    # ARRW keys at y=-0.003; raise to -0.002.
    text, n = re.subn(r"^(AGM183[FB]Positions=0,)-0\.003(,0\.01)$",
                      r"\g<1>-0.002\g<2>", text, flags=re.M)
    if n != 2:
        sys.exit(f"dts_b-52h.ini: expected 2 ARRW position keys to raise, got {n}")

    # The bay was EMPTY on both ARRW fits - the block existed with nothing in
    # it. Fill it from the aircraft's own donors: Strike158 proves the CSRL
    # carries dts_agm-158b-2 (8x JASSM-ER, 800 nm) with this exact
    # SubModelsToHide list, and the nuclear fit takes usaf_agm-86b, the real
    # nuclear ALCM (Power 1000, from the B-52G AGM-86 mod's own family).
    if "Station6=dts_agm-158b-2|CSRL" not in text:
        sys.exit("dts_b-52h.ini: Strike158 no longer carries the 158B-2 CSRL - re-check")
    if re.search(r"^Station\d+=", ws1_body, re.M):
        sys.exit("dts_b-52h.ini: Strike183 bay is no longer empty upstream - re-check")
    conv_bay = ws1_body + "Station6=dts_agm-158b-2|CSRL\n"
    nuke_bay = ws1_body + "Station6=usaf_agm-86b|CSRL\n"

    nuke = ("[WeaponSystem1Strike183Nuke]\n" + nuke_bay
            + "[WeaponSystem2Strike183Nuke]\n"
            + ws2_body.replace("dts_agm-183a|", "dts_agm-183a(w62)|"))
    if "(w62)" not in nuke:
        sys.exit("W62 substitution did not take - station syntax changed")

    # The 419th FLTS testbed's own fit on the H's proven ARRW carriage: its
    # usn_arrw round, one in the bay (no rotary key, as the testbed carries
    # it) and the four pylon rounds Strike183 already seats correctly. The
    # round lives in the ARRW mod, so this fit exists only when that is
    # exported.
    if testbed:
        nuke += ("\n[WeaponSystem1" + TESTBED_KEY + "]\n"
                 + ws1_body + f"Station6={TESTBED_ROUND}\n"
                 + "[WeaponSystem2" + TESTBED_KEY + "]\n"
                 + re.sub(r"=dts_agm-183a\|", f"={TESTBED_ROUND}|", ws2_body))
    # and load the conventional fit's own bay in place
    text = (text[:m.start()]
            + "[WeaponSystem1Strike183]\n" + conv_bay
            + "[WeaponSystem2Strike183]\n" + ws2_body
            + text[m.end():])
    m = re.search(r"^\[WeaponSystem1Strike183\]\n(.*?)(?=^\[WeaponSystem2Strike183\])"
                  r"(?:\[WeaponSystem2Strike183\]\n)(.*?)(?=^\[|\Z)", text, re.M | re.S)

    # Append after the Strike183 pair, and register it in the picker.
    text = text[:m.end()] + "\n" + nuke + text[m.end():]
    keys = ["Strike183Nuke"] + ([TESTBED_KEY] if testbed else [])
    text = declare(text, "dts_b-52h.ini", *keys)

    dst = OUT / "aircraft" / "dts_b-52h.ini"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    n = nuke.count("dts_agm-183a(w62)")
    extra = f"; +{TESTBED_KEY} 1+4x usn_arrw" if testbed else ""
    print(f"  aircraft/dts_b-52h.ini  (+Strike183Nuke {n}x W62; "
          f"bays: 8x JASSM-ER / 8x AGM-86B{extra})")


def drop_stale(*rels):
    """Remove pack output whose upstream mod is no longer exported.

    Skipping the build of a file does not unship the copy from last time. A
    stale unit .ini left behind after its mod is unsubscribed describes a unit
    whose model is gone - the same trap as mods-source keeping directories for
    mods you removed.
    """
    for rel in rels:
        f = OUT / rel
        if f.exists():
            f.unlink()
            print(f"    removed stale {rel} (upstream no longer exported)")


def build_b52o(testbed):
    """Give Red Storm Arsenal's B-52O the ARRW, on the pylon it already uses.

    First cut reused RSA's RGM110_Rack position key, on the theory that its
    large-hypersonic fit was the ARRW fit. In game the missile hung visibly
    below the pylon: that key's -0.0090 y-offset is tuned for the much fatter
    AGM-110L. The B-52H settles it - it flies the SAME round under the SAME
    pylon geometry (stations at y=-0.0071, x=+/-0.077 in both files) with a
    -0.003 offset, flush, and carries TWO per side nose-to-tail at 0.0457 of
    z-separation. So the pack now injects its own AGM183_Pylon key into the
    B-52O's WeaponSystem2, reproducing the H's proven silhouette exactly:
    aft round at z-0.02, forward round at z+0.062, both at y=-0.003
    (the user confirmed this height correct; the hang-low report was the H). The
    height checked out in game; the separation has been widened twice on
    screenshots - the H's 0.0457 was too tight, 0.0677 still lapped the
    forward round's fins - and now sits at 0.082 nose-to-tail. Two per pylon, four per loadout.

    The pack's own 16-round AntiShipLRASM (8 external on an invented
    LRASM_Pylon key + 8 in the CSRL) is GONE, replaced by the B-52H's
    20-round fit on the H's own AGM86_Pylon triangle - more rounds, and the
    author's geometry instead of this pack's.

    Its WeaponSystem1 wing pylons (Station7/8) are deliberately NOT used - the
    matching #RGM110_RackPositions there is commented out in RSA's own file, so
    the author disabled that carriage and second-guessing it would put missiles
    at an offset nobody has ever looked at.
    """
    src = RSA / "aircraft" / "usaf_b-52o.ini"
    if not src.exists():
        print("  usaf_b-52o.ini  SKIPPED - Red Storm Arsenal not exported")
        drop_stale("aircraft/usaf_b-52o.ini")
        return
    text = src.read_text(encoding="utf-8-sig")
    m = re.search(r"^\[WeaponSystem2AntiShipHeavy\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not m:
        sys.exit("usaf_b-52o.ini: AntiShipHeavy not found - upstream changed")
    body = m.group(1)
    if "usn_agm_110l|RGM110_Rack" not in body:
        sys.exit("usaf_b-52o.ini: AntiShipHeavy no longer uses the RGM110 rack")

    # Our own position key, injected into the WS2 table next to the author's.
    # Geometry is the B-52H's proven two-per-side ARRW carriage, verbatim.
    if "AGM183_Pylon" in text or "LRASM_Pylon" in text:
        sys.exit("usaf_b-52o.ini: AGM183_Pylon already defined upstream - re-check")
    rk = re.search(r"^RGM110_RackPositions=[^\n]*\n", text, re.M)
    if not rk:
        sys.exit("usaf_b-52o.ini: RGM110_RackPositions gone - upstream changed")
    text = (text[:rk.end()]
            + "AGM183_PylonPositions=0,-0.003,-0.02|0,-0.003,0.062\n"
            + text[rk.end():])
    m = re.search(r"^\[WeaponSystem2AntiShipHeavy\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    body = m.group(1)

    # Bay: the O's own Standoff donor - a CSRL of AGM-86 - minus "Pylons" from
    # its SubModelsToHide, because unlike Standoff our fits hang ARRW out there.
    sd = re.search(r"^\[WeaponSystem1Standoff\]\n(.*?)(?=^\[)", text, re.M | re.S)
    if not sd or "Station6=usaf_agm-86c|CSRL" not in sd.group(1):
        sys.exit("usaf_b-52o.ini: Standoff CSRL donor gone - upstream changed")
    bay = sd.group(1).replace("SubModelsToHide=Pylons,", "SubModelsToHide=")

    # HISTORY, kept because it says what NOT to do here: the retired
    # AntiShipLRASM hung its rounds on an LRASM_Pylon key invented in this
    # pack, after a first cut on AGM84_Pylon made the fat LRASM airframes
    # read as a Harpoon cluster. Both are gone - the B-52H's own 20-round
    # fit below uses the H's AGM86_Pylon triangle instead, so the carriage
    # is the mod author's rather than this pack's guess at one.
    fits = [("Strike183", "dts_agm-183a|AGM183_Pylon", "usaf_agm-86c"),
            ("Strike183Nuke", "dts_agm-183a(w62)|AGM183_Pylon", "usaf_agm-86b")]
    # The ARRW testbed's own fit, on the O's proven ARRW carriage: one round
    # in the rotary launcher and two per pylon, the 419th FLTS arrangement.
    # It flies usn_arrw, so it only exists when the ARRW mod is exported.
    if testbed:
        fits.append((TESTBED_KEY, f"{TESTBED_ROUND}|AGM183_Pylon", TESTBED_ROUND))
    blocks = ""
    for name, ws2, alcm in fits:
        bay_block = bay.replace("usaf_agm-86c", alcm).rstrip("\n")
        if name == TESTBED_KEY:
            # A single round on the CSRL station, not a rotary of eight -
            # the bay round the testbed actually carries.
            bay_block = bay_block.replace(f"Station6={TESTBED_ROUND}|CSRL",
                                          f"Station6={TESTBED_ROUND}")
        blocks += (f"[WeaponSystem1{name}]\n" + bay_block + "\n"
                   + f"[WeaponSystem2{name}]\n"
                   + body.replace("usn_agm_110l|RGM110_Rack", ws2).rstrip("\n") + "\n\n")

    # The 20-round LRASM fit, ported whole from the B-52H. It REPLACES this
    # pack's own AntiShipLRASM (8 external + 8 CSRL = 16 on a pylon key
    # invented here): the H's is the bigger load and the author's own
    # geometry, and the two airframes' pylons are the same points.
    text = extend_pylon_table(text, "usaf_b-52o.ini")
    blocks += lrasm20(bay, "usaf_b-52o.ini") + "\n"

    m = re.search(r"^\[WeaponSystem2AntiShipHeavy\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    text = text[:m.end()] + "\n" + blocks + text[m.end():]
    text = declare(text, "usaf_b-52o.ini", *[f[0] for f in fits], LRASM20_KEY)

    dst = OUT / "aircraft" / "usaf_b-52o.ini"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    extra = f", +{TESTBED_KEY} 1+4x usn_arrw" if testbed else ""
    print(f"  aircraft/usaf_b-52o.ini  (+Strike183/+Nuke 4x ARRW; "
          f"+{LRASM20_KEY} 8+12x LRASM, replacing the 16-round fit{extra})")


def build_419_flts():
    """Fix usn_arrw's MaxVelocity typo.

    It declares MaxVelocity=10,648 - the ONLY numeric value carrying a
    thousands separator anywhere in the ammunition of all 129 exported mods.
    Nothing else in the collection writes a number that way, so it is a typo,
    and a parser reading it as 10 knots leaves the round crawling.

    NOT touched: this aircraft's AvailableLoadouts. An earlier version of this
    script declared Empty and Default here, on the reasoning that the blocks
    existed but were unreachable. That was wrong. Vanilla's own usn_f-14a and
    usaf_b-52g do not declare them either and plainly have them in game, and
    95 of 135 allied airframes across the collection are the same - the game
    supplies Default/Empty/Ferry implicitly. Declaring them adds nothing and
    risks a doubled entry in the picker.
    """
    a = ARRW_MOD / "ammunition" / "usn_arrw.ini"
    if not a.exists():
        print("  usn_arrw.ini  SKIPPED - ARRW mod not exported")
        drop_stale("ammunition/usn_arrw.ini", "aircraft/usaf_b-52h_419_flts.ini")
        return
    at = a.read_text(encoding="utf-8-sig")
    fixed = re.sub(r"^(MaxVelocity=)([0-9]{1,3}),([0-9]{3})\b", r"\1\2\3", at, flags=re.M)
    if fixed == at:
        sys.exit("usn_arrw.ini: the MaxVelocity thousands separator is gone - re-check")
    (OUT / "ammunition").mkdir(parents=True, exist_ok=True)
    (OUT / "ammunition" / "usn_arrw.ini").write_text(fixed, encoding="utf-8")
    print("  ammunition/usn_arrw.ini  (MaxVelocity 10,648 -> 10648)")

    # The testbed flies ONE fit. Give it the H's 20-round LRASM fit too, so
    # the ARRW aircraft is not a one-trick airframe while its two siblings
    # carry the same anti-ship load. Its bay template is its own
    # AntiShipPrecision block - the recipient's submodel names, not the H's.
    src = ARRW_MOD / "aircraft" / "usaf_b-52h_419_flts.ini"
    if not src.exists():
        print("  usaf_b-52h_419_flts.ini  SKIPPED - aircraft file not exported")
        drop_stale("aircraft/usaf_b-52h_419_flts.ini")
        return
    text = src.read_text(encoding="utf-8-sig")
    m = re.search(r"^\[WeaponSystem1AntiShipPrecision\]\n(.*?)(?=^\[)", text, re.M | re.S)
    if not m or f"Station6={TESTBED_ROUND}" not in m.group(1):
        sys.exit("usaf_b-52h_419_flts.ini: AntiShipPrecision bay block gone - upstream changed")
    text = extend_pylon_table(text, "usaf_b-52h_419_flts.ini")

    end = re.search(r"^\[WeaponSystem2AntiShipPrecision\]\n(.*?)(?=^\[|\Z)",
                    text, re.M | re.S)
    if not end:
        sys.exit("usaf_b-52h_419_flts.ini: AntiShipPrecision pylon block gone")
    text = (text[:end.end()] + "\n"
            + lrasm20(m.group(1), "usaf_b-52h_419_flts.ini") + "\n"
            + text[end.end():])
    text = declare(text, "usaf_b-52h_419_flts.ini", LRASM20_KEY)
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "usaf_b-52h_419_flts.ini").write_text(text, encoding="utf-8")
    print(f"  aircraft/usaf_b-52h_419_flts.ini  (+{LRASM20_KEY} 8+12x LRASM)")


def build_b1b(testbed):
    """Give the B-1B the testbed's ARRW round on its own six pylon seats.

    The B-1B already flies dts_agm-183a from Strike183 - six rounds on the
    three LAM pylon pairs, each a bare station seat the mod author placed.
    The testbed fit is the same six seats with the ARRW mod's own round, so
    nothing about the carriage is invented here; only the round changes.
    Unlike the B-52s there is no bay round: the B-1B's bays are separate
    weapon systems with their own racks, and external carriage is what the
    real aircraft flew its hypersonic tests with."""
    src = B1B_MOD / "aircraft" / "usaf_b-1b_dts.ini"
    if not (testbed and src.exists()):
        why = "ARRW mod not exported" if src.exists() else "B-1B mod not exported"
        print(f"  usaf_b-1b_dts.ini  SKIPPED - {why}")
        drop_stale("aircraft/usaf_b-1b_dts.ini")
        return
    text = src.read_text(encoding="utf-8-sig")
    m = re.search(r"^\[WeaponSystem1Strike183\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not m:
        sys.exit("usaf_b-1b_dts.ini: Strike183 not found - upstream changed")
    body = m.group(1)
    if body.count("dts_agm-183a\n") != 6:
        sys.exit(f"usaf_b-1b_dts.ini: Strike183 carries {body.count('dts_agm-183a')} "
                 "ARRW station(s), expected 6 - re-check the mirror by hand")
    block = (f"[WeaponSystem1{TESTBED_KEY}]\n"
             + body.replace("dts_agm-183a", TESTBED_ROUND).rstrip("\n") + "\n\n")
    text = text[:m.end()] + block + text[m.end():]
    text = declare(text, "usaf_b-1b_dts.ini", TESTBED_KEY)
    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    (OUT / "aircraft" / "usaf_b-1b_dts.ini").write_text(text, encoding="utf-8")
    print(f"  aircraft/usaf_b-1b_dts.ini  (+{TESTBED_KEY} 6x usn_arrw)")


def write_language():
    """Name the ARRW mod's own B-52H distinctly.

    The mission editor's type list showed two entries both reading "B-52H":
    the Dingtools dts_b-52h this pack extends, and usaf_b-52h_419_flts - the
    ARRW mod's separate test aircraft with its own single-loadout assortment.
    It looked like a broken duplicate. Language files merge key-by-key, so
    one entry renames it without touching anything else.
    """
    d = OUT / "language_en"
    d.mkdir(parents=True, exist_ok=True)
    (d / "loadout_names.ini").write_text(
        "[LoadoutNames]\n"
        "# SEST B-52 ARRW - only keys this pack introduces; Strike183 keeps its\n"
        "# upstream name because the F-15EX also declares that key and loadout\n"
        "# names are a GLOBAL key->name table.\n"
        "Strike183Nuke=SEST Strike183 Nuclear (W62 + AGM-86B)\n"
        f"{LRASM20_KEY}=SEST AntiShip LRASM (20x)\n"
        f"{TESTBED_KEY}=SEST ARRW Testbed\n",
        encoding="utf-8")
    (d / "aircraft_names.ini").write_text(
        "# SEST B-52 ARRW - disambiguate the ARRW mod's own test aircraft.\n"
        "[usaf_b-52h_419_flts]\n"
        "Default=B-52H 419th FLTS (ARRW Testbed),B-52H FLTS\n",
        encoding="utf-8")
    print("  language_en/aircraft_names.ini  (419th FLTS named distinctly)")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(
        "[Language_en]\n"
        "Name=SEST B-52 ARRW\n"
        "Description=AGM-183A across every in-service B-52, flying a real "
        "boost-glide profile. The Dingtools round that wins the load order "
        "models the ARRW as a sea-skimmer with the skim altitude set to 90000 "
        "feet - a hypersonic weapon reduced to a level high-altitude cruise. "
        "This restores the profile the ARRW mod's own author gave the same "
        "airframe: a steep 75 degree boost to 99000 feet over 35 seconds, "
        "booster separation on the mesh swap already in the file, then a "
        "descending hypersonic glide that keeps most of its speed. Also the "
        "W62 on the B-52H and ARRW on Red Storm Arsenal's B-52O. The three "
        "bombers also now share their fits - the B-52H's 20x LRASM load flies "
        "on the B-52O (replacing a 16-round one) and on the 419th FLTS testbed, "
        "and the testbed's own usn_arrw fit flies on both B-52s and on the "
        "B-1B.\n",
        encoding="utf-8")
    print("SEST_B52_ARRW")

    # usn_arrw is the ARRW mod's round; every testbed fit below is gated on
    # it, so unsubscribing that mod removes the fits rather than leaving
    # four aircraft pointing at a round nothing defines.
    testbed = (ARRW_MOD / "ammunition" / f"{TESTBED_ROUND}.ini").exists()
    if not testbed:
        print(f"  note: {TESTBED_ROUND} not exported - testbed fits skipped")

    # Porting a fit between airframes is only sound while they agree on
    # where the bay and the pylons are. Check before writing anything.
    shared = {}
    for label, path in (("dts_b-52h", B52_MOD / "aircraft" / "dts_b-52h.ini"),
                        ("usaf_b-52o", RSA / "aircraft" / "usaf_b-52o.ini"),
                        ("usaf_b-52h_419_flts",
                         ARRW_MOD / "aircraft" / "usaf_b-52h_419_flts.ini")):
        if path.exists():
            shared[label] = path.read_text(encoding="utf-8-sig")
    assert_shared_geometry(shared)
    if "dts_b-52h" not in shared:
        sys.exit("dts_b-52h.ini not exported - it is the donor for every ported fit")
    assert_pylon_seat(shared["dts_b-52h"])
    print(f"  geometry contract: {len(shared)} B-52 airframe(s) agree on bay and pylons")

    build_ammunition()
    build_aircraft(testbed)
    build_b52o(testbed)
    build_419_flts()
    build_b1b(testbed)
    write_language()


if __name__ == "__main__":
    main()
