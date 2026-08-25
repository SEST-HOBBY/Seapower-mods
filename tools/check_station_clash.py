#!/usr/bin/env python3
"""Find stores mounted on top of each other in a SEST loadout.

Two stores whose stations sit at nearly the same point render as one missile
growing out of another, or a missile buried in a fuel tank. Nothing in the game
complains - it just looks wrong.

    python3 tools/check_station_clash.py [separation]

Default separation is the one clash confirmed in game (0.0181). Close-set rails
on a shared pylon are NORMAL and will show at that threshold, so start tight:

    python3 tools/check_station_clash.py 0.001   # only true co-location

READ THIS BEFORE TRUSTING THE OUTPUT. Each [WeaponSystemN] block has its OWN
station table, and the same station NUMBER means different coordinates in each.
usaf_f-15ex_SEII has Station13 in two tables - fuselage aft in one, wing station
in the other. Matching loadouts against the wrong table invents co-locations
that are not there: a first cut of this script reported twenty stores at exactly
d=0.00000, every one of them a phantom. A bare [WeaponSystemN] starts a table;
[WeaponSystemN<Name>] is a loadout that must be read against table N only.
"""
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HDR = re.compile(r"^\[WeaponSystem(\d+)(\w*)\][^\n]*$", re.M)


def main():
    sep = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0181
    hits = 0
    for f in sorted(ROOT.glob("integration/*/SEST_*/aircraft/*.ini")):
        text = f.read_text(encoding="utf-8", errors="replace")
        marks = [(m.start(), m.group(1), m.group(2)) for m in HDR.finditer(text)]
        tables, loadouts = {}, []
        for i, (start, num, suffix) in enumerate(marks):
            body = text[start:marks[i + 1][0] if i + 1 < len(marks) else len(text)]
            if suffix == "":
                tables[num] = {int(a): (float(b), float(c), float(d)) for a, b, c, d
                               in re.findall(r"^Station(\d+)=([-\d.]+),([-\d.]+),([-\d.]+)",
                                             body, re.M)}
            else:
                loadouts.append((num, suffix, body))
        for num, name, body in loadouts:
            pos = tables.get(num, {})
            st = {int(a): b.split("|")[0] for a, b in
                  re.findall(r"^Station(\d+)=([A-Za-z]\S*)", body, re.M)}
            for (s1, v1), (s2, v2) in itertools.combinations(sorted(st.items()), 2):
                if s1 not in pos or s2 not in pos:
                    continue
                d = sum((pos[s1][i] - pos[s2][i]) ** 2 for i in range(3)) ** 0.5
                if d <= sep:
                    hits += 1
                    print(f"{f.name:<22} WS{num} {name:<24} "
                          f"S{s1}={v1} <-> S{s2}={v2}  d={d:.5f}")
    print(f"\n{hits} pair(s) within {sep} across the SEST packs"
          + ("" if hits else " - nothing stacked"))


if __name__ == "__main__":
    main()
