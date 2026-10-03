#!/usr/bin/env python3
"""Build SEST Rafale F5: JATM, MALICE and LRASM fits for the late Rafales.

The donor is the French Air Force mod (3758943352), which since 3 Oct 2026
ships the whole Rafale family under the ids the retired Dassault Rafale mod
(3504168760) used. New loadouts on each of the three late-standard combat
airframes (fr_rafale_b_l, fr_rafale_c_l, fr_rafale_m_l - the M_L is the
carrier aeroplane, fielded off the Charles de Gaulle and in Long Reach). Each
is derived from one of the mod's own fits by swapping rounds on the stations
the donor already proves, so the geometry is the author's:

  SEST_Intercept260F5   from AirToAirLongRange: every MICA NG EM becomes
                        AIM-260, the Meteors too. Wingtip MICA IR and the
                        tanks stay.
  SEST_Intercept260Heavy from AirToAirIntercept, wing tanks dropped: six
                        AIM-260 (the fat JATM clipped the tanks beside it).
  SEST_MALICE           from StrikeLongRange: the SCALP-EG becomes AIM-424 on
                        the same seat; the radar MICAs and Meteors AIM-260.
  SEST_AntiShipLRASM    from AntiShip: the Exocet becomes LRASM; the radar
                        MICAs and Meteors AIM-260.

The B and C Late hang TWO heavy stores under the wings (stations 5/6) and
hide the centreline pylon, so their MALICE and LRASM fits carry two rounds,
and each has an _ER twin that adds the centreline tank the donor never fits
(three tanks). The M Late's new geometry is different: the French Air Force
mod puts ONE SCALP or ONE Exocet on the centreline (station 11, seat
AM39Center) with wing tanks on 7/8 and the outer MICA rails empty. The M's
MALICE and LRASM fits therefore carry one round each, already with two
tanks, and have no _ER twin - there is no third tank to add. The LRASM
keeps the centreline seat the SCALP and Exocet share there.

Wingtip IR MICAs are kept everywhere - the jet stays French.

Usage (repo root):  python3 integration/rafale-f5/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAFALE = ROOT / "mods-source" / "3758943352"
WEAPON_PACK = ROOT / "mods-source" / "3760871384"
OUT = Path(__file__).resolve().parent / "SEST_Rafale_F5"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402

AIRFRAMES = ["fr_rafale_b_l", "fr_rafale_c_l", "fr_rafale_m_l"]

# (new name, donor loadout, [(old store spec, new store spec), ...],
#  extra lines, pylons to un-hide, stations to drop)
#
# The donor loadouts carry fr_mica-ng-em (MICA NG) on the radar rails since
# the 20 Sep 2026 export of the old mod, and the French Air Force mod keeps
# that - except the M Late's AntiShip fit, which still hangs the legacy
# fr_mica-em; both ids are swapped where they appear. The IR round is
# deliberately not swapped: these derivations replace the radar AAMs with
# JATM and leave the short-range pair alone.
_AAM = [("?fr_mica-ng-em", "dts_aim-260"), ("?fr_mica-em", "dts_aim-260"),
        ("?fr_meteor", "dts_aim-260")]

# Land-based B and C Late: two heavy stores under the wings on the SCALP and
# AM39 seats, centreline pylon hidden by the donors.
WING_PAIR = [
    ("SEST_Intercept260F5", "AirToAirLongRange", _AAM),
    # The 424 mounts BARE, like the AIM-260 does - the SCALP seat's
    # -0.006 z offset floated it visibly clear of the pylon (screenshot).
    ("SEST_MALICE", "StrikeLongRange",
     [("fr_scalp-eg|SCALP", AIM424_ID)] + _AAM),
    ("SEST_AntiShipLRASM", "AntiShip",
     [("fr_am-39_B2|AM39", "dts_agm-158c-3|SCALP")] + _AAM),   # LRASM keeps the heavy seat
    # Heavy AAM: max JATM. The donor's WING tanks (7/8) go - the AIM-260s the
    # swap puts on the adjacent rails are Meteor-class fat and clip them
    # (reported in-game); the centreline tank stays, nothing sits beside it.
    ("SEST_Intercept260Heavy", "AirToAirIntercept", _AAM,
     (), (), ("Station7", "Station8")),
    # Both _ER fits add the centreline tank, so both must UN-hide Center_Pylon:
    # their donors never fit a centre store and hide the empty pylon, which
    # left the tank hanging under an invisible pylon.
    ("SEST_MALICE_ER", "StrikeLongRange",
     [("fr_scalp-eg|SCALP", AIM424_ID)] + _AAM,
     ["Station11=fr_tank_1200"], ("Center_Pylon",)),
    ("SEST_LRASM_ER", "AntiShip",
     [("fr_am-39_B2|AM39", "dts_agm-158c-3|SCALP")] + _AAM,
     ["Station11=fr_tank_1200"], ("Center_Pylon",)),
]

# Carrier M Late: one heavy store on the centreline seat, wing tanks already
# fitted by the donors, so no _ER twins.
CENTRELINE = [
    ("SEST_Intercept260F5", "AirToAirLongRange", _AAM),
    ("SEST_MALICE", "StrikeLongRange",
     [("fr_scalp-eg|AM39Center", AIM424_ID)] + _AAM),
    ("SEST_AntiShipLRASM", "AntiShip",
     [("fr_am-39_B2|AM39Center", "dts_agm-158c-3|AM39Center")] + _AAM),
    ("SEST_Intercept260Heavy", "AirToAirIntercept", _AAM,
     (), (), ("Station7", "Station8")),
]

DERIVATIONS = {"fr_rafale_b_l": WING_PAIR, "fr_rafale_c_l": WING_PAIR,
               "fr_rafale_m_l": CENTRELINE}

LOADOUT_NAMES = {
    # No store counts in the labels: the late airframes keep Meteor on the
    # fuselage stations their donors gave them, and the M Late carries one
    # heavy round where the B and C carry two, so composition varies.
    "en": {"SEST_Intercept260F5": "SEST Intercept (AIM-260)",
           "SEST_MALICE": "SEST InterceptMALICE (AIM-424/AIM-260)",
           "SEST_AntiShipLRASM": "SEST AntiShip LRASM",
           "SEST_Intercept260Heavy": "SEST Intercept Heavy (6x AIM-260)",
           "SEST_LRASM_ER": "SEST AntiShip LRASM LongRange (3 tanks)",
           "SEST_MALICE_ER": "SEST InterceptMALICE LongRange (3 tanks)"},
}

INFO_INI = """[Language_en]
Name=SEST Rafale F5
Description=JATM-era fits for the late Rafales: AIM-260 intercept, AIM-424 \
MALICE, and LRASM anti-ship on the heavy stations. Wingtip MICA IR retained.

[Compatibility]
ApproximateVersion=0.8.4
"""


def derive(text, name, donor, swaps, airframe, extra=(), unhide=(), drop=()):
    m = re.search(rf"^\[WeaponSystem1{donor}\][^\n]*\n(.*?)(?=^\[)", text, re.M | re.S)
    if not m:
        sys.exit(f"{airframe}: donor loadout {donor} not found")
    body = m.group(1)
    swapped = 0
    for old, new in swaps:
        optional = old.startswith("?")
        old = old.lstrip("?")
        n = len(re.findall(rf"^Station\d+={re.escape(old)}\s*$", body, re.M))
        if n == 0 and not optional:
            sys.exit(f"{airframe}/{donor}: no stations carry {old} - upstream changed")
        swapped += n
        body = re.sub(rf"^(Station\d+=){re.escape(old)}(\s*)$", rf"\g<1>{new}\g<2>",
                      body, flags=re.M)
    if not swapped:
        sys.exit(f"{airframe}/{name}: donor {donor} carries none of the rounds "
                 "this fit swaps - upstream changed")
    for st in drop:
        # Deleting a donor station outright - used to shed the wing tanks the
        # intercept donors carry, which the fatter AIM-260s on the adjacent
        # rails visibly clip. Fails loudly if the donor stops fitting it.
        body, n = re.subn(rf"^{st}=\S+\s*\n", "", body, count=1, flags=re.M)
        if n != 1:
            sys.exit(f"{airframe}/{name}: expected donor {donor} to fit {st} - "
                     "upstream changed, re-check the drop list")
    for line in extra:
        st = line.split("=")[0]
        if re.search(rf"^{st}=", body, re.M):
            sys.exit(f"{airframe}/{name}: {st} already occupied in donor")
        body = body.rstrip("\n") + "\n" + line + "\n"
    for sub in unhide:
        # A donor that never fits a store hides its empty pylon; a derivation
        # that adds the store must reveal it again, or the store hangs on a
        # hidden pylon (the *_ER centreline tanks did exactly that).
        before = body
        body = re.sub(rf"^(SubModelsToHide=.*?){re.escape(sub)},?", r"\1", body,
                      count=1, flags=re.M)
        body = re.sub(r"^(SubModelsToHide=.*?),\s*$", r"\1", body, flags=re.M)
        if body == before:
            sys.exit(f"{airframe}/{name}: expected {sub} in donor {donor}'s "
                     "SubModelsToHide - upstream changed, re-check the unhide list")
    return f"[WeaponSystem1{name}]\n" + body.rstrip("\n") + "\n\n"


def main():
    for a, need in [(WEAPON_PACK, "ammunition/dts_aim-260.ini"),
                    (WEAPON_PACK, "ammunition/dts_agm-158c-3.ini"),
                    (RAFALE, f"aircraft/{AIRFRAMES[0]}.ini")]:
        if not (a / need).exists():
            sys.exit(f"missing dependency: {a / need}")

    (OUT / "aircraft").mkdir(parents=True, exist_ok=True)
    print("SEST_Rafale_F5")
    for airframe in AIRFRAMES:
        text = (RAFALE / "aircraft" / f"{airframe}.ini").read_text(encoding="utf-8",
                                                                   errors="replace")
        derivations = DERIVATIONS[airframe]
        keys = [d[0] for d in derivations]
        la = re.search(r"^(AvailableLoadouts=)(.+)$", text, re.M)
        if any(k in la.group(2) for k in keys):
            sys.exit(f"{airframe}: SEST keys already declared upstream")
        text = (text[:la.end(2)] + "," + ",".join(keys) + text[la.end(2):])

        blocks = "".join(derive(text, *d[:3], airframe,
                                d[3] if len(d) > 3 else (),
                                d[4] if len(d) > 4 else (),
                                d[5] if len(d) > 5 else ())
                         for d in derivations)
        marker = "[---------- WeaponMagazines ----------]"
        if marker not in text:
            sys.exit(f"{airframe}: WeaponMagazines marker missing")
        text = text.replace(marker, blocks + marker, 1)
        (OUT / "aircraft" / f"{airframe}.ini").write_text(text, encoding="utf-8")
        print(f"  aircraft/{airframe}.ini  (+{len(keys)} loadouts)")

    write_aim424(OUT)
    for lang, names in LOADOUT_NAMES.items():
        d = OUT / f"language_{lang}"
        d.mkdir(exist_ok=True)
        body = "[LoadoutNames]\n\n# ---------- SEST Rafale F5 ----------\n"
        body += "".join(f"{k}={v}\n" for k, v in names.items())
        (d / "loadout_names.ini").write_text(body, encoding="utf-8")
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print("  ammunition/sest_aim-424.ini + loadout names")


if __name__ == "__main__":
    main()
