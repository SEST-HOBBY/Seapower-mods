#!/usr/bin/env python3
"""Add the Red Storm Arsenal reinforcements and RAAF Base Townsville to NFIII.

Three additions, all found in the RSA survey:

  RED   3x H-6K inbound from the north-west with AntiShipHeavy (8x YJ-12
        supersonic AShM each) - the standoff missile-truck threat the mission
        had no equivalent of.
  RED   The Type 004 carrier gets the missing halves of a real carrier air
        wing: 4x KJ-600 (carrier AEW - the group was radar-blind beyond the
        escorts) and 12x J-15T (the catapult bird, fitting a CATOBAR hull).
  BLUE  RAAF Base Townsville at its real coordinates, flying the roster the
        SEST_RAAF_Bases pack gives it (AH-64E, 6 SQN F-15EX, MH-60R, S-70B-2,
        KC-130T). Placed instead of Amberley by request.

Idempotent: each addition has a presence marker and is skipped when found, so
the pass can sit in the refresh-mission chain and survive editor round-trips.

    python3 integration/missions/add_nfiii_reinforcements.py --mission "NORTHERN FRONT III FINAL" --write
"""
import argparse
import re
import sys
from pathlib import Path

MISSIONS = Path(__file__).resolve().parent

# Real geography via the mission's own mapping: x=(lon-centreLon)*60,
# z=(lat-centreLat)*60 - verified against Darwin (9429.85,-4001.8).
TOWNSVILLE = (-19.2526, 146.7652)   # RAAF Base Townsville / Garbutt


def bump(text, key, by):
    m = re.search(rf"^{key}=(\d+)$", text, re.M)
    if not m:
        sys.exit(f"{key} not found")
    return (text[:m.start(1)] + str(int(m.group(1)) + by) + text[m.end(1):],
            int(m.group(1)) + by)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mission", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    f = MISSIONS / f"{args.mission}.ini"
    if not f.exists():
        sys.exit(f"no such mission: {f}")
    text = f.read_text(encoding="utf-8", errors="replace")

    if "plan_cvn_004" not in text:
        print("no Type 004 carrier in this mission - skipping reinforcements")
        return
    did = []

    # --- 1. carrier air wing: KJ-600 AEW + J-15T ----------------------------
    if "plan_kj600=" not in text:
        m = re.search(r"^(plan_j-15d=[^\n]*\n)", text, re.M)
        if not m:
            sys.exit("Type 004's air group lost its plan_j-15d line - re-anchor this pass")
        text = (text[:m.end()]
                + "plan_j_15t=Squadron1,12\n"
                + "plan_kj600=Squadron1,4\n"
                + text[m.end():])
        did.append("Type 004 wing: +12x J-15T, +4x KJ-600 AEW")

    # --- 2. H-6K strike package ---------------------------------------------
    if "Type=plaaf_h6k" not in text:
        n0 = max(int(x) for x in re.findall(r"^\[Taskforce2Aircraft(\d+)\]", text, re.M))
        blocks = ""
        for i in range(3):
            n = n0 + 1 + i
            x, z = 9040 + i * 4, -3060 - i * 3
            blocks += (f"[Taskforce2Aircraft{n}]\n"
                       f"Type=plaaf_h6k\n"
                       f"SquadronReference=Default\n"
                       f"UnlimitedFuel=False\n"
                       f"LoadoutVariant=AntiShipHeavy\n"
                       f"WeaponStatus=Free\n"
                       f"CrewSkill=Trained\n"
                       f"Morale=3\n"
                       f"RelativePositionInNM={x},37000,{z}\n"
                       f"Telegraph=3\n"
                       f"Heading=118\n"
                       f"Waypoints={x + 320:.0f},37000,{z - 260:.0f}\n")
        last = re.search(r"^\[Taskforce2Aircraft" + str(n0) + r"\]\n.*?(?=^\[)",
                         text, re.M | re.S)
        if not last:
            sys.exit(f"could not locate [Taskforce2Aircraft{n0}] block")
        text = text[:last.end()] + blocks + text[last.end():]
        text, _ = bump(text, "NumberOfTaskforce2Aircraft", 3)
        did.append("3x H-6K (AntiShipHeavy, 8x YJ-12 each) inbound from the NW")

    # --- 3. RAAF Base Townsville --------------------------------------------
    if "Type=airbase_raaf_townsville" not in text:
        clat = float(re.search(r"^MapCenterLatitude=([\-\d.]+)", text, re.M).group(1))
        clon = float(re.search(r"^MapCenterLongitude=([\-\d.]+)", text, re.M).group(1))
        x = (TOWNSVILLE[1] - clon) * 60
        z = (TOWNSVILLE[0] - clat) * 60
        n0 = max(int(m) for m in re.findall(r"^\[Taskforce1LandUnit(\d+)\]", text, re.M))
        n = n0 + 1
        block = (f"[Taskforce1LandUnit{n}]\n"
                 f"Type=airbase_raaf_townsville\n"
                 f"VariantReference=Variant1\n"
                 f"UnlimitedFuel=False\n"
                 f"CrewSkill=Trained\n"
                 f"Morale=3\n"
                 f"RelativePositionInNM={x:.2f},low,{z:.2f}\n"
                 f"Nation=australia\n"
                 f"Heading=0\n")
        last = re.search(r"^\[Taskforce1LandUnit" + str(n0) + r"\]\n.*?(?=^\[)",
                         text, re.M | re.S)
        if not last:
            sys.exit(f"could not locate [Taskforce1LandUnit{n0}] block")
        text = text[:last.end()] + block + text[last.end():]
        text, _ = bump(text, "NumberOfTaskforce1LandUnits", 1)
        text, nf = bump(text, "Taskforce1_NumberOfFormations", 1)
        fm = re.search(r"^(Taskforce1_Formation\d+=[^\n]*\n)(?!Taskforce1_Formation)",
                       text, re.M)
        text = (text[:fm.end()]
                + f"Taskforce1_Formation{nf}=Taskforce1LandUnit{n}|RAAF Base Townsville"
                  f"|Circle|1.5|OverrideSpawnPositions\n"
                + text[fm.end():])
        ov = re.search(r"^(Taskforce1LandUnit\d+ShortNameOverride=[^\n]*\n)", text, re.M)
        text = (text[:ov.start()]
                + f"Taskforce1LandUnit{n}NameOverride=RAAF Base Townsville\n"
                + f"Taskforce1LandUnit{n}ShortNameOverride=YBTL\n"
                + text[ov.start():])
        did.append(f"RAAF Base Townsville at ({x:.0f},{z:.0f}), pack roster "
                   "(AH-64E, 6 SQN F-15EX, MH-60R, S-70B-2, KC-130T)")

    if not did:
        print("NFIII reinforcements already present - nothing to do")
        return
    for d in did:
        print(f"  + {d}")
    if args.write:
        f.write_text(text, encoding="utf-8")
        print(f"written: {f}")
    else:
        print("dry run - pass --write to apply")


if __name__ == "__main__":
    main()
