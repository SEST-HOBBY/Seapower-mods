#!/usr/bin/env python3
"""Build SEST Rafale F5: JATM, MALICE and LRASM fits for the late Rafales.

Three new loadouts on each of the three late-standard combat airframes
(fr_rafale_b_l, fr_rafale_c_l, fr_rafale_m_l - the M_L is fielded in every
NORTHERN FRONT mission). Each is derived from one of the mod's own fits by
swapping rounds on the stations the donor already proves, so the geometry is
the author's:

  SEST_Intercept260  from AirToAirLongRange: every MICA-EM becomes AIM-260.
                     Wingtip MICA-IR, the donors' Meteors and the tanks stay.
  SEST_MALICE        from StrikeLongRange: the two SCALP-EG (S5/6, the heavy
                     wet stations) become AIM-424 on the same SCALP seat; the
                     four MICA-EM become AIM-260.
  SEST_AntiShipLRASM from AntiShip: the two Exocets become LRASM, seated on
                     the SCALP key rather than the Exocet one (1,023 kg rides
                     the 1,300 kg round's mount, not the 655 kg one's); the
                     four MICA-EM become AIM-260.

Wingtip IR MICAs are kept everywhere - the jet stays French.

Usage (repo root):  python3 integration/rafale-f5/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAFALE = ROOT / "mods-source" / "3504168760"
WEAPON_PACK = ROOT / "mods-source" / "3760871384"
OUT = Path(__file__).resolve().parent / "SEST_Rafale_F5"

sys.path.insert(0, str(ROOT / "integration"))
from common.aim424 import AIM424_ID, write_aim424  # noqa: E402

AIRFRAMES = ["fr_rafale_b_l", "fr_rafale_c_l", "fr_rafale_m_l"]
NEW_KEYS = ["SEST_Intercept260", "SEST_MALICE", "SEST_AntiShipLRASM",
            "SEST_Intercept260Heavy", "SEST_LRASM_ER", "SEST_MALICE_ER"]

# (new name, donor loadout, [(old store spec, new store spec), ...])
DERIVATIONS = [
    ("SEST_Intercept260", "AirToAirLongRange",
     [("fr_mica-em", "dts_aim-260"), ("?fr_meteor", "dts_aim-260")]),
    # The 424 mounts BARE, like the AIM-260 does - the SCALP seat's
    # -0.006 z offset floated it visibly clear of the pylon (screenshot).
    ("SEST_MALICE", "StrikeLongRange",
     [("fr_scalp-eg|SCALP", AIM424_ID),
      ("fr_mica-em", "dts_aim-260"), ("?fr_meteor", "dts_aim-260")]),
    ("SEST_AntiShipLRASM", "AntiShip",
     [("fr_am-39_Block2|AM39", "dts_agm-158c-3|SCALP"),   # LRASM keeps the heavy seat
      ("fr_mica-em", "dts_aim-260"), ("?fr_meteor", "dts_aim-260")]),
    # Heavy AAM: max JATM, no tanks beyond the donor's.
    ("SEST_Intercept260Heavy", "AirToAirIntercept",
     [("fr_mica-em", "dts_aim-260"), ("?fr_meteor", "dts_aim-260")]),
    # LRASM with the centreline tank the AntiShip donor never fits.
    # MALICE with the centreline tank its StrikeLongRange donor never fits.
    ("SEST_MALICE_ER", "StrikeLongRange",
     [("fr_scalp-eg|SCALP", AIM424_ID),
      ("fr_mica-em", "dts_aim-260"), ("?fr_meteor", "dts_aim-260")],
     ["Station11=fr_tank_1200"]),
    ("SEST_LRASM_ER", "AntiShip",
     [("fr_am-39_Block2|AM39", "dts_agm-158c-3|SCALP"),
      ("fr_mica-em", "dts_aim-260"), ("?fr_meteor", "dts_aim-260")],
     ["Station11=fr_tank_1200"]),
]

LOADOUT_NAMES = {
    # No store counts in the labels: the late airframes keep Meteor on the
    # fuselage stations their donors gave them, so composition varies.
    "en": {"SEST_Intercept260": "SEST Intercept (AIM-260)",
           "SEST_MALICE": "SEST InterceptMALICE (AIM-424/AIM-260)",
           "SEST_AntiShipLRASM": "SEST AntiShip LRASM",
           "SEST_Intercept260Heavy": "SEST Intercept Heavy (6x AIM-260)",
           "SEST_LRASM_ER": "SEST AntiShip LRASM LongRange (3 tanks)",
           "SEST_MALICE_ER": "SEST InterceptMALICE LongRange (3 tanks)"},
}

INFO_INI = """[Language_en]
Name=SEST Rafale F5
Description=JATM-era fits for the late Rafales: AIM-260 intercept, AIM-424 \
MALICE, and LRASM anti-ship on the SCALP stations. Wingtip MICA IR retained.

[Compatibility]
ApproximateVersion=0.8.1
"""


def derive(text, name, donor, swaps, airframe, extra=()):
    m = re.search(rf"^\[WeaponSystem1{donor}\][^\n]*\n(.*?)(?=^\[)", text, re.M | re.S)
    if not m:
        sys.exit(f"{airframe}: donor loadout {donor} not found")
    body = m.group(1)
    for old, new in swaps:
        optional = old.startswith("?")
        old = old.lstrip("?")
        n = len(re.findall(rf"^Station\d+={re.escape(old)}\s*$", body, re.M))
        if n == 0 and not optional:
            sys.exit(f"{airframe}/{donor}: no stations carry {old} - upstream changed")
        body = re.sub(rf"^(Station\d+=){re.escape(old)}(\s*)$", rf"\g<1>{new}\g<2>",
                      body, flags=re.M)
    for line in extra:
        st = line.split("=")[0]
        if re.search(rf"^{st}=", body, re.M):
            sys.exit(f"{airframe}/{name}: {st} already occupied in donor")
        body = body.rstrip("\n") + "\n" + line + "\n"
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
        la = re.search(r"^(AvailableLoadouts=)(.+)$", text, re.M)
        if any(k in la.group(2) for k in NEW_KEYS):
            sys.exit(f"{airframe}: SEST keys already declared upstream")
        text = (text[:la.end(2)] + "," + ",".join(NEW_KEYS) + text[la.end(2):])

        blocks = "".join(derive(text, *d[:3], airframe, d[3] if len(d) > 3 else ())
                 for d in DERIVATIONS)
        marker = "[---------- WeaponMagazines ----------]"
        if marker not in text:
            sys.exit(f"{airframe}: WeaponMagazines marker missing")
        text = text.replace(marker, blocks + marker, 1)
        (OUT / "aircraft" / f"{airframe}.ini").write_text(text, encoding="utf-8")
        print(f"  aircraft/{airframe}.ini  (+{len(NEW_KEYS)} loadouts)")

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
