#!/usr/bin/env python3
"""Build the SEST B-52H ARRW patch: make the AGM-183A actually loft, and give
the B-52H the nuclear variant it is the only aircraft entitled to carry.

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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(
        "[Language_en]\n"
        "Name=SEST B-52H ARRW\n"
        "Description=Gives the AGM-183A the lofted boost-glide profile every "
        "other hypersonic weapon here has, and lets the B-52H carry the W62.\n",
        encoding="utf-8")
    print("SEST_B52_ARRW")
    build_ammunition()
    build_aircraft()


if __name__ == "__main__":
    main()
