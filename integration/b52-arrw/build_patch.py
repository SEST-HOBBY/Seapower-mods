#!/usr/bin/env python3
"""Build the SEST B-52 ARRW patch: put the AGM-183A on every in-service B-52,
and make it actually loft.

TWO DEFECTS, both found by comparing against the collection rather than by
taste.

1. The AGM-183A never lofts. Every other hypersonic weapon here pairs a high
   SeaSkimmingAlt (the cruise altitude) with a MaxLoftAlt (the boost apex):
   usn_cps 99000/90000, plan_yj21 99000/90000, plan_yj_17 92000/95000,
   usa_prsm 160000/160000, wp_ss-n-26 46000/46000. dts_agm-183a and
   dts_agm-183a(w62) are the ONLY two files in the collection carrying a
   SeaSkimmingAlt above 20,000 ft with no MaxLoftAlt at all - so the boost-
   glide weapon flies a flat cruise instead of the lofted profile that is the
   entire point of it. Same class of omission as the AIM-424's missing
   DragCoefficient: a key left off, silently costing the weapon its behaviour.

   Anchored to usn_cps - the US Navy's own boost-glide round, which this
   collection already fields on the Zumwalt - rather than to the ARRW mod's
   usn_arrw. usn_arrw models the profile well but gets the hardware wrong:
   850 kg against the real ~2270 kg, Power 45 against 300, and a MaxVelocity
   written "10,648" with a thousands separator that no other value in the
   collection uses. Dingtools has the mass and warhead right and the profile
   missing, so the profile is what gets added; nothing else is touched.

2. The B-52H cannot carry the W62. dts_agm-183a(w62) ships in the B-52H mod's
   own folder, and the F-15EX and B-1B both have loadouts for it - but the
   B-52H, the only aircraft that ever actually flew ARRW, has none. Adding
   Strike183Nuke mirrors the existing Strike183 exactly: the same four pylon
   stations, the same position keys, the same SubModelsToHide.

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

# usn_cps, the Navy boost-glide round already in the collection, is the anchor.
# MaxLoftAngle is the one value not copied straight across: CPS is surface-
# launched and needs a shallow 35 deg to reach its 1889 nm; ARRW is released
# above 40,000 ft and boosts steeply from there, so 45 sits between CPS and the
# ARRW mod's 75 without inventing range the weapon does not claim.
LOFT = {
    "MaxLoftAngle": "45.0",
    "MaxLoftAlt": "90000.0",
    "IgnoreHeightDifferenceForTargetDist": "True",
    "TerminalVelocity": "3800",
}

AGM183 = ["dts_agm-183a", "dts_agm-183a(w62)"]


def add_loft(text: str, name: str) -> str:
    """Insert the loft block right after SeaSkimmingAlt, where its peers put it."""
    for key in LOFT:
        if re.search(rf"^{re.escape(key)}=", text, re.M):
            sys.exit(f"{name}: {key} already present - upstream changed, re-check by hand")
    m = re.search(r"^SeaSkimmingAlt=[^\n]*\n", text, re.M)
    if not m:
        sys.exit(f"{name}: no SeaSkimmingAlt to anchor the loft block to")
    block = ("".join(f"{k}={v}\n" for k, v in LOFT.items()))
    return text[:m.end()] + block + text[m.end():]


def build_ammunition():
    for a in AGM183:
        src = DINGTOOLS / "ammunition" / f"{a}.ini"
        if not src.exists():
            sys.exit(f"missing upstream: {src}")
        out = add_loft(src.read_text(encoding="utf-8"), a)
        dst = OUT / "ammunition" / f"{a}.ini"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out, encoding="utf-8")
        print(f"  ammunition/{a}.ini  (+{len(LOFT)} loft keys)")


def build_aircraft():
    src = B52_MOD / "aircraft" / "dts_b-52h.ini"
    text = src.read_text(encoding="utf-8")

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

    nuke = ("[WeaponSystem1Strike183Nuke]\n" + ws1_body
            + "[WeaponSystem2Strike183Nuke]\n"
            + ws2_body.replace("dts_agm-183a|", "dts_agm-183a(w62)|"))
    if "(w62)" not in nuke:
        sys.exit("W62 substitution did not take - station syntax changed")

    # Append after the Strike183 pair, and register it in the picker.
    text = text[:m.end()] + "\n" + nuke + text[m.end():]
    la = re.search(r"^AvailableLoadouts=([^\n]+)$", text, re.M)
    if "Strike183Nuke" in la.group(1):
        sys.exit("Strike183Nuke already declared upstream")
    text = (text[:la.start(1)] + la.group(1) + ",Strike183Nuke" + text[la.end(1):])

    dst = OUT / "aircraft" / "dts_b-52h.ini"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    n = nuke.count("dts_agm-183a(w62)")
    print(f"  aircraft/dts_b-52h.ini  (+Strike183Nuke, {n}x W62)")


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


def build_b52o():
    """Give Red Storm Arsenal's B-52O the ARRW, on the pylon it already uses.

    The B-52O has no AGM183 position key. It does not need one: RSA already
    hangs a large hypersonic (usn_agm_110l) one-per-pylon on WeaponSystem2 via
    RGM110_Rack, which is exactly the ARRW fit. Copying that block and swapping
    the round keeps the geometry the author tuned.

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
    text = src.read_text(encoding="utf-8")
    m = re.search(r"^\[WeaponSystem2AntiShipHeavy\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not m:
        sys.exit("usaf_b-52o.ini: AntiShipHeavy not found - upstream changed")
    body = m.group(1)
    if "usn_agm_110l|RGM110_Rack" not in body:
        sys.exit("usaf_b-52o.ini: AntiShipHeavy no longer uses the RGM110 rack")

    blocks = ""
    for name, round_ in (("Strike183", "dts_agm-183a"),
                         ("Strike183Nuke", "dts_agm-183a(w62)")):
        blocks += (f"[WeaponSystem2{name}]\n"
                   + body.replace("usn_agm_110l", round_).rstrip("\n") + "\n\n")
    text = text[:m.end()] + "\n" + blocks + text[m.end():]

    la = re.search(r"^AvailableLoadouts=([^\n]+)$", text, re.M)
    if "Strike183" in la.group(1):
        sys.exit("usaf_b-52o.ini: Strike183 already declared upstream")
    text = text[:la.start(1)] + la.group(1) + ",Strike183,Strike183Nuke" + text[la.end(1):]

    dst = OUT / "aircraft" / "usaf_b-52o.ini"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print("  aircraft/usaf_b-52o.ini  (+Strike183, +Strike183Nuke, 2x each on the pylons)")


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
    at = a.read_text(encoding="utf-8")
    fixed = re.sub(r"^(MaxVelocity=)([0-9]{1,3}),([0-9]{3})\b", r"\1\2\3", at, flags=re.M)
    if fixed == at:
        sys.exit("usn_arrw.ini: the MaxVelocity thousands separator is gone - re-check")
    (OUT / "ammunition").mkdir(parents=True, exist_ok=True)
    (OUT / "ammunition" / "usn_arrw.ini").write_text(fixed, encoding="utf-8")
    print("  ammunition/usn_arrw.ini  (MaxVelocity 10,648 -> 10648)")
    drop_stale("aircraft/usaf_b-52h_419_flts.ini")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(
        "[Language_en]\n"
        "Name=SEST B-52 ARRW\n"
        "Description=AGM-183A across every in-service B-52: the lofted "
        "boost-glide profile it was missing, the W62 on the B-52H, ARRW on "
        "Red Storm Arsenal's B-52O, and the 419th FLTS testbed's unreachable "
        "loadouts declared.\n",
        encoding="utf-8")
    print("SEST_B52_ARRW")
    build_ammunition()
    build_aircraft()
    build_b52o()
    build_419_flts()


if __name__ == "__main__":
    main()
