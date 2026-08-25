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
    # and load the conventional fit's own bay in place
    text = (text[:m.start()]
            + "[WeaponSystem1Strike183]\n" + conv_bay
            + "[WeaponSystem2Strike183]\n" + ws2_body
            + text[m.end():])
    m = re.search(r"^\[WeaponSystem1Strike183\]\n(.*?)(?=^\[WeaponSystem2Strike183\])"
                  r"(?:\[WeaponSystem2Strike183\]\n)(.*?)(?=^\[|\Z)", text, re.M | re.S)

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
    print(f"  aircraft/dts_b-52h.ini  (+Strike183Nuke {n}x W62; bays: 8x JASSM-ER / 8x AGM-86B)")


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

    # Our own position key, injected into the WS2 table next to the author's.
    # Geometry is the B-52H's proven two-per-side ARRW carriage, verbatim.
    if "AGM183_Pylon" in text or "LRASM_Pylon" in text:
        sys.exit("usaf_b-52o.ini: AGM183_Pylon already defined upstream - re-check")
    rk = re.search(r"^RGM110_RackPositions=[^\n]*\n", text, re.M)
    if not rk:
        sys.exit("usaf_b-52o.ini: RGM110_RackPositions gone - upstream changed")
    text = (text[:rk.end()]
            + "AGM183_PylonPositions=0,-0.003,-0.02|0,-0.003,0.062\n"
            + "LRASM_PylonPositions=-0.0084,-0.0042,-0.035|0.0084,-0.0042,-0.035"
              "|-0.0084,-0.0042,0.035|0.0084,-0.0042,0.035\n"
            + text[rk.end():])
    m = re.search(r"^\[WeaponSystem2AntiShipHeavy\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    body = m.group(1)

    # Bay: the O's own Standoff donor - a CSRL of AGM-86 - minus "Pylons" from
    # its SubModelsToHide, because unlike Standoff our fits hang ARRW out there.
    sd = re.search(r"^\[WeaponSystem1Standoff\]\n(.*?)(?=^\[)", text, re.M | re.S)
    if not sd or "Station6=usaf_agm-86c|CSRL" not in sd.group(1):
        sys.exit("usaf_b-52o.ini: Standoff CSRL donor gone - upstream changed")
    bay = sd.group(1).replace("SubModelsToHide=Pylons,", "SubModelsToHide=")

    # AntiShipLRASM gets its OWN carriage. The first cut reused AGM84_Pylon -
    # the Harpoon six-pack - and in game the fat LRASM airframes read as a
    # Harpoon cluster. LRASM_Pylon keeps the Harpoon rack's proven x/z frame
    # but drops its centre column: the four corner positions only, uncanted,
    # at the centre row's hang height. Four per pylon, eight external, plus a
    # CSRL of eight - the round the B-52H's AntiShip already flies.
    blocks = ""
    for name, ws2, alcm in (
            ("Strike183", "dts_agm-183a|AGM183_Pylon", "usaf_agm-86c"),
            ("Strike183Nuke", "dts_agm-183a(w62)|AGM183_Pylon", "usaf_agm-86b"),
            ("AntiShipLRASM", "dts_agm-158c-3|LRASM_Pylon", "dts_agm-158c-3")):
        blocks += (f"[WeaponSystem1{name}]\n"
                   + bay.replace("usaf_agm-86c", alcm).rstrip("\n") + "\n"
                   + f"[WeaponSystem2{name}]\n"
                   + body.replace("usn_agm_110l|RGM110_Rack", ws2).rstrip("\n") + "\n\n")
    text = text[:m.end()] + "\n" + blocks + text[m.end():]

    la = re.search(r"^AvailableLoadouts=([^\n]+)$", text, re.M)
    if "Strike183" in la.group(1):
        sys.exit("usaf_b-52o.ini: Strike183 already declared upstream")
    text = (text[:la.start(1)] + la.group(1)
            + ",Strike183,Strike183Nuke,AntiShipLRASM" + text[la.end(1):])

    dst = OUT / "aircraft" / "usaf_b-52o.ini"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print("  aircraft/usaf_b-52o.ini  (+Strike183/+Nuke 4x ARRW; +AntiShipLRASM 8+8x LRASM)")


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
    write_language()


if __name__ == "__main__":
    main()
